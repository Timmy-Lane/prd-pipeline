# Verification — what counts as evidence in this loop

Phases 4, 5 and 6 all make the same claim: *this is done.* This file is the evidence standard behind
that claim. It is not a checklist — the checklists live in `anti-slop.md` (tells),
`accessibility.md` (conformance) and `critique.md` (process). This file answers the prior question:
**which signals are allowed to close a gate, and which only feel like they do.**

One rule governs the whole file:

> A verification loop is only a verification loop if a **non-model signal** enters it — an exit code,
> an axe result, a computed style, a rendered pixel, a human. "Grade your own draft against the
> rubric" is not verification, it is a second draft. Where there is no external signal, do not loop:
> fork more candidates and let the mechanical score break the tie (arXiv 2310.12397).

## Contents

1. [A checker in the loop is worth +3.0 — and more context is worth −3.0](#1-a-checker-in-the-loop-is-worth-30--and-more-context-is-worth-30)
2. [axe-core: 57% of WCAG, zero false positives](#2-axe-core-57-of-wcag-zero-false-positives)
3. [Never measure from a screenshot — query the DOM](#3-never-measure-from-a-screenshot--query-the-dom)
4. [Screenshot-in-the-loop: +0.3 to +2.2 on a frontier model, −36 on a weak one](#4-screenshot-in-the-loop-03-to-22-on-a-frontier-model-36-on-a-weak-one)
5. [The stop rule, and the numbers behind it](#5-the-stop-rule-and-the-numbers-behind-it)
6. [How the render gate's caps were calibrated](#6-how-the-render-gates-caps-were-calibrated)

---

## 1. A checker in the loop is worth +3.0 — and more context is worth −3.0

SWE-agent ([arXiv 2405.15793](https://arxiv.org/abs/2405.15793), Table 3). SWE-bench Lite, GPT-4
Turbo, ablating one interface element at a time from the 18.0 baseline:

| Ablation | Score | Δ |
|---|---|---|
| **Full agent-computer interface** (edit with linting, summarized search, 100-line viewer, last-5 observations) | **18.0** | — |
| Edit action **without** linting | 15.0 | **−3.0** |
| No structured edit command at all | 10.3 | −7.7 |
| **Full history** instead of last-5-observations | 15.0 | **−3.0** |
| File viewer 30 lines | 14.3 | −3.7 |
| File viewer full file | 12.7 | −5.3 |
| Iterative search UI | 12.0 | −6.0 |
| No search | 15.7 | −2.3 |
| No demonstration | 16.3 | −1.7 |

Two rows carry the whole table.

**A linter in the edit loop is worth +3.0 absolute — a 20% relative lift — for free, deterministically,
with no extra model call.** That is the entire argument for `scripts/anti-slop-gate.sh` and
`scripts/design-audit.mjs` being commands rather than prose. The paper's own framing: *"Guardrails
mitigate error propagation and hasten recovery… a code syntax checker that automatically detects
mistakes can help agents recognize and quickly correct errors."*

**Keeping the full history is worse than keeping the last five observations, by the same 3.0 points.**
More context actively hurt. This is why the phase gates emit ~10 lines of script output instead of
loading three reference files, and why the reference-map load budget exists at all.

Transfer caveat: this is a coding benchmark, not a design one. The mechanism — a deterministic
checker closing the loop — is what transfers; the magnitude is not claimed for UI.

## 2. axe-core: 57% of WCAG, zero false positives

Deque's own published figures for axe-core: *"you can find on average **57% of WCAG issues
automatically**"* and *"it returns **zero false positives** (bugs notwithstanding)."* Where a rule
needs a human, axe returns `incomplete` rather than guessing.

That pair is the best cost-to-quality ratio available to this skill. A ~2-second run settles more
than half the conformance surface with no false alarms, which is what earns the Phase-5 instruction
to load `accessibility.md` **only** for the items axe marks incomplete. An axe `violation` is not a
suggestion; it is a defect with a node reference.

What axe cannot do bounds the claim honestly: the remaining ~43% is judgement — focus order that is
technically valid and cognitively wrong, an `aria-label` that is present and useless, a live region
that fires at the wrong moment. Those are Phase 5's manual items, and they are the reason the phase
does not end at the exit code.

## 3. Never measure from a screenshot — query the DOM

BLINK ([arXiv 2404.12390](https://arxiv.org/abs/2404.12390)) ran 17 multimodal LLMs on low-level
perception tasks humans solve in seconds. **Humans 95.70%; GPT-4V 51.26%** — 13.17 points above
random guessing. Specialist CV models beat GPT-4V by 62.8 points absolute on visual correspondence,
38.7 on relative depth, 34.6 on multi-view reasoning.

*"Is the card padding 24px and the gap 32px, so `internal ≤ external` holds?"* is a relative-metric
perception question — exactly the class BLINK shows vision models fail. `getComputedStyle` answers it
exactly, for about thirty tokens.

**The rule: never ask the model to measure from a screenshot. Ask the DOM.** Anything with a number
in it — spacing, contrast ratio, shadow count, outline width, animated property — goes through
`getComputedStyle` / `getBoundingClientRect` / axe inside `scripts/design-audit.mjs`. Screenshots are
for *gestalt* only: does this read as designed, is the hierarchy legible in grayscale, is the accent
scarce, does anything overflow at 390px. That is the judgement class a model is actually good at, and
it is all Phase 6 asks of one.

## 4. Screenshot-in-the-loop: +0.3 to +2.2 on a frontier model, −36 on a weak one

Design2Code ([arXiv 2403.03163](https://arxiv.org/abs/2403.03163), Si et al.), 484 curated real-world
webpages. Its *self-revision* condition is exactly screenshot-in-the-loop: the model is given the
reference screenshot, **a screenshot of its own rendered output**, and its own code, and asked to
close the gap. Text-Augmented → Self-Revision:

| Model | Block | Position | CLIP |
|---|---|---|---|
| GPT-4o | 92.4 → **92.7** | 84.5 → **84.9** | 89.9 → **90.1** |
| GPT-4V | 87.6 → **88.8** | 80.2 → **81.1** | 87.2 → 87.2 |
| Claude 3 Opus | 89.8 → **90.3** | 75.9 → **78.1** | 86.6 → 86.6 |
| Gemini 1.0 Pro Vision | 84.8 → 84.1 ▼ | 70.4 → 70.1 ▼ | 84.4 → 84.3 ▼ |
| LLaVA-1.6-7B | 68.4 → 62.6 ▼ | 68.7 → 64.7 ▼ | 84.5 → 83.8 ▼ |
| DeepSeek-VL-7B | 66.1 → **30.1** ▼▼ | 69.2 → 28.9 ▼▼ | 84.3 → 79.9 ▼ |
| Idefics2-8B | 23.6 → 12.3 ▼▼ | 35.7 → 13.2 ▼▼ | 78.7 → 78.4 |

The paper's own summary: *"Self-revision has some minor improvement on block-match and position
similarity for GPT-4V and Claude 3, but brings no improvement on Gemini Pro Vision and all other
open-source models."*

**Honest reading: roughly +0.3 to +2.2 points of layout fidelity on a frontier model, nothing on a
mid model, and catastrophic on a weak one (−36 on DeepSeek-VL-7B).** Phase 6 is therefore worth
running here and is not a technique to recommend generically. Human annotators were more favourable
than the automatic metrics — 49% of GPT-4V self-revision pages were judged interchangeable with the
human-built reference and 64% *better designed* — but Fleiss' κ was 0.32 and 0.26, fair-to-slight, so
both figures are directional, not precise.

The same paper supplies the strongest argument for writing copy before markup: text-augmented
prompting *"successfully increases the block-match score and text similarity score on most tested
models"* and is the best non-self-revision method on every open model tested (§4.1).

## 5. The stop rule, and the numbers behind it

**Repair once per new signal, then stop.** Fix every P0/P1 the gate reported, re-run it, exit 0 or
stop and report. Every additional loop must introduce a signal the previous loop did not have — a new
script run, a new render, a human. At most **two** model-critique passes on one screen.

Why the ceiling is two, not "iterate until it looks right":

- Huang et al. ([arXiv 2310.01798](https://arxiv.org/abs/2310.01798), Table 3): under repeated
  *intrinsic* self-correction — no external feedback — GPT-4 on GSM8K goes **95.5 → 91.5 → 89.0**,
  and GPT-3.5 on CommonSenseQA goes **75.8 → 38.1**. The loop does not converge; it decays.
- Self-Refine ([arXiv 2303.17651](https://arxiv.org/abs/2303.17651)) reports that on the one task
  class where its feedback could be checked, the model's own feedback said *"everything looks good"*
  for **94%** of instances. Self-generated feedback saturates before the artifact does.
- Stechly et al. ([arXiv 2310.12397](https://arxiv.org/abs/2310.12397)): iterative self-critique
  performs *worse* than a single direct answer on a verifiable task, and where an external verifier
  does help, *"the actual content of iterative back prompts is not important"* — the gain is
  equivalent to sampling more and letting the verifier pick.
- Duan et al. (CHI 2024) found LLM heuristic-evaluation accuracy *falls as the UI improves*: on their
  corpus, **9 of 100** violations were LLM-only against **62** human-only.
- UICrit: *"only 13.1 percent of the design comments generated by Gemini were valid."*

The practical consequence for this skill: pass 1 of the judge-lens finds real defects. Pass 2 is
allowed. Pass 3 is measurably worse than the design it is critiquing. If two passes have not closed
it, the missing thing is a signal — a render, an axe run, a person — not another opinion.

---

## 6. How the render gate's caps were calibrated

`scripts/design-audit.mjs` enforces caps. A cap is only evidence if a known-good screen and a
known-bad one land on opposite sides of it, so each was set by sweeping three classes and putting
the number in the gap — `scripts/calibrate-caps.mjs` is that sweep, kept so the numbers can be
re-argued from data rather than from taste.

| Class | Corpus |
|---|---|
| **good** | the five gate-clean pages in `examples/` — four static landings + the React `app-ui` |
| **slop** | `scripts/fixtures/slopped-geometry.html`, a plausible marketing page with deliberately undisciplined geometry |
| **wild** | linear.app · stripe.com · ui.shadcn.com — not a target, a reality check on what shipped products score |

**Capped, with the observed spread:**

| Metric | Cap | good | slop | wild | Why the number |
|---|---|---|---|---|---|
| `offGrid` | 0 | 0 | 14 | 0 · 8 · 8 | odd spacing values. No Tailwind step, half or full, is odd — an odd value is hand-typed |
| `off4` | 8 | 2–3 | 17 | 4 · 14 · 17 | off the 4px grid. Tailwind's `.5` steps (`px-3.5` = 14px) land here legitimately, so the cap sits in the real 4→14 gap |
| `shadows` | 3 | 0–3 | 6 | 3 · 4 · 12 | distinct live recipes, zero-alpha layers dropped. Also the sourced ≤3 rule |
| `transition: all` | 0 | 0 | 1 | 0 · 4 · 8 | the wildcard sweeps layout in behind you |
| focus ring · axe | 0 | 0 | 0 | 15 · 22 · 22 | — |

**Measured NOT to separate — printed every run, never capped.** Each scored the slop fixture *at or
below* the known-good pages, so a threshold would have failed real work while passing slop:

| Metric | good | slop | Why it fails as a gate |
|---|---|---|---|
| `nearMiss` | 0–11 | 2 | counts how many block edges land 1–3px apart, which tracks how many boxes a page has. The *pairs* are actionable; the count is not |
| `fontSizes` | 7–13 | 12 | computed sizes include inherited and rem-derived values — a larger population than the CSS-declared count `anti-slop.md` caps at 8 |
| `spacingSteps` | 9–17 | 18 | one step apart |
| `radii` | 1–7 | 8 | one step apart; `tokens.md` wants one `--radius` derived, not a step count |
| `layoutAnim` | 0–7 | 2 | shadcn's own Sidebar ships `transition-[left,right,width]`, so the React reference scores 7 by using it as published. A sidebar collapse has to animate width |

Three of these metrics originally measured the *harness*, not the page, and every one of them looked
plausible while doing it — which is the general lesson. Host `reducedMotion` was left unset, so on a
machine that prefers reduced motion the page's own `@media (prefers-reduced-motion)` block
activated and the animation census reported that reset on every element. `transition-property` was
read where no transition runs, and it defaults to `all`. And counts were of elements rather than
distinct values, so one off-grid padding on a card repeated forty times read as forty defects.

**Never move a cap to make a screen pass.** Re-run the sweep and show a new gap, or fix the screen.
