# Modals / Dialogs / Sheets / Drawers

> **Category:** `dialogs`
> **Stack:** React 19 · Tailwind CSS v4 · shadcn/ui
> **Primitives:** `Dialog` · `AlertDialog` · `Sheet` · `Drawer` (Vaul) · `Button` · `Input` · `Label` · `Select` · `Sonner`
> **Install:** `pnpm dlx shadcn@latest add dialog alert-dialog sheet drawer button input label select sonner`

A modal is a promise: *"stop everything, this one thing needs you."* All four
primitives here are the same idea — a focus-trapped layer rendered over inert,
scroll-locked content — differing only in **where they anchor** and **how you're
allowed to leave**. Choosing the wrong one, or leaving a state undesigned, is what
separates a Linear/Vercel overlay from a boilerplate one. Design the *dismissal
contract* and the *loading/error/success arc* before you write the markup.

---

## 1. When to use it — pick the right primitive

All four ship in shadcn. `Sheet` extends `Dialog`; `Drawer` wraps Vaul;
`AlertDialog` is the confirm-only variant that deliberately removes the easy exits.

| Primitive | Anchor / motion | Dismiss contract | Use for |
|---|---|---|---|
| **Dialog** | Centered; zoom + fade | X · outside-click · Escape | Focused create/edit forms, detail views, short confirmations with input |
| **AlertDialog** | Centered | **No X, no outside-click** — only Cancel / Action + Escape | Destructive & irreversible confirms: delete, discard, sign out, "type to confirm" |
| **Sheet** | Edge-anchored (`side`: top/right/bottom/left); slides in | X · outside-click · Escape | Side panels that *complement* the page: filters, settings, a detail inspector |
| **Drawer** (Vaul) | Edge-anchored, usually bottom; draggable + snap points | Swipe-down · outside-click · Escape | Mobile bottom sheets, quick actions, and the mobile half of a responsive pair |

**The headline pattern: responsive Dialog ↔ Drawer.** Render a centered `Dialog`
on desktop and a bottom `Drawer` on mobile for the *same* content, switched by a
media-query hook. The drawer feels native on a phone (bottom sheet + swipe); the
dialog is right on a pointer device. shadcn documents this explicitly, and §8
below ships a single `ResponsiveDialog` primitive that does it for you.

**Also in the family:** the command menu (`CommandDialog` / cmdk) is a Dialog
specialization for Cmd+K palettes — see the `command-menu` recipe. And a
**Popover is not a modal** (no focus trap, non-blocking): if the interaction
doesn't demand undivided attention, use a Popover, Dropdown, or inline expand —
never a Dialog.

**Decision in one line:** needs input & a graceful exit → **Dialog**; irreversible
& needs friction → **AlertDialog**; complements the page → **Sheet**; mobile /
bottom / gesture → **Drawer**; same content, both worlds → **Responsive pair**.

---

## 2. Anatomy

Every variant is the same slot structure — only the prefix and the footer actions
change. Header stays fixed, **body scrolls**, footer stays pinned.

```
Dialog
├── DialogTrigger              (asChild → wraps YOUR <Button>, no nested buttons)
└── DialogContent              (the panel; portalled, sits above DialogOverlay)
    ├── DialogHeader           (stack: title + description)
    │   ├── DialogTitle        (REQUIRED for a11y — the aria-labelledby target)
    │   └── DialogDescription  (the aria-describedby target)
    ├── {body}                 (form / content — the scroll region)
    ├── DialogFooter           (actions: right-aligned on desktop, stacked on mobile)
    └── DialogClose            (the built-in X, top-right; showCloseButton={false} to hide)
```

Deltas per primitive:

- **Sheet** → `Sheet{Trigger,Content,Header,Title,Description,Footer,Close}` + a `side` prop.
- **Drawer** → `Drawer{Trigger,Content,Header,Title,Description,Footer,Close}` + a `direction` prop; renders a **drag-handle** affordance at the top instead of an X.
- **AlertDialog** → swaps `DialogClose` for **`AlertDialogCancel`** + **`AlertDialogAction`**; **no X, no overlay-click dismissal**.

Composition rules that actually matter:

