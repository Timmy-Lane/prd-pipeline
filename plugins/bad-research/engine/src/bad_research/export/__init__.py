"""Export formatters.

Render a final research report (markdown) to a shareable HTML/PDF artifact with a
RESOLVED References appendix — every bare `[N]` / `[[note-id]]` citation marker is
mapped to its source note's title/url from the owned vault (the auditable-grounding
moat made shareable). Keyless: stdlib + the in-repo `serve.renderer`; PDF reuses the
already-bundled `pymupdf`.
"""

from __future__ import annotations

from .html import (
    ExportResult,
    export_report,
    render_references_markdown,
    render_report_html,
)
from .refs import (
    ResolvedReference,
    SourceRef,
    collect_markers,
    resolve_references,
    source_refs_from_notes,
    source_refs_from_vault,
)

__all__ = [
    "ExportResult",
    "ResolvedReference",
    "SourceRef",
    "collect_markers",
    "export_report",
    "render_references_markdown",
    "render_report_html",
    "resolve_references",
    "source_refs_from_notes",
    "source_refs_from_vault",
]
