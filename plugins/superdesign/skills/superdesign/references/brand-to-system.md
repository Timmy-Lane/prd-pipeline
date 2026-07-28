# Archetype Seed Design Systems

Seven complete, ready-to-ship design languages that seed the adaptive engine. Each is a
full token bundle — color primitives, type trio, radius base, shadow character, motion
curves — not a palette. They exist so that **v1 always lands on a strong floor**: when the
brand-derivation pipeline (see SKILL.md → Phase 1) produces an attribute vector, it snaps to
the nearest archetype, then perturbs the primitives; when there is no brand signal at all,
it ships the archetype verbatim rather than the beige mean everyone converges on.

## How the engine uses these

The brand pipeline compresses inputs into ~6 spectrum floats (Serious↔Playful,
Traditional↔Modern, Warm↔Cool, Restrained↔Bold, Economical↔Premium, Calm↔Energetic). Map
that vector to an archetype with the fingerprint table, then re-seed **only the primitive
layer** — the seed hue, the `--radius` base, the type family, the shadow character, the
easing pair. The semantic and component token layers are **identical across all seven
archetypes** (this is what makes swapping cheap: same trick as dark mode — repoint semantic
aliases at different primitives). Every archetype ships light + dark, obeys the 60-30-10
application rule (neutral 60 / secondary 30 / saturated accent 10), and must clear the same
gate: WCAG AA (4.5:1 body / 3:1 large-UI/focus) and APCA (Lc ≥ 75 body, ≥ 60 large),
validated per foreground/background pair, in both modes.

| Archetype | Fingerprint (dominant axes) | Aaker / archetype | Radius base | Motion |
|---|---|---|---|---|
| **SaaS-minimal** | Modern+, Cool+, Restrained+, Calm+ | Competence | 8px | fast, productive, no bounce |
| **Editorial** | Traditional+, Warm+, Premium+, Calm+ | Sophistication / Sincerity | 2px | slow, smooth, fade-forward |
| **Playful** | Playful+, Bold+, Energetic+, Warm+ | Excitement | 16px + pills | springy, expressive, overshoot |
| **Dark-premium** | Premium++, Modern+, Restrained+ | Sophistication | 10px | slow, controlled decelerate |
| **Brutalist** | Bold++, Restrained−−, Energetic+ | Outlaw / Creator | 0px | snappy, mechanical, abrupt |
| **AI-dev-tool** | Modern++, Cool+, Restrained+, Premium+ | Competence / Sage | 4–6px | snappy expo, one idle breath |
| **Warm-paper** | Warm+, Modern+, Premium+, Restrained+ | Sincerity / Competence | 8px | snappy expo, seam-draw + one breath |

All color values are OKLCH `oklch(L C H)` — L 0–1, C 0–~0.37 (sRGB-safe), H 0–360° — the
canonical space for the whole system (perceptually uniform, Tailwind v4 native, Baseline
since 2023). Neutral hue angles reference the corpus: red ≈ 25, amber ≈ 65, yellow ≈ 95,
green ≈ 150, teal ≈ 190, blue ≈ 259, violet ≈ 300, pink ≈ 350.

---

## 1. SaaS-minimal (Linear / Vercel / Raycast lane)

**Personality.** Competence made visible. Precise, calm, engineered, gets out of the way.
Reads as "infrastructure built by people who care about craft." Neutrals carry ~90% of the
surface; one restrained accent lives strictly in the 10% action lane. The whole aesthetic is
*restraint as a signal* — every visible element looks like a decision.

**When to use.** B2B SaaS, dashboards, dev tools, productivity, internal tools, data-dense
product UI. The safe default when the brand vector is weak or the domain is "serious
software." **Avoid** for consumer/lifestyle, kids, or anything that needs warmth or delight.

**Color.** Achromatic base, faintly cool-tinted (slate), so grays never read dead. One
considered blue accent — *not* the reflexive `indigo-500 #6366F1`; commit to a real blue at
moderate (not peak) chroma, or go fully achromatic Vercel-style (white/near-black as the
"accent"). Semantic hues standard.

