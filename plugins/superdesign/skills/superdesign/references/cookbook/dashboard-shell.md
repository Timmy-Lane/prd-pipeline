# App Dashboard Shell (Sidebar + Topbar + Content)

**Slug:** `dashboard-shell`
**Stack:** React + Tailwind v4 + shadcn/ui
**Primitives:** `sidebar`, `breadcrumb`, `dropdown-menu`, `separator`, `tooltip`, `command`, `dialog`, `avatar`, `skeleton`, `button`, `input`

---

## When to use it

Reach for the app shell when you're building the **authenticated frame** of a product — the persistent chrome that wraps every page. Its defining property is a **stable frame**: the sidebar and topbar stay fixed while only the content region swaps as the user navigates. This is the default layout for Linear, Vercel, Stripe, Notion, Datadog, and GitHub.

**Use it when:**
- The app has **5+ top-level destinations** and needs grouped navigation.
- Users run **long sessions** inside the product and benefit from preserved spatial context.
- You need **workspace / org switching**, a global command palette, and an account menu always in reach.

**Don't use it when:**
- You have **≤4 destinations** — a topbar-only layout is lighter and less chrome.
- It's a marketing site, docs, or a single-purpose tool — the sidebar is dead weight.
- The primary surface is a full-bleed canvas (map, editor, whiteboard) where a persistent 256px rail steals real estate — consider `collapsible="icon"` or an offcanvas overlay instead.

---

## Anatomy

Three regions: a **sidebar column** next to a **content column**, where the content column is a sticky **topbar** stacked over a scrollable **main**.

```
┌────────────┬──────────────────────────────────────────────┐
│ SIDEBAR    │ TOPBAR (sticky, h-16)                         │
│            │ [trigger]│[breadcrumb] ····· [⌘K][theme][user]│
│ header     ├──────────────────────────────────────────────┤
│  ↳ switcher│                                              ▲│
│            │ MAIN (owns scroll)                           ││
│ content    │  ┌ page header row (title + actions) ─────┐  ││
│  ↳ nav     │  │                                        │  ││
│    groups  │  └────────────────────────────────────────┘  ││
│            │  ┌ cards / table / grid ──────────────────┐  ││
│ footer     │  │                                        │  ││
│  ↳ user    │  └────────────────────────────────────────┘  ▼│
└────────────┴──────────────────────────────────────────────┘
```

**Sidebar** (`SidebarHeader` / `SidebarContent` / `SidebarFooter`):
- **Header** — brand mark + **workspace/org switcher** (a `DropdownMenu`).
- **Content** (scrollable) — grouped nav. Group = optional uppercase label + items. Item = icon + label (+ optional badge/count, hover action, or one level of submenu). Order: primary group (Home / Inbox / Issues) → Projects/Workspaces → Favorites/Teams.
- **Footer** — user account menu (theme toggle, settings, plan, sign out).

**Topbar** (left → right):
- `SidebarTrigger` (toggle; primary control on mobile).
- Vertical `Separator`, then **breadcrumbs** / page title.
- Flexible spacer (`ml-auto`).
- Command-palette launcher (⌘K), theme toggle, user avatar menu.

**Content** (`<main>`):
- **Page header row** — title (+ description) left, actions/filters/tabs right.
- **Body** — constrained container (`max-w-*` + `mx-auto`) for dashboards, or full-bleed for tables and canvases.
- Owns its own scroll; the sidebar and topbar never scroll with it.

---

## Token-driven styling

Everything is driven by CSS variables — **no hardcoded hex in components**. shadcn's `sidebar` block ships a dedicated token namespace so the chrome can sit *behind* the content (dimmer, lower contrast) without hand-tuning colors per component. On Tailwind v4 these live in `@theme` / `:root` blocks in your `globals.css`.

