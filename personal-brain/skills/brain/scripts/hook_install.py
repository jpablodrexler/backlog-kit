#!/usr/bin/env python3
"""Add (or remove) the brain's SessionEnd hook in the user's Claude Code settings.

    python3 hook_install.py            # enable auto-save
    python3 hook_install.py --remove   # disable it

Edits $CLAUDE_HOME/settings.json (default ~/.claude/settings.json); keeps everything else.
"""
import json
import os
import sys
from pathlib import Path


def settings_path():
    return Path(os.environ.get("CLAUDE_HOME") or Path.home() / ".claude") / "settings.json"


def main(argv):
    script = Path(__file__).resolve().with_name("session_end.py")
    command = f'"{sys.executable}" "{script}"'
    path = settings_path()
    data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    groups = data.setdefault("hooks", {}).setdefault("SessionEnd", [])
    mine = lambda h: "session_end.py" in h.get("command", "") and "brain" in h.get("command", "").lower()
    for g in groups:                                  # drop any earlier copy of this hook
        g["hooks"] = [h for h in g.get("hooks", []) if not mine(h)]
    groups[:] = [g for g in groups if g.get("hooks")]
    if "--remove" not in argv:
        groups.append({"hooks": [{"type": "command", "command": command, "timeout": 30}]})
    if not groups:
        del data["hooks"]["SessionEnd"]
    if not data["hooks"]:
        del data["hooks"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(("auto-save removed from " if "--remove" in argv else "auto-save enabled in ") + str(path))


if __name__ == "__main__":
    main(sys.argv[1:])