- **`DialogTitle` is mandatory**, even when visually hidden. Radix/Vaul warn at
  runtime without it and screen readers announce nothing. If the design has no
  visible title (e.g. a command palette), wrap it in `<VisuallyHidden>` / `sr-only`.
- **Trigger uses `asChild`** so your `<Button>` *is* the trigger — never a button
  inside a button.
- **Fixed header, scrolling body, sticky footer** for anything that can overflow.
  The naïve single-scroll panel pushes the footer below the fold on long forms.

---

## 3. Token-driven styling

Every color is a **CSS variable** exposed as a Tailwind v4 utility via
`@theme inline` in `globals.css`, so the same overlay is correct in light and dark
with zero per-theme code. Never write `bg-white`, `text-gray-500`, or `bg-[#0a0a0a]`
in a dialog.

| Element | Token utility | CSS var |
|---|---|---|
| Panel surface | `bg-background` | `--background` |
| Panel / title text | `text-foreground` | `--foreground` |
| Description, hints | `text-muted-foreground` | `--muted-foreground` |
| Panel border / footer rule | `border` | `--border` |
| Focus ring | `ring-ring` (via primitives) | `--ring` |
| Primary action | `Button` default | `--primary` / `--primary-foreground` |
| Destructive action / errors | `variant="destructive"`, `text-destructive`, `bg-destructive/10` | `--destructive` |
| Drawer drag handle | `bg-muted` | `--muted` |

**The one deliberate exception — the scrim.** shadcn's overlay is `bg-black/80`.
The backdrop is *intentionally a fixed black alpha, not a token*, because it must
read dark in **both** themes — a `--foreground`-based scrim would flip to a white
wash in dark mode. What you *should* change for a premium feel is the weight: drop
to `bg-black/50` and add `backdrop-blur-sm`. Linear/Vercel/Stripe scrims are
lighter and softer than the shadcn default — the heavy 80% black is the #1 "stock
shadcn" tell.

```css
/* globals.css — the tokens a dialog touches (already present in a shadcn v4 app;
   shown so the recipe is self-contained — do NOT re-declare hexes in components). */
:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --border: oklch(0.922 0 0);
  --ring: oklch(0.708 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
  --destructive: oklch(0.577 0.245 27.325);
}
.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --border: oklch(1 0 0 / 10%);
  --ring: oklch(0.556 0 0);
  --primary: oklch(0.985 0 0);
  --primary-foreground: oklch(0.205 0 0);
  --destructive: oklch(0.704 0.191 22.216);
}
```

Spacing baseline (shadcn defaults — keep them unless you have a reason):

- **Padding** `p-6` (24px); with a scrolling body, move padding onto
  header/body/footer (`px-6`) so the scrollbar hugs the panel edge.
- **Radius** `rounded-lg`. **Elevation** `shadow-lg`.
- **Width** `sm:max-w-lg` (~512px) + `w-[calc(100%-2rem)]` so the panel keeps a
  1rem gutter on mobile. Gotcha: `sm:max-w-lg` out-specifies a bare `max-w-*`, so
  override at the **`sm:` breakpoint** (`sm:max-w-md`) or the default wins.
- **Height** cap at `max-h-[85dvh]` (desktop) / `max-h-[90dvh]` (drawer) with
  `dvh` (not `vh`) so mobile browser chrome doesn't clip the footer.
- **Rhythm** `gap-4` (16px) between header/body/footer.

---

## 4. Interaction / state matrix

Design every row — not just "open". This is where premium overlays are won.

| State | Trigger | Behavior |
|---|---|---|
| **Closed** | Default | Not in the DOM (portal unmounted); trigger focusable. |
| **Opening** | `open` → true | `data-[state=open]` fade + zoom-in (~200ms); focus moves into the panel. |
| **Open (idle)** | — | Focus trapped; background inert + scroll-locked. |
| **Submitting** | Async action fired | **Keep the dialog open.** Disable the primary button, show a spinner + "Saving…", keep Cancel *usable but guarded*, block outside-click / Escape so a stray click can't abandon an in-flight write. |
| **Field error** | Validation fail | Inline error under the field; `aria-invalid` + `aria-describedby`; focus the first bad field. Never a second modal for validation. |
| **Form error** | Request fail | Inline summary at the top of the body in a **polite `role="alert"` live region**; re-enable the form; keep the user's input. |
| **Success** | Request ok | **Close, then confirm with a toast** — not another modal. |
| **Empty** | Detail sheet, no record | Render an empty state *inside* the panel, don't leave it blank. |
| **Destructive** | Delete / discard | Use `AlertDialog`; primary is `variant="destructive"`; for high-stakes deletes, **type-to-confirm** the resource name. |
| **Guarded close** | Dismiss w/ unsaved changes | Intercept `onOpenChange`; raise a "Discard changes?" `AlertDialog` (the one allowed double-confirm). |
| **Closing** | `open` → false | `data-[state=closed]` fade + zoom-out (**faster** than open, ~150ms); **return focus to the trigger**. |
| **Reduced motion** | `prefers-reduced-motion` | Fade only — drop the zoom/slide transform. |

