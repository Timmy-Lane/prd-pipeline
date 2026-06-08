---
name: context-engineering
description: Curate the smallest high-signal token set for an agent or long task — manage context rot, retrieval, compaction, and KV-cache. Use when context is filling up, a long-running task spans many turns, you're designing an agent harness or system prompt, deciding what to load vs. retrieve, or the agent is "getting dumber," slower, or more expensive as the session grows.
---

# Context Engineering

Context is a finite resource with diminishing returns. The goal is **the smallest set of high-signal tokens that maximizes the desired outcome** — not the shortest context, the *highest-signal* one. Minimal does not mean short: you still give the agent everything it genuinely needs. You just stop paying for tokens that don't change the answer.

**Spend tokens first — "lean" is not "always fewest tokens."** Per Anthropic's multi-agent research system, token spend *alone* explained ~80% of agent-performance variance on their eval (token count + tool-call count + model choice together ~95%); their multi-agent win over a single agent came from spending ~15× more tokens, not from the architecture. Read these as a directional lever, not universal constants: when a result is poor, the first thing to try is usually *more* tokens on the right context — not a cleverer prompt and not more agents.

So lean means two moves, not one: cut the tokens that don't change the answer, *and* deliberately spend many where compute is the lever. Don't mistake this skill for "minimize everything."

## When to use

- Context is filling up — the working window is past ~40% and growing, or you're seeing the agent repeat itself, lose earlier decisions, or slow down.
- A task spans more turns than fit in one window (multi-file refactor, research, long debugging session).
- You're designing an agent harness, a sub-agent, or a system prompt and deciding what goes in.
- You're choosing between pre-loading data and retrieving it on demand.
- Cost is climbing and you suspect cache misses.

Skip it for a short, single-shot task that comfortably fits — context engineering is overhead, and a one-pass answer doesn't need it.

## Why context degrades: rot and the attention budget

As tokens grow, the model's ability to **accurately recall** any one fact *decreases*. The cause is architectural: attention scales as n² pairwise relationships across n tokens, so a fixed attention budget spreads thinner with every token you add. This is a gradient, not a cliff — but it means a bloated context is actively *worse* at the task, not just more expensive. Recall measurably degrades as the window fills — Chroma's *Context Rot* benchmark shows loss even on a trivial retrieval task, ~40% down by ~170K tokens on some tasks (and far sooner with low-signal filler).

The practical consequence: every token you add spends from a shared budget. Spend it on signal.

The flip side: context is also a **capability lever**, not only a cost. Loading the *right* large body of context — a whole codebase, a domain corpus — can make the model dramatically better at the task, comparable to a jump in model scale, because it's learning in-context. So the goal isn't "less," it's *all signal, no noise*: pay for the tokens that buy capability, cut the ones that don't.

## Just-in-time retrieval beats pre-loading

Don't dump everything the agent *might* need into the prompt. Keep **lightweight identifiers** — file paths, queries, URLs, IDs — and load the actual content at runtime with tools. This mirrors how people work: you don't memorize the filesystem, you `ls` and `grep` when you need to. It also enables progressive disclosure — the agent discovers what's relevant by exploring, instead of drowning in an exhaustive dump that's mostly irrelevant to *this* question.

The honest tradeoff: runtime exploration is slower than reading pre-computed data, and a poorly-equipped agent can waste context chasing dead ends. So use a **hybrid** when up-front data buys real speed. Claude Code is the canonical example: it naively drops `CLAUDE.md` into context up front (small, always relevant) while using `glob`/`grep` for everything else just-in-time. The rule is **do the simplest thing that works** — pre-load the small, always-needed stuff; retrieve the rest.

### Programmatic tool calling: keep intermediate results out of context entirely
JIT retrieval controls *what* enters context; programmatic tool calling controls whether the *plumbing between tools* enters it at all. When a task chains tools — fetch 200 rows, filter, join, take the top 5 — don't round-trip every intermediate through the model. Have the agent write a few lines of code that call the tools and do the filtering/aggregation in the execution environment, returning only the final small result. The 200 rows never hit the context; only the 5 that matter do. This is different from JIT retrieval (load on demand): here the agent *orchestrates in code* so bulky intermediates are born and die outside the window. Reach for it when a step's raw output is large but its useful distillate is small.

## Order context by volatility (static prefix → dynamic boundary)

Lay out context so the **stable parts come first and the volatile parts come last**, split by an explicit boundary. Everything before the boundary is byte-identical across requests and can be served from cache; everything after changes per turn and can't.

- **Static prefix (cacheable):** base instructions, tool descriptions, the verification checklist, durable conventions. No timestamps, no per-request data — anything dynamic here silently breaks the cache for the whole prefix.
- **Dynamic suffix (not cached):** cwd/OS, today's date, git status, the live conversation, retrieved files.

Claude Code does this literally, splitting its system prompt on a `__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__` sentinel — blocks before it are eligible for cross-session caching, blocks after are not. Putting the always-useful stuff (like the verification checklist) in the static prefix means it's present at *zero marginal cost* every turn.

