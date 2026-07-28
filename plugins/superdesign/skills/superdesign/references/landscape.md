# Landscape: The 2026 shadcn + Tailwind UI Tooling Ecosystem

A curated map of the tools worth reaching for when generating a brand-adaptive design system in
React + Tailwind v4 + shadcn/ui. Everything here is verified maintained as of **2026-07** unless a
staleness flag says otherwise. Each entry says **what it's best at**, **when to reach for it**, and an
honest **hype-vs-substance** read. Values (stars, prices, versions) are point-in-time — treat them as
signal, not gospel, and re-verify volatile ones before hardcoding.

---

## 0. The substrate: shadcn is a distribution protocol, not a component library

The one fact that organizes everything below: in 2025 shadcn/ui (`shadcn-ui/ui`, ~118k stars) stopped
being "a component set" and became **a code-distribution platform**. You don't `npm install` components;
`npx shadcn@latest add button` copies the real source into your repo and you own it. Every registry
below plugs into the same plumbing, which makes them interchangeable and lock-in-free.

The mechanics a skill must know (CLI 3.0, shipped Aug 2025):
- **Namespaced install:** `npx shadcn@latest add @<namespace>/<component>` (e.g. `@aceternity/hero`,
  `@coss/button`). Namespaces are configured in `components.json` under a `registries` key and can carry
  auth headers / query params for private registries (`"Authorization": "Bearer ${REGISTRY_TOKEN}"`).
- **Two schemas:** `registry.json` (catalog manifest) + `registry-item.json` (one item: component / block
  / hook / page / **theme** / **font** / file, with `dependencies`, `registryDependencies`, `cssVars`).
  `shadcn registry:build` compiles them to static JSON served over any HTTP stack.
- **Discovery loop:** `search @ns -q "…"` → `view @ns/name` → `add @ns/name`.
- **Official MCP:** `npx shadcn@latest mcp init --client claude` — lets an agent browse/search/install
  from any configured registry conversationally.
- **Official directory:** https://ui.shadcn.com/docs/directory (curated, zero-config). shadcn's own
  warning applies to all community registries: *"review code on installation"* — they are unaudited.

**Skill implication:** treat "which registry" as a *sourcing* decision, default to copy-paste + own the
code, and ship our own design system as a shadcn registry (`registry:theme` for tokens + `registry:*`
for components) so both humans and agents install it with the same one command.

Verified 2026 stack norm across the whole ecosystem: **Tailwind v4 (CSS-first, no `tailwind.config.js`)
+ React 19/TS + `new-york` style (the only style now; `default` deprecated) + Lucide icons + `sonner`
(not the deprecated `toast`) + `tw-animate-css` (replaced `tailwindcss-animate`) + OKLCH tokens**. The
init base-color enum was updated for v4 to `neutral, stone, zinc, mauve, olive, mist, taupe` (the old
`gray`/`slate` are gone).

---

## 1. shadcn core + first-party surfaces

| Surface | What it is | Reach for it when |
|---|---|---|
| **shadcn/ui core** | ~50 Radix-based (Base UI opt-in) accessible primitives, copy-paste | Always — the accessible structural layer for real product UI (forms, dialogs, menus, focus mgmt) |
| **shadcn/ui blocks** (`ui.shadcn.com/blocks`) | Free registry blocks: Sidebar, Dashboard, Login, Signup, Calendar | App-shell scaffolding; "Open in v0" round-trips them into AI editing |
| **shadcn/ui charts** (`ui.shadcn.com/charts`) | Official Recharts-based charts (area/bar/line/pie/radar/radial), MIT | Default charting — themed via `--chart-1..5` tokens, no third-party chart kit needed |

**Substance: high.** This is the default target for AI codegen and the taste floor for "looks designed,
not templated." Its five principles (Open Code, Composition, Distribution, Beautiful Defaults, AI-Ready)
and its token contract (semantic `X`/`X-foreground` pairs, one `--radius` → derived scale, `@theme
inline` bridge) are the thing to build *on*, not around.

---

## 2. Component & block registries (the scorecard)

