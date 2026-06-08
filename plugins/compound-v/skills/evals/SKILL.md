---
name: evals
description: Measure whether an AI feature actually works by looking at its outputs systematically — error analysis, a binary judge aligned to a human, and an eval set decomposed by mechanism. Use when building or validating an LLM output, agent, RAG, classifier, or prompt and you need to know if it's good — "is my prompt/agent good?", flaky AI output, choosing a model, before adding or shipping an LLM feature, even when no one asked for evals.
---

# Evals

You cannot tell if an AI feature works by reading the code or vibe-checking a few outputs. You find out by looking at its outputs across the inputs real users send, and turning what you see into a measurement you can re-run. **Shipping an LLM feature with no eval is the single most common cause of a failed AI product** — teams iterate on prompts forever with no idea whether a change helped, hurt, or did nothing.

This is the AI-behavior counterpart to the code-correctness skills: compound-v:test-driven-development and compound-v:verification-before-completion prove a *deterministic* change does what the diff says; compound-v:recheck reviews a diff for bugs. Evals prove a *probabilistic* feature produces good output over a distribution of inputs. Different problem, different tool.

## When to use

- You're adding an LLM call, agent, RAG pipeline, or classifier and you're about to tune the prompt by feel.
- The output is flaky — good on your three test cases, weird on real traffic.
- You're choosing between models (or deciding whether the new model is actually better).
- A stakeholder asks "is it good enough to ship?" and you have no number to point at.
- **Skip the heavy machinery** for a one-off script or a throwaway prompt you'll run twice. The cheapest eval (a handful of assertions, below) still earns its keep; a labeled judge with calibration does not.

## Verifiable signal first

Before any LLM-judge cleverness, ask: **can this be checked by code?** A cheap deterministic assertion beats an LLM judge on cost, speed, and reliability every time. Make the model emit its objective answer *first* (a number, a label, a JSON field), then its prose — so the check is `output startswith "X"` instead of an LLM-judge call on every case. CoCounsel's discipline: "evals are way easier when you can say `matches word X`." Reserve LLM-as-judge for genuinely open-ended quality (tone, faithfulness, helpfulness) where no assertion exists — it's sometimes the only option, not the default one. Code with an automated pass/fail signal is exactly why coding agents work; engineer your feature so its output has one too.

## The #1-ROI activity: look at your data (error analysis)

Reading actual traces is the highest-return thing you can do — higher than any prompt tweak. The person doing it should be the **domain expert** who holds the real definition of "correct" — the lawyer, the doctor, the support lead — labeling and writing criteria directly in the product UI, not an engineer guessing at it. The loop:

1. **Read traces.** Pull 30-100 real interactions (production if you have it, a realistic beta otherwise). One row per interaction in a spreadsheet.
2. **Open-code.** Write a free-text note on what went wrong with each bad one — no categories yet, just observations ("dropped the date", "invented a citation", "ignored the second question").
3. **Build a taxonomy (axial coding).** Cluster the notes into failure types. An LLM can do this clustering pass over your notes.
4. **Count.** Map each row to its failure type; pivot-table the frequencies.

Almost always a **handful of failure types dominate** the long tail — a few buckets account for most of the bad outputs. That's the point: you stop guessing and fix the two or three things that actually matter. In the canonical field-guide write-up, a few categories dominated and fixing the top one (date/scheduling handling) produced a large jump in that category once the team saw it ranked. None of these bugs were findable by reading code; only by watching the system fail on real inputs.

Generic off-the-shelf metrics are *worse than useless* here — a rising "helpfulness score" while users can't complete the task is "optimizing page-load time while checkout is broken." Build the taxonomy from *your* failures, not a vendor's metric list.

## Judges: binary + a written critique

When you do need an LLM to grade open-ended output:

- **Binary pass/fail, never a 1-5 Likert.** Both humans and models can't reliably tell a 3 from a 4, so Likert scores are noise dressed as precision. A 10% rise in *passing* outputs is immediately meaningful; a 0.3 rise on a 5-point scale means nothing. A continuous 0.0-1.0 *is* fine as a **diagnostic alongside** the binary (emit both in one judge call — the score tells you how close, the binary decides) — just never let the score become the **ship-gate**, where its false precision lets borderline output sneak through.
- **Prefer pairwise/binary over absolute scoring.** "Is A better than B?" and "did this pass?" are judgments a model makes reliably; "rate this 7.4/10" is not, because there's no stable anchor for the number and it drifts run to run. Comparative and binary questions have a fixed reference; absolute scores invent one.
- **Pair every verdict with a one-line written critique** of *why* it failed. This is the highest-leverage trick in the whole skill: those critiques become the **few-shot examples for the LLM judge**, materially raising judge↔human agreement. Critique first, score second.
- **The same aligned judge can become a runtime gate, not just an offline scorer.** Wrap the deliverable in a generate→grade→revise loop: the judge returns pass / needs-revision + its written critique, and on needs-revision the agent retries using that critique as the fix-list. **Bound the loop** (e.g. 3 attempts, then accept-with-flag) — an unbounded retry-until-pass loop spins forever and burns tokens on a case that never satisfies the rubric. [Anthropic cookbook evaluator-optimizer; `anthropic` SDK `define_outcome` grader defaults to 3 revision cycles, max 20]
- **Use the most capable model you can afford as the judge** — it can be slower and pricier than your production model; it runs offline.
- **Align the judge to a human before trusting it.** On 25-50 examples, lay out `model_response | model_critique | model_verdict` against your own human verdict; refine the judge prompt until they agree. **Target >90% agreement.** When pass/fail classes are imbalanced, don't report raw agreement — **measure precision and recall separately** (a judge that always says "pass" looks 90% accurate on 90%-pass data and is useless).
- **Criteria emerge from grading.** You cannot fully specify the rubric up front; the act of labeling *defines* what good means. Expect the rubric to sharpen as you grade, and re-calibrate periodically as it drifts.