## The compaction ladder (climb only as far as you need)

When context grows, apply the cheapest effective lever first. Don't summarize the whole transcript when only tool outputs are fat.

1. **Observation masking — do this first.** Keep the full history of *actions and reasoning*, but replace older *observations* (tool outputs) with placeholders, retaining only the most recent ~10 turns of full observations. Measured result: **52% cheaper with a +2.6% solve-rate improvement** — as good as full summarization at a fraction of the cost. Old tool outputs are rarely re-read, but old reasoning still informs current decisions. This is the highest-ROI single knob there is. One exception to "drop old observations": keep recent *failed* actions and their error output visible — the model learns from the stack trace it just produced, so masking a failure it hasn't resolved yet makes it repeat the mistake. Mask resolved noise, not the live failure it's still working.
2. **Tool-result clearing — free and mechanical.** Replace consumed `tool_result` bytes with a literal marker like `"[cleared to save context]"`, while **keeping the `tool_use` record** so the agent still knows *what action it took*. Zero inference cost — it's a string swap, not a model call. In practice this alone took one workload from 335K peak tokens to 173K.
3. **Summarizing compaction — costs one model call, so do it later.** Near the window limit, summarize the conversation and reinitialize with the summary. Preserve **architectural decisions, unresolved bugs, and implementation details**; discard redundant tool chatter. Tune by **maximizing recall first, then precision**. A workable stacked recipe: clear tool-uses at ~50K input tokens (keep the 6 most recent, never clear memory results), compact at ~180K.
4. **Carry critical state deterministically — never trust the summary to hold it.** A summary is prose; it will drop things. Keep a `NOTES.md` / `todo.md` / progress file *outside* the context, and re-read it after a reset. Structured state (the plan, TODOs, open questions, hard constraints) must be carried by code, not entrusted to summary prose — full rewrites of a memory doc corrupt unrelated fields, so prefer targeted updates.

A useful side effect: re-injecting the plan/TODOs at the *recent end* of context counteracts lost-in-the-middle — the model's attention is strongest at the edges, so the current objective belongs there.

**Durable state survives a crashed window.** The transcript is ephemeral and capped by the window; the workspace persists across as many windows as the task takes — so treat it, not the transcript, as the agent's real memory. The progress file from step 4 is half of this; **git is the other half.** Commit at each clean checkpoint. If a window dies mid-task — runs out, gets compacted badly, derails — the next one recovers by reading `git log`/`git diff` rather than reconstructing intent from a lossy summary: the last good commit is the rollback point, and the diff since it is exactly "what's in flight."

### Compaction as a deliberate cadence, not a panic button
Don't wait for the context limit to force a compaction. Compact *proactively* between work units — after a sub-task lands and before the next begins — so each unit starts on a clean, intentional summary instead of a window that's 90% full of the previous unit's noise. The cheap levers (mask, clear) run continuously; the summarizing compaction is the natural seam between units of work.

One hard rule for any summary: **it must never assert a completion that wasn't confirmed.** A summary that says "tests pass" when they were never run hands the next window a false premise it will build on. Mark unconfirmed steps as *in-progress*, not done; only a step you verified crosses into "complete." A summary is allowed to lose detail — it is never allowed to invent success.

### The agent-readable instruction file (`CLAUDE.md` / `AGENTS.md`): persist durable facts, keep it small
When a session discovers a fact the *next* session will also need — the build command, a non-obvious env quirk, a directory that's load-bearing — write it to the repo's agent-readable file so the next session boots already knowing it instead of re-deriving it. **Hard guard: this is one markdown line in a file the agent reads at startup — not a database, not a vector index, not a memory framework.** The whole value is that it's plain text the model already reads; a retrieval system around it reintroduces the cost and the failure surface you were avoiding.

Gate the write — persist only a fact that is (a) durable (still true in future sessions, not just this run), (b) general (helps future tasks, not only this one), and (c) safe to commit. **Never save:** transient failures or a one-off error you already fixed; secrets, tokens, or credentials; anything task-specific that's noise outside this run. The bar is "a teammate would want this in the README," not "this happened."

