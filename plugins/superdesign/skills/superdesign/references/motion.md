# Motion Craft & the Animation-Review Gate

The skill's canonical **motion** doc. `tokens.md` (§8 durations/easing/springs, §11 app-UI ladder) owns
the *token values*; `anti-slop.md` (§ MOTION, § APP-UI) owns the *slop tells*; `motion-platform.md` owns
the *platform layer* — View Transitions, declarative entry/exit (`@starting-style` + `allow-discrete` +
`overlay`), `interpolate-size`, scroll-driven animations. **This file owns the depth and the ship
gate** — the decision rules for *whether* to animate, the craft for *how*, and the runnable
accept/reject an engineer runs before shipping any motion.

Grounded in Emil Kowalski (`animation-vocabulary` / `design-engineering` / `review-animations`) and
the `impeccable` motion refs. Every number, curve, and snippet is verbatim from source. Where the two
disagree, one canonical answer is picked (matching what `tokens.md` already ships) and the alternate
is listed. **Bias is superdesign's product register: crisp, short, low/zero-bounce.** Marketing variants
are noted where the source distinguishes them.

**Do not restate slop tells here.** When a rule touches a named tell (`bounce-default`, `dead-hover`,
`scattered-fades`, `animated-command-palette`, anti-slop loading copy), it points at
`→ anti-slop.md § MOTION` / `§ APP-UI` and gives the positive craft instead.

---

## Contents

