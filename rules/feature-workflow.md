# Feature Workflow (PRD-driven, plan-confirmed, parallel-worktree)

The default path for building anything non-trivial. Run it via the **`/prd-pipeline`** skill,
which sequences the phases and composes the skills below. **The project's own `CLAUDE.md`
overrides this where they conflict** (spec dir, template, triggers, invariants, project skills).

## The one rule
**No non-trivial code touches disk before a human confirms the plan.** Everything else serves this.

## Tier gate — does this need a spec/PRD?
- **No spec (T0):** bug fix · refactor with no behavior change · docs · dep bump · prompt/threshold tweak measured vs an existing eval · devops/CI. Just do it: TDD + code-review.
- **Light spec (T1):** small feature · single subsystem · mostly reversible · <~8 files. One-pager spec → 1 grill pass → confirmed plan → build → verify.
- **Full spec (T2):** new pipeline/behavior · new DB table/column · new public API or external data source · cross-cutting · **one-way (irreversible) door** · anything moving user-visible outcomes. Full PRD → adversarial grill → architecture lock-in → editable plan-gate → parallel worktree build → verify → ship.
- Unsure → **route up**, not reflexively to T2. Spec is required *before* implementation starts (human or AI). When in doubt, write the spec: two pages of intent prevents two weeks of rework.

## Plan-confirmation gate
Emit the plan (sub-tasks + per-task file scope + risks; **no time estimates**), then **pause for approve/edit/proceed.** Gate HARD on one-way-door / schema / public-API / outcome-moving changes; let reversible single-file changes flow with a one-line heads-up. Once confirmed: **disagree-and-commit** — stop re-arguing scope. Specs are append-only (`draft → accepted → implemented`; never delete; `superseded`/`abandoned` link forward).

## Parallel agents + git worktrees (mandatory for speed; you stay on your branch)
- **≥2 independent tasks ⇒ parallelize.** One agent per task, each `isolation: "worktree"` (Claude Code gives it its own worktree + branch under `.claude/worktrees/`; its plan/memory/hooks/transcript attach to the worktree, not your repo; auto-cleans if unchanged). Independent agents launch concurrently (multiple `Agent` calls in ONE message).
- **You NEVER switch branches.** Your working tree stays put on its current branch. The orchestrator `git merge`s each agent's branch back — never `git checkout` the user's tree.
- **Disjoint-file partition makes merges conflict-free.** Two agents must never edit the same file; cross-cutting edits (shared types, config, schema, build files, docs) serialize AFTER the parallel block, on your branch.
- **Cleanup is part of the task:** after merging a worktree branch, `git worktree remove` it and delete the merged branch — leftover locked worktrees pile up otherwise.
- **Ceiling 4–8 concurrent worktrees** — above that you're bottlenecked on review, not on Claude.
- Every spawned agent gets the 7-field contract: objective · inputs (incl. exact file scope) · output_shape · tools_allowed · stop_conditions · context · verification.

## Composes
`superpowers:brainstorming` (intent) → `/prd-pipeline` (spec + grill + plan-gate) → `deep-research` / `deep-researcher` (research + grill critics) → `superpowers:writing-plans` → `dispatching-parallel-agents` + `subagent-driven-development` + `test-driven-development` → `verification-before-completion` → `code-reviewer`/`security-reviewer` → `finishing-a-development-branch`.
