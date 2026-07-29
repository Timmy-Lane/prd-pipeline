# Recipe: Marketing Sections — Feature / Bento / Logo Cloud / Testimonial

> The four "trust + value" sections that sit between the hero and pricing on a modern SaaS
> landing page. Built with **React + Tailwind v4 (CSS-first) + shadcn/ui**. Token-driven,
> accessible, and shaped so hierarchy is encoded in *size and placement* — not just copy.

## Contents

- [1. When to use it](#1-when-to-use-it) — the four questions a visitor asks after the hero, one per section
- [2. Anatomy (layout structure)](#2-anatomy-layout-structure) — the shared section shell, the bento grid, and the other three
- [3. Token-driven styling (CSS vars, not hardcoded hex)](#3-token-driven-styling-css-vars-not-hardcoded-hex) — semantic tokens plus the marquee tokens and keyframes
- [4. Variants](#4-variants) — bento feature grid · testimonial marquee (behind an evidence gate) · logo cloud
- [5. Interaction / state matrix](#5-interaction--state-matrix) — every surface across all four sections
- [6. Responsive behavior](#6-responsive-behavior) — reset ALL grid spans below 768px
- [7. Accessibility notes](#7-accessibility-notes) — section landmarks, and why `grid-auto-flow: dense` is banned on interactive tiles
- [8. Anti-slop callout](#8-anti-slop-callout) — the one failure mode: a uniform grid of equal cards
- [9. Complete, copy-pasteable code](#9-complete-copy-pasteable-code) — shared header, marquee primitive, all three variants, skeleton, composed page
- [10. Ship checklist](#10-ship-checklist) — the pre-ship boxes
- [11. Scroll narrative](#11-scroll-narrative) — native scroll by default, and the measured case against smooth-scroll libraries
- [12. WebGL / 3D — what earns it](#12-webgl--3d--what-earns-it) — 4 of 13 sites, ambient background only

---

## 1. When to use it

Reach for these when a visitor has just seen the hero and is silently asking four questions
in sequence. Each section answers exactly one:

| Section | Question it answers | Density | Motion | Where it goes |
|---|---|---|---|---|
| **Logo cloud** | "Who else trusts this?" | low (6–36 marks, median 11) | none / slow marquee | directly under hero, ~0.9 screens down |
| **Feature section** | "What does it do?" | medium (3–6 items) | subtle on-scroll reveal | after logos |
| **Bento grid** | "Why is it *better*?" (parallel props) | high (5–9 cells) | hover lift, in-cell demos | primary feature slot |
| **Testimonials** | "Do real people love it?" | high wall / low spotlight | marquee / carousel | near pricing + CTAs |

Canonical page order: `hero → logo cloud → bento (or zigzag) → secondary features → testimonials → pricing/CTA`.
Alternate density — drop a low-density logo cloud between two dense sections so the eye rests.

**Use the bento grid when** features run in *parallel* (each tile targets a different
segment/use-case and can be scanned in any order). **Do not** use bento for sequential or
long-form content (docs, tutorials, checkout) — the pattern forces each cell down to a
phrase, a number, or one screenshot. If your features are *alternatives* to one another, use
a tabbed feature explorer instead.

---

## 2. Anatomy (layout structure)

### 2a. Section shell (shared by all four)

Every section uses the same outer rhythm so edges align down the page:

```
<section>                          py-16 / py-24 / py-32, relative
  <div container>                  max-w-7xl mx-auto px-6
    <header>                       max-w-2xl, mb-12 / mb-16
      eyebrow                      text-sm font-medium text-primary
      heading                      text-3xl md:text-4xl font-semibold tracking-tight
      subhead                      text-muted-foreground
    <content grid / track>
```

**Page rhythm, measured.** Median page = **11.2 viewports tall** across 13 leading software
marketing sites (range 5.9–17.4). Median top-level section count = **8** (range 3–15). That puts
the **median section at ~1.4 viewports**. Use it as a governor: under **0.8** viewports a section
is a fragment and should merge with its neighbour; over **2.5** it needs an internal heading.

And rank ruthlessly. NN/g eyetracking (130k fixations, 120 participants) puts **57% of viewing
time above the fold and 74% inside the first two screenfuls**, with only 26% spread across
everything after ([NN/g](https://www.nngroup.com/articles/scrolling-and-attention/)). Screens 3+
are elaboration; nothing required to convert may live there alone, and the primary CTA must
repeat at the bottom.

### 2b. Bento grid (the flagship)

```
grid container ─ grid-cols-1  →  md:grid-cols-2  →  lg:grid-cols-3, one gap, fixed auto-rows
│
├─ ANCHOR tile      exactly ONE, top-left, lg:col-span-2 lg:row-span-2   (≈1.5–2× a support tile)
│    └─ inner:  flex flex-col justify-between   (media pins top, copy pins bottom)
│         ├─ visual / live mini-UI / chart  (top)
│         ├─ heading  (ranked typography — keeps a dense grid readable)
│         └─ supporting sentence OR one big metric  (bottom)
│
├─ WIDE tiles       lg:col-span-2  (2×1)
└─ FILL tiles       1×1
```

Rules that make it read as a bento and not a card wall:

- **One** dominant cell, in prime real estate (top-left). Two co-equal anchors = no focal point.
- **5–9 cells** is the scannable sweet spot; hard ceiling ~12 before hierarchy collapses.
- Every tile inner is `flex flex-col justify-between` so media and copy pin to opposite ends
  regardless of tile height.
- Put a **live mini-UI / chart / looping demo** in the anchor, not a static PNG.

### 2c. The other three, in one line each

- **Logo cloud** — `grid` of capped-height marks at **full colour and full opacity**, eyebrow
  above. Measured across 12 sites: **grayscale on 0 of them, `opacity: 1` on all of them.**
  `grayscale opacity-60` is a 2021 Tailwind-UI convention this tier has left. Cap **height**
  (`h-8`/`h-10`), never a box. **6–36 marks; median 11** — above ~20 the strip reads as a
  deliberate *wall* (Stripe 36, Vercel 21) and should be full-bleed; below ~12 it reads as a row
  and should be centred in the container. If a mark is illegible at `h-8` in dark mode, supply a
  light variant — do not reach for grayscale to hide the problem.
- **Feature grid** — three-column `icon → heading → body → "Learn more →"`, icon in a tinted rounded square.
- **Testimonials** — cards of `quote → avatar + name + role@company`, in a wall, a masonry column set, or a dual-row marquee.

---

## 3. Token-driven styling (CSS vars, not hardcoded hex)

Everything is driven by shadcn's semantic tokens so the sections theme themselves in light/dark
and inherit your brand with zero edits. **No hex literals in markup.** Add the marquee tokens +
keyframes to your global stylesheet (Tailwind v4 does *not* auto-inject these):

```css
/* app/globals.css — Tailwind v4 CSS-first config */
@import "tailwindcss";

@theme inline {
  /* Marquee primitive — durations tuned per row; slower = calmer/more premium */
  --animate-marquee: marquee var(--duration, 40s) linear infinite;
  --animate-marquee-vertical: marquee-vertical var(--duration, 40s) linear infinite;
}

@keyframes marquee {
  from { transform: translateX(0); }
  to   { transform: translateX(calc(-100% - var(--gap, 1rem))); }
}
@keyframes marquee-vertical {
  from { transform: translateY(0); }
  to   { transform: translateY(calc(-100% - var(--gap, 1rem))); }
}
```

Tokens the recipe leans on (all from the shadcn base theme — override once, applies everywhere):

| Token | Used for |
|---|---|
| `--background` / `--foreground` | page + primary text; also the fade-mask `from-background` |
| `--card` / `--card-foreground` | tile + testimonial surfaces |
| `--muted-foreground` | subheads, roles, supporting copy |
| `--border` | tile hairlines (`border-border`, or `border-white/[0.08]` in dark) |
| `--primary` | eyebrow accent, hover link color, focus ring |
| `--ring` | `focus-visible` rings on every interactive element |
| `--radius` | tile radius — bento wants a generous `rounded-2xl`/`rounded-3xl` "tray" feel |

Numeric spec (ship these): gap **one consistent value** (`gap-4`/16px, never mixed) · radius
`rounded-3xl` (~24px — under 16px kills the tray feel) · inner padding `p-6` (leave 20–30%
whitespace) · fixed `auto-rows` (`lg:auto-rows-[16rem]`) · logo cap `h-8`/`h-10` (cap *height*,
never a fixed box — logos have wildly different aspect ratios).

---

## 4. Variants

### Variant A — Bento feature grid (primary)
One 2×2 anchor with a live mini-chart, two wide tiles, two fill tiles. This is the default
"why we're better" slot. Full code in §9.

### Variant B — Testimonial marquee (dual-row), behind an evidence gate
Headline + subhead over two independent marquee rows scrolling in **opposite directions**, each
with edge fade masks and pause-on-hover. Code in §9.

**This is not the default.** A marquee shows each card only a fraction of the time, and that is
the documented failure mode of auto-forwarding content: Nielsen's study found a self-rotating
panel showed its content "only **20%** of the time" and that users "assume that it might be an
advertisement, which makes them more likely to ignore it"
([NN/g](https://www.nngroup.com/articles/auto-forwarding/)). A marquee is a carousel with better
manners, not a different pattern. Ship one only when **all three** hold: (a) `pauseOnHover` is
on, (b) the same quotes are reachable as a static list or via a "read all" link, (c) no quote
carries information the visitor needs to convert. If a quote is load-bearing, put it in a static
spotlight card. **Default to a static 3-column wall.**

### Variant C — Logo cloud (static grid)
Capped-height marks at full colour and full opacity, eyebrow above. Swap to the same `Marquee`
primitive from Variant B when you have many logos. Code in §9.

---

## 5. Interaction / state matrix

| State | Bento tile | Feature card | Logo | Testimonial card | Marquee |
|---|---|---|---|---|---|
| **default** | resting `bg-card`, hairline border | flat | full colour, `opacity: 1` | resting card | scrolling |
| **hover** | lift `hover:shadow-lg`, border brightens, in-tile demo plays | icon/link → `text-primary`, subtle bg | no change — it is already at full strength | border/bg lift | pause (`group-hover:[animation-play-state:paused]`) |
| **focus-visible** | `ring-2 ring-ring` on interactive tiles; **keep DOM order** | ring on link | ring on linked logo | ring | n/a |
| **active/press** | scale `active:scale-[0.99]` | link press | — | — | — |
| **loading** | `Skeleton` block per tile | skeleton | skeleton logo | skeleton avatar + 2 lines | n/a |
| **empty** | hide the section — never show empty proof | hide | hide | **hide — never fabricate** | hide |
| **reduced-motion** | disable in-tile loops/parallax | disable reveal | static | static | **paused/static** |
| **dark mode** | dark `bg-card` + faint border | inherits tokens | may need light logo variants | dark card | fade mask stays `from-background` |

Make the whole anchor tile one link when it has a single destination — wrap in an `<a>`/`Link`
and use a `focus-within` ring so keyboard focus is visible on the card, not just the text.

---

## 6. Responsive behavior

- **Desktop (≥1024px):** full asymmetric multi-column layout; anchor spans 2×2.
- **Tablet (768–1024px):** collapse to **2 columns**; anchor spans both columns, keeps its height.
- **Mobile (<768px):** single-column full-width stack; **reset ALL grid spans** and switch to
  `auto-rows: auto` so tiles size to content.
- **Critical failure mode:** a 4-col grid that naively stacks into 8–12 equal cards on mobile
  becomes a long, hierarchy-free scroll. **Cut, merge, or re-prioritize** cells at small
  breakpoints — don't just let them stack.
- Logo cloud: `grid-cols-2 md:grid-cols-3 lg:grid-cols-6`. Testimonials: single column stack or
  swipeable carousel on mobile — never a tight side-scrolling grid.

---

## 7. Accessibility notes

- **Section landmarks:** each `<section>` gets `aria-labelledby` pointing at its heading `id`.
- **`grid-auto-flow: dense` is banned on interactive tiles** — it reorders visual position
  without reordering DOM/focus, so keyboard + screen-reader focus jump unpredictably. Reserve
  `dense` for non-interactive media galleries only.
- **Text over image** needs a bottom scrim (`bg-gradient-to-t from-black/60`) and a re-checked
  **4.5:1** contrast per tile (glass-blur overlays commonly fail WCAG 1.4.3).
- **Marquee:** gate the animation behind `motion-safe:` (or `motion-reduce:[animation-play-state:paused]`)
  so `prefers-reduced-motion` users get a static list. Mark duplicated/cloned children
  `aria-hidden="true"` so screen readers don't read every quote twice. Fade masks are
  `pointer-events-none` so hover/click pass through.
- **Logos:** every logo `<img>`/SVG has `alt` = company name (decorative-only if the name is
  also visible text). Dark-on-dark logos vanish in dark mode — supply light variants or a card background.
- **Testimonials:** use a real `<blockquote>` + `<cite>`; a quote with no real name + face reads
  as fabricated *and* is inaccessible.
- **Focus:** every interactive element (linked tile, logo, "Learn more") shows a `focus-visible:ring-2 ring-ring`.

---

## 8. Anti-slop callout

> **The one failure mode:** a uniform grid of equal cards. That is a card wall wearing a
> trend's name. Hierarchy must live in **size and placement**, not just copy.

Ship / avoid:

- ❌ Equal-size cells → ✅ exactly **one** 2×2 anchor; everything else 2×1 / 1×1.
- ❌ Mixed gutter values → ✅ **one** gap value everywhere (rule of thumb: gutter ≈ half the inner padding).
- ❌ Two co-equal anchors → ✅ a single focal point, top-left.
- ❌ Radius < 16px → ✅ `rounded-3xl`; the "tray" feel is the whole point.
- ❌ Static screenshot in the anchor → ✅ a live mini-UI / chart / looping demo.
- ❌ Testimonial headline = "Great product!" → ✅ headline = a **quantified outcome** ("Cut onboarding 60%").
- ❌ 40+ full-color logos at random sizes → ✅ **6–36, height-capped, full colour, one consistent optical weight** (not boxed, not grayscale).
- ❌ A marquee as the default testimonial layout → ✅ a **static 3-column wall**; the marquee only clears the three-part gate in Variant B.
- ❌ Marquee too fast / no pause / ignores reduced-motion → ✅ 40s, `pauseOnHover`, `motion-safe` gated.
- ❌ `grid-auto-flow: dense` on interactive tiles → ✅ dense only for non-interactive media.
- ❌ 4+ bento sections on one page → ✅ **2–3 max**; alternate density for rhythm.
- ❌ Fabricated / faceless / over-polished quotes → ✅ real name, role, company, headshot; hide the section if you have none.

---

## 9. Complete, copy-pasteable code

Requires: `npx shadcn@latest add card badge avatar button skeleton` and `lucide-react`.
Add the marquee tokens/keyframes from §3 to `globals.css` first.

### 9.1 Shared section header

```tsx
// components/marketing/section-header.tsx
import { cn } from "@/lib/utils";

interface SectionHeaderProps {
  id: string;
  eyebrow?: string;
  title: string;
  description?: string;
  className?: string;
}

export function SectionHeader({
  id,
  eyebrow,
  title,
  description,
  className,
}: SectionHeaderProps) {
  return (
    <div className={cn("max-w-2xl", className)}>
      {eyebrow ? (
        <p className="text-sm font-medium text-primary">{eyebrow}</p>
      ) : null}
      <h2
        id={id}
        className="mt-3 text-3xl font-semibold tracking-tight text-balance sm:text-4xl"
      >
        {title}
      </h2>
      {description ? (
        <p className="mt-4 text-base leading-relaxed text-muted-foreground text-pretty">
          {description}
        </p>
      ) : null}
    </div>
  );
}
```

### 9.2 Marquee primitive (Tailwind v4)

```tsx
// components/marketing/marquee.tsx
import { cn } from "@/lib/utils";

interface MarqueeProps extends React.ComponentPropsWithoutRef<"div"> {
  /** Reverse scroll direction — use for the 2nd row. */
  reverse?: boolean;
  /** Pause on hover (recommended for readable content). */
  pauseOnHover?: boolean;
  /** Duplicate children N times for a seamless loop. */
  repeat?: number;
  /** Scroll duration, e.g. "40s". Slower reads as calmer/more premium. */
  duration?: string;
  children: React.ReactNode;
}

export function Marquee({
  reverse = false,
  pauseOnHover = false,
  repeat = 4,
  duration = "40s",
  className,
  children,
  ...props
}: MarqueeProps) {
  return (
    <div
      {...props}
      style={{ "--duration": duration, "--gap": "1rem" } as React.CSSProperties}
      className={cn(
        "group flex gap-[--gap] overflow-hidden p-2 [--gap:1rem]",
        className,
      )}
    >
      {Array.from({ length: repeat }).map((_, i) => (
        <div
          key={i}
          // Clones after the first are decorative — hide from AT to avoid re-reading.
          aria-hidden={i > 0 ? "true" : undefined}
          className={cn(
            "flex shrink-0 justify-around gap-[--gap]",
            // Motion gated behind motion-safe -> reduced-motion users get a static list.
            "motion-safe:animate-[marquee_var(--duration)_linear_infinite]",
            reverse && "[animation-direction:reverse]",
            pauseOnHover &&
              "group-hover:[animation-play-state:paused]",
          )}
        >
          {children}
        </div>
      ))}
    </div>
  );
}
```

### 9.3 Bento feature grid (Variant A)

```tsx
// components/marketing/bento-features.tsx
import Link from "next/link";
import {
  Activity,
  ArrowRight,
  GitBranch,
  Lock,
  Zap,
  type LucideIcon,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { SectionHeader } from "./section-header";

interface BentoTile {
  title: string;
  description: string;
  icon: LucideIcon;
  href?: string;
  className?: string;
  /** Optional in-tile visual rendered above the copy (chart, mini-UI, demo). */
  visual?: React.ReactNode;
}

const tiles: BentoTile[] = [
  {
    title: "Ships in milliseconds",
    description:
      "Every interaction is optimistic and local-first, so the UI never waits on the network.",
    icon: Zap,
    href: "/features/performance",
    // Anchor: 2x2 on desktop, full width on mobile.
    className: "lg:col-span-2 lg:row-span-2",
    visual: <PerformanceSparkline />,
  },
  {
    title: "Branch-aware previews",
    description: "Spin up an isolated environment for every pull request automatically.",
    icon: GitBranch,
    href: "/features/previews",
    className: "lg:col-span-2",
  },
  {
    title: "SOC 2 by default",
    description: "Encryption, audit logs, and SSO on every plan — no enterprise upsell.",
    icon: Lock,
    href: "/security",
  },
  {
    title: "Live observability",
    description: "Traces, logs, and metrics in one timeline you can actually read.",
    icon: Activity,
    href: "/features/observability",
  },
];

export function BentoFeatures() {
  return (
    <section
      aria-labelledby="bento-heading"
      className="relative py-24 sm:py-32"
    >
      <div className="mx-auto max-w-7xl px-6">
        <SectionHeader
          id="bento-heading"
          eyebrow="Built for velocity"
          title="Everything your team needs to ship faster"
          description="A parallel set of capabilities — scan them in any order. Each one removes a step between an idea and production."
          className="mb-12 sm:mb-16"
        />

        {/* One gap value. Reset spans at mobile; anchor is 2x2 from lg up. */}
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:auto-rows-[16rem] lg:grid-cols-3">
          {tiles.map((tile) => (
            <BentoCard key={tile.title} {...tile} />
          ))}
        </div>
      </div>
    </section>
  );
}

function BentoCard({
  title,
  description,
  icon: Icon,
  href,
  className,
  visual,
}: BentoTile) {
  return (
    <Card
      className={cn(
        // Tray feel: generous radius, hairline border, resting card surface.
        "group/tile relative flex flex-col justify-between overflow-hidden rounded-3xl border-border p-6",
        // Hover: lift + border brighten. Press: subtle scale. Focus lives on the link.
        "transition-all duration-200 hover:shadow-lg has-[a:focus-visible]:ring-2 has-[a:focus-visible]:ring-ring",
        "active:scale-[0.99] motion-reduce:transition-none motion-reduce:active:scale-100",
        className,
      )}
    >
      {/* Media pins top */}
      <div className="flex items-start justify-between">
        <span className="inline-flex size-11 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-inset ring-primary/20">
          <Icon className="size-5" aria-hidden="true" />
        </span>
      </div>

      {visual ? <div className="my-4 flex-1">{visual}</div> : null}

      {/* Copy pins bottom */}
      <div className={cn(!visual && "mt-8")}>
        <h3 className="text-lg font-semibold tracking-tight">
          {href ? (
            <Link
              href={href}
              // Stretched link makes the whole tile clickable; ring shows via has-[a:focus-visible] above.
              className="before:absolute before:inset-0 before:rounded-3xl focus-visible:outline-none"
            >
              {title}
            </Link>
          ) : (
            title
          )}
        </h3>
        <p className="mt-2 text-sm leading-relaxed text-muted-foreground text-pretty">
          {description}
        </p>
        {href ? (
          <span className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-primary opacity-0 transition-opacity group-hover/tile:opacity-100 motion-reduce:opacity-100">
            Learn more
            <ArrowRight className="size-4" aria-hidden="true" />
          </span>
        ) : null}
      </div>
    </Card>
  );
}

/** Illustrative in-tile visual — a token-driven sparkline (no hardcoded colors). */
function PerformanceSparkline() {
  const points = [12, 18, 10, 24, 16, 30, 22, 38, 28, 46];
  const max = Math.max(...points);
  const path = points
    .map((p, i) => {
      const x = (i / (points.length - 1)) * 100;
      const y = 100 - (p / max) * 100;
      return `${i === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");

  return (
    <div className="relative h-full min-h-32 w-full overflow-hidden rounded-2xl bg-muted/40 ring-1 ring-inset ring-border">
      <svg
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        className="absolute inset-0 size-full"
        role="img"
        aria-label="p95 latency trending down over the last 30 days"
      >
        <defs>
          <linearGradient id="spark-fill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="currentColor" stopOpacity="0.25" />
            <stop offset="100%" stopColor="currentColor" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path
          d={`${path} L 100 100 L 0 100 Z`}
          className="text-primary"
          fill="url(#spark-fill)"
        />
        <path
          d={path}
          fill="none"
          className="text-primary"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          vectorEffect="non-scaling-stroke"
        />
      </svg>
      <Badge
        variant="secondary"
        className="absolute right-3 top-3 tabular-nums"
      >
        p95 · 42ms
      </Badge>
    </div>
  );
}
```

### 9.4 Testimonial marquee (Variant B)

```tsx
// components/marketing/testimonials.tsx
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { Marquee } from "./marquee";
import { SectionHeader } from "./section-header";

interface Testimonial {
  /** Lead with a quantified outcome, not generic praise. */
  headline: string;
  quote: string;
  name: string;
  role: string;
  company: string;
  avatarSrc?: string;
}

const testimonials: Testimonial[] = [
  {
    headline: "Cut onboarding time 60%",
    quote:
      "We replaced three internal tools with one. New engineers ship on day one instead of week two.",
    name: "Dana Ortiz",
    role: "VP Engineering",
    company: "Northwind",
    avatarSrc: "/avatars/dana.jpg",
  },
  {
    headline: "Zero incidents in 6 months",
    quote:
      "The observability timeline caught a regression before a single customer noticed. That's never happened before.",
    name: "Marcus Lee",
    role: "Staff SRE",
    company: "Helio",
    avatarSrc: "/avatars/marcus.jpg",
  },
  {
    headline: "Saved $80k/yr in tooling",
    quote:
      "Consolidating onto one platform paid for itself in the first quarter. The team actually enjoys using it.",
    name: "Priya Nair",
    role: "Head of Platform",
    company: "Cobalt",
    avatarSrc: "/avatars/priya.jpg",
  },
  {
    headline: "Shipped our launch on time",
    quote:
      "Preview environments per PR meant design, product, and eng were reviewing the same thing. No more 'works on my machine.'",
    name: "Tom Becker",
    role: "Product Lead",
    company: "Vela",
    avatarSrc: "/avatars/tom.jpg",
  },
];

export function Testimonials() {
  const firstRow = testimonials.slice(0, Math.ceil(testimonials.length / 2));
  const secondRow = testimonials.slice(Math.ceil(testimonials.length / 2));

  return (
    <section
      aria-labelledby="testimonials-heading"
      className="relative overflow-hidden py-24 sm:py-32"
    >
      <div className="mx-auto max-w-7xl px-6">
        <SectionHeader
          id="testimonials-heading"
          eyebrow="Loved by product teams"
          title="Teams ship more with less overhead"
          description="Real outcomes from teams who consolidated their stack."
          className="mb-12 sm:mb-16"
        />
      </div>

      {/* Dual rows, opposite directions, pause on hover, gated for reduced motion. */}
      <div className="relative flex flex-col gap-4">
        <Marquee pauseOnHover duration="45s" className="[--gap:1rem]">
          {firstRow.map((t) => (
            <TestimonialCard key={t.name} {...t} />
          ))}
        </Marquee>
        <Marquee reverse pauseOnHover duration="55s" className="[--gap:1rem]">
          {secondRow.map((t) => (
            <TestimonialCard key={t.name} {...t} />
          ))}
        </Marquee>

        {/* Edge fade masks. pointer-events-none so hover/click pass through. */}
        <div className="pointer-events-none absolute inset-y-0 left-0 w-1/6 bg-gradient-to-r from-background" />
        <div className="pointer-events-none absolute inset-y-0 right-0 w-1/6 bg-gradient-to-l from-background" />
      </div>
    </section>
  );
}

function TestimonialCard({
  headline,
  quote,
  name,
  role,
  company,
  avatarSrc,
}: Testimonial) {
  const initials = name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2);

  return (
    <Card
      className={cn(
        "flex w-80 shrink-0 flex-col gap-4 rounded-2xl border-border p-6",
        "transition-colors hover:bg-muted/40",
      )}
    >
      <blockquote className="flex flex-col gap-2">
        <p className="text-sm font-semibold text-primary">{headline}</p>
        <p className="text-sm leading-relaxed text-card-foreground text-pretty">
          &ldquo;{quote}&rdquo;
        </p>
      </blockquote>
      <figcaption className="mt-auto flex items-center gap-3">
        <Avatar className="size-10">
          <AvatarImage src={avatarSrc} alt="" />
          <AvatarFallback>{initials}</AvatarFallback>
        </Avatar>
        <div className="text-sm">
          <div className="font-medium">{name}</div>
          <div className="text-muted-foreground">
            {role} · {company}
          </div>
        </div>
      </figcaption>
    </Card>
  );
}
```

### 9.5 Logo cloud (Variant C)

```tsx
// components/marketing/logo-cloud.tsx
import Image from "next/image";

interface LogoCloudProps {
  logos: { name: string; src: string }[];
}

export function LogoCloud({ logos }: LogoCloudProps) {
  return (
    <section aria-labelledby="logos-heading" className="py-16">
      <div className="mx-auto max-w-7xl px-6">
        <h2
          id="logos-heading"
          className="text-center text-sm font-medium text-muted-foreground"
        >
          Trusted by teams at
        </h2>
        <div className="mt-8 grid grid-cols-2 items-center gap-8 md:grid-cols-3 lg:grid-cols-6">
          {logos.map((logo) => (
            <div key={logo.name} className="flex justify-center">
              <Image
                src={logo.src}
                alt={logo.name}
                width={120}
                height={40}
                // Cap HEIGHT, never a fixed box — logos have different aspect ratios.
                // Full colour, full opacity: measured on 12 leading sites, 0 grayscale.
                // If a mark dies in dark mode, ship a light variant — not a filter.
                className="h-8 w-auto"
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
```

### 9.6 Loading state (Skeleton)

```tsx
// Drop-in per-tile skeleton for the bento grid while data streams in.
import { Skeleton } from "@/components/ui/skeleton";

export function BentoSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:auto-rows-[16rem] lg:grid-cols-3">
      <Skeleton className="rounded-3xl lg:col-span-2 lg:row-span-2" />
      <Skeleton className="h-64 rounded-3xl lg:col-span-2" />
      <Skeleton className="h-64 rounded-3xl" />
      <Skeleton className="h-64 rounded-3xl" />
    </div>
  );
}
```

### 9.7 Composing the page

```tsx
// app/page.tsx
import { BentoFeatures } from "@/components/marketing/bento-features";
import { LogoCloud } from "@/components/marketing/logo-cloud";
import { Testimonials } from "@/components/marketing/testimonials";

const logos = [
  { name: "Northwind", src: "/logos/northwind.svg" },
  { name: "Helio", src: "/logos/helio.svg" },
  { name: "Cobalt", src: "/logos/cobalt.svg" },
  { name: "Vela", src: "/logos/vela.svg" },
  { name: "Acme", src: "/logos/acme.svg" },
  { name: "Lumen", src: "/logos/lumen.svg" },
];

export default function Page() {
  return (
    <main>
      {/* hero … */}
      <LogoCloud logos={logos} />
      <BentoFeatures />
      <Testimonials />
      {/* pricing / CTA … */}
    </main>
  );
}
```

---

## 10. Ship checklist

- [ ] Exactly **one** 2×2 anchor, top-left; 5–9 total cells.
- [ ] **One** gap value everywhere; `rounded-3xl` tray radius; `p-6` inner padding.
- [ ] Anchor holds a live visual (chart/mini-UI), not a static PNG.
- [ ] All grid spans **reset** at the mobile breakpoint (no 8–12 equal stacked cards).
- [ ] Zero hex literals — everything on `--card` / `--primary` / `--muted-foreground` / `--ring` / `--border`.
- [ ] Marquee only if it clears the three-part gate (§4 Variant B); otherwise a static wall. If shipped: dual rows, opposite directions, `pauseOnHover`, `motion-safe` gated, clones `aria-hidden`, fade masks `pointer-events-none`.
- [ ] Logos: 6–36, **full colour, full opacity**, height-capped, real `alt`, light variants for dark mode where needed.
- [ ] Section rhythm: every section 0.8–2.5 viewports; the primary CTA repeats at the bottom of the page.
- [ ] Testimonials lead with a **quantified outcome**; real name + role + company + headshot; `<blockquote>`/`<figcaption>`.
- [ ] Every interactive element shows `focus-visible:ring-2 ring-ring`; DOM order == visual order (no `grid-auto-flow: dense` on interactive tiles).
- [ ] Section landmarks via `aria-labelledby`; text-over-image has a scrim + verified 4.5:1 contrast.
- [ ] **2–3 bento sections max** per page; alternate density for rhythm.

---

## 11. Scroll narrative

**Default: native scroll.** Measured on 13 leading software marketing sites — **0 of 13 ship
Lenis, locomotive-scroll, or GSAP.** Smooth-scroll libraries are an award-portfolio convention
(darkroom.engineering maintains Lenis and lists it in its own stack), not a product-marketing
convention. Two of the 13 set `scroll-behavior: smooth` in CSS; that is the native one-liner and
it is enough.

**Reveals.** `IntersectionObserver`'s default `threshold` is **0**, which fires before a single
pixel is visible — the commonest reveal bug, and it reads as "already animated". Use one of:

```js
new IntersectionObserver(onReveal, { threshold: 0.25 });                             // quarter visible
new IntersectionObserver(onReveal, { threshold: 0, rootMargin: "0px 0px -15% 0px" }); // 15% up from bottom
```

Unobserve on first fire. Never pass a threshold array for a one-shot reveal — arrays exist for
progress tracking, and each extra threshold is another callback per element per scroll.

**CSS-only alternative, progressive enhancement only.** `animation-timeline` / `view-timeline`
are **not Baseline** — MDN: "This feature is not Baseline because it does not work in some of the
most widely-used browsers." The page must be finished without it.

```css
@supports (animation-timeline: view()) {
  @media (prefers-reduced-motion: no-preference) {
    .reveal { animation: reveal linear both; animation-timeline: view();
              animation-range: entry 15% cover 35%; }
  }
}
@keyframes reveal { from { opacity: 0; transform: translateY(1rem); } }
```

**Sticky stacks.** A sticky element sticks to its nearest ancestor with a scrolling mechanism
(`overflow: hidden | scroll | auto | overlay`) "even if that ancestor isn't the nearest actually
scrolling ancestor" (MDN) — an `overflow-hidden` wrapper silently kills sticky. Add
`will-change: transform` to sticky content; MDN names the repaint cost and that remedy. Measured
sticky counts in this tier: **0 on 5 of 13 sites, 1–2 on 6**, and only Liveblocks (14) and Cursor
(6) run a real sticky narrative. A sticky stack is a deliberate choice, not a default.

**Parallax budget.**

| Effect | Budget |
|---|---|
| Parallax translate range | ≤ **8%** of the element's own height, one direction of travel per section |
| Speed differential between layers | ≤ **0.15×** scroll velocity |
| Scroll-linked motion | strictly linked to scroll *position* — never time-based while scrolling |
| Full-viewport wipes / zooms | don't |
| `opacity`, `color`, `filter: blur()` | unbudgeted |

The mechanism, from A List Apart's vestibular piece: motion "across a large amount of space"
relative to the viewport is the trigger, while animation "that involves only non-moving
properties, like opacity, color, and blurs" is "unlikely to be problematic". Affected population,
per vestibular.org: ~**8 million** US adults with a chronic balance problem plus **2.4 million**
with chronic dizziness.

**Animate `transform` and `opacity` only.** They are the only two properties the compositor
handles alone (web.dev). The same animation on `top`/`left` drops **50% of frames**; on
`transform`, **1%**. Aim for **4–5 ms** of compositing per frame during scroll.

**If you do ship Lenis** (v1.3.25): it has **no reduced-motion option** among its 23 settings, so
you must not instantiate it — `lenis.destroy()` on a `matchMedia` change. It also **breaks anchor
links by default** (`anchors: true` required) and traps modal scroll unless you set
`data-lenis-prevent`. Awwwards weights Usability at **30%**; each of these is a direct deduction.

**If you also use GSAP ScrollTrigger:** never nest a scrubbed trigger inside a timeline; create
pinned triggers in scroll order (or set `refreshPriority`); make viewport-dependent `start`/`end`
values *functions* with `invalidateOnRefresh: true`; and **remove `scroll-behavior: smooth` from
`<html>`** — GSAP's own docs say it breaks refresh calculations, and Bootstrap 5.x sets it by
default (`scroll-behavior: auto !important` to override).

---

## 12. WebGL / 3D — what earns it

Measured: **4 of 13** leading software marketing sites run a WebGL context, and every one of them
uses it for a **single ambient background behind the headline** — never a navigable 3D object.
Nine ship zero and are not worse for it: Linear serves a 348 kB page with a 64px headline and a
static screenshot, and is the most-emulated site in the category.

| Constraint | Value |
|---|---|
| WebGL contexts per page | **≤ 1** |
| Draw calls | ≤ **300** target, **1000** hard ceiling (r3f: "no more than 1000 as the very maximum, and optimally a few hundred or less") |
| Frameloop | `<Canvas frameloop="demand">` unless something is genuinely always moving |
| Mobile / weak GPU | `<PerformanceMonitor onIncline={() => setDpr(2)} onDecline={() => setDpr(1)}>` starting at 1.5, or `performance={{ min: 0.5 }}` + `regress()` |
| `prefers-reduced-motion: reduce` | do **not** mount the Canvas — render the poster |
| Fallback | a real `<img>` in the same DOM at the canvas's exact aspect ratio (Stripe ships `wave-fallback-desktop.png` at 1392px next to its two canvases) |
| Total page transfer with WebGL | ≤ **3 MB** |

Construction cost is real: creating 510 `TextGeometry` instances at once "will cause
approximately **1.5 seconds of pure jank** (Apple M1)" — distribute the work
([r3f scaling-performance](https://docs.pmnd.rs/react-three-fiber/advanced/scaling-performance)).

**Split-text display headlines** — the studio-tier signature — must keep an accessible copy, and
must split by **word**, not character:

```tsx
<h1><span className="sr-only">{headline}</span>
  <span aria-hidden className="inline-flex flex-wrap">
    {headline.split(" ").map((w, i) => (
      <span key={i} className="mr-[0.25em] motion-safe:animate-[rise_.6s_var(--ease)_both]"
            style={{ animationDelay: `${i * 40}ms` }}>{w}</span>))}
  </span></h1>
```

Without it, antinomy.studio's headline reaches a text client as
`Antinomyisanindependentcreativestudio…` and darkroom.engineering's as `WhereThingsGetDeveloped`.
