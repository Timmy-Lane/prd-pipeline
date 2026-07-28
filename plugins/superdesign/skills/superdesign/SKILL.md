---
name: superdesign
description: >-
  Design and build top-tier, brand-specific UI with React + Tailwind v4 + shadcn/ui via a
  system-first workflow (brand → OKLCH tokens → cookbook patterns → polish → anti-slop & a11y
  gates) that defeats generic "AI-slop" output. Use for ANY UI/UX work — building or restyling a
  component, screen, page, dashboard, landing, marketing site, or design system; choosing
  colors/typography/spacing/radius/shadow/motion; theming or composing shadcn/ui; or whenever an
  interface looks generic, "AI-generated", or off-brand and needs to look deliberately designed.
---

# superdesign

A design-system *generator*, not a fixed theme. It infers brand/mood, generates a tuned OKLCH
token system from a strong preset, composes screens from a vetted cookbook, and self-audits
against named anti-slop defects — so the output looks deliberately designed for its brand.

## What this does

Produce UI that looks **deliberately designed for its brand**, not generated. The default failure
mode of any model is convergence on the statistical center of every SaaS template it was trained on
("AI slop"): Inter, indigo, purple gradients, centered hero + three cards, one flat shadow, no real
states. This skill defeats that by forcing a **system-first workflow** — commit to a brand, generate
a token system, compose from vetted patterns, then gate the result — instead of hand-writing markup
that drifts toward the mean.

Stack: **React + Tailwind v4 + shadcn/ui**, OKLCH color, semantic CSS-variable tokens.

**Separate the three jobs.** Slop comes from fusing them in one prompt: (1) *taste direction* —
what should this feel like, (2) *exploration* — what are the options, (3) *spec/build* — what
exactly to build. Do them in order, in separate phases. **Self-diagnostic:** if you are reacting to
your own output with adjectives ("cleaner", "more premium", "less generic"), the jobs are still
fused — stop and go back to Phase 1.

---

## The loop

Run these phases **in order** for any UI task. Never skip to markup. Paste this checklist into your
working notes and check each box before moving on.

```
[ ] Phase 1  Brand → preset → tokens exist and are committed to CSS
[ ] Phase 2  Screen composed from cookbook patterns using semantic tokens only
[ ] Phase 3  Polish pass: spacing rhythm, optical alignment, full state matrix, motion
[ ] Phase 4  Anti-slop gate passed (no tells; forked ≥2 directions early)
[ ] Phase 5  Accessibility gate passed (contrast, focus, keyboard, states, reduced-motion)
[ ] Quality bar met (see end)
```

**Hard rule:** no component markup before a token file exists. Tokens are the shared source of truth
that keeps every screen consistent; writing colors/spacing inline is the #1 cause of cross-screen
drift.

---

## Phase 1 — Brand → preset → tokens (system-first)

Decide the aesthetic *before* writing any UI. Read `references/brand-to-system.md` for the full
derivation method.

