# Compound V — Sources

The grounding spine for the kit. Every load-bearing numeric/factual claim across the skills maps
here to a **public primary source** — a real URL — or is marked a judgment call that needs none.
This file is what makes the **"Grounded — if a claim isn't grounded, it says so"** non-negotiable
(`using-compound-v`, `README.md`) checkable. It also satisfies the format constitution's grounding
rule (`references/skill-format.md`).

## How to read this

Three categories, one per claim:

- **PRIMARY** — an empirical/factual claim attributed to a real-world result; a public primary
  source (URL) is given. This is the bar the kit holds itself to.
- **JUDGMENT-CALL / CANONICAL** — a UI/recipe constant or a well-known historical illustration that
  is vendor-neutral common knowledge or an internal recipe knob. **No citation needed** (e.g.
  `16px`, `0.96` press-scale, `200–300ms`, `N=3` cap, `<40%` context, the compaction-ladder
  thresholds). These ARE the skill, not claims about the world.
- **REMOVED / SOFTEN** — a claim that was wrong, unverified at its source, or being cut. Marked so it
  is not re-cited.

A `skill:line` column locates each claim in the shipped skill. Line numbers are approximate and drift
as skills are edited.

---

## recheck

| Claim (short) | skill:line | Category | Source / note |
|---|---|---|---|
| Cross-model reviewer closes **~74.7%** of a same-model quality gap | `recheck` | **REMOVED** | **Do not cite.** The "cross-model reviewer" section was cut: the decimal was unsourced and contradicts the kit's single-strong-model identity (implementer and reviewer both run on your strongest model). If ever re-added: one sentence, no decimal, with a real cite. |
| Reviewer must be **read-only** (the canonical safe reviewer mutates nothing) | `recheck:19` | PRIMARY | Convergent across production coding agents whose review/oracle paths are read-only by construction. Attribute as "production reviewers are read-only." Mechanism corroborated by Cognition (below). |
| Clean-context reviewer is *smarter* (attention math / Context Rot) and reasons backward from the diff | `recheck:19-21` | PRIMARY | Cognition, "Multi-Agents: What's Actually Working" — https://cognition.ai/blog/multi-agents-working. |
| Devin Review catches **avg 2 bugs/PR, ~58% severe** (logic/edge/security) | `recheck` (vuln-step) | PRIMARY | Cognition, "Multi-Agents: What's Actually Working" — https://cognition.ai/blog/multi-agents-working. The grounded replacement for the removed 74.7% line. |
| **N=3** fix↔recheck cap | `recheck:62` | PRIMARY (borderline recipe-knob) | Production agents converge on ~3 retries (CI-failure loops, lint-fix loops, retry caps). Owning skill is `systematic-debugging`; recheck cross-refs it. |
| Lethal trifecta = private data + untrusted content + exfiltration channel | `recheck:33` | PRIMARY | Simon Willison, "The lethal trifecta for AI agents" — https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/. |
| Signal-density cap **~10-12 findings/pass**; **N=3** cycle cap | `recheck:58,62` | JUDGMENT-CALL | Recipe knobs (signal-density + convergence). No citation needed beyond the N=3 row above. |
| A reviewer must **not flag changes the author clearly made on purpose**, nor hold the diff to a **rigor bar the surrounding code doesn't meet** — a deliberate design choice is not a bug | `recheck:68` | PRIMARY | OpenAI Codex CLI review prompt — `codex-rs/core/review_prompt.md` (public openai/codex repo), review guidelines #8 ("the bug is clearly not just an intentional change by the original author") and #3 ("fixing the bug does not demand a level of rigor that is not present in the rest of the codebase"). |

---

## evals

