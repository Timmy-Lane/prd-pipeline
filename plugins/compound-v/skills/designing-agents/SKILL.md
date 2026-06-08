---
name: designing-agents
description: Pick the least-structure design that solves an AI/LLM feature — climb from a single call up to autonomous agents and sub-agents only when complexity demonstrably earns its keep. Use when deciding "should this be an agent or a workflow?", "how many agents?", how many LLM calls, whether to add a loop or tools or sub-agents, or when architecting any multi-step LLM pipeline — even when the ask is just "make this smarter."
---

# Designing Agents

Find the simplest thing that works, then add agentic complexity **only when it demonstrably improves outcomes**. Every step up the ladder trades latency and cost for capability — so each rung has to pay for that tax. For many features, a single LLM call with good retrieval and a few in-context examples is already enough; reach higher only when a fixed call can't express the task.

Two definitions to keep straight, because the whole decision turns on them:
- **Workflow** — LLMs and tools orchestrated through *predefined code paths*. You wrote the control flow; the model fills in the steps.
- **Agent** — the LLM *dynamically directs its own process and tool use*. The model drives the loop and decides what to do next.

Workflows are predictable and debuggable; agents handle the unpredictable at the cost of predictability. Most "I need an agent" turns out to be "I need a workflow," and most "I need a workflow" turns out to be one good call.

## When to use

- You're deciding the *shape* of an AI feature: one call vs. a chain vs. a loop vs. multiple agents.
- Someone said "let's make this an agent" and you're not sure it needs to be.
- You're adding a multi-step LLM feature, a pipeline, or tool use and choosing how much structure.
- An existing LLM feature is flaky, slow, or expensive and you suspect it's over-built (or under-built).
- Skip it when the shape is obvious — a single, well-understood call needs no architecture decision; just write it.

This skill owns the **decision** — which shape, how much complexity. It does not own execution: for token/context mechanics use compound-v:context-engineering; for the fan-out details once you've chosen to parallelize use compound-v:dispatching-parallel-agents; for the evaluator/review loop use compound-v:recheck.

## The escalation ladder — climb only as far as the task forces you

Start at the bottom. Move up one rung only when you can name the specific thing the current rung *can't* do. A **latency budget** can force you *down* the ladder regardless of capability: if the feature has to feel instant (compound-v:product-taste names the perceptual cliffs), a multi-round agent is off the table no matter how nicely it would reason — pick the highest rung that still fits the budget.

1. **Single augmented-LLM call** — one model call with retrieval, tools, and in-context examples. The atomic building block; everything above is composed from it. Default here.
2. **A Skill** — a reusable prompt/procedure that runs *in the main context*. The cheapest reuse there is: no isolation tax, no extra round-trips. If the win is "I keep re-explaining the same thing," it's a Skill, not an agent.
3. **A workflow (predefined control flow)** — when the task cleanly decomposes into *fixed* steps you can write in code. Three canonical shapes:
   - **Prompt chaining** — sequential steps, each consuming the last's output; add a programmatic gate between steps to catch errors early. Use when the decomposition is fixed and clean (outline → validate → write).
   - **Routing** — classify the input, dispatch to a specialized handler. Use when inputs fall into distinct categories better handled separately; doubles as a cost lever (send easy cases to a small model, hard ones to a big one). Routing isn't only a front-door classifier: a cheap agent can run until it hits a hard subtask, **forward a fork of its full context to a stronger model** for that one step, then resume on the cheap model with the result. The catch — a cheap model **cannot reliably detect its own limits**, so the escalation trigger must be *explicit and external* ("always escalate on a merge conflict"), never "escalate when you feel stuck." This is a routing tactic, not a reason to build a model-router.
   - **Parallelization** — *sectioning* (independent subtasks at once) or *voting* (same task N times for confidence). Use for speed or when multiple perspectives raise reliability.
