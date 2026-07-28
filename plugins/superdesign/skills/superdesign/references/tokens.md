# Token System — OKLCH, 3-Tier, Tailwind v4 `@theme`

The complete, concrete token system the skill emits. Every value is authored in **OKLCH**
(`oklch(L C H)`), organized in **three tiers** (primitive → semantic → component), and shipped
as Tailwind v4 CSS-first tokens (`:root` / `.dark` + `@theme inline`). All numbers below are
grounded in the research notes (Tailwind v4, Radix Colors, Material 3, shadcn/ui, tweakcn,
Evil Martians, IBM Carbon, Inter Dynamic Metrics, Emil Kowalski / Rauno / M3 motion).

**The one knob that adapts everything to a brand:** the brand **hue angle `H`** (0–360). Hold `H`
constant down the brand ramp, keep the neutral ramp faintly tinted toward it, and every other
value (spacing, radius, type, motion) is brand-agnostic. Swap `H` → the whole system re-skins.

---

## 0. Governing rules (why OKLCH + 3 tiers)

- **OKLCH is perceptually uniform:** equal `L` steps *look* equally spaced, and `L` is decoupled
  from hue/chroma. HSL lies (yellow vs blue at `L 50%` look nothing alike). Consequence: verify
  contrast **once per L step**, then swap hues freely — contrast guarantees survive. This is the
  single biggest reason to author in OKLCH. Baseline-supported since May 2023 (~90% global); ship
  without fallbacks. Default in Tailwind v4.
- **`L` 0–1, `C` 0→~0.37 (hard ceiling for sRGB+P3 safety), `H` 0–360.** Never crank `C` past a
  hue's gamut ceiling — Chrome/Safari clip rather than gamut-map, so it renders wrong.
- **3-tier chain is strictly one-way:** `component → semantic (alias) → primitive → raw value`.
  A component token **never** points straight at a primitive. Dark mode / re-branding = re-pointing
  the **semantic** layer only; components and markup never change. Only ~10–20% of primitives get
  promoted to semantics. Promote a component token upward only at **3+ consumers** (Curtis rule).
- **Delivery format:** raw `oklch()` primitives + semantic values live in `:root` / `.dark`; a single
  `@theme inline` block maps them into Tailwind's `--color-*` / `--radius-*` / `--shadow-*` namespaces
  so `bg-primary`, `rounded-lg`, `shadow-md` resolve. `@theme inline` is **mandatory** whenever a token
  references another variable (the dark-mode case) — plain `@theme` breaks scope reactivity.
- **Anti-slop guardrail (Anthropic cookbook + slop catalog):** do **not** ship the training-data default
  accent `indigo-500 #6366F1` / `violet-500 #8B5CF6` / `purple-500 #A855F7`, nor purple→blue gradients
  on white (both flagged by the cookbook), nor a single `rgba(0,0,0,0.1)` shadow on everything, nor
  uniform `16px` radius everywhere (the latter two from the wider slop catalog).
  Purple is allowed only as a *real* brand decision. The worked example below uses a deliberate cobalt
  `H=240` — swap it for the project's actual brand hue.

---

## 1. Color primitives — the ramps

### 1.1 Ramp-building recipe (applies to every hue family)

1. **Hold `H` constant** down the ramp (small "hue torsion" of ±2° is fine and matches Tailwind).
2. **Descend `L` monotonically.** Canonical 11-step `L` ramp (50→950), matched across Tailwind v4 /
   Evil Martians: `0.978, 0.936, 0.881, 0.827, 0.742, 0.648, 0.573, 0.469, 0.394, 0.320, 0.238`.
3. **`C` follows a bell curve** — near-white and near-black can't hold chroma. Peak at 500–600,
   taper to the ends. Example per-step `C`: `0.011, 0.032, 0.061, 0.091, 0.140, 0.147, 0.130, 0.107,
   0.090, 0.073, 0.054`.
4. **Neutrals get tiny chroma (`C ≈ 0.002–0.01`) tinted toward the brand hue** — never pure `C=0`
   (feels dead), never high chroma. Only `L` varies meaningfully.

Verified real anchors to sanity-check generated values (Tailwind v4, authoritative):
`red-500 oklch(0.637 0.237 25.331)` · `blue-500 oklch(0.623 0.214 259.815)` ·
`green-500 oklch(0.723 0.219 149.579)` · `gray-950 oklch(0.13 0.028 261.692)`.