```css
/* light */                              /* dark (flip the ramp) */
--background:  oklch(0.994 0.002 260);   /* oklch(0.16  0.008 260) */
--foreground:  oklch(0.22  0.010 260);   /* oklch(0.96  0.003 260) */
--muted-fg:    oklch(0.52  0.012 260);   /* oklch(0.68  0.010 260) */
--border:      oklch(0.92  0.006 260);   /* oklch(0.27  0.010 260) */
--primary:     oklch(0.60  0.150 256);   /* oklch(0.68  0.130 256) — desaturated + lighter for dark */
--primary-fg:  oklch(0.99  0.002 260);   /* oklch(0.16  0.010 256) */
--radius: 0.5rem;                        /* 8px */
```
Neutral chroma stays 0.002–0.012 (tinted, not pure C=0). In dark mode drop accent chroma
~0.02 and raise L one step (saturated blue vibrates on dark surfaces).

**Type.** One neo-grotesque, weight-contrast only — the cleanest premium move. **Geist**
(Sans + Mono) or **Inter** (Text ≤20px / Display ≥20px via the `opsz` axis). Body 450,
headings 550–600. Scale ratio **1.2–1.25** (minor→major third; dense UI wants a low ratio).
Apply the Inter dynamic-tracking table (0 at ≤12px → −0.011em at 16px → −0.022em floor at
40px+). `tabular-nums slashed-zero` on every metric and data cell. *Trap:* if you pick
Geist, self-host via npm (`geist/font`) — Google Fonts Geist ships no OpenType features, so
`tnum`/stylistic sets silently fail. *Anti-convergence:* Geist is authentic here but is also
the v0/shadcn convergence font — if the brand needs distance, use Inter or a paid grotesque
(Söhne, Neue Haas Grotesk) rather than the escape-hatch Space Grotesk.

**Radius.** Base **8px** (`--radius: 0.5rem`), derive `xs/sm/md/lg/xl` via the shadcn
multiplier pattern (`*0.5 / *0.75 / *0.875 / *1 / *1.5`). Buttons/inputs 8px, cards 12px,
modals 12–16px, tables/dense grids 0px, avatars/tags full. Reads modern/competent/neutral.

**Shadow character.** Crisp and low — the object sits *just* above the page. Alpha
**decreases** per layer (sharp), and fold a hairline ring into the token (Radix trick) so
border-and-shadow read as one system. In dark mode switch the depth cue entirely: lighten
the surface (M3 dark tone ladder 4→10→12→17→22) + a faint inset top highlight; reserve real
shadow for modals only.

```css
--shadow-sm: 0 0 0 1px oklch(0 0 0 / 0.05), 0 1px 2px oklch(0 0 0 / 0.06);
--shadow-md: 0 0 0 1px oklch(0 0 0 / 0.05), 0 4px 6px -1px oklch(0 0 0 / 0.08),
             0 2px 4px -2px oklch(0 0 0 / 0.06);
/* dark: drop the outer layers, keep the ring + inset highlight */
--shadow-md-dark: inset 0 1px 0 oklch(1 0 0 / 0.06), 0 0 0 1px oklch(1 0 0 / 0.08);
```

**Motion.** Fast and productive; <100ms feels instantaneous on hot paths, hard-cap
interactive UI at 300ms. Single primary curve = strong ease-out `cubic-bezier(0.23, 1, 0.32,
1)` (or IBM Carbon productive `cubic-bezier(0.2, 0, 0.38, 0.9)`). Durations: button press
120ms, dropdown 160ms, modal 220ms. **No bounce.** Keyboard-triggered actions get zero
animation. This archetype pairs naturally with a Cmd+K command backbone.

---

## 2. Editorial

**Personality.** Considered, literary, authoritative, unhurried. Hierarchy comes from
**type and whitespace, not boxes** — big serif display against small quiet body, ruled
dividers instead of cards. Feels like a well-set magazine or a thoughtful essay.