```css
/* globals.css — Tailwind v4 */
@import "tailwindcss";
@import "tw-animate-css";

@custom-variant dark (&:is(.dark *));

:root {
  --radius: 0.625rem;

  --background: oklch(1 0 0);
  --foreground: oklch(0.205 0.006 240);
  --border: oklch(0.922 0.004 240);
  --ring: oklch(0.53 0.17 240);

  /* Sidebar namespace — dimmer than content; tinted toward brand H (never pure C=0) */
  --sidebar: oklch(0.985 0.003 240);
  --sidebar-foreground: oklch(0.269 0.007 240);
  --sidebar-primary: oklch(0.53 0.17 240);
  --sidebar-primary-foreground: oklch(0.985 0.002 240);
  --sidebar-accent: oklch(0.955 0.004 240);     /* hover / active bg */
  --sidebar-accent-foreground: oklch(0.269 0.007 240);
  --sidebar-border: oklch(0.922 0.004 240);     /* hairline */
  --sidebar-ring: oklch(0.53 0.17 240);         /* focus ring */
}

.dark {
  --background: oklch(0.145 0.006 240);
  --foreground: oklch(0.985 0.002 240);
  --border: oklch(1 0 0 / 10%);
  --ring: oklch(0.556 0.008 240);

  --sidebar: oklch(0.205 0.006 240);
  --sidebar-foreground: oklch(0.985 0.002 240);
  --sidebar-primary: oklch(0.704 0.140 240);
  --sidebar-primary-foreground: oklch(0.205 0.006 240);
  --sidebar-accent: oklch(0.269 0.007 240);
  --sidebar-accent-foreground: oklch(0.985 0.002 240);
  --sidebar-border: oklch(1 0 0 / 10%);
  --sidebar-ring: oklch(0.556 0.008 240);
}

@theme inline {
  --radius-lg: var(--radius);
  --radius-md: calc(var(--radius) - 2px);
  --radius-sm: calc(var(--radius) - 4px);

  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-border: var(--border);
  --color-ring: var(--ring);

  --color-sidebar: var(--sidebar);
  --color-sidebar-foreground: var(--sidebar-foreground);
  --color-sidebar-primary: var(--sidebar-primary);
  --color-sidebar-primary-foreground: var(--sidebar-primary-foreground);
  --color-sidebar-accent: var(--sidebar-accent);
  --color-sidebar-accent-foreground: var(--sidebar-accent-foreground);
  --color-sidebar-border: var(--sidebar-border);
  --color-sidebar-ring: var(--sidebar-ring);
}
```

**Sizing tokens** (from `sidebar.tsx`; override per-instance with CSS vars):

| Token | Default | Meaning |
|---|---|---|
| `--sidebar-width` | `16rem` (256px) | expanded width |
| `--sidebar-width-icon` | `3rem` (48px) | icon-collapsed rail |
| `--sidebar-width-mobile` | `18rem` (288px) | Sheet overlay on mobile |

To widen a label-heavy nav, pass a style var to `SidebarProvider`:
`style={{ "--sidebar-width": "17rem" } as React.CSSProperties}`.

