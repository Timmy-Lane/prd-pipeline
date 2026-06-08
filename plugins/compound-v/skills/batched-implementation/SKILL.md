---
name: batched-implementation
description: Execute a written implementation plan with fresh-context implementer subagents, batched ~2-3 related tasks each with a read-only recheck gate per batch. Use when you have an approved plan or task list to build out in this session and want isolated, reviewable execution — phrases like "implement the plan", "build these tasks", "run the implementer", "execute the spec".
---

# Batched Implementation

Run a plan as a small number of fresh-context implementer subagents (one per 2-3 related tasks, all on your strongest model), recheck each batch, and keep going without stopping to ask permission.

## When to use

- You have an approved plan (from compound-v:writing-plans) or a concrete task list, and you're about to build.
- The work is the **Standard** tier (a feature, ~2-8 tasks). For a one-file change or a typo, skip this entirely and just do it inline → compound-v:verification-before-completion. Spawning a subagent for a one-liner is the overkill this kit exists to refuse.
- For **Large** work (multiple subsystems), decompose into sub-projects first; each runs its own Standard cycle.

## Why batches, not one-agent-per-task

Superpowers dispatches a fresh agent per task plus two sequential reviewers plus a final review — ~16 dispatches for a 5-task plan. The 1:1 ratio is justified only by fear of context pollution. A strong model's window holds 2-3 related tasks comfortably, and keeping shared types/imports/helpers in one agent's head keeps them *coherent* (the same struct named the same way across the tasks that touch it). Batching cuts dispatches ~60% with no loss of isolation — each batch is still a clean context, and recheck (not a second reviewer) is the quality gate.

WARP's finding is the counterweight that makes this safe: for coupled, latency-sensitive work, one strong agent beats a planner→executor→critic fan-out. So group coupled tasks together; don't shatter a plan into atomized agents.

## The loop

**Setup (once):**
1. **Sanity-check the environment** before building — confirm the verify commands (test/lint/typecheck/build) actually run here. A plan that can't be verified in this session is a plan you'll finish blind.
2. Confirm you're not on `main`/`master`; if you are, branch first. If the harness already gave you an isolated workspace (a worktree, a fresh clone, a sandbox), use it — don't nest a second one. If it didn't and the work wants isolation, prefer a native worktree, and always branch before the first edit.
3. Read the plan file **once**. Extract every task with its full text and context. Build a TodoWrite with one entry per task.
4. Group tasks into batches of **2-3 by coupling** — tasks that share files, types, or a feature surface go together. A task that's independent of everything else can be its own batch. When a batch's tasks are *structurally similar* (say three near-identical endpoints), the brief must spell out what **differs** per task — a fresh-context implementer falls into a rhythm and adapts the third from the first two, inheriting their assumptions (Manus, on few-shot rut).

**Per batch:**
1. Dispatch **one implementer subagent** (Task tool, `general-purpose`, your strongest model) for the batch.
   - **Paste the full task text** into the prompt. Never tell the subagent to "read task 3 from the plan file" — it costs a read and risks it grabbing the wrong context. The dispatch prompt is the contract; it must stand alone.
   - Include: the pasted tasks, scene-setting context (what exists, what the batch fits into), the relevant file paths, and **how to verify** (the exact test/lint/typecheck commands). An implementer told how to check its own work produces far less for recheck to catch.
   - Mandate the discipline: follow existing conventions — and when a convention matters, **paste the exemplar** (the file or snippet to imitate) into the prompt, not a bare "follow conventions"; a fresh-context agent regresses to model defaults for any convention it wasn't shown (Anthropic, building effective agents: a good tool/interface definition includes example usage). Never assume a library is present without checking the manifest, write tests (compound-v:test-driven-development), keep changes minimal, and self-review before reporting. If the env can't run the verify commands, the implementer must **say so** in its report — an honest "couldn't run the suite here" beats a fabricated green.
   - **Brief the *what* and the constraints, not the *how*** — paste tasks, exemplars and verify commands, but don't dictate the implementation line-by-line; an over-prescribed brief wastes the implementer's judgment and misses what it would have found, and over-prescription backfires hardest exactly where you hold less of the detail than the implementer will once it's in the code (Cognition, "Multi-Agents: What's Actually Working": managers "default to being overly prescriptive, which backfires when the manager lacks deep codebase context").