**When to use.** Content sites, long-form/blogs, documentation, publishing, portfolios,
premium brand/marketing pages, anything where reading is the product. **Avoid** for
data-dense dashboards or high-frequency tool UI (the register mismatch — an italic serif
headline on a dev tool — is a named slop tell).

**Color.** Warm paper neutral (sand/stone), never clinical white. Text is warm near-black
(≈ `rgba(0,0,0,0.9)`), not `#000`. Accent is a single *restrained, dusty* ink — oxblood,
forest, or navy at low chroma — used sparingly for links and rules.

```css
/* light */                              /* dark */
--background:  oklch(0.980 0.008 85);    /* oklch(0.19  0.008 70)  — warm near-black */
--foreground:  oklch(0.24  0.012 60);    /* oklch(0.92  0.010 80) */
--muted-fg:    oklch(0.50  0.015 60);    /* oklch(0.66  0.012 75) */
--border:      oklch(0.88  0.010 75);    /* oklch(0.30  0.010 70) */
--primary:     oklch(0.45  0.120 25);    /* oklch(0.62  0.110 25)  — oxblood link/accent */
--radius: 0.125rem;                      /* 2px */
```
Chroma stays 0.08–0.13 on the accent (muted, "dusty"), neutrals 0.008–0.015 warm-tinted.

**Type.** The one archetype that *should* pair two families. High-contrast display serif +
quiet body. Display: **Fraunces**, **Playfair Display**, or **Newsreader** (700, tight
tracking −0.02em on large sizes). Body: a readable serif (**Source Serif 4**, **Crimson
Pro**, **Lora**) or a humanist sans for contrast. Mono captions optional (IBM Plex Mono).
Scale ratio **high, 1.333–1.5** (perfect fourth → fifth — dramatic, headings must dominate;
push size contrast to ~3–5:1). `max-width: 65ch` on every prose wrapper. `oldstyle-nums` in
serif body. Base 18px reads more premium than 16 for long-form.

**Radius.** **0–2px** (`--radius: 0.125rem`, or 0). Sharp corners read serious/editorial;
tables and rules stay 0. Roundness here would undercut the authority.

**Shadow character.** Essentially flat. Depth is **hairline rules and generous whitespace**,
not elevation. A 1px border out-performs a shadow on near-white paper (the shadow just
vanishes). Reserve one soft shadow for overlays/modals only.

```css
--shadow-sm: none;                       /* editorial is flat by default */
--shadow-overlay: 0 8px 40px oklch(0 0 0 / 0.08), 0 0 0 1px oklch(0 0 0 / 0.06);
--rule: 1px solid var(--border);         /* the primary separator */
```

**Motion.** Slow, smooth, restrained — reveals and cross-fades, no snap. Strong ease-in-out
`cubic-bezier(0.77, 0, 0.175, 1)` for on-screen movement; simple `ease-out` for reveals.
Durations **300–500ms** (content reveals ~480ms). No bounce. One well-orchestrated staggered
page-load reveal (30–80ms between items) beats scattered scroll fade-ins.

---

## 3. Playful

**Personality.** Excitement, warmth, energy, delight. High-chroma color, round shapes,
springy motion. Approachable and human without being childish (unless it's for kids, then
lean further). Optimistic and tactile — the UI wants to be touched.

**When to use.** Consumer apps, social, fintech-for-humans, wellness, education, games,
mobile-first products, onboarding-heavy flows. **Avoid** for enterprise/finance/trust-
critical UI and any high-frequency repeated action (bouncy easing gets tiresome and undercuts
credibility fast).

**Color.** Vibrant, high-chroma seed — a warm coral/orange or a candy pair, applied as flat
fills (never rainbow gradients). Even here, obey 60-30-10: the saturated accent stays scarce;
neutrals are warm-tinted and light/airy. M3 `Vibrant`/`Expressive` scheme variant fits.

