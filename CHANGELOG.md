# Changelog

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

## 0.1.0 — 2026-05-30

Initial base.

- `prd-pipeline` skill: tier-routed orchestrator (T0 no-spec / T1 light spec / T2 full PRD + adversarial grill + architecture lock-in + editable plan-gate + parallel worktree build).
- `feature-workflow` rule: always-on norm — spec gate, plan-confirmation gate (one-way vs two-way doors), mandatory parallel-agent + git-worktree mandate (you never switch branches; merge back + cleanup; 4–8 cap).
- `spec-template.md` default template; `research-notes.md` cited best-practice synthesis.
- `bin/prd` installer CLI: install / update / uninstall / doctor.
