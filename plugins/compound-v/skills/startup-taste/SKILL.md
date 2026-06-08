---
name: startup-taste
description: Pressure-tests whether and what to build — moat, scope, distribution, and bullshit — before any code is written. Use when scoping a feature, deciding "should we build X", estimating timelines, writing a roadmap or pitch, choosing a moat, or whenever a plan smells like overkill — even if nobody asked for a sanity check. This decides whether/what to build; brainstorming explores how once that's settled.
---

# Startup Taste

Code is commodity. The only things that compound are **taste, distribution, and a primitive nobody else has.** Everything else is either in service of those three, or it's the bullshit — and your job is to catch it before it ships.

Building stopped being the long pole around 2026: a product that took a quarter in 2021 takes a weekend now. So the scarce inputs are *what* to build and *getting people to care* — not the typing. The gates below all defend that shift.

## When to use
- Scoping anything, estimating timelines, or writing a roadmap / PRD / pitch.
- Someone asks "should we build X?", "is this a moat?", "what's our edge?"
- A plan smells like overkill: new framework, new abstraction, infra-first milestone, "make it configurable."
- **Skip it for:** pure execution of an already-scoped task (that's `writing-plans` → `batched-implementation`). Once the "should we?" is settled, **compound-v:brainstorming** takes over for the *how*.

## The master gate
**Does this grow taste, distribution, or a primitive?** None of the three → it's the bullshit; cut it or say why it's exempt. Run this first; most bad scope dies here.

**Suspect the safe-feeling default.** Inaction is a hidden risk that feels safe — it's often easier to do a hard thing that matters than an easy thing that doesn't (Sam Altman, "What I Wish Someone Had Told Me"). When choosing what to build, the comfortable low-stakes option is frequently the actual risk.

## The gates (run the relevant ones, name what you find)

This skill **owns** the scoping discipline the rest of the kit defers to: YAGNI / "every feature costs you forever" (name-the-cut), no premature machinery, de-risk the load-bearing assumption first, and verifier-first. **compound-v:brainstorming** and **compound-v:writing-plans** point here rather than re-deriving them.

**Estimate hygiene — hours/days for building, never weeks/months.**
If the bottleneck you name is "writing the code," re-estimate in hours, or move the time onto a *decision* or a *distribution* problem — that's where the real long pole now lives. A roadmap that budgets months of *building* is optimizing the part that got cheap.
Flag these strings whenever they're applied to construction (not to a decision or a distribution problem, where they may be honest): *"this will take weeks/months"*, *"multi-week"*, *"several months"*, *"a quarter to build."*

**Every scope names a cut.**
Subtraction is a first-class move — every feature costs you forever (Jobs cut Apple 350 products → 10; Granola cut half its features to expose the core interaction). A proposal that only *adds* (flags, endpoints, config, integrations) with zero removals is a feature factory, not a product call. Ask: "what did this remove?" If nothing, that's the finding.

**No premature machinery.**
Don't install the manager-mode apparatus — abstractions, microservices, config systems, a plugin framework — before the *third* copy-paste forces it. On a small/solo team this is pure cost. "Make it configurable" as a reflex is flexibility theater: pick the opinionated default, remove the option.

**Schlep ≠ overkill — cut ceremony, run toward the moat.**
"Cut the bullshit" is not "avoid hard work" — don't let one blur into the other. Ceremony-overkill (the premature abstraction above, restatement, process for its own sake) adds cost and no moat → cut it. A schlep is the unglamorous, hard-to-fake work — the data pipeline, the integration nobody wants to build, owning the ceiling layer, the 99.9%-reliability grind — that *is* the moat precisely because rivals won't stomach it. Run toward that. Test which one you're looking at: does skipping it make the product worse for the user, or just faster to ship? If skipping it only saves *you* effort and costs the *user* nothing, it was ceremony. If it's the thing a well-funded competitor would also have to grind through, it's the schlep — that's the work, do it.

**Wrapper test.**
Mentally swap the underlying model for the next release. Product basically unchanged, or the upgrade *kills* it → you built a wrapper (a feature), not a company. The upgrade should *help* you. The real bar: does this have architectural dependencies a well-funded competitor needs months to rebuild? (Reality check: wrapper-class apps sit far lower on retention than the category leaders — that gap is the tell.)

**Primitive in one sentence.**
You have a primitive only when you can state it in one sentence — "the search result, from links to a cited answer"; "speculative editing"; "the sync engine." Can't? You have a roadmap, not a primitive — stop and find it. The product is the *consequence* of the primitive (Figma built a WebGL renderer + multiplayer protocol for ~4 years; the design tool was then inevitable). "Existing workflow + LLM call" with no named core = a faster horse with a chat box.

**Contrarian insight + a timing leg.**
A real opportunity has three parts: the conventional wisdom, a contrarian truth you believe that most don't, *and* a tech enabler that makes it doable **now**. If your insight leads you to the same architecture as the incumbents, it isn't contrarian enough — that's cosplay, not an edge. Most people with a contrarian take stop at part two; the timing leg is where theses die. So name the enabler: what changed recently (a model capability, a cost curve, a platform shift) that makes this buildable now and wasn't a year or two ago? No honest answer → either right-idea-wrong-decade, or there's no insight at all. The decisive bet usually looks irrational at the time — ask which of your "obviously wrong" ideas is wrong because it's *early*, not because it's *bad*.

**Noticed, not brainstormed.**
The best ideas are *noticed* by someone who has lived in a domain for years, not *produced* in a list-making session (Paul Graham, "How to Do Great Work"). Provenance is a tell independent of how contrarian the idea sounds: if it came from a brainstorm rather than a problem you keep bumping into, that's the finding. Find the one you noticed, not the one you generated.

**Tar-pit filter.**
Some markets are graveyards — saturated, perennially attempted, historically resistant to solving (the calendar app, the universal inbox, the "Slack but better"). They look appealing precisely *because* the need is obvious, which is why everyone walks in and dies. Ask: is this a tar pit people keep stepping into? If so, the burden of proof is the *timing leg above* — what is finally different now — not enthusiasm.

**Persist on the goal, not the means.**
The scoping gates judge *starting*; this judges *continuing*. Persistence and obstinacy look identical from outside and split on one axis: the persistent are fixed on the goal and flexible on means, updating on evidence; the obstinate are fixed on the means, driven by ego (Paul Graham, "The Right Kind of Stubborn"). At a wall, ask whether the evidence still backs the goal — or only your pride does.

**Bounded beats unbounded.**
A bounded problem with a proprietary data flywheel (one narrow job done end-to-end) is how a small team owns a category; an unbounded problem (general intelligence, "an assistant for everything") is how it wraps a model and competes with the lab. Prefer the bounded scope where you can own the flywheel.

**Feature vs Product vs Company.**
Classify it. A feature does one thing and is cloned by next Tuesday (ships in days); a product solves a complete workflow (months); only a company compounds (data flywheel, distribution, lock-in). If it's a feature, name the company-level moat behind it — no moat → "wedge at best," say so.

**Revenue, not cost.**
Sell AI that grows the customer's revenue (no ceiling), not AI that cuts their cost (ceiling = the headcount you displaced, then you're done). Rewrite any pitch that leads with *"save time" / "cut costs" / "X% more efficient"* to lead with the outcome — leads found, deals closed, pipeline generated.