**Controlled vs uncontrolled:** reach for `open` / `onOpenChange` the moment
dismissal must be *gated* — submission in flight, a routing side effect, or an
unsaved-changes guard. Uncontrolled (`DialogTrigger` + `DialogClose`) is fine for
a read-only detail view with nothing to lose.

---

## 5. Variants

### Variant A — Responsive form (Dialog on desktop, Drawer on mobile)

The workhorse. An invite/create/edit form that:

- renders a centered **Dialog** ≥640px and a bottom **Drawer** below it, from one
  component and one set of children;
- keeps itself **open during submit**, disables the primary button with a spinner,
  and blocks outside-click / Escape mid-request;
- shows **inline field errors** + a polite form-error live region;
- **guards dismissal** — closing with unsaved changes raises a discard confirm;
- on success **closes and fires a toast**.

Full code in §8.

### Variant B — Destructive confirm with type-to-confirm (AlertDialog)

The high-friction path for irreversible actions. An `AlertDialog` (no X, no
outside-click) that requires the user to **type the resource name** before the
destructive button enables, keeps the dialog open through the async delete, and
reports the outcome via toast. This is the Stripe/GitHub "delete production"
treatment. Full code in §8.

### Bonus — Sheet for a complementary panel (filters)

When the panel *augments* the page rather than blocking a task, use a `Sheet`.
Same slot API, edge-anchored, wider affordance for lists of controls:

```tsx
import {
  Sheet, SheetContent, SheetDescription, SheetFooter,
  SheetHeader, SheetTitle, SheetTrigger, SheetClose,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";

export function FiltersSheet({ children }: { children: React.ReactNode }) {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="outline">Filters</Button>
      </SheetTrigger>
      {/* side="right" is the default; w-3/4 on mobile, capped on desktop */}
      <SheetContent side="right" className="flex w-3/4 flex-col gap-0 p-0 sm:max-w-sm">
        <SheetHeader className="border-b px-6 py-4">
          <SheetTitle>Filters</SheetTitle>
          <SheetDescription>Narrow the results. Applied instantly.</SheetDescription>
        </SheetHeader>
        <div className="flex-1 space-y-6 overflow-y-auto overscroll-contain px-6 py-4">
          {children}
        </div>
        <SheetFooter className="flex-row justify-between border-t px-6 py-4">
          <Button variant="ghost">Reset</Button>
          <SheetClose asChild>
            <Button>Done</Button>
          </SheetClose>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}
```

---

## 6. Responsive behavior

- **Swap the primitive, not just the CSS.** A centered dialog squeezed onto a phone
  is worse than a native bottom sheet. Switch `Dialog` ↔ `Drawer` at `sm` (640px)
  via `useMediaQuery` — the `ResponsiveDialog` in §8 encapsulates this so callers
  write one tree.
- **Footer buttons: stack reversed on mobile.** `flex flex-col-reverse gap-2
  sm:flex-row sm:justify-end` puts the **primary on top** (thumb-reachable) and
  full-width on phones, then right-aligns them inline on desktop. This is the most
  commonly botched responsive detail.
- **Mobile gutter + dvh height.** `w-[calc(100%-2rem)]` keeps the panel off the
  screen edges; `max-h-[90dvh]` (dynamic viewport height) prevents the footer from
  hiding behind the mobile URL bar.
- **Width per intent.** Dialog `sm:max-w-lg`; Sheet `w-3/4 sm:max-w-sm`; Drawer
  full-width bottom. Override at the `sm:` breakpoint to beat shadcn's specificity.