```css
/* light */                              /* dark */
--background:  oklch(0.99  0.006 60);    /* oklch(0.18  0.010 60) */
--foreground:  oklch(0.25  0.020 40);    /* oklch(0.95  0.008 60) */
--muted-fg:    oklch(0.55  0.030 45);    /* oklch(0.70  0.020 55) */
--border:      oklch(0.90  0.020 55);    /* oklch(0.30  0.015 55) */
--primary:     oklch(0.68  0.190 40);    /* oklch(0.72  0.175 40)  — vivid coral */
--accent-2:    oklch(0.72  0.200 350);   /* optional candy pink second hue */
--radius: 1rem;                          /* 16px */
```
Chroma runs high (0.18–0.24 on accents). In dark mode ease chroma down ~0.02 and raise L so
it doesn't vibrate.

**Type.** Rounded/humanist geometric with a heavy display. **Satoshi**, **Clash Display**,
**Cabinet Grotesk**, or **Bricolage Grotesque**; display weights 700–900, high x-height body
for friendliness. Scale ratio **1.25–1.333** (balanced→confident). Positive tracking on
uppercase labels (+0.04–0.1em). Weight extremes (300 body vs 800 display) beat a timid
400/600 split.

**Radius.** **16–24px** (`--radius: 1rem`, up to 1.4rem for very soft), **full pills for
CTAs and chips**. Rounded shapes are processed faster and read as safe/friendly (the contour
bias). Mind the nesting rule (`inner = outer − padding`, clamp ≥ 0) — generous radii make
concentric-corner errors more visible.

**Shadow character.** Soft, diffuse, floaty — alpha **increases** per layer. Optionally tint
the shadow toward the accent hue (subtle), never a neon glow (the #1 "cyberpunk-by-default"
slop tell). Larger, softer shadows imply higher/lighter objects.

```css
--shadow-md: 0 2px 4px oklch(0.68 0.19 40 / 0.06),
             0 8px 16px oklch(0.68 0.19 40 / 0.10),
             0 16px 32px oklch(0.68 0.19 40 / 0.14);
```

**Motion.** Expressive springs with a little overshoot — this is where delight lives. Spring
`{ visualDuration: 0.4, bounce: 0.25 }` (keep bounce 0.1–0.3) for physical props; IBM Carbon
expressive `cubic-bezier(0.4, 0.14, 0.3, 1)` for tweens. Durations 250–400ms. Spend the
delight budget *inversely to frequency*: confetti/celebration on rare first-time moments,
calm on hot paths.

---

## 4. Dark-premium

**Personality.** Sophisticated, exclusive, focused, expensive. A tinted near-black canvas
with depth built from *lightening surfaces*, one vivid jewel-tone accent, and slow deliberate
motion. Reads as a pro tool or a luxury product — Raycast/Linear-dark energy, not a gamer
theme.

**When to use.** Dev tools, creative/pro apps, crypto/finance-premium, media players,
AI/agent products, anything that wants to feel focused and high-end. Often paired with a
light mode; "dark-first" is a legitimate choice here. **Avoid** as a reflex — permanent dark
mode + all-caps labels + colored glows is itself a named slop cluster; it must be a real
decision, not the default cool look.

**Color.** Never pure `#000` (causes OLED smearing/halation) — a tinted near-black. Depth =
a surface ladder that gets *lighter* with elevation (M3 dark tones), plus hairline rings.
Text is a white-alpha ladder (87% / 60% / 38%), not `#fff`. Single accent, chroma boosted to
stay vivid on dark.

```css
--background:      oklch(0.15  0.012 260);   /* canvas — tinted near-black, not #000 */
--surface:         oklch(0.19  0.012 260);   /* +1 elevation (lighter) */
--surface-high:    oklch(0.23  0.012 260);   /* modals/menus */
--foreground:      oklch(0.97  0.003 260 / 0.90);
--muted-fg:        oklch(0.97  0.003 260 / 0.60);
--border:          oklch(1 0 0 / 0.08);      /* hairline ring, alpha-white */
--primary:         oklch(0.70  0.170 250);   /* electric blue jewel accent */
--primary-fg:      oklch(0.16  0.010 260);
--radius: 0.625rem;                          /* 10px */
```
Swap the accent hue for the brand (violet ≈ 300, teal ≈ 190, gold/amber ≈ 85). Keep chroma
0.15–0.19 — vivid but singular. A matching light mode just flips tones (canvas → ~0.98, text
→ ~0.22).

