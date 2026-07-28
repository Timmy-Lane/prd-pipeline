# Changelog

## 1.0.0 — 2026-07-28

**prd-pipeline is a standalone plugin again, and it stops writing documents nobody reads.**

### Two regressions fixed
- **The legacy installer had been broken since 0.5.2.** `refactor(plugins): fold prd-pipeline into compound-v` (3e18801) moved the skill to `plugins/compound-v/skills/prd-pipeline/`, but `bin/prd` still copied from `plugins/prd-pipeline/skills/prd-pipeline` — a path that no longer existed. `tests/smoke.sh` aborted before its first assertion. Restoring the standalone plugin restores the path; the suite is green again.
- **`install.sh` never took its local-checkout branch.** It probed `$HERE/skills/prd-pipeline/SKILL.md`, the pre-0.5.0 layout, so every run from a clone fell through to a network `git clone` of itself. Now probes the real path.

### prd-pipeline — standalone
- New `plugins/prd-pipeline/` plugin. **No hard dependency on any other plugin**: `git` is the only requirement, every phase has an inline procedure, and the optional accelerants (compound-v, bad-research) are listed in one clearly-marked table with their fallbacks. Preflight no longer treats a missing skill as a gap to report.
- **Removed from compound-v**, which never wanted it: upstream's own `references/sources.md` records that prd-pipeline's build machinery is "deliberately NOT adopted — that's per-build process, not PRD content." The vendored fork had regressed that. `using-compound-v` now routes Large-tier work *to* the plugin and says why the copy isn't there, so the two can't drift.

