---
name: prd-pipeline
description: >
  Use when building, adding, implementing, or substantially changing a feature or
  behavior — the end-to-end path from idea to shipped code. Tier-adaptive: a trivial
  change skips straight to TDD + review; a small feature gets a one-pager spec, a
  single grill pass, and a confirmed plan; a large or irreversible change gets a full
  PRD, an adversarial grill, an architecture lock-in, an editable plan-gate, and a
  parallel worktree build. Enforces: no non-trivial code without a confirmed spec +
  plan, parallel agents in isolated git worktrees (you never switch branches), and
  verification before "done". Composes brainstorming, deep-research, the project's
  grill/eng-review, parallel-agent dispatch, TDD, and verification skills.
---

# prd-pipeline — idea → spec → confirmed plan → parallel build → verified ship

You are the **orchestrator**. You sequence the phases below; the heavy lifting is done by
composed skills and subagents. You do NOT write production code yourself during a Tier-2
run — you route disjoint tasks to worktree-isolated agents and merge their work back.

This skill encodes one rule above all: **for anything non-trivial, a human confirms the
plan before code touches disk.** Everything else serves that.

> Reference (the *why*, with sources): `references/research-notes.md`. Default spec
> template: `references/spec-template.md`. Read those only if you need the rationale or
> a template — this file is the operational procedure.

---

## Step 0 — Load project context + seed todos (always)

1. **Read the project's `CLAUDE.md`** (repo root). Extract, with fallbacks:
   - **Spec directory + template** — where specs/PRDs live (e.g. `docs/prd/`, `docs/rfd/`,
     `docs/specs/`) and the template path. *Fallback:* `docs/specs/NNNN-kebab-title.md` +
     this skill's `references/spec-template.md`.
   - **"Spec-required" triggers** — the project's list of what mandates a spec.
     *Fallback:* the universal list in Step 1.
   - **Project-specific skills** — a project grill skill (e.g. `grill-prd`) and an
     architecture-review skill (e.g. `eng-review`). *Fallback:* the built-in grill (Step 3)
     and `Agent(subagent_type: Plan)` (Step 4).
   - **Project invariants** — display conventions, config-vs-env rules, category lists,
     read-only DBs, etc. Carry these into the spec and the grill lenses.
   - **Research engine** — the project may pin one. *Fallback:* `Skill(deep-research)` for
     synthesis and `Agent(subagent_type: deep-researcher)` for grill critics.
2. **Classify the tier** (Step 1) from the user's request.
3. **Seed `TodoWrite`** with the phases for the chosen tier, in order. The todo list is
   your durable memory — it survives context compaction. Re-read this file and the spec
   file if you wake up unsure where you are.

---

## Step 1 — Tier routing (decide once, up front)

Borrowed from Google's "warranted when 3+ ambiguity answers are yes" + Bezos one-way/two-way
doors + bad-research's route table. **Respect the tier — don't add ceremony to a fix; don't
skip the gate on a one-way door.**

| Tier | Trigger | Pipeline |
|---|---|---|
| **T0 — no spec** | Bug fix · refactor with no behavior change · docs · dep bump · prompt/threshold tweak measured against an existing eval · devops/CI. Two-way door, solution obvious. | Skip to **Step 5** (implement) → **Step 6** (verify) → review. No spec, no gate. Exit fast. |
| **T1 — light spec** | Small feature · single subsystem · mostly reversible · < ~8 files, ≤2 new components. | Step 2 (one-pager spec) → Step 3 (single grill pass) → Step 4 (plan, lightweight) → **plan-gate** → Step 5 → Step 6 → ship. |
| **T2 — full spec** | New pipeline/behavior · new DB table or column · new public API/endpoint · new external data source · cross-cutting change · **one-way door** · anything that moves user-visible outcomes. | Step 2 (full PRD) → Step 3 (adversarial grill) → Step 4 (architecture lock-in) → **editable plan-gate** → Step 5 (parallel worktree build) → Step 6 → ship. |

If unsure between two tiers, **route up** — but never silently upgrade every change to T2.
State the tier and one-line reason before proceeding.

---

## Step 2 — Spec (T1/T2)

Run `Skill(superpowers:brainstorming)` first if intent/requirements are not already crisp
(creating features ⇒ brainstorm before writing). Then write the spec to the project's spec
directory at `status: draft`, using the project template (fallback: `references/spec-template.md`).

