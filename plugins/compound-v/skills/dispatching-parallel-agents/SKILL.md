---
name: dispatching-parallel-agents
description: Fan work out to multiple sub-agents only when the pieces are genuinely independent — file-disjoint, no shared state. Use when you have several independent tasks (multi-file edits, parallel research, batch processing) and are deciding whether to parallelize, how to brief each agent, and how to combine results. If the work is coupled, don't split it.
---

# Dispatching Parallel Agents

Parallel sub-agents multiply throughput *and* isolate context — but only when the work is actually independent. The default failure isn't too little parallelism, it's splitting coupled work: isolated agents make divergent assumptions and return pieces that don't fit together. Fan out when the seams are clean; otherwise keep it single-threaded.

compound-v:designing-agents decides *whether* to fan out and into which shape (orchestrator-workers, evaluator-optimizer, …); this skill is the *how* once that choice is made. Each sub-agent is a context firewall (compound-v:context-engineering owns that mechanism) — that's why fan-out also buys context isolation, not just throughput.

## When to fan out

Parallelize when **all** of these hold:

- **Genuinely independent** — task B doesn't need task A's output. (If B consumes A, that's a pipeline, not a fan-out — see below.)
- **File-disjoint** — agents write to non-overlapping files. Two agents editing the same file means last-write-wins, silently — one agent's work just vanishes. Partition by file or use separate worktrees.
- **No shared mutable state** — no shared in-memory structure, no contended resource they'd race on.
- **Each piece is worth a fresh context** — it produces enough output (or noise) that isolating it in its own window is a real win.

Good fits: editing N unrelated modules, researching N independent sub-questions, processing a batch of independent items, gathering context across disjoint areas of a repo. When unsure, stay single-threaded — the red-flags table below catches the coupled-work case.

### Parallelize intelligence; keep writes single-threaded
The sharpest version of the independence rule isn't "file-disjoint" — it's *what kind* of work is being parallelized. Per Cognition, multi-agent pays when the extra agents **contribute intelligence (reads, research, critique), while writes stay single-threaded**. Parallel *reading* is safe — N agents can explore disjoint areas at once with no way to collide. Parallel *writing* is where divergence bites: two agents editing toward a shared design make incompatible choices, and the merge costs more than the fan-out saved. So the canonical safe worker is a **read-only retrieval worker** — it gathers and reports findings, mutates nothing; Cognition notes these "mostly resemble tool calls rather than true multi-agent collaboration," which is exactly why they're safe to run in parallel. If a step must *write*, route it through one agent.

## Pipeline by default; barrier only when you must merge

Don't block on all workers if you don't have to. If results feed a next stage one at a time, **pipeline** them — start downstream work as each finishes. Use a **barrier** (wait for everything) only when the next step genuinely needs all results together, like a synthesis that reasons over the full set. A premature barrier turns N parallel agents back into the latency of the slowest one for no reason.

## Brief each worker to stand alone

A sub-agent starts with a **fresh, isolated context** — it does *not* see your conversation, the files you've read, or the skills you've invoked. The only thing that crosses the boundary is the prompt string you give it. So every brief must be self-contained. Include:

1. **One clear objective** — one job per worker; don't bundle. Keep tasks distinct and non-overlapping so two workers never redo or collide on the same thing.
2. **All the context it needs** — paths (absolute), the relevant facts, constraints, the spec. It can't ask you mid-run, and it can't see what you saw.
3. **How to verify its own work** — the test command to run, the check to pass. A worker that can confirm its result returns something trustworthy.
4. **The return contract** — ask for a tight summary (aim for ≤500 words / ~1–2K tokens): what it did, what it found, what's left, anything that surprised it. Findings cross the boundary; raw dumps do not.

Two structural limits to design around: sub-agents **cannot spawn sub-agents** (one level of nesting — fan out from the orchestrator, not recursively), and many workers each returning verbose results will themselves flood the orchestrator's context, so enforce the condensed-summary contract.

## Don't over-spawn

More workers means more overhead and more reconciliation, not linearly more value. Prefer **fewer, more capable workers** over many narrow ones; add a worker only when it does something genuinely distinct. A 50-CEO lookup splits cleanly into a handful of workers handling batches — not fifty one-each. Match the count to the real independent seams in the work, and route down to a single agent (or no sub-agent at all) when the task doesn't actually have them.

**~4 is the practical optimal for a typical task** (e.g. a frontend / backend / tests / infra split). Beyond a handful you hit the named failure mode YC's Light Cone calls "Claude Code cyber psychosis" — workers stepping on each other's edits and generating incompatible implementations of the same interface, faster than you can reconcile them (the coinage is YC's Light Cone; the ~4 figure is directional, not a measured optimum). The fix is the file-ownership discipline above, but the cheaper fix is *not spawning the extra workers in the first place*.

The right count also scales with the *kind* of task — roughly one worker for a fact-find, a few for a comparison, more only for genuinely broad search — and a lead left to size its own fan-out over-invests: Anthropic's research lead "spawned 50 subagents for simple queries" until the budget was written into its prompt. Put the worker budget in the brief; don't trust the model to set it (Anthropic, multi-agent research system).

## Runtime budgets and the synthesis barrier

An unbounded worker is a hang waiting to happen. Give each one a budget and make the barrier tolerant of a worker that blows it:

- **Per-worker step/tool cap.** Bound how many tool calls or steps a worker may take before it must return what it has. A worker that can loop forever will, on the one input that confuses it — and it takes the whole batch's latency hostage.
- **Per-worker timeout → soft-fail at the barrier.** When you wait for all workers (a synthesis barrier), don't block indefinitely on the slowest. Set a per-worker deadline; if one misses it, **proceed with the partial results and note the gap** rather than hanging the whole fan-out on one stuck agent. Best-so-far beats never-returns.
- **A pending-set guard against double-dispatch.** The orchestrating model will sometimes re-dispatch a worker it already launched (it forgets, or a retry fires twice). Track in-flight jobs in a pending set and refuse a duplicate with a recoverable message ("already running") — otherwise two agents do the same write and you're back to last-write-wins.

## Red flags

| Symptom | What it means |
|---|---|
| Two workers touch the same file | Not file-disjoint — one will silently overwrite the other. Re-partition or serialize. |
| A worker needs another worker's output | It's a pipeline dependency, not a fan-out. Sequence them. |
| Briefs reference "the file we just looked at" | The worker can't see it — fresh context. Inline the content or the absolute path. |
| Spawning a worker per tiny item | Over-spawn. Batch items per worker; prefer fewer capable workers. |
| Blocking on all workers before any next step | Premature barrier. Pipeline unless the next step truly needs the full set. |
| The same worker dispatched twice | Double-dispatch. Guard with a pending set; refuse the duplicate. |
| The barrier hangs on one slow worker | No per-worker timeout. Soft-fail it and synthesize the partial results. |
| Splitting a tightly-coupled design across agents | Coupled work — they'll diverge. Keep it single-threaded. |