**1a. Compress the brand into ~6 spectrum floats** (−1…+1): Serious↔Playful, Traditional↔Modern,
Warm↔Cool, Restrained↔Bold, Economical↔Premium, Calm↔Energetic. These make every downstream choice a
pure function. If two brand moods genuinely conflict, force a priority — do not average them into
mush. **Name the aesthetic explicitly** (e.g. "warm editorial", "precise fintech", "neobrutalist
terminal"). Vague "clean and modern" invites the center. State the font choice out loud here.

**1b. Pick a starting preset, then re-seed.** Start from a tweakcn preset near the target vibe
(a preset is a *complete design language* — font trio + radius + shadow params + full light/dark
color set, not just a palette), then override its primitives to the brand seed. Radius is the
sharpest single personality dial: `2–4px` = serious/fintech, `8–12px` = friendly/consumer (the
common default), `16px+` = playful, pill = maximal play.

**1c. Generate the token system.** Author in **OKLCH**; adopt shadcn's semantic vocabulary verbatim
(`background/foreground`, `card`, `popover`, `primary`, `secondary`, `muted`, `accent`,
`destructive`, `border`, `input`, `ring`, `chart-1..5`, `sidebar-*`, `radius`) with the
**base = surface, `-foreground` = text-on-surface** pairing rule (guarantees a legible pair for every
color). Reference direction is one-way: **component → semantic → primitive**, never skip up. Author
few primitives, **derive scales with `calc()`** (one `--radius` → sm/md/lg/xl; one shadow set → the
elevation scale). Wire runtime-swappable vars through `@theme inline`; dark mode re-points the *same*
semantic names under `.dark`. → `references/tokens.md` (§0–3 color, surfaces, semantic `@theme`).

**Apply color by 60-30-10:** ~60% neutral surface, ~30% secondary, ~10% saturated accent. The
saturated brand seed belongs in the **10% accent/action** role, not flooded across surfaces — accent
signals "act here" *because* it is scarce.

**Phase 1 gate:** the token file compiles, every color role has a fg/bg pair, and light + dark both
exist. Do not proceed until tokens are committed to CSS.

---

## Phase 2 — Compose from cookbook patterns

Do not invent layouts from scratch — compose from the vetted recipes in `references/cookbook/`. Each
recipe carries a "when to use / when not to", anatomy, real shadcn code, states, and a11y wiring.

| Building… | Recipe |
|---|---|
| Auth screens | `cookbook/auth.md` |
| Cards / bento | `cookbook/cards.md` |
| Command palette (⌘K) | `cookbook/command-menu.md` |
| App shell (sidebar + topbar) | `cookbook/dashboard-shell.md` |
| Data table | `cookbook/data-table.md` |
| Modals / sheets / confirms | `cookbook/dialogs.md` |
| Empty / zero states | `cookbook/empty-states.md` |
| Forms (create / settings / validation) | `cookbook/forms.md` |
| Landing hero | `cookbook/hero.md` |
| Marketing sections | `cookbook/marketing-sections.md` |
| Nav / header | `cookbook/nav-header.md` |
| Pricing | `cookbook/pricing.md` |
| Settings page | `cookbook/settings-page.md` |
| Code/API product hero (dev tools) | `cookbook/code-panel-hero.md` |
| Onboarding / first-run flow | `cookbook/onboarding.md` |

**Composition rules** (→ `references/landscape.md` §composition): compose small parts
(`Card` + `CardHeader` + …), don't prop-explode; use **semantic tokens only** in markup
(`bg-primary`, never `bg-zinc-900` or raw hex) so theming/dark-mode keep working; thread `className`
last through `cn()`; reskin via tokens, never by forking `components/ui/*`.

**One primary action per screen.** Let content dictate card count and layout — do not reflexively
emit three feature cards or an 11-card grid. Prefer an asymmetric/editorial layout over
centered-everything where it fits the brand.

**When exploring a novel layout, fork ≥2 distinct directions and compare** — do not iterate a single
output. Convergence stop-rule: if after two revise loops the variants aren't converging on your
constraints, stop re-rolling and **tighten the brief** instead.

---

## Phase 3 — Polish pass

This is what separates designed from generated. Work top-down; details last. Full values in the
referenced files.

**Spacing rhythm** (→ `references/tokens.md` (§5 spacing)). Everything is a multiple of 4 on an 8pt grid;
use the ramp `4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96` (skip near-duplicates like 56/72 so large
steps stay distinct). Enforce **internal ≤ external**: the gap *around* a group must be ≥ the padding
*within* it (card padding ≤ inter-card gap) — the single highest-leverage layout fix. Body measure
`max-width: 66ch`, not a px width. Whitespace is proportional to importance.

**Hierarchy via weight + color, not size** (→ `references/tokens.md` (§4 typography)). Three gray text levels
(primary near-black, secondary, tertiary) and mostly two weights. For real headings use **extremes:
weight 200 vs 800, size jumps ≥3×**, not 400/600 at 1.5×. Emphasize by de-emphasizing neighbors.
Tighten headline tracking; add letter-spacing to ALL-CAPS. Never gray text on a colored background —
use a same-hue, lower-saturation, higher-lightness tint.

**Optical alignment** (→ `references/tokens.md` (§5 spacing)). Start on the grid, then nudge: shift play/▶
triangles right; oversize circles vs equal-box squares; pad text off rounded corners ~proportional to
radius; offset menus by their own padding to align with the trigger text; trim card top padding for
line-height overhang. Apply the nesting formula: **inner radius = outer radius − padding**.

**Elevation** (→ `references/tokens.md` (§6–7 radius, elevation)). Define **3–5 named elevation tokens**, each a
**two-layer** shadow (soft ambient + tight direct, offset down — light from above), applied by role
(resting card → dropdown → modal). One light source; tint shadows toward the bg hue, never pure
black. In dark mode, elevation = **lighter surface**, not shadow; desaturate accents; no pure
`#000`/`#fff`. Prefer border-first elevation (1px hairline) for static surfaces; reserve real shadows
for floating/interactive layers.

**Full state matrix** (→ `references/tokens.md` (§10 interaction states)). Every interactive element ships **rest, hover,
active/pressed, focus-visible, disabled, loading** plus, where relevant, **selected, error, empty**.
Model states on two axes: *fill* = exclusive pointer state, *ring* = focus, *border/indicator* =
selected — so they stack without collision. Derive hover/press from one on-color overlay
(hover ≈ 8%, pressed ≈ 10%, disabled content 38% / fill 12%) instead of per-component color-picking.
Loading keeps fixed width (transparent label + centered spinner) and guards against double-submit.
**Empty states are a deliverable:** illustration/graphic + headline + one CTA, with surrounding chrome
hidden when there's no data.

**Motion** (→ `references/tokens.md` (§8 motion)). Ship a **two-curve vocabulary** and force everything through
it: `--ease-out-quint: cubic-bezier(0.23,1,0.32,1)` (entrances) and
`--ease-ios: cubic-bezier(0.32,0.72,0,1)` (micro-interactions) + `linear` for spinners. Default
`ease-out`; **ban `ease-in` for UI**. Cap interactive motion **< 300ms** (target ~180ms); larger
surfaces get more time. Animate **only `transform` + `opacity`**. Never `scale(0)` — floor at ~0.95 +
fade. Animate from the trigger's origin. Prefer **one orchestrated page-load reveal** (staggered
`animation-delay` 30–80ms) over scattered fade-ins; the more frequent an action, the less it should
animate (100+/day → none). Suppress transitions during theme switch.

