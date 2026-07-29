---
name: superdesign
description: >-
  Design and build top-tier, brand-specific UI with React + Tailwind v4 + shadcn/ui via a
  system-first workflow (brand → OKLCH tokens → cookbook patterns → polish → anti-slop & a11y
  gates) that defeats generic "AI-slop" output. Use for ANY UI/UX work — building or restyling a
  component, screen, page, dashboard, landing, marketing site, or design system; choosing
  colors/typography/spacing/radius/shadow/motion; theming or composing shadcn/ui; or whenever an
  interface looks generic, "AI-generated", or off-brand. Triggers include "build a landing page",
  "design a dashboard", "make this look better", "restyle this component", "pick a color palette",
  "this looks AI-generated", "set up shadcn theming". Do NOT use for backend logic, data modelling,
  build configuration, or copywriting unattached to a surface.
license: MIT
---

# superdesign

A design-system *generator*, not a fixed theme.

**Requires** React 19, Tailwind CSS v4 (CSS-first, no `tailwind.config.js`), and shadcn/ui
new-york style. Tailwind v3 is not supported. Phases 5–6 and reference mining need a browser:
**`Skill(silver)` is the default** (→ Phase 0); chrome-devtools MCP or a project-local Playwright
also work.

## Non-negotiables

These 12 apply to every UI task, from this line onward — not at the end. Everything else in this
file is elaboration. Phases 4–6 are how you *verify* these, not when they start applying.

1. MUST write the token file before any component markup.
2. MUST author color in OKLCH and use shadcn semantic names only in markup (`bg-primary`, never
   `bg-zinc-900`, never a raw hex).