| Claim (short) | skill:line | Category | Source / note |
|---|---|---|---|
| Mastra drove agent memory toward SOTA across LongMemEval | `evals:51` | PRIMARY | Mastra research page — https://mastra.ai/research/observational-memory. Correct facts: baseline **60.2%** (gpt-4o full-context), LongMemEval has **six** categories (single-session-user / -assistant / -preference, knowledge-update, temporal-reasoning, multi-session), SOTA **94.87%** (gpt-5-mini). Earlier "67% / five buckets / absence-awareness" was wrong — do not re-cite. |
| NurtureBoss: a few categories dominated; fixing the top one (date/scheduling) produced a large jump | `evals:33` | **SOFTEN (directional)** | The precise "3 issues = 60%+ / 33% → 95%" figures are not stated verbatim at the source; the public breakdown differs. Keep directional only. Candidate primary: Hamel Husain, "A Field Guide to Rapidly Improving AI Products" — https://hamel.dev/blog/posts/field-guide/. |
| Teams with a data viewer iterate dramatically faster | `evals:69` | **SOFTEN** | Hamel field-guide (https://hamel.dev/blog/posts/field-guide/) says "game-changer," not "10x." Keep directional. |
| Critiques as few-shot raise judge↔human agreement | `evals:42` | **SOFTEN (no exact decimal)** | Repeated across the Hamel/Shreya canon but no single page states a "15-20%" delta. Cite Hamel "Your AI Product Needs Evals" — https://hamel.dev/blog/posts/evals/ — and say "materially raises agreement." |
| CoCounsel ships at a very high pass bar | `evals:79` | **SOFTEN** | The "999/1000" figure could not be verified; keep directional. Source thread: Jake Heller, "Context Engineering: Lessons from Scaling CoCounsel" (YC talk). |
| CoCounsel: "evals are way easier when you can say `matches word X`" | `evals:22` | PRIMARY | Jake Heller, CoCounsel context-engineering talk (YC). |
| Error analysis is the #1-ROI activity; open-code → axial → count | `evals:24-35` | PRIMARY | Hamel Husain, "A Field Guide to Rapidly Improving AI Products" — https://hamel.dev/blog/posts/field-guide/. |
| Binary pass/fail not 1-5 Likert; align judge to human; **target >90%** agreement; P/R when imbalanced | `evals:41,44` | PRIMARY | Hamel "Your AI Product Needs Evals" — https://hamel.dev/blog/posts/evals/ + Shreya Shankar eval canon. |
| Read **30-100** traces; align on **25-50** examples; grow the set toward hundreds-to-1,000 | `evals:28,44,79` | JUDGMENT-CALL | Recipe knobs (sample sizes for the loop). Directionally from Hamel; the exact ranges are practitioner defaults. No citation needed. |
| Shipping an LLM feature with no eval = #1 cause of failed AI products | `evals:8` | PRIMARY | Hamel field-guide thesis — https://hamel.dev/blog/posts/field-guide/; restated as `startup-taste`'s verifier-first gate. |
| The same aligned judge can be reused as a **runtime gate** via a generate→grade→revise loop (judge returns pass / needs-revision + critique; agent retries on needs-revision with the critique as a fix-list); the loop **must be bounded** (e.g. 3 attempts then accept-with-flag) because unbounded retry-until-pass spins forever | `evals:44` | PRIMARY | Anthropic public anthropic-cookbook evaluator-optimizer pattern (evaluator emits PASS / NEEDS_IMPROVEMENT / FAIL + `<feedback>`); public `anthropic` SDK managed-agents `define_outcome` grader ("Eval→revision cycles before giving up. Default 3, max 20"; verdicts satisfied / needs_revision / max_iterations_reached). Corroborated by Datadog's CrewAI/AI-growth talk: a high-quality grader "triggers second-pass refinement when quality is below threshold." |
| Trajectory evals should pin **only the tool calls the task truly requires**; over-specifying the trajectory turns the eval into a brittle change-detector (breaks on a legitimate tool refactor; marks resourceful recovery as failure) — when the goal is reachable many ways, assert on the final result, not the path | `evals:91` | PRIMARY | Scott Yak, Datadog — DeepLearning.AI "MCP Server Evals Deep Dive" (trajectory strictness EXACT / IN_ORDER / ANY_ORDER; assert on result when the path is non-unique). |

---

## context-engineering

This is the kit's best-grounded skill — every load-bearing number was verified exact against its
public primary source.

| Claim (short) | skill:line | Category | Source / note |
|---|---|---|---|
| Token usage *alone* explains **~80%** of agent-performance variance (token + tool-call + model ≈ **95%**); multi-agent uses **~15×** more tokens than chat | `context-engineering:10` | PRIMARY | Anthropic, "How we built our multi-agent research system" — https://www.anthropic.com/engineering/multi-agent-research-system (verbatim: "token usage by itself explains 80% of the variance"; "three factors explained 95% of the performance variance"; "multi-agent systems use about 15× more tokens than chats"). |
| The instruction file (CLAUDE.md/AGENTS.md) is scoped to its directory subtree (deeper wins; root→cwd chain preloaded); hold only durable load-bearing facts; keep it small (always-loaded = paid every turn), single-source-of-truth, prune on a cadence; treat a persisted fact as a hint, verify on contradiction | `context-engineering:68-71` | PRIMARY | AGENTS.md open spec — https://agents.md ("scope … is the entire directory tree"; "more-deeply-nested … take precedence"; content = run/test commands, code organization, conventions). Keep-small/prune anchored by Anthropic "Effective context engineering" (above); single-source-of-truth corroborated by Cognition, "Multi-Agents: What's Actually Working" — https://cognition.ai/blog/multi-agents-working. "Hint, not ground truth" = durable judgment-call. |
| Observation masking: **52% cheaper, +2.6% solve-rate** | `context-engineering:47` | PRIMARY | arXiv 2508.21433, "The Complexity Trap" (JetBrains; NeurIPS 2025; Qwen3-Coder 480B) — https://arxiv.org/abs/2508.21433. |
| Masking is "as good as summarization at a fraction of the cost" (not "strictly better") | `context-engineering:47` | **SOFTEN (framing, not number)** | The source's thesis is masking is *as good as* summarization at a fraction of the cost ("matching, sometimes slightly exceeding"), NOT strictly better. The 52%/+2.6% numbers are correct; only a superlative would overstate. https://arxiv.org/abs/2508.21433. |
| Tool-result clearing took one workload **335K → 173K** peak tokens | `context-engineering:48` | PRIMARY | Anthropic Claude Cookbooks / API tool-use context-management (`clear_tool_uses_20250919`) — https://github.com/anthropics/claude-cookbooks. |
| Context Rot: recall **~40% down by ~170K tokens** on some tasks | `context-engineering:22` | PRIMARY | Chroma, "Context Rot" technical report — https://research.trychroma.com/context-rot (attributed inline in the skill). |
| Attention scales as **n²** pairwise relationships; "attention budget" | `context-engineering:22` | PRIMARY | Anthropic, "Effective context engineering for AI agents" — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (verbatim). |
| Agent traffic ~**100:1** input:output; cached input ~**10×** cheaper ($0.30 vs $3/MTok) | `context-engineering:56` | PRIMARY | Manus, "Context Engineering for AI Agents: Lessons from Building Manus" — https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus (verbatim "around 100:1", "10x difference"). |
| Mask tool logits don't remove; append-only; deterministic JSON; todo.md recitation vs lost-in-the-middle | `context-engineering:50,52,59-61` | PRIMARY | Manus blog (all verbatim) — https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus. |
| Sub-agent returns a distilled **~1–2K-token** digest | `context-engineering:65` | PRIMARY | Anthropic "Effective context engineering" (verbatim "often 1,000–2,000 tokens") — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents. |
| Claude Code splits its prompt on a dynamic boundary; drops `CLAUDE.md` up front, glob/grep JIT | `context-engineering:32,41` | PRIMARY | Anthropic "Effective context engineering for AI agents" (Claude Code as the worked example) — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents. |
| Working context **< 40%**; clear at ~50K, compact at ~180K; keep last **~10** turns / **6** recent tool-uses | `context-engineering:12,49,80` | JUDGMENT-CALL | Compaction-ladder recipe knobs (tuning defaults, not empirical claims). The optimal-window ≈ last 10 turns does trace to arXiv 2508.21433. No citation needed. |

---

## startup-taste

| Claim (short) | skill:line | Category | Source / note |
|---|---|---|---|
| Wrapper-class apps sit far lower on retention than category leaders | `startup-taste:39` | **SOFTEN (directional)** | Stated directionally in the skill (not a pinned figure). The earlier "60–85% vs ~14% DAU/MAU" decimals are not cited to a public source — keep directional. |
| Perplexity built its own index → near-zero URL overlap with competitors | `startup-taste:60` | PRIMARY (directional) | Source: Aravind Srinivas, "How To Build The Future: Aravind Srinivas" (YC). The precise "1.4%" decimal is not pinned to a public line; skill says "near-zero." |
| v0 took one model to error-free via four engineering layers (a large jump, no model upgrade) | `startup-taste:69` | PRIMARY (directional) | "Lessons from building Vercel v0 and the d0 agent" — https://www.youtube.com/watch?v=_f2WpsmW76Y. The exact "65→94%" figure is not pinned; skill says "a large jump." |
| Jobs cut Apple **350 products → 10** | `startup-taste:30` | JUDGMENT-CALL | Well-known historical illustration; directionally exact. Optional cite: Jobs WWDC 1997 — https://www.youtube.com/watch?v=_LsvdlaF5_k. |
| Granola cut **half its features** to expose the core interaction | `startup-taste:30` | JUDGMENT-CALL / illustration | "How to Build a Beloved AI Product: Granola" — https://www.youtube.com/watch?v=IcbuTTVUY7M. |
| Figma built a WebGL renderer + multiplayer protocol for **~4 years**; the tool was then inevitable | `startup-taste:42` | JUDGMENT-CALL / illustration | Dylan Field / Figma, Latent Space — https://www.latent.space/p/figma. |
| **4,000** good verifiable examples beat **4M** low-quality ones | `startup-taste:66` | JUDGMENT-CALL (maxim) | Stat-shaped "bitter-lesson taste residue" (quality + verifiability > quantity). The specific 4K/4M is illustrative, not a measured result. |
| Perplexity outgrew the Bing API; Cursor forked VS Code (extension API blocked speculative edit) | `startup-taste:60` | PRIMARY | Aravind Srinivas (YC) + Michael Truell, Cursor talks. Historical/architectural fact about owning the ceiling layer. |
| Building stopped being the long pole ~2026 (quarter-in-2021 → weekend now) | `startup-taste:10` | JUDGMENT-CALL | The kit's stated thesis/stance (estimate hygiene), not a measured datum. No citation needed. |
| Validate an AI idea on a prompted frontier model before fine-tuning/collecting data ("Fire, Ready, Aim") | `startup-taste:71` | PRIMARY | swyx, "The Rise of the AI Engineer" — https://www.latent.space/p/ai-engineer. |
| Verifier-first: no eval = #1 cause of failed AI products | `startup-taste:65-66` | PRIMARY | Hamel field-guide — https://hamel.dev/blog/posts/field-guide/ (same as `evals:8`). |
| Inaction is a hidden risk that feels safe; often easier to do a hard thing that matters than an easy thing that doesn't | `startup-taste:21` | PRIMARY | Sam Altman, "What I Wish Someone Had Told Me" — https://blog.samaltman.com/what-i-wish-someone-had-told-me. |
| The best ideas are *noticed* by someone who has lived in a domain for years, not produced in a list-making session; provenance is a tell | `startup-taste:50` | PRIMARY | Paul Graham, "How to Do Great Work" — https://paulgraham.com/greatwork.html. |
| Persistence vs obstinacy split on one axis: persistent = fixed on the goal, flexible on means; obstinate = fixed on means, driven by ego | `startup-taste:56` | PRIMARY | Paul Graham, "The Right Kind of Stubborn" — https://paulgraham.com/persistence.html. |

---

## product-taste

The numeric checklist here is the **opposite** of ungrounded — these are testable,
industry-canonical UI constants. They need no citation; they ARE the skill. The two named-product
anchors carry sources.

| Claim (short) | skill:line | Category | Source / note |
|---|---|---|---|
| Dialogs scale from **~0.8** (not 0); buttons depress to **~0.96** | `product-taste:39-40` | JUDGMENT-CALL / CANONICAL | Canonical UI craft constants. Corroborated by Rauno Freiberg's interface checklist — https://github.com/raunofreiberg/interfaces. No citation needed. |
| **16px** minimum input font (iOS auto-zoom threshold) | `product-taste:41` | JUDGMENT-CALL / CANONICAL | Verifiable platform fact (iOS zooms inputs < 16px). Rauno interfaces checklist — https://github.com/raunofreiberg/interfaces. No citation needed. |
| `tabular-nums` on timers/columns; pause off-screen; full-row hit targets | `product-taste:40,42,43` | JUDGMENT-CALL / CANONICAL | Canonical interface rules (Rauno `interfaces`). No citation needed. |
| Animate only **`transform`/`opacity`** (GPU composite path); **60fps** | `product-taste:56,50` | JUDGMENT-CALL / CANONICAL | Browser-rendering common knowledge (compositor-only properties). No citation needed. |
| Durations **200–300ms**, `ease-out` for enter/exit | `product-taste:56` | JUDGMENT-CALL / CANONICAL | Canonical motion-design constant. No citation needed. |
| Latency: **<200ms** instant / **>500ms** slow / **<50ms** the bar (Linear) / Cursor tab ~**260ms** | `product-taste:62-64` | JUDGMENT-CALL + PRIMARY anchors | The perceptual cliffs (<200/<500/<50) are canonical HCI constants — no citation. Named anchors: Linear (Karri Saarinen, "How We Redesigned the Linear UI" — https://linear.app/now/how-we-redesigned-the-linear-ui); Cursor ~260ms tab completion (Cursor talks). |
| Linear collapsed **98 color variables → 3** | `product-taste:74` | PRIMARY | Karri Saarinen, "How We Redesigned the Linear UI" — https://linear.app/now/how-we-redesigned-the-linear-ui (also "Inside Linear" talk — https://www.youtube.com/watch?v=4muxFVZ4XfM). |
| The 98→3 collapse works because the palette is built in **LCH, not HSL**: LCH is perceptually uniform (same lightness looks equally light across hues), so one base/accent/contrast triple generates every theme incl. high-contrast a11y; HSL's lightness lies, forcing per-color hand-tuning | `product-taste:76` | PRIMARY | Linear, "How We Redesigned the Linear UI" — https://linear.app/now/how-we-redesigned-the-linear-ui (extends the 98→3 row above). |
| Habituation blinds you to normalized flows; the worst flaws are the ones you've stopped seeing — view your own product as a first-time user / stay a beginner | `product-taste:19` | PRIMARY | Tony Fadell, "The first secret of design is … noticing" (TED) — https://www.ted.com/talks/tony_fadell_the_first_secret_of_design_is_noticing. |
| Open menus/dropdowns on **`mousedown`** not `click` — firing on press-down shaves perceptible delay, makes the menu feel instant | `product-taste:45` | PRIMARY | Rauno Freiberg, Web Interface Guidelines — https://github.com/raunofreiberg/interfaces. |
| Teenage Engineering's fixed palettes as a generative force | `product-taste:74` | PRIMARY (illustration) | "Config 2024: A Look Inside Teenage Engineering." Illustration. |
| Snapchat runs at several deliberate taps/second (reduce cognitive load, not clicks) | `product-taste:69` | JUDGMENT-CALL (illustration) | Well-known product example; illustrative. No hard citation needed. |
| Older Safari renders `outline` without following `border-radius` (use `box-shadow`) | `product-taste:31` | JUDGMENT-CALL / CANONICAL | Canonical front-end knowledge (focus-ring fix). No citation needed. |
| Designers measurably improve; an 8-year-old's output ≠ a master's (taste is objective) | `product-taste:8` | JUDGMENT-CALL (stance) | The skill's argued stance that taste is learnable, not a cited datum. Thematic source: Chris Olah, "Research Taste" — https://colah.github.io/notes/taste/. |
| Product judgment is domain-specific and does not transfer; strong practitioners are good at saying when they don't have it — so in an unlived domain, flag missing calibration rather than bluffing a crisp verdict | `product-taste:22` | PRIMARY | Paul Adams (CPO, Intercom), "Product Judgment" — https://www.intercom.com/blog/product-judgment/. |

---

## designing-agents

The strongest-grounded skill in the AI-design group; spine verified near-verbatim against primary
sources.

| Claim (short) | skill:line | Category | Source / note |
|---|---|---|---|
| Workflow vs agent definitions; the six workflow patterns; "add complexity only when it demonstrably improves outcomes" | `designing-agents:11-14,32-39,8` | PRIMARY | Anthropic, "Building effective agents" — https://www.anthropic.com/engineering/building-effective-agents (exact quotes). |
| A working coding agent is **under ~400 lines**, **~190 after three tools**; "an LLM + a loop + tools, no secret" | `designing-agents:66,68` | PRIMARY | ghuntley, "How to build a coding agent" ("just ~300 lines in a loop") — https://ghuntley.com/agent/. Exact line counts are the kit's own from the build. |
| Per-step reliability: **0.9^100 ≈ 0** (≈0.003%); need ~**99.9%/step**; each nine ~an order of magnitude harder | `designing-agents:76` | PRIMARY (math) + JUDGMENT | The arithmetic is standard. The "march of nines" framing is Karpathy, Dwarkesh interview — https://www.dwarkesh.com/p/andrej-karpathy. |
| Invest as much in the agent-computer interface (ACI) as in HCI; keep tools dumb/deterministic | `designing-agents:70,84` | PRIMARY | Anthropic "Building effective agents" (ACI section) — https://www.anthropic.com/engineering/building-effective-agents. |
| Skip high-level agent SDKs; target the provider API directly | `designing-agents:72` | PRIMARY | Anthropic "Building effective agents" ("reduce abstraction layers… use LLM APIs directly"); corroborated by Cognition. |
| CoT is not a faithful trace; "show your reasoning" is not a correctness check | `designing-agents:80,110` | PRIMARY | Anthropic, "Reasoning models don't always say what they think" — https://www.anthropic.com/research/reasoning-models-dont-always-say-what-they-think. |
| Read-only subagents "mostly resemble tool calls rather than true multi-agent collaboration" | `designing-agents:39` | PRIMARY | Cognition, "Multi-Agents: What's Actually Working" — https://cognition.ai/blog/multi-agents-working (verbatim). |
| Swarm demos (200k-LOC browser, C compiler) have a verifiable success criterion; real software scales human taste | `designing-agents` (stance) | PRIMARY | Cognition, "Multi-Agents: What's Actually Working" — https://cognition.ai/blog/multi-agents-working. |
| "You're a senior software engineer" / "think for longer" = gimmicky prompt-engineering | (cross-kit red flag) | PRIMARY | Cognition, "Multi-Agents: What's Actually Working" — https://cognition.ai/blog/multi-agents-working. |
| When retrying a flaky LLM/agent step, retrying with the same model often reproduces the failure; failing over to a different model (cross-model fallback chain) fixes it | `designing-agents:78` | PRIMARY | Warp engineering blog — https://www.warp.dev/blog/swe-bench-verified ("We originally attempted to retry with the same model, and found that this often produced repeat failures" → cross-model fallback chain: Sonnet → Claude 3.7 → Gemini 2.5 Pro → GPT-4.1). |
| **≈10** is a sane default turn ceiling for an agentic loop (bound the loop; on the last step force-finish) | `designing-agents:84` | PRIMARY | OpenAI Agents SDK — run configuration's documented default `DEFAULT_MAX_TURNS = 10` (the framework's own shipped default max-turns value; raises `MaxTurnsExceeded` once exceeded). |
| Before adding agents, look at where cost/variance go: **three factors explain ~95% of agent-performance variance, token spend alone ~80%** — "spend more tokens on the hard part" beats "add another agent" | `designing-agents:80` | PRIMARY | Anthropic, "How we built our multi-agent research system" — https://www.anthropic.com/engineering/multi-agent-research-system (verbatim: "three factors explained 95% of the performance variance"; "token usage by itself explains 80% of the variance"). Same datum as the context-engineering row above. |

---

## batched-implementation

| Claim (short) | skill:line | Category | Source / note |
|---|---|---|---|
| Superpowers spends **~16 dispatches for a 5-task plan** (fresh agent/task + 2 reviewers + final) | `batched-implementation:18`, `README.md` | PRIMARY | Direct audit of the public superpowers skill set — https://github.com/obra/superpowers. |
| Batching **2-3 tasks/agent** cuts dispatches **~60%** with no loss of isolation | `batched-implementation:8,18,27` | JUDGMENT-CALL (recipe) | The 2-3 batch size and ~60% are the kit's own design recipe derived from the ~16→~4 comparison. Not an external empirical claim. No citation needed. |
| For coupled, latency-sensitive work, one strong agent beats planner→executor→critic fan-out | `batched-implementation:20` | PRIMARY | Convergent finding from production orchestration practice; corroborated by Cognition (below). |
| Writes stay single-threaded; agents contribute *intelligence*, not *actions*; serial unless file-disjoint | `batched-implementation:52-56` | PRIMARY | Cognition, "Don't Build Multi-Agents" + "Multi-Agents: What's Actually Working" — https://cognition.ai/blog/dont-build-multi-agents, https://cognition.ai/blog/multi-agents-working. |
| **N=3** fix↔recheck cycle cap | `batched-implementation:49` | PRIMARY (borderline recipe) | Same N=3 as `recheck`/`systematic-debugging` (see recheck table). |
| When a convention matters, **paste the exemplar** (the file/snippet to imitate) into the dispatch prompt, not a bare "follow conventions" — a fresh-context agent regresses to model defaults for any convention it wasn't shown | `batched-implementation:34` | PRIMARY | Anthropic, "Building effective agents" — https://www.anthropic.com/engineering/building-effective-agents ("a good tool definition often includes example usage"; examples anchor behavior). Corroborated by the leaked OpenAI Codex system prompt's anti-default rules (no purple/dark-mode bias, no default `useMemo`/`useCallback`) — models default to generic patterns absent a local anchor. |
| A batch of **structurally similar** tasks risks a few-shot rut — a fresh-context implementer "falls into a rhythm" and adapts later tasks from earlier ones; the brief must name what *differs* per task | `batched-implementation:28` | PRIMARY | Manus, "Context Engineering for AI Agents" — https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus (verbatim: "the agent often falls into a rhythm—repeating similar actions… leads to drift, overgeneralization, or sometimes hallucination"; "don't few-shot yourself into a rut"). |

---

## writing-plans

| Claim (short) | skill:line | Category | Source / note |
|---|---|---|---|
| Build failures cluster at the **edges** — setup (environment/dependencies, first ~5%) and the finish (deploy/env-vars/prod-config, last ~5%) — while the middle application logic is reliable; front-load setup and deploy tasks | `writing-plans:30` | PRIMARY | Amjad Masad (Replit CEO) on the a16z podcast — https://www.youtube.com/watch?v=g-WeCOUYBrk. |
| When a load-bearing assumption proves false mid-build, the implementer **stops and reports back** rather than improvising or looping, with an explicit attempt budget (surface after ~3 failed attempts) — an execution→planning backtrack | `writing-plans:73` | PRIMARY | Cognition Devin (published/leaked system prompt): "Return to PLANNING if you discover unexpected complexity" and "ask the user for help if CI does not pass after the third attempt." Google Antigravity agent formalizes the same EXECUTION→PLANNING backtrack. Shares the **N=3** budget with the recheck table. |
| A plan must **forbid editing a test to make it pass**: when a test fails the suspect is the code under test, not the test; change the test only if the task is explicitly about the test | `writing-plans:95` | PRIMARY | Cognition Devin (published/leaked system prompt): "never modify the tests themselves, unless your task explicitly asks … Always first consider that the root cause might be in the code you are testing rather than the test itself." |
| Pair each verification criterion with the **negative constraint** that rules out the degenerate/cheat solution (tests pass AND no assertion weakened, no output hardcoded) — the code-side defense to the no-edit-the-test rule | `writing-plans:95` | PRIMARY | a16z — Jacob Steinhardt (UC Berkeley) on specification gaming: coding agents that "pass tests" by hardcoding expected outputs; "a technically correct answer that violates the intent." a16z podcast, video KSgPNVmZ8jQ. |
| Plans must **flag destructive/irreversible actions up front** in the preamble (a User-Review flag) so the human signs off before the implementer executes autonomously | `writing-plans:73` | PRIMARY | Google Antigravity's leaked `implementation_plan.md` template mandates a `## User Review Required` section as the plan's second block: "Document anything that requires user review or clarification, for example, breaking changes or significant design decisions. Use GitHub alerts (IMPORTANT/WARNING/CAUTION) to highlight critical items." |

---

## writing-prd

| Claim (short) | skill:line | Category | Source / note |
|---|---|---|---|
| The durable PRD section grammar — problem/context, goal, core functions, **non-goals**, architecture — is convergent across the canonical engineering-doc formats | `writing-prd` | PRIMARY | Google Engineering Practices "Design Docs / Context and Scope"; Rust RFC template (guide-level explanation, unresolved questions); ADR (alternatives considered); Amazon PR-FAQ. Cross-format convergence, not one source. |
| A PRD is **institutional memory** — the durable record of what the product is and why, captured once so a cold reader (human or fresh AI session) doesn't reverse-engineer it | `writing-prd:8` | PRIMARY | prd-pipeline — https://github.com/Timmy-Lane/prd-pipeline ("spec as institutional memory"). Its build machinery (tier routing, multi-critic grill, 9-pass gates, a CLI) is deliberately NOT adopted — that's per-build process, not PRD content. |
| **Prose over bullets** where precision matters (writing forces the thinking a bullet skips); ~2-page cap | `writing-prd` | PRIMARY | Amazon working-backwards / PR-FAQ (narrative memos, no bullets). |
| On supersede, leave a **one-line forward pointer** rather than deleting (cheap decision genealogy), decoupled from any code lifecycle | `writing-prd` | JUDGMENT-CALL | Oxide RFD process (status frontmatter + decision genealogy), adapted as a light touch. |
| **Non-goals** carry the *support boundary* — what the product does for inputs past its scope (reject/escalate), because agents don't reliably ask when uncertain (they assume and proceed) | `writing-prd:22` | PRIMARY | a16z — Jacob Steinhardt (UC Berkeley) on agent failure modes: "current agents do not robustly ask for clarification when uncertain; they tend to make assumptions and proceed"; specification gaming (agents "pass tests" by hardcoding outputs). a16z podcast, video KSgPNVmZ8jQ. Finn/offline-RL OOD citation considered and dropped as too-stretched. |
| Single-source-of-truth, edit-in-place, prune-on-cadence | `writing-prd` | (see context-engineering) | Reuses the AGENTS.md-spec + Anthropic "Effective context engineering" maintenance rules grounded in the context-engineering section; the PRD links to them, doesn't re-derive. |

---

## systematic-debugging

| Claim (short) | skill:line | Category | Source / note |
|---|---|---|---|
| **3-attempt rule** before questioning the design ("production agents converge on ~3 across CI retries, lint-fix loops") | `systematic-debugging:45-47` | PRIMARY (borderline recipe-knob) | This is the **owning skill** for the N=3 claim. Convergent across production coding agents (CI-failure loops, lint-fix loops, retry caps). recheck and batched-implementation cross-ref here. |
| Don't thrash the environment before diagnosing; write a failing reproduction first | `systematic-debugging:33,41` | JUDGMENT-CALL | Standard debugging discipline (root-cause-before-fix); cross-refs `test-driven-development`. No empirical claim. No citation needed. |
| AI/agent code fails silently — a passing-looking result you cannot account for is a bug lead, not a finish; never trust an output you can't explain | `systematic-debugging:18` (Phase 1) | PRIMARY | Andrej Karpathy, "A Recipe for Training Neural Networks" — http://karpathy.github.io/2019/04/25/recipe/ ("neural nets fail silently… never trust a result you can't explain"). |
| A nondeterministic agent/LLM bug that fires intermittently has no single reproducible stack trace; build a small graded example set and treat where it fails across runs as the repro and regression guard — the role a failing test plays for deterministic code | `systematic-debugging:19` (Phase 1) | PRIMARY | Hamel Husain, "Your AI Product Needs Evals" — https://hamel.dev/blog/posts/evals/ (from 30+ production builds; "no eval system" is the #1 reason AI products fail). Cross-refs `compound-v:evals`. |
| Classify a failure before spending a retry: deterministic reds (validation/type/missing-arg/auth) are guaranteed to recur on the same inputs so get zero retries; reserve the retry budget for transient faults (network blip, 503, rate limit) | `systematic-debugging:68` | PRIMARY | Standard production resilience practice (transient-fault handling), e.g. Microsoft Azure Architecture Center "Transient fault handling": retry only faults expected to be short-lived; do not retry faults guaranteed to recur. |
| If you can't state what "correct" looks like, the bug is **underspecification, not a code defect** — pin the expected behavior first, or the symptom shifts as your notion of "right" drifts | `systematic-debugging:41` | PRIMARY | Hamel Husain, "A Field Guide to Rapidly Improving AI Products" — https://hamel.dev/blog/posts/field-guide/ (*criteria drift*: evaluation criteria can't be fully fixed before you look at real outputs). |

