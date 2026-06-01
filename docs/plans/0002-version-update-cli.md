# Version-aware `prd` CLI + update notifications — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the `prd` CLI version-aware — report its version, check for newer releases, warn on skill drift, optionally nudge at session start, and scaffold/list specs — without breaking the project's "no phone-home by default" promise.

**Architecture:** All command logic lives in the single self-contained `bin/prd` (portability for `curl | bash` + a symlinked entry point > many-small-files here — a conscious trade). A root `VERSION` file is the single source of truth; releases are annotated git tags `vX.Y.Z`. The passive notifier is a `SessionStart` hook whose command is a thin `prd notify --hook` shim — wired into `~/.claude/settings.json` **only** on explicit `prd notify on`, so the default install makes zero settings edits and zero network calls. Each command is TDD'd against the existing `tests/smoke.sh` harness (isolated temp envs, content assertions), green on ubuntu + macos CI.

**Tech Stack:** Pure bash (BSD + GNU portable — no `readlink -f`, no `stat -f/-c`), `git ls-remote` for the release check, `python3`-or-`jq` (with a manual fallback) for the one JSON merge, the existing `tests/smoke.sh` assertion harness.

**Spec:** `docs/specs/0002-version-update-cli.md`

**Execution context:** Runs on a feature branch in an isolated worktree (created via `superpowers:using-git-worktrees` at execution time). The draft spec `docs/specs/0002-*.md` is committed **with** this work (project rule SKILL.md:80 — specs land on the feature branch, not `main` up front). `main` is touched only at ship.

