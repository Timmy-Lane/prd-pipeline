"""``bad install --codex`` — render the bad-research pipeline as a Codex skill.

Single source of truth: this reads the SAME step-skill ``.md`` files and agent
prompt constants the Claude installer uses (``core.hooks``), translates them to
Codex vocabulary via ``codex_translate``, and writes
``~/.codex/skills/bad-research/``.

Layout written::

    ~/.codex/skills/bad-research/
    |-- SKILL.md                       # router (Codex frontmatter + preamble + translated body)
    |-- agents/
    |   `-- openai.yaml                # Codex UI metadata
    `-- references/
        |-- <step>.md                  # one per hooks._BAD_RESEARCH_STEP_SKILLS entry
        |-- dispatch-table.md          # static stage -> agent map
        `-- agents/
            `-- <name>.md              # one per hooks.py *_AGENT constant (frontmatter kept)

The ``bad`` CLI core is untouched. AGENTS.md injection replaces the Claude
PreToolUse hook; ``multi_agent = true`` is set idempotently in config.toml.
"""

from __future__ import annotations

import re
from pathlib import Path

from bad_research.core import hooks
from bad_research.core.codex_translate import (
    agentref_path,
    skillref_path,
    strip_frontmatter,
    to_codex_skill_frontmatter,
    translate_tool_vocabulary,
)

# Subagent roster, single-sourced from hooks.py constants. The Codex filename
# is DERIVED from each agent's frontmatter `name:` (strip `bad-research-`), so
# `subagent_type: bad-research-X` references and the file written for that agent
# always agree — including the readability-recommender and the assumption
# critic. This mirrors the 17 _install_*_agent calls in
# hooks.install_global_hooks.
#
# Each tuple: (hooks constant name, render strategy). Strategies mirror the
# exact per-agent rendering the Claude installer uses so substance cannot drift.
_AGENT_RENDER: tuple[tuple[str, str], ...] = (
    ("RESEARCHER_AGENT", "format"),
    ("LOCI_ANALYST_AGENT", "format"),
    ("SOURCE_ANALYST_AGENT", "format"),
    ("DEPTH_INVESTIGATOR_AGENT", "format"),
    ("DIALECTIC_CRITIC_AGENT", "format"),
    ("DEPTH_CRITIC_AGENT", "format"),
    ("WIDTH_CRITIC_AGENT", "format"),
    ("INSTRUCTION_CRITIC_AGENT", "format"),  # no placeholder; harmless
    ("ASSUMPTION_CRITIC_AGENT", "format"),
    ("LIGHT_CRITIC_AGENT", "format"),
    ("CORPUS_CRITIC_AGENT", "replace"),       # uses .replace("{hpr_path}", ...)
    ("DRAFT_ORCHESTRATOR_AGENT", "replace"),  # uses .replace("{hpr_path}", ...)
    ("SYNTHESIZER_AGENT", "raw"),             # no placeholder
    ("PATCHER_AGENT", "raw"),                 # no placeholder
    ("POLISH_AUDITOR_AGENT", "polish"),       # uses {scaffold_only_sections}
    ("READABILITY_REFORMATTER_AGENT", "raw"), # no placeholder (recommender body)
    ("FRESH_REVIEWER_AGENT", "raw"),          # no placeholder
)

_NAME_RE = re.compile(r"^name:\s*(\S+)\s*$", re.MULTILINE)


def _render_agent(const_name: str, strategy: str, hpr_path: str) -> str:
    """Render one agent constant exactly as the Claude installer would."""
    raw: str = getattr(hooks, const_name)
    hpr_posix = hpr_path.replace("\\", "/")
    if strategy == "format":
        return raw.format(hpr_path=hpr_posix)
    if strategy == "replace":
        return raw.replace("{hpr_path}", hpr_posix)
    if strategy == "polish":
        return raw.format(
            scaffold_only_sections=hooks._render_scaffold_only_bullets(indent="- "),
        )
    # "raw"
    return raw


def _agent_filename(rendered: str, const_name: str) -> str:
    """Derive the Codex agent filename from the rendered frontmatter `name:`."""
    m = _NAME_RE.search(rendered)
    if not m:
        raise RuntimeError(f"{const_name}: no `name:` frontmatter line found")
    # agentref_path -> "references/agents/<slug>.md"; we want just the basename.
    return agentref_path(m.group(1)).rsplit("/", 1)[-1]


