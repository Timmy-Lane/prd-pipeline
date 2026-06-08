---
name: using-compound-v
description: Routes any task to the right Compound V skill and the right effort tier before work starts. Use at the start of every task — scoping, building, reviewing, design, or a quick fix — to decide what's worth doing and how much machinery it deserves.
---

# Using Compound V

Match effort to the task, and only build what compounds. Overkill is a defect, not a safety margin.

You don't have to remember what each skill does — match the **task** to a trigger and invoke that skill with the `Skill` tool **before acting**, even for a question, even when the user didn't name it. The descriptions fire on intent, not keywords; when a skill might apply, invoke it and let it bow out if it doesn't fit. Silently skipping a skill that applies is the failure this kit exists to prevent.

## Instruction priority
User CLAUDE.md > Compound V skills > default behavior. If the user's instructions contradict a skill (e.g. "don't use TDD here"), the user wins — always.

## The master gate
**Does this grow taste, distribution, or a primitive?** None of the three → it's the bullshit; cut it.

## Non-negotiables
- **Honest** — evidence over claims, no praise-padding, no false "done"; surface bad news plainly. Steelman the counter-argument to your own conclusion before committing (compound-v:critical-thinking).
- **Safe** — never trade security to ship; flag vulns (incl. the lethal trifecta). No harmful code.
- **Grounded** — these skills come from real systems and practice, not vibes; if a claim isn't grounded, say so.

## Tier routing — smallest box that fits; route *down* when unsure

The kit's bet is that adaptive effort is something the model is increasingly good at on its own; this table makes that judgment explicit rather than trusting it implicitly (anti-overkill law, a JUDGMENT-CALL stance — `references/sources.md` → using-compound-v). Use it as the explicit floor, not a replacement for judgment.

| Tier | Trigger | Workflow |
|---|---|---|
| **Trivial** | typo, rename, one-liner, config flip | Just do it → `verification-before-completion`. No plan, no agents. |
| **Small** | one function/file, clear spec | inline `test-driven-development` → verify. Skip the plan doc. |
| **Standard** | a feature, ~2–8 tasks | (open "should we?" → `startup-taste` first) → `brainstorming` → `writing-plans` → `batched-implementation` → `recheck`. |
| **Large** | multiple subsystems | split into sub-projects; each runs its own Standard cycle. |

## Other skills
- **Judgment:** `startup-taste` · `product-taste`
- **Plan:** `brainstorming` · `writing-plans` (per-build plan) · `writing-prd` (the product's stable source-of-truth doc)
- **Thinking:** `critical-thinking` (red-team your own reasoning before you commit — steelman + disconfirm)
- **Build:** `batched-implementation` · `recheck` · `finishing`
- **Correctness:** `test-driven-development` · `systematic-debugging` · `verification-before-completion`
- **AI design:** `designing-agents` · `evals` · `context-engineering`
- **Security:** `agent-security` (lethal trifecta, untrusted input, model-written code)
- **Power:** `searching-patterns` (pull the canonical pattern + its anti-pattern) · `dispatching-parallel-agents` (file-disjoint only)
