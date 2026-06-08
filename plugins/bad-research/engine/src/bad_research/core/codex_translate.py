"""Translate Claude Code skill/agent sources into Codex equivalents.

Pure functions only — no filesystem side effects. The Codex installer
(``codex_install.py``) composes these to render the skill directory.

The translation is a deterministic substitution layer, NOT free-form prose
rewriting:

1. ``Skill(skill: "bad-research-N-...")`` -> "read ``references/N-....md``"
2. ``Task(`` -> ``spawn_agent(`` and ``subagent_type: bad-research-X`` ->
   ``agent: references/agents/X.md`` (the inline-prompt source for that agent)
3. ``TodoWrite`` -> ``update_plan``
4. Claude install-surface paths (``.claude/skills/...`` etc.) -> Codex paths
5. ``to_codex_skill_frontmatter`` strips a Claude skill's frontmatter down to
   ``name`` + ``description`` (Codex SKILL.md rule); ``strip_frontmatter``
   removes it entirely (reference docs need no frontmatter).

Every public function is idempotent: running it on already-translated text is a
no-op, because the output contains none of the source tokens.
"""

from __future__ import annotations

import re

import yaml  # type: ignore[import-untyped]

_SKILL_PREFIX = "bad-research-"

# The entry skill's own slug (no trailing ``-<step>`` segment). A self-reinvoke
# ``Skill(skill: "bad-research")`` must point back at THIS skill's ``SKILL.md``,
# NOT at a nonexistent ``references/bad-research.md``.
_ENTRY_SKILL = "bad-research"


def skillref_path(skill_name: str) -> str:
    """``bad-research-5-depth-investigation`` -> ``references/5-depth-investigation.md``.

    Strips the ``bad-research-`` prefix and places the remainder under
    ``references/``. Used for both step procedures and (via ``agentref_path``)
    subagent prompts.
    """
    rest = skill_name[len(_SKILL_PREFIX):] if skill_name.startswith(_SKILL_PREFIX) else skill_name
    return f"references/{rest}.md"


def agentref_path(agent_name: str) -> str:
    """``bad-research-fetcher`` -> ``references/agents/fetcher.md``.

    The Codex filename for a subagent is its Claude frontmatter ``name:`` with
    the ``bad-research-`` prefix stripped. Deriving it this way (rather than a
    hardcoded table) guarantees ``subagent_type: bad-research-X`` and the file
    written for that agent always agree, even for the readability-recommender
    (whose name differs from the historical "reformatter" label).
    """
    rest = agent_name[len(_SKILL_PREFIX):] if agent_name.startswith(_SKILL_PREFIX) else agent_name
    return f"references/agents/{rest}.md"


# --- tool-vocabulary substitution ------------------------------------------


def _skillref_for(skill_name: str) -> str:
    """Codex target for a `Skill(skill: "...")` call or `.claude/skills/...` path.

    The entry skill (``bad-research``, no step segment) is its OWN ``SKILL.md``,
    so a self-reinvoke points back at this file rather than a dangling
    ``references/bad-research.md``. Every other (step) skill goes through
    ``skillref_path``.
    """
    if skill_name == _ENTRY_SKILL:
        return "SKILL.md"
    return skillref_path(skill_name)


# Run FIRST: the explicit `.claude/skills/bad-research-<step>/SKILL.md` install
# path. Routed through `skillref_path` so it lands on the REAL rendered
# reference filename (`references/<step>.md`) — NOT the dangling
# `references/bad-research-<step>/SKILL.md` the bare `.claude/skills/` literal
# would have produced. Must precede that literal (below) and the bare-path
# fallbacks. The entry-skill path (`.claude/skills/bad-research/SKILL.md`, no
# step segment) maps to this skill's own `SKILL.md`.
_CLAUDE_SKILL_PATH_RE = re.compile(
    r'\.claude/skills/(' + re.escape(_SKILL_PREFIX[:-1]) + r'[\w.-]*)/SKILL\.md'
)

# Run NEXT: the structured Skill(...) call. Tolerates `skill:` / `skill =`
# spacing and single/double quotes. Consumes the whole call into a file-read
# instruction. The entry self-reinvoke `Skill(skill: "bad-research")` resolves
# to this skill's own SKILL.md.
_SKILL_CALL_RE = re.compile(r'Skill\(\s*skill\s*[:=]\s*["\']([^"\']+)["\']\s*\)')

# Run NEXT: a `subagent_type: bad-research-X` line (the multi-line Task(...)
# form the skills use). Rewrites to `agent: references/agents/X.md`. Tolerates
# `:` or `=` and surrounding whitespace; captures the agent slug.
_SUBAGENT_TYPE_RE = re.compile(r'subagent_type\s*[:=]\s*(' + re.escape(_SKILL_PREFIX) + r'[\w.-]+)')