def build_agent_files(hpr_path: str = "bad") -> dict[str, str]:
    """Return ``{codex_filename: translated_agent_body}`` for all 17 agents.

    Frontmatter is KEPT on agent files (it carries the model / tool-lock hints
    the orchestrator must honor on Codex), but the body is tool-vocab translated.
    """
    out: dict[str, str] = {}
    for const_name, strategy in _AGENT_RENDER:
        rendered = _render_agent(const_name, strategy, hpr_path)
        filename = _agent_filename(rendered, const_name)
        out[filename] = translate_tool_vocabulary(rendered)
    return out


# Built once at import for cheap introspection (count assertions in tests).
AGENT_FILES: dict[str, str] = build_agent_files()


def read_codex_asset(name: str) -> str:
    """Read a static Codex asset from ``src/bad_research/skills/codex/``."""
    import importlib.resources

    try:
        return (
            importlib.resources.files("bad_research.skills.codex")
            .joinpath(name)
            .read_text(encoding="utf-8")
        )
    except Exception:
        path = Path(__file__).parent.parent / "skills" / "codex" / name
        return path.read_text(encoding="utf-8")


# --- filesystem writers -----------------------------------------------------


def _codex_skill_root(home: Path) -> Path:
    return home / ".codex" / "skills" / "bad-research"


def _write(path: Path, content: str, actions: list[str], label: str) -> None:
    """Write ``content`` to ``path`` only if changed; record the action."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    path.write_text(content, encoding="utf-8")
    actions.append(label)


def write_codex_skill(home: Path, hpr_path: str = "bad") -> list[str]:
    """Write ``~/.codex/skills/bad-research/`` (SKILL.md + references). Returns actions."""
    root = _codex_skill_root(home)
    refs = root / "references"
    agents = refs / "agents"
    agents.mkdir(parents=True, exist_ok=True)
    actions: list[str] = []

    # SKILL.md = Codex frontmatter + Codex preamble + translated router body.
    entry_src = hooks._read_skill_source("bad-research.md")
    if entry_src is None:
        raise RuntimeError("bad-research.md entry skill source missing")
    entry = to_codex_skill_frontmatter(entry_src)
    parts = entry.split("---\n", 2)  # ["", frontmatter, body]
    fm, body = parts[1], parts[2]
    preamble = read_codex_asset("router-preamble.md")
    skill_md = f"---\n{fm}---\n\n{preamble}\n\n{translate_tool_vocabulary(body)}"
    _write(root / "SKILL.md", skill_md, actions, "Codex: skills/bad-research/SKILL.md")

    # Step procedures -> references/<rest>.md (frontmatter stripped, vocab translated).
    for skill_name in hooks._BAD_RESEARCH_STEP_SKILLS:
        src = hooks._read_skill_source(f"{skill_name}.md")
        if src is None:
            continue
        rel = skillref_path(skill_name)  # references/<rest>.md
        content = translate_tool_vocabulary(strip_frontmatter(src))
        _write(root / rel, content, actions, f"Codex: {rel}")

    # Subagent prompts -> references/agents/<name>.md (frontmatter KEPT).
    for filename, content in build_agent_files(hpr_path).items():
        _write(agents / filename, content, actions, f"Codex: references/agents/{filename}")

    # Static dispatch table.
    _write(
        refs / "dispatch-table.md",
        read_codex_asset("dispatch-table.md"),
        actions,
        "Codex: references/dispatch-table.md",
    )

    return actions


_OPENAI_YAML = """\
display_name: Bad Research
short_description: Deep, multi-source, fully-cited research pipeline
default_prompt: Run deep research on the following question, with a fully-cited report
"""


def write_openai_yaml(home: Path) -> list[str]:
    """Write the Codex UI metadata file ``agents/openai.yaml``."""
    dest = _codex_skill_root(home) / "agents" / "openai.yaml"
    dest.parent.mkdir(parents=True, exist_ok=True)
    actions: list[str] = []
    _write(dest, _OPENAI_YAML, actions, "Codex: skills/bad-research/agents/openai.yaml")
    return actions


# --- AGENTS.md injection (replaces the Claude PreToolUse hook) ---------------

_AGENTS_MD_START = "<!-- bad-research:start -->"
_AGENTS_MD_END = "<!-- bad-research:end -->"

_AGENTS_MD_BLURB = """\
{start}
## Research Base (bad-research)