### 1.2 Neutral ramp (60% of the UI — the most important ramp)

Tinted toward the brand hue (`H=240`), chroma held ≈0.002–0.008. Does all the heavy lifting:
backgrounds, surfaces, borders, body text, disabled states.

```css
--neutral-50:  oklch(0.985 0.002 240);
--neutral-100: oklch(0.970 0.003 240);
--neutral-200: oklch(0.922 0.004 240);
--neutral-300: oklch(0.870 0.005 240);
--neutral-400: oklch(0.708 0.007 240);
--neutral-500: oklch(0.556 0.008 240);
--neutral-600: oklch(0.439 0.008 240);
--neutral-700: oklch(0.371 0.008 240);
--neutral-800: oklch(0.269 0.007 240);
--neutral-900: oklch(0.205 0.006 240);
--neutral-950: oklch(0.145 0.006 240);
```
Also ship **alpha neutrals** for compositing over color/photos (where solid grays fail) — use
`--alpha(var(--neutral-950) / 8%)` / Tailwind's `bg-neutral-950/8`, which compile to
`color-mix(in oklab, …, transparent)`. Prefer these over ad-hoc `rgba(0,0,0,.08)`.

### 1.3 Brand ramp (`H=240`, one knob to re-skin)

`L` on the canonical ramp, `C` bell-curve peaking at 600 (the primary fill). Kept under the P3
ceiling.

```css
--brand-50:  oklch(0.971 0.014 240);
--brand-100: oklch(0.936 0.032 240);
--brand-200: oklch(0.885 0.061 240);
--brand-300: oklch(0.808 0.091 240);
--brand-400: oklch(0.704 0.140 240);
--brand-500: oklch(0.637 0.170 240);  /* accent / solid rest */
--brand-600: oklch(0.573 0.180 240);  /* chroma peak → accent, large/bold text (3:1) */
--brand-700: oklch(0.505 0.155 240);  /* PRIMARY button fill (clears AA 4.5:1 on white) / solid hover */
--brand-800: oklch(0.444 0.125 240);
--brand-900: oklch(0.396 0.100 240);
--brand-950: oklch(0.258 0.065 240);
```
Brand solid **with white text on it = 700** (`L ≤ ~0.545` clears AA 4.5:1 for 14px labels); 500/600
are for accents, borders, and large/bold text only (3:1). Hover = one step darker; subtle container =
**50/100**; brand text on neutral bg = **700** (light) / **300–400** (dark). The same "≤0.545 fill for
white text" rule applies to success/info solids — hence the darkened semantic values above. Keep brand in the **10% lane** (60-30-10 rule):
buttons, active states, links, focus rings — never flood 60% of the UI with saturated brand.

### 1.4 Semantic hue ramps (success / warning / error / info)

Conventional, color-blind-distinguishable hues (always pair color with icon/label — never hue alone):
**success** green `H≈150`, **warning** amber `H≈85`, **error** red `H≈27`, **info** blue `H≈255`.
Each ships the same slot structure; the used steps:

```css
/* SUCCESS — green H150 (white on-text) */
--success-100: oklch(0.950 0.040 150);   /* subtle bg   */
--success-300: oklch(0.830 0.110 150);   /* border      */
--success-500: oklch(0.723 0.190 150);   /* solid       */
--success-600: oklch(0.627 0.170 150);   /* solid hover */
--success-700: oklch(0.520 0.130 150);   /* text on neutral */

/* WARNING — amber H85 (⚠ DARK on-text — the exception) */
--warning-100: oklch(0.965 0.050 85);
--warning-300: oklch(0.880 0.120 85);
--warning-500: oklch(0.850 0.160 85);    /* solid — light fill  */
--warning-600: oklch(0.760 0.150 85);
--warning-700: oklch(0.560 0.110 70);    /* text on neutral */

/* ERROR / DANGER — red H27 (white on-text) */
--error-100: oklch(0.945 0.030 27);
--error-300: oklch(0.808 0.110 25);
--error-500: oklch(0.637 0.237 27);
--error-600: oklch(0.577 0.245 27);      /* == shadcn --destructive */
--error-700: oklch(0.505 0.213 27);

/* INFO — blue H255 (white on-text) */
--info-100: oklch(0.932 0.032 255);
--info-300: oklch(0.809 0.114 256);
--info-500: oklch(0.623 0.214 259);
--info-600: oklch(0.546 0.215 262);
--info-700: oklch(0.488 0.190 262);
```