---

## Phase 4 — Anti-slop gate

Block "done" until this passes. Full named-defect catalog + grep rules in `references/anti-slop.md`.

**Never ship:**
- **Fonts:** Inter, Roboto, Open Sans, Lato, Arial, or a default system stack as the display face.
  (Also avoid the escape-hatch clichés: Space Grotesk, Geist, single-word Instrument-Serif italics.)
- **Color:** the indigo/purple default (`#6366f1`/`#8b5cf6`), purple→blue gradient on white, gradient
  text on stat numbers, "VibeCode" lavender from image-gen. Purple is allowed *only* as a real brand
  decision.
- **Structure:** centered-everything, reflexive three-feature-card row, uniform radius/padding on all
  elements, card-in-card nesting, colored left-border cards, badge-above-H1, emoji section headings.
- **Copy:** vague aspirational headlines ("Build the future of work", "For Modern Teams"), lorem
  ipsum, fake testimonials/logos, unsourced stats. Litmus: *"Would the founder actually say this?"*

**Cheap high-precision greps:** `indigo|violet|purple|#6366f1`; a single flat `rgba(0,0,0,0.1)`
shadow used everywhere; leading emoji in headings; colored `border-left`. (Note: the tell is a *flat
uniform* 0.1 shadow — a graduated elevation scale legitimately uses 0.1 at some steps. The real check
is "≤3 shadow recipes, applied by role" — see Phase 3.)

**Numeric gate:** sample 10 components — **≥8 must map cleanly to tokens** for color, type, spacing,
radius, and elevation. If fewer pass, pause and repair the token baseline before adding screens.
Every screen must reference the one shared theme (no per-screen ad-hoc values).

