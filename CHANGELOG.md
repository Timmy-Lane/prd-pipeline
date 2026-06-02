# Changelog

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
