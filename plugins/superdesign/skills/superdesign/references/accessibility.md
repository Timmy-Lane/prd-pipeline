# Accessibility Gate — WCAG 2.2 AA

The concrete, buildable subset of WCAG 2.2 Level AA that a generated product UI must pass. Every rule cites its Success Criterion (SC) and level. WCAG 2.2 became a W3C Recommendation on 2023-10-05; Level AA = all A + AA criteria (56 total). The EU Accessibility Act is in force since 2025-06-28, so AA is the de-facto legal floor. **SC 4.1.1 Parsing was removed in 2.2 — do not cite it.**

This file is a gate, not a wiki. The skill runs the checklist at the bottom; the sections above define the exact numbers and the copy-paste primitives that make each check pass by default.

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

**Tooling:** WebAIM Contrast Checker; Chrome/Firefox DevTools color picker (live AA/AAA pass); axe-core in CI. **APCA is the WCAG 3 draft algorithm — not normative. Never ship an AA compliance claim measured against APCA;** use it only for perceptual fine-tuning.

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
- **Use `:focus-visible`, not `:focus`** — mouse clicks don't show the ring, keyboard/AT users do. Safe baseline everywhere 2024–2026.
- **Use `outline`, not `border`/`box-shadow` alone** — outline doesn't shift layout, respects `border-radius`, and survives forced-colors mode. `box-shadow` rings vanish inside cards/modals/overflow-clipped containers.
- **`outline-offset: ~2px`** for breathing room (outline is outside the box model, so no layout shift).
- **Dashed/dotted outlines: double the thickness to 4px** — the gaps eat into the required area.
- **Do NOT transition `outline`** — it should snap on focus. Transition only background/border/color (e.g. `transition: background-color 120ms ease`).

**Contrast-proof ring (works on any background):** two-color "focus-ring sandwich" — solid dark outline + white halo (keep the two layers ≥ 9:1 with each other so one always beats the background):
```css
:focus-visible { outline: 3px solid black; box-shadow: 0 0 0 6px white; }
```
Provide `ring.color.onAccent` / `ring.color.onDanger` variants so a ring on a colored button switches to a contrasting color. **Safari's default pink ring (~2.1:1) fails 1.4.11 — always replace browser defaults.**