**On-color rule (bake it into the token, never leave it to component authors):**
switch on-text from black→white when the fill's **`L` drops below ~0.60–0.65**. So error/success/info
solids (`L 0.57–0.72` but higher chroma darker perceived) take **white**; **warning/amber takes DARK
text** because its fill is light (`L 0.85`). This is the "warning trap" — in Radix the full dark-text
set is **sky, mint, lime, yellow, amber**; any bright high-`L` step-9 fill needs dark on-text.
Quantitative law (Material HCT / Carbon): on a 0–100 tone axis, **Δtone ≥ 40 ⇒ WCAG 3:1**,
**Δtone ≥ 50 ⇒ 4.5:1** (≈ ΔL 0.40 / 0.50 in OKLCH) — use it to auto-place on-text and borders.

### 1.5 Chart / data-viz palette (do NOT reuse semantic hues for categories)

A separate sub-system. Categorical hues ≥30° apart, capped at 5–6, equal perceptual weight.
Below is shadcn's chart palette, lightly chroma-balanced so no series dominates. For strict
color-blind safety, swap in the Okabe–Ito 8-color set (orange/sky-blue/bluish-green/yellow/blue/
vermillion/reddish-purple) mapped to OKLCH. Always double-encode with shape/label.

```css
--chart-1: oklch(0.646 0.222 41);    /* orange   */
--chart-2: oklch(0.600 0.118 185);   /* teal     */
--chart-3: oklch(0.398 0.130 250);   /* deep blue*/
--chart-4: oklch(0.828 0.189 84);    /* gold     */
--chart-5: oklch(0.640 0.245 16);    /* red      */
```
Sequential = single-hue monotonic `L` (or viridis); diverging = blue↔red through a light neutral.

---

## 2. Surfaces & elevation (tone-based, both modes)

Elevation is expressed by **surface tone**, not just shadow. Light mode: higher = *slightly darker/
more contained*. **Dark mode: higher = LIGHTER surface** (light comes from above) — never darker-than-
canvas or big black shadows. **Light `L`** = Material 3's verified tonal ladder; **Dark `L`** = aligned
to this system's neutral base so surfaces equal `--background` / `--card` / etc. (both obey M3's rule:
higher = lighter in dark). M3's own dark tones sit lower (6/10/12/17/22) if you want a darker feel:

| Role | Light `L` | Dark `L` | Use |
|---|---|---|---|
| `surface-dim` | 0.87 | 0.06 | dimmest canvas |
| `surface` (canvas) | 0.98–1.0 | 0.145 | page background |
| `surface-container-low` | 0.96 | 0.205 | non-interactive cards |
| `surface-container` | 0.94 | 0.24 | default component container |
| `surface-container-high` | 0.92 | 0.28 | modal sheet / high-emphasis |
| `surface-container-highest` | 0.90 | 0.32 | dialogs, drawers, menus |

> Note: the shipped scaffold (§3) and `assets/theme.css` use a tighter 3-step container ladder —
> light `0.985 / 0.970 / 0.955`, dark `0.240 / 0.280 / 0.320` for `surface-container[-high|-highest]`.
> The fuller M3 ladder in the table above is available if you need more elevation levels.

Dark base = **never `#000`** — use `oklch(0.145 0.006 240)` (≈`#121212`, tinted). Steps of ~+3–4% `L`
read as clean, distinct elevation; overlay lightening caps out ~16% (`L ≈ 0.32`) before "gray" stops
reading as a surface. Name surfaces by **role** (`surface.raised`, `surface.overlay`) so components
self-place across modes.

---

## 3. Semantic layer (shadcn vocabulary, extended) + full `@theme` scaffold

Adopt shadcn/ui's battle-tested semantic set verbatim, extended with `success/warning/info` and the
surface-elevation roles. **Every surface ships a `-foreground` pair**: the base token is the surface
color, `-foreground` is the text/icon color that sits on it — guarantees a legible pair in both modes
and makes automatic WCAG checking trivial.