**Rules of thumb:** everything on a **4px grid** (Tailwind's scale maps cleanly). Hairline `1px` borders on `--sidebar-border` / `--border`. **One divider or a subtle bg shift between regions — not both.** Reserve saturated color for status, the active item, and the primary CTA; keep the rest of the chrome muted.

---

## Variants

**1. Inset + icon-collapse (recommended default — the "app-in-a-card" look, à la Vercel's new dashboard).**
`variant="inset"` floats the content in a rounded, elevated card with the sidebar in a padded gutter. `collapsible="icon"` shrinks the rail to 48px (icons + tooltips) instead of hiding it, so navigation survives a collapse.

```tsx
<SidebarProvider>
  <AppSidebar variant="inset" collapsible="icon" />
  <SidebarInset>{/* topbar + main */}</SidebarInset>
</SidebarProvider>
```
> Gotcha: the inset variant can produce a ~16px horizontal overflow — pair the outer wrapper with `overflow-hidden`.

**2. Flush + offcanvas (content-heavy / data-dense, à la Linear).**
`variant="sidebar"` (default) sits flush against the screen edge with a border seam; `collapsible="offcanvas"` slides it fully off to hand every pixel to a dense table or board. Best when the work area is the star and the nav is secondary.

```tsx
<SidebarProvider>
  <AppSidebar variant="sidebar" collapsible="offcanvas" />
  <SidebarInset>{/* topbar + main */}</SidebarInset>
</SidebarProvider>
```

Other axes: `side="right"` for a secondary contextual/inspector panel (keep left = global nav, right = selection context); `collapsible="none"` for always-open desktop/kiosk tools; `variant="floating"` for a lighter card-style panel with a gutter.

---

## Interaction & state matrix

**Sidebar container:**

| State | Behavior |
|---|---|
| Expanded (256px) | Default on desktop; labels visible. |
| Icon-collapsed (48px) | Labels hidden; **every item must expose its label via tooltip + `aria-label`.** |
| Offcanvas-hidden | Trigger + rail remain; ⌘B / rail / trigger reopens. |
| Mobile Sheet (288px) | Overlay + scrim below `md`; dismiss on backdrop tap, Esc, or route change. |
| Toggle | ⌘B / Ctrl+B (built into shadcn), the `SidebarTrigger`, or the `SidebarRail`. |
| Persistence | Collapsed state stored in the `sidebar_state` cookie — survives reload/SSR. |

**Nav item** (each needs a distinct visual):

| State | Cue |
|---|---|
| Default | muted foreground, transparent bg |
| Hover | `--sidebar-accent` bg |
| Active / current | `isActive` → accent bg + stronger foreground **and** `aria-current="page"`. Pick **one** signal (bg *or* left bar), not two. |
| Focus-visible | `--sidebar-ring` outline for keyboard users |
| Disabled | reduced opacity, `aria-disabled`, not focusable |
| With badge/count | `SidebarMenuBadge`, right-aligned |
| With hover action | `SidebarMenuAction` reveals on row hover/focus |
| Submenu parent | chevron rotates on open; `SidebarMenuSub` for one level of nesting |

**Content / data:**

| State | Behavior |
|---|---|
| Loading | Skeletons **shaped like the target layout** (rows/cards/table) — *not* a centered spinner. Keep the shell painted. |
| Empty | Illustration/short copy + primary CTA, centered in the content region. |
| Error | Inline retry; the shell stays intact. |
| Populated | Normal. |
| Permission-gated | Hide or disable nav the user can't reach — don't 403 after a click. |

**Global:** first-paint auth skeleton; a thin trial/impersonation/non-prod banner strip above the topbar (the shell must tolerate an extra top band without breaking sticky offsets).

---

## Responsive behavior

- **≥ `md`:** persistent sidebar (expanded or icon-collapsed per the user's saved preference).
- **< `md`:** the sidebar auto-converts to a **Sheet** off-canvas overlay (288px) triggered by the hamburger; content goes full width. `useSidebar()` exposes `isMobile`, `openMobile`, `setOpenMobile` — shadcn handles the swap for you. **Never** render a persistent 256px sidebar on a phone.
- **Topbar** stays sticky (`sticky top-0 z-10`) at all widths; it can shrink from `h-16` to `h-12` when the sidebar is icon-collapsed (`group-has-data-[collapsible=icon]/sidebar-wrapper:h-12`).
- **Content container** uses `max-w-6xl mx-auto` for dashboards; drop the cap and go full-bleed for data tables and canvases. Density is a one-time choice — Stripe-airy (1280px) vs Linear-dense (~1024px) — applied everywhere.

---

## Accessibility notes

- **Keyboard:** ⌘B/Ctrl+B toggles the sidebar (built in); wire ⌘K for the command palette. Full tab traversal; the mobile Sheet traps focus and closes on Esc.
- **Landmarks:** nav is `<nav aria-label="Main">` with a real list; content is the `<main>` landmark. Add a **skip-to-content** link before the shell.
- **Current page:** mark the active item with `aria-current="page"` (not color alone).
- **Icon-only rail:** collapsed items **must** carry an accessible name — a `SidebarMenuButton` tooltip plus `aria-label`. Never ship icon-only with no name.
- **Focus rings:** always visible via `--sidebar-ring` — don't remove outlines.
- **Motion:** respect `prefers-reduced-motion` for collapse/expand and view transitions.
- **RTL:** use logical properties / `dir` so the whole shell mirrors.

---

## Anti-slop callout

The generic AI dashboard tell is a **loud, high-contrast, over-nested sidebar** competing with the content — a purple-gradient rail, 15 top-level links three levels deep, a spinner on every load, and a bar *and* a bg *and* a color all firing on the active item at once. Ship the Linear discipline instead:

- **Dim the chrome.** The sidebar sits *behind* the work. Muted greys, hairline borders, saturated color reserved for status/active/primary CTA only.
- **Cap depth at ~2 levels** (3 absolute max, the 3rd collapsing into a dropdown). Group and collapse; use "Show more" for long lists. Deep trees spike navigation-failure rates.
- **One active cue.** Background *or* left bar — never both, never plus a color shift.
- **Shaped skeletons, not spinners.** Keep the shell painted while data loads.
- **Persist the shell across navigation.** Transition only the content; a full-page reload that flashes the entire frame on every click destroys spatial context.
- **Persist collapse state** (cookie/localStorage — shadcn does this by default). Losing the user's preference on reload is a slop signal.
- **Progressive disclosure.** Don't cram every feature into nav; put secondary analytics behind a tab, not on the first screen.

---

## Complete code example

Six files: `app-sidebar.tsx`, `nav-main.tsx`, `workspace-switcher.tsx`, `nav-user.tsx`, `command-menu.tsx`, and the page that composes them. Assumes shadcn primitives are installed:

```bash
npx shadcn@latest add sidebar breadcrumb dropdown-menu separator tooltip command dialog avatar skeleton button input
```

### `components/app-sidebar.tsx`

```tsx
"use client"

import * as React from "react"
import {
  Home,
  Inbox,
  CircleDot,
  FolderKanban,
  BarChart3,
  Settings,
  LifeBuoy,
} from "lucide-react"

import { NavMain, type NavGroup } from "@/components/nav-main"
import { NavUser } from "@/components/nav-user"
import { WorkspaceSwitcher } from "@/components/workspace-switcher"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar"

// In a real app this comes from your router/loader/API, not module scope.
const data = {
  user: {
    name: "Ada Lovelace",
    email: "ada@analytical.dev",
    avatar: "/avatars/ada.jpg",
  },
  workspaces: [
    { name: "Analytical Engine", plan: "Enterprise", logo: "AE" },
    { name: "Difference Machine", plan: "Pro", logo: "DM" },
  ],
  nav: [
    {
      // Primary group has no label — it reads as the "home base".
      items: [
        { title: "Home", url: "/", icon: Home },
        { title: "Inbox", url: "/inbox", icon: Inbox, badge: "12" },
        { title: "Issues", url: "/issues", icon: CircleDot },
      ],
    },
    {
      label: "Workspace",
      items: [
        {
          title: "Projects",
          url: "/projects",
          icon: FolderKanban,
          items: [
            { title: "Active", url: "/projects/active" },
            { title: "Archived", url: "/projects/archived" },
          ],
        },
        { title: "Analytics", url: "/analytics", icon: BarChart3 },
      ],
    },
  ] satisfies NavGroup[],
  footer: [
    { title: "Support", url: "/support", icon: LifeBuoy },
    { title: "Settings", url: "/settings", icon: Settings },
  ] satisfies NavGroup["items"],
}

export function AppSidebar(props: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="icon" variant="inset" {...props}>
      <SidebarHeader>
        <WorkspaceSwitcher workspaces={data.workspaces} />
      </SidebarHeader>

      <SidebarContent>
        <NavMain groups={data.nav} />
      </SidebarContent>

      <SidebarFooter>
        <NavMain groups={[{ items: data.footer }]} />
        <NavUser user={data.user} />
      </SidebarFooter>

      {/* Thin edge strip to drag/click-toggle the collapse. */}
      <SidebarRail />
    </Sidebar>
  )
}
```

### `components/nav-main.tsx`

```tsx
"use client"

import * as React from "react"
import { ChevronRight, type LucideIcon } from "lucide-react"
// Swap for your router. next/navigation shown; react-router → useLocation().
import { usePathname } from "next/navigation"
import Link from "next/link"

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from "@/components/ui/sidebar"

export type NavItem = {
  title: string
  url: string
  icon?: LucideIcon
  badge?: string
  items?: { title: string; url: string }[]
}

export type NavGroup = {
  label?: string
  items: NavItem[]
}

export function NavMain({ groups }: { groups: NavGroup[] }) {
  const pathname = usePathname()

  const isActive = (url: string) =>
    url === "/" ? pathname === "/" : pathname.startsWith(url)

  return (
    <>
      {groups.map((group, i) => (
        <SidebarGroup key={group.label ?? `group-${i}`}>
          {group.label && <SidebarGroupLabel>{group.label}</SidebarGroupLabel>}
          <SidebarMenu>
            {group.items.map((item) => {
              const active = isActive(item.url)

              // Leaf item — no children.
              if (!item.items?.length) {
                return (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton
                      asChild
                      isActive={active}
                      tooltip={item.title} // shows the label when icon-collapsed
                    >
                      <Link
                        href={item.url}
                        aria-current={active ? "page" : undefined}
                      >
                        {item.icon && <item.icon />}
                        <span>{item.title}</span>
                      </Link>
                    </SidebarMenuButton>
                    {item.badge && (
                      <SidebarMenuBadge>{item.badge}</SidebarMenuBadge>
                    )}
                  </SidebarMenuItem>
                )
              }

              // Parent with one level of submenu.
              const childActive = item.items.some((c) => isActive(c.url))
              return (
                <Collapsible
                  key={item.title}
                  asChild
                  defaultOpen={active || childActive}
                  className="group/collapsible"
                >
                  <SidebarMenuItem>
                    <CollapsibleTrigger asChild>
                      <SidebarMenuButton
                        tooltip={item.title}
                        isActive={active && !childActive}
                      >
                        {item.icon && <item.icon />}
                        <span>{item.title}</span>
                        <ChevronRight className="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />
                      </SidebarMenuButton>
                    </CollapsibleTrigger>
                    <CollapsibleContent>
                      <SidebarMenuSub>
                        {item.items.map((sub) => {
                          const subActive = isActive(sub.url)
                          return (
                            <SidebarMenuSubItem key={sub.title}>
                              <SidebarMenuSubButton
                                asChild
                                isActive={subActive}
                              >
                                <Link
                                  href={sub.url}
                                  aria-current={subActive ? "page" : undefined}
                                >
                                  <span>{sub.title}</span>
                                </Link>
                              </SidebarMenuSubButton>
                            </SidebarMenuSubItem>
                          )
                        })}
                      </SidebarMenuSub>
                    </CollapsibleContent>
                  </SidebarMenuItem>
                </Collapsible>
              )
            })}
          </SidebarMenu>
        </SidebarGroup>
      ))}
    </>
  )
}
```

### `components/workspace-switcher.tsx`

```tsx
"use client"

import * as React from "react"
import { ChevronsUpDown, Plus } from "lucide-react"

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar"

type Workspace = { name: string; plan: string; logo: string }

export function WorkspaceSwitcher({ workspaces }: { workspaces: Workspace[] }) {
  const { isMobile } = useSidebar()
  const [active, setActive] = React.useState(workspaces[0])

  if (!active) return null

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton
              size="lg"
              className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
            >
              <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sm font-semibold text-sidebar-primary-foreground">
                {active.logo}
              </div>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-semibold">{active.name}</span>
                <span className="truncate text-xs text-muted-foreground">
                  {active.plan}
                </span>
              </div>
              <ChevronsUpDown className="ml-auto size-4" />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            className="w-(--radix-dropdown-menu-trigger-width) min-w-56 rounded-lg"
            align="start"
            side={isMobile ? "bottom" : "right"}
            sideOffset={4}
          >
            <DropdownMenuLabel className="text-xs text-muted-foreground">
              Workspaces
            </DropdownMenuLabel>
            {workspaces.map((ws, i) => (
              <DropdownMenuItem
                key={ws.name}
                onClick={() => setActive(ws)}
                className="gap-2 p-2"
              >
                <div className="flex size-6 items-center justify-center rounded-md border text-xs font-medium">
                  {ws.logo}
                </div>
                {ws.name}
                <DropdownMenuShortcut>⌘{i + 1}</DropdownMenuShortcut>
              </DropdownMenuItem>
            ))}
            <DropdownMenuSeparator />
            <DropdownMenuItem className="gap-2 p-2">
              <div className="flex size-6 items-center justify-center rounded-md border bg-background">
                <Plus className="size-4" />
              </div>
              <span className="text-muted-foreground">Add workspace</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  )
}
```

### `components/nav-user.tsx`

```tsx
"use client"

import * as React from "react"
import {
  BadgeCheck,
  Bell,
  ChevronsUpDown,
  CreditCard,
  LogOut,
  Monitor,
  Moon,
  Sun,
} from "lucide-react"
import { useTheme } from "next-themes"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar"

type User = { name: string; email: string; avatar: string }

export function NavUser({ user }: { user: User }) {
  const { isMobile } = useSidebar()
  const { setTheme } = useTheme()
  const initials = user.name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton
              size="lg"
              className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
            >
              <Avatar className="size-8 rounded-lg">
                <AvatarImage src={user.avatar} alt={user.name} />
                <AvatarFallback className="rounded-lg">
                  {initials}
                </AvatarFallback>
              </Avatar>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-semibold">{user.name}</span>
                <span className="truncate text-xs text-muted-foreground">
                  {user.email}
                </span>
              </div>
              <ChevronsUpDown className="ml-auto size-4" />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            className="w-(--radix-dropdown-menu-trigger-width) min-w-56 rounded-lg"
            side={isMobile ? "bottom" : "right"}
            align="end"
            sideOffset={4}
          >
            <DropdownMenuLabel className="flex items-center gap-2 p-2 font-normal">
              <Avatar className="size-8 rounded-lg">
                <AvatarImage src={user.avatar} alt={user.name} />
                <AvatarFallback className="rounded-lg">
                  {initials}
                </AvatarFallback>
              </Avatar>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-semibold">{user.name}</span>
                <span className="truncate text-xs text-muted-foreground">
                  {user.email}
                </span>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuGroup>
              <DropdownMenuItem>
                <BadgeCheck />
                Account
              </DropdownMenuItem>
              <DropdownMenuItem>
                <CreditCard />
                Billing
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Bell />
                Notifications
              </DropdownMenuItem>
              <DropdownMenuSub>
                <DropdownMenuSubTrigger>
                  <Sun className="size-4 dark:hidden" />
                  <Moon className="hidden size-4 dark:block" />
                  Theme
                </DropdownMenuSubTrigger>
                <DropdownMenuSubContent>
                  <DropdownMenuItem onClick={() => setTheme("light")}>
                    <Sun /> Light
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setTheme("dark")}>
                    <Moon /> Dark
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setTheme("system")}>
                    <Monitor /> System
                  </DropdownMenuItem>
                </DropdownMenuSubContent>
              </DropdownMenuSub>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            <DropdownMenuItem variant="destructive">
              <LogOut />
              Sign out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  )
}
```

### `components/command-menu.tsx`

```tsx
"use client"

import * as React from "react"
import { BarChart3, CircleDot, Home, Inbox, Search } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"

/** ⌘K launcher for the topbar. */
export function CommandMenu() {
  const [open, setOpen] = React.useState(false)

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((o) => !o)
      }
    }
    document.addEventListener("keydown", down)
    return () => document.removeEventListener("keydown", down)
  }, [])

  return (
    <>
      <Button
        variant="outline"
        onClick={() => setOpen(true)}
        className="relative h-8 w-full justify-start gap-2 text-muted-foreground sm:w-56 md:w-64"
      >
        <Search className="size-4" />
        <span>Search…</span>
        <kbd className="pointer-events-none absolute right-1.5 top-1.5 hidden h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium sm:flex">
          ⌘K
        </kbd>
      </Button>

      <CommandDialog open={open} onOpenChange={setOpen}>
        <CommandInput placeholder="Type a command or search…" />
        <CommandList>
          <CommandEmpty>No results found.</CommandEmpty>
          <CommandGroup heading="Navigation">
            <CommandItem onSelect={() => setOpen(false)}>
              <Home /> Home
            </CommandItem>
            <CommandItem onSelect={() => setOpen(false)}>
              <Inbox /> Inbox
            </CommandItem>
            <CommandItem onSelect={() => setOpen(false)}>
              <CircleDot /> Issues
            </CommandItem>
            <CommandItem onSelect={() => setOpen(false)}>
              <BarChart3 /> Analytics
            </CommandItem>
          </CommandGroup>
        </CommandList>
      </CommandDialog>
    </>
  )
}
```

### `app/(app)/layout.tsx` — the shell + a sample page

```tsx
import * as React from "react"

import { AppSidebar } from "@/components/app-sidebar"
import { CommandMenu } from "@/components/command-menu"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { Skeleton } from "@/components/ui/skeleton"
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    // `overflow-hidden` guards the known ~16px inset overflow.
    <SidebarProvider className="overflow-hidden">
      {/* Skip link — first focusable element, before the shell. */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-background focus:px-3 focus:py-2 focus:shadow-md"
      >
        Skip to content
      </a>

      <AppSidebar />

      <SidebarInset>
        <header className="sticky top-0 z-10 flex h-16 shrink-0 items-center gap-2 border-b bg-background/95 px-4 backdrop-blur transition-[height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem className="hidden md:block">
                <BreadcrumbLink href="/">Analytical Engine</BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator className="hidden md:block" />
              <BreadcrumbItem>
                <BreadcrumbPage>Overview</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>

          <div className="ml-auto flex items-center gap-2">
            <CommandMenu />
            <Button size="sm">New issue</Button>
          </div>
        </header>

        <main
          id="main-content"
          className="flex flex-1 flex-col gap-6 p-4 md:p-6"
        >
          <div className="mx-auto w-full max-w-6xl">
            {/* Page header row */}
            <div className="flex flex-col gap-1 md:flex-row md:items-center md:justify-between">
              <div>
                <h1 className="text-2xl font-semibold tracking-tight">
                  Overview
                </h1>
                <p className="text-sm text-muted-foreground">
                  Everything happening across your workspace.
                </p>
              </div>
            </div>

            {children ?? <OverviewSkeleton />}
          </div>
        </main>
      </SidebarInset>
    </SidebarProvider>
  )
}

/** Shaped skeleton — matches the incoming card grid, not a spinner. */
function OverviewSkeleton() {
  return (
    <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <div
          key={i}
          className="flex flex-col gap-3 rounded-xl border bg-card p-4"
        >
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-8 w-16" />
          <Skeleton className="h-3 w-full" />
        </div>
      ))}
    </div>
  )
}
```

> **Root providers.** Wrap the tree in `next-themes` `<ThemeProvider attribute="class" defaultTheme="system" enableSystem>` and shadcn's `<TooltipProvider>` (the sidebar tooltips need it) at the app root. `SidebarProvider` reads the `sidebar_state` cookie on mount, so collapse state survives reloads with no extra work.

---

## Sources

- shadcn/ui Sidebar — https://ui.shadcn.com/docs/components/sidebar
- shadcn/ui Sidebar blocks — https://ui.shadcn.com/blocks/sidebar
- shadcn/ui Blocks (dashboard-01) — https://ui.shadcn.com/blocks
- Linear, "How we redesigned the Linear UI (part II)" — https://linear.app/now/how-we-redesigned-the-linear-ui
- 925studios, Linear design breakdown — https://www.925studios.co/blog/linear-design-breakdown-saas-ui-2026
- Vercel, new dashboard — https://vercel.com/try/new-dashboard
- shadcn inset overflow gotcha — https://github.com/shadcn-ui/ui/issues/7947
