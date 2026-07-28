# Forms (Settings / Create · Validation · Multi-field)

> Category: `forms` · Stack: React + Tailwind v4 + shadcn/ui
> A multi-field settings/create form: `react-hook-form` + `zod`, rendered with shadcn's
> **Field** family. One column, top-aligned labels, validate-on-submit-then-re-validate,
> and a Linear-style sticky save bar that only appears when something actually changed.

---

## When to use it

Reach for this recipe whenever a user **enters or edits structured data** and expects to
review it before it's committed: a settings panel, a "create new resource" screen, a profile
editor, an onboarding step. It's the workhorse behind every `/settings`, every "New project"
dialog, every account page.

Use it when:

- You have **more than one field** and at least one needs **validation** (required, format,
  length, or a cross-field rule like "end date after start date").
- The user makes a **batch of declarative edits** (text, select, radio, checkbox) and commits
  them with an explicit **Save** — the opposite of a single instant toggle.
- You're prefilling **existing values** and need clean **dirty-state** tracking so "Save"
  means something (settings), or starting from **empty defaults** and redirecting on success
  (create).

Reach for something else when:

- It's a **single instant toggle** (dark mode, notifications on/off) — that's an **autosaving
  Switch**, not a form. Never bolt a Save button onto one switch.
- It's **one value edited in place** in a table or card — that's an **inline edit** (Enter
  saves, Esc cancels), not a full form surface.
- The flow is **long or branching** (>~9 fields, distinct phases like onboarding/checkout) —
  promote it to a **multi-step wizard** (Variant C).
- It's a **search / filter** bar — reuse the field anatomy but drop submit-and-validate;
  debounce and apply live.

---

## Anatomy

The canonical settings form, top → bottom. The field order inside a group is load-bearing:
**label → control → description → error**, always in that stack.

```
┌────────────────────────────────────────────────┐
│  Project settings                   ✓ All saved │ ← 1. Header: title + desc + aria-live status
│  Update your project's name, URL, and…          │
│                                                  │
│  ⚠ Couldn't save your changes. Try again.       │ ← 2. Form-level (server) error, role="alert"
│                                                  │
│  Project name                                    │ ← 3. Field = label → control → desc → error
│  [ Acme Marketing Site                     ]     │
│  The display name shown across your dashboard.   │
│                                                  │
│  URL slug                                        │ ← 4. Prefixed input (still ONE datum)
│  [ acme.dev/ ▏ acme-marketing              ]     │
│  Lowercase letters, numbers, and hyphens.        │
│                                                  │
│  Description                            42 / 280 │ ← 5. Textarea + live character count
│  [ Landing pages and campaign microsites…  ]     │
│  ⚠ Add a description before going public.        │    inline error: icon + text, never color-only
│                                                  │
│  ┌ Visibility ─────────────────────────────────┐│ ← 6. FieldSet + FieldLegend (grouped radios)
│  │ (•) Private            ( ) Public            ││    card-style options, one hit target each
│  └──────────────────────────────────────────────┘│
│                                                  │
│  Region                                          │ ← 7. Select (controlled via Controller)
│  [ Washington, D.C. (iad1)                 ▾ ]   │
│                                                  │
│  Usage analytics                          [ ●▭ ] │ ← 8. Switch in a horizontal Field —
│  Collect anonymous events to improve…            │    part of explicit Save, NOT autosaved
└────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────┐
  │ You have unsaved changes.  [Discard] [ Save ] │ ← 9. Sticky save bar: mounts only when dirty
  └──────────────────────────────────────────────┘
```

**Layout structure (the shell):**

- **Content column** — one column, `max-w-2xl` for a settings card (`max-w-lg`/`max-w-xl` for
  a bare form body, `max-w-md` for auth). Never let inputs run the full viewport width.
- **shadcn `Field` family** is the composition layer (the modern successor to the old
  `Form`/`FormField` primitives):
  - `Field` — wraps one field; carries `data-invalid` to style the whole block red at once;
    `orientation="horizontal"` puts the control beside the label (used for the Switch).
  - `FieldLabel` — the styled `<label>`; `htmlFor` wired to the control `id`. `asChild`-friendly
    so a whole card can *be* the label of a radio option.
  - `FieldContent` — flex column that groups label + description when the control sits beside them.
  - `FieldDescription` — helper text; wired to the control via `aria-describedby`.
  - `FieldError` — accessible error slot; takes an rhf `errors` array or `children`.
  - `FieldGroup` — stacks fields with `gap-6` and enables container queries.
  - `FieldSet` + `FieldLegend` — semantic `<fieldset>`/`<legend>` for radio/checkbox groups.
  - `FieldSeparator` — a divider between sections; use sparingly.
