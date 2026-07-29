# Pricing Section / Table

> A tier-card pricing section with an annual/monthly billing toggle, a highlighted recommended plan, and per-plan CTAs. Built with React + Tailwind v4 + shadcn/ui. The kind Vercel/Linear ships: dark-friendly, one accent color, restrained motion, `tabular-nums` prices that never jiggle.

## Contents

- [When to use it](#when-to-use-it) — 2–4 self-serve plans, or anchoring a pricing page above a comparison table
- [Anatomy](#anatomy) — header, billing toggle, tier cards, footnote
- [Token-driven styling](#token-driven-styling) — the token layer plus the recommended-tier tint
- [Variants](#variants) — 3-tier with billing toggle · in-app "current plan" upgrade screen · cards + comparison table
- [Interaction / state matrix](#interaction--state-matrix) — toggle, cards and CTAs, state by state
- [Responsive behavior](#responsive-behavior) — two-up on tablet, recommended-first on mobile, no scaling in a single column
- [Accessibility](#accessibility) — the toggle is a radiogroup, not a lone switch; announce price changes
- [Anti-slop callout](#anti-slop-callout) — prices that jiggle, every emphasis at once
- [Complete code](#complete-code) — drop-in `PricingSection` with an accessible segmented toggle

---

## When to use it

Reach for this pattern when you need to:

- **Present 2-4 self-serve plans** side by side and drive a purchase/upgrade decision (Free → Pro → Enterprise is the canonical shape).
- **Anchor a pricing page** above a deeper comparison table and FAQ. Cards make the decision; the table below serves due diligence.
- **Offer a billing choice** (monthly vs annual) where annual is discounted.

Do **not** use it when:

- You have a **single product, single price** — use a single-plan spotlight (one big price + a feature list to the side), not a grid.
- You have **>4 tiers** — decision paralysis kills conversion (4+ tiers convert meaningfully worse than 3). Collapse to 3 marketed tiers and push the rest into a comparison table or an "add-ons" section.
- Pricing is **fully usage-based** with no discrete tiers — use a calculator (slider/input → live price) instead. You can still wrap it in this section's header + shell.

---

## Anatomy

```
section  (vertical rhythm, centered container)
├─ header            eyebrow? + H2 headline + one-line subhead
├─ billing toggle    segmented Monthly | Annual  +  "Save 20%" pill   (defaults to Annual)
│                    └─ visually-hidden radiogroup for a11y + keyboard
├─ card grid         2-4 tier cards, recommended card centered/highlighted
│   └─ Card (per tier)
│      ├─ "Most popular" badge      (recommended tier only, anchored top)
│      ├─ tier name                 (label / small heading)
│      ├─ price block               big tabular-nums numeral + /mo period + billed-note
│      ├─ description               one line: who it's for
│      ├─ primary CTA               full-width; solid on recommended, outline elsewhere
│      ├─ Separator
│      └─ feature list              4-8 rows, check icon + label, "Everything in X, plus…"
└─ footnote          links to full comparison table / all features   (optional)
```

Card internal order is load-bearing: **name → price → description → CTA → features**. The CTA sits *above* the feature list so the decision is reachable without scrolling the card; the features justify the click after.

The **Enterprise/custom** card swaps the numeral for `Custom` / "Let's talk" and the CTA for **Contact sales**.

**Assume the visitor jumped here.** Pricing sits deep in the page — the median measured landing
page is 11.2 viewports and only 26% of viewing time falls past the second screenful
([NN/g](https://www.nngroup.com/articles/scrolling-and-attention/)). So: **repeat the hero's
primary CTA verbatim** at the top of the section, allow **no more than two** actions per plan
card — the CTA plus at most one low-emphasis link, never three — and make the section
self-explanatory with no context carried down from above.

---

## Token-driven styling

Everything maps to shadcn/ui CSS variables — **no hardcoded hex**. Light and dark both fall out of the token layer. The recommended-tier tint is the only custom token you may want to add.

```css
/* app/globals.css — shadcn v4 token layer (abridged) */
:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --border: oklch(0.922 0 0);
  --ring: oklch(0.708 0 0);
  --radius: 0.75rem;

  /* custom: subtle tint behind the recommended card. Derive from --primary. */
  --pricing-highlight: color-mix(in oklch, var(--primary) 4%, var(--card));
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --card: oklch(0.205 0 0);
  --card-foreground: oklch(0.985 0 0);
  --primary: oklch(0.922 0 0);
  --primary-foreground: oklch(0.205 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --border: oklch(1 0 0 / 10%);
  --ring: oklch(0.556 0 0);

  --pricing-highlight: color-mix(in oklch, var(--primary) 8%, var(--card));
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-muted-foreground: var(--muted-foreground);
  --color-border: var(--border);
  --color-ring: var(--ring);
  --color-pricing-highlight: var(--pricing-highlight);
  --radius-lg: var(--radius);
}
```

Then in JSX you only ever reach for semantic classes: `bg-card`, `text-foreground`, `text-muted-foreground`, `border-primary`, `ring-ring`, `bg-pricing-highlight`, `text-primary`. Swap the accent once (`--primary`) and the whole section re-themes — including the highlight tint, because it's `color-mix`-derived.

**Rules of thumb**

- Price numeral: `text-4xl md:text-5xl font-semibold tracking-tight tabular-nums`. `tabular-nums` is non-negotiable — it stops the price from reflowing width when it swaps on toggle.
- Recommended emphasis = pick **2-3** of {accent border+ring, `bg-pricing-highlight`, elevated shadow, `lg:scale-[1.03]`, badge, solid CTA}. All of them at once is slop.
- Check icons: `text-primary` for included, `text-muted-foreground` for muted — but never rely on color alone (see a11y).

---

## Variants

### Variant A — 3-tier cards with billing toggle (default / workhorse)

Free/Starter → **Pro (highlighted, center)** → Enterprise. Left→right reads simple→complex. This is the full code example below.

### Variant B — Cards + "Current plan" state (in-app upgrade screen)

Same grid, but the app knows the signed-in user's plan. The active tier renders a `Badge` "Current plan", its CTA becomes a disabled "Your plan" button, and lower tiers can show "Downgrade" while higher tiers show "Upgrade". Pass a `currentPlanId` prop; derive each card's CTA from it. (Wiring shown in code comments.)

### Variant C — Cards + comparison table combo (Vercel pattern)

Keep the cards for the decision, then render a full `<table>` below with plans as columns and grouped feature rows. Give the plan-header row `position: sticky; top: 0` so columns stay identified while scrolling, group rows under labeled `<th>` section headers, and make long sections collapsible with an `Accordion`. Frame cells positively ("Unlimited seats") rather than as caps.

---

## Interaction / state matrix

| Surface | States | Behavior |
|---|---|---|
| **Billing toggle** | Monthly selected / Annual selected | Defaults to **Annual**. Switching updates every price + billed-note instantly; savings pill sits by the Annual label. Keyboard: arrow keys move between options (native radios). |
| **Price** | monthly value / annual value | Swaps in place, `tabular-nums` (no width jump). Wrapped in `aria-live="polite"` so SR users hear the new value. |
| **Card emphasis** | default / recommended | Recommended: accent border + ring + `bg-pricing-highlight` + shadow + `lg:scale-[1.03]` + badge. |
| **CTA button** | default, hover, focus-visible, active, disabled | Solid (`variant="default"`) on recommended, `outline` elsewhere. Visible `focus-visible` ring; ≥44×44px hit area. Disabled only for "Current plan". |
| **Card hover** | rest / hover | Subtle: `hover:border-foreground/20` or a small shadow lift. Recommended card already elevated — don't double-lift. |
| **Feature row** | included / muted / differentiator | Check icon + text (included), muted check + muted text (muted). Prefer *omitting* excluded features over listing `x` rows. |
| **Current plan** (Variant B) | is-current / upgrade / downgrade | Badge + disabled "Your plan"; other cards say "Upgrade"/"Downgrade". |
| **Async data** | loading / error | Skeleton blocks for price + CTA while fetching; inline retry on error. Never show `$0`/`NaN` mid-fetch. |
| **Theme** | light / dark | Both derive from tokens; verify the accent *and* `--pricing-highlight` read in both. |

---

## Responsive behavior

- **Grid**: `grid gap-6 lg:gap-8`, `md:grid-cols-2 lg:grid-cols-3`. Two-up on tablet, single column on mobile.
- **Recommended-first on mobile**: on a single-column stack the highlighted plan should appear at or near the top so it isn't buried. Either order the data with the recommended tier first, or use `order-first lg:order-none` on the recommended card so it leads on mobile but keeps its center slot on desktop.
- **`lg:scale-[1.03]`** only from `lg` up — never scale a card in a single-column stack (it just causes horizontal overflow).
- **Toggle**: stays centered; on long pages consider `sticky top-4` so it's reachable after scrolling into the cards.
- **Comparison table (Variant C)**: never horizontal-scroll on mobile. Stack vertically per-plan, or offer a "pick 2 to compare" control. Horizontal-scroll tables tank mobile conversion.
- Container: `mx-auto max-w-6xl px-4 md:px-6`; section rhythm `py-16 md:py-24`.

---

## Accessibility

- **Billing toggle = radiogroup, not a lone switch.** Two *named* options ("Monthly", "Annual") map to a `radiogroup` with a visible/associated group label. The example uses native `<input type="radio">` inside a `<fieldset>` with a `<legend>` — free keyboard support (arrow keys), free single-selection semantics, and SR announces the selected option. (A `role="switch"` is only appropriate if the control is genuinely on/off; if you use one, its label must stay fixed — "Billing period" — and not change with state.)
- **Announce price changes**: wrap the price in `aria-live="polite"` so toggling billing is announced to screen readers.
- **CTAs are real elements**: `<button>` for actions, `<a>` for navigation. Visible `focus-visible` ring (shadcn `Button` ships this). Minimum 44×44px hit target — `w-full` + default button height covers it.
- **Don't encode meaning by color alone**: pair every check/muted state with an icon *and* text, or omit excluded features. Add `aria-hidden` to purely decorative icons and give screen-reader-only context where a row's inclusion state matters.
- **Headings**: section `<h2>`, tier names `<h3>` — keep the outline linear.
- **Comparison table (Variant C)**: a real `<table>` with `<th scope="col">` for plans and `<th scope="row">` for features. Not a grid of divs.
- **Reduced motion**: gate the scale/hover lift behind `motion-safe:` (or respect `prefers-reduced-motion`) so the highlight doesn't animate for users who opt out.

---

## Anti-slop callout

Ship-blockers that scream "AI generated a pricing page":

- **Prices that jiggle on toggle** — forgetting `tabular-nums`. The single most obvious tell.
- **Every emphasis at once** — border + ring + scale + shadow + glow + gradient + badge + inverted bg on the recommended card. Pick 2-3. Restraint is the Linear/Vercel signature.
- **Rainbow of accents** — a different color per tier. One accent, used once, on a near-neutral/dark surface.
- **Monthly default with the discount hidden** — sticker shock. Default to **annual**, show the *concrete* savings ("$240/yr", not just "20%"), and keep monthly available (never force annual — it reads as coercion).
- **Feature-parity walls** — repeating all 12 features on all 3 cards. Lead each higher tier with "Everything in [previous], plus…".
- **Vague CTAs** — "Learn more" / "Click here". Use "Start free", "Get started", "Contact sales".
- **`x` rows for excluded features in muted gray** — mostly noise; omit them and let "everything in X plus…" imply the ladder.
- **Hover-only tooltips** for feature explanations — they cover content, break on touch, and fail a11y. Use click/accordion reveal.
- **Hardcoded hex** instead of tokens → breaks dark mode and re-theming. Everything through CSS vars.
- **`>3` competing interactive widgets** in one section — a toggle *and* a slider *and* a currency picker *and* an add-on selector fights the one decision you want the user to make.

---

## Complete code

Drop-in, copy-pasteable. Requires shadcn/ui `card`, `button`, `badge`, `separator` and `lucide-react`. The billing toggle is a self-contained accessible segmented radiogroup (no extra dependency). Tailwind v4.

```tsx
// components/pricing-section.tsx
"use client";

import * as React from "react";
import { Check } from "lucide-react";

import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

type BillingPeriod = "monthly" | "annual";

type Tier = {
  id: string;
  name: string;
  description: string;
  /** Price per month, in whole currency units. `null` = custom/contact sales. */
  price: { monthly: number; annual: number } | null;
  cta: string;
  href: string;
  popular?: boolean;
  features: string[];
};

const CURRENCY = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const TIERS: Tier[] = [
  {
    id: "starter",
    name: "Starter",
    description: "For individuals shipping their first project.",
    price: { monthly: 0, annual: 0 },
    cta: "Start for free",
    href: "/signup?plan=starter",
    features: [
      "1 project",
      "Community support",
      "1 GB storage",
      "Basic analytics",
    ],
  },
  {
    id: "pro",
    name: "Pro",
    description: "For teams that need scale and collaboration.",
    price: { monthly: 24, annual: 19 }, // annual = per-month when billed yearly
    cta: "Start free trial",
    href: "/signup?plan=pro",
    popular: true,
    features: [
      "Everything in Starter, plus:",
      "Unlimited projects",
      "Priority support",
      "100 GB storage",
      "Advanced analytics",
      "Team roles & permissions",
    ],
  },
  {
    id: "enterprise",
    name: "Enterprise",
    description: "For organizations with security and scale needs.",
    price: null, // custom
    cta: "Contact sales",
    href: "/contact",
    features: [
      "Everything in Pro, plus:",
      "SSO & SAML",
      "SLA & dedicated support",
      "Audit logs",
      "Custom contracts",
    ],
  },
];

const ANNUAL_SAVINGS_PCT = 20;

/* -------------------------------------------------------------------------- */
/* Billing toggle — accessible segmented radiogroup                            */
/* -------------------------------------------------------------------------- */

function BillingToggle({
  value,
  onChange,
}: {
  value: BillingPeriod;
  onChange: (next: BillingPeriod) => void;
}) {
  const options: { value: BillingPeriod; label: string }[] = [
    { value: "monthly", label: "Monthly" },
    { value: "annual", label: "Annual" },
  ];

  return (
    <fieldset className="flex flex-col items-center gap-2">
      <legend className="sr-only">Billing period</legend>
      <div
        role="radiogroup"
        aria-label="Billing period"
        className="inline-flex items-center rounded-full border border-border bg-card p-1"
      >
        {options.map((opt) => {
          const checked = value === opt.value;
          return (
            <label
              key={opt.value}
              className={cn(
                "relative flex cursor-pointer items-center gap-2 rounded-full px-4 py-1.5",
                "text-sm font-medium transition-colors",
                "focus-within:outline-none focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2 focus-within:ring-offset-background",
                checked
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground",
              )}
            >
              <input
                type="radio"
                name="billing-period"
                value={opt.value}
                checked={checked}
                onChange={() => onChange(opt.value)}
                className="sr-only"
              />
              {opt.label}
              {opt.value === "annual" && (
                <Badge
                  variant={checked ? "secondary" : "outline"}
                  className="px-1.5 py-0 text-[11px] font-semibold leading-5"
                >
                  Save {ANNUAL_SAVINGS_PCT}%
                </Badge>
              )}
            </label>
          );
        })}
      </div>
    </fieldset>
  );
}

/* -------------------------------------------------------------------------- */
/* Price — swaps in place, tabular-nums, announced to screen readers           */
/* -------------------------------------------------------------------------- */

function Price({ tier, period }: { tier: Tier; period: BillingPeriod }) {
  if (tier.price === null) {
    return (
      <div className="flex min-h-[3.5rem] items-baseline gap-1">
        <span className="text-4xl font-semibold tracking-tight md:text-5xl">
          Custom
        </span>
      </div>
    );
  }

  const perMonth = tier.price[period];
  const billedNote =
    period === "annual"
      ? tier.price.annual === 0
        ? "Free forever"
        : `${CURRENCY.format(tier.price.annual * 12)} billed annually`
      : tier.price.monthly === 0
        ? "No credit card required"
        : "billed monthly";

  return (
    <div>
      <div
        className="flex min-h-[3.5rem] items-baseline gap-1"
        aria-live="polite"
      >
        <span className="text-4xl font-semibold tracking-tight tabular-nums md:text-5xl">
          {CURRENCY.format(perMonth)}
        </span>
        <span className="text-sm text-muted-foreground">/mo</span>
      </div>
      <p className="mt-1 text-sm text-muted-foreground">{billedNote}</p>
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/* Tier card                                                                   */
/* -------------------------------------------------------------------------- */

function TierCard({
  tier,
  period,
  currentPlanId,
}: {
  tier: Tier;
  period: BillingPeriod;
  currentPlanId?: string; // Variant B: the signed-in user's plan
}) {
  const isCurrent = currentPlanId === tier.id;

  // Variant B: derive CTA from the current plan when signed in.
  const ctaLabel = isCurrent ? "Your plan" : tier.cta;

  return (
    <Card
      className={cn(
        "relative flex flex-col rounded-2xl transition-shadow",
        tier.popular
          ? // recommended emphasis: border + ring + tint + shadow + scale (motion-safe)
            "border-primary bg-pricing-highlight shadow-lg ring-1 ring-primary lg:motion-safe:scale-[1.03] order-first lg:order-none"
          : "hover:border-foreground/20 hover:shadow-sm",
      )}
    >
      {tier.popular && (
        <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 shadow-sm">
          Most popular
        </Badge>
      )}

      <CardHeader className="gap-2">
        <CardTitle asChild>
          <h3 className="text-base font-semibold">{tier.name}</h3>
        </CardTitle>
        <CardDescription>{tier.description}</CardDescription>
      </CardHeader>

      <CardContent className="flex flex-1 flex-col">
        <Price tier={tier} period={period} />

        <Button
          asChild={!isCurrent}
          disabled={isCurrent}
          variant={tier.popular ? "default" : "outline"}
          size="lg"
          className="mt-6 w-full"
          aria-current={isCurrent ? "true" : undefined}
        >
          {isCurrent ? (
            <span>{ctaLabel}</span>
          ) : (
            <a href={tier.href}>{ctaLabel}</a>
          )}
        </Button>

        {isCurrent && (
          <p className="mt-2 text-center text-xs text-muted-foreground">
            You&apos;re on this plan
          </p>
        )}

        <Separator className="my-6" />

        <ul className="flex flex-col gap-3 text-sm">
          {tier.features.map((feature, i) => {
            // "Everything in X, plus:" is a lead-in, not a checkable feature.
            const isLeadIn = feature.endsWith("plus:");
            if (isLeadIn) {
              return (
                <li key={feature} className="font-medium text-foreground">
                  {feature}
                </li>
              );
            }
            return (
              <li key={feature} className="flex items-start gap-3">
                <Check
                  aria-hidden="true"
                  className="mt-0.5 size-4 shrink-0 text-primary"
                />
                <span className="text-muted-foreground">{feature}</span>
              </li>
            );
          })}
        </ul>
      </CardContent>

      <CardFooter />
    </Card>
  );
}

/* -------------------------------------------------------------------------- */
/* Section                                                                     */
/* -------------------------------------------------------------------------- */

export function PricingSection({
  currentPlanId,
}: {
  currentPlanId?: string;
}) {
  // Default to annual — anchor to the lower per-month number, lift annual adoption.
  const [period, setPeriod] = React.useState<BillingPeriod>("annual");

  return (
    <section className="py-16 md:py-24" aria-labelledby="pricing-heading">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <header className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-medium text-primary">Pricing</p>
          <h2
            id="pricing-heading"
            className="mt-3 text-3xl font-semibold tracking-tight text-foreground md:text-4xl"
          >
            Simple, transparent pricing
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Start free. Upgrade when your team grows. Cancel anytime.
          </p>
        </header>

        <div className="mt-8 flex justify-center">
          <BillingToggle value={period} onChange={setPeriod} />
        </div>

        <div className="mt-12 grid items-start gap-6 md:grid-cols-2 lg:grid-cols-3 lg:gap-8">
          {TIERS.map((tier) => (
            <TierCard
              key={tier.id}
              tier={tier}
              period={period}
              currentPlanId={currentPlanId}
            />
          ))}
        </div>

        <p className="mt-10 text-center text-sm text-muted-foreground">
          Need a detailed breakdown?{" "}
          <a
            href="#compare"
            className="font-medium text-foreground underline underline-offset-4 hover:text-primary"
          >
            Compare all features
          </a>
        </p>
      </div>
    </section>
  );
}
```

### Notes on the implementation

- **Annual price model**: `price.annual` is the *per-month* rate when billed yearly; the billed-note multiplies it by 12 to show the concrete yearly total ("$228 billed annually"). This shows both the low anchor number and the real dollar amount — the research-backed pattern.
- **`tabular-nums` + `min-h`** on the price block: numerals stay fixed-width and the block reserves its height, so switching billing never reflows the card.
- **`aria-live="polite"`** on the price announces the new value on toggle.
- **Accessible toggle**: native radios inside a `role="radiogroup"` labelled `<fieldset>`/`<legend>` — arrow-key navigation and single-selection are free from the platform; `focus-within` surfaces a visible ring on the styled label.
- **Recommended emphasis** is deliberately restrained: border + ring + `bg-pricing-highlight` + shadow + `lg:motion-safe:scale-[1.03]` + one badge + solid CTA. Scale is gated on `lg` and `motion-safe`.
- **`order-first lg:order-none`** puts Pro at the top on mobile (single column) but back in the center on desktop.
- **Variant B** is wired via `currentPlanId`: pass the signed-in user's plan id and the matching card disables its CTA to "Your plan". Extend `ctaLabel` to return "Upgrade"/"Downgrade" by comparing tier order if you want directional CTAs.
- **Lead-in rows** ("Everything in Pro, plus:") render as a label, not a checkmark row, so the feature ladder reads cleanly without repeating every feature on every card.
- All colors are semantic tokens (`bg-card`, `text-muted-foreground`, `border-primary`, `ring-primary`, `bg-pricing-highlight`, `text-primary`) — light/dark and re-theming come free.
