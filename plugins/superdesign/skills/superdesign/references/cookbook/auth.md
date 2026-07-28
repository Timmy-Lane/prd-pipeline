# Auth Screens (Sign In / Sign Up)

> Category: `auth` · Stack: React + Tailwind v4 + shadcn/ui
> The one card the user meets before they trust you. Make it feel inevitable.

---

## When to use it

Reach for this recipe whenever a user must **prove who they are** before entering the
product: sign in, sign up, magic-link / OTP, SSO, password reset. It is the highest-stakes
low-content screen you will ship — one card, one primary action, zero distractions.

Use it when:

- You need a **dedicated route** (`/login`, `/signup`, `/reset`) rather than a modal. Full
  pages win for anything a user might deep-link, bookmark, or land on from an email.
- You want a design that reads as **premium and trustworthy** on first contact — the
  Linear / Vercel / Stripe register: high contrast, generous air, one accent, geometric type.
- You're wrapping a hosted auth provider (Clerk, Auth0, Supabase, WorkOS, NextAuth) and want
  your own front-end instead of their default widget.

Reach for something else when:

- The auth is a **one-off gate inside a flow** (e.g. "confirm your password to delete") —
  that's a dialog, not a page.
- You need **enterprise SSO discovery** at scale — use the email-first variant below, but be
  aware of the enumeration caveat (see Anti-slop).

---

## Anatomy

The canonical sign-in card, top → bottom. Every part is optional except heading + fields +
primary CTA, but this is the order that scans.

```
┌─────────────────────────────────────────┐
│                                          │
│            [▣]  Acme Inc.                 │  ← 1. Brand mark (logo chip + wordmark)
│                                          │
│   ┌───────────────────────────────────┐  │
│   │        Welcome back               │  │  ← 2. Heading (text-2xl/xl font-bold)
│   │   Login with Google or email      │  │     + subheading (text-sm muted)
│   │                                   │  │
│   │  [  Continue with Google      ]   │  │  ← 3. Social / SSO (outline, full-width, ≤3)
│   │                                   │  │
│   │  ──────  Or continue with  ────── │  │  ← 4. Divider (hairline + centered label)
│   │                                   │  │
│   │  Email                            │  │  ← 5. Fields (single column, label above input)
│   │  [ you@example.com            ]   │  │
│   │                                   │  │
│   │  Password        Forgot? →        │  │     Password label row: link pinned ml-auto
│   │  [ ••••••••••              👁 ]   │  │     eye toggle inside the field
│   │                                   │  │
│   │  [        Login              ]    │  │  ← 6. Primary CTA (full-width, value-bearing)
│   │                                   │  │
│   │  ☐ Remember me                    │  │  ← 7. Secondary row (remember / ToS microcopy)
│   └───────────────────────────────────┘  │
│                                          │
│   Don't have an account?  Sign up         │  ← 8. Mode switch (a link, not a button)
│                                          │
│   By continuing you agree to Terms…       │  ← 9. Legal / trust microcopy (text-xs muted)
│                                          │
└─────────────────────────────────────────┘
```

**Layout structure (the shell):**

- **Page shell** — `flex min-h-svh flex-col items-center justify-center p-6 md:p-10`.
  Use `min-h-svh`, never `min-h-screen` (avoids the mobile viewport jump when the URL bar
  hides). Optional `bg-muted` for the "floating card" look.
- **Stack** — `w-full max-w-sm flex flex-col gap-6`. Everything (logo, card, footer) lives
  in this one narrow column so it's optically centered as a unit.
- **Card** — the shadcn `Card` provides elevation and the border/radius. The form is a
  `grid gap-6` inside `CardContent`; each field group is a `grid gap-2` (label → input).

Sign-up adds an inline **password-requirements checklist** (unmet → met) and a short
**email-verification expectation** line ("We'll send a link to confirm your email"). It
drops "Remember me" and swaps the legal microcopy to the ToS acceptance line.

---

## Token-driven styling

Everything is driven by shadcn's CSS variables so light/dark and rebrands are free. **Never
hardcode hex in an auth screen** — it's the one place a mismatched near-black screams "unfinished".