- **One logical datum per row.** Fields go one-per-row, top-aligned label above the control.
  The *only* time two controls share a row is when they're one datum (City/State/Zip, card
  expiry/CVC, first/last name). The slug here is one input with a static prefix — still one row.
- **Save models, never mixed on one surface:** explicit **Save** for declarative text/select
  fields (this recipe); **autosave** for imperative toggles that expect instant feedback. The
  Switch above is included only because it commits *with* the Save button — it isn't autosaved.

---

## Token-driven styling

Every color is a shadcn CSS variable — **no hardcoded hex**. Light/dark and per-tenant rebrands
fall out of the token layer for free; a stray `#111` is the single fastest way to make a form
look unfinished in dark mode.

| Surface | Token / class | Notes |
|---|---|---|
| Page background | `bg-muted/40` or `bg-background` | `muted/40` gives the card something to float on |
| Card surface | `bg-card text-card-foreground` | shadcn `Card` sets this |
| Field label | `text-foreground` | shadcn `Label`/`FieldLabel` default |
| Helper / description | `text-muted-foreground` | `FieldDescription`; the whole "quiet" layer |
| Input surface + border | `bg-transparent border-input` | built into shadcn `Input`/`Textarea` |
| Placeholder | `placeholder:text-muted-foreground` | built in — example value, never an instruction |
| Focus ring | `focus-visible:ring-ring/50` | built into every shadcn control |
| Invalid state | `aria-invalid:border-destructive aria-invalid:ring-destructive/20` | shadcn styles `aria-invalid` for you |
| Error text | `text-destructive` | `FieldError` |
| Primary CTA | `bg-primary text-primary-foreground` | shadcn `Button` default |
| Discard / secondary | `variant="ghost"` → `text-foreground` | low-emphasis, never a red "Reset" |
| Selected radio card | `border-primary bg-primary/5` | via `has-[[data-state=checked]]:` |
| Save bar | `bg-card/80 backdrop-blur border shadow-lg` | frosted, elevated, floats above content |

The variables (provided by `npx shadcn init`; shown so the recipe is self-contained). Tailwind v4
wires them into utilities via the `@theme inline` block:

```css
/* app/globals.css — shadcn v4 token layer, trimmed to the tokens this recipe uses */
:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --border: oklch(0.922 0 0);
  --input: oklch(0.922 0 0);
  --ring: oklch(0.708 0 0);
  --destructive: oklch(0.577 0.245 27.325);
  --radius: 0.625rem;
}
.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --card: oklch(0.205 0 0);
  --card-foreground: oklch(0.985 0 0);
  --primary: oklch(0.985 0 0);
  --primary-foreground: oklch(0.205 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --border: oklch(1 0 0 / 10%);
  --input: oklch(1 0 0 / 15%);
  --ring: oklch(0.556 0 0);
  --destructive: oklch(0.704 0.191 22.216);
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --color-destructive: var(--destructive);
  --radius-lg: var(--radius);
  --radius-md: calc(var(--radius) - 2px);
}
```

**Rules of thumb**

- **Spacing:** `FieldGroup` handles it — `gap-6` (24px) between fields, a tight `gap-2` inside a
  field (label → control → error). Between distinct sections use `gap-8`–`gap-10` or a
  `FieldSeparator`. Don't hand-roll `space-y-*` per field; let the group own the rhythm.
- **Invalid = one source of truth:** `data-invalid` on `Field` + `aria-invalid` on the control.
  Set both from the same `!!errors.field` and the border, ring, label, and message all flip red
  together.
- **Never invent an accent for "valid".** A green ring on every filled field is noise. Reserve
  affordances (a check) for high-stakes fields only (password strength, slug availability).
- Swap `--primary` once and the whole form — selected radio card, focus ring on the CTA — re-themes.

---

## Variants

### Variant A — Create / new-resource form

First-time creation, not editing. Differences from the settings default:

