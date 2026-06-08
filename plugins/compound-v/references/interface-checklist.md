# Interface Checklist — the named-property vocabulary

The full vocabulary behind **product-taste**'s "name the property" rule: ~50 concrete,
vendor-neutral, copyable interface properties. The SKILL body carries the ~12 most-violated; this
is the long tail — load it on demand when auditing a real interface or when a vague verdict needs
the *specific* rule to name.

Not a skill (no always-on cost), not prose — a checklist you scan against the thing in front of
you. Every item is a **canonical** craft constant or a **judgment** default: these ARE the
properties, not empirical claims about the world, so none carries a per-line citation. The grouping
follows the surfaces behind any polished interface (interactivity, type, motion, touch,
performance, accessibility, design). Source spine: Rauno Freiberg's interface guidelines
(https://github.com/raunofreiberg/interfaces), mapped in `references/sources.md` → product-taste.

How to use: when you can only say "feels off," walk the relevant group, find the violated line,
name it, fix it. A property you can name you can fix and hand off; one you can't, you can't.

---

## Interactivity
- Clicking an input's label focuses the input.
- Inputs are wrapped in a `<form>` so Enter submits.
- Inputs carry the right `type` (`password`, `email`, `tel`, …) for keyboard + validation.
- Disable `spellcheck` / `autocomplete` on inputs where they don't help (names, codes, usernames).
- Use the `required` attribute to get native HTML validation for free.
- Prefix/suffix icons are absolutely positioned over the input with padding (not laid out beside it), and clicking them focuses the input.
- Toggles take effect immediately — no separate confirm step.
- Disable a submit button after submission to prevent duplicate network requests.
- Disable `user-select` on the inner content of interactive elements (so a double-click doesn't select label text).
- Decorative elements (glows, gradients) set `pointer-events: none` so they don't intercept clicks.
- No dead areas between adjacent list items — grow `padding` to fill the gap so the whole row is a hit target. *(also in the SKILL body)*

## Typography
- `-webkit-font-smoothing: antialiased` and `text-rendering: optimizeLegibility` for legibility.
- Subset fonts to the content's alphabet / language to cut weight.
- Font weight must **not** change on hover or when selected — it causes layout shift.
- Avoid font weights below 400; medium headings read best at **500–600**.
- Fluid type with `clamp()` — e.g. `clamp(48px, 5vw, 72px)` for a hero heading.
- `font-variant-numeric: tabular-nums` on tables, timers, and anywhere reflow as digits change is undesirable. *(also in the SKILL body)*
- `16px` minimum input font — anything smaller triggers iOS zoom-on-focus. *(also in the SKILL body)*
- Prevent iOS landscape text inflation with `-webkit-text-size-adjust: 100%`.

## Motion
- Theme switches must not trigger transitions/animations — disable transitions for the swap, then re-enable.
- Interaction animations stay **≤ 200ms** to feel immediate.
- Animation magnitude is proportional to the trigger:
  - Dialogs/popovers scale in from **~0.8, not 0** (0 looks like a glitch); fade opacity alongside. *(SKILL body)*
  - Buttons depress to **~0.96 / ~0.9** on press, never to 0. *(SKILL body)*
- Frequent / low-novelty actions drop the animation — right-click menus, list add/delete, trivial hovers. (An element seen 100+ times a day should *lose* its motion.) *(SKILL body)*
- Looping animations pause when off-screen (saves CPU/GPU). *(SKILL body)*
- `scroll-behavior: smooth` for in-page anchors, with a scroll offset so the target isn't flush to the edge.

## Touch
- Hover states must not fire on touch press — gate them with `@media (hover: hover)`.
- Don't autofocus inputs on touch devices (the keyboard covers the screen).
- `muted` + `playsinline` on `<video>` so it can autoplay on iOS.
- Disable `touch-action` on custom pan/zoom components so native gestures don't fight yours.
- Replace the default iOS tap highlight (`-webkit-tap-highlight-color: transparent`) — but always supply your own press feedback in its place.

## Performance / optimizations
- Animate only `transform` and `opacity` — the GPU composite-only path; layout/color animations force repaints and drop frames. *(SKILL body)*
- Large `blur()` on `filter` / `backdrop-filter` is expensive — use sparingly.
- Scaling or blurring filled rectangles causes banding; use a radial gradient instead.
- Enable GPU rendering deliberately (`transform: translateZ(0)`) only for a genuinely janky animation, not by default.
- Toggle `will-change` only for the *duration* of the janky scroll/animation — leaving it on pre-emptively backfires.
- Pause or unmount off-screen autoplaying videos — too many choke iOS.
- For real-time values that commit straight to the DOM (wheel delta, cursor position), bypass the framework render cycle with a ref.
- Detect and adapt to device hardware / network capability rather than assuming the high end.

## Accessibility
- Disabled buttons don't get tooltips — they're skipped in tab order, so keyboard users never hear the reason. Prefer not fully disabling, or explain elsewhere.
- Use `box-shadow` for focus rings, not `outline` — older Safari versions render `outline` without following `border-radius`. *(this is the slop-fix in the SKILL body)*
- Sequential lists are navigable with ↑ ↓ and deletable with ⌘+Backspace.
- Dropdown menus open on `mousedown`, not `click` — it feels instant.
- Icon-only interactive elements carry an explicit `aria-label`.
- Hover-triggered tooltips contain no interactive content (you can't reach it without dismissing the tooltip).
- Use a real `<img>` (screen-reader + right-click-copy) for content images, not a background image.
- HTML/CSS illustrations get an `aria-label` so screen readers don't announce the raw DOM tree.
- Nested menus need a "prediction cone" — moving the pointer diagonally toward the submenu doesn't close it.
- An SVG favicon with an internal `<style>` can follow `prefers-color-scheme`.
- Unset gradient text on `::selection` (and style `::selection` generally) so highlighted text stays legible.

## Design
- Optimistically update locally and roll back on server error, with feedback — the canonical perceived-speed primitive. *(SKILL latency section)*
- Auth redirects happen on the server before the client loads, to avoid a janky URL flash.
- Display feedback relative to its trigger — a temporary inline checkmark on copy, the offending input(s) highlighted on form error — not a disconnected corner toast. *(this is the slop-fix in the SKILL body)*
- Empty states prompt to create the first item, with optional templates — the empty screen is onboarding, not a dead end. *(slop-fix in the SKILL body)*
- A design system removes choices, not adds them — fewer, opinionated primitives produce more coherence than infinite flexibility. *(SKILL "constraints generate taste")*

---

### Perceptual constants (the cliffs to design against)
- **< 200ms** feels instant — the target for interactive feedback.
- **> 500ms** feels slow — never let a core interaction cross this *perceived* without a mask.
- **< 50ms** is the bar the best products hold for every interaction.
- Motion durations **200–300ms**, `ease-out` for enter/exit; **60fps** or it reads as broken.

These are canonical HCI / motion constants — they need no citation; they are the measuring stick the
properties above are checked against.
