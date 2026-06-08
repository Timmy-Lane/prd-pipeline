"""Code chunker: tree-sitter AST splits + NIA AST-header (dossier 04 §2, §3.1).

NIA's single biggest insight: before embedding a code chunk, walk the AST and
PREPEND a plain-text header so the embedder sees the call graph as tokens. The
header is for *embedding only* — `Chunk.text` stays a verbatim `note.body` slice
for provenance (Plan 06 grounding). `embed_text_for(chunk, note)` builds the
augmented string the store actually embeds.

[CORRECTION 2026-05-26] vs the plan's pure-Python `tree_sitter` API, verified
against the installed `tree-sitter-language-pack==1.8.1` (a Rust/PyO3 binding):
the node API is METHOD-based, not property-based, and uses `.kind()` not `.type`:
  - `parser.parse(code)` takes a `str` (NOT `code.encode()` bytes).
  - `tree.root_node()` is a method, not a property.
  - node accessors are callables: `node.kind()`, `node.child_count()`,
    `node.child(i)`, `node.start_byte()`, `node.end_byte()`,
    `node.child_by_field_name(name)`. There is no `.children` list and no `.type`.
  - byte offsets still align with str offsets for ASCII/UTF-8 source.
`_NodeView` below adapts BOTH the method-style (installed) and the legacy
property-style API so the chunker is robust across tree-sitter versions.
"""
from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from tree_sitter_language_pack import get_parser

from bad_research.models.note import Note
from bad_research.retrieval.base import Chunk
from bad_research.retrieval.chunker import make_chunk_id
from bad_research.retrieval.constants import CHUNK_BYTE_MIN

# Map common file extensions to tree-sitter-language-pack language names.
_EXT_LANG = {
    ".py": "python", ".js": "javascript", ".ts": "typescript", ".tsx": "tsx",
    ".jsx": "javascript", ".rs": "rust", ".go": "go", ".java": "java",
    ".c": "c", ".cpp": "cpp", ".cc": "cpp", ".rb": "ruby", ".php": "php",
}
# Node kinds that count as a top-level splittable definition, per language family.
_DEF_TYPES = {
    "function_definition", "function_declaration", "method_definition",
    "class_definition", "class_declaration", "function_item", "impl_item",
    "struct_item", "method_declaration", "arrow_function",
}
_BRANCH_TYPES = {"if_statement", "conditional_expression", "match", "match_statement",
                 "switch_statement", "case", "elif_clause", "else_clause", "match_arm"}
_LOOP_TYPES = {"for_statement", "while_statement", "for_in_statement",
               "do_statement", "loop_expression", "for_expression", "while_expression"}
_CALL_TYPES = {"call", "call_expression", "method_invocation", "macro_invocation"}
_IDENT_KINDS = ("identifier", "field_identifier")


def _call_or_value(obj: Any) -> Any:
    """Return obj() if it's a method, else obj — bridges the method-style Rust
    binding and the property-style pure-Python tree_sitter API."""
    return obj() if callable(obj) else obj


def _byte_to_char(src_bytes: bytes, byte_off: int) -> int:
    """Convert a tree-sitter UTF-8 *byte* offset into a *character* index into
    the decoded source. `Chunk.char_start`/`char_end` are char indices into
    `note.body` (INTERFACES.md), so the grounding verifier can slice
    `note.body[char_start:char_end] == chunk.text`. For multibyte source the
    byte offset is shifted vs the char index — decode the prefix to recover it."""
    return len(src_bytes[:byte_off].decode("utf-8", "replace"))


class _NodeView:
    """Uniform read-only view over a tree-sitter node regardless of binding."""

    __slots__ = ("_n",)

    def __init__(self, node: Any):
        self._n = node

    @property
    def kind(self) -> str:
        # method-style: .kind() ; property-style: .type
        n = self._n
        if hasattr(n, "kind"):
            return str(_call_or_value(n.kind))
        return str(_call_or_value(n.type))

    @property
    def start_byte(self) -> int:
        return int(_call_or_value(self._n.start_byte))

    @property
    def end_byte(self) -> int:
        return int(_call_or_value(self._n.end_byte))

    def child_count(self) -> int:
        return int(_call_or_value(self._n.child_count))

    def child(self, i: int) -> _NodeView:
        return _NodeView(self._n.child(i))

    def children(self) -> list[_NodeView]:
        return [self.child(i) for i in range(self.child_count())]

    def field(self, name: str) -> _NodeView | None:
        sub = self._n.child_by_field_name(name)
        return _NodeView(sub) if sub is not None else None


