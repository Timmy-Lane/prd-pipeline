# Anti-Slop Gate

The final quality gate. Run this **before declaring any screen done**. It catches the defects that make AI-generated UI read as cheap, generic, and machine-authored — the "AI slop" aesthetic.

> **Canonical anti-slop defect catalog — single source of truth (SSOT).** This file is *the* one authoritative defect list for the skill. The automatable greps (§ Automatable detectors), the Phase-4 product-taste judge-lens, and the eval judge all import their defects from here — add, rename, or retune a slop tell **here and nowhere else**, and the three consumers inherit it. Last updated **2026-07-27**.

> **Where a ban may appear.** Naming a forbidden token in the prompt that *generates* the design RAISES its probability. Rana 2026 (arXiv:2601.08070, n=40,000) finds violation probability rises logistically with the model's intrinsic pressure toward the forbidden token (`p = σ(−2.40 + 2.27·P₀)`), and that **87.5% of violations are PRIMING failures — the instruction's explicit mention of the forbidden word activates rather than suppresses it**. Jang et al. (arXiv:2209.12711) find negated prompts show INVERSE scaling: bigger models obey them worse. *(One study, one team, unreplicated — the mechanism is the best available explanation, not a settled law.)* Therefore:
>
> - Every list in this file is a **post-generation grep gate**. It runs on the emitted code, never in the brief that produces it.
> - Any ban that must appear in a generation prompt is written as a **pair** — `BANNED: Inter → USE: <the archetype's named face>`, never "not Inter". A ban with no positive replacement leaves probability mass with nowhere to go.
> - Never enumerate banned hex codes inside a generation prompt. State the positive chroma budget instead (→ `brand-to-system.md § What stays constant across all seven`).
>
> This is the mechanism behind the second-order trap named below: the file already observed that "not Inter, not purple" produces a *new* cliché; priming is why.

## Contents

