"""`bad export` — render a final report to a shareable HTML (and optional PDF)
artifact with a RESOLVED References appendix.

The shipped report carries bare `[N]` / `[[note-id]]` citation markers; the source
title/url lives off-band in the vault note frontmatter. This command closes that
loop: it resolves every marker to its source and emits a clickable References
appendix, so the exported artifact stands on its own. Keyless (stdlib + in-repo
renderer; PDF reuses the bundled pymupdf).

Standalone-safe (mirrors verify-citations / uncited-gate): with a vault present the
source map is built from `research/notes/*.md`; otherwise pass `--sources`/
`--note-bodies` (a JSON `{note_id: body}` map) — numeric `[N]` resolves
positionally ([1] = first key).
"""

from __future__ import annotations

import json
from pathlib import Path

import typer


def export_cmd(
    report: str = typer.Argument(..., help="Path to the final report markdown."),
    out: str = typer.Option(
        None, "--out", "-o",
        help="Output HTML path (default: <report>.html beside the report).",
    ),
    pdf: bool = typer.Option(
        False, "--pdf",
        help="Also render a PDF (keyless, via the bundled pymupdf; HTML-only if it "
             "is unavailable — no new dep is added).",
    ),
    sources: str = typer.Option(
        None, "--sources", "--note-bodies",
        help="JSON {note_id: body-with-frontmatter} map for standalone use (no "
             "vault). `[[note-id]]` resolves by id; numeric `[N]` resolves to the "
             "N-th key in insertion order ([1] = first key). Default: read the "
             "vault's research/notes/*.md.",
    ),
    title: str = typer.Option(None, "--title", help="Document title (default: the report's H1)."),
    json_output: bool = typer.Option(False, "--json", "-j"),
) -> None:
    """Render REPORT to HTML (+PDF) with a resolved References appendix.

    Resolves bare `[N]` / `[[note-id]]` citations into a real References list mapped
    to each source's title/url, so the exported report has no dangling brackets."""
    from bad_research.export import (
        SourceRef,
        export_report,
        source_refs_from_notes,
        source_refs_from_vault,
    )

    report_path = Path(report)
    if not report_path.is_file():
        raise typer.BadParameter(f"report not found: {report}")
    report_md = report_path.read_text(encoding="utf-8")

    # Build the {note_id: SourceRef} map. Explicit --sources wins (standalone);
    # otherwise read the discovered vault's notes dir. A missing vault degrades to
    # an empty map (markers then resolve as dangling and are honestly disclosed).
    src_map: dict[str, SourceRef]
    if sources:
        bodies = json.loads(Path(sources).read_text(encoding="utf-8"))
        src_map = source_refs_from_notes(bodies)
    else:
        try:
            from bad_research.core.vault import Vault, VaultError

            try:
                vault = Vault.discover()
                src_map = source_refs_from_vault(Path(vault.root) / "research" / "notes")
            except VaultError:
                src_map = {}
        except ImportError:
            src_map = {}

    out_html = Path(out) if out else report_path.with_suffix(".html")
    out_pdf = out_html.with_suffix(".pdf") if pdf else None

    result = export_report(
        report_md, src_map, out_html, out_pdf=out_pdf, title=title
    )

    payload = {
        "html": str(result.html_path),
        "pdf": str(result.pdf_path) if result.pdf_path else None,
        "pdf_requested": pdf,
        "markers": result.n_markers,
        "resolved": result.n_resolved,
        "dangling": result.n_dangling,
        "references": [
            {
                "n": r.n,
                "marker": r.marker,
                "title": r.ref.title if r.ref else None,
                "url": r.ref.url if r.ref else None,
                "resolved": r.ref is not None,
            }
            for r in result.references
        ],
    }
    if json_output:
        typer.echo(json.dumps(payload))
        return

    typer.echo(f"Exported HTML: {result.html_path}")
    if pdf:
        if result.pdf_path:
            typer.echo(f"Exported PDF:  {result.pdf_path}")
        else:
            typer.echo("PDF skipped: pymupdf unavailable; wrote HTML only (no new dep).")
    typer.echo(
        f"References: {result.n_resolved}/{result.n_markers} markers resolved"
        + (f", {result.n_dangling} dangling (disclosed in the appendix)." if result.n_dangling else ".")
    )


__all__ = ["export_cmd"]
