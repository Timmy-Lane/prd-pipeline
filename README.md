# prd-pipeline

A tier-adaptive **feature-development pipeline** for Claude Code: idea → spec/PRD → adversarial grill → confirmed plan → parallel worktree build → verified ship. Drops into any repo.

This repo is a **self-contained Claude Code plugin marketplace**. One `/plugin install` gives you the whole stack — you don't fetch anything separately:

| Plugin | What it is |
|---|---|
| **prd-pipeline** | The orchestrator (this project). Tier-routes a change and runs it spec → grill → plan-gate → parallel worktree build → verify → ship. |
| **compound-v** | The composed skill set (brainstorming, plans, batched build, TDD, verification, finishing, plus taste / critical-thinking / agent-security / recheck). *Vendored from [LeventySeven/compound-v](https://github.com/LeventySeven/compound-v).* |
| **bad-research** | The deep, fully-cited research engine prd-pipeline uses for empirical grounding. *Vendored from [LeventySeven/badresearch](https://github.com/LeventySeven/badresearch).* |

`prd-pipeline` **depends on** the other two, so installing it auto-installs and enables them from this same marketplace.

## The one rule

**No non-trivial code touches disk before a human confirms the plan.** Everything else serves that.

## Install (via `/plugins` — recommended)

In Claude Code:

```
/plugin marketplace add Timmy-Lane/prd-pipeline
/plugin install prd-pipeline@prd-pipeline
```

That's it. `compound-v` and `bad-research` install automatically (same marketplace, declared as dependencies). Invoke the pipeline with `/prd-pipeline` (it also fires on its own when you ask to build/add/implement a feature).

> **bad-research engine — one-time caveat.** The research *skills and agents* load instantly with zero setup. The actual deep-research **engine** is a small Python CLI (`bad`) that the plugin **self-bootstraps into its own data dir on first use** — you run no commands. It needs **Python 3.11–3.13** (and ideally [`uv`](https://docs.astral.sh/uv/) or `pipx`) on your machine. If that toolchain is absent, prd-pipeline degrades gracefully to Claude-native web search; the core build pipeline never breaks. No heavy ML downloads — the default engine is the keyless base (no torch/transformers).

## Tier routing — a spec only when it earns its keep

| Tier | Trigger | Pipeline |
|---|---|---|
| **T0 — no spec** | Bug fix · refactor (no behavior change) · docs · dep bump · prompt/threshold tweak vs an existing eval · devops/CI. Two-way door, solution obvious. | Just build it: TDD + code-review. |
| **T1 — light spec** | Small feature · single subsystem · mostly reversible · <~8 files. | One-pager spec → 1 grill pass → confirmed plan → build → verify. |
| **T2 — full spec** | New pipeline/behavior · new DB table/column · new public API or data source · cross-cutting · **one-way (irreversible) door** · anything moving user-visible outcomes. | Full PRD → adversarial grill (parallel critics + pre-mortem) → architecture lock-in (disjoint-file task partition) → **editable plan-gate** → parallel worktree build → verify → ship. |

Unsure → route up, never reflexively to T2.

## Parallel agents in git worktrees — you stay on `main`, work auto-branches

- **Always start from `main`.** For a feature, the pipeline auto-creates an independent feature branch in its own git worktree and works there — `main` stays clean the whole time. You never `git checkout`, never manually branch.
- **≥2 independent sub-tasks ⇒ parallelize.** One `Agent(isolation:"worktree")` per task — its own worktree+branch; auto-cleans if unchanged.
- **Merge inward; touch `main` only at ship.** Sub-task branches merge into the feature branch (disjoint-file partition = conflict-free); the feature branch lands on `main` only at the deliberate ship step. `main` is never half-built.
- **Cleanup is part of the task** — after merge, `git worktree remove` + delete the branch. 4–8 concurrent cap.

## What's in here

```
.claude-plugin/marketplace.json     the marketplace catalog (lists the 3 plugins)
plugins/
  prd-pipeline/                     the orchestrator plugin
    .claude-plugin/plugin.json        manifest — declares deps on compound-v + bad-research
    skills/prd-pipeline/SKILL.md      the procedure
    skills/prd-pipeline/references/   cited best-practice synthesis + default spec template
    hooks/                            SessionStart router (re-homes the always-on trigger)
  compound-v/                       vendored compound-v plugin (the composed skill set)
  bad-research/                     vendored bad-research
    skills/ agents/                   prompt layer (loads instantly, no Python)
    engine/                           the Python deep-research engine (self-bootstrapped on first use)
    bin/bad                           launcher that builds the engine venv on first call
bin/prd · install.sh                LEGACY non-plugin installer (see below)
rules/feature-workflow.md           legacy always-on rule (used only by bin/prd)
```

## Legacy install (without `/plugins`)

For environments that don't use Claude Code plugins, the original script installer still works — it copies the prd-pipeline skill + rule into `~/.claude` and wires a managed `CLAUDE.md` block. It does **not** bundle compound-v or bad-research; prefer the `/plugins` path above.

```bash
git clone https://github.com/Timmy-Lane/prd-pipeline ~/.prd-pipeline
less ~/.prd-pipeline/bin/prd ~/.prd-pipeline/install.sh   # inspect before running
~/.prd-pipeline/bin/prd install
```

`prd doctor` reports install status + a dependency check (`git`, `compound-v`, the research engine). Other subcommands: `prd update[ --check]`, `prd uninstall`, `prd new <topic>`, `prd list`, `prd audit`, `prd notify on|off|status`.

## Security / trust

- The `/plugins` install copies plugins into Claude Code's plugin cache; nothing phones home. The bad-research engine, when first used, builds a local Python venv from the **vendored** engine source in this repo (it does fetch that engine's own PyPI dependencies at that point — the keyless base, no ML stack).
- The legacy `bin/prd` only writes under `~/.claude` + `~/.local/bin`, edits a clearly-marked managed `CLAUDE.md` block (atomic, truncation-safe), never uses `eval`, and makes no network calls unless you opt into `prd notify on` (a read-only `git ls-remote` against this repo, ≤1/day, cached).

## Credit

Process canon distilled from Google's *Design Docs*, Amazon's *Working Backwards* PR-FAQ, the Rust RFC + Oxide RFD lineage, Basecamp's *Shape Up*, Gary Klein's pre-mortem, and spec-driven-development tools (GitHub spec-kit, OpenSpec, BMAD). Sources in `plugins/prd-pipeline/skills/prd-pipeline/references/research-notes.md`. Bundles **compound-v** (© Slava / LeventySeven, MIT) and **bad-research** (© LeventySeven, MIT); each plugin keeps its upstream license.

## License

MIT — see `LICENSE`.
