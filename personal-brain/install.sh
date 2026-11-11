#!/usr/bin/env bash
# Install the brain skill for the current user (all projects) and create the brain folder.
#   ./install.sh              # skill -> ~/.claude/skills/brain, brain -> $BRAIN_DIR or ~/brain
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
dest="${CLAUDE_HOME:-$HOME/.claude}/skills/brain"
mkdir -p "$(dirname "$dest")"
rm -rf "$dest"
cp -r "$here/skills/brain" "$dest"
find "$dest" -name __pycache__ -prune -exec rm -rf {} +
python3 "$dest/scripts/brain.py" init
echo "skill installed at $dest"