For an open-ended task, a judge can score a few **independent axes** rather than one blurred verdict. A research-answer judge, for instance, scores *factual accuracy*, *citation accuracy*, *completeness*, *source quality*, and *tool efficiency* — each as its own binary (plus an optional diagnostic score), so a regression in citations is visible even when factual accuracy holds. Start small — roughly **20 queries** is enough to find the gross failures — and scale toward hundreds as the feature matures, keeping a human in the loop on the edge cases the judge is least sure about.

## The judge is a proxy — assume it will be gamed

An LLM judge is a stand-in for the goal, not the goal itself. The moment anything optimizes *against* it (an agent tuning its own output, an RL loop, even you iterating on a prompt), it will find the cheap way to pass. Defend the gate:

- **Make the model emit its objective answer first**, then its prose — so the pass condition is a fixed prefix check the optimizer can't reverse-engineer into "say the magic words." A gate the optimizer can read is a gate it will game.
- **Hold out off-distribution cases** the feature was never tuned on; a judge only ever seen on the training inputs measures memorization, not capability.
- **Require ≥2 independent signals for anything high-stakes** — one judge is a single point of failure with an incentive to be fooled.
- **Make the eval itself tamper-resistant.** Agents optimize the *measured* thing, not the *intended* one: an agent could "solve" any SWE-bench instance by `git pull`-ing the future commit that contains the fix and reading it off `git log` — so the harness defensively runs **`git remote remove origin`** to cut that path off. If the environment hands the agent a route to the answer, it will take it — find and close the route.

## Decompose by mechanism, not difficulty

A single aggregate score hides signal. Group your eval cases by the **mechanism** each one tests, so a change that helps one mechanism is visible even when it doesn't move the others. Mastra drove agent memory on LongMemEval from a **60.2%** full-context baseline to a **94.87%** SOTA this way, decomposing it into the benchmark's **six** categories — single-session-user, single-session-assistant, single-session-preference, knowledge-update, temporal-reasoning, multi-session — so each isolated a different failure cause. Temporal-reasoning turned out to be a date-*presentation* problem; knowledge-update was a *write*-path problem (targeted overwrite, not full rewrite). The fixes were mechanism-specific and would have been invisible under one blended number.

If you split by difficulty (easy/medium/hard) instead, you learn nothing actionable — "hard cases fail more" doesn't tell you *what to fix*. Split by what's being exercised.

## Three cadences, matched to cost

Run cheaper checks more often (ordered by what dictates the cadence):

| Level | What | When it runs |
|---|---|---|
| **1 — Assertions** | code-checkable pass/fail (format, contains-X, schema valid, no banned string) | every change, in CI — cheap, so constant |
| **2 — LLM / human eval** | the aligned binary judge over your mechanism-decomposed set | on a schedule / before a release |
| **3 — A/B** | real users, real outcomes | only for major changes |

Build out Level 1 first and lean on it hardest; it's free to re-run. **Cascade the levels cheapest-first** — run the assertions before the judge, the judge before the A/B; a case that fails a cheap deterministic check never needs to reach an expensive one. Don't reach for Level 3 to settle a question Level 1 already answers — that's the overkill compound-v:using-compound-v warns against. (Choosing a model = Level 2 over a fixed input set, not a vibe: run old and new on the *same* inputs and compare on your metrics before swapping.)

## The eval pipeline is the moat

The durable advantage in an AI product is rarely the prompt or the model — both are copyable in a weekend. It's the **eval pipeline**: the harvested failure cases, the aligned judge, the data viewer, the regression set. That's the asset compounding while everyone else vibe-checks. Two consequences for how you build:

