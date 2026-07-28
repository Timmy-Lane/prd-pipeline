#!/usr/bin/env bash
# Structural checks on the marketplace bundle itself. No install, no network.
#
#   bash tests/bundle-consistency.sh
#
# Exit 0 = clean, 1 = at least one failure.
set -uo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root" || exit 2

fail=0
ok()   { printf '  \033[32mPASS\033[0m  %s\n' "$1"; }
bad()  { printf '  \033[31mFAIL\033[0m  %s\n' "$1"; fail=1; }

printf '\n\033[1m[1] Every marketplace plugin with a local source exists and declares itself\033[0m\n'
while read -r name src; do
  case "$src" in
    ./*)
      if [ -f "$src/.claude-plugin/plugin.json" ]; then
        declared="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["name"])' "$src/.claude-plugin/plugin.json")"
        [ "$declared" = "$name" ] \
          && ok "$name: manifest present, name matches" \
          || bad "$name: manifest declares '$declared'"
      else
        bad "$name: $src/.claude-plugin/plugin.json missing"
      fi ;;
    *) ok "$name: remote source ($src) — resolved at install time" ;;
  esac
done < <(python3 - <<'PY'
import json
m = json.load(open(".claude-plugin/marketplace.json"))
for p in m["plugins"]:
    s = p["source"]
    print(p["name"], s if isinstance(s, str) else s.get("url", "remote"))
PY
)

printf '\n\033[1m[2] Every local plugin ships at least one skill\033[0m\n'
for d in plugins/*/; do
  n="$(basename "$d")"
  if compgen -G "$d/skills/*/SKILL.md" >/dev/null; then
    ok "$n: $(compgen -G "$d/skills/*/SKILL.md" | wc -l | tr -d ' ') skill(s)"
  else
    bad "$n: no skills/*/SKILL.md"
  fi
done

printf '\n\033[1m[3] Every SKILL.md has frontmatter whose name matches its directory\033[0m\n'
for f in plugins/*/skills/*/SKILL.md; do
  d="$(basename "$(dirname "$f")")"
  head -1 "$f" | grep -q '^---' || { bad "$f: no frontmatter opener"; continue; }
  name="$(awk -F': *' '/^name:/{print $2; exit}' "$f")"
  [ "$name" = "$d" ] || { bad "$f: name '$name' != dir '$d'"; continue; }
  awk '/^description:/{ok=1} END{exit !ok}' "$f" || { bad "$f: no description"; continue; }
  ok "$d"
done

# bad-research vendors its own engine, and the engine carries a second copy of every
# step skill for the standalone `bad install --steps-only` path. The two copies use
# different skill-name forms on purpose (namespaced vs bare), so they can never be
# byte-identical — but they MUST NOT contradict each other on whether the step skills
# need installing at all. When they do, whichever copy the model happens to read
# decides whether it sprays 19 diverging skill directories into the user's repo.
printf '\n\033[1m[4] bad-research entry skill: the two copies agree on the step-skills install\033[0m\n'
plug="plugins/bad-research/skills/bad-research/SKILL.md"
eng="plugins/bad-research/engine/src/bad_research/skills/bad-research.md"
if [ -f "$plug" ] && [ -f "$eng" ]; then
  # Both must tell a plugin user NOT to run the per-project step install.
  grep -q 'ships bundled inside this plugin' "$plug" \
    && ok "plugin copy: states the step skills ship bundled" \
    || bad "plugin copy: lost the bundled-step-skills statement"
  if grep -q 'steps-only' "$eng"; then
    grep -q 'do NOT run `bad install --steps-only`' "$eng" \
      && ok "engine copy: guards the lazy install behind a plugin check" \
      || bad "engine copy: instructs 'bad install --steps-only' with no plugin guard (github.com/Timmy-Lane/prd-pipeline/issues/1)"
  else
    ok "engine copy: no lazy-install instruction"
  fi
else
  bad "bad-research entry skill copies not found"
fi

printf '\n'
[ "$fail" -eq 0 ] && printf '\033[32mbundle consistent\033[0m\n' || printf '\033[31mbundle has failures\033[0m\n'
exit "$fail"
