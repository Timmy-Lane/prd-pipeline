---
name: critical-thinking
description: Distrust your own reasoning before you commit to it — steelman the strongest counter-argument, hunt for disconfirming evidence, and treat your own confidence as a flag rather than proof. Use the moment you're about to commit to a conclusion, recommendation, or design rationale that feels obviously right — especially when nobody is pushing back and your certainty is the only evidence. This is in-flight self-skepticism over your OWN current reasoning; recheck is a separate reviewer over finished work, verification-before-completion runs the command that proves an output, and startup-taste judges whether to build.
---

# Critical Thinking

The moment a conclusion feels *obviously* right and nobody is pushing back is the moment you're least likely to check it. This is the discipline of red-teaming your *own* reasoning before you commit — turning the search for confirmation into a search for where you're wrong.

## When to use
- You're about to commit to a conclusion, recommendation, design rationale, or "this is the answer" — and your own confidence is the main thing backing it.
- The call is load-bearing or hard to reverse, or you notice you've only gathered evidence that agrees with you.
- You're converging on a design in **compound-v:brainstorming** — pressure-test the approach you're about to recommend instead of confirming your first instinct (it should beat the *real* alternative, not a strawman). This is the discipline's prime home during design.
- **Skip it** for trivial or reversible calls — red-teaming a rename is its own overkill. This is for reasoning with consequences.
- This is in-flight self-skepticism over your OWN current reasoning. **compound-v:recheck** is a separate reviewer over finished work; **compound-v:verification-before-completion** runs the command that proves an output; **compound-v:startup-taste** judges whether to build at all.

## The gates (run the relevant ones; name what you find)

**Felt-certainty is a flag, not a verdict.**
When your chain-of-thought feels obviously right and nothing is pushing back, treat that confidence as the cue to look *harder*, not as proof. (The most conventional-minded people are the surest they think for themselves — Paul Graham, "How to Think for Yourself.") Audit the claim at its weakest joints, not the version that already convinced you. Your own stated reasoning isn't evidence — a chain-of-thought rationalizes a conclusion as easily as it reaches one.

**Steelman your own claim, then keep only what survives.**
Build the strongest form of the *counter*-argument — the one its smartest proponent would make, not a strawman you can knock down — and name who would make it. Let it shave your claim down to the load-bearing part still standing. You don't own an opinion until you can argue the other side better than the person who holds it (Charlie Munger). Where two people you respect genuinely disagree is the frontier: sit in the contradiction and form your own bet rather than picking a side.

**Seek the disconfirming case, not agreement.**
Pressure-test a conviction by hunting for the input or argument that *breaks* it — breadth-first, looking for the limit — instead of collecting wins that confirm it. (A claim is only worth something if you can say what would falsify it — Popper; "Sparks of AGI" probed for where the model failed, not for more demos — Bubeck.) Two tells you're fooling yourself: your reasoning lands exactly where everyone already is, or no evidence could change your mind — that's an identity, not a conclusion. **And check the frame, not just the claim:** the deepest disconfirmation is finding you're rigorously right about the *wrong question*. Ask why the problem is even posed this way — "why does this workflow exist at all?" not "how do I make it faster?" (Bob McGrew, ex-OpenAI: a real "heretic" questions the premise itself, not the answer inside the frame.)

## Shared with startup-taste — use them there, don't re-derive
- **Idea vs ego at a wall:** persistence and obstinacy split on whether you're attached to the *goal* or your *means* — **compound-v:startup-taste** ("persist on the goal, not the means").
- **Actually contrarian, or just confident?** the contrarian-insight + timing test lives in **compound-v:startup-taste**.

## Red flags
| Smell | Why it's the tell |
|---|---|
| "It's obviously right" and nobody's disagreeing | Absence of pushback isn't agreement — it's that you haven't looked. Build the counter-argument yourself. |
| You only have evidence that fits | You searched for confirmation, not truth. Name what would falsify the claim, then go look for *that*. |
| The counter-argument you "considered" is easy to beat | That's a strawman. Steelman it to the version that actually threatens the claim before you dismiss it. |
