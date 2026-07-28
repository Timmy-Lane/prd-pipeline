# Anti-Slop Gate

The final quality gate. Run this **before declaring any screen done**. It catches the defects that make AI-generated UI read as cheap, generic, and machine-authored — the "AI slop" aesthetic.

## Why slop happens (the one paragraph)

An LLM predicts the highest-probability next token. Given an open design brief, that is the *most common* answer in the training corpus — "the median of every Tailwind tutorial scraped from GitHub between 2019 and 2024." So the model collapses to the statistical center: Inter, indigo, centered hero, three feature cards. Anthropic's own cookbook names it: *"You tend to converge toward generic, 'on distribution' outputs… this creates what users call the 'AI slop' aesthetic."* Convergence is a **default, not a destiny** — this gate exists to override it. Note the second-order trap: telling the model "not Inter, not purple" makes it converge on a *new* cliché (Space Grotesk + teal; now Geist + Instrument-Serif italic). Escaping the center requires committed, specific choices, not the next-safest default.

## How to run the gate

1. **Grep the high-precision tells** (§ Automatable detectors) — these are near-zero-false-positive and cost nothing.
2. **Walk the named-defect catalog** (§ Catalog) against the rendered screen, one category at a time.
3. **Apply the density rule:** any single screen showing **4+ tells** from the Starter Pack fails outright, even if each tell is individually defensible.
4. **Run the handoff gates** (§ Gates) — token coverage, shadow recipes, contrast, state coverage. A failing gate keeps the screen in **draft** status; it is not shippable.
5. **Score it** (optional): borrow shitfa.st's ShitScore banding — 40–60 = noticeably generic, 65–80 = heavy AI residue, 85+ = full slop. Ship under 40.

### The Starter Pack (the density trip-wire)

Multiple independent sources converge on nearly this exact list. 4+ on one screen = flag:

- Inter / Roboto font (no personality)
- Purple / indigo accent or purple→blue gradient
- Centered hero: one headline + one CTA
- Exactly three icon-topped feature cards under the hero
- White or light-gray background, rounded corners on everything
- Subtle shadow at exactly `0.1` opacity, applied uniformly
- "Get Started" / "Build the future of work" copy
- No empty / loading / error / focus states

---

## Automatable detectors (grep first, cheap and precise)

| Signal | Detector | Verdict |
|---|---|---|
| Indigo default | grep `indigo\|violet\|purple\|#6366f1\|#8b5cf6\|#a855f7` | direct — 1 hit = investigate |
| Uniform flat shadow | grep `rgba(0,0,0,0.1)` **count per file** | co-occurrence — flag when it's the *only* shadow recipe (see D-Shadow) |
| Emoji headings | regex leading emoji in `<h1-6>` / list items | direct — strong "an LLM wrote this" tell |
| Colored left border | grep `border-l-[0-9]\|border-left:` on cards | direct — "almost as reliable a sign of AI design as em-dashes" |
| Default font | grep `Inter\|Roboto\|Open Sans\|Lato\|Arial\|-apple-system` in font stack | direct |
| Escape-hatch font | grep `Space Grotesk\|Geist\|Instrument Serif` | investigate — 2026 convergence points, not fixes |
| Gradient text | grep `background-clip:\s*text\|bg-clip-text` on stat numbers | direct |
| Centered density | count centered blocks; **>60% of blocks `text-center`/`mx-auto`** | co-occurrence |
| Slop copy | regex `Get Started`, `Build the future`, `all-in-one`, `Unlock the power`, `For Modern Teams`, `In Today's Fast-Paced World`, `Stop \w+\. Start \w+` | direct |

Model each catalog defect as a rule with a **mode** (`direct` = 1 match flags; `co-occurrence` = count per file, flag above a threshold) so density slop only trips when tells cluster.

---

## Catalog — named defects (detect → why it's cheap → fix)

### COLOR

