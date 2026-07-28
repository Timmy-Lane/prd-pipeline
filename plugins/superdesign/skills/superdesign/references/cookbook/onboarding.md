# Cookbook — Onboarding / first-run

Get a new user to first value fast, without a forced tour. The best onboarding is a **great empty
state + a short setup checklist**, revealed progressively — not a modal carousel that blocks the app.

## When to use
- First run of an app/dashboard; a workspace with no data yet; multi-step account setup.

## When NOT to use
- Don't gate the whole product behind a mandatory multi-slide tour (a named slop/annoyance tell).
  Let people into the product; guide from inside it.
- Skip onboarding chrome entirely once the account is set up — the checklist should disappear when done.

## Patterns (pick by need)
1. **Empty-first-run** — the primary screen's empty state carries the onboarding (headline + one CTA +
   optional sample data). Cheapest, highest-signal. See `cookbook/empty-states.md`.
2. **Setup checklist** — a dismissible card of 3–5 concrete tasks with progress; each links into the
   real flow. Best for products needing config before value.
3. **Progressive disclosure** — reveal advanced surfaces only after the basics are done; don't dump
   everything at once.
Avoid tooltip coach-marks stacked over a busy UI (they age badly and block interaction).

## Code — setup checklist card (React + Tailwind v4 + shadcn/ui)
```tsx
import { Check, Circle, ArrowRight, X } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

type Step = { id: string; title: string; desc: string; href: string; done: boolean };

export function SetupChecklist({ steps, onDismiss }: { steps: Step[]; onDismiss?: () => void }) {
  const done = steps.filter((s) => s.done).length;
  const pct = Math.round((done / steps.length) * 100);
  const nextId = steps.find((s) => !s.done)?.id; // the single "current" step
  if (done === steps.length) return null; // vanish when complete — don't linger

  return (
    <Card className="relative">
      {onDismiss && (
        <button
          type="button" aria-label="Dismiss setup"
          onClick={onDismiss}
          className="absolute right-3 top-3 grid size-7 place-items-center rounded-md text-muted-foreground transition-colors hover:bg-muted focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
        >
          <X className="size-4" />
        </button>
      )}
      <CardHeader>
        <CardTitle>Finish setting up</CardTitle>
        <CardDescription>{done} of {steps.length} done — a couple minutes to first value.</CardDescription>
        <Progress value={pct} className="mt-2" aria-label={`Setup ${pct}% complete`} />
      </CardHeader>
      <CardContent className="p-0">
        <ul className="divide-y">
          {steps.map((step) => (
            <li key={step.id}>
              <a
                href={step.href}
                aria-current={step.id === nextId ? "step" : undefined}
                className="group flex items-center gap-3 px-6 py-3.5 transition-colors hover:bg-muted/50 focus-visible:outline focus-visible:-outline-offset-2 focus-visible:outline-2 focus-visible:outline-ring"
              >
                {step.done
                  ? <Check className="size-5 shrink-0 text-success" aria-hidden />
                  : <Circle className="size-5 shrink-0 text-muted-foreground" aria-hidden />}
                <span className="flex-1">
                  <span className={"block text-sm font-medium " + (step.done ? "text-muted-foreground line-through" : "text-foreground")}>
                    {step.title}
                  </span>
                  <span className="block text-sm text-muted-foreground">{step.desc}</span>
                </span>
                {!step.done && (
                  <ArrowRight className="size-4 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" aria-hidden />
                )}
              </a>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
```

## States
- **Step:** todo (`Circle`, foreground title) · done (`Check` in `text-success`, muted + line-through) ·
  hover (row `bg-muted/50` + arrow fades in) · focus-visible (inset ring). Optional "locked" step:
  reduced opacity + `aria-disabled`, unlocks when its prerequisite completes.
- **Card:** hides itself at 100% complete; dismiss is available but progress persists server-side.

## Accessibility
- Real `<a>`/`<button>` per step; `aria-current` on the active/next step; icons `aria-hidden`.
- `Progress` carries an `aria-label` with the percentage; completion is announced via a live region if
  it happens in place.
- Never signal done with color only — the check icon + strike-through carry it too.

## Anti-slop
- No forced full-screen tour; no confetti on routine steps (reserve delight for the true first "aha").
- Concrete, product-specific task copy ("Connect your first repo"), not vague ("Get started",
  "Explore features").
- The checklist must be genuinely dismissible and must disappear when finished — lingering onboarding
  chrome reads as unfinished product.
