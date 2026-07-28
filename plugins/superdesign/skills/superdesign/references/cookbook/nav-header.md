# Marketing Nav / Header with Menu

> A sticky, full-bleed marketing header: logo left, primary nav (with dropdown + mega-menu panels) in the middle, low-emphasis "Sign in" + high-emphasis CTA on the right, and a mobile hamburger that opens a `Sheet` with the panels re-expressed as an `Accordion`. Built on shadcn/ui `NavigationMenu` (Radix) so keyboard, focus, and ARIA come for free. React + Tailwind v4. The kind Linear/Vercel/Stripe ship: slim chrome, frosted-on-scroll, monochrome + one accent, real links everywhere, restrained motion.

---

## When to use it

Reach for this pattern when you need to:

- **Anchor a marketing / product site** — the persistent top bar that carries brand (logo → home), wayfinding (primary nav), and conversion (CTA) on every page.
- **Expose a multi-level IA** where a few top-level sections fan out into grouped destinations — use a **mega menu** for "Product" (features across several areas) and a **simple dropdown** for "Resources" (a flat list).
- **Drive a single primary action** (Start free / Get started / Book a demo) that must sit in the same place on every page.

Do **not** use it when:

- You're building **app chrome for a signed-in product** — that's a dashboard shell (sidebar + top bar with account menu, search, notifications), not a marketing header. Different pattern.
- You have **one or two destinations and no CTA** — a flat bar of 2-3 text links needs none of this machinery. Skip the `NavigationMenu` entirely.
- Your nav has **>7 top-level items** — that's a fatigue/skim problem, not a component problem. Reduce to ~5 and group the rest into panels *before* you reach for code.

---

## Anatomy

```
header                          sticky top-0 z-50, full-bleed, transition bg/border on scroll
├─ skip link                    sr-only until focused → jumps to #main-content
└─ inner bar                    mx-auto max-w-7xl, h-16, flex items-center justify-between, px-4/6/8
   ├─ Left cluster              flex items-center gap-6
   │   ├─ MobileNav trigger     md:hidden — hamburger → Sheet (drawer)
   │   ├─ Logo → "/"            shrink-0, real link, mark + wordmark
   │   └─ DesktopNav            hidden md:flex — shadcn NavigationMenu
   │       └─ NavigationMenuList
   │          ├─ Item · Link            simple link (Pricing, Customers, Docs)  → navigationMenuTriggerStyle()
   │          ├─ Item · Trigger+Content  dropdown (Resources) — single-column list
   │          └─ Item · Trigger+Content  mega menu (Product) — featured card + 2-col rows
   │                                       row = icon tile + title + one-line description
   │       └─ NavigationMenuViewport     single morphing panel container (auto, from shadcn)
   └─ Right cluster             flex items-center gap-2
       ├─ (optional slot)       theme toggle / search — kept minimal
       ├─ "Sign in"             variant="ghost", hidden on xs (low emphasis)
       └─ Primary CTA           variant="default" — far right (high emphasis)

MobileNav (Sheet, side="left")
├─ SheetHeader                  logo + SheetTitle (a11y)
├─ nav · Accordion (single)     each dropdown/mega → collapsible section of icon+label rows
│                                flat links render as their own full-width rows
└─ footer (mt-auto)             Sign in (outline) + CTA (solid), pinned full-width at bottom
```

Load-bearing ordering: **CTA is always the last thing on the right.** Users look to the end of the bar for the action; moving it between pages is disorienting. "Sign in" sits immediately left of it as the quiet sibling.

Radix `NavigationMenu` deliberately **does not** use `role="menu"/"menubar"` — those are for app/OS-style composite-focus menus and confuse users on a website. This is semantic navigation: `<header>` → `<nav>` → list of real links. Don't force `role="menu"` onto it.

---

## Token-driven styling

Everything maps to shadcn/ui CSS variables — **no hardcoded hex**. Light and dark fall out of the token layer; swap `--primary` once and the CTA, active state, and focus ring all re-theme. Two small additions carry the header's own concerns.

