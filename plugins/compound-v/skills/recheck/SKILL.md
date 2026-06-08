---
name: recheck
description: Dispatch one read-only review pass over a finished batch of work to catch misalignment, bugs, security holes, and over-engineering before it ships, returning severity-tagged findings and a verdict. Use after an implementer reports DONE, before finishing or merging, or whenever you want a finished change independently verified — phrases like "review this", "check the diff", "is this ready", "did the agent actually do it right".
---

# Recheck

One reviewer on your strongest model reads the actual diff, runs the tests itself, and reports discrete findings with a verdict. It is **read-only** — it never edits — and it runs a fixed pass ordered cheapest-disqualifying-first so a wrong feature is caught before anyone grades its style.

## When to use

- An implementer batch reports `DONE` / `DONE_WITH_CONCERNS` (compound-v:batched-implementation hands off here).
- Before compound-v:finishing or any merge/PR.
- Any time you need a finished change verified by something other than the agent that wrote it.
- Skip it for a typo, rename, or config flip — a Trivial-tier change goes straight to compound-v:verification-before-completion. Recheck is for changes with logic in them.

## Three rules that make this work

**Read-only.** The reviewer gets read + run-tests tools, never Edit/Write. A reviewer that can edit can introduce its own bugs, and the bug it adds is the one nobody reviews. Every serious coding agent enforces this on its reviewer (Amp's `oracle` is read-only; Codex's review prompt never patches). The **implementer** applies fixes; recheck only finds them.

**Don't trust the report — verify independently.** The implementer's summary may be optimistic, incomplete, or wrong. Read the actual VCS diff yourself (`git diff <base>..<head>`; if nothing is committed yet, the staged/working set via `git diff HEAD`; with no VCS at all, the changed files named in the handoff). Re-run the tests yourself. "Agent reports success" is not evidence; fresh output is.