```css
@import "tailwindcss";
@custom-variant dark (&:is(.dark *));

:root {
  /* --- radius / spacing / tracking bases (scales derived in @theme) --- */
  --radius: 0.625rem;                 /* 10px base; personality dial, see §6 */

  /* --- core surfaces --- */
  --background: oklch(1 0 0);            --foreground: oklch(0.205 0.006 240);
  --card: oklch(1 0 0);                  --card-foreground: oklch(0.205 0.006 240);
  --popover: oklch(1 0 0);              --popover-foreground: oklch(0.205 0.006 240);
  --muted: oklch(0.970 0.003 240);      --muted-foreground: oklch(0.54 0.010 240); /* AA 4.5:1 even on bg-muted */

  /* --- brand / actions --- */
  --primary: oklch(0.53 0.17 240);      --primary-foreground: oklch(0.985 0.002 240); /* darkened from brand-600 → clears AA 4.5:1 for white 14px labels */
  --secondary: oklch(0.970 0.003 240);  --secondary-foreground: oklch(0.269 0.007 240);
  --accent: oklch(0.936 0.032 240);     --accent-foreground: oklch(0.396 0.100 240);

  /* --- semantic feedback (base = solid, -foreground = on-color) --- */
  --success: oklch(0.53 0.15 150);      --success-foreground: oklch(0.985 0 0); /* darkened → AA 4.5:1 on white */
  --warning: oklch(0.850 0.160 85);     --warning-foreground: oklch(0.280 0.070 70); /* DARK */
  --destructive: oklch(0.577 0.245 27); --destructive-foreground: oklch(0.985 0 0);
  --info: oklch(0.55 0.19 259);         --info-foreground: oklch(0.985 0 0); /* darkened → AA 4.5:1 on white */

  /* --- lines --- */
  --border: oklch(0.922 0.004 240);     --input: oklch(0.922 0.004 240);
  --ring: oklch(0.53 0.17 240);         /* focus ring = brand; must hit 3:1 vs adjacent */

  /* --- elevation surfaces (tone-based) --- */
  --surface-container:        oklch(0.985 0.002 240);
  --surface-container-high:   oklch(0.970 0.003 240);
  --surface-container-highest:oklch(0.955 0.004 240);

  /* --- charts --- */
  --chart-1: oklch(0.646 0.222 41);  --chart-2: oklch(0.600 0.118 185);
  --chart-3: oklch(0.398 0.130 250); --chart-4: oklch(0.828 0.189 84);
  --chart-5: oklch(0.640 0.245 16);
}

.dark {
  --background: oklch(0.145 0.006 240);  --foreground: oklch(0.985 0.002 240);
  --card: oklch(0.205 0.006 240);        --card-foreground: oklch(0.985 0.002 240);
  --popover: oklch(0.205 0.006 240);    --popover-foreground: oklch(0.985 0.002 240);
  --muted: oklch(0.269 0.007 240);       --muted-foreground: oklch(0.708 0.007 240);

  /* brand LIGHTENS + DESATURATES in dark (same hue): +L, -C */
  --primary: oklch(0.704 0.140 240);     --primary-foreground: oklch(0.205 0.006 240);
  --secondary: oklch(0.269 0.007 240);   --secondary-foreground: oklch(0.985 0.002 240);
  --accent: oklch(0.320 0.070 240);      --accent-foreground: oklch(0.985 0.002 240);

  --success: oklch(0.723 0.150 150);     --success-foreground: oklch(0.205 0.006 240);
  --warning: oklch(0.860 0.140 85);      --warning-foreground: oklch(0.280 0.070 70);
  --destructive: oklch(0.704 0.191 22);  --destructive-foreground: oklch(0.205 0.006 240);
  --info: oklch(0.715 0.150 255);        --info-foreground: oklch(0.205 0.006 240);

  /* translucent-white lines on dark — softer than solid gray (steal this) */
  --border: oklch(1 0 0 / 10%);          --input: oklch(1 0 0 / 15%);
  --ring: oklch(0.556 0.008 240);

  --surface-container:        oklch(0.240 0.007 240);
  --surface-container-high:   oklch(0.280 0.007 240);
  --surface-container-highest:oklch(0.320 0.008 240);

  --chart-1: oklch(0.488 0.243 264); --chart-2: oklch(0.696 0.170 162);
  --chart-3: oklch(0.769 0.188 70);  --chart-4: oklch(0.627 0.265 304);
  --chart-5: oklch(0.645 0.246 16);
}

@theme inline {
  --color-background: var(--background);       --color-foreground: var(--foreground);
  --color-card: var(--card);                   --color-card-foreground: var(--card-foreground);
  --color-popover: var(--popover);             --color-popover-foreground: var(--popover-foreground);
  --color-primary: var(--primary);             --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);         --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);                 --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);               --color-accent-foreground: var(--accent-foreground);
  --color-success: var(--success);             --color-success-foreground: var(--success-foreground);
  --color-warning: var(--warning);             --color-warning-foreground: var(--warning-foreground);
  --color-destructive: var(--destructive);     --color-destructive-foreground: var(--destructive-foreground);
  --color-info: var(--info);                   --color-info-foreground: var(--info-foreground);
  --color-border: var(--border);               --color-input: var(--input);  --color-ring: var(--ring);
  --color-surface-container: var(--surface-container);
  --color-surface-container-high: var(--surface-container-high);
  --color-surface-container-highest: var(--surface-container-highest);
  --color-chart-1: var(--chart-1); --color-chart-2: var(--chart-2); --color-chart-3: var(--chart-3);
  --color-chart-4: var(--chart-4); --color-chart-5: var(--chart-5);

  /* radius scale derived from ONE base token (shadcn canonical) */
  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
}

@layer base {
  * { @apply border-border outline-ring/50; }
  body { @apply bg-background text-foreground; }
}
```

