---
name: prd-pipeline
description: >
  Use when building, adding, implementing, or substantially changing a feature or behavior —
  the end-to-end path from idea to shipped code. Tier-adaptive: a trivial change goes straight
  to test-first + review with no document at all; a small feature gets a spec and plan confirmed
  in the conversation; a large or irreversible change gets one written change file, an adversarial
  grill, an editable plan-gate, and a parallel git-worktree build. Routes every change against the
  documentation that already exists — amend, supersede, or create — instead of writing a new PRD
  by reflex, and budgets at most one new document per change. Enforces: no non-trivial code before
  a human confirms the plan, parallel agents in isolated worktrees so you never switch branches,
  and a real command run before anything is called done. Standalone — needs no other plugin.
---

# prd-pipeline — idea → smallest spec that earns its keep → confirmed plan → parallel build → verified ship

You are the **orchestrator**. You sequence the phases below and route work to subagents. On a
Tier-2 run you do not write production code yourself — you partition it into disjoint-file tasks,
dispatch worktree-isolated agents, and merge their work back.

Two rules sit above everything else:

1. **For anything non-trivial, a human confirms the plan before code touches disk.**
2. **A change produces at most one new document, and only when the tier earns it.** Writing a PRD
   is the expensive default, not the safe one. Route against the docs that already exist first.

> `references/change-template.md` — the one change-file template. `references/research-notes.md` —
> the sourced rationale. Read them only when you need a template or the *why*; this file is the
> operational procedure.

---

## Step 0 — Preflight (always)

**`git` is a hard requirement** (the worktree build needs it). If it is absent, stop and say so.
Everything else this skill uses is native to the harness: `Read` · `Write` · `Edit` · `Bash` ·
`Agent` (incl. `isolation: "worktree"`) · `TodoWrite`/`TaskCreate`. **Do not assume any other skill
or plugin exists.** If you want the optional accelerants, check the session's own skill listing by
name first — see *Optional composition* at the end. A missing one is never a blocker; the inline
procedure here is complete on its own.

1. **Read the project's `CLAUDE.md`** (repo root) and extract, with fallbacks:
   - **Where change records live** — `docs/specs/`, `docs/prd/`, `docs/rfd/`, `openspec/changes/`.
     *Fallback:* `docs/specs/NNNN-kebab-title.md` + `references/change-template.md`.
   - **What mandates a spec** — the project's own list. *Fallback:* the tier table in Step 1.
   - **Project invariants** — display conventions, config-vs-env rules, read-only stores, naming.
     Carry these into the change file and into the grill lenses.
   - **Project skills** — a project grill or architecture-review skill, if one exists.
   - **Documentation doctrine** — many projects cap which standalone documents may exist at all.
     **The project's cap wins over this skill's Step 2**; if the project says a change belongs in
     the commit message, it belongs in the commit message.
2. **Classify the tier** (Step 1) and say it out loud with a one-line reason.
3. **Seed the task list** with the phases for that tier, in order. It is your durable memory —
   it survives compaction.
4. **Open the run log.** Append-only, one line per stage, to
   `.claude/prd-pipeline/<change-id>.jsonl` (gitignored):
   `{"stage":"tier","verdict":"T2","reason":"new public endpoint"}`. Compaction re-attaches only
   the most recent invocation of a skill, so a long run loses its own early verdicts — which
   alternative was rejected, what the grill blocked on, what the human approved. The log is how
   you get them back. One line per stage; never rewrite an earlier line, supersede it with a new
   one. If it grows into a report it will be useless for the same reason the skill body was.
5. **Worktree sweep.** `git worktree list`; `git worktree remove --force` any orphaned
   `.claude/worktrees/*` not tied to an active task and prune its dead branch. Then confirm you
   are on `main` — a T1/T2 build creates its own branch in Step 5 and must not inherit a stale one.

> **Run this from *inside* the target repo.** The worktree build uses the session's git repo.

---

## Step 1 — Tier routing (decide once, up front)

| Tier | Trigger | Pipeline | New docs |
|---|---|---|---|
| **T0** | Bug fix · refactor with no behavior change · docs · dep bump · a threshold tweak measured against an existing test · devops/CI **config**. Two-way door, obvious solution. *(A test harness, or any script guarding a `curl\|bash` / release / migration path, is NOT trivial devops — it earns T1.)* | Step 5 → Step 6. No spec, no grill, no gate. Exit fast. | **0** |
| **T1** | Small feature · single subsystem · mostly reversible · under ~8 files, ≤2 new components. | Step 2 (spec **in the conversation**) → Step 3 (one grill pass) → Step 4 (plan + gate) → Step 5 → Step 6. | **0** |
| **T2** | New pipeline or behavior · new DB table or column · new public API/endpoint · new external data source · cross-cutting · **one-way door** · anything that moves user-visible outcomes. | Step 2 (one change file) → Step 2.5 → Step 3 (adversarial grill) → Step 4 (architecture lock-in + editable gate) → Step 5 (parallel worktree build) → Step 6. | **1** |