**Build ordering note:** `bin/prd` and `tests/smoke.sh` are edited by nearly every task, so those tasks are **serial** (no parallel worktrees — they'd collide on the same two files). The only genuinely parallel artifact is the docs task (Task 9: `README.md` + `CHANGELOG.md`), which may run in its own worktree against the others.

---

## File Structure

| File | Responsibility | Tasks |
|---|---|---|
| `VERSION` (create) | Single source-of-truth version string (`0.2.0`) | 1, 9 |
| `bin/prd` (modify) | All new commands + symlink-safe path resolution + `REPO_URL` | 1–8 |
| `tests/smoke.sh` (modify) | New CASE blocks asserting each command's behavior | 1–8 |
| `README.md` (modify) | Rewrite Security/trust promise; document new commands | 9 |
| `CHANGELOG.md` (modify) | `0.2.0` entry | 9 |
| `docs/specs/0002-version-update-cli.md` | Mark `implemented` at ship | 9 |

`prd new`/`prd list` operate on the **current working repo's** `docs/specs/` (not the prd-pipeline clone).

---

## Task 1: `VERSION` file + symlink-safe paths + `prd version`

**Files:**
- Create: `VERSION`
- Modify: `bin/prd:11-19` (path resolution + `REPO_URL`), add `cmd_version` + `version` case arm
- Test: `tests/smoke.sh` (new CASE block)

- [ ] **Step 1: Create the VERSION file**

```bash
printf '0.2.0\n' > VERSION
```

- [ ] **Step 2: Write the failing test** — append a new CASE block to `tests/smoke.sh` **before** the final summary footer (the `printf` that reports `$PASS`/`$FAIL`):

```bash
# ============================================================
# CASE 8: prd version + symlink-safe invocation
# ============================================================
printf '\n\033[1m[8] prd version (direct + via symlink)\033[0m\n'

C8="$TMPROOT/c8"
mkdir -p "$C8/claude" "$C8/bin" "$C8/prd"
export CLAUDE_HOME="$C8/claude"; export PRD_BIN_DIR="$C8/bin"; export PRD_HOME="$C8/prd"

EXPECT_VER="$(tr -d '[:space:]' < "$REPO/VERSION")"
assert_eq "C8: prd version (direct)" "$EXPECT_VER" "$(prd version)"

# install, then invoke through the installed symlink — exercises symlink-safe REPO_ROOT
prd install >/dev/null 2>&1
assert_symlink "C8: symlink exists" "$PRD_BIN_DIR/prd"
assert_eq "C8: prd version (via symlink)" "$EXPECT_VER" "$(bash "$PRD_BIN_DIR/prd" version)"
prd uninstall >/dev/null 2>&1
```

- [ ] **Step 3: Run test to verify it fails**

Run: `bash tests/smoke.sh`
Expected: FAIL at "C8: prd version (direct)" — `version` is an unknown command (and, before the fix, the symlink invocation would resolve `REPO_ROOT` to `~/.local`).

- [ ] **Step 4: Implement — symlink-safe paths + `REPO_URL` + `cmd_version`.** In `bin/prd`, replace the `REPO_ROOT="..."` line (currently line 12) with a portable symlink resolver, and add `REPO_URL` next to the other globals:

```bash
# Resolve this script's real directory even when invoked through a symlink
# (portable: no GNU readlink -f). $0/BASH_SOURCE may be a symlink on PATH.
_resolve_dir() {
  local src="${BASH_SOURCE[0]}" dir
  while [ -h "$src" ]; do
    dir="$(cd -P "$(dirname "$src")" && pwd)"
    src="$(readlink "$src")"
    case "$src" in /*) ;; *) src="$dir/$src" ;; esac
  done
  cd -P "$(dirname "$src")" && pwd
}
REPO_ROOT="$(cd "$(_resolve_dir)/.." && pwd)"
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
SKILLS_DST="$CLAUDE_HOME/skills"
RULES_DST="$CLAUDE_HOME/rules/common"
CLAUDE_MD="$CLAUDE_HOME/CLAUDE.md"
BIN_DST="${PRD_BIN_DIR:-$HOME/.local/bin}"
REPO_URL="${PRD_REPO_URL:-https://github.com/Timmy-Lane/prd-pipeline.git}"
case "$REPO_URL" in https://*) : ;; *) err "PRD_REPO_URL must be https:// (got: $REPO_URL)"; exit 1 ;; esac
```

Add a version reader + command (place near the other `cmd_*` functions):

```bash
prd_version() { tr -d '[:space:]' < "$REPO_ROOT/VERSION" 2>/dev/null; }
cmd_version() { local v; v="$(prd_version)"; echo "${v:-unknown}"; }
```

Wire the case arm in `main()` (add alongside `install|update|...`):

```bash
    version|--version|-v) cmd_version ;;
```

(Move the `err()`/`green()`/`dim()` helper definitions above the globals if `err` is now referenced during the `REPO_URL` assertion — they are currently defined at lines 21-23; relocate those three lines to just after `set -euo pipefail`.)

- [ ] **Step 5: Run test to verify it passes**

Run: `bash tests/smoke.sh`
Expected: PASS for all C8 assertions; total PASS count increased by 3.

- [ ] **Step 6: Commit**

```bash
git add VERSION bin/prd tests/smoke.sh
git commit -m "feat(prd): VERSION file + symlink-safe paths + prd version"
```

---

## Task 2: `install` copies VERSION + `prd doctor` two-version drift report

**Files:**
- Modify: `bin/prd` — `cmd_install_global` (copy VERSION into skill dir), `cmd_doctor` (two versions + drift)
- Test: `tests/smoke.sh` (new CASE block)

- [ ] **Step 1: Write the failing test** — append CASE 9:

```bash
# ============================================================
# CASE 9: doctor reports version + warns on drift
# ============================================================
printf '\n\033[1m[9] doctor version + drift\033[0m\n'

C9="$TMPROOT/c9"
mkdir -p "$C9/claude" "$C9/bin" "$C9/prd"
export CLAUDE_HOME="$C9/claude"; export PRD_BIN_DIR="$C9/bin"; export PRD_HOME="$C9/prd"

prd install >/dev/null 2>&1
assert_file_exists "C9: VERSION copied into skill dir" "$CLAUDE_HOME/skills/prd-pipeline/VERSION"

CLONE_VER="$(tr -d '[:space:]' < "$REPO/VERSION")"
DOC="$(prd doctor 2>&1)"
case "$DOC" in *"$CLONE_VER"*) pass "C9: doctor prints version" ;; *) fail "C9: doctor missing version" ;; esac

# Seed a stale installed VERSION → doctor must warn about drift
printf '0.0.1\n' > "$CLAUDE_HOME/skills/prd-pipeline/VERSION"
DOC2="$(prd doctor 2>&1)"
case "$DOC2" in *drift*) pass "C9: doctor warns on drift" ;; *) fail "C9: no drift warning" ;; esac
prd uninstall >/dev/null 2>&1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash tests/smoke.sh`
Expected: FAIL at "C9: VERSION copied into skill dir" — install doesn't copy VERSION yet.

- [ ] **Step 3: Implement.** In `cmd_install_global` (after the `cp -R "$REPO_ROOT/skills/prd-pipeline" "$SKILLS_DST/"` line), add:

```bash
  cp "$REPO_ROOT/VERSION" "$SKILLS_DST/prd-pipeline/VERSION" 2>/dev/null || true
```

In `cmd_doctor`, add a version block (after the `claude home:` line):

```bash
  local clone_v inst_v
  clone_v="$(prd_version)"
  inst_v="$(tr -d '[:space:]' < "$SKILLS_DST/prd-pipeline/VERSION" 2>/dev/null)"
  echo "  version (clone):     ${clone_v:-unknown}"
  echo "  version (installed): ${inst_v:-not installed}"
  if [ -n "$clone_v" ] && [ -n "$inst_v" ] && [ "$clone_v" != "$inst_v" ]; then
    err "  drift: installed skill v$inst_v differs from clone v$clone_v — run: prd install"
  fi
```

- [ ] **Step 4: Run test to verify it passes**

Run: `bash tests/smoke.sh`
Expected: PASS for all C9 assertions.

- [ ] **Step 5: Commit**

```bash
git add bin/prd tests/smoke.sh
git commit -m "feat(prd): doctor reports clone+installed version and warns on drift"
```

---

## Task 3: `prd update --check` (SemVer compare against latest release tag)

**Files:**
- Modify: `bin/prd` — `ver_gt` helper, `latest_remote_tag` (with a test seam), `cmd_update_check`, route `update --check`
- Test: `tests/smoke.sh` (new CASE block, mocked tag source)

- [ ] **Step 1: Write the failing test** — append CASE 10. It mocks the remote tag list via the `PRD_LSREMOTE_TAGS_FILE` test seam (no network):

```bash
# ============================================================
# CASE 10: prd update --check (mocked remote tags)
# ============================================================
printf '\n\033[1m[10] prd update --check\033[0m\n'

CLONE_VER="$(tr -d '[:space:]' < "$REPO/VERSION")"   # e.g. 0.2.0

# Newer tag available → "update available"
FAKE="$TMPROOT/tags-newer"; printf 'v0.2.0\nv0.10.0\nv0.9.0\n' > "$FAKE"
OUT="$(PRD_LSREMOTE_TAGS_FILE="$FAKE" prd update --check 2>&1)"
case "$OUT" in *"update available"*"0.10.0"*) pass "C10: detects newer release" ;; *) fail "C10: did not detect newer release ($OUT)" ;; esac

# Only equal/older tags → "up to date"
FAKE2="$TMPROOT/tags-same"; printf 'v0.0.9\nv%s\n' "$CLONE_VER" > "$FAKE2"
OUT2="$(PRD_LSREMOTE_TAGS_FILE="$FAKE2" prd update --check 2>&1)"
case "$OUT2" in *"up to date"*) pass "C10: up to date when no newer tag" ;; *) fail "C10: expected up to date ($OUT2)" ;; esac

# No tags reachable → graceful, non-fatal
FAKE3="$TMPROOT/tags-empty"; : > "$FAKE3"
PRD_LSREMOTE_TAGS_FILE="$FAKE3" prd update --check >/dev/null 2>&1
assert_eq "C10: empty tag list is non-fatal (exit 0)" "0" "$?"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash tests/smoke.sh`
Expected: FAIL at C10 — `update --check` is not handled (current `update` ignores extra args and runs a real pull).

- [ ] **Step 3: Implement.** Add helpers + the check command to `bin/prd`:

```bash
# ver_gt A B → exit 0 if A > B (numeric per-component; handles 0.10.0 > 0.9.0)
ver_gt() {
  local a="${1#v}" b="${2#v}"; [ "$a" = "$b" ] && return 1
  local IFS=. ; set -- $a; local a1=${1:-0} a2=${2:-0} a3=${3:-0}
  set -- $b; local b1=${1:-0} b2=${2:-0} b3=${3:-0}
  [ "$a1" -ne "$b1" ] 2>/dev/null && { [ "$a1" -gt "$b1" ]; return; }
  [ "$a2" -ne "$b2" ] 2>/dev/null && { [ "$a2" -gt "$b2" ]; return; }
  [ "$a3" -gt "$b3" ] 2>/dev/null
}

# Highest vX.Y.Z release tag from the remote (test seam: PRD_LSREMOTE_TAGS_FILE)
latest_remote_tag() {
  local raw
  if [ -n "${PRD_LSREMOTE_TAGS_FILE:-}" ]; then
    raw="$(cat "$PRD_LSREMOTE_TAGS_FILE" 2>/dev/null)"
  else
    raw="$(git ls-remote --tags "$REPO_URL" 2>/dev/null)"
  fi
  printf '%s\n' "$raw" \
    | sed -n 's#.*\(v\{0,1\}[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\)$#\1#p' \
    | sed 's/^v//' | sort -t. -k1,1n -k2,2n -k3,3n | tail -1
}

cmd_update_check() {
  local cur latest; cur="$(prd_version)"; latest="$(latest_remote_tag)"
  if [ -z "$latest" ]; then dim "  could not check for updates (offline?)"; return 0; fi
  if ver_gt "$latest" "$cur"; then
    green "  update available: v$cur → v$latest (run: prd update)"
  else
    green "  up to date (v$cur)"
  fi
}
```

Route it: change the `update)` arm in `main()` to branch on `--check`:

```bash
    update)    if [ "${1:-}" = "--check" ]; then cmd_update_check; else cmd_update; fi ;;
```

- [ ] **Step 4: Run test to verify it passes**

Run: `bash tests/smoke.sh`
Expected: PASS for all C10 assertions.

- [ ] **Step 5: Commit**

```bash
git add bin/prd tests/smoke.sh
git commit -m "feat(prd): update --check compares latest release tag (SemVer, no pull)"
```

---

## Task 4: `prd notify on|off` — wire/unwire the SessionStart hook in settings.json

**Files:**
- Modify: `bin/prd` — `json_tool` detector, `notify_hook_add`/`notify_hook_remove`, `cmd_notify`, route `notify`
- Test: `tests/smoke.sh` (new CASE block; JSON validity + foreign-hook survival + idempotency)

> **Pre-implementation gate:** Before writing the JSON shape, confirm the Claude Code `SessionStart` hook schema via the `update-config` skill. The shape assumed below is `hooks.SessionStart[] = { hooks: [ { type: "command", command: "<cmd>" } ] }`. If `update-config` reports a different shape (e.g. a required `matcher`), adjust the embedded merge accordingly. This resolves the spec's one `[NEEDS CLARIFICATION]`.

- [ ] **Step 1: Write the failing test** — append CASE 11:

```bash
# ============================================================
# CASE 11: prd notify on|off (settings.json safety + idempotency)
# ============================================================
printf '\n\033[1m[11] prd notify on/off\033[0m\n'

if command -v python3 >/dev/null 2>&1 || command -v jq >/dev/null 2>&1; then
  C11="$TMPROOT/c11"; mkdir -p "$C11/claude" "$C11/bin" "$C11/prd"
  export CLAUDE_HOME="$C11/claude"; export PRD_BIN_DIR="$C11/bin"; export PRD_HOME="$C11/prd"
  SET="$CLAUDE_HOME/settings.json"

  # Seed a foreign hook that must survive untouched
  printf '{\n  "hooks": {\n    "SessionStart": [\n      { "hooks": [ { "type": "command", "command": "echo keep-me" } ] }\n    ]\n  }\n}\n' > "$SET"

  prd notify on >/dev/null 2>&1
  assert_eq "C11: settings.json is valid JSON after on" "0" \
    "$(python3 -c 'import json,sys;json.load(open(sys.argv[1]))' "$SET" 2>/dev/null; echo $?)"
  assert_contains    "C11: prd hook present after on"  "prd notify --hook" "$SET"
  assert_contains    "C11: foreign hook survived on"   "echo keep-me"      "$SET"

  prd notify on >/dev/null 2>&1   # idempotent — exactly one prd hook
  assert_count       "C11: exactly one prd hook"  1  "prd notify --hook" "$SET"

  prd notify off >/dev/null 2>&1
  assert_not_contains "C11: prd hook gone after off"   "prd notify --hook" "$SET"
  assert_contains     "C11: foreign hook survived off" "echo keep-me"      "$SET"
  assert_eq "C11: settings.json valid JSON after off" "0" \
    "$(python3 -c 'import json,sys;json.load(open(sys.argv[1]))' "$SET" 2>/dev/null; echo $?)"
else
  pass "C11: skipped (no python3/jq — notify gates itself off)"
fi
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash tests/smoke.sh`
Expected: FAIL at "C11: prd hook present after on" — `notify` is an unknown command.

- [ ] **Step 3: Implement.** Add to `bin/prd`:

```bash
NOTIFY_CMD="prd notify --hook"   # stable identifier for our SessionStart hook

json_tool() {
  if command -v python3 >/dev/null 2>&1; then echo python3
  elif command -v jq >/dev/null 2>&1; then echo jq
  else echo none; fi
}

notify_hook_add() {   # python3 path (jq path analogous); atomic temp+mv
  local set="$CLAUDE_MD"; set="$CLAUDE_HOME/settings.json"
  local tmp="$set.tmp.$$"
  python3 - "$set" "$NOTIFY_CMD" > "$tmp" <<'PY'
import json,sys,os
path,cmd=sys.argv[1],sys.argv[2]
data=json.load(open(path)) if os.path.exists(path) and os.path.getsize(path)>0 else {}
ss=data.setdefault("hooks",{}).setdefault("SessionStart",[])
present=any(h.get("command")==cmd for g in ss for h in g.get("hooks",[]))
if not present:
    ss.append({"hooks":[{"type":"command","command":cmd}]})
json.dump(data,sys.stdout,indent=2); sys.stdout.write("\n")
PY
  mv "$tmp" "$set"
}

notify_hook_remove() {
  local set="$CLAUDE_HOME/settings.json"
  [ -f "$set" ] || return 0
  local tmp="$set.tmp.$$"
  python3 - "$set" "$NOTIFY_CMD" > "$tmp" <<'PY'
import json,sys,os
path,cmd=sys.argv[1],sys.argv[2]
data=json.load(open(path)) if os.path.getsize(path)>0 else {}
ss=data.get("hooks",{}).get("SessionStart",[])
ss=[g for g in ss if not any(h.get("command")==cmd for h in g.get("hooks",[]))]
ss=[g for g in ss if g.get("hooks")]
if ss: data.setdefault("hooks",{})["SessionStart"]=ss
else:
    data.get("hooks",{}).pop("SessionStart",None)
    if data.get("hooks")=={}: data.pop("hooks",None)
json.dump(data,sys.stdout,indent=2); sys.stdout.write("\n")
PY
  mv "$tmp" "$set"
}

cmd_notify() {
  case "${1:-}" in
    on)
      if [ "$(json_tool)" = none ]; then
        err "  prd notify needs python3 or jq to edit settings.json safely."
        err "  Add this SessionStart hook to $CLAUDE_HOME/settings.json by hand:"
        dim '    {"hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"prd notify --hook"}]}]}}'
        exit 1
      fi
      mkdir -p "$CLAUDE_HOME"; notify_hook_add
      green "  prd notify enabled (SessionStart nudge, opt-in, ≤1 network check/day)." ;;
    off)
      notify_hook_remove; green "  prd notify disabled." ;;
    --hook) cmd_notify_hook ;;
    ""|status)
      if grep -qsF "$NOTIFY_CMD" "$CLAUDE_HOME/settings.json" 2>/dev/null; then echo "  notify: on"; else echo "  notify: off"; fi ;;
    *) err "usage: prd notify {on|off|status}"; exit 1 ;;
  esac
}
```

> If `update-config` confirmed a `jq`-only environment is in scope, add a `jq` branch mirroring the python merge; otherwise the `none`→manual fallback above covers it. `cmd_notify_hook` is implemented in Task 5; for this task it may be a no-op stub: `cmd_notify_hook() { :; }`.

Route it in `main()`:

```bash
    notify)    cmd_notify "$@" ;;
```

- [ ] **Step 4: Run test to verify it passes**

Run: `bash tests/smoke.sh`
Expected: PASS for all C11 assertions (or the skip branch on a runner without python3/jq).

- [ ] **Step 5: Commit**

```bash
git add bin/prd tests/smoke.sh
git commit -m "feat(prd): notify on|off wires an opt-in SessionStart hook (atomic JSON merge)"
```

---

## Task 5: `prd notify --hook` runtime shim (24h cache, network only when stale)

**Files:**
- Modify: `bin/prd` — replace the `cmd_notify_hook` stub with the real cache+check shim
- Test: `tests/smoke.sh` (new CASE block; cache write + cached read with no network)

- [ ] **Step 1: Write the failing test** — append CASE 12:

```bash
# ============================================================
# CASE 12: prd notify --hook (cache + nudge, no network when fresh)
# ============================================================
printf '\n\033[1m[12] prd notify --hook\033[0m\n'

C12="$TMPROOT/c12"; mkdir -p "$C12/claude"
export CLAUDE_HOME="$C12/claude"; export PRD_BIN_DIR="$C12/bin"; export PRD_HOME="$C12/prd"
CACHE="$CLAUDE_HOME/.prd-update-cache"
CLONE_VER="$(tr -d '[:space:]' < "$REPO/VERSION")"

# Stale/empty cache + a newer mocked tag → prints a nudge AND writes the cache
FAKE="$TMPROOT/c12-tags"; printf 'v99.0.0\n' > "$FAKE"
OUT="$(PRD_LSREMOTE_TAGS_FILE="$FAKE" prd notify --hook 2>&1)"
case "$OUT" in *"update available"*"99.0.0"*) pass "C12: hook nudges on newer release" ;; *) fail "C12: no nudge ($OUT)" ;; esac
assert_file_exists "C12: cache written" "$CACHE"

# Fresh cache (just written) → no network needed; remove the seam so a network call would fail loudly
OUT2="$(prd notify --hook 2>&1)"
case "$OUT2" in *"update available"*"99.0.0"*) pass "C12: fresh cache reused (no network)" ;; *) fail "C12: cache not reused ($OUT2)" ;; esac

# Current version equals latest → no nudge
FAKE2="$TMPROOT/c12-same"; printf 'v%s\n' "$CLONE_VER" > "$FAKE2"
rm -f "$CACHE"
OUT3="$(PRD_LSREMOTE_TAGS_FILE="$FAKE2" prd notify --hook 2>&1)"
assert_eq "C12: no nudge when up to date" "" "$OUT3"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash tests/smoke.sh`
Expected: FAIL at "C12: hook nudges on newer release" — `cmd_notify_hook` is still the no-op stub.

- [ ] **Step 3: Implement.** Replace the `cmd_notify_hook` stub with:

```bash
cmd_notify_hook() {
  local cache="$CLAUDE_HOME/.prd-update-cache" now last="" latest="" age=86400
  now="$(date +%s 2>/dev/null)" || exit 0
  if [ -f "$cache" ]; then IFS='	' read -r last latest < "$cache" 2>/dev/null; fi
  if [ -z "${last:-}" ] || [ $((now - last)) -ge $age ]; then
    latest="$(latest_remote_tag)"
    [ -n "$latest" ] && printf '%s\t%s\n' "$now" "$latest" > "$cache" 2>/dev/null
  fi
  local cur; cur="$(prd_version)"
  if [ -n "${latest:-}" ] && ver_gt "$latest" "$cur"; then
    echo "prd-pipeline: update available v$cur → v$latest (run: prd update)"
  fi
  exit 0
}
```

(The cache line is `epoch<TAB>tag`; the `IFS='	'` is a literal tab. Network happens only when the cache is missing or ≥24h old — matching the spec's active-vs-passive split: `update --check` is always fresh, the hook is cached.)

- [ ] **Step 4: Run test to verify it passes**

Run: `bash tests/smoke.sh`
Expected: PASS for all C12 assertions.

- [ ] **Step 5: Commit**

```bash
git add bin/prd tests/smoke.sh
git commit -m "feat(prd): notify --hook shim with 24h cache (network only when stale)"
```

---

## Task 6: `prd new <topic>` — scaffold a spec from the template

**Files:**
- Modify: `bin/prd` — `cmd_new`, route `new`
- Test: `tests/smoke.sh` (new CASE block; runs inside a temp working repo)

- [ ] **Step 1: Write the failing test** — append CASE 13:

```bash
# ============================================================
# CASE 13: prd new <topic> scaffolds docs/specs/NNNN-<topic>.md
# ============================================================
printf '\n\033[1m[13] prd new\033[0m\n'

C13="$TMPROOT/c13-repo"; mkdir -p "$C13/docs/specs"
( cd "$C13" && bash "$REPO/bin/prd" new auth-rate-limit >/dev/null 2>&1 )
NEWSPEC="$C13/docs/specs/0001-auth-rate-limit.md"
assert_file_exists "C13: spec file created"        "$NEWSPEC"
assert_contains    "C13: id filled"   "id: 0001"             "$NEWSPEC"
assert_contains    "C13: title filled" "title: auth-rate-limit" "$NEWSPEC"
assert_not_contains "C13: no NNNN placeholder left" "id: NNNN" "$NEWSPEC"

# Next number increments past existing specs
( cd "$C13" && bash "$REPO/bin/prd" new second-thing >/dev/null 2>&1 )
assert_file_exists "C13: second spec is 0002" "$C13/docs/specs/0002-second-thing.md"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash tests/smoke.sh`
Expected: FAIL at "C13: spec file created" — `new` is unknown.

- [ ] **Step 3: Implement.** Add to `bin/prd` (template comes from the skill — never a CLI-local copy):

```bash
spec_template() {
  if [ -f "$REPO_ROOT/skills/prd-pipeline/references/spec-template.md" ]; then
    echo "$REPO_ROOT/skills/prd-pipeline/references/spec-template.md"
  else
    echo "$SKILLS_DST/prd-pipeline/references/spec-template.md"
  fi
}

cmd_new() {
  local topic="${1:-}"
  [ -n "$topic" ] || { err "usage: prd new <topic-kebab-case>"; exit 1; }
  local dir="docs/specs"; mkdir -p "$dir"
  local last n
  last="$(ls "$dir" 2>/dev/null | sed -n 's/^\([0-9]\{4\}\)-.*/\1/p' | sort -n | tail -1)"
  n="$(printf '%04d' "$(( 10#${last:-0} + 1 ))")"
  local tmpl out today; tmpl="$(spec_template)"; out="$dir/$n-$topic.md"; today="$(date +%Y-%m-%d)"
  [ -f "$tmpl" ] || { err "spec template not found ($tmpl)"; exit 1; }
  sed -e "s/^id: NNNN/id: $n/" \
      -e "s/^title: <kebab-case-title>/title: $topic/" \
      -e "s/^created: <YYYY-MM-DD>/created: $today/" "$tmpl" > "$out"
  green "created $out"
}
```

Route in `main()`:

```bash
    new)       cmd_new "$@" ;;
```

- [ ] **Step 4: Run test to verify it passes**

Run: `bash tests/smoke.sh`
Expected: PASS for all C13 assertions.

- [ ] **Step 5: Commit**

```bash
git add bin/prd tests/smoke.sh
git commit -m "feat(prd): new <topic> scaffolds a spec from the skill template"
```

---

## Task 7: `prd list` — list specs with status

**Files:**
- Modify: `bin/prd` — `cmd_list`, route `list`
- Test: `tests/smoke.sh` (new CASE block)

- [ ] **Step 1: Write the failing test** — append CASE 14:

```bash
# ============================================================
# CASE 14: prd list shows id · title · status from frontmatter
# ============================================================
printf '\n\033[1m[14] prd list\033[0m\n'

C14="$TMPROOT/c14-repo"; mkdir -p "$C14/docs/specs"
printf 'id: 0001\ntitle: alpha\nstatus: draft\n' > "$C14/docs/specs/0001-alpha.md"
printf 'id: 0002\ntitle: beta\nstatus: implemented\n' > "$C14/docs/specs/0002-beta.md"
LIST="$( cd "$C14" && bash "$REPO/bin/prd" list 2>&1 )"
case "$LIST" in *0001*alpha*draft*) pass "C14: lists draft spec" ;; *) fail "C14: missing alpha/draft ($LIST)" ;; esac
case "$LIST" in *0002*beta*implemented*) pass "C14: lists implemented spec" ;; *) fail "C14: missing beta/implemented ($LIST)" ;; esac
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash tests/smoke.sh`
Expected: FAIL at "C14: lists draft spec" — `list` is unknown.

- [ ] **Step 3: Implement.** Add to `bin/prd`:

```bash
cmd_list() {
  local dir="docs/specs"
  [ -d "$dir" ] || { dim "  no $dir/ in $(pwd)"; return 0; }
  local f id title status found=0
  for f in "$dir"/*.md; do
    [ -f "$f" ] || continue
    found=1
    id="$(sed -n 's/^id: *//p' "$f" | head -1)"
    title="$(sed -n 's/^title: *//p' "$f" | head -1)"
    status="$(sed -n 's/^status: *//p' "$f" | head -1 | sed 's/[[:space:]]*#.*//' | tr -d '[:space:]')"
    printf '  %-6s %-28s %s\n' "${id:-?}" "${title:-?}" "${status:-?}"
  done
  [ "$found" = 1 ] || dim "  no specs in $dir/"
}
```

Route in `main()`:

```bash
    list)      cmd_list ;;
```

- [ ] **Step 4: Run test to verify it passes**

Run: `bash tests/smoke.sh`
Expected: PASS for all C14 assertions.

- [ ] **Step 5: Commit**

```bash
git add bin/prd tests/smoke.sh
git commit -m "feat(prd): list shows specs with status from frontmatter"
```

---

## Task 8: Update `--help` / usage text for the new verbs

**Files:**
- Modify: `bin/prd` — the help string + unknown-command usage line
- Test: `tests/smoke.sh` (new CASE block asserting help mentions the new verbs)

- [ ] **Step 1: Write the failing test** — append CASE 15:

```bash
# ============================================================
# CASE 15: help lists the new verbs
# ============================================================
printf '\n\033[1m[15] help text\033[0m\n'
HELP="$(bash "$REPO/bin/prd" --help 2>&1)"
for v in version "update --check" notify new list; do
  case "$HELP" in *"$v"*) pass "C15: help mentions $v" ;; *) fail "C15: help missing $v" ;; esac
done
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash tests/smoke.sh`
Expected: FAIL at "C15: help mentions version" — usage string is stale.

- [ ] **Step 3: Implement.** Replace both usage strings in `main()` (the `""|-h|--help|help)` arm and the `*)` arm) with:

```bash
    ""|-h|--help|help)
      cat <<'USAGE'
usage: prd <command>
  install [--project DIR]   install globally (or just the skill into DIR)
  update [--check]          git pull + reinstall  (--check: report newer release, no pull)
  uninstall                 remove skill, rule, CLAUDE.md block, symlink
  doctor                    show install status + versions (clone vs installed)
  version                   print the prd-pipeline version
  notify {on|off|status}    opt-in SessionStart update nudge (≤1 network check/day)
  new <topic>               scaffold docs/specs/NNNN-<topic>.md from the template
  list                      list specs (id · title · status)
USAGE
      ;;
```

And the unknown-command arm:

```bash
    *) err "unknown command: $sub"; err "run: prd --help"; exit 1 ;;
```

- [ ] **Step 4: Run test to verify it passes**

Run: `bash tests/smoke.sh`
Expected: PASS for all C15 assertions; full suite green.

- [ ] **Step 5: Commit**

```bash
git add bin/prd tests/smoke.sh
git commit -m "docs(prd): help text covers version/update --check/notify/new/list"
```

---

## Task 9: Docs — rewrite the "no phone-home" promise, CHANGELOG, command table, tag the release

**Files:**
- Modify: `README.md` (Security/trust section + command table), `CHANGELOG.md`, `docs/specs/0002-version-update-cli.md` (mark implemented)

> This is the **one parallelizable task** — it touches only docs, disjoint from `bin/prd`/`tests/`. May run in its own worktree.

- [ ] **Step 1: Update the README command table.** In the install-commands table, add rows for `prd version`, `prd update --check`, `prd notify on|off`, `prd new <topic>`, `prd list`.

- [ ] **Step 2: Rewrite the Security/trust bullet** (currently: *"The only network operation is `git clone` / `git pull` of this repo…"*) to:

```markdown
- **No telemetry, no phone-home, no third-party downloads.** Network operations are limited to
  `git clone` / `git pull` of *this* repo over HTTPS, plus — **only if you opt in with
  `prd notify on`** — a read-only `git ls-remote --tags` against the same repo (≤ once/day, cached;
  no data is sent). A default install makes no `settings.json` edits and no network calls.
```

- [ ] **Step 3: Add the CHANGELOG entry:**

```markdown
## 0.2.0 — 2026-06-01

- `prd version` + a root `VERSION` file (single source of truth); releases are git tags `vX.Y.Z`.
- `prd update --check` — report a newer release tag without pulling (SemVer compare).
- `prd doctor` now shows clone vs installed-skill version and warns on drift.
- `prd notify on|off` — opt-in `SessionStart` update nudge (≤1 `ls-remote`/day, cached; default install untouched).
- `prd new <topic>` / `prd list` — scaffold and list specs (template reused from the skill).
- Fix: symlink-safe path resolution so commands work through the installed `~/.local/bin/prd` symlink.
```

- [ ] **Step 4: Mark the spec implemented.** At the top of `docs/specs/0002-version-update-cli.md`, set `status: implemented` and add an `> **Implemented 2026-06-01**` note summarizing what shipped + any scope deltas (mirroring 0001's style).

- [ ] **Step 5: Run the full suite once more**

Run: `bash tests/smoke.sh`
Expected: all cases PASS, exit 0.

- [ ] **Step 6: Commit + tag**

```bash
git add README.md CHANGELOG.md docs/specs/0002-version-update-cli.md
git commit -m "docs: document version/notify commands + rewrite network-promise for 0.2.0"
git tag -a v0.2.0 -m "prd-pipeline 0.2.0 — version awareness + update notifications"
```

(The tag is what `prd update --check` and the notify hook compare against — without it, every clone reads as "up to date" at 0.2.0. Push tags at ship: `git push --tags`.)

---

## Self-Review

**Spec coverage:**
- `VERSION` + `prd version` → Task 1. ✓
- Symlink-safe `REPO_ROOT` (latent bug) → Task 1 (asserted via symlink invocation). ✓
- `prd doctor` two-version + drift → Task 2. ✓
- `prd update --check` (git-tags + ls-remote, SemVer, always-fresh) → Task 3. ✓
- `prd notify on|off` + SessionStart hook + opt-in + settings.json safety → Task 4. ✓
- `prd notify --hook` 24h cache (passive ≠ active semantics) → Task 5. ✓
- `prd new` (reuses template, no fork) → Task 6. ✓
- `prd list` → Task 7. ✓
- README promise rewrite (in-scope, not polish) + CHANGELOG + release tag → Task 9. ✓
- Release discipline (SemVer, annotated tag, start 0.2.0) → Task 9. ✓
- CI green ubuntu+macos → existing `.github/workflows/ci.yml` runs `tests/smoke.sh` (no change needed; all new cases use the same harness). ✓

**Placeholder scan:** No "TBD"/"implement later". The one deferred item — exact SessionStart JSON shape — is gated behind a concrete `update-config` verification step in Task 4 with a stated assumed shape and a fallback, not a blank. ✓

**Type/name consistency:** `prd_version`, `ver_gt`, `latest_remote_tag`, `cmd_update_check`, `NOTIFY_CMD`, `cmd_notify`, `cmd_notify_hook`, `spec_template`, `cmd_new`, `cmd_list`, `PRD_LSREMOTE_TAGS_FILE` (test seam) used consistently across tasks. `cmd_notify_hook` is stubbed in Task 4 and implemented in Task 5 (noted explicitly). ✓

**Risk checks honored:** zero-touch default install (C9/C11 use explicit `notify on`); JSON validity + foreign-hook survival (C11); `0.10.0 > 0.9.0` numeric compare (C10); offline/empty graceful (C10); symlink resolution (C8). ✓