**Own the layer that sets your quality ceiling.**
Delete every third-party dependency on paper. If the core value dies, that dependency controls how good you're *allowed* to be — it's the layer you must eventually own. (Perplexity outgrew the Bing API and built its own index → near-zero URL overlap with competitors on identical queries; Cursor forked VS Code because the extension API made speculative edit impossible.) Label each external API "ceiling-setting" vs "commodity/swappable."

**De-risk the load-bearing assumption first.**
Order work by information gained ÷ time. Which single assumption, if false, makes the whole plan worthless? Test *that* first, with the cheapest experiment that resolves it. A plan whose first milestone is infra/scaffolding is fun-part-first — you're building on an untested belief. ("A month of fixed setup before the first result" is the classic red flag.) For an AI capability the cheapest experiment is almost always a *prompt*: validate the idea on a prompted frontier model before you fine-tune or collect data — never fine-tune to find out *whether* it works (latent.space, "The Rise of the AI Engineer").

**Verifier-first for AI.**
Before building an AI feature, name the verifiable signal / eval. No auto-check → you can't drive quality, and *no eval system is the #1 cause of failed AI products.* Build the verifier before the feature; "we'll eyeball quality" is the failure mode, not a plan. (Quality + verifiability beat quantity: 4,000 good verifiable examples beat 4M low-quality ones.) Once you commit to building, **compound-v:evals** is how you actually construct that signal — error analysis, binary judge, align-to-human. (Note: AI that automates a motion only amplifies whatever you feed it — an SDR that scales a script that doesn't close just automates the broken version at volume. Validate the loop before you scale it.)

**Harness before model.**
When an AI system underperforms, the fix is almost never a bigger model — it's context, tools, error recovery. Same model, different harness = real swings (v0 took one model to error-free via four engineering layers — a large jump with no model upgrade). Challenge *"upgrade to a bigger model" / "wait for the next model"*: have you exhausted context, tool design, and the verify-retry loop first?

**Reliability before capability.**
A reliable-but-narrower feature beats a more-capable-but-flaky one once users get burned: a feature that fails often enough to notice teaches the user not to trust it, and that lesson sticks. The impressive-demo, unreliable-in-practice trade is usually the wrong one: pick the boring thing that always works over the magic thing that mostly works. This is why each extra "nine" of reliability is worth real schlep (see above), and it's the demand-side reason the verifier and **compound-v:evals** come first — you cannot drive reliability you cannot measure.

**PMF is a number, not a vibe.**
"Users seem to like it" is not product-market fit. The field-standard read: survey users with "how would you feel if you could no longer use this?" and build for the segment that answers *very disappointed* — when a large enough share answers that way, you have a fit signal, not just enthusiasm. Track **paid power-user retention**, not signups or MAU. No segment clears the bar → you have interest, not fit; keep finding the people who'd be gutted to lose it rather than widening to please everyone.

**A number went up ≠ better.**
A moving metric is not proof of value (Goodhart). Bolt Tetris onto anything and engagement rises — it doesn't mean the product improved; engagement can just redistribute activity or measure friction. Before celebrating a number, name the *user outcome* it's a proxy for and check that outcome moved too. Popularity, anecdotes ("my cousin loved it"), a competitor having it, the boss's preference, and "someone else will build it" are bad reasons dressed as evidence — run the master gate regardless of who's asking or what spiked.

## Refusal templates (use the shape, fill the specifics)
- **Bullshit / over-scope:** "This grows none of taste, distribution, or the primitive — and it only adds. Cutting it (or tell me which of the three it serves)."
- **Wrapper:** "Swap the model for the next release and this is unchanged / dies. That's a feature, not a moat. The company-level lock-in behind it would be ___ — do we have it?"
- **Weeks/months for code:** "Building isn't the long pole anymore. The hard part here is the *decision* about ___ — let's spend the time there and ship the build in hours/days."
- **No eval:** "There's no verifiable signal yet, so we can't drive quality. Let's define the eval before writing the feature."

## What this skill is NOT
It is not a fan. A response that flatters every claim *is* the bullshit it's trying to remove. Name the violated property; offer the rewrite; assume a high-agency operator who already ships, so cut hand-holding, not rigor.