**Add a new semantic token = exactly 3 edits:** add to `:root`, add to `.dark`, add one line to
`@theme inline` (`--color-x: var(--x)`) → `bg-x text-x-foreground` now exists. Never half-wire it.

**Dark-mode accent rule applied above:** same hue, **+L −C** (`brand-600 → brand-400`-ish); desaturate
~15–20% relative (drop `C` ~0.02–0.05, raise `L` one ramp step). Flip on-text (dark text on the lighter
dark-mode primary). Ration saturated color to small elements. Text tiers on dark are best done as white
alpha (`87% / 60% / 38%`) so they re-composite over any elevated surface.

---

## 4. Typography scale

**Ratio by product type** (encode as a switch, not a fixed default):
`1.125–1.2` dashboards/dense apps · `1.25–1.333` content sites · `1.5+` marketing/landing.
Base body **16px minimum** on the web (never below for primary body). **Line-height shrinks as size
grows.** Sizes/line-heights track Tailwind v4's proven scale:

```css
@theme {
  --text-xs:   0.75rem;   --text-xs--line-height:   1.333;  /* 12/16 — captions, meta */
  --text-sm:   0.875rem;  --text-sm--line-height:   1.429;  /* 14/20 — labels, UI     */
  --text-base: 1rem;      --text-base--line-height: 1.5;    /* 16/24 — body           */
  --text-lg:   1.125rem;  --text-lg--line-height:   1.556;  /* 18/28 — lead body      */
  --text-xl:   1.25rem;   --text-xl--line-height:   1.4;    /* 20/28 — h4             */
  --text-2xl:  1.5rem;    --text-2xl--line-height:  1.333;  /* 24/32 — h3             */
  --text-3xl:  1.875rem;  --text-3xl--line-height:  1.2;    /* 30/36 — h2             */
  --text-4xl:  2.25rem;   --text-4xl--line-height:  1.111;  /* 36/40 — h1             */
  --text-5xl:  3rem;      --text-5xl--line-height:  1;      /* 48    — display        */
  --text-6xl:  3.75rem;   --text-6xl--line-height:  1;      /* 60    — hero           */

  --font-weight-normal:   400;   /* body */
  --font-weight-medium:   500;   /* UI labels, emphasis */
  --font-weight-semibold: 600;   /* headings */
  --font-weight-bold:     700;   /* strong headings */
}
```

**Weights:** differentiate hierarchy with **weight + color + space**, not size alone (essential in
low-ratio dense UI). Product default: body `400`, headings `600–700`. For expressive/marketing, use
**weight extremes (200 vs 800), not 400 vs 600**, and **size jumps of 3×**, not 1.5× (anti-slop).

**Tracking (letter-spacing) — tighten as size grows, loosen as size shrinks.** Ship the Inter
Dynamic-Metrics curve (`tracking ≈ -0.0223 + 0.185·e^(-0.1745·px)`; works for any neo-grotesque):