Unsure between two tiers → **route up**. But never reflexively to T2: ceremony on a two-way door
costs more than it protects, and a repo full of specs nobody reads is the observable symptom.

**Research-grounding axis (orthogonal).** Does the spec rest on external or empirical claims —
benchmarks, vendor capabilities, "X beats Y", a performance or accuracy number? If yes, ground
those claims **before** Step 2 and bind each one to its source in Step 2.5 pass 8. Two specs — one
grounded, one invented — look identical; only the binding gate tells them apart.

---

## Step 1.5 — Route against the documentation that already exists

**Run this before writing anything.** The dominant failure of a spec-driven pipeline is not a
missing spec — it is a *new* spec for something an existing document already owns. That is how a
repo ends up with nine overlapping PRDs and a README that contradicts all of them.

**a. Inventory, once, cheaply.** `git ls-files '*.md' 'docs/**'` (skip vendored trees). Sort what
comes back into five buckets — do not read them all, read titles and headings:

| Bucket | Owns | Typical home |
|---|---|---|
| **Product intent** | what this is, who it serves | `README.md`, `docs/product.md`, `PRD.md` |
| **Decisions** | *why* it is this way, and what was rejected | `docs/adr/*`, RFDs |
| **Change records** | what one change did, and its `status:` | `docs/specs/*`, `openspec/changes/*` |
| **Runbooks** | commands a human runs | `docs/runbook*`, `RUNBOOK.md` |
| **Reference** | API/CLI/config surface, often generated | `docs/api/*`, `--help`, config tables |

**b. Route the change against it — pick exactly one, and log the verdict:**

- **Amend.** An existing change record or living spec already covers this surface and the change
  extends it → add a delta section to that document. **Do not create a second one.** Prefer this.
  A living spec is cumulative; change records are not meant to breed. (This is the OpenSpec split:
  requirements endure, proposals are ephemeral — `references/research-notes.md` §8.)
- **Supersede.** The change reverses a decision an ADR owns → write the **new ADR** (which is a
  decision record, not a PRD), link it back to the one it replaces, and mark the old one
  `superseded`. The change itself then needs no spec of its own.
- **Create.** Genuinely new surface that nothing owns → one new change file (T2 only).
- **None.** T0/T1 → the record is the commit message and the confirmed plan in the conversation.

**c. Name the stale set.** List every existing doc this change will make *wrong*: a README claim,
a runbook command, a config table, an ADR's status, a CLI help string. **Each becomes a task in
the Step 4 plan** — not a follow-up, not a nice-to-have. Step 6's doc-sync gate blocks on them.
A change that invalidates documentation and does not update it has not shipped.

> **Artifact budget (invariant).** One change ⇒ **at most one new document**. The Step 2.5
> consistency findings and the Step 4 plan are **sections of that one file**, never siblings.
> The run log is machine state under `.claude/`, not a document. If you are about to write a
> second `.md` for one change, you have made an error — fold it in.

---

## Step 2 — The spec (T1 in conversation · T2 in one file)

If intent or requirements are not crisp yet, resolve them first: state the problem in one
paragraph, propose 2–3 approaches with their trade-offs, and get the user's pick. Do not write a
spec around an ambiguity — write down the ambiguity, or resolve it.

**T1 — no file.** Emit the spec **in the conversation**: Problem · Goals & Non-Goals · Wedge ·
Success criteria · Risks/invalidators. Five short paragraphs. It gets confirmed at the Step 4 gate
and its durable form is the commit message body. A one-pager on disk that nobody will open again
is cost without a reader.

**T2 — one file** at `<change-dir>/NNNN-kebab-title.md`, `status: draft`, from the project template
(fallback: `references/change-template.md`). Sections, **prose not bullet dumps** — writing forces
precision, and bullets are where the hard thinking gets skipped:

**Problem/Context** (anchored in observable evidence — a metric, a log, a failing case) ·
**Goals & Non-Goals** · the win in the user's words (one paragraph, no jargon) ·
**Proposed solution + the trade-offs you made** · **Alternatives considered** (a spec with no
rejected alternative was not designed) · **Success criteria** (which measurable thing moves, by how
much, measured how) · cross-cutting concerns (security · privacy · observability · cost · data) ·
**Drawbacks, risks and hypothesis-invalidators** · **Wedge** (the narrowest slice that delivers
value) · open questions.

Two hard constraints on content:

- **Every invalidator is a triple**: *observable condition → how it is measured → that it means
  roll back*. "We aim for −25%" is a target, not an invalidator.
- **Never a calendar deferral.** "Revisit in two weeks", "monitor for N days" is forbidden as an
  invalidator condition and as a plan step. Triggers are concrete: N production runs, a named
  real-world event, a data-volume threshold.

**Fits about two pages or it is too broad — split it.** The change file is committed on the
feature branch in Step 5 alongside the code, so intent and implementation reach `main` together.

---

## Step 2.5 — Consistency gate (T2; optional for T1)

Before the grill, run a mechanical pass so the critics spend their cycles on novel problems rather
than rediscovering a structural omission. Spawn **one read-only agent** (`[Read]`) over the change
file + the ADRs + the project's `CLAUDE.md` invariants. Eight passes:

1. **Ambiguity** — vague terms ("fast", "scalable") with no measurable criterion; unresolved
   `[NEEDS CLARIFICATION]` markers.
2. **Underspecification** — a requirement with no success criterion; a reference to an undefined component.
3. **Invariant alignment** — conflicts with a project invariant from Step 0.
4. **Inconsistency** — terminology drift against the ADRs; an approach that contradicts a shipped change.
5. **Duplication** — near-duplicate requirements, and **whether Step 1.5 should have routed this
   to *amend* instead of *create*** (if an existing document covers ≥60% of this surface, that is
   a CRITICAL routing error, not a style note).
6. **Required-section coverage** — every section the active template marks `(required)` is present
   and non-empty. A missing or stub **Wedge**, **Alternatives**, or **Invalidators** is CRITICAL.
7. **Invalidator presence** — at least one full triple, with a concrete (non-calendar) trigger.
   Zero valid triples is CRITICAL. *(This pass checks that they exist; the grill critiques whether
   they are any good.)*
8. **Claim ↔ source binding** — every load-bearing quantitative or empirical claim (a number,
   "improves X by N%", "research shows", a vendor capability) either cites a source, is this
   change's own post-ship success criterion, or is tagged `[ASSUMPTION]`. An unsourced load-bearing
   number is CRITICAL — it is the line between a grounded spec and a plausible-sounding hollow one.

**Findings go into the change file** as a `## Consistency findings` section (severity · location ·
fix), never into a sibling `-analysis.md`. **CRITICAL blocks Step 3**; HIGH/MED are passed to the
Step 3 critics as context so they amplify rather than re-derive.

---

## Step 3 — Grill (find problems; do not propose fixes)

Seed an explicit `grill: done/skipped` task before the gate, so a forgotten grill is observable on
the list rather than silently missing. **T0 skips it; for T1 and T2 it is not skippable.**

Use the project's grill skill if it has one. Otherwise:

- **T1** — ONE critic (`Agent(subagent_type: general-purpose)`, read-only) over the spec: edge
  cases, invalidator measurability, and one pre-mortem question.
- **T2** — **3–4 critics in parallel** (one message, multiple `Agent` calls), each with a *distinct*
  lens. Redundant critics hide failure modes; diverse ones surface them. Each is told to steelman
  the change first, then attack it:
  1. **Architecture/conflict** — contradicts an ADR? duplicates shipped scope? inconsistent with
     how the system actually works today? violates a project invariant?
  2. **Edge case / invalidator** — is there a measurable invalidator at all? success criteria with
     no measurement plan? null / empty / race / restart / partial failure / rate limit / quota
     exhaustion?
  3. **Cost, ops, telemetry** — is the cost math shown? are the operator knobs in the right place
     (config vs env)? is there telemetry to query this later? backwards-compat for existing data?
  4. **Pre-mortem** — "it is a year later, this shipped and failed; list the causes." Roughly +30%
     risk identification for 20 minutes of work (Klein, HBR 2007).

Every spawned critic gets the **7-field contract** (see Step 5). Sort findings into three buckets:
**(1) must-fix before `accepted`** · (2) open question, recorded in the change file · (3)
acknowledged and accepted, recorded under out-of-scope. **Exit criterion: bucket 1 is empty.**
Until then the change stays `draft`. Log the bucket counts.

---

## Step 4 — Plan and the gate

