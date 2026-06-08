---
name: verification-before-completion
description: Run the command that proves a claim and read its output before asserting the work is done, fixed, or passing. Use whenever you're about to say something works, claim a fix or feature is complete, report tests/build green, or trust that a subagent finished — evidence before assertions, always.
---

# Verification Before Completion

If you haven't run the verifying command *in this turn*, you can't claim it passed. "Should pass," "looks right," and "I fixed it" are predictions, not evidence — and the cheapest way to break a user's trust is to confidently report a green that was actually red.

This is one half of the generation–verification loop: the model generates, then something *verifies*. Your job is to make that verification real and fast, not to skip it because the change "obviously" works. The whole leash that lets work proceed without re-reading every line is the evidence at the end. When the verifier fails, feed its output *back into context* and act on it — the failure message is the next input to reason from, not a wall you read once and re-guess past.

## The gate (run before any completion claim)

1. **Identify** the command whose output would actually prove the claim.
2. **Run** it fresh and in full — not a remembered result from earlier, not a subset.
3. **Read** the full output: the summary line, the exit code, the failure count.
4. **Confirm** the output actually says what you're about to claim.
5. **Then** make the claim — quoting the evidence, not paraphrasing your hope.

Skipping any step is asserting something you haven't checked.

**No command proves it yet? Build the observation channel before you claim — don't skip the gate.** The reason agents confidently ship broken work is an *observation* gap, not an action gap: the files were written, the tool returned no error, but the result was never sensed. When step 1 has no answer, add the missing sense — a screenshot, an assertion, a structured-output check — then run *that*. A claim with no way to observe the outcome is a guess wearing a checkmark. [Anthropic "Claude Agent SDK Deep Dive", DeepLearning.AI: closing the feedback loop — e.g. a browser-screenshot channel for a UI the agent can't otherwise see — is one of the biggest unlocks for autonomous task length.]

## What each claim actually requires

| Claim | Requires (evidence) | Not sufficient |
| --- | --- | --- |
| "Tests pass" | Ran the suite this turn; output shows **0 failures** + exit 0 | "Should pass" · the tests passed before your last edit · only one test ran |
| "Build / typecheck is clean" | Ran the build/typecheck; **exit 0** | The linter passed · it compiled an hour ago · no red in the editor |
| "The bug is fixed" | A test that reproduces the **original symptom** now passes | The code looks right · it no longer crashes on *your* one input |
| "Feature is complete" | Each requirement checked off against the spec, line by line | "I implemented the main part" · it handles the happy path |
| "It runs" | Actually started it (booted the server, ran the CLI, hit the endpoint) | The unit tests are green — passing tests don't prove the app boots |
| "The subagent finished it" | **You read the VCS diff yourself** and ran the suite | The agent reported success · its summary says DONE |

That last row is the one that bites most: a subagent (or a prior you) reporting success is a *claim*, not proof. Run `git diff` and read what actually changed, then run the tests yourself. Agents make systematic errors and optimistic summaries — trust the diff, not the report.

For anything a user touches, "it runs" means **end-to-end as a real user** — boot the app and click through the actual flow, not just `curl` one endpoint or watch the unit tests pass. The gap between "the API returns 200" and "the feature works in the browser" is exactly where the bugs you'd ship live.

## Red flags — stop before you type the claim

- You're about to write "Perfect!", "Done!", "All green!" — and you haven't run anything this turn.
- You're reaching for "should," "probably," "seems to," "I believe it." Those words mean you're guessing; go run the command.
- You're trusting a test run, build, or agent report from *before* your most recent change. Stale evidence is not evidence — the change may have broken it.
- "It's a tiny change, no need to verify." Tiny changes break builds too. The check is cheap; run it.

When the gate passes, state the evidence: "Ran `pytest`: 142 passed, 0 failed (exit 0)." That sentence is worth more than any amount of "looks good." If a verification reveals a failure you don't understand, that's a debugging task — use **compound-v:systematic-debugging**.
