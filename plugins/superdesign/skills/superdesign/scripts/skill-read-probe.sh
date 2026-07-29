#!/usr/bin/env bash
# skill-read-probe — the only way to know whether a reference file was ever OPENED.
# A skill that is never read cannot have worked; adherence is a claim until this says otherwise.
#
#   scripts/skill-read-probe.sh --install   # print the PostToolUse hook to paste into settings
#   scripts/skill-read-probe.sh             # report what this session actually read
#
# The hook is NOT installed automatically — .claude/settings.json is the operator's file.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$HERE/../.claude/skill-reads.log"

if [[ "${1:-}" == "--install" ]]; then
  cat <<'HOOK'
Paste into .claude/settings.json (Probe A — log every read for one session):

{ "hooks": { "PostToolUse": [ { "matcher": "Read|Grep",
  "hooks": [ { "type": "command",
    "command": "jq -r '.tool_input.file_path // .tool_input.path // empty' >> .claude/skill-reads.log" } ] } ] } }
HOOK
  exit 0
fi

if [[ ! -f "$LOG" ]]; then
  echo "no .claude/skill-reads.log — run \`$0 --install\`, paste the hook, then run a session."
  exit 1
fi

echo "reference reads : $(grep -c 'superdesign/references' "$LOG")"
echo "distinct files  :"
sort -u "$LOG" | grep superdesign | sed 's/^/    /'

cat <<'PROBES'

Probe B — citation challenge. After the run, ask:
  "Quote the exact line from references/tokens.md §10 that defines the hover overlay percentage."
  A model that never opened the file paraphrases or invents.

Probe C — canary. Put CANARY-TOKENS-A7 in a comment at line 3 of each reference file and grep
  the transcript. A quoted canary is proof of a read; its absence is not proof of a miss.

Pass bar (Anthropic's skill checklist): at least three evaluation scenarios, run on Haiku, Sonnet
and Opus, with the no-skill baseline measured FIRST.
PROBES