```css
@theme {
  --tracking-tight:  -0.022em;  /* ≥40px display / hero headings */
  --tracking-snug:   -0.014em;  /* 18–24px subheads */
  --tracking-normal: -0.011em;  /* 16px body */
  --tracking-wide:    0em;      /* 12–13px small */
  --tracking-caps:    0.06em;   /* uppercase eyebrows/overlines (POSITIVE, +0.04–0.1em) */
}
```
Rule: **never** let display-level negative tracking (`−0.02em`+) leak onto body/small text (the #1
amateur tell) — the small `−0.011em` on 16px body above is Inter's own optical metric, not a violation;
keep 12–13px small text at `0`. Uppercase labels get **positive** tracking. Large display headings get
`-0.02–0.03em` — one of the biggest "premium" tells.

**Numerics:** emit `font-variant-numeric: tabular-nums` on every metric, counter, and data-table
numeric cell (kills digit "jump" / misalignment); add `slashed-zero` for code/IDs. **Measure:**
`max-width: 65ch` on prose wrappers (target 45–75ch, ~66 ideal) — scales with zoom, satisfies WCAG 1.4.4.

**Fonts (brand-adaptive, anti-slop):** do **not** default to `Inter / Roboto / Arial / system` or the
escape-hatch clichés (`Space Grotesk`, `Geist`, `Instrument Serif` italic accent word). Pick a
distinctive pairing per brand — high contrast reads as interesting (display + mono, serif + geometric
sans). Expose `--font-sans / --font-serif / --font-mono` as tokens; keep the scale above font-agnostic.

---

## 5. Spacing rhythm (4/8pt)

**8pt grid with a 4pt half-step; everything is a multiple of 4.** Tailwind v4's single-variable model:
`--spacing: 0.25rem` (4px) and every utility is `calc(var(--spacing) * n)`, so any integer works
(`p-4`=16px, `w-17`, `gap-2`). Canonical ramp (Carbon/Tailwind/Atlassian all resolve to these exact px):

```
0 · 2 · 4 · 8 · 12 · 16 · 24 · 32 · 40 · 48 · 64 · 80 · 96   (+ 128 / 160 for heroes)
```
Deliberately **skip 56/72/112** so nobody picks near-identical large gaps (≈1.5× steps at the top).
The scale is **breakpoint-invariant** — don't rescale tokens per breakpoint; change *which* token +
column count/margins.

**Semantic spacing families** (retheme density without touching components):
`space.inset.*` (padding inside a container) · `space.stack.*` (vertical gap) · `space.inline.*`
(horizontal gap). Component defaults: input/button vertical padding **8–12**, card inset **16–24**,
section vertical gap **48–96**.

**Highest-leverage rule — `internal ≤ external`:** the gap *around* an element must be ≥ the padding
*within* it (card padding ≤ inter-card gap), or groups blur together. **Min tap target 44×44pt.**
Grid: 12 columns; margins 16 (mobile) → 24 (tablet+); gutters 16–24.

---

## 6. Radius scale

**Derive the whole scale from ONE `--radius` base** (change one number → re-skin all corners). shadcn
canonical derivation (subtractive) — the `sm`–`xl` steps are already in the `@theme inline` block above;
extend with `2xl`/`full`:

```
--radius-sm: calc(var(--radius) - 4px);   /* chips, small buttons, tooltips */
--radius-md: calc(var(--radius) - 2px);   /* inputs, standard buttons       */
--radius-lg: var(--radius);               /* cards, base                    */
--radius-xl: calc(var(--radius) + 4px);   /* modals, dialogs, popovers      */
--radius-2xl: calc(var(--radius) + 14px); /* large containers, sheets       */
--radius-full: 9999px;                    /* pills, avatars, status dots     */
```

Default token values (Tailwind/M3/Fluent consensus): `xs 2 · sm 4 · md 8 · lg 12 · xl 16 · 2xl 24 ·
full 9999`. **Base default `10px` (0.625rem)** for general SaaS. **Personality dial** = set the base:
`0px` serious/technical (finance, data, enterprise) · `4px` neutral/pro (B2B SaaS) · `8–12px` friendly
(default consumer SaaS) · `16px+` playful (wellness, social).

**Nested-radius rule (removes a top AI-generated tell):** a padded child must NOT share its parent's
radius. `inner = outer − padding`, clamped to 0 (`max(0px, calc(var(--radius) - var(--pad)))`). Map
radius to the element's **shortest side**, not to component type; elements <32px shortest side drop to
2px. Same radius on all 4 corners; don't round where elements meet a container edge; reserve `xl/2xl`
for big surfaces only; tables/dense data = `0`. Optional premium: `corner-shape: squircle` for hero
surfaces/icons behind `@supports`.