# Literal substitutions applied after the regexes. Order matters — longer /
# more-specific forms first so a later short form can't pre-empt them.
_LITERAL_SUBS: tuple[tuple[str, str], ...] = (
    # Claude install-surface paths -> Codex layout. Specific dirs before the
    # bare `.claude/` catch-all.
    (".claude/skills/", "references/"),
    (".claude/agents/", "references/agents/"),
    (".claude/settings.json", ".codex/config.toml"),
    (".claude/", ".codex/"),
    # The lazy step-skill bootstrap does not exist on Codex (procedures are
    # bundled). Neutralise the command AND the `--steps-only` token so the
    # orchestrator doesn't try it (and the leak-lint stays clean of the flag).
    ("bad install --steps-only . --json", "(no-op on Codex — step procedures are bundled here)"),
    ("bad install --steps-only .", "(no-op on Codex — step procedures are bundled here)"),
    ("bad install --steps-only", "(no-op on Codex — step procedures are bundled here)"),
    ("--steps-only", "(no-op on Codex — step procedures are bundled here)"),
    # Claude-only hook / slash-command vocabulary with no Codex equivalent. The
    # PreToolUse vault-check is carried by the AGENTS.md "prefer the vault"
    # section; the `/bad-research` slash command is just "this skill" on Codex.
    ("PreToolUse hook", "prefer-the-vault guidance in AGENTS.md"),
    ("PreToolUse", "prefer-the-vault guidance in AGENTS.md"),
    ("`/bad-research`", "this `bad-research` skill"),
    ("/bad-research", "this bad-research skill"),
    # Subagent dispatch tool.
    ("the Task tool", "the spawn_agent tool"),
    ("Task tool", "spawn_agent tool"),
    ("Task call", "spawn_agent call"),
    ("Task(", "spawn_agent("),
    # Any residual bare `subagent_type` token (e.g. in prose) -> `agent`.
    ("subagent_type", "agent"),
    # Task tracking.
    ("TodoWrite", "update_plan"),
    # Skill-loader phrasing.
    ("the Skill tool", "the file-read tool"),
    ("Skill tool", "file-read tool"),
    # Model phrasing (the orchestrator-as-Opus framing).
    ("orchestrator (Opus)", "orchestrator"),
    ("(Opus)", ""),
)


def translate_tool_vocabulary(text: str) -> str:
    """Rewrite Claude Code tool references into Codex equivalents.

    Idempotent: the output contains none of the source tokens, so a second
    pass is a no-op.
    """
    # .claude/skills/bad-research-<step>/SKILL.md -> the REAL rendered ref path.
    # MUST precede the `.claude/skills/` literal so the path is routed through
    # `skillref_path` instead of becoming a dangling `references/<dir>/SKILL.md`.
    # Emits the bare path (any surrounding `backticks` in the source are kept).
    text = _CLAUDE_SKILL_PATH_RE.sub(lambda m: _skillref_for(m.group(1)), text)
    # Skill(skill: "bad-research-N-...") -> read `references/N-....md`
    # (entry self-reinvoke `bad-research` -> this skill's own SKILL.md).
    text = _SKILL_CALL_RE.sub(lambda m: f"read `{_skillref_for(m.group(1))}`", text)
    # subagent_type: bad-research-X -> agent: references/agents/X.md
    text = _SUBAGENT_TYPE_RE.sub(lambda m: f"agent: {agentref_path(m.group(1))}", text)
    # Literal token substitutions.
    for old, new in _LITERAL_SUBS:
        text = text.replace(old, new)
    return text


# --- frontmatter handling ---------------------------------------------------

_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)


def _split_frontmatter(text: str) -> tuple[str | None, str]:
    """Return ``(frontmatter_block_without_fences, body)``.

    ``frontmatter`` is ``None`` if the text has no leading ``---`` block.
    """
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    return m.group(1), text[m.end():]


def _extract_field(fm: str, field: str) -> str | None:
    """Extract a scalar or folded (``>``) YAML field from a frontmatter block.

    Handles both ``field: value`` and the folded/literal block form::

        field: >
          line one
          line two

    Returns the value folded to a single space-joined line, or ``None`` if the
    field is absent.
    """
    lines = fm.splitlines()
    for i, line in enumerate(lines):
        if not line.startswith(f"{field}:"):
            continue
        rest = line[len(field) + 1:].strip()
        if rest and rest not in (">", "|", ">-", "|-", ">+", "|+"):
            return rest
        # Folded/literal block: collect subsequent more-indented lines.
        collected: list[str] = []
        for cont in lines[i + 1:]:
            if cont.strip() == "":
                continue
            if not cont.startswith((" ", "\t")):
                break
            collected.append(cont.strip())
        return " ".join(collected) if collected else None
    return None


def to_codex_skill_frontmatter(text: str) -> str:
    """Rewrite a Claude skill's frontmatter to Codex-valid (``name`` + ``description``).

    Strips every other field (``user-invocable``, ``color``, ``model``,
    ``tools``, ...). If the text has no frontmatter, it is returned unchanged.

    The two retained scalars are emitted via ``yaml.safe_dump`` so the result is
    ALWAYS valid YAML for ANY value — including descriptions that contain ``: ``
    (the folded entry-skill description does), quotes, ``#``, or newlines.
    Hand-formatting ``key: value`` broke on the embedded ``: `` and produced a
    frontmatter that ``yaml.safe_load`` rejected with "mapping values are not
    allowed here".
    """
    fm, body = _split_frontmatter(text)
    if fm is None:
        return text
    name = _extract_field(fm, "name") or "bad-research"
    description = _extract_field(fm, "description") or ""
    dumped = yaml.safe_dump(
        {"name": name, "description": description},
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=10**9,  # keep each scalar on a single line (no wrap-folding)
    )
    return f"---\n{dumped}---\n" + body


def strip_frontmatter(text: str) -> str:
    """Remove a leading YAML frontmatter block entirely (for reference docs)."""
    _, body = _split_frontmatter(text)
    return body