---

## Phase 5 — Accessibility gate

WCAG 2.2 AA is the floor, not optional. Full checklist in `references/accessibility.md`.

- **Contrast:** text ≥ 4.5:1 (large ≥ 3:1); UI/icon borders ≥ 3:1 in every state. Check in **light
  AND dark**, across ~5 text styles. For dark schemes prefer **APCA Lc ≥ 90 body / 75 large-body / 60 non-body** —
  WCAG 2 ratios are unreliable near-black.
- **Color is never the only signal** (errors, links, status, chart series need a second cue).
- **Focus:** visible `:focus-visible` ring on every interactive element — `outline` (survives rounded
  corners + overflow + forced-colors) `2–3px` solid, `outline-offset: 2px`; never `outline:none`
  without a replacement. shadcn pattern: crisp `border-ring` + soft `ring-ring/50 ring-[3px]`.
- **Keyboard:** full operation, logical tab order, no traps, Esc closes overlays, skip link. Modals
  trap focus while open and restore it on close.
- **Native-first:** real `<button>/<a>/<input>`; ARIA only fills gaps; every icon-only control gets
  `aria-label`; every disclosure gets `aria-expanded` + `aria-controls`. Any `role=`/`tabindex` is a
  review flag.
- **Targets ≥ 24×24px** (aim 44×44 for touch/primary), input `font-size ≥ 16px` (prevents iOS zoom).
- **Reduced motion:** ship the `@media (prefers-reduced-motion: reduce)` reset by default, then opt
  comprehension fades back in under `no-preference`. Reduce (cross-fade), don't delete feedback.
- **Forms:** every field labeled (`<label>`, not placeholder); errors in text + `aria-invalid` +
  `aria-describedby`; move focus to the first error on submit.
- **Live regions:** announce async changes via `role="status"`/`alert`.

---

## Master quality bar (definition of done)

Ship only when **all** are true. This is the north star every phase serves.

1. **Branded, not generic.** A stranger could name the aesthetic; nothing on the anti-slop block-list
   survives; the layout is content-driven, not the template mean.
2. **Systematic.** Every value comes from a token; ≥8/10 sampled components map to tokens; one theme
   drives every screen; light + dark both real.
3. **Hierarchical.** It reads correctly in grayscale — hierarchy carried by spacing, weight, and gray
   level before size or color. `internal ≤ external` holds everywhere.
4. **Complete.** Every interactive element has its full state matrix; empty/loading/error states
   exist; real domain content, no lorem/placeholder.
5. **Alive but restrained.** Motion goes through the two-curve vocabulary, ≤300ms, transform/opacity
   only, one orchestrated reveal — purposeful, never decorative-everywhere.
6. **Accessible.** WCAG 2.2 AA passes in light and dark: contrast, visible focus, keyboard, targets,
   labels, reduced-motion.
7. **Own-your-code.** Composed from shadcn primitives with semantic tokens; `className` threads last;
   no forked `components/ui/*`.

---

## Reference map

Load a reference only when the current phase needs it (progressive disclosure — these are large;
files over ~100 lines carry their own table of contents).

| File | Use for |
|---|---|
| `references/brand-to-system.md` | Phase 1: spectrum vector, the 7 archetype presets, invariant layer, brand → decision rules |
| `references/tokens.md` | Phase 1 & 3: the complete OKLCH 3-tier system — color/ramps, surfaces/elevation, semantic `@theme` scaffold, typography, spacing, radius, shadow, motion, and interaction states |
| `references/landscape.md` | Phase 2: shadcn composition rules (`cn`/`cva`/`asChild`/`data-slot`, registry) + the tooling/registry ecosystem map |
| `references/anti-slop.md` | Phase 4: named-defect catalog, grep rules, gates |
| `references/accessibility.md` | Phase 5: WCAG 2.2 AA full checklist |
| `references/cookbook/*.md` | Phase 2: 15 composable screen/section recipes |
| `assets/theme.css` | Phase 1: starter Tailwind v4 token theme (light + dark) — copy into `app/globals.css`, then swap the fonts and brand hue |
