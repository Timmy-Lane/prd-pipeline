## Execution model on Codex (READ FIRST)

This skill is the Codex build of the bad-research pipeline. The mechanics below
override any Claude-Code-specific phrasing in the sections that follow.

- **Step procedures are bundled reference files.** Every step that the body
  refers to as a separate skill lives in `references/` inside THIS skill dir
  (e.g. `references/5-depth-investigation.md`). To "run a step," READ that
  reference file with your native file-read tool at the moment the step runs.
  There is no separate `Skill` tool and no `.codex/skills` lazy install on
  Codex — ignore any bootstrap step that tells you to materialize step skills
  per-project; the procedures are already here.
- **Subagents are dispatched with `spawn_agent`.** Each subagent's prompt lives
  in `references/agents/<name>.md`. To dispatch one: read that file, append the
  per-call inputs (verbatim `research_query`, pipeline position, file paths),
  and call `spawn_agent` with the result as an inline prompt. Collect results
  with `wait_agent`; free finished slots with `close_agent`. Parallel fan-outs
  (fetcher waves, two loci-analysts, per-locus depth-investigators, the five
  step-12 critics) = multiple `spawn_agent` calls. See
  `references/dispatch-table.md` for which agent runs at which stage and how
  many run in parallel.
- **Model & tool-locks.** Codex runs a single model. Where an agent file names
  `model: opus` use your highest reasoning effort; `model: sonnet` = default
  effort. Where an agent file names a restricted tool set (e.g. `tools: Read`
  for the fresh-reviewer, `Read, Edit` for the patcher / polish auditor,
  `Read, Write` for the synthesizer / readability recommender), HONOR that
  restriction in the spawned agent's instructions — do not let it Write or run
  shell commands beyond what the lock allows. The pipeline's CLI gates
  (`bad uncited-gate`, `bad recitation-gate`, grounding, patch-log) enforce the
  rest and are unchanged.
- **Task tracking** uses `update_plan` (not a separate todo tool).
- **The `bad` CLI is identical to every other platform.** Run `bad fetch`,
  `bad search`, `bad note ...` etc. through your native shell tool exactly as
  the step procedures describe.
