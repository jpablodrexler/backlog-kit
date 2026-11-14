#!/usr/bin/env bash
# Install the brain skill for the current user (all projects) and create the brain folder.
#   ./install.sh              # skill -> ~/.claude/skills/brain, brain -> its default location
#   ./install.sh --auto-save  # also save a summary of every session (SessionEnd hook)
#   ./install.sh --no-auto-save   # remove that hook
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
# First interpreter that really runs (on Windows, `python3` is often a Microsoft Store stub that does nothing).
py=""
for c in python3 python py; do
  if "$c" -c "import sys; sys.exit(sys.version_info < (3, 8))" >/dev/null 2>&1; then py="$c"; break; fi
done
[ -n "$py" ] || { echo "No working Python 3.8+ found (tried python3, python, py). Install Python and retry." >&2; exit 1; }
dest="${CLAUDE_HOME:-$HOME/.claude}/skills/brain"
mkdir -p "$(dirname "$dest")"
rm -rf "$dest"
cp -r "$here/skills/brain" "$dest"
find "$dest" -name __pycache__ -prune -exec rm -rf {} +
"$py" "$dest/scripts/brain.py" init
case "${1:-}" in
  --auto-save) "$py" "$dest/scripts/hook_install.py" ;;
  --no-auto-save) "$py" "$dest/scripts/hook_install.py" --remove ;;
esac
echo "skill installed at $dest"