Synthesized section skeleton (bold = always; rest = when relevant): **Problem/Context**,
**Goals & Non-Goals**, customer-framing (working-backwards, 1 paragraph), **Proposed
solution + trade-offs**, metric delta / success criteria, alternatives considered,
cross-cutting concerns (security/privacy/observability/cost/data), **Drawbacks / risks /
hypothesis-invalidators** (observable conditions that mean *roll back*), **Wedge** (narrowest
valuable slice), open questions. **Prose, not bullets** (writing forces precision). **Fits ~2
pages or it's too broad — split it.** A spec with no "alternatives considered" wasn't designed.

For T1 the spec is a one-pager (Problem · Goals/Non-Goals · Wedge · Success criteria · Risks).

---

## Step 3 — Grill (adversarial review of the spec)

Find problems; do NOT propose fixes (that's Step 4). Use the project grill skill if present
(e.g. `Skill(grill-prd)`); otherwise run the built-in grill:

- **T1:** ONE critic pass (`Agent(subagent_type: deep-researcher)`) over the spec, covering
  edge cases + invalidator-measurability + one pre-mortem question.
- **T2:** **3–4 critics IN PARALLEL** (one message, multiple `Agent` calls), each a distinct
  lens — redundant critics hide failure modes, diverse lenses surface them:
  1. **Architecture/conflict** — contradicts an existing decision (ADR)? duplicates shipped
     scope? inconsistent with how the system works today? violates a project invariant?
  2. **Edge-case/invalidator** — invalidators named but not measurable? success criteria
     with no measurement plan? null/empty/race/restart/partial-failure/rate-limit/cap-exhaustion?
  3. **Cost/ops/telemetry** — cost math shown? operator knobs in the right place (config vs
     env)? telemetry to query it later? backwards-compat for existing data?
  4. **Pre-mortem** — "it's a year later and this shipped and failed: list the causes." (+30%
     risk identification; Klein/HBR.)

Each critic gets the **7-field subagent contract** (see Step 5). Aggregate findings into 3
buckets: **(1) must-fix before `accepted`**, (2) open-question (record in the spec), (3)
acknowledge-and-accept (record in anti-goals/out-of-scope). **Exit criterion: bucket 1 is
empty.** Until then the spec stays `draft`.

For deep external/literature questions a critic surfaces, escalate to `Skill(deep-research)`.

---

## Step 4 — Plan / architecture lock-in (T1/T2)

Produce the implementation plan. For T2 use the project architecture-review skill if present
(e.g. `Skill(eng-review)`), else `Agent(subagent_type: Plan)` with this requirement:

> "Lock the architecture for `<spec>`: data flow, file boundaries, edge cases, test coverage.
> Output an **ordered task list where each task touches DISJOINT files** so parallel agents
> don't collide. Cross-cutting edits (shared types, config, schema, build files, CLAUDE.md,
> docs) **serialize after** the parallel block."

The plan MUST have: disjoint-file task partition · ordered phases with named dependencies ·
test plan (the commands the reviewer runs) · rollback/reversibility · risks + blast radius.
Right-size the diff — smallest change that cleanly expresses the intent, but don't compress a
necessary rewrite into a patch.

### The plan-gate (the one human gate that matters) — MANDATORY for T2, recommended for T1
**Emit the plan** (sub-tasks + per-task file scope + risks; **no time estimates**) and **PAUSE for
approve / edit / proceed.** No code touches disk before approval.
- **Gate HARD** on one-way-door / cross-cutting / schema / public-API / outcome-moving changes.
- Let two-way-door, reversible, single-file changes flow with a one-line heads-up.
- On `accepted`, set the spec `status: accepted` and record the decision (one line) in the
  spec. **Disagree-and-commit: once confirmed, stop re-arguing scope.**

---

## Step 5 — Implement (parallel, worktree-isolated)

**The mandate: you stay on `main`; the work auto-branches into isolated git worktrees; you
(and the user) NEVER switch branches and `main` is never left half-built.** Git worktrees solve
the file-conflict problem completely — they are the enabling technique for parallel AI development.

**Always start from `main`.** For a T1/T2 feature, FIRST auto-create an independent feature
branch in its own worktree and do all the work there — `main` stays clean and usable the whole
time. The user never `git checkout`s, never manually branches, never gets pulled off `main`.

