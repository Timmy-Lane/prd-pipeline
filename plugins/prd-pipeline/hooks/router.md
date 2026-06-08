You have **prd-pipeline** — the tier-adaptive path from idea to shipped code. Plugins can't auto-load rules, so this tiny router is injected each session; the full procedure lives in the `prd-pipeline` skill (load it with the Skill tool).

**Invoke `Skill(prd-pipeline)` BEFORE writing code whenever the task is to build, add, implement, or substantially change a feature or behavior.** It tier-routes:

- **T0** (bug fix · refactor w/ no behavior change · docs · dep bump · config) → no spec; just TDD + review.
- **T1** (small feature · single subsystem · reversible · <~8 files) → one-pager spec → 1 grill pass → **confirmed plan-gate** → build → verify.
- **T2** (new pipeline/behavior · new DB table/API/data source · cross-cutting · one-way door · moves user-visible outcomes) → full PRD → adversarial grill → architecture lock-in → **editable plan-gate** → parallel worktree build → verify → ship.

**The one rule: no non-trivial code touches disk before a human confirms the plan.** Unsure on tier → route up, write the spec.

prd-pipeline composes the bundled **compound-v** skills (`compound-v:brainstorming`, `writing-plans`, `batched-implementation`, `test-driven-development`, `verification-before-completion`, `finishing`, plus `critical-thinking` / `agent-security` / `recheck` / `startup-taste`) and the bundled **bad-research** engine for cited deep research — all installed together, nothing extra to fetch.