**`purple-everything`** (indigo/violet default)
- *Detect:* accent resolves to `indigo-500 #6366F1`, `violet-500 #8B5CF6`, or `purple-500 #A855F7`. Also watch for **"VibeCode Purple"** — a lavender shade that leaks from image-generation models, distinct from Tailwind's `#6366f1`.
- *Why cheap:* Tailwind's default hero button was `bg-indigo-500`; its creator publicly apologized for "every AI generated UI on earth also being indigo." It is the single loudest "a model chose this, not a designer" signal.
- *Fix:* Commit to **one dominant color + one sharp accent**, drawn from IDE themes or a real cultural/brand reference, stored as semantic tokens. Purple is allowed *only* as a deliberate brand decision, never as a default.

**`gradient-overuse`** (gradient dependency syndrome)
- *Detect:* gradient is the primary decoration — hero background, CTA fill, and section accents are all gradients; `linear-gradient` with purple+blue/cyan stops; purple-cyan mesh; floating 3D blobs.
- *Why cheap:* the purple→blue mesh gradient is the canonical vibe-coded backdrop; it substitutes atmosphere for a real color system.
- *Fix:* Replace decorative gradients with a semantic color system. For depth, layer *subtle* gradients or geometric patterns tuned to the aesthetic — keep the hues **analogous** (adjacent on the wheel) and interpolate `in oklch` so they don't mud out, not the default rainbow. Reference: Stripe uses deep navy + precise accents, not a mesh.

**`gradient-text-metrics`**
- *Detect:* `background-clip: text` gradient on big stat numbers ("10x", "99.9%").
- *Why cheap:* a top surface-level "tell"; gradient numbers signal decoration over substance.
- *Fix:* Solid color, strong weight, real units + a source.

**`timid-palette`** (evenly-distributed pastels)
- *Detect:* 5 pastel colors each used ~equally; no clear dominant hue.
- *Why cheap:* "Dominant colors with sharp accents outperform timid, evenly-distributed palettes" (Anthropic cookbook). Even distribution reads as indecision.
- *Fix:* ~**60/30/10** distribution — dominant surface, secondary, one sharp accent. Reserve color for emphasis; a mostly-neutral UI with color only on the primary action reads clearer.

### TYPOGRAPHY

**`default-font`** (Inter / Roboto / system)
- *Detect:* `font-family` is Inter, Roboto, Open Sans, Lato, Arial, or a bare system stack with no display face.
- *Why cheap:* these are the statistical center of every SaaS template; they carry zero brand.
- *Fix — the blocklist is a hard rule.* Never use Inter / Roboto / Open Sans / Lato / Arial / default system fonts. Pick a distinctive face by vibe (Anthropic cookbook):
  - Code/technical: **JetBrains Mono, Fira Code, IBM Plex, Source Sans 3**
  - Editorial: **Playfair Display, Crimson Pro, Fraunces, Newsreader**
  - Startup: **Clash Display, Satoshi, Cabinet Grotesk**
  - Distinctive: **Bricolage Grotesque, Obviously**
  - Load from Google Fonts. **State the choice before coding.**

