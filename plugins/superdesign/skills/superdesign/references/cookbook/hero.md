# Marketing Hero Section

> Above-the-fold marketing hero for a landing page. React + Tailwind CSS v4 + shadcn/ui.
> The default here is a **split-with-screenshot** hero (copy left, product visual right)
> with one primary + one secondary CTA, an optional announcement badge, a grayscale trust
> strip, and a subtle single background accent. Full light/dark + `prefers-reduced-motion`
> support. A **centered / background-effect** variant is included below.

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
│  │  │ 4. CTA group (primary + 2ndary) │   │                          │  │  │
│  │  │ 5. Trust strip (grayscale)      │   │                          │  │  │
│  │  └─────────────────────────────────┘   └──────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

| # | Part | Rules |
|---|---|---|
| 1 | **Eyebrow / badge** *(optional)* | A pill linking to a changelog/launch, or a category label. Use `<Badge>`. Keep it one short phrase. |
| 2 | **Headline** | Exactly one `<h1>`, real text (never baked into an image). Benefit-driven, ≤ ~10 words / ~90 chars. `text-balance`. |
| 3 | **Subheadline** | Who it's for + one tangible benefit. ≤ ~25 words. `text-muted-foreground`, `text-pretty`. |
| 4 | **CTA group** | One **primary** (filled, action + value) + at most one **secondary** (outline/ghost). Never two competing primaries. |
| 5 | **Trust strip** *(optional)* | Grayscale logo row / avatar stack + rating, directly under the CTA. Must not out-shout the CTA. |
| 6 | **Hero visual** | Show *what changes for the user*. Aspect-locked to prevent CLS. Decorative → `alt=""`; meaningful → descriptive `alt`. |
| — | **Background accent** *(optional)* | Dot/line grid, gradient mesh, or aurora. `aria-hidden`, `-z-10`, low opacity, must not drop text below 4.5:1. |

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
  <h1 className="mt-6 text-5xl font-semibold tracking-tight text-balance sm:text-7xl">
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
| **CTA — default** | Primary = filled `bg-primary`; secondary = `variant="outline"`. |
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
- **Type scale**: headline `text-4xl sm:text-5xl lg:text-6xl`; subhead `text-lg sm:text-xl`.
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

---

## Anti-slop callout

> Heroes fail loudly. In a study of 100 startup heroes, **74% failed**. The most common,
> most punishing mistakes — avoid all of them:

- **Two competing primary CTAs.** ~27% of failures; measured up to **−266%** conversion.
  One dominant primary, at most one *lower-emphasis* secondary that reduces friction.
- **Carousel / slider hero.** Fragments attention, hurts SEO, tanks LCP. Never for marketing.
- **Describe instead of show.** Prose where a screenshot/clip of the actual product belongs.
- **Generic CTA copy** ("Learn more", "Submit", "Click here"). Use *action + value*
  ("Start free", "Book a demo").
- **Over-animation.** Aurora + spotlight + parallax + typewriter stacked. Pick **one** accent;
  gate it behind `prefers-reduced-motion`.
- **Muddy contrast / cramped spacing.** Whitespace + contrast are the whole game — take the
  spacing that feels right, then add more. One accent color; neutrals do 95% of the work.
- **Jargon over outcome.** "Ship faster with confidence" beats "Multi-tenant CI orchestration".
- **Slow LCP.** An unoptimized hero video/image as first paint. Optimize the LCP asset; 5s load
  ≈ 38% bounce.
- **Stock-photo filler** disconnected from the message. Every pixel of the visual reinforces
  the copy or it's cut.

The tell of AI-generated slop: three buttons of equal weight, a gradient blob for no reason,
`text-gray-500` hardcoded everywhere, and a headline that says "Welcome to our platform."

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
import { ArrowRight, Star } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const LOGOS = ["Acme", "Globex", "Umbra", "Initech", "Hooli"] as const;

export function Hero() {
  return (
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

          {/* 2. Headline — the only <h1> */}
          <h1
            id="hero-heading"
            className="mt-6 text-4xl font-semibold tracking-tight text-balance sm:text-5xl lg:text-6xl"
          >
            Ship faster with a workspace built for momentum
          </h1>

          {/* 3. Subheadline */}
          <p className="mt-6 max-w-xl text-lg leading-relaxed text-muted-foreground text-pretty sm:text-xl">
            The planning tool product teams actually enjoy using. Plan sprints,
            track issues, and ship — without the busywork.
          </p>

          {/* 4. CTA group — one primary, one secondary */}
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

          {/* 5. Trust strip — grayscale, quieter than the CTA */}
          <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:gap-6">
            <div className="flex items-center gap-1 text-sm text-muted-foreground">
              <span className="flex" aria-hidden>
                {Array.from({ length: 5 }).map((_, i) => (
                  <Star key={i} className="size-4 fill-current" />
                ))}
              </span>
              <span>4.9/5 from 2,000+ teams</span>
            </div>
            <ul className="flex flex-wrap items-center gap-x-6 gap-y-2 opacity-60 grayscale">
              {LOGOS.map((name) => (
                <li key={name} className="text-sm font-medium text-foreground">
                  {name}
                </li>
              ))}
            </ul>
          </div>
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
- **One `<h1>`**, real text, `id` wired to the section's `aria-labelledby`.
- **One primary + one secondary CTA.** Both use shadcn `<Button asChild>` so they render real
  `<a>` links (correct semantics, keyboard + focus-visible rings for free).
- **Motion is gated** — the glow only pulses under `motion-safe:`, icon nudges too; the static
  frame is fully finished.
- **No CLS** — `next/image` with `width`/`height` + `aspect-video`; `priority` eager-loads the
  LCP visual with proper `sizes`.
- **Copy-first on mobile** by DOM order; single `lg:` switch to the two-column split.
- Not on Next.js? Swap `next/image` for a plain `<img width={1200} height={750} loading="eager"
  decoding="async" />` and drop the import — everything else is framework-agnostic.
