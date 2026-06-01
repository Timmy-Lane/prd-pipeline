#!/usr/bin/env bash
# tests/smoke.sh — installer smoke test for bin/prd + install.sh
#
# Usage: bash tests/smoke.sh
# Exits 0 when all invariants pass; non-zero (with a message) on first failure.
#
# Isolation: every case uses mktemp subdirs under TMPROOT. Real dirs are NEVER
# touched. CLAUDE_HOME, PRD_BIN_DIR, and PRD_HOME are all re-exported per case.
#
# Portability: macOS (BSD awk/sed/ln/mktemp) + Linux (GNU). No GNU-only flags.
# No readlink -f, no stat -f/-c, no sed -i without extension, no sha256sum.
#
# Idempotency: bin/prd's wire_claude_md refresh path strips the old block, then
#   strips trailing blank lines, then appends exactly one separator + the block.
#   This makes refresh reach a stable steady state — repeated `prd install` on an
#   already-wired CLAUDE.md is byte-identical (no blank-line growth). Case 2 asserts
#   whole-file identity across runs #2 and #3, plus exactly one marker pair, an
#   intact sentinel line, and a byte-identical block body.
set -euo pipefail

# ---------------------------------------------------------------------------
# Repo root (works from any cwd; CI checks out elsewhere)
# ---------------------------------------------------------------------------
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ---------------------------------------------------------------------------
# Temp root — everything lives here; cleaned up on exit
# ---------------------------------------------------------------------------
TMPROOT="$(mktemp -d)"
trap 'rm -rf "$TMPROOT"' EXIT

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
PASS=0
FAIL=0

pass() { PASS=$((PASS+1)); printf '  \033[32mPASS\033[0m  %s\n' "$1"; }
fail() { FAIL=$((FAIL+1)); printf '  \033[31mFAIL\033[0m  %s\n' "$1" >&2; exit 1; }

assert_eq() {
  # assert_eq LABEL expected actual
  local label="$1" expected="$2" actual="$3"
  if [ "$expected" = "$actual" ]; then pass "$label"; else
    printf '  \033[31mFAIL\033[0m  %s\n    expected: %s\n    actual:   %s\n' \
      "$label" "$expected" "$actual" >&2; exit 1
  fi
}

assert_file_exists()   { [ -f "$2" ] && pass "$1" || fail "$1 — file missing: $2"; }
assert_file_missing()  { [ ! -f "$2" ] && pass "$1" || fail "$1 — file should be absent: $2"; }
assert_dir_missing()   { [ ! -d "$2" ] && pass "$1" || fail "$1 — dir should be absent: $2"; }
assert_symlink()       { [ -L "$2" ] && pass "$1" || fail "$1 — expected symlink at: $2"; }
assert_no_symlink()    { [ ! -L "$2" ] && pass "$1" || fail "$1 — unexpected symlink at: $2"; }
assert_contains()      { grep -qF "$2" "$3" && pass "$1" || fail "$1 — '$2' not found in $3"; }
assert_not_contains()  { ! grep -qF "$2" "$3" && pass "$1" || fail "$1 — '$2' found (should be absent) in $3"; }
assert_count() {
  # assert_count LABEL expected_count pattern file
  local label="$1" expected="$2" pat="$3" file="$4"
  local actual; actual="$(grep -cF "$pat" "$file" 2>/dev/null || true)"
  assert_eq "$label" "$expected" "$actual"
}
assert_files_identical() {
  diff -q "$2" "$3" >/dev/null 2>&1 && pass "$1" || \
    fail "$1 — files differ: $2 vs $3"
}

prd() { bash "$REPO/bin/prd" "$@"; }

# ---------------------------------------------------------------------------
# Belt-and-suspenders: snapshot real CLAUDE.md mtime before anything runs
# ---------------------------------------------------------------------------
REAL_CLAUDE_MD="$HOME/.claude/CLAUDE.md"
if [ -f "$REAL_CLAUDE_MD" ]; then
  REAL_CLAUDE_SNAP="$TMPROOT/real_claude_md.snap"
  cp "$REAL_CLAUDE_MD" "$REAL_CLAUDE_SNAP"
fi