2. Read the subagent's report. It must end in one of **four statuses**:

   | Status | What it means | What you do |
   |---|---|---|
   | `DONE` | Built, tested, self-reviewed, clean | Proceed to recheck. |
   | `DONE_WITH_CONCERNS` | Built, but flagged something | If the concern is correctness or scope, resolve it before recheck. If it's a benign observation, note it and proceed. |
   | `NEEDS_CONTEXT` | Missing info it couldn't infer | Supply the missing context, re-dispatch the same batch. |
   | `BLOCKED` | Can't proceed | Assess: too large → split the batch; plan is wrong → escalate to the user; genuinely ambiguous → ask. Don't re-dispatch unchanged. |

   The status is a clean state machine — act on it, don't re-parse the prose.
3. Hand the batch to **compound-v:recheck** (one read-only pass over **this batch's diff** — see "Track the batch's range" below) for the verdict and the fix↔recheck cycle; that skill owns the three verdicts and the N=3 cap. The one routing rule that lives *here*: an `ARCHITECTURE_CONCERN` (whether on the first pass or after 3 cycles) **stops the loop** — escalate to re-plan (compound-v:writing-plans), never re-dispatch the same batch, and never hand to finishing. Finishing is reachable only from `APPROVED`.
4. On `APPROVED`, **commit the batch** (mark its tasks done in TodoWrite first). One commit per green, rechecked batch makes git the state machine: each commit is a known-good point, so a later batch that breaks the build rolls back to the last green without losing earlier work. Keep the tree mergeable as you go — small, coherent commits, not one giant end-of-plan blob.

### Track the batch's range
Before dispatching a batch, note the current `HEAD` (`git rev-parse HEAD`). After the implementer reports, the batch's diff is exactly `that-SHA..HEAD` (or the changed-file list from `git diff --name-only that-SHA`). Hand recheck *that* range, so it reviews only this batch and not the whole accumulated branch. The per-batch commit at the end gives you a clean range marker for the next batch.

## Serial by default; parallel only when file-disjoint

Run implementers **serially**; the one exception is batches that are genuinely file-disjoint (no shared files or state), which may fan out — but the gating test and conflict-check-on-return belong to **compound-v:dispatching-parallel-agents**, so defer to it and run serially when unsure.

## Continuous execution

Do not pause between batches to ask "should I continue?" — it wastes the user's turn. The only legal stops are: a `BLOCKED` you can't resolve, a recheck `ARCHITECTURE_CONCERN` (stop the loop, escalate to re-plan), a genuine ambiguity that changes scope, or all batches done and rechecked. Keep going until the plan is built and every batch is APPROVED, then hand off to **compound-v:finishing**.

## Responding to findings

When recheck (or the user) hands back findings for the implementer to fix, the findings are *input to judgment*, not orders to type out:

- **Verify before implementing.** Confirm the finding is real against the actual code — a reviewer can be wrong about what the code does. Fixing a phantom bug adds a real one.
- **Clarify an ambiguous finding before acting** rather than guessing at its intent; a wrong guess costs a whole fix↔recheck cycle.
- **Scan suggestions for scope creep.** A "while you're here, do it properly / handle the general case / add a config for this" finding is often YAGNI — implement what the plan needs, not the gold-plated version, and say why you're deferring it.
- **No performative agreement.** Don't "you're absolutely right" a finding you haven't checked. If a finding is wrong or out of scope, push back with the reason; that's the value of the loop, not a failure of it.

## Red flags

| Smell | Why it's wrong |
|---|---|
| Implementing on `main`/`master` | No isolation; a bad batch dirties the default branch. Branch first. |
| Re-dispatching a `BLOCKED` batch unchanged | Same input → same block. Change the context, split the batch, or escalate. |
| Skipping recheck "because the batch was simple" | Recheck is the only quality gate in this loop; skipping it removes the gate. |
| Two implementers on shared files in parallel | Merge conflicts and clobbers. Serial unless file-disjoint. |