**shadcn/ui v4 recipe (crisp border + soft halo):**
```
focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]
```
Invalid state swaps colors: `aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40`.
**Tailwind v4 gotcha: use `outline-hidden`, not `outline-none`, as the reset.** `outline-none` sets `outline-style:none`, which also removes the forced-colors-mode outline. (shadcn's own registry is still inconsistently migrated — issue #10101.)

**Focus Appearance measurable spec (SC 2.4.13, AAA — use as the design target):** the indicator's contrasting area must be ≥ the area of a **2 CSS px thick perimeter** of the component (≈ `4×width + 4×height` px — a 150×75 button needs ≈ 900 px²; a solid 2px outline satisfies it), with **≥ 3:1 between the focused and unfocused states** of the same pixels.

**Focus Not Obscured — SC 2.4.11 (AA):** a focused control must be at least partly visible — never fully covered by sticky headers/footers/cookie banners. Fix with `scroll-padding` (technique C43) equal to the sticky-bar height:
```css
html { scroll-padding-top: 4rem; scroll-padding-bottom: 4rem; }
```

---

## 3. Keyboard operability (SC 2.1.1 A, 2.1.2 A, 2.4.3 A, 2.4.1 A)

- **2.1.1 Keyboard (A):** every action works with the keyboard alone. Native `<button>`, `<a href>`, `<input>`, `<select>` give Enter/Space activation and Tab focus for free.
- **2.1.2 No Keyboard Trap (A):** focus can always leave via Tab/Shift+Tab/Esc. Modals trap focus *inside while open*, then **release and restore focus to the trigger on close**.
- **2.4.3 Focus Order (A):** DOM/tab order matches visual reading order. Avoid positive `tabindex`; use `tabindex="0"` to add and `tabindex="-1"` to remove from the tab flow.
- **2.4.1 (A):** a **"Skip to main content"** link is the first focusable element.
- **Roving tabindex** for composite widgets (menus, tabs, radio groups, toolbars, grids): one tab stop for the group, arrow keys move between items (per WAI-ARIA APG).
- Interactive elements built from `<div>`/`<span>` must add `role`, `tabindex="0"`, AND keydown handlers for **both Enter and Space**. Prefer native elements and avoid all of this.

**Expected keys (APG):** Buttons = Enter + Space · Links = Enter · Checkbox/Switch = Space · Radio group = arrows · Tabs = arrows + Home/End · Menu = arrows + Esc · Dialog = Esc to close · Combobox = arrows + Enter + Esc.

---

## 4. Target / hit size (SC 2.5.8 AA; 2.5.5 AAA; 2.5.7 AA; 2.5.1 A)

- **SC 2.5.8 Target Size Minimum (AA): ≥ 24×24 CSS px.**
- **SC 2.5.5 Target Size Enhanced (AAA): ≥ 44×44 CSS px** — the widely-quoted "44px" (Apple HIG 44pt; Google Material recommends 48dp). Ship 44–48px for primary/mobile targets.
- **Spacing exception (2.5.8):** an under-24px target passes if a 24px-diameter circle centered on it doesn't overlap the circle of any adjacent target (i.e. ≥ 24px center-to-center).
- **Exceptions:** inline links inside a sentence; an equivalent ≥24px control exists elsewhere; browser-default sizing; essential/legally-required.
- **Practical defaults:** buttons `min-height: 44px`; icon buttons 44×44 (24px glyph + padding); list rows ≥ 44px; **≥ 8px gap** between adjacent small controls.
- **Input font-size ≥ 16px** — smaller triggers iOS Safari auto-zoom on focus.

**SC 2.5.7 Dragging Movements (AA):** every drag (sliders, reorder, kanban, map pan) needs a single-pointer non-drag alternative (buttons, tap-to-place, number input) unless dragging is essential. **SC 2.5.1 Pointer Gestures (A):** no path-based or multipoint gesture without a single-pointer alternative.

---

## 5. ARIA essentials — the rules that prevent damage

**The 5 Rules of ARIA (W3C / MDN):**
1. **Use native HTML first.** If a native element gives the role/state/keyboard behavior, use it — don't rebuild it with ARIA.
2. **Don't change native semantics** (no `role="button"` on a `<button>`, no `role="heading"` on `<h2>`).
3. **All interactive ARIA widgets must be keyboard-operable** (§3). ARIA adds *semantics only* — never behavior, focusability, or key handling.
4. **Never put `aria-hidden="true"` or `role="presentation"` on a focusable element** — it creates a control AT can't perceive but keyboard can reach.
5. **Every interactive element needs an accessible name** (visible label, `aria-label`, or `aria-labelledby`).

**Naming:** `aria-label` (invisible name, e.g. icon-only `<button aria-label="Close">`) · `aria-labelledby="id"` (point to visible text, e.g. dialog title → dialog) · `aria-describedby="id"` (supplementary help/error, announced after the name).

**State/property (keep in sync with the visual state via JS):** `aria-expanded` (disclosures/accordions/menus/comboboxes) · `aria-controls` (trigger → region) · `aria-current="page|step|true"` (nav/breadcrumb/stepper) · `aria-pressed` (toggle buttons) · `aria-checked` (custom checkbox/switch/radio) · `aria-disabled="true"` (custom controls — note: still focusable, unlike `disabled`) · `aria-selected` (tabs/options) · `aria-haspopup`.

**Live regions — SC 4.1.3 Status Messages (AA):** announce dynamic changes (toasts, "3 results", async validation, cart count) without moving focus. Ship **exactly two singletons in the app shell**: one `role="status"` / `aria-live="polite"` (non-urgent, waits for a pause) and one `role="alert"` / `aria-live="assertive"` (urgent, interrupts — use sparingly). The region must exist in the DOM **before** content is injected; `aria-atomic="true"` re-reads the whole region.

**Structure — SC 1.3.1 (A) / 4.1.2 (A):** real headings (`<h1>`–`<h6>`, one `h1`, no skipped levels); landmarks (`<header>/<nav>/<main>/<footer>` or roles); `<ul>/<ol>` for lists; `<table>` + `<th scope>` for data tables; `<fieldset>` + `<legend>` for grouped controls.

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
- In JS, read the same preference: `window.matchMedia('(prefers-reduced-motion: reduce)').matches`. The View Transitions API does **not** auto-respect it — call `transition.skipTransition()` when it matches.

---

## 7. Forms — labels, instructions, errors (SC 3.3.1 A, 3.3.2 A, 3.3.3 AA, 3.3.4 AA, 2.5.3 A, 1.3.5 AA)

**Labels — SC 3.3.2 (A):** every field has a programmatic label via `<label for="id">` (or wrap). **Placeholder text is NOT a label** (disappears on input, low contrast, not reliably read).
- Mark required fields both visually and programmatically. **Prefer the word "(optional)" on the minority of optional fields over an asterisk** (GOV.UK: do not mark mandatory fields with asterisks). If you use `*`, add a legend "* = required" and `aria-required="true"`.
- **SC 2.5.3 Label in Name (A):** the accessible name must *contain* the visible text (so voice-control "click Submit" works). Never let `aria-label` contradict the visible label.
- **SC 1.3.5 Identify Input Purpose (AA):** use correct `autocomplete` tokens (`name`, `email`, `tel`, `street-address`, `cc-number`, `current-password`/`new-password`, `one-time-code`) and correct `type`/`inputmode`.

**Error identification — SC 3.3.1 (A):** on validation failure, identify the field AND describe the error **in text** (not color/icon alone). **Error suggestion — SC 3.3.3 (AA):** when you know the fix, state it ("Date must be MM/DD/YYYY"). Never rely on `:invalid` styling alone; never block paste in email/password fields.

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

## 8. Layout / zoom resilience (SC 1.4.4 AA, 1.4.10 AA, 1.4.12 AA, 1.4.13 AA)

- **1.4.4 Resize Text (AA):** usable at **200%** text zoom with no clipping/overlap/loss. Use `rem`/`em`, not fixed `px` heights on text containers.
- **1.4.10 Reflow (AA):** no horizontal scroll or content loss at **320 CSS px** width (= a 1280px viewport at **400%** zoom). Single-column, responsive. Two-dimensional scroll only where essential (data tables, maps, code).
- **1.4.12 Text Spacing (AA):** no loss when users override to line-height **1.5×**, paragraph spacing **2×**, letter-spacing **0.12em**, word-spacing **0.16em**. Avoid fixed-height text boxes with `overflow: hidden`.
- **1.4.13 Content on Hover or Focus (AA):** tooltips/popovers must be **Dismissible** (Esc without moving the pointer), **Hoverable** (pointer can move onto them), and **Persistent** (stay until dismissed or focus moves). No pure-CSS `:hover` tooltips that vanish.

---

## The gate — pre-ship checklist (the skill runs this)

- [ ] **Contrast:** text ≥ 4.5:1 (≥ 3:1 for ≥24px / ≥18.66px-bold); UI/icon borders and focus rings ≥ 3:1 in every state. (1.4.3, 1.4.11)
- [ ] **No color-only signals;** inline links have a non-color cue and ≥ 3:1. (1.4.1)
- [ ] **Visible `:focus-visible` ring** on every interactive element — `outline` + `outline-offset`, ≥ 3:1, never `outline:none` alone; Tailwind reset is `outline-hidden`. (2.4.7, 1.4.11, 2.4.13)
- [ ] **Focus never fully hidden** by sticky UI (`scroll-padding`). (2.4.11)
- [ ] **Full keyboard operation:** logical tab order, no traps, skip link first, Esc closes overlays, focus restored on modal close. (2.1.1, 2.1.2, 2.4.3, 2.4.1)
- [ ] **Targets ≥ 24×24px** (aim 44×44 for touch/primary), or ≥ 24px spacing; ≥ 8px gap between small controls; input font ≥ 16px. (2.5.8, 2.5.5)
- [ ] **Every drag has a non-drag alternative;** no path/multipoint-only gestures. (2.5.7, 2.5.1)
- [ ] **Native HTML first;** ARIA only fills gaps; every control has an accessible name; visible label ⊆ accessible name. (4.1.2, 2.5.3)
- [ ] **Dynamic updates announced** via the two live-region singletons (`role="status"` / `role="alert"`). (4.1.3)
- [ ] **`prefers-reduced-motion: reduce` honored** (global reset, motion opted back in under `no-preference`); auto-motion > 5s has pause; nothing flashes > 3×/sec. (2.3.3, 2.2.2, 2.3.1)
- [ ] **Every field labeled** (`<label>`, not placeholder); errors in text + `aria-invalid` + `aria-describedby`; focus moves to first error; page title prefixed "Error:". (3.3.1, 3.3.2, 3.3.3)
- [ ] **Correct `autocomplete`/`type`/`inputmode`;** destructive/legal actions reversible or confirmed; no re-entry of prior data. (1.3.5, 3.3.4, 3.3.7)
- [ ] **Works at 200% text zoom, reflows at 320px / 400%,** survives text-spacing overrides; tooltips dismissible + hoverable + persistent. (1.4.4, 1.4.10, 1.4.12, 1.4.13)

**Enforce as tokens + CI, not a wiki:** bake the focus token into the base stylesheet; encode contrast (4.5 text / 3.0 large & UI) and target (24 min / 44 recommended) as design-system tokens; ship the reduced-motion reset globally; make `aria-label` on icon-only buttons and `aria-expanded`+`aria-controls` on disclosures **required props (TS types)**; run axe-core in CI. Every `role=`/`tabindex` in a PR is a code-review flag.

---

## Sources (primary first)

- W3C — What's New in WCAG 2.2: https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/
- W3C — WCAG 2.2 Recommendation: https://www.w3.org/TR/WCAG22/
- W3C Understanding 2.5.8 Target Size (Minimum): https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
- W3C Understanding 2.4.13 Focus Appearance: https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html
- W3C Understanding 2.4.11 Focus Not Obscured (Minimum): https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html
- W3C Understanding 2.4.7 Focus Visible: https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html
- W3C Technique C39 (prefers-reduced-motion): https://www.w3.org/WAI/WCAG21/Techniques/css/C39
- W3C Technique ARIA21 (aria-invalid): https://www.w3.org/WAI/WCAG21/Techniques/aria/ARIA21
- MDN — ARIA guides/techniques (rules of ARIA, live regions): https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Guides/Techniques
- MDN — :focus-visible: https://developer.mozilla.org/en-US/docs/Web/CSS/:focus-visible
- Sara Soueidan — Designing WCAG-conformant focus indicators: https://www.sarasoueidan.com/blog/focus-indicators/
- WebAIM — Contrast and Color Accessibility: https://webaim.org/articles/contrast/
- WebAIM — WCAG 2 Checklist: https://webaim.org/standards/wcag/checklist
- GOV.UK Design System — Error message / Error summary: https://design-system.service.gov.uk/components/error-message/
- shadcn/ui — outline-none → outline-hidden issue #10101: https://github.com/shadcn-ui/ui/issues/10101