- **Empty `defaultValues`**, not prefilled.
- **Autofocus the first field** — desktop only (an autofocus on mobile yanks the keyboard up and
  scrolls the page).
- **One primary CTA** — "Create project", always visible (no dirty-gated save bar; there's nothing
  to "discard" yet). Disabled only while submitting.
- **Redirect on success** instead of resetting in place.

```tsx
// Wire createSchema / createProject to your own API — shape shown for intent.
export function CreateProjectForm() {
  const router = useRouter()
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CreateValues>({
    resolver: zodResolver(createSchema),
    defaultValues: { name: "", slug: "" },
    reValidateMode: "onChange",
  })

  async function onSubmit(values: CreateValues) {
    const project = await createProject(values) // POST + idempotency key
    router.push(`/projects/${project.slug}`) // redirect on success
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <FieldGroup>
        <Field data-invalid={!!errors.name}>
          <FieldLabel htmlFor="name">Project name</FieldLabel>
          <Input id="name" autoFocus aria-invalid={!!errors.name} {...register("name")} />
          <FieldError errors={[errors.name]} />
        </Field>
        {/* …slug field… */}
        <Button type="submit" disabled={isSubmitting} className="w-full">
          {isSubmitting ? (
            <>
              <Loader2 className="size-4 animate-spin" />
              Creating…
            </>
          ) : (
            "Create project"
          )}
        </Button>
      </FieldGroup>
    </form>
  )
}
```

### Variant B — Card-per-section settings (per-section Save)

The other dominant SaaS settings pattern (Vercel/Stripe): instead of one form with a global
sticky bar, each concern is its **own bordered card with its own footer Save**. The footer carries
a helper note on the **left** and the Save button on the **right**; each card is an independent
`react-hook-form` instance, so saving "Name" doesn't touch "Danger zone". Use this when sections
are genuinely independent and you want per-section success/error. Use the sticky-bar default
(below) when it's one cohesive set of settings edited together.

```tsx
<Card>
  <CardHeader>
    <CardTitle>Project name</CardTitle>
    <CardDescription>Used to identify your project on the dashboard.</CardDescription>
  </CardHeader>
  <CardContent>
    <Input id="name" aria-invalid={!!errors.name} {...register("name")} />
    <FieldError errors={[errors.name]} />
  </CardContent>
  <CardFooter className="border-t justify-between gap-4">
    <p className="text-muted-foreground text-sm">Max 64 characters.</p>
    {/* Save stays enabled; only disabled while submitting. */}
    <Button type="submit" disabled={isSubmitting}>Save</Button>
  </CardFooter>
</Card>
```

### Variant C — Multi-step wizard (long / branching flows)

For onboarding, checkout, or anything >~9 fields or with distinct phases. 3–6 steps, ≤5–9 fields
per step, a progress/step indicator, **validate per step before "Next"** (`await trigger(stepFields)`),
data preserved on "Back", a final review step, and save-and-resume for long flows. Same field
anatomy; the wizard is orchestration around it.

---

## Interaction / state matrix

Every element ships with **all** these states, not just the happy path.

**Per field:**

| State | Behavior |
|---|---|
| **Empty / placeholder** | Placeholder is an *example value* (`acme-marketing`, `you@example.com`), never an instruction. Optional trailing ellipsis to signal intent. |
| **Focus** | Visible `focus-visible` ring (`ring-ring/50`) — `:focus-visible`, never bare `:focus`. Built into shadcn controls. |
| **Filled / valid** | No special styling by default. A success affordance (check) only for high-stakes fields. |
| **Invalid** | `aria-invalid` on control + `data-invalid` on `Field` → destructive border + ring + red inline message with an icon. Never color alone. |
| **Loading (async validation)** | e.g. checking slug availability — inline spinner in the field's suffix; don't block typing. |
| **Disabled** | Only when input is truly impossible. Keep fields *focusable* while the form saves; don't disable a whole form on invalid. |
| **Read-only** | Value shown, not editable — visually distinct from disabled. |

**Per form:**

