# prd-pipeline

A tier-adaptive **build pipeline** for Claude Code: idea → the smallest spec that earns its keep →
adversarial grill → confirmed plan → parallel git-worktree build → verified ship. Drops into any repo.

The repo is also a **Claude Code plugin marketplace**. `prd-pipeline` is one plugin in it and stands
entirely alone; the others are separate tools that happen to compose well with it.

## The two rules

1. **No non-trivial code touches disk before a human confirms the plan.**
2. **A change produces at most one new document, and only when the tier earns it.**

The second rule exists because the first one, applied naively, produces a repo full of specs nobody
reads. Writing a PRD is the expensive default, not the safe one.

## Install

```
/plugin marketplace add Timmy-Lane/prd-pipeline
/plugin install prd-pipeline@prd-pipeline
```

Then say what you want to build — the skill fires on its own — or invoke `/prd-pipeline` directly.
It needs `git` and nothing else. No other plugin is required; if one of the optional accelerants
below happens to be installed, it uses it, and if not, it uses its own inline procedure.

## What's in the marketplace

| Plugin | What it is | Source |
|---|---|---|
| **prd-pipeline** | The build pipeline. Tier-routes a change, routes it against the docs that already exist, grills the spec, gates the plan, builds it in parallel worktrees, verifies, ships. | this repo |
| **compound-v** | ~28 short skills for the judgment around the code: startup / product / distribution taste, plans, TDD, systematic debugging, verification, read-only review, agent security, evals, context engineering. | [LeventySeven/compound-v](https://github.com/LeventySeven/compound-v), live |
| **bad-research** | Deep, multi-source, fully-cited research; tier-adaptive, adversarially reviewed. | vendored, from [LeventySeven/badresearch](https://github.com/LeventySeven/badresearch) |
| **superdesign** | Brand-specific UI with React + Tailwind v4 + shadcn/ui: brand → OKLCH tokens → pattern cookbook → anti-slop and a11y gates. | this repo |

Install them individually — none depends on another. `compound-v` is pulled **live from its own
repo** rather than copied in here, so it cannot go stale behind upstream.

> **bad-research engine — one-time caveat.** Its skills and agents load instantly with zero setup.
> The deep-research **engine** is a small Python CLI (`bad`) that the plugin self-bootstraps into
> its own data dir on first use — you run no commands. It wants **Python 3.11–3.13** and ideally
> [`uv`](https://docs.astral.sh/uv/) or `pipx`. Without that toolchain it degrades to native web
> search; nothing else breaks. No ML stack is downloaded.

## Tier routing — a document only when it earns its keep

| Tier | Trigger | Pipeline | New docs |
|---|---|---|---|
| **T0** | Bug fix · refactor with no behavior change · docs · dep bump · devops/CI config. Two-way door, obvious solution. | Build it: test-first + review. | **0** |
| **T1** | Small feature · single subsystem · mostly reversible · under ~8 files. | Spec and plan **in the conversation** → one grill pass → confirmed plan → build → verify. The record is the commit message. | **0** |
| **T2** | New pipeline or behavior · new DB table/column · new public API or data source · cross-cutting · **one-way door** · anything moving user-visible outcomes. | One change file → consistency gate → adversarial grill → architecture lock-in → **editable plan-gate** → parallel worktree build → verify → ship. | **1** |

Unsure → route up. Never reflexively to T2.

## Working with the docs that already exist

Before writing anything, the pipeline inventories the repo's documentation — product intent,
ADRs, change records, runbooks, API/CLI/config reference — and picks exactly one route:

- **amend** the document that already owns this surface (the default),
- **supersede** the ADR this change reverses,
- **create** one change file, or
- **none** at all.

Then it names every doc the change will make *wrong* and turns each into a plan task. A change that
invalidates documentation has not shipped until that documentation is updated. The rationale, with
sources, is in
[`plugins/prd-pipeline/skills/prd-pipeline/references/research-notes.md`](plugins/prd-pipeline/skills/prd-pipeline/references/research-notes.md) §8.

## Parallel agents in git worktrees — you stay on `main`

- **Always start from `main`.** A feature auto-creates its own branch in its own worktree; `main` stays clean the whole time. You never `git checkout`, never manually branch.
- **Two or more disjoint-file tasks ⇒ parallelize.** One `Agent(isolation:"worktree")` per task — its own worktree and branch, auto-cleaned if unchanged.
- **Merge inward; touch `main` only at ship.** Sub-task branches merge into the feature branch; the feature branch lands on `main` only at the deliberate ship step, so `main` is never half-built.
- **Cleanup is part of the task**, on success and on failure. Ceiling 4–8 concurrent worktrees — past that you are bottlenecked on review, not on the model.

## Layout

```
.claude-plugin/marketplace.json     the catalog
plugins/
  prd-pipeline/                     the pipeline plugin (standalone)
    skills/prd-pipeline/SKILL.md      the procedure
    skills/prd-pipeline/references/   sourced rationale + the one change template
  bad-research/                     vendored deep-research plugin (skills + agents + Python engine)
  superdesign/                      vendored UI design plugin
tests/smoke.sh                      legacy-installer smoke test
tests/bundle-consistency.sh         structural checks on the marketplace itself
bin/prd · install.sh                LEGACY non-plugin installer (see below)
rules/feature-workflow.md           the condensed rule the legacy installer wires into CLAUDE.md
```

## Legacy install (without `/plugin`)

For environments with no plugin support, the script installer still works — it copies the
prd-pipeline skill and rule into `~/.claude` and wires a clearly-marked managed `CLAUDE.md` block.
It installs only prd-pipeline; prefer the `/plugin` path above.

```bash
git clone https://github.com/Timmy-Lane/prd-pipeline ~/.prd-pipeline
less ~/.prd-pipeline/bin/prd ~/.prd-pipeline/install.sh   # inspect before running
~/.prd-pipeline/bin/prd install
```

`prd doctor` reports install status and checks `git` (the only hard dependency). Other subcommands:
`prd update[ --check]`, `prd uninstall`, `prd new <topic>`, `prd list`, `prd audit`,
`prd notify on|off|status`.

## Security / trust

- `/plugin` copies plugins into Claude Code's cache; nothing phones home. The bad-research engine, on first use, builds a local Python venv from the **vendored** engine source here (that step does fetch the engine's own PyPI dependencies — the keyless base, no ML stack).
- `bin/prd` writes only under `~/.claude` and `~/.local/bin`, edits an atomic truncation-safe managed `CLAUDE.md` block, never uses `eval`, and makes no network call unless you opt into `prd notify on` (a read-only `git ls-remote` against this repo, at most once a day, cached).

## Credit

Process canon distilled from Google's *Design Docs*, Amazon's *Working Backwards* PR-FAQ, the Rust
RFC and Oxide RFD lineage, Basecamp's *Shape Up*, Gary Klein's pre-mortem, and the spec-driven
tools — GitHub spec-kit, OpenSpec, BMAD — plus Diátaxis for how documentation divides. Sources in
`plugins/prd-pipeline/skills/prd-pipeline/references/research-notes.md`. Bundles **bad-research**
(© LeventySeven, MIT); each plugin keeps its upstream license.

## License

MIT — see `LICENSE`.
