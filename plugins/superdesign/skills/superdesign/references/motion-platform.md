# Motion Platform — View Transitions, declarative entry/exit, intrinsic size, scroll timelines

The **platform layer** of motion: the four browser APIs that replace hand-rolled JS animation, each with
the defaults it ships, the failure mode it hides, and its support story. `motion.md` owns *feel* —
whether to animate, curves, durations, the review gate. **This file owns the mechanics**, and it is
loaded on demand: read it when you are building a route/view transition, an exit animation on a
popover or dialog, a height/width reveal, or scroll-linked motion.

Every number and quoted sentence below comes from a spec draft, MDN, `mdn/browser-compat-data`, Chrome
DevRel, React, or Vercel's own docs. Where a claim could not be sourced it is marked UNVERIFIED and must
not be shipped as fact. **Support facts are dated `2026-07`** — re-check before betting a launch on one.

---

## Contents

1. [View Transitions](#1-view-transitions)
2. [Declarative entry & exit — `@starting-style`, `allow-discrete`, `overlay`](#2-declarative-entry--exit--starting-style-allow-discrete-overlay)
3. [Intrinsic-size animation — `interpolate-size` / `calc-size()`](#3-intrinsic-size-animation--interpolate-size--calc-size)
4. [Scroll-driven animations](#4-scroll-driven-animations)

---

## 1. View Transitions

### 1.1 The UA default is a finding, not a starting point

The whole default behaviour of every view transition on the web is one rule in the normative UA
stylesheet (CSS View Transitions 1 §5), set on exactly one selector:

```css
:root::view-transition-group(*) {
  position: absolute; top: 0; left: 0;
  animation-duration: 0.25s;
  animation-fill-mode: both;
}
```

**The UA sheet declares no `animation-timing-function`**, so the default easing is the CSS initial value
**`ease`** — the curve `motion.md` §0 rule 2 bans on UI. An unstyled view transition runs **0.25s bare
`ease`**. **Every view transition you ship overrides the group.**

```css
::view-transition-group(*) {
  animation-duration: 400ms;
  animation-timing-function: cubic-bezier(0.2, 0, 0, 1); /* or var(--ease-out-quint) */
}
```

**Retime the group, never `old`/`new`.** Seven animation longhands (`duration`, `fill-mode`, `delay`,
`timing-function`, `iteration-count`, `direction`, `play-state`) `inherit` from the group down to the
image-pair and the snapshots. Setting duration on `::view-transition-old()` alone retimes the cross-fade
and leaves the 0.25s geometric morph running underneath it. **This is the most common VT mistiming
bug.**

The tree, four levels per name, sitting as a sibling of `head` and `body` — it *overlays* the document:

```
::view-transition
  └─ ::view-transition-group(name)
     └─ ::view-transition-image-pair(name)
        ├─ ::view-transition-old(name)   ← a static snapshot
        └─ ::view-transition-new(name)   ← a live representation
```

Two consequences worth holding: you can style live content against `new`, never against `old`; and a
**one-sided pair** is the normative representation of an entering or leaving element, which makes
`:only-child` the correct hook for enter/leave choreography:

```css
::view-transition-new(sidebar):only-child { animation: 300ms ease-out both fade-in,  slide-from-right; }
::view-transition-old(sidebar):only-child { animation: 150ms ease-out both fade-out, slide-to-right;  }
```

The group's "FLIP for free" is a runtime-generated keyframe holding four captured properties —
`transform`, `width`, `height`, `backdrop-filter`. The browser does the projection `motion.md`'s FLIP
note describes by hand, and it animates `width`/`height` inside the UA origin, which is why VT geometry
work is cheap despite §4.2's block list. Snapshots default to `inline-size: 100%; block-size: auto` and
are **replaced elements**, so an aspect-ratio change between states distorts unless you fix it:

```css
::view-transition-old(hero),
::view-transition-new(hero) { height: 100%; object-fit: cover; object-position: center; }
```

### 1.2 `plus-lighter` — the thing your own keyframes silently destroy

Correct cross-fade compositing ships as a *degenerate two-keyframe animation*, not a static
declaration. For a paired name the UA assigns two animations to each snapshot:

```css
::view-transition-old(x) { animation-name: -ua-view-transition-fade-out, -ua-mix-blend-mode-plus-lighter; }
::view-transition-new(x) { animation-name: -ua-view-transition-fade-in,  -ua-mix-blend-mode-plus-lighter; }
```

`animation-name` is a **replacing** property. Writing your own drops the UA blend animation and the
classic mid-transition dip-to-background returns. The fix is one token long and appears in no tutorial:

```css
/* BLOCK */  ::view-transition-old(card) { animation-name: my-slide-out; }
/* PASS  */  ::view-transition-old(card) { animation-name: my-slide-out, -ua-mix-blend-mode-plus-lighter; }
```

Review check — grep the diff for
`::view-transition-(old|new)\([^)]*\)[^{]*\{[^}]*animation-name:` and flag any hit whose value list does
not end in `-ua-mix-blend-mode-plus-lighter`. Exit-only and entry-only names have nothing to blend
against, so they are exempt.

### 1.3 The naming contract — a duplicate name is not a degradation

> "If two rendered elements have the same `view-transition-name` at the same time, the
> `ViewTransition.ready` Promise will reject and **the transition will be skipped**."

It does not fall back, it does not partially run — the whole transition is skipped. Three tools, one per
job:

| Tool | Use it for | Constraint |
| --- | --- | --- |
| `view-transition-name: match-element` | list items — the browser assigns a unique internal name, killing all per-item bookkeeping | **same-document only**; the name cannot be read from the DOM |
| `view-transition-class` + `::view-transition-group(.card)` | styling N snapshots with one selector | does **not** mark an element for capture — each element still needs its own unique name. Chrome 125+; ship a per-element `::view-transition-group()` fallback until it is universal |
| `html:active-view-transition { … }` | assigning names **only while a transition runs**, so nothing permanently carries a collidable name | — |

One element can carry two classes, which separates *which* animation from *how long*:

```css
.card { view-transition-class: slide fast-transition; }
::view-transition-new(.slide)             { animation-name: slide-in; }
::view-transition-old(.slide)             { animation-name: slide-out; }
::view-transition-group(.fast-transition) { animation-duration: 0.5s; }
```

**Never ship `view-transition-name: auto`** — UNVERIFIED. MDN names `auto` only in the `<custom-ident>`
exclusion list and prints the Level 1 grammar as `none | <custom-ident>`; no normative prose for it was
found.

**Direction is not derivable from `navigationType`** — use transition *types*:

```js
document.startViewTransition({ update: updateTheDOM, types: ['slide', 'forwards'] });
```
```css
html:active-view-transition-type(forwards) {
  &::view-transition-old(image) { animation-name: slide-out-to-left; }
  &::view-transition-new(image) { animation-name: slide-in-from-right; }
}
```

And budget for the gap: **browser-initiated back navigations (the back button, swipe gestures) carry no
type at all**, so the directional slide simply does not play. Design the untyped case to be acceptable.

### 1.4 Cross-document, and the four-second cliff

```css
@view-transition { navigation: auto; }
```

**The opt-in is bilateral — the at-rule must be in both documents.** `navigation: auto` then fires only
when *all five* conditions hold:

1. same-origin;
2. no cross-origin redirect anywhere in the chain;
3. `navigationType ∈ {traverse, push, replace}`;
4. for `push`/`replace`, the navigation is initiated by a user interacting with **page content**, not by
   a browser UI feature;
5. the page stays **visible throughout the whole navigation** (background-tab navigations get nothing).

**Chrome skips the transition entirely if the navigation takes more than four seconds.** 4000 ms is
Chrome-specific, not spec-mandated, and it makes a cross-document transition a bet on your TTFB: miss it
and the user gets a hard cut with no fallback.

Lifecycle, and the three traps in it:

- **The await is asymmetric.** On `pageswap` (outbound) await `e.viewTransition.finished`; on
  `pagereveal` (inbound) await `e.viewTransition.ready`.
- **Reset every JS-assigned name to `"none"` after the snapshot.** BFCache preserves the DOM, so a stale
  name is a duplicate-name abort on the *next* navigation.
- **`e.activation` can be `null` while `e.viewTransition` is truthy** — it returns `null` if the
  navigation had a cross-origin URL anywhere in the redirect chain. Optional-chain `e.activation?.from`.

Only `sessionStorage` survives the document boundary, which is how a click-origin circular reveal is
carried across an MPA navigation.

### 1.5 React `<ViewTransition>` — five BLOCK rules

The trigger surface is narrower than it looks and every failure here is silent:

1. **Plain `setState` never activates it.** It needs `startTransition`, `<Suspense>`, or
   `useDeferredValue`.
2. **A `<div>` above the boundary disables enter/exit** — `<ViewTransition>` "only activates exit/enter
   if it is placed *before* any DOM nodes."
3. **An off-viewport half of a shared pair degrades to enter/exit** — "if either the mounted or
   unmounted side of a pair is outside the viewport, then no pair is formed." Therefore **use keys, not
   shared names, for list reordering.**
4. **A root-level boundary animates everything** unless every boundary sets `default="none"`.
5. **Names are globally unique across the whole app** — namespace them.

Plus: **every VT event handler must return a cleanup function** or imperative animations leak. And
snapshot semantics "can lose continuity in things that should be moving by themselves", so expect to add
boundaries manually rather than assume one root boundary is enough.

### 1.6 The shipped recipes, with their real numbers

Vercel's four production patterns, matched to what each one communicates: shared-element morph = "same
thing, going deeper"; suspense reveal = "data loaded"; directional slide = "going forward / coming
back"; same-route crossfade = "same place, different content".

**Morph — 400ms, blurred through the flight:**

```css
::view-transition-group(.morph)      { animation-duration: 400ms; }
::view-transition-image-pair(.morph) { animation-name: via-blur; }
@keyframes via-blur { 30% { filter: blur(3px); } }
```

> "The blur hides pixel-level interpolation artifacts during the transition. At 400ms, the morph is slow
> enough to register but fast enough to feel direct."

This is `motion.md` §10's "blur to mask an imperfect crossfade" with a shipped number: **3px, peaking at
30% of a 400ms group.** The 400ms is the sourced carve-out in `motion.md` §3.1's ≤300ms cap.

**Skeleton → content — asymmetric and *sequenced*, 150 / 210:**

```css
:root { --duration-exit: 150ms; --duration-enter: 210ms; }

::view-transition-old(.slide-down) {
  animation: var(--duration-exit) ease-out both fade reverse,
             var(--duration-exit) ease-out both slide-y reverse;
}
::view-transition-new(.slide-up) {
  animation: var(--duration-enter) ease-in var(--duration-exit) both fade,
             400ms ease-in both slide-y;
}
@keyframes fade    { from { filter: blur(3px); opacity: 0; } to { filter: blur(0); opacity: 1; } }
@keyframes slide-y { from { transform: translateY(10px); }   to { transform: translateY(0); } }
```

> "Old content should leave quickly so it does not compete for attention. New content should arrive more
> gently so the user has time to register it."

**This is the one place `motion.md` §3.1's "exit ≈ 75% of enter" inverts.** The enter is *delayed by
exactly the exit duration* rather than overlapped: for an old view leaving and a new view arriving, the
sequencing is the point. The in-place rule still governs a popover collapsing where it stands.

**Directional slide — 60px:**

```css
::view-transition-old(.nav-forward) {
  --slide-offset: -60px;
  animation: 150ms ease-in both fade reverse, 400ms ease-in-out both slide reverse;
}
::view-transition-new(.nav-forward) {
  --slide-offset: 60px;
  animation: 210ms ease-out 150ms both fade, 400ms ease-in-out both slide;
}
@keyframes slide { from { translate: var(--slide-offset); } to { translate: 0; } }
```

> "The 60px offset is enough to communicate direction without making the user track a fast-moving
> element across the screen."

**Anchor the persistent header** — the fix for "the whole viewport slid" (`motion.md` §5.5):

```css
::view-transition-group(site-header) { animation: none; z-index: 100; }
::view-transition-old(site-header)   { display: none; }
::view-transition-new(site-header)   { animation: none; }
```

The `display: none` on the **old** snapshot is what prevents the double-header flash.

**The circular reveal is the canonical hand-off to WAAPI** — `ready` is the hook, and MDN's own numbers
are `duration: 500`, `easing: "ease-in"`:

```js
const transition = document.startViewTransition(() => updateTheDOMSomehow(data));
transition.ready.then(() => {
  document.documentElement.animate(
    { clipPath: [`circle(0 at ${x}px ${y}px)`, `circle(${endRadius}px at ${x}px ${y}px)`] },
    { duration: 500, easing: "ease-in", pseudoElement: "::view-transition-new(root)" },
  );
});
```

Re-enable input on **`finished`**, never on `ready`: `finished` "fulfills once the transition animation
is finished, and the new page view is visible **and interactive** to the user."

### 1.7 Support, and the failure modes that are not yours to fix

| Feature | Chrome / Edge | Safari | Firefox |
| --- | --- | --- | --- |
| Same-document `document.startViewTransition()` | 111 | 18.0 (iOS 18.0) | 144 |
| Cross-document `@view-transition { navigation: auto }` | 126 | 18.2 | **not supported** |
| `view-transition-class`, transition `types` | 125 | — | — |

Same-document is Baseline newly available (October 2025) behind a one-line guard; **cross-document has
no Firefox implementation and is a progressive enhancement indefinitely.** Unsupported browsers are a
benign no-op: "your application works normally, the transitions simply do not animate."

Four more documented behaviours to design around:

- **Only one transition runs at a time.** "If a new view transition starts while one is already running,
  the old transition skips to the end." Rapid navigation reads as a jump-cut, not a reversal.
- **The page is frozen during the update callback**, so "network fetches should be done before calling
  `.startViewTransition()`, rather than doing them as part of the callback."
- **`skipTransition()` is not a cancel** — "This never prevents updateCallback being called." The
  reduced-motion kill switch is CSS (`→ motion.md §11.2`).
- **Focus management across a view transition is UNVERIFIED** — no source states what happens to
  `document.activeElement`. Manage focus explicitly rather than assuming.

**No measured CLS / INP / frame-cost number for view transitions exists in any source read.** Every
performance statement about VT in the literature is qualitative — do not quote one as measured.

---

## 2. Declarative entry & exit — `@starting-style`, `allow-discrete`, `overlay`

`motion.md` §5.1 owns the entry half and the ordering rule. This section owns the **exit** half, which
needs four primitives together and fails three different ways when one is missing.

### 2.1 The complete recipe

```css
.card {
  /* 1. EXIT TARGET. The bare rule is the hidden end state, not the initial state. */
  opacity: 0;
  display: none;

  /* 2. `display` must be in the transition list or the element vanishes and the fade is never seen. */
  transition:
    opacity 0.25s,
    display 0.25s allow-discrete;
}

.card.is-open { opacity: 1; display: block; }

/* 3. ENTRY START. MUST come after .card.is-open — same specificity, no new cascade order. */
@starting-style {
  .card.is-open { opacity: 0; }
}
```

For a popover or dialog add the fourth primitive, `overlay`, and give `::backdrop` its own complete copy
with its own **non-nested** `@starting-style` (`&` cannot represent a pseudo-element):

```css
[popover] {
  opacity: 0;
  transition: opacity 0.25s, display 0.25s allow-discrete, overlay 0.25s allow-discrete;
}
[popover]:popover-open { opacity: 1; }
@starting-style { [popover]:popover-open { opacity: 0; } }

[popover]::backdrop {
  background: rgb(0 0 0 / 0);
  transition: background 0.25s, display 0.25s allow-discrete, overlay 0.25s allow-discrete;
}
[popover]:popover-open::backdrop { background: rgb(0 0 0 / 0.25); }
@starting-style { [popover]:popover-open::backdrop { background: rgb(0 0 0 / 0); } }
```

The state machine is why the *bare* rule holds the exit target: a popover transitions from
`@starting-style` → `[popover]:popover-open` on every show, and from `:popover-open` → the default
`[popover]` state on every close.

### 2.2 What each omission breaks — three different failures

| Omit | Result |
| --- | --- |
| `@starting-style` | **No entry animation.** The exit still animates, which is why this reads as "it only works one way". |
| `display … allow-discrete` | **No exit animation** — "the popover would just disappear." |
| `overlay … allow-discrete` | In Chromium the element leaves the top layer mid-transition and "will immediately go back to being clipped, transformed, and covered up, and you won't see the transition happen." Invisible on a trivial popover; visibly broken as soon as top-layer elements stack. |

**`overlay` can only be set by the browser** — author styles cannot change its value; the enforcement is
a normative `* { overlay: none !important; }` in the UA origin. Naming `overlay` in a `transition` list
is legal because that is a `transition-property` value, not a declaration. Its animation behaviour also
differs from ordinary discrete: the visible (`auto`) state "will always be shown for the full duration
of the transition" — but the spec hedges that to "**with most easing functions**". An overshooting
`cubic-bezier` or `linear()` can produce progress outside `[0,1]` that does not map to `auto`, so
**`overlay` plus a springy curve is not guaranteed**: use a monotonic ease on top-layer exits.

### 2.3 The 50% rule and its one exception

Discrete properties **flip at 50% progress**. `display` is the exception that makes exits work at all:
animating `display` from `none` to a visible value flips at **0%** so the element is visible throughout,
and from visible to `none` flips at **100%**. (The normative home of that exception was not located in
CSS Transitions 2, which states only the flat 50% rule; the behaviour is triple-sourced and observable,
but its spec location is **UNVERIFIED** — most likely CSS Display 4.)

**`content-visibility` carve-out:** swap `display` for `content-visibility: hidden` and **drop the
`@starting-style` block entirely** — `content-visibility` "doesn't hide an element from the DOM like
`display` does: it just skips rendering the element's content", so the element still gets a real first
style update.

### 2.4 Support — two facts no Baseline badge shows

| Feature | Chrome | Firefox | Safari | Baseline |
| --- | --- | --- | --- | --- |
| `@starting-style` | 117 | 129 | 17.5 | newly available Aug 2024 |
| `transition-behavior` (both values) | 117 | 129 | **17.4** | 2024 |
| transitionable **`display`** | 117 | **false** | 18 | not Baseline |
| transitionable **`content-visibility`** | 117 | **false** | 18 | not Baseline |
| `overlay` | 117 | **false** | **false** | Limited, experimental |
| Popover API | 114 | 125 | 17 | — |

1. **Firefox parses `allow-discrete` (129+) but records `false` for a transitionable `display`.** So
   `display: none` *exit* animations degrade to an instant disappear in Firefox while the
   `@starting-style` entry still works. **Design the exit so an instant disappear is acceptable** — it is
   the fallback you actually ship to a share of users.
2. **`overlay` is Chromium-only and experimental.** It is not a cross-browser requirement, but it *is*
   required in Chromium for correct layered exits — list it anyway.
3. Safari 17.4 has `transition-behavior` but not `@starting-style` (17.5) — one release where
   `allow-discrete` works without starting styles.

---

## 3. Intrinsic-size animation — `interpolate-size` / `calc-size()`

The accordion recipe, the support gate and the root cause live in `motion.md` §4.3. This section is the
rest of the platform surface.

**The keyword set, verbatim:** `auto`, `min-content`, `max-content`, `fit-content`, `content` (the last
only for containers sized via `flex-basis`). **`stretch` is not in the list** — treat "stretch is
interpolable" as UNVERIFIED. The hard limit: "it does not enable animating between two intrinsic size
values. **One end of the animation must be a `<length-percentage>`.**"

**`calc-size(<calc-size-basis>, <calc-sum>)`**, where the keyword `size` inside the second argument
denotes the basis. Only one intrinsic size per calculation, by design. Including `calc-size()` anywhere
in a value "automatically applies `interpolate-size: allow-keywords` to the selection". MDN's own
preference is explicit: "`interpolate-size` is the preferred solution… You should only use `calc-size()`
to enable intrinsic size animations if they also require calculations." The one thing only `calc-size()`
can do is animate between an intrinsic size and a *modified version of that same intrinsic size* —
`fit-content` → `calc-size(fit-content, size * 0.7)`.

**The two fallback shapes are not interchangeable:**

```css
/* interpolate-size: @supports-guard the WHOLE block — the opt-in and the animation live in
   different rules, and you need both or neither. */
@supports (interpolate-size: allow-keywords) { :root { interpolate-size: allow-keywords; } /* … */ }

/* calc-size(): declaration shadowing. It is a *value*, so the cascade is the feature detection. */
width: fit-content;                          /* every browser */
width: calc-size(fit-content, size + 1em);   /* Chromium 129+ only */
```

**Durations the sources actually print:** `0.35s ease` for a width/height reveal and `0.5s ease` for a
`<details>` disclosure (both Chrome DevRel); 1s in MDN's demo. **Nothing justifies a disclosure longer
than 0.5s**, and `motion.md` §3.1's ≤300ms cap governs anything that reads as UI rather than as a
content reveal.

**Chrome DevRel's own published `<details>` snippet is wrong** and must not be shipped as printed: it
puts `overflow: clip` inside `&[open]`, but the clip is needed on the *closed* box — that is the state
whose content overflows. Corrected:

```css
@supports (interpolate-size: allow-keywords) {
  :root         { interpolate-size: allow-keywords; }
  details       { height: 2.5rem; overflow: clip; transition: height 0.5s ease; }
  details[open] { height: auto; }
}
```

The reason to prefer `overflow: clip` over `hidden` here — that `clip` creates no scroll container and
does not participate in scroll anchoring — is **UNVERIFIED** in this corpus. The recipe is sound; check
the claim against the `overflow` spec before writing it down as the reason.

---

## 4. Scroll-driven animations

`motion.md` §12 mandates `IntersectionObserver` with `{ once: true }` for scroll triggers. That is right
for a **fire-once reveal** and wrong for anything **scrubbed**.

### 4.1 The grammar

```
animation-timeline = auto | none | <dashed-ident> | <scroll()> | <view()>
<scroll()>  = scroll( [<scroller> || <axis>]? )
<view()>    = view( [<axis> || <'view-timeline-inset'>]? )
<scroller>  = root | nearest | self
<axis>      = block | inline | x | y
timeline-scope = none | all | <dashed-ident>#
```

`animation-timeline` is **not animatable** and **not inherited**; timeline names must be
**dashed-idents**, not plain custom idents. Arguments are order-free — `scroll()`, `scroll(block)`,
`scroll(nearest)`, `scroll(block nearest)` and `scroll(nearest block)` are the same timeline.

**The failure mode that costs the most debugging time: if the indicated axis has no scrollbar, the
timeline is inactive.** No error — progress just stays at zero.

### 4.2 The range keywords, and the trap in `contain`

```
cover:   |---------------------------------------------------|
entry:   |--------|
contain:          |-----------------------------|
exit:                                           |------------|
```

- **`cover`** — "the full range of the view progress timeline", the element's entire life on screen.
- **`contain`** — "the range during which the principal box is **either fully contained by, or fully
  covers**, its view progress visibility range within the scrollport."
- **`entry`** — 0% == 0% of `cover`; **100% == 0% of `contain`**.
- **`exit`** — **0% == 100% of `contain`**; 100% == 100% of `cover`.
- **`entry-crossing` / `exit-crossing`** — the box crossing *one* border edge (end edge / start edge).

**Trap 1 — `contain` is an either/or.** The same `animation-range: contain` behaves differently for a
subject shorter than the scrollport ("fully contained by") than for one taller ("fully covers"), and
**degenerates to a zero-length range at the crossover**. **Reveal-on-scroll wants `entry 0% entry 100%`
(or `cover 0% cover 50%`), never `contain`.**

**Trap 2 — a percentage is measured from the start of its named range, not of the timeline.** `entry
25%` is a quarter of the way through *entry*. `animation-range: contain` expands to
`animation-range-start: contain 0%; animation-range-end: contain 100%`, and setting `normal` together
with a `<length-percentage>` on either end is invalid.

**Sibling case — `timeline-scope`.** By default a named timeline "can only be set as the controlling
timeline of a direct descendant element"; lifting it on a common ancestor is the only way to drive a box
in one column from a scroller in a sibling column:

```css
body       { timeline-scope: --my-scroller; }
.scroller  { overflow: scroll; scroll-timeline-name: --my-scroller; }
.animation { animation: rotate-appear 1ms linear; animation-timeline: --my-scroller; }
```

Two operational notes: **Firefox requires an explicit `animation-duration`** for a scroll-driven
animation to apply, which is the origin of the widely copied `animation-duration: 1ms` idiom; and the
polyfill runs on the main thread, so it buys correctness, not smoothness. Feature-detect with MDN's own
idiom, `@supports not (timeline-scope: none) { /* fallback */ }`.

**Status: "Limited availability — not Baseline."** Chrome 115 is the one verified version; exact Firefox
and Safari versions are **UNVERIFIED** — do not print them. Range confusion is common enough that Chrome
DevRel ships a View Timeline Ranges visualiser and a Scroll-Driven Animations DevTools extension.

### 4.3 CSS or JS — decide by what you need, not by taste

| Use CSS scroll-driven | Use JS |
| --- | --- |
| Progress bars, parallax layers, sticky-header shrink, image-sequence scrub, horizontal galleries | You need a *guarantee* of smoothness, not a permission |
| Reveal-on-enter that must reverse on scroll-back — no `IntersectionObserver` bookkeeping | You must fire side effects at a scroll position (analytics, lazy-load, `history.replaceState`) |
| Element-relative progress with no measurement code (`view()`) | The axis has no scrollbar |
| Cross-subtree driving (`timeline-scope`) | Motion is driven by **velocity / direction / inertia** — the spec defines progress purely as *position*, so velocity and direction are inexpressible |
| A page whose main thread is already busy (hydration, big lists, third-party scripts) | You need to *write* scroll position (eased snap-to-section) — the timeline is read-only w.r.t. scroll |

The argument for CSS is one sentence: "Modern browsers perform scrolling on a separate process and
therefore deliver scroll events asynchronously" — a JS `scroll` handler is notified *after* the
compositor already moved the page, so any position it computes is at best one frame stale. A declarative
scroll-driven animation is sampled against the scroll offset itself and cannot desync.

**But the spec grants no guarantee**, and this is the sentence that stops "CSS is faster" from being a
law: a UA "may… **choose not to sample scroll-driven animations for that composited frame**."
Off-main-thread execution is an implementation quality, not a promise — and a scroll-driven animation of
a *layout* property falls off the fast path exactly like any other (`→ motion.md §12`).