### prd-pipeline — the documentation fix
The old pipeline emitted three permanent files per T2 feature (spec, a sibling `-analysis.md`, a plan under `docs/plans/`), never read the project's existing documentation before deciding to write more, and never updated what it invalidated.
- **New Step 1.5 — route against the docs that already exist.** Inventory the repo's documentation into five buckets (product intent · decisions/ADRs · change records · runbooks · reference), then pick exactly one route: **amend** (the default) · **supersede** · **create** · **none**. Then name every doc the change makes wrong; each becomes a plan task.
- **Artifact budget, as an invariant: one change ⇒ at most one new document.** The consistency findings and the implementation plan are now **sections of the change file**, not siblings. T0 and T1 produce **zero** documents — T1's spec and plan are confirmed in the conversation and land in the commit message. Only T2 writes a file.
- **Doc-sync gate at ship (Step 6.4).** The stale-doc list is walked and each entry verified updated before the branch merges. A change that invalidates documentation has not shipped.
- **Fold-down at ship.** The change file's durable content moves into the living spec or an ADR and the change is archived, so scaffolding stops accumulating. (OpenSpec's persistent-specs / ephemeral-changes split; `references/research-notes.md` §8, with spec-kit and Diátaxis.)
- **Stage verdicts persist to disk** — append-only `.claude/prd-pipeline/<change-id>.jsonl`, one line per stage. Compaction re-attaches only the most recent invocation of a skill, so a long run loses which alternative was rejected and what the human approved; Recovery now reads the log instead of guessing. (LeventySeven/compound-v#7.)
- `references/spec-template.md` → `change-template.md`: `routing:` and `stale_docs:` frontmatter, and inline placeholders for the findings and plan sections that used to be separate files.
- Step 2.5 drops from nine passes to eight and gains the routing check: an existing document covering ≥60% of the surface is a CRITICAL routing error, not a style note.

### Marketplace — all six plugins, and no more stale vendoring
- **compound-v is no longer vendored.** The bundled fork was pinned at 0.3.0 while upstream had reached 0.5.0, so seven skills (`code-review`, `extracting-specs`, `frame-the-goal`, `make-it-stable`, `simplest-thing-that-works`, `ai-system-reliability`, `architecting-ai-systems`), the `user-prompt-submit` re-assertion hook, and the trigger-eval harness were all silently missing. The entry now points at `LeventySeven/compound-v` live. The `code-reviewer` agent added here in 0.5.2 was pushed upstream rather than dropped.
- **Added `silver`** ([LeventySeven/silver](https://github.com/LeventySeven/silver)), live from its own repo, which gained a plugin manifest upstream. `workflow-investigation` is deliberately **not** here — a plugin is installed from a marketplace, and that repo is private and internal, so it stays on its `npx github:` install path.
- **Added `superdesign`**, vendored (its upstream repo is a research/eval repo, not a skill package).
- **No plugin depends on another** any more — install any subset.

### bad-research
- The engine's copy of the entry skill told the model to run `bad install --steps-only`, which sprays 19 diverging step-skill directories into the working repo; the plugin copy said the opposite. The engine copy now checks for the namespaced bundled skills first. (Issue #1.)
- New `tests/bundle-consistency.sh`: every marketplace plugin resolves, every local plugin ships a skill, every `SKILL.md` name matches its directory, and the two bad-research entry-skill copies can't contradict each other again.

## 0.5.2 — 2026-07-08

- **compound-v — new `code-reviewer` agent (0.2.2).** The spawnable, read-only agent form of the `recheck` skill: reads the actual diff, re-runs the tests itself, returns severity-tagged findings + one verdict (APPROVED / FIX_REQUIRED / ARCHITECTURE_CONCERN). Tool-locked to `Read/Grep/Glob/Bash` (never edits — the implementer applies fixes), `model: opus`. Closes the gap where `Agent(subagent_type: "code-reviewer")` (referenced by downstream project CLAUDE.md files inherited from the retired gstack/superpowers stack) resolved to nothing; use `compound-v:code-reviewer` or the `/code-review` skill.

## 0.5.1 — 2026-06-25

Resilience + experience-driven hardening across all three bundled plugins (no breaking changes).

- **bad-research — survive a present-but-slim `bad` CLI.** The pipeline assumed the full hyperresearch CLI; on a slim v0.1.0 build (no `fetch`/`assets`/`note new`/`note update`/`sources`) every tier hard-failed at the first source under `set -e`. Added a Step 0 capability probe (`bad doctor -j` + `fetch`/`assets --help` → `research/cli-caps.json`) and native-fallback branches in the fetcher / depth-investigator / source-analyst agents (WebFetch + direct note-write with engine-compatible frontmatter; `bad search` for dedup; Read+Edit for curation). Asset steps in the fast/ultrafast/width-sweep tiers degrade to "no assets" instead of aborting.
- **prd-pipeline — discipline made observable + a stale map fixed.** `rules/feature-workflow.md`'s `## Composes` map no longer points at the removed superpowers/deep-research skills (→ compound-v/bad-research). Real dependency preflight (probe, don't assume) replaces the dead `prd doctor` reference. Worktree cleanup now fires on failure/abandonment + a Step 0/Step 6 orphan sweep. Grill surfaced as a non-skippable todo; the SessionStart router auto-routes feature work and names the research-grounding axis. Invalidators must use concrete triggers, never calendar-time deferrals. Reversible-toggle verification is owned by the agent. Migration-journal monotonicity caution for branch merges. Dev-machine self-references neutralized in `references/research-notes.md`.
- **compound-v — experience-driven skill upgrades.** `searching-patterns`: live docs over stale internal specs for 3rd-party APIs + a docs-MCP (context7-style) rung in the tool ladder. `evals`: the model's own outputs are never the ground-truth label. `finishing`: measure the shipped change's intended effect, don't assert it; a blocked measurement is tracked, not "done". `verification-before-completion`: render user-visible / hard-to-unsend output to a safe sink for human review before the prod send. `product-taste`: dropped a dead `humanizer` cross-reference.
- **writing-prd ← prd-pipeline consolidation.** Folded the portable PRD/spec-authoring disciplines into `compound-v:writing-prd` as the canonical document-quality home — alternatives-considered, cross-cutting constraints, key-bets/invalidators-as-triples (no calendar deferrals), working-backwards goal framing, required-section self-check. prd-pipeline's spec step now invokes writing-prd for the quality bar instead of re-deriving it.

## 0.5.0 — 2026-06-08

Repackaged as a **self-contained Claude Code plugin marketplace** so a user installs everything through `/plugins` with nothing extra to fetch. prd-pipeline no longer depends on a separately-installed `superpowers` plugin; it now composes the **bundled compound-v** skill set and the **bundled bad-research** deep-research engine, both vendored into this repo and pulled in automatically as plugin dependencies.

- **New layout:** repo root is a marketplace (`.claude-plugin/marketplace.json`) shipping three plugins under `plugins/` — `prd-pipeline`, `compound-v` (vendored from LeventySeven/compound-v), `bad-research` (vendored from LeventySeven/badresearch).
- **One-command install:** `/plugin marketplace add Timmy-Lane/prd-pipeline` → `/plugin install prd-pipeline@prd-pipeline`. The other two auto-install/enable (same-marketplace `dependencies`).
- **Skill rewiring (superpowers → compound-v):** `brainstorming`, `writing-plans`, `test-driven-development`, `verification-before-completion` map 1:1; `subagent-driven-development` → `batched-implementation`; `finishing-a-development-branch` → `finishing`. Folded in compound-v's net-new skills where there's a real slot — `critical-thinking` (grill lens), `agent-security` + `recheck` (review), `startup-taste`/`product-taste` (spec).
- **Research engine:** the `deep-research`/`deep-researcher` fallback is replaced by the bundled `bad-research` engine (with Claude-native WebSearch/WebFetch fallback). Its prompt skills + 16 agents load instantly; the Python `bad` CLI self-bootstraps into the plugin data dir on first use (needs Python 3.11–3.13 + uv/pipx; keyless base, no ML stack). bad-research's internal `Skill()` calls were namespaced to `bad-research:…` (plugin skills require the qualified form); its agents resolve by bare name.
- **Always-on trigger re-homed:** plugins don't load `rules`/`CLAUDE.md`, so the workflow trigger moved into a minimal `SessionStart` router hook in the prd-pipeline plugin.
- **Legacy `bin/prd` installer retained** as a non-plugin alternative; its dependency check now reports `compound-v` + `bad-research` instead of `superpowers`/`deep-research`.

## 0.4.0 — 2026-06-04

Spec-corpus visibility + a consistency audit (spec `docs/specs/0003-prd-audit.md`). Until now the repo accumulated specs with no at-a-glance view of the corpus and nothing that checked a spec's declared lifecycle state was still internally consistent or true.

- `prd list` now prints a **count summary** header (`total` + per-status tally + `invalid`) and takes `--status S` to filter the rows. Reuses the existing frontmatter extraction — no second parser.
- `prd audit` — **read-only** spec-lifecycle consistency check. Findings grouped by severity; exits non-zero on any ERROR (CI-friendly):
  - **ERROR** — missing/unparseable `status`, `status` outside `{draft,accepted,implemented,abandoned,superseded}`, missing `id`/`title`, duplicate `id`, `id` ≠ filename prefix; `superseded` with no `supersedes:`, `supersedes:` → a non-existent id.
  - **WARN** — git desync (a `feat/NNNN-*` branch exists but the spec is still `draft`/`accepted`), `implemented` without a `> **Implemented …**` body marker, and `draft`/`accepted` specs older than `--stale-days N` (default 30). Git checks degrade gracefully outside a git repo.
- `prd audit --fix` applies only the **one** genuinely safe fix (a spec with frontmatter but no `status:` line → `status: draft`), behind a `[y/N]` prompt. Every other finding prints a suggested manual action. **Specs stay append-only — nothing is deleted, renamed, or moved.**
- `prd audit --json` emits machine-readable findings (validated parseable) while preserving the exit code, for hooks/CI.
- Design note (git-check polarity): "`implemented` but no branch" is the *success* state — the workflow deletes merged branches — so an implemented claim is verified via the body marker, not branch existence. The audit reports clean on the repo's own `implemented` specs (0001, 0002).
- Smoke suite grows 84 → 115 assertions (CASE 17–23), including an isolated `git init` + branch fixture for the desync check and a positive staleness case that exercises the BSD/GNU date math on each CI leg. BSD+GNU portable.
- Review hardening: `date_to_epoch` probes BSD support with a concrete `date -j -f` parse of a fixed date (not bare `date -j`, whose no-arg behaviour is version-dependent); `prd list --status` / `prd audit --stale-days` now reject a missing value instead of silently no-opping; the `list` summary appends `(showing: …)` when filtered.

## 0.3.0 — 2026-06-02

Stronger pre-acceptance gates in the `prd-pipeline` skill — three of the skill's "signature disciplines" were enforced only by scattered prose, so compliance was interpretation-dependent (a diligent agent caught them, a compacted/rushed one didn't). Made them explicit, mandatory Step 2.5 passes (pass 7 is deterministic; 8–9 are judgment-guided but now required, not optional). Validated RED→GREEN, then held under three combined-pressure subagent scenarios (authority+time / sunk-cost / spirit-vs-letter) on a deliberately-defective Tier-2 spec.

- **Step 2.5 grows from 6 to 9 passes.** New passes run *before* the grill so critics never have to rediscover a structural omission:
  - **Pass 7 — Template-section coverage**: every required (bold) template section present and non-empty; missing **Wedge** / **Alternatives considered** / **Drawbacks-invalidators** = CRITICAL.
  - **Pass 8 — Invalidator presence**: ≥1 hypothesis-invalidator stated as an *observable-condition → measurement → rollback* triple; zero triples = CRITICAL (Step 3 lens 2 critiques their quality, this pass enforces existence).
  - **Pass 9 — Claim↔source binding**: every load-bearing quantitative/empirical claim cites a source / is the spec's own post-ship success criterion / is tagged `[ASSUMPTION]`; an unsourced load-bearing number = CRITICAL. Reuses the Step 6.2b citation-verifier pattern at spec-time.
- **Step 1 — research-grounding axis** (orthogonal to the tier): if a spec rests on external/empirical claims, a cited research pass is required before Step 2, and Pass 9 binds each claim to it.
- **Step 3 — grill lens 2** now checks invalidator *presence* ("is there ≥1 at all?"), not only measurability.
- **Step 0 — lifecycle-field check**: if the adopted template carries status as prose rather than a machine-readable `status:` field, the task list is the authoritative phase marker — prevents silent Recovery/Step-6 breakage on prose-status templates.
- **spec-template**: section headers now carry explicit `(required)` / `(when relevant)` markers (so Pass 7 has a literal source instead of relying on bold-in-prose that the template never actually applied); header reminds authors to cite load-bearing numbers and pair each Goal with a rollback invalidator (Passes 8–9). Pass 7 wording aligned to the `(required)` markers; a project template's own required set still wins.

## 0.2.0 — 2026-06-01

Version awareness + update notifications (spec `docs/specs/0002-version-update-cli.md`).

- `VERSION` file (single source of truth); releases are annotated git tags `vX.Y.Z`.
- `prd version` — print the installed version.
- `prd update --check` — report whether a newer release tag exists (SemVer compare via `git ls-remote --tags`), **without** pulling.
- `prd doctor` now reports clone vs installed-skill version and warns on drift.
- `prd notify on|off|status` — **opt-in** SessionStart update nudge. Default install makes no `settings.json` edits and no network calls; when enabled, a read-only `ls-remote` runs at most once/day (cached). The settings.json edit is parse-or-abort + atomic; `off` removes only our hook.
- `prd new <topic>` / `prd list` — scaffold and list specs (template reused from the skill, never forked).
- Fix: symlink-safe path resolution so commands work through the installed `~/.local/bin/prd` symlink.
- Fix: `prd doctor` no longer leaks a shell error on a not-installed environment.
- Fix: SemVer parsing handles multi-digit major versions (e.g. `v100.2.3`).
- Hardening: `prd notify --hook` survives a corrupted or hand-edited cache file — always exits 0, never breaks a session start.
- Hardening: `prd new <topic>` validates kebab-case, rejecting topics that could inject into `sed` or traverse out of `docs/specs/`.

## 0.1.0 — 2026-05-30

Initial base.

- `prd-pipeline` skill: tier-routed orchestrator (T0 no-spec / T1 light spec / T2 full PRD + adversarial grill + architecture lock-in + editable plan-gate + parallel worktree build).
- `feature-workflow` rule: always-on norm — spec gate, plan-confirmation gate (one-way vs two-way doors), mandatory parallel-agent + git-worktree mandate (you never switch branches; merge back + cleanup; 4–8 cap).
- `spec-template.md` default template; `research-notes.md` cited best-practice synthesis.
- `bin/prd` installer CLI: install / update / uninstall / doctor.
