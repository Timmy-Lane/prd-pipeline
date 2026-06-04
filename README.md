# prd-pipeline

A portable, tier-adaptive **feature-development pipeline** for Claude Code: idea → spec/PRD → adversarial grill → confirmed plan → parallel worktree build → verified ship. Drops into any repo. Pure Skill + Agent + git — **no binary, no service, no runtime dependency.**

Inspired by the *architecture* of [bad-research](https://github.com/LeventySeven/badresearch) (tier routing, an editable plan-gate, adversarial critic fan-out, a compaction-resistant skill, a strict subagent contract) — but it composes Claude Code's native skills and git worktrees instead of shipping its own engine.

## The one rule

**No non-trivial code touches disk before a human confirms the plan.** Everything else serves that.

## Tier routing — a spec only when it earns its keep

| Tier | Trigger | Pipeline |
|---|---|---|
| **T0 — no spec** | Bug fix · refactor (no behavior change) · docs · dep bump · prompt/threshold tweak vs an existing eval · devops/CI. Two-way door, solution obvious. | Just build it: TDD + code-review. |
| **T1 — light spec** | Small feature · single subsystem · mostly reversible · <~8 files. | One-pager spec → 1 grill pass → confirmed plan → build → verify. |
| **T2 — full spec** | New pipeline/behavior · new DB table/column · new public API or data source · cross-cutting · **one-way (irreversible) door** · anything moving user-visible outcomes. | Full PRD → adversarial grill (parallel critics + pre-mortem) → architecture lock-in (disjoint-file task partition) → **editable plan-gate** → parallel worktree build → verify → ship. |

Unsure → route up, never reflexively to T2.

## Parallel agents in git worktrees — you stay on `main`, work auto-branches

- **Always start from `main`.** For a feature, the pipeline auto-creates an independent feature branch in its own git worktree and works there — `main` stays clean and usable the whole time. You never `git checkout`, never manually branch.
- **≥2 independent sub-tasks ⇒ parallelize.** One `Agent(isolation:"worktree")` per task — its own worktree+branch; plan/memory/hooks attach to the worktree, not your repo; auto-cleans if unchanged.
- **Merge inward; touch `main` only at ship.** Sub-task branches merge into the feature branch (disjoint-file partition = conflict-free); the feature branch lands on `main` only at the deliberate ship step. `main` is never half-built.
- **Cleanup is part of the task** — after merge, `git worktree remove` + delete the branch. 4–8 concurrent cap.

## Install

**Recommended (review-then-install):**

```bash
git clone https://github.com/Timmy-Lane/prd-pipeline ~/.prd-pipeline
less ~/.prd-pipeline/bin/prd ~/.prd-pipeline/install.sh   # inspect before running
~/.prd-pipeline/bin/prd install
```

**One-liner** (only do this if you trust the source — it runs a script from the internet):

```bash
curl -fsSL https://raw.githubusercontent.com/Timmy-Lane/prd-pipeline/main/install.sh | bash
```

`prd install` is idempotent and:
- copies the skill → `~/.claude/skills/prd-pipeline/` (invoke with `/prd-pipeline`),
- copies the rule → `~/.claude/rules/common/feature-workflow.md` (auto-loads every session),
- inserts/refreshes a **managed block** in `~/.claude/CLAUDE.md` (between `<!-- prd-pipeline:start -->` markers — and skips if you've already wired it by hand),
- symlinks `prd` onto `~/.local/bin`,
- runs a **dependency check** (see below).

| Command | Does |
|---|---|
| `prd install` | global install (above) |
| `prd install --project DIR` | install just the skill into `DIR/.claude/skills/` (commit it with the repo) |
| `prd update` | `git pull --ff-only` (if a clone) + reinstall |
| `prd update --check` | report whether a newer release tag exists — **no pull, no mutation** |
| `prd uninstall` | remove skill, rule, managed CLAUDE.md block, and the `prd` symlink |
| `prd doctor` | show install status + dependency check + versions (clone vs installed, warns on drift) |
| `prd version` | print the prd-pipeline version |
| `prd notify on` / `off` / `status` | **opt-in** SessionStart update nudge (default off; ≤ 1 network check/day, cached) |
| `prd new <topic>` | scaffold `docs/specs/NNNN-<topic>.md` from the skill's spec template |
| `prd list [--status S]` | list specs in `docs/specs/` (id · title · status) with a count summary header; `--status` filters the rows |
| `prd audit [--fix] [--json] [--stale-days N]` | check spec-lifecycle consistency (read-only). Flags missing/invalid `status`, dup/mismatched `id`, broken `supersedes` links, git desync (a `feat/NNNN-*` branch still at `draft`/`accepted`), and stale drafts. `--fix` applies only the one safe metadata fix (missing `status:` → `draft`, prompted) — **never deletes, renames, or moves a spec**. Exits non-zero on any ERROR (CI-friendly) |

## Dependencies (checked by `prd doctor` and at runtime)

The skill **composes** other skills and degrades gracefully when they're absent — but `prd doctor` (and the skill's own Step-0 preflight) report what's present:

- **git** — *required* (the worktree build needs it).
- **superpowers** plugin — strongly recommended (brainstorming · writing-plans · dispatching-parallel-agents · TDD · verification · finishing-a-branch). Missing → built-in inline fallbacks.
- **deep-research** skill — research/grill engine. Missing → falls back to a `deep-researcher` agent / web tools.

## What's in here

```
skills/prd-pipeline/
  SKILL.md                      the orchestrator (the procedure)
  references/research-notes.md  cited best-practice synthesis (Google design docs, Amazon
                                PR-FAQ, Rust RFC, Oxide RFD, Shape Up, pre-mortem, spec-kit)
  references/spec-template.md   the default spec/PRD template
rules/feature-workflow.md       the always-on rule (gate + worktree mandate)
bin/prd                         install / update[--check] / uninstall / doctor / version / notify / new / list
VERSION                         single source of truth for the version (releases are git tags vX.Y.Z)
install.sh                      bootstrap (clone + install)
```

## Security / trust

- **No telemetry, no phone-home, no third-party downloads, no data ever sent.** Network operations are limited to `git clone` / `git pull` of *this* repo over HTTPS (pinned in `install.sh`; the `PRD_REPO_URL` override is asserted to be `https://`) — **plus**, *only if you opt in with `prd notify on`*, a read-only `git ls-remote --tags` against the **same** repo (at most once/day, cached on disk; it sends no data and talks to no third party). A default install makes **no** `settings.json` edits and **no** network calls. Reviewed for malware/exfiltration — clean.
- `bin/prd` only writes under `~/.claude` + `~/.local/bin`. It edits a clearly-marked managed block in `CLAUDE.md` (atomic write, skips if the end-marker is missing to avoid truncation). `prd notify on` adds an opt-in SessionStart hook to `~/.claude/settings.json` — parsed-or-aborted (a malformed file is left untouched), written atomically, and removed cleanly by `prd notify off` (your other hooks are preserved). It never uses `eval` or executes downloaded content beyond this repo's own `bin/prd`.
- Prefer the **clone-then-inspect** install over `curl | bash`. Pin to a tagged release if you want a frozen version.

## Composes (doesn't reinvent)

`superpowers:brainstorming` → spec → grill (`deep-research` / `deep-researcher`, or the project's grill skill) → `superpowers:writing-plans` → `dispatching-parallel-agents` + `subagent-driven-development` + `test-driven-development` (in worktrees) → `verification-before-completion` → code/security review → `finishing-a-development-branch`.

## Credit

Process canon distilled from Google's *Design Docs*, Amazon's *Working Backwards* PR-FAQ, the Rust RFC + Oxide RFD lineage, Basecamp's *Shape Up*, Gary Klein's pre-mortem, and spec-driven-development tools (GitHub spec-kit, OpenSpec, BMAD). Sources in `references/research-notes.md`. Orchestration architecture inspired by bad-research.

## License

MIT — see `LICENSE`.
