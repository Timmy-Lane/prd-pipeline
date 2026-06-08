"""Render a final report to a standalone HTML document (and, when the keyless
`pymupdf` dep is present, a PDF) with a RESOLVED References appendix.

Wires the existing `serve.renderer.render_markdown` (the markdown→HTML pass that
also resolves `[[wiki-links]]`) and `export.refs` (citation resolution). The body
is rendered to HTML; every in-text `[N]` / `[[note-id]]` marker is rewritten to a
numbered superscript anchor link into a generated References list, so the shipped
report no longer carries bare unresolved brackets.

Keyless by design: HTML uses only stdlib + the in-repo renderer. PDF uses
`pymupdf` (`fitz`), already a hard dependency (it's the PDF text extractor) — no
new/heavy dep is added; if it is somehow unavailable the export degrades to
HTML-only.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path

from bad_research.serve.renderer import render_markdown

from .refs import (
    ResolvedReference,
    SourceRef,
    collect_markers,
    render_references_markdown,
    resolve_references,
)

# Same marker grammar as refs.collect_markers — numeric [N] OR [[note-id]] (with an
# optional |alias and/or :L42-L58 suffix). Used to rewrite in-text markers to anchors.
_MARKER_RE = re.compile(r"\[(\d+)\]|\[\[([^\]|]+)(?:\|[^\]]*)?\]\]")

_REFS_HEADING_RE = re.compile(r"^\s*#{1,6}\s+(sources|references)\b", re.IGNORECASE)

_HTML_STYLE = """
:root { color-scheme: light dark; }
body { max-width: 46rem; margin: 2.5rem auto; padding: 0 1.25rem;
  font: 16px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: #1a1a1a; background: #fff; }
h1, h2, h3, h4 { line-height: 1.25; margin-top: 1.6em; }
h1 { font-size: 1.9rem; }
a { color: #0b5cad; }
code { background: #f2f2f2; padding: 0.1em 0.3em; border-radius: 3px; font-size: 0.9em; }
pre { background: #f6f8fa; padding: 1rem; overflow-x: auto; border-radius: 6px; }
blockquote { border-left: 3px solid #ccc; margin: 0; padding-left: 1rem; color: #555; }
table.md-table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
table.md-table th, table.md-table td { border: 1px solid #ddd; padding: 0.4rem 0.6rem; text-align: left; }
sup.cite a { text-decoration: none; font-weight: 600; }
.references { margin-top: 2.5rem; border-top: 1px solid #ddd; padding-top: 1rem; }
.references ol { padding-left: 1.4rem; }
.references li { margin: 0.35rem 0; }
.references li.unresolved { color: #b00; }
""".strip()


@dataclass
class ExportResult:
    """The outcome of an export: where files landed + the resolution audit."""

    html_path: Path
    pdf_path: Path | None
    references: list[ResolvedReference]
    n_markers: int
    n_resolved: int
    n_dangling: int


def _marker_to_number(refs: list[ResolvedReference]) -> dict[str, int]:
    """`{marker-key: appendix-number}` so the in-text rewrite and the appendix
    agree on numbering. The key is the resolved marker (note-id or numeric ordinal),
    matching refs.collect_markers / resolve_references."""
    return {r.marker: r.n for r in refs}


def _split_body_and_existing_refs(report_md: str) -> str:
    """Report prose up to any existing Sources/References heading (we always emit
    our own resolved appendix in its place)."""
    out: list[str] = []
    for line in report_md.splitlines():
        if _REFS_HEADING_RE.match(line):
            break
        out.append(line)
    return "\n".join(out)


def _references_html(refs: list[ResolvedReference]) -> str:
    """The References appendix as an HTML <ol> with per-entry anchors (`id=ref-N`)
    so the in-text superscripts can link to them. Empty string when no markers."""
    if not refs:
        return ""
    items: list[str] = []
    for r in refs:
        if r.ref is None:
            items.append(
                f'<li id="ref-{r.n}" class="unresolved">[unresolved citation: '
                f"<code>{html.escape(r.marker)}</code>]</li>"
            )
        else:
            title = html.escape(r.ref.title)
            if r.ref.url and r.ref.url != r.ref.title:
                url = html.escape(r.ref.url, quote=True)
                body = f'{title} — <a href="{url}">{html.escape(r.ref.url)}</a>'
            else:
                body = title
            items.append(f'<li id="ref-{r.n}">{body}</li>')
    return (
        '<section class="references">\n<h2>References</h2>\n<ol>\n'
        + "\n".join(items)
        + "\n</ol>\n</section>"
    )


def render_report_html(
    report_md: str,
    sources: dict[str, SourceRef],
    *,
    title: str | None = None,
) -> tuple[str, list[ResolvedReference]]:
    """Render `report_md` to a full standalone HTML document with a resolved
    References appendix. Returns (html_document, resolved_references).

    The body's `[N]` / `[[note-id]]` markers are rewritten to numbered superscript
    anchor links into the appendix. Markers are resolved against `sources` via
    export.refs.resolve_references (note-id direct; numeric [N] positional)."""
    refs = resolve_references(report_md, sources)
    marker_num = _marker_to_number(refs)
    body_md = _split_body_and_existing_refs(report_md)

    # Rewrite markers to placeholders BEFORE render_markdown (which html-escapes the
    # whole body). A unique sentinel survives escaping; we swap in the real <sup>
    # anchor after rendering. This keeps the renderer untouched.
    placeholders: dict[str, str] = {}

    def _to_placeholder(m: re.Match[str]) -> str:
        raw = m.group(0)
        if m.group(1) is not None:  # numeric [N]
            key = m.group(1)
        else:  # [[note-id]] — strip :L42-L58 suffix to match the appendix key
            inner = m.group(2).strip()
            key = inner.split(":", 1)[0] if ":L" in inner else inner
        n = marker_num.get(key)
        if n is None:
            return raw  # not a numbered marker (shouldn't happen) — leave verbatim
        token = f"\x00CITE{n}\x00"
        placeholders[token] = (
            f'<sup class="cite"><a href="#ref-{n}">[{n}]</a></sup>'
        )
        return token

    body_md = _MARKER_RE.sub(_to_placeholder, body_md)
    body_html = render_markdown(body_md)
    for token, sup in placeholders.items():
        body_html = body_html.replace(token, sup)

    refs_html = _references_html(refs)
    doc_title = title or _infer_title(report_md)
    return (
        "<!DOCTYPE html>\n"
        f'<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{html.escape(doc_title)}</title>\n"
        f"<style>\n{_HTML_STYLE}\n</style>\n</head>\n<body>\n"
        f"{body_html}\n{refs_html}\n</body>\n</html>\n"
    ), refs


def _infer_title(report_md: str) -> str:
    """The document title = the report's first H1, else 'Research Report'."""
    for line in report_md.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip() or "Research Report"
    return "Research Report"


def _render_pdf(html_doc: str, pdf_path: Path) -> bool:
    """Render the HTML document to PDF via pymupdf's Story API (keyless; pymupdf is
    already a hard dep). Returns True on success, False if pymupdf is unavailable or
    the render fails — in which case the caller keeps HTML-only (no heavy new dep)."""
    try:
        import fitz  # type: ignore[import-untyped]  # PyMuPDF (PDF text extractor dep)
    except ImportError:
        return False
    try:
        story = fitz.Story(html=html_doc)
        writer = fitz.DocumentWriter(str(pdf_path))
        mediabox = fitz.paper_rect("a4")
        # 0.5" margins: fitz.Rect arithmetic (NOT list concat — adds a margin box).
        where = mediabox + fitz.Rect(36, 36, -36, -36)
        more = 1
        while more:
            dev = writer.begin_page(mediabox)
            more, _ = story.place(where)
            story.draw(dev)
            writer.end_page()
        writer.close()
        return True
    except Exception:
        # Any pymupdf-side failure degrades to HTML-only rather than crashing export.
        if pdf_path.exists():
            pdf_path.unlink()
        return False


def export_report(
    report_md: str,
    sources: dict[str, SourceRef],
    out_html: Path,
    *,
    out_pdf: Path | None = None,
    title: str | None = None,
) -> ExportResult:
    """Render `report_md` to `out_html` (always) and `out_pdf` (when `out_pdf` is
    given AND pymupdf renders it). Resolves citations into a References appendix.

    Returns an ExportResult carrying the file paths + the resolution audit
    (marker/resolved/dangling counts) so the CLI can report honestly."""
    doc, refs = render_report_html(report_md, sources, title=title)
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(doc, encoding="utf-8")

    pdf_written: Path | None = None
    if out_pdf is not None and _render_pdf(doc, out_pdf):
        pdf_written = out_pdf

    n_markers = len(refs)
    n_dangling = sum(1 for r in refs if r.ref is None)
    return ExportResult(
        html_path=out_html,
        pdf_path=pdf_written,
        references=refs,
        n_markers=n_markers,
        n_resolved=n_markers - n_dangling,
        n_dangling=n_dangling,
    )


__all__ = [
    "ExportResult",
    "collect_markers",
    "export_report",
    "render_references_markdown",
    "render_report_html",
]