**Give the reviewer the diff and the spec — not the implementer's reasoning transcript.** A reviewer that inherits the coder's chain-of-thought inherits its blind spots: the same wrong assumption that produced the bug rationalizes it on review. A clean context reasons *backward* from the diff and the goals, and is free to question a pattern the user asked for that turns out to be insecure or misaligned. (Cognition's Devin Review, run this way, catches an average of ~2 bugs/PR, about 58% of them severe — logic, edge-case, or security.) The findings then **filter back through the agent that holds the full user and spec context**, which decides scope — what's in this batch, what's a separate issue, what the user actually wants. Recheck is a two-way bridge, not a reviewer shouting at a coder.

## The pass — cheapest-disqualifying-first, short-circuit

Run these in order. If a step disqualifies the work, **stop and report** — don't spend effort grading code quality on a feature that's wrong or off-plan.

1. **Goals / principles alignment.** Does this serve the real objective (the spec + the user's CLAUDE.md + the three-compounds gate: does it grow taste, distribution, or a primitive)? Is it overkill — complexity, abstraction, or machinery the task never asked for? *Misaligned or over-built → stop, report, don't go further.*

2. **Plan alignment.** Does the diff match the approved plan? Watch both directions: scope creep (features nobody requested) and under-build (a planned requirement missing). *Diverged → report before any correctness review.*

3. **Bugs.** Read the diff. Logic errors, unhandled edge cases, error paths that swallow or mishandle, off-by-one, null/undefined, race conditions, resource leaks. Only flag bugs **introduced in this diff** — pre-existing bugs are out of scope (flag them separately at most, never as blockers for this batch).

4. **Vulnerabilities** (first-class — most review skills omit this entirely). Recheck *detects* these; compound-v:agent-security is the build-time counterpart that *prevents* them — when you find one, the fix usually lives there. Name the class and the exact triggering input, plus the constructive defense:
   - **Injection** — SQL/command/template; parameterize, never string-concatenate untrusted input into a query/shell.
   - **Broken authz** — BOLA/IDOR, missing ownership/permission checks; every object access verifies the caller owns it.
   - **SSRF** — a user-controlled URL the server fetches; the boundary is an egress allowlist or an SSRF-filtering proxy, not a regex denylist.
   - **RCE / arbitrary exec** — any code-exec, eval, or deploy endpoint must be auth-gated and, for model-written code, run sandboxed (allowlist/AST-check before exec).
   - **Secret leakage** — keep secrets *and* raw `str(exception)`/stack traces out of agent-facing paths, logs, and error responses; a leaked key or internal path is the next exploit's foothold.
   - **Destructive tools** — delete/migrate/spend/send actions need an approval gate, not silent autonomy.
   - **Path traversal** — CWE-22 via `../`; resolve and confine to a base dir.
   - **The lethal trifecta** (agent/LLM code) — private data + untrusted content + an exfiltration channel in one flow. The injection vector is almost always **untrusted document or page content** the agent reads as if it were instructions; break one leg of the trifecta.

   A security hole is at least Important, usually Critical. Call out the second-order or at-scale version — a named, reproducible exploit is what gets it fixed.

5. **Re-test.** Actually run the test suite, the linter, and the typecheck/build. Read the full output and the exit code — count failures, don't trust "should pass". Confirm the tests are *real*: they exercise behavior, not mock-into-tautology assertions that pass no matter what the code does. Green only counts with fresh evidence in this pass.

6. **Patterns / anti-patterns.** Does it follow the codebase's existing conventions and the canonical pattern for what it's doing (use compound-v:searching-patterns when the right pattern is non-obvious)? Flag known anti-patterns. And ask the question over-engineering hides from: **is there a materially simpler version that's just as correct?** If yes, that simpler-possible is a finding — and rate it **Important**, not a throwaway Minor, when the extra machinery is unused/dead code, violates an explicit simplicity requirement, or carries latent risk (memory blowup, a cross-user leak if it were wired up, a maintenance trap). Minor only when it's genuinely cosmetic.

## Output

A list of findings, each:

```
[Critical|Important|Minor] path/to/file.ext:line
  issue: one sentence — what is wrong
  why:   one sentence — the concrete impact / the input that triggers it
  fix:   one sentence — what would resolve it (the implementer applies it, not you)
```

Then exactly one verdict:

- **APPROVED** — no Critical or Important findings; ship it.
- **FIX_REQUIRED** — at least one Critical/Important; the implementer fixes, then re-check.
- **ARCHITECTURE_CONCERN** — the approach itself is wrong (failed step 1 or 2, or fixes keep failing); escalate to a re-plan rather than patching.

**Anti-sycophancy.** Report only newly-introduced, discrete, non-speculative issues. No praise padding, no "great job", no "you might consider…" hedging. "It is not enough to speculate that a change *may* disrupt another part of the codebase" — if you can't name the trigger, it isn't a finding. And don't flag what the author clearly did on purpose, or hold the diff to a rigor bar the surrounding code doesn't meet — a deliberate design choice is not a bug, and a clean-context reviewer (which you are) is the one most likely to misread intent it can't see (OpenAI Codex CLI review prompt). Severity must be honest and calibrated by **impact, not by category label** — a "smell" / "style" / "nit" tag does not cap a finding at Minor if its real-world consequence is large. Don't inflate a true nit to Critical; don't bury a high-impact issue as Minor. A clean diff gets a one-line APPROVED, not a manufactured list.

**Signal-density cap.** At most ~10-12 findings per pass. Returning 40 small findings buries the critical one. If there are more than a dozen real problems, the right finding is ARCHITECTURE_CONCERN.

## The loop and its cap

Findings go back to the **same implementer** to fix (it has the context; it holds the edit tools). Then re-check. **Cap at 3 fix↔recheck cycles** — the same N=3 that compound-v:systematic-debugging owns (where the convergent production-agent evidence lives). Still failing at cycle 3 is a signal, not a reason for cycle 4: return ARCHITECTURE_CONCERN and question the design or the plan.

## Red flags

| Smell | Why it's wrong |
|---|---|
| The diff makes a failing test pass by **weakening or deleting the assertion** | A reward-hack — the test now proves nothing, and an assertion gutted to go green is the same shape as a quietly introduced vuln. Flag it; the bug is unfixed. |
| The reviewer was handed the implementer's reasoning, not just the diff + spec | It inherits the blind spot that produced the bug and rationalizes it. Review from a clean context. |
| Approving from the implementer's summary | You reviewed prose, not code. Read the diff and re-run the tests this pass. |