**Type.** Refined neo-grotesque for UI — **Inter Display**, **Geist**, or a premium grotesque
(**Söhne**, **Neue Haas Grotesk**). For a luxury-editorial dark variant, a Didone display
(Didot/Playfair) over a neutral sans body. Body 400–450 (lighter weights read fine on dark),
headings 550–650. Scale ratio 1.25. Body text uses the white-alpha ladder, never solid white
(halation).

**Radius.** **8–12px** (`--radius: 0.625rem`) — enough to feel crafted, restrained enough to
stay serious. Optional premium upgrade: `corner-shape: squircle` (Chrome) / Figma corner
smoothing ≈ 60% on hero surfaces, degrade to plain radius.

**Shadow character.** Shadows barely read on dark, so **elevation is the lighter surface**,
not the shadow. Use the surface ladder + a faint inset top highlight (the light-catch edge)
as the primary cue; add a real diffuse shadow only on the top 1–2 levels (modals) for extra
separation. No colored glows.

```css
--elev-1: inset 0 1px 0 oklch(1 0 0 / 0.06), 0 0 0 1px oklch(1 0 0 / 0.06);
--elev-modal: inset 0 1px 0 oklch(1 0 0 / 0.06), 0 0 0 1px oklch(1 0 0 / 0.08),
              0 16px 48px oklch(0 0 0 / 0.55);
```

**Motion.** Slow, smooth, controlled — deliberate reads as expensive. Emphasized-decelerate
`cubic-bezier(0.05, 0.7, 0.1, 1)` for enters, durations **300–500ms**. No bounce, ever
(bounce reads cheap here). Spatial navigation can use a critically-damped spring (damping ~1,
no overshoot). Disable transitions during theme swap.

---

## 5. Brutalist (neo-brutalism)

**Personality.** Loud, raw, confident, anti-corporate. Hard edges, thick black borders,
flat saturated color blocks, hard-offset shadows with zero blur, and type as a graphic
element. Zero apology. The aesthetic *is* the statement — it deliberately breaks the smooth-
SaaS consensus.

**When to use.** Portfolios, creative agencies, indie/dev products with attitude, launch/
landing pages, music/culture, developer marketing that wants to stand out. A deliberate
"name the aesthetic family" choice — never the fallback. **Avoid** for trust-critical flows
(banking, healthcare), dense data tools, or accessibility-sensitive contexts unless the
contrast is carefully managed.

**Color.** Stark high-contrast: near-pure white or a flat primary block against pure black
borders/text, plus one or two saturated primaries applied as **flat fills, never gradients**.
Acid yellow, pure red, electric blue, or hot pink.

```css
--background:  oklch(0.99 0 0);           /* stark white (or a flat color block) */
--foreground:  oklch(0.14 0 0);           /* near-pure black */
--border:      oklch(0.14 0 0);           /* black, and THICK */
--primary:     oklch(0.65 0.240 25);      /* pure red — or yellow oklch(0.87 0.19 100) */
--primary-fg:  oklch(0.14 0 0);
--accent-2:    oklch(0.78 0.170 235);     /* electric blue block */
--radius: 0;                              /* hard corners, everywhere */
--border-width: 2px;                      /* 2–3px solid — the signature */
```
Chroma runs high and flat (0.17–0.24). This is the one archetype where near-max contrast and
big color blocks are the point, not a violation.

**Type.** Monospace or heavy grotesque display as a graphic device. **Space Mono**,
**JetBrains Mono**, **Archivo** (heavy), or a condensed heavy display. Weight extremes
(100/200 vs 800/900) and **size jumps of 3×+**. All-caps labels are legitimate here (a
deliberate choice, not a reflex) with positive tracking. High-contrast pairing —
display + monospace — is the brutalist signature.