# ============================================================
# CASE 1: install → doctor → uninstall leaves no residue
# ============================================================
printf '\n\033[1m[1] install → doctor → uninstall (no residue)\033[0m\n'

C1="$TMPROOT/c1"
mkdir -p "$C1/claude" "$C1/bin" "$C1/prd"
export CLAUDE_HOME="$C1/claude"
export PRD_BIN_DIR="$C1/bin"
export PRD_HOME="$C1/prd"

# Fresh install — CLAUDE.md doesn't exist yet
prd install >/dev/null 2>&1
assert_file_exists  "C1: skill SKILL.md present"      "$CLAUDE_HOME/skills/prd-pipeline/SKILL.md"
assert_file_exists  "C1: rule installed"               "$CLAUDE_HOME/rules/common/feature-workflow.md"
assert_symlink      "C1: cli symlink exists"           "$PRD_BIN_DIR/prd"
assert_file_exists  "C1: CLAUDE.md created"            "$CLAUDE_HOME/CLAUDE.md"
assert_contains     "C1: CLAUDE.md has start marker"   "prd-pipeline:start" "$CLAUDE_HOME/CLAUDE.md"
assert_contains     "C1: CLAUDE.md has end marker"     "prd-pipeline:end"   "$CLAUDE_HOME/CLAUDE.md"
assert_count        "C1: exactly one start marker"  1  "prd-pipeline:start" "$CLAUDE_HOME/CLAUDE.md"
assert_count        "C1: exactly one end marker"    1  "prd-pipeline:end"   "$CLAUDE_HOME/CLAUDE.md"

# doctor exits 0
prd doctor >/dev/null 2>&1 && pass "C1: doctor exits 0" || fail "C1: doctor non-zero"

# Uninstall
prd uninstall >/dev/null 2>&1
assert_dir_missing  "C1: skill dir removed"            "$CLAUDE_HOME/skills/prd-pipeline"
assert_file_missing "C1: rule removed"                 "$CLAUDE_HOME/rules/common/feature-workflow.md"
assert_no_symlink   "C1: symlink removed"              "$PRD_BIN_DIR/prd"
# CLAUDE.md may still exist (empty) but must have no markers
if [ -f "$CLAUDE_HOME/CLAUDE.md" ]; then
  assert_not_contains "C1: start marker gone after uninstall" "prd-pipeline:start" "$CLAUDE_HOME/CLAUDE.md"
  assert_not_contains "C1: end marker gone after uninstall"   "prd-pipeline:end"   "$CLAUDE_HOME/CLAUDE.md"
else
  pass "C1: CLAUDE.md absent after uninstall (ok)"
  pass "C1: no end marker (file absent)"
fi

# ============================================================
# CASE 2: managed-block insert → refresh (idempotent) → remove
# ============================================================
printf '\n\033[1m[2] CLAUDE.md insert → refresh (idempotent) → remove\033[0m\n'

C2="$TMPROOT/c2"
mkdir -p "$C2/claude" "$C2/bin" "$C2/prd"
export CLAUDE_HOME="$C2/claude"
export PRD_BIN_DIR="$C2/bin"
export PRD_HOME="$C2/prd"

SENTINEL="UNIQUE-SENTINEL-LINE-42"
printf '%s\n' "$SENTINEL" > "$CLAUDE_HOME/CLAUDE.md"

# Install #1: append block
prd install >/dev/null 2>&1
assert_count "C2: one start marker after install#1" 1 "prd-pipeline:start" "$CLAUDE_HOME/CLAUDE.md"
assert_count "C2: one end marker after install#1"   1 "prd-pipeline:end"   "$CLAUDE_HOME/CLAUDE.md"
assert_contains "C2: sentinel intact after install#1" "$SENTINEL" "$CLAUDE_HOME/CLAUDE.md"

# Snapshot block body to compare across refreshes
BLOCK_BODY_1="$(awk '/<!-- prd-pipeline:start/{f=1; next} /<!-- prd-pipeline:end -->/{f=0} f{print}' "$CLAUDE_HOME/CLAUDE.md")"