| Surface | Token / class | Notes |
|---|---|---|
| Page background | `bg-background` or `bg-muted` | `bg-muted` for the floating-card look |
| Card surface | `bg-card text-card-foreground` | shadcn `Card` sets this |
| Headings / body | `text-foreground` | default; don't set it explicitly unless overriding |
| Subhead / legal / hints | `text-muted-foreground` | the entire "quiet" layer |
| Primary CTA | `bg-primary text-primary-foreground` | shadcn `Button` default |
| Logo chip | `bg-primary text-primary-foreground` | `size-8 rounded-md` icon tile |
| Borders / dividers | `border` / `border-t` (→ `--border`) | hairline rules, input outline |
| Focus ring | `ring-ring/50` via `focus-visible:` | shadcn `Input`/`Button` build this in |
| Error state | `text-destructive`, `aria-invalid:ring-destructive/20` | shadcn `Input` styles `aria-invalid` for you |
| Split aside | `bg-muted` | plus `dark:brightness-[0.2] dark:grayscale` on the image |

The corresponding variables (already defined by a shadcn install; shown so the recipe is
self-contained). Tailwind v4 wires them in the `@theme inline` block of `globals.css`:

```css
/* app/globals.css — provided by `npx shadcn init`, trimmed to the tokens this recipe uses */
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
  --ring: oklch(0.556 0 0);
  --destructive: oklch(0.704 0.191 22.216);
}
```

Because the whole screen is monochrome tokens + one `--primary` accent, flipping to dark
mode, theming per-tenant, or shipping a whole new brand is a variables-only change. Zero
component edits.

---

## Variants

### Variant A — Centered card (default)

The workhorse. `flex min-h-svh items-center justify-center p-6 md:p-10`, inner
`w-full max-w-sm`. Optionally on `bg-muted` so the card floats. This is the full code example
below. Maps to shadcn `login-01` / `login-03`. **Use this unless you have a reason not to.**

### Variant B — Split screen with cover

A two-column grid: the form on the left, a full-bleed brand panel on the right that carries a
product screenshot, gradient, or a single customer testimonial (the Vercel/Clerk move). The
aside is `hidden lg:block`, so on tablet/mobile it collapses to the centered card
automatically — **zero extra responsive work**. Maps to shadcn `login-02`.

```tsx
// Swap only the outer shell; <LoginForm /> is unchanged from the example below.
export function SplitAuthPage() {
  return (
    <div className="grid min-h-svh lg:grid-cols-2">
      <div className="flex flex-col gap-4 p-6 md:p-10">
        <div className="flex justify-center gap-2 md:justify-start">
          <a href="/" className="flex items-center gap-2 font-medium">
            <span className="bg-primary text-primary-foreground flex size-6 items-center justify-center rounded-md">
              <GalleryVerticalEnd className="size-4" />
            </span>
            Acme Inc.
          </a>
        </div>
        <div className="flex flex-1 items-center justify-center">
          <div className="w-full max-w-xs">
            <LoginForm />
          </div>
        </div>
      </div>
      <div className="bg-muted relative hidden lg:block">
        <img
          src="/cover.jpg"
          alt=""
          className="absolute inset-0 h-full w-full object-cover dark:brightness-[0.2] dark:grayscale"
        />
      </div>
    </div>
  )
}
```

### Variant C — Email-first, multi-step (Vercel / Linear / Clerk feel)

Step 1 is email + "Continue". On submit, the **same card morphs** to the right second factor
(password, OTP, or a passkey prompt) with the email echoed as an editable chip so the user
can correct a typo without losing their place. Sketch:

```tsx
const [step, setStep] = useState<"email" | "password">("email")
const [email, setEmail] = useState("")
// step === "email"  → single Input + "Continue"
// step === "password" → email shown as a chip with an "Edit" button + password field + "Login"
```

Keep the CTA value-bearing on the final step ("Log in", not "Continue"). See the Anti-slop
note on SSO discovery before you branch the second step on account existence.

---

## State matrix

Every interactive element ships with **all** of these states, not just the happy path.