def _parse_root(code: str, language: str) -> _NodeView:
    parser = get_parser(language)
    tree = parser.parse(code)            # str input (binding-verified)
    root = _call_or_value(tree.root_node)  # type: ignore[union-attr]
    return _NodeView(root)


def _walk(node: _NodeView) -> Iterator[_NodeView]:
    yield node
    for child in node.children():
        yield from _walk(child)


def _call_names(root: _NodeView, src: bytes) -> list[str]:
    names: list[str] = []
    for n in _walk(root):
        if n.kind in _CALL_TYPES:
            fn = n.field("function")
            if fn is None and n.child_count():
                fn = n.child(0)
            ident = fn
            # Descend an attribute/member chain to the rightmost identifier.
            while (ident is not None and ident.kind not in _IDENT_KINDS
                   and ident.child_count()):
                ident = ident.child(ident.child_count() - 1)
            if ident is not None:
                txt = src[ident.start_byte:ident.end_byte].decode("utf-8", "replace")
                if txt and txt.isidentifier():
                    names.append(txt)
    # De-dup preserving order.
    seen: dict[str, None] = {}
    for x in names:
        seen.setdefault(x, None)
    return list(seen)


def _control_flow(root: _NodeView) -> tuple[int, int, int]:
    branches = loops = 0
    for n in _walk(root):
        if n.kind in _BRANCH_TYPES:
            branches += 1
        elif n.kind in _LOOP_TYPES:
            loops += 1
    complexity = branches + loops + 1  # cyclomatic-ish: decision points + 1
    return branches, loops, complexity


def ast_header(path_label: str, code: str, *, language: str) -> str:
    """Build the NIA verbatim AST header for a code chunk."""
    src = code.encode("utf-8")
    root = _parse_root(code, language)
    calls = _call_names(root, src)
    branches, loops, complexity = _control_flow(root)
    lines = [path_label]
    if calls:
        lines.append("Calls: " + ", ".join(calls))
    lines.append(f"Control flow: {branches} branches, {loops} loops, complexity {complexity}")
    return "\n".join(lines)


def _language_for(source_url: str) -> str:
    for ext, lang in _EXT_LANG.items():
        if source_url.endswith(ext) or source_url.endswith(ext + ".md"):
            return lang
    return "python"


def _path_label(note: Note) -> str:
    url = note.meta.source or note.path
    # "owner/repo/file" style: keep the last 3 path segments when it's a github blob URL.
    m = re.search(r"github\.com/([^/]+)/([^/]+)/blob/[^/]+/(.+)$", url)
    if m:
        return f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
    return url


def chunk_code_note(note: Note) -> list[Chunk]:
    body = note.body
    url = note.meta.source or note.path
    if len(body.encode()) < CHUNK_BYTE_MIN:
        return [Chunk(chunk_id=make_chunk_id(url, note.meta.title or "_0"),
                      note_id=note.meta.id, text=body, char_start=0, char_end=len(body),
                      score=0.0, source_id="")]
    language = _language_for(url)
    src = body.encode("utf-8")
    root = _parse_root(body, language)
    # Top-level definitions become chunk boundaries (zero overlap, clean AST cuts).
    defs = [c for c in root.children() if c.kind in _DEF_TYPES]
    if not defs:
        return [Chunk(chunk_id=make_chunk_id(url, note.meta.title or "_0"),
                      note_id=note.meta.id, text=body, char_start=0, char_end=len(body),
                      score=0.0, source_id="")]
    chunks: list[Chunk] = []
    for idx, d in enumerate(defs):
        bstart, bend = d.start_byte, d.end_byte
        # Slice `.text` from BYTE offsets (correct), but store CHARACTER offsets
        # so `note.body[char_start:char_end] == text` holds for multibyte source.
        text = src[bstart:bend].decode("utf-8", "replace")
        name = ""
        nm = d.field("name")
        if nm is not None:
            name = src[nm.start_byte:nm.end_byte].decode("utf-8", "replace")
        cid = make_chunk_id(url, name or f"_{idx}")
        chunks.append(Chunk(chunk_id=cid, note_id=note.meta.id, text=text,
                            char_start=_byte_to_char(src, bstart),
                            char_end=_byte_to_char(src, bend), score=0.0, source_id=""))
    return chunks


def embed_text_for(chunk: Chunk, note: Note) -> str:
    """The augmented string the store embeds: header + blank line + raw code.
    Chunk.text stays the verbatim provenance slice."""
    language = _language_for(note.meta.source or note.path)
    header = ast_header(_path_label(note), chunk.text, language=language)
    return f"{header}\n\n{chunk.text}"
