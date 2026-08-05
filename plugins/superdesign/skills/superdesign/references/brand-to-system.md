# Archetype Seed Design Systems

Seven complete, ready-to-ship design languages that seed the adaptive engine. Each is a
full token bundle — color primitives, type trio, radius base, shadow character, motion
curves — not a palette. They exist so that **v1 always lands on a strong floor**: when the
brand-derivation pipeline (see SKILL.md → Phase 1) produces an attribute vector, it snaps to
the nearest archetype, then perturbs the primitives; when there is no brand signal at all,
it ships the archetype verbatim rather than the beige mean everyone converges on.

## Contents

- [How the engine uses these](#how-the-engine-uses-these) — the fingerprint table (type · radius · texture · motion per archetype), the OKLCH hue conventions
- [Design dials](#design-dials-set-these-five-before-layout) — the five named knobs and what each gates, the product-vs-marketing defaults, the seven archetypes on the dials
- [The art-direction brief](#the-art-direction-brief-the-pre-token-ritual) — PROPOSITION / ANCHORS / MOVEMENT are authored here; why adjectives go beige and why anchors are exemplars, not personas
- [The cold-start intake](#the-cold-start-intake) — the three questions a non-designer can answer, the room→float table, the archetype pairs, the movement lock, the anchor rule
- [The font anti-reflex procedure](#the-font-anti-reflex-procedure) — the 4-step reject loop, the serif-in-a-dashboard ban, metric-matched fallbacks, `font-display`
- [Retrieving a starting preset](#retrieving-a-starting-preset-tweakcn-registry) — the tweakcn registry URLs, the verified catalog of preset names, the `registry:style` shape, the offline fallback, the radius personality dial
- The seven archetypes — each a full bundle (personality · palette · type · radius · shadow · motion · signature moves):
  [1. SaaS-minimal](#1-saas-minimal-linear--vercel--raycast-lane) ·
  [2. Editorial](#2-editorial) ·
  [3. Playful](#3-playful) ·
  [4. Dark-premium](#4-dark-premium) ·
  [5. Brutalist](#5-brutalist-neo-brutalism) ·
  [6. AI-dev-tool](#6-ai-dev-tool-code-panel-hero-lane) ·
  [7. Warm-paper](#7-warm-paper)
- [Tuning an archetype](#tuning-an-archetype-intensity-verbs--keyworddial-map) — the intensity verbs (BOLDER / QUIETER / DISTILL) and the keyword→dial map that resolves "clean", "premium", "editorial", "bold", "minimal"
- [The movement layer](#the-movement-layer-orthogonal-to-the-archetype) — movements are a second axis, orthogonal to the archetype and mandatory; includes [the seed axis](#the-seed-axis-across-run-variance) for across-run variance
- [The invariant layer](#what-stays-constant-across-all-seven-the-invariant-layer) — what never changes: 3-tier tokens, fg/bg pairs, the chroma-budget ratios, neutral pairing, dark mode as a second art direction, the Accent and Shape locks, the gates

## How the engine uses these

The brand pipeline compresses inputs into ~6 spectrum floats (Serious↔Playful,
Traditional↔Modern, Warm↔Cool, Restrained↔Bold, Economical↔Premium, Calm↔Energetic). Map
that vector to an archetype with the fingerprint table, then re-seed **only the primitive
layer** — the seed hue, the `--radius` base, the type family, the shadow character, the
easing pair. The semantic and component token layers are **identical across all seven
archetypes** (this is what makes swapping cheap: same trick as dark mode — repoint semantic
aliases at different primitives). Every archetype ships light + dark, obeys the 60-30-10
application rule (neutral 60 / secondary 30 / saturated accent 10), and must clear the same
gate: WCAG AA (4.5:1 body / 3:1 large-UI/focus), validated per foreground/background pair, in both
modes. **Never gate on an APCA Lc number** — no W3C document specifies one (→ `accessibility.md`
§ APCA); compute it as an advisory and never let it override a WCAG 2 failure.

| Archetype | Fingerprint (dominant axes) | Aaker / archetype | Type | Radius base | Texture | Motion |
|---|---|---|---|---|---|---|
| **SaaS-minimal** | Modern+, Cool+, Restrained+, Calm+ | Competence | one neo-grotesque, weight-contrast only | 8px | 0 | fast, productive, no bounce |
| **Editorial** | Traditional+, Warm+, Premium+, Calm+ | Sophistication / Sincerity | display serif + quiet body serif | 2px | 0 | slow, smooth, fade-forward |
| **Playful** | Playful+, Bold+, Energetic+, Warm+ | Excitement | rounded geometric + heavy display | 16px + pills | 0 | springy, expressive, overshoot |
| **Dark-premium** | Premium++, Modern+, Restrained+ | Sophistication | refined/premium grotesque | 10px | 0 | slow, controlled decelerate |
| **Brutalist** | Bold++, Restrained−−, Energetic+ | Outlaw / Creator | mono or heavy grotesque display | 0px | 0 | snappy, mechanical, abrupt |
| **AI-dev-tool** | Modern++, Cool+, Restrained+, Premium+ | Competence / Sage | grotesque UI + mono labels | 4–6px | 1 | snappy expo, one idle breath |
| **Warm-paper** | Warm+, Modern+, Premium+, Restrained+ | Sincerity / Competence | geometric display + humanist + mono | 8px | 1 | snappy expo, seam-draw + one breath |

Type, radius and texture are **outputs, not defaults** — an archetype that leaves any of the three
unstated is an incomplete seed. The Texture column is the archetype's `TEXTURE_LEVEL` starting
value; `GRID_DISCIPLINE` is fixed by the MOVEMENT, not the archetype (→ the movement layer below).

All color values are OKLCH `oklch(L C H)` — L 0–1, C 0–~0.37 (sRGB-safe), H 0–360° — the
canonical space for the whole system (perceptually uniform, Tailwind v4 native, Baseline
since 2023). Neutral hue angles reference the corpus: red ≈ 25, amber ≈ 65, yellow ≈ 95,
green ≈ 150, teal ≈ 190, blue ≈ 259, violet ≈ 300, pink ≈ 350.

## Design dials (set these five before layout)

Five named numeric knobs govern every downstream layout/motion/density rule. Set them once,
per surface, and let one decision cascade instead of a thousand ad-hoc calls. **Never rename
them** (`LAYOUT_VARIANCE`, `ANIM_LEVEL`, `DENSITY_LEVEL` are banned aliases).

| Dial | Range | What it gates |
|---|---|---|
| **DESIGN_VARIANCE** | 1 symmetric → 10 chaotic | **> 4 ⇒ centered-hero BANNED** (force split/asymmetric/left-lead); drives grid fractionality + overlap. |
| **MOTION_INTENSITY** | 1 static → 10 cinematic | **> 3 ⇒ `prefers-reduced-motion` handling REQUIRED**; motion claimed = motion shown (a static surface at 7 is broken). |
| **VISUAL_DENSITY** | 1 gallery → 10 cockpit | **> 7 ⇒ drop card containers** (1px lines/`divide-y` separate data) **+ `font-mono` mandatory on all numbers**; sets section padding band. |
| **GRID_DISCIPLINE** | 0 free → 3 modular | 0 = document flow; 1 = 12-col; 2 = modular field grid (Müller-Brockmann 8/20/32 fields, leading = whole multiple of the baseline unit, every element snaps); 3 = 1px-gap determinism (`grid gap-px` on a contrasting wrapper, `bg-background` cells — never per-cell borders, which double to 2px at intersections). **≥2 ⇒ a baseline unit must be declared as a token and every vertical rhythm value must be a whole multiple of it.** |
| **TEXTURE_LEVEL** | 0 none → 3 material | 0 = flat; 1 = ONE faint technical texture (dot-grid, vertical rules, scan); 2 = grain overlay; 3 = grain + halftone/duotone imagery. **Never stack two textures at the same level. ≥2 ⇒ the grain must live on a fixed `pointer-events-none` overlay, never a scrolling container.** Recipes with real parameter values: → `cookbook/texture.md`. |

The last two are what a MOVEMENT sets and an archetype does not: the seven archetypes fix
colour/type/radius/shadow/motion, a movement additionally fixes grid behaviour and texture. Without
them a movement cannot be expressed as a preset.

**superdesign defaults — the product register inverts the taste-skill baseline.** The flagship
taste skill ships a *marketing* baseline of **8 / 6 / 4** (variance / motion / density); superdesign
is a dense product surface, so it flips two of the three:

| Surface | VARIANCE | MOTION | DENSITY |
|---|---|---|---|
| **Product** (dashboard, app shell, data UI) | **3–4** | **2–3** | **7–8** |
| **Marketing** (landing, about, launch) | **7–8** | **5–7** | **2–4** |
| taste-skill baseline (reference only) | 8 | 6 | 4 |

Infer from vibe words: minimalist/Linear ≈ `5-6 / 3-4 / 2-3`; premium/Apple ≈ `7-8 / 5-7 / 3-4`;
playful/Awwwards ≈ `9-10 / 8-10 / 3-4`; trust-first/public-sector ≈ `3-4 / 2-3 / 4-5`.

**The seven archetypes on the dials** (rough product-register readings; marketing surfaces push
variance/motion up, density down):

| Archetype | VARIANCE | MOTION | DENSITY |
|---|---|---|---|
| **SaaS-minimal** | 3–4 | 2–3 | 6–8 |
| **Editorial** | 5–7 | 3–4 | 2–3 |
| **Playful** | 6–8 | 7–9 | 3–4 |
| **Dark-premium** | 4–6 | 3–5 | 5–7 |
| **Brutalist** | 7–9 | 2–3 (or 8+ if animated) | 6–8 |
| **AI-dev-tool** | 4–6 | 3–5 | 5–7 |
| **Warm-paper** | 4–6 | 3–5 | 4–6 |

**The dials feed downstream, which is why they are set once and never re-derived:**
DESIGN_VARIANCE guards Phase 4's anti-center gate, MOTION_INTENSITY sets the Phase 3 motion
budget, VISUAL_DENSITY sets the Phase 3 spacing and state expectations.

## The art-direction brief (the pre-token ritual)

**Before emitting a single token, fill every field of this `DESIGN BRIEF`.** It is the binding
artefact of SKILL.md → Phase 1c: a token that contradicts the brief is a defect, not a preference,
and a blank field is a blocked phase, not a default.

```
PROJECT NAME:  <memorable, 1-3 words, not the client name>
PROPOSITION:   <exactly one sentence. If it needs "and", it is two briefs.>
AESTHETIC:     <a named direction, ≤4 words>
SPECTRUM:      <the 6 floats>
ANCHORS (2-3): <named real objects/places/products; at least one NON-UI. Each anchor must
               carry at least one PARAMETER, not just a name — "Muji notebook (paper
               oklch(0.977 0.006 85), zero shadow)" not "Muji".>
MOVEMENT:      <one row from the movements table. "Modern" and "clean" are not movements.>
PALETTE:       <3–5 colors, each with its role>
TYPE:          <≤2 families + the pairing logic>
RADIUS:
DIALS:         <VARIANCE / MOTION / DENSITY / GRID_DISCIPLINE / TEXTURE_LEVEL>
TENSION:       <exactly one of: asymmetry | colour clash | scale jump | grid violation>
               <plus the ONE element it acts on>
CONSTRAINT:    <one hard COUNTABLE limit: "exactly 2 hues + neutrals", "radius in {0}",
               "<=3 type sizes". An uncountable constraint is an adjective.>
THE ANOMALY:   <one element that deliberately breaks the system, named in advance and
               justified in one clause. Exactly one. Zero = template; two = noise.>
THREE THINGS THIS IS NOT:
MANDATORIES:   <a11y gates, brand locks, legal — what cannot move>
```

**THE ANOMALY is a device this skill imposes**, grounded in the U-shaped constraint–creativity
finding (145 studies, ICDC2018) — not in the "Persian flaw" story, which no museum or textile
archive documents. Exactly one, named in advance.

Three fields are authored in detail here.

**PROPOSITION** — exactly one sentence. If it needs "and", it is two briefs. Two tests: Ogilvy's
single-minded proposition; Hegarty's test — *would it still hold written on a card held next to the
product?*

**ANCHORS** — one scene sentence + 2–3 named references, **never adjectives.** "Modern, clean,
premium" is unfalsifiable, so the model reverts to the statistical-mean layout: *unnamed ambition
becomes beige.* Name real anchors instead — products, materials, places, objects — so the pipeline
snaps to something specific:

- ✗ "A clean, modern, premium dashboard." → beige.
- ✓ "A flight-deck telemetry panel with the restraint of Linear and the paper warmth of a
  Muji notebook." → Linear + Muji + telemetry are checkable anchors that pin hue, density,
  and shadow character.

Two named anchors minimum, three max; at least one should be a concrete non-UI object or place
(not just another SaaS brand), which is what pulls the system off the SaaS mean. Each anchor carries
at least one **parameter**, not just a name — "Muji notebook (paper `oklch(0.977 0.006 85)`, zero
shadow)", not "Muji".

Anchors are **exemplars, not personas.** Name the artefact ("a Braun ET66 calculator", "a Muji A5
notebook") and attach a parameter to it; do not name a designer and ask the model to be them.
Persona prompting is the weakest mechanism measured: 162 roles × 4 model families × 2,410 questions
found "adding personas in system prompts does not improve model performance," and "the effect of
each persona can be largely random" (arXiv:2311.10054, EMNLP 2024 Findings).

**MOVEMENT** — one row from the movements table below. "Modern" and "clean" are not movements.

**Capturing a named product reference.** If the brief cites a real product ("like Linear",
"Stripe's pricing page"), **capture it before designing** — write down **six mechanics**: type
pairing and weights, palette with roles, radius, elevation recipe, grid/measure, and motion. Design
against those six values, never against the adjective. A named product that is not captured is just
another adjective, and adjectives go beige.

Do not recall the six from memory — a recalled mechanic is invented plausible detail, the same
failure mode as a recalled preset. **`reference-mining.md` owns the procedure**: how to pick three
references instead of one, the five-rung evidence ladder (a first-party `design.md` beats
everything), `scripts/extract-reference.mjs` for measuring them, how each measured value maps into
the brief fields below, and the differentiation gate that stops a mined reference from shipping as a
clone. If you genuinely cannot capture it, say so and ask for one concrete constraint instead.

**Why three candidates with probabilities, and not one.** Phase 1b asks for three complete briefs
each labelled with its probability of being the direction a generic model would produce, then takes
the lowest-probability one that clears every MANDATORY. **Verbalized Sampling** (arXiv 2510.01171)
measures **1.6–2.1×** diversity over direct prompting on creative tasks, training-free, with no
accuracy or safety cost. Transfer to UI is UNVERIFIED but mechanism-level. Never average the three —
averaging is how you arrive back at the mean you were escaping.

## The cold-start intake

Fires at SKILL.md → Phase 1a-0, and only there: the user named a surface and supplied no product,
no audience and no reference. Ask all three questions in one message, print every default, and
build on the defaults in the same turn. An unanswered intake still produces a specific sourced
direction; an answered one is strictly better. Nothing here waits.

**Use no design vocabulary in the questions.** Not "aesthetic", not "palette", not "typography",
not "vibe", not "brand". A user who could answer those would not have triggered this section, and
an adjective in reply is worse than silence — *unnamed ambition becomes beige*.

### Q1 — the room

> *Which room is this for? And finish this in five words: "it lets someone ___".*
>
> A. Somewhere a mistake is expensive — money, health, records, the law.
> B. Somewhere skilled work happens all day with a tool in hand.
> C. Somewhere someone decides whether to buy.
> D. Somewhere someone does this for themselves, unhurried.
> E. Somewhere something is happening now and someone must react.
>
> Default if unanswered: **A** for a product surface, **C** for a marketing surface.

Negative is the left-hand pole of each axis named in § How the engine uses these.

| Room | Serious↔Playful | Trad↔Modern | Warm↔Cool | Restrained↔Bold | Econ↔Premium | Calm↔Energetic |
|---|---|---|---|---|---|---|
| A expensive mistake | −0.8 | +0.2 | 0.0 | −0.7 | +0.1 | −0.6 |
| B skilled work all day | −0.5 | +0.6 | −0.2 | −0.5 | +0.3 | −0.4 |
| C deciding to buy | 0.0 | +0.5 | −0.4 | +0.6 | +0.5 | +0.4 |
| D for themselves | +0.4 | +0.1 | −0.7 | −0.2 | +0.2 | −0.5 |
| E react now | −0.7 | +0.7 | +0.6 | +0.5 | −0.3 | +0.8 |

The five-word blank is the field that matters. Its noun becomes the audience, its verb becomes
PROPOSITION, and its object is the first candidate for the NON-UI anchor — "it lets someone contest
a parking ticket" gives you the ticket, the envelope and the deadline. A tautological blank ("use
my app", "do their work") carries no noun; treat Q1 as unanswered.

**Q1 does not choose the archetype.** Rooms A and B would snap straight back to SaaS-minimal, which
is the defect. Q1 sets the floats and the noun; Q2 sets the archetype.

### Q2 — the mistake you'd accept

> *Both of these are well made and they fail in opposite directions. Which failure would you rather
> ship?*
>
> Two named products, six words each, plus **"neither / haven't used either"**.

| Room | Option 1 → archetype | Option 2 → archetype | Neither → |
|---|---|---|---|
| A | **GOV.UK** — plain, ugly, never once confusing → Brutalist | **Monzo** — your money, but it talks back → Playful | Brutalist |
| B | **Ableton Live** — dense, gridded, nothing decorative → AI-dev-tool | **iA Writer** — one thing on screen, paper → Warm-paper | AI-dev-tool |
| C | **Gumroad** — loud flat colour, no persuasion theatre → Playful | **Aesop** — apothecary restraint, everything is type → Editorial | Editorial |
| D | **Are.na** — a filing cabinet you enjoy → Brutalist | **Bear** — warm paper, serif, no chrome → Warm-paper | Warm-paper |
| E | **Bloomberg Terminal** — black, mono, dense, no chrome → AI-dev-tool | **Citymapper** — colour-coded lines, legible at speed → Playful | AI-dev-tool |

**SaaS-minimal and Dark-premium appear on no pair and in no default.** They are the two lanes the
corpus itself names as reflexes; a menu that offers the mean will be handed the mean.

When a product is chosen, hand its URL to `scripts/extract-reference.mjs` on the Phase 1a path and
design against the six measured mechanics. Never recall them — a recalled mechanic is invented
plausible detail. If the capture fails (exit 3 no page, exit 4 no playwright), say so in one line
and fall to the archetype in the table; the intake still completes.

**THREE THINGS THIS IS NOT is filled from the rejected options**: the unchosen half of the pair,
plus SaaS-minimal and Dark-premium. You never needed to know what the product is to know what it
is not.

### Q3 — the never

> *Finish the sentence: whatever else this does, it must never ___.*
>
> 1. make someone hunt for the thing they came for
> 2. look more finished than it is
> 3. feel fragile
> 4. make someone lose their place
> 5. hide what the machine is doing
>
> Default if unanswered: **1** for a product surface, **4** for a marketing surface.

| Never | MOVEMENT | GRID | TEXTURE | TENSION | CONSTRAINT (countable) | NON-UI anchor + structural parameter |
|---|---|---|---|---|---|---|
| 1 hunt | Swiss / International Typographic | 2 | 0 | scale jump | exactly 2 hues + neutrals | a station departure board — 8/20/32 field grid, leading a whole multiple of the baseline unit |
| 2 finished | Brutalism (web) | 1 | 0 | grid violation | radius in {0} | a photocopied zine — 1px hairlines, zero shadow |
| 3 fragile | Neo-brutalism | 1 | 0 | colour clash | border 3px on every interactive element | a road sign — border 2–4px, shadow offset 4–8px at zero blur |
| 4 lose place | Editorial / print | 0 | 1 | asymmetry | measure 66ch, ≤3 type sizes | a Penguin paperback — 45–75ch, 66 the target |
| 5 hide | Cyberpunk / terminal / CRT | 3 | 1 | colour clash | `font-mono` on every number | an oscilloscope — 1px scan line, single phosphor hue |

Every parameter above is sourced in § The movement layer. **Liquid Glass and Neumorphism are off
the menu** even though they carry numbers: the first is current platform fashion, the second fails
the contrast gate by construction.

**The collision bump.** If Q3's movement is the archetype's own native school (Q2 → Brutalist and
Q3 → 2 or 3), take the next row down the list. A movement that restates the archetype is not a
second axis.

**Form versus voice — the tie-break.** The movement wins **radius**, border width, grid and
texture. The archetype wins colour, type and motion. This extends the split already stated above
(archetypes fix colour/type/radius/shadow/motion; a movement additionally fixes grid and texture) at
the one field the two both claim, which is radius.

### The anchor rule

An intake anchor carries a **structural** parameter — a length, a count, a border width, a grid, a
measure. **Never a colour.** The colour would be recalled, and a recalled colour is invented
plausible detail presented as measurement. Colour is derived from the floats and the archetype;
structure is what the anchor is for.

### Identity versus function

**Differentiate:** accent hue, type stack, canvas lightness, radius base, texture level, elevation
recipe. **Never differentiate:** the 4px spacing grid, the ≤300ms duration ceiling, the two easing
curves, the contrast floors, the state matrix, the 45–75ch measure. Fleeing a settled answer is a
bug, not differentiation — `reference-mining.md` already says this for the mined-reference case;
it holds for every case.

### PROPOSITION on a cold start

PROPOSITION is a commitment about the artifact, never a market claim. "Behaves like an instrument,
not a dashboard" is authorship about a thing you are building. "The fastest way to invoice" is a
claim about a product you know nothing about, and it is fabrication. Hegarty's card test still
applies — hold it next to the artifact, not next to the market.

## The font anti-reflex procedure

Type is the highest-ROI, lowest-risk brand move (→ Fix-Priority §1 in the workflow) and the
single most recognizable AI tell if you reflex to the default. Run this procedure, in order,
before committing a family:

1. **Say 3 physical brand-voice words** — the register in the body, not the mood board
   ("engineered / warm / terse", "loud / raw / mechanical").
2. **List your 3 reflex fonts** — the first three that come to mind for those words.
3. **Check each against the ban list** (→ anti-slop.md — the single source of truth for the
   banned/escape-hatch faces). If any of your three is on it, **reject that one.**
4. **If your final pick == your original reflex, start over** — the reflex is the convergence
   font by definition; distance requires a second choice.

Hard rule regardless of procedure: **serif is ALWAYS banned in a dashboard shell** (a serif on
software UI is a named register-mismatch tell → anti-slop.md); an italic-serif accent word on a
dev tool is the same tell. **System fonts are legit for product** (SaaS-minimal / neutral
briefs) — the ban is on *character* fonts used reflexively, not on an honest system stack.

**Ship the family with a metric-matched fallback.** A webfont without one is a layout shift with a
brand on it. Chrome's own worked example, which is the shape the numbers must have:

```css
@font-face {
  font-family: poppins-fallback;
  src: local("Arial");
  size-adjust: 60.85099821%;
  ascent-override: 164.3358416%;
  descent-override: 57.51754455%;
  line-gap-override: 16.43358416%;
}
```

Once `size-adjust` scales the glyphs, ascent/descent must be divided by the same factor
(105% / 0.6085 ≈ 164%) — **never hand-write these**; generate with Fontaine / `@next/font`, read the
metrics with Capsize or fontdrop.info. A fallback block whose overrides are round numbers next to a
non-round `size-adjust` is a placeholder someone forgot to replace.

`font-display` is then a decision, not a default:

| condition | value |
|---|---|
| self-hosted + metric-matched fallback present | `swap` — the swap is invisible, the fallback occupies identical space |
| no metric-matched fallback, or a brand face that must not flash | `optional` — extremely small block, **no swap period** → minimises CLS |

The block/swap periods in ms (→ `performance.md` §6 for the full table) are **web.dev's
implementation figures, not spec text** — MDN gives the periods only qualitatively and points at
Firefox's `gfx.downloadable_fonts.fallback_delay` prefs. Use them; don't cite them as the spec.

## Retrieving a starting preset (tweakcn registry)

**Retrieve the preset — do not recall one.** A recalled preset is invented plausible OKLCH, which
is exactly the convergence this skill exists to prevent. `https://tweakcn.com/r/registry.json`
lists the catalog — **36 presets as of 2026-08-05**, up from the 15 recorded on 2026-07-26, with
all 15 still present: `modern-minimal`, `t3-chat`, `twitter`, `mocha-mousse`, `bubblegum`,
`doom-64`, `catppuccin`, `graphite`, `perpetuity`, `kodama-grove`, `cosmic-night`, `tangerine`,
`quantum-rose`, `nature`, `bold-tech`. **Read the manifest rather than this list** — it grew by 21
in ten days, and `claude`, which the earlier note called unlisted-but-resolvable, is now listed.
Fetch the nearest at `https://tweakcn.com/r/themes/<name>.json` — a shadcn
`registry:style` whose `cssVars.theme` carries `font-sans`/`font-mono`/`font-serif`, `radius` and
the `tracking-*` ramp, and whose `cssVars.light` / `cssVars.dark` carry the full semantic set as
real OKLCH. If the fetch fails, fall back to `assets/theme.css` and say out loud that you are
working from the bundled starter.

A preset is a **complete design language, not a palette** — take it as the floor, then override its
primitives to the brand seed and snap the result to the nearest archetype below. **Radius is the
sharpest single personality dial:** `2–4px` = serious/fintech, `8–12px` = friendly/consumer,
`16px+` = playful, pill = maximal play. (Scale derivation, the nested-radius rule and the
per-archetype radius bases: `tokens.md` §6 and the fingerprint table above.)

---

## 1. SaaS-minimal (Linear / Vercel / Raycast lane)

**Personality.** Competence made visible. Precise, calm, engineered, gets out of the way.
Reads as "infrastructure built by people who care about craft." Neutrals carry ~90% of the
surface; one restrained accent lives strictly in the 10% action lane. The whole aesthetic is
*restraint as a signal* — every visible element looks like a decision.

**When to use.** B2B SaaS, dashboards, dev tools, productivity, internal tools, data-dense
product UI. **Avoid** for consumer/lifestyle, kids, or anything that needs warmth or delight.

**Color.** Achromatic base, faintly cool-tinted (slate), so grays never read dead. One
considered blue accent — *not* the reflexive `indigo-500 #6366F1`; commit to a real blue at
moderate (not peak) chroma, or go fully achromatic Vercel-style (white/near-black as the
"accent"). Semantic hues standard.

```css
/* light */                              /* dark (a second ramp, authored — not the light one flipped) */
--background:  oklch(0.994 0.002 260);   /* oklch(0.16  0.008 260) */
--foreground:  oklch(0.22  0.010 260);   /* oklch(0.96  0.003 260) */
--muted-fg:    oklch(0.52  0.012 260);   /* oklch(0.68  0.010 260) */
--border:      oklch(0.92  0.006 260);   /* oklch(0.27  0.010 260) */
--primary:     oklch(0.60  0.150 256);   /* oklch(0.68  0.130 256) — desaturated + lighter for dark */
--primary-fg:  oklch(0.99  0.002 260);   /* oklch(0.16  0.010 256) */
--radius: 0.5rem;                        /* 8px */
```
Neutral chroma stays 0.002–0.012 (tinted, not pure C=0). In dark mode drop accent chroma
~0.02 and raise L one step (saturated blue vibrates on dark surfaces).

**Recommended product-shell bundle (the calibrated-neutral / "Stitch" preset).** This is the
closest concrete lane to superdesign's default and the one to reach for when the vector is weak: a
**Zinc/Slate neutral base + exactly ONE accent at saturation < 80%**, on a **warm-not-blue
canvas** — `#F9FAFB` (never a clinical blue-white), surface `#FFFFFF`, ink `#18181B` (Zinc-950,
never `#000`), steel secondary `#71717A`, muted slate `#94A3B8`, whisper border
`rgba(226,232,240,0.5)`. Never mix warm + cool gray systems in one project. Domain picks the
accent: Emerald `#10B981` (growth), Electric Blue `#3B82F6` (SaaS/dev), Deep Rose `#E11D48`
(creative), Amber `#F59E0B` (community). Elevation is one **whisper shadow** —
`0 20px 40px -15px rgba(0,0,0,0.05)` (wide 40px blur, −15px offset, 5% alpha) tinted to the bg
hue — the opposite of the harsh default `shadow-md`. This bundle maps 1:1 onto superdesign's OKLCH
tokens; it is the recommended starting shell for any product surface without a strong brand.

**Type.** One neo-grotesque, weight-contrast only — the cleanest premium move. **Geist**
(Sans + Mono) or **Inter** (Text ≤20px / Display ≥20px via the `opsz` axis). Body 450,
headings 550–600. Scale ratio **1.2–1.25** (minor→major third; dense UI wants a low ratio).
Apply the Inter dynamic-tracking table (0 at ≤12px → −0.011em at 16px → −0.022em floor at
40px+). `tabular-nums slashed-zero` on every metric and data cell. *Trap:* if you pick
Geist, self-host via npm (`geist/font`) — Google Fonts Geist ships no OpenType features, so
`tnum`/stylistic sets silently fail. *Anti-convergence:* Geist is authentic here but is also
the v0/shadcn convergence font — if the brand needs distance, use Inter or a paid grotesque
(Söhne, Neue Haas Grotesk) rather than the escape-hatch Space Grotesk.

**Radius.** Base **8px** (`--radius: 0.5rem`), derive `xs/sm/md/lg/xl` via the shadcn
multiplier pattern (`*0.5 / *0.75 / *0.875 / *1 / *1.5`). Buttons/inputs 8px, cards 12px,
modals 12–16px, tables/dense grids 0px, avatars/tags full. Reads modern/competent/neutral.

**Shadow character.** Crisp and low — the object sits *just* above the page. Alpha
**decreases** per layer (sharp), and fold a hairline ring into the token (Radix trick) so
border-and-shadow read as one system. In dark mode switch the depth cue entirely: lighten
the surface (M3 dark tone ladder 4→10→12→17→22) + a faint inset top highlight; reserve real
shadow for modals only.

```css
--shadow-sm: 0 0 0 1px oklch(0 0 0 / 0.05), 0 1px 2px oklch(0 0 0 / 0.06);
--shadow-md: 0 0 0 1px oklch(0 0 0 / 0.05), 0 4px 6px -1px oklch(0 0 0 / 0.08),
             0 2px 4px -2px oklch(0 0 0 / 0.06);
/* dark: drop the outer layers, keep the ring + inset highlight */
--shadow-md-dark: inset 0 1px 0 oklch(1 0 0 / 0.06), 0 0 0 1px oklch(1 0 0 / 0.08);
```

**Motion.** Fast and productive; <100ms feels instantaneous on hot paths, hard-cap
interactive UI at 300ms. Single primary curve = strong ease-out `cubic-bezier(0.23, 1, 0.32,
1)` (or IBM Carbon productive `cubic-bezier(0.2, 0, 0.38, 0.9)`). Durations: button press
120ms, dropdown 160ms, modal 220ms. **No bounce.** Keyboard-triggered actions get zero
animation. This archetype pairs naturally with a Cmd+K command backbone.

---

## 2. Editorial

**Personality.** Considered, literary, authoritative, unhurried. Hierarchy comes from
**type and whitespace, not boxes** — big serif display against small quiet body, ruled
dividers instead of cards. Feels like a well-set magazine or a thoughtful essay.

**When to use.** Content sites, long-form/blogs, documentation, publishing, portfolios,
premium brand/marketing pages, anything where reading is the product. **Avoid** for
data-dense dashboards or high-frequency tool UI (the register mismatch — an italic serif
headline on a dev tool — is a named slop tell).

**Color.** Warm paper neutral (sand/stone), never clinical white. Text is warm near-black
(≈ `rgba(0,0,0,0.9)`), not `#000`. Accent is a single *restrained, dusty* ink — oxblood,
forest, or navy at low chroma — used sparingly for links and rules.

```css
/* light */                              /* dark */
--background:  oklch(0.980 0.008 85);    /* oklch(0.19  0.008 70)  — warm near-black */
--foreground:  oklch(0.24  0.012 60);    /* oklch(0.92  0.010 80) */
--muted-fg:    oklch(0.50  0.015 60);    /* oklch(0.66  0.012 75) */
--border:      oklch(0.88  0.010 75);    /* oklch(0.30  0.010 70) */
--primary:     oklch(0.45  0.120 25);    /* oklch(0.62  0.110 25)  — oxblood link/accent */
--radius: 0.125rem;                      /* 2px */
```
Chroma stays 0.08–0.13 on the accent (muted, "dusty"), neutrals 0.008–0.015 warm-tinted.

**Warm-editorial / Notion-tier variant (the palette IS the style).** For a document-register
editorial (as opposed to literary-serif), the concrete corpus values: canvas `#FFFFFF` or warm
bone `#F7F6F3` / `#FBFBFA`; card surface `#FFFFFF` / `#F9F9F8`; borders/dividers ultra-light
`#EAEAEA` or `rgba(0,0,0,0.06)`. Body text **never pure black** — off-black `#111111` or
`#2F3437` at line-height 1.6; secondary muted gray `#787774`. Semantic color arrives *only* as
washed-out **pastel bg+text pairs** (the paired text guarantees legible tags): Pale Red
`#FDEBEC`/`#9F2F2D`, Pale Blue `#E1F3FE`/`#1F6C9F`, Pale Green `#EDF3EC`/`#346538`, Pale Yellow
`#FBF3DB`/`#956400`. Encode each as `--tag-{hue}-bg` / `--tag-{hue}-fg` → shadcn `Badge`
variants. No saturated accent fills, no primary-colored hero blocks.

**Type.** The one archetype that *should* pair two families. High-contrast display serif +
quiet body. Display: **Fraunces**, **Playfair Display**, or **Newsreader** (700, tight
tracking −0.02em on large sizes). Body: a readable serif (**Source Serif 4**, **Crimson
Pro**, **Lora**) or a humanist sans for contrast. Mono captions optional (IBM Plex Mono).
Scale ratio **high, 1.333–1.5** (perfect fourth → fifth — dramatic, headings must dominate;
push size contrast to ~3–5:1). **Measure: `max-width: 66ch` on every single-column prose wrapper,
`max-width: 48ch` on any multi-column body.** Bringhurst puts the satisfactory band at 45–75
characters per line with **66 as the ideal**, and multi-column at 40–50; Butterick's band is 45–90
with 60–70 practical. Caveat that survives both: **`ch` is the advance width of `0`, not a
character** — it is wider than the mean lowercase, so count the rendered characters once per font
and adjust. `oldstyle-nums` in serif body. Base 18px reads more premium than 16 for long-form.

**Radius.** **0–2px** (`--radius: 0.125rem`, or 0). Sharp corners read serious/editorial;
tables and rules stay 0. Roundness here would undercut the authority.

**Shadow character.** Essentially flat — the **No-Shadow law**: never `shadow-md/lg/xl`; if a
shadow appears at all it is ultra-diffuse at **< 0.05 opacity**. Depth is **hairline rules and
generous whitespace**, not elevation. A 1px border out-performs a shadow on near-white paper
(the shadow just vanishes). Cards get exactly `border: 1px solid #EAEAEA`, radius 8–12px max
(never `rounded-full` on a large container/card), internal padding 24–40px; card hover lifts
only from `0 0 0` to `0 2px 8px rgba(0,0,0,0.04)` over 200ms. Reserve one soft shadow for
overlays/modals only. Flatness + hairline borders is exactly what reads as premium-editorial
rather than "SaaS card with a default shadow" — so when elevation *does* appear, it means
something.

```css
--shadow-sm: none;                       /* editorial is flat by default (< 0.05 opacity if at all) */
--shadow-card-hover: 0 2px 8px oklch(0 0 0 / 0.04);   /* the only card lift, 200ms */
--shadow-overlay: 0 8px 40px oklch(0 0 0 / 0.08), 0 0 0 1px oklch(0 0 0 / 0.06);
--rule: 1px solid var(--border);         /* the primary separator */
```

**Motion.** Slow, smooth, restrained — reveals and cross-fades, no snap. Strong ease-in-out
`cubic-bezier(0.77, 0, 0.175, 1)` for on-screen movement; simple `ease-out` for reveals.
Durations **300–500ms** (content reveals ~480ms). No bounce. One well-orchestrated staggered
page-load reveal (30–80ms between items) beats scattered scroll fade-ins.

---

## 3. Playful

**Personality.** Excitement, warmth, energy, delight. High-chroma color, round shapes,
springy motion. Approachable and human without being childish (unless it's for kids, then
lean further). Optimistic and tactile — the UI wants to be touched.

**When to use.** Consumer apps, social, fintech-for-humans, wellness, education, games,
mobile-first products, onboarding-heavy flows. **Avoid** for enterprise/finance/trust-
critical UI and any high-frequency repeated action (bouncy easing gets tiresome and undercuts
credibility fast).

**Color.** Vibrant, high-chroma seed — a warm coral/orange or a candy pair, applied as flat
fills (never rainbow gradients). Even here, obey 60-30-10: the saturated accent stays scarce;
neutrals are warm-tinted and light/airy. M3 `Vibrant`/`Expressive` scheme variant fits.

```css
/* light */                              /* dark */
--background:  oklch(0.99  0.006 60);    /* oklch(0.18  0.010 60) */
--foreground:  oklch(0.25  0.020 40);    /* oklch(0.95  0.008 60) */
--muted-fg:    oklch(0.55  0.030 45);    /* oklch(0.70  0.020 55) */
--border:      oklch(0.90  0.020 55);    /* oklch(0.30  0.015 55) */
--primary:     oklch(0.68  0.190 40);    /* oklch(0.72  0.175 40)  — vivid coral */
--accent-2:    oklch(0.72  0.200 350);   /* optional candy pink second hue */
--radius: 1rem;                          /* 16px */
```
Chroma runs high (0.18–0.24 on accents). In dark mode ease chroma down ~0.02 and raise L so
it doesn't vibrate.

**Type.** Rounded/humanist geometric with a heavy display. **Satoshi**, **Clash Display**,
**Cabinet Grotesk**, or **Bricolage Grotesque**; display weights 700–900, high x-height body
for friendliness. Scale ratio **1.25–1.333** (balanced→confident). Positive tracking on
uppercase labels (+0.04–0.1em). Weight extremes (300 body vs 800 display) beat a timid
400/600 split.

**Radius.** **16–24px** (`--radius: 1rem`, up to 1.4rem for very soft), **full pills for
CTAs and chips**. Rounded shapes are processed faster and read as safe/friendly (the contour
bias). Mind the nesting rule (`inner = outer − padding`, clamp ≥ 0) — generous radii make
concentric-corner errors more visible.

**Shadow character.** Soft, diffuse, floaty — alpha **increases** per layer. Optionally tint
the shadow toward the accent hue (subtle), never a neon glow (the #1 "cyberpunk-by-default"
slop tell). Larger, softer shadows imply higher/lighter objects.

```css
--shadow-md: 0 2px 4px oklch(0.68 0.19 40 / 0.06),
             0 8px 16px oklch(0.68 0.19 40 / 0.10),
             0 16px 32px oklch(0.68 0.19 40 / 0.14);
```

**Motion.** Expressive springs with a little overshoot — this is where delight lives. Spring
`{ visualDuration: 0.4, bounce: 0.25 }` (keep bounce 0.1–0.3) for physical props; IBM Carbon
expressive `cubic-bezier(0.4, 0.14, 0.3, 1)` for tweens. Durations 250–400ms. Spend the
delight budget *inversely to frequency*: confetti/celebration on rare first-time moments,
calm on hot paths.

---

## 4. Dark-premium

**Personality.** Sophisticated, exclusive, focused, expensive. A tinted near-black canvas
with depth built from *lightening surfaces*, one vivid jewel-tone accent, and slow deliberate
motion. Reads as a pro tool or a luxury product — Raycast/Linear-dark energy, not a gamer
theme.

**When to use.** Dev tools, creative/pro apps, crypto/finance-premium, media players,
AI/agent products, anything that wants to feel focused and high-end. Often paired with a
light mode; "dark-first" is a legitimate choice here. **Avoid** as a reflex — permanent dark
mode + all-caps labels + colored glows is itself a named slop cluster; it must be a real
decision, not the default cool look.

**Color.** Never pure `#000` (causes OLED smearing/halation) — a tinted near-black. Depth =
a surface ladder that gets *lighter* with elevation (M3 dark tones), plus hairline rings.
Text is a white-alpha ladder (87% / 60% / 38%), not `#fff`. Single accent, chroma boosted to
stay vivid on dark.

```css
--background:      oklch(0.15  0.012 260);   /* canvas — tinted near-black, not #000 */
--surface:         oklch(0.19  0.012 260);   /* +1 elevation (lighter) */
--surface-high:    oklch(0.23  0.012 260);   /* modals/menus */
--foreground:      oklch(0.97  0.003 260 / 0.90);
--muted-fg:        oklch(0.97  0.003 260 / 0.60);
--border:          oklch(1 0 0 / 0.08);      /* hairline ring, alpha-white */
--primary:         oklch(0.70  0.170 250);   /* electric blue jewel accent */
--primary-fg:      oklch(0.16  0.010 260);
--radius: 0.75rem;                           /* 12px — the crafted end of the 8–12px band.
                                             NOT shadcn's 0.625rem: shipping the framework default
                                             is the tell anti-slop.md § SUBSTRATE-DEFAULTS fires on. */
```
Swap the accent hue for the brand (violet ≈ 300, teal ≈ 190, gold/amber ≈ 85). Keep chroma
0.15–0.19 — vivid but singular. A matching light mode is **authored** (canvas ≈ 0.98, text ≈ 0.22),
not derived by inverting these values — see the dark-mode invariant at the end of this file.

**Type.** Refined neo-grotesque for UI — **Inter Display**, **Geist**, or a premium grotesque
(**Söhne**, **Neue Haas Grotesk**). For a luxury-editorial dark variant, a Didone display
(Didot/Playfair) over a neutral sans body. Body 400–450 (lighter weights read fine on dark),
headings 550–650. Scale ratio 1.25. Body text uses the white-alpha ladder, never solid white
(halation).

**Radius.** **8–12px** (`--radius: 0.75rem`) — enough to feel crafted, restrained enough to
stay serious. Optional premium upgrade: `corner-shape: squircle` (Chrome) / Figma corner
smoothing ≈ 60% on hero surfaces, degrade to plain radius.

**Signature "expensive object" moves (the high-end / Doppelrand kit — use sparingly on hero
surfaces).** These are the strongest machined-hardware cues, all concentric-radius disciplined:
- **Double-bezel (Doppelrand).** Never place a premium card flat on the page — nest two
  enclosures like a glass plate in an aluminium tray. Outer shell: subtle bg (`bg-white/5`),
  hairline `ring-1 ring-white/10`, padding `p-1.5`–`p-2`, large radius `rounded-[2rem]`. Inner
  core: distinct bg, inner highlight `shadow-[inset_0_1px_1px_rgba(255,255,255,0.15)]`, and a
  **mathematically smaller concentric radius `rounded-[calc(2rem-0.375rem)]`** (the `calc()`
  keeps an equal border gap all around — the same nesting rule as `inner = outer − padding`).
- **Button-in-button.** A primary pill's trailing arrow (`↗`) never sits naked beside the
  label — nest it in its own circular wrapper (`w-8 h-8 rounded-full bg-white/10`), flush with
  the button's right inner padding; on hover the inner circle translates diagonally + `scale-105`,
  the whole button `active:scale-[0.98]`.

**Shadow character.** Shadows barely read on dark, so **elevation is the lighter surface**,
not the shadow. Use the surface ladder + a faint inset top highlight (the light-catch edge)
as the primary cue; add a real diffuse shadow only on the top 1–2 levels (modals) for extra
separation. No colored glows.

```css
--elev-1: inset 0 1px 0 oklch(1 0 0 / 0.06), 0 0 0 1px oklch(1 0 0 / 0.06);
--elev-modal: inset 0 1px 0 oklch(1 0 0 / 0.06), 0 0 0 1px oklch(1 0 0 / 0.08),
              0 16px 48px oklch(0 0 0 / 0.55);
```

**Motion.** Slow, smooth, controlled — deliberate reads as expensive. Emphasized-decelerate
`cubic-bezier(0.05, 0.7, 0.1, 1)` for enters, durations **300–500ms**. No bounce, ever
(bounce reads cheap here). Spatial navigation can use a critically-damped spring (damping ~1,
no overshoot). Disable transitions during theme swap. For a mass-and-physics premium feel, the
high-end house curve is `transition-all duration-700 ease-[cubic-bezier(0.32,0.72,0,1)]`, and
the single most AI-omitted detail is **entry blur**: scroll-in elements move
`translate-y-16 blur-md opacity-0` → `translate-y-0 blur-0 opacity-100` over 800ms+ (blur-up,
not just a fade-rise).

---

## 5. Brutalist (neo-brutalism)

**Personality.** Loud, raw, confident, anti-corporate. Hard edges, thick black borders,
flat saturated color blocks, hard-offset shadows with zero blur, and type as a graphic
element. Zero apology. The aesthetic *is* the statement — it deliberately breaks the smooth-
SaaS consensus.

**When to use.** Portfolios, creative agencies, indie/dev products with attitude, launch/
landing pages, music/culture, developer marketing that wants to stand out. A deliberate
"name the aesthetic family" choice — never the fallback. **Avoid** for trust-critical flows
(banking, healthcare), dense data tools, or accessibility-sensitive contexts unless the
contrast is carefully managed.

**Color — commit to ONE substrate, never mix.** Brutalism is bimodal; a hybrid reads as an
accident. Pick one per project: **(a) Swiss-industrial (light)** — bg `#F4F4F0` or `#EAE8E3`
(unbleached documentation paper), fg `#050505`–`#111111` (carbon ink); **(b) Tactical-telemetry
(dark)** — bg `#0A0A0A` or `#121212` (deactivated CRT, **never pure `#000000`**), fg `#EAEAEA`
(white phosphor). Both modes share **exactly ONE accent: Hazard Red `#E61919`** (or `#FF2A2A`)
— strike-throughs, structural dividers, vital data only. Terminal Green `#4AF626` is optional
on **exactly one** element (one status dot / one readout), never as body text. Apply saturated
primaries as **flat fills, never gradients** (acid yellow, pure red, electric blue, hot pink).

```css
/* (a) Swiss-industrial LIGHT */               /* (b) Tactical-telemetry DARK */
--background:  oklch(0.955 0.003 100);         /* #F4F4F0 */   /* oklch(0.14 0 0) — #0A0A0A, not #000 */
--foreground:  oklch(0.16 0 0);                /* #111111 */   /* oklch(0.93  0 0)  — #EAEAEA phosphor */
--border:      oklch(0.16 0 0);                /* black, THICK */ /* oklch(0.93 0 0) — light hairlines */
--accent:      oklch(0.58 0.235 27);           /* Hazard Red #E61919 — the ONLY accent, both modes */
--status-live: oklch(0.86 0.24 138);           /* Terminal Green #4AF626 — ONE element max */
--radius: 0;                                   /* hard corners, ABSOLUTE rounded-none everywhere */
--border-width: 2px;                           /* SEED AXIS: 2–4px solid — the signature */
```
Chroma runs high and flat (0.17–0.24). Near-max contrast and big color blocks are the point
here, not a violation. A single hazard-red mark across a monochrome field makes every red read
as a live signal.

**Grid — 1px-gap determinism (no border math).** Generate razor-thin rules *without* border
declarations: `display: grid; gap: 1px` on a wrapper whose bg contrasts the child cells
(`grid gap-px bg-border` wrapper, `bg-background` cells). This yields mathematically perfect
single-pixel rules that never double to 2px seams at intersections the way per-cell borders do.
Anchor everything to grid tracks — nothing floats. `+` crosshair glyphs at intersections.

**Type.** Monospace or heavy grotesque display as a graphic device. **Space Mono**,
**JetBrains Mono**, **Archivo** (heavy), or a condensed heavy display. Weight extremes
(100/200 vs 800/900) and **size jumps of 3×+**. All-caps labels are legitimate here (a
deliberate choice, not a reflex) with positive tracking. High-contrast pairing —
display + monospace — is the brutalist signature.

**Radius.** **0px** (`--radius: 0`). Every corner is hard. Rounding anything breaks the
language.

**Shadow character.** Hard **offset** shadow — solid color, **no blur, no spread falloff**.
The documented convention is **offset 4–8px equally in x and y, with 6–8px the "classic" heavy
value**, paired with a **2–4px** solid border. Both are **seed-axis values, not constants** — pick
one pair per project and hold it, or two brutalist projects come out identical. This is the exact
opposite of the layered-penumbra rule and is intentional.

```css
/* light end of the range — roll the offset per project */
--shadow-sm: 2px 2px 0 var(--foreground);
--shadow-md: 4px 4px 0 var(--foreground);
--shadow-lg: 6px 6px 0 var(--foreground);
/* heavy end, still inside the documented band: 4px / 6px / 8px on the same three rungs */
/* hover = shift toward the shadow, shrink the offset (the object "presses in") */
```

**Motion.** Snappy, mechanical, or none. Short `linear` / fast `ease-out`, **100–150ms**. No
smoothing softness — motion can be abrupt on purpose. Hover = hard `translate(2px, 2px)` +
shadow offset collapse (the pressed-in effect), instant on `:active`. Never spring/bounce.

---

## 6. AI-dev-tool (code-panel-hero lane)

**Personality.** Precise, technical, credible — "built by engineers who ship." The dominant 2026
look for AI-infra / developer-API products (Supermemory, AgentMail, HydraDB, React Bits, Vercel,
Zed). It proves the product *is* code and *is* trusted, then gets out of the way. A specialization
of SaaS-minimal / Dark-premium with a fixed **pattern language** more than a distinct palette.

**When to use.** Developer tools, APIs, SDKs, AI/agent infra, databases, DX products, technical
docs marketing. **Avoid** for consumer/lifestyle or non-technical audiences (a code panel becomes
noise, not proof).

**Two modes — pick one, never mix on a surface:**
- **Dark** (AgentMail / Vercel / React Bits): tinted near-black + one faint technical texture + one
  saturated accent.
- **Warm-paper light** (Supermemory): cream/paper canvas + electric-blue accent + navy-*tinted*
  (not gray) borders — a rarer, premium-feeling take. Tokens below are from Supermemory's live CSS.
  This mode is §7's design language specialized for dev tools; when the product is *not* a dev
  tool but the vector still says Warm+Modern+Premium, use the standalone **Warm-paper** archetype (§7).

**Color.**
```css
/* DARK */
--background: oklch(0.14 0.004 260);          /* tinted near-black (AgentMail) — never #000 */
--foreground: oklch(0.97 0.003 260 / 0.90);
--border:     oklch(1 0 0 / 0.08);            /* hairline alpha-white */
--primary:    oklch(0.62 0.200 258);          /* ONE saturated accent (blue/violet/orange) */

/* WARM-PAPER LIGHT (Supermemory: #FAF7F2 / #0562EF / #0B1015) */
--background: oklch(0.975 0.006 85);          /* warm cream paper */
--foreground: oklch(0.20 0.015 250);          /* blue-black ink, not #000 */
--muted-foreground: oklch(0.50 0.020 250);
--border:     oklch(0.90 0.012 250);          /* NAVY-tinted hairline, not neutral gray */
--primary:    oklch(0.55 0.220 258);          /* electric blue #0562EF */
--radius: 0.375rem;                           /* 4–6px, small/blocky */
```
Ration the accent to CTA + one highlight (60-30-10); tint neutrals toward the accent hue.

**Type.** Grotesque UI (Space Grotesk / DM Sans / Geist) + **mono for labels and the code panel**
(DM Mono / JetBrains Mono / Geist Mono) — **uppercase wide-tracked mono eyebrows are the genre
signature**. Optional **monospace/pixel display** for systems/DB products (HydraDB) to signal
precision; a serif-italic accent word (21st.dev "*beautiful*") is a legit craft counter-signal.

**Radius.** **4–6px** small/blocky (`--radius: 0.375rem`) — technical, not fully sharp, not soft.

**Shadow / texture.** Flat + hairline; depth from borders. **Exactly ONE faint technical texture** —
dot-grid (Supermemory), vertical rules (HydraDB), or binary/scan (AgentMail); never stack them.
Optional **bracket / crop-mark framing** on a single element (blueprint motif). No neon glows.

**Motion.** Snappy, productive, expo. Signature `cubic-bezier(0.22, 1, 0.36, 1)` @ 120–240ms
(Supermemory's live curve). One idle "breathing" accent (logo/orb) is a tasteful hero
micro-interaction; everything else < 200ms. Frequency gate applies (command menu = no animation).

**Signature patterns (ship these — they define the genre):**
- **Code-panel hero** — a real syntax-highlighted snippet (bonus: language tabs Py/TS/cURL/CLI) as
  the hero visual; doubles as proof + docs. → `cookbook/code-panel-hero.md`.
- **Copyable install-command pill** — a `$ npx <tool> setup` chip with a copy button.
- **Credential badges near the hero** — GitHub stars, YC, funding, mono "used by" logo wall (the
  dev audience's social proof).

---

## 7. Warm-paper

**Personality.** Technical warmth — precise like an engineering blueprint, warm like good
paper. Cream canvas, blue-black ink, one electric accent, mono labels, dashed-grid dividers.
Reads as "careful people built this *for humans*," splitting the difference between
SaaS-minimal's cool restraint and Editorial's literary warmth. Corpus anchor: Supermemory
(by Memetic Design) — the rarest lane of the seven in the wild, which is exactly why it
doesn't read as template.

**When to use.** Human-facing technical products: AI companions and consumer-AI apps,
note-taking / PKM / knowledge tools, education, docs-as-product, productivity, health,
fintech-for-humans — anywhere the vector lands Warm+ Modern+ Premium+ but *not* Playful and
*not* dev-tool-cold. This fills a real hole in the vector space: before it, a
warm-modern-restrained brief had no honest landing spot (Editorial is Traditional+, Playful
is Bold+/Energetic+, AI-dev-tool is Cool+). **Avoid** for dev-infra audiences that expect a
dark terminal (→ §6 dark mode), luxury exclusivity (→ Dark-premium), or loud statement
brands (→ Brutalist / Playful). A dev tool that wants this feel uses §6's warm-paper-light
mode — the same language plus the code-panel pattern kit.

**Color.** Warm cream paper — never clinical white — with blue-black *ink* text (not `#000`)
and ONE saturated electric-blue accent. The signature trick: **borders and shadows are
navy-tinted, never neutral gray** — low-alpha navy hairlines harmonize with the accent
instead of reading dead. Cards sit near-white *on* the cream, so elevation reads as
"brighter paper." All pairs below are WCAG-AA-verified (computed, both modes).

```css
/* light */                                   /* dark ("ink" mode) */
--background:  oklch(0.977 0.006 85);         /* oklch(0.19  0.012 250) — warm blue-black ink */
--card:        oklch(0.995 0.002 85);         /* oklch(0.23  0.012 250) */
--foreground:  oklch(0.21  0.015 250);        /* oklch(0.95  0.006 85)  — paper-tinted white */
--muted-fg:    oklch(0.48  0.020 250);        /* oklch(0.70  0.015 250) */
--border:      oklch(0.30 0.08 258 / 0.12);   /* oklch(0.85 0.04 250 / 0.16) — tinted, not gray */
--primary:     oklch(0.55  0.215 258);        /* oklch(0.68  0.165 258) — electric blue, raised */
--primary-fg:  oklch(0.995 0.002 85);         /* oklch(0.17  0.015 250) — ink on the lighter blue */
--radius: 0.5rem;                             /* 8px */
```

Accent chroma stays high (0.20–0.22 light / 0.16–0.17 dark) but the accent itself is rationed
hard to the 10% action lane; neutrals carry warmth via hue (paper ≈ 85, ink ≈ 250), not chroma.

**Type.** Geometric-quirky display + humanist body + mono labels. The corpus trio is
**Space Grotesk / DM Sans / DM Mono**. On warm paper this is authentic — the named
escape-hatch cliché is Space-Grotesk-*plus-teal-on-near-black*, not the face itself — but if
the brand needs distance, swap the display to **Bricolage Grotesque** or **Cabinet Grotesk**.
Display tracking −0.02…−0.04em; **uppercase mono eyebrow labels at +0.1–0.16em** head every
section. The tight-display / wide-mono-label contrast is the core typographic signature.
Body 16–18px at weight 400–450, scale ratio 1.25.

**Radius.** Base **8px** (`--radius: 0.5rem`) — chips 4px, cards 10–12px, pills full. Blocky
enough to feel drafted, round enough to stay warm. Nothing over-rounded.

**Shadow character.** **Blue-tinted layered shadows**, matching the tinted borders — never
neutral gray on a branded surface. Fold the hairline in via the `0 0 0 1px` trick; the focus
ring is soft blue at ~10–12% alpha over the crisp outline.

```css
--shadow-card:  0 1px 2px oklch(0.25 0.09 258 / 0.16), 0 8px 18px -8px oklch(0.55 0.215 258 / 0.35);
--shadow-modal: 0 32px 64px -24px oklch(0.20 0.015 250 / 0.28), 0 0 0 1px oklch(0.20 0.015 250 / 0.04);
--ring-soft:    0 0 0 4px oklch(0.55 0.215 258 / 0.12);
/* dark: elevation = lighter surface + hairline; keep one real shadow for modals only */
```

**Motion.** Snappy, decisive expo settle — signature `cubic-bezier(0.22, 1, 0.36, 1)` at
**120–240ms**. Two earned exceptions: **seam-draw** (dashed dividers animate
`stroke-dashoffset` → 0 on scroll — the blueprint "drawing itself") and ONE idle
**breathing presence element** (the Orb pattern: breathe when idle, pulse when busy) for
AI products. Everything else settles fast; no bounce.

**Signature patterns (the blueprint kit — pick 2–3, never all):**
- **Dashed grid dividers with plus-mark intersections** — content in bordered blocks, `+`
  glyphs where hairlines cross.
- **Uppercase mono eyebrow** over every section heading.
- **Window-chrome mockup** (traffic-light dots) framing product shots.
- **Frosted nav:** `backdrop-filter: blur(10px) saturate(140%)` — the saturation boost is
  what keeps cream from going gray under the blur.

---

## Tuning an archetype (intensity verbs + keyword→dial map)

Once an archetype is seeded, "make it more/less X" is a **dial move on the existing system**,
not a new language. Amplify what's there before adding anything (a new token is a spec change,
not a styling whim → anti-slop.md). The intensity verbs each pull specific levers:

- **BOLDER** = amplify *contrast*, not volume. Raise contrast between primary/secondary/tertiary
  and pick **one focal point**; everything louder is flatter, not bolder. On product this means
  stronger hierarchy / weight-contrast / density, **not** theatrics (drama corrodes a trusted
  tool). Ship test: if someone would believe "AI made this bolder" on sight, you reached for
  gradients/glass/neon/glow and failed.
- **QUIETER** = desaturate to **70–85%** (drop OKLCH chroma ~15–30%), let neutrals carry the
  surface, hold color to the 10% accent lane; step weights **down** (900→600, 700→500) and
  recover hierarchy with space. Keep one anchor — quiet ≠ grayscale, and the POV must survive.
- **DISTILL** = **one goal, one primary action**, everything else tertiary or hidden; cap to
  1–2 colors + neutrals, 3–4 sizes, 2–3 weights; flatten nesting (never card-in-card); cut copy
  in half, twice. All-caps only where the archetype already earns it. Don't oversimplify a
  genuinely complex domain (mystery ≠ minimalism).

**Keyword → dial map** (named user words resolve deterministically, never as "add more effects"):

| Keyword | Resolves to |
|---|---|
| **"clean"** | VISUAL_DENSITY **down**, clarity up; more whitespace than the AI instinct. |
| **"premium"** | clarity high, art-direction **controlled** (not maxed); one considered accent, no gradient-text shortcut. |
| **"editorial"** | type contrast + asymmetry **up** (DESIGN_VARIANCE up); serif display allowed *only* off the dashboard shell. |
| **"bold"** | contrast up on ONE focal point (see BOLDER); not chroma/glow. |
| **"minimal"** | density down, variance mid; restraint IS the design — suspend the "add variation" gates. |

---

## The movement layer (orthogonal to the archetype)

An ARCHETYPE fixes **register** (who this is for). A MOVEMENT fixes **signature** (what school it
belongs to). They compose: SaaS-minimal × Swiss is a different system from SaaS-minimal ×
Japanese-minimal, and both are still SaaS-minimal. Pick exactly one of each. **Never blend two
movements on one surface.**

Selecting a movement is **MANDATORY** and the default "none" is **BANNED** — "none" is the
statistical mean under another name. Movements are not archetypes 8–23; they are a second axis.

Cells marked ° are **DERIVED** — a translation to screen parameters, not a sourced value. Cells
marked ✱ are **UNVERIFIED** — no source in the corpus carries a value. Ship a ✱ cell only as an
explicit invention of your own, never as canon.

| Movement | Palette behaviour | Type | Grid behaviour | Radius | Shadow | Texture | Motion |
|---|---|---|---|---|---|---|---|
| **Swiss / Int'l Typographic** | achromatic + exactly 1 flat spot colour; neutrals C ≤ 0.01, accent C 0.15–0.20° | Akzidenz-Grotesk / Helvetica / Univers; **flush-left ragged-right** | mathematical modular grid, **8 / 20 / 32 fields**; leading = whole multiple of baseline unit, everything snaps | 0° | none — hierarchy is position + weight° | none; **objective documentary photography** | 120–160ms linear, or none° |
| **Bauhaus** | primary R/Y/B + black + white as flat fills; **≤3 hues**, no tints, no gradients° | Bayer universal alphabet — **single case, lowercase only**, geometric primitives, uniform stroke weight ("even colour on the page") | geometric; diagonals permitted° | **0 or full circle only, nothing between**° | none° | none° | rotate/translate primitives, linear, 200–300ms° |
| **Brutalism (web, Copeland)** | browser defaults; unstyled links **underlined**° | system/default; content-first | document flow; **"view content by scrolling"** | 0° | none° | none — "decoration when needed and no unrelated content" | none; **"performance is a feature"** |
| **Neo-brutalism** | flat saturated fills, no gradients; one hazard accent | heavy grotesque + mono; size jumps ≥3× | **1px-gap grid** (`grid gap-px` on a contrasting wrapper) — never per-cell borders | **0** strict / 4–8px soft variant | **hard offset, 0 blur, solid colour, 4–8px x+y** (6–8 classic) | none | 100–150ms linear; hover = `translate(2px,2px)` + offset collapse |
| **Memphis** | 4–6 hues at C 0.18–0.26, **flat fills only**, on white or black° | heavy geometric display° | apparently random surface over a **hidden geometric system (equilateral triangles)** | mixed 0 / full circle° | none° | **exactly one scatter pattern** (Bacterio dots / squiggle / terrazzo), used once° | none, or a hard 100ms snap° |
| **Y2K / cybercore** | ✱ | ✱ | ✱ | ✱ | ✱ | chrome, translucent plastic ✱ | ✱ |
| **Frutiger Aero** | **white / green / blue** | Frutiger family | ✱ | large, glossy° | glossy highlight + soft drop° | **wet-look gloss, cloudy sky, water droplets, bubbles, lens flare, aurora, bokeh** | ✱ |
| **Editorial / print** | warm paper neutral; 1 dusty ink accent, C 0.08–0.13° | high-contrast display serif + quiet body; **measure 45–75 cpl, ideal 66; multi-column 40–50** | baseline grid; ruled dividers instead of cards° | 0–2px° | flat; < 0.05 opacity if present° | paper stock, letterpress bite° | 300–500ms cross-fade, no snap° |
| **Cyberpunk / terminal / CRT** | 1 phosphor hue on near-black (never `#000`)° | monospace only° | fixed character cell° | 0° | none; glow is the shadow° | **scanlines: every 2nd row, 20–30% weak / 60–70% strong; phosphor persistence 20–30ms; barrel warp; one preset = opacity 0.25, persistence 0.12** | flicker/typewriter, linear° |
| **Skeuomorphism (pre-2013)** | material-derived (leather, wood, felt)° | contextual to the imitated object° | object-shaped, not grid° | matched to the real object° | real cast shadow + bevel° | photographic material fills° | mimic physical mechanism° |
| **Liquid Glass (2025–26)** | monochromatic by default; symbols/text darken over light content and lighten over dark | system font; vibrancy label ladder (avoid quaternary on thin/ultraThin) | **functional layer floats above content; never in the content layer** | rounded, "nest neatly in the rounded curves of modern devices" | **lensing** — bends/shapes/concentrates light, does not scatter | `regular` vs `clear`; **`clear` over bright content needs a 35% dark dimming layer**; content layer uses ultraThin/thin/regular/thick | materialize in/out by **modulating lensing, not fading**; "visuals AND motion designed as one"; gel flex on touch |
| **Claymorphism** | saturated pastels ✱ | rounded geometric ✱ | ✱ | very large (24–40px) ✱ | **outer soft drop + two inner highlights** ✱ | none ✱ | soft spring ✱ |
| **Glassmorphism** | translucent fill over a colourful ground° | any° | floating cards° | 12–24px° | 1px light hairline + soft drop° | backdrop blur (a **scatter**, unlike lensing) | fade° |
| **Neumorphism** | **single flat background colour**; shadows are tints of it | any° | flat plane° | 12–24px° | **`9px 9px 18px #bec3c9, -9px -9px 18px #ffffff`** — dual light/dark on same-colour bg | none | press = shadow inversion° |
| **Japanese minimal** | white as **emptiness**, not background; ≤2 values + 1 ink° | quiet, one family, small° | **the empty interval (*ma*) is the largest composed element**, not leftover space° | 0–4px° | none° | uncoated paper, natural fibre° | slow, 400–600ms, ease-in-out° |
| **Maximalism** | ✱ as a movement — ship as a dial: ≥6 hues, C ≥ 0.20, pattern density high° | mixed families° | layered/overlapping° | mixed° | stacked° | multiple simultaneous patterns° | ✱ |
| **Anti-design (Archizoom, 1966)** | Pop + Kitsch appropriation; deliberately "wrong" combinations° | deliberately mismatched° | grid violated on purpose | inconsistent **on purpose**° | inconsistent° | kitsch pattern° | ✱ |

Two cautions the table cannot carry. **Kandinsky's yellow→triangle / red→square / blue→circle mapping
is not a perceptual law** — an IAT replication found no support for it and attributes it to "Kandinsky's
personal artistic choices or Bauhaus cultural construction" (PMC3769683). Cite it as his theory, never
as perception. And **"Brutalism" names two different things**: Copeland's manifesto is a *usability*
document, Deville's gallery is an *anti-aesthetic* one. A brief that says "brutalist" must say which.

Texture recipes with real parameter values — grain, halftone, duotone, paper, chromatic aberration —
live in `cookbook/texture.md`.

**The seven movements that carry hard numbers.**

- **Swiss / International Typographic.** Type is grotesque and setting is **flush-left,
  ragged-right — never justified**. The grid is Müller-Brockmann's: specimens at **8, 20 and 32
  fields**, the type area divided by columns *and* rows inside defined margins, **leading equal to a
  whole multiple of the baseline unit and every element snapped to it**. Imagery is *objective
  documentary* photography, explicitly not persuasive or commercial photography — a movement-level
  rule about which kind of photograph, which is the decision AI output never makes. The palette
  (achromatic + one flat spot colour) is DERIVED.
- **Brutalism (web).** Copeland's seven principles, verbatim: "Content is readable on all reasonable
  screens and devices." · "Only hyperlinks and buttons respond to clicks." · "Hyperlinks are
  underlined and buttons look like buttons." · "The back button works as expected." · "View content
  by scrolling." · "Decoration when needed and no unrelated content." · "Performance is a feature."
  A site's true materials are "its content and the context in which it's consumed," not HTML or CSS.
- **Neo-brutalism.** Converged community convention, not a founding spec — **no canonical token file
  is reachable**; values aggregate NN/g's explainer and generator pages. Border **2–4px solid** on
  interactive elements *and* containers · shadow **hard-edged, zero blur, solid colour, offset 4–8px
  in both x and y** (6–8px classic) · radius **0** strict, **4–8px** in the soft variant · spacing
  **4px base** → 4 / 8 / 12 / 16 / 24 / 32 · card padding **24–32px** · section vertical margin
  **48–64px**. This corroborates §5's Brutalist archetype and widens it — see the seed axis below.
- **Editorial / print.** Bringhurst: **45–75 characters per line** is satisfactory for a
  single-column serif page, **66 is the ideal target**, and for multi-column "a better average is 40
  to 50 characters." The rationale is perceptual: too short and "the eye snaps back and forth like a
  ping-pong ball," too long and it "loses its place returning to the start of the next line." No
  number is attached to Brodovitch — his whitespace-driven layout is documented design history, not
  a parameter set.
- **Cyberpunk / terminal / CRT.** The only located numbers are **retro-emulation shader docs —
  hobbyist tier, and UNVERIFIED for the CSS case**: scanlines darken every 2nd (or 3rd/4th) pixel
  row, "weak" ≈ **20–30% darkness**, "strong" ≈ **60–70%**; phosphor persistence is a **decay curve,
  not a cutoff**, some phosphors holding **20–30ms**; barrel distortion is a configurable outward
  warp from centre; one cited preset runs scanline opacity **0.25**, persistence **0.12**, small
  positive bloom. Transfer them by analogy and say so.
- **Liquid Glass.** The four Apple rules, verbatim-sourced:
  1. It is a **FUNCTIONAL layer** for controls and navigation that floats above content. "Don't use
     Liquid Glass in the content layer." Content-layer depth uses the four standard materials
     (ultraThin / thin / regular / thick) instead.
  2. "Use Liquid Glass effects sparingly." Limit it to the most important functional elements.
  3. The `clear` variant over BRIGHT content requires a dark dimming layer at **35% opacity**.
     `regular` is the default and the one to reach for whenever the component carries significant text.
  4. The signature is **LENSING, not blur**: "previous materials scattered light; this new set of
     materials dynamically bends, shapes, and concentrates light in real time." Transitions
     "materialize in and out by gradually modulating the light bending" — never a plain fade.

  **And the walk-back, which is part of the spec.** Apple shipped this in iOS 26 (Sept 2025) and
  spent four releases adding opacity back (26.1 Clear→Tinted toggle; 26.2 Lock Screen Glass/Solid;
  iOS 27 raised the default transparency floor and added a High Contrast Liquid Glass middle mode
  with ~50% less blur). *The iOS 27 percentages come from ONE secondary blog and are UNVERIFIED.*
  Therefore any glass preset in this skill MUST ship, in the same commit:
  - an opacity floor token (`--glass-min-opacity`, default 0.60);
  - a `prefers-reduced-transparency` branch that resolves the surface to an opaque fill — and since
    that query is not Baseline, **the opaque treatment is the base style and the glass is the
    progressive enhancement**, not the reverse;
  - a contrast check against the WORST-CASE background, not the demo background.

  ```css
  /* base: opaque. The glass is the enhancement. */
  .glass { background: var(--surface); }

  @supports (backdrop-filter: blur(1px)) {
    @media not (prefers-reduced-transparency: reduce) {
      .glass {
        backdrop-filter: blur(10px) saturate(140%);
        background: color-mix(in oklch, var(--surface) 60%, transparent);  /* --glass-min-opacity */
        box-shadow: inset 0 1px 0 oklch(1 0 0 / .12), 0 0 0 1px oklch(1 0 0 / .08);
      }
    }
  }
  /* approximates `regular`, not lensing — lensing has no CSS analogue. */
  ```
- **Neumorphism.** The whole movement reduces to one recipe — two box-shadows on a single flat
  background, light highlight top-left, dark shadow bottom-right, on rounded corners:
  ```css
  box-shadow: 9px 9px 18px #bec3c9, -9px -9px 18px #ffffff;
  /* the background must sit between the two shadow colours */
  ```
  Its coiner's own verdict travels with it: "low contrast is the main problem being raised with all
  of these design styles," and glassmorphism is more salvageable than neumorphism because it "merges
  well with both light and dark modes, and can be used with good accessibility and contrast in
  mind." Ship neumorphism only where the contrast gate still passes — which is rarely.

### The seed axis (across-run variance)

Hard constraints raise distance-from-the-mean but **lower** variance across runs — two different
metrics the literature measures separately (Kirk et al., arXiv:2310.06452, on RLHF reducing output
diversity). Once the per-run constraints are tight, the seed axis is the only remaining source of
across-run variance. This generalises anti-slop.md's "rotate to a different palette family each
project" from hue to the whole parameter space.

Before each new project, roll one value on each axis and record it in the brief:

```
  MOVEMENT        : one row of the movements table above
  ACCENT HUE      : {25 red, 65 amber, 95 yellow, 150 green, 190 teal, 259 blue, 300 violet, 350 pink}
                    minus the previous project's hue +/-30 degrees
  RADIUS BASE     : {0, 2, 4, 6, 8, 10, 12, 16, 24}px
  GRID_DISCIPLINE : {0, 1, 2, 3}
  TEXTURE_LEVEL   : {0, 1, 2, 3}
  TENSION CAUSE   : {asymmetry, colour clash, scale jump, grid violation}
```

**Hard rule: never ship the same (MOVEMENT, ACCENT HUE, RADIUS BASE) tuple twice in a row.**
Within a movement, its own documented ranges are seed values too — a neo-brutalist project rolls
border ∈ 2–4px and shadow offset ∈ 4–8px rather than defaulting both to the thin end.

---

## What stays constant across all seven (the invariant layer)

Only the primitives above change. Everything below is archetype-invariant, so the same
components skin any archetype by swapping one primitive file:

- **3-tier tokens** (primitive → semantic → component). Components consume only the semantic
  layer; a component that references a primitive (`blue-500`) directly is a bug.
- **Foreground/background pairs** for every color role (`x` + `x-foreground`), so contrast is
  auto-checkable and every surface has a legible text color.
- **Semantic hue conventions**: success ≈ green 150, warning ≈ amber 65 (dark on-text — the
  exception), error ≈ red 25, info ≈ blue 259. Each ships bold / bold-hovered / subtle /
  border / text / text-strong sub-slots + a paired `on-color`.
- **Derived scales from one base token**: `--radius` → xs/sm/md/lg/xl; one tracking base → 6
  steps; 6 shadow params → the full scale. Author ~10 knobs, emit ~60 tokens.
- **Chroma budget as ratios**, from Google's own `material-color-utilities` `CorePalette` source.
  HCT absolute values do not transfer to OKLCH; the RATIOS do, and they are unit-free:

  ```
  secondary       = primary_chroma / 3
  tertiary        = primary_chroma / 2      at hue = brand_hue + 60 degrees
  neutral         = primary_chroma / 12, hard-capped
  neutral-variant = primary_chroma / 6,  hard-capped at 2x neutral
  error           = FIXED hue 25, chroma pinned high, NEVER brand-derived

  Worked in OKLCH for a brand at C=0.21:
    --primary:          oklch(L 0.210 H)
    --secondary:        oklch(L 0.070 H)
    --tertiary:         oklch(L 0.105 H+60)
    --neutral:          oklch(L 0.0175 H)     /* clamp to <=0.012 in practice */
    --neutral-variant:  oklch(L 0.035  H)     /* clamp to <=0.020 in practice */
    --destructive:      oklch(L 0.190 25)     /* hue 25, independent of brand */
  ```

  **The chroma ceiling.** Exactly ONE step in the ramp carries full brand chroma. Radix names it
  step 9 — "the purest step, the step mixed with the least amount of white or black" — and reserves
  it for solid backgrounds only. Nothing else in the system may exceed step 9's chroma.
- **Neutral pairing (Radix's rule, named).** Two sanctioned strategies: **Neutral pairing** — pure
  gray (C ≈ 0.002), works with any accent, "simple" vibe; **Natural pairing** — tint the neutral
  toward the hue *closest to the accent hue*, "more colorful and harmonious." Reference tints:
  purple-based (mauve), blue (slate), green (sage), lime (olive), yellow (sand). **Cap it.**
  Linear's own fix for a UI that had drifted off-neutral was "limiting how much chrome (blue in our
  case) was used in the calculations applied to our color system." Hard ceiling **C ≤ 0.012** on any
  neutral; M3's own neutral chroma is 6 HCT (≈ 0.01 OKLCH) and its neutral-*variant* is 8.
- **Dark mode is a second art direction, not an inversion.** Keep semantic names stable and re-point
  the aliases — but AUTHOR a second ramp; do not flip the first. Apple states it outright: dark
  colours "aren't necessarily inversions of their light counterparts: while many colors are
  inverted, some are not." Four systems independently author rather than flip (Apple base/elevated;
  Material `#121212` + tone 200 + overlay ladder; Carbon four themes with non-mirrored layer ranges;
  Atlassian separate light/dark neutral ramps + alpha tokens). The five hard numbers:
  1. **Surface base = a tinted near-black, never `#000`.** Material names `#121212`. A branded dark
     surface = brand at 8% over `#121212` (their worked example lands on `#1F1B24`).
  2. **Dark-surface contrast floor = 15.8:1** between white body text and the DARKEST surface. This
     is what guarantees 4.5:1 still holds at the HIGHEST (lightest) elevation. Gate on this, not
     just on 4.5:1 at the base surface.
  3. **Elevation is a white overlay ladder, not a shadow** — 0dp 0%, 1dp 5%, 2dp 7%, 3dp 8%, 4dp 9%,
     6dp 11%, 8dp 12%, 12dp 14%, 16dp 15%, 24dp 16%. Overlays are NOT applied to surfaces that use
     the primary or secondary colour.
  4. **Accent = the 200-tone equivalent**, desaturated. Saturated accents on dark "produce optical
     vibrations… which can induce eye strain" and fail 4.5:1.
  5. **Icons get a negative optical grade on dark, not a thinner stroke.** Material Symbols' GRAD
     axis exists for exactly this: "To reduce glare for a light symbol on a dark background, use a
     low grade" (e.g. GRAD −25). Match the text font's grade.

  Explicit don't (Material): "Don't use light glows in place of dark shadows to express elevation."
  Target 7:1 rather than 4.5:1 for custom small text (Apple). Test the compound case: dark +
  Increase Contrast + Reduce Transparency, separately and together — Apple documents that Increase
  Contrast in Dark Mode can REDUCE visual contrast.
- **Accent Consistency Lock** (mandatory): one accent, chosen once, used on the WHOLE surface —
  a warm-grey product does not get a blue CTA in section 7, a rose brand does not get a teal
  badge in the footer. Saturation < 80% by default; do not fluctuate between warm and cool
  greys within one project. Override only if the brand explicitly demands a second hue.
- **Shape Lock** (mandatory): one corner-radius scale for the whole surface, derived from the
  single `--radius` base (all-sharp / all-soft / all-pill). Mixed radii are allowed **only**
  with a documented rule ("buttons full-pill, cards 12px, inputs 8px") followed everywhere.
  Round buttons on a square layout, or square cards on a pill-button page, is broken design.
- **Gates**: WCAG AA on every pair in both modes, APCA advisory only; ≤2 type families (3 only if one is
  mono); ≤3 motion curves; `prefers-reduced-motion` reduces (cross-fades) rather than
  deletes; coherence check (a "playful +0.8" vector must not emit radius 0).
- **Anti-convergence guardrails**: no reflexive `indigo/violet/purple-500` accent; no
  purple→cyan mesh as primary decoration; no uniform `rgba(0,0,0,0.1)` shadow on everything;
  no gradient text on metrics; flag the escape-hatch clichés (Space Grotesk + teal on
  near-black, Geist-by-default, single Instrument-Serif-italic accent word) as their own slop.