Deep-research pipeline available as the `bad-research` Codex skill. To run a
fully-cited research session, trigger that skill; its SKILL.md is the router and
the step procedures live in its `references/` directory.

**Prefer the vault over raw web access.** Before any raw web search/fetch on a
research topic, check the local research base and fetch through the CLI (this
carries the intent of the Claude PreToolUse hook, which Codex has no equivalent
for):

- `{hpr} search "<query>" --json` — search the vault first
- `{hpr} fetch "<url>" --json` — fetch sources (auto-extracts PDFs); do NOT use
  a raw web-fetch tool for source pages
- `{hpr} note show <id> --json` — read a stored note

The `bad` CLI is identical across platforms; run it through your shell tool.
{end}"""


def inject_codex_agents_md(home: Path, hpr_path: str = "bad") -> list[str]:
    """Inject the marker-delimited Research Base section into ``~/.codex/AGENTS.md``.

    Preserves existing content; replaces the marker section on re-run; never
    clobbers. Mirrors the Claude installer's CLAUDE.md injection contract.
    """
    hpr = hpr_path.replace("\\", "/")
    blurb = _AGENTS_MD_BLURB.format(start=_AGENTS_MD_START, end=_AGENTS_MD_END, hpr=hpr)
    target = home / ".codex" / "AGENTS.md"
    result = _inject_markered(target, blurb, _AGENTS_MD_START, _AGENTS_MD_END, "AGENTS.md")
    return [f"Codex: {result}"] if result else []


def _inject_markered(path: Path, blurb: str, start: str, end: str, label: str) -> str | None:
    """Marker-delimited section writer. Returns the action taken or None."""
    blurb = blurb.strip()
    if path.exists():
        content = path.read_text(encoding="utf-8-sig")
        if start in content:
            pat = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
            new = pat.sub(lambda _: blurb, content)
            if new != content:
                path.write_text(new, encoding="utf-8")
                return f"{label} (updated)"
            return None
        sep = "\n\n" if not content.endswith("\n") else "\n"
        path.write_text(content + sep + blurb + "\n", encoding="utf-8")
        return f"{label} (appended)"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {path.stem}\n" + blurb + "\n", encoding="utf-8")
    return f"{label} (created)"


# --- config.toml multi_agent flag -------------------------------------------


def ensure_multi_agent(home: Path) -> str | None:
    """Idempotently ensure ``[features] multi_agent = true`` in config.toml.

    Additive: never reorders or rewrites existing config. Returns the action
    taken, or ``None`` if the flag was already present.
    """
    path = home / ".codex" / "config.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if re.search(r"^\s*multi_agent\s*=\s*true", text, re.MULTILINE):
        return None
    if re.search(r"^\[features\]", text, re.MULTILINE):
        new = re.sub(
            r"^\[features\]\s*\n",
            "[features]\nmulti_agent = true\n",
            text,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        sep = "" if text.endswith("\n") or text == "" else "\n"
        new = text + sep + "\n[features]\nmulti_agent = true\n"
    path.write_text(new, encoding="utf-8")
    return "Codex: config.toml ([features] multi_agent = true)"


# --- top-level entrypoint ---------------------------------------------------


def install_codex(home: Path | None = None, hpr_path: str = "bad") -> list[str]:
    """Full Codex install: skill dir + references + openai.yaml + AGENTS.md + config.

    Idempotent: a second run with everything current returns ``[]``.
    """
    home = home or Path.home()
    actions: list[str] = []
    actions += write_codex_skill(home, hpr_path=hpr_path)
    actions += write_openai_yaml(home)
    actions += inject_codex_agents_md(home, hpr_path=hpr_path)
    cfg = ensure_multi_agent(home)
    if cfg:
        actions.append(cfg)
    return actions


__all__ = [
    "AGENT_FILES",
    "build_agent_files",
    "ensure_multi_agent",
    "inject_codex_agents_md",
    "install_codex",
    "read_codex_asset",
    "write_codex_skill",
    "write_openai_yaml",
]
