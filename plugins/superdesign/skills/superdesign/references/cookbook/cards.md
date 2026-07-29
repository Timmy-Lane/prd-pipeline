# Cards (product / feature / stat cards)

> One self-contained surface that groups a single concept and drives (ideally) one action. Built on the shadcn/ui `Card` skeleton with React + Tailwind v4. The kind Linear/Vercel ships: flat with a hairline border (not floaty shadows), one accent color, `tabular-nums` metrics that never jitter, layered-lightness elevation in dark mode, and accessible clickable surfaces via the stretched-link trick.

## Contents

- [When to use it](#when-to-use-it) — the three card families, and when a card is the wrong container
- [Anatomy](#anatomy) — the shadcn `Card` skeleton every variant extends
- [Token-driven styling](#token-driven-styling) — the token layer plus the two semantic additions
- [Variants](#variants) — stat/KPI card with trend + sparkline · whole-surface-clickable product card
- [Interaction / state matrix](#interaction--state-matrix) — every state a card must define
- [Responsive behavior](#responsive-behavior) — single-column first, equal tile heights per row
- [Accessibility](#accessibility) — the stretched-link trick for clickable cards
- [Anti-slop callout](#anti-slop-callout) — value jitter, jagged heights, and the rest
- [Complete code](#complete-code) — drop-in `StatCard`, the clickable product card, implementation notes

---

## When to use it

A card is the right tool when you're **browsing diverse content** and each item groups one concept behind one primary decision. The three families this recipe covers:

- **Stat / KPI card** — muted label + big number + trend delta (+ optional sparkline), tiled 3-4 across a dashboard. *Highest-value, so it's the main example below.*
- **Product / content card** — media + title + meta + one CTA (e-commerce, article, media, profile). *Second variant below.*
- **Feature card** — icon/visual + title + description, laid out in a grid or bento for marketing.

Reach for a card when you need to:

- **Surface a small set of scannable metrics** (a dashboard KPI row) where each tile can drill down.
- **Present a grid of browsable items** with imagery where the whole surface should be clickable.
- **Group a single concept** — one dominant element, one primary action.

Do **not** use it when:

- You have **uniform, comparable rows** — use a **list** (scannable) or a **table** (sort / rank / compare). "Stop defaulting to cards." Settings, search results, and data grids are not cards.
- The content demands **more than one primary decision** per item — that's a sign the concept is too big; split it.
- You're building a **sequential form** — cards fragment a flow that should read top-to-bottom.

The single biggest quality lever is **restraint**: one concept, one primary action, ≤3 clickable elements, and equal heights per row. The default failure mode is overloading.

---

## Anatomy

shadcn/ui's `Card` is the canonical skeleton every variant extends — don't fork the base file, wrap it.

```
Card                     root surface: flex flex-col, bg-card, text-card-foreground,
│                        rounded-xl, ring-1 ring-foreground/10, py-(--card-spacing)
├─ CardHeader            grid: title/description stack left, action pinned top-right
│   ├─ CardTitle         primary heading OR the big metric value
│   ├─ CardDescription   muted label / helper text (text-muted-foreground)
│   └─ CardAction        top-right slot: trend badge / menu / period selector
├─ CardContent           body: sparkline, media, description, price
└─ CardFooter            secondary content + grouped actions at the bottom
```

**Stat card** internal order (top → bottom): **label → value → trend delta → optional sparkline**. Label goes in `CardDescription`, value in `CardTitle`, the delta pill in `CardAction`, the sparkline in `CardContent`.

**Product card** order: **media → title → meta (rating) → price → CTA**. Choose ONE element to be visually dominant — usually the image or the price.

Two shadcn implementation facts the recipe leans on:

- **Density is tokenized** via `--card-spacing`. Default is `--spacing(4)` (16px); `size="sm"` sets `--spacing(3)` (12px). Padding uses `px-(--card-spacing)` / `py-(--card-spacing)`, so you retune density in one place instead of editing every child. (If your shadcn Card predates the `size` prop, set `[--card-spacing:--spacing(3)]` in `className` instead.)
- **Border, not shadow, by default**: `ring-1 ring-foreground/10` (a hairline ring), `rounded-xl`, `bg-card`, no drop shadow — the flat Linear/Vercel aesthetic.

---

## Token-driven styling

Everything maps to CSS variables — **no hardcoded hex**. Light and dark both fall out of the token layer. The only additions beyond stock shadcn are two semantic tokens: `--success` (positive delta) and `--warning` (rating stars). `--destructive` (negative delta) already ships with shadcn.

```css
/* app/globals.css — shadcn v4 token layer (abridged) */
:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
  --accent: oklch(0.97 0 0);
  --accent-foreground: oklch(0.205 0 0);
  --destructive: oklch(0.577 0.245 27.325);
  --border: oklch(0.922 0 0);
  --ring: oklch(0.708 0 0);
  --radius: 0.75rem;

  /* custom semantic tokens for cards */
  --success: oklch(0.62 0.17 149); /* emerald — positive delta */
  --warning: oklch(0.79 0.16 84);  /* amber   — rating stars   */
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  /* card stepped LIGHTER than the app bg — layered elevation, not shadow (see §Elevation) */
  --card: oklch(0.205 0 0);
  --card-foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --primary: oklch(0.922 0 0);
  --primary-foreground: oklch(0.205 0 0);
  --accent: oklch(0.269 0 0);
  --accent-foreground: oklch(0.985 0 0);
  --destructive: oklch(0.704 0.191 22.216);
  --border: oklch(1 0 0 / 10%); /* white @ 10% — hairline, not weight */
  --ring: oklch(0.556 0 0);

  --success: oklch(0.70 0.15 150);
  --warning: oklch(0.82 0.15 84);
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-border: var(--border);
  --color-ring: var(--ring);
  --color-success: var(--success);
  --color-warning: var(--warning);
  --radius-xl: var(--radius);
}
```

In JSX you then only reach for semantic classes: `bg-card`, `text-card-foreground`, `text-muted-foreground`, `text-success`, `text-destructive`, `text-warning`, `bg-accent`, `ring-ring`. Swap the accent or restep the greys once and every card re-themes, light and dark.

**Rules of thumb**

- Metric value: `text-3xl font-semibold tracking-tight tabular-nums`. `tabular-nums` is non-negotiable — it stops the number reflowing width when it updates on a live dashboard.
- Elevation: hairline ring at rest; add lift only on hover for clickable cards (`hover:bg-accent/40` or a `hover:shadow-sm`), never on resting dashboard tiles.
- Don't color every card. A single saturated accent inside an otherwise desaturated system; deltas are the only place green/red appears.
- Media: enforce a fixed aspect ratio (`aspect-square` / `aspect-video`) + `object-cover` + `loading="lazy"` so grids stay even.

---

## Variants

### Variant A — Stat / KPI card with trend delta + sparkline (default / workhorse)

Muted label, big `tabular-nums` value, a directional trend pill (`text-success` up / `text-destructive` down), and an optional dependency-free inline-SVG sparkline whose fill is keyed to trend direction. Rendered `size="sm"` and tiled 4-across. This is the full code below.

### Variant B — Product / content card, whole-surface clickable (accessible stretched link)

Media on top, title as the only semantic link, a rating, a price, and an "Add to cart" CTA. The whole card is clickable via the `::after` stretched-link trick, but only the heading is the link — and the CTA is lifted above the overlay with `relative z-10` so it stays independently clickable. Code included below the main example.

*(For marketing **feature / bento** cards, keep this anatomy but go softer — `rounded-2xl`/`rounded-3xl`, a subtle gradient fill, and one or two hero tiles spanning extra columns via `md:col-span-2 md:row-span-2` over `auto-rows`. Reserve cursor-follow/hover-gradient flourishes for marketing surfaces; never on dense dashboard tiles.)*

---

## Interaction / state matrix

Every state below must be defined — skipping any is where cards start to feel cheap.

| State | Treatment |
|---|---|
| **Default** | `bg-card`, hairline `ring-foreground/10`, no shadow. |
| **Hover** (clickable only) | Lift signal: `hover:bg-accent/40` or `hover:shadow-sm`; add `cursor-pointer` (a real `<a>` gives it for free). Resting dashboard tiles get **no** hover unless they drill down. |
| **Focus / focus-within** | Ring on the whole card when the inner link is focused: `focus-within:ring-2 focus-within:ring-ring`. Never strip focus outlines. |
| **Active / pressed** | Subtle only — `active:scale-[.99]` or a slightly darker bg. |
| **Selected** | Persistent `ring-2 ring-primary` + optional check affordance. Not color-only. |
| **Loading** | **Skeleton that matches the final layout** (same heights/widths, same slots) to prevent layout shift — never a bare spinner. |
| **Empty** | Icon/illustration + one-line explanation + optional CTA inside the card frame; don't render a broken tile. |
| **Error** | Inline message + retry; don't silently collapse the card. Never flash `$0`/`NaN` mid-fetch. |
| **Disabled** | `opacity-50 pointer-events-none`. |
| **Live update** | Value swaps in place (fixed by `tabular-nums`); wrap in `aria-live="polite"` if it updates without user action. |
| **Theme** | Light/dark both derive from tokens; verify the delta colors and the dark card-vs-bg step both read. |

---

## Responsive behavior

- **Design single-column first**, then 2-up on tablet, 3-4-up on desktop. The majority of traffic is mobile; test at **375px with real content**, not lorem.
- **Stat grid**: `grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4`. Product grid: `sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4`.
- **Keep tiles equal height per row.** Truncate variable text with `line-clamp-2` and reserve heights (e.g. a `min-h` on the value block) so a KPI row never reads jagged.
- **Cap the default KPI count at ~5-7.** Showing the priority metrics first and hiding the rest behind an expand measurably cuts time-to-insight; more tiles is noise.
- **Media aspect ratio is fixed** (`aspect-square`) so image cards line up regardless of source dimensions.
- Gap: `gap-4` (16px) tight, `gap-6` (24px) comfortable. Radius stays consistent within a surface.

---

## Accessibility

Clickable cards are the part everyone gets wrong. The rules:

- **Make the heading text the link, not the whole `<div>`.** Wrapping the entire card in one `<a>` produces a giant useless link label and swallows nested interactive content.
- **Stretch the hit area with a pseudo-element.** Card is `relative`; the heading link gets `after:absolute after:inset-0`, so the whole surface is clickable while only the heading is the semantic link. Bump real secondary actions (the CTA) above the overlay with `relative z-10`. (Tradeoff: the overlay blocks text selection — fine for tiles; if selecting body text matters, drop the overlay and use a JS click handler that ignores drags.)
- **Group cards in a list** — `<ul>`/`<li>` — so screen readers can enumerate and jump between them.
- **Source order = heading first.** Use CSS `order`/flex ordering to move an image above it visually if needed.
- **Focus visibility**: surface a ring on the card via `focus-within:ring-2 focus-within:ring-ring`; never remove outlines.
- **Decorative visuals are hidden**: sparklines, trend arrows, and rating stars get `aria-hidden`; the number and an `sr-only` "increase"/"decrease" carry the meaning. Don't encode trend by color alone.
- **Meaningful images get real `alt`**; only truly decorative ones get `alt=""`.
- **Contrast**: verify muted label text and the green/red deltas meet WCAG in both themes — the `--success`/`--destructive` tokens above are tuned for it.
- **Reduced motion**: gate hover scale / image zoom behind `motion-safe:`.

---

## Anti-slop callout

Ship-blockers that scream "AI generated a card grid":

- **Value jitter** — metrics without `tabular-nums` that reflow width when they update. The most obvious dashboard tell.
- **Jagged heights** — variable content with no `line-clamp` / reserved height, so the grid rhythm breaks row to row.
- **Whole-card single `<a>` wrapper** — kills nested links and gives the card a useless accessible name. Use the stretched-link trick.
- **Shadow-heavy dark mode** — floaty `shadow-xl` on every dark tile. Shadows are the worst depth cue on dark surfaces; step the card background *lighter* than the app bg instead (layered elevation).
- **Overloading** — five badges, three icons, two CTAs, metadata shrunk below 14px to fit. One concept, one primary action, ≤3 clickable elements.
- **Scattered actions** — buttons placed unpredictably per card. Group them in `CardAction` (header) or `CardFooter`.
- **Spinner-only loading** — a centered spinner that then pops the layout in. Use a skeleton that matches the final slots.
- **Cards for the wrong job** — a "card" grid that's really a data table. If items are uniform and comparable, use a list or table.
- **Rainbow of accents** — a different color per card. One accent, used sparingly; color lives in the deltas.
- **Hardcoded hex** — breaks dark mode and re-theming. Everything through tokens.
- **Marketing flourishes on data tiles** — cursor-follow spotlights and hover gradients on dense KPIs; motion + data = noise.

---

## Complete code

Drop-in and copy-pasteable. Requires shadcn/ui `card`, `badge`, `button`, `skeleton` and `lucide-react`. The sparkline is a self-contained inline SVG (no charting dependency). Tailwind v4.

```tsx
// components/stat-card.tsx
"use client";

import * as React from "react";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";

import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export type Stat = {
  id: string;
  label: string;
  /** Preformatted for display — format upstream with Intl.NumberFormat. */
  value: string;
  /** Signed percentage change, e.g. 12.5 or -3.2. */
  delta: number;
  /** Context for the delta, e.g. "vs last month". */
  deltaLabel?: string;
  /** Optional sparkline series, oldest → newest. */
  series?: number[];
  /** Optional drill-down; makes the whole tile clickable. */
  href?: string;
};

/* -------------------------------------------------------------------------- */
/* Trend badge — directional, token-colored, screen-reader labeled            */
/* -------------------------------------------------------------------------- */

function TrendBadge({ delta }: { delta: number }) {
  const positive = delta >= 0;
  const Icon = positive ? ArrowUpRight : ArrowDownRight;

  return (
    <Badge
      variant="outline"
      className={cn(
        "gap-0.5 rounded-md px-1.5 py-0.5 font-medium tabular-nums",
        positive ? "text-success" : "text-destructive",
      )}
    >
      <Icon aria-hidden className="size-3" />
      {positive ? "+" : ""}
      {delta.toFixed(1)}%
      <span className="sr-only">{positive ? "increase" : "decrease"}</span>
    </Badge>
  );
}

/* -------------------------------------------------------------------------- */
/* Sparkline — dependency-free inline SVG, no axes, fill keyed to trend        */
/* -------------------------------------------------------------------------- */

function Sparkline({
  data,
  positive,
  className,
}: {
  data: number[];
  positive: boolean;
  className?: string;
}) {
  const gradientId = React.useId();
  const W = 100;
  const H = 32;

  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;

  const points = data.map((d, i) => ({
    x: (i / (data.length - 1)) * W,
    y: H - ((d - min) / range) * H,
  }));

  const line = points
    .map((p, i) => `${i === 0 ? "M" : "L"}${p.x.toFixed(2)},${p.y.toFixed(2)}`)
    .join(" ");
  const area = `${line} L${W},${H} L0,${H} Z`;

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      preserveAspectRatio="none"
      aria-hidden
      className={cn(
        "h-10 w-full overflow-visible",
        positive ? "text-success" : "text-destructive",
        className,
      )}
    >
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="currentColor" stopOpacity={0.2} />
          <stop offset="100%" stopColor="currentColor" stopOpacity={0} />
        </linearGradient>
      </defs>
      <path d={area} fill={`url(#${gradientId})`} />
      <path
        d={line}
        fill="none"
        stroke="currentColor"
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  );
}

/* -------------------------------------------------------------------------- */
/* Stat card                                                                   */
/* -------------------------------------------------------------------------- */

export function StatCard({ stat }: { stat: Stat }) {
  const positive = stat.delta >= 0;
  const interactive = Boolean(stat.href);

  return (
    <Card
      size="sm"
      className={cn(
        "relative overflow-hidden",
        interactive &&
          "transition-colors hover:bg-accent/40 focus-within:ring-2 focus-within:ring-ring",
      )}
    >
      <CardHeader>
        <CardDescription>{stat.label}</CardDescription>
        <CardTitle className="text-3xl font-semibold tracking-tight tabular-nums">
          {interactive ? (
            // Stretched link: whole tile clickable, only the value is the link.
            <a
              href={stat.href}
              className="after:absolute after:inset-0 focus:outline-none"
            >
              {stat.value}
            </a>
          ) : (
            stat.value
          )}
        </CardTitle>
        <CardAction>
          <TrendBadge delta={stat.delta} />
        </CardAction>
      </CardHeader>

      {(stat.series || stat.deltaLabel) && (
        <CardContent className="space-y-2 pt-0">
          {stat.series && <Sparkline data={stat.series} positive={positive} />}
          {stat.deltaLabel && (
            <p className="text-xs text-muted-foreground">{stat.deltaLabel}</p>
          )}
        </CardContent>
      )}
    </Card>
  );
}

/* -------------------------------------------------------------------------- */
/* Skeleton — matches the real layout to avoid layout shift                    */
/* -------------------------------------------------------------------------- */

export function StatCardSkeleton() {
  return (
    <Card size="sm" aria-hidden>
      <CardHeader>
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-8 w-28" />
        <CardAction>
          <Skeleton className="h-5 w-14 rounded-md" />
        </CardAction>
      </CardHeader>
      <CardContent className="pt-0">
        <Skeleton className="h-10 w-full" />
      </CardContent>
    </Card>
  );
}

/* -------------------------------------------------------------------------- */
/* Grid — equal-height tiles in a list, single column → 4-up                   */
/* -------------------------------------------------------------------------- */

export function StatGrid({
  stats,
  loading,
}: {
  stats: Stat[];
  loading?: boolean;
}) {
  return (
    <section aria-label="Key metrics">
      <ul className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {loading
          ? Array.from({ length: 4 }).map((_, i) => (
              <li key={i}>
                <StatCardSkeleton />
              </li>
            ))
          : stats.map((stat) => (
              <li key={stat.id}>
                <StatCard stat={stat} />
              </li>
            ))}
      </ul>
    </section>
  );
}

/* -------------------------------------------------------------------------- */
/* Demo data + usage                                                           */
/* -------------------------------------------------------------------------- */

const DEMO_STATS: Stat[] = [
  {
    id: "revenue",
    label: "Revenue",
    value: "$48.2k",
    delta: 12.5,
    deltaLabel: "vs last month",
    href: "/dashboard/revenue",
    series: [30, 32, 31, 35, 34, 38, 42, 40, 45, 48],
  },
  {
    id: "customers",
    label: "New customers",
    value: "1,240",
    delta: 8.1,
    deltaLabel: "vs last month",
    series: [800, 820, 900, 880, 950, 1000, 1100, 1180, 1210, 1240],
  },
  {
    id: "churn",
    label: "Churn rate",
    value: "2.4%",
    delta: -0.6,
    deltaLabel: "vs last month",
    series: [3.4, 3.3, 3.1, 3.0, 2.9, 2.8, 2.7, 2.6, 2.5, 2.4],
  },
  {
    id: "active",
    label: "Active users",
    value: "9,317",
    delta: -3.2,
    deltaLabel: "vs last month",
    series: [10200, 10100, 9900, 9800, 9700, 9600, 9500, 9450, 9380, 9317],
  },
];

export function DashboardStats() {
  return <StatGrid stats={DEMO_STATS} />;
}
```

### Variant B — accessible clickable product card

```tsx
// components/product-card.tsx
import { Star } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export type Product = {
  id: string;
  name: string;
  href: string;
  price: string; // preformatted with Intl.NumberFormat
  image: string;
  rating: number;
  badge?: string;
};

export function ProductCard({ product }: { product: Product }) {
  return (
    <Card className="group relative gap-0 overflow-hidden py-0 transition-shadow hover:shadow-sm focus-within:ring-2 focus-within:ring-ring">
      <div className="relative aspect-square overflow-hidden bg-muted">
        <img
          src={product.image}
          alt={product.name}
          loading="lazy"
          className="size-full object-cover transition-transform duration-300 motion-safe:group-hover:scale-105"
        />
        {product.badge && (
          <Badge className="absolute left-3 top-3">{product.badge}</Badge>
        )}
      </div>

      <CardHeader className="pt-4">
        <CardTitle className="text-base font-medium">
          {/* Stretched link: whole card clickable, heading is the only link. */}
          <a
            href={product.href}
            className="after:absolute after:inset-0 focus:outline-none"
          >
            {product.name}
          </a>
        </CardTitle>
        <div className="flex items-center gap-1 text-sm text-muted-foreground">
          <Star aria-hidden className="size-3.5 fill-current text-warning" />
          <span className="tabular-nums">{product.rating.toFixed(1)}</span>
        </div>
      </CardHeader>

      <CardContent className="pb-0">
        <p className="text-lg font-semibold tabular-nums">{product.price}</p>
      </CardContent>

      <CardFooter className="pt-4 pb-4">
        {/* Secondary action must sit ABOVE the stretched-link overlay. */}
        <Button size="sm" className="relative z-10 w-full">
          Add to cart
        </Button>
      </CardFooter>
    </Card>
  );
}
```

### Notes on the implementation

- **`tabular-nums` everywhere a number lives** (value, delta, rating, price). Fixed-width digits mean a live dashboard never reflows when a metric ticks.
- **The sparkline is dependency-free.** It normalizes the series into a `0-100 × 0-32` viewBox, draws a line + a gradient area under it, and uses `preserveAspectRatio="none"` to stretch to any tile width while `vectorEffect="non-scaling-stroke"` keeps the 1.5px line crisp. Fill color inherits `currentColor`, keyed to `text-success`/`text-destructive` by trend direction. `React.useId()` gives the gradient a collision-safe id across many tiles. (Swap in shadcn's Recharts `ChartContainer` with `--chart-1..5` if you want tooltips.)
- **Trend semantics aren't color-only**: the arrow direction, the `+`/`-` sign, and an `sr-only` "increase"/"decrease" all carry the meaning; the arrow itself is `aria-hidden`.
- **Stretched link, done right**: `Card` is `relative`, the heading/value link gets `after:absolute after:inset-0`, and `focus-within:ring-2 focus-within:ring-ring` surfaces the focus ring on the whole card. In the product card, the "Add to cart" button is lifted with `relative z-10` so it stays independently clickable above the overlay.
- **Skeletons mirror the real slots** (label, value, trend, sparkline) at matching sizes, so swapping loading → loaded causes zero layout shift.
- **Cards live in a `<ul>`** with `aria-label` on the section, so assistive tech can enumerate the metrics.
- **`size="sm"`** tightens `--card-spacing` to 12px for dense dashboard tiles in one place; the product card keeps the default 16px.
- **Dark-mode elevation** comes from `--card` being stepped *lighter* than `--background` in the token layer — no shadows required on resting tiles; hover adds only a subtle `bg-accent/40` (stat) or `shadow-sm` (product).
- All colors are semantic tokens (`bg-card`, `text-muted-foreground`, `text-success`, `text-destructive`, `text-warning`, `bg-accent`, `ring-ring`) — light/dark and re-theming come free.
