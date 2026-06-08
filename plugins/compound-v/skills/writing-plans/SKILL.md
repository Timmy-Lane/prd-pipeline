---
name: writing-plans
description: Turns an approved design or spec into a step-by-step implementation plan with exact files, real code, and runnable verification. Use when you have requirements for a multi-step task and are about to start building, or when an agent will execute the work task-by-task.
---

# Writing Plans

A plan is where most of the quality is decided. Get the research and the plan right and the implementation almost writes itself; get them wrong and you generate thousands of bad lines from a few bad ones.

## When to use

- You have an approved design (from `compound-v:brainstorming`) or a clear spec, and the work is more than one obvious edit.
- An implementer — a subagent or a fresh session — will execute the plan without your current context.
- Producing the product's stable PRD instead? That's its own skill — **compound-v:writing-prd**.

**Skip the plan doc** for trivial and small changes per the `using-compound-v` tier table — make the change and verify. The plan earns its cost on Standard-or-larger work.

## Research before plan, plan before code

The leverage runs uphill. A bad line of code is one bad line. A bad decision in the plan is hundreds of bad lines. A bad piece of *research* — misunderstanding how the system works, where data flows, where the change actually belongs — is thousands. So the order is **Research → Plan → Implement**, and you spend disproportionately at the top.

**Research first.** Before writing tasks, understand the system you're changing: the files that matter, where the problem actually lives, how data flows through it. Read the code; don't assume. The output of this phase is concrete — name real files and the specific line ranges the plan will touch, so the implementer doesn't re-discover the codebase from scratch. If you're shouting at the implementer later, the research or the plan was thin.

**Search the pattern first when it's unfamiliar.** Before you plan a non-trivial, unfamiliar, or security-sensitive pattern — or pick a library or API shape — find how it's actually done well. Use `compound-v:searching-patterns` to pull the canonical pattern *and* its matching anti-pattern, then bake both into the plan so the implementer copies the right one. An hour of pattern research up front beats a recheck cycle that rejects the wrong abstraction. Don't do this for code you already know cold.

## Order tasks by risk, not by comfort

Sequence the work so the riskiest assumption gets tested first, with the cheapest task that resolves it — don't lay scaffolding or build the fun part while the load-bearing assumption sits unexamined. (Identifying *which* assumption is load-bearing is **compound-v:startup-taste**'s job; this is where that judgment becomes task order.)

The risk clusters at the edges: setup (environment, dependencies, scaffolding) and the finish (deploy, env vars, prod config) are where builds fail; the middle application logic is the reliable part (Amjad Masad / Replit, a16z podcast). Add setup and deploy tasks early instead of trusting them to fall out at the end.

## Write for an implementer with zero context

Assume the implementer is a capable engineer who knows nothing about this codebase or problem domain and has questionable taste. Everything they need is in the plan: which files to touch, the actual code, how to test it, what "done" looks like. They may read tasks out of order, so each task stands alone.

The bar is the **intern test**: if a clear brief would let a competent intern do this task, an agent can. If even a sharp intern would have to come back and ask, the gap is ambiguity in your plan — not a limit of the model — and the fix is to close it here, not to wait for a stronger model.

### File structure first

Before defining tasks, map which files get created or modified and what each is responsible for. This is where the decomposition gets locked in.