```css
/* app/globals.css — shadcn v4 token layer (abridged) */
:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --accent: oklch(0.97 0 0);
  --accent-foreground: oklch(0.205 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
  --border: oklch(0.922 0 0);
  --ring: oklch(0.708 0 0);
  --radius: 0.625rem;

  /* header-specific */
  --header-height: 4rem;                 /* keep in sync with h-16 on the inner bar   */
  --header-bg: var(--background);        /* frosted surface tints from the page bg     */
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --accent: oklch(0.269 0 0);
  --accent-foreground: oklch(0.985 0 0);
  --primary: oklch(0.922 0 0);
  --primary-foreground: oklch(0.205 0 0);
  --border: oklch(1 0 0 / 10%);
  --ring: oklch(0.556 0 0);
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-border: var(--border);
  --color-ring: var(--ring);
  --radius-lg: var(--radius);
}

/* Sticky-header anchor offset: section tops land BELOW the bar, not under it.
   One line on the scroll container beats per-section scroll-margin-top. */
html {
  scroll-padding-top: var(--header-height);
}
```

In JSX you only ever reach for semantic classes: `bg-background`, `text-foreground`, `text-muted-foreground`, `bg-accent`, `text-accent-foreground`, `border-border`, `ring-ring`, `bg-primary`, `text-primary-foreground`.

**Rules of thumb**

