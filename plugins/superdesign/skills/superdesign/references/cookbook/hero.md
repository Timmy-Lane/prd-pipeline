# Marketing Hero Section

> Above-the-fold marketing hero for a landing page. React + Tailwind CSS v4 + shadcn/ui.
> The default here is a **split-with-screenshot** hero (copy left, product visual right)
> with exactly two CTAs ranked by hue and contrast, an optional news eyebrow, and a subtle
> single background accent. The trust strip lives *below* the hero, not inside it. Full
> light/dark + `prefers-reduced-motion` support. A **centered / background-effect** variant
> is included below.
>
> Every measured figure in this file was read off the live DOM of **13 leading software
> marketing sites at 1440×900 and 390×844 on 2026-07-26** (Linear, Vercel, Stripe, Raycast,
> Resend, Clerk, Cal.com, Liveblocks, Supabase, Framer, Cursor, trigger.dev, Arc). n=13, one
> observer, one date — strong signals at that n, but one snapshot of one tier.

## Contents

- [When to use it](#when-to-use-it) — the ~3–5 seconds a first-time, act-first visitor gives you
- [Anatomy](#anatomy) — vertical scan order mirrors the decision funnel, plus the headline formulas
- [Token-driven styling](#token-driven-styling) — custom-property routing and the hero's LCP budget
- [Variants](#variants) — split with screenshot (default) · background-effect centered
- [Interaction / state matrix](#interaction--state-matrix) — theme, motion, CTA and reduced-motion requirements
- [Responsive behavior](#responsive-behavior) — one breakpoint switch; copy-first on mobile
- [Accessibility notes](#accessibility-notes) — exactly one `<h1>`, contrast over accents, scrims
- [Anti-slop callout](#anti-slop-callout) — the few ways heroes fail, all of them loud
- [Complete example (copy-pasteable)](#complete-example-copy-pasteable) — the full split hero with both CTAs ranked

---

## When to use it

Use a hero when a **first-time, act-first visitor** lands on a marketing/landing page and
you have ~3–5 seconds to answer *what is it → who is it for → why care → what do I do next*.

Reach for it when:

- You're building a **landing / product / launch / pricing** page top section.
- You want to pair a **value-prop headline** with a **single dominant action**.
- You can *show* the product (screenshot, clip, live snippet), not just describe it.

Do **not** use a hero when:

- The surface is a **returning-user app/dashboard** — those users want to work, not be sold to.
- The product is **browse-first** (ecommerce grid, news feed, search) — lead with content.
- You'd be forced into a **carousel/slider** to fit multiple messages (see anti-slop).

Default variant picker:

| If you want to… | Use |
|---|---|
| Balance message + product proof (most SaaS) | **Split with screenshot** (default below) |
| Let the copy *be* the product (dev tools, launches) | **Simple centered** |
| Show a polished UI without splitting attention | **Centered + screenshot below** |
| Add one "wow" accent (AI / dev products) | **Background-effect centered** (variant B) |
| Capture a lead inline (waitlist, PLG) | **Split with form** |

---

## Anatomy

Vertical scan order mirrors the decision funnel. Render in this order; hide the optional
parts rather than reordering.

```
┌─ <section> relative isolate overflow-hidden ──────────────────────────────┐
│  [ background accent ]  aria-hidden, -z-10, low opacity, motion-gated      │
│                                                                            │
│  ┌─ container: mx-auto max-w-7xl px-6 lg:px-8 py-24 sm:py-32 lg:py-40 ──┐  │
│  │  ┌─ copy column (max-w-2xl) ───────┐   ┌─ visual column ──────────┐  │  │
│  │  │ 1. Eyebrow / announcement badge │   │ 6. Hero visual           │  │  │
│  │  │ 2. Headline  ← the only <h1>    │   │    aspect-locked, LCP     │  │  │
│  │  │ 3. Subheadline (muted)          │   │    bordered + shadow      │  │  │
│  │  │ 4. CTA group — exactly 2, or 0 │   │                          │  │  │
│  │  │ 5. Trust strip → next section  │   │                          │  │  │
│  │  └─────────────────────────────────┘   └──────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

| # | Part | Rules |
|---|---|---|
| 1 | **Eyebrow / badge** *(optional)* | Present on **6 of 13**, and in every case it carries **news**: a version launch ("Cal.com launches v6.7", "NEW v4.5.0: AI Agents are GA"), a funding round ("Clerk raises $50m Series C — Learn more"), an event ("Join us at Resend Forward"), a content drop, or a live statistic ("Global GDP running on Stripe: 1.687444…%"). **Never a category label.** 12–16px; half are links. If you have no news, omit it — an eyebrow that says "PLATFORM" is filler. |
| 2 | **Headline** | Exactly one `<h1>`, real text (never baked into an image). **6–9 words** (median 7; 10 of 13 in band). **64px at ≥1440** — the mode, hit exactly by Linear, Vercel, Raycast, Clerk, Cal.com and Liveblocks. `leading-none` (median 1.0; 12 of 13 ≤ 1.15). `tracking-tight` (−0.025em; median −0.02em, 9 of 13 negative, **0 positive**). Must wrap to **exactly two lines** at 1440 — `text-balance` is how you guarantee it (11 of 13 are 2 lines). **Never `uppercase`** (0 of 13). **Never gradient-filled** unless it is the brand's single idea (1 of 13). At 390 the headline is **0.5–0.75×** desktop, median 0.67. |
| 3 | **Subheadline** | Who it's for + one tangible benefit. **Median 23 words**, range 11–32; keep ≤ ~25. `text-muted-foreground`, `text-pretty`. |
| 4 | **CTA group** | **Exactly two, or zero. Never one, never three.** 12 of 13 ship exactly 2; Linear ships 0 and delegates conversion to the persistent nav. Rank by **hue and contrast**, not necessarily fill-vs-outline — 6 of the 12 render *both* buttons filled in different colours (Arc, Clerk, Cursor, Raycast, Stripe, Vercel). Two equally-filled CTAs are correct only for genuinely parallel choices (Arc: Mac / Windows). Minimum height **44px at 390**. |
| 5 | **Trust strip** *(optional)* | **Not inside the hero.** Only Stripe and Vercel put marks in the hero box; everyone else's first strip sits at **0.4–1.8 screens** down, median **0.9** — the first reward for the first scroll. Keep the hero ≤ **90vh** so the strip's top edge peeks above the fold (median hero height 87vh; only 3 of 13 exceed 100vh). Full colour, full opacity — see `marketing-sections.md` §2c. |
| 6 | **Hero visual** | Show *what changes for the user*. Aspect-locked to prevent CLS. Decorative → `alt=""`; meaningful → descriptive `alt`. |
| — | **Background accent** *(optional)* | Dot/line grid, gradient mesh, or aurora. `aria-hidden`, `-z-10`, low opacity, must not drop text below 4.5:1. |

### Headline formulas that ship

Verbatim from the live `<h1>` of the 13 measured sites:

| Formula | n | Examples |
|---|---|---|
| `The <category> for <audience>` | **4** | "The product development system for teams and agents" · "Realtime infrastructure for multiplayer apps and agents" · "Email for developers" · "Framer is the AI website builder for standout sites" |
| Bare noun phrase, no verb | 3 | "Agentic Infrastructure" · "Email for developers" |
| Outcome pair / antithesis | 2 | "Build in a weekend / Scale to millions" · "More than authentication, Complete User Management" |
| Imperative + object | 2 | "Build and deploy fully-managed AI agents and workflows" |
| Possessive promise | 1 | "Your shortcut to everything." |
| Customer quote as headline | 1 | "Arc is the Chrome replacement I've been waiting for." |
| Paragraph-as-display | 1 | Stripe's 22-word `<h1>` at 300 weight |

**6 of 13 contain no verb. 2 of 13 contain any superlative or intensifier.** There is no
"revolutionary", "seamless", "powerful", "cutting-edge" or "next-generation" anywhere in the set.

```tsx
<h1 className="text-4xl leading-none font-semibold tracking-tight text-balance sm:text-5xl lg:text-[4rem]">
```

---

## Token-driven styling

Everything routes through **CSS custom properties**, not hardcoded hex. shadcn already maps
its palette to tokens (`--background`, `--foreground`, `--muted-foreground`, `--border`,
`--ring`, `--primary`, …) consumed by utilities like `bg-background` / `text-foreground`.
The only new thing a hero needs is **one accent token** for the background layer so it
re-themes for free in dark mode.

`app/globals.css` (Tailwind v4 — note `@theme inline` and the `.dark` overrides):

```css
@import "tailwindcss";
@custom-variant dark (&:is(.dark *));

:root {
  /* shadcn base tokens (abridged — keep your generated set) */
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --border: oklch(0.922 0 0);
  --ring: oklch(0.708 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);

  /* hero accent — one token, themed. keep the grid near-subliminal. */
  --hero-grid: color-mix(in oklab, var(--foreground) 6%, transparent);
  --hero-grid-size: 32px;
  --hero-glow: color-mix(in oklab, var(--primary) 14%, transparent);
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --border: oklch(1 0 0 / 10%);
  --ring: oklch(0.556 0 0);
  --primary: oklch(0.985 0 0);
  --primary-foreground: oklch(0.205 0 0);

  --hero-grid: color-mix(in oklab, var(--foreground) 8%, transparent);
  --hero-glow: color-mix(in oklab, var(--primary) 10%, transparent);
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-muted-foreground: var(--muted-foreground);
  --color-border: var(--border);
  --color-ring: var(--ring);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
}
```

Rules:

- **No literal colors in TSX.** Use `bg-background`, `text-foreground`, `text-muted-foreground`,
  `border`, `ring-ring`, `bg-primary`. The background accent reads its color from
  `var(--hero-grid)` / `var(--hero-glow)` via arbitrary properties, so it flips with the theme.
- **Spacing is tokenized by Tailwind's scale** — stick to the researched rhythm
  (`py-24 sm:py-32 lg:py-40`, `mt-6` subhead, `mt-8`/`mt-10` CTA) rather than magic numbers.
- **Radius** rides `--radius` (`rounded-xl` on the visual, `rounded-full` on the badge).

### LCP budget for the hero

The hero *is* the LCP element, so it owns the page's Core Web Vitals. Target subparts
([web.dev](https://web.dev/articles/optimize-lcp)): **TTFB ~40% · resource load delay <10% ·
resource load duration ~40% · element render delay <10%.** Two operational rules from the same
page: the LCP resource "should start loading at the same time as the first resource loaded by
that page", and **no more than one or two images may carry `fetchpriority="high"`** — beyond
that, priority setting stops helping.

| Budget | Value |
|---|---|
| Total transfer, landing page, first load | **≤ 1.5 MB** |
| Largest single asset | **≤ 400 kB** |
| `fetchpriority="high"` images | **≤ 2** |
| DOM nodes | ≤ 1,500 (Lighthouse warns at 1,400) |
| Animated properties | `transform` + `opacity` only |

The measured median for this tier is **2.6 MB**, and its four heaviest sites each ship a single
asset over 700 kB. That is exactly what the cleanest published field test says costs money:
Vodafone's 50/50 A/B on ~34K visits/day per variant, versions "visually and functionally
identical" — a **31% LCP improvement** (5.7 s vs 8.3 s) produced **+8% sales, +15%
lead-to-visit, +11% cart-to-visit** ([web.dev](https://web.dev/case-studies/vodafone)). Note the
winner was *still* at 5.7 s: the **relative** improvement is what paid, so "we're already slow,
the video is free" is false at any absolute level.

---

## Variants

### Variant A — Split with screenshot (default)

Copy left, product visual right; collapses to a single **copy-first** stack on mobile.
This is the full code example below. Best for most SaaS: balances message and product proof.

### Variant B — Background-effect centered

Centered copy over a subtle dot-grid + radial glow, no side visual. Best for AI/dev products
that want one restrained "wow" accent. Same tokens; swap the grid layout for a single
centered column and drop the visual column:

```tsx
<div className="mx-auto flex max-w-3xl flex-col items-center py-24 text-center sm:py-32 lg:py-40">
  <Badge variant="secondary" className="rounded-full">v2.0 is live</Badge>
  <h1 className="mt-6 text-4xl leading-none font-semibold tracking-tight text-balance sm:text-5xl lg:text-[4rem]">
    The interface for modern software teams
  </h1>
  <p className="mt-6 max-w-2xl text-lg text-muted-foreground text-pretty sm:text-xl">
    Plan, build, and ship in one place — fast enough to feel local.
  </p>
  <div className="mt-10 flex flex-col gap-3 sm:flex-row">
    <Button size="lg" asChild><a href="/signup">Start free</a></Button>
    <Button size="lg" variant="ghost" asChild>
      <a href="/docs">Read the docs <ArrowRight className="size-4" /></a>
    </Button>
  </div>
</div>
```

Keep the accent to **one** effect (grid *or* aurora *or* glow) — never stacked.

---

## Interaction / state matrix

| Dimension | States & requirements |
|---|---|
| **Theme** | Light + dark via tokens (`bg-background`, `text-foreground`, `text-muted-foreground`, `border`). Accent opacity re-themed via `--hero-grid` / `--hero-glow`. |
| **Viewport** | Desktop split → tablet → mobile stacked (copy first). Primary CTA stays above the fold at every size. |
| **CTA — default** | Exactly two, ranked by **hue and contrast**. Filled + outline is one legal ranking; two fills in different colours is another (6 of 13 do this) — Stripe's primary is a saturated brand fill with white text, its secondary a 65%-white fill with the *same* brand colour as text. Both filled, ranking unmistakable. |
| **CTA — hover** | shadcn `<Button>` handles `hover:bg-primary/90` etc. Optional icon nudge: `group-hover:translate-x-0.5`, gated `motion-safe:`. |
| **CTA — focus-visible** | Visible `ring-2 ring-ring ring-offset-2` (built into shadcn Button). Never remove the ring. |
| **CTA — active / disabled / loading** | Active handled by Button. Loading: `disabled` + spinner (`<Loader2 className="animate-spin" />`) + `aria-busy`. |
| **Motion** | `prefers-reduced-motion`: gate the animated glow behind `motion-safe:animate-*` and provide a static frame. No parallax/typewriter by default. |
| **Media loading** | Reserve space with `aspect-video` (or explicit `width`/`height`) → no CLS. Eager-load the LCP visual (`priority` / `loading="eager"`), lazy-load anything below. |
| **Content length** | Headline survives 1–3 lines (`text-balance`); subhead wraps (`text-pretty`); long CTA labels don't overflow (buttons size to content, `w-full` on mobile). |
| **RTL / i18n** | Use logical direction from `dir`; icon nudges use `rtl:-scale-x-100` or logical margins. Expect +30% string length. |
| **No-JS / hydration** | Headline + both CTAs render server-side. The animated accent is progressive enhancement only. |

---

## Responsive behavior

- **One breakpoint switch** (`lg:` ≈ 1024px): `grid-cols-1` → `lg:grid-cols-2`. Copy column
  is first in DOM, so mobile is naturally **copy-first, visual-second**.
- **Text alignment** flips: centered on mobile (`text-center`), left-aligned on desktop
  (`lg:text-left`, `lg:items-start`).
- **Type scale**: headline `text-4xl sm:text-5xl lg:text-[4rem]` (36 → 48 → **64px**, a 0.56
  mobile ratio — inside the measured 0.5–0.75 band, median 0.67); subhead `text-lg sm:text-xl`.
  Prefer one clean jump over many breakpoints (or `clamp()` for truly fluid sizing).
- **Section padding** grows with viewport: `py-24 sm:py-32 lg:py-40`; gutters `px-6 lg:px-8`.
- **CTA buttons** are full-width and thumb-friendly on mobile (`w-full sm:w-auto`, ≥44px tall
  via `size="lg"`), inline row on `sm+`.
- **Readable measure**: copy column capped at `max-w-2xl` (~45–75ch) even inside a wide grid.

---

## Accessibility notes

- Exactly **one `<h1>`** per page; it lives here and is real, selectable text.
- **Contrast ≥ 4.5:1** for headline/subhead over the background accent. On photo/video heroes
  add a scrim (`bg-background/60` overlay) before overlaying text.
- **Decorative background** is `aria-hidden` + `pointer-events-none` and never a focus target.
- **Focus-visible rings** on every CTA/link — keep shadcn's defaults; logical tab order puts
  the **primary CTA before** the secondary.
- **`prefers-reduced-motion`**: all non-essential animation is gated behind `motion-safe:` with
  a static fallback (no motion = the hero still looks finished).
- **Images**: meaningful screenshot → descriptive `alt`; pure decoration → `alt=""`. Never bake
  the headline into an image.
- **Landmark**: wrap in `<section aria-labelledby="hero-heading">` and point it at the `<h1 id>`.
- **Hero CTAs ≥ 44×44 CSS px at 390 width.** Measured, **7 of 11 leading sites fail this** —
  Framer 29px, Clerk 30px, Supabase 38px, trigger.dev/Vercel/Liveblocks 40px, Raycast 41px. They
  clear WCAG 2.5.8 AA (24×24) and fail 2.5.5 AAA. **Do not copy the tier here.**
- **If you split the headline for a stagger animation, keep one accessible copy.** Split by
  **word**, not character — a word split keeps the visible text selectable and keeps the node
  count at ~8 instead of ~50. Without this, a split headline reaches a text client as
  `WhereThingsGetDeveloped`:
  ```tsx
  <h1><span className="sr-only">{headline}</span>
    <span aria-hidden className="inline-flex flex-wrap">
      {headline.split(" ").map((w, i) => (
        <span key={i} className="mr-[0.25em] motion-safe:animate-[rise_.6s_var(--ease)_both]"
              style={{ animationDelay: `${i * 40}ms` }}>{w}</span>))}
    </span></h1>
  ```
- **`animation-timeline` goes behind `@supports`.** It is not Baseline; the hero must be complete
  without it.
- **Any self-advancing content shows each item a fraction of the time and reads as an ad** (NN/g).
  If it matters, it does not move by itself.

---

## Anti-slop callout

> Heroes fail loudly, and mostly in the same few ways. Avoid all of them:

- **Two *undifferentiated* CTAs.** Two is the correct number — 12 of 13 leading software heroes
  ship exactly two — but they must be ranked by hue and contrast. Two identical-weight buttons
  are correct only for genuinely parallel choices (Mac / Windows).
- **Burying the point.** NN/g eyetracking (130k fixations, 120 participants): **57%** of
  page-viewing time is above the fold, **74%** is in the first two screenfuls, **42%** is in the
  top 20% of the page ([NN/g](https://www.nngroup.com/articles/scrolling-and-attention/)).
- **Carousel / slider hero.** Fragments attention, hurts SEO, tanks LCP. **0 of 13** measured
  sites ship one. Never for marketing.
- **Describe instead of show.** Prose where a screenshot/clip of the actual product belongs.
- **Generic CTA copy** ("Learn more", "Submit", "Click here"). Use *action + value*
  ("Start free", "Book a demo").
- **Over-animation.** Aurora + spotlight + parallax + typewriter stacked. Pick **one** accent;
  gate it behind `prefers-reduced-motion`.
- **Muddy contrast / cramped spacing.** Whitespace + contrast are the whole game — take the
  spacing that feels right, then add more. One accent color; neutrals do 95% of the work.
- **Jargon over outcome.** "Ship faster with confidence" beats "Multi-tenant CI orchestration".
- **Slow LCP.** An unoptimized hero video/image as first paint. Vodafone's A/B test put a price
  on it: a 31% LCP improvement bought +8% sales (see § LCP budget). The marginal megabyte always
  costs money.
- **Stock-photo filler** disconnected from the message. Every pixel of the visual reinforces
  the copy or it's cut.

The tell of AI-generated slop: three buttons of equal weight, a gradient blob for no reason,
`text-gray-500` hardcoded everywhere, and a headline that says "Welcome to our platform."

**Grep the copy before you ship it.** The ban list rotates by model era, so a 2023 list ("delve",
"tapestry", "testament") is now a false-positive machine; the **mid-2025-and-on** cluster is short
and is what to grep hardest for — ***emphasizing, enhance, highlighting, showcasing***
([Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)).

```bash
# Tier-1 current-era vocabulary + promo puffery.
rg -i --pcre2 -n \
  '\b(showcas(e|ing|es)|emphasi[sz](e|ing|es)|highlight(ing|s)? (the|its|our)|enhanc(e|ing|es|ement)|robust|seamless(ly)?|leverag(e|ing)|unlock(ing)?|delve|tapestry|testament to|pivotal|meticulous(ly)?|vibrant|groundbreaking|cutting[- ]edge|next[- ]generation|revolutioniz|world[- ]class|state[- ]of[- ]the[- ]art|commitment to|renowned|boasts?)\b' \
  src app components content

# Structural tells: negative parallelism, copula avoidance, rule of three.
rg -i --pcre2 -n \
  "(not just [a-z' ]+,? but|it'?s not [a-z' ]+,? it'?s|no [a-z]+, no [a-z]+, just)|\b(serves as|stands as|functions as|represents) an?\b|\b\w+, \w+,? and \w+\b\.\s*$" \
  src app components content
```

Threshold: **more than 2 Tier-1 hits per 300 words of marketing copy is a rewrite, not an edit.**
The structural tells matter more than the vocabulary — **negative parallelism** ("not just X, but
Y"), **copula avoidance** ("serves as a" for "is" — one study measured a >10% drop in *is*/*are*
in 2023 academic writing), **rule of three**, and **elegant variation**. The phenomenon is real at
population scale: ≥13.5% of 2024 PubMed abstracts show LLM excess vocabulary, up to 40% in some
subcorpora (Kobak et al., *Science Advances* 11(27), 2025). But humans cannot judge it by eye — a
2025 study found human discrimination no better than chance — so **use the list as a grep, never
as a verdict.**

Two rules from Linear's own design team
([linear.app/now](https://linear.app/now/behind-the-latest-design-refresh), Mar 2026) cover most
hero failures between them: **"Don't compete for attention you haven't earned"** and **"Structure
should be felt not seen."** And on why generated UI looks right and feels wrong
([Karri Saarinen, Apr 2026](https://linear.app/now/output-isn-t-design)): "products that look
polished, ambitious, and impressive at first glance, but begin to unravel the moment you actually
use them… The form is there. The fit is not."

---

## Complete example (copy-pasteable)

Requires shadcn `button` and `badge`, plus `lucide-react`:

```bash
npx shadcn@latest add button badge
npm i lucide-react
```

```tsx
// components/marketing/hero.tsx
import Image from "next/image";
import { ArrowRight } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export function Hero() {
  return (
    // Keep the whole section ≤ ~90vh so the next section's top edge peeks above the
    // fold — measured median hero height is 87vh; only 3 of 13 sites exceed 100vh.
    <section
      aria-labelledby="hero-heading"
      className="relative isolate overflow-hidden bg-background"
    >
      {/* Background accent: near-subliminal dot grid + soft glow.
          Decorative, themed via CSS vars, gated for reduced motion. */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10"
        style={{
          backgroundImage:
            "radial-gradient(var(--hero-grid) 1px, transparent 1px)",
          backgroundSize: "var(--hero-grid-size) var(--hero-grid-size)",
          maskImage:
            "radial-gradient(ellipse 100% 80% at 50% 0%, black 40%, transparent 100%)",
        }}
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -top-32 left-1/2 -z-10 h-[36rem] w-[72rem] -translate-x-1/2 rounded-full blur-3xl motion-safe:animate-pulse"
        style={{ background: "var(--hero-glow)" }}
      />

      <div className="mx-auto grid max-w-7xl grid-cols-1 items-center gap-16 px-6 py-24 sm:py-32 lg:grid-cols-2 lg:gap-12 lg:px-8 lg:py-40">
        {/* ── Copy column (DOM-first → mobile shows copy first) ── */}
        <div className="mx-auto flex max-w-2xl flex-col items-center text-center lg:mx-0 lg:items-start lg:text-left">
          {/* 1. Eyebrow / announcement */}
          <a
            href="/changelog"
            className="group inline-flex items-center gap-2 rounded-full border px-3 py-1 text-sm text-muted-foreground transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
          >
            <Badge variant="secondary" className="rounded-full">
              New
            </Badge>
            <span>Realtime sync just shipped</span>
            <ArrowRight className="size-4 transition-transform motion-safe:group-hover:translate-x-0.5" />
          </a>

          {/* 2. Headline — the only <h1>. 7 words; 36 → 48 → 64px; leading-none;
              tracking-tight; text-balance forces the two-line wrap at 1440. */}
          <h1
            id="hero-heading"
            className="mt-6 text-4xl leading-none font-semibold tracking-tight text-balance sm:text-5xl lg:text-[4rem]"
          >
            Ship faster with a workspace built for momentum
          </h1>

          {/* 3. Subheadline */}
          <p className="mt-6 max-w-xl text-lg leading-relaxed text-muted-foreground text-pretty sm:text-xl">
            The planning tool product teams actually enjoy using. Plan sprints,
            track issues, and ship — without the busywork.
          </p>

          {/* 4. CTA group — exactly two, ranked by hue and contrast. size="lg"
              keeps both ≥44px tall at 390. */}
          <div className="mt-8 flex w-full flex-col gap-3 sm:w-auto sm:flex-row sm:items-center">
            <Button size="lg" className="w-full sm:w-auto" asChild>
              <a href="/signup">Start free</a>
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="group w-full sm:w-auto"
              asChild
            >
              <a href="/demo">
                Book a demo
                <ArrowRight className="size-4 transition-transform motion-safe:group-hover:translate-x-0.5" />
              </a>
            </Button>
          </div>

          {/* 5. Trust strip is NOT here. Render <LogoCloud> as the next section
              (marketing-sections.md §2c) so it lands ~0.9 screens down — the first
              reward for the first scroll. Only 2 of 13 measured sites put marks in
              the hero box. */}
        </div>

        {/* ── 6. Visual column — aspect-locked, LCP-optimized ── */}
        <div className="relative w-full">
          <div className="overflow-hidden rounded-xl border bg-muted shadow-2xl">
            <Image
              src="/hero-product.png"
              alt="Sprint board showing issues moving from In Progress to Done"
              width={1200}
              height={750}
              priority
              sizes="(min-width: 1024px) 50vw, 100vw"
              className="aspect-video h-auto w-full object-cover"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
```

Notes on the example:

- **Zero hardcoded colors** — every surface uses a token (`bg-background`, `text-foreground`,
  `text-muted-foreground`, `border`, `ring-ring`); the accent reads `var(--hero-grid)` /
  `var(--hero-glow)` and flips in dark mode automatically.
- **One `<h1>`**, real text, `id` wired to the section's `aria-labelledby`, 64px at `lg`.
- **Exactly two CTAs.** Both use shadcn `<Button asChild>` so they render real `<a>` links
  (correct semantics, keyboard + focus-visible rings for free), and `size="lg"` keeps both over
  the 44px floor at 390.
- **No trust strip inside the hero** — it is the next section, at ~0.9 screens.
- **Motion is gated** — the glow only pulses under `motion-safe:`, icon nudges too; the static
  frame is fully finished.
- **No CLS** — `next/image` with `width`/`height` + `aspect-video`; `priority` eager-loads the
  LCP visual with proper `sizes`.
- **Copy-first on mobile** by DOM order; single `lg:` switch to the two-column split.
- Not on Next.js? Swap `next/image` for a plain `<img width={1200} height={750} loading="eager"
  decoding="async" />` and drop the import — everything else is framework-agnostic.
