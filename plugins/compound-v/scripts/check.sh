#!/usr/bin/env bash
# check.sh — verify Compound V against its own constitution and publish boundary.
# No dependencies. Run from anywhere:  bash scripts/check.sh
# Exit 0 = clean, 1 = at least one failure.

set -uo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root" || exit 2

fail=0
warn=0
err()  { printf 'FAIL  %s\n' "$1"; fail=$((fail + 1)); }
note() { printf 'warn  %s\n' "$1"; warn=$((warn + 1)); }

# 1. Frontmatter, name matches directory, description present, line budget.
#    Constitution: target <=250 lines, hard ceiling 500.
for f in skills/*/SKILL.md; do
  d="$(basename "$(dirname "$f")")"
  head -1 "$f" | grep -q '^---' || err "$f: missing frontmatter opener"
  name="$(awk -F': *' '/^name:/{print $2; exit}' "$f")"
  [ "$name" = "$d" ] || err "$f: name '$name' does not match directory '$d'"
  awk '/^description:/{ok=1} END{exit !ok}' "$f" || err "$f: no description"
  n="$(wc -l < "$f")"
  if   [ "$n" -gt 500 ]; then err  "$f: $n lines (over the 500 hard ceiling)"
  elif [ "$n" -gt 250 ]; then note "$f: $n lines (over the 250 target)"
  fi
done

# 2. Publish boundary: shipped files must never name the internal research corpus.
#    (scripts/ is excluded on purpose — this file holds the pattern itself.)
leak="$(grep -rnoE 'BAD_GUIDE|researchfms|teardowns|skills_research|research/(findings|SYNTH|sources)|/Users/[a-z]' \
  skills/ references/ README.md .claude-plugin/ 2>/dev/null || true)"
if [ -n "$leak" ]; then
  err "internal-corpus references in shipped files (these must never publish):"
  printf '%s\n' "$leak" | sed 's/^/        /'
fi

# 3. Cross-reference integrity: every compound-v:<name> resolves to a real skill.
for r in $(grep -rhoE 'compound-v:[a-z][a-z-]+' skills/ README.md 2>/dev/null | sed 's/compound-v://' | sort -u); do
  [ -d "skills/$r" ] || err "dangling cross-reference: compound-v:$r (no skills/$r)"
done

# 4. No @path skill links (they force-load and burn context).
if grep -rnE '@[a-z][a-z-]*/SKILL|@compound-v' skills/ >/dev/null 2>&1; then
  err "@path skill link found (use 'compound-v:<name>' by name instead):"
  grep -rnE '@[a-z][a-z-]*/SKILL|@compound-v' skills/ | sed 's/^/        /'
fi

skills_n="$(find skills -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')"
printf '\n%s skills checked — %s failure(s), %s warning(s)\n' "$skills_n" "$fail" "$warn"
[ "$fail" -eq 0 ]