**Radius.** **0px** (`--radius: 0`). Every corner is hard. Rounding anything breaks the
language.

**Shadow character.** Hard **offset** shadow — solid color, **no blur, no spread falloff**.
The neo-brutalist signature is `4px 4px 0 #000`. Pair with thick 2–3px solid borders. This is
the exact opposite of the layered-penumbra rule and is intentional.

```css
--shadow-sm: 2px 2px 0 var(--foreground);
--shadow-md: 4px 4px 0 var(--foreground);
--shadow-lg: 6px 6px 0 var(--foreground);
/* hover = shift toward the shadow, shrink the offset (the object "presses in") */
```

**Motion.** Snappy, mechanical, or none. Short `linear` / fast `ease-out`, **100–150ms**. No
smoothing softness — motion can be abrupt on purpose. Hover = hard `translate(2px, 2px)` +
shadow offset collapse (the pressed-in effect), instant on `:active`. Never spring/bounce.

---

## 6. AI-dev-tool (code-panel-hero lane)

**Personality.** Precise, technical, credible — "built by engineers who ship." The dominant 2026
look for AI-infra / developer-API products (Supermemory, AgentMail, HydraDB, React Bits, Vercel,
Zed). It proves the product *is* code and *is* trusted, then gets out of the way. A specialization
of SaaS-minimal / Dark-premium with a fixed **pattern language** more than a distinct palette.

**When to use.** Developer tools, APIs, SDKs, AI/agent infra, databases, DX products, technical
docs marketing. **Avoid** for consumer/lifestyle or non-technical audiences (a code panel becomes
noise, not proof).

**Two modes — pick one, never mix on a surface:**
- **Dark** (AgentMail / Vercel / React Bits): tinted near-black + one faint technical texture + one
  saturated accent.
- **Warm-paper light** (Supermemory): cream/paper canvas + electric-blue accent + navy-*tinted*
  (not gray) borders — a rarer, premium-feeling take. Tokens below are from Supermemory's live CSS.
  This mode is §7's design language specialized for dev tools; when the product is *not* a dev
  tool but the vector still says Warm+Modern+Premium, use the standalone **Warm-paper** archetype (§7).

**Color.**
```css
/* DARK */
--background: oklch(0.14 0.004 260);          /* tinted near-black (AgentMail) — never #000 */
--foreground: oklch(0.97 0.003 260 / 0.90);
--border:     oklch(1 0 0 / 0.08);            /* hairline alpha-white */
--primary:    oklch(0.62 0.200 258);          /* ONE saturated accent (blue/violet/orange) */

/* WARM-PAPER LIGHT (Supermemory: #FAF7F2 / #0562EF / #0B1015) */
--background: oklch(0.975 0.006 85);          /* warm cream paper */
--foreground: oklch(0.20 0.015 250);          /* blue-black ink, not #000 */
--muted-foreground: oklch(0.50 0.020 250);
--border:     oklch(0.90 0.012 250);          /* NAVY-tinted hairline, not neutral gray */
--primary:    oklch(0.55 0.220 258);          /* electric blue #0562EF */
--radius: 0.375rem;                           /* 4–6px, small/blocky */
```
Ration the accent to CTA + one highlight (60-30-10); tint neutrals toward the accent hue.

**Type.** Grotesque UI (Space Grotesk / DM Sans / Geist) + **mono for labels and the code panel**
(DM Mono / JetBrains Mono / Geist Mono) — **uppercase wide-tracked mono eyebrows are the genre
signature**. Optional **monospace/pixel display** for systems/DB products (HydraDB) to signal
precision; a serif-italic accent word (21st.dev "*beautiful*") is a legit craft counter-signal.

**Radius.** **4–6px** small/blocky (`--radius: 0.375rem`) — technical, not fully sharp, not soft.

**Shadow / texture.** Flat + hairline; depth from borders. **Exactly ONE faint technical texture** —
dot-grid (Supermemory), vertical rules (HydraDB), or binary/scan (AgentMail); never stack them.
Optional **bracket / crop-mark framing** on a single element (blueprint motif). No neon glows.