Everything here installs via the shadcn CLI and lands as owned source that inherits your theme tokens.
Two clean taste registers to keep separate: **maximalist marketing motion** (Aceternity, Cult shaders,
React Bits) vs **restrained app craft** (Origin UI/COSS, Skiper, Magic UI). Don't mix registers on one
surface.

### Primary references (study + steal patterns)

**Aceternity UI** — https://ui.aceternity.com · `@aceternity`
- Best at: high-impact **marketing/landing** motion — heroes (21+), bento, 3D card effects, aurora/lamp/
  beam/spotlight backgrounds, shaders. "$50k landing page" look.
- Reach for it: one splashy hero effect. **Not** for dashboards/forms/a11y-critical UI.
- Signal: ~28k stars, ~200 components, mainstream. Free MIT-ish core + Pro one-time (~$200–300,
  promo-dependent). Stack: Tailwind + Motion; some components pull Three.js (heavy, keep off app bundle).
- Hype-vs-substance: **substance, but bundle/perf/a11y risk** — animation-heavy; gate behind
  `prefers-reduced-motion`, lazy-load 3D.

**Magic UI** — https://magicui.design (`magicuidesign/magicui`, ~21.4k stars, by Dillion Verma)
- Best at: **tasteful small effects** — animated beams, shimmer/rainbow buttons, number tickers,
  marquees, bento. Explicitly "the companion for shadcn/ui." Works light + dark.
- Reach for it: adding restrained flair to an otherwise calm app. 150+ components, free MIT + Pro (~$199).
- Hype-vs-substance: **substance.** Best-in-class small, composable, tasteful effects.

**React Bits** — https://reactbits.dev (`DavidHDev/react-bits`, ~42k stars, #2 JS Rising Stars 2025)
- Best at: **statement/creative-coding surfaces** — hero text reveals, WebGL/shader backgrounds,
  cursor/micro-interaction effects. Deepest creative-background catalog.
- Architectural differentiator: **does NOT mandate Motion** — most effects are CSS-only; GSAP/Three.js/
  Matter.js are optional peer deps only where needed. Best for bundle-conscious / RSC-heavy builds. Ships
  a shadcn registry (`@react-bits/<Component>-TS-TW` — use the `TS-TW` variant for shadcn stacks).
- Reach for it: 1–2 effects on marketing/landing only. **Not Radix, not a11y-first** — keep out of forms,
  menus, dialogs, and interactive controls. Does not auto-guard reduced motion — wire the fallback yourself.
- License gotcha: **MIT + Commons Clause** — free to ship in apps/client work, but you **cannot resell**
  its source repackaged as a component kit.
- Hype-vs-substance: fast-growing and genuinely useful, but ~30% production-grade / 70% demo-reel
  spectacle — **curate hard**.

**Skiper UI** — https://skiper-ui.com · `@skiper-ui`
- Best at: **craft-level micro-interaction detail** — Dynamic Island, image reveal/cursor-trail,
  Vercel-style tooltips, sign-in flows. Explicitly in the Rauno Freiberg / Emil Kowalski *Devouring
  Details* lineage.
- Reach for it: the taste bar for detail-obsessed interactions. 105+ components. Premium $129 / Exclusive
  $549 (adds Figma + templates), one-time. Stack: Next + Tailwind + Motion.
- Hype-vs-substance: **substance for taste**, niche but tastemaker-respected.

### Situational

**KokonutUI** — https://kokonutui.com (`kokonut-labs/kokonutui`, ~1.9k stars) · `@kokonutui`
- Best at: **AI-app UI** — action search bars, AI chat/prompt/composer UI, notification systems,
  flip/glass cards. Motion built-in. Backed by Vercel's OSS program; every component opens in v0.
- Reach for it: chat/prompt surfaces and fresh interactions. 100+ free + Pro. Lower stars but strong v0
  distribution.

**Cult UI** — https://cult-ui.com (`nolly-studio/cult-ui`, ~5.6k stars)
- Best at: animated marketing components **plus a distinctive AI-SDK agent-pattern library** (shader
  heroes, collab toolbars, device mockups, research/analysis/chart-gen artifacts).