| State | Behavior |
|---|---|
| **Pristine** | `defaultValues` loaded, no errors, no save bar (nothing to save). |
| **Dirty** | `formState.isDirty` → sticky save bar slides in; drives the unsaved-changes guard. |
| **Submitting** | `formState.isSubmitting` → Save shows a spinner, **keeps its label width**, disables itself *now only*; prevent double-submit with an idempotency key. |
| **Submit success** | Persist → `reset(values)` to rebaseline (clears `isDirty`, hides the bar) → announce inline via `aria-live` ("All changes saved"), not a toast-only confirmation. |
| **Submit error (server)** | **Preserve every value.** Show a form-level `role="alert"` banner, map field-specific errors back with `setError`, and let rhf focus the first invalid field. |

Two rules that separate shipped-quality from demo-quality:

1. **The Save button is gated on *submitting*, not on *validity*.** Keep it clickable when the form
   is invalid — clicking surfaces the errors and jumps focus to the first bad field. A pre-disabled
   button just hides *why* it's disabled.
2. **On any error, never clear what the user typed.** Server rejected the slug? Keep all six fields
   exactly as entered and point the error at the slug.

---

## Validation timing (the rule that matters most)

- **Validate on submit, then re-validate on change.** `mode: "onSubmit"` + `reValidateMode: "onChange"`
  (both rhf defaults) is the researched sweet spot: don't nag a field the user hasn't finished, but
  once it *has* errored, clear the message live as they fix it.
- **Required/empty:** validate on **submit only** — never throw "required" at a field the user hasn't
  reached yet.
- **Format fields with clear rules** (slug, email, password): on-blur (`mode: "onTouched"`) or live
  inline feedback (strength meter, "slug available") is welcome. `onChange`-from-first-keystroke is
  too aggressive.
- **Cross-field / conditional rules** live in Zod `.superRefine()` (or `.refine()`), which sees the
  whole object — confirm-password, "end date after start date", or the "public projects need a
  description" rule in the example below:

  ```ts
  .superRefine((values, ctx) => {
    if (values.visibility === "public" && !values.description) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["description"], // attach the error to the right field
        message: "Add a description before making the project public.",
      })
    }
  })
  ```

- **`trim()` in the schema** before validating so trailing whitespace never trips a length check.
  **Don't block paste or keystrokes** — validate and show feedback instead.
- **Always re-validate server-side.** Client validation is UX, not security.
- **Error grammar** (Geist / NN/G): name the field, name the constraint, end with a period, skip
  "please". `Project name is required.` / `Slug must be at least 3 characters.` — not `Invalid input.`

---

## Responsive behavior

- **Body width:** `max-w-2xl` for the settings card; the card is `w-full` up to that cap, so on a
  phone it's edge-to-edge minus the page gutter (`px-4`). Inputs never span a wide desktop viewport.
- **Input font-size ≥16px on mobile.** shadcn `Input`/`Textarea` are `text-base md:text-sm` — 16px on
  mobile (prevents iOS auto-zoom), 14px on desktop. **Don't** override to `text-sm` unconditionally.
- **Container-query field groups:** `FieldGroup` enables `@container/field-group`, so a horizontal
  field can fold to vertical based on *its container's* width, not a global media query. The radio
  cards here go `grid gap-3 sm:grid-cols-2` — stacked on mobile, side-by-side once there's room.
- **Sticky save bar:** `sticky bottom-4` keeps it reachable without scrolling to the page bottom; on
  mobile it hugs the viewport bottom above the browser chrome.
- **Page height:** `min-h-svh`, not `min-h-screen`, so the layout doesn't jump when the mobile URL bar
  shows/hides.
- **Touch targets:** shadcn's default control height plus label padding clears the comfortable tap
  zone; a checkbox/radio and its label share one hit target (no dead zone). Don't shrink controls on
  mobile.

---

## Accessibility

- **Real `<label htmlFor>` for every control** (`FieldLabel` gives you this). Clicking the label
  focuses the control. Never placeholder-as-label — it vanishes on input and fails screen readers.
- **Helper + error wired via `aria-describedby`; `aria-invalid` on invalid controls.** shadcn's
  `Field`/`FieldDescription`/`FieldError` wire the ARIA relationships; you supply `aria-invalid`.
- **Group radios/checkboxes** in `FieldSet` + `FieldLegend` (`<fieldset>`/`<legend>`) so the group has
  an accessible name.
- **Never signal an error by color alone** — pair the destructive text with an icon (the example puts
  an `AlertCircle` in every `FieldError`) *and* the `aria-invalid` ring.