4. **Orchestrator-workers** — a lead LLM decides the subtasks *at runtime* and delegates them. The distinction from parallelization: the subtasks **aren't known in advance**. Use only when you genuinely can't predict the decomposition (multi-file edits, open-ended search).
5. **Evaluator-optimizer** — a generator and an evaluator loop until a signal says "good enough." Use only when you have a *clear evaluation criterion* and iterative refinement measurably helps — i.e. there's real signal that feedback improves the result, like a reviewer would give.
6. **Autonomous agent** — the model plans and operates the loop itself on environmental feedback, for as many steps as it takes. Use for open-ended problems where you *can't* hardcode a fixed path or predict the step count. Precondition: the agent can get **ground truth from the environment each step** (test results, code execution, tool returns) — without that grounding it drifts.
7. **Sub-agents (context isolation)** — split work into fresh, isolated context windows. The real reason is **context control**, not role-play "my PM / my QA": a sub-agent is a *context firewall* — it does the token-heavy reading/searching and returns only a distilled digest, so the raw material never touches the parent (the mechanism, and when this pays off, lives in compound-v:context-engineering). But it starts clean-slate (sees none of your history) and pays a latency tax to re-gather context, plus a "telephone" risk on what it returns — so don't reach for it when the task needs tight back-and-forth or shares a lot of context with the main thread.

Walk it as a short series of questions — stop at the first "yes":

1. One good call (+ retrieval + examples) does it? → **single call / Skill**.
2. The steps are a fixed, known-in-advance sequence? → **workflow** (chain / route / parallelize).
3. There's a clear verifiable signal to iterate against? → **evaluator-optimizer** (compound-v:recheck).
4. You can't predict the subtasks but each is still bounded? → **orchestrator-workers**.
5. It's open-ended with no fixed path or step count, and the environment gives ground truth each step? → **autonomous agent**.
6. A side task floods context with stuff the parent won't reuse? → **add a sub-agent** for it (compound-v:dispatching-parallel-agents).

## An agent is an LLM + a loop + tools — there is no secret

A working coding agent is **under ~400 lines, most of it boilerplate** (~190 after three tools). The loop is the whole heartbeat: read input → append to the conversation → call the model with the full conversation + tool defs → if the model returns a tool call, run it and append the result → if it returns text, show the user → loop. The model server is *stateless*; it only sees what you put in the `conversation` — maintaining that history is your job, which is why context engineering is the substance of agent quality.

A tool is four parts: **name**, **description** (what it does, when to use it, when not, what it returns — written like a docstring for a new hire), **input schema**, and the **function**. Give a model a tool and it *wants* to use it — it auto-triggers and chains without coaching. So the leverage is in the tool interface, not clever prompting: builders routinely spend more time optimizing tools than the prompt.

At ship time you wrap those four parts in a few **operational** concerns the primitive doesn't carry: a **timeout that returns a result** (a slow tool reports "timed out," it doesn't throw), an **approval gate** on irreversible actions, an **`is_enabled`** predicate to hide a tool the model shouldn't reach for in the current state, and an **error formatter** that turns a raw stack trace into a terse, model-readable message. The pattern that ties these together: **a tool error is a tool *result*, not an exception.** When a tool fails, feed the failure back into the conversation as the tool's output and let the model adapt — don't crash the loop or silently swallow it. Hand results back as **structured objects**, not a stringified chat blob; a typed return the next step can read beats prose it has to re-parse.

**Skip the high-level agent SDKs.** Model differences are large enough that you'll end up building your own thin abstraction anyway, and the SDKs obscure the underlying prompts/responses and can mangle message history. Target the provider API directly so you control cache points and see real errors.

## Tool design is an interface (ACI)

Invest as much in the agent-computer interface as you would in a human UI. The agent is a non-deterministic caller that will call the wrong tool, with the wrong args, in the wrong order — unless the interface prevents it. So when you design (or look up) a tool's shape:

- **Poka-yoke the arguments** — make wrong calls hard to express. Requiring **absolute paths** instead of relative ones eliminated a whole error class on real benchmarks. Constrain types and enums so invalid states can't be passed.
- **Minimal overlap.** If a human engineer can't say which of two tools to use in a situation, neither can the agent. Curate a small set of distinct tools; consolidate (one `search_x` that does the work) rather than exposing every low-level endpoint.
- **Describe it like a docstring for a junior.** State what it does, when to use it, when *not* to, and what it returns. Return high-signal semantic fields (names, types) over cryptic IDs (`uuid`, `mime_type`). Small refinements to a tool's description yield outsized improvements in how reliably it's used.
- **Make the tool dumb and deterministic, not agentic.** A tool that is itself an LLM or sub-agent is hard to reason about and chains two non-deterministic systems, compounding failure. Prefer a plain deterministic action (a literal web search, a direct lookup) over "ask a sub-agent to figure it out" — push the intelligence into the *calling* agent and keep the tool a predictable primitive.