- Reach for it: when the product *is* an AI app, or for nice shaders. 78+ free MIT + Pro + templates.

**21st.dev** — https://21st.dev (community marketplace, "npm for design engineers")
- Best at: **discovery/inspiration** across community-published shadcn components (heroes, pricing
  sections, shaders, testimonials). Human-curated ("Crafted React components, not AI slop"; founder
  personally reviews submissions). Installs by direct URL `https://21st.dev/r/<author>/<name>` or
  namespace `@21st`.
- Hype-vs-substance flag: **the company pivoted** (YC W2026) to the **21st Agents SDK** as its revenue
  product; the OSS marketplace repo (`serafimcloud/21st`) has been **frozen since 2025-05-28** and Magic
  MCP is security-only maintenance (see §5). The *hosted marketplace still runs and is worth browsing*;
  the durable, low-risk dependency is the shadcn-registry URL, not their MCP. Quality varies (it's UGC).

### Paid block/template shops (breadth, not to build the skill on)

- **shadcnblocks** (shadcnblocks.com) — the **breadth leader**: ~1,721 blocks, ~1,684 components, 17
  templates, 49 pre-built pages, Figma Kit V2 (484 block designs). Per-category counts are the best map
  of "what sections a marketing page needs" (Hero + Feature carry the most variety). Pro $149 / Premium
  $299 / Elite $399, one-time. Ships shadcn CLI + MCP + IDE extensions.
- **Tailark** (tailark.com) — cohesive **bespoke marketing** aesthetic; 200+ blocks, 4 distinct visual
  styles, 43+ pages. Pick it when you want one opinionated look over a grab-bag. Free / $249 / $299 / $499.
- **Tailwind Plus** (was Tailwind UI, by the Tailwind team) — the **taste benchmark**: 500+ expertly
  crafted examples on Tailwind v4, React/Vue/HTML, plus full Next templates. €129/category or €249 all +
  Catalyst kit, one-time. License gotcha: no reselling/derivative kits/feeding a site builder.

### Reference-only (know they exist)

| Registry | Best at | Signal |
|---|---|---|
| **awesome-shadcn-ui** (github.com/birobirobiro) | The master discovery index (~20k stars) | Use as the root |
| **shadcn.io** | "AI-native" mega-marketplace, 6,000+ blocks | Community, NOT official; huge but uneven |
| **ReUI** (reui.io) | Largest *free* set (~1,000+ components) | ~2.9k stars, MIT + Pro |
| **MynaUI** (mynaui.com) | Tailwind+shadcn kit with tight Figma parity, 12k+ icons | Designer/dev alignment |
| **Preline / Flowbite / HyperUI / daisyUI** | Largest *free* block/component counts, Tailwind v4 | Functional but read "template-y" without heavy theming |

---

## 3. COSS / Cal.com (the Origin UI successor — track this)

**coss.com/ui** (`cosscom/coss`, ~10.2k stars, MIT for `apps/ui`) — the **official Cal.com design system**,
built on **Base UI** (not Radix) + Tailwind v4, copy-paste-and-own. This is where **Origin UI went**:
Origin UI (the deepest free collection of application form primitives — ~700 blocks: inputs 59, selects
51, etc.) was acquired into COSS and now ships as a legacy snapshot at **coss.com/origin** (MIT, limited
support). Active development moved to COSS.

Why it matters for a design skill:
- **Signature vocabulary — Primitives → Particles → Atoms**: unstyled a11y primitives (54) → composed
  blocks ("492 particles": auth forms, tables, date pickers) → data-connected features (atoms are still
  roadmap — only primitives + particles ship today).
- **The "premium feel" recipe** is concrete and stealable: `::before` 1px-inset nested-highlight borders,
  top-lit tinted solid buttons (`inset-shadow` highlight + tinted `shadow-primary/24`), **alpha-based
  neutrals** (`--alpha(black/4–10%)` instead of hardcoded grays), directional light in dark mode (lifted
  near-black, never `#000`), status = 8% tint fills, `data-slot` on every part.
- **Built for AI:** ships an **Agent Skill** (`pnpm dlx skills add cosscom/coss`) with progressive
  loading (root `SKILL.md` + on-demand per-component guides) and an `llms.txt`. This is the blueprint for
  how *our* skill should be authored.
- Install: `pnpm dlx shadcn@latest init @coss/style` (full theme + Inter + Geist Mono) or `add @coss/ui`.

Reach for it: when you want a more opinionated, production-tested layer than raw shadcn, or as the
reference for Base-UI-based a11y and the "crisp/premium" CSS moves. **Substance, but early/active dev** —
cite the patterns, watch the maturity.

---

## 4. Theming / token generators

**tweakcn** — https://tweakcn.com (`jnsahaj/tweakcn`, ~10k stars, Vercel OSS, free) — the **canonical
visual theme editor + token generator for shadcn/ui**. Solves "every shadcn site looks the same." This is
the single most important reference for our adaptive-token generator because its architecture *is* the
pattern:
- **~47 tokens per mode** (full light + dark copies): 19 color tokens (all as `x`/`x-foreground` pairs +
  border/input/ring), 5 chart, 8 sidebar, 3 fonts + letter-spacing, radius/spacing, and **6 shadow
  primitives**.
- **Author few knobs, derive full scales via `calc()`:** one `--radius` → sm/md/lg/xl (−4/−2/0/+4px); one
  `--tracking-normal` → 6 tracking steps; 6 shadow params → an 8-step shadow scale with fixed opacity
  multipliers. Expose ~10 knobs, emit ~60 tokens deterministically.
- **OKLCH canonical** (convert to hsl/rgb/hex only at export), with a **live WCAG contrast checker** on
  every fg/bg pair, and v3/v4 + OKLCH/HSL export toggles.
- **AI generation** (`/ai`): image OR text prompt → full production OKLCH theme (all tokens, both modes),
  gated behind account credits; the editor/presets/export are fully free.
- **~40 presets**, each a *complete design language* (font trio + radius + shadow params + full light/dark
  colors), including reverse-engineered brand themes (Vercel, Supabase, Twitter, T3, Claude).
- **Round-trips** to shadcn-CLI registry JSON (`cssVars.light/.dark`), so anything generated is
  one-command installable. Companion: BankkRoll's tweakcn-theme-picker (43+ installable themes).

Reach for it: any time the deliverable is "a theme." **Substance — highest-signal single tool in this
whole list for our purpose.**

---

## 5. AI UI-generation tools + design MCP servers

### The mental model (the actual product insight)

The enemy is **distributional convergence** ("AI slop"): un-constrained, every tool emits the mean of its
training data — Inter, purple/indigo gradient on white, three `rounded-2xl shadow-lg p-6` cards, shadows
at 0.1 opacity, centered hero + single CTA, "Empower/Unlock/Transform" copy. Anthropic's own cookbook
says it verbatim: Claude *"defaults to safe choices… converge[s] toward generic, 'on distribution'
outputs."* The fix is **process, not adjectives**: split the three fused jobs — (1) taste direction, (2)
visual exploration, (3) implementation spec — and constrain with a token file, not with "make it cleaner."

### Generation tools

| Tool | Stack | Best at | Honest read |
|---|---|---|---|
| **Claude Artifacts + Anthropic frontend-design skill** | any | Best-documented anti-slop *framework* (purpose→audience→direction→code); explicit banlists + positive directives | **Substance.** The reference for the process our skill encodes |
| **Vercel v0** | Locked: Next+React+TS+Tailwind+shadcn+Radix+Lucide+Motion | Only tool with **image/Figma→code**; UI-specialized fine-tune; a11y (WCAG 2.1 AA) as default | **Substance** for greenfield + visual references; opinionated stack |
| **Lovable** | React+Vite+Tailwind+shadcn | Best *default* aesthetic; aggressively design-token-first system prompt ("USE SEMANTIC TOKENS… never direct colors") | **Substance**; slower but less refactoring than Bolt |
| **Bolt.new** | shadcn+Tailwind | Fastest prototype | Weaker default design, messier code — "coding agent that emits UI" |
| **superdesign.dev** | outputs React/Tailwind/CSS | **Design agent, not coding agent**: breadth-before-depth (10+ variants), cheap-wireframe→expensive-render ladder, fork-the-winner, `DESIGN.md` config | **Substance thesis**, but the **original IDE extension is unmaintained** — dev shifted to the web app |

### Design MCP servers (for an agent building UI)

| MCP | What it enables | When to use | Read |
|---|---|---|---|
| **shadcn registry MCP** (official, `shadcn mcp`) | Install real, versioned, dep-resolved components from any configured registry by natural language | **Default.** Codebase already on shadcn; want consistent real components (not hallucinated JSX) | **Highest-signal, free.** Cheapest-first: `get_project_registries`→`search_items`→`get_item`→`add_item` |
| **Figma Dev Mode MCP** (official, beta) | Design-to-code from source of truth: `get_code`, `get_variable_defs` (tokens), `get_code_connect_map` (map Figma→real components — biggest accuracy lever), screenshots | A real Figma design exists | **Substance.** Free during beta; write-to-canvas will become paid. Order: metadata→screenshot→code→variables→code-connect |
| **21st Magic MCP** (`@21st-dev/magic`) | `/ui` generates React/TS components from NL from the 21st corpus; `logo_search` via SVGL | Greenfield ideation, "give me 3 variants," logos | **Flag: maintenance-mode/beta.** 5.3k stars, no published releases, last feature commit ~2025-12-23; last commit (2026-02) was a security-only patch. Vendor attention moved to the Agents SDK. Free tier 100 credits/mo; Pro $20/400, Max $100/2000. Don't over-couple |
| **v0 MCP** (community) | `v0_generate_ui` / `v0_generate_from_image` / `v0_chat_complete` | v0-style generation via API in-editor | Community wrapper |
| **Refero MCP** | Query 135k+ real shipped screens + 10k flows as agent reference | Grounding generation in real-world UI | Useful for retrieval-before-generation |
| **context7 MCP** | Up-to-date library docs (React/Tailwind/Next/shadcn) | Pair with any of the above so generated code uses current APIs | Present in this env |

Also relevant here: Vercel exposes first-party tools in this environment
(`mcp__plugin_vercel_vercel__import-claude-design-from-url`, `deploy_to_vercel`) for design-import +
deploy loops.

**Config cheat-sheet:** shadcn/21st use `"mcpServers"`; VS Code uses `"servers"` (+ `"type":"http"` for
remote); Figma local endpoint `http://127.0.0.1:3845/mcp`, remote `https://mcp.figma.com/mcp`; Claude Code
adds HTTP servers via `claude mcp add --transport http <name> <url>`, inspect with `/mcp`.

---

## 6. Icon sets

Rule #0 that matters more than the library: **one family, one stroke width, one corner style — never
mix.** Ship an 8-based size scale (16 dense / 20 inline / 24 default, +32/40/48 marketing).

| Library | Icons | Style | Grid / stroke | License | Best at |
|---|---|---|---|---|---|
| **Lucide** | ~1,500+ | Single outline (Feather fork) | 24×24, **2px**, `strokeWidth` is a prop | ISC | **Default.** shadcn/ui built-in, ~5M weekly npm. Use `absoluteStrokeWidth` to hold line weight across sizes |
| **Heroicons** | ~292/style | 24 outline/solid, 20 mini, 16 micro | design-per-size (1.5px outline) | MIT | Tailwind Labs; when you want outline+solid state pairs and size-native variants |
| **Phosphor** | 1,248 ×6 weights (~9k) | thin→fill→duotone | 256 viewBox @16px | MIT | Breadth + weight-as-token (regular UI, fill = selected); expressive/marketing |
| **Radix Icons** | ~300 | Single | 15×15 | MIT | Tiny/tight Radix UI at 15px — but small + effectively frozen; most teams use Lucide now |
| **SVGL** (API) | brand logos | — | — | — | Company logos as SVG/React (what 21st Magic's `logo_search` wraps) |

Reach for it: **Lucide by default** (20–24px, strokeWidth 1.5–2). Heroicons if you need outline/solid
state pairs. Phosphor for breadth/weight range. Draw missing glyphs to the family's spec rather than
borrowing from another set. Color budget: 1 color = icon (`currentColor`), 2 = brand exception, 3+ = it's
an illustration.

---

## 7. Fonts

| Font | License | Best at | Watch out |
|---|---|---|---|
| **Inter** (Rasmus Andersson) | OFL | The "safe premium" UI default; two optical sizes (Text ≤20px / Display ≥20px); excels 12–14px | The AI-slop default — pair with weight contrast or a display face to avoid generic look |
| **Geist** (Vercel) | OFL | Developer-brand aesthetic (Linear/Raycast lane); Sans + Mono + Pixel | **Trap:** Google Fonts Geist ships **no** OpenType features — stylistic sets / `tnum` silently fail. Use the `geist/font` npm package or self-host |
| **General Sans / Satoshi / Hanken Grotesk** | free | Characterful grotesques when Inter feels overused | Fontshare / Google Fonts |
| **Söhne / Neue Haas Grotesk / Helvetica Now** | paid | Stripe-tier "expensive" polish | licensing cost |
| **JetBrains Mono / Geist Mono / Berkeley Mono / Commit Mono** | mixed | Code + tabular data | keep one mono in every system |
| **Playfair Display / Fraunces / Source Serif 4** | OFL | Editorial/marketing contrast against a sans | reserve serif for marketing/long-form |

Delivery options: **Google Fonts** (easiest, but no OpenType features for some faces — see Geist), **npm
packages** (`geist/font`), **`next/font`** (self-hosts + eliminates layout shift), or self-hosted
`@font-face`. Prefer **variable fonts** (one file spans the weight range; enables "in-between" weights
like 450 body / 550 headings). Rules to encode: max 2 families (3 if one is mono); contrast via
role/weight not two similar sans; `font-variant-numeric: tabular-nums` on every metric.

**Anti-slop banlist (from Anthropic's cookbook):** never default to Inter, Roboto, Arial, Open Sans, Lato,
or system fonts — **and not Space Grotesk** (the model's alt-default). Recommended by vibe: code →
JetBrains Mono, Fira Code; editorial → Playfair, Crimson Pro, Fraunces; startup → Clash Display,
Satoshi, Cabinet Grotesk; technical → IBM Plex, Source Sans 3; distinctive → Bricolage Grotesque,
Newsreader.

---

## 8. Motion libraries

**Motion** (motion.dev) — the library formerly called **Framer Motion**; the package renamed from
`framer-motion` to **`motion`**. The default React animation engine across the whole ecosystem
(Aceternity, Magic UI, KokonutUI, Skiper, Tailark all ship it). ~35KB gz shared cost (~4.6KB with
`LazyMotion`). Provides layout animations (FLIP via transform-only), `AnimatePresence` (exit animations),
springs (physical props) + tweens (visual props), and the modern `visualDuration + bounce` spring API.

- **Reach for it:** interactive/gesture-driven React motion, shared-element (`layoutId`), exit animations.
- **Substance**, but *use deliberately* — most UI needs no library at all.

**CSS-native primitives (prefer these when they suffice — no bundle cost):**
- **View Transitions API** — native state/route cross-fades + shared-element morphs; default 250ms; does
  NOT auto-respect reduced motion (guard it). The modern replacement for a lot of JS animation.
- **`@starting-style`** — JS-free enter animations (replaces the `useEffect(setMounted)` dance); pairs
  with `transition-behavior: allow-discrete`.
- **`tw-animate-css`** — the Tailwind v4 animation utility layer that replaced `tailwindcss-animate`
  (shadcn/COSS ship it).

**Purpose-built micro-libraries** (Emil Kowalski / Devouring Details lineage — genuinely worth depending
on): **Vaul** (iOS-quality drawer/sheet, curve `cubic-bezier(0.32,0.72,0,1)`), **Sonner** (the toast that
deprecated shadcn's own `toast`; stacking + swipe physics). Effect *catalogs* (React Bits, Magic UI,
Aceternity) covered in §2 — reserve for marketing surfaces, one statement per viewport, always behind
`prefers-reduced-motion`.

Motion defaults to encode: two-curve vocabulary (`--ease-out-quint: cubic-bezier(0.23,1,0.32,1)` for
entrances, `--ease-ios: cubic-bezier(0.32,0.72,0,1)` for micro-interactions), duration ladder
100/150/200/300ms (hard-cap interactive at 300ms), never `ease-in` for UI, `scale` floor 0.95, animate
only `transform`+`opacity`.

---

## 9. Inspiration galleries

Two camps — **aim from (a), ground in (b)**:

**(a) Curated "best-of" (aesthetic ceiling, motion, art direction):**
| Gallery | Best for | Cost |
|---|---|---|
| **Godly → recent.design** | Cutting-edge marketing/portfolio, WebGL, motion (quality over quantity) | Free |
| **Awwwards** | Award-tier experimental; its rubric (Design 40 / Usability 30 / Creativity 20 / Content 10) is a portable quality checklist | Free browse |
| **Land-book** | Landing pages + portfolios, filter by color/type/style/industry/platform | Free + PRO |
| **Lapa Ninja** | Landing pages browsable by page element (hero/pricing/footer), 7,300+ | Free |

**(b) Real-product reference DBs (ship correct, familiar UX):**
| Gallery | Best for | Cost |
|---|---|---|
| **Mobbin** | Largest real production app screens + full flows (500k+ screens), copy to Figma | Freemium ~$10–15/mo |
| **Refero** | 135k+ shipped web+iOS screens, search by font/color/plain-language, **has an MCP** for agents | Freemium |
| **SaaS Interface** | SaaS UI by page type (28 page + 6 component categories) — a great scaffold taxonomy | Freemium |
| **Page Flows / ScreensDesign** | Video of real user *journeys* (timing/transitions); ScreensDesign attaches revenue/install data to iOS onboarding/paywall screens | ~$99/yr / ~$15/mo |

Rule of thumb: **Mobbin + Refero** for product/SaaS UX research, **Awwwards + Godly** for visual ambition,
**Land-book + Lapa Ninja** for landing pages, **Page Flows + ScreensDesign** for flows/conversion moments.

---

## 10. Taste authorities (the lineage to cite, not tools to install)

The named practitioners whose rules are concrete enough to encode — worth referencing so the skill
isn't inventing taste:
- **Rauno Freiberg** — Web Interface Guidelines (interfaces.rauno.me) + Devouring Details. The single best
  interaction checklist in the space; copy near-verbatim.
- **Emil Kowalski** — animations.dev + his public skill file. The motion authority (curves, durations,
  when-not-to-animate, `| Before | After | Why |` review format). Author of Vaul/Sonner-adjacent craft.
- **Refactoring UI** (Steve Schoger / Adam Wathan) — the foundational "make it look designed" rules
  (spacing, color, hierarchy, depth).
- **Anthropic frontend-design skill / cookbook** — the explicit anti-slop framework + banlists (§5).
- **awesome-claude-design** (rohitg00) — 9 named aesthetic families each with a real-brand exemplar +
  palette + typefaces (Editorial Minimalism→Linear, Warm Editorial→Claude, Terminal-Core→Ollama, etc.)
  and two-brand "remix" recipes. The best "pick one bold direction" menu.

---

## 11. Decision matrix + honest calls

| Job to be done | First choice | Backup |
|---|---|---|
| Accessible product primitives | **shadcn/ui core (Radix)** | COSS/Origin (Base UI) |
| Generate/adapt a brand theme | **tweakcn** (visual/AI) | hand-author tokens |
| Marketing hero "wow" | **Aceternity** | Magic UI, React Bits |
| Tasteful small effects on an app | **Magic UI** | KokonutUI |
| Craft-level micro-interaction detail | **Skiper UI** | study Rauno/Emil |
| Statement/WebGL backgrounds, bundle-conscious | **React Bits** | Aceternity |
| Application form/table density | **COSS Particles / Origin legacy** | shadcn core, MynaUI |
| AI-app UI (chat, prompt, agent artifacts) | **KokonutUI / Cult UI** | 21st.dev |
| Bulk marketing/dashboard blocks (paid) | **shadcnblocks** | Tailark, Tailwind Plus |
| Charts | **shadcn/ui charts (official)** | — |
| Icons | **Lucide** | Heroicons, Phosphor |
| React motion engine | **Motion** | CSS View Transitions / `@starting-style` |
| Install components via agent | **shadcn registry MCP** | Figma MCP (if design exists) |
| Discovery / inspiration | **Mobbin + Refero + awesome-shadcn-ui** | 21st.dev, Godly, Awwwards |

**Hype to discount:** community mega-marketplaces (shadcn.io's 6,000 blocks, 21st.dev UGC) — breadth
without a curation guarantee; 21st Magic MCP as a *dependency* (maintenance-mode, vendor pivoted);
"AI-native" branding generally. **Substance to trust:** shadcn core + registry protocol, tweakcn's token
architecture, official shadcn/Figma MCPs, Lucide, Motion + CSS-native primitives, COSS's premium-CSS
recipes, and the Rauno/Emil/Refactoring-UI/Anthropic rule sets.

---

## 12. Cross-cutting caveats (encode as rules)

1. **Own the code, don't depend on it.** The ecosystem's whole value is copy-paste + you edit the source.
   Pin the exact source URL; no runtime lock-in.
2. **Motion is universal but budgeted.** Gate heavy motion behind `prefers-reduced-motion`; keep
   Three.js/shaders out of the app-shell bundle; one statement effect per viewport.
3. **Brand volatility is real — date every claim.** Origin UI → COSS/Cal.com (Base UI); "Framer Motion" →
   "Motion"; 21st.dev → Agents SDK pivot; base-color enum changed for v4. Re-verify before hardcoding.
4. **Community registries are unaudited** — shadcn's own docs say review code on install. Prefer named,
   maintained registries over UGC dumps.
5. **Premium comes from tokens, not blocks.** Every shadcn-based block inherits your `--primary`,
   `--radius`, font, and spacing. Default-gray + `0.625rem` radius + Inter = slop; a distinctive accent +
   tuned radius + a real display font + tinted (not gray) borders = premium.
6. **Retrieve before generate.** Prefer install-from-curated-registry (shadcn MCP) or reference-a-real-
   screen (Refero MCP) over blank-prompt generation — it directly counters AI slop.

---

## Composition (shadcn) — the Phase-2 rules

How to build ON shadcn/ui without fighting it (referenced from SKILL Phase 2):

- **Compose small parts, don't prop-explode.** Assemble `Card` + `CardHeader` + `CardTitle` +
  `CardContent`; a component with 15 boolean props is a smell — split it.
- **`cn()` = `clsx` + `tailwind-merge`.** Thread `className` **last** so callers can override, and
  never hand-concatenate class strings (the later Tailwind class must win the merge).
- **Variants via `cva`** (`class-variance-authority`) — encode `variant`/`size` as variants, not
  ad-hoc conditionals; expose them as typed props.
- **Polymorphism via `asChild`** (Radix `Slot`) or **`render`** (Base UI) — e.g. a link-button:
  `<Button asChild><Link/></Button>`; don't duplicate styles across element types.
- **`data-slot` on every part** as the stable styling/query hook (shadcn/coss convention); style
  and test against `data-slot` / `data-state`, not brittle class chains.
- **Semantic tokens only in markup** — `bg-primary`, `text-muted-foreground`; never `bg-zinc-900`
  or raw hex, so theming + dark mode keep working.
- **Reskin via tokens, never by forking `components/ui/*`.** Own the code, but change the theme
  (`:root` / `.dark` vars), not the primitive source, so registry updates stay mergeable.
- **Install from any registry:** `npx shadcn@latest add @<namespace>/<component>` (CLI 3.0 +
  `components.json` `registries`); pin the source URL. See the registry map above.
