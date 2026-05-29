# prd-pipeline

A portable, tier-adaptive **feature-development pipeline** for Claude Code: idea → spec/PRD → adversarial grill → confirmed plan → parallel worktree build → verified ship. Drops into any repo. Pure Skill + Agent + git — **no binary, no service, no dependency.**

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

## Parallel agents in git worktrees (you never switch branches)

- ≥2 independent tasks ⇒ one `Agent(isolation:"worktree")` each — its own worktree + branch under `.claude/worktrees/`, plan/memory/hooks attached to the worktree, not your repo.
- **Your working tree never moves.** The orchestrator `git merge`s each agent's branch back — never `git checkout` your tree.
- **Disjoint-file partition** (from the plan) makes merges conflict-free; cross-cutting edits serialize after the parallel block.
- **Cleanup is part of the task:** after merge, `git worktree remove` + delete the branch. 4–8 concurrent cap.

## Install

```bash
git clone <this-repo> ~/Documents/GitHub/prd-pipeline
~/Documents/GitHub/prd-pipeline/bin/prd install
```

`prd install` copies the skill into `~/.claude/skills/prd-pipeline/` and the always-on rule into `~/.claude/rules/common/feature-workflow.md`, then prints the one-line snippet to add to your global `~/.claude/CLAUDE.md` routing. Other commands: `prd update`, `prd uninstall`, `prd doctor`.

Then invoke it in any repo:

```
/prd-pipeline
```

It reads that repo's `CLAUDE.md` for the spec directory, template, "spec-required" triggers, project skills (grill/eng-review), and invariants — falling back to sane defaults when absent. **The project's `CLAUDE.md` always wins on conflict.**

## What's in here

```
skills/prd-pipeline/
  SKILL.md                      the orchestrator (the procedure)
  references/research-notes.md  cited best-practice synthesis (Google design docs,
                                Amazon PR-FAQ, Rust RFC, Oxide RFD, Shape Up, pre-mortem,
                                spec-kit/OpenSpec/BMAD, Claude Code worktrees)
  references/spec-template.md   the default spec/PRD template
rules/feature-workflow.md       the always-on global rule (gate + worktree mandate)
bin/prd                         install / update / uninstall / doctor
```

## Composes (doesn't reinvent)

`superpowers:brainstorming` → spec → grill (`deep-research` / `deep-researcher`, or the project's grill skill) → `superpowers:writing-plans` → `dispatching-parallel-agents` + `subagent-driven-development` + `test-driven-development` (in worktrees) → `verification-before-completion` → code/security review → `finishing-a-development-branch`.

## Credit

Process canon distilled from Google's *Design Docs*, Amazon's *Working Backwards* PR-FAQ, the Rust RFC + Oxide RFD lineage, Basecamp's *Shape Up*, Gary Klein's pre-mortem, and the spec-driven-development tools (GitHub spec-kit, OpenSpec, BMAD). Sources in `references/research-notes.md`. Orchestration architecture inspired by bad-research.

## License

MIT — see `LICENSE`.
