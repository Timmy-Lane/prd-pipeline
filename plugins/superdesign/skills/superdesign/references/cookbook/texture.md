# Cookbook — Texture (the material layer)

The layer AI output always omits. A generated surface is flat because nothing in the default
distribution puts grain, halftone, paper or aberration on it — so shipping any of them is, on its
own, distance from the mean. This file is the parameter set for the `TEXTURE_LEVEL` dial
(→ `brand-to-system.md` → Design dials); every value below is copy-pasteable.

| `TEXTURE_LEVEL` | What ships | Recipes |
|---|---|---|
| **0** | flat | — |
| **1** | ONE faint technical texture | dot-grid · vertical rules · scanlines |
| **2** | grain overlay | film grain |
| **3** | grain + halftone/duotone imagery | halftone/riso · duotone · paper · chromatic aberration |

## Contents

- [When to use](#when-to-use) — `TEXTURE_LEVEL ≥ 1` set by the MOVEMENT, not chosen at markup time
- [When NOT to use](#when-not-to-use) — never stack two textures; never behind dense data
- [The performance law (applies to every recipe here)](#the-performance-law-applies-to-every-recipe-here) — fixed `pointer-events-none` overlay, never a scrolling container
- [Level 1 — one faint technical texture](#level-1--one-faint-technical-texture) — dot-grid, vertical rules, scanlines in pure CSS gradients
- [Level 2 — film grain](#level-2--film-grain) — the four `feTurbulence` parameters that decide film vs lava lamp
- [Level 3 — halftone, duotone, paper, aberration](#level-3--halftone-duotone-paper-aberration) — the imagery filters and their primitives
- [Blend modes — the craft map](#blend-modes--the-craft-map) — the three that are decisions; the rest are guesses
- [Faking bespoke assets in pure CSS/SVG — the buildable set](#faking-bespoke-assets-in-pure-csssvg--the-buildable-set) — asset → primitive → parameters
- [Accessibility](#accessibility) — contrast is measured on the composited result
- [Anti-slop](#anti-slop) — one texture per surface; turbulence where grain was meant

## When to use
- `TEXTURE_LEVEL ≥ 1` is set in the brief, by the MOVEMENT — not chosen at markup time.
- The surface has large empty regions that read as unfinished rather than composed.
- The movement names a material (Editorial → paper stock; Cyberpunk/CRT → scanlines; AI-dev-tool →
  one technical texture; Frutiger Aero → gloss).

## When NOT to use
- **Never stack two textures at the same level.** Dot-grid *or* rules *or* scan — one, once.
- Behind dense data (tables, KPI grids). Texture under numbers is noise under signal.
- On a scrolling container — see the performance law below.
- As a substitute for hierarchy. Grain on a flat layout is still a flat layout.

## The performance law (applies to every recipe here)

Texture lives on a **fixed, `pointer-events-none` overlay**, never on a scrolling container — a
filtered or blended element inside a scroller repaints continuously on the GPU. One overlay per
surface, `aria-hidden`, out of the tab order and out of the hit-testing path.

```css
.texture-overlay {
  position: fixed; inset: 0;
  pointer-events: none;
  z-index: 1;              /* above the canvas, below every control */
}
```

---

## Level 1 — one faint technical texture

Pure CSS gradients; no filter, no repaint cost. When `GRID_DISCIPLINE ≥ 2` the cadence must be a
whole multiple of the declared baseline unit, exactly like every other vertical rhythm value —
declare that unit as `--grid-track` on the surface and drive the rules off it.

```css
/* dot grid — the AI-dev-tool / blueprint default */
.tex-dots {
  background-image: radial-gradient(var(--color-border) 1px, transparent 1px);
  background-size: 22px 22px;
  opacity: .4;
}

/* vertical rules — hairlines on the grid tracks, never an arbitrary cadence */
.tex-rules {
  background-image: linear-gradient(to right, var(--color-border) 1px, transparent 1px);
  background-size: var(--grid-track, 22px) 100%;
  opacity: .4;
}

/* CRT scanlines — darken every 2nd row */
.tex-scan {
  background-image: repeating-linear-gradient(
    to bottom,
    oklch(0 0 0 / .25) 0 1px,     /* "weak" band: 20–30% darkness */
    transparent 1px 2px
  );
}
```

Scanline numbers come from retro-emulation shader documentation, **hobbyist tier and UNVERIFIED for
the CSS case**: darken every 2nd (or 3rd/4th) pixel row, "weak" ≈ **20–30%** darkness, "strong" ≈
**60–70%**; one cited preset runs scanline opacity **0.25** with phosphor persistence **0.12**.
Phosphor persistence is a decay curve, not a cutoff — some phosphors hold **20–30ms**. Transfer them
by analogy and say so in the brief.

---

## Level 2 — film grain

The whole recipe is one `feTurbulence`. Four parameters decide whether it reads as film or as a
lava lamp.

| Parameter | Value | Why |
|---|---|---|
| `type` | `fractalNoise` | **not** `turbulence` — `turbulence` gives a marbled cloud, `fractalNoise` gives film grain |
| `baseFrequency` | `0.65` | higher = finer grain; MDN's own example uses `0.05`, which is cloud/marble scale |
| `numOctaves` | `3` | MDN's example uses `2`; 3 is the grain value |
| `stitchTiles` | `stitch` | required, or the tile seams visibly |

**The shipping form** — a data-URI on a fixed overlay, so nothing filters at paint time:

```css
/* TEXTURE_LEVEL 2 — film grain. Fixed overlay only. */
.grain::after {
  content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 1;
  opacity: .035;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200'%3E%3Cfilter id='g'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23g)'/%3E%3C/svg%3E");
}
```

**The inline form**, when the grain must be tuned live or composited with a gradient:

```html
<svg aria-hidden="true" class="pointer-events-none fixed inset-0 -z-10 size-full opacity-[.035]"
     viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <filter id="grain">
    <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch"/>
  </filter>
  <rect width="100%" height="100%" filter="url(#grain)"/>
</svg>
```

```css
/* the pass that turns raw turbulence into visible grain */
.grain-svg { filter: contrast(170%) brightness(1000%); }
```

Two documented caveats: the contrast/brightness pass "forgoes a huge range of colors," and
performance is a stated concern in the recipe's own comment thread — which is why the overlay is
fixed and the opacity is `.035`, not `.15`.

**Cloud / marble** is the same primitive with the other settings — `type="turbulence"`,
`baseFrequency="0.05"`, `numOctaves="2"`. It is a different material, not a weaker grain.

---

## Level 3 — halftone, duotone, paper, aberration

### Halftone / riso posterise

`feComponentTransfer` with `type="discrete"` and an n-entry `tableValues` is an n-level posterise
per channel; `type="table"` interpolates between the entries instead. This is the primitive for
risograph banding.

```xml
<!-- 3-level posterise per channel -->
<feComponentTransfer>
  <feFuncR type="discrete" tableValues="0 0.5 1"/>
  <feFuncG type="discrete" tableValues="0 0.5 1"/>
  <feFuncB type="discrete" tableValues="0 0.5 1"/>
</feComponentTransfer>

<!-- channel remap: slope + intercept, for a printed-ink cast -->
<feFuncR type="linear" slope="0.5" intercept="0"/>
<feFuncG type="linear" slope="0.5" intercept="0.25"/>
<feFuncB type="linear" slope="0.5" intercept="0.5"/>
```

### Duotone

```xml
<!-- The two lines everyone omits -->
<filter id="duo" color-interpolation-filters="sRGB">   <!-- default is linearRGB = wrong midtones -->
  <feColorMatrix type="luminanceToAlpha"/>              <!-- NOT saturate="0" -->
  <feComponentTransfer>
    <feFuncR type="table" tableValues="0.06 0.98"/>
    <feFuncG type="table" tableValues="0.09 0.86"/>
    <feFuncB type="table" tableValues="0.18 0.42"/>
  </feComponentTransfer>
</filter>
```

```css
img.duotone { filter: url(#duo); }
```

Both omissions are the difference between a duotone that looks printed and one that looks like a
Photoshop mistake: **filter primitives operate in `linearRGB` by default**, and the first step of a
duotone is collapsing to luminance (`luminanceToAlpha`), not desaturating. The `tableValues` above
are **illustrative, not sourced** — they are the two colour stops; replace them with the brand's own
dark and light stop, in that order (first entry = shadow, last = highlight).

### Paper

Ink goes *into* paper with `multiply`, never `overlay`:

```css
.paper {
  background-color: var(--color-background);
  background-image: url("/textures/paper.avif");   /* or the fractalNoise grain above */
  background-blend-mode: multiply;
}
```

### Chromatic aberration

**No source in the corpus gives parameter values** — the recipe is assembled from primitives that
are sourced (`feColorMatrix` splits the channels, `feOffset` displaces them, `feBlend` recombines),
and the displacement below is a starting point, not a measured value.

```xml
<filter id="aberr" color-interpolation-filters="sRGB">
  <!-- red channel, displaced left -->
  <feColorMatrix type="matrix" in="SourceGraphic" result="r"
                 values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0"/>
  <feOffset in="r" dx="-1" dy="0" result="rOff"/>
  <!-- cyan remainder, displaced right -->
  <feColorMatrix type="matrix" in="SourceGraphic" result="gb"
                 values="0 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 1 0"/>
  <feOffset in="gb" dx="1" dy="0" result="gbOff"/>
  <feBlend in="rOff" in2="gbOff" mode="screen"/>
</filter>
```

Keep `dx` at ±1 on body-adjacent surfaces; anything larger reads as a rendering bug rather than a
lens, and it destroys text contrast.

---

## Blend modes — the craft map

`mix-blend-mode` accepts `normal | darken | multiply | color-burn | lighten | screen | color-dodge |
overlay | soft-light | hard-light | difference | exclusion | hue | saturation | color | luminosity`,
plus the compositing operator `plus-lighter`. Three of them are decisions; the rest are guesses:

| Mode | Use it for |
|---|---|
| `multiply` | ink into paper — the paper-texture move |
| `luminosity` | a texture's tonality without its colour (keeps the brand hue underneath) |
| `plus-lighter` | **two-layer cross-fades** — MDN: "prevents unwanted blinking when two overlaying elements animate their opacity in opposite directions". The one nobody uses. |

```css
/* cross-fade between two stacked layers without the mid-transition dip */
.crossfade > * { mix-blend-mode: plus-lighter; transition: opacity 200ms var(--ease-out-quint); }
```

Web Almanac 2022 (HTTP Archive) measured that around **18% of pages** use a custom property named
`var(--overlay-mix-blend-mode)` — "a specific name that must come from a library or tool of some
sort." Most blend-mode usage on the web is a library default, not a decision. Make yours a decision.

---

## Faking bespoke assets in pure CSS/SVG — the buildable set

| Asset | Primitive | Parameters |
|---|---|---|
| Film grain | `feTurbulence` | `fractalNoise`, `baseFrequency 0.65`, `numOctaves 3`, `stitchTiles stitch` + `contrast(170%) brightness(1000%)` |
| Cloud / marble | `feTurbulence` | `turbulence`, `baseFrequency 0.05`, `numOctaves 2` |
| Halftone / riso | `feComponentTransfer` | `feFunc* type="discrete"` with an n-entry `tableValues` |
| Duotone | `feColorMatrix` | `luminanceToAlpha` → two-stop remap; **must set `color-interpolation-filters: sRGB`** |
| Paper | texture image + `mix-blend-mode: multiply` | ink into paper |
| Chromatic aberration | `feColorMatrix` + `feOffset` + `feBlend` | values UNVERIFIED; recipe derivable |
| Blueprint seam-draw | SVG `stroke-dasharray` + animated `stroke-dashoffset` | the Warm-paper archetype's signature |
| Cross-fade without blink | `mix-blend-mode: plus-lighter` | MDN-stated purpose |

## Accessibility
- Contrast is measured on the **composited** result. A grain overlay at `.035` and a scanline
  overlay at `.25` both shift every text pair underneath them — re-run the contrast gate with the
  overlay on, not off.
- `aria-hidden="true"` and `pointer-events: none` on every overlay. Texture is never in the
  accessibility tree and never in the hit-testing path.
- **Never animate grain.** A moving overlay is animation and needs a `prefers-reduced-motion`
  branch; static grain needs none, which is one more reason to keep it static.
- Texture that carries meaning (a hatched "unavailable" cell) fails colour-alone — pair it with text.

## Anti-slop
- One texture per surface. Stacking dot-grid + grain + gloss is the single clearest tell that the
  material layer was decorated rather than decided.
- `type="turbulence"` where grain was meant. Marbled cloud at 3% opacity looks like a dirty screen.
- A duotone without `color-interpolation-filters="sRGB"`. The midtones are wrong and it reads as a
  filter, not a print.
- Grain on a scrolling container. It will be smooth in the screenshot and janky in the hand.
- Texture as the whole idea. If removing the overlay collapses the design, there was no design.