- **On submit with errors, move focus to the first invalid field** — rhf does this by default
  (`shouldFocusError: true`).
- **Announce success without a toast:** an `aria-live="polite"` region ("All changes saved") is read
  out and stays on screen. Toasts have real a11y pitfalls; if you use one, pair it with a visible
  persistent signal (the save bar disappearing).
- **The form-level server error is `role="alert"`** (assertive live region) so it's announced the
  moment it appears.
- **`autoComplete` + meaningful `name`** for autofill; support password managers, 2FA/one-time-code
  paste. Turn autocomplete *off* only where it's genuinely wrong (like a slug).
- **Keyboard:** everything operable; a `Textarea` uses Enter for newlines and Cmd/Ctrl+Enter to
  submit; a single-input form submits on Enter. Autofocus the primary input on **desktop only**.

---

## Anti-slop callout

> The tells that mark a form as AI-generated or junior — and what to do instead.

- ❌ **Hardcoded `#111`/`#f5f5f5`.** → `bg-card` / `text-foreground` / `text-muted-foreground`. One
  off-token color and dark mode looks broken.
- ❌ **Placeholder used as the label.** → A persistent `<label>` above the control; the placeholder is
  an optional *example value*.
- ❌ **Pre-disabling Save until the form is valid.** → Keep it enabled; clicking surfaces the errors and
  focuses the first bad field. Gate on *submitting*, not validity.
- ❌ **Validating every keystroke from empty.** → Validate on submit, then re-validate on change. Don't
  flash "required" at a field the user is still walking toward.
- ❌ **Vague errors — "Invalid input", "Error".** → Name the field + the fix: "Slug must be at least 3
  characters." End with a period, skip "please".
- ❌ **A red "Reset" / "Clear" button.** → In a save bar, offer **Discard** (reverts to last-saved), and
  make it low-emphasis. Never a form-clearing Reset next to Submit — one mis-click nukes their work.
- ❌ **Multi-column form bodies.** → One column, top-aligned labels. Two controls share a row only when
  they're one datum (expiry/CVC, city/state/zip).
- ❌ **Losing input on a server error.** → Preserve every value; map field errors back and repopulate.
- ❌ **Toast as the *only* save confirmation.** → Inline `aria-live` status; pair a toast with a visible
  signal if you must use one.
- ❌ **Mixing autosave and explicit Save in one form.** → Pick one per surface. A lone Switch autosaves;
  a form of text fields uses explicit Save (a Switch inside it commits *with* Save).
- ❌ **Blocking paste, or blocking keystrokes in number fields.** → Let them type/paste anything;
  validate and show feedback.
- ❌ **Wrapping a labelled input in a tooltip for its explainer.** → Put the explainer in a
  `FieldDescription` sibling; a tooltip steals the accessible name.
- ❌ **A 15-field single page** that should be a wizard. → Split into 3–6 steps with per-step validation.
- ❌ **Spinner flicker on a 200ms save.** → Add a ~150–300ms show-delay and a ~300–500ms minimum
  visible time so fast saves don't strobe.

---

## Complete example

A drop-in multi-field **project settings** form: `react-hook-form` + `zod`, the shadcn `Field`
family, a live character count, a card-style radio group, a controlled Select and Switch, a
cross-field rule, an unsaved-changes guard, and a sticky save bar that appears only when dirty.
Wire the `updateProject` call where marked.

Prereqs:

```bash
npx shadcn@latest add button card input textarea select radio-group switch field
npm i react-hook-form zod @hookform/resolvers lucide-react
```