- [0 · Three instrument classes](#0--three-instrument-classes-read-before-enforcing-anything) — D / S / P, and what each class is allowed to block
- [What this gate does not do](#what-this-gate-does-not-do)
- [Why slop happens (the one paragraph)](#why-slop-happens-the-one-paragraph)
- [How to run the gate](#how-to-run-the-gate) — the Starter Pack trip-wire, the density score, the enforcement steps
- [Automatable detectors](#automatable-detectors-grep-first-cheap-and-precise) — the greps, what needs a computed detector, the off-the-shelf lint layer
- [Catalog — named defects](#catalog--named-defects-detect--why-its-cheap--fix) — SUBSTRATE-DEFAULTS · COLOR · TYPOGRAPHY · LAYOUT & STRUCTURE · DEPTH/SHADOW · MOTION · CONTENT & COPY · STATES, TOKENS & A11Y · APP-UI · TOKEN-DRIFT
- [Handoff gates (metric · window · trigger)](#handoff-gates-metric--window--trigger)
- [Process fixes](#process-fixes-the-real-leverage--slop-is-a-workflow-bug-not-a-better-adjective-bug) — the workflow counters, which is where the leverage is
- [Good-defaults reference](#good-defaults-reference-encode-these-as-the-antidote)

## 0 · Three instrument classes (read before enforcing anything)

A tell makes one of three claims. They are not interchangeable, and enforcement follows the **class**, not the loudness of the tell.

| Class | The claim | Evidence needed | Can it hard-fail a ship? |
|---|---|---|---|
| **D — deterministic substrate match** | "this literal is byte-identical to a published default" | the published default (a URL) | **Yes.** It asserts *nothing was decided here*, not *a machine wrote this*. A human who ran `shadcn init` and shipped trips it identically — and that is the correct verdict. |
| **S — self-relative drift** | "this literal is outside the project's own declared token ramp" | the project's own `DESIGN.md` / theme file | **Yes.** It cannot be wrong about the world; it compares the artifact to its own stated system. |
| **P — probabilistic style inference** | "this pattern co-occurs with generated output" | a corpus frequency, which mostly does not exist | **No.** It inherits the entire false-positive problem of AI-content detection (§ What this gate does not do). Density-score only. |

Every named defect below carries a `*Class:*` field. Enforcement by class is § How to run the gate, step 3; how to *word* a finding from each class is `critique.md § 1.9`.

Some catalog entries are not tells at all — a WCAG contrast failure, an animated layout property, a missing form validation. They carry `*Class:* n/a (measured defect)` and block on **their own measurement**, never on density. Do not read that as a fourth inference class: nothing is being inferred, something is being measured.

## What this gate does not do

It does not detect AI authorship, and must never claim to. Purpose-trained code detectors reach macro F1 0.845 out-of-distribution but collapse to macro F1 0.345 when asked *which* generator (arxiv.org/pdf/2604.26990v1) — so any rule naming "the v0 look" from markup alone is claiming more than the state of the art. Off-the-shelf detectors on code sit at ~0.5 accuracy. This gate detects **undesigned**, which is decidable, not **machine-authored**, which largely is not.

**Do not add these as tells** (Wikipedia's documented ineffective indicators): perfect grammar · mixed casual/formal register · "bland" or "robotic" prose · "fancy"/"academic" prose · transition words in isolation · unsourced content · unusual markup. Each has a large human population behind it.

## Why slop happens (the one paragraph)

An LLM predicts the highest-probability next token. Given an open design brief, that is the *most common* answer in the training corpus — "the median of every Tailwind tutorial scraped from GitHub between 2019 and 2024." So the model collapses to the statistical center: Inter, indigo, centered hero, three feature cards. Anthropic's own cookbook names it: *"You tend to converge toward generic, 'on distribution' outputs… this creates what users call the 'AI slop' aesthetic."* Convergence is a **default, not a destiny** — this gate exists to override it. Note the second-order trap: telling the model "not Inter, not purple" makes it converge on a *new* cliché (Space Grotesk + teal; now Geist + Instrument-Serif italic). Escaping the center requires committed, specific choices, not the next-safest default.

## How to run the gate

1. **Grep the high-precision tells** (§ Automatable detectors) — these are near-zero-false-positive and cost nothing. The **binary hard fails** (one hit ships nothing) are the class-D and class-S rows: a byte-identical substrate default (§ SUBSTRATE-DEFAULTS) and any color/radius/font literal outside the declared token ramp.
2. **Walk the named-defect catalog** (§ Catalog) against the rendered screen, one category at a time.
3. **Enforcement by class.**
   - **Class D** (byte-identical to a published substrate default) and **class S** (outside the project's own declared ramp) — **1 hit blocks ship.** These assert "nothing was decided here", not "a machine wrote this", and cannot be wrong about the world.
   - **Class P** (statistical style inference) — **density only.** 4+ Starter-Pack tells on one screen flags. No single class-P tell may block a ship on its own.
   Why: off-the-shelf detectors on code run at ~0.5 accuracy (arxiv.org/html/2401.03676v1); seven text detectors false-positive on 61.22% of non-native-English human writing (arxiv.org/pdf/2304.02819v3); humans are at chance (en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing). Class-P tells inherit all of that.
4. **Run the handoff gates** (§ Handoff gates) — token coverage, token drift, shadow recipes, contrast, countable colour/size/spacing, copy density, state coverage. A failing gate keeps the screen in **draft** status; it is not shippable.
5. **Score it** (optional): borrow shitfa.st's ShitScore banding — 40–60 = noticeably generic, 65–80 = heavy AI residue, 85+ = full slop. Ship under 40.

### The Starter Pack (the density trip-wire)

Multiple independent sources converge on nearly this exact list. 4+ on one screen = flag:

- Inter / Roboto font (no personality), or the escape-hatch Geist / Space Grotesk / Fraunces + Instrument Serif italic
- Purple / indigo accent or purple→blue/cyan gradient (hex `#7c3aed #8b5cf6 #a855f7 #6366f1 #764ba2 #667eea`)
- Warm cream / beige `--background` (the second-order escape from white)
- Centered hero with a tiny tracked eyebrow pill above the H1
- Exactly three icon-tile-topped feature cards under the hero
- White or light-gray background, rounded corners on everything
- Subtle shadow at exactly `0.1` opacity, applied uniformly
- "Get Started" / "Build the future of work" copy; **spaced** em dashes (` — `, the actual fingerprint)
- No empty / loading / error / focus states

---

## Automatable detectors (grep first, cheap and precise)

| Signal | Detector | Verdict |
|---|---|---|
| AI purple/cyan palette | grep the hex tell-list `#7c3aed\|#8b5cf6\|#a855f7\|#9333ea\|#7e22ce\|#6d28d9\|#6366f1\|#764ba2\|#667eea`, plus Tailwind `from-\(purple\|violet\|indigo\)` co-occurring with `to-\(purple\|violet\|indigo\|blue\|cyan\|pink\|fuchsia\)`, plus `text-\(violet\|purple\)-[567]00` on headings | direct — 1 hit = investigate. Rendered check: purple/violet **hue 260-310, chroma ≥50** heading text, or neon cyan (hue 160-200) / purple **chroma ≥80** text on dark (lum <0.1) |
| Uniform flat shadow | grep `rgba(0,0,0,0.1)` **count per file** | co-occurrence — flag when it's the *only* shadow recipe (see D-Shadow) |
| Emoji headings | regex leading emoji in `<h1-6>` / list items | direct — strong "an LLM wrote this" tell |
| Side-tab accent border | grep `border-\(l\|r\|t\|b\)-[234]\b` co-occurring with a non-neutral color on cards; **fires** when one side ≥2px AND (other 3 sides ≤1px OR this side ≥2× others); left/right also fire with any `border-radius>0` or width ≥3px | direct — **the #1 "AI generated this" tell** ("almost as reliable a sign of AI design as em-dashes") |
| Default font | grep `Inter\|Roboto\|Open Sans\|Lato\|Arial\|-apple-system` in font stack | direct |
| Overused / escape-hatch font | grep `Inter\|Roboto\|Fraunces\|Geist\|Plus Jakarta\|Space Grotesk\|Instrument Serif` as the primary face | investigate — fires when one of these is primary on **≥15% of text** (min 20 elements); these are 2026 convergence points, not fixes |
| Gradient text | grep `background-clip:\s*text\|bg-clip-text` (esp. with `bg-gradient-to-*` / `text-transparent`) on headings + stat numbers | direct |
| Cream/beige default surface | grep body/html `bg-\(amber\|orange\|yellow\)-50\|bg-stone-50\|bg-stone-100\|bg-stone-200`, plus banned premium hex `#f5f1ea\|#f7f5f1\|#efeae0`, plus arbitrary `bg-\[#...\]` passing the cream test (`min(r,g,b)≥209`, `r≥g≥b`, warmth `r-b` 6-48) | direct — any warm off-white as `--background` |
| Centered density | count centered blocks; **>60% of blocks `text-center`/`mx-auto`** | co-occurrence |
| Spaced em dash | `/\S \x{2014} \S/` run through `perl -CSD` (BSD grep has no `\x{}` ranges) — an em dash **surrounded by spaces**. A closed em dash (`word—word`) is normal typography and does not fire | co-occurrence — density cap ≤1 em dash per 400 words (see CONTENT › `spaced-em-dash`) |
| Slop copy | regex `Get Started`, `Build the future`, `all-in-one`, `Unlock the power`, `For Modern Teams`, `In Today's Fast-Paced World`, `Stop \w+\. Start \w+`, plus the live-band vocabulary `emphasizing\|enhance\|highlighting\|showcasing` and the decayed band `streamline\|empower\|supercharge\|world-class\|enterprise-grade\|next-generation\|cutting-edge\|Elevate\|Seamless\|Unleash\|Revolutionize` | co-occurrence — >2 hits per 300 words of marketing copy is a rewrite, not an edit |
| Copula avoidance | `grep -nE '\b(serves as\|stands as\|functions as\|represents a\|boasts\|refers to)\b'` — a periphrasis standing in for a plain "is" | co-occurrence — counts toward the copy density cap |
| Substrate default shipped unedited | grep the shadcn default token literals, the Tailwind default shadow recipe, and the shadcn `Button` cva base string (§ SUBSTRATE-DEFAULTS) | **direct — class D, 1 verbatim hit = finding** |
| Gradient temperature | `linear-gradient\([^)]*\b(pink\|magenta\|fuchsia)\b[^)]*\b(green\|emerald\|lime\|teal\|cyan)\b` and `from-(orange\|amber\|red)-\d+\s+to-(blue\|cyan\|sky\|indigo)-\d+` | direct — opposing-temperature stops (see COLOR › `gradient-temp`) |
| Blob filler | `absolute[^"]*\brounded-full\b[^"]*\bblur-(2xl\|3xl)\b` · `\bbg-gradient-to-\w+[^"]*\bblur-` · `-z-10[^"]*\bblur-3xl\b` · emoji-as-icon `>\s*[\x{1F300}-\x{1FAFF}]\s*<` (perl) | direct — the strongest AI-hero tell (see LAYOUT › `blob-filler`) |
| `text-wrap: balance` on a container | grep `text-wrap:\s*balance` where the selector is `body`, `*`, `:root`, or any container/layout class | direct — balance is a headline tool; on a container it is a blanket applied without measuring |
| VT `plus-lighter` dropped | `grep -nE '::view-transition-(old\|new)\([^)]*\)[^{]*\{[^}]*animation-name:'` — flag any hit whose value list does not end in `-ua-mix-blend-mode-plus-lighter` | direct — overriding `animation-name` silently drops the UA's cross-fade blend |
| `@starting-style` ordering | for any `@starting-style` block, assert its target selector already appeared earlier in the file | direct — a `@starting-style` that precedes its target never applies |
| Missing tabular figures *(app-UI)* | grep numeric surfaces — tables, KPI/stat cards, timers, numeric inputs — for the **absence** of `tabular-nums` / `tnum` / `slashed-zero` / `font-variant-numeric` | co-occurrence — flag numeric UI that never declares tabular figures |
| Off-scale spacing *(app-UI)* | grep arbitrary utilities `p-\[`, `gap-\[`, `m-\[`, `space-[xy]-\[`, or inline `px` values **not a multiple of 4** (`13px`, `18px`, `22px`) | direct — any non-4px-multiple spacing token |
| Brand hue as active fill *(app-UI)* | grep `data-\[state=(selected\|active)\]:bg-`, `aria-current` rows, or `.active`/`.selected` list rows filled with `bg-(primary\|indigo\|violet\|purple\|brand)` | investigate — active/selected fill should be a **neutral** accent; brand hue belongs on the focus ring + CTA only |
| Colored strip / chip on nav rows *(app-UI)* | extend the `border-l-[0-9]` / `border-left:` card check to nav + list rows, plus colored `bg-*` on nav/list **icon wrappers** | direct/investigate — decorative color substituting for spacing + weight hierarchy |
| Missing grid keyboard model *(app-UI)* | on a `<table>` whose rows hold 2+ focusable controls, grep for the **absence** of `role="grid"`, roving `tabindex={-1}`, and arrow-key `onKeyDown` | investigate — grep assist only; correctness is judge-only (see APP-UI › `no-grid-keyboard-model`) |

Model each catalog defect as a rule with a **mode** (`direct` = 1 match flags; `co-occurrence` = count per file, flag above a threshold) so density slop only trips when tells cluster.

### A tell that survives grep needs a computed detector

The skill shipped Tailwind's stock `blue-700` and `purple-500` as `--chart-1` / `--chart-4` in dark mode for months and **no grep caught it**, because a stock colour expressed in OKLCH is invisible to a hex grep. `grep '#a855f7\|purple-500'` returned nothing on a file that rendered `purple-500`.

The counter is not a longer pattern list. It is a **computed check**: parse the value, convert it, and compare in a colour space. `scripts/validate-chart-palette.mjs` does exactly this for the chart palette — it reads `--chart-*` and `--card` out of the theme for both modes and runs six computable checks (lightness band, chroma floor, CVD separation, normal-vision separation, surface contrast), exiting non-zero on the count of failures. Any tell whose *value* can be transformed before it is compared — a colour in another space, a resolved computed style, a ratio between two measured boxes, a count over the built CSS — belongs in a `.mjs` gate, not in the grep table. Put it in the grep table only if a literal substring decides it.

### Queued for `scripts/anti-slop-gate.sh` (written here, not yet wired)

These expressions are canonical and ready to paste into the script's `flag "<name>" "$(scan '<pattern>')"` form. They are **not** in the script today — the script owner picks them up from here.

```bash
# copula avoidance
grep -rnE '\b(serves as|stands as|functions as|represents a|boasts|refers to)\b'
# gradient temperature — opposing-temperature stops
grep -rnE 'linear-gradient\([^)]*\b(pink|magenta|fuchsia)\b[^)]*\b(green|emerald|lime|teal|cyan)\b'
grep -rnE 'from-(orange|amber|red)-[0-9]+[[:space:]]+to-(blue|cyan|sky|indigo)-[0-9]+'
# blob filler
grep -rnE 'absolute[^"]*\brounded-full\b[^"]*\bblur-(2xl|3xl)\b'
grep -rnE '\bbg-gradient-to-\w+[^"]*\bblur-'
grep -rnE '\-z-10[^"]*\bblur-3xl\b'
# text-wrap: balance applied to a container rather than a heading
grep -rnE '^(body|\*|:root|\.container|\.prose)[^{]*\{[^}]*text-wrap:[[:space:]]*balance'
# View Transitions: an animation-name override that drops the UA plus-lighter blend
grep -rnE '::view-transition-(old|new)\([^)]*\)[^{]*\{[^}]*animation-name:'
# shadcn / Tailwind substrate defaults shipped unedited (class D — 1 hit blocks)
grep -rnE 'oklch\(1 0 0\)|oklch\(0\.145 0 0\)|oklch\(0\.205 0 0\)|oklch\(0\.922 0 0\)|oklch\(0\.708 0 0\)'
grep -rnF '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)'

# The two Unicode tells go through perl, not grep — BSD grep has no \x{} ranges, and the
# script already uses this exact form for the emoji-heading detector.
perl -CSD -ne 'print "$ARGV:$.: $_" if /\S \x{2014} \S/; close ARGV if eof;'          # spaced em dash
perl -CSD -ne 'print "$ARGV:$.: $_" if />\s*[\x{1F300}-\x{1FAFF}]\s*</; close ARGV if eof;'  # emoji as icon
```

Two of these need a computed detector rather than a grep and must be written as node checks, not `scan()` calls: the **`@starting-style` ordering** assertion (for each `@starting-style` block, its target selector must already have appeared earlier in the file — a position comparison, not a match) and the **countable-colour / size / spacing gates** below (a count of unique resolved values in the built CSS).

### The off-the-shelf lint layer

Four `eslint-plugin-better-tailwindcss` rules do work this gate currently does by grep, with autofix and CI integration: `no-restricted-classes` (regex palette ban), `no-deprecated-classes` (catches the v3→v4 leak automatically), `no-unknown-classes` (hallucinated utilities), `no-conflicting-classes` (`p-4 p-6`).

```json
{ "better-tailwindcss/no-restricted-classes": ["error", { "restrict": [
  { "pattern": "^([a-zA-Z0-9:/_-]*:)?(bg|text|border|ring|from|via|to)-(indigo|violet|purple|fuchsia)-[0-9]{2,3}(\\/[0-9]{1,3})?$",
    "message": "AI-default accent hue. Use the brand token (bg-primary / text-primary)." },
  { "pattern": "^([a-zA-Z0-9:/_-]*:)?(p|m|gap|space)-[xytrbl]?-?\\[[0-9]*[13579]px\\]$",
    "message": "Off-scale spacing. Use the 4px-multiple scale." }
]}]}
```

Adoption numbers for the plugin are **UNVERIFIED** (npmjs.com returned HTTP 403); judge it on the rules, not on downloads.

---

## Catalog — named defects (detect → why it's cheap → fix)

### The five loudest tells, as a diff

A wrong line next to the right line is a stronger constraint than a paragraph, and it costs fewer tokens. Read this before the prose.

| WRONG | RIGHT |
|---|---|
| `<Button className="bg-indigo-500">` | `<Button>` — the accent lives in `--primary`, not at the call site |
| `font-family: Inter, sans-serif;` | `font-family: var(--font-display), var(--font-sans);` with a face named in the brief |
| `<Card className="border-l-4 border-violet-500">` | `<Card>` + `space-y-2` inside / `space-y-8` between — hierarchy from spacing and weight |
| `<div className="absolute -z-10 size-96 rounded-full bg-gradient-to-br from-purple-500 to-cyan-400 blur-3xl" />` | delete it, or put a real product screenshot there |
| `<div className="p-[13px] text-[#8b5cf6]">` | `<div className="p-3 text-primary">` — 4px scale, semantic token |

### SUBSTRATE-DEFAULTS (class D — a literal match means "nothing was decided here")

**`shadcn-default-tokens`** — *deterministic; 1 verbatim hit = finding*
- *Detect:* any of these appear unedited — `--radius: 0.625rem` · `--background: oklch(1 0 0)` · `--foreground: oklch(0.145 0 0)` · `--primary: oklch(0.205 0 0)` · `--border: oklch(0.922 0 0)` · `--ring: oklch(0.708 0 0)`, and the full chart/destructive set.
- *Why cheap:* these are the literals `shadcn init` writes. Shipping them is not a choice, it is the absence of one.
- *Fix:* tint the neutrals, move the base radius, and re-derive the chart set (`scripts/validate-chart-palette.mjs` checks it).
- *Class:* D. Source: https://ui.shadcn.com/docs/theming (§ Default Theme CSS).

**`tailwind-default-shadow`** — *deterministic*
- *Detect:* the verbatim recipe `0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)` (or the sm/lg/xl equivalents) in a project that claims a custom elevation scale.
- *Why cheap:* `rgb(0 0 0 / 0.1)` is the alpha in *every* Tailwind v4 default shadow; an exact recipe match means the scale was never authored.
- *Fix:* keep the two-layer shape, change the colour (→ DEPTH › `flat-uniform-shadow`).
- *Class:* D. Source: https://raw.githubusercontent.com/tailwindlabs/tailwindcss/main/packages/tailwindcss/theme.css

**`shadcn-button-verbatim`** — *deterministic*
- *Detect:* the cva base string `inline-flex shrink-0 items-center justify-center gap-2 rounded-md text-sm font-medium whitespace-nowrap transition-all outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 …` unmodified.
- *Why cheap:* the button is the most-seen control in the product; an unedited base string means the design language never reached it.
- *Fix:* any deliberate edit, or record the decision to keep it.
- *Class:* D. Source: https://ui.shadcn.com/r/styles/new-york-v4/button.json

### COLOR

**`purple-everything`** (indigo/violet/cyan AI palette) — *machine-precise triggers*
- *Detect:* fires on any of — purple/violet **heading text** at hue **260-310, chroma ≥50** (on h1/h2/h3 or `font-size ≥20px`); purple/violet **OR** cyan (hue **160-200**) gradient background; **neon** cyan/purple text at **chroma ≥80** on a dark bg (luminance **<0.1**). Hex tell-list (grep these literally): `#7c3aed #8b5cf6 #a855f7 #9333ea #7e22ce #6d28d9 #6366f1 #764ba2 #667eea`. Tailwind: `from-{purple,violet,indigo}-N to-{purple,violet,indigo,blue,cyan,pink,fuchsia}-N`; `text-violet-600` / `text-purple-600` headings. Also watch **"VibeCode Purple"** — a lavender shade that leaks from image-generation models, distinct from Tailwind's `#6366f1`.
- *Why cheap:* Tailwind's default hero button was `bg-indigo-500`; its creator publicly apologized for "every AI generated UI on earth also being indigo." Purple/violet gradients and cyan-on-dark are THE recognizable AI palette tells — the single loudest "a model chose this, not a designer" signal.
- *Fix:* Commit to **one dominant color + one sharp accent** (saturation <80%), drawn from IDE themes or a real cultural/brand reference, stored as semantic tokens. Never `text-violet-600` headings or `from-purple-500 to-cyan-500`. Purple is allowed *only* as a deliberate brand decision, never as a default.
- *Class:* P — except a byte-identical Tailwind literal (`oklch(0.627 0.265 303.9)` *is* `purple-500`), which is class **D**. A stock colour written in OKLCH is invisible to a hex grep; that one needs a computed check.

**`gradient-overuse`** (gradient dependency syndrome)
- *Detect:* gradient is the primary decoration — hero background, CTA fill, and section accents are all gradients; `linear-gradient` with purple+blue/cyan stops (every stop chroma ≥40); purple-cyan mesh; floating 3D blobs.
- *Why cheap:* the purple→blue mesh gradient is the canonical vibe-coded backdrop; it substitutes atmosphere for a real color system.
- *Fix:* Replace decorative gradients with a semantic color system. For depth, layer *subtle* gradients or geometric patterns tuned to the aesthetic — keep the hues **analogous** (adjacent on the wheel) and interpolate `in oklch` so they don't mud out, not the default rainbow. Reference: Stripe uses deep navy + precise accents, not a mesh.
- *Class:* P.

**`gradient-temp`** (the general gradient law — opposing temperatures, multi-stop meshes)
- *Detect:* any gradient that is not (a) a subtle accent, (b) **analogous** hues only (`blue→teal`, `purple→pink`, `orange→red`), (c) **2–3 stops maximum**. Fires hard on **opposing temperatures** — `pink→green`, `orange→blue`, `red→cyan` — and on a gradient used as a primary element or a CTA fill. Grep: `linear-gradient\([^)]*\b(pink|magenta|fuchsia)\b[^)]*\b(green|emerald|lime|teal|cyan)\b` and `from-(orange|amber|red)-\d+\s+to-(blue|cyan|sky|indigo)-\d+`.
- *Why cheap:* the default is no gradient — solid colors. Opposing-temperature stops pass through a desaturated mud band in the middle, which is why they read cheap regardless of hue choice.
- *Fix:* Solid fill. If a gradient genuinely earns its place, keep it analogous, 2–3 stops, off the CTA, and interpolate `in oklch`.
- *Class:* P.

**`gradient-text-metrics`** (gradient-filled headings + stat numbers)
- *Detect:* `background-clip: text` + any gradient, OR the Tailwind pair `bg-clip-text` + `bg-gradient-to-*` (+ `text-transparent`) on headings or big stat numbers ("10x", "99.9%").
- *Why cheap:* a top surface-level "tell"; gradient numbers signal decoration over substance.
- *Fix:* Solid text color, strong weight, real units + a source. Ban on all headings/metrics.
- *Class:* P.

**`cream-beige-surface`** (warm off-white default `--background`) — *machine-precise trigger*
- *Detect:* page background is a warm off-white — `min(r,g,b) ≥209`, channel ordering `r ≥ g ≥ b` (warm), warmth `r-b` between **6 and 48** (tinted, not pure white, not a strong color). Tailwind on body/html: `bg-amber-50/100`, `bg-orange-50/100`, `bg-yellow-50`, `bg-stone-50/100/200`, or arbitrary `bg-[#f5f0e6]` passing the cream test. Banned "premium" hex specifically: `#f5f1ea #f7f5f1 #efeae0`.
- *Why cheap:* warm cream/beige has become the default "tasteful" AI surface, reached for by reflex — the second-order escape hatch from white.
- *Fix:* Don't default `--background` to beige. Choose a background from a deliberate palette. **Rotate to a different palette family each project** — never ship beige+brass+espresso twice in a row.
- *Class:* P.

**`glowing-dark-accents`** (neon glow shadows on dark surfaces) — *machine-precise trigger*
- *Detect:* a `box-shadow` with visible chroma (channel spread **≥30**) and blur **>4px** on a dark background (luminance **<0.1**) — e.g. `shadow-[0_0_24px_theme(colors.cyan.500)]` on a near-black card.
- *Why cheap:* neon colored glows on near-black cards are a 2020s codegen fingerprint; light that comes from nowhere reads as decoration, not a light model.
- *Fix:* Subtle, purposeful lighting only. In dark mode, elevation = a **lighter surface color**, not a colored glow. No `shadow-[0_0_24px_cyan]`.
- *Class:* P.

**`timid-palette`** (evenly-distributed pastels)
- *Detect:* 5 pastel colors each used ~equally; no clear dominant hue.
- *Why cheap:* "Dominant colors with sharp accents outperform timid, evenly-distributed palettes" (Anthropic cookbook). Even distribution reads as indecision.
- *Fix:* ~**60/30/10** distribution — dominant surface, secondary, one sharp accent. Reserve color for emphasis; a mostly-neutral UI with color only on the primary action reads clearer.
- *Class:* P.

### TYPOGRAPHY

**`default-font`** (Inter / Roboto / system)
- *Detect:* `font-family` is Inter, Roboto, Open Sans, Lato, Arial, or a bare system stack with no display face.
- *Why cheap:* these are the statistical center of every SaaS template; they carry zero brand.
- *Fix — the blocklist is a hard rule.* Never use Inter / Roboto / Open Sans / Lato / Arial / Helvetica / default system fonts. Generic serifs (Times New Roman / Georgia / Garamond / Palatino) are banned too. **Serif is ALWAYS banned in dashboards/software UIs** regardless of vibe — serif only in editorial/marketing. Reach-for list by vibe:
  - Startup / product: **Geist, Satoshi, Outfit, Cabinet Grotesk, Clash Display, Plus Jakarta Sans**
  - Code/technical (mono): **Geist Mono, JetBrains Mono, Fira Code, IBM Plex Mono, SF Mono**
  - Editorial (distinctive serifs only): **Fraunces, Instrument Serif, Newsreader, PP Editorial New, Gambarino, Playfair Display, Crimson Pro**
  - Load via `next/font` (never a `<link>` Google Fonts tag in prod). **State the choice before coding.**
- *Class:* D when the stack is Tailwind's `--default-font-family` unedited; P when a face was chosen and it is Inter/Roboto. A font outside the declared ramp is class S and a hard finding either way.

**`overused-font`** (converged-on faces, incl. the escape hatches) — *machine-precise trigger*
- *Detect:* fires when a face in the overused set — **Inter, Roboto, Fraunces, Geist, Plus Jakarta Sans, Space Grotesk** — is the *primary* font on **≥15% of text-bearing elements** (measured across ≥20 elements min). Two specific 2026 tells: **Geist** (Vercel's font, now a v0/shadcn convergence point) and a **single accent word set in Instrument Serif italic** inside an otherwise-sans page. **`Fraunces` + `Instrument Serif` are BANNED as defaults** — "creative brief = serif" is the single most-tested tell.
- *Why cheap:* it is slop's *own* escape hatch — telling the model "not Inter" makes it converge on the next-most-common "interesting" font. Reads as "tried to look designed."
- *Fix:* Vary deliberately across generations; pick a face genuinely tied to the product's context, not the next-most-common escape font. Brand-font-on-its-own-domain is exempt.
- *Class:* P.

**`single-font`** (one face for everything) — *machine-precise trigger*
- *Detect:* exactly ONE distinct primary font across a **≥20-element** page.
- *Why cheap:* one undifferentiated face gives no display/body contrast; it reads as a template default.
- *Fix:* Define at least two families (`--font-display` + `--font-sans`, plus a `--font-mono` for numerals) and actually apply the display face to headings.
- *Class:* P.

**`weak-hierarchy`** (flat type hierarchy) — *machine-precise trigger*
- *Detect:* fires when **≥3 distinct font sizes** exist and the **largest:smallest ratio is <2.0** (heading vs body differ only by weight 400 vs 600 and size ×1.5); the page reads flat in grayscale.
- *Why cheap:* timid contrast is the signature of size-only hierarchy; nothing signals importance.
- *Fix:* Make the heading-to-body span **≥2×** (`text-4xl` over `text-base`, not `text-lg` over `text-base`). Use **weight extremes: 100/200 vs 800/900, not 400 vs 600.** Pairing principle: high contrast = interesting (display + mono, serif + geometric sans). Establish hierarchy with **weight + color (3 gray levels) first, size last** — de-emphasize competitors rather than shouting the primary.
- *Class:* P.

**`register-mismatch`** (italic serif display hero) — *machine-precise trigger*
- *Detect:* fires on `font-style: italic` + a serif face (Fraunces/Playfair/Recoleta/Newsreader, or stack ending in `serif`) on an **h1 (or h2 ≥48px) at `font-size ≥48px`** — an editorial italic-serif headline slapped onto a technical/dev-tool product where it doesn't fit.
- *Why cheap:* oversized italic serif hero reads as taste in isolation but is now the universal AI-startup landing hero; the typographic voice contradicts a product's voice.
- *Fix:* Roman, or a non-serif display face. Match typographic register to product register. (Editorial/magazine surfaces may legitimately want italic serif — everywhere else, no `italic font-serif text-6xl` on the hero.)
- *Class:* P.

### LAYOUT & STRUCTURE

**`centered-everything`**
- *Detect:* hero is centered text + centered CTA; **>60% of blocks** are `text-center` + `mx-auto`.
- *Why cheap:* the centered single-column is the path of least resistance; it has no editorial point of view.
- *Fix:* Introduce an **asymmetric grid** as a deliberate choice. Left-align anything over 2–3 lines; center only short headings. Use negative space intentionally. Not everything is a centered column.
- *Class:* P.

**`three-card-religion`**
- *Detect:* exactly three feature cards, each icon-on-top + heading + one sentence, directly under the hero.
- *Why cheap:* the reflexive 3-up is the most-templated section on the web.
- *Fix:* Let content dictate count and shape — varied card sizes, a bento layout, or prose. Also flag the 2026 variants: badge directly above the H1, numbered "1, 2, 3" step sequences, generic stat banners.
- *Class:* P.

**`icon-tile-above-heading`** (the rounded-square chip stacked over a title) — *machine-precise trigger*
- *Detect:* a heading's **previous sibling** is a squarish tile — **32-128px** on both axes, aspect ratio **0.7-1.4**, has a visible bg/border, `border-radius < width/2` (rounded square, not a circle/avatar), contains an svg/icon smaller than the tile, and sits directly above the heading. The universal `size-12 rounded-xl bg-primary/10` feature-card chip.
- *Why cheap:* the rounded-square-icon-above-heading is the feature-card template every generator emits.
- *Fix:* Go horizontal (icon + heading side-by-side), or let the icon sit inline without its own container, or drop the chip.
- *Class:* P.

**`hero-eyebrow-pill`** (tiny kicker above the H1) — *machine-precise trigger*
- *Detect:* an h1's **previous sibling** is a tiny label (2-60 chars, `font-size ≤14px`) that is EITHER classic tracked-uppercase (`letter-spacing ≥1.6px`) OR modern accent-bold (`font-weight ≥700` + an accent color). Also the soft-skill `rounded-full px-3 py-1 text-[10px] uppercase tracking-[0.2em]` micro-pill.
- *Why cheap:* the tiny tracked label (or pill) above an oversized hero headline is now the default AI SaaS hero.
- *Fix:* Drop the eyebrow; fold the kicker into the headline (section location already categorizes it).
- *Class:* P.

**`feature-grid-overload`**
- *Detect:* the opposite failure — 11+ uniform cards crammed in.
- *Why cheap:* dumping everything at equal weight signals no prioritization.
- *Fix:* "One primary action per screen." Cut and rank. A dashboard = ~4 stat cards + one main chart + a short activity list, not a wall of tiles.
- *Class:* P.

**`uniform-sizing`** (no hierarchy of components)
- *Detect:* every element shares `border-radius: 16px` and `padding: 24px`; nothing signals importance.
- *Why cheap:* uniformity is what a template does; hierarchy is what a designer does.
- *Fix:* Varied spacing and radius scales mapped to role. Primary surfaces get more room than secondary.
- *Class:* P.

**`card-in-card`** (nested containers) — *machine-precise trigger*
- *Detect:* a "card-like" element inside another card-like element (only the innermost fires). "Card-like" = (shadow OR border) AND (radius OR bg), with **>10 chars** of text and rect **≥50×30px**; popovers/tooltips/menus/modals/dialogs and absolute/fixed elements are excluded. Don't wrap a shadcn `<Card>` in `<Card>`.
- *Why cheap:* recursive boxing is visual noise that betrays no layout thinking.
- *Fix:* Flatten with spacing, dividers, and typography. Use spacing + one level of elevation, not nested borders. Prefer more spacing / a background-color difference / a shadow over 1px borders everywhere.
- *Class:* P.

**`layout-family-repetition`** (same section shape reused) — *machine-precise trigger*
- *Detect:* each layout family (3-col cards, quote, split, bento, stat banner) should appear **at most once**; an 8-section page uses **≥4 distinct families**; **max 2 consecutive** zigzag/split sections; **no 3 equal feature cards**.
- *Why cheap:* one repeated section shape down the page is the fingerprint of a template, not composition.
- *Fix:* Vary the section archetype deliberately; enforce the family-count floor and the consecutive-zigzag cap as a pre-flight check.
- *Class:* P.

**`monotonous-spacing`** (one gap value everywhere) — *machine-precise trigger*
- *Detect:* across **≥10** collected spacing values (padding/margin/gap), a single value is **>60%** of them AND there are **≤3 unique values** — `gap-4`/`p-4` uniformly.
- *Why cheap:* one spacing value everywhere = no rhythm; deliberate designs vary the scale.
- *Fix:* Use a real scale — tight groupings inside a group (`space-y-2`), generous separation between sections (`space-y-12`). More space *around* a group than *within* it. *(→ STATES › `inconsistent-spacing` for the proximity rule.)*
- *Class:* P.

**`repeated-kickers`** (eyebrow/numbered markers on every section) — *machine-precise cap*
- *Detect:* **≥3** section headings each preceded by a tiny uppercase tracked eyebrow. Hard cap: **eyebrow count ≤ `ceil(sectionCount/3)`** (hero counts as 1). Numbered "SECTION 01" / "01 / 02" display markers are **banned forever**.
- *Why cheap:* scaffolding every section with an `<p class="uppercase tracking-wide">EYEBROW</p>` is the AI editorial scaffold; numbered markers are one tier deeper.
- *Fix:* Replace with stronger structure, imagery, or a real brand system; keep total eyebrows under the cap.
- *Class:* P.

**`bento-empty-cell`** (padded grid with dead cells) — *machine-precise rule*
- *Detect:* a bento grid where **cell count ≠ item count** (3 items padded to 6 with blanks), or a grid with a dead/empty corner cell.
- *Why cheap:* the sparse, unbalanced bento with a blank corner is the immediate "auto-generated grid" tell.
- *Fix:* **Cell count MUST equal item count** (3 items → 3 cells); apply `grid-flow-dense`; give ≥2-3 cells real visual variation (image/tint), never all-white-on-white.
- *Class:* P.

**`rounded-everything`**
- *Detect:* one generous radius on every box, button, image, and input.
- *Why cheap:* "bubbly" uniform radius is a shadcn-default fingerprint.
- *Fix:* A radius **scale (e.g. 0 / 4 / 8 / 16)** chosen per element role; some things should be square.
- *Class:* D when every radius resolves from an unedited `--radius: 0.625rem`; P when a radius was chosen and then applied uniformly.

**`blob-filler`** (abstract filler geometry) — *machine-precise trigger*
- *Detect:* gradient circles, blurred squares, floating orbs, decorative blobs — geometry placed to fill space rather than to carry information. Also: hand-authored SVG standing in for a complex illustration or a map (use a real mapping library), and emoji standing in for an icon. Grep: `absolute[^"]*\brounded-full\b[^"]*\bblur-(2xl|3xl)\b` · `\bbg-gradient-to-\w+[^"]*\bblur-` · `-z-10[^"]*\bblur-3xl\b` · `>\s*[\x{1F300}-\x{1FAFF}]\s*<` (perl).
- *Why cheap:* it is the single most recognisable AI-hero tell. A blurred orb behind a headline is what gets generated when there is nothing real to show.
- *Fix:* Delete it, or put a real product screenshot in that space. Depth comes from a light model and a layout, not from a blurred circle at `-z-10`.
- *Class:* P.

### DEPTH / SHADOW

**`flat-uniform-shadow`** (the 0.1-opacity shadow) — *corrected*
- *Detect:* one `box-shadow … rgba(0,0,0,0.1)` recipe applied to *everything*. **Nuance:** the literal `rgba(0,0,0,0.1)` value is **not** the defect — Refactoring UI's own `md`/`lg` shadows legitimately use `0.1`. The tell is **a single flat shadow used uniformly**, not the number. Grep-`0.1` is a *starting hint*; the real check is "how many distinct recipes, applied by role?"
- *Why cheap:* one flat shadow on every surface means depth is decoration, not a light model.
- *Fix:* Define **3–5 named elevation tokens** by role. Every level **above resting = two layers** (a tight near shadow + a wider, softer far one), both offset downward (light from above) — never one flat blur. Canonical layered scale, in **Tailwind v4 names** (v4 renamed v3's `shadow-sm` to `shadow-xs` and moved `shadow-sm` up a rung; shipping a v3 value under a v4 name is itself the version-leak tell):
  - `--shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.05)` — hairline resting (single layer is fine here)
  - `--shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)` — resting cards/buttons
  - `--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)` — dropdowns
  - `--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)` — popovers
  - `--shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)` — modals
  - In dark mode, elevation = **lighter surface color**, not shadow.

  These five literals are Tailwind v4's own emitted defaults, which is why `tailwind-default-shadow` (§ SUBSTRATE-DEFAULTS) fires on a verbatim match. **Match the two-layer shape, change the colour** — a shadow tinted toward the surface hue is the craft signal; the shape alone is Tailwind's.
- *Class:* D on a verbatim Tailwind recipe (§ SUBSTRATE-DEFAULTS); P on "one recipe, used everywhere".

**`shadow-recipe-drift`**
- *Detect:* every component has its own ad-hoc shadow; more than 3 distinct recipes on core surfaces (cards, menus, modals, buttons) in one flow.
- *Why cheap:* depth cues behave like random decoration.
- *Fix:* Collapse to **≤3 recipes on core surfaces**; normalize all shadows to the named tokens.
- *Class:* S — counted against the project's own declared elevation set.

**`reflexive-glassmorphism`**
- *Detect:* frosted `backdrop-blur` panels used because it's trendy, not because real layering demands it.
- *Why cheap:* blur-for-blur's-sake is a 2020s codegen fingerprint.
- *Fix:* Use blur only where genuine depth stacking exists; otherwise solid + border.
- *Class:* P.

### MOTION

> **Canonical motion-tell section (SSOT).** `references/motion.md` references these anchors — retune easing/curve triggers here, not there.

**`bounce-default`** (elastic / overshoot easing) — *machine-precise trigger*
- *Detect:* animation name matches `bounce|elastic|wobble|jiggle|spring`, or Tailwind `animate-bounce`, or any `cubic-bezier()` with a **Y control point outside `[-0.1, 1.1]`** (overshoot). Everything feels toylike.
- *Why cheap:* one elastic easing everywhere means motion wasn't characterized to the brand; overshoot reads dated and tacky.
- *Fix:* Physical deceleration — ease-out-quart/quint/expo, e.g. `ease-[cubic-bezier(0.22,1,0.36,1)]` (ease-out-quint) or `cubic-bezier(0.16,1,0.3,1)`. Easing matches brand character (Stripe = precise `ease-out`; Duolingo = playful bounce — pick on purpose, don't default).
- *Class:* P.

**`layout-property-animation`** (animating width/height/padding) — *machine-precise trigger*
- *Detect:* a transition/animation targets any of **width, height, padding, margin, min/max-width/height** (all longhands) — causes layout thrash / jank.
- *Why cheap:* animating layout properties drops the animation off the compositor thread and tanks mobile FPS; it's the motion equivalent of not knowing the primitives.
- *Fix:* Animate **`transform` and `opacity` only**; for height (accordions) animate `grid-template-rows: 0fr → 1fr`. Never `transition-[width]` / `transition-[height]`.
- *Class:* n/a (measured defect).

**`keyframes-on-dynamic`** (perpetual/scroll motion done wrong)
- *Detect:* infinite/perpetual keyframe loops or scroll reveals driven by `window.addEventListener('scroll')` or by `useState` on pointer/scroll move (a re-render per frame); CPU-heavy loops not isolated.
- *Why cheap:* continuous reflows and per-frame React re-renders collapse mobile FPS; it's effort spent making the page *feel* worse.
- *Fix:* `IntersectionObserver`/`useScroll` (never a scroll listener — **hard ban**); continuous input via `useMotionValue`/`useTransform` outside the render cycle; isolate + `React.memo` every perpetual loop in its own leaf Client Component; every `useEffect` animation has cleanup.
- *Class:* n/a (measured defect).

**`dead-hover`** (snap transitions)
- *Detect:* hover states do nothing; buttons snap instead of easing.
- *Why cheap:* the absence of micro-interaction reads as unfinished.
- *Fix:* Add micro-interactions to primary CTAs + form inputs first. Each should (1) communicate a state change, (2) direct attention, or (3) reinforce brand.
- *Class:* P.

**`scattered-fades`** (identical fade-ins + count-up numbers)
- *Detect:* every element has the same generic scroll fade-in; stats dramatically count up; parallax stacking — animation is the hardest engineering on the page while the product is thin.
- *Why cheap:* motion effort concentrated on decoration instead of the product signals an empty product.
- *Fix:* "One well-orchestrated page-load reveal with staggered `animation-delay` beats scattered micro-interactions" (Anthropic cookbook). Gate all animation behind `prefers-reduced-motion`.
- *Class:* P.

### CONTENT & COPY

**`spaced-em-dash`** (the actual fingerprint) — *direct pattern, density verdict*
- *Detect:* `/\S \x{2014} \S/` run through `perl -CSD` (see § Queued) — an em dash **surrounded by spaces**. AI-generated em dashes are usually surrounded by spaces, contrary to common typographic guidelines. A closed em dash (`word—word`) is normal typography and does **not** fire. *Density cap:* ≤1 em dash per 400 words of visible copy; ≥3 in one section fires regardless of spacing. *En dashes:* ranges use a hyphen (`2018-2026`). Unchanged.
- *Why cheap:* the spacing, not the glyph, is the tell. Treating every em dash as a hard fail put the catalog's only binary ship-block on its weakest instrument class, and the signal is decaying anyway — OpenAI suppressed em dashes in GPT-5.1.
- *Fix:* Close the dash (`word—word`) or use commas, colons, periods, parentheses. Hyphen for ranges. The zero-em-dash rule survives as **house style** in `critique.md § 3.2`, not as a detection signal.
- *Class:* P — density only. It may not block a ship on its own.

**`vague-headline`** (aspirational nothing-copy + buzzwords)
- *Detect:* "Build the future of work," "Your all-in-one platform," "Scale without limits," "For Modern Teams," "In Today's Fast-Paced World," "The Intelligent Way To…," "Stop [X]. Start [Y]." Says nothing about the actual product. The vocabulary blocklist is **banded by model era** — a list calibrated to 2023-era GPT-4 no longer fires on current output:
  - *Live band (mid-2025 →, GPT-5):* **emphasizing, enhance, highlighting, showcasing** — these four are the current signal. Grok adds **causal, empirical, correlate, underscore**.
  - *Decayed band (2023 – mid-2024, GPT-4), keep only for auditing older copy:* Additionally, boasts, bolstered, crucial, delve, enduring, garner, intricate, interplay, key, landscape, meticulous, pivotal, underscore, tapestry, testament, valuable, vibrant. (Plus the marketing set the file has always carried: streamline, empower, supercharge, world-class, enterprise-grade, next-generation, cutting-edge, Elevate, Seamless, Unleash, Revolutionize.)
  - *Copula avoidance (strong):* **serves as / stands as / marks / functions as / represents / boasts / features / maintains / offers / refers to** standing in for a plain "is". Corpus evidence: >10% drop in "is"/"are" in academic writing in 2023 with no prior trend. Grep: `grep -nE '\b(serves as|stands as|functions as|represents a|boasts|refers to)\b'`.
  - *Structural tells, which matter more than vocabulary:* **negative parallelism** ("not just X, but Y"), copula avoidance, **rule of three**, **elegant variation** (renaming the same thing every mention to avoid repeating a word).
  - Source: https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
- *Why cheap:* generic aspiration plus era-typical vocabulary is the textual signature of AI copy. Population evidence: ≥13.5% of 2024 PubMed abstracts show LLM excess vocabulary, up to 40% in some subcorpora (Kobak et al., *Science Advances* 11(27), 2025).
- *Fix:* Rewrite in the founder's voice with a concrete verb+noun that says what the product literally does. Litmus: **"Would our CEO actually say this?"** Models: Stripe "Financial infrastructure for the internet"; Linear "Plan and build products." Sentence case headers, not Title Case; active voice; no "Oops!" errors; no exclamation marks in success copy.
- *Threshold:* **>2 live-band or structural hits per 300 words of marketing copy is a rewrite, not an edit.**
- *Class:* P. A 2025 study found human discrimination no better than chance — use the list as a grep, never as a verdict.

**`aphoristic-cadence`** (manufactured-contrast lines) — *machine-precise trigger*
- *Detect:* **≥3** sections landing on a short rebuttal ("X. No Y." / "X. Just Y.") or manufactured-contrast aphorism ("Not a feature. A platform."). Once is fine; the *pattern* is the tell.
- *Why cheap:* the repeated "X. No Y." cadence is a recognizable AI rhythm.
- *Fix:* Vary sentence structure across section subheads and taglines.
- *Class:* P.

**`fake-content`** (placeholder / "Jane Doe" data) — *machine-precise ban*
- *Detect:* "Lorem ipsum," "User Name," "Item 1 / Item 2 / Item 3," generic avatars; **no John Doe / Jane Smith / Acme / Nexus / SmartFlow**; **no fake round numbers** (`99.99%`, `50%`, `$100.00`, `1234567`); identical dates; one shared avatar.
- *Why cheap:* placeholder data + round numbers + repeated placeholders are the instant "demo data / nothing was designed against real content" tell.
- *Fix:* Realistic domain data — "Whole Foods Market −$67.23 (today)," "Netflix −$15.99 (yesterday)," real merchant icons, green for income. Use **messy organic values** (`47.2%`, `$99.00`, `+1 (312) 847-1928`), diverse realistic names, invented contextual brand names, randomized dates, a unique **seeded** avatar per person (`picsum.photos/seed/{id}/...`).
- *Class:* P.

**`fake-precise-numbers`** (unlabeled fabricated metrics)
- *Detect:* fake-precise stats like `92%`, `4.1x`, `48k` presented as real when they aren't.
- *Why cheap:* a precise number without a referent reads as invented authority.
- *Fix:* Only real figures, or explicitly mark mock data (`{/* mock */}`). *(→ `unsourced-stats` for the cite-or-cut rule.)*
- *Class:* P.

**`ai-illustrations`** (stock blobs / floating widgets)
- *Detect:* abstract 3D blobs floating in space; impossibly-lit diverse-office stock photos; decorative UI widgets with no function; "slightly too smooth, too symmetrical, plastic."
- *Why cheap:* AI-gen imagery is instantly recognizable and undermines trust.
- *Fix:* Real product screenshots (Loom, Amplitude show real dashboards), real team photos, or custom illustration in one committed style.
- *Class:* P.

**`fake-testimonials`**
- *Detect:* "Sarah K., verified customer," "Mike from Seattle," rotating first-name+initial casts; stock headshots with "perfect pores, no life behind the eyes"; tautological quotes.
- *Why cheap:* invented social proof is both a slop tell and a trust killer.
- *Fix:* Real named customers with company + role + a specific outcome, or omit the section.
- *Class:* P.

**`fake-trust-bar`** (logo/social-proof theater)
- *Detect:* "Trusted by 5,000+ teams" on a 3-week-old site; unlabeled "As Seen On" press strip; one logo standing in for "10,000+ organizations."
- *Why cheap:* unverifiable claims read as fabricated.
- *Fix:* Only real, verifiable logos/counts; otherwise cut the section.
- *Class:* P.

**`unsourced-stats`**
- *Detect:* "8x," "750m+ Organic Views," "70% / 25% / 5%" pie charts with no methodology; "SOC 2 Type II (pending)."
- *Why cheap:* numbers without referents scream slop.
- *Fix:* Cite the source/method or delete.
- *Class:* P.

**`emoji-headings`**
- *Detect:* section titles or bullets led by emoji (🚀 Features, ✨ Benefits, 💡 How it works); emoji as icon substitutes throughout; emoji nav/sidebar icons.
- *Why cheap:* a leading emoji in a heading is one of the strongest "an LLM wrote this" tells and reads as unpolished.
- *Fix:* A real icon set (consistent stroke width, size, grid) or nothing. No emoji anywhere — UI, code, markup, alt text. Differentiate from the default Lucide/Feather set (→ Phosphor/Heroicons/Radix), pin ONE stroke width, and avoid cliché metaphors (rocket=Launch, shield=Security → bolt/fingerprint/spark/vault).
- *Class:* P.

**`ai-tells-blocklist`** (the hard-ban chrome tells) — *hard-ban unless explicitly briefed*
- *Detect:* **div-based fake screenshots / terminals / dashboards** (**the #1 LLM-design tell**); version labels in a hero (`V0.6`, `BETA`); section-number eyebrows and `01/4` pagination; scroll cues (`↓ Scroll to explore`); fake version footers (`Build 0048`, `last sync 4s ago`); weather/locale strips (`LIS 14:23 · 18°C`); performative-craftsman labels ("Field notes", "On our desks"); **custom mouse cursors**.
- *Why cheap:* each is a recognizable template artifact that adds no information; the div-based fake product screenshot is the strongest single "an LLM built this" signal.
- *Fix:* Show a real product screenshot (or a believable minimal fragment), keep the default cursor, and strip version/scroll/weather chrome unless the product genuinely needs it.
- *Class:* P.

### STATES, TOKENS & A11Y (functional slop — visual review misses this)

**`no-empty-loading-states`** (missing interaction states)
- *Detect:* only the happy, fully-loaded path exists; no focus / disabled / error / empty / loading.
- *Why cheap:* real products live in their edge states; their absence proves the screen was never used.
- *Fix — handoff gate:* core interactive components MUST ship **focus + disabled + error/loading + empty**. Follow the response-time ladder: `<1s` no indicator · `1–2s` immediate control feedback · `2–10s` skeleton (content) or spinner+label (discrete action) · `>10s` determinate progress + cancel. Empty state = illustration + one-line contextual headline + one supporting line + **exactly one** imperative CTA ("Add your first task"); hide surrounding chrome when there's no data.
- *Class:* n/a (measured defect) — the ratio gate in § Handoff gates decides it.

**`no-validation`** (forms without guardrails)
- *Detect:* forms with no required markers, no inline validation, no error copy.
- *Why cheap:* validation is invisible until you build it; its absence is a codegen signature.
- *Fix:* Required indicators, inline validation on blur (never mid-typing), explicit blame-free error copy that answers what happened / why / how to fix, and preserves user input.
- *Class:* n/a (measured defect).

**`a11y-omission`**
- *Detect:* no contrast consideration, tiny targets, missing focus ring / ARIA / keyboard.
- *Why cheap:* inaccessible UI is unfinished UI.
- *Fix — WCAG 2.2 AA:*
  - Contrast **4.5:1** normal text, **3:1** large text (large = ≥24px, or ≥18.66px/≥18px bold) and **3:1** for UI component boundaries in every state — computed as the **worst case across all gradient stops** — verified across ~5 common text styles in **both light and dark**.
  - Target size **≥24×24 CSS px** (AA minimum); flag any interactive element **<44×44px**; ship **44–48px** for primary/mobile targets (AAA / Apple HIG 44pt / Material 48dp), primary CTAs in the thumb zone (bottom half).
  - Body text like `#374151` on white — not pure `#000`, not low-contrast gray. Darkest gray `#111827`, not `#000`.
  - Visible `:focus-visible` ring (outline + offset), never `outline: none` without a replacement. Keyboard nav + ARIA labels on icon-only buttons. Keep semantic heading order (no h1→h3 skip).
- *Class:* n/a (measured defect).

**`text-legibility-floors`** (the machine-precise a11y/legibility thresholds) — *each is a direct grep/render check*
- *Detect (each fires independently):*
  - **Low contrast** — text/bg pair below **4.5:1** body / **3.0:1** large (`≥18px`, or bold), worst case across gradient stops, in **both** themes.
  - **Gray-on-color** — near-neutral text (chroma **<20**) on an all-chromatic bg (every stop chroma **≥40**). `text-gray-400` on a saturated button.
  - **Cramped padding** — vertical padding `< max(4px, fontSize×0.3)` OR horizontal `< max(8px, fontSize×0.5)`; also wrapper children flush (`≤2px` inset) against a bordered/colored boundary.
  - **Tight line-height** — non-heading text (>50 chars) with `line-height / font-size < 1.3`.
  - **Line length too long** — text rendering **>85 chars/line**.
  - **Tiny body text** — body content (>20 chars) `<12px` outside UI chrome (buttons/labels/badges exempt).
  - **Extreme negative tracking** — body (>20 chars) `letter-spacing ≤ -0.05em`.
  - **Wide tracking on body** — non-uppercase body `letter-spacing > 0.05em`.
  - **All-caps / justified body** — `uppercase` over >30 chars; `text-align:justify` without `hyphens:auto`.
  - **Body text at viewport edge** — wide `<p>`/`<li>` with `rect.left <16px` or `right > vw-16px`.
- *Why cheap:* each is a "nobody rendered this against real content" giveaway and a real accessibility failure.
- *Fix:* Body **≥14px** (16 ideal), `leading-relaxed` (1.5-1.7), `max-w-[65ch]`/`max-w-prose`, tracking within `[-0.02em, +0.05em]`, `p-3`+ inside any bordered/colored container, `text-white` or a bg-hue tint on colored surfaces, `px-4`/`px-6` gutters. Wide tracking = short uppercase labels only.
- *Class:* n/a (measured defect).

**`token-coverage-failure`**
- *Detect:* ad-hoc colors / spacing / radius / shadow hardcoded across components instead of tokens.
- *Why cheap:* every value invented on the spot guarantees drift and inconsistency.
- *Fix — audit gate:* **8 of 10 sampled components must map cleanly to tokens** for color, typography, spacing, radius, and elevation. If <8 pass, **pause new screens and repair the token baseline first.** Use semantic tokens in markup (`bg-primary`, not `bg-zinc-900`).
- *Class:* S.

**`cross-screen-inconsistency`**
- *Detect:* different colors/fonts/spacing screen-to-screen because each was generated in isolation.
- *Why cheap:* inconsistency is the fingerprint of one-shot-per-screen generation.
- *Fix:* Reference one shared theme file in every prompt/build ("primary `#…`, bg `#…`, [font], 8pt grid").
- *Class:* S.

**`inconsistent-spacing`** (rhythm loss)
- *Detect:* arbitrary off-scale gaps; layout breaks when content changes; **more space *within* a group than *around* it** (the biggest amateur tell — a label must sit closer to its own input than to the field above).
- *Why cheap:* arbitrary spacing is the #1 developer tell.
- *Fix:* One **8-point grid** for all spacing (4/8/12/16/24/32/48/64/96/128); remap generated spacing onto the approved scale; never invent an off-scale value. Group by proximity.
- *Class:* S.

**`default-shadcn-untouched`** — *co-occurrence, not a single trigger*
- *Detect:* fires when **≥3 of 5** hold simultaneously — (1) every neutral token has literal chroma 0 `oklch(L 0 0)`; (2) `--radius: 0.625rem` unchanged; (3) `--ring: oklch(0.708 0 0)` unchanged; (4) `--font-sans` still a bare system stack; (5) the chart/destructive set matches Tailwind's shipped palette byte-for-byte (§ SUBSTRATE-DEFAULTS). Each default individually is a defensible choice — 10px is a fine base radius — and only co-occurrence proves nothing was decided.
- *Why cheap:* shadcn's restrained neutral defaults are a *starting point*; shipping them unmodified is indistinguishable from every other boilerplate.
- *Fix:* Apply a real theme — brand hue + chroma on the neutral skeleton, a chosen radius and shadow set, a font trio (sans/serif/mono). A theme is a complete design language, not a palette. (Tools like tweakcn generate a full OKLCH theme from an image/brand.)
- *Class:* D. Any single one of these alone is advisory.

### APP-UI (product surfaces — dashboards, tables, ⌘K, settings, forms, states, onboarding)

The slop tells that show up in *app* chrome rather than marketing pages. The through-line (from the product-UI corpus): AI-slop app UI fails because it is **decorative where it should be functional, and generic where it should be specific** — color and motion get spent on ornament while density, keyboard control, and multi-state design go missing. Each defect below is tagged **grep-detectable** (a pattern the § Automatable detectors can see) or **judge-only** (a behavioral/structural *absence* a grep can't prove — needs the human/judge lens).

> **Threshold caveat (read before enforcing).** Several numbers in this subsection are directional or single-author — e.g. ">200ms hover on a table row reads bouncy," the <300ms motion ceiling and exact cubic-bezier easings (largely one practitioner, Emil Kowalski), and command-palette latency targets (~50–100ms, reconstructed from a single dated post). Treat them as **starting points, not hard law**; the judge should flag *direction* (a springy 400ms row hover, a visibly animated palette) rather than fail a screen for missing a specific millisecond value.

**`nav-color-chips`** (colored icon-background chips on nav / list rows)
- *Detect:* every sidebar or list row carries a colored icon-background chip / colored swatch; color rides on chrome instead of on data.
- *Why cheap:* it is decorative color standing in for hierarchy that should come from spacing, weight, and alignment. Linear stripped team-icon color backgrounds entirely in its refresh — calm chrome recedes so data leads.
- *Fix:* Remove the chips; mute/shrink inactive icons; let a 4/8px spacing scale + weight-not-size type carry hierarchy. Ration brand hue to one role (focus ring / primary CTA).
- *Mode:* **judge-only** (structural), with a grep assist — colored `bg-*` on nav/list icon wrappers.
- *Class:* P.

**`brand-as-active-fill`** (brand hue as the active/selected row fill)
- *Detect:* the active nav row or selected table row is filled with the brand/indigo/violet color.
- *Why cheap:* the loudest surface gets the loudest color, so the whole chrome shouts; the accent stops meaning "primary action."
- *Fix:* Use a **neutral accent fill** for hover/active (shadcn `--sidebar-accent`, `hover:bg-muted/50` / `data-[state=selected]:bg-muted` — two opacity levels of one neutral token). Reserve the brand hue for the **focus ring and the primary CTA**.
- *Mode:* **grep-detectable** — brand `bg-` on `data-[state=selected/active]` / `aria-current` / `.active` rows.
- *Class:* P.

**`single-density-lock`** (one fixed row height, no tier toggle)
- *Detect:* a table/list ships a single "comfortable" row height with no way to compact it; power users waste screen space.
- *Why cheap:* a designer-dictated density that ignores that dense surfaces are scanned by power users.
- *Fix:* **Named density tiers that change padding only, never font-size** (Carbon: 24 / 32 / 48 / 64px; MUI compact ~32 / standard 52px), persisted as a user toggle.
- *Mode:* **judge-only** (behavioral — a grep can't see the missing toggle).
- *Class:* P.

**`proportional-numerals`** (proportional figures in numeric columns) — *the single most common table slop tell*
- *Detect:* prices / counts / timestamps use proportional figures, so digits jitter and numeric columns misalign.
- *Why cheap:* it is the fastest "nobody looked at real data in this table" giveaway.
- *Fix:* `font-variant-numeric: tabular-nums` (fallback `font-feature-settings:"tnum","zero"`) on **all** numeric UI — tables, KPI/stat cards, timers, numeric inputs. Works in Inter/Roboto/SF/system-ui with no special font.
- *Mode:* **grep-detectable** — absence of `tabular-nums`/`tnum` on numeric surfaces.
- *Class:* n/a (measured defect).

**`animated-command-palette`** (decorative entrance/motion on a ⌘K surface)
- *Detect:* the command palette fades/zooms/blurs in, or the selected-row highlight animates, so highlight lags fast arrow-key nav.
- *Why cheap:* a high-frequency keyboard surface is where perceived latency compounds; ornament makes it feel slow. Raycast ships **zero** open/close animation on its palette.
- *Fix:* Open the palette (and other keyboard-triggered / high-frequency surfaces — filters, context menus) with **0ms**. Swap the selected row via an instant data-attribute token change, no transition. If you must animate the container, cap it ≪300ms fade+zoom, opacity-only overlay.
- *Mode:* **judge-only** (behavioral/structural — the tell is presence of animation *where there should be none*; a grep can spot `animate-*`/`transition` on a command dialog but can't judge the 0ms intent).
- *Class:* P.

**`mouse-only-surface`** (no ⌘K, no shortcuts, no keyboard row nav)
- *Detect:* the app is fully mouse-driven — no global command menu, no single-letter object actions, no `J/K`/arrow row traversal, no `?` overlay.
- *Why cheap:* keyboard-first interaction is the defining trait of top-tier product UI; its absence marks a generic build.
- *Fix:* One global palette (`⌘/Ctrl+K`), single-letter object actions, two-key `G`+letter navigation, and `?` for a searchable shortcut overlay. Keep navigation (highlight cursor) and selection (bulk-mark) as **orthogonal** states with separate keys.
- *Mode:* **judge-only** (behavioral — greps can't prove the absence of a whole interaction model).
- *Class:* n/a (measured defect — press the keys).

**`no-grid-keyboard-model`** (a multi-control table with no cell/row keyboard navigation)
- *Detect:* every row holds 2+ focusable controls and the only keyboard affordance is Tab, so crossing one 25-row table costs 50–75 tab stops. No arrow-key cursor, no Home/End, no Ctrl+Home/End, no Shift+Space row select, no F2/Enter edit contract, no `role="grid"`.
- *Why cheap:* it is the single largest gap between a generated table and a shipped one, and the spec has published the whole answer for years. The APG says grid grouping "can dramatically reduce the number of tab stops on a page."
- *Fix:* Keep the semantic `<table>`, add `role="grid"`, implement the APG data-grid key map with **roving tabindex**. Set `aria-rowcount`/`aria-rowindex` when virtualized. Scope single-letter shortcuts to the grid container (WCAG 2.1.4, Level A).
- *Mode:* **grep-detectable assist** (absence of `role="grid"` / `tabindex={-1}` / arrow-key `onKeyDown` on a table with 2+ interactive cells per row) + **judge-only** for correctness.
- *Class:* n/a (measured defect — count the tab stops).

**`missing-state-machine`** (focus / disabled / loading / empty / error missing or bolted on) — *see also STATES › `no-empty-loading-states`*
- *Detect:* only the happy, fully-loaded path exists; states were added as an afterthought rather than designed into the component contract.
- *Why cheap:* real product surfaces live in their edge states; their absence proves the screen was never used.
- *Fix:* Treat every interactive element as a **6+ state machine** (default/hover/focus/active/disabled/loading/empty/error), each with its own token + transition, and pair every hover/active/disabled change with a matching `focus-visible` treatment for keyboard parity.
- *Mode:* **judge-only** (an absence).
- *Class:* n/a (measured defect).

**`off-scale-spacing`** (non-4px-multiple values) — *see also STATES › `inconsistent-spacing`*
- *Detect:* arbitrary gaps like 13 / 18 / 22px — the fastest tell of ungoverned generation.
- *Why cheap:* off-scale spacing is the #1 "a machine emitted this, unchecked" signal.
- *Fix:* A strict **4px-multiple** scale (4/8/12/16/24/32/48/64/96/128), no exceptions; remap generated spacing onto it. (The corpus tightens the marketing 8pt grid to a 4px half-step for dense app chrome.)
- *Mode:* **grep-detectable** — arbitrary `p-[…]`/`gap-[…]` or inline `px` not divisible by 4.
- *Class:* S.

**`card-soup`** (every section wrapped in a bordered + shadowed card) — *see also LAYOUT › `card-in-card`*
- *Detect:* every region is boxed in a bordered+shadowed card, cards nested 3–5 deep, one flat drop-shadow reused on all of them.
- *Why cheap:* recursive boxing is visual noise that betrays no layout thinking.
- *Fix:* **Cardless chrome** — bold section titles + whitespace carry structure; reserve cards/shadows for genuinely floating surfaces. In light app surfaces prefer a 1px border at rest, shadow only when a surface actually floats.
- *Mode:* **judge-only** (structural), with a grep assist for nested bordered cards.
- *Class:* P.

**`one-layer-focus-ring`** (single outline ring that vanishes on colored nav)
- *Detect:* a one-layer `outline`/single-stroke focus ring that disappears against a colored or dark nav background.
- *Why cheap:* it reads as "focus was styled once for the white canvas and never tested on chrome."
- *Fix:* A **two-layer ring** — a background-color gap then a colored stroke: `box-shadow: 0 0 0 2px var(--background), 0 0 0 4px #006bff` — visible on both light and colored backgrounds. Use `:focus-visible`, full opacity (shadcn's default ~50% ring commonly fails AA 3:1).
- *Mode:* **judge-only** (needs rendering against real chrome), with a grep assist for single-layer `outline` on `:focus`.
- *Class:* n/a (measured defect — compute the ring's contrast against the chrome it sits on).

**`bulk-edit-modal`** (a separate bulk-edit modal instead of ⌘K reuse)
- *Detect:* selecting rows opens a bespoke bulk-action modal with its own controls, divorced from the single-row edit affordances.
- *Why cheap:* it duplicates interaction surface and breaks the keyboard-first model — two ways to set the same field.
- *Fix:* **Reuse the ⌘K palette as the bulk-action surface** once rows are selected, with the *same* field pickers as single-row inline edits.
- *Mode:* **judge-only** (behavioral).
- *Class:* P.

**`select-all-scope-unstated`** (a select-all whose scope the UI never states)
- *Detect:* the header checkbox says "select all" and nothing says *all of what* — the current page, the current filter, or the entire table. Three different destructive blast radii behind one control.
- *Why cheap:* it is the difference between deleting 25 rows and deleting 40,000, decided by an assumption the UI never surfaced.
- *Fix:* State the scope in the control and offer the escalation explicitly — "25 on this page selected · Select all 1,284 matching this filter".
- *Mode:* **judge-only** (a copy/behaviour absence).
- *Class:* n/a (measured defect — read the label).

**`dead-end-filter-empty`** (filter-empty states that don't offer a next step)
- *Detect:* filtering to zero results yields a lone icon + "No data" + a vague "Get Started," with no way forward and no echo of the query.
- *Why cheap:* the state most often skipped; a dead end proves the empty path was never designed.
- *Fix:* Filter-empty states **always offer a next step** (clear-filters or a docs link) and **echo the live query** ("No logs match \"…\". Clear the filter…"). Guided empty states name the exact absent/filtered condition and cap CTAs at 1 primary + ≤1 secondary, semantic and in tab order.
- *Mode:* **judge-only** (an absence / copy-quality call).
- *Class:* n/a (measured defect).

### TOKEN-DRIFT & PROVIDER-GATED

**`token-drift`** (literals outside the declared closed system) — *machine-precise tolerances*
- *Detect:* when a `DESIGN.md`/`design.json` (or theme token file) exists, treat the palette/type/radius as a **closed system** and flag any literal outside the ramp. Detector tolerances: **color ±6 per RGB channel**; **radius ±0.5px** (any **≥99px** = pill, allowed if a pill token exists). Hardcoding `#8b5cf6` or `rounded-[7px]` when the scale is defined = a finding. `var()` refs, `transparent`/`currentColor`/`inherit`, and alpha `≤0.05` colors are always allowed; only flag color literals in a real style context (after `color/background/border/...:`, in a gradient/`color-mix()`, or a JS color key). A drifted **font** is a hard finding; drifted color/radius are advisory.
- *Why cheap:* every value invented on the spot guarantees drift; a closed system is what makes a design language coherent.
- *Fix:* Map colors to CSS vars (`--primary`, tonal ramps) and radii to shadcn `--radius`; justify any deliberate addition to the ramp or delete it. *(→ STATES › `token-coverage-failure` for the coverage gate.)*
- *Mode:* **grep-detectable** against the token source of truth.
- *Class:* S.

**`provider-gated-tells`** (advisory — enable per model)
- *GPT:* **hairline border + wide diffuse shadow co-occurring** — ≥2 thin borders (`width ≤1.5px`, alpha ≥0.28) with a shadow whose max blur ≥16px (layers alpha ≥0.12). Commit to a defined **edge OR** a soft **float**, not both. Also: decorative `repeating-{linear,radial,conic}-gradient()` stripes or a two-hairline-stop tiling **grid background** on a plain surface (reserve grids for canvas/map/blueprint); `"<word> theater"` framing copy.
- *Gemini:* **`img:hover` transform** — `hover:scale-/rotate-/translate-/skew-` (e.g. `hover:scale-105`) on an `<img>`. Let imagery sit still.
- *Mode:* **grep-detectable**, off by default; enable via `--gpt` / `--gemini`.
- *Class:* P.

---

## Handoff gates (metric · window · trigger)

Each gate = a metric measured over a window, with an action trigger. A failing gate blocks "done."

| Gate | Metric | Window | Trigger on failure |
|---|---|---|---|
| Token coverage | 8 of 10 components map to tokens (color/type/space/radius/elevation) | 10 components on the screen | Pause new screens; repair token baseline |
| Token drift | every color/radius/font literal within tolerance of the ramp (color ±6/channel, radius ±0.5px, ≥99px=pill) | all literals vs the `DESIGN.md`/theme source | Justify the addition or delete the literal |
| Shadow recipes | ≤3 shadow recipes on core surfaces | cards, menus, modals, buttons in one flow | Collapse to named elevation levels |
| Contrast | 4.5:1 normal / 3:1 large / 3:1 UI boundary (worst case across gradient stops) | 5 text styles × light AND dark | Blocks handoff |
| Copy density | ≤1 em dash per 400 words; ≤2 live-band or structural hits per 300 words | all UI + marketing + empty-state strings | Rewrite the copy. Class P — never blocks a ship on its own |
| State coverage | **≥90% of data-rendering components contain all three of** `isLoading\|isPending\|Skeleton`, `error\|isError`, and an empty branch (`\.length === 0` or `<Empty`) | every file under the route that imports data | Keep screen in "draft" |
| Distinct colour literals | count unique resolved colour values, excluding alpha variants of the same base | the built CSS for the route | **HARD FAIL above 20.** GOV.UK's entire functional palette is **20 named roles resolving to 13 unique hex values**; the median real desktop page ships **48 distinct text colours and 24 duplicates** (HTTP Archive Web Almanac 2019, p10/p25/p50/p75/p90 = 8/22/48/83/131). Land on the GOV.UK side |
| Distinct font sizes | count unique `font-size` values | the built CSS for the route | **Investigate above 8.** Median real page: **40 on mobile, 38 on desktop** (same source). A 6–8 step scale is the whole budget |
| Distinct spacing values | count unique margin/padding values | the built CSS for the route | **Investigate above 10.** Median real desktop page: **96 distinct margin values** (same source) |
| Convergence stop-rule | variants visibly converge toward the brief | after 2 generate-revise loops | Stop re-rolling; **tighten the brief** instead |

---

## Process fixes (the real leverage — slop is a workflow bug, not a "better adjective" bug)

One prompt fuses three jobs — taste direction, visual exploration, implementation spec — so the model outputs the safe center that satisfies all three.

**`adj-only`** (an adjective standing in for a direction) — *the named process defect*
- *Detect:* an instruction of the form *"make it beautiful / premium / modern / not cookie cutter"* — from the user **or from you to yourself**.
- *Why cheap:* it is a defect, not a direction. It names no dimension to move along, so the model returns the distributional mean — the exact output the adjective was meant to avoid. (One leaked-prompt archive, uncorroborated, records a major generator whose entire design prompt is this one sentence; its default output is the weakest of the tools compared there.)
- *Fix:* convert every adjective into one of the **five design dials** (→ `brand-to-system.md § Design dials`), a numeric cap, or a named reference with the mechanics extracted from it. Same defect as the self-diagnostic below, seen from the other side.
- *Class:* n/a (measured defect — read the instruction).

- **Self-diagnostic:** *"If you're replying to AI output with adjectives ('cleaner', 'more premium', 'less generic'), the three jobs are still fused."* Adjectives are not an input.
- **Separate the three jobs.** Decide the aesthetic first (needs references + a POV), explore distinct options second (needs multiple directions to compare), spec + build last (needs concrete tokens).
- **Fork, don't iterate.** Generate ≥2 *distinct* directions and compare; don't refine one.
- **Feed real references before generation** — extract 3–5 designs from Dribbble/Mobbin, describe what makes each work, then generate against those descriptions.
- **Name the aesthetic explicitly** ("Neobrutalism: thick borders, bold colors"), not "clean and modern." Specificity of the aesthetic name is the lever that collapses the model's options to one coherent direction.
- **Pin a design-system file before code** and reference it in every generation; state the font choice before coding.
- **Structured review passes:** critique → audit → polish → normalize. Iterate layout → styling → detail. Never ship the first output.
- **Do not import superdesign.dev's OSS prompt.** Its aesthetic block — "elegant minimalism", "well-proportioned white space", "subtle shadows and modular card layouts", "refined rounded corners" — *is* the distributional centre, described approvingly. Its rule "all text should be only black or white" contradicts this file's three-gray-level hierarchy and the no-pure-`#000`/`#fff` dark-mode rule; ours wins, because pure black on pure white is a glare and contrast failure at scale and it collapses the hierarchy that carries the layout in grayscale. Take only the structural parts: three parallel variant agents, `{name}_{n}` file naming, and the 4/8pt multiple rule.

---

## Good-defaults reference (encode these as the antidote)

| Dimension | Slop default | Encode instead |
|---|---|---|
| Accent color | `#6366F1` indigo, purple/cyan gradients (`#7c3aed #8b5cf6 #a855f7 #764ba2`) | 1 dominant + 1 sharp accent (<80% sat), semantic tokens |
| Background | warm cream/beige (`#f5f1ea #f7f5f1 #efeae0`, `bg-stone/amber-50`) | deliberate palette; rotate family each project; off-white never `#fff` |
| Palette balance | even pastels | ~60/30/10, dominant + sharp accent |
| Font | Inter / Roboto / system; escape-hatch Geist / Space Grotesk / Fraunces + Instrument Serif | distinctive display + body + mono trio (Geist / Satoshi / Cabinet Grotesk + a mono); serif never in dashboards |
| Weight contrast | 400 vs 600 | 100/200 vs 800/900 |
| Size scale | ×1.5 steps | ×3+ steps; hand-picked 12/14/16/18/20/24/30/36/48/60/72 |
| Spacing | ad hoc | 8pt grid: 4/8/12/16/24/32/48/64/96/128 |
| Radius | uniform 16px | scale 0/4/8/16 by role |
| Shadow | one `rgba(0,0,0,0.1)` everywhere | 3–5 named elevation tokens, two-layer above resting, alpha by role (~.05→.1) |
| Grays | pure `#000`/`#fff` | 8–10 tinted shades; darkest `#111827`, body `#374151` |
| Layout | centered column + 3 cards | asymmetric grid, content-driven counts |
| Motion | bounce + scattered fades | one staggered page-load reveal, purposeful easing, reduced-motion gated |
| Contrast | unchecked | 4.5:1 / 3:1, worst case across gradient stops, verified light + dark |
| Touch target | tiny (<44px) | ≥24px (AA); 44–48px primary/mobile, thumb zone |
| Copy | spaced em dashes, live-band buzzwords, "Jane Doe", fake-precise stats | closed dashes at ≤1 per 400 words, concrete verb+noun, messy organic data, cited or mock-labeled numbers |
| Body text | proportional figures, sub-14px, >85ch lines | tabular-nums on metrics, ≥14px, `max-w-[65ch]`, leading 1.5-1.7 |
| States | happy path only | focus + disabled + error + loading + empty |

**Semantic token naming (do this, not raw values in markup):** `--color-action-primary`, `--color-feedback-success`, `--elev-1..5`, `--space-1..8`, `--radius-sm/md/lg`. Store in one file (e.g. `app/globals.css`) referenced everywhere.