Produce the implementation plan. **It is a section of the change file (T2) or a message (T1) —
not a new document.** For T2, lock the architecture first (`Agent(subagent_type: Plan)`, or the
project's architecture-review skill) with this requirement:

> "Lock the architecture for `<change>`: data flow, file boundaries, edge cases, test coverage.
> Output an **ordered task list where every task touches DISJOINT files** so parallel agents cannot
> collide. Cross-cutting edits — shared types, config, schema, build files, CLAUDE.md, docs —
> **serialize after** the parallel block."

The plan MUST carry: the disjoint-file partition · ordered phases with named dependencies · **the
doc-sync tasks from Step 1.5c** · the test plan (the exact commands the reviewer will run) ·
rollback/reversibility · risks and blast radius. Right-size the diff: the smallest change that
cleanly expresses the intent — but do not compress a necessary rewrite into a patch.

> **Ordered-migration caution.** When a branch-merged build introduces a timestamp- or
> sequence-keyed migration journal, the merge step must verify the journal stays strictly
> monotonic. An out-of-order branch merge can land a migration whose key predates an
> already-applied one, and the runner then silently skips it.

**Plan grader loop (T2).** Before the human sees it, converge its quality. Spawn a grader agent
tool-locked to `[Read, Edit]` over the plan section. Score 1–5 on: disjoint-file coverage ·
rollback per task · test plan present · doc-sync tasks present · complexity fit for the tier. For
any criterion under 4, apply **surgical edits to that section — patch, never regenerate**. Re-score;
at most 3 rounds. Append the final scores so the gate can see them. T1 skips this.

### The plan-gate — mandatory for T2, the default for T1

**Emit the plan** — sub-tasks, per-task file scope, the docs it will update, risks; **no time
estimates** — and **pause for approve / edit / proceed. No code touches disk before approval.**

- Gate **hard** on one-way-door, cross-cutting, schema, public-API, or outcome-moving changes.
- Let a reversible single-file change flow with a one-line heads-up.
- On approval: set `status: accepted`, record the decision in one line, log
  `{"stage":"plan-gate","status":"accepted","tasks":N}`.
- **Disagree and commit.** Once it is confirmed, stop re-arguing scope.

---

## Step 5 — Implement (parallel, worktree-isolated)

**You stay on `main`; the work auto-branches into isolated git worktrees; neither you nor the user
ever switches branches, and `main` is never left half-built.** Worktrees solve the file-conflict
problem completely — they are what makes parallel agent development safe.

- **Always start from `main`.** For a T1/T2 feature, first create the feature branch in its own
  worktree and do all the work there.
- **Two or more disjoint-file tasks ⇒ parallelize.** One `Agent` per task with
  `isolation: "worktree"` — the harness spins a fresh worktree and dedicated branch under
  `.claude/worktrees/`, attaches that agent's plan, memory, hooks and transcript to the worktree
  rather than the user's repo, and auto-cleans it if unchanged. Dispatch independent agents
  concurrently: multiple `Agent` calls in ONE message.
- **Merge inward; touch `main` only at ship.** Sub-task branches merge into the **feature branch**
  as they finish — the disjoint-file partition makes that conflict-free. The feature branch lands
  on `main` only at the deliberate ship step. Never continuously.
- **Test-first per task.** Write the failing test, watch it fail, then make it pass. A test that
  has never failed proves nothing.
- **Cleanup is part of the task, on success *and* on failure.** After merging, `git worktree
  remove` the tree and delete the branch. When an agent fails or is abandoned, `git worktree
  remove --force` and prune the dead branch too — locked worktrees otherwise pile up silently.
- **Ceiling: 4–8 concurrent worktrees.** Past that you are bottlenecked on review, not on the
  model. Cross-cutting edits run serially after the parallel block.

**7-field subagent contract** — every spawned `Agent` prompt must open with:
`objective` (one self-contained sentence) · `inputs` (change-file path, the task's exact file
scope, the branch) · `output_shape` · `tools_allowed` · `stop_conditions` · `context` (the project
invariants that bear on this task) · `verification` (the command that proves the task done — and
the agent **must commit on its worktree branch before returning**, or there is nothing to merge).

T0 can go straight onto `main` (test-first + review) with no worktree fan-out.

---

## Step 6 — Verify, sync the docs, ship

1. **Run the real thing.** Execute the test plan's commands and read the output. A typecheck, a
   lint, or a successful build is not verification. Quote the deciding line. For a pipeline, agent,
   or behavior change, run the project's real-run check. When verification needs a **reversible,
   bounded-cost runtime switch** (a feature flag, a shadow→on toggle), own the whole loop yourself
   — enable, observe, disable — and report the bounded result rather than handing the user a
   switch. Still escalate anything irreversible, destructive, or open-endedly expensive.
2. **Independent review.** One read-only pass over the actual diff — misalignment with the plan,
   bugs, security holes, over-engineering — by something other than the agent that wrote it. Add a
   security lens for anything touching auth, keys, payments, or external input; for anything that
   fetches pages, reads documents, or executes model-written code, check the lethal trifecta
   explicitly (untrusted input + private data + an exfiltration channel).
3. **Traceability gate (T2).** A read-only agent (`[Read]`) over the confirmed plan, the change
   file, and `git diff main..<feature-branch>`. Every plan task has a diff change or an explicit
   "skipped" note; every requirement maps to at least one task; no orphan file in the diff without
   a covering task. Orphan files are scope creep; uncovered requirements are silent omissions.
   Both are CRITICAL and block the next step.
4. **Doc-sync gate — the one people skip.** Walk the **stale set from Step 1.5c** and confirm each
   entry was actually updated: README claims, runbook commands, config tables, CLI help, the
   superseded ADR's status, the CHANGELOG. Anything still stale blocks the ship. Then **fold the
   change file down**: its durable content — the decision and why, and what was rejected — belongs
   in the living spec or an ADR; mark the change `status: implemented` and archive it where the
   project keeps archived changes. The record survives; the scaffolding does not accumulate.
5. **Ship.** Integrate the feature branch into `main` per the project's git convention (open a PR
   only when asked), then prune its worktree. **This is the only moment `main` changes.** Sweep
   `git worktree list` one final time and force-remove any orphan, leaving a clean `main`.

