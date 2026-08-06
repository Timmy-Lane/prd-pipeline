# Critique & Anti-Laziness Harness

The review **process** and the anti-laziness **gates**. `anti-slop.md` owns the defect *tells* (what a slop artifact looks like); this file owns *how you review* and *why AI ships slop in the first place*, plus the mechanical counters that remove the model's discretion to shortcut.

> **Boundary with `anti-slop.md` (SSOT).** Every named defect, grep, threshold, and "why it's cheap" lives in `references/anti-slop.md` and **only** there. When a gate below needs a tell, it *references* the catalog (`→ anti-slop.md § <section>`) — it never restates it. If you find yourself re-typing a defect definition here, stop and link instead. This file is the harness the catalog runs inside.

The one load-bearing idea: **slop is a workflow bug, not a taste bug.** AI ships generic, incomplete UI *on purpose* — laziness is a behavioral artifact of RLHF stopping-pressure, not a memory or capability failure (controlled 2025 tests: greedy output matched the model's own top-confidence solution; models stayed resilient across 200-turn runs). You do not fix that by explaining more. You fix it by **removing the discretion to shortcut** — mandatory sections, forbidden-pattern lists, evidence blocks, non-model gates, and pre-flight checkboxes that convert "is it good?" into pass/fail boxes the model can't fudge. Everything below is those boxes.

## Contents

1. [The critique framework](#1--the-critique-framework-how-to-review-a-ui) — isolated A/B + the geometry prohibition, cognitive-load ≤4, Nielsen as a checklist, the five-axis technical audit, P0–P3, personas, voice, instrument class, the judge-lens table
2. [The named acceptance tests](#2--the-named-acceptance-tests-does-this-effect-earn-its-place) — Wow / Removal / Device / Accessibility / Context, plus Silhouette and Name-swap
3. [The anti-laziness playbook](#3--the-anti-laziness-playbook-force-effort--completeness) — root-cause→counter, banned-output blocklist, scope-lock, grounding, verification, dials, anti-center, completeness
4. [The redesign ladder](#4--the-redesign-ladder-audit--diagnose--fix-non-destructive) — impact/risk fix order, the iteration-decay stop rule, the never-change-silently list
5. [The pointed-at defect](#5--the-pointed-at-defect) — when a human points at a pixel: the pin schema, the blast-radius layer decision, the sibling-token trap, the severity mapping

- [Cross-references](#cross-references) — which file owns the tells, the WCAG numbers, the tokens, the recipes

---

## 1 · The critique framework (how to review a UI)

Run this as a **repeatable review, not a vibe check.** Eight moves, in order.

### 1.1 Two isolated assessments, never inline

Assessment **A** (subjective LLM design review: "does this look deliberately designed?") and Assessment **B** (deterministic detector + browser evidence — the greps and judge-lens in `anti-slop.md`) run as **two parallel passes that never see each other's output.** A must finish *before* B's findings enter synthesis.

- **Why:** independence prevents the LLM from rationalizing around the detector — anchoring bias is the failure mode being engineered out. If A can see B's score, it launders it; if B can see A's prose, it stops firing.
- **Degraded run:** a single-context run (A and B in one pass) is **DEGRADED** and must be banner-flagged — `⚠️ DEGRADED: single-context critique`. A **skipped** detector pass = a **failed** run, not a lighter one.
- **Self-review transfer:** when reviewing your *own* screen, physically separate the "does this look designed?" pass from the mechanical checklist pass (run the greps in `anti-slop.md § Automatable detectors` in a distinct step) so one doesn't launder the other.

**The geometry prohibition.** Assessment A may not assert ANY of: a pixel gap, a spacing value, an alignment error, a size ratio, or an optical offset. Those claims come only from a computed measurement — `scripts/design-audit.mjs`, or `getBoundingClientRect()` / `getComputedStyle()` read in the browser.

Why: four SOTA VLMs average **58.07%** on BlindTest, seven tasks a human scores 100% on, and accuracy recovers to ~100% only when the shapes are moved further apart (arXiv 2407.06581). Nine MLLMs identify UI display issues — misalignment, crowding, overlap, overflow — at **0.2714** accuracy (arXiv 2506.06251, Finding 9). Assessment A's competence is composition, hierarchy, register, and restraint. Geometry is measured. A review that mixes the two launders a 27%-reliable claim into a 95%-reliable one.

### 1.2 Cognitive load — the ≤4 rule (Cowan, not Miller's 7)

Humans hold **≤4** items in working memory. At any decision point: **≤4** fine · **5–7** group or progressively disclose · **8+** overloaded (users skip, misclick, abandon).

Concrete caps (flag any decision point that exceeds one):

| Surface | Cap |
|---|---|
| Top-level nav | **≤5** items |
| Form fields per visual group | **≤4** before a break |
| Buttons in one cluster | **1 primary + 1–2 secondary** (rest → menu) |
| Dashboard KPIs above the fold | **≤4** |
| Pricing tiers | **≤3** |

Score the **8-item load checklist** — single focus · chunking (≤4/group) · grouping (proximity/border/shared bg) · visual hierarchy · one-thing-at-a-time · ≤4 options · no cross-screen recall · progressive disclosure. **0–1 fails = good · 2–3 = moderate · 4+ = critical.** (superdesign is `VISUAL_DENSITY` high, so density is expected — but density is *chunked* information, never an unstructured wall; ≤4 still governs each decision point.)

### 1.3 Nielsen heuristics — a checklist, not a score

Walk all 10. For each, answer ONE closed question: **is there a specific, nameable violation on this screen? (yes / no)** — with the element named. Do **not** emit a /40.

**Why the score was removed.** Absolute rubric scoring is the regime where LLM/VLM judges diverge most from humans: GPT-4V reaches Pearson 0.490 against human scores but 0.773 pairwise accuracy and 79.3% human agreement (arXiv 2402.04788). Weak judges pile up at 4/5 ("High-Score bias"). A /40 you cannot calibrate is a number that feels like measurement and is not.

**When you need a verdict, compare two candidates, not one against an absolute scale.** Generate the alternative — the previous version, or a deliberately different composition — and pick. Ties are a finding: they mean the change did not do anything.

**Run every pairwise comparison in BOTH orders.** Present (A,B), then (B,A). Declare a winner only if the same candidate wins both; otherwise TIE and fall back to the deterministic gates. Rationale: on MT-Bench "only GPT-4 outputs consistent results in more than 60% of cases" under position swap (arXiv 2306.05685 §3.1); the paper's own prescribed fix is exactly this. Also guard verbosity bias: more elements is not a better screen. If the winning candidate has more DOM nodes AND more gate findings, it loses.

### 1.4 Five-dimension technical audit — yes/no per axis, no /20

Walk five axes, kept apart from the design critique. For each, name the violation or write "none" — the same closed question as §1.3. The **/20 is deleted for the same reason the /40 is**: an absolute rubric score you cannot calibrate is not a measurement.

| Axis | Fails when | Passes when |
|---|---|---|
| **Accessibility** | no contrast/focus/keyboard | WCAG 2.2 AA verified light + dark (→ `references/accessibility.md`) |
| **Performance** | layout-property animation, scroll listeners, full-page repaints | `transform`/`opacity` only, isolated motion leaves |
| **Theming** | hardcoded colors, dark mode broken | colors are tokens, dark mode actually works (→ `references/tokens.md` §0–3) |
| **Responsive** | fixed widths, horizontal scroll on mobile | grid + `min-h-[100dvh]`, thumb-zone CTAs |
| **Anti-Patterns** (CRITICAL) | "AI slop gallery, 5+ tells" (→ `anti-slop.md` Starter Pack) | "distinctive intentional design, no tells" |

**Never report an issue without its user impact.** The Anti-Patterns axis reads directly off the `anti-slop.md` enforcement rule (§ How to run the gate, step 3): one class-D or class-S hit fails it outright; class-P tells fail it at 4+ on one screen.

### 1.5 P0–P3 severity — the support-ticket test

| Sev | Meaning | Timing |
|---|---|---|
| **P0** | blocks task completion | fix now |
| **P1** | major difficulty *or* WCAG AA violation | before release |
| **P2** | annoyance with a workaround | next pass |
| **P3** | polish, no real user impact | if time permits |

**Tiebreaker:** *"would a user contact support about this?"* → yes = **at least P1.** Prioritize ruthlessly — *"if everything is important, nothing is."* Tag every finding; don't let P3 polish noise drown a P0. (WCAG AA failures are the one class that is P1 *by definition* regardless of the ticket test — see `anti-slop.md § STATES › a11y-omission` for the thresholds.)

### 1.6 Persona selection — by interface type

Auto-pick 2–3 of five personas; report *this-persona-specific* red flags, never generic prose:

| Interface | Personas |
|---|---|
| Landing / marketing | Jordan (clarity) · Riley (edge cases) · Casey (mobile/interruption) |
| **Dashboard / admin** | **Alex** (power user: keyboard nav, bulk actions) **+ Sam** (a11y: keyboard-only flow, focus, announcements) |
| Checkout / e-commerce | Casey · Riley · Jordan |
| Data / analytics | Alex · Sam |
| Form / wizard | Jordan · Sam · Casey |

**For superdesign dashboards, ALWAYS run Alex + Sam.** A good finding is persona-anchored and specific: *"Alex: the bulk-approve action takes 8 clicks and has no keyboard shortcut"* / *"Sam: the selected-row state is conveyed by color alone, no announcement."* Never *"navigation could be improved."* (Alex's failure modes map directly to the `mouse-only-surface` / `bulk-edit-modal` tells; Sam's map to `one-layer-focus-ring` / `a11y-omission` — see `anti-slop.md § APP-UI` and `§ STATES`.)

### 1.7 Direct-feedback voice

Every issue = **What / Why it matters to users / concrete Fix.**

- Name **"the submit button,"** not "some elements." Name **"the selected-row fill,"** not "the states."
- **Cut "consider exploring…" entirely.** Don't soften. State the defect and the fix.
- Every clarifying question references a **specific finding** and offers **2–3 concrete options** — never a generic "who's your audience?" dump.
- Apply this to your own self-reviews and PR feedback, not just external critique.

### 1.8 Peak-end emotional journey

Users remember the **peak** and the **end**, not the average. Find the emotional valleys; place reassurance at high-stakes moments (destructive actions, payment, data loss, final success). Guard every destructive action with a confirming beat. Put the most reassuring copy/motion at the confirmation step and the success state.

### 1.9 Cite the instrument class, never assert authorship

Every finding names its class from `anti-slop.md § 0` and states only what that class licenses.

- **Class D:** "this is byte-identical to shadcn's shipped `--chart-4`." → *nothing was decided here.*
- **Class S:** "`#8b5cf6` is outside the ramp declared in `DESIGN.md`." → *the system was broken.*
- **Class P:** "purple heading + centred hero + three cards + Lucide Sparkles — four Starter-Pack tells on one screen." → *reads generic.* Never *"this was AI-generated."*

Never write "this looks AI-generated" in a finding. It is unfalsifiable, it is the claim the detection literature cannot support, and it is the claim that makes a review feel like an accusation rather than a critique.

### 1.10 The judge-lens — a forced table, not a free self-review

Greps see textual tells; they cannot see the absence of a behaviour. After `scripts/anti-slop-gate.sh` exits 0, emit this table and fill **every** row. An empty Evidence cell is a FAIL — the Evidence column is the oracle, and a self-review without one is the failure mode Huang et al. (2024) measured. Fill the Evidence column before the Verdict column; the row order is fixed.

| Tell | Evidence in this screen | Verdict |
|---|---|---|
| Keyboard path (⌘K, row nav, shortcuts) | | |
| Full state machine (focus/disabled/loading/empty/error) | | |
| Hierarchy from spacing + weight, not color | | |
| Density tier (compact/comfortable) exists | | |
| ⌘K opens at 0ms | | |
| Optical layout (the five checks below) | | |

**Optical layout** — the checkable items, all measured, never eyeballed (→ §1.1 geometry prohibition):

- concentric radii satisfy `inner = outer − (padding + border)`, per corner;
- top and bottom whitespace inside every button/badge/chip measure within **1px** of each other, or `text-box: trim-both` is applied;
- an icon is centred on the **cap band**, not the line box — `optical_offset = ((ascent − descent) − capHeight)/2` em;
- a triangle/chevron in a circular button is nudged by **w/6, capped at 2px**, in the pointing direction — and **symmetric glyphs get zero nudge; a speculative nudge is itself a finding**;
- flush-left display headings ≥32px carry `margin-inline-start: -0.05em`; body text never does.

---

## 2 · The named acceptance tests (does this effect earn its place?)

Before an effect, animation, decoration, or flourish ships, run it through the relevant test. A "no" is a cut, not a debate. Use these to decide *whether an element earns its place* — they are the qualitative complement to the mechanical greps in `anti-slop.md`.

| Test | The question | Fail ⇒ |
|---|---|---|
| **Wow** | Does this create a genuine moment of delight, or is it motion for motion's sake? | Cut it — it's `scattered-fades` (→ `anti-slop.md § MOTION`). |
| **Removal** | If I delete this effect, is the UI *worse*? | If not worse, it wasn't doing work — remove it. |
| **Device** | Does it hold up on a mid-range phone at 60fps, and honor `prefers-reduced-motion`? | Isolate + gate it, or cut it (→ audit §1.4 Performance). |
| **Accessibility** | Keyboard-reachable, focus-visible, not conveyed by color/motion alone, announced to SR? | Fix or cut — a P1 by the support-ticket test. |
| **Context** | Does it match the product register (superdesign product = low `DESIGN_VARIANCE`/`MOTION_INTENSITY`), or is it borrowed award-site flair? | Down-tune to register; marketing surfaces may keep more. |

The **Removal test is the sharpest** — most slop survives because no one asked whether deleting it would hurt. Default to removal; make each effect *earn re-entry*.

Two more tests run on the **whole page**, not on one effect. They catch the slop that no per-element test can see, because the defect is the shape of the page and the register of the copy.

| Test | The question | Fail ⇒ |
|---|---|---|
| **Silhouette** | Reduce the page to a 200px black-on-white silhouette (blocks for sections, lines for text, circles for avatars). Lay it beside five competitors. Can you pick yours out? | Structural slop. Fix the section sequence, not the palette. |
| **Name-swap** | Replace the product name with a direct competitor's throughout the copy and read it aloud. Does it still work? | The copy describes a category, not a product. Rewrite from a real customer sentence. |

---

## 3 · The anti-laziness playbook (force effort & completeness)

### 3.1 Why AI ships generic/incomplete UI — root cause → counter

Spend your prompt budget on **prohibitions and gates**, not on re-teaching Tailwind. The model already knows; it is *choosing* to shortcut.

| Root cause | Mechanism | Counter |
|---|---|---|
| **Laziness is a choice** | RLHF stopping-pressure + effort thresholds — *not* a memory bug (proven: greedy output = the model's own top solution) | Spend budget on prohibitions + gates, never on re-explanation. Re-prompting "you forgot X" treats a choice as amnesia and burns tokens. |
| **Effort-threshold trigger** | Fires when the task *looks* easy **OR** context is *excessively long* | Never frame a component as "just a card"; frame it as production-critical. Keep working context tight — lazy-load references as skills, don't paste them inline. |
| **Error-avoidance truncation** | Longer output = more error surface = riskier, so it bails early | **Ground** the work (real-feeling data, fetched shadcn API) so *more UI ≠ more risk.* |
| **Context-window asymmetry** | Output hard-capped (~8K) even with huge input; the model pre-compresses the whole answer to dodge a cutoff | **Chunk:** outline → each panel → wire-up. Never one-shot "build the whole app." |
| **Consumer middleware pruning** | Web apps silently prune earlier instructions (~32K history cap) | Keep the design system in a loaded skill / CLAUDE.md, not pasted early in a chat that gets pruned. |

### 3.2 The banned-output blocklist (hard failures — never emit)

Treat every item as a **hard fail**; run it as a recheck/lint gate on generated code and copy.

- **In code:** `// ...` · `// rest of code` · `// implement here` · `// TODO` · `/* ... */` · `// similar to above` · `// continue pattern` · `// add more as needed` · bare `...`
- **In prose:** "for brevity" · "the rest follows the same pattern" · "similarly for the remaining" · "and so on" · "I'll leave that as an exercise" · "Let me know if you want me to continue" · "I can provide more details if needed"
- **Structural:** skeleton-instead-of-implementation · first+last-section-skip-middle · one-example-plus-a-description · describing-code-instead-of-writing-it
- **House style, in shipped copy:** no `—` em dash and no `–` en dash anywhere visible; ranges use a hyphen (`2018-2026`). This is a **style rule, not a detection signal** — the detection signal is the *spaced* em dash and it is class P, density only (→ `anti-slop.md § CONTENT › spaced-em-dash`). Do not let a house-style violation block a ship on its own.

If output would exceed the token budget, do **not** compress or skip to a conclusion. Write at full quality to a clean breakpoint and end exactly with `[PAUSED — X of Y complete. Resume from: <next section>]`; on continue, resume with no recap.

### 3.3 Scope-lock-then-cross-check

Converts "did I do enough?" (a discretion the model shortcuts) into a **mechanical equality check** it can't fudge.

1. **Scope** — read the full request, count distinct deliverables (files / components / sections / cards), **lock that number.**
2. **Build** — generate each one completely.
3. **Cross-check** — re-read the original request, compare the count to the lock, add anything missing *before* responding.

*"Build 6 dashboard cards"* → lock **6** → verify **6** exist. *"Make several components"* with no lock is how the model delivers two and stops.

### 3.4 Grounding over weights

**Never write a component from memory when the canonical source is one HTTP GET away.** A shadcn registry is JSON over HTTPS at a templated path — `components.json` maps a namespace to `https://<host>/r/{name}.json` — so real, current source is retrievable with WebFetch or `curl`, with nothing installed. Verified live 2026-07-26: `https://magicui.design/r/marquee.json` returns `{$schema, name, type, title, description, files, cssVars, css}` with the component body inside `files`.

**Tier 1 — always available, always first.** Fetch the registry item, read `files`, and build from that text. Fetch `https://<host>/r/registry.json` first when you need to know what exists.

**Tier 2 — optional, only if the server is actually connected.** The shadcn registry MCP (`pnpm dlx shadcn@latest mcp init --client claude`) does the same job conversationally. Refer to any MCP tool by its **fully qualified** `ServerName:tool_name`; never guess a bare tool name — without the server prefix the tool may not resolve, and the shadcn MCP's tool names are not published anywhere, so a guessed name is a fabrication. If the server is not connected, fall back to Tier 1; do not ask the user to install it mid-task.

Verify the stack against the skill's stated requirements (`SKILL.md`, top) and `package.json` — never from assumption. Tailwind v4 is confirmed for superdesign; don't emit v3 config.

### 3.5 Verification loop before "done"

**A verification loop is only a verification loop if a NON-MODEL signal enters it:** an exit code, an axe result, a computed style, a rendered pixel, a human. "Grade your own draft against the rubric" is not verification — it is a second draft. Stechly et al. (arXiv 2310.12397) find iterative self-critique performs *worse* than a single direct answer on a verifiable task, and that where an external verifier does help, *"the actual content of iterative back prompts is not important"* — the verifier is doing the work, not the critique. Where you have no external signal, do not loop: fork more candidates and let the deterministic gates break the tie.

Never single-pass. End with one of:

- **Reference-guided grading (preferred).** Before critiquing the draft, build your OWN version of the same screen from the brief, without looking at the draft. Then critique the draft against that reference. Measured effect on grading-failure rate: default 14/20 → CoT 6/20 → **reference-guided 3/20** (arXiv 2306.05685, Table 4).
- **Chain-of-verification (fallback).** Answer → generate verification questions about your own claims → answer them independently → revise. Note: CoT reduces hallucination but does **not** improve agreement with human preference and sometimes lowers it (arXiv 2402.04788 §4.6) — use it for factual self-checks, not as an alignment mechanism.

These loops **consume the shortcut budget** — the model must re-read and re-justify, which crowds out lazy summarization. The terminal check is the non-model one: `scripts/anti-slop-gate.sh` and `scripts/design-audit.mjs` exiting 0, against `anti-slop.md § Catalog` + the pre-flight boxes below.

### 3.6 Parameter dials (API-level control)

- Structured UI code: **temp 0.0–0.5, top-p 0.0–0.6** — sharpens the softmax so the model commits to the *full* continuation instead of a truncating token.
- Reasoning **medium/high** for code — but **do not pair floor-temp with `high` thinking** (induces reasoning loops).
- Reserve **temp 1.5+** for concept ideation only, then **drop to floor to implement.**

### 3.7 Anti-center discipline (defeat the statistical default)

LLMs always pick the first (blandest) layout option. Break the loop mechanically:

- **Simulate a deterministic RNG in a `<design_plan>`** (seed off prompt char-count) to *choose* hero architecture, type stack, and component architectures — then follow the draw. **Forbidden to default to the same UI twice.**
- **`DESIGN_VARIANCE > 4` → centered heroes BANNED** — force split-screen / left-content-right-asset / asymmetric whitespace. (superdesign product is low-variance, so this bites mainly on marketing surfaces; the *discipline* — don't reflex to the center — still applies to product layouts.)
- **`VISUAL_DENSITY > 7` → generic card boxes BANNED, `font-mono` mandatory on all numbers** — group with `border-t` / `divide-y` / negative space. (This is superdesign's product default — see `anti-slop.md § APP-UI › card-soup` and `proportional-numerals`.)
- **The 2-line iron rule:** an H1 never exceeds 2–3 lines (4–6 = catastrophic failure). Fix with a *wider* container (`max-w-5xl`) + `clamp(3rem, 5vw, 5.5rem)`, never a narrow box that wraps six lines.
- **Cap the artifact, don't sharpen the prompt.** Total lines of code is a near-perfect predictor of architectural decay in agent-generated systems, and few-shot prompting measurably *failed* to reduce the bloat (arxiv.org/abs/2605.02741). The counter is a hard per-component budget — **≤150 lines per component file, ≤5 props, one data source** — enforced at the scope-lock step (§3.3), not a longer instruction.

### 3.8 Mandatory completeness (the states AI forgets)

Every data component ships all three — this is a **hard gate**, not a nicety (→ `anti-slop.md § STATES › no-empty-loading-states` for the response-time ladder and empty-state anatomy):

- **Loading** — skeletons matching the layout shape, **NOT** spinners.
- **Empty** — composed, shows how to populate (one imperative CTA); filter-empty echoes the query and offers a next step.
- **Error** — inline under the field, **never** `alert()`.

Plus tactile `:active` feedback (`-translate-y-[1px]` / `scale-[0.98]`) and a `focus-visible` treatment paired to every hover/active change (keyboard parity).

---

## 4 · The redesign ladder (audit → diagnose → fix, non-destructive)

**Never rewrite from scratch — improve what's there.** Each rung leaves a shippable improvement, ordered by impact/risk.

**Step 1 — Scan.** Read the codebase: framework, styling method, current patterns. Detect mode — Greenfield / Redesign-Preserve / Redesign-Overhaul. Ask **once** if genuinely ambiguous, otherwise infer.

**Step 2 — Diagnose.** Run the full §1 critique + the `anti-slop.md` catalog. List every generic pattern, weak point, and missing state. Read the *existing* site's dial values (that's your starting point, not the baseline). **Extract the existing brand color before applying any de-purple rule** — a brand that is *already* purple stays purple.

**Step 3 — Fix, in impact/risk order** (front-load the biggest wins at the lowest risk):

1. **Font swap** — biggest instant win, lowest risk (~70% of the value at ~40% of the risk). (→ `anti-slop.md § TYPOGRAPHY › default-font`.)
2. **Color palette cleanup** — remove clashing/oversaturated hues; recalibrate but **keep the brand accent** (→ `anti-slop.md § COLOR`).
3. **Hover / active states** — makes it feel alive (→ `anti-slop.md § MOTION › dead-hover`).
4. **Layout & spacing** — grid, max-width, consistent 4px-scale padding (→ `anti-slop.md § LAYOUT`, `§ STATES › inconsistent-spacing`).
5. **Replace generic components** — swap the named fingerprints (→ `anti-slop.md § Catalog`): three-equal-cards → bento/asymmetric; colored side-strip → full ring or spacing; pure `#000` → off-black.
6. **Add loading / empty / error states** — skeletons shaped to the layout, composed empty, inline errors, active-nav indicator, branded 404 (§3.8).
7. **Polish type scale & spacing** — the premium final touch (→ `references/tokens.md` §4–5).

**Stop rule — the critique decays as the screen improves.** One repair pass per **new external signal**, and at most **two** model-critique passes on one screen. A loop that introduces no new signal is banned outright. Pass 1 finds real defects; by pass 3 the suggestions are measurably worse than the design (Duan et al., CHI 2024: LLM heuristic-evaluation accuracy *falls* as the UI improves; only 9 of 100 violations were LLM-only vs 62 human-only). After pass 2, switch instruments: run the deterministic gates (`scripts/anti-slop-gate.sh`, `scripts/design-audit.mjs`) and, if you still want a verdict, generate a genuinely different alternative and compare the two in both orders (§1.3). Do not keep asking the model what's wrong — you will get plausible, invalid P3 noise that displaces real work.

**Hard redesign rules:** don't migrate frameworks/styling libs; **test after every change** (don't break functionality); check `package.json` before any new import; lock Tailwind v3-vs-v4 before touching config; keep changes small and reviewable.

**Never change silently** — these break SEO / analytics / muscle-memory and are invisible in a mockup (the #1 redesign risk):

- URL / route slugs
- Primary nav labels
- Form field **names and order** (breaks autofill *and* analytics)
- Brand logo / wordmark
- Legal / consent copy

---

## 5 · The pointed-at defect

Everything above reviews work the model can see. This section covers the other direction: a human
points at a rendered element and says one sentence. That sentence is the **new external signal**
§3.5's stop rule demands — the only kind of iteration that is not theatre.

**The failure it prevents is not "we misunderstood the user".** It is that a complaint about a
screen gets fixed on the node the finger landed on. A one-off `className` at a call site is a named
defect (SKILL.md § Phase 2 → "Add a variant, never a call-site override"), so a review loop that
produces node patches manufactures the exact slop this file gates. **The layer is decided before the
fix, mechanically, and never by reading the sentence.**

**One command turns a dev server into a surface you can point at:**

```bash
node scripts/pin.mjs --dir <project>     # → open the URL it prints, alt-click things
node scripts/pin-report.mjs --dir <project>
```

`pin.mjs` probes the usual dev ports, puts itself in front of whichever answers, and injects
`pin-overlay.js` into every HTML response it proxies — including the websocket, so HMR keeps
working. **Nothing is installed into the project**: no plugin, no script tag, nothing that could
reach a production build. Pass `--app <url>` when the port is unusual and `--no-proxy` when the
project already injects the overlay itself.

**Then alt-click, one sentence, enter.** The overlay walks the CSSOM rather than
`getComputedStyle`, because computed values are the specified value *with `var()` already
substituted* — by the time you read `oklch(0.542 0.205 27)` the token name is gone. The declared
value survives in CSSOM and names it exactly. A pin leaves a numbered marker on its element;
the ring is the accent when a token owns the pixel and amber when nothing does, which is the layer
decision below made visible before the sentence is even typed. Pins land in `window.__sdPins` and
in `<project>/.superdesign/pins.jsonl`.

**Alt+shift+drag instead where an element is missing.** That pin (`kind: "add"`) names no element,
because there is not one yet: it names the parent that would hold it, the index between which two
named siblings, and the box that was drawn. It is the answer to the other half of a design
complaint, and it exists because "instead create kanban here" alt-clicked onto the nearest button
cannot say whether the kanban replaces that button, sits beside it, or goes in the other panel.

**The layer decision — one `querySelectorAll`, not a judgement call:**

| The winning rule reaches | Layer | The edit |
|---|---|---|
| **>1 distinct `data-slot`** | **TOKEN** | one line in the theme; every consumer moves together |
| **exactly one `data-slot`** | **VARIANT** | a row in that component's `cva` table — never the shared token |
| **one node, no owning component** | **OVERRIDE** | already a defect. Delete it, add a variant. Report it as one. |
| **an inline `style` attribute** | **OVERRIDE** | never a design decision; always a leak |
| **no `data-slot` anywhere** | **NODE** | the project has no component boundary to hang a variant on — say so rather than inventing one |

**The sibling trap, which no screenshot can show.** Several tokens routinely carry a byte-identical
value, and moving one silently leaves the rest behind — fixed on the pinned screen, broken two
routes away. Measured on a real project, 2026-08-05: `--primary` shares `oklch(0.542 0.205 27)` with
`--destructive`, `--ring`, `--sidebar-primary` and `--sidebar-ring` in `:root`, **and again in
`.dark`** at a different value. Eight declarations, one intent. `pin-report.mjs` scans the theme file
per block and names them; the in-page overlay names only the ones live in the current mode, which is
why the report reads the file and the overlay does not.

That scan is also a **design finding in its own right**: a brand hue identical to the destructive hue
means colour cannot distinguish "publish" from "delete", which is § Accessibility's "colour is never
the only signal" failing before anyone opened axe.

**Severity, read off the resolution and never off the sentence** (→ §1.5 for the scale):

| Resolution | Severity |
|---|---|
| the token is also the `--ring` or a state colour, or the sibling set crosses semantic roles | **P0** |
| TOKEN, and the value fails a contrast floor in either theme | **P0** |
| OVERRIDE | **P1** — a defect the user did not know they were pointing at |
| no property resolved to any token, on a pin that points AT an element | **P1**, and it is a *Phase 1* finding: the value is hard-coded, so there is no system to correct |
| TOKEN or VARIANT, no contrast consequence | **P2** |

**A pin that resolves to no token is returned, not answered.** It means the surface was built without
a token baseline; patching the pinned value hides that and leaves the next forty values wrong. Say
which phase failed and repair the baseline. **An `add` pin is the one exception**: it points at the
gap between two elements, so it resolves the *parent's* styling and having no token of its own is
what it is rather than a defect it found. `pin-report.mjs` exempts it from the exit code for exactly
that reason — answer it by building the thing, in the layer the parent's resolution names.

**Two limits, both structural.** Cross-origin and `file://` stylesheets are not origin-clean, so
`cssRules` throws and resolution returns nothing — the pin carries `blockedSheets` and the report
refuses to pretend; serve over `http://localhost`. And the pin records one viewport and one theme,
because a `@media` context is part of the answer: the same node at 1440 and at 390 can resolve to
different owners, and both are correct. Pin at both, or state which one you pinned.

---

## Cross-references

- **Defect tells, greps, thresholds, "why it's cheap"** → `references/anti-slop.md` (SSOT). This file never restates them.
- **WCAG 2.2 AA full checklist** (the a11y numbers behind §1.4 Accessibility, §1.5 P1, Sam's persona) → `references/accessibility.md`.
- **Tokens** (the color/type/spacing/elevation/motion systems the audit scores against) → `references/tokens.md` (incl. §11 app-UI product defaults).
- **Composition recipes** (the vetted layouts the redesign ladder swaps *toward*) → `references/cookbook/*.md`.
- **SKILL.md Phase 4** invokes this harness + `anti-slop.md` as the "before done" gate.