3. MUST name the aesthetic in one phrase before choosing anything ("warm editorial", "precise
   fintech"). A named aesthetic is the input to every later decision.
4. MUST put the saturated brand hue in the ~10% accent role, not across surfaces.
5. MUST compose screens from `references/cookbook/` recipes. Read the recipe first.
6. MUST keep every spacing value on the 4px grid, and keep card padding ≤ inter-card gap.
7. MUST carry hierarchy with weight + gray level before size or color; the screen reads correctly
   in grayscale.
8. MUST ship rest / hover / active / focus-visible / disabled / loading for every interactive
   element, plus empty and error where data can be absent.
9. MUST route all motion through the two named curves — `--ease-out-quint` for entrances,
   `--ease-ios` for micro-interactions — keep UI motion ≤ 300ms (Phase 3 names the one carve-out),
   and animate only `transform` and `opacity`. Use 0ms for keyboard-initiated surfaces (⌘K, menus,
   filters).
10. MUST ship a visible `:focus-visible` outline (2–3px solid, `outline-offset: 2px`) and pass
    4.5:1 text contrast in light AND dark.
11. MUST run the gate commands named in Phases 4 and 5 before claiming done. Each must exit 0.
12. MUST use real domain copy. No lorem, no fake testimonials, no unsourced stats.

## Project state (auto-injected — this is ground truth, do not re-derive it)

```!
test -f package.json && node -e "const p=require('./package.json');const d={...p.dependencies,...p.devDependencies};for(const k of ['tailwindcss','react','next','motion','framer-motion','lucide-react','sonner','tw-animate-css','class-variance-authority','tailwind-merge'])if(d[k])console.log(k+' '+d[k])" 2>/dev/null || echo "no package.json — static mock-up target"
test -f components.json && cat components.json || echo "no components.json — shadcn not initialised"
grep -l -r --include=globals.css --include=theme.css -e '@theme' . 2>/dev/null | head -3 || echo "no Tailwind v4 @theme block found — Phase 1 has not run"
```

No `@theme` file above means **Phase 1 has not run and no markup may be written**. Tailwind v3
means stop and say so — this skill targets v4 only. If the block rendered as `[shell command
execution disabled by policy]`, read those three files by hand before starting Phase 1.

## What this does

Produce UI that looks **deliberately designed for its brand**, not generated. The default failure
mode of any model is convergence on the statistical center of every SaaS template it was trained on
("AI slop"): Inter, indigo, purple gradients, centered hero + three cards, one flat shadow, no real
states. This skill defeats that with a **system-first workflow** — commit to a brand, generate a
token system, compose from vetted patterns, then gate the result — instead of hand-writing markup
that drifts toward the mean.

**Separate the three jobs.** Slop comes from fusing them in one prompt: (1) *taste direction* —
what should this feel like, (2) *exploration* — what are the options, (3) *spec/build* — what
exactly to build. Do them in order, in separate phases. **Self-diagnostic:** reacting to your own
output with adjectives ("cleaner", "more premium", "less generic") means the jobs are still fused —
stop and go back to Phase 1.

---

## The loop

Run these phases **in order** for any UI task. Never skip to markup. Paste this checklist into your
working notes and check each box before moving on.

```
[ ] Phase 1  Brand → brief → preset → tokens exist and are committed to CSS
[ ] Phase 2  Screen composed from cookbook patterns using semantic tokens only
[ ] Phase 3  Polish pass: spacing rhythm, optical alignment, full state matrix, motion
[ ] Phase 4  Anti-slop gate passed (script exits 0; three forked candidates judged)
[ ] Phase 5  Accessibility gate: palette + render commands exit 0; the rest judged by hand
[ ] Phase 6  Rendered and inspected: screenshot read at 1440 + 390, a11y audit clean, console clean
[ ] Quality bar met (see end)
```

**Default to discussion for the first turn of any new surface.** Produce the Design Brief and one
sentence of layout intent, then stop — unless the user used an action word (build, implement, code,
make it, ship). Ambiguity resolved before Phase 2 is free; ambiguity resolved after Phase 3 costs a
rebuild. If one thing is genuinely unclear, ask once, then proceed on a stated assumption. Never
ask twice.

**App-UI targets need a scaffold first — a one-time pre-step, NOT part of the loop.** For a real
React + Tailwind v4 + shadcn/ui *product* surface (dashboard, data table, ⌘K palette), run
`npm create vite` + `shadcn init` **before** Phase 1 — the loop starts at tokens and assumes a host
app already exists. A static single-file mock-up skips this. A built reference composing the
app-shell / data-table / command-menu recipes on the real stack lives at `examples/app-ui/`,
resolved from the **repository root**, not from this skill directory.

Add the Phase-5/6 render dependencies in the same pre-step. **`Skill(silver)` is the default
browser**: it is a local headless Playwright, and every script here borrows its engine from silver
before asking you to install one, so only axe is missing.
```bash
npm i -g agent-silver && npm i -D @axe-core/playwright
# no silver:  npm i -D playwright @axe-core/playwright && npx playwright install chromium --with-deps
```
The audit script is committed to the repo, not regenerated per run: a script costs zero context and
only its output enters the window.

---

## Reference map

**Read the file named in each phase before doing that phase's work.** A pointer here is a command,
not a citation. Load a reference only when its phase needs it — these are large. Where a file opens
with a `## Contents` list, read that first and pull only the section you need.

| File | Load when building | Read it for |
|---|---|---|
| `references/brand-to-system.md` | all | Phase 1: spectrum vector, **the DESIGN BRIEF template**, **the tweakcn preset catalogue**, the 7 archetype presets, the invariant layer, brand → decision rules, **the five design dials** |
| `references/reference-mining.md` | a real product is the reference | Phases 1a & 4: finding comparable products, the 5-rung evidence ladder, `extract-reference.mjs`, the measured→brief mapping, the ten-surface transfer test, **the differentiation rule** |
| `references/tokens.md` | all (§11 = app) | Phase 1 & 3: the complete OKLCH 3-tier system — color ramps, **the hard caps**, surfaces/elevation, the semantic `@theme` scaffold, typography, spacing + optical alignment, radius, shadow, interaction states, **§11 app-UI product defaults** (density tiers, 0ms ⌘K, full-opacity focus ring, tabular-nums) |
| `references/motion.md` | all | Phase 3: motion craft depth, the duration/easing/spring values, and the **animation-review ship gate** — frequency gate, what to never animate, enter/exit + origin + stagger, interruptibility, reduced-motion-is-gentler |
| `references/motion-platform.md` | all | Phase 3, only when the effect needs it: View Transitions, `@starting-style` and discrete transitions, `interpolate-size`, scroll-driven animation (`motion.md` owns feel and the gate; this owns the platform primitives) |
| `references/landscape.md` | all | Phase 2: shadcn composition rules (`cn`/`cva`/`asChild`/`data-slot`, registry) + the tooling/registry ecosystem map |
| `references/anti-slop.md` | all (§ APP-UI = app) | Phase 4: the **canonical (SSOT) named-defect catalog** — grep rules + judge-lens tells; imported by the gate script, the judge-lens, `critique.md`, and the eval judge |
| `references/critique.md` | all | Phase 4: the review **process** — two isolated assessments, P0–P3 severity, Alex+Sam dashboard personas, the anti-laziness playbook + redesign ladder |
| `references/accessibility.md` | all | Phase 5: the WCAG 2.2 AA checklist |
| `references/performance.md` | all | Phase 5: the Core Web Vitals budgets and the design decisions that move them (`accessibility.md` owns conformance; this owns speed) |
| `references/verification.md` | all | Phases 4–6: what counts as evidence — why a linter in the loop beats a re-read, why the DOM beats the screenshot, and the numbers behind the stop rule |
| `references/cookbook/*.md` | landing · app · flow | Phase 2: 15 composable screen/section recipes indexed by output type in the Phase 2 list, plus `texture.md` for the TEXTURE_LEVEL dial |
| `assets/theme.css` | all | Phase 1: the starter Tailwind v4 token theme (light + dark) — copy into `app/globals.css`, then swap the fonts and brand hue |
| `Skill(dataviz)` | chart | Any chart, KPI tile, sparkline, or dashboard palette. Invoke the skill; do not improvise a series palette |

**Never hold `anti-slop.md` + `critique.md` + `accessibility.md` in one window.** Combined they are
150+ simultaneous constraints — the density at which primacy effects peak and errors shift from
modification to omission (IFScale, arXiv 2507.11538). Phase 4a runs the detect rules as a script
(zero context); Phase 4b loads only `anti-slop.md` § APP-UI; Phase 5 loads only `accessibility.md`,
and only for the items the commands cannot decide. Put the two highest-stakes constraints FIRST and
LAST in any prompt (arXiv 2307.03172).

---

## Phase 1 — Brand → brief → tokens (system-first)

Decide the aesthetic *before* writing any UI. Read `references/brand-to-system.md` before starting.

**1a. Compress the brand into the ~6 spectrum floats** (−1…+1; the axes are named in
`brand-to-system.md` § How the engine uses these). `ultrathink` here — this is one of the two
judgement calls in the whole skill, and the floats make every downstream choice a pure function. If
two brand moods genuinely conflict, force a priority; never average them into mush. **Name the
aesthetic explicitly** ("warm editorial", "precise fintech", "neobrutalist terminal") — vague "clean
and modern" invites the center. State the font choice out loud here.

**If a real product is the reference — measure it, never recall it.** "Like Linear" from memory is
an adjective wearing a product's name, and it goes beige like every other adjective. **Read
`references/reference-mining.md`** for the ladder (a first-party `design.md` beats measuring), the
three declared reference roles, and what to record. Capture with:

```bash
node scripts/extract-reference.mjs --url <reference-url> --theme dark --out ref/<name>
```

**1b. Emit three candidate directions with probabilities, then take the least probable that still
satisfies the brief.** Write literally: *"Give me 3 complete art-direction briefs for this product,
each with its probability of being the direction a generic model would produce. They must differ on
ALL of: MOVEMENT, accent hue family, radius base, and grid discipline."* Take the LOWEST-probability
candidate that clears every MANDATORY; never average them. The measured diversity gain and its
caveat are in `brand-to-system.md` § The art-direction brief.

**1c. Write the winning direction up as one binding Design Brief.** **The fenced template is in
`brand-to-system.md` § The art-direction brief** — 15 fields, from PROJECT NAME through THE ANOMALY
to MANDATORIES. Fill every one. If you write a Design Brief, you MUST follow it: every later phase
cites it, a value that contradicts it is a defect rather than a preference, and a blank field is a
blocked phase rather than a default.

**Skip the brief only when:** the work is backend/API with no visual surface; it is a minor styling
tweak to an existing token-driven screen; the user supplied mockups or an exact design to
replicate; or the user provided a complete spec.

**1d. Retrieve a starting preset — do not recall one.** A recalled preset is invented plausible
OKLCH, which is the convergence this skill exists to prevent. **Read `references/brand-to-system.md`
§ Retrieving a starting preset now** — it carries the tweakcn registry URLs, the verified catalog of
preset names, the `registry:style` shape to expect, the offline fallback, and the radius personality
dial. A preset is a *complete design language*, not a palette: override its primitives to the brand
seed rather than shipping it as found.

**1e. Generate the token system.** **Read `references/tokens.md` §0–§3 before writing the file** —
those sections own the OKLCH ramps, shadcn's semantic vocabulary in full, the
`base = surface / -foreground = text-on-surface` pairing rule, the one-way
`component → semantic → primitive` chain, and the complete `@theme inline` scaffold. Dark mode
re-points the *same* semantic names under `.dark`; it is a second authored ramp, never an inversion.

**Apply color by 60-30-10:** ~60% neutral surface, ~30% secondary, ~10% saturated accent. Accent
signals "act here" *because* it is scarce.

> **Hard caps:** **3–5 colors total** (1 brand hue + 2–3 neutrals + 1–2 accents) and **≤2 font
> families**. Never exceed either without the user asking. 60-30-10 does not prevent sprawl on its
> own — a 9-hue palette can still be 60-30-10. The line-height band and the per-register body-size
> floors that go with these caps are in `tokens.md` §0 → "Hard caps".

**Set the five design dials** — `DESIGN_VARIANCE`, `MOTION_INTENSITY`, `VISUAL_DENSITY`,
`GRID_DISCIPLINE`, `TEXTURE_LEVEL`. **Read `references/brand-to-system.md` § Design dials** for the
ranges, what each one gates, the product-vs-marketing defaults, and the per-archetype readings. Set
all five here and record them in the brief; Phases 2–4 read them and never re-derive them.

**Phase 1 gate:** the token file compiles, every color role has a fg/bg pair, and light + dark both
exist. Do not proceed until tokens are committed to CSS.

---

## Phase 2 — Compose from cookbook patterns

**Scope-lock first.** Before writing markup, enumerate every screen, section, state, and component
and write the count into your working notes. Cross-check against that count before "done"
(→ `critique.md` §3.3). This is the "missing-step error" class Plan-and-Solve targets (arXiv
2305.04091); DCGen's segment-then-assemble wins 8–15% for the same reason (arXiv 2406.16386).

**Write the real copy before the first div.** Commit the actual headline, sub, nav labels,
empty-state text, and error strings to a `content.ts` before composing. Design2Code measures
text-augmented prompting as the strongest non-self-revision method across every open model tested
(arXiv 2403.03163 §4.1), and it removes `lorem` and `vague-headline` at the source, not at the gate.

Do not invent layouts from scratch — compose from the vetted recipes in `references/cookbook/`.
Each recipe carries a "when to use / when not to", anatomy, real shadcn code, states, and a11y
wiring. Read the recipe before composing from it. All 15, by output type:

- **landing** — `hero` · `marketing-sections` · `pricing` · `nav-header` · `cards` (bento) ·
  `code-panel-hero` (dev-tool product hero)
- **app** — `dashboard-shell` (sidebar + topbar) · `data-table` · `command-menu` (⌘K) ·
  `settings-page`
- **flow** — `auth` · `forms` (create / settings / validation) · `onboarding` · `empty-states` ·
  `dialogs` (modals / sheets / confirms)
- **any of the three, when `TEXTURE_LEVEL` > 0** — `texture` (the material layer, with parameters)

**Composition rules.** Read `references/landscape.md` § Composition before composing. Compose small
parts (`Card` + `CardHeader` + …), don't prop-explode; thread `className` last through `cn()`;
reskin via tokens, never by forking `components/ui/*`.

**Four Tailwind hygiene laws.** Never mix `margin`/`padding` with `gap` on the same element. Use
`gap`, never `space-x-*`/`space-y-*`. Wrap headlines in `text-balance` and lead paragraphs in
`text-pretty`. Put the page background on the root element: `<html className="bg-background">`.
These four are author-side rules, not gate detectors — nothing downstream catches them for you.

**Wire accessibility while composing, not after:** semantic elements (`main`, `header`, `nav`) over
`div`; correct ARIA roles; `sr-only` for screen-reader-only text; `alt` on every image unless
decorative or redundant.

**Add a variant, never a call-site override.** A one-off `className` colour or size at a call site
is a defect: if you need a different appearance, add a `cva` variant to the component. Known trap:
shadcn's `outline` variant has a transparent background, so white text on it is invisible — define
a real variant with both surface and foreground, do not patch it with `text-white` at the call site.

**One primary action per screen.** Let content dictate card count and layout — do not reflexively
emit three feature cards or an 11-card grid. Prefer an asymmetric/editorial layout over
centered-everything where it fits the brand.

**Always fork 3, never re-roll.** Generate exactly three candidates that differ on a DECLARED axis,
not on sampling noise:

```
A = cookbook default at the Phase-1 dials
B = DESIGN_VARIANCE +3   (asymmetric / editorial; centred hero banned)
C = VISUAL_DENSITY +2    (compact tier; border-t/divide-y grouping)
```

N=3 is the ceiling — past it you pay linearly for a judge whose discrimination collapses exactly as
candidates converge, which is why the axis is declared rather than sampled (the numbers:
`references/verification.md`). Write to `design_iterations/{surface}_{1,2,3}.tsx`; name the winner
and the one property carried over from each loser; iterate only the winner, as `{surface}_{n+1}`.

**Run the Phase-4 gate at the end of this phase, not only at the end of the build** —
`bash scripts/anti-slop-gate.sh src/`. The value is catching a defect before it is copied into nine
more components.

---

## Phase 3 — Polish pass

This is what separates designed from generated. Work top-down; details last.

**Every value and every craft rule this phase applies lives in `references/tokens.md`. Read these
five, in this order, before touching the screen — each constrains the next:**

1. **§5 spacing rhythm** — the 4pt ramp, `internal ≤ external`, and the optical-alignment nudges.
2. **§4 typography** — the three gray levels, weight/size extremes, tracking, measure, and
   emphasis-by-de-emphasis.
3. **§6–§7 elevation** — one light source by role, border-first for resting surfaces, lighter
   surface in dark.
4. **§10 interaction states** — the three non-colliding axes, the single on-color overlay, all six
   states enumerated *before* the component, empty states as a deliverable.
5. **`references/motion.md` in full** — motion craft plus the animation-review gate that every
   bespoke or interactive motion (gestures/drag, drawers/sheets, hero transitions, orchestrated
   reveals) must clear before "done".

Non-negotiables 6–9 are the floor; those sections are how you meet them. The one carve-out to the
300ms cap is a **cross-view transition** (shared-element morph, route change) at **300–400ms** —
sourced in `tokens.md` §8. Everything else stays under the cap.

Re-run `bash scripts/anti-slop-gate.sh src/` at the end of this phase.

---

## Phase 4 — Anti-slop gate

Block "done" until this passes. `references/anti-slop.md` is the **canonical defect catalog (single
source of truth)** — the gate script, this gate's judge-lens, and the eval judge all import their
tells from it. Edit a tell there and nowhere else.

**4a — run the gate. Do not self-assess it.**

```bash
bash scripts/anti-slop-gate.sh src/
```

A non-zero exit blocks "done"; the exit code is the number of distinct tells found. The script is the
gate; `anti-slop.md`'s detector table documents what it checks. The greps are the **oracle** — a
self-review with no external signal measurably degrades output (→ `references/verification.md`).

**4a-bis — the differentiation gate, only when a real product was mined in Phase 1.** "We changed it
enough" is exactly the claim a model makes about a clone, so it is a count — exit 0 requires **≥3 of
6 mechanics moved** and the accent hue **never** within 10° of the reference's:

```bash
node scripts/extract-reference.mjs --url <your dev-server url> --theme dark --out ref/ours
node scripts/extract-reference.mjs --diff ref/<reference>.json ref/ours.json
```

What may and may not be carried over, and what this gate cannot see: `references/reference-mining.md`.

**The one brand exemption.** The OKLCH detector flags accent tokens in the **270–319°** hue window
(measured off Tailwind: `blue-700` is 264.376, `indigo-500` is 277.117 — a plain-blue brand does not
trip it). A genuinely blue-violet brand declares that token in a `DESIGN.md`; the gate then skips it
and treats every other hit as a finding. That is the only exemption — never widen or silence a
detector.

**Numeric gate — two counts, not a sampled score.** A model that picks its own sample, applies its
own criterion, and reports its own number has produced no evidence:

```bash
grep -rIoE '\b(p|px|py|m|gap|w|h)-\[[^]]+\]' src --include='*.tsx' \
  | grep -vE '\[[0-9.]+ch\]|calc\(|var\(' | wc -l    # must be 0
grep -rIoE 'className="[^"]*\[#[0-9a-fA-F]{3,8}\]' src | wc -l               # must be 0
```

**The three exclusions are not leniency, they are correctness.** A `ch` measure is *mandated* by
Phase 3 (`max-width: 66ch`, never a px width), and `calc()` / `var()` are how shadcn's own
primitives size themselves — `w-[var(--radix-select-trigger-width)]` has no token form. Without
them this grep flags the skill's own reference implementation and its own instruction, which is how
it read before it was ever run against `examples/`.

A surviving hit is a **hardcoded dimension** — `h-[320px]`, `w-[8rem]` — and is a Phase-1
token-baseline defect: repair the tokens, do not patch the component. The honest exception is a
fixed-height chart or media container, which has no token because it is not a spacing decision;
justify it in one line or delete it. Every screen must reference the one shared theme.

**What to reach for.** Naming a forbidden token *while generating* raises its own probability, so the
positive form is the only one that belongs in a build prompt — this list, not a ban list:

- **type** — the face named in the brief's TYPE field
- **color** — the brief's PALETTE hues in their declared roles
- **layout** — content-driven, at the brief's DIALS, carrying the brief's one TENSION
- **copy** — the strings already committed to `content.ts`. Litmus: *"Would the founder actually say this?"*

The matching ban list is **audit-only** and lives in `references/anti-slop.md` § Good-defaults
reference — every entry paired with its replacement. Read it when you review, never when you write.

**4b — product-taste judge-lens** (catches what greps structurally cannot; `ultrathink` here). Load
only `anti-slop.md` § APP-UI for this pass. Greps see textual tells; they cannot see the *absence*
of a behavior. Review the screen against the judge-only tells there: **mouse-only** (no ⌘K, no
keyboard row-nav, no shortcuts), **missing state machine** (focus/disabled/loading/empty/error not
all present), **decorative color where hierarchy should come from spacing + weight**, **one fixed
density** (no compact/comfortable tier), and **an animated ⌘K surface** (should open at 0ms). A
screen that passes every grep and still reads generic has failed this lens — fix before "done".
`bash scripts/anti-slop-gate.sh --lens src/` prints this checklist alongside the gate.

**For anything past a single component, run the review harness in `references/critique.md`** — it
owns the *process* (two isolated assessments, the Nielsen heuristics as yes/no, P0–P3 severity, the
Alex + Sam personas for product surfaces, and the redesign ladder for "off but I can't say why").
`anti-slop.md` stays SSOT for the *tells*.

**Never skip this pass to save time.** No shipping AI UI product verifies anything before
completion; this gate is the whole difference between this skill and a well-configured v0 prompt.

---

## Phase 5 — Accessibility gate

**Phase 5 runs, it does not read.** Where a check is computable, compute it — never eyeball a
number a command can produce. Two tiers.

**Tier 1 — always available.** No install, no browser:
```bash
node scripts/validate-chart-palette.mjs app/globals.css   # the project's theme, not the starter
```
Exit 0 or the palette is not shippable; the exit code is the count of failed checks.

**Tier 2 — the render gate.** Needs the Phase-0 dependencies:
```bash
node scripts/design-audit.mjs --url <route> --theme light,dark
```
Install them, or say in one line that this tier did not run — an unrun gate is not a passed gate.
**Its caps are calibrated** — each set in the gap between the five gate-clean `examples/` and
`scripts/fixtures/slopped-geometry.html` — so a non-zero exit is a block, not a suggestion. It also
prints five **uncapped** numbers that measurably do not separate good work from slop: read them, do
not gate on them. Never loosen a cap to pass a screen; fix the screen. Its axe section is
authoritative — never re-derive contrast by inspection, and only what axe marks **incomplete** is
yours to judge. The corpus behind every cap, and why a command outranks your own look at the screen:
`references/verification.md` (§6 for the caps).

WCAG 2.2 AA is the floor, not optional. Full checklist in `references/accessibility.md` — load only
the items the commands above cannot decide.

- **Contrast:** text ≥ 4.5:1 (large ≥ 3:1); UI/icon borders ≥ 3:1 in every state. Check in **light
  AND dark**, across ~5 text styles. Gate on WCAG 2 ratios only: APCA is **not** in WCAG 3 — it was
  removed from the draft in July 2023 — so an Lc figure is advisory and never overrides a WCAG 2
  failure.
- **Color is never the only signal** (errors, links, status, chart series need a second cue).
- **Focus:** visible `:focus-visible` on every interactive element, `outline` `2–3px` solid with
  `outline-offset: 2px`; never `outline:none` without a replacement, and never Tailwind's `ring-*`
  as the indicator itself. Why `outline` and not `box-shadow` — three reasons, all decided:
  `tokens.md` §10 → "Focus ring: `outline`, decided".
- **Keyboard:** full operation, logical tab order, no traps, Esc closes overlays, skip link. Modals
  trap focus while open and restore it on close.
- **Native-first:** real `<button>/<a>/<input>`; ARIA only fills gaps. Any `role=`/`tabindex` is a
  review flag.
- **Reduced motion:** ship the `@media (prefers-reduced-motion: reduce)` reset by default, then opt
  comprehension fades back in under `no-preference`. Reduce (cross-fade), don't delete feedback.
- **Everything else is in `references/accessibility.md`** and axe decides most of it: target sizes
  (§4 — SC 2.5.8 is an inscribed-square test, so a circle is not a square), labelling, form errors
  and focus-on-submit, live regions, `aria-expanded`/`aria-controls`, and `font-size ≥ 16px` on
  inputs. Read it for what axe marks incomplete; do not restate it from memory.

---

## Phase 6 — Render and inspect

Text review cannot see a broken layout. Before "done", look at the result.

**In this environment:** use `Skill(silver)` to open the dev-server URL and capture at **1440×900
and 390×844**, in **light and dark**. Read the screenshots against the Design Brief from Phase 1,
not against your memory of the code.

**Alternative, if chrome-devtools-mcp is connected:** `resize_page` 1440 → `take_screenshot` → read
→ `resize_page` 390 → `take_screenshot` → read → `lighthouse_audit` → `list_console_messages`.
Refer to those tools fully qualified (`chrome-devtools:take_screenshot`).

**Timing rule:** wait for `networkidle` before screenshotting or inspecting the DOM on any dynamic
app. Screenshotting before network idle captures an empty shell and produces a false pass.

**What you are looking for** — the defects only vision catches: horizontal overflow at 390px (a
critical failure), a clipped popover, text colliding with a container edge, a squint-test hierarchy
failure, whether the grayscale read still resolves. Console errors and a failing Lighthouse
accessibility score both block "done".

If no browser is available, say so in one line — do not claim the gate passed.

**Stop rule for Phases 4–6: repair once per new signal, then stop.** Fix every P0/P1 the gate
reports, re-run it, exit 0 or stop and report. **Every additional loop must introduce a signal the
previous loop did not have** — a new script run, a new render, a human. Otherwise it is theatre. At
most **two** model-critique passes on one screen: pass 1 finds real defects; by pass 3 the
suggestions are measurably worse than the design. Evidence: GPT-4 GSM8K 95.5 → 91.5 → 89.0 and
GPT-3.5 CommonSenseQA 75.8 → 38.1 under repeated intrinsic self-correction (arXiv 2310.01798
Table 3); Duan et al. CHI 2024 found LLM heuristic-evaluation accuracy *falls* as the UI improves —
9 of 100 violations LLM-only vs 62 human-only. The rest of the evidence, including the ablation that
prices a checker in the loop at +3.0 absolute, is in `references/verification.md`.

---

## Master quality bar (definition of done)

Ship only when **all** are true. This is the north star every phase serves.

1. **Branded, not generic.** A stranger could name the aesthetic; nothing on the "Never ship" list
   survives; the layout is content-driven, not the template mean. It survives the `critique.md`
   harness (isolated A/B, no P0/P1 open) — not just the greps. If a real product was mined in Phase
   1, `node scripts/extract-reference.mjs --diff <reference>.json <ours>.json` exits 0.
2. **Systematic.** Every value comes from a token; both Phase-4 counts are 0; one theme drives every
   screen; light + dark both real.
3. **Hierarchical.** It reads correctly in grayscale — hierarchy carried by spacing, weight, and gray
   level before size or color. `internal ≤ external` holds everywhere.
4. **Complete.** Every interactive element has its full state matrix; empty/loading/error states
   exist; real domain content, no lorem/placeholder.
5. **Alive but restrained.** Motion goes through the two-curve vocabulary, ≤300ms (cross-view
   transitions ≤400ms), transform/opacity only, one orchestrated reveal. Bespoke/interactive motion
   cleared the `motion.md` gate: interruptible, faster-exit, reduced-motion gentler-not-gone.
6. **Accessible — by exit code, not by claim.** `bash scripts/anti-slop-gate.sh src/`,
   `node scripts/validate-chart-palette.mjs <theme.css>` and
   `node scripts/design-audit.mjs --url <route> --theme light,dark` all exit 0. If the render gate
   could not run, say so — an unrun gate is not a passed gate, and the WCAG 2.2 AA items it cannot
   decide (contrast in both themes, visible focus, keyboard, targets, labels, reduced-motion) are
   still yours.
7. **Own-your-code.** Composed from shadcn primitives with semantic tokens; `className` threads last;
   no forked `components/ui/*`.
8. **Seen.** Phase 6 done: rendered at 1440×900 and 390×844, both themes, console clean.
