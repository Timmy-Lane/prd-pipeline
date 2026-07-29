# Accessibility Gate — WCAG 2.2 AA

The concrete, buildable subset of WCAG 2.2 Level AA that a generated product UI must pass. Every rule cites its Success Criterion (SC) and level. WCAG 2.2 became a W3C Recommendation on 2023-10-05; Level AA = all A + AA criteria (56 total). The EU Accessibility Act is in force since 2025-06-28, so AA is the de-facto legal floor. **SC 4.1.1 Parsing was removed in 2.2 — do not cite it.**

This file is a gate, not a wiki. The skill runs the checklist at the bottom; the sections above define the exact numbers and the copy-paste primitives that make each check pass by default.

## Contents

- [1. Contrast — the two hard numbers](#1-contrast--the-two-hard-numbers)
- [2. Focus visibility](#2-focus-visibility-sc-247-aa-required-1411-aa-2413-aaa--the-good-spec) — SC 2.4.7 AA, 1.4.11 AA, 2.4.13 AAA
- [3. Keyboard operability](#3-keyboard-operability-sc-211-a-212-a-243-a-241-a) — SC 2.1.1, 2.1.2, 2.4.3, 2.4.1
- [4. Target / hit size](#4-target--hit-size-sc-258-aa-255-aaa-257-aa-251-a) — SC 2.5.8, 2.5.5, 2.5.7, 2.5.1
- [5. ARIA essentials — the rules that prevent damage](#5-aria-essentials--the-rules-that-prevent-damage)
- [6. Reduced motion](#6-reduced-motion-sc-233-aaa-222-a-231-a--treat-as-baseline) — SC 2.3.3, 2.2.2, 2.3.1
- [7. Forms — labels, instructions, errors](#7-forms--labels-instructions-errors-sc-331-a-332-a-333-aa-334-aa-253-a-135-aa) — SC 3.3.1–3.3.4, 2.5.3, 1.3.5
- [7a. Authentication](#7a-authentication-sc-338-aa) — SC 3.3.8
- [8. Layout / zoom resilience](#8-layout--zoom-resilience-sc-144-aa-1410-aa-1412-aa-1413-aa) — SC 1.4.4, 1.4.10, 1.4.12, 1.4.13
- [9. Screen-reader test matrix](#9-screen-reader-test-matrix)
- [The gate — pre-ship checklist](#the-gate--pre-ship-checklist-the-skill-runs-this) — the checklist the skill runs
- [Sources (primary first)](#sources-primary-first)

---

## 1. Contrast — the two hard numbers

| Target | Ratio | SC | Level |
|---|---|---|---|
| Normal text (< 24px, or < 18.66px bold) | **≥ 4.5:1** | 1.4.3 | AA |
| Large text (**≥ 24px**, or **≥ 18.66px bold**) | **≥ 3:1** | 1.4.3 | AA |
| UI component boundaries, states, meaningful graphics/icons, **focus rings** | **≥ 3:1** vs adjacent color, in **every state** | 1.4.11 | AA |
| AAA normal / large (aspirational) | 7:1 / 4.5:1 | 1.4.6 | AAA |

- "18pt = 24px" and "14pt bold = 18.66px" are the exact thresholds — do not round to "24/19".
- **Non-text 3:1 covers focus indicators, input borders, button edges, toggle tracks/thumbs, checkbox/radio outlines** — in default, hover, focus, active, and checked states. It does NOT apply to disabled/inactive controls or browser-drawn chrome.
- **Exempt from 1.4.3:** text in logos/brand names, disabled controls, purely decorative text, text baked into a photo where the presentation is essential.

**Use of color — SC 1.4.1 (A):** color is never the only signal. Errors, required fields, chart series, statuses, and inline links each need a second cue (icon, underline, text, pattern). Inline links in body text: **underline them** (the non-color cue settles it) — or, if you distinguish them by color alone, give them **≥ 3:1 contrast vs the body text** *plus* a non-color distinction on hover/focus.

**The math (implement it; don't trust a library blindly):** contrast ratio = `(L_lighter + 0.05) / (L_darker + 0.05)`, range 1:1 → 21:1, where `L` is relative luminance. The `+0.05` flare term is why WCAG 2 overstates contrast at the dark end.

**Tooling:** WebAIM Contrast Checker; Chrome/Firefox DevTools color picker (live AA/AAA pass); axe-core in CI (exact command in the gate below).

**APCA is not in WCAG 3.** It was removed from the draft in **July 2023** under the AGWG's automatic-removal rule for exploratory content that does not advance within six months, and the **WCAG 3.0 Working Draft of 3 March 2026** does not mention it — that draft states no contrast algorithm has been chosen, carries no Bronze/Silver/Gold model, and gives no timeline to Recommendation. **Gate on WCAG 2 ratios only. Compute APCA Lc as an advisory** — it is the better predictor on dark surfaces and for small or light-weight type — **and never let an Lc pass override a WCAG 2 failure.** Reference constants (0.98G-4g): `mainTRC 2.4`, `normBG 0.56` / `normTXT 0.57` (dark-on-light), `revBG 0.65` / `revTXT 0.62` (light-on-dark), `blkThrs 0.022`, `blkClmp 1.414`, `scale 1.14`; output **Lc −108 … +106**, sign = polarity. **No W3C document specifies an Lc threshold** — there is no Lc number you can gate on, so do not write one down. Two structural disagreements with WCAG 2 say where the advisory is worth reading: WCAG 2 is polarity-blind (white-on-black and black-on-white return the identical ratio), and its `+0.05` flare term overstates contrast near black — exactly where dark themes live.

---

## 2. Focus visibility (SC 2.4.7 AA required; 1.4.11 AA; 2.4.13 AAA = the good spec)

**Never remove focus without replacing it.** `:focus { outline: none; }` alone violates 2.4.7.

Ship **one focus token, everywhere**, baked into the base stylesheet — not per-component. This kills the single most common AA failure.

```css
:focus-visible {
  outline: 2px solid var(--color-ring); /* 3px is safer for area */
  outline-offset: 2px;                          /* separates ring from the edge */
}
/* Fallback for browsers without :focus-visible */
@supports not selector(:focus-visible) {
  :focus { outline: 2px solid var(--color-ring); outline-offset: 2px; }
}
/* Windows High Contrast / forced colors */
@media (forced-colors: active) {
  :focus-visible { outline: 2px solid CanvasText; }
}
```

Rules:
- **Use `:focus-visible`, not `:focus`** — mouse clicks don't show the ring, keyboard/AT users do. **Baseline: widely available since March 2022.** One heuristic surprises people: a **mouse click into a text input *does* match `:focus-visible`** (buttons and links do not), because the user needs to see where typing will land. Programmatic `element.focus()` is user-agent dependent — which is why the APG has you focus a *static* element when a dialog opens instead of relying on the ring (§5).
- **Use `outline`, not `border`/`box-shadow` alone** — outline doesn't shift layout, respects `border-radius`, and survives forced-colors mode. `box-shadow` rings vanish inside cards/modals/overflow-clipped containers — and `contain: paint` (so also `content-visibility: auto`) "acts like `overflow: hidden` for visual rendering", clipping them identically. **Inside a virtualised or containment-optimised list, `outline` is the only layer that survives** (→ `performance.md` §5).
- **`outline-offset: ~2px`** for breathing room (outline is outside the box model, so no layout shift).
- **Dashed/dotted outlines: double the thickness to 4px** — the gaps eat into the required area.
- **Do NOT transition `outline`** — it should snap on focus. Transition only background/border/color (e.g. `transition: background-color 120ms ease`).
- **Light up the container, not just the control,** where a group should read as focused: `.field-group:has(:focus-visible) { border-color: var(--color-ring); }`.

**Resolved conflict — do not "fix" this back.** The Web Interface Guidelines (`raunofreiberg/interfaces`) recommend `box-shadow` for focus rings on the grounds that `outline` ignores `border-radius`. That stopped being true in current browsers, and `box-shadow` is dropped entirely in forced-colors mode. **We use `outline` + `outline-offset`.**

**Contrast-proof ring (works on any background):** two-color "focus-ring sandwich" — solid dark outline + white halo (keep the two layers ≥ 9:1 with each other so one always beats the background):
```css
:focus-visible { outline: 3px solid black; box-shadow: 0 0 0 6px white; }
```
Provide `ring.color.onAccent` / `ring.color.onDanger` variants so a ring on a colored button switches to a contrasting color. **Browser default rings are not conformant — always replace them.** (The often-repeated "Safari's pink ring is ~2.1:1" has no primary source — *unverified*; the instruction stands without the number.)

**shadcn/ui v4 recipe (crisp border + soft halo):**
```
focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]
```
Invalid state swaps colors: `aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40`.
**Tailwind's `ring-*` *is* `box-shadow`, so this halo is the decorative layer, never the load-bearing one.** The conformance indicator is the `outline` token above; the shadcn ring sits on top of it and must be treated as absent wherever `contain: paint`, `content-visibility: auto`, an `overflow: hidden` ancestor, or forced-colors mode is in play.
**Tailwind v4 gotcha: use `outline-hidden`, not `outline-none`, as the reset.** `outline-none` sets `outline-style:none`, which also removes the forced-colors-mode outline. (shadcn's own registry is still inconsistently migrated — issue #10101.)

**Focus Appearance measurable spec (SC 2.4.13, AAA — use as the design target):** the indicator's contrasting area must be ≥ the area of a **2 CSS px thick perimeter** of the component (≈ `4×width + 4×height` px — a 150×75 button needs ≈ 900 px²; a solid 2px outline satisfies it), with **≥ 3:1 between the focused and unfocused states** of the same pixels.

Understanding 2.4.13's own worked example: a **90 × 30 px** button needs `(92 × 32) − (88 × 28) = 480 px²` — the +2/−2 terms cancel, which is why the shorthand is exactly `4W + 4H`. **An outset or boundary-aligned 2px ring passes; an *inset* ring at 2px fails and must be ≥ 3px** — inset 2px on that button covers `90·30 − 86·26 = 464 px²` < 480, inset 3px covers 684 px². So the moment you reach for `outline-offset: -2px`, an inset `box-shadow`, or a border-based ring to dodge clipping, bump it to **3px**.

**2.4.13 and 1.4.11 are different measurements and both apply:** 2.4.13 measures the **contrast change between the focused and unfocused states of the same pixels**; 1.4.11 measures **adjacent contrast within one state**. A ring that appears where nothing was before clears the 2.4.13 leg trivially; a ring that merely darkens an existing border usually does not.

**Focus Not Obscured — SC 2.4.11 (AA):** a focused control must be at least partly visible — never fully covered by sticky headers/footers/cookie banners. Fix with `scroll-padding` (technique C43) equal to the sticky-bar height:
```css
html { scroll-padding-top: 4rem; scroll-padding-bottom: 4rem; }
```
AA allows **partial** obscuring; the named failure is **F110**, a sticky header or footer *completely* hiding the focused element. Two exceptions: content the **user** opened may cover the focused component as long as the user can reveal it without advancing focus (an open dropdown over its own trigger is fine), and for user-movable content "only the initial positions … are considered for testing and conformance" — a panel the user dragged over the ring is not your failure.

---

## 3. Keyboard operability (SC 2.1.1 A, 2.1.2 A, 2.4.3 A, 2.4.1 A)

- **2.1.1 Keyboard (A):** every action works with the keyboard alone. Native `<button>`, `<a href>`, `<input>`, `<select>` give Enter/Space activation and Tab focus for free.
- **2.1.2 No Keyboard Trap (A):** focus can always leave via Tab/Shift+Tab/Esc. Modals trap focus *inside while open*, then **release and restore focus to the trigger on close**. **Implement the trap via `inert` on the background (`<main inert>`) or native `<dialog>`+`showModal()`** — both give a browser-guaranteed trap + Escape, unlike fragile hand-rolled focus JS. shadcn Dialog (Radix) already ships trap + Escape + scroll-lock.
- **2.4.3 Focus Order (A):** DOM/tab order matches visual reading order. Avoid positive `tabindex`; use `tabindex="0"` to add and `tabindex="-1"` to remove from the tab flow.
- **2.4.1 (A):** a **"Skip to main content"** link is the first focusable element.
- **Roving tabindex** for composite widgets (menus, tabs, radio groups, toolbars, grids): one item `tabindex="0"`, the rest `-1`, arrow keys move the `0`, Tab exits the group (per WAI-ARIA APG). **Radix Tabs/DropdownMenu/RadioGroup implement this already — use them; never `map` a set of plain `<button>`s and hope Tab does the right thing (it won't — every button becomes its own tab stop).**
- Interactive elements built from `<div>`/`<span>` must add `role`, `tabindex="0"`, AND keydown handlers for **both Enter and Space**. Prefer native elements and avoid all of this.

**Expected keys (APG):** Buttons = Enter + Space · Links = Enter · Checkbox/Switch = Space · Radio group = arrows · Tabs = arrows + Home/End · Menu = arrows + Esc · Dialog = Esc to close · Combobox = arrows + Enter + Esc.

---

## 4. Target / hit size (SC 2.5.8 AA; 2.5.5 AAA; 2.5.7 AA; 2.5.1 A)

- **SC 2.5.8 Target Size Minimum (AA): ≥ 24×24 CSS px** — and it is an **inscribed-square test, not a bounding-box test**: "it must be conceptually possible to draw a solid 24 by 24 CSS pixel square, aligned to the horizontal and vertical axis such that the square is completely within the target."
- **Consequence for round targets:** the largest axis-aligned square inside a circle of diameter *d* has side *d*/√2, so a circular button needs **d ≥ 34 px** to pass on size alone. In Tailwind, `size-9` (36px) passes; **`size-6` (24px) and `size-8` (32px) do not.** Default every `rounded-full` icon button to `size-9`, and `size-11` (44px) where touch is primary. This is the highest-frequency 2.5.8 defect in generated shadcn UI — avatar menus, close buttons, toolbar icons.
- **SC 2.5.5 Target Size Enhanced (AAA): ≥ 44×44 CSS px.** Ship 44–48px for primary/mobile targets. The widely-quoted **Apple HIG 44 pt** and **Material 48 dp** stay as design targets, annotated: *vendor guidance; both sites are client-rendered and neither number could be machine-verified. The enforceable numbers are WCAG's 24 (AA) and 44 (AAA).*
- **Spacing exception (2.5.8), stated exactly:** an undersized target passes if 24px-diameter circles centred on the **bounding box of each** undersized target do not intersect another target or another such circle ⇒ **≥ 24 px centre-to-centre**. Do not approximate this as a gap: two 12px targets with a 6px gap are 18px apart and fail.
- **Exceptions:** inline links inside a sentence; an equivalent ≥24px control exists elsewhere; browser-default sizing; essential/legally-required.
- **Practical defaults:** buttons `min-height: 44px`; icon buttons 44×44 (24px glyph + padding); list rows ≥ 44px; **≥ 24px centre-to-centre** between adjacent small controls.
- **Input font-size ≥ 16px** — smaller triggers iOS Safari auto-zoom on focus.

**SC 2.5.7 Dragging Movements (AA):** every drag (sliders, reorder, kanban, map pan) needs a single-pointer non-drag alternative unless dragging is essential. **Keyboard access does not satisfy it** — 2.1.1 independently requires keyboard equivalents, but 2.5.7 additionally requires a path operable by pointer click/tap with no keyboard dependency, so a drag handle with arrow-key support still fails. Canonical alternatives from the Understanding doc: slider → click anywhere on the track; carousel → prev/next buttons; kanban → tap the card, then an arrow/move button; colour wheel → click a position; rectangle → click two opposite corners. **SC 2.5.1 Pointer Gestures (A):** no path-based or multipoint gesture without a single-pointer alternative. 2.5.1 covers *path-based* gestures where direction matters and 2.5.7 covers grab-and-move where it does not — a kanban board is subject to both.

---

## 5. ARIA essentials — the rules that prevent damage

**The four rules of ARIA** (W3C *Using ARIA* — a **Discontinued Draft, 24 Feb 2026**, superseded by the APG; the rules are kept for reference):
1. **Use native HTML first.** "If you *can* use a native HTML element or attribute with the semantics and behavior you require **already built in** … **then do so**."
2. **"Do not change native semantics, unless you really have to"** (no `role="button"` on a `<button>`, no `role="heading"` on `<h2>`).
3. **"All interactive ARIA controls must be usable with the keyboard"** (§3). ARIA adds *semantics only* — never behavior, focusability, or key handling.
4. **"Do not use `role="presentation"` or `aria-hidden="true"` on a *focusable* element"** — it creates a control AT can't perceive but keyboard can reach.

**Every interactive element needs an accessible name** (visible label, `aria-label`, or `aria-labelledby`). That is **SC 4.1.2 (A)** — a hard requirement, but *not* one of the rules of ARIA. Do not cite it as the fifth.

**No ARIA is better than bad ARIA** (APG *Read Me First*): "Incorrect ARIA misrepresents visual experiences, with potentially devastating effects on their corresponding non-visual experiences." · "Unlike HTML input elements, ARIA roles do not cause browsers to provide keyboard behaviors or styling." · **"A role is a promise"** — adopting a role obligates you to every keyboard interaction it implies, so a `<nav>` of links wearing `role="menu"` without arrow keys, typeahead, Home/End, Escape and roving tabindex is bad ARIA by definition. Evidence: WebAIM Million, Feb 2026 — pages with ARIA averaged **59.1** detected errors vs **42** without, across **133** ARIA attributes per page (up 27% in a year). WebAIM calls it correlation, not causation; it is still the right prior for a generator.

**Naming:** `aria-label` (invisible name, e.g. icon-only `<button aria-label="Close">`) · `aria-labelledby="id"` (point to visible text, e.g. dialog title → dialog) · `aria-describedby="id"` (supplementary help/error, announced after the name).

**State/property (keep in sync with the visual state via JS):** `aria-expanded` (disclosures/accordions/menus/comboboxes) · `aria-controls` (trigger → region) · `aria-current="page|step|true"` (nav/breadcrumb/stepper) · `aria-pressed` (toggle buttons) · `aria-checked` (custom checkbox/switch/radio) · `aria-disabled="true"` (custom controls — note: still focusable, unlike `disabled`) · `aria-selected` (tabs/options) · `aria-haspopup`.

**Combobox — the ARIA 1.2 shape, and the most botched pattern in generated code:** `role="combobox"` goes **on the `<input>`**, never on a wrapper. Always present: `aria-expanded` (`false`/`true`), `aria-controls` → the popup's id (valid even while the popup is hidden), `aria-autocomplete` (`none` | `list` | `both`). `aria-haspopup` only when the popup is `grid`/`tree`/`dialog` — `listbox` is implicit. **DOM focus never leaves the input**; move AT focus with `aria-activedescendant` (dragging real focus into the list is the classic generated bug — it breaks typing). Legacy tells to reject on sight: **`aria-owns`** (the ARIA 1.0 shape) and `role="combobox"` on a wrapping `<div>` (the ARIA 1.1 shape). Keys: ↓ into the popup · ↑ last item · Alt+↓ open without moving focus · Alt+↑ close and return · Esc close · Enter accept.

**Dialog — `aria-modal`, and where initial focus lands:** `alertdialog` is reserved for "dialogs that divert users' attention to a brief, important message" (a destructive confirm); a settings or form modal is `dialog`. Set `aria-modal="true"` only when **both** hold — code prevents all interaction outside **and** styling obscures the outside; prefer `inert` / `<dialog>.showModal()`, because browser-enforced beats AT-interpreted. Label with `aria-labelledby` → the visible title, and **omit `aria-describedby`** when the body holds lists, tables, or multiple paragraphs (flattening them into one description string destroys the structure). **Initial focus, in priority order:** complex content → a `tabindex="-1"` static element at the top · large dialog → a static title/paragraph so it does not scroll on open · **irreversible action → the *least* destructive button** · simple dialog → the most-used control. Never autofocus the destructive button. On close, restore focus to the invoker unless it no longer exists or the workflow implies a better target (the first cell of a newly added row).

**Live regions — SC 4.1.3 Status Messages (AA):** announce dynamic changes (toasts, "3 results", async validation, cart count) without moving focus. Ship **exactly two singletons in the app shell**: one `role="status"` / `aria-live="polite"` (non-urgent, waits for a pause) and one `role="alert"` / `aria-live="assertive"` (urgent, interrupts — use sparingly). The region must exist in the DOM **before** content is injected; `aria-atomic="true"` re-reads the whole region. Never park a live region inside a virtualised list: off-screen `content-visibility: auto` content stays in the accessibility tree, so it will still announce (→ `performance.md` §5).

**Structure — SC 1.3.1 (A) / 4.1.2 (A):** real headings (`<h1>`–`<h6>`, one `h1`, no skipped levels); landmarks (`<header>/<nav>/<main>/<footer>` or roles); `<ul>/<ol>` for lists; `<table>` + `<th scope>` for data tables; `<fieldset>` + `<legend>` for grouped controls.

**Consistent Help — SC 3.2.6 (A):** if any of *human contact details · human contact mechanism · self-help option · fully automated contact mechanism* repeats across pages, it must "occur in the same order relative to other page content." The test is **serialized DOM order**, not visual position — a support link that is 3rd in the footer on one page and 1st on another fails even though both render bottom-right. Rule: the help affordance lives in exactly one shared layout slot, never rendered per-page.

---

## 6. Reduced motion (SC 2.3.3 AAA, 2.2.2 A, 2.3.1 A) — treat as baseline

Respecting the OS setting is cheap and expected even though 2.3.3 is only AAA. Motion (parallax, big slides, zoom transitions, autoplaying carousels) triggers vestibular nausea/dizziness, migraine, and scotopic sensitivity.

Ship the global reset **by default**, then opt individual animations back in under `no-preference` — motion becomes progressive enhancement:
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
@media (prefers-reduced-motion: no-preference) {
  .panel { transition: transform .3s ease; }
}
```

- **"Reduce" means reduce, not remove.** Under `reduce`, swap transform/translate/scale motion for a **cross-fade** (opacity/color) — keep the comprehension cue, kill the movement. Immediate feedback is non-negotiable (a tap with no response feels broken).
- **SC 2.2.2 Pause/Stop/Hide (A):** any auto-moving/blinking/scrolling content running > 5s alongside other content needs a pause/stop/hide control (carousels, marquees, auto-advancing).
- **SC 2.3.1 (A):** no content flashes more than **3 times per second** (seizure risk).
- Keep interactive UI motion **< 300ms** (perceived-instant ≈ 180ms).
- **The CSS media query does NOT catch JS-driven transforms.** The global `@media (prefers-reduced-motion: reduce)` reset only touches CSS `animation`/`transition`/`scroll-behavior` — it does nothing to Framer Motion, GSAP, `requestAnimationFrame` loops, or WAAPI, which write `transform` directly. **Also gate those in JS**: read `window.matchMedia('(prefers-reduced-motion: reduce)').matches`, or Framer's `useReducedMotion()` to drop the translate/scale while keeping the fade (`const closedX = reduce ? 0 : '-100%'`). (→ references/motion.md §11 for the "reduce, don't delete" pattern and the `motion-reduce:` / `motion-safe:` Tailwind variants; §13 is the runnable animation-review gate.)
- **The View Transitions API does not auto-respect it either, and the kill switch is CSS — not `skipTransition()`.** That call "never prevents updateCallback being called", so it is not a cancel. Override the pseudo-elements under the reduce query — the **group** as well as old/new, with `!important` to beat the UA sheet's inherited animations:
  ```css
  @media (prefers-reduced-motion: reduce) {
    ::view-transition-group(*),
    ::view-transition-old(*),
    ::view-transition-new(*) { animation: none !important; }
  }
  ```
  React does not ship this for you. (→ references/motion.md §11.2.)

---

## 7. Forms — labels, instructions, errors (SC 3.3.1 A, 3.3.2 A, 3.3.3 AA, 3.3.4 AA, 2.5.3 A, 1.3.5 AA)

**Labels — SC 3.3.2 (A):** every field has a programmatic label via `<label for="id">` (or wrap). **Placeholder text is NOT a label** (disappears on input, low contrast, not reliably read).
- Mark required fields both visually and programmatically. **Prefer the word "(optional)" on the minority of optional fields over an asterisk** (GOV.UK: do not mark mandatory fields with asterisks). If you use `*`, add a legend "* = required" and `aria-required="true"`.
- **SC 2.5.3 Label in Name (A):** the accessible name must *contain* the visible text (so voice-control "click Submit" works). Never let `aria-label` contradict the visible label.
- **SC 1.3.5 Identify Input Purpose (AA):** use correct `autocomplete` tokens (`name`, `email`, `tel`, `street-address`, `cc-number`, `current-password`/`new-password`, `one-time-code`) and correct `type`/`inputmode`.

**Error identification — SC 3.3.1 (A):** on validation failure, identify the field AND describe the error **in text** (not color/icon alone). **Error suggestion — SC 3.3.3 (AA):** when you know the fix, state it ("Date must be MM/DD/YYYY"). Never rely on `:invalid` styling alone; never block paste in email/password fields (§7a — that one is an AA failure, not a style note).

**Validation timing — validate on blur, not per-keystroke.** Firing an error on every keystroke fights the user mid-entry (it flags "invalid email" while they're still typing the domain) and, on a live region, spams the screen reader. Validate `onBlur`, then re-validate on change *only once a field is already in the error state* so the message clears as they fix it. **Exception: password-strength meters and character counters** update live by design. Place the error message **directly below the field** and wire it with `aria-describedby` so it's announced with the input (the canonical block below does this).

**Canonical accessible error field (satisfies 3.3.1 / 3.3.2 / 3.3.3 / 4.1.3 in one block):**
```html
<label for="email">Email</label>
<input id="email" type="email" name="email"
       autocomplete="email" required
       aria-describedby="email-err" aria-invalid="true">
<p id="email-err" role="alert">Enter a valid email, e.g. name@example.com</p>
```
- Set `aria-invalid="true"` **only** on fields actually in error; remove it once fixed.
- Link the message with `aria-describedby` so it's read with the field.
- **On submit-with-errors:** move focus to the first invalid field (or an error-summary block whose entries are links that jump to each field), announce a count via a live region, and prefix the page `<title>` with "Error:".
- Error copy formula (GOV.UK): empty → "Enter your X"; constraint → "X must be [rule]"; format → "Enter a X in the correct format, like [example]." Banned words: please / sorry / valid / invalid / oops / forgot / illegal.

**Error prevention — SC 3.3.4 (AA):** legal/financial/data-deletion actions must be **Reversible, Checked (validated), or Confirmed** (review step / "are you sure?"). **Redundant Entry — SC 3.3.7 (A):** within one flow, auto-populate or let users pick previously entered data ("billing same as shipping").

---

## 7a. Authentication (SC 3.3.8 AA)

**SC 3.3.8 Accessible Authentication (Minimum) — AA.** No cognitive function test — "a task that requires the user to remember, manipulate, or transcribe information" — is required at any step of an authentication process, unless that step offers one of four exceptions: an **Alternative** method, a **Mechanism** that helps complete the test, **Object Recognition**, or **Personal Content**.

The consequences are concrete and greppable:
- **Never block paste** on a password or OTP field, and never script around password managers or autofill. Quoted: "Copy and paste can be relied on to avoid transcription"; blocking it "would fail this criterion unless an alternative is provided."
- **Never split an OTP into N single-character inputs.** It defeats paste and `autocomplete="one-time-code"`. Ship one `<input>` for the whole code.
- A puzzle CAPTCHA with no non-cognitive alternative fails.
- Ship `autocomplete="current-password"` / `"new-password"` / `"one-time-code"` and let the browser do the transcription.

---

## 8. Layout / zoom resilience (SC 1.4.4 AA, 1.4.10 AA, 1.4.12 AA, 1.4.13 AA)

- **1.4.4 Resize Text (AA):** usable at **200%** text zoom with no clipping/overlap/loss. Use `rem`/`em`, not fixed `px` heights on text containers.
- **1.4.10 Reflow (AA):** no horizontal scroll or content loss at **320 CSS px** width (= a 1280px viewport at **400%** zoom). Single-column, responsive. Two-dimensional scroll only where essential (data tables, maps, code).
- **1.4.12 Text Spacing (AA):** no loss when users override to line-height **1.5×**, paragraph spacing **2×**, letter-spacing **0.12em**, word-spacing **0.16em**. Avoid fixed-height text boxes with `overflow: hidden`.
- **1.4.13 Content on Hover or Focus (AA):** tooltips/popovers must be **Dismissible** (Esc without moving the pointer), **Hoverable** (pointer can move onto them), and **Persistent** (stay until dismissed or focus moves). No pure-CSS `:hover` tooltips that vanish.

---

## 9. Screen-reader test matrix

WebAIM Screen Reader User Survey #10 (Dec 2023 – Jan 2024, n = 1,539):

| Primary desktop reader | Share | Most common reader + browser | Share |
|---|---|---|---|
| JAWS | **40.5%** | JAWS + Chrome | **24.7%** |
| NVDA | **37.7%** | NVDA + Chrome | **21.3%** |
| VoiceOver | **9.7%** | JAWS + Edge | 11.4% |
| SuperNova 3.7 · ZoomText/Fusion 2.7 · Orca 2.4 · Narrator 0.7 · other 2.7 | 12.2% | NVDA + Firefox · VoiceOver + Safari | 10.0% · 7.0% |

**91.3% also use a screen reader on mobile** (iOS 70.6%, Android 27.6%); only 40.2% are desktop-mostly.

**Minimum honest matrix: NVDA + Chrome on Windows, and VoiceOver + Safari on iOS.** VoiceOver on macOS is the only reader most engineers on Macs ever touch and it validates **under 10%** of desktop users, while JAWS+NVDA on Chromium is 46% in two combinations.

The APG's own position: "Testing assistive technology interoperability is essential before using code from this guide in production," and "Some ARIA features are not supported in any mobile browser." A pattern being in the APG is not evidence that it works. Per-AT bug lists are deliberately absent from this file — no primary source for them was reachable, and the matrix is the honest substitute.

---

## The gate — pre-ship checklist (the skill runs this)

**Run the automated half first — it is a handful of commands, and 95.9% of home pages fail even that bar.** Automated tools catch the six failure classes at the top of the WebAIM Million list (low-contrast text 83.9% · missing alt 53.1% · missing form labels 51% · empty links 46.3% · empty buttons 30.6% · missing document language 13.5%) and **essentially nothing** about focus craft, ARIA correctness, or announcement behaviour. Commands below assume the app is served at `http://localhost:3000`.

| Automatable check | SC | Command | What it cannot catch |
|---|---|---|---|
| Contrast, accessible names, labels, alt, `lang`, invalid ARIA | 1.4.3, 1.1.1, 3.3.2, 4.1.2, 3.1.1 | `npx @axe-core/cli http://localhost:3000 --tags wcag2a,wcag2aa,wcag21aa,wcag22aa --exit` | text over images/gradients/video (reported *incomplete*, not fail); non-default states (hover/focus/disabled/checked); whether the alt text means anything |
| Target size ≥ 24×24 | 2.5.8 | `npx @axe-core/cli http://localhost:3000 --rules target-size --exit` — **`target-size` is off by default in axe-core**, so a plain `--tags wcag22aa` run never checks it | the inscribed-square rule for round targets; boundary cases of the centre-to-centre maths |
| Landmarks, heading order, skip link | 1.3.1, 2.4.1 | `npx @axe-core/cli http://localhost:3000 --tags best-practice --exit` — `region`, `landmark-one-main`, `heading-order`, `bypass` sit under `best-practice`, **not** `wcag2aa` | whether the heading text describes its section |
| Static JSX a11y at build time | many | `npx eslint . --ext .ts,.tsx` with `eslint-plugin-jsx-a11y`, **explicitly enabling the non-recommended** `no-aria-hidden-on-focusable`, `control-has-associated-label`, `anchor-ambiguous-text`, `prefer-tag-over-role`, `lang` | anything runtime — computed contrast, focus order, live-region behaviour |
| Positive `tabIndex` | 2.4.3 | jsx-a11y `tabindex-no-positive` + `grep -rn 'tabIndex={[1-9]' src/` | order broken by CSS (`order`, `grid-area`, `row-reverse`) |
| `outline-none` misuse | 2.4.7 | `grep -rn '\boutline-none\b' src/` — v4's reset is `outline-hidden` | — |
| A ring exists on every interactive element | 2.4.7 | Playwright: loop `page.keyboard.press('Tab')`, read `getComputedStyle(document.activeElement)`, assert `outlineStyle !== 'none' && parseFloat(outlineWidth) > 0` | the ring's 3:1 contrast, and the 2.4.13 area maths |
| Reflow at 320px | 1.4.10 | Playwright `page.setViewportSize({width:320,height:256})`, then assert `document.documentElement.scrollWidth <= 320` | content present but unusable (overlap, clipping) |
| Text-spacing override | 1.4.12 | Playwright `page.addStyleTag` injecting `* { line-height:1.5 !important; letter-spacing:.12em !important; word-spacing:.16em !important } p { margin-bottom:2em !important }`, then the same assertion | subtle overlap that does not overflow |
| Reduced-motion reset present | 2.3.3 | `grep -rq 'prefers-reduced-motion' src/ \|\| echo MISSING` | whether JS/Framer/GSAP transforms are actually gated |

**Human checks — no tool implements these. A green axe run does not tick any of them:** whether the ARIA describes what is on screen ("a role is a promise") · focus **order** vs visual reading order (2.4.3) · focus-indicator **area** ≥ 4W+4H and the 3:1 focused-vs-unfocused change (2.4.13 — pixel measurement across two rendered states) · non-text contrast of borders, toggles, rings and icons **in every state** (1.4.11 — axe has no rule and the crawler never renders the states) · focus not obscured by sticky UI (2.4.11) · dialog initial-focus target and restoration · a live region actually announcing (4.1.3 — only real AT confirms it) · keyboard-trap escape (2.1.2) · drag alternatives **by pointer**, not keyboard (2.5.7) · Consistent Help ordering across pages (3.2.6) · paste and autofill not blocked in auth (3.3.8) · error wording and suggestion quality (3.3.1 / 3.3.3) · meaningful alt text (1.1.1) · screen-reader output on the §9 matrix. Do not report any of these as passing unless a human ran them.

- [ ] **Contrast:** text ≥ 4.5:1 (≥ 3:1 for ≥24px / ≥18.66px-bold); UI/icon borders and focus rings ≥ 3:1 in every state. (1.4.3, 1.4.11)
- [ ] **No color-only signals;** inline links have a non-color cue and ≥ 3:1. (1.4.1)
- [ ] **Visible `:focus-visible` ring** on every interactive element — `outline` + `outline-offset`, ≥ 3:1, never `outline:none` alone; Tailwind reset is `outline-hidden`. (2.4.7, 1.4.11, 2.4.13)
- [ ] **Focus never fully hidden** by sticky UI (`scroll-padding`). (2.4.11)
- [ ] **Full keyboard operation:** logical tab order, no traps, skip link first, Esc closes overlays, focus restored on modal close. (2.1.1, 2.1.2, 2.4.3, 2.4.1)
- [ ] **Targets ≥ 24×24px** — **≥ 34px diameter if circular** (inscribed square: `size-9`, not `size-8`) — aim 44×44 for touch/primary; otherwise ≥ 24px **centre-to-centre**; input font ≥ 16px. (2.5.8, 2.5.5)
- [ ] **Every drag has a single-pointer non-drag alternative** — keyboard support does not count; no path/multipoint-only gestures. (2.5.7, 2.5.1)
- [ ] **Native HTML first;** ARIA only fills gaps; every control has an accessible name; visible label ⊆ accessible name; combobox role on the `<input>` with `aria-activedescendant`, dialog initial focus never on the destructive button. (4.1.2, 2.5.3)
- [ ] **Dynamic updates announced** via the two live-region singletons (`role="status"` / `role="alert"`). (4.1.3)
- [ ] **`prefers-reduced-motion: reduce` honored** (global CSS reset, motion opted back in under `no-preference`) **AND JS/Framer transforms gated with `useReducedMotion()`** — the media query alone misses them; auto-motion > 5s has pause; nothing flashes > 3×/sec. (2.3.3, 2.2.2, 2.3.1) (→ motion.md §13)
- [ ] **Every field labeled** (`<label>`, not placeholder); **validate on blur, not per-keystroke** (except strength meters); errors in text below the field + `aria-invalid` + `aria-describedby`; focus moves to first error; page title prefixed "Error:". (3.3.1, 3.3.2, 3.3.3)
- [ ] **Correct `autocomplete`/`type`/`inputmode`;** destructive/legal actions reversible or confirmed; no re-entry of prior data. (1.3.5, 3.3.4, 3.3.7)
- [ ] **Auth blocks nothing:** paste allowed on password/OTP, password managers and autofill unimpeded, OTP is one input, no cognitive-test-only CAPTCHA. (3.3.8)
- [ ] **Help lives in one shared layout slot,** in the same DOM position on every page. (3.2.6)
- [ ] **Works at 200% text zoom, reflows at 320px / 400%,** survives text-spacing overrides; tooltips dismissible + hoverable + persistent. (1.4.4, 1.4.10, 1.4.12, 1.4.13)

**Enforce as tokens + CI, not a wiki:** bake the focus token into the base stylesheet; encode contrast (4.5 text / 3.0 large & UI) and target (24 min / 34 circular / 44 recommended) as design-system tokens; ship the reduced-motion reset globally; make `aria-label` on icon-only buttons and `aria-expanded`+`aria-controls` on disclosures **required props (TS types)**; run the axe and eslint commands in the table above in CI. Every `role=`/`tabindex` in a PR is a code-review flag.

---

## Sources (primary first)

- W3C — What's New in WCAG 2.2: https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/
- W3C — WCAG 2.2 Recommendation: https://www.w3.org/TR/WCAG22/
- W3C Understanding 2.5.8 Target Size (Minimum): https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
- W3C Understanding 2.4.13 Focus Appearance: https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html
- W3C Understanding 2.4.11 Focus Not Obscured (Minimum): https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html
- W3C Understanding 2.4.7 Focus Visible: https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html
- W3C Understanding 2.5.7 Dragging Movements: https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html
- W3C Understanding 3.2.6 Consistent Help: https://www.w3.org/WAI/WCAG22/Understanding/consistent-help.html
- W3C Understanding 3.3.8 Accessible Authentication (Minimum): https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html
- W3C Technique C39 (prefers-reduced-motion): https://www.w3.org/WAI/WCAG21/Techniques/css/C39
- W3C Technique ARIA21 (aria-invalid): https://www.w3.org/WAI/WCAG21/Techniques/aria/ARIA21
- W3C — Using ARIA (Discontinued Draft, 24 Feb 2026 — the four rules): https://www.w3.org/TR/using-aria/
- W3C ARIA APG — Read Me First ("no ARIA is better than bad ARIA", "a role is a promise"): https://www.w3.org/WAI/ARIA/apg/practices/read-me-first/
- W3C ARIA APG — Combobox pattern: https://www.w3.org/WAI/ARIA/apg/patterns/combobox/
- W3C ARIA APG — Modal Dialog pattern: https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/
- W3C — WCAG 3.0 Working Draft, 3 March 2026 (no contrast algorithm chosen): https://www.w3.org/TR/wcag-3.0/
- Myndex — apca-w3 reference implementation (0.98G-4g constants): https://github.com/Myndex/apca-w3
- MDN — ARIA guides/techniques (live regions): https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Guides/Techniques
- MDN — contain (`paint` "acts like `overflow: hidden` for visual rendering"): https://developer.mozilla.org/en-US/docs/Web/CSS/contain
- MDN — :focus-visible: https://developer.mozilla.org/en-US/docs/Web/CSS/:focus-visible
- Sara Soueidan — Designing WCAG-conformant focus indicators: https://www.sarasoueidan.com/blog/focus-indicators/
- WebAIM — Contrast and Color Accessibility: https://webaim.org/articles/contrast/
- WebAIM — WCAG 2 Checklist: https://webaim.org/standards/wcag/checklist
- WebAIM Million, Feb 2026 (95.9% failure rate; ARIA 59.1 vs 42 errors): https://webaim.org/projects/million/
- WebAIM Screen Reader User Survey #10: https://webaim.org/projects/screenreadersurvey10/
- GOV.UK Design System — Error message / Error summary: https://design-system.service.gov.uk/components/error-message/
- shadcn/ui — outline-none → outline-hidden issue #10101: https://github.com/shadcn-ui/ui/issues/10101
