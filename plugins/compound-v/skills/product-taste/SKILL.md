---
name: product-taste
description: Turns vague UI/UX verdicts into named, fixable properties and catches AI-slop defaults before they ship. Use for any design, polish, animation, latency, copy, or "does this look good?" decision — even a quick gut-check — and whenever an interface feels generic but you can't say why.
---

# Product Taste

Taste is not a gift and it's not subjective — it's a perceptual apparatus you build, and good design has objective properties (designers measurably improve over time; an eight-year-old's output is not interchangeable with a master's). So when something is wrong, the job is to **name which property is violated**, not to say "it feels off." The interface IS the product for almost every user.

As AI makes code and features cheap, *how well it's made* becomes the moat — details, polish, performance, cohesion, opinion. That's the differentiator this skill defends.

## When to use
- Any UI/UX/design/polish/animation/latency/copy decision.
- A "looks good?" / "is this done?" verdict on something visual or interactive.
- An interface feels generic, dead, or off and you can't articulate why.
- **Skip it for:** non-visual backend logic with no felt surface. This is about what the user *feels*.

## Name the property — refuse the vague verdict
You can only name a flaw once you notice it, and habituation blinds you to broken flows you've normalized — the worst flaws are the ones you've stopped seeing. Periodically look at your own product as a first-time user (Tony Fadell, TED — "noticing").
*"I like it" / "feels off" / "looks clean" / "looks good"* are not verdicts; they're the absence of one. A taste call you can't name, you can't fix or hand off. So convert every vague reaction into a named, copyable property. The operating vocabulary — reach for these first:
**spacing** (rhythm/density), **alignment** (to a grid/optical edge), **hierarchy** (what the eye hits first), **contrast** (figure/ground, WCAG), **easing** (the curve, not linear), **motion purpose** (it communicates a state change or it's noise), **latency** (perceived speed), **affordance** (does it look like what it does), **feedback** (the system answers every action), **density** (information per screen), **consistency** (same thing looks the same), **copy clarity** (clear over clever).
Useful drills: "If a rival shipped this, would I be impressed or relieved?" "Name the one mechanism that makes this interaction feel alive." For *settled* questions there's a right answer, not a taste call — checkbox vs radio, standard button states — just cite the known pattern; reserve the apparatus for genuinely open calls. And name the inverse honestly: product judgment is domain-specific and doesn't transfer — strong practitioners are good at saying when they *don't* have it (Paul Adams, Intercom — "Product Judgment"). In a domain you haven't lived in, don't bluff a crisp verdict; flag the missing calibration and judge from the running surface, not from a summary. The full ~50-property vocabulary (the concrete, vendor-neutral rules behind these headings) lives in **references/interface-checklist.md** — load it when auditing a real interface or when "name the property" needs the specific rule.

## Slop detector — every default is a decision you didn't make
AI hands you mediocre defaults; the skill is knowing which to override (the load-bearing ones, not all). The slop aesthetic is recognizable — grep your own output for it, and each hit carries its fix:
- Uniform rounded corners on everything → pick a radius scale on purpose, or square the cases that should read as structural.
- Gradients that don't match the brand → drop them or pull from the actual palette.
- Copy edited to be **inoffensive instead of clear** → rewrite for clarity and opinion (pairs with the `humanizer` skill).
- Layouts grid-perfect but tonally flat → add deliberate emphasis/asymmetry; flatness is the absence of a hierarchy decision.
- Default easing curves → set an `ease-out` (or a spring), never ship linear.
- **Generic empty state** → make it the onboarding: prompt to create the first item, with optional templates.
- **Default focus ring** (`outline`) → use `box-shadow` so it follows border-radius (older Safari versions render `outline` without following `border-radius`).
- **A toast for everything** → show feedback *at the trigger* — an inline checkmark on the copy button, the offending input highlighted on form error — not a disconnected corner toast.

Each hit: "was this deliberate, or did the tool decide for me?"

## The invisible-details checklist (these are the whole game)
Users can't articulate why one interaction feels alive and another dead, but the difference is specific and copyable. Most builders never notice they're leaving these on defaults:
- Dialogs/popovers scale in from **~0.8, not 0** (0 looks like a glitch; 0.8 feels physical).
- Buttons depress to **~0.96** on press.
- **`tabular-nums`** on timers and numeric columns so they don't reflow as digits change.
- **16px minimum** input font (anything smaller triggers iOS auto-zoom).
- Pause animations/loops when off-screen.
- No dead zones between adjacent list items — full-row hit targets.
- Open menus/dropdowns on `mousedown`, not `click` — firing on press-down instead of release shaves the perceptible delay and makes the menu feel instant (Web Interface Guidelines).

## Animation gate — motion has a job or it's noise
Decoration kills UX. Run every motion through six checks; any fail → cut or fix:
1. Natural (not robotic).
2. Right speed.
3. **Clear purpose — it communicates a state change.**
4. 60fps.
5. **Interruptible mid-flight** (a spring that argues with the user when they act feels like the app fighting them).
6. Accessible (respects reduced-motion).

Motion added "because it looks nice," with no state change to communicate, fails #3 → it's decoration → cut it.

Craft refinements: animate only **`transform` and `opacity`** — they ride the GPU's composite-only path, while animating layout or color forces repaints that drop frames; keep durations in the **200–300ms** range, `ease-out` for enter/exit. And invert the intuition for *frequency*: an element seen 100+ times a day should **lose** its animation — repeated motion stops reading as delight and becomes noise.

Prototype animation, keyboard nav, and touch in **code, not Figma**. A static design tool cannot represent easing, interruptibility, or input modes — it shows you the keyframes, not the *feel*. The only honest medium for a motion or interaction decision is the running thing.

## Latency gates — perceived speed is taste work, not an infra afterthought
Hold the perceptual cliffs:
- **< 200ms** feels instant — target for interactive feedback.
- **> 500ms** feels slow — never let a core interaction cross this *perceived* without a mask.
- **< 50ms** is the bar the best hold for every interaction (Linear); Cursor's tab completion lives at ~260ms — fast enough, deliberately measured.

The levers are perceived-speed work — optimistic updates, skeleton states, streaming — applied *before* you reach for backend speed. "We'll optimize latency later, it's infra" is the wrong call; bake the masks in now. When the felt surface sits on an AI system, the latency budget is an architecture constraint, not just a polish layer — it can force a simpler, faster rung (fewer agent hops, a smaller model, no extra round-trip); see **compound-v:designing-agents**.

## Reduce cognitive load, not clicks
The thing to minimize is *thinking*, not taps. Software that stops the user with a decision they don't understand makes them feel stupid — that's the real cost, not one more click. A flow of many trivially-obvious taps can feel effortless (Snapchat runs at several deliberate taps a second), while a single screen demanding an unfamiliar judgment feels heavy. Cut decisions and unfamiliar choices first; only collapse clicks that each carry real cognitive weight.

Friction is *perceived*, not calculated — users reject on felt cost, often to an irrational degree, and proving the rational math doesn't move them. The cheapest fix is usually to *re-frame* the cost, not actually reduce it: pre-pay it once so each use feels free, mask it (optimistic update, skeleton), or pick a default so the choice disappears. Same lever as latency masks: change the feeling, not just the number.

## Constraints generate taste — remove options, don't add them
Fewer, more opinionated primitives produce more coherence than infinite flexibility; a design system's job is to *remove* choices, not offer them (Teenage Engineering's fixed palettes as a generative force; Linear collapsed 98 color variables → 3). That collapse works because the palette is built in LCH, not HSL — LCH is perceptually uniform (a red and a yellow at the same lightness actually look equally light), so one base/accent/contrast triple generates every theme, including high-contrast a11y variants (Linear — How We Redesigned the Linear UI); HSL's lightness lies, forcing per-color hand-tuning. Default to removing — justify every new variable/flag/token against the coherence it costs — and build for specific users, not everyone. The spec is the floor, not the ceiling: ship craft as continuous improvements rather than gating it behind one big polish phase, and reduce scope to raise quality (fewer things, done excellently) instead of chasing a longer feature list.

## Start from the experience, work backward to the tech
Lead with what the user *feels*, then work back to the architecture — never the reverse (the slop trap is tech-first: grid-perfect, tonally dead). Decline to spec prompts/models/plumbing before the target experience is named. You own the felt quality, not just the diff — the agent that writes the code owns whether it feels right, so don't defer the taste call to "a designer later."

## Refusal templates
- **Vague verdict:** "I can't ship 'looks good' — which property? The spacing reads cramped at the card edges / the easing is the default ease-in-out / the primary action has no hierarchy. Pick the one to fix."
- **Slop:** "These are tool defaults, not decisions — uniform 8px radius everywhere, an off-brand gradient, hedged copy. Which were deliberate? Let's override the load-bearing ones."
- **Decorative motion:** "This animation doesn't communicate a state change and isn't interruptible. It's decoration — cut it or give it a job."
- **Latency punt:** "Latency is a design decision. This crosses 500ms perceived — add an optimistic update / skeleton now, don't defer it to 'infra later.'"