**Structure it by scope.** The file governs its directory subtree: one root file for repo-wide rules, a nested file only where a subtree genuinely differs — deeper files win, and the chain from repo root down to the working directory is preloaded (the open `AGENTS.md` spec; Claude Code's nested `CLAUDE.md` and Cursor project rules work the same way). Hold only what's durable and load-bearing for *acting on the code*: build/test/run commands, a map of how the code is organized, naming and style conventions, the non-obvious env quirks. Not a tutorial, not prose.

**Maintain it like context, because it is.** The file is always-loaded — every line is paid from the same finite attention budget on *every* turn, so a fact-dense short file beats a complete long one: prune stale rules, merge duplicates, and push rarely-needed detail into a doc the agent reads only when relevant (Anthropic, "Effective context engineering"). Keep **one source of truth** — each durable fact lives in exactly one artifact and every other doc *links* to it instead of restating it; never restate what the code, tests, or config already assert (a pointer beats a copy that silently goes stale). Reconcile on a cadence — append-only growth is rot — and treat any persisted fact as a **hint, not ground truth**: the moment the code or the user contradicts it, fix or delete that line rather than act on it. A stale memory trusted as fact is worse than no memory.

## KV-cache discipline (where the cost actually is)

Agent traffic runs roughly **100:1 input-to-output tokens**, so the input cache matters ~100× more than output length. Cached input can be ~10× cheaper than uncached. To keep the cache warm:

- **Static prefix** — no timestamps or dynamic content in the cached region (see volatility ordering above).
- **Append-only context** — never edit or reorder a previous turn; any change downstream of a cached span invalidates it. Add, don't rewrite.
- **Deterministic serialization** — sorted JSON keys, stable formatting, so prefixes are byte-identical request to request.
- **To disable a tool, mask its logits — don't remove it from the tool list.** Removing a tool changes the prefix and busts the cache for everything after it. Keep the tool list constant; suppress unwanted tools at decode time.

At scale the discipline gets concrete. **On a fork (a sub-agent or a retried turn), copy the parent prefix byte-for-byte** — one differing whitespace or reordered field means a cache miss on the entire shared span, so the fork pays full price for context it could have inherited. The steady-state shape per turn is **a static cached prefix plus a freshly rebuilt dynamic suffix**: you don't mutate the prefix to add the new turn, you append the volatile part after the boundary and let the prefix stay byte-identical. And **derive the cache key deterministically** from the stable inputs (prefix hash) so the same prefix maps to the same cached entry every time — nondeterministic serialization upstream (unsorted keys, a stray timestamp) silently fragments one logical prefix into many cache entries, none of which hit.

## Sub-agents are context firewalls

This is the mechanism the rest of the kit refers to. A sub-agent runs in its **own separate context window**; the parent sees *only the final summary it returns*. Every intermediate read, search, failed attempt, and tool dump happens inside the child's window and **never enters the parent's** — the boundary is a one-way valve that passes a distilled result and blocks the raw byte-stream that produced it. That isolation *is* the firewall: the parent's context stays small and high-signal no matter how noisy the gathering was.

So delegate the token-heavy, noisy work — deep exploration, large searches, browser sessions, reading a sprawling codebase — to a sub-agent and get back a distilled ~1–2K-token digest. The parent spends a couple thousand tokens to buy work that would have cost tens of thousands inline.

The discipline that makes it hold: **findings cross the boundary, raw documents do not.** The parent holds the high-level plan and synthesizes; sub-agents do the messy gathering and report conclusions, not transcripts. (For *whether* to fan out and how to brief workers, use compound-v:dispatching-parallel-agents; for choosing the agent *shape*, compound-v:designing-agents. Both build on this firewall.)

## Right-altitude system prompts

When you do put instructions up front, aim between two failure modes: too *brittle* (hardcoded if-else logic that overfits and rots) and too *vague* (high-level prose that assumes shared context the model doesn't have). Strike specific-enough-to-guide yet flexible-enough-to-give-strong-heuristics. Delineate sections with Markdown headers or XML tags. Start from a minimal prompt on the best model, then add instructions and examples to fix observed failure modes — don't pre-write guards for problems you haven't seen.

## Encode what transfers across models; defer what scale washes away

The harness is the durable asset; the model is swappable — so spend effort on what *survives* a model upgrade and let the model handle what it'll soon do unaided. **Encode** the things that transfer across generations: verifiable environments and checks, the plan/state/conventions, agent-addressable structure, and representations that turn a fuzzy task into one the model is already strong at. The sharpest version of that last one: **make a non-coding task look like a coding task** — hand the agent files plus `bash`/`grep` over prose-described data instead of a bespoke tool-for-every-step, because coding-agent training generalizes to anything shaped like filesystem ops. **Don't encode** elaborate cognitive scaffolds, role-play personas, or hand-built planners that the next model will simply absorb — that work gets washed away. The test when unsure whether to build a mechanism: would it still earn its place against a clearly smarter model? If no, defer it.

## The quick checklist

- Target the smallest high-signal set; cut tokens that don't change the outcome.
- Keep working context under ~40%; when it climbs, climb the compaction ladder (mask → clear → compact), cheapest first.
- Retrieve just-in-time via lightweight identifiers; pre-load only the small, always-needed stuff.
- Order by volatility: static cacheable prefix, dynamic suffix, explicit boundary.
- Keep the cached prefix static, the context append-only, serialization deterministic; mask tools, don't delete them.
- Carry the plan/state in an external file, not in summary prose; recite it at the recent end of context. Compact proactively between work units; never let a summary claim an unconfirmed success.
- Persist a *durable* discovered fact to `CLAUDE.md`/`AGENTS.md` (one line, not a memory system); never persist transient failures or secrets.
- Push noisy, token-heavy work into sub-agents that return only findings.
- Hard-code only what survives a model upgrade (verifiable checks, state, structure); let the model handle what scale will soon do unaided.