- **≥2 disjoint-file tasks ⇒ parallelize.** Spawn one `Agent` per task **with
  `isolation: "worktree"`** (Claude Code spins a fresh worktree + dedicated branch under
  `.claude/worktrees/`, attaches that agent's plan/memory/hooks/transcript to the worktree —
  not the user's repo — and auto-cleans if unchanged). Run independent agents concurrently
  (multiple `Agent` calls in ONE message); or use `Skill(superpowers:dispatching-parallel-agents)`
  + `Skill(superpowers:subagent-driven-development)`.
- **Merge inward; touch `main` only at ship.** Sub-task branches `git merge` into the **feature
  branch** as they finish (disjoint-file partition from Step 4 makes this conflict-free). The
  feature branch lands on `main` ONLY at the deliberate ship step (Step 6) — never continuously,
  so `main` is never half-built. The orchestrator never `git checkout`s the user's tree.
- **Each task does TDD** (`Skill(superpowers:test-driven-development)`): test first (RED) →
  minimal impl (GREEN) → refactor.
- **Cleanup is part of the task.** After merging a worktree branch, `git worktree remove` it
  and delete the merged branch — leftover locked worktrees pile up otherwise.
- **Concurrency ceiling: 4–8 worktrees.** Above that you're bottlenecked on review, not on
  Claude. Cross-cutting edits run serially AFTER the parallel block, on the user's branch.

**7-field subagent contract** — every spawned `Agent` prompt MUST include, near the top:
`objective` (one self-contained sentence) · `inputs` (spec path, task's exact file scope,
branch) · `output_shape` (what to return) · `tools_allowed` · `stop_conditions` · `context`
(relevant project invariants) · `verification` (the test/command that proves the task done — and
the agent must **commit its work on its worktree branch before returning**, else there is nothing
to merge back).

T0: a single trivial change can go directly on `main` (TDD + review), no worktree fan-out — or
its own throwaway branch if you want PR hygiene. Anything bigger gets the feature-branch worktree above.

---

## Step 6 — Verify, review, ship

1. **Verify before claiming done** — `Skill(superpowers:verification-before-completion)`.
   Run the test plan's commands, confirm output. Evidence before assertions. For pipeline /
   agent / behavior changes, run the project's real-run check (the project CLAUDE.md names it).
2. **Auto code review** — `code-reviewer` (every diff) · `typescript-reviewer` (TS) ·
   `security-reviewer` (auth/keys/payments/external input) · `database-reviewer` (schema/SQL).
3. **Re-anchor to the spec** — does what shipped match the confirmed plan? Flag any drift.
4. **Mark `status: implemented`** in the spec; it stays as the record of what was decided and why.
5. **Ship** — `Skill(superpowers:finishing-a-development-branch)` → integrate the feature branch
   into `main` (merge or PR) per the project's git convention (PRs only when asked), then prune
   its worktree. This is the ONLY moment `main` changes.

---

## Invariants (cannot break)

1. **No non-trivial code without a confirmed plan.** The plan-gate is mandatory for T2 and
   the default for T1. Skipping it is the single most damaging failure mode.
2. **Specs are append-only.** `draft → accepted → implemented`; killed → `abandoned`; changed
   → `superseded` (link forward). Never delete a spec.
3. **Parallel tasks touch disjoint files.** Two agents editing the same file = collision.
   Cross-cutting edits serialize after the parallel block.
4. **Agents work in worktrees; the user's tree never switches branches.** Merge back with
   `git merge`, then clean up the worktree + branch.
5. **Grill finds problems; eng-review/plan proposes fixes.** Don't blur the phases.
6. **Respect the tier.** Don't gold-plate a T0 fix; don't skip the grill or gate on a T2
   one-way door. Route up when unsure, not reflexively to T2.
7. **Defer to the project.** Project CLAUDE.md (spec dir, template, triggers, invariants,
   project skills) overrides this skill's fallbacks where they conflict.

---

## Recovery (if context compacted mid-run)

1. Check the `TodoWrite` list — it carries the phase you're on.
2. Check disk: the spec file's `status:` (draft = pre-gate; accepted = plan confirmed,
   implementing; implemented = done) and any merged worktree branches.
3. Resume from the next incomplete phase. Re-invoke `Skill(prd-pipeline)` to reload this file.

## Composition map

| Phase | Composes |
|---|---|
| Spec intent | `superpowers:brainstorming` |
| Deep research | `deep-research` skill / `deep-researcher` agent (project may pin another) |
| Grill | project grill skill (e.g. `grill-prd`) ‖ built-in parallel `deep-researcher` critics |
| Architecture | project eng-review skill ‖ `Agent(subagent_type: Plan)` |
| Plan persistence | `superpowers:writing-plans` |
| Parallel build | `superpowers:dispatching-parallel-agents` + `subagent-driven-development` + `Agent(isolation:"worktree")` |
| Per-task TDD | `superpowers:test-driven-development` |
| Verify | `superpowers:verification-before-completion` |
| Review | `code-reviewer` · `typescript-reviewer` · `security-reviewer` · `database-reviewer` |
| Ship | `superpowers:finishing-a-development-branch` |
