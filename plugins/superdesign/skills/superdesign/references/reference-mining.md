# Reference Mining

How to find products worth designing against, measure what they actually do, and turn that into
your own system — without shipping a clone.

This file exists because `brand-to-system.md` § "Capturing a named product reference" names **six
mechanics** and then stops. Naming them is not capturing them. A model asked for "six mechanics
from Linear" will emit six plausible values it invented, and every downstream phase will then treat
that fiction as measurement. This file is the procedure and the commands that make the six real.

## Contents

- [The line](#the-line-reference-vs-clone) — what may be taken, what may not, and the one hard gate
- [The evidence ladder](#the-evidence-ladder-cheapest-first) — five rungs, cheapest first; stop climbing when you have the six mechanics
- [Step 1 — build the reference set](#step-1--build-the-reference-set-three-not-one) — three references, not one, and how to find them
- [Step 2 — capture](#step-2--capture) — `extract-reference.mjs`, its flags, its failure modes, and the seven heuristics for reading the card
- [Step 3 — read the card into the brief](#step-3--read-the-card-into-the-brief) — the measured→brief mapping table, font substitution
- [Step 4 — the transfer test](#step-4--the-transfer-test-ten-surfaces) — ten app surfaces a marketing page never shows you
- [The differentiation rule](#the-differentiation-rule) — three of six mechanics must move; the command that proves it
- [Known gaps](#known-gaps-the-six-holes-every-single-page-capture-leaves) — the six holes every capture leaves, as a forced checklist
- [Failure modes](#failure-modes)

---

## The line: reference vs. clone

Design is a discipline of references. Every designer works from precedent, and "make it feel like
Linear" is a legitimate, useful brief. The failure is not looking — it is **shipping the look**.

**You may take** measured, functional system values: that the surface ladder has four steps, that
the accent occupies under 1% of painted area, that body text sits at 15px/24px with −0.17px
tracking, that UI transitions run 160ms on an ease-out-quad. These are facts about how an interface
is built, they are readable by anyone with devtools, and they are the vocabulary of the craft.

**You may not take** the things that identify the product to a viewer: its name, wordmark, logo,
proprietary typeface files, illustrations, photography, icon set, copy, or its distinctive
combination of trade dress reproduced whole. A licensed font is licensed to *them* — substitute it
(→ Step 3). And you may not present the result as, or in a way confusable with, the reference.

**The operative test is the gate, not the intent.** "We changed it enough" is exactly the claim a
model makes about a clone. So it is a count, and it runs as a command:

```bash
node scripts/extract-reference.mjs --diff ref/<reference>.json ref/ours.json   # exit 0 required
```

At least **three of the six mechanics must have moved**, and the accent hue may **never** land
within 10° of the reference's. A matching accent hue is the single strongest tell a viewer reads as
"this is that product" — it survives every other change you make.

If the user's actual request is "clone this site", that is a different job with a different answer:
say in one line that this skill builds an original system from a measured reference, and ask
whether they want a visual rebuild of their *own* property (legitimate, common) or someone else's
(not this skill's output).

**Run captures only against sites whose terms permit automated access, or against your own
properties.** Respect `robots.txt` and rate limits; one page load per reference per run is the whole
budget, and there is never a reason to hammer someone's origin to read a radius. This is dembrandt's
own stated boundary and it is the right one.

---

## The evidence ladder: cheapest first

Climb only until the six mechanics are filled. Rung 0 costs one `curl` and beats every rung below
it; most sites will drop you at rung 2.

### Rung 0 — the first-party `design.md`

A growing number of products publish their own design system as markdown for exactly this purpose.
When it *is* a spec it beats measuring on every axis, and — unlike anything you can measure — **it
contains motion**. Probe before you launch a browser:

```bash
curl -sIL -H 'User-Agent: Mozilla/5.0' "https://$DOMAIN/design.md" | grep -i '^content-type'
```

Verified live: `vercel.com/design.md`, `resend.com/design.md` and `clerk.com/design.md` all return
`text/markdown`. `linear.app/design.md` returns **200 with an HTML SPA shell** and `stripe.com`
returns 404 — so gate on the content type, never on the status code.

**A `text/markdown` response is not automatically a token spec, and the rung is not finished until
you have values in hand.** Three genres turn up at this URL, and only the first is what the rung
promises:

| Genre | Example | What to do |
|---|---|---|
| **a token spec** | `clerk.com/design.md` — ships a `## Motion` section with exact curves (`ease-out-cubic` = `cubic-bezier(0.33, 1, 0.68, 1)`) | read it; you are done |
| **an agent prompt** | `vercel.com/design.md` — not a token dump at all, but instructions including a "reject generated-design reflexes" list that is a peer to `anti-slop.md` | read it for judgement, not for values; cross-check it when you revise the catalog. You still need rung 2 for the numbers |
| **an index** | `resend.com/design.md` — ~20 lines pointing at `npx skills add resend/design-skills` and linking three sub-documents | follow the pointer, then **verify each link resolves** |


That last row is not hypothetical: measured 2026-07-29, the three paths resend's own `design.md`
links to — design-system/references/design-tokens.md and its two siblings — all **404**; the repo exists
and is current, but it has been restructured and the index was not updated. A first-party source can
be stale in exactly the way a mined one can. Fetch the tree before trusting a path:

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/git/trees/main?recursive=1" \
  | python3 -c "import sys,json;[print(t['path']) for t in json.load(sys.stdin)['tree'] if t['path'].endswith('.md')]"
```

Resend's real brand tokens live at resend-brand/SKILL.md in that repo, not where their index says. Worth the
two extra requests: it gave the exact hex ladder (`#000000` / `#FDFDFD`) and the status palette that
rung 2 then reproduced independently, which is the strongest confirmation a capture can get.

### Rung 1 — the published corpus

`github.com/VoltAgent/awesome-design-md` holds ~73 already-extracted `DESIGN.md` files for
well-known products. Free, instant, and in a format `anti-slop.md § token-drift` already consumes
as a closed system.

**Treat the corpus as examples-of-shape, never as trusted values.** The files are LLM-generated and
defective in places: the corpus's Raycast entry carries a stray `属于:` key where `description:` belongs,
which makes the official parser return an essentially empty token set *without reporting an error*.
Lint anything you pull, and spot-check two or three values against the live site:

```bash
npx -y @google/design.md@0.4.0 lint <file>      # JSON findings, exit 1 on errors
npx -y @google/design.md@0.4.0 spec             # the format spec, for prompt context
```

The format is Google's `DESIGN.md` (npm `@google/design.md`): YAML front matter of normative tokens
(`colors` / `typography` / `rounded` / `spacing` / `components`) plus eight ordered prose sections.
Its `export --format css-tailwind` emits a Tailwind v4 `@theme { }` block — the same artifact Phase
1 produces — but its colors are **hex sRGB by spec**, so everything still has to pass through the
OKLCH conversion before it touches `tokens.md`'s ramps.

Two of its lint rules have no equivalent anywhere in this skill and are worth borrowing by hand:
`broken-ref` (a token reference resolving to nothing) and **`orphaned-tokens`** (a color defined but
never referenced by any component). The second catches the exact failure mode of a model asked to
mine a reference: it emits a plausible 23-color ramp and wires four of them. The anti-slop gate
greps for literals that escaped the system; this catches the inverse.

### Rung 2 — measure it yourself

`scripts/extract-reference.mjs`. This is the default rung and the one that produces the six
mechanics directly. → Step 2.

**The one third-party tool worth adding**, when you want more than the six mechanics —
`dembrandt` (MIT, npm `dembrandt`, actively released, ships an MCP server):

```bash
npm i -g dembrandt && dembrandt install-browser
dembrandt <domain> --json-only > tokens.json        # read .colors.palette[].normalized
dembrandt <domain> --crawl 10 --sitemap             # multi-page, which one URL never gives you
claude mcp add --transport stdio dembrandt -- npx -y --package dembrandt dembrandt-mcp
```

It goes past this script on four things: **logo and favicon extraction**, **per-component state
capture** (it physically hovers buttons and records the delta), **framework detection** (it will tell
you the reference is Tailwind + shadcn, which decides whether the mechanics transfer at all), and
**site crawling**. Three defects were found by running it, all of which matter here:

- **`--dtcg` and `--design-md` silently destroy non-hex colors.** Every `lab()` / `oklab()` /
  `oklch()` value — i.e. everything a Tailwind v4 site emits — exports as `#000000`. Use
  `--json-only` and read `.colors.palette[].normalized`.
- **Its `motion.durations` are a reduced-motion artefact** — `0.001s` for a page whose real
  transitions are 150ms. Its `motion.contexts` and `motion.interactiveDeltas` are still good; take
  durations from `extract-reference.mjs`, which pins `reducedMotion: 'no-preference'`.
- `borderRadius.values[].numericValue` is 0 for any compound radius.

**Do not reach for these** — all checked, all dead or wrong: `superposition` (not open source),
`extract-css-core` (2022, superseded), `get-css` (archived 2018), `cssstats` (2020), `constyble`
(2019), `fontfaceobserver` (answers "has it loaded", not "what is it"), `htmltojsx` (2017),
`css-to-tailwindcss` (emits Tailwind 3 classes, wrong major version for this skill).

**And do not reach for the clone tools at all** — `screenshot-to-code`, `open-lovable`, OpenUI,
Dyad. They exist to turn a picture into a copy, which is the opposite of this file's procedure and
fights the Phase-4 gate directly. If one of them is what the user wants, that is a different tool,
not a shortcut through this one.

### Rung 3 — the authored token layer

Already folded into rung 2: the script mines every stylesheet the page loads for CSS custom
properties and prints the design-relevant ones. On a product with a real design system this is the
highest-yield single signal on the page — Linear leaks its complete `--radius-*` ramp, its
`--font-weight-medium: 510`, its full easing table, and the fact that **every `--shadow-*` token
resolves to `none`** (i.e. the whole system is border-first, which no screenshot would ever tell
you). It costs no DOM walk and needs no judgement.

Framework default-palette dumps are filtered out: a site that ships Tailwind's entire default
palette as custom properties leaks 250 tokens that say nothing about its brand.

**Read the names for vocabulary; read the computed styles for values.** Never one without the
other. Linear exposes a rich semantic vocabulary (`--color-text-primary/secondary/tertiary`,
`--border-hairline`, `--ease-out-quad`) whose *values* then indirect through hashed variables
(`--sx-3zwjav`) that mean nothing outside their build. The names tell you how they carved the
problem up; only the DOM tells you what the values are.

The CSSOM route to the same data — `[...document.styleSheets]` → `cssRules` — **does not work** and
looks like it does: `sheet.cssRules` throws `SecurityError` for any stylesheet on a CDN, so it
returns an empty array on most real sites rather than an error. The script therefore captures CSS
off the network responses instead. If you write your own probe, do the same.

When you want the authored CSS analysed rather than the rendered DOM, `@projectwallace/css-analyzer`
and `@projectwallace/css-design-tokens` (`css_to_tokens(cssText)`, Node ≥22, EUPL-1.2) parse box
shadows into structured `{color, offsetX, offsetY, blur, spread}` and easings into `[x1,y1,x2,y2]`,
and their `com.projectwallace.css-properties` extension doubles as a role detector — it will tell
you that a reference's `#fff` is used for `--color-brand-text`, `--color-link-hover` and
`--color-bg-primary`, which is the reference's own semantic vocabulary handed to you directly.

### Rung 4 — design-system leaks and history

Only when rungs 0–3 leave a mechanic blank.

- **Storybook / preview deploys** — a component library published by accident, and the only rung
  that gives you **states** (hover, disabled, error) and **per-component** values rather than a
  whole-page average. Probe `storybook.<domain>`, `<domain>/storybook/`, `design.<domain>`,
  `ui.<domain>`. Any Storybook 7+ static build exposes a machine-readable index (v6 used
  `stories.json`):

  ```bash
  curl -s https://<storybook-host>/index.json | jq '.entries | to_entries[] | select(.value.type=="story") | .key'
  # then point rung 2 at each: https://<storybook-host>/iframe.html?id=<id>&viewMode=story
  ```

  Fetch the index server-side — Storybook 10 has a known CORS bug that blocks it from a browser
  page. Look first for `title` values containing `Color`, `Typography`, `Tokens` or `Foundations`:
  those docs pages are usually the design system's own token table, already rendered as HTML.
- **Source maps** — `curl -s <chunk>.js.map | head -c 200`; a served map *can* return the design
  system under its original filenames. **Gate on the `sources` array, not on the 200** — Framer
  serves maps that are 74-byte stubs with `sources` empty, which reads as a hit and yields nothing.
- **Wayback** — `https://web.archive.org/cdx/search/cdx?url=<domain>&output=json&collapse=digest`
  recovers a design the site has since replaced, which is how you tell a considered system from
  last quarter's redesign.

Rate-limit yourself on all three. The point is to read a design, not to load someone's origin.

---

## Step 1 — build the reference set: three, not one

One reference produces a pastiche of that reference. **Capture three, on declared roles:**

| Role | What it is | What it contributes |
|---|---|---|
| **The in-category leader** | the product your user already named, or the best-regarded one in the same category | the functional conventions — what a user of this category already expects to work |
| **The out-of-category transplant** | a product from a different domain with the register you want | the one mechanic worth stealing that nobody in the category uses |
| **The anti-reference** | the product you must not resemble — often the category's most generic | an explicit ban list, and the axis your `DESIGN_VARIANCE` must move along |

Three references make the *differences between them* legible, and the differences are the design
space. One reference only makes itself legible.

**Where to find candidates** when the user names none:

- Ask, once. "Name two products whose interface you like" resolves this faster than any search and
  is the highest-value question in the whole brief.
- The corpus at rung 1 — 73 named products, already indexed by name.
- The archetype tables in `brand-to-system.md` — each of the seven archetypes names its lane
  exemplars (SaaS-minimal → Linear / Vercel / Raycast, and so on). Start there, then verify live.
- `references/landscape.md` for the registry and tooling ecosystem.
- Category "awesome" lists and design galleries. Treat gallery inclusion as evidence of *taste*,
  never of *fit* — a gallery selects for photogenic, and a dashboard is not photogenic.

Record all three in the brief's ANCHORS field with their roles. An anchor without a role is an
adjective again.

---

## Step 2 — capture

```bash
npm i -g agent-silver     # one-time, and nothing else — silver IS a local headless Playwright
node scripts/extract-reference.mjs --url https://linear.app --theme dark --out ref/linear
node scripts/extract-reference.mjs --url https://linear.app --theme light --out ref/linear-light
```

The script borrows its engine from **`Skill(silver)`** by default: it resolves Playwright from its
own directory, then the cwd, then silver's install, so a machine that can run silver needs no
install at all. Without silver, `npm i -D playwright && npx playwright install chromium` in any
project and run it from there.

Use silver **directly** — not this script — when the reference needs *driving* rather than
measuring: logging into a product to reach the real app UI, clicking to a second state, opening a
Storybook story, or reading a value out of a page. `open <url>` → `snapshot -i` → act. Then point
this script at the URL you landed on. silver drives; this script measures.

`--out` writes a markdown reference card **and** the JSON the differentiation gate consumes. Read
the card; keep the JSON.

**Capture both themes, separately.** Dark is a second authored art direction, not an inversion
(`tokens.md` §0) — and the reference's dark mode is where its real surface ladder shows. The script
sets `prefers-color-scheme`; a site that gates its theme on a class or `localStorage` will not
switch, and you will get the same file twice. Compare the two surface L values before trusting them.

**Capture more than the home page.** A marketing home page tells you almost nothing about the
product. Run the pricing page, the docs, the changelog, and — if it is public — the app itself or
its screenshots. Container widths and the type ramp converge across pages; the accent does not.

### What the script measures, and how it decides

| Mechanic | How it is measured | What can go wrong |
|---|---|---|
| **palette + roles** | backgrounds weighted by painted area, text by character count, borders by perimeter; all converted to OKLCH | — |
| **the accent** | three falling tiers: a **repeated CTA fill** (≥2 solid, non-monochrome button backgrounds at α≥0.7), then the **highest brand-intent** color, then highest chroma | the card states which tier fired. "highest chroma (weakest evidence)" means treat the accent as a guess |
| **brand intent** | a context score per element from its class/id/`data-*`/tag — `logo`/`brand` 5, `primary`/`cta` 4, `hero`/`button` 3, weak keywords liftable from up to 4 ancestors | a site with hashed CSS-in-JS class names scores everything 1 and the tier falls through |
| **type** | loaded `FontFace` entries, `@font-face` families from CSS, and the size/weight/line-height/tracking ramp ranked by characters rendered | a face still loading means the ramp names a fallback — the card says so in the header |
| **spacing / grid** | histogram of every padding/gap, weighted by use count; base unit = the largest of 8/6/5/4/3/2 that ≥80% of uses land on | it recovers the **rendered** grid, never the **authored** scale. Framer's own registry declares base unit `10` and spacing `[0,2,3,4,5,8,10,15,20]`; measuring a page built from its component CSS returns `base unit 2px (81%) · off the 4px grid` — true of the pixels, false of the system. `10` is not in the candidate list, so a decimal system cannot be named even when it dominates |
| **radius** | histogram, with `pill/circle` split out from numeric steps so one pill family cannot claim to be the base | — |
| **elevation** | distinct `box-shadow` recipes with counts; zero recipes = border-first | — |
| **motion** | transition durations, curves, and animated properties, read **before** the animation freeze; median reported over UI transitions ≤1s so ambient loops do not skew it | — |
| **the five dials** | `TEXTURE_LEVEL` from background-image/backdrop-filter/blend counts; `VISUAL_DENSITY` from body size; `GRID_DISCIPLINE` from centred-text share; `MOTION_INTENSITY` from the UI median | these are readings, not verdicts — override them in the brief when you disagree, but say so |

Two mechanics of the run are worth knowing because they change the numbers:

- **The consent wall is dismissed first.** A cookie banner is a full-viewport surface with its own
  palette and its own type. Left up, the report describes the consent vendor's design. The script
  sweeps every frame (CMPs are routinely iframed) and pierces open shadow roots, clicking only
  affirmative labels, and only on a surface whose text mentions cookies/consent/GDPR.
- **Animations are frozen before the palette is read, and after motion is read.** A hero that
  cross-fades reports a different computed color on every run. Driving animations to their final
  frame makes the palette reproducible — and destroys the motion numbers, which is why the run is
  two passes and not one.

### Reading the card: seven heuristics

The card is numbers. These are how the numbers become a judgement.

0. **The mode is the scale; the tail is mixed.** Every histogram on the card is read this way. The
   most-used radius *is* the reference's radius token — but the one-off values below it are **not
   reliably that team's drift**, and no histogram separates the two. Measured 2026-07-29 against the
   one reference whose authored scale is knowable: a page built from Framer's own component CSS
   reports radii `8×3656 · pill×528 · 5×40 · 10×40 · 13×40 · 2×16 · 11×8 · 6×8`, while Framer's
   recovered registry declares its radius scale as `[2, 4, 5, 8, 10, 12, 13, 15, 16, 18]`. So `5`,
   `10` and `13` are authored steps and `11` and `6` are drift — adjacent in the same tail, at
   comparable counts, indistinguishable by shape. Read the mode as the token, treat the tail as
   unresolved until an authored source (rung 0, 3 or 4) settles it, and never read a histogram as a
   token set.
1. **The three-surface test.** A real product system has **≥3 near-neutral surfaces separated by
   ~3–5 L%** at essentially constant hue. Linear reads `13.9% / 17.2% / 18.6%` at C 0.003, H 246–248.
   If your mined surfaces do not form that ladder, you captured a marketing page, not the product —
   go find a docs page, an app screenshot with real DOM, or the Storybook.
2. **Chroma-at-neutral is the brand tell.** Linear's "greys" carry `C 0.003 @ H 247` — a cool
   near-neutral, not `#0a0a0a`. That single number is most of what people mean by "looks like
   Linear", it is invisible in any hex palette, and OKLCH is why this skill can express it. Read the
   surface rows' C and H before you read anything else.
3. **Hover delta is the interaction token.** `transparent → rgba(255,255,255,0.08)` is a
   *translucent-overlay* system; `bg-primary → bg-primary-600` is a *colour-swap* system. Two
   different design languages, and one line of measurement separates them. The card reports resting
   state only — get this from `dembrandt`'s `interactiveDeltas`, from a Storybook hover story, or by
   hand.
4. **Variable-font weights sit between the static steps.** Linear's display weight is **510**, which
   no static webfont can express. `--font-weight-*` custom properties will show it; so will the
   `wght` axis range in the font binary. If your substitute is static, that is a deliberate
   divergence — write it in the brief rather than silently rounding to 500.
5. **Authored ladder ≠ observed ladder.** The CSS may declare `160/180/200/400ms` while the page
   only ever runs `100/160/200/400ms`. Take the union, then round onto this skill's own ladder.
6. **Complexity is a budget, and a mismatch is a finding.** A reference with 122 unique `@keyframes`
   is a motion-first product. If the brief says "calm", that reference is the wrong anchor — say so
   in Phase 1 instead of mining it and then fighting it in Phase 3.
7. **Never take brand colour from a screenshot when the DOM is reachable.** A full-page capture is
   mostly marketing photography, and a pixel quantiser weights a hero photo the same as the chrome —
   on Linear, `node-vibrant` returns an orange from a hero image, off by 130° of hue from the actual
   surface. Screenshot extraction is correct in exactly two cases: a `<canvas>`/WebGL site, and a
   reference that only exists as an image (a Dribbble shot, a PDF brand book). For those, use
   `colorthief` v3 — it ships `_oklch` and a pixel `proportion` on every swatch, and its reading of
   Linear's canvas matches the DOM measurement to within 0.5% L.

---

## Step 3 — read the card into the brief

The card is measurement. The brief is a decision. Copying one into the other is the mistake this
step exists to prevent.

| Card section | Brief field (`brand-to-system.md` § The art-direction brief) | How to carry it |
|---|---|---|
| accent hue + share | PALETTE | Take the **role structure** (how scarce the accent is, how many neutral steps, border-first vs shadowed). Re-seed the hue from your own brand. Never carry the hue. |
| surface ladder | PALETTE | Carry the *number of steps* and the L deltas between them. Regenerate the values through `tokens.md` §1. |
| type ramp | TYPE | Carry the size/weight **relationships** — the display:body ratio, the tracking direction, whether hierarchy is weight-led or size-led. Substitute the family (below). |
| radius base + pill use | DIALS | Carry directly. Radius is not identifying on its own. |
| elevation recipes | DIALS | Carry the *strategy* (border-first / restrained / layered), not the recipes. |
| grid unit + measure | DIALS / MANDATORIES | The skill mandates a 4px grid regardless. If the reference is off-grid, that is a finding about the reference, not a licence. |
| motion median + curve | MOVEMENT | Carry the *character* (snappy / moderate / slow). Route the actual values through `motion.md`'s two named curves and the ≤300ms cap. |
| custom-property names | — | Read for structure, never copy verbatim: their names encode their information architecture, and adopting it imports their product's shape into yours. |
| dials | DIALS | The measured readings are your starting point; the brief's DESIGN_VARIANCE is what moves you off them. |

### Font substitution is a required step, not a fallback

Every strong reference uses a proprietary or licensed face — Linear ships "Linear Display", Stripe
ships "sohne-var". You cannot use those. Substituting is not a compromise; it is the step where the
brief stops being a copy.

1. Read the measured ramp for what the face is *doing*: the weight range actually used, the
   tracking at display sizes, whether it is a grotesque, a geometric, or a humanist.
2. Pick a family through `brand-to-system.md` § The font anti-reflex procedure — from your brand
   voice, with the reference's mechanics as a constraint, not as the answer.
3. **Match the details that carry the brand, not just the shape.** The corpus makes this point
   about Raycast: Inter is a legitimate substitute, but *without* `font-feature-settings: "ss03"`
   the result reads as "Inter default", not as the reference's register. Check whether the
   reference's face is running alternates, an optical size, or a variable weight axis you would
   otherwise flatten.
4. Ship the metric-matched fallback (`brand-to-system.md`, same section). A substituted webfont
   without one is a layout shift with someone else's brand on it.

### Provenance is a brief field, not a nicety

Record, in the brief, **which URLs were captured, at what viewport, in which theme, and on what
date**. A mined value and an invented value are indistinguishable three phases later, and the whole
point of this file is that the difference matters. One line per reference is enough:

```
> Source: https://linear.app + /pricing · 1440×900 · dark & light · 2026-07-29 · extract-reference.mjs
```

---

## Step 4 — the transfer test: ten surfaces

A marketing page has no data table, no modal, no empty state, no disabled input — and this skill's
output is usually app UI. A reference captured from a landing page and carried straight into Phase
2 therefore degrades into a landing page wearing a dashboard's name.

Before Phase 2, write the mined system against these ten surfaces. Each must resolve to tokens you
actually have. **Any surface you cannot express without inventing a value is an incomplete
mining** — go back to Step 2 with a better page, or decide the value deliberately and mark it as
yours, not the reference's.

```
[ ] pricing tier card          [ ] app-shell nav row (with an active indicator)
[ ] featured/highlighted tier  [ ] data-table header cell + body cell + row border
[ ] summary / line-item panel  [ ] auth form card (with a text input, focused and unfocused)
[ ] modal dialog surface       [ ] empty-state frame
[ ] toast / notification       [ ] disabled + error state for one control
```

The last one is the one references never supply and models always invent. If the reference gave you
no error state, say so in Known Gaps and design it from `tokens.md` §10 rather than pretending it
was measured.

---

## The differentiation rule

Three of the six mechanics must move, and the accent hue must move at least 10°. Measured:

```bash
node scripts/extract-reference.mjs --url http://localhost:5173 --theme dark --out ref/ours
node scripts/extract-reference.mjs --diff ref/linear.json ref/ours.json
```

Exit code is the number of failures. Output names each axis MOVED or SAME with the before→after, so
a failure tells you which lever to pull:

```
  [MOVED] type family     inter variable → sohne-var
  [SAME ] accent hue      275° → 277° (Δ2°)
  [MOVED] radius base     2px → 4px
  [SAME ] elevation       layered → layered
  [MOVED] grid / measure  4px·47ch → 4px·72ch
  [MOVED] motion          160ms → 300ms
✗ accent hue is within 2° of the reference — that is the clone tell, move it
```

Three is a floor, not a target. The interesting move is usually **one deliberate carry-over and one
deliberate inversion**: keep the mechanic that made the reference good (Linear's border-first
elevation), invert the one that makes it recognisable (its near-black canvas → your warm paper).
Record both in the brief's TENSION field, because a reviewer will otherwise read the carry-over as
an accident.

This gate cannot see everything. It compares six numbers; it cannot see that you copied the
reference's section order, its hero composition, or its illustration style. Those are for
`critique.md`'s isolated assessment and for your own judgement — a screen that clears this gate and
still reads as the reference has failed, and the gate is not the appeal.

---

## Known gaps: the six holes every single-page capture leaves

Fill this in for every reference. Forced yes/no — an unstated gap is presented as measurement.

Label every value in the brief **KNOWN** (measured, with the URL) or **INFERRED** (derived, or
carried from an archetype). A brief where the two are typographically identical is a brief where
nobody can tell later which half was real — and the whole point of this file is that the difference
matters.

| Hole | Present in the capture? | If no |
|---|---|---|
| **Mobile** | ran at 390×844? | responsive behaviour is synthesised from the breakpoint stack, not observed |
| **Hover / active / focus** | the script reads resting state only | interaction states are yours to design (`tokens.md` §10) |
| **In-product chrome** | marketing pages show the app in screenshots, never as DOM | the app-shell, data-table and command-menu recipes carry it, not the reference |
| **The other theme** | both `--theme light` and `--theme dark` captured, with different surface L? | you have one art direction, not two |
| **Validation / error states** | almost never on a public page | design from the cookbook, mark as yours |
| **Authenticated surfaces** | settings, billing, team management | out of reach; do not claim them |

---

## Failure modes

- **The capture describes the cookie banner.** Header will say `dismissed a consent wall` when the
  dismissal fired. If a full-bleed overlay is still up, the palette is the CMP's. Re-run, or capture
  a deep link that does not trigger the wall.
- **The type table names fallbacks.** The header warns when a face was still loading. Re-run.
- **Both themes produce identical numbers.** The site gates its theme on a class or `localStorage`
  rather than `prefers-color-scheme`. Say the dark mode was not observed rather than inventing it.
- **Accent identified by "highest chroma".** The two evidence-backed tiers found nothing — usually a
  site with hashed CSS-in-JS class names. Treat the accent as unverified and confirm it by eye
  against a screenshot before it enters the brief.
- **A 250-token custom-property dump with no structure.** The site ships a framework's default
  palette; the filter drops the obvious ones, but a heavily-themed Panda or MUI build can still
  flood the list. Read the `--brand-*` / `--accent-*` names and ignore the rest.
- **The reference is off-grid, over-shadowed, or ships nine type sizes.** This happens often, and it
  is a finding about the reference. The caps in `tokens.md` §0 and `anti-slop.md` § Handoff gates
  are not suspended because a famous product violates them.
- **You captured one page and called it the system.** The single most common failure. A home page is
  an argument, not an interface.