- **Frosted chrome, not opaque:** `bg-background/70 backdrop-blur-lg supports-[backdrop-filter]:bg-background/60 border-b`. The `supports-[]` fallback keeps it legible where `backdrop-filter` is unavailable.
- **Animate paint, never layout.** On scroll, transition `background-color`, `border-color`, `backdrop-filter` — never height/padding. Reserve the header height so nothing under it shifts.
- **Trigger / link rest state is muted** (`text-muted-foreground`), and **every** interaction state has *more* contrast than rest (Vercel's rule). Hover → `text-foreground` + `bg-accent`.
- **Panel row** = `size-9 rounded-md border bg-muted` icon tile + `text-sm font-medium` title + `text-xs text-muted-foreground` description. Constrain the panel width (`w-[38rem] lg:w-[44rem]`) and let the Radix viewport morph between panels.

---

## Variants

### Variant A — Solid sticky, frosted (default / workhorse)

Always-frosted sticky bar over a normal (non-hero) page. Logo-left / nav-left / actions-right. This is the default of the component below (`variant="solid"`). It's what most SaaS marketing sites want.

### Variant B — Transparent-over-hero → frosted on scroll (Stripe/Vercel)

Same markup, `variant="transparent"`. The bar renders with a transparent background and a transparent bottom border while sitting over a full-bleed hero; once `scrollY` passes a small threshold (~8px) it fades in the frosted background + border. Nothing about the box model changes — only paint — so there's no layout shift. Pair it with a hero that has enough contrast under the nav (or a top scrim) so links stay legible before the frost kicks in.

Both variants share one implementation; the prop just decides whether the frosted classes are always on or gated behind the scroll threshold. (Other positioning flavors — floating pill, logo-centered/editorial — are layout swaps on the same inner bar.)

---

## Interaction / state matrix

Design each interactive surface explicitly. Rule: **every state has more contrast than rest.**

| Surface | States | Behavior |
|---|---|---|
| **Nav link (simple)** | rest / hover / focus-visible / current | Rest `text-muted-foreground`; hover `text-foreground` + `bg-accent`; `focus-visible` ring; current page → `data-active` + `aria-current="page"` (persistent accent/underline). |
| **Trigger (dropdown/mega)** | rest / hover / open / focus-visible | Space/Enter opens the panel; `data-state="open"` highlights the trigger and rotates the built-in chevron 180°. |
| **Panel (Content)** | closed / open (enter/exit) | Animates in via Radix `data-motion` + viewport CSS vars; the shared viewport morphs width/height and slides directionally when moving between triggers. |
| **Panel row** | rest / hover / focus-visible / current | Whole row is one link; hover/focus → `bg-accent`, icon tile foreground brightens; ≥44px tall for touch. |
| **CTA button** | rest / hover / active / focus-visible / disabled | Solid `variant="default"`; visible `focus-visible` ring; ≥44×44px hit area on mobile. |
| **Sign in** | rest / hover / focus-visible | `variant="ghost"`; hidden below `sm` (CTA carries mobile). |
| **Hamburger** | rest / hover / focus-visible / open | `md:hidden`; opens the Sheet; `aria-label` + toggles `aria-expanded` via the trigger. |
| **Mobile accordion section** | collapsed / expanded | One section open at a time (`type="single" collapsible`); chevron rotates on expand. |
| **Header (scroll)** | at-top / scrolled | Variant B: transparent → frosted past threshold. Variant A: frosted always. Paint-only transition. |
| **Theme** | light / dark | Both derive from tokens; verify frost legibility and ring contrast in both. |
| **Reduced motion** | motion-safe / reduce | Panel + header transitions gated so `prefers-reduced-motion` users get instant, non-animated swaps. |

If you *add* hover-to-open on top of click/keyboard (never instead of), respect the intent timings: open after ~0.5s of a stationary pointer, keep a ~0.5s close grace period, and add a diagonal "hover tunnel" tolerance. Radix gives you sane defaults here — don't set them to zero. Panels must satisfy WCAG 1.4.13: **dismissible** (Esc), **hoverable** (you can move onto the panel without it closing), and **persistent** (stays until dismissed).

---

## Responsive behavior

- **`md` is the breakpoint.** Below it: hide the desktop `NavigationMenu`, show the hamburger + `Sheet`. At/above: hide the hamburger, show the horizontal nav. Never render both.
- **Desktop → mobile is a re-expression, not a copy.** The mega menu becomes an `Accordion` inside the drawer; big tap targets, icon + label rows, no two-dimensional grid. Replicating the desktop panel verbatim on mobile is a classic tell.
- **Container:** `mx-auto max-w-7xl px-4 sm:px-6 lg:px-8`; inner bar `h-16`. Panels cap their width (`w-[38rem] lg:w-[44rem]`) and never exceed the viewport; give long panels a max-height + scroll.
- **CTA survives on mobile; "Sign in" folds** (`hidden sm:inline-flex`) so the bar doesn't crowd. The full-width "Sign in" lives at the bottom of the drawer instead.
- **Mobile drawer footer is pinned** (`mt-auto`) with Sign in + CTA full-width — the conversion path stays reachable without scrolling the link list.
- **Hit targets:** ≥24px desktop, ≥44px mobile; `touch-action: manipulation` on interactive controls to kill the 300ms double-tap zoom.

---

## Accessibility

- **Real links, always.** Every navigation target is an `<a>` / Next `<Link>` (via `asChild`) — never a `<button>` or `<div>`. This is what makes Cmd/middle/right-click, "open in new tab", copy-link, and SEO work. Buttons are only for the panel triggers and the hamburger (which *do* toggle UI, not navigate).
- **Keyboard (free from Radix `NavigationMenu`):** Space/Enter opens a Trigger's Content; Esc closes it and restores focus to the Trigger; Tab moves through focusable elements; Arrow keys move between triggers and into the open panel; Home/End jump to first/last.
- **Focus is always visible.** Every focusable element shows a `:focus-visible` ring (`focus-visible:ring-2 ring-ring ring-offset-2`). Never remove the outline; never rely on `:focus` (it flashes for mouse users).
- **Current page is announced and shown:** `aria-current="page"` + `data-active` on the active link, with a persistent visual indicator — not color alone.
- **Skip link first.** A visually-hidden "Skip to content" link is the first focusable element, jumping to `<main id="main-content">`. Combined with `scroll-padding-top`, keyboard users skip the nav and anchor targets clear the sticky bar.
- **Mobile drawer traps + restores focus** and closes on Esc (Radix `Dialog`/`Sheet` handles this). `SheetTitle` is present (visually hidden if needed) so the dialog is labelled; the trigger carries an `aria-label`.
- **Semantic structure:** `<header>` → `<nav>` → list of links; triggers expose `aria-expanded`; decorative icons get `aria-hidden`. Don't add `role="menu"`.
- **Reduced motion:** gate the panel/header transitions behind `motion-safe:` (or a `prefers-reduced-motion` query) so opt-out users get instant swaps.

---

## Anti-slop callout

Ship-blockers that scream "AI generated a navbar":

- **Too many top-level items.** More than ~5 (hard cap 7) and users skim/stall. Group into panels first.
- **Hover-only menus.** They break keyboard and touch and fail WCAG 1.4.13. Support click + keyboard; hover is at most an *additive* affordance with intent delays.
- **Zero-delay hover open/close.** Panels flicker and fire when the cursor merely crosses a trigger. Use ~0.5s open / ~0.5s close grace + a hover tunnel.
- **`<div>`/`<button>` as a navigation link.** Kills new-tab, copy-link, and SEO. Anchors only.
- **Removed focus outline** or reliance on `:focus`. Use `:focus-visible` and keep the ring.
- **No current-page indicator** — users lose their place. Wire `aria-current` + `data-active`.
- **Layout shift on scroll** — animating height/padding instead of paint. Reserve the height; transition background/border/blur only.
- **Sticky header eating anchor targets** — forgetting `scroll-padding-top`/`scroll-margin-top`, so section headings hide under the bar.
- **Desktop mega menu copied verbatim to mobile** — collapse to Sheet + Accordion instead.
- **Form widgets (search box, inputs) inside a mega menu** — they steal focus and break keyboard flow.
- **Social icons in the header** — exit doors off the conversion path; they belong in the footer.
- **CTA not pinned far-right / moving between pages** — users look to the end of the bar; keep it fixed.
- **Panel wider than the viewport with no max-height** — clips content on small screens.
- **Hardcoded hex** — breaks dark mode and re-theming. Everything through tokens.
- **Six emphasis effects on the CTA** (gradient + glow + shadow + scale + ring + border). One accent, one solid button. Restraint is the Linear/Vercel signature.

---

## Complete code

Drop-in, copy-pasteable. Requires shadcn/ui `navigation-menu`, `sheet`, `accordion`, `button` and `lucide-react`, plus the `--header-height` / `scroll-padding-top` additions above. Uses `next/link` + `usePathname` for active detection (swap for your router's equivalent, or a plain `<a>` + `props.pathname`, if you're not on Next). Tailwind v4.

```bash
npx shadcn@latest add navigation-menu sheet accordion button
```

```tsx
// components/site-header.tsx
"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  BookOpen,
  LifeBuoy,
  Menu,
  Newspaper,
  Puzzle,
  ShieldCheck,
  Sparkles,
  Users,
  Workflow,
  Zap,
  type LucideIcon,
} from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";

/* -------------------------------------------------------------------------- */
/* Nav config — data drives both desktop and mobile so they never drift        */
/* -------------------------------------------------------------------------- */

type NavLeaf = {
  title: string;
  href: string;
  description?: string;
  icon: LucideIcon;
};

type NavItem =
  | { title: string; href: string; type?: "link" }
  | { title: string; type: "dropdown"; items: NavLeaf[] }
  | { title: string; type: "mega"; featured: NavLeaf; items: NavLeaf[] };

const NAV: NavItem[] = [
  {
    title: "Product",
    type: "mega",
    featured: {
      title: "Platform overview",
      href: "/product",
      description: "See how every piece fits together in one place.",
      icon: Zap,
    },
    items: [
      {
        title: "Analytics",
        href: "/product/analytics",
        description: "Understand your traffic and funnels.",
        icon: BarChart3,
      },
      {
        title: "Automations",
        href: "/product/automations",
        description: "Trigger actions from any event.",
        icon: Workflow,
      },
      {
        title: "Integrations",
        href: "/product/integrations",
        description: "Connect the tools you already use.",
        icon: Puzzle,
      },
      {
        title: "Security",
        href: "/product/security",
        description: "SOC 2, SSO, and audit logs.",
        icon: ShieldCheck,
      },
    ],
  },
  {
    title: "Resources",
    type: "dropdown",
    items: [
      {
        title: "Blog",
        href: "/blog",
        description: "Product news and engineering.",
        icon: Newspaper,
      },
      {
        title: "Guides",
        href: "/guides",
        description: "Step-by-step tutorials.",
        icon: BookOpen,
      },
      {
        title: "Changelog",
        href: "/changelog",
        description: "What shipped, and when.",
        icon: Sparkles,
      },
      {
        title: "Community",
        href: "/community",
        description: "Join the conversation.",
        icon: Users,
      },
      {
        title: "Support",
        href: "/support",
        description: "Get help from our team.",
        icon: LifeBuoy,
      },
    ],
  },
  { title: "Pricing", href: "/pricing" },
  { title: "Customers", href: "/customers" },
  { title: "Docs", href: "/docs" },
];

/* -------------------------------------------------------------------------- */
/* Active-path helper                                                          */
/* -------------------------------------------------------------------------- */

function isActive(pathname: string, href: string) {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(href + "/");
}

/* -------------------------------------------------------------------------- */
/* Scroll state — for the transparent-over-hero variant                        */
/* -------------------------------------------------------------------------- */

function useScrolled(threshold = 8) {
  const [scrolled, setScrolled] = React.useState(false);
  React.useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > threshold);
    onScroll(); // sync on mount (handles refresh mid-page)
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [threshold]);
  return scrolled;
}

/* -------------------------------------------------------------------------- */
/* Logo                                                                        */
/* -------------------------------------------------------------------------- */

function Logo({ className }: { className?: string }) {
  return (
    <Link
      href="/"
      className={cn(
        "flex shrink-0 items-center gap-2 rounded-md outline-none",
        "focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
        className,
      )}
    >
      <span
        aria-hidden="true"
        className="flex size-7 items-center justify-center rounded-md bg-primary text-primary-foreground"
      >
        <Zap className="size-4" />
      </span>
      <span className="text-base font-semibold tracking-tight text-foreground">
        Acme
      </span>
      <span className="sr-only">Acme home</span>
    </Link>
  );
}

/* -------------------------------------------------------------------------- */
/* Desktop panel row — the whole card is one link                              */
/* -------------------------------------------------------------------------- */

function PanelRow({
  item,
  pathname,
}: {
  item: NavLeaf;
  pathname: string;
}) {
  const active = isActive(pathname, item.href);
  const Icon = item.icon;
  return (
    <li>
      <NavigationMenuLink asChild active={active}>
        <Link
          href={item.href}
          aria-current={active ? "page" : undefined}
          className={cn(
            "group/row flex select-none gap-3 rounded-md p-3 leading-none no-underline outline-none transition-colors",
            "hover:bg-accent hover:text-accent-foreground",
            "focus-visible:bg-accent focus-visible:text-accent-foreground",
            "data-[active=true]:bg-accent",
          )}
        >
          <span className="flex size-9 shrink-0 items-center justify-center rounded-md border border-border bg-muted text-muted-foreground transition-colors group-hover/row:text-foreground">
            <Icon className="size-4" aria-hidden="true" />
          </span>
          <span className="flex flex-col gap-1">
            <span className="text-sm font-medium text-foreground">
              {item.title}
            </span>
            {item.description ? (
              <span className="line-clamp-2 text-xs text-muted-foreground">
                {item.description}
              </span>
            ) : null}
          </span>
        </Link>
      </NavigationMenuLink>
    </li>
  );
}

/* -------------------------------------------------------------------------- */
/* Desktop nav                                                                 */
/* -------------------------------------------------------------------------- */

function DesktopNav({ className }: { className?: string }) {
  const pathname = usePathname();

  return (
    <NavigationMenu className={className}>
      <NavigationMenuList className="gap-1">
        {NAV.map((item) => {
          // Mega menu: featured card + 2-column rows.
          if (item.type === "mega") {
            return (
              <NavigationMenuItem key={item.title}>
                <NavigationMenuTrigger>{item.title}</NavigationMenuTrigger>
                <NavigationMenuContent>
                  <div className="grid w-[38rem] grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)] gap-3 p-4 lg:w-[44rem]">
                    <NavigationMenuLink asChild>
                      <Link
                        href={item.featured.href}
                        className="flex h-full w-full flex-col justify-end rounded-md bg-gradient-to-b from-muted/50 to-muted p-5 no-underline outline-none transition-colors hover:to-accent focus-visible:ring-2 focus-visible:ring-ring"
                      >
                        <item.featured.icon
                          className="size-6 text-foreground"
                          aria-hidden="true"
                        />
                        <span className="mt-3 text-sm font-medium text-foreground">
                          {item.featured.title}
                        </span>
                        <span className="mt-1 text-xs text-muted-foreground">
                          {item.featured.description}
                        </span>
                      </Link>
                    </NavigationMenuLink>
                    <ul className="grid grid-cols-2 gap-1">
                      {item.items.map((leaf) => (
                        <PanelRow
                          key={leaf.href}
                          item={leaf}
                          pathname={pathname}
                        />
                      ))}
                    </ul>
                  </div>
                </NavigationMenuContent>
              </NavigationMenuItem>
            );
          }

          // Simple dropdown: single-column list.
          if (item.type === "dropdown") {
            return (
              <NavigationMenuItem key={item.title}>
                <NavigationMenuTrigger>{item.title}</NavigationMenuTrigger>
                <NavigationMenuContent>
                  <ul className="grid w-[22rem] gap-1 p-2">
                    {item.items.map((leaf) => (
                      <PanelRow
                        key={leaf.href}
                        item={leaf}
                        pathname={pathname}
                      />
                    ))}
                  </ul>
                </NavigationMenuContent>
              </NavigationMenuItem>
            );
          }

          // Flat link.
          const active = isActive(pathname, item.href);
          return (
            <NavigationMenuItem key={item.title}>
              <NavigationMenuLink asChild active={active}>
                <Link
                  href={item.href}
                  aria-current={active ? "page" : undefined}
                  className={navigationMenuTriggerStyle()}
                >
                  {item.title}
                </Link>
              </NavigationMenuLink>
            </NavigationMenuItem>
          );
        })}
      </NavigationMenuList>
    </NavigationMenu>
  );
}

/* -------------------------------------------------------------------------- */
/* Mobile nav — Sheet + Accordion                                              */
/* -------------------------------------------------------------------------- */

function MobileLink({
  href,
  pathname,
  className,
  children,
}: {
  href: string;
  pathname: string;
  className?: string;
  children: React.ReactNode;
}) {
  const active = isActive(pathname, href);
  return (
    <SheetClose asChild>
      <Link
        href={href}
        aria-current={active ? "page" : undefined}
        className={cn(
          "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm outline-none transition-colors",
          "hover:bg-accent hover:text-accent-foreground focus-visible:bg-accent",
          active ? "text-foreground" : "text-muted-foreground",
          className,
        )}
      >
        {children}
      </Link>
    </SheetClose>
  );
}

function MobileNav() {
  const pathname = usePathname();
  const [open, setOpen] = React.useState(false);

  // Close the drawer whenever the route changes (client-side nav).
  React.useEffect(() => {
    setOpen(false);
  }, [pathname]);

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
          aria-label="Open main menu"
        >
          <Menu className="size-5" aria-hidden="true" />
        </Button>
      </SheetTrigger>
      <SheetContent
        side="left"
        className="flex w-full max-w-sm flex-col gap-0 p-0"
      >
        <SheetHeader className="border-b border-border p-4 text-left">
          <SheetTitle asChild>
            <Logo />
          </SheetTitle>
        </SheetHeader>

        <nav className="flex-1 overflow-y-auto p-3">
          <Accordion type="single" collapsible className="w-full">
            {NAV.map((item) => {
              if (item.type === "mega" || item.type === "dropdown") {
                const leaves =
                  item.type === "mega"
                    ? [item.featured, ...item.items]
                    : item.items;
                return (
                  <AccordionItem
                    key={item.title}
                    value={item.title}
                    className="border-b border-border"
                  >
                    <AccordionTrigger className="px-3 py-3 text-sm font-medium hover:no-underline">
                      {item.title}
                    </AccordionTrigger>
                    <AccordionContent className="pb-2">
                      <ul className="flex flex-col">
                        {leaves.map((leaf) => (
                          <li key={leaf.href}>
                            <MobileLink href={leaf.href} pathname={pathname}>
                              <span className="flex size-8 shrink-0 items-center justify-center rounded-md border border-border bg-muted text-muted-foreground">
                                <leaf.icon
                                  className="size-4"
                                  aria-hidden="true"
                                />
                              </span>
                              {leaf.title}
                            </MobileLink>
                          </li>
                        ))}
                      </ul>
                    </AccordionContent>
                  </AccordionItem>
                );
              }

              return (
                <div key={item.title} className="border-b border-border">
                  <MobileLink
                    href={item.href}
                    pathname={pathname}
                    className="px-3 py-3.5 text-sm font-medium"
                  >
                    {item.title}
                  </MobileLink>
                </div>
              );
            })}
          </Accordion>
        </nav>

        <div className="mt-auto flex flex-col gap-2 border-t border-border p-4">
          <SheetClose asChild>
            <Button asChild variant="outline" className="w-full">
              <Link href="/login">Sign in</Link>
            </Button>
          </SheetClose>
          <SheetClose asChild>
            <Button asChild className="w-full">
              <Link href="/signup">Get started</Link>
            </Button>
          </SheetClose>
        </div>
      </SheetContent>
    </Sheet>
  );
}

/* -------------------------------------------------------------------------- */
/* Site header                                                                 */
/* -------------------------------------------------------------------------- */

export function SiteHeader({
  variant = "solid",
}: {
  /** "solid": always frosted. "transparent": clear over a hero, frosts on scroll. */
  variant?: "solid" | "transparent";
}) {
  const scrolled = useScrolled();
  const frosted = variant === "solid" || scrolled;

  return (
    <header
      data-scrolled={scrolled}
      className={cn(
        "sticky top-0 z-50 w-full border-b transition-colors duration-200 motion-reduce:transition-none",
        frosted
          ? "border-border bg-background/70 backdrop-blur-lg supports-[backdrop-filter]:bg-background/60"
          : "border-transparent bg-transparent",
      )}
    >
      {/* Skip link — first focusable element on the page. */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-3 focus:z-[60] focus:rounded-md focus:bg-background focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:text-foreground focus:shadow-md focus:outline-none focus:ring-2 focus:ring-ring"
      >
        Skip to content
      </a>

      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        {/* Left: mobile trigger + logo + desktop nav */}
        <div className="flex items-center gap-2 md:gap-6">
          <MobileNav />
          <Logo />
          <DesktopNav className="hidden md:flex" />
        </div>

        {/* Right: actions — CTA pinned far right */}
        <div className="flex items-center gap-2">
          {/* Optional slot: theme toggle / search trigger goes here. */}
          <Button
            asChild
            variant="ghost"
            size="sm"
            className="hidden sm:inline-flex"
          >
            <Link href="/login">Sign in</Link>
          </Button>
          <Button asChild size="sm">
            <Link href="/signup">Get started</Link>
          </Button>
        </div>
      </div>
    </header>
  );
}
```

Then in your layout, mark the main region so the skip link and anchor offsets resolve:

```tsx
// app/layout.tsx (excerpt)
<SiteHeader /> {/* or <SiteHeader variant="transparent" /> over a hero */}
<main id="main-content">{children}</main>
```

### Notes on the implementation

- **One data source, two renderers.** `NAV` drives both `DesktopNav` and `MobileNav`, so the mega menu and its mobile accordion can never drift out of sync. Add a section once; it appears in both.
- **Real links, buttons only for UI toggles.** Every destination is a Next `<Link>` via `NavigationMenuLink asChild` (or `SheetClose asChild` on mobile). The only `<button>`s are the panel triggers (Radix, `aria-expanded` handled) and the hamburger (`aria-label="Open main menu"`).
- **Active state is wired end to end.** `isActive(pathname, href)` sets both `data-active` (styling, via `NavigationMenuLink active`) and `aria-current="page"` (assistive tech) on desktop and mobile.
- **The morphing panel is free.** shadcn's `NavigationMenu` renders the `NavigationMenuViewport` for you; it resizes and slides between "Product" and "Resources" using Radix's `data-motion` + `--radix-navigation-menu-viewport-[width|height]`. No custom animation code — this is the Stripe/Linear panel morph out of the box.
- **Chevron rotation is built in.** shadcn's `NavigationMenuTrigger` ships the `ChevronDown` that rotates on `data-state="open"` — don't add your own.
- **Frosted-on-scroll transitions paint only.** The `variant="transparent"` header swaps `bg`/`border` classes past an 8px threshold via `useScrolled`; height and padding never change, so there's no layout shift. `motion-reduce:transition-none` respects reduced-motion.
- **Mobile drawer closes on navigation.** `SheetClose asChild` closes on tap; a `useEffect` on `pathname` also closes it after client-side route changes. Footer CTAs are pinned with `mt-auto` so the conversion path never scrolls off.
- **`SheetTitle` is present** (wrapping the `Logo`) so the dialog is labelled for screen readers; Radix traps and restores focus and closes on Esc.
- **All colors are tokens** (`bg-background`, `bg-accent`, `text-muted-foreground`, `border-border`, `ring-ring`, `bg-primary`) — including the featured card's `from-muted/50 to-muted` gradient. Light/dark and re-theming come free; the only custom vars are `--header-height` and the `scroll-padding-top` it feeds.
- **Not on Next?** Replace `next/link` with your framework's link and `usePathname()` with its current-path hook (or thread a `pathname` prop down); everything else is framework-agnostic.
