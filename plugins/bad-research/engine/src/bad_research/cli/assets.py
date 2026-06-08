"""`bad assets` — list and resolve persisted note assets (figures, screenshots,
rendered PDF pages) for the host-model Read-tool vision path.

The host model (Claude) is natively multimodal, but until the assets write path
was wired NOTHING persisted a figure: crawl4ai screenshots and figure-dense /
text-layerless PDF pages were captured then dropped. These commands close the
loop — `bad assets list` shows what is bound to a note, and `bad assets path`
resolves an asset id to a real on-disk PNG the skill can hand to `Read`.

  bad assets list [--note-id <id>] [--type screenshot|image|pdf|other] [--json]
  bad assets path <asset-id> [--json]      # -> absolute readable file path

`save_pdf_page_assets` is the persistence helper the PDF branch uses: it renders
text-layerless / figure-dense pages to PNG (fetch_clean.render_pdf_pages) and
INSERTs one `type='image'` asset row per page so the substance-in-pixels case is
Read-able and citable.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import typer

from bad_research.cli._output import output
from bad_research.models.output import error as envelope_error
from bad_research.models.output import success

if TYPE_CHECKING:
    import sqlite3

    from bad_research.core.vault import Vault


assets_app = typer.Typer(
    name="assets",
    help="List and resolve persisted note assets (figures, screenshots, PDF pages).",
    no_args_is_help=True,
)


def _discover_vault() -> Vault:
    from bad_research.core.vault import Vault

    return Vault.discover()


def _asset_to_dict(asset: Any, vault_root: Path) -> dict[str, Any]:
    """Serialize an Asset, adding the resolved absolute path (None if missing)."""
    abs_path = vault_root / asset.filename
    return {
        "id": asset.id,
        "note_id": asset.note_id,
        "type": asset.type,
        "filename": asset.filename,
        "path": str(abs_path),
        "exists": abs_path.exists(),
        "url": asset.url,
        "alt_text": asset.alt_text,
        "content_type": asset.content_type,
        "size_bytes": asset.size_bytes,
        "created_at": asset.created_at,
    }


@assets_app.command("list")
def list_cmd(
    note_id: str | None = typer.Option(
        None, "--note-id", "--note", help="Only assets for this note id"
    ),
    type: str | None = typer.Option(
        None, "--type", help="Filter by type: screenshot|image|pdf|other"
    ),
    json_output: bool = typer.Option(False, "--json", "-j", help="Emit JSON"),
) -> None:
    """List persisted assets, optionally filtered by note id and/or type."""
    from bad_research.core.db import list_assets

    vault = _discover_vault()
    rows = list_assets(vault.db, note_id=note_id, type=type)
    data = [_asset_to_dict(a, vault.root) for a in rows]
    if json_output:
        output(success(data, count=len(data), vault=str(vault.root)), json_mode=True)
    else:
        if not data:
            typer.echo("No assets found.")
            return
        for d in data:
            mark = "" if d["exists"] else "  [MISSING]"
            typer.echo(f"{d['id']}\t{d['type']}\t{d['note_id']}\t{d['path']}{mark}")


@assets_app.command("path")
def path_cmd(
    asset_id: int = typer.Argument(..., help="Numeric asset id (from `assets list`)"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Emit JSON"),
) -> None:
    """Resolve an asset id to its readable absolute file path.

    The path is what the figure-reading skill instruction feeds to the `Read`
    tool so the host model can transcribe a figure/chart/scanned page.
    """
    from bad_research.core.db import get_asset

    vault = _discover_vault()
    asset = get_asset(vault.db, asset_id)
    if asset is None:
        if json_output:
            output(
                envelope_error(f"No asset with id {asset_id}", code="NOT_FOUND"),
                json_mode=True,
            )
        else:
            typer.echo(f"ERROR: no asset with id {asset_id}", err=True)
        raise typer.Exit(code=1)

    abs_path = vault.root / asset.filename
    if not abs_path.exists():
        if json_output:
            output(
                envelope_error(
                    f"Asset {asset_id} file missing on disk: {abs_path}",
                    code="FILE_MISSING",
                ),
                json_mode=True,
            )
        else:
            typer.echo(f"ERROR: asset {asset_id} file missing: {abs_path}", err=True)
        raise typer.Exit(code=1)

    if json_output:
        output(
            success(_asset_to_dict(asset, vault.root), vault=str(vault.root)),
            json_mode=True,
        )
    else:
        # plain path on stdout so it can be piped straight into Read / $(...)
        typer.echo(str(abs_path))


# --- persistence helper used by the PDF branch --------------------------------

def save_pdf_page_assets(
    conn: sqlite3.Connection,
    note_id: str,
    pdf_bytes: bytes,
    assets_dir: Path,
    *,
    url: str | None = None,
    only_figure_dense: bool = True,
) -> list[dict[str, Any]]:
    """Render text-layerless / figure-dense PDF pages to PNG assets.

    For a scanned or chart-heavy PDF, pdf_to_markdown yields no usable text, so the
    page's substance is in its pixels. This renders those pages (via
    fetch_clean.render_pdf_pages -> page.get_pixmap) to
    `research/assets/<note_id>/page-NNN.png` and INSERTs one `type='image'` asset
    row each, so the host model can Read the page and transcribe the figure. Returns
    a manifest list; IO/decode failures on a single page are swallowed.
    """
    import hashlib

    from bad_research.core.db import insert_asset
    from bad_research.web.content.fetch_clean import render_pdf_pages

    pages = render_pdf_pages(pdf_bytes, only_figure_dense=only_figure_dense)
    if not pages:
        return []
    assets_dir = Path(assets_dir)
    assets_dir.mkdir(parents=True, exist_ok=True)
    saved: list[dict[str, Any]] = []
    for entry in pages:
        png: bytes = entry["png"]
        page_no: int = entry["page"]
        try:
            digest = hashlib.sha256(png).hexdigest()[:8]
            filename = f"page-{page_no:03d}-{digest}.png"
            dest = assets_dir / filename
            dest.write_bytes(png)
            rel = f"research/assets/{note_id}/{filename}"
            asset_id = insert_asset(
                conn,
                note_id=note_id,
                filename=rel,
                type="image",
                url=url,
                alt_text=f"PDF page {page_no + 1} (figure-dense / text-layerless)",
                content_type="image/png",
                size_bytes=len(png),
            )
            saved.append(
                {"id": asset_id, "page": page_no, "path": rel, "bytes": len(png)}
            )
        except Exception:
            continue
    return saved


__all__ = ["assets_app", "save_pdf_page_assets"]