---

## Invariants (cannot break)

1. **No non-trivial code without a confirmed plan.** Skipping the gate is the single most damaging
   failure mode this skill exists to prevent.
2. **At most one new document per change**, and only at T2. Findings and plans are sections, not
   siblings. If a document already owns the surface, amend it.
3. **A change that invalidates documentation has not shipped until that documentation is updated.**
4. **Change records are append-only.** `draft → accepted → implemented`; killed → `abandoned`;
   changed → `superseded`, linked forward. Never delete one.
5. **Parallel tasks touch disjoint files.** Cross-cutting edits serialize after the parallel block.
6. **Agents work in worktrees; the user's tree never switches branches.**
7. **Grill finds problems; the plan proposes fixes.** Do not blur the two phases.
8. **Respect the tier.** No ceremony on a T0 fix; no skipped gate on a one-way door.
9. **The project wins.** Its `CLAUDE.md` — spec directory, template, triggers, invariants, and
   especially its documentation cap — overrides every fallback in this file.

---

## Recovery (if context was compacted mid-run)

1. Read `.claude/prd-pipeline/<change-id>.jsonl` — it carries the stage verdicts the context lost.
2. Check the task list for the phase, and the change file's `status:` (draft = pre-gate,
   accepted = approved and implementing, implemented = done).
3. `git worktree list` and `git branch` show which tasks actually landed.
4. Resume from the first incomplete phase. Re-invoke this skill to reload the procedure.

## Optional composition

This skill is complete on its own. If — and only if — one of these appears **by name** in the
session's skill listing, prefer it over the inline fallback; never assume it is installed, and
never block on its absence.

| Phase | Optional skill | Inline fallback (always available) |
|---|---|---|
| Should-we-build / UI judgement | `compound-v:startup-taste` · `compound-v:product-taste` | Step 1 tier routing + the grill's pre-mortem lens |
| Sharpening intent | `compound-v:brainstorming` | Step 2's problem-then-approaches paragraph |
| Cited external research | `bad-research:bad-research` | `WebSearch`/`WebFetch`, bound by Step 2.5 pass 8 |
| Critic reasoning | `compound-v:critical-thinking` | Step 3's steelman-then-attack instruction |
| Parallel dispatch | `compound-v:dispatching-parallel-agents` · `compound-v:batched-implementation` | Step 5's 7-field contract + worktree isolation |
| Test-first | `compound-v:test-driven-development` | Step 5's "watch it fail first" |
| Verification | `compound-v:verification-before-completion` | Step 6.1 |
| Diff review | `compound-v:recheck` · `compound-v:code-review` · the `code-reviewer` agent | Step 6.2 |
| Security lens | `compound-v:agent-security` | Step 6.2's lethal-trifecta check |
| Merge / PR | `compound-v:finishing` | Step 6.5 |
