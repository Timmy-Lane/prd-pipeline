# Performance Gate — Core Web Vitals as design craft

The performance numbers a generated product UI is judged on, and the design decisions that move them.
Every metric here is a **field** measurement at the **75th percentile** of page loads, so a lab run is
evidence, not proof. `accessibility.md` owns the conformance gate; this file owns the speed gate.

The load-bearing idea: most of these are **design** decisions wearing engineering clothes. A skeleton
that resizes when data lands is a CLS bug the designer authored. A distinctive display face with no
matched fallback metrics is a CLS bug the brand decision authored. Treat them here, not in a
post-hoc optimisation pass.

## Contents

- [1. The budgets](#1-the-budgets)
- [2. INP — what actually counts, and how to yield](#2-inp--what-actually-counts-and-how-to-yield)
- [3. CLS — a burst, not a total](#3-cls--a-burst-not-a-total)
- [4. LCP — where the 2.5 s goes](#4-lcp--where-the-25-s-goes)
- [5. Containment and `content-visibility`](#5-containment-and-content-visibility)
- [6. Fonts without CLS](#6-fonts-without-cls)
- [7. Images](#7-images)
- [8. What the stack costs](#8-what-the-stack-costs)
- [The gate — pre-ship checklist](#the-gate--pre-ship-checklist)
- [Sources (primary first)](#sources-primary-first)

---

## 1. The budgets

| Metric | Good | Poor | Measures |
|---|---|---|---|
| **LCP** Largest Contentful Paint | **≤ 2.5 s** | — | loading |
| **INP** Interaction to Next Paint | **≤ 200 ms** | **> 500 ms** | interactivity (200–500 ms = needs improvement) |
| **CLS** Cumulative Layout Shift | **≤ 0.1** | **> 0.25** | visual stability |

"Tools that assess Core Web Vitals compliance should consider a page passing if it meets the recommended
targets at the 75th percentile for all three." **FID is retired** — INP replaced it when it went stable
in 2024. Do not cite FID.

---

## 2. INP — what actually counts, and how to yield

**INP = input delay + processing duration + presentation delay.** Only three interaction types count:
**mouse click, touch tap, key press.** **Scroll, hover and zoom are excluded** — a janky scroll is a real
defect but it is not an INP defect, so do not defend a scroll effect by pointing at a green INP. INP
reports the *longest* interaction over the page lifetime, ignoring outliers.

**A long task is any task over 50 ms**; blocking time = duration − 50 ms. Break them up by yielding:

```js
function yieldToMain () {
  if (globalThis.scheduler?.yield) return scheduler.yield();   // Chrome/Edge 129+, Firefox 142+
  return new Promise(resolve => { setTimeout(resolve, 0); });  // after 5 nested calls: forced 5 ms floor
}

async function runJobs (jobQueue, deadline = 50) {
  let lastYield = performance.now();
  for (const job of jobQueue) {
    job();
    if (performance.now() - lastYield > deadline) { await yieldToMain(); lastYield = performance.now(); }
  }
}
```

`scheduler.yield()` gives "prioritized continuation" — the continuation of the current task runs *before*
any other similar task, which `setTimeout(…, 0)` does not. **`isInputPending()` is explicitly no longer
recommended**; do not generate it.

**INP cannot be measured in the lab.** Lighthouse reports TBT as a proxy. A real INP number needs field
data (CrUX, or the `web-vitals` library in RUM).

---

## 3. CLS — a burst, not a total

`layout shift score = impact fraction × distance fraction`. CLS is **the largest burst**, where a burst is
one or more shifts "in rapid succession with less than **1 second** in between each shift and a maximum of
**5 seconds** for the total window duration."

**Shifts within 500 ms of a user input are excluded** (`hadRecentInput`). That single rule is the design
consequence: **an accordion that expands on click costs nothing; the same expansion on data arrival costs
CLS.** Anything that changes size because a fetch resolved must have its box reserved first — skeletons
that match the arriving geometry, `min-height` or `aspect-ratio` on late-loading embeds and ads,
`width`+`height` on every image.

Animate with `translate`: "Composited animations using `translate` can't impact other elements, and so
don't count toward CLS." Never animate `top` / `left` / `box-shadow` / `box-sizing` for motion
(→ `motion.md`).

---

## 4. LCP — where the 2.5 s goes

Subpart budget: **TTFB ~40% · resource load delay <10% · resource load duration ~40% · element render
delay <10%.** These are "guidelines, not strict rules" — "if the LCP times on your pages are consistently
within 2.5 seconds, then it doesn't really matter what the relative proportions are." Use the split to
find *which* quarter is blown, not as a target in itself.

Two hard rules:
- `fetchpriority="high"` on the element you expect to be LCP (usually the hero `<img>`).
- **"Never lazy-load your LCP image, as that will always lead to unnecessary resource load delay."**
  `loading="lazy"` above the fold is a defect, not a saving.

---

## 5. Containment and `content-visibility`

The cheapest large win on a long page, and the one with the most non-obvious side effects.

```css
.section {
  content-visibility: auto;
  contain-intrinsic-size: auto 500px; /* `auto` remembers the last rendered size — key for infinite scroll */
}
```

Measured: web.dev's travel-blog demo went **232 ms → 30 ms initial render (7×)**; the article expects
"a reduction of 50% or more from rendering costs" on pages with substantial off-screen content. Baseline
since **September 2024**.

- `content-visibility: auto` applies **layout + style + paint** containment and skips rendering off-screen,
  but the content stays "accessible to user-agent features": find-in-page works, tab order works, it stays
  focusable, selectable, **and in the accessibility tree**. `hidden` behaves like `display: none` for those
  features. Two consequences: add `aria-hidden="true"` to off-screen **landmark** elements so they do not
  clutter the tree, and **never park a live region inside one** — it will still announce
  (→ `accessibility.md` §5).
- **Without `contain-intrinsic-size` the element is zero-height and the scrollbar jumps** — which is a CLS
  regression introduced by a performance fix.
- `contain: strict` = `size layout paint style`; `contain: content` = `layout paint style`.
  - `size` — the element sizes itself ignoring children, so it collapses to zero unless explicitly sized.
  - `layout` — internal layout isolated both ways.
  - `paint` — descendants cannot paint outside the border box; "acts like `overflow: hidden` for visual
    rendering", so it **clips `box-shadow` focus rings** (→ `accessibility.md` §2 — `outline` survives).
  - `style` — scopes CSS counters and quotes.
- **Every value except `none` creates a new containing block for `position: absolute`/`fixed`, a new
  stacking context, and a new block formatting context.** This is the hidden cost, and it is why a
  Tooltip or Popover inside a contained virtualised row starts anchoring to the row instead of the
  viewport and its `z-index` stops resolving where you expected.

---

## 6. Fonts without CLS

`font-display`, exactly:

| Value | Block period | Swap period |
|---|---|---|
| `block` | 2–3 s | infinite |
| `swap` | 0 ms | infinite |
| `fallback` | **100 ms** | **3 s** |
| `optional` | **100 ms** | none |

`optional` is the CLS-safe choice; `swap` is the FOUT-accepting choice. Pick deliberately per register —
a marketing hero can accept FOUT, a dense dashboard should not shift.

- **WOFF2 only** — "Use only WOFF2 and forget about everything else"; it "compresses 30% better than WOFF."
- **`preload` ignores `unicode-range`**, so preloading a subsetted family defeats the subsetting. Preload
  the one face that renders above the fold, subset it, and stop.
- Self-hosting only beats a third party if you have "a CDN and HTTP/2."
- **Match the fallback's metrics** with `size-adjust`, `ascent-override`, `descent-override`,
  `line-gap-override` so the fallback occupies the same box as the web font. Neither source publishes
  per-family override values — computing them per typeface is the craft step. (Next.js and `fontaine`
  are reported to automate this — *unverified*, do not generate a dependency on it.)

This is the price of the ban on Inter/Roboto/Open Sans/Lato as the display face
(→ `anti-slop.md`): **a distinctive face with no matched fallback metrics turns a brand-typography
decision into a CLS regression.** Ship the overrides in the same commit as the `@font-face`.

---

## 7. Images

```html
<!-- resolution switching: w descriptors + sizes -->
<img srcset="hero-480w.jpg 480w, hero-800w.jpg 800w"
     sizes="(width <= 600px) 480px, 800px"
     src="hero-800w.jpg" width="800" height="450" alt="…">

<!-- format switching + art direction -->
<picture>
  <source type="image/avif" srcset="hero.avif">
  <source type="image/webp" srcset="hero.webp">
  <source media="(width < 800px)" srcset="hero-portrait.jpg">
  <img src="hero.jpg" width="800" height="450" alt="…">
</picture>
```

- MDN's measured saving: the 480px version is **63 KB** against **128 KB** for the 800px one — 65 KB for a
  mobile user on a narrow screen. Density switching: 320px **39 KB** vs 640px **93 KB**.
- Selection order: viewport width → pixel density → zoom → first matching `sizes` condition → nearest
  `srcset` candidate. `sizes` is **not** used with `x` descriptors. A fallback `<img>` inside `<picture>`
  is required.
- **Always ship `width` and `height`** — the browser derives `aspect-ratio: auto W / H` and reserves the
  box before the bytes arrive. This is the single highest-yield CLS fix.
- Format order `avif` → `webp` → the raw fallback; art direction goes in `media`, not in `srcset`.

LQIP/blur-up placeholders and `sizes="auto"` are **unverified** in this corpus — no source was reachable.
Do not present either as a rule.

---

## 8. What the stack costs

**Tailwind v4 build times** (vendor's own benchmark — build-time, not runtime):

| Build | v3.4 | v4.0 |
|---|---|---|
| Full | 378 ms | **100 ms** |
| Incremental, new CSS | 44 ms | **5 ms** |
| Incremental, no new CSS | 35 ms | **192 µs** |

Tailwind's *runtime* cost is the shipped CSS byte count, which that benchmark does not measure —
**unverified**; do not quote a byte figure.

**Radix / shadcn dependency weight** (bundlephobia — secondary, not the vendor's own measurement):

| Package | Version | Min+gzip | Deps |
|---|---|---|---|
| `@radix-ui/react-dialog` | 1.1.23 | **12.6 KB** | 15 |
| `@radix-ui/react-select` | 2.3.7 | **29.4 KB** | 22 |
| `lucide-react` | 1.27.0 | **159 KB** (whole barrel) | 0 |

The reading: individual Radix primitives are cheap in bytes but arrive with 15–22 transitive packages
each, so a dozen primitives is a large module graph even at a modest byte cost. `lucide-react`'s 159 KB is
the **barrel** — it only ships if tree-shaking fails, but the thousands-of-modules dev graph is a real
cold-start cost either way. **Import icons by name and verify with a bundle analyser** rather than
trusting the tree-shakeable flag. Per-component runtime cost of shadcn patterns (re-render counts, `cva`
class-string cost, `cn()` merge cost) is **unverified** — no source measures it.

---

## The gate — pre-ship checklist

Automatable, in CI (assumes the app is served at `http://localhost:3000`):

| Check | Command | What it cannot catch |
|---|---|---|
| LCP / CLS / TBT / a11y score | `npx lhci autorun` with a `lighthouserc.js` carrying `{ ci: { assert: { preset: 'lighthouse:recommended' } } }` | **INP — not measurable in the lab.** TBT is the proxy; a real number needs CrUX or `web-vitals` RUM |
| Images without `width`/`height` | Lighthouse `unsized-images` | Next.js `<Image fill>` and CSS-sized images are false positives |
| Lazy-loaded LCP image | Lighthouse `lcp-lazy-loaded` | whether the *right* element is LCP on your real content |
| `font-display` missing | Lighthouse `font-display` | whether the fallback's metrics match (`size-adjust` and friends) |
| Render-blocking font `@import` | `grep -rn "@import.*fonts.googleapis.com" src/` | fonts loaded via a `<link>` in a framework head |

Human checks — no tool implements these:

- [ ] **Field INP**, not lab TBT, on the interactions this UI is actually built around.
- [ ] **Every fetch-driven size change has its box reserved** — skeleton geometry matches the arriving
      content, embeds carry `aspect-ratio`, images carry `width`+`height`.
- [ ] **The LCP element is identified deliberately**, has `fetchpriority="high"`, and is not lazy-loaded.
- [ ] **Fallback metrics are overridden** for every non-system face (`size-adjust` / `ascent-override` /
      `descent-override` / `line-gap-override`).
- [ ] **`content-visibility: auto` sections carry `contain-intrinsic-size`**, no live region sits inside
      one, and off-screen landmarks are `aria-hidden`.
- [ ] **No `box-shadow`-only focus ring inside a contained or virtualised subtree**
      (→ `accessibility.md` §2).
- [ ] **Icons imported by name**, verified in a bundle analyser rather than assumed.

---

## Sources (primary first)

- web.dev — Web Vitals (thresholds, 75th percentile): https://web.dev/articles/vitals
- web.dev — INP: https://web.dev/articles/inp
- web.dev — Optimize long tasks (`scheduler.yield`, the 50 ms rule): https://web.dev/articles/optimize-long-tasks
- web.dev — CLS (burst definition, `hadRecentInput`): https://web.dev/articles/cls
- web.dev — Optimize LCP (subpart budget, `fetchpriority`): https://web.dev/articles/optimize-lcp
- web.dev — Optimize CLS (`aspect-ratio`, fallback metric overrides): https://web.dev/articles/optimize-cls
- web.dev — Font best practices (`font-display` table, WOFF2, preload caveat): https://web.dev/articles/font-best-practices
- web.dev — content-visibility (232 ms → 30 ms): https://web.dev/articles/content-visibility
- MDN — Responsive images (`srcset`/`sizes`/`<picture>`, measured savings): https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Responsive_images
- MDN — contain: https://developer.mozilla.org/en-US/docs/Web/CSS/contain
- MDN — content-visibility: https://developer.mozilla.org/en-US/docs/Web/CSS/content-visibility
- Tailwind CSS — v4.0 announcement (build benchmark): https://tailwindcss.com/blog/tailwindcss-v4
- Bundlephobia (secondary — Radix and lucide weights): https://bundlephobia.com