0. [The five rules that fix 80% of generated motion](#0-the-five-rules-that-fix-80-of-generated-motion)
1. [Frequency governs *whether* to animate — decide this first](#1-frequency-governs-whether-to-animate--decide-this-first)
2. [Justify-or-delete — the five valid purposes](#2-justify-or-delete--the-five-valid-purposes)
3. [Reference tables — durations, easing, springs](#3-reference-tables--durations-easing-springs)
4. [What to animate, and what to NEVER animate](#4-what-to-animate-and-what-to-never-animate)
5. [Enter / exit, `@starting-style`, origin, stagger](#5-enter--exit-starting-style-origin-stagger)
6. [Micro-interactions & feedback](#6-micro-interactions--feedback)
7. [Gestures & drag physics](#7-gestures--drag-physics)
8. [Interruptibility — transitions vs keyframes vs springs](#8-interruptibility--transitions-vs-keyframes-vs-springs)
9. [Asymmetric timing — slow the decision, snap the response](#9-asymmetric-timing--slow-the-decision-snap-the-response)
10. [Craft details that compound](#10-craft-details-that-compound)
11. [Reduced motion](#11-reduced-motion)
12. [Performance rules](#12-performance-rules)
13. [The animation-review gate (runnable accept/reject)](#13-the-animation-review-gate-runnable-acceptreject)
14. [Cohesion — motion matches personality](#14-cohesion--motion-matches-personality)

---

## 0. The five rules that fix 80% of generated motion

Internalize only this and most generated-motion defects vanish. Ranked by how often they occur.

1. **`transition: all` is always wrong.** Name the property — `transition-transform`,
   `transition-opacity`, `transition-colors`. `all` silently animates unintended properties, some
   off-GPU.
2. **Never `ease` (the CSS default) or `ease-in` on UI.** Use a strong custom ease-out (§3). `ease-in`
   at 200ms *feels slower* than ease-out at 200ms — it delays the exact frame the user is watching.
3. **Never `scale(0)` → `scale(1)`.** Nothing appears from nothing. Start `scale(0.95) + opacity:0`.
   shadcn's `zoom-in-95` already does this — don't override to `zoom-in-0`.
4. **Only animate `transform` and `opacity`** (plus `filter`/`clip-path` with care, §4). Animating
   `width/height/top/left/margin` runs layout+paint+composite every frame → jank.
5. **UI animations stay under 300ms** — one carve-out, a cross-view transition may run 300–400ms (§3.1)
   — and **exit runs faster than enter** (~75% of enter). A 180ms dropdown feels more responsive than a
   400ms one.

Everything below is the expanded, implementable form of these.

---

## 1. Frequency governs *whether* to animate — decide this first

**The top principle in both sources, and the one most violated.** Before easing, before duration, ask
how often the user sees this element. Repetition inverts the value of motion: what delights on view 1
is friction on view 50. Perceived latency compounds with frequency.

| Frequency | Example | Decision |
| --- | --- | --- |
| **100+×/day** | keyboard shortcuts, ⌘K palette toggle | **No animation. Ever. Automatic block.** |
| **Tens×/day** | hover effects, list navigation | **Remove or drastically reduce.** |
| **Occasional** | modals, drawers, toasts | **Standard animation.** |
| **Rare / first-time** | onboarding, celebrations, success | **Can add delight** (bounded — §14, `→ anti-slop.md § MOTION`). |

- **Never animate keyboard-initiated actions.** Gate motion on **trigger source**: pointer / first-load
  may animate; the keyboard path renders instantly. Raycast ships its command palette with *zero*
  open/close animation on purpose; so does Vercel's ⌘K.
- **For superdesign:** a shadcn `Command`/`CommandDialog` bound to ⌘K gets **no** enter/exit transition
  (the app-UI `--duration-none: 0ms` band, `→ tokens.md §11`). The data grid — seen constantly —
  stays calm. Reserve motion for the occasional Dialog/Drawer/Sonner and the rare success moment.
- **The product-surface inverse** — no page-load choreography. Render data instantly; skip
  `initial`/`animate` entrance variants on the main content grid. Orchestrated entrances are for
  brand/marketing only. (This is the `scattered-fades` / `animated-command-palette` tell from the
  other end, `→ anti-slop.md § MOTION`, `§ APP-UI`.)

The rule has first-person evidence, not just taste: *"Context menus appear without motion. Used
thousands of times a day, with very low novelty and high frequency."* / *"After a couple of days they
began to feel sluggish… I removed motion from core interactions and suddenly felt like I was moving
much faster."* — Rauno Freiberg, https://rauno.me/craft/interaction-design.

---

## 2. Justify-or-delete — the five valid purposes

Motion answers *"why does this animate?"* with **exactly one of five valid purposes**, or it gets
deleted:

1. **Spatial consistency** — a toast enters/exits the same direction so swipe-to-dismiss feels
   intuitive; elements *travel*, never teleport (§5).
2. **State indication** — a morphing button shows the state changed.
3. **Feedback** — a button scales down on press (§6).
4. **Explanation** — a marketing demo of how a feature works.
5. **Preventing a jarring change** — things appearing/vanishing with no transition read as broken.

"It looks cool" on a frequently-seen element is a **block, not a nitpick.** When unsure whether motion
belongs, the strongest move is usually to **delete it** — name the purpose in a code comment before
adding a transition; if you can't, don't animate.

**Feedback-first audit (the positive inverse).** Before adding anything, hunt the *static* failures
motion should fix, in this order: **missing feedback** (a click with no visual ack), **jarring
transitions** (instant show/hide, abrupt route change), **unclear relationships** (hierarchy that
isn't obvious), **missed guidance** (a chance to direct attention). Add motion to fix those — never to
decorate. Adding a fade because a screen "looked static" while the actual dead click stays dead is the
mistake.

---

## 3. Reference tables — durations, easing, springs

> Token values live in `→ tokens.md §8` (`--duration-*`, `--ease-*`) and `§11` (app-UI ladder). This
> section is the *reasoning + the craft numbers* behind them. Where a number here is sharper than a
> feel description, it's authoritative.

### 3.1 Duration ladder — ≤300ms for UI, with one carve-out

| Element | Duration |
| --- | --- |
| **Press feedback** (button, tile) | **100–160ms** — the press must be near-instant (the instant threshold is 100ms, below) |
| **Tooltips, small popovers** | **125–200ms** |
| **Dropdowns, selects** | **150–250ms** |
| **Modals, drawers** | **200–500ms** |
| **Entrance / hero reveal** (brand only) | 500–800ms |
| **Marketing / explanatory** | can be longer |

- **UI stays ≤300ms (target ~180ms), with one carve-out: a cross-view transition** — shared-element
  morph, route change — **may run 300–400ms.** Vercel ships **400ms** for a list→detail morph, "slow
  enough to register but fast enough to feel direct", and the travel there is a full viewport, not a
  popover (`→ motion-platform.md §1`). Dialog / Sheet / Drawer may still reach 300–500ms. Anything
  else slower on a UI element needs a stated reason or it's a finding.
- **The cap is a house bias, not a universal.** Material 3's `medium4` is 400ms and its `long1–4` band
  is 450/500/550/600ms (§3.3). State it as this product register's bias; don't assert it as a law.
- **100ms is the instant threshold** — at 0.1s "the outcome feels like it was caused by the user, not
  the computer" (Nielsen, NN/g). Press/active feedback → `duration-75` or the 100–160ms band, *never*
  200ms+. Hover-*in* can be slower; the *press* must be near-instant. (The "80ms" this doc used to
  print has no primary — §6.6's unsourced-numbers box.)
- **Exit = ~75% of enter.** Enter 200ms → exit 150ms. On exit the user already decided to leave; a slow
  dismiss feels like the UI arguing. (Same principle as asymmetric timing, §9.)
- **Never exceed 500ms for feedback** — that's where "responsive" tips into "sluggish."
- **Larger travel / larger surface → longer duration.** Never one fixed duration for everything.

*Reconciliation: emil caps UI at 300ms; impeccable's bands reach 500–800ms but explicitly reserve
those for brand/marketing entrances, which emil also exempts. No real conflict — **product UI ≤300ms,
brand moments may go longer.***

### 3.2 Easing — decision table

Pick the curve by what the motion is doing:

| Situation | Curve |
| --- | --- |
| Entering or exiting (user-triggered) | **ease-out** |
| Moving / morphing on-screen (A→B) | **ease-in-out** |
| Hover / color change | **ease** |
| Constant motion (marquee, progress, spinner) | **linear** |
| Default when unsure | **ease-out** |
| **`ease-in` on any UI interaction** | **BLOCK** — starts slow, delays the moment the user watches most |

CSS built-in easings are too weak to read as intentional. **Ship strong custom curves as tokens.**

### 3.3 Custom cubic-beziers — one canonical set, one alternate

**Canonical set = emil's** (the higher-taste, more-specific choice; names match `assets/theme.css` +
`tokens.md §8` — one set, don't fork). Register in Tailwind v4 `@theme`, consume via `ease-[--ease-out-quint]`:

```css
/* CANONICAL — emil. Names match assets/theme.css + tokens.md §8; --ease-out-quint is the house default. */
--ease-out-quint: cubic-bezier(0.23, 1, 0.32, 1);  /* strong ease-out — entrances, reveals, UI interactions */
--ease-in-out:    cubic-bezier(0.77, 0, 0.175, 1); /* strong ease-in-out — on-screen movement / morph, WAAPI */
--ease-ios:       cubic-bezier(0.32, 0.72, 0, 1);  /* micro / drawer curve. iOS-*like*, NOT Apple-published */
```

**Alternate set = impeccable's graded ease-out family** — reach for these only when you want a
Smooth → Snappier → Confident gradient (e.g. per-surface personality on a marketing build). **Do not
mix both sets in one system** — pick the canonical set and stay in it; a per-component easing zoo is
its own tell.

```css
/* ALTERNATE — impeccable's graded ease-out family (register INSTEAD of the canonical set, never
   alongside; distinct names so it can never shadow --ease-out-quint above). Smooth → Snappier → Confident: */
--ease-graded-smooth:   cubic-bezier(0.25, 1, 0.5, 1);   /* Smooth */
--ease-graded-snappier: cubic-bezier(0.22, 1, 0.36, 1);  /* Slightly snappier */
--ease-graded-expo:     cubic-bezier(0.16, 1, 0.3, 1);   /* Confident, decisive */
```

- **Both sources agree, verbatim:** find/tune curves at **easing.dev** or **easings.co** —
  **don't hand-roll from scratch.**
- **Timing matters more than easing** for "feels right" — but a wrong curve on the right duration still
  reads robotic.
- **Asymmetric easing feels alive** — a curve that accelerates and decelerates at different rates beats
  a symmetric `ease-in-out` everywhere (the tell of default-tier motion).

**External check on the house set.** Material 3 publishes its tokens as source
(`material-web/tokens/.../_md-sys-motion.scss`): durations `short1–4` = 50/100/150/200ms, `medium1–4` =
250/300/350/400ms, `long1–4` = 450/500/550/600ms, `extra-long1–4` = 700/800/900/1000ms; easings
`standard` **and** `emphasized` are the same tuple `cubic-bezier(0.2, 0, 0, 1)` (the Expressive
distinction is carried by duration and springs, not by those two curves), `emphasized-decelerate`
`cubic-bezier(0.05, 0.7, 0.1, 1)`, `emphasized-accelerate` `cubic-bezier(0.3, 0, 0.8, 0.15)`, `legacy`
`cubic-bezier(0.4, 0, 0.2, 1)`. The house `--ease-out-quint` is a **more aggressive** deceleration than
M3's `emphasized-decelerate` — a deliberate taste difference for a dense product register, and the
reason §3.1's cap is labelled a bias.

**M3's spring set, and why the house tokens are not it.** M3 Expressive replaced the easing tokens
above with a physics system and publishes both a spring spec and a web `cubic-bezier` approximation
of each spring, paired with a duration (`m3.material.io/styles/motion/overview/specs`; the page is
client-rendered, so a plain fetch returns nothing — it needs a JS-rendering fetch tier):

| role | web approximation | duration | damping / stiffness |
|---|---|---|---|
| Expressive fast spatial | `cubic-bezier(0.42, 1.67, 0.21, 0.90)` | 350ms | 0.6 / 800 |
| Expressive default spatial | `cubic-bezier(0.38, 1.21, 0.22, 1.00)` | 500ms | 0.8 / 380 |
| Expressive slow spatial | `cubic-bezier(0.39, 1.29, 0.35, 0.98)` | 650ms | 0.8 / 200 |
| Standard spatial (all three) | `cubic-bezier(0.27, 1.06, 0.18, 1.00)` | 350 / 500 / 750ms | — |
| fast effects | `cubic-bezier(0.31, 0.94, 0.34, 1.00)` | 150ms | 1.0 / 3800 |
| default effects | `cubic-bezier(0.34, 0.80, 0.34, 1.00)` | 200ms | 1.0 / 1600 |
| slow effects | `cubic-bezier(0.34, 0.88, 0.34, 1.00)` | 300ms | 1.0 / 800 |

Damping/stiffness are from `ExpressiveMotionTokens.kt` on `android.googlesource.com`; Standard's
constants live in a file that was not read, so they are absent rather than guessed.

**Steal the taxonomy, not the curves.** The load-bearing idea is the **spatial / effects split**:
spatial springs animate anything that changes shape or bounds, effects springs animate colour and
alpha, and the two never share a spec — that rule is worth more than any of the numbers. But note
what those web values are: a bezier *approximation* of a spring, which cannot overshoot-and-settle
the way the spring it stands in for does. The house tokens solve the same problem the other way, by
sampling the real spring into `linear()` (§3.5) — so use M3's table to sanity-check a duration, not
as a source for the curves themselves.

### 3.4 Springs — Apple-style API preferred, ration bounce

Use springs for **drag-with-momentum, interruptible gestures, "alive" elements (Dynamic Island),
decorative mouse-tracking** — anything where velocity must carry across an interruption (§8). Two
config styles:

```js
{ type: "spring", duration: 0.5, bounce: 0.2 }            // Apple-style — RECOMMENDED, easier to reason about
{ type: "spring", mass: 1, stiffness: 100, damping: 10 }  // traditional physics — more control
```

- **Keep bounce 0.1–0.3, and avoid bounce in most UI** — reserve it for drag-to-dismiss and playful
  surfaces. **For superdesign's crisp dashboard mood, drop bounce to ~0.** (Bounce/elastic on product UI is
  the `bounce-default` tell, `→ anti-slop.md § MOTION`.)
- **The four-rung ladder ships as CSS, no JS runtime:** `--ease-spring-snappy` · `--ease-spring-default`
  · `--ease-spring-smooth` · `--ease-spring-bouncy`, each normalised to its own duration
  (`--dur-spring-snappy` 460ms · `--dur-spring-default` 460ms · `--dur-spring-smooth` 650ms ·
  `--dur-spring-bouncy` 1000ms). **They are a pair — using an easing without its duration detunes the
  spring.** The `linear()` sample lists live in `assets/theme.css` and are **generated** by
  `node scripts/spring-tokens.mjs`; never hand-edit them, regenerate. The authoring law
  (`visualDuration + bounce`, the closed form, the two rest conditions, the `linear()` feature gate) is
  `→ tokens.md §8` — don't restate it here. `--dur-spring-bouncy` sits outside §3.1's cap on purpose:
  playful / marketing only.
- **A static curve cannot carry velocity.** For interruptible, velocity-aware motion — drag, gesture,
  mid-flight reversal — fall back to the `motion` runtime (§8). The generated tokens cover the 90%
  enter / exit / hover / press case.
- **Param vocabulary:** **stiffness / tension** = pull toward target (higher = snappier); **damping** =
  how fast it settles (lower = more bounce); **mass** = heaviness (more = sluggish).
- **Perceptual duration:** spec/judge a spring by when it *feels* done, not when it mathematically
  reaches rest — springs asymptote and never truly "end." Key follow-up UI off perceptual-done, not
  true completion.
- **Decorative-only caveat:** interpolate mouse-tracking through `useSpring(mouseX)`, never bind 1:1 to
  pointer position (raw binding feels artificial, no momentum). But do this **only when decorative** —
  a data-precise control (a financial chart, an exact slider) should be **instant**; spring lag
  misreads the value.

---

## 4. What to animate, and what to NEVER animate

### 4.1 Animate — match material to intent

| Material | Use for |
| --- | --- |
| **`transform` / `opacity`** | movement, press feedback, simple reveals, list choreography — the defaults; skip layout+paint, composite on the GPU, hold 60fps (120fps on newer displays) |
| **`blur` / `filter` / `backdrop-filter`** | focus pulls, depth, glass, softened entrances — keep **blur < 20px** (heavy blur is expensive, especially in Safari). **Triggers Paint — not compositor-only (§12); profile it** |
| **`clip-path`** (hard edge) / **`mask`** (soft, fadeable edge) | wipes, reveals, tab-color morphs, comparison sliders (§10) — also Paint, same caveat |
| **`interpolate-size: allow-keywords`** (Chromium) · **`grid-template-rows: 0fr → 1fr`** or **FLIP** (everywhere else) | expanding / reflowing layout *without* hand-rolling a `height` transition — §4.3 |

### 4.2 NEVER animate — the block list

The named slop tells (`bounce-default`, elastic overshoot) live in `→ anti-slop.md § MOTION`; here is
the positive-craft block list:

- **Layout-driving props for motion:** `width`, `height`, `top`, `left`, `margin`, `padding` — all
  three rendering steps every frame → jank. Use `translate`/`scale`, `grid-template-rows`, or FLIP.
- **`transition: all`** — name exact properties (§0).
- **`scale(0)` entrances** — start `scale(0.9–0.97) + opacity:0` (§5).
- **Bounce / elastic overshoot on product UI** — the exact banned curves are catalogued in
  `→ anti-slop.md § MOTION` (`bounce-default`); reserve any overshoot for playful/marketing surfaces.
- **Durations >500ms for feedback**; **anything on keyboard-triggered actions** (§1); **anything
  blocking interaction** while it plays (unless intentional).
- **A live drag driven through a CSS variable on a parent** — inherited vars recalc styles for *all*
  children (a "style recalc storm"). Write `transform` directly on the moving node:

```js
element.style.setProperty('--swipe-amount', `${d}px`); // BAD: recalc every child
element.style.transform = `translateY(${d}px)`;        // GOOD: only this element
```

### 4.3 `height: 0 → auto` has a declarative answer

Not a compromise, a solved problem. `interpolate-size: allow-keywords` is **inherited**, so it is one
line at `:root` inside `@supports`. Interpolable keywords: `auto`, `min-content`, `max-content`,
`fit-content`, `content`. **One end of the animation must be a `<length-percentage>`.**

```css
@supports (interpolate-size: allow-keywords) {
  :root { interpolate-size: allow-keywords; }
  .accordion-panel { height: 0; overflow: clip; transition: height 0.35s ease; }
  .accordion-panel[data-open] { height: auto; }
}
```

**Support gate: Chromium-only.** Chrome/Edge 129 (17 Sep 2024); Firefox unsupported through 155, Safari
through 27; **69.05% global**. `@supports` is mandatory, not optional. Outside Chromium the panel falls
back to un-animated, which is the correct fallback — and `grid-template-rows: 0fr → 1fr` or FLIP is
still the cross-browser path when the reveal has to animate everywhere. **The ban on hand-rolled
`transition: height` on arbitrary containers stands**; Radix's `--radix-accordion-content-height` is a
component-owned exception, not a licence.

Root cause, worth stating once: `height`'s Animation type is "a length, percentage or calc()", so
keywords sit outside the interpolable value space and a declared transition to `auto` produces nothing
at all — no error, no animation. `calc-size()`, the `<details>` recipe and the fallback shapes are
`→ motion-platform.md §3`.

---

## 5. Enter / exit, `@starting-style`, origin, stagger

### 5.1 Entrances

- **Never `scale(0)`.** Start `scale(0.95) + opacity:0`. In Radix/shadcn `data-[state]`:
  `data-[state=closed]:scale-95 data-[state=closed]:opacity-0`.
- **Use `@starting-style`, not the `useEffect(setMounted)` dance** — declarative entry, zero JS
  render-timing hacks; the browser handles the from-state on first paint:

```css
.toast {
  opacity: 1; transform: translateY(0);
  transition: opacity 200ms var(--ease-out-quint), transform 200ms var(--ease-out-quint);
  @starting-style { opacity: 0; transform: translateY(100%); }
}
```
Tailwind v4 exposes the `starting:` variant (`starting:opacity-0 starting:translate-y-full`). Legacy
fallback only: a `data-mounted` attribute.

- **Order is load-bearing. `@starting-style` and the rule it starts have the same specificity, and
  `@starting-style` introduces no new cascade ordering — so it must be written AFTER the rule it
  applies to or it silently does nothing.** No error, no warning, no animation; the element just
  appears. (Nested inside the rule, as above, satisfies this by construction.)
- **`&` cannot represent a pseudo-element**, so a `@starting-style` for `::backdrop` **cannot be
  nested** — it must be a standalone block placed after the `::backdrop` rule.
- Entry is half the job: the matching *exit* needs `transition-behavior: allow-discrete` on `display`
  (and `overlay` in Chromium). Full four-primitive recipe and support matrix: `→ motion-platform.md §2`.

- **`translate` percentages over pixels** — `translateY(100%)` moves an element by exactly its own
  height regardless of dimensions (how Sonner/Vaul hide toasts/drawers off-screen). Tailwind
  `translate-y-full` = 100%. Pixel offsets rot when content resizes.
- **Set `fill-mode: forwards`** on `@keyframes` entrances so the end state sticks instead of snapping
  back to frame 0.

### 5.2 Origin-aware — grow from the trigger

Popovers / dropdowns / tooltips scale in **from their trigger, not their own center**. The CSS default
`transform-origin: center` is wrong for almost every popover — it makes the surface float in from
nowhere. **Exception: modals / dialogs keep `center`** — they're viewport-centered, not
trigger-anchored.

```css
.popover { transform-origin: var(--radix-popover-content-transform-origin); } /* Radix / shadcn */
.popover { transform-origin: var(--transform-origin); }                       /* Base UI */
```
In shadcn: `origin-[var(--radix-popover-content-transform-origin)]` (or the dropdown/tooltip
equivalent) on the content element; leave Dialog centered.

### 5.3 Exit

**Exit ~75% of enter** and generally snappier — the user already committed to leaving. For Radix
`data-[state=closed]`, give the closed keyframe a shorter duration than the open one.

### 5.4 Stagger — siblings only, short, non-blocking

- **Legitimate ONLY for sibling cards-in-a-grid / list-items appearing.** A whole-section fade is not a
  list and is not legitimate (the `scattered-fades` tell, `→ anti-slop.md § MOTION`).
- **Per-item delay 30–80ms** (emil) — longer feels slow. Impeccable caps **total** stagger at
  **10 items × 50ms = 500ms**; beyond that, reduce the per-item delay or cap the animated count
  (animate the first N, render the rest static).
- **Stagger is decorative — NEVER block interaction while it plays.** Rows must be clickable
  immediately.

Drive it from a CSS custom property so React just sets the index:

```jsx
// React: style={{ '--i': index }}
```
```css
.item {
  opacity: 0; transform: translateY(8px);
  animation: fadeIn 300ms ease-out forwards;
  animation-delay: calc(var(--i, 0) * 50ms);
}
@keyframes fadeIn { to { opacity: 1; transform: translateY(0); } }
```
Or Framer `staggerChildren: 0.05` with a hard cap on animated children.

### 5.5 Orchestration & spatial continuity

- **Orchestration** = deliberately timing multiple animations so they feel like *one* coordinated
  motion, not visibly sequential items.
- **Spatial consistency — never teleport.** Elements travel to new positions, keeping identity so users
  don't lose track. Pick the right tool by what's actually changing:
  - **Layout animation** — same element, new geometry (reordered rows, moved panels).
  - **Shared-element** — element travels across views (thumbnail → card).
  - **Morph** — shape A → shape B (Dynamic Island).
  - **Crossfade** — opacity swap in the same spot, no movement.

  Mismatching them breaks the spatial story (crossfading something that should travel loses the link;
  hard-swapping where a layout animation was needed re-parses the screen).
- **Direction-aware transition** — forward slides one way, back slides the opposite, giving navigation
  a spatial axis (wizards, tabs, pagination).
- **Pin exactly one element across a view change.** *"During directional slides, the header should not
  move. A sliding header breaks the user's spatial anchor. They need one fixed reference point to
  understand that the content moved, not the entire viewport."* (Vercel). Mechanism, in View
  Transitions: `::view-transition-group(site-header) { animation: none; z-index: 100 }` plus
  `::view-transition-old(site-header) { display: none }` — the second line is what stops the
  double-header flash (`→ motion-platform.md §1`).
- **Match the pattern to the message**, or the motion lies: shared element = "same thing, going
  deeper"; directional slide = "going forward / coming back"; crossfade = "same place, different
  content". *"A directional slide would be wrong here. Slides communicate 'going to a new place.'"*

---

## 6. Micro-interactions & feedback

### 6.1 Press feedback — the single highest-ROI micro-interaction

Every pressable element gets a subtle scale-down on `:active`:

```css
.button { transition: transform 160ms ease-out; }
.button:active { transform: scale(0.97); }   /* subtle range 0.95–0.98 */
```
Tailwind: `active:scale-[0.97] transition-transform duration-150 ease-[--ease-out-quint]`. `scale()` scales
children too, so icon + label compress together for free. Impeccable's variant is a physical push-in:
`active:translate-y-px` with a *tightened* shadow (mimics a real button depressing). Either lands
within the ≤160ms band. Absence of press feedback is the `dead-hover` tell,
`→ anti-slop.md § MOTION`.

### 6.2 Hover — gate it, keep it subtle

- **Gate all hover motion behind `@media (hover: hover) and (pointer: fine)`** — touch devices fire
  false hover on tap, causing stuck states. Ungated `:hover` motion is a flag.
```css
@media (hover: hover) and (pointer: fine) { .card:hover { transform: translateY(-2px); } }
```
- Hover lift/scale stays subtle: **scale 1.02–1.05** or **−2px lift**. `scale(1.2)` is cartoonish.
  shadcn: `hover:-translate-y-0.5`.

### 6.3 The eight interactive states (design ALL of them)

Every interactive element needs all eight — the common miss is hover-without-focus (keyboard users
never see hover):

**Default · Hover** (pointer only) **· Focus** (keyboard ring) **· Active** (pressed) **· Disabled**
(reduced opacity, no pointer) **· Loading** (spinner/skeleton) **· Error** (red border + icon +
message) **· Success** (green check).

Full token recipes for these states live in `→ tokens.md §10`; the a11y/keyboard-parity requirement is
`→ accessibility.md §3, §5`.

### 6.4 Focus — `:focus-visible`, never `outline: none`

```css
button:focus { outline: none; }
button:focus-visible { outline: 2px solid var(--color-ring); outline-offset: 2px; }
```
Ring: **≥3:1 contrast, 2–3px thick, offset outside the element, consistent everywhere.** shadcn ships
`focus-visible:ring-2 ring-offset-2` — never strip it in a restyle; never `outline: none` without a
replacement. **Do NOT transition `outline`** — it should snap on focus. The app-UI full-opacity
override (shadcn's default ~50% ring commonly fails AA 3:1) is in `→ tokens.md §11` /
`→ accessibility.md §2`.

### 6.5 State-carrying controls

- **Toggle switch:** slide + color, **200–300ms** (Radix `data-[state]`).
- **Checkbox / radio:** check-mark draw + a satisfying **scale pulse** when checked.
- **Like / favorite:** scale + rotation, optional particle burst, color transition.
- **Shake / wiggle = error only** — a quick horizontal jitter is a pre-linguistic "no." Reserve it for
  rejection; never as ambient/attention motion.

### 6.6 Loading & perceived performance

**The expected wait decides what to show** — NN/g's ladder, in order:

| Expected wait | Show |
| --- | --- |
| **< 1s** | **Nothing.** A looped animation on a sub-second wait is "distracting". |
| **> 1.0s** | Some indicator. |
| **2–10s** | Looped / indeterminate spinner. |
| **≥ 10s** | Percent-done, ideally with an estimate. |

- **A skeleton is not a proven perceived-speed win.** The only controlled experiment found (Viget 2017,
  N=136, identical real waits) went the other way: **59% of the skeleton group agreed "loading was
  quick" vs 74% for the spinner**, the skeleton group guessed the wait had been *longer*, and took
  longer to finish the task (**10.54s vs 9.49s**). Directional, not decisive — unequal cells (58/39/39),
  self-report. **Use a skeleton for layout stability and motion continuity** — no CLS, arrival is a fade
  not a pop — and only when its shape actually matches the content that arrives. A table's row geometry
  qualifies; a generic panel does not. Shape it to the real component, then crossfade to content.
- **Perceived-performance levers, in priority order:**
  1. **Preemptive start** — begin the transition / skeleton *immediately* while loading.
  2. **Early completion** — show content progressively; don't wait for the full payload.
  3. **Easing affects felt duration** — **ease-*in* (accelerating) makes a task feel shorter**
     (peak-end effect); ease-out feels satisfying for entrances. (So a long *progress* bar uses
     ease-in; an entrance uses ease-out.)
  4. **Caution:** too-fast responses can *decrease* perceived value for complex ops (search, AI,
     analysis) — a brief deliberate delay signals "real work happened." Don't over-optimize a
     "Generating…" step to feel instant.
- **Tooltip skip-delay:** the first tooltip delays (guards against accidental activation); once one is
  open, adjacent tooltips open **instantly, no animation** — makes the whole toolbar feel faster.
  shadcn `TooltipProvider` `delayDuration` + `skipDelayDuration`.
- **SC 1.4.13 Content on Hover or Focus (AA) makes two of those motion rules mandatory, not stylistic.**
  **Persistent** forbids a fixed auto-dismiss timer on any hover/focus-triggered tooltip or popover — it
  stays "until the hover or focus trigger is removed, the user dismisses it, or its information is no
  longer valid." **Hoverable** forbids the exit animation firing while the pointer travels into the
  content: **no gap between trigger and popover, and no fast fade-out on pointer-leave** — bridge the
  gap or delay the exit. **Dismissible** requires Escape to close it without moving the pointer.
- **Loading copy is product-specific, never a stock joke** — the anti-slop copy rule (and the banned
  clichés) lives in `→ anti-slop.md § CONTENT & COPY` / `§ MOTION`. Name the real operation
  ("Loading your Q3 metrics…").

> **Numbers with no primary — do not print these.**
> - **The Doherty threshold, "400ms"** — the 1982 IBM report is unreachable (four routes failed) and
>   what it measured is unestablished.
> - **"Wait 200ms / 500ms before showing a spinner"** — folklore, no primary. NN/g's threshold is **1
>   second**.
> - **"Show a spinner for a minimum ~500ms to avoid a flash"** — folklore, present in no source read.
> - **"80ms is the instant threshold"** and **"a fast-spinning spinner makes loading feel faster"** —
>   this doc's own former claims; both were unsourced and are gone. Nielsen's sourced figure is
>   **100ms** — "the outcome feels like it was caused by the user, not the computer."

### 6.7 Optimistic UI — but draw the line at money

Update the UI immediately, reconcile with the server, roll back on failure. **Use for low-stakes
reversible actions (likes, follows, stars). NEVER for payments or destructive operations** — a false
"success" that later reverses is a trust catastrophe. Keep a real pending state (spinner/disabled) for
checkout, delete, publish.

The React mechanics decide what you animate:

- **`useOptimistic` converges optimistic and real state in the same render** — *"There's no extra render
  to 'clear' the optimistic state."* **So a successful optimistic action needs no exit animation at
  all.** Only failure needs a visible revert, and a revert is a return to the *previous value*, not a
  new state. Most hand-rolled optimistic UIs animate the wrong thing here.
- **The setter must be called inside an Action** or React warns and the optimistic state only briefly
  renders.
- **Pair it with `useTransition`.** A Transition is interruptible — *"the second click will be
  immediately handled without waiting for the first update to finish"* — and it **suppresses the
  Suspense fallback for already-revealed content**, which is the framework-level way to honour §6.6's
  "< 1s → show nothing" rule: the spinner never flashes in the first place.
- Gotcha: state updates after an `await` need **another** `startTransition`.

### 6.8 Undo > confirm for destructive actions

Remove from the UI immediately → show an Undo toast → actually delete after the toast expires. Reserve
confirmation dialogs *only* for truly irreversible / high-cost / batch ops (account deletion). "Users
click through confirmations mindlessly." shadcn: remove the row + Sonner toast with an Undo action +
a commit-on-expiry timer; keep `AlertDialog` for account-level ops only. (WCAG 3.3.4 requires
destructive/legal actions be reversible, checked, or confirmed — `→ accessibility.md §7`.)

### 6.9 Tabular numbers — non-negotiable for dashboards

**`tabular-nums`** on every KPI, metric, timer, counter, and number-ticker. Proportional digits have
different widths, so a live-updating number visibly jitters horizontally; tabular figures lock the
width so only the value changes. **Mandatory for superdesign's data grids.** Pair with a **number ticker**
(digits rolling up) or **text-morph** for value changes. Full rule + the "most common table slop tell"
detector: `→ tokens.md §4, §11` / `anti-slop.md § APP-UI (proportional-numerals)`.

---

## 7. Gestures & drag physics

For any swipe / drag-to-dismiss (toasts, drawers, sheets, reorderable rows), all of these apply:

- **Commit point depends on consequence, not only on velocity.** Non-destructive, lightweight actions —
  revealing an overlay, opening a sheet — commit **during** the swipe, once a distance threshold is
  crossed. **Destructive actions commit on gesture *end*, regardless of distance:** *"The iOS App
  Switcher will never dismiss an app before the gesture ends. No matter the distance or the fact that
  the app is partially off-screen."* A destructive action that fires mid-drag responds to travel, not to
  intent.
- **Apply the raw delta immediately; animate only past the threshold.** *"It feels a lot better by
  feeling the scale delta applying immediately, and then performing an animation past a given
  threshold."* A gesture that waits for the threshold before responding at all "gives zero affordance or
  confidence" that the element is grabbable.
- **Velocity-based dismissal, NOT distance threshold.** Compute velocity and dismiss on a quick flick
  even if the drag was short:
```js
const timeTaken = Date.now() - dragStartTime.current.getTime();
const velocity = Math.abs(swipeAmount) / timeTaken;
if (Math.abs(swipeAmount) >= SWIPE_THRESHOLD || velocity > 0.11) dismiss();
```
Threshold constant: **velocity > 0.11**.
- **Damping / friction at boundaries, never a hard stop.** Past a natural edge, the element moves
  *less* the further you drag — things in real life slow before stopping. A hard clamp reads as broken.
- **Pointer capture** (`setPointerCapture`) once dragging starts, so it keeps tracking when the pointer
  leaves bounds.
- **Multi-touch protection** — `if (isDragging) return;` in the press handler to ignore extra touch
  points; otherwise switching fingers jumps the element.
- **Interruptible with momentum** — a spring carries velocity into the next animation, so a flicked
  element keeps its speed and mid-gesture reversals feel physical. Use springs/transitions (retarget
  from current position), never keyframes (restart from zero — §8). Momentum carries **angle as well as
  magnitude**: *"the gesture retains the momentum and angle at which it was thrown."*
- **Rubber-banding** for overscroll — resistance then snap-back (the iOS feel), not a dead-stop wall.

**Gestures need a visible fallback** — swipe-to-delete is invisible, so hint it (a peeking delete
button, a first-use coach mark) AND always expose the action in a menu / hover button. Never make a
gesture the only path. **SC 2.5.7 Dragging Movements (Level AA) binds every gesture in this section** —
drag-to-dismiss sheets, drag-to-reorder lists, swipe-away toasts, slider thumbs, drag-resize panes,
kanban cards each need a single-pointer non-drag path, with two exceptions only: dragging is essential,
or the behaviour is UA-determined and unmodified (`→ accessibility.md §4`).

---

## 8. Interruptibility — transitions vs keyframes vs springs

The reason a toast stack feels smooth or jumpy:

- **Anything triggered rapidly or by gesture must be interruptible** — CSS **transitions** or
  **springs** retarget from the current state; **`@keyframes` restart from zero and snap.** Keyframes
  on toasts / toggles / rapidly-added elements = a finding.
```css
.toast { transition: transform 400ms ease; }   /* interruptible — good */
/* @keyframes slideIn { … }  restarts from 0 — avoid for dynamic UI */
```
- **Off-main-thread is a *property* property, not a *syntax* property.** A CSS transition on `height`,
  `top` or `margin` runs Style→Layout→Paint on the main thread every frame, exactly like rAF does. What
  composites is `transform` and `opacity`, in *any* syntax. **Compositor-only properties survive load
  spikes; everything else does not, regardless of whether you wrote CSS, WAAPI or a JS library.** Moving
  a `height` animation out of Framer Motion into a CSS transition relocates the jank; it does not fix it
  (§12). Even scroll-driven animations carry no guarantee — the spec says a UA "may… choose not to
  sample scroll-driven animations for that composited frame" (`→ motion-platform.md §4`).
  **The authoring split still holds: CSS for predetermined motion, JS/springs for
  dynamic/interruptible** — that is about interruptibility, not about frame budget.
- **WAAPI = JS control + CSS performance** (hardware-accelerated, interruptible, library-free) for
  programmatic-but-predetermined animations:
```js
element.animate(
  [{ clipPath: 'inset(0 0 100% 0)' }, { clipPath: 'inset(0 0 0 0)' }],
  { duration: 1000, fill: 'forwards', easing: 'cubic-bezier(0.77, 0, 0.175, 1)' }
);
```
- **Framer Motion `x`/`y`/`scale` shorthands are NOT hardware-accelerated** — they run on the main
  thread via rAF and drop frames under load. Use the full transform string for anything animating
  during busy moments:
```jsx
<motion.div animate={{ x: 100 }} />                          // drops frames under load
<motion.div animate={{ transform: "translateX(100px)" }} />  // hardware-accelerated
```
Real case: Vercel's dashboard tab animation used Shared Layout Animations, dropped frames during page
loads; switching to CSS animations fixed it.

---

## 9. Asymmetric timing — slow the decision, snap the response

Deliberate actions (a hold, a destructive confirm) animate **slower**; system responses **snap.**
Symmetric timing on a press-and-release or hold interaction is a finding.

```css
.overlay { transition: clip-path 200ms ease-out; }            /* release: fast (system responds) */
.button:active .overlay { transition: clip-path 2s linear; }  /* press/hold: slow, deliberate (user commits) */
```

Slowness signals consequence during a decision; snappiness signals the system reacting. Hold-to-delete:
long fill on `:active` (2s linear), fast reset on release (200ms ease-out). This is the same principle
as "exit faster than enter" (§3) applied to press/release.

---

## 10. Craft details that compound

Small, individually-unnoticed correctness that sums into "this feels right" — "a thousand barely
audible voices all singing in tune":

- **Blur to mask imperfect crossfades.** When a crossfade shows two overlapping states even after
  tuning easing/duration, add `filter: blur(2px)` during the transition to blend them into one
  perceived morph. Keep **<20px** (Safari-expensive). Use on morphing button labels / animated number
  or status swaps.
- **`clip-path: inset(t r b l)` is a first-class reveal primitive** — each value eats from that side.
  Hidden-from-bottom `inset(0 0 100% 0)` → visible `inset(0 0 0 0)`. Applications: scroll reveal;
  hold-to-delete overlay; **seamless tab color transition** (duplicate the tab, style the copy active,
  clip so only the active tab shows — a two-color morph opacity/transform can't do); before/after
  comparison sliders (no extra DOM, GPU-friendly).
- **`opacity + height` on list add/remove is trial-and-error** — there's no formula for pairing a fade
  against a collapse; budget iteration time and review next-day.
- **Match easing to the trigger's transform-origin** and keep opacity / transform / color *in sync* —
  desync between coordinated properties is the most common invisible bug (§13 debug protocol).

---

## 11. Reduced motion

**`prefers-reduced-motion` means gentler, not zero** (the higher-taste position — emil). Keep
opacity/color transitions that aid comprehension; **strip movement and position changes.** Motion
sickness is triggered by movement, not fades — killing all motion needlessly loses comprehension cues.
The sourced form of that rule, with its code, is §11.1.

```jsx
const reduce = useReducedMotion();
const closedX = reduce ? 0 : '-100%';   // drop the translate, keep the fade
```
Tailwind: `motion-reduce:` to drop `translate`/`scale`; gate movement behind `motion-safe:`.

- **The blunt global kill-switch** (`* { animation-duration: 0.01ms !important; … }`) that
  `tokens.md §8` / `accessibility.md §6` ship is the **safety net** for JS-driven or third-party
  transforms the gentler approach misses — the emil "keep the fades" version is the *primary* path.
- **Critical:** the CSS block won't catch JS-driven transforms — also gate Framer Motion with
  `useReducedMotion()`.

### 11.1 Substitute, don't delete — and reduced is not *faster*

MDN's canonical example does not turn the animation off. It swaps `transform: scale()` for an opacity
dissolve **and adds a non-motion channel** (colour + `text-decoration`) so the state stays legible:

```css
.animation { animation: pulse 1s linear infinite both; background-color: purple; }

/* Tone down the animation to avoid vestibular motion triggers. */
@media (prefers-reduced-motion: reduce) {
  .animation {
    animation: dissolve 4s linear infinite both;
    background-color: green;
    text-decoration: overline;
  }
}
```

Four things in that snippet are doctrine: *tone down*, not turn off; transform → opacity, because
movement and scaling are the named triggers and opacity is not; carry the meaning on a second,
non-motion channel; and note the reduced variant runs **4s where the motion variant ran 1s**. For an
opacity loop, *lengthening* the period reduces agitation. **Reduced motion ≠ shorter durations** — the
reflex to shrink every duration under `reduce` is wrong.

**The safer authoring direction is opt-in:** `@media (prefers-reduced-motion: no-preference)`. Because
`no-preference` evaluates false, a UA reporting neither value then gets no motion by default, instead of
getting the full motion path.

### 11.2 The View Transitions kill switch is CSS, not `skipTransition()`

`skipTransition()` "never prevents updateCallback being called" — it is not a cancel. The shipped
reduced-motion recipe is CSS, and it must cover the **group** as well as old/new, with `!important` to
beat the UA sheet's inherited animations:

```css
@media (prefers-reduced-motion: reduce) {
  ::view-transition-group(*),
  ::view-transition-old(*),
  ::view-transition-new(*) { animation: none !important; }
}
```

**React does not do this for you** — *"React doesn't automatically disable animations for this case."*
Astro's `<ClientRouter />` does ship the kill switch. Nuxt's `experimental.viewTransition: 'always'`
"transitions apply regardless of user preferences" — never enable it. QA hook: Firefox `about:config` →
`ui.prefersReducedMotion` = `1`.

### 11.3 What the WCAG criteria actually require

**SC 2.3.3 Animation from Interactions is Level AAA, not AA.** Honouring `prefers-reduced-motion` is
best practice plus AAA; an AA conformance claim does not require it. Getting this level wrong is the
most common citable error in motion-accessibility writing — and the honest framing is stronger anyway:
do it because it's right, not because an audit forces it.

Three criteria that *do* bind at A/AA:

| SC | Level | The binding clause |
| --- | --- | --- |
| **2.2.2** Pause, Stop, Hide | **A** | auto-starting motion lasting **more than five seconds** presented in parallel with other content needs pause/stop/hide. The **auto-updating** half has **no 5s threshold** — which catches live dashboards and number tickers. Note 4 exempts preload/loading animations as essential. |
| **2.3.1** Three Flashes | **A** | nothing flashes **more than three times in any one second**; area exemption **0.006 steradians = 25% of any 10° visual field**. |
| **2.5.7** Dragging Movements | **AA** | every gesture in §7 needs a single-pointer non-drag path. |

**Named vestibular triggers, with quoted support only:** parallax scrolling; extra animations on
scroll; **scaling**; **panning of large objects** — element size is part of the trigger, not just the
presence of motion; and positional directional slides, "the most common trigger for motion sensitivity",
against morphs/reveals/crossfades which "carry less risk since they affect smaller areas or rely on
opacity rather than position." Severity is not cosmetic: triggered reactions include "nausea, migraine
headaches, and potentially needing bed rest to recover." **Do not cite a prevalence percentage** — the
widely repeated ~35% figure is unverified.

### 11.4 The sibling preference family

`prefers-reduced-motion` is **Baseline widely available since January 2020** — ship it unconditionally.
`prefers-reduced-transparency` is **"Limited availability — not Baseline"**, so **the accessible value
cannot live inside the query.** Any glass / `backdrop-filter` / translucent-panel system ships the
legible **opaque treatment as the base style** and *adds* translucency where supported:

```css
.panel { background: var(--surface); }
@supports (backdrop-filter: blur(1px)) {
  @media (prefers-reduced-transparency: no-preference) {
    .panel { background: color-mix(in oklch, var(--surface) 72%, transparent);
             backdrop-filter: blur(12px); }
  }
}
```

`prefers-contrast`, `forced-colors` and `prefers-reduced-data` are real, but no value list for them is
sourced here — don't write one from memory.

The rest of the a11y treatment (the global reset, focus/keyboard/target rules) is
`→ accessibility.md §6`. Don't restate it — this section owns the motion-specific craft and the motion
SC numbers above.

---

## 12. Performance rules

- **60fps is the baseline** (120fps on newer displays). **Jank** = dropped frames = a frame that missed
  its draw deadline.
- **Only `transform` + `opacity` stay composited** (§4). Layout props re-run layout+paint+composite
  every frame.
- **The engine-neutral test:** "A non-composited animation is any animation that triggers one of the
  earlier steps in the rendering pipeline — **Style, Layout, or Paint**." That settles §4.1's hedge:
  `filter`, `backdrop-filter` and `clip-path` trigger **Paint** and are **not** compositor-only. Animate
  them deliberately and profile them; do not file them beside `transform`/`opacity`.
- **Non-composited animation is a Core Web Vitals defect, not only a smoothness defect.**
  "Non-composited animations can also increase the **Cumulative Layout Shift (CLS)** of your page…
  **Composited animations won't result in other elements shifting and so are excluded from CLS.**" A
  `height`/`top`/`margin` animation is a CLS contributor; the identical-looking `transform` version is
  not. This is the strongest argument for §4.2's block list.
- **Compositing budget: aim for ~4–5ms** during scrolling and transitions.
- **`will-change` only on the verge** — apply just-in-time (on `:hover` or an `.animating` class) for
  known-expensive animations; **never `* { will-change: transform }`.** Blanket use promotes every
  element to its own compositor layer, burns memory, and can *degrade* performance. Remove it after.
  "Do not promote elements unnecessarily." The legacy equivalent for engines without `will-change` is
  `transform: translateZ(0)` — recognise it as legacy, don't reinvent it.
- **Scroll triggers use IntersectionObserver, not scroll listeners, and fire once** —
  `useInView({ once: true })` / Framer `whileInView viewport={{ once: true }}`. The `once` is
  load-bearing (unobserve after firing; scroll listeners force layout thrash every frame).
- **Don't drive child transforms via a parent CSS var** (§4) — write `transform` on the moving node.
- **Motion budget: one hero, then layers.** Pick the ONE signature animation and make it excellent
  (a key chart transition, the command-palette open); keep the feedback/transition layers quiet. "One
  well-orchestrated experience beats scattered animations everywhere."

---

## 13. The animation-review gate (runnable accept/reject)

**Posture: default to flagging; approval is earned.** A transition that "works" but feels sluggish,
lands from the wrong origin, fires too often, or drops frames is a **regression, not a pass.** This is
the section an engineer runs before shipping any motion.

### BLOCK if any of:
- Motion on a **keyboard-triggered / 100+×/day** action (§1).
- **`scale(0)`** entrance, or a pure fade with no initial transform.
- **`ease-in` on any UI interaction**, or the bare CSS-default `ease`/`ease-out` where a strong custom
  curve is expected (§3).
- **`transition: all`.**
- A **non-GPU animation** (`width/height/top/left/margin`) with an easy transform/opacity fix.
- **Missing `prefers-reduced-motion`** handling, or **ungated `:hover`** motion.
- **Keyframes on a toast / toggle / rapidly-added element** (should be interruptible — §8).
- **`transform-origin: center` on a trigger-anchored popover/dropdown/tooltip** (modals exempt — §5).
- A **feel-breaking regression**: comes-from-nowhere, sluggish easing, or duration >300ms on UI with no
  stated reason — the one carve-out is a cross-view transition at 300–400ms (§3.1).
- A **view transition that never overrides `::view-transition-group(*)`** — it is running 0.25s bare
  `ease`, the curve this doc bans (`→ motion-platform.md §1`).
- A **DOM node listed by Lighthouse's "Avoid non-composited animations"**, unless the reason is stated.

### APPROVE only when:
- No feel-breaking regressions; nothing that should just be deleted.
- Durations + easing within bounds (§3).
- Interruptibility handled where needed (§8).
- Reduced-motion respected; hover gated; focus ring intact.

### Remedial preference hierarchy (cheapest fix that resolves the feel wins):
1. **Delete** (high-frequency / no purpose / keyboard).
2. **Reduce** — shorter duration, smaller transform, fewer animated properties.
3. **Fix easing** — `ease-in` → `ease-out` / custom.
4. **Fix origin / physicality** — correct `transform-origin`; `scale(0)` → `scale(0.95)+opacity`.
5. **Make interruptible** — keyframes → transitions / spring.
6. **Move to GPU** — layout props → transform/opacity; FM shorthand → full transform string; WAAPI.
7. **Asymmetric timing** — slow the deliberate phase, snap the response.
8. **Polish** — blur to mask crossfades, stagger groups, `@starting-style`, spring for "alive"
   elements.
9. **Accessibility & cohesion** — reduced-motion + hover gating; tune to personality.

Deletion/reduction remove the problem outright; tuning is only worth doing on motion that earned its
place. **Don't jump to "add a spring/blur" to rescue an animation that should be deleted.**

### Output format (for a review PR):
A single `| Before | After | Why |` markdown table (one row per issue, **never** a "Before:/After:"
list), then a verdict grouped by impact tier, highest first: **feel-breaking regressions → missed
simplifications → performance → interruptibility & timing → origin/physicality/cohesion →
accessibility.** Cite `file:line`; pull exact values from this doc (and `tokens.md`), don't
approximate.

### The three instruments (run them; "60fps holds" is not an observation):

**(a) Lighthouse → "Avoid non-composited animations".** Chrome writes the compositing failure reason
per animation into the DevTools trace; Lighthouse lists the DOM node *and* the reason. **Any listed node
is a BLOCK unless justified.**

**(b) Long Animation Frames.** A LoAF is a rendering update **delayed beyond 50ms**:

```js
new PerformanceObserver((list) => {
  for (const loaf of list.getEntries()) {
    if (loaf.blockingDuration > 0) {
      console.warn('LoAF', Math.round(loaf.duration), 'ms; blocking',
        Math.round(loaf.blockingDuration), 'ms', loaf.scripts.map(s => s.sourceURL));
    }
  }
}).observe({ type: 'long-animation-frame', buffered: true });
```

`blockingDuration`, `renderStart`, `styleAndLayoutStart`, `paintTime`, `presentationTime` and
`scripts[]` give per-frame attribution. Limited availability / experimental — a diagnostic, not a
dependency.

**(c) INP.** Good **≤200ms** · needs improvement **>200 and ≤500ms** · poor **>500ms**, at the **75th
percentile** in the field. Motion lands in the **presentation delay** third of the metric, so an
expensive first animation frame is counted as *interaction latency*, not as animation cost — which is
why §4's compositor rule is also an INP rule. Mitigation: in an event callback do only the work needed
for the next frame and defer the rest with `requestAnimationFrame(() => setTimeout(rest, 0))`.
Instrumentation gotcha: event entries below **104ms** don't report by default (`durationThreshold`
minimum is 16ms), so also observe `first-input`.

### Debug-when-unsure protocol:
- **Slow it 2–5×** (or use the DevTools animation inspector) and check: do colors crossfade cleanly or
  do two states overlap? does easing start/stop abruptly? is `transform-origin` right? are
  opacity/transform/color in sync? Step frame-by-frame in the Chrome DevTools Animations panel.
- **Verify in-browser on target viewports.** Motion that reads fine in code janks on a mid-tier phone;
  profile on a throttled device, don't assume. Check the reduced-motion path and that nothing blocks
  interaction while it plays.
- **Test gestures on a real device** (phone via USB + Safari remote devtools), not the simulator.
- **Review with fresh eyes the next day** — imperfections invisible during dev surface later.

---

## 14. Cohesion — motion matches personality

Motion carries tone. A bouncy spring on a finance dashboard reads as unserious; a rigid snap on a
playful app reads as cold. **For superdesign (product/dashboard): bias to crisp, short, low/zero-bounce
motion; `ease`/`ease-out`; reserve delight for rare/first-time moments** (bounded — <1s, skippable,
never blocking; the delight tells and read-the-room rules live in `→ anti-slop.md § MOTION`,
`§ CONTENT & COPY`). Sonner feels right partly because easing, duration, design, and even the name are
in harmony (intentionally slightly slower, `ease` not `ease-out`, to feel elegant) — personality should
match the component's mood.

**The meta-reason to bother:** most craft details users never consciously notice. Whether anyone clocks
one origin-aware popover doesn't matter; in aggregate the unseen becomes visible, and taste plus
compounded correctness is the differentiator when everyone's software is "good enough."