# Install #2: refresh — block body must be identical, sentinel must survive
prd install >/dev/null 2>&1
assert_count "C2: one start marker after install#2" 1 "prd-pipeline:start" "$CLAUDE_HOME/CLAUDE.md"
assert_count "C2: one end marker after install#2"   1 "prd-pipeline:end"   "$CLAUDE_HOME/CLAUDE.md"
assert_contains "C2: sentinel intact after install#2" "$SENTINEL" "$CLAUDE_HOME/CLAUDE.md"
cp "$CLAUDE_HOME/CLAUDE.md" "$TMPROOT/c2_run2.md"

BLOCK_BODY_2="$(awk '/<!-- prd-pipeline:start/{f=1; next} /<!-- prd-pipeline:end -->/{f=0} f{print}' "$CLAUDE_HOME/CLAUDE.md")"
assert_eq "C2: block body byte-identical after refresh" "$BLOCK_BODY_1" "$BLOCK_BODY_2"

# Install #3: refresh path now strips trailing blanks before re-appending, so the
# whole file reaches a stable steady state — run #2 and run #3 must be byte-identical.
prd install >/dev/null 2>&1
assert_count "C2: one start marker after install#3" 1 "prd-pipeline:start" "$CLAUDE_HOME/CLAUDE.md"
assert_count "C2: one end marker after install#3"   1 "prd-pipeline:end"   "$CLAUDE_HOME/CLAUDE.md"
assert_contains "C2: sentinel intact after install#3" "$SENTINEL" "$CLAUDE_HOME/CLAUDE.md"
cp "$CLAUDE_HOME/CLAUDE.md" "$TMPROOT/c2_run3.md"
assert_files_identical "C2: whole-file steady state (run#2 == run#3, no blank-line growth)" \
  "$TMPROOT/c2_run2.md" "$TMPROOT/c2_run3.md"

# Remove: uninstall strips the markers
prd uninstall >/dev/null 2>&1
assert_not_contains "C2: start marker gone after uninstall" "prd-pipeline:start" "$CLAUDE_HOME/CLAUDE.md"
assert_not_contains "C2: end marker gone after uninstall"   "prd-pipeline:end"   "$CLAUDE_HOME/CLAUDE.md"
# Sentinel line must still be in the file (truncation guard)
assert_contains "C2: sentinel survives uninstall" "$SENTINEL" "$CLAUDE_HOME/CLAUDE.md"

# ============================================================
# CASE 3: missing :end marker — CLAUDE.md left unchanged (automated mutation)
# ============================================================
printf '\n\033[1m[3] Missing :end marker guard — CLAUDE.md unchanged (mutation case)\033[0m\n'

C3="$TMPROOT/c3"
mkdir -p "$C3/claude" "$C3/bin" "$C3/prd"
export CLAUDE_HOME="$C3/claude"
export PRD_BIN_DIR="$C3/bin"
export PRD_HOME="$C3/prd"

# Seed a block with :start but deliberately NO :end (the mutated/broken state)
cat > "$CLAUDE_HOME/CLAUDE.md" <<'SEED'
BEFORE_CONTENT
<!-- prd-pipeline:start (managed by `prd install` — do not edit inside) -->
## prd-pipeline (feature workflow)
Body line without the end marker.
AFTER_SENTINEL_NO_END
SEED

# Snapshot CLAUDE.md before install
cp "$CLAUDE_HOME/CLAUDE.md" "$TMPROOT/c3_before.md"

# install must exit 0 (the warning branch still exits 0; skill/rule/symlink get created)
prd install >/dev/null 2>&1 && pass "C3: prd install exits 0 even with missing :end" || \
  fail "C3: prd install should exit 0 even with missing :end marker"

# CLAUDE.md must be byte-identical to before
assert_files_identical "C3: CLAUDE.md byte-identical (missing :end guard worked)" \
  "$TMPROOT/c3_before.md" "$CLAUDE_HOME/CLAUDE.md"

# Skill, rule, and symlink must still be installed (the guard only skips CLAUDE.md)
assert_file_exists "C3: skill installed despite guard" "$CLAUDE_HOME/skills/prd-pipeline/SKILL.md"
assert_file_exists "C3: rule installed despite guard"  "$CLAUDE_HOME/rules/common/feature-workflow.md"
assert_symlink      "C3: symlink created despite guard" "$PRD_BIN_DIR/prd"