| Element | States |
|---|---|
| **Text input** | empty · focus (ring) · filled · valid (✓ on blur) · invalid (`aria-invalid` + destructive ring + inline message) · disabled |
| **Password field** | above + show/hide toggle · (sign-up) requirement checklist unmet → met |
| **Primary button** | default · hover · focus-visible · **loading (spinner, `disabled`, width preserved)** · disabled (form empty/invalid) · brief success (✓) before redirect |
| **Social button** | default · hover · loading (per provider — only that button spins) |
| **Form level** | idle → submitting → error banner (`role="alert"`, ARIA live) → success |
| **Magic-link / OTP** | sent confirmation ("Check your inbox · Resend") · countdown before resend · expired → single regenerate CTA |
| **Field error** | inline under the field, icon + text, **input value preserved** |

Two rules that separate shipped-quality from demo-quality:

1. **On error, never clear what the user typed.** Keep the email across password retries.
   Keep the password visible if the eye toggle was on so they can spot the typo.
2. **The submit button keeps its width while loading.** Spinner replaces the label; the
   layout never jumps.

---

## Responsive behavior

- **Page:** `min-h-svh` + `p-6 md:p-10`. The `svh` unit tracks the *small* viewport so the
  card never gets shoved under a mobile URL bar.
- **Card width:** `max-w-sm` (~384px) centered; `max-w-xs` for the form column inside a split;
  `max-w-4xl` for a wide form-plus-image card. The card is `w-full` up to those caps, so on a
  narrow phone it's edge-to-edge minus the `p-6` gutter.
- **Split aside** is `hidden lg:block` — it simply disappears below `lg`, degrading to the
  centered card with no media-query bookkeeping.
- **Touch targets:** shadcn's default control height (`h-9`, and `size-*` icon buttons)
  clears the 44px comfortable-tap zone with the surrounding padding. Don't shrink inputs on
  mobile.
- **Keyboards:** `type="email"` and `inputMode` surface the right on-screen keyboard;
  `autoComplete` lets iOS/Android and password managers fill in one tap.

---

## Accessibility

- **Real `<label htmlFor>` for every field.** Never placeholder-as-label — it fails SR users
  and vanishes the moment they type. Placeholders are optional *examples* only.
- **`autoComplete` is an a11y feature,** not just convenience: `username`, `email`,
  `current-password`, `new-password` (sign-up), `one-time-code` (OTP).
- **Errors are announced.** Field errors use `aria-invalid` + `aria-describedby` pointing at
  the message node. The form-level error banner is `role="alert"` (assertive live region) so
  it's read immediately.
- **Focus management:** autofocus the first empty field on load. On submit failure, move
  focus to the error summary or the first invalid field.
- **Show/hide toggle** is a real `<button type="button">` with `aria-label` ("Show password"
  / "Hide password") and `aria-pressed`; toggling `type` between `password`/`text` keeps the
  value.
- **Focus-visible rings** come from the tokens (`ring-ring`). Never `outline-none` without a
  replacement — keyboard users must always see focus.
- **Contrast:** the monochrome token scale is designed to pass AA; keep body text on
  `foreground`/`muted-foreground`, don't tint it lighter for "elegance".
- **Don't disable paste** on password fields — it breaks password managers and assistive
  tech. If you use a CAPTCHA, provide the audio alternative.

---

## Anti-slop callout

> The tells that mark an auth screen as AI-generated or junior — and what to do instead.

- ❌ **Hardcoded `#000`/`#fff` (or a random near-black).** → Use `bg-background` / `bg-card` /
  `text-foreground`. One off-token color and the dark mode looks broken.
- ❌ **Placeholder instead of a `<label>`.** → Real labels above inputs; placeholders are
  optional examples.
- ❌ **"Confirm password" field.** → A show/hide eye toggle. Confirm fields are friction that
  password managers already solved.
- ❌ **Clearing the form (or the email) after an error.** → Preserve every value; keep the
  email across password retries.
