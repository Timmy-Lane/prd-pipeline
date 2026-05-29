#!/usr/bin/env bash
# prd-pipeline bootstrap installer.
#
#   Remote one-liner:
#     curl -fsSL https://raw.githubusercontent.com/Timmy-Lane/prd-pipeline/main/install.sh | bash
#   Or from a clone:
#     ./install.sh
#
# Clones (or updates) the repo to $PRD_HOME (default ~/.prd-pipeline) when run
# remotely, then runs `bin/prd install` (skill + rule + CLAUDE.md wiring + PATH).
set -euo pipefail

PRD_HOME="${PRD_HOME:-$HOME/.prd-pipeline}"
REPO_URL="${PRD_REPO_URL:-https://github.com/Timmy-Lane/prd-pipeline.git}"
# Only allow https:// clone sources — block git transport-helper tricks (ext::, fd::, file://…).
case "$REPO_URL" in
  https://*) : ;;
  *) echo "PRD_REPO_URL must be an https:// URL (got: $REPO_URL)" >&2; exit 1 ;;
esac

# If executed from inside a checkout (not piped), install from here.
SELF="${BASH_SOURCE[0]:-}"
if [ -n "$SELF" ] && [ -f "$SELF" ]; then
  HERE="$(cd "$(dirname "$SELF")" && pwd)"
  if [ -f "$HERE/skills/prd-pipeline/SKILL.md" ]; then
    exec "$HERE/bin/prd" install
  fi
fi

# Otherwise (curl | bash): clone or fast-forward, then install.
command -v git >/dev/null 2>&1 || { echo "git is required" >&2; exit 1; }
if [ -d "$PRD_HOME/.git" ]; then
  echo "updating $PRD_HOME ..."
  git -C "$PRD_HOME" pull --ff-only || true
else
  echo "cloning prd-pipeline → $PRD_HOME ..."
  git clone --depth 1 "$REPO_URL" "$PRD_HOME"
fi
exec "$PRD_HOME/bin/prd" install