- **Add evals before you scale tool count or agent complexity.** Each new tool or rung multiplies the ways the system can fail; without a measurement harness you're adding surface area you can't see. The eval comes first, then the capability it gates.
- **Log full traces, not just final answers**, so the eval can inspect the *process* — which tool was called, in what order, on what input — not only the output. Most agent failures are in the trajectory (wrong tool, wrong order, redundant calls); an answer-only eval is blind to them.

## Guard against drift, decoration, and trajectory bugs

Three checks that catch failure modes the basic loop misses:

- **Freeze a golden set; re-run it when you change the judge.** Your judge prompt and rubric *are* code, and editing them silently moves the bar. Keep a small set of human-verified cases with locked verdicts; after any judge change, re-run it — if previously-passing golden cases now fail (or vice versa), you changed the measurement, not the system. This is the regression test for the eval itself.
- **Negative-control / ablation: remove the input the feature depends on and watch the metric drop.** If a RAG answer scores the same with retrieval turned *off*, the retrieval is decorative and the model was answering from priors. A component that can be ablated with no metric change isn't earning its place — this is how you catch features that look like they work but don't.
- **For agents, score the trajectory, not just the answer.** Compare the tool-call sequence against the expected one at the strictness the task needs: **EXACT** (same calls, same order, nothing extra), **IN_ORDER** (the required calls appear in order, extras allowed), or **ANY_ORDER** (the required calls all happened, order-free). A right answer reached by a wrong path is a bug waiting to surface on the next input. But pin only the tool calls the task truly requires — over-specifying the trajectory turns the eval into a brittle change-detector that breaks on a legitimate tool refactor and marks resourceful recovery (an agent that works around a bad input) as failure. When the goal is reachable many ways, assert on the final result, not the path. [Scott Yak, Datadog — DeepLearning.AI "MCP Server Evals Deep Dive"]

## Build a one-screen data viewer

Teams with a thoughtfully built data viewer iterate **dramatically faster** — it's the single biggest force-multiplier on the whole loop. You'll build it in **hours** with AI assistance (Streamlit / Gradio / FastHTML — anything you already have; don't go buy a fancy eval platform first). What makes it pay off:

- **All context for one interaction on a single screen** — input, output, retrieved chunks, the trace. No clicking between tabs.
- **One-click / hotkey labeling** — pass/fail plus an open-ended note box. Keystrokes beat forms; this is what makes labeling 100 traces tolerable.
- **Filter and sort by failure type** — so you can jump straight to the cluster you're working.

The viewer is what makes "look at your data" actually happen at volume instead of dying after five traces.

## Count experiments, not features

Progress on an AI product is the number of hypotheses you tested against data, not the number of features you shipped. A feature added without a way to measure whether it helped is a guess you'll never resolve. So: don't add a capability until you can measure it (Mastra deliberately deferred reranking and episodic memory until each was measurable), and grow the eval set with real failures — start at ~10 cases you wrote, scale toward hundreds-to-1,000 by **harvesting the dumb, weird inputs real users actually send** in a small "it'll be rough at first" beta. Ship when you pass the bar on that set at a very high pass rate; never promise perfection. This is the same gate compound-v:startup-taste calls verifier-first — no eval, no ship.

**When you don't yet have real traffic, generate synthetic inputs — but with discipline.** Build the set as **features × scenarios × personas** (each capability, crossed with the situations it runs in, crossed with the kinds of users who hit it) so coverage is structured, not a pile of similar prompts. Generate the **inputs, never the outputs** — the whole point is to see what your system produces, so a synthetic "correct answer" defeats the exercise. And **verify each synthetic case actually triggers the path it claims to**; a scenario that doesn't exercise the feature is a silent blind spot dressed as coverage.

**Trace-reading stop rule:** read logs until you stop learning. Each new trace should teach you something — a fresh failure mode, a surprising input. When several in a row tell you nothing new, you've saturated this batch; **~100 is a reasonable floor** before you trust that signal, fewer only for a throwaway. Stop reading when the marginal trace stops surprising you, not when you hit a quota.

## Red flags

| Smell | Why it's wrong |
|---|---|
| Tuning the prompt by re-reading 3 outputs | You're optimizing on noise. Do error analysis on 30-100 real traces. |
| A 1-5 quality score | Graders can't separate 3 from 4. Use binary pass/fail. |
| A judge you never aligned to a human | Could be agreeing with itself. Calibrate on 25-50 examples; target >90% agreement, P/R when imbalanced. |
| One aggregate accuracy number | Hides which mechanism broke. Decompose by mechanism. |
| Reaching for an off-the-shelf "helpfulness" metric | Generic metrics are worse than useless — checkout's broken while load-time improves. |
| LLM-judging something code could assert | Slower, costlier, flakier. Emit the answer first; assert on it. |
| Test cases only from your imagination | Real users send inputs you'd never invent. Harvest failures from a beta. |
| Shipping the feature with no eval at all | The #1 cause of failed AI products. Even a handful of assertions beats nothing. |
