# Subagent dispatch table (Codex)

Read this when a step calls for subagents. Each row: the pipeline stage, the
prompt file under `references/agents/`, how many run in parallel, and the
intended model / tool-lock to encode in the spawned agent's instructions.

The routes are `fast` / `ultrafast` / `full` (the query-router emits
`fast`/`full`; `ultrafast` is forced only by an explicit `--ultrafast` flag or
an explicit "ultrafast mode" request). The depth columns scale by route — the
critics fan-out and patcher run on `full` only; `fast`/`ultrafast` use the slim
single critic.

| Stage | Agent prompt file | Parallel | Model | Tool-lock |
|---|---|---|---|---|
| Width sweep (step 2) + depth fetches | `fetcher.md` | wave (2–6) | sonnet | Bash, Read, Write |
| Long-source digest | `source-analyst.md` | per long source | sonnet | Bash, Read, Write |
| Loci analysis (step 4) | `loci-analyst.md` | 2 | sonnet | Bash, Read, Write |
| Depth investigation (step 5) | `depth-investigator.md` | one per locus | sonnet | Bash, Read, Write, spawn_agent |
| Corpus critic (step 8) | `corpus-critic.md` | 1 | sonnet | Bash, Read, Write |
| Triple draft (step 10) | `draft-orchestrator.md` | 3 | opus | Bash, Read, Write |
| Synthesize (step 11) | `synthesizer.md` | 1 | opus | Read, Write |
| Critics (step 12, full) | `dialectic-critic.md`, `depth-critic.md`, `width-critic.md`, `instruction-critic.md`, `assumption-critic.md` | 5 | opus | Bash, Read, Write |
| Critic (fast / ultrafast slim pass) | `light-critic.md` | 1 | sonnet | Bash, Read, Write |
| Patcher (step 14) | `patcher.md` | 1 | sonnet | Read, Edit |
| Fresh review (step 14.5, full) | `fresh-reviewer.md` | 1 | opus | Read |
| Polish (step 15) | `polish-auditor.md` | 1 | sonnet | Read, Edit |
| Readability (step 16) | `readability-recommender.md` | 1 | opus | Read, Write |