(compound-v:searching-patterns points here for ACI when the thing you're building is itself a tool.)

## Per-step reliability is the real bottleneck

Multi-step agents fail on *compounding* error, not on any single hard step. At 90% per step, 100 steps gives 0.9^100 ≈ 0.003% — effectively zero. You need roughly **99.9% per step** before long chains work, and each added "nine" is roughly an order-of-magnitude harder. This is *the* reason to favor less structure: fewer steps means fewer places to fail.

Two design consequences:
- **Scope tasks small and verify each one.** A short chain of well-verified steps beats a long autonomous run you can't check. Prefer subtasks that have **automated verification** (tests, type-checks, a runnable result) — verifiability, not model IQ, is what limits how far an agent can reliably go. **A verifiable signal is the precondition for autonomy:** the more you let the loop run unattended, the more it needs ground truth from the environment each step (a test, a type-check, a tool return) rather than its own say-so. No signal → no autonomy → keep it a short, checked workflow.
- **Don't trust the model's own narration as a check.** "Show your reasoning" is not a correctness signal — the visible chain-of-thought can be edited to nonsense and the model still answers correctly, so it isn't a faithful trace of the computation. Ground every step in environment feedback, not self-narration.
- **On a retryable failure, change a variable — don't re-roll the same dice.** "One hypothesis, one variable" governs deterministic debugging; a *stochastic* step re-run with the identical model and prompt is the same dice thrown again. Warp found that retrying the same model "often produced repeat failures," and fixed it with a cross-model fallback chain (Warp eng. blog, swe-bench-verified). So fail *over* — a different model, or a substantively changed prompt/context — so the retry is a new experiment, not a re-roll.

Before reaching for more agents, look at where the cost and the variance actually go. Anthropic's multi-agent research found that **three factors explain ~95% of the performance variance — and token spend alone explains ~80%, the other two being tool-call count and model choice.** "Add another agent" is rarely the lever; "let the one agent spend more tokens on the hard part" usually is. Spend the budget on thinking and verification, not on org-chart depth.

## Bound the loop; reinforce the objective every turn

- **Cap the loop and force a finish.** An unbounded "keep going until done" loop is a bug — a stuck agent burns tokens forever. Set a hard turn ceiling (≈10 is a sane default — OpenAI's Agents SDK ships DEFAULT_MAX_TURNS = 10) and, on the last allowed step, switch the prompt to **forced-done**: "summarize and stop, you are out of budget." A loop with no exit other than success is a loop with a missing exit.
- **Gate irreversible actions behind a human (HITL).** Deleting data, sending a message, deploying, spending money — anything you can't undo gets an approval checkpoint before it runs, not a post-hoc apology. Reversible actions can run free; the gate is for the one-way doors.
- **Reinforce the objective on every tool return**, not once up front. Each tool result is a chance to re-state the goal and current status, hint when a tool failed, and report state changes. A todo/echo tool that just reflects the agent's own task list back is enough to keep it on track — that's most of what it does.
- **Manage cache points explicitly** (this is where agent cost lives — see compound-v:context-engineering). Keep the system prompt and tool list static so the prefix stays cached; feed dynamic data (current time, fresh state) in a *later* message, never in the cached prefix.

### The stop rule (write it down; the model won't infer it)

Any agentic loop needs an auditable, four-clause stop condition — the loop halts when **any** of these fires:

1. **Hard cap** — turn/tool/token budget hit (the ceiling above).
2. **Coverage green** — the success signal is satisfied (tests pass, the criterion is met).
3. **Diminishing returns** — the last few steps stopped changing the answer.
4. **Model-done** — the model declares the task complete *and* that survives a check.

Two riders: **reserve budget for synthesis** so the loop doesn't spend its last token mid-thought with nothing written up, and **tell the model how much budget it has left** each turn so it can pace itself. You write this rule explicitly because a strong RL'd model's internal stopping policy is not extractable — you can't read it off the weights, so you state the contract.

## Multi-agent is delegation, not a message bus

When you do split across agents, the working shape is **agent-as-tool**: a parent calls a sub-agent the way it calls any tool, gets a result back, and stays in control. It is *not* a swarm of peers gossiping on a shared channel and editing the same files. The rule that keeps this sane: **parallelize intelligence, keep writes single-threaded.** Fan out the *reading, searching, and analysis* (those are read-only and compose cleanly); funnel every *write* through one actor in a defined order. Two agents editing the same file concurrently is a merge conflict you chose to create. (For the fan-out execution mechanics, see compound-v:dispatching-parallel-agents.)

Be skeptical of "look, a swarm built a whole compiler" demos. The famous multi-agent successes **all had a cheap, verifiable success criterion** (it compiles, the browser renders, the test suite is green) that let agents grind without a human in the loop. Most real software has no such oracle — correctness is "did this match the user's actual intent," which only a human can score — so the swarm has nothing to converge against and drifts. No verifiable criterion → no swarm.

### Counterweights (when the simple rule bends)

- **Maximal-then-restrict for a strong RL'd model.** The "start minimal" default assumes structure helps. For a heavily-RL'd frontier model, every hand-built abstraction is often a *liability* it has to work around — so the better move can be to hand it broad tools and full context, then claw back only what demonstrably hurts. Strip down from maximal rather than building up from minimal.
- **The Ralph loop beats the org chart.** A single deterministic loop running on *fresh* context, restarted each cycle, routinely outperforms an elaborate multi-agent graph running on *stale* accumulated context. Freshness of context beats sophistication of topology — which is exactly why batching work into clean-context units (compound-v:batched-implementation) wins over a standing committee of agents.
- **Decider/executor split.** Separate the model that *decides what to do* from the fast path that *does it* (e.g. a planning model handing edits to a high-throughput apply model). The split lets each half be tuned for its job instead of forcing one model to be both deliberate and fast.

## Worked example — "add an AI feature that answers questions about our docs"

The reflex is "build a RAG agent with sub-agents." Walk the ladder instead:

1. **Single call?** Paste the relevant doc section + the question into one call with a grounding instruction ("answer only from the provided context"). If the docs fit and retrieval is trivial, *you are done* — ship this.
2. **Retrieval too big to paste?** Add a retrieval step → a two-call **chain** (retrieve → answer). Still a workflow, still debuggable. Most "doc Q&A" lives here.
3. **Questions span unrelated domains?** Add **routing** (billing questions → billing docs + a billing-tuned prompt; API questions → API docs). A classifier in front, specialized handlers behind.
4. **Questions need multi-hop research across many sources you can't predict?** *Now* it's **orchestrator-workers**: a lead decides which sources to pull and dispatches readers. Each reader is a **sub-agent** so its raw page dumps never pollute the lead's context — only findings return.
5. **Answers need to meet a quality bar?** Wrap an **evaluator-optimizer** loop (compound-v:recheck) that checks groundedness and retries.

Each rung was added only because the previous one *couldn't* express the requirement. Stop the moment the task is satisfied — every rung you didn't need is latency and cost you didn't pay.

## Red flags

| Symptom | The actual problem |
| --- | --- |
| "Let's make it multi-agent" before a single call was tried | Skipping the ladder. Burden of proof is on complexity — prove the call fails first. |
| Sub-agents named after job titles ("PM agent", "QA agent") | Role-play, not context control. Split for *context isolation*, not org-chart cosplay. |
| Long autonomous loop with no verification between steps | 0.9^n is killing you. Scope smaller, verify each step against ground truth. |
| A tool that is itself an LLM agent | Compounding non-determinism. Make the tool deterministic; lift the intelligence to the loop. |
| Reaching for a heavyweight agent framework on day one | It hides the prompts and mangles history. Drive the loop yourself. |
| Dynamic data (timestamps, state) in the system prompt | Busts the cache every turn. Static prefix; feed dynamics in a later message. |
| "Show your reasoning" used as the correctness check | CoT isn't a faithful trace. Verify with tools, not self-narration. |
