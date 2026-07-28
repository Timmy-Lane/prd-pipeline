# Feature Workflow (tier-adaptive, plan-confirmed, parallel-worktree)

The default path for building anything non-trivial. Run it via the **`/prd-pipeline`** skill,
which sequences the phases. **The project's own `CLAUDE.md` overrides this where they conflict** —
spec directory, template, triggers, invariants, and especially its documentation cap.

## The two rules
1. **No non-trivial code touches disk before a human confirms the plan.**
2. **A change produces at most one new document, and only when the tier earns it.**

## Route against the docs that already exist — before writing anything
Inventory what the repo already has (product intent · decisions/ADRs · change records · runbooks ·
API/CLI/config reference), then pick exactly one: **amend** the document that already owns this
surface · **supersede** the ADR this reverses · **create** one change file (T2 only) · **none**.
Then list every doc this change will make wrong — each becomes a task in the plan, not a follow-up.

## Tier gate — does this need a written spec?
- **T0 — no document:** bug fix · refactor with no behavior change · docs · dep bump · a threshold tweak measured against an existing test · devops/CI config. Just build it: test-first + review.
- **T1 — no document:** small feature · single subsystem · mostly reversible · under ~8 files. Spec and plan are emitted **in the conversation** and confirmed there; the durable record is the commit message.
- **T2 — one document:** new pipeline/behavior · new DB table or column · new public API or external data source · cross-cutting · **one-way door** · anything moving user-visible outcomes. One change file → consistency gate → adversarial grill → architecture lock-in → editable plan-gate → parallel worktree build → verify → ship.
- Unsure → **route up**, never reflexively to T2. Ceremony on a two-way door costs more than it protects.

## Plan-confirmation gate
Emit the plan (sub-tasks + per-task file scope + the docs it will update + risks; **no time
estimates**), then **pause for approve / edit / proceed.** Gate HARD on one-way-door, schema,
public-API, or outcome-moving changes; let a reversible single-file change flow with a one-line
heads-up. Once confirmed: **disagree and commit** — stop re-arguing scope. Change records are
append-only (`draft → accepted → implemented`; never deleted; `superseded`/`abandoned` link forward).

## Parallel agents + git worktrees (you stay on `main`, work auto-branches)
- **Always start from `main`.** A T1/T2 feature auto-creates its own feature branch in its own worktree — `main` stays clean and usable throughout. You never `git checkout`, never manually branch.
- **Two or more disjoint-file tasks ⇒ parallelize.** One `Agent(isolation:"worktree")` per task — its own worktree and branch; plan, memory and hooks attach to the worktree, not your repo; auto-cleans if unchanged. Launch independent agents concurrently, multiple `Agent` calls in ONE message.
- **Merge inward; touch `main` only at ship.** Sub-task branches merge into the feature branch as they finish; the feature branch lands on `main` only at the deliberate ship step.
- **The disjoint-file partition is what makes the inward merges conflict-free.** Two agents must never edit the same file; cross-cutting edits serialize AFTER the parallel block.
- **Cleanup is part of the task** — on success and on failure: `git worktree remove` and delete the branch, else locked worktrees pile up.
- **Ceiling 4–8 concurrent worktrees** — past that you are bottlenecked on review, not on the model.
- Every spawned agent gets the 7-field contract: objective · inputs (incl. exact file scope) · output_shape · tools_allowed · stop_conditions · context · verification.

## Before "done"
Run the real command and read its output — a typecheck or a green build is not verification.
Then walk the stale-doc list and confirm each one was actually updated. **A change that invalidates
documentation has not shipped until that documentation is updated.**