---

## 7. Shadow / elevation scale

**Rules:** never a single-layer shadow above "resting" (2–5 stacked layers, offset & blur ≈double per
layer). One light source (vertical offset ≈2× horizontal, or x=0). As elevation rises: `offset↑, blur↑,
opacity↓`. **Tint the shadow toward the surface hue, not pure black.** Fold a 1px ring into the shadow
token (Radix pattern) so border+shadow read as one system, never two competing effects. Cap at **6
role-named levels**; small controls (badges, chips, inputs) get **no** shadow. Ban `rgba(0,0,0,0.1)` on
everything and colored dark-mode "glows" (both documented slop tells).

Six role-named levels (Tailwind v4 scale, hue-tinted, ring-fused). Alpha-on-neutral, first layer = hairline ring:

```css
@theme {
  /* role-named elevation — light mode */
  --shadow-xs:  0 0 0 1px oklch(0.145 0.006 240 / 0.04),
                0 1px 2px 0 oklch(0.145 0.006 240 / 0.06);              /* resting cards, inputs */
  --shadow-sm:  0 0 0 1px oklch(0.145 0.006 240 / 0.04),
                0 1px 3px 0 oklch(0.145 0.006 240 / 0.10),
                0 1px 2px -1px oklch(0.145 0.006 240 / 0.10);           /* cards */
  --shadow-md:  0 0 0 1px oklch(0.145 0.006 240 / 0.04),
                0 4px 6px -1px oklch(0.145 0.006 240 / 0.10),
                0 2px 4px -2px oklch(0.145 0.006 240 / 0.10);           /* dropdowns, selects */
  --shadow-lg:  0 0 0 1px oklch(0.145 0.006 240 / 0.04),
                0 10px 15px -3px oklch(0.145 0.006 240 / 0.10),
                0 4px 6px -4px oklch(0.145 0.006 240 / 0.10);           /* popovers, menus, tooltips */
  --shadow-xl:  0 0 0 1px oklch(0.145 0.006 240 / 0.04),
                0 20px 25px -5px oklch(0.145 0.006 240 / 0.10),
                0 8px 10px -6px oklch(0.145 0.006 240 / 0.10);          /* modals, command palette */
  --shadow-2xl: 0 25px 50px -12px oklch(0.145 0.006 240 / 0.25);       /* full dialogs (+ scrim) */
}
```
Note the **negative spread** on far layers (`-3px … -12px`) keeps big shadows tight (Tailwind pattern).
Role map: `xs`=resting → `sm`=card → `md`=dropdown → `lg`=popover → `xl`=modal → `2xl`=dialog. One
shadow per role, everywhere (uniform-by-role = system; uniform-everywhere = slop).

**Dark mode:** switch the primary depth cue to **lighter surface** (§2), keep shadows subtle, reserve
real (deeper, larger) shadows for the top 1–2 levels only, and add a faint top light-catch:
`inset 0 1px 0 oklch(1 0 0 / 0.06)`. **Never animate a multi-layer shadow** — animate
`transform: translateY(-2px)` and cross-fade to the next elevation token instead.

---

## 8. Motion tokens (durations + easing)

**Two-curve vocabulary covers ~90%** (a small vocabulary = a coherent motion language). Plus `linear`
for constant motion and a standard curve for on-screen morphs. **Default everything to `ease-out`;
ban `ease-in` for UI** (sluggish start).

```css
@theme {
  /* easing → generates ease-* utilities */
  --ease-out-quint: cubic-bezier(0.23, 1, 0.32, 1);   /* entrances, reveals, content        */
  --ease-ios:       cubic-bezier(0.32, 0.72, 0, 1);   /* micro-interactions, dropdowns, sheets */
  --ease-standard:  cubic-bezier(0.2, 0, 0, 1);       /* M3 standard — on-screen move/morph  */
  --ease-out:       cubic-bezier(0, 0, 0.58, 1);      /* generic default                     */
  /* linear is built-in — spinners, progress, marquees */
}

:root {
  /* durations (kept as vars; use via duration-[var(--duration-fast)] or transitions) */
  --duration-instant: 100ms;  /* button press feedback (100–160ms) */
  --duration-fast:    150ms;  /* tooltips, small popovers          */
  --duration-base:    200ms;  /* dropdowns, selects, hovers        */
  --duration-slow:    300ms;  /* HARD CAP for interactive UI       */
  --duration-slower:  500ms;  /* modals, drawers, large surfaces   */
}
```
Duration law: **larger travel / larger surface → longer duration**; interactive UI **< 300ms**
(perceived-instant ≈180ms); never one fixed duration for everything. M3 full ladder available if a
"system" feel is wanted (short 50/100/150/200 · medium 250/300/350/400 · long 450–600 · x-long 700–1000).