# ============================================================
# CASE 4: manual mention (bare "prd-pipeline", no markers) — left untouched
# ============================================================
printf '\n\033[1m[4] Manual mention (no markers) — CLAUDE.md left untouched\033[0m\n'

C4="$TMPROOT/c4"
mkdir -p "$C4/claude" "$C4/bin" "$C4/prd"
export CLAUDE_HOME="$C4/claude"
export PRD_BIN_DIR="$C4/bin"
export PRD_HOME="$C4/prd"

printf 'This CLAUDE.md already mentions prd-pipeline without markers.\n' \
  > "$CLAUDE_HOME/CLAUDE.md"
cp "$CLAUDE_HOME/CLAUDE.md" "$TMPROOT/c4_before.md"

prd install >/dev/null 2>&1

assert_files_identical "C4: CLAUDE.md byte-identical (manual-mention left untouched)" \
  "$TMPROOT/c4_before.md" "$CLAUDE_HOME/CLAUDE.md"

# ============================================================
# CASE 5: symlink resolves to repo's bin/prd
# ============================================================
printf '\n\033[1m[5] Symlink resolves to repo bin/prd\033[0m\n'

C5="$TMPROOT/c5"
mkdir -p "$C5/claude" "$C5/bin" "$C5/prd"
export CLAUDE_HOME="$C5/claude"
export PRD_BIN_DIR="$C5/bin"
export PRD_HOME="$C5/prd"

prd install >/dev/null 2>&1

assert_symlink "C5: $PRD_BIN_DIR/prd is a symlink" "$PRD_BIN_DIR/prd"
LINK_TARGET="$(readlink "$PRD_BIN_DIR/prd")"
assert_eq "C5: symlink targets repo bin/prd" "$REPO/bin/prd" "$LINK_TARGET"

# ============================================================
# CASE 6: plain-file uninstall guard — pre-existing file left intact
# ============================================================
printf '\n\033[1m[6] Plain-file guard — pre-existing file at PRD_BIN_DIR/prd left untouched\033[0m\n'
# Rationale: uninstall uses [ -L ] so it only removes what it created (a symlink).
# A pre-existing plain file we didn't create is intentionally preserved — don't
# delete what we didn't create. This is a safety feature, not a bug.

C6="$TMPROOT/c6"
mkdir -p "$C6/claude" "$C6/bin_plain" "$C6/prd"
export CLAUDE_HOME="$C6/claude"
export PRD_BIN_DIR="$C6/bin_plain"
export PRD_HOME="$C6/prd"

# Place a plain file at the target path (NOT a symlink we created)
printf 'pre-existing plain file\n' > "$PRD_BIN_DIR/prd"
cp "$PRD_BIN_DIR/prd" "$TMPROOT/c6_plain_before"

# Run uninstall (no install was run — simulate pre-existing file scenario)
prd uninstall >/dev/null 2>&1

assert_file_exists  "C6: plain file still present after uninstall" "$PRD_BIN_DIR/prd"
assert_no_symlink   "C6: plain file is not a symlink"              "$PRD_BIN_DIR/prd"
assert_files_identical "C6: plain file contents unchanged"         \
  "$TMPROOT/c6_plain_before" "$PRD_BIN_DIR/prd"

# ============================================================
# CASE 7: install --project writes only to project dir (no global writes)
# ============================================================
printf '\n\033[1m[7] install --project — only project dir written, no global writes\033[0m\n'

C7="$TMPROOT/c7"
mkdir -p "$C7/claude" "$C7/bin" "$C7/prd" "$C7/myproject"
export CLAUDE_HOME="$C7/claude"
export PRD_BIN_DIR="$C7/bin"
export PRD_HOME="$C7/prd"

prd install --project "$C7/myproject" >/dev/null 2>&1

assert_file_exists "C7: project skill SKILL.md installed" \
  "$C7/myproject/.claude/skills/prd-pipeline/SKILL.md"