- ❌ **Vague errors — "Login failed."** → Be specific and offer the next step ("That password
  doesn't match. Reset it?"). But keep credential errors *uniform* to avoid enumeration.
- ❌ **Generic "Continue" as the final CTA.** → Value-bearing verbs: "Log in", "Create
  account". "Continue" is fine only on an intermediate step.
- ❌ **>3 social buttons stacked.** → Show the top 2–3, collapse the rest behind "More options".
- ❌ **No loading state — the UI freezes on a slow network.** → Spinner in the button, keep
  its width, disable it, and disable the form.
- ❌ **`min-h-screen`.** → `min-h-svh`, or the card jumps when the mobile browser chrome moves.
- ❌ **"Sign in" vs "Sign up" one-glance ambiguity.** → Prefer "Log in" vs "Create account".
- ❌ **Mandatory 2FA every session.** → Offer "remember this device".
- ❌ **SSO/email discovery that reveals whether an account exists.** → Uniform responses, or
  gate discovery — leaking org membership is an enumeration vuln.
- ❌ **Cramming, gradients, and three accent colors "to look modern".** → One card, huge
  whitespace, one accent. Auth should feel *inevitable*, not decorated.

---

## Complete example

Drop-in `LoginForm` + page. Uses shadcn primitives (`Button`, `Card`, `Input`, `Label`,
`Checkbox`) and `lucide-react` icons. Everything is token-driven and fully accessible. Wire
`onSubmit` to your auth provider (Clerk/Auth0/Supabase/NextAuth) where marked.

Prereqs:

```bash
npx shadcn@latest add button card input label checkbox
npm i lucide-react
```

```tsx
// components/login-form.tsx
"use client"

import * as React from "react"
import { Eye, EyeOff, GalleryVerticalEnd, Loader2 } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

type FieldErrors = { email?: string; password?: string }

function GoogleIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="currentColor"
        d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z"
      />
    </svg>
  )
}

export function LoginForm({ className, ...props }: React.ComponentProps<"div">) {
  const [showPassword, setShowPassword] = React.useState(false)
  const [status, setStatus] = React.useState<"idle" | "loading" | "google">("idle")
  const [formError, setFormError] = React.useState<string | null>(null)
  const [errors, setErrors] = React.useState<FieldErrors>({})

  const isSubmitting = status !== "idle"

  function validate(email: string, password: string): FieldErrors {
    const next: FieldErrors = {}
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      next.email = "Enter a valid email address."
    }
    if (password.length < 8) {
      next.password = "Password must be at least 8 characters."
    }
    return next
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)

    // FormData preserves the user's input — we never read+clear the fields.
    const data = new FormData(event.currentTarget)
    const email = String(data.get("email") ?? "")
    const password = String(data.get("password") ?? "")

    const nextErrors = validate(email, password)
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) return

    setStatus("loading")
    try {
      // ── Wire your auth provider here ──────────────────────────────
      // await signIn("credentials", { email, password, redirectTo: "/app" })
      await new Promise((r) => setTimeout(r, 1200))
      throw new Error("demo") // remove — placeholder so the demo shows the error path
    } catch {
      // Uniform, non-enumerating message. The typed values stay intact.
      setFormError("That email or password is incorrect. Try again.")
    } finally {
      setStatus("idle")
    }
  }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card>
        <CardHeader className="text-center">
          <CardTitle className="text-xl">Welcome back</CardTitle>
          <CardDescription>Log in with Google or your email</CardDescription>
        </CardHeader>

        <CardContent>
          <form onSubmit={onSubmit} noValidate className="grid gap-6">
            {/* Form-level error — assertive live region */}
            {formError && (
              <p
                role="alert"
                className="border-destructive/50 bg-destructive/10 text-destructive rounded-md border px-3 py-2 text-sm"
              >
                {formError}
              </p>
            )}

            {/* Social / SSO — only this button spins on its own load */}
            <Button
              type="button"
              variant="outline"
              className="w-full"
              disabled={isSubmitting}
              onClick={() => setStatus("google")}
            >
              {status === "google" ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <GoogleIcon className="size-4" />
              )}
              Continue with Google
            </Button>

            {/* Theme-aware divider: one hairline + a centered label */}
            <div className="after:border-border relative text-center text-sm after:absolute after:inset-0 after:top-1/2 after:z-0 after:flex after:items-center after:border-t">
              <span className="bg-card text-muted-foreground relative z-10 px-2">
                Or continue with
              </span>
            </div>

            {/* Email */}
            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                name="email"
                type="email"
                autoComplete="username"
                placeholder="you@example.com"
                autoFocus
                required
                disabled={isSubmitting}
                aria-invalid={!!errors.email}
                aria-describedby={errors.email ? "email-error" : undefined}
              />
              {errors.email && (
                <p id="email-error" className="text-destructive text-sm">
                  {errors.email}
                </p>
              )}
            </div>

            {/* Password — forgot link on the label row, eye toggle in the field */}
            <div className="grid gap-2">
              <div className="flex items-center">
                <Label htmlFor="password">Password</Label>
                <a
                  href="/reset"
                  className="ml-auto text-sm underline-offset-4 hover:underline"
                >
                  Forgot your password?
                </a>
              </div>
              <div className="relative">
                <Input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  required
                  disabled={isSubmitting}
                  className="pr-10"
                  aria-invalid={!!errors.password}
                  aria-describedby={errors.password ? "password-error" : undefined}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  aria-pressed={showPassword}
                  disabled={isSubmitting}
                  className="text-muted-foreground hover:text-foreground focus-visible:ring-ring absolute inset-y-0 right-0 flex items-center px-3 focus-visible:ring-2 focus-visible:outline-none disabled:opacity-50"
                >
                  {showPassword ? (
                    <EyeOff className="size-4" />
                  ) : (
                    <Eye className="size-4" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p id="password-error" className="text-destructive text-sm">
                  {errors.password}
                </p>
              )}
            </div>

            {/* Remember me */}
            <div className="flex items-center gap-2">
              <Checkbox id="remember" name="remember" disabled={isSubmitting} />
              <Label htmlFor="remember" className="text-sm font-normal">
                Remember this device
              </Label>
            </div>

            {/* Primary CTA — spinner replaces label, width preserved */}
            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {status === "loading" ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Logging in…
                </>
              ) : (
                "Log in"
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Mode switch — a link, not a button */}
      <p className="text-muted-foreground text-center text-sm">
        Don&apos;t have an account?{" "}
        <a href="/signup" className="text-foreground underline underline-offset-4">
          Create account
        </a>
      </p>

      {/* Legal / trust microcopy — lives outside the card */}
      <p className="text-muted-foreground [&_a]:hover:text-foreground text-center text-xs text-balance [&_a]:underline [&_a]:underline-offset-4">
        By continuing you agree to our <a href="/terms">Terms of Service</a> and{" "}
        <a href="/privacy">Privacy Policy</a>.
      </p>
    </div>
  )
}
```

```tsx
// app/login/page.tsx
import { GalleryVerticalEnd } from "lucide-react"
import { LoginForm } from "@/components/login-form"

export default function LoginPage() {
  return (
    <div className="bg-muted flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10">
      <div className="flex w-full max-w-sm flex-col gap-6">
        {/* Brand mark */}
        <a href="/" className="flex items-center gap-2 self-center font-medium">
          <span className="bg-primary text-primary-foreground flex size-8 items-center justify-center rounded-md">
            <GalleryVerticalEnd className="size-5" />
          </span>
          Acme Inc.
        </a>
        <LoginForm />
      </div>
    </div>
  )
}
```

### Turning it into Sign Up

Same component, four edits — no new layout:

1. Title → "Create your account"; description → "Get started for free".
2. `autoComplete="current-password"` → `"new-password"`; add an inline **requirements
   checklist** (length, number, symbol) that flips unmet → met as they type.
3. Primary CTA → **"Create account"**.
4. Drop "Remember me"; the legal line becomes the ToS acceptance ("By creating an account…");
   mode switch → "Already have an account? **Log in**". Show/hide toggle replaces a confirm
   field entirely.

---

## Quick checklist before you ship

- [ ] All colors are tokens (`grep` the file for `#` — should find nothing).
- [ ] Every input has a real `<label htmlFor>` and an `autoComplete`.
- [ ] Submit shows a spinner, keeps its width, and disables the form.
- [ ] Errors don't clear the user's input; the email survives a password retry.
- [ ] Field errors use `aria-invalid` + `aria-describedby`; the banner is `role="alert"`.
- [ ] Password has a show/hide toggle (labeled), and paste is **not** blocked.
- [ ] `min-h-svh`, not `min-h-screen`.
- [ ] CTA verbs are value-bearing ("Log in" / "Create account", never bare "Continue").
- [ ] Looks correct in both light and dark with no component edits.

---

_Sources: shadcn/ui login blocks & authentication example; blocks.so / shadcndesign
pro-blocks; Authgear & LearnUI login/signup UX guides; the Stripe/Linear/Vercel design-
principles writeups; Clerk enterprise SSO flows; SSO email-discovery enumeration advisory._