```tsx
// components/project-settings-form.tsx
"use client"

import * as React from "react"
import { useForm, Controller } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { AlertCircle, Check, Loader2 } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Field,
  FieldContent,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
  FieldLegend,
  FieldSet,
} from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Switch } from "@/components/ui/switch"

const REGIONS = [
  { value: "iad1", label: "Washington, D.C. (iad1)" },
  { value: "sfo1", label: "San Francisco (sfo1)" },
  { value: "fra1", label: "Frankfurt (fra1)" },
  { value: "sin1", label: "Singapore (sin1)" },
] as const

const VISIBILITY_OPTIONS = [
  {
    value: "private" as const,
    title: "Private",
    description: "Only members of your team can access it.",
  },
  {
    value: "public" as const,
    title: "Public",
    description: "Anyone with the link can view it.",
  },
]

const DESCRIPTION_MAX = 280

// `trim()` first so trailing whitespace never trips a length rule.
const schema = z
  .object({
    name: z
      .string()
      .trim()
      .min(1, "Project name is required.")
      .max(64, "Keep the name under 64 characters."),
    slug: z
      .string()
      .trim()
      .min(3, "Slug must be at least 3 characters.")
      .regex(/^[a-z0-9-]+$/, "Use lowercase letters, numbers, and hyphens only."),
    description: z
      .string()
      .trim()
      .max(DESCRIPTION_MAX, `Keep the description under ${DESCRIPTION_MAX} characters.`)
      .optional(),
    visibility: z.enum(["private", "public"]),
    region: z.string().min(1, "Select a region."),
    analytics: z.boolean(),
  })
  .superRefine((values, ctx) => {
    // Cross-field rule: superRefine sees the whole object.
    if (values.visibility === "public" && !values.description) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["description"],
        message: "Add a description before making the project public.",
      })
    }
  })

type FormValues = z.infer<typeof schema>

// Prefilled from the server. In a real app these arrive as a prop.
const defaultValues: FormValues = {
  name: "Acme Marketing Site",
  slug: "acme-marketing",
  description: "Landing pages and campaign microsites for the Acme brand.",
  visibility: "private",
  region: "iad1",
  analytics: true,
}

export function ProjectSettingsForm() {
  const [justSaved, setJustSaved] = React.useState(false)

  const {
    register,
    control,
    handleSubmit,
    reset,
    watch,
    setError,
    clearErrors,
    formState: { errors, isDirty, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues,
    // Validate on submit; once a field has errored, clear it live as it's
    // fixed. Both are rhf defaults — spelled out here for intent.
    mode: "onSubmit",
    reValidateMode: "onChange",
  })

  const descriptionLength = watch("description")?.length ?? 0

  // Guard hard navigation (tab close / reload) while dirty. Pair this with
  // your router's in-app navigation guard for client-side route changes.
  React.useEffect(() => {
    if (!isDirty) return
    const onBeforeUnload = (event: BeforeUnloadEvent) => {
      event.preventDefault()
      event.returnValue = ""
    }
    window.addEventListener("beforeunload", onBeforeUnload)
    return () => window.removeEventListener("beforeunload", onBeforeUnload)
  }, [isDirty])

  // Auto-clear the "saved" confirmation after a beat.
  React.useEffect(() => {
    if (!justSaved) return
    const timer = setTimeout(() => setJustSaved(false), 2500)
    return () => clearTimeout(timer)
  }, [justSaved])

  async function onSubmit(values: FormValues) {
    setJustSaved(false)
    clearErrors("root")
    try {
      // ── Wire your API here ────────────────────────────────────────────
      // Pass an idempotency key so a double-submit or retry can't write twice:
      //   await updateProject(values, { idempotencyKey })
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // reset() to the just-saved values: clears isDirty (hides the save bar)
      // while keeping the new values as the baseline for the next edit.
      reset(values)
      setJustSaved(true)
    } catch {
      // Server error: preserve every field, surface a form-level message, and
      // map any field-specific errors back onto their fields, e.g.
      //   setError("slug", { message: "That slug is already taken." })
      setError("root", { message: "Couldn't save your changes. Try again." })
    }
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      noValidate
      className="mx-auto w-full max-w-2xl"
    >
      <Card>
        <CardHeader>
          <CardTitle>Project settings</CardTitle>
          <CardDescription>
            Update your project&apos;s name, URL, and visibility.
          </CardDescription>
          {/* Success announced politely + shown inline, not a toast-only
              confirmation. The region is always mounted so SRs pick it up. */}
          <div aria-live="polite" className="min-h-5 text-sm">
            {justSaved && (
              <span className="text-foreground inline-flex items-center gap-1.5">
                <Check className="size-3.5" aria-hidden="true" />
                All changes saved
              </span>
            )}
          </div>
        </CardHeader>

        <CardContent>
          <FieldGroup>
            {/* Form-level (server) error — assertive live region */}
            {errors.root && (
              <div
                role="alert"
                className="border-destructive/50 bg-destructive/10 text-destructive flex items-center gap-2 rounded-md border px-3 py-2 text-sm"
              >
                <AlertCircle className="size-4 shrink-0" aria-hidden="true" />
                {errors.root.message}
              </div>
            )}

            {/* Project name — uncontrolled Input via register (no re-render/keystroke) */}
            <Field data-invalid={!!errors.name}>
              <FieldLabel htmlFor="name">Project name</FieldLabel>
              <Input
                id="name"
                aria-invalid={!!errors.name}
                placeholder="Acme Marketing Site"
                {...register("name")}
              />
              <FieldDescription>
                The display name shown across your dashboard.
              </FieldDescription>
              {errors.name && (
                <FieldError className="flex items-center gap-1.5">
                  <AlertCircle className="size-3.5 shrink-0" aria-hidden="true" />
                  {errors.name.message}
                </FieldError>
              )}
            </Field>

            {/* URL slug — a prefixed input; still one logical datum, one row */}
            <Field data-invalid={!!errors.slug}>
              <FieldLabel htmlFor="slug">URL slug</FieldLabel>
              <div className="relative">
                <span className="text-muted-foreground pointer-events-none absolute inset-y-0 left-3 flex items-center text-sm">
                  acme.dev/
                </span>
                <Input
                  id="slug"
                  aria-invalid={!!errors.slug}
                  placeholder="acme-marketing"
                  autoComplete="off"
                  spellCheck={false}
                  className="pl-[4.75rem]" // clears the static prefix
                  {...register("slug")}
                />
              </div>
              <FieldDescription>
                Lowercase letters, numbers, and hyphens. This is your public URL.
              </FieldDescription>
              {errors.slug && (
                <FieldError className="flex items-center gap-1.5">
                  <AlertCircle className="size-3.5 shrink-0" aria-hidden="true" />
                  {errors.slug.message}
                </FieldError>
              )}
            </Field>

            {/* Description — Textarea with a live character count */}
            <Field data-invalid={!!errors.description}>
              <div className="flex items-center justify-between">
                <FieldLabel htmlFor="description">Description</FieldLabel>
                <span
                  className={cn(
                    "text-muted-foreground text-xs tabular-nums",
                    descriptionLength > DESCRIPTION_MAX && "text-destructive"
                  )}
                >
                  {descriptionLength}/{DESCRIPTION_MAX}
                </span>
              </div>
              <Textarea
                id="description"
                rows={3}
                aria-invalid={!!errors.description}
                placeholder="What is this project for?"
                {...register("description")}
              />
              {errors.description && (
                <FieldError className="flex items-center gap-1.5">
                  <AlertCircle className="size-3.5 shrink-0" aria-hidden="true" />
                  {errors.description.message}
                </FieldError>
              )}
            </Field>

            {/* Visibility — grouped controls live in a fieldset/legend.
                Each whole card IS the radio's label. */}
            <Controller
              control={control}
              name="visibility"
              render={({ field }) => (
                <FieldSet>
                  <FieldLegend>Visibility</FieldLegend>
                  <FieldDescription>
                    Public projects are discoverable by anyone with the link.
                  </FieldDescription>
                  <RadioGroup
                    value={field.value}
                    onValueChange={field.onChange}
                    className="grid gap-3 sm:grid-cols-2"
                  >
                    {VISIBILITY_OPTIONS.map((option) => (
                      <FieldLabel
                        key={option.value}
                        htmlFor={`visibility-${option.value}`}
                        className="has-[[data-state=checked]]:border-primary has-[[data-state=checked]]:bg-primary/5 flex cursor-pointer items-start gap-3 rounded-lg border p-4 font-normal transition-colors"
                      >
                        <RadioGroupItem
                          id={`visibility-${option.value}`}
                          value={option.value}
                          className="mt-0.5"
                        />
                        <span className="grid gap-1">
                          <span className="text-sm leading-none font-medium">
                            {option.title}
                          </span>
                          <span className="text-muted-foreground text-sm">
                            {option.description}
                          </span>
                        </span>
                      </FieldLabel>
                    ))}
                  </RadioGroup>
                </FieldSet>
              )}
            />

            {/* Region — controlled Select via Controller */}
            <Controller
              control={control}
              name="region"
              render={({ field }) => (
                <Field data-invalid={!!errors.region}>
                  <FieldLabel htmlFor="region">Region</FieldLabel>
                  <Select value={field.value} onValueChange={field.onChange}>
                    <SelectTrigger
                      id="region"
                      aria-invalid={!!errors.region}
                      className="w-full"
                    >
                      <SelectValue placeholder="Select a region" />
                    </SelectTrigger>
                    <SelectContent>
                      {REGIONS.map((region) => (
                        <SelectItem key={region.value} value={region.value}>
                          {region.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FieldDescription>
                    Where your project&apos;s data is stored. This can&apos;t be
                    changed later.
                  </FieldDescription>
                  {errors.region && (
                    <FieldError className="flex items-center gap-1.5">
                      <AlertCircle className="size-3.5 shrink-0" aria-hidden="true" />
                      {errors.region.message}
                    </FieldError>
                  )}
                </Field>
              )}
            />

            {/* Usage analytics — a Switch in a horizontal Field. It's part of
                explicit Save (grouped with the rest), NOT autosaved. */}
            <Controller
              control={control}
              name="analytics"
              render={({ field }) => (
                <Field orientation="horizontal">
                  <FieldContent>
                    <FieldLabel htmlFor="analytics">Usage analytics</FieldLabel>
                    <FieldDescription>
                      Collect anonymous events to improve your dashboard.
                    </FieldDescription>
                  </FieldContent>
                  <Switch
                    id="analytics"
                    checked={field.value}
                    onCheckedChange={field.onChange}
                  />
                </Field>
              )}
            />
          </FieldGroup>
        </CardContent>
      </Card>

      {/* Sticky save bar — mounts only when the form is dirty (Linear/Stripe
          pattern). Save is disabled only while submitting, never on invalid:
          clicking an invalid form surfaces the errors and focuses the first
          bad field (rhf shouldFocusError default). */}
      {isDirty && (
        <div className="bg-card/80 supports-[backdrop-filter]:bg-card/60 sticky bottom-4 z-10 mt-4 flex items-center gap-3 rounded-xl border px-4 py-3 shadow-lg backdrop-blur">
          <p className="text-muted-foreground text-sm">You have unsaved changes.</p>
          <div className="ml-auto flex gap-2">
            {/* Discard reverts to the last-saved values — low-emphasis, never a red Reset. */}
            <Button
              type="button"
              variant="ghost"
              onClick={() => reset()}
              disabled={isSubmitting}
            >
              Discard
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Saving…
                </>
              ) : (
                "Save changes"
              )}
            </Button>
          </div>
        </div>
      )}
    </form>
  )
}
```