assert_file_missing "C7: no global CLAUDE.md created"     "$CLAUDE_HOME/CLAUDE.md"
assert_dir_missing  "C7: no global skill dir created"     "$CLAUDE_HOME/skills/prd-pipeline"
assert_no_symlink   "C7: no global symlink created"        "$PRD_BIN_DIR/prd"

# ============================================================
# CASE 8: install.sh local-checkout path (exec's bin/prd install)
# ============================================================
printf '\n\033[1m[8] install.sh local-checkout — exec'\''s bin/prd install\033[0m\n'

C8="$TMPROOT/c8"
mkdir -p "$C8/claude" "$C8/bin" "$C8/prd"
export CLAUDE_HOME="$C8/claude"
export PRD_BIN_DIR="$C8/bin"
export PRD_HOME="$C8/prd"

bash "$REPO/install.sh" >/dev/null 2>&1

assert_file_exists "C8: skill installed via install.sh" "$CLAUDE_HOME/skills/prd-pipeline/SKILL.md"
assert_file_exists "C8: rule installed via install.sh"  "$CLAUDE_HOME/rules/common/feature-workflow.md"
assert_symlink     "C8: symlink created via install.sh" "$PRD_BIN_DIR/prd"
assert_contains    "C8: CLAUDE.md wired via install.sh" "prd-pipeline:start" "$CLAUDE_HOME/CLAUDE.md"

# ============================================================
# CASE 9: prd version + symlink-safe invocation
# ============================================================
printf '\n\033[1m[9] prd version (direct + via symlink)\033[0m\n'

C9="$TMPROOT/c9"
mkdir -p "$C9/claude" "$C9/bin" "$C9/prd"
export CLAUDE_HOME="$C9/claude"; export PRD_BIN_DIR="$C9/bin"; export PRD_HOME="$C9/prd"

EXPECT_VER="$(tr -d '[:space:]' < "$REPO/VERSION")"
assert_eq "C9: prd version (direct)" "$EXPECT_VER" "$(prd version)"

# install, then invoke through the installed symlink — exercises symlink-safe REPO_ROOT
prd install >/dev/null 2>&1
assert_symlink "C9: symlink exists" "$PRD_BIN_DIR/prd"
assert_eq "C9: prd version (via symlink)" "$EXPECT_VER" "$(bash "$PRD_BIN_DIR/prd" version)"
prd uninstall >/dev/null 2>&1

# ============================================================
# CASE 10: doctor reports version + warns on drift
# ============================================================
printf '\n\033[1m[10] doctor version + drift\033[0m\n'

C10="$TMPROOT/c10"
mkdir -p "$C10/claude" "$C10/bin" "$C10/prd"
export CLAUDE_HOME="$C10/claude"; export PRD_BIN_DIR="$C10/bin"; export PRD_HOME="$C10/prd"

prd install >/dev/null 2>&1
assert_file_exists "C10: VERSION copied into skill dir" "$CLAUDE_HOME/skills/prd-pipeline/VERSION"

CLONE_VER="$(tr -d '[:space:]' < "$REPO/VERSION")"
DOC="$(prd doctor 2>&1)"
case "$DOC" in *"$CLONE_VER"*) pass "C10: doctor prints version" ;; *) fail "C10: doctor missing version" ;; esac

# Seed a stale installed VERSION → doctor must warn about drift
printf '0.0.1\n' > "$CLAUDE_HOME/skills/prd-pipeline/VERSION"
DOC2="$(prd doctor 2>&1)"
case "$DOC2" in *drift*) pass "C10: doctor warns on drift" ;; *) fail "C10: no drift warning" ;; esac
prd uninstall >/dev/null 2>&1

# ============================================================
# Belt-and-suspenders: real CLAUDE.md must be untouched
# ============================================================
if [ -f "$REAL_CLAUDE_MD" ] && [ -f "$REAL_CLAUDE_SNAP" ]; then
  assert_files_identical "ISOLATION: real ~/.claude/CLAUDE.md unchanged throughout" \
    "$REAL_CLAUDE_SNAP" "$REAL_CLAUDE_MD"
fi

# ============================================================
# Summary
# ============================================================
printf '\n\033[32m✓ All %d assertions passed.\033[0m\n' "$PASS"
