# Landscape: the shadcn substrate, where to retrieve from, and the composition rules

Two jobs only: make **retrieval** possible (real URLs a tool can hit), and state the **composition
rules** for building on shadcn/ui without fighting it. Referenced from SKILL Phase 2.

This file used to carry a tooling/registry ecosystem map — star counts, prices, maintenance status,
per-vendor tool tables. That is deleted on purpose. It was time-sensitive (which a skill must not
carry), derivable by the model, and never once load-bearing for a design decision. What remains is the
part that is not derivable: the protocol, the endpoints, and the rules.

## Contents

- [0. The substrate: shadcn is a distribution protocol, not a component library](#0-the-substrate-shadcn-is-a-distribution-protocol-not-a-component-library)
- [1. Machine-readable endpoints](#1-machine-readable-endpoints-verified-by-fetch-2026-07-26) — the real URLs a tool can hit
- [2. The verified negative: nothing upstream gives you visual quality](#2-the-verified-negative-nothing-upstream-gives-you-visual-quality)
- [Composition (shadcn) — the Phase-2 rules](#composition-shadcn--the-phase-2-rules)

---

## 0. The substrate: shadcn is a distribution protocol, not a component library

The one fact that organizes everything else: shadcn/ui is **a code-distribution platform**. You don't
`npm install` components; `npx shadcn@latest add button` copies the real source into your repo and you
own it. Every registry plugs into the same plumbing, which makes them interchangeable and
lock-in-free.

The mechanics a skill must know:

- **Namespaced install:** `npx shadcn@latest add @<namespace>/<component>`. Namespaces are configured in
  `components.json` under a `registries` key and can carry auth headers / query params for private
  registries (`"Authorization": "Bearer ${REGISTRY_TOKEN}"`).
- **Two schemas:** `registry.json` (catalog manifest) + `registry-item.json` (one item: component /
  block / hook / page / style / theme / font / file, with `dependencies`, `registryDependencies`,
  `cssVars`). `shadcn registry:build` compiles them to static JSON served over any HTTP stack.
- **Discovery loop:** `search @ns -q "…"` → `view @ns/name` → `add @ns/name`.
- **Community registries are unaudited.** shadcn's own docs say *"review code on installation"*. Prefer
  named, maintained registries over UGC dumps, and read what you install.

Stack norms this skill targets: **Tailwind v4** (CSS-first, no `tailwind.config.js`) + React/TS +
the `new-york` style + Lucide icons + `sonner` (not the deprecated `toast`) + `tw-animate-css` (which
replaced `tailwindcss-animate`) + OKLCH tokens.

**Skill implication:** treat "which registry" as a *sourcing* decision, default to copy-paste + own the
code, and ship our own design system as a shadcn registry — a `registry:style` item for the full token
set plus `registry:*` items for components — so humans and agents install it with the same one command.

---

## 1. Machine-readable endpoints (verified by fetch, 2026-07-26)

Every shadcn-compatible registry serves items as JSON at a templated path. `components.json` declares
the template: `{"registries": {"@ns": "https://host/r/{name}.json"}}`. **No MCP, npm, or auth needed** —
WebFetch or curl is sufficient.

| URL | Returns |
|---|---|
| `https://tweakcn.com/r/registry.json` | Catalog manifest — 15 preset names |
| `https://tweakcn.com/r/themes/<name>.json` | `registry:style` — full light+dark OKLCH token set, fonts, radius, tracking, shadows |
| `https://magicui.design/r/<name>.json` | `registry:ui` — real component source in `files` |

Probe pattern for an unlisted registry: try `<site>/r/registry.json`, then `<site>/r/<name>.json`.
**Report only endpoints you actually hit.** `https://ui.shadcn.com/llms.txt` does NOT resolve to an
llms.txt index (checked 2026-07-26) — do not build a step on it. The manifest is the reliable
enumeration and the guessable `/r/<name>.json` path is the reliable retrieval; a site can serve more
than it advertises.

**Retrieve before generate.** This is the skill's own doctrine, and this table is the only reason it has
an address. Prefer install-from-a-curated-registry or reference-a-real-screen over blank-prompt
generation — it directly counters distributional convergence. The registry-over-HTTP path needs nothing
installed (no MCP, no npm, no auth, no account), which makes it the *default* grounding mechanism, not
the fallback.

---

## 2. The verified negative: nothing upstream gives you visual quality

**The general coding agents contribute nothing to visual quality.** Cursor's leaked Agent Prompt v1.2
(sections: knowledge cutoff, communication, tool_calling, maximize_context_understanding,
making_code_changes, Tools, functions, multi_tool_use) contains **no design instruction of any kind**.
Windsurf's Wave 11 prompt has no design section. Replit's has none. Bolt's original `prompts.ts` has
none — its entire aesthetic budget is the sentence *"For all designs I ask you to make, have them be
beautiful, not cookie cutter"*, which is an adjective with no dimension attached. **100% of visual
quality on those hosts has to come from the skill.**

(Provenance: every one of those prompts comes from a single unaudited leak archive with no capture
dates. The conclusion is load-bearing; the quotes are uncorroborated.)

---

## Composition (shadcn) — the Phase-2 rules

How to build ON shadcn/ui without fighting it:

- **Compose small parts, don't prop-explode.** Assemble `Card` + `CardHeader` + `CardTitle` +
  `CardContent`; a component with 15 boolean props is a smell — split it.
- **`cn()` = `clsx` + `tailwind-merge`.** Thread `className` **last** so callers can override, and
  never hand-concatenate class strings (the later Tailwind class must win the merge).
- **Variants via `cva`** (`class-variance-authority`) — encode `variant`/`size` as variants, not
  ad-hoc conditionals; expose them as typed props.
- **Polymorphism via `asChild`** (Radix `Slot`) or **`render`** (Base UI) — e.g. a link-button:
  `<Button asChild><Link/></Button>`; don't duplicate styles across element types.
- **`data-slot` on every part** as the stable styling/query hook (shadcn convention); style
  and test against `data-slot` / `data-state`, not brittle class chains.
- **Semantic tokens only in markup** — `bg-primary`, `text-muted-foreground`; never `bg-zinc-900`
  or raw hex, so theming + dark mode keep working.
- **Reskin via tokens, never by forking `components/ui/*`.** Own the code, but change the theme
  (`:root` / `.dark` vars), not the primitive source, so registry updates stay mergeable.
- **Premium comes from tokens, not blocks.** Every shadcn-based block inherits your `--primary`,
  `--radius`, font and spacing. Default-gray + untouched radius + Inter = slop; a distinctive accent +
  tuned radius + a real display face + tinted (not gray) borders = premium.
- **Icons: one family, one stroke width, one corner style — never mix.** Size scale 16 dense / 20
  inline / 24 default (+32/40/48 marketing). Lucide ships with shadcn (`strokeWidth` is a prop;
  `absoluteStrokeWidth` holds the line weight across sizes). Differentiating the set away from the
  Lucide/Feather default is `→ anti-slop.md`.
- **Own the code, don't depend on it.** The ecosystem's whole value is copy-paste + you edit the source.
  Pin the exact source URL; no runtime lock-in.
- **Install from any registry:** `npx shadcn@latest add @<namespace>/<component>` with the namespace
  declared in `components.json`; pin the source URL. Endpoints in §1.