- **`overscroll-contain` on the body** so flick-scrolling the panel to its end
  doesn't chain-scroll the page behind it.

---

## 7. Accessibility notes

Radix + Vaul give you most of this for free — but you still have to *not break it*.

- **Roles & labels.** `role="dialog"` (or `alertdialog` for critical confirms) +
  `aria-modal="true"`, `aria-labelledby` → title, `aria-describedby` → description.
  All wired automatically **iff** you render `DialogTitle` (and ideally
  `DialogDescription`). Missing title = broken a11y + a console warning.
- **Focus trap.** Tab / Shift+Tab cycle *within* the panel and wrap; focus can't
  reach the inert page behind it.
- **Initial focus.** Moves into the panel on open — first focusable element for
  forms; for a destructive `AlertDialog`, prefer the **least-destructive** action
  (Cancel) so muscle-memory Enter doesn't nuke data.
- **Return focus.** On close, focus goes back to the trigger (or a sensible
  successor if it's gone). Don't dump focus on `<body>`.
- **Escape & scrim.** Escape closes Dialog/Sheet/Drawer. `AlertDialog` keeps
  Escape but **removes outside-click** on purpose — that friction is the point.
- **Inert + scroll-lock + `overscroll-contain`.** Background is inert and the page
  can't scroll; the panel body contains its own overscroll.
- **Announce async, don't hijack.** Surface submit errors in a `role="alert"`
  (polite) live region rather than moving focus abruptly; disabled controls carry
  the "busy" meaning.
- **Visible, designed focus rings.** Every actionable element shows `ring-ring`
  focus, never the raw browser outline. Guaranteed by the shadcn primitives.
- **Respect reduced motion** — fade only, no transform (see §8 CSS).

---

## 8. Complete, copy-pasteable code

Four files: a subscription-safe media-query hook, a `ResponsiveDialog` primitive
that renders Dialog on desktop / Drawer on mobile behind one API, the two flagship
variants, and the reduced-motion / scrim CSS.

```tsx
// hooks/use-media-query.ts
"use client";

import * as React from "react";

/**
 * SSR-safe, subscription-based media query. useSyncExternalStore avoids the
 * hydration flash you get from the useState+useEffect version, and updates when
 * the viewport crosses the breakpoint mid-session.
 */
export function useMediaQuery(query: string): boolean {
  const subscribe = React.useCallback(
    (onChange: () => void) => {
      const mql = window.matchMedia(query);
      mql.addEventListener("change", onChange);
      return () => mql.removeEventListener("change", onChange);
    },
    [query],
  );

  return React.useSyncExternalStore(
    subscribe,
    () => window.matchMedia(query).matches, // client snapshot
    () => false, // server snapshot: assume mobile-first (no match)
  );
}
```

```tsx
// components/ui/responsive-dialog.tsx
"use client";

import * as React from "react";
import { useMediaQuery } from "@/hooks/use-media-query";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";
import { cn } from "@/lib/utils";

/**
 * One overlay API, two renderings: a centered Dialog ≥640px, a bottom Drawer
 * below it. Callers write a single tree; the breakpoint picks the primitive.
 * We layer our own header/body/footer so the body scrolls and the footer sticks.
 */
const DesktopContext = React.createContext(true);
const useIsDesktop = () => React.useContext(DesktopContext);

function ResponsiveDialog(props: React.ComponentProps<typeof Dialog>) {
  const isDesktop = useMediaQuery("(min-width: 640px)");
  const Root = isDesktop ? Dialog : Drawer;
  return (
    <DesktopContext.Provider value={isDesktop}>
      <Root {...props} />
    </DesktopContext.Provider>
  );
}

function ResponsiveDialogTrigger(
  props: React.ComponentProps<typeof DialogTrigger>,
) {
  const Trigger = useIsDesktop() ? DialogTrigger : DrawerTrigger;
  return <Trigger {...props} />;
}

function ResponsiveDialogClose(props: React.ComponentProps<typeof DialogClose>) {
  const Close = useIsDesktop() ? DialogClose : DrawerClose;
  return <Close {...props} />;
}

function ResponsiveDialogContent({
  className,
  children,
  showCloseButton,
  ...props
}: React.ComponentProps<typeof DialogContent>) {
  const isDesktop = useIsDesktop();

  if (isDesktop) {
    return (
      // gap-0 + p-0: header/body/footer own their padding so the body can scroll
      // independently. max-h-[85dvh] + flex-col keeps header/footer pinned.
      <DialogContent
        showCloseButton={showCloseButton}
        className={cn(
          "flex max-h-[85dvh] flex-col gap-0 overflow-hidden p-0 sm:max-w-lg",
          className,
        )}
        {...props}
      >
        {children}
      </DialogContent>
    );
  }

  return (
    <DrawerContent
      className={cn("flex max-h-[90dvh] flex-col", className)}
      {...props}
    >
      {children}
    </DrawerContent>
  );
}

function ResponsiveDialogHeader({
  className,
  ...props
}: React.ComponentProps<"div">) {
  // pr-12 leaves room for the desktop close X (harmless on mobile).
  return (
    <div
      className={cn(
        "flex flex-col gap-1.5 px-6 pt-6 pr-12 pb-4 text-left",
        className,
      )}
      {...props}
    />
  );
}

function ResponsiveDialogTitle({
  className,
  ...props
}: React.ComponentProps<typeof DialogTitle>) {
  const Title = useIsDesktop() ? DialogTitle : DrawerTitle;
  return <Title className={cn("text-lg font-semibold", className)} {...props} />;
}

function ResponsiveDialogDescription({
  className,
  ...props
}: React.ComponentProps<typeof DialogDescription>) {
  const Description = useIsDesktop() ? DialogDescription : DrawerDescription;
  return (
    <Description
      className={cn("text-sm text-muted-foreground", className)}
      {...props}
    />
  );
}

function ResponsiveDialogBody({
  className,
  ...props
}: React.ComponentProps<"div">) {
  // The scroll region. overscroll-contain stops scroll-chaining to the page.
  return (
    <div
      className={cn("flex-1 overflow-y-auto overscroll-contain px-6", className)}
      {...props}
    />
  );
}

function ResponsiveDialogFooter({
  className,
  ...props
}: React.ComponentProps<"div">) {
  // Mobile: stacked reversed + full-width (primary on top). Desktop: right-aligned.
  return (
    <div
      className={cn(
        "mt-auto flex flex-col-reverse gap-2 border-t px-6 py-4 sm:flex-row sm:justify-end",
        className,
      )}
      {...props}
    />
  );
}

export {
  ResponsiveDialog,
  ResponsiveDialogTrigger,
  ResponsiveDialogClose,
  ResponsiveDialogContent,
  ResponsiveDialogHeader,
  ResponsiveDialogTitle,
  ResponsiveDialogDescription,
  ResponsiveDialogBody,
  ResponsiveDialogFooter,
};
```

```tsx
// components/invite-member-dialog.tsx  — Variant A
"use client";

import * as React from "react";
import { Loader2Icon } from "lucide-react";
import { toast } from "sonner";
import {
  ResponsiveDialog,
  ResponsiveDialogBody,
  ResponsiveDialogClose,
  ResponsiveDialogContent,
  ResponsiveDialogDescription,
  ResponsiveDialogFooter,
  ResponsiveDialogHeader,
  ResponsiveDialogTitle,
  ResponsiveDialogTrigger,
} from "@/components/ui/responsive-dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

type Role = "viewer" | "editor" | "admin";
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

// Replace with your real mutation (server action / TanStack mutation / fetch).
async function inviteMember(input: { email: string; role: Role }) {
  await new Promise((r) => setTimeout(r, 900));
  if (input.email.endsWith("@example.com")) throw new Error("blocked domain");
}

export function InviteMemberDialog() {
  const [open, setOpen] = React.useState(false);
  const [confirmDiscard, setConfirmDiscard] = React.useState(false);
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [email, setEmail] = React.useState("");
  const [role, setRole] = React.useState<Role>("editor");
  const [errors, setErrors] = React.useState<{ email?: string; form?: string }>(
    {},
  );

  const isDirty = email.trim() !== "" || role !== "editor";

  function reset() {
    setEmail("");
    setRole("editor");
    setErrors({});
    setIsSubmitting(false);
  }

  // Guarded dismissal: never close mid-submit; confirm if there are unsaved
  // changes; otherwise close and reset.
  function handleOpenChange(next: boolean) {
    if (next) return setOpen(true);
    if (isSubmitting) return; // ignore Escape / overlay-click while writing
    if (isDirty) return setConfirmDiscard(true);
    setOpen(false);
    reset();
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!EMAIL_RE.test(email.trim())) {
      setErrors({ email: "Enter a valid email address." });
      return;
    }
    setErrors({});
    setIsSubmitting(true);
    try {
      await inviteMember({ email: email.trim(), role });
      setOpen(false);
      reset();
      // Success is a toast, never another modal.
      toast.success("Invitation sent", {
        description: `${email.trim()} was invited as ${role}.`,
      });
    } catch {
      // Keep the dialog + the user's input; surface the failure inline.
      setIsSubmitting(false);
      setErrors({ form: "We couldn't send that invite. Please try again." });
    }
  }

  return (
    <>
      <ResponsiveDialog open={open} onOpenChange={handleOpenChange}>
        <ResponsiveDialogTrigger asChild>
          <Button>Invite member</Button>
        </ResponsiveDialogTrigger>

        <ResponsiveDialogContent
          // Block the easy exits while a request is in flight.
          onInteractOutside={(e) => isSubmitting && e.preventDefault()}
          onEscapeKeyDown={(e) => isSubmitting && e.preventDefault()}
        >
          <form onSubmit={handleSubmit} className="flex min-h-0 flex-1 flex-col">
            <ResponsiveDialogHeader>
              <ResponsiveDialogTitle>Invite a team member</ResponsiveDialogTitle>
              <ResponsiveDialogDescription>
                They&apos;ll get an email invite to join this workspace.
              </ResponsiveDialogDescription>
            </ResponsiveDialogHeader>

            <ResponsiveDialogBody className="space-y-4 py-4">
              {errors.form && (
                <p
                  role="alert"
                  aria-live="polite"
                  className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive"
                >
                  {errors.form}
                </p>
              )}

              <div className="space-y-2">
                <Label htmlFor="invite-email">Email address</Label>
                <Input
                  id="invite-email"
                  type="email"
                  autoComplete="off"
                  placeholder="teammate@company.com"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (errors.email) setErrors((p) => ({ ...p, email: undefined }));
                  }}
                  aria-invalid={!!errors.email}
                  aria-describedby={errors.email ? "invite-email-error" : undefined}
                  disabled={isSubmitting}
                  autoFocus
                />
                {errors.email && (
                  <p id="invite-email-error" className="text-sm text-destructive">
                    {errors.email}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="invite-role">Role</Label>
                <Select
                  value={role}
                  onValueChange={(v) => setRole(v as Role)}
                  disabled={isSubmitting}
                >
                  <SelectTrigger id="invite-role" className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="viewer">Viewer</SelectItem>
                    <SelectItem value="editor">Editor</SelectItem>
                    <SelectItem value="admin">Admin</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </ResponsiveDialogBody>

            <ResponsiveDialogFooter>
              <ResponsiveDialogClose asChild>
                <Button type="button" variant="ghost" disabled={isSubmitting}>
                  Cancel
                </Button>
              </ResponsiveDialogClose>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting && <Loader2Icon className="animate-spin" />}
                {isSubmitting ? "Sending…" : "Send invite"}
              </Button>
            </ResponsiveDialogFooter>
          </form>
        </ResponsiveDialogContent>
      </ResponsiveDialog>

      {/* The one allowed double-confirm: discard unsaved changes. */}
      <AlertDialog open={confirmDiscard} onOpenChange={setConfirmDiscard}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Discard this invite?</AlertDialogTitle>
            <AlertDialogDescription>
              You have unsaved changes. If you leave now, they&apos;ll be lost.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Keep editing</AlertDialogCancel>
            <AlertDialogAction
              className={cn(buttonVariants({ variant: "destructive" }))}
              onClick={() => {
                setConfirmDiscard(false);
                setOpen(false);
                reset();
              }}
            >
              Discard
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
```

```tsx
// components/delete-project-dialog.tsx  — Variant B
"use client";

import * as React from "react";
import { Loader2Icon } from "lucide-react";
import { toast } from "sonner";
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

/**
 * Irreversible action → AlertDialog (no X, no outside-click). Type-to-confirm
 * adds friction proportional to the blast radius. NOTE: we use a plain
 * destructive <Button> for the action instead of <AlertDialogAction>, because
 * AlertDialogAction auto-closes on click — and we must stay open until the async
 * delete resolves so errors land back in the same surface.
 */
export function DeleteProjectDialog({
  projectName,
  onConfirm,
}: {
  projectName: string;
  onConfirm: () => Promise<void>;
}) {
  const [open, setOpen] = React.useState(false);
  const [confirmText, setConfirmText] = React.useState("");
  const [isDeleting, setIsDeleting] = React.useState(false);
  const canDelete = confirmText === projectName && !isDeleting;

  React.useEffect(() => {
    if (!open) setConfirmText(""); // clear the challenge each time it opens
  }, [open]);

  async function handleDelete() {
    if (!canDelete) return;
    setIsDeleting(true);
    try {
      await onConfirm();
      setOpen(false);
      toast.success(`"${projectName}" was deleted.`);
    } catch {
      setIsDeleting(false);
      toast.error("Couldn't delete the project. Please try again.");
    }
  }

  return (
    <AlertDialog open={open} onOpenChange={(o) => !isDeleting && setOpen(o)}>
      <AlertDialogTrigger asChild>
        <Button variant="destructive">Delete project</Button>
      </AlertDialogTrigger>

      <AlertDialogContent
        onEscapeKeyDown={(e) => isDeleting && e.preventDefault()}
      >
        <AlertDialogHeader>
          <AlertDialogTitle>Delete “{projectName}”?</AlertDialogTitle>
          <AlertDialogDescription>
            This permanently deletes the project, its history, and all associated
            data. This action cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>

        <div className="space-y-2">
          <Label htmlFor="confirm-delete">
            Type{" "}
            <span className="font-medium text-foreground">{projectName}</span> to
            confirm
          </Label>
          <Input
            id="confirm-delete"
            value={confirmText}
            onChange={(e) => setConfirmText(e.target.value)}
            autoComplete="off"
            disabled={isDeleting}
          />
        </div>

        <AlertDialogFooter>
          {/* Cancel is the least-destructive action → it gets initial focus. */}
          <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
          <Button
            variant="destructive"
            disabled={!canDelete}
            onClick={handleDelete}
          >
            {isDeleting && <Loader2Icon className="animate-spin" />}
            {isDeleting ? "Deleting…" : "Delete project"}
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
```

```css
/* globals.css — motion polish for every overlay */

/* Premium scrim: lighter + blurred instead of the default bg-black/80.
   Set these on the *Overlay className in components/ui/{dialog,alert-dialog,sheet}.tsx:
   e.g.  "fixed inset-0 z-50 bg-black/50 backdrop-blur-sm ..."               */

/* Reduced motion: keep the fade, drop the zoom/slide. These --tw-* vars are
   what tailwindcss-animate uses for zoom-in-95 / slide-in-*; neutralizing them
   leaves opacity-only transitions. */
@media (prefers-reduced-motion: reduce) {
  [data-slot="dialog-content"],
  [data-slot="alert-dialog-content"],
  [data-slot="sheet-content"] {
    --tw-enter-scale: 1;
    --tw-exit-scale: 1;
    --tw-enter-translate-x: 0;
    --tw-enter-translate-y: 0;
    --tw-exit-translate-x: 0;
    --tw-exit-translate-y: 0;
    animation-duration: 120ms !important;
  }
}
```

**Wiring notes.** `<Toaster />` (from `sonner`) must be mounted once at the root
for the success/error toasts. Exit animations (~150ms) run faster than entrances
(~200ms) because the user is already leaving — shadcn's defaults encode this; keep
it. Modals scale from **center** (`transform-origin: center`) — never from the
trigger — because they're centered, not anchored.

---

## 9. Anti-slop callout

The tells that mark an overlay as generated-not-crafted — and the fix:

- **A modal for errors / loading / success.** These happen constantly; a modal
  demands undivided attention. Use inline messages, button spinners, and **toasts**.
  A "Success!" modal you have to dismiss is peak slop.
- **The heavy `bg-black/80` scrim.** The stock shadcn backdrop screams "untouched
  default." Drop to `bg-black/50 backdrop-blur-sm` for the Linear/Vercel feel.
- **No loading state — closes optimistically then errors.** Firing the mutation,
  closing the modal, then toasting a failure loses the user's input. Keep it open,
  disable the primary, block the exits until it resolves.
- **Missing `DialogTitle`.** Silent a11y break + runtime warning. Always render it;
  `sr-only` if the design has no visible title.
- **Desktop-aligned footer on mobile.** Right-aligned buttons that don't stack are
  unreachable by thumb. `flex-col-reverse` → full-width, primary on top.
- **Trapping the user.** A dialog with no X, no Escape, no outside-click, no Cancel
  is hostile — *unless* it's an `AlertDialog`, where removing outside-click is the
  intentional friction. Know which one you're building.
- **Stacked / nested modals.** A modal opening a modal opening a modal is a flow
  smell. The only sanctioned nesting is a single discard/confirm `AlertDialog`.
- **Dumping a whole page into a dialog.** Multi-section, heavily-scrolling content
  wants a page or a multi-step flow with autosave — not a 90vh modal.
- **A Dialog where a Popover would do.** Reserve the blocking, focus-trapping
  overlay for genuinely modal moments; don't nuke a tooltip-sized interaction.
- **Animating width/height or `scale(0)`.** Layout-animating jank. Animate
  **transform + opacity only**, entering from `scale(0.95)` — never `scale(0)`.
- **Hardcoded grays.** `bg-white` / `text-gray-500` break in dark mode. Use
  `bg-background` / `text-muted-foreground` tokens.
- **A `vh`-height panel on mobile.** The footer hides behind the URL bar. Use `dvh`.

---

## 10. Decision flow (recap)

1. **Pick the primitive** — Dialog (form) · AlertDialog (irreversible) · Sheet
   (complementary) · Drawer (mobile/bottom) · Responsive pair (both). Not modal at
   all? → Popover / Dropdown / inline.
2. **Anatomy** — Trigger `asChild`, required Title/Description (`sr-only` if
   needed), fixed header, scrolling body, sticky footer.
3. **Token everything** — `bg-background`, `text-muted-foreground`, `border`,
   `ring-ring`, destructive tokens; the scrim is the one deliberate fixed alpha,
   lightened + blurred.
4. **Design every state** — submitting keeps-open + disabled primary + blocked
   exits; inline field errors + polite form-error region; success → toast;
   destructive → AlertDialog (+ type-to-confirm for high stakes); guarded close.
5. **Go responsive** — swap Dialog ↔ Drawer at `sm`; footer stacks reversed +
   full-width; `dvh` height; `overscroll-contain` body.
6. **A11y** — focus trap, correct initial focus (Cancel for destructive), return
   focus, Escape, inert + scroll-lock, visible focus rings.
7. **Motion** — 200ms in / 150ms out, ease-out, `scale(0.95)` + fade,
   transform-origin center, reduced-motion = fade only.
8. **Controlled state** whenever dismissal must be gated (in-flight / unsaved).

---

## Sources

- shadcn/ui — Dialog: https://ui.shadcn.com/docs/components/dialog
- shadcn/ui — Alert Dialog: https://ui.shadcn.com/docs/components/alert-dialog
- shadcn/ui — Sheet: https://ui.shadcn.com/docs/components/sheet
- shadcn/ui — Drawer (Vaul): https://ui.shadcn.com/docs/components/drawer
- shadcn/ui — Responsive Dialog/Drawer pattern (Combobox docs): https://ui.shadcn.com/docs/components/combobox
- Radix Primitives — Dialog & Alert Dialog: https://www.radix-ui.com/primitives/docs/components/alert-dialog
- Vaul (Emil Kowalski): https://vaul.emilkowal.ski/
- W3C WAI-ARIA APG — Dialog (Modal) Pattern: https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/
- Vercel — Web Interface Guidelines: https://vercel.com/design/guidelines
- Emil Kowalski — Animations on the Web: https://animations.dev/
- Mantlr — How Stripe/Linear/Vercel ship premium UI: https://mantlr.com/blog/stripe-linear-vercel-premium-ui
- LogRocket — Modal UX design patterns & best practices: https://blog.logrocket.com/ux-design/modal-ux-design-patterns-examples-best-practices/