**Motion.** Snappy, productive, expo. Signature `cubic-bezier(0.22, 1, 0.36, 1)` @ 120–240ms
(Supermemory's live curve). One idle "breathing" accent (logo/orb) is a tasteful hero
micro-interaction; everything else < 200ms. Frequency gate applies (command menu = no animation).

**Signature patterns (ship these — they define the genre):**
- **Code-panel hero** — a real syntax-highlighted snippet (bonus: language tabs Py/TS/cURL/CLI) as
  the hero visual; doubles as proof + docs. → `cookbook/code-panel-hero.md`.
- **Copyable install-command pill** — a `$ npx <tool> setup` chip with a copy button.
- **Credential badges near the hero** — GitHub stars, YC, funding, mono "used by" logo wall (the
  dev audience's social proof).

---

## 7. Warm-paper

**Personality.** Technical warmth — precise like an engineering blueprint, warm like good
paper. Cream canvas, blue-black ink, one electric accent, mono labels, dashed-grid dividers.
Reads as "careful people built this *for humans*," splitting the difference between
SaaS-minimal's cool restraint and Editorial's literary warmth. Corpus anchor: Supermemory
(by Memetic Design) — the rarest lane of the seven in the wild, which is exactly why it
doesn't read as template.

**When to use.** Human-facing technical products: AI companions and consumer-AI apps,
note-taking / PKM / knowledge tools, education, docs-as-product, productivity, health,
fintech-for-humans — anywhere the vector lands Warm+ Modern+ Premium+ but *not* Playful and
*not* dev-tool-cold. This fills a real hole in the vector space: before it, a
warm-modern-restrained brief had no honest landing spot (Editorial is Traditional+, Playful
is Bold+/Energetic+, AI-dev-tool is Cool+). **Avoid** for dev-infra audiences that expect a
dark terminal (→ §6 dark mode), luxury exclusivity (→ Dark-premium), or loud statement
brands (→ Brutalist / Playful). A dev tool that wants this feel uses §6's warm-paper-light
mode — the same language plus the code-panel pattern kit.

**Color.** Warm cream paper — never clinical white — with blue-black *ink* text (not `#000`)
and ONE saturated electric-blue accent. The signature trick: **borders and shadows are
navy-tinted, never neutral gray** — low-alpha navy hairlines harmonize with the accent
instead of reading dead. Cards sit near-white *on* the cream, so elevation reads as
"brighter paper." All pairs below are WCAG-AA-verified (computed, both modes).

```css
/* light */                                   /* dark ("ink" mode) */
--background:  oklch(0.977 0.006 85);         /* oklch(0.19  0.012 250) — warm blue-black ink */
--card:        oklch(0.995 0.002 85);         /* oklch(0.23  0.012 250) */
--foreground:  oklch(0.21  0.015 250);        /* oklch(0.95  0.006 85)  — paper-tinted white */
--muted-fg:    oklch(0.48  0.020 250);        /* oklch(0.70  0.015 250) */
--border:      oklch(0.30 0.08 258 / 0.12);   /* oklch(0.85 0.04 250 / 0.16) — tinted, not gray */
--primary:     oklch(0.55  0.215 258);        /* oklch(0.68  0.165 258) — electric blue, raised */
--primary-fg:  oklch(0.995 0.002 85);         /* oklch(0.17  0.015 250) — ink on the lighter blue */
--radius: 0.5rem;                             /* 8px */
```

Accent chroma stays high (0.20–0.22 light / 0.16–0.17 dark) but the accent itself is rationed
hard to the 10% action lane; neutrals carry warmth via hue (paper ≈ 85, ink ≈ 250), not chroma.

**Type.** Geometric-quirky display + humanist body + mono labels. The corpus trio is
**Space Grotesk / DM Sans / DM Mono**. On warm paper this is authentic — the named
escape-hatch cliché is Space-Grotesk-*plus-teal-on-near-black*, not the face itself — but if
the brand needs distance, swap the display to **Bricolage Grotesque** or **Cabinet Grotesk**.
Display tracking −0.02…−0.04em; **uppercase mono eyebrow labels at +0.1–0.16em** head every
section. The tight-display / wide-mono-label contrast is the core typographic signature.
Body 16–18px at weight 400–450, scale ratio 1.25.

**Radius.** Base **8px** (`--radius: 0.5rem`) — chips 4px, cards 10–12px, pills full. Blocky
enough to feel drafted, round enough to stay warm. Nothing over-rounded.

**Shadow character.** **Blue-tinted layered shadows**, matching the tinted borders — never
neutral gray on a branded surface. Fold the hairline in via the `0 0 0 1px` trick; the focus
ring is soft blue at ~10–12% alpha over the crisp outline.

```css
--shadow-card:  0 1px 2px oklch(0.25 0.09 258 / 0.16), 0 8px 18px -8px oklch(0.55 0.215 258 / 0.35);
--shadow-modal: 0 32px 64px -24px oklch(0.20 0.015 250 / 0.28), 0 0 0 1px oklch(0.20 0.015 250 / 0.04);
--ring-soft:    0 0 0 4px oklch(0.55 0.215 258 / 0.12);
/* dark: elevation = lighter surface + hairline; keep one real shadow for modals only */
```

**Motion.** Snappy, decisive expo settle — signature `cubic-bezier(0.22, 1, 0.36, 1)` at
**120–240ms**. Two earned exceptions: **seam-draw** (dashed dividers animate
`stroke-dashoffset` → 0 on scroll — the blueprint "drawing itself") and ONE idle
**breathing presence element** (the Orb pattern: breathe when idle, pulse when busy) for
AI products. Everything else settles fast; no bounce.

**Signature patterns (the blueprint kit — pick 2–3, never all):**
- **Dashed grid dividers with plus-mark intersections** — content in bordered blocks, `+`
  glyphs where hairlines cross.
- **Uppercase mono eyebrow** over every section heading.
- **Window-chrome mockup** (traffic-light dots) framing product shots.
- **Frosted nav:** `backdrop-filter: blur(10px) saturate(140%)` — the saturation boost is
  what keeps cream from going gray under the blur.

---

## What stays constant across all seven (the invariant layer)

Only the primitives above change. Everything below is archetype-invariant, so the same
components skin any archetype by swapping one primitive file:

- **3-tier tokens** (primitive → semantic → component). Components consume only the semantic
  layer; a component that references a primitive (`blue-500`) directly is a bug.
- **Foreground/background pairs** for every color role (`x` + `x-foreground`), so contrast is
  auto-checkable and every surface has a legible text color.
- **Semantic hue conventions**: success ≈ green 150, warning ≈ amber 65 (dark on-text — the
  exception), error ≈ red 25, info ≈ blue 259. Each ships bold / bold-hovered / subtle /
  border / text / text-strong sub-slots + a paired `on-color`.
- **Derived scales from one base token**: `--radius` → xs/sm/md/lg/xl; one tracking base → 6
  steps; 6 shadow params → the full scale. Author ~10 knobs, emit ~60 tokens.
- **Dark mode = re-point semantic aliases**, keep names stable; flip the ramp, desaturate
  accents ~0.02–0.05 chroma and raise L, switch elevation to lighter-surface cues.
- **Gates**: WCAG AA + APCA on every pair in both modes; ≤2 type families (3 only if one is
  mono); ≤3 motion curves; `prefers-reduced-motion` reduces (cross-fades) rather than
  deletes; coherence check (a "playful +0.8" vector must not emit radius 0).
- **Anti-convergence guardrails**: no reflexive `indigo/violet/purple-500` accent; no
  purple→cyan mesh as primary decoration; no uniform `rgba(0,0,0,0.1)` shadow on everything;
  no gradient text on metrics; flag the escape-hatch clichés (Space Grotesk + teal on
  near-black, Geist-by-default, single Instrument-Serif-italic accent word) as their own slop.