---

## test-driven-development

| Claim (short) | skill:line | Category | Source / note |
|---|---|---|---|
| The test is **"five tokens"** of instruction and the model spins on it (Willison) | `test-driven-development:10` | PRIMARY | Simon Willison, "Engineering practices that make coding agents work" (talk) — https://www.youtube.com/watch?v=owmJyKVu5f8. Agentic-coding writing also at https://simonwillison.net/tags/ai-assisted-programming/. |
| TDD bounds the work / is the verifiable signal (the leash for autonomous agents) | `test-driven-development:12-13` | JUDGMENT-CALL (stance) | The kit's reframing of TDD for agents; reasoning, not a cited datum. No citation needed. |
| Tests-after "ratify whatever you wrote, bugs included" | `test-driven-development:92` | JUDGMENT-CALL | Standard TDD rationale. No citation needed. |
| Testing intensity should scale **inversely with how easily a bug is observed**: test database and business-logic layers rigorously (corruption hides for weeks), test the visible frontend lightly (bugs show up in the browser) | `test-driven-development:25` | PRIMARY | Andrew Ng, DeepLearning.AI talk on AI-era engineering. |
| When verifying tests, start with the **narrowest test** for the code you changed (fastest signal), then **widen to the full suite** to confirm nothing else broke | `test-driven-development:65` | PRIMARY | OpenAI Codex CLI agent instructions, published "Testing Philosophy." |
| The model writes the assertion for free; **choosing what to assert (spec fidelity) is the human judgment that now differentiates** — a flawless test against the wrong spec is a worthless suite | `test-driven-development:48` | PRIMARY | Andrew Ng, DeepLearning.AI panel — AI writes tests trivially, so test-spec fidelity becomes the differentiating skill. (Same Ng talk grounding the test-intensity row above.) |
| Wait on a **condition**, not a fixed delay, for async work in tests (poll until true with a timeout cap; never a bare `setTimeout`/`sleep`) | `test-driven-development:99` | JUDGMENT-CALL | Standard async-test discipline; the canonical fix for clock-based test flakiness (Testing Library's `waitFor`/`findBy` polling utilities replace arbitrary timeouts). No empirical decimal claimed. |

---

## using-compound-v

| Claim (short) | skill:line | Category | Source / note |
|---|---|---|---|
| The three compounds: **taste, distribution, a primitive** (master gate) | `using-compound-v:13-14` | JUDGMENT-CALL (kit thesis) | The kit's founding stance, distilled from practitioner founder talks and the top-1% founder canon. Reinforced at `startup-taste:18`, `recheck:27`. Not a single-source empirical claim. No citation needed. |
| Lethal trifecta (flag vulns incl.) | `using-compound-v:18` | PRIMARY | Simon Willison — https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/ (same as `recheck:33`). |
| Tier routing / "overkill is a defect" | `using-compound-v:8,21-28` | JUDGMENT-CALL | The kit's anti-overkill law (constitution Ruling B). No citation needed. |

---

## dispatching-parallel-agents

| Claim (short) | skill:line | Category | Source / note |
|---|---|---|---|
| **~4** is the practical optimal for a typical task; beyond a handful, workers step on each other ("Claude Code cyber psychosis") | `dispatching-parallel-agents:45` | PRIMARY (directional) | YC Light Cone (the "cyber psychosis" coinage). The ~4 figure is directional, not a measured optimum. |
| Each sub-agent is a context firewall; fan-out buys isolation, not just throughput | `dispatching-parallel-agents:10` | JUDGMENT-CALL | Owned by `context-engineering` (sub-agents-as-firewalls). No separate citation needed. |
| Managers/orchestrators default to over-prescription when delegating to agents; brief the **what and constraints, not the how**, line-by-line | `dispatching-parallel-agents:32-35` | PRIMARY | Cognition, "Multi-Agents: What's Actually Working" — https://cognition.ai/blog/multi-agents-working (already cited PRIMARY above for the writes-single-threaded finding). |
| The right worker count **scales with task class** (≈1 for a fact-find, a few for a comparison, more for broad search); a lead left to size its own fan-out over-invests — put the budget in the brief | `dispatching-parallel-agents:47` | PRIMARY | Anthropic, "How we built our multi-agent research system" — https://www.anthropic.com/engineering/multi-agent-research-system (verbatim: "spawning 50 subagents for simple queries"; "Simple fact-finding requires just 1 agent with 3-10 tool calls, direct comparisons might need 2-4 subagents with 10-15 calls each"). |

---

## searching-patterns

| Claim (short) | skill:line | Category | Source / note |
|---|---|---|---|
| When a repo already has an established shape (house wrapper, AGENTS.md/CLAUDE.md rule, neighboring-file pattern), that **local convention overrides** the external canonical pattern — match the local shape, don't import a clashing "correct" one | `searching-patterns:25` | PRIMARY | AGENTS.md spec — https://agents.md (AGENTS.md carries code-style guidelines for in-scope code; "explicit user chat prompts override everything" — a local instruction layer that governs the diff). OpenAI Codex / Cursor system prompts: "If working within an existing website or design system, preserve the established patterns, structure, and visual language." |
| An official **conformance suite** (a protocol, wire format, standard's test vectors) is the strongest primary source — precise, executable, drift-free; point the implementer at it and write code until it passes | `searching-patterns:32` | PRIMARY | Simon Willison, "Engineering practices that make coding agents work" (talk) — https://www.youtube.com/watch?v=owmJyKVu5f8 ("if there's an existing language-agnostic test suite… WebAssembly has a very detailed specification which includes hundreds of tests… write code until this test suite passes, and it kind of will"). |

---

## verification-before-completion

| Claim (short) | skill:line | Category | Source / note |
|---|---|---|---|
| The reason agents confidently ship broken work is an **observation gap, not an action gap**; closing the feedback loop (e.g. a browser-screenshot channel for a UI the agent cannot otherwise see) is one of the biggest unlocks for autonomous task length | `verification-before-completion:14` | PRIMARY | Tanveer Mittal & Utkarsh Lamba (Anthropic), "Claude Agent SDK Deep Dive" (DeepLearning.AI): developers over-optimize for the action pillar and under-invest in the feedback pillar — Claude builds a React app for 20 minutes, the layout is wrong, but it cannot observe this without a browser-screenshot mechanism; closing that loop is one of the biggest unlocks for autonomous task length. |

---

## finishing

| Claim (short) | skill:line | Category | Source / note |
|---|---|---|---|
| **Local-green is not CI-green:** a post-push concern worth a dedicated step — monitor remote PR checks rather than declaring done at PR creation | `finishing:35` | PRIMARY | Warp's production coding agent ships a public `diagnose-ci-failures` skill, and Claude Code provides autonomous PR-check monitoring — both encode local-green ≠ CI-green as a first-class post-push concern. |
| Before a destructive discard, the at-risk work to surface is precisely **uncommitted changes, untracked files, and unpushed commits** | `finishing:39` | PRIMARY | Anthropic's published Claude Code worktree auto-cleanup refuses to remove a worktree unless it has no uncommitted changes, no untracked files, and no unpushed commits — the same three categories that define unrecoverable work. |

---

## agent-security

| Claim (short) | Category | Source / note |
|---|---|---|
| The lethal trifecta (private data + untrusted content + exfiltration) as the core threat | PRIMARY | Simon Willison — https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/. |
| Threat taxonomy: memory-poisoning, tool-misuse, privilege-compromise, excessive-agency, indirect injection | PRIMARY | Google, "Securing Your AI Agents" — https://cloud.google.com/transform/securing-your-ai-agents. |
| Source-trust hierarchy (system > developer > user > tool > page) as the constructive defense | PRIMARY | Source-trust primitive convergent across production deep-research agents. |
| Sandbox model-written code (AST-walk before exec; microVM > container); SSRF/RCE defenses; secret-redaction; deploy-endpoint auth-gate | PRIMARY | Convergent across production agent frameworks (SSRF proxies, deploy-endpoint auth-gates, secret-redaction). |
| Reviewer can question an insecure pattern the user asked for | PRIMARY | Cognition, "Multi-Agents: What's Actually Working" — https://cognition.ai/blog/multi-agents-working. |
| Credentials never enter the model's context (not prompt, args, or results); the model passes a **handle** (session ID / secret name) and the tool resolves it out of view | PRIMARY | Google ADK security workshop (Adam Idelman) — https://www.youtube.com/watch?v=jZXvqEqJT7o ("authentication should happen as much as possible within a specific tool… you don't want the agent to handle credentials directly"; agent passes a session ID, the tool fetches the token). |
| Apply the trifecta at **tool-selection** time: one tool — an MCP server especially — can hold all three legs at once, so vet each before enabling it | PRIMARY | Simon Willison, "The lethal trifecta" — https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/ (MCP "encourages users to mix and match tools"; GitHub MCP exploit — https://simonwillison.net/2025/May/26/github-mcp-exploited/). |

---

## Primary-source index (deduplicated)

The recurring public primary URLs, for quick verification:

- **Anthropic — Building effective agents:** https://www.anthropic.com/engineering/building-effective-agents
- **Anthropic — Effective context engineering for AI agents:** https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- **Anthropic — How we built our multi-agent research system (~80% variance, ~15× tokens):** https://www.anthropic.com/engineering/multi-agent-research-system
- **Anthropic — Reasoning models don't always say what they think:** https://www.anthropic.com/research/reasoning-models-dont-always-say-what-they-think
- **Anthropic — Claude Cookbooks (tool-use context management, 335K→173K):** https://github.com/anthropics/claude-cookbooks
- **Cognition — Don't Build Multi-Agents:** https://cognition.ai/blog/dont-build-multi-agents
- **Cognition — Multi-Agents: What's Actually Working (2 bugs/PR, ~58% severe; clean-context reviewer; verifiable-criterion):** https://cognition.ai/blog/multi-agents-working
- **Cognition Devin — published/leaked system prompt (test-protection; EXECUTION→PLANNING backtrack; third-attempt CI rule):** judgment-call / canonical (published agent prompt; corroborated by Google Antigravity's EXECUTION→PLANNING backtrack)
- **Manus — Context Engineering for AI Agents (100:1, 10×, cache discipline):** https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus
- **Chroma — Context Rot (~40% by ~170K):** https://research.trychroma.com/context-rot
- **arXiv 2508.21433 — The Complexity Trap (observation masking 52%/+2.6%):** https://arxiv.org/abs/2508.21433
- **Mastra — Observational Memory (60.2%→94.87%, six LongMemEval categories):** https://mastra.ai/research/observational-memory
- **Hamel Husain — Your AI Product Needs Evals:** https://hamel.dev/blog/posts/evals/
- **Hamel Husain — A Field Guide to Rapidly Improving AI Products:** https://hamel.dev/blog/posts/field-guide/
- **Simon Willison — The lethal trifecta:** https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/
- **Simon Willison — Engineering practices that make coding agents work (talk, "five tokens"):** https://www.youtube.com/watch?v=owmJyKVu5f8
- **Karpathy — Dwarkesh interview ("march of nines"):** https://www.dwarkesh.com/p/andrej-karpathy
- **Karpathy — A Recipe for Training Neural Networks (neural nets fail silently; never trust a result you can't explain):** http://karpathy.github.io/2019/04/25/recipe/
- **Warp — SWE-bench Verified eng. blog (same-model retry → repeat failures; cross-model fallback chain):** https://www.warp.dev/blog/swe-bench-verified
- **ghuntley — How to build a coding agent:** https://ghuntley.com/agent/
- **Sam Altman — What I Wish Someone Had Told Me (inaction is a hidden risk):** https://blog.samaltman.com/what-i-wish-someone-had-told-me
- **Paul Graham — How to Do Great Work (best ideas are noticed, not brainstormed):** https://paulgraham.com/greatwork.html
- **Paul Graham — The Right Kind of Stubborn (persistence vs obstinacy):** https://paulgraham.com/persistence.html
- **Tony Fadell — The first secret of design is … noticing (TED; habituation/beginner):** https://www.ted.com/talks/tony_fadell_the_first_secret_of_design_is_noticing
- **Amjad Masad / Replit — a16z podcast (build failures cluster at the edges):** https://www.youtube.com/watch?v=g-WeCOUYBrk
- **AGENTS.md spec (local convention overrides external canonical):** https://agents.md
- **Linear — How We Redesigned the Linear UI (98→3 colors, <50ms):** https://linear.app/now/how-we-redesigned-the-linear-ui
- **Rauno Freiberg — interfaces (16px, 0.8/0.96, tabular-nums — canonical UI constants):** https://github.com/raunofreiberg/interfaces
- **Vercel — Lessons from building v0 and d0 (~65%→94%):** https://www.youtube.com/watch?v=_f2WpsmW76Y
- **Aravind Srinivas / Perplexity (owned index, near-zero URL overlap):** YC "How To Build The Future: Aravind Srinivas"
- **Jake Heller / CoCounsel (matches-word-X, very high pass bar):** YC "Context Engineering: Lessons from Scaling CoCounsel"
- **Dylan Field / Figma (~4yr renderer, taste-as-moat):** https://www.latent.space/p/figma
- **Google — Securing Your AI Agents:** https://cloud.google.com/transform/securing-your-ai-agents
- **Superpowers skill set (audited for the leanness comparison):** https://github.com/obra/superpowers
- **Paul Graham — How to Think for Yourself (felt-certainty; conventional minds are surest they think for themselves):** https://paulgraham.com/think.html — grounds `critical-thinking` gate 1.
- **Charlie Munger — steelman standard ("you don't own an opinion until you can argue the other side better than its proponent"):** widely attributed (Munger, USC Law 2007 / Poor Charlie's Almanack) — maxim; grounds `critical-thinking` gate 2.
- **Karl Popper (falsification — a claim must state what would refute it) + Sébastien Bubeck et al., "Sparks of AGI" (probe breadth-first for the limit, not for demos):** Popper canonical; Bubeck https://arxiv.org/abs/2303.12712 — grounds `critical-thinking` gate 3.
- **OpenAI Codex CLI — review prompt (`codex-rs/core/review_prompt.md`, don't-flag-intentional / no-extra-rigor):** public openai/codex repo — grounds `recheck:68`.
- **OpenAI Codex CLI — published "Testing Philosophy" (narrowest test first, then widen):** OpenAI Codex agent instructions — grounds `test-driven-development:65`.
- **OpenAI Agents SDK — `DEFAULT_MAX_TURNS = 10` (shipped default turn cap):** framework run-config default — grounds `designing-agents:84`.
- **Paul Adams (Intercom) — "Product Judgment" (domain-specific, doesn't transfer):** https://www.intercom.com/blog/product-judgment/ — grounds `product-taste:22`.
- **Google Antigravity — leaked `implementation_plan.md` template (`## User Review Required` second block):** grounds `writing-plans:73` (also corroborates the EXECUTION→PLANNING backtrack above).
- **Anthropic — "Claude Agent SDK Deep Dive" (DeepLearning.AI; Mittal & Lamba — observation gap, feedback-loop unlock):** grounds `verification-before-completion:14`.
- **Datadog / Scott Yak — DeepLearning.AI "MCP Server Evals Deep Dive" (trajectory strictness; second-pass refinement below threshold):** grounds `evals:91` and the judge-as-runtime-gate row.
- **Anthropic — anthropic-cookbook evaluator-optimizer pattern + `anthropic` SDK `define_outcome` grader (bounded generate→grade→revise, default 3 / max 20):** https://github.com/anthropics/anthropic-cookbook — grounds `evals:44`.
- **Warp — `diagnose-ci-failures` skill + Claude Code PR-check monitoring (local-green ≠ CI-green):** grounds `finishing:35`.
- **Anthropic — Claude Code worktree auto-cleanup (no uncommitted/untracked/unpushed = removable):** grounds `finishing:39`.

### Removed / do-not-cite

- **recheck cross-model "74.7% / +4.8%"** — section cut; unsourced. Do not re-cite.
- **evals Mastra "67% / five buckets / absence-awareness"** — verified wrong; use 60.2% / six
  categories / 94.87% from the Mastra source above.
- **evals NurtureBoss "33% → 95%" / "60%+ from three"** — unverified at the cited source; keep
  directional only.