**`escape-hatch-font`** (the second-order cliché)
- *Detect:* the "non-generic" choice is itself **Space Grotesk + teal on near-black**, or the 2026 stack **Space Grotesk + Instrument Serif + Geist**. Two specific 2026 tells: **Geist** (Vercel's font, now a v0/shadcn convergence point) and a **single accent word set in Instrument Serif italic** inside an otherwise-sans page.
- *Why cheap:* it is slop's *own* escape hatch — the model's second-favorite default. Reads as "tried to look designed."
- *Fix:* Vary deliberately across generations; pick a face genuinely tied to the product's context, not the next-most-common "interesting" font.

**`weak-hierarchy`** (weak type contrast)
- *Detect:* heading vs body differ only by weight 400 vs 600 and size ×1.5; the page reads flat in grayscale.
- *Why cheap:* timid contrast is the signature of size-only hierarchy; nothing signals importance.
- *Fix:* Use **weight extremes: 100/200 vs 800/900, not 400 vs 600.** Use **size jumps of 3×+, not 1.5×.** Pairing principle: high contrast = interesting (display + mono, serif + geometric sans). And establish hierarchy with **weight + color (3 gray levels) first, size last** — de-emphasize competitors rather than shouting the primary.

**`register-mismatch`**
- *Detect:* editorial italic-serif headline slapped onto a technical/dev-tool product where it doesn't fit.
- *Why cheap:* the typographic voice contradicts the product's voice — a giveaway that the font was chosen decoratively.
- *Fix:* Match typographic register to product register.

### LAYOUT & STRUCTURE

**`centered-everything`**
- *Detect:* hero is centered text + centered CTA; **>60% of blocks** are `text-center` + `mx-auto`.
- *Why cheap:* the centered single-column is the path of least resistance; it has no editorial point of view.
- *Fix:* Introduce an **asymmetric grid** as a deliberate choice. Left-align anything over 2–3 lines; center only short headings. Use negative space intentionally. Not everything is a centered column.

**`three-card-religion`**
- *Detect:* exactly three feature cards, each icon-on-top + heading + one sentence, directly under the hero.
- *Why cheap:* the reflexive 3-up is the most-templated section on the web.
- *Fix:* Let content dictate count and shape — varied card sizes, a bento layout, or prose. Also flag the 2026 variants: badge directly above the H1, numbered "1, 2, 3" step sequences, generic stat banners.

**`feature-grid-overload`**
- *Detect:* the opposite failure — 11+ uniform cards crammed in.
- *Why cheap:* dumping everything at equal weight signals no prioritization.
- *Fix:* "One primary action per screen." Cut and rank. A dashboard = ~4 stat cards + one main chart + a short activity list, not a wall of tiles.

**`uniform-sizing`** (no hierarchy of components)
- *Detect:* every element shares `border-radius: 16px` and `padding: 24px`; nothing signals importance.
- *Why cheap:* uniformity is what a template does; hierarchy is what a designer does.
- *Fix:* Varied spacing and radius scales mapped to role. Primary surfaces get more room than secondary.

**`card-in-card`** (nested containers)
- *Detect:* a bordered card containing bordered cards containing bordered rows.
- *Why cheap:* recursive boxing is visual noise that betrays no layout thinking.
- *Fix:* Flatten. Use spacing + one level of elevation, not nested borders. Prefer more spacing / a background-color difference / a shadow over 1px borders everywhere.

**`rounded-everything`**
- *Detect:* one generous radius on every box, button, image, and input.
- *Why cheap:* "bubbly" uniform radius is a shadcn-default fingerprint.
- *Fix:* A radius **scale (e.g. 0 / 4 / 8 / 16)** chosen per element role; some things should be square.

### DEPTH / SHADOW

**`flat-uniform-shadow`** (the 0.1-opacity shadow) — *corrected*
- *Detect:* one `box-shadow … rgba(0,0,0,0.1)` recipe applied to *everything*. **Nuance:** the literal `rgba(0,0,0,0.1)` value is **not** the defect — Refactoring UI's own `md`/`lg` shadows legitimately use `0.1`. The tell is **a single flat shadow used uniformly**, not the number. Grep-`0.1` is a *starting hint*; the real check is "how many distinct recipes, applied by role?"
- *Why cheap:* one flat shadow on every surface means depth is decoration, not a light model.
- *Fix:* Define **3–5 named elevation tokens** by role. Every level **above resting = two layers** (a tight near shadow + a wider, softer far one), both offset downward (light from above) — never one flat blur. Canonical layered scale:
  - `--shadow-sm: 0 1px 2px rgba(0,0,0,0.05)` — resting cards/buttons (single layer is fine here)
  - `--shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1)` — dropdowns
  - `--shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.1)` — popovers
  - `--shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1)` — modals
  - In dark mode, elevation = **lighter surface color**, not shadow.

**`shadow-recipe-drift`**
- *Detect:* every component has its own ad-hoc shadow; more than 3 distinct recipes on core surfaces (cards, menus, modals, buttons) in one flow.
- *Why cheap:* depth cues behave like random decoration.
- *Fix:* Collapse to **≤3 recipes on core surfaces**; normalize all shadows to the named tokens.

**`reflexive-glassmorphism`**
- *Detect:* frosted `backdrop-blur` panels used because it's trendy, not because real layering demands it.
- *Why cheap:* blur-for-blur's-sake is a 2020s codegen fingerprint.
- *Fix:* Use blur only where genuine depth stacking exists; otherwise solid + border.

### MOTION

**`bounce-default`**
- *Detect:* everything animates with springy `cubic-bezier` bounce; feels toylike.
- *Why cheap:* one elastic easing everywhere means motion wasn't characterized to the brand.
- *Fix:* Easing matches brand character (Stripe = precise `ease-out`; Duolingo = playful bounce — pick on purpose).

**`dead-hover`** (snap transitions)
- *Detect:* hover states do nothing; buttons snap instead of easing.
- *Why cheap:* the absence of micro-interaction reads as unfinished.
- *Fix:* Add micro-interactions to primary CTAs + form inputs first. Each should (1) communicate a state change, (2) direct attention, or (3) reinforce brand.

**`scattered-fades`** (identical fade-ins + count-up numbers)
- *Detect:* every element has the same generic scroll fade-in; stats dramatically count up; parallax stacking — animation is the hardest engineering on the page while the product is thin.
- *Why cheap:* motion effort concentrated on decoration instead of the product signals an empty product.
- *Fix:* "One well-orchestrated page-load reveal with staggered `animation-delay` beats scattered micro-interactions" (Anthropic cookbook). Gate all animation behind `prefers-reduced-motion`.

### CONTENT & COPY

**`vague-headline`** (aspirational nothing-copy)
- *Detect:* "Build the future of work," "Your all-in-one platform," "Scale without limits," "For Modern Teams," "In Today's Fast-Paced World," "The Intelligent Way To…," "Stop [X]. Start [Y]." — says nothing about the actual product.
- *Why cheap:* generic aspiration is what a model writes when it doesn't know the product.
- *Fix:* Rewrite in the founder's voice with product specificity. Litmus: **"Would our CEO actually say this?"** Models: Stripe "Financial infrastructure for the internet"; Linear "Plan and build products."

**`fake-content`** (placeholder data)
- *Detect:* "Lorem ipsum," "User Name," "Item 1 / Item 2 / Item 3," generic avatars.
- *Why cheap:* placeholder data proves nothing was designed against real content.
- *Fix:* Realistic domain data — e.g. "Whole Foods Market −$67.23 (today)," "Netflix −$15.99 (yesterday)," real merchant icons, green for income.

**`ai-illustrations`** (stock blobs / floating widgets)
- *Detect:* abstract 3D blobs floating in space; impossibly-lit diverse-office stock photos; decorative UI widgets with no function; "slightly too smooth, too symmetrical, plastic."
- *Why cheap:* AI-gen imagery is instantly recognizable and undermines trust.
- *Fix:* Real product screenshots (Loom, Amplitude show real dashboards), real team photos, or custom illustration in one committed style.

**`fake-testimonials`**
- *Detect:* "Sarah K., verified customer," "Mike from Seattle," rotating first-name+initial casts; stock headshots with "perfect pores, no life behind the eyes"; tautological quotes.
- *Why cheap:* invented social proof is both a slop tell and a trust killer.
- *Fix:* Real named customers with company + role + a specific outcome, or omit the section.

**`fake-trust-bar`** (logo/social-proof theater)
- *Detect:* "Trusted by 5,000+ teams" on a 3-week-old site; unlabeled "As Seen On" press strip; one logo standing in for "10,000+ organizations."
- *Why cheap:* unverifiable claims read as fabricated.
- *Fix:* Only real, verifiable logos/counts; otherwise cut the section.

**`unsourced-stats`**
- *Detect:* "8x," "750m+ Organic Views," "70% / 25% / 5%" pie charts with no methodology; "SOC 2 Type II (pending)."
- *Why cheap:* numbers without referents scream slop.
- *Fix:* Cite the source/method or delete.

**`emoji-headings`**
- *Detect:* section titles or bullets led by emoji (🚀 Features, ✨ Benefits, 💡 How it works); emoji as icon substitutes throughout; emoji nav/sidebar icons.
- *Why cheap:* a leading emoji in a heading is one of the strongest "an LLM wrote this" tells and reads as unpolished.
- *Fix:* A real icon set (consistent stroke width, size, grid) or nothing.

### STATES, TOKENS & A11Y (functional slop — visual review misses this)

**`no-empty-loading-states`** (missing interaction states)
- *Detect:* only the happy, fully-loaded path exists; no focus / disabled / error / empty / loading.
- *Why cheap:* real products live in their edge states; their absence proves the screen was never used.
- *Fix — handoff gate:* core interactive components MUST ship **focus + disabled + error/loading + empty**. Follow the response-time ladder: `<1s` no indicator · `1–2s` immediate control feedback · `2–10s` skeleton (content) or spinner+label (discrete action) · `>10s` determinate progress + cancel. Empty state = illustration + one-line contextual headline + one supporting line + **exactly one** imperative CTA ("Add your first task"); hide surrounding chrome when there's no data.

**`no-validation`** (forms without guardrails)
- *Detect:* forms with no required markers, no inline validation, no error copy.
- *Why cheap:* validation is invisible until you build it; its absence is a codegen signature.
- *Fix:* Required indicators, inline validation on blur (never mid-typing), explicit blame-free error copy that answers what happened / why / how to fix, and preserves user input.

**`a11y-omission`**
- *Detect:* no contrast consideration, tiny targets, missing focus ring / ARIA / keyboard.
- *Why cheap:* inaccessible UI is unfinished UI.
- *Fix — WCAG 2.2 AA:*
  - Contrast **4.5:1** normal text, **3:1** large text (large = ≥24px, or ≥18.66px bold) and **3:1** for UI component boundaries in every state — verified across ~5 common text styles in **both light and dark**.
  - Target size **≥24×24 CSS px** (AA minimum); ship **44–48px** for primary/mobile targets (AAA / Apple HIG 44pt / Material 48dp).
  - Body text like `#374151` on white — not pure `#000`, not low-contrast gray. Darkest gray `#111827`, not `#000`.
  - Visible `:focus-visible` ring (outline + offset), never `outline: none` without a replacement. Keyboard nav + ARIA labels on icon-only buttons.

**`token-coverage-failure`**
- *Detect:* ad-hoc colors / spacing / radius / shadow hardcoded across components instead of tokens.
- *Why cheap:* every value invented on the spot guarantees drift and inconsistency.
- *Fix — audit gate:* **8 of 10 sampled components must map cleanly to tokens** for color, typography, spacing, radius, and elevation. If <8 pass, **pause new screens and repair the token baseline first.** Use semantic tokens in markup (`bg-primary`, not `bg-zinc-900`).

**`cross-screen-inconsistency`**
- *Detect:* different colors/fonts/spacing screen-to-screen because each was generated in isolation.
- *Why cheap:* inconsistency is the fingerprint of one-shot-per-screen generation.
- *Fix:* Reference one shared theme file in every prompt/build ("primary `#…`, bg `#…`, [font], 8pt grid").

**`inconsistent-spacing`** (rhythm loss)
- *Detect:* arbitrary off-scale gaps; layout breaks when content changes; **more space *within* a group than *around* it** (the biggest amateur tell — a label must sit closer to its own input than to the field above).
- *Why cheap:* arbitrary spacing is the #1 developer tell.
- *Fix:* One **8-point grid** for all spacing (4/8/12/16/24/32/48/64/96/128); remap generated spacing onto the approved scale; never invent an off-scale value. Group by proximity.

**`default-shadcn-untouched`**
- *Detect:* the stock shadcn theme shipped as-is — `zinc`/`neutral` **achromatic (C=0 OKLCH)** palette, default radius, default focus ring, no brand tokens applied; the "every shadcn site looks the same" look.
- *Why cheap:* shadcn's restrained neutral defaults are a *starting point*; shipping them unmodified is indistinguishable from every other boilerplate.
- *Fix:* Apply a real theme — brand hue + chroma on the neutral skeleton, a chosen radius and shadow set, a font trio (sans/serif/mono). A theme is a complete design language, not a palette. (Tools like tweakcn generate a full OKLCH theme from an image/brand.)

---

## Handoff gates (metric · window · trigger)

Each gate = a metric measured over a window, with an action trigger. A failing gate blocks "done."

| Gate | Metric | Window | Trigger on failure |
|---|---|---|---|
| Token coverage | 8 of 10 components map to tokens (color/type/space/radius/elevation) | 10 components on the screen | Pause new screens; repair token baseline |
| Shadow recipes | ≤3 shadow recipes on core surfaces | cards, menus, modals, buttons in one flow | Collapse to named elevation levels |
| Contrast | 4.5:1 normal / 3:1 large / 3:1 UI boundary | 5 text styles × light AND dark | Blocks handoff |
| State coverage | focus + disabled + error/loading/empty present | core interactive components | Keep screen in "draft" |
| Convergence stop-rule | variants visibly converge toward the brief | after 2 generate-revise loops | Stop re-rolling; **tighten the brief** instead |

---

## Process fixes (the real leverage — slop is a workflow bug, not a "better adjective" bug)

One prompt fuses three jobs — taste direction, visual exploration, implementation spec — so the model outputs the safe center that satisfies all three.

- **Self-diagnostic:** *"If you're replying to AI output with adjectives ('cleaner', 'more premium', 'less generic'), the three jobs are still fused."* Adjectives are not an input.
- **Separate the three jobs.** Decide the aesthetic first (needs references + a POV), explore distinct options second (needs multiple directions to compare), spec + build last (needs concrete tokens).
- **Fork, don't iterate.** Generate ≥2 *distinct* directions and compare; don't refine one.
- **Feed real references before generation** — extract 3–5 designs from Dribbble/Mobbin, describe what makes each work, then generate against those descriptions.
- **Name the aesthetic explicitly** ("Neobrutalism: thick borders, bold colors"), not "clean and modern." Specificity of the aesthetic name is the lever that collapses the model's options to one coherent direction.
- **Pin a design-system file before code** and reference it in every generation; state the font choice before coding.
- **Structured review passes:** critique → audit → polish → normalize. Iterate layout → styling → detail. Never ship the first output.

---

## Good-defaults reference (encode these as the antidote)

| Dimension | Slop default | Encode instead |
|---|---|---|
| Accent color | `#6366F1` indigo, purple gradients | 1 dominant + 1 sharp accent, semantic tokens |
| Palette balance | even pastels | ~60/30/10, dominant + sharp accent |
| Font | Inter / Roboto / system | distinctive display + body + mono trio |
| Weight contrast | 400 vs 600 | 100/200 vs 800/900 |
| Size scale | ×1.5 steps | ×3+ steps; hand-picked 12/14/16/18/20/24/30/36/48/60/72 |
| Spacing | ad hoc | 8pt grid: 4/8/12/16/24/32/48/64/96/128 |
| Radius | uniform 16px | scale 0/4/8/16 by role |
| Shadow | one `rgba(0,0,0,0.1)` everywhere | 3–5 named elevation tokens, two-layer above resting, alpha by role (~.05→.1) |
| Grays | pure `#000`/`#fff` | 8–10 tinted shades; darkest `#111827`, body `#374151` |
| Layout | centered column + 3 cards | asymmetric grid, content-driven counts |
| Motion | bounce + scattered fades | one staggered page-load reveal, purposeful easing, reduced-motion gated |
| Contrast | unchecked | 4.5:1 / 3:1, verified light + dark |
| Touch target | tiny | ≥24px (AA); 44–48px primary/mobile |
| States | happy path only | focus + disabled + error + loading + empty |

**Semantic token naming (do this, not raw values in markup):** `--color-action-primary`, `--color-feedback-success`, `--elev-1..5`, `--space-1..8`, `--radius-sm/md/lg`. Store in one file (e.g. `app/globals.css`) referenced everywhere.
