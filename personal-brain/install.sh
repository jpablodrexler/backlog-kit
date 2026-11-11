#!/usr/bin/env bash
# Install the brain skill for the current user (all projects) and create the brain folder.
#   ./install.sh              # skill -> ~/.claude/skills/brain, brain -> its default location
#   ./install.sh --auto-save  # also save a summary of every session (SessionEnd hook)
#   ./install.sh --no-auto-save   # remove that hook
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
dest="${CLAUDE_HOME:-$HOME/.claude}/skills/brain"
mkdir -p "$(dirname "$dest")"
rm -rf "$dest"
cp -r "$here/skills/brain" "$dest"
find "$dest" -name __pycache__ -prune -exec rm -rf {} +
python3 "$dest/scripts/brain.py" init
case "${1:-}" in
  --auto-save) python3 "$dest/scripts/hook_install.py" ;;
  --no-auto-save) python3 "$dest/scripts/hook_install.py" --remove ;;
esac
echo "skill installed at $dest"