- One clear responsibility per file. Files that change together live together — split by responsibility, not by technical layer.
- Focused files are more reliable to edit (yours and the implementer's). If a file is growing unwieldy on the path you're touching, planning a split is fair; don't unilaterally restructure unrelated code.
- In an existing codebase, follow the established patterns rather than imposing new ones.

### Bite-sized tasks with real content

Each task produces a self-contained, testable change. Within a task, the steps follow the test-first rhythm — write the failing test, see it fail, implement the minimum, see it pass, commit (see `compound-v:test-driven-development`). Right-size the granularity to the work: don't fetishize a separate "run it to see it fail" line for a one-line mechanical step, but never collapse real behavior into "implement the feature."

```markdown
### Task N: <component>

**Files:**
- [NEW]    `src/exact/path.py`
- [MODIFY] `src/exact/existing.py:123-145`
- [DELETE] `src/exact/dead.py`
- [TEST]   `tests/exact/path_test.py`

- [ ] Write the failing test:
      ```python
      def test_rejects_expired_token():
          assert verify(expired_token()) is False
      ```
- [ ] Run `pytest tests/exact/path_test.py -v` → expect FAIL ("verify not defined")
- [ ] Implement the minimal code in `src/exact/path.py`:
      ```python
      def verify(token): ...   # real body, not a sketch
      ```
- [ ] Run `pytest tests/exact/path_test.py -v` → expect PASS
- [ ] Commit: `git commit -am "feat: reject expired tokens"`
```

Start the plan with a **preamble** the implementer inherits before any task: a one-line goal, a plan-level `Done = <machine-checkable signal>` (the command or eval that says the whole plan is finished — each task has its own test, but the plan as a whole needs one too), two-to-three sentences on the approach with key libraries, and a **distilled fold-in of the research** — the real files, the line ranges, the data-flow facts, and the canonical/anti-pattern you found. The implementer has none of your context; whatever you learned and don't write here, they re-discover from scratch or guess. Add a **divergence rule** too — if a load-bearing assumption proves false mid-build, the implementer stops and reports back rather than improvising in code or looping; give an explicit budget (e.g. after ~3 failed attempts at the same thing, surface it instead of grinding) (Cognition Devin; Google Antigravity formalize this execution→planning backtrack). And a **User-Review flag** — call out up front, in the preamble, anything destructive or irreversible the plan introduces (a migration/backfill, a deleted public API, a prod-config change) so the human signs off before the implementer runs it autonomously, not after (Google Antigravity's `implementation_plan.md` template mandates a `## User Review Required` block — breaking changes, significant design decisions — as the plan's second section).

## No placeholders

A placeholder in a plan is a decision you pushed onto someone with less context — it becomes a guess in the code. These are plan failures; don't write them:

- "TBD", "TODO", "implement later", "fill in the details"
- "Add appropriate error handling / validation / edge cases" — name them, or write the code
- "Write tests for the above" with no actual test code
- "Similar to Task N" — repeat the code; the implementer may read this task first
- Steps that say *what* without *how* (code steps need code blocks)
- References to types, functions, or methods no task defines

Estimate effort in hours or days. If a plan reads "this will take weeks", the construction isn't the long pole — re-scope into shippable slices, because building is rarely what's actually slow anymore.

## Verification Plan

End the plan with how the finished work gets checked — the per-task tests prove each piece; this proves the whole thing holds together. Two parts:

- **Automated** — the exact commands a fresh session runs to confirm done: the full test suite, the type check, the lint, the build, any end-to-end command. Write them runnable (`pytest -q && ruff check . && npm run build`), not described. This is the plan-level `Done =` signal, made executable.
- **Manual** — what a machine can't assert: the thing to click, the screen to eyeball, the case to try by hand. Keep it to what genuinely needs a human; if a step *can* be automated, move it up.

The tests *are* the done-signal, so the plan must forbid editing a test to make it pass: when a test fails the suspect is the code under test, not the test — change the test only if the task is explicitly about the test (Cognition Devin). Defend the criterion from the other side too: pair each one with the negative constraint that rules out the cheat — *tests pass* **and** no assertion weakened, no expected output hardcoded — because an agent rewarded only for green tests will hardcode the green (a16z / Steinhardt, specification gaming).

## Self-review the plan

After the plan is complete, read it against the spec with fresh eyes. This is your own pass, not a subagent.

- **Spec coverage** — for each requirement in the spec, point to the task that implements it. List the gaps; add tasks to fill them.
- **Placeholder scan** — hunt the patterns above and resolve every hit.
- **Type consistency** — do signatures and names line up across tasks? `clearLayers()` in Task 3 and `clearFullLayers()` in Task 7 is a bug waiting to happen.

Fix inline and move on. Save the plan to `docs/plans/YYYY-MM-DD-<feature>.md` (user's location preference wins), then hand off to `compound-v:batched-implementation` to execute it.

## A product PRD is a different artifact
A PRD is the product's *stable* source of truth (goal, core functions, tech stack), read first for context — not a per-build plan. It has its own skill: **compound-v:writing-prd**. This skill owns the plan; that one owns the durable product doc.
