# Cookbook — Code-panel hero (dev-tool / API products)

The signature hero of the **AI-dev-tool** archetype (Supermemory, AgentMail, React Bits, Vercel,
Stripe docs). The hero visual is a *real, syntax-highlighted code snippet* — it doubles as proof
("the product is code") and as instant docs. Pairs with a copyable install-command pill and
credential badges.

## When to use
- Developer tools, APIs, SDKs, AI/agent infra, databases, DX products, technical docs marketing.
- The primary conversion is "a developer tries the snippet."

## When NOT to use
- Consumer/lifestyle/non-technical audiences — a code panel reads as noise, not proof. Use a
  product screenshot (`cookbook/hero.md`) or illustration instead.
- Don't stack a code panel AND a product screenshot AND an illustration — one hero visual.

## Anatomy
```
[eyebrow: mono, uppercase, wide-tracked]      ┌───────────────────────────┐
Big grotesque H1 (2 lines max)                │ ● ● ●   window chrome      │
Muted subhead (≤ 2 lines)                     │ [Python][TS][cURL][CLI] ⧉ │  ← language tabs + copy
[ $ npx tool setup            ⧉ ]  ← install  │  from tool import Client  │
[ Primary CTA ] [ ghost CTA ]                 │  client = Client()        │  ← syntax-highlighted
                                              └───────────────────────────┘
[ ⭐ 42k · YC · used-by mono logo wall ]  ← credential badges
```
Left = copy (system tokens), right = code panel. One faint technical texture behind (dot-grid /
vertical rules / binary) — never more than one.

## Code (React + Tailwind v4 + shadcn/ui)
Uses `Tabs`, `Button` from shadcn. Swap the `highlight()` stub for Shiki/`rehype-pretty-code` at
build time (never ship a client-side highlighter on the hot path).

```tsx
"use client";
import { useState } from "react";
import { Copy, Check, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

const SNIPPETS = {
  python: `from tool import Client\n\nclient = Client()\ninbox = client.inboxes.create(\n    name="billing",\n)`,
  ts: `import { Client } from "tool";\n\nconst client = new Client();\nconst inbox = await client.inboxes.create({ name: "billing" });`,
} as const;

function CopyButton({ text, label = "Copy", className = "" }: { text: string; label?: string; className?: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      type="button"
      aria-label={copied ? "Copied" : label}
      onClick={() => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 1500); }}
      className={"grid size-8 place-items-center rounded-md text-muted-foreground transition-colors hover:bg-muted focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring " + className}
    >
      {copied ? <Check className="size-4 text-success" /> : <Copy className="size-4" />}
    </button>
  );
}

export function CodePanelHero() {
  return (
    <section className="relative mx-auto grid max-w-6xl gap-12 px-6 py-24 lg:grid-cols-2 lg:items-center">
      {/* one faint technical texture — dot grid */}
      <div aria-hidden className="pointer-events-none absolute inset-0 -z-10
        [background-image:radial-gradient(var(--color-border)_1px,transparent_1px)] [background-size:22px_22px] opacity-40" />

      {/* left: copy */}
      <div className="flex flex-col items-start gap-6">
        <span className="font-mono text-xs uppercase tracking-[0.06em] text-muted-foreground">
          Context cloud for agents
        </span>
        <h1 className="text-balance text-5xl font-semibold tracking-[-0.022em] text-foreground">
          Email inboxes for AI agents
        </h1>
        <p className="max-w-md text-lg text-muted-foreground">
          Give every agent its own inbox — like Gmail does for humans. Low latency, any model.
        </p>

        {/* copyable install pill */}
        <div className="flex w-full max-w-md items-center justify-between gap-2 rounded-md border bg-card px-3 py-2 font-mono text-sm">
          <span><span className="text-muted-foreground select-none">$ </span>npx tool setup</span>
          <CopyButton text="npx tool setup" label="Copy install command" />
        </div>

        <div className="flex flex-wrap gap-3">
          <Button size="lg">Start for free <ArrowRight className="size-4" /></Button>
          <Button size="lg" variant="ghost">Docs</Button>
        </div>

        {/* credential badges */}
        <div className="flex items-center gap-4 pt-2 text-sm text-muted-foreground">
          <span className="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 font-mono text-xs">★ 42.5k</span>
          <span className="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs">Backed by Y Combinator</span>
        </div>
      </div>

      {/* right: code panel with language tabs */}
      <Tabs defaultValue="python" className="overflow-hidden rounded-xl border bg-card shadow-lg">
        <div className="flex items-center gap-2 border-b bg-muted/40 px-4 py-2.5">
          <span className="flex gap-1.5" aria-hidden>
            <span className="size-3 rounded-full bg-destructive/70" />
            <span className="size-3 rounded-full bg-warning/70" />
            <span className="size-3 rounded-full bg-success/70" />
          </span>
          <TabsList className="ml-2 bg-transparent p-0">
            <TabsTrigger value="python" className="font-mono text-xs">Python</TabsTrigger>
            <TabsTrigger value="ts" className="font-mono text-xs">TypeScript</TabsTrigger>
          </TabsList>
        </div>
        {(["python", "ts"] as const).map((lang) => (
          <TabsContent key={lang} value={lang} className="relative m-0">
            <CopyButton text={SNIPPETS[lang]} className="absolute right-3 top-3 z-10" />
            {/* replace with build-time Shiki output; this is the shape */}
            <pre className="overflow-x-auto p-5 font-mono text-sm leading-relaxed text-foreground">
              <code>{SNIPPETS[lang]}</code>
            </pre>
          </TabsContent>
        ))}
      </Tabs>
    </section>
  );
}
```

## States
- **Install pill / copy buttons:** rest → hover (`bg-muted`) → focus-visible ring → copied (check +
  `text-success`, revert after ~1.5s). Announce the copied state (`aria-label` flips).
- **Tabs:** active tab uses the third axis (underline/indicator), not the hover fill; full keyboard
  support comes from the shadcn/Radix `Tabs` primitive.

## Accessibility
- The `<pre><code>` is real selectable text (screen-reader friendly) — never an image of code.
- Copy buttons have `aria-label`; the copied state is conveyed in text, not color alone.
- Traffic-light dots are `aria-hidden` decoration.
- Keep body/subhead ≥ 4.5:1; on dark, prefer APCA Lc ≥ 75.

## Anti-slop
- **One** background texture (dot-grid *or* rules *or* binary), low opacity — never stacked, never a
  neon glow.
- Mono only for the eyebrow, code, and badges — not for body copy.
- Real, runnable code (correct API shape), never lorem or a fake snippet.
- Credential badges must be true (real star count / real backer) — fake social proof is a named slop tell.
- Highlight at build time (Shiki / `rehype-pretty-code`); don't ship a client highlighter on the hero.