```tsx
// app/settings/page.tsx
import { ProjectSettingsForm } from "@/components/project-settings-form"

export default function SettingsPage() {
  return (
    <main className="bg-muted/40 min-h-svh px-4 py-10 md:py-16">
      <ProjectSettingsForm />
    </main>
  )
}
```

---

## Quick checklist before you ship

- [ ] All colors are tokens (`grep` the file for `#` — should find nothing).
- [ ] Every control has a real `<label htmlFor>` (via `FieldLabel`); no placeholder-as-label.
- [ ] Invalid state sets both `data-invalid` on `Field` and `aria-invalid` on the control.
- [ ] Every error names the field + the fix, ends with a period, and has an icon (not color alone).
- [ ] Save is enabled while invalid; disabled only while submitting; spinner keeps its width.
- [ ] Validation is submit-first, then re-validate on change; cross-field rules use `superRefine`.
- [ ] On server error, input is preserved and field errors map back with `setError`.
- [ ] Success is announced via `aria-live`, not a toast alone; `reset(values)` rebaselines dirty.
- [ ] Unsaved-changes guard (`beforeunload` + in-app route guard) fires while dirty.
- [ ] One column, top-aligned labels; two controls share a row only when one datum.
- [ ] Inputs are ≥16px on mobile (don't override shadcn's `text-base md:text-sm`).
- [ ] Looks correct in both light and dark with no component edits.

---

_Sources: shadcn/ui — React Hook Form guide & Field component; Vercel Geist (Input, Description) +
Web Interface Guidelines; GitHub Primer "Saving" pattern; NN/G form usability, placeholder, and
error-reporting guidelines; LogRocket & Smashing / Smart Interface Patterns on inline vs.
after-submit validation; Smashing & WeWeb multi-step form guides; Wasp advanced rhf + Zod + shadcn;
UXmatters label placement; Damian Wajer autosave vs. explicit save._