**Craft rules to enforce:** only animate `transform` + `opacity` (composite-only, 60fps) — never
`width/height/top/left/margin`. Entrances start from `scale(0.95–0.98)` + `opacity 0` — **never
`scale(0)`**. Popovers/dropdowns set `transform-origin` to the trigger side (default `center` is a
smell); modals stay centered. **Frequency gate:** actions firing 100+×/day (keyboard, command menu) get
**no animation**. Springs for interactive/gesture (preserve velocity on interrupt), tweens for one-shot;
use `visualDuration + bounce` (bounce **0.1–0.3**, never higher for UI). Disable all transitions during
theme switch.

**Reduced motion (required, not optional) — reduce (cross-fade), don't delete:**
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important; animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important; scroll-behavior: auto !important;
  }
}
```
Then opt specific comprehension-aiding fades back in per component. View Transitions do **not**
auto-respect it — call `transition.skipTransition()` when the media query matches.

---

## 9. Delivery checklist (what "done" looks like)

- All color output in `oklch(L C H)`; `C ≤ 0.37`; neutrals `C ≈ 0.002–0.01` tinted to brand `H`.
- 3-tier chain intact: components reference **semantic** tokens only (`bg-primary`, `text-muted-foreground`),
  never raw ramps or hex. Dark mode = re-pointed semantics via `.dark`, zero per-element `dark:` colors.
- Every colored surface has a `-foreground` pair; verify contrast on **both** (WCAG AA: 4.5:1 body /
  3:1 large+UI; APCA Lc 90 body / 75 large-body / 60 non-body to tune perceived quality). Focus rings
  hit 3:1 vs adjacent.
- Warning takes dark on-text; everything else white (per the on-color `L<0.6` rule).
- Scales derived from single bases: `--radius` → radius scale, `--spacing` → all spacing, shadow
  primitives → elevation scale, `--tracking-normal` → tracking scale.
- No slop defaults: not unmodified `#6366F1`/purple gradients, not `rgba(0,0,0,0.1)` everywhere, not
  uniform `16px` radius, not Inter/Roboto/system as the font default, no `ease-in`, no `scale(0)`.
- `@theme inline` used for every runtime-swappable var; `prefers-reduced-motion` reset shipped.

---

## 10. Interaction states

Model every interactive element on **three non-colliding axes** so states stack without clashing:
**fill** = exclusive pointer state (rest/hover/press), **ring** = focus-visible, **border/indicator**
= selected. Derive hover/press/disabled from ONE on-color overlay instead of picking colors per
component — keep the overlay math in tokens (`--overlay-hover: 0.08; --overlay-press: 0.10`) so the
whole system tunes from one place.

| State | Recipe |
|---|---|
| rest | base token (`bg-primary`, `bg-card`, …) |
| hover | +8% on-color overlay — `color-mix(in oklab, var(--x) 92%, var(--foreground))` (or `bg-primary/90`) |
| active / pressed | +10–12% overlay + `translateY(0.5px)`; drop one elevation step |
| focus-visible | `outline: 2px solid var(--ring); outline-offset: 2px` — or shadcn pair `border-ring` + `ring-[3px] ring-ring/50` |
| disabled | content `opacity: 0.38`, fill `opacity: 0.12`, `pointer-events: none`, `box-shadow: none` |
| selected | `border`/indicator on the third axis — never reuse the hover fill |
| loading | preserve width (transparent label + absolutely-centered spinner), `aria-busy`, guard double-submit |
| error | `--destructive` border + text + `aria-invalid` — never color alone |

Ship rest / hover / active / focus-visible / disabled / loading on **every** control; add
selected / error / empty where relevant. Full application guidance: SKILL Phase 3 → "Full state matrix".
