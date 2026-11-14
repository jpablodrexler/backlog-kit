#!/usr/bin/env python3
"""SessionEnd hook: save a summary of the finished session into the brain.

Claude Code runs this with the hook input as JSON on stdin (session_id,
transcript_path, cwd, reason). It extracts the conversation text and starts a
detached headless `claude -p` that writes the journal entry and updates the
project notes, following the brain skill. It never runs git.

Environment:
    BRAIN_DIR                where the brain is (same rule as brain.py)
    BRAIN_AUTOSAVE_MODEL     model for the summary (default: the CLI's default)
    BRAIN_AUTOSAVE_CLAUDE    the claude executable (default: found on PATH)
    BRAIN_AUTOSAVE_WAIT=1    run in the foreground (tests, debugging)
Log: <brain>/.autosave.log
"""
import json
import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brain import brain_dir  # noqa: E402

GUARD = "BRAIN_AUTOSAVE_RUNNING"   # set for the child, so its own SessionEnd does not start another summary
MIN_USER_MESSAGES = 2
MAX_CHARS = 60000

PROMPT = """You are saving the summary of a finished work session into the user's personal brain, using the `brain` skill rules (Capture).

Brain folder (your working directory): {brain}
Session id: {sid}    Date: {today}    Project folder of the session: {cwd}

The conversation is on stdin. Do this, and nothing else:
1. Run `{py} {script} search <project and subject terms>` and read the notes it finds.
2. Append an entry to journal/{today}.md (create it with front matter if missing): what was done, what was decided, what is left, with links to the notes you touch. Start the entry with `<!-- session: {sid} -->`; if an entry with that marker already exists, update it instead of adding another.
3. Update or create project/topic/decision notes ONLY for durable context a future session would need. Prefer updating an existing note; bump `updated`.
4. Run `{py} {script} index`.
Never write credentials, tokens, or private data about third parties. If the session had nothing worth keeping, write only a one-line journal entry. Write in the language the user used. Do not run git."""


def text_of(content):
    if isinstance(content, str):
        return content
    return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")


def conversation(path):
    """-> (text, number of user messages). Only the spoken text: no tool calls or results."""
    out, users = [], 0
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("type") not in ("user", "assistant") or e.get("isMeta") or e.get("isSidechain"):
            continue
        t = text_of((e.get("message") or {}).get("content", "")).strip()
        if not t or t.startswith("<"):          # command and system wrappers
            continue
        users += e["type"] == "user"
        out.append(f"{'USER' if e['type'] == 'user' else 'CLAUDE'}: {t}")
    text = "\n\n".join(out)
    if len(text) > MAX_CHARS:                   # keep the start (the goal) and the end (the outcome)
        text = text[:MAX_CHARS // 3] + "\n\n[... middle of the session omitted ...]\n\n" + text[-2 * MAX_CHARS // 3:]
    return text, users


def main():
    if os.environ.get(GUARD):
        return 0
    try:
        hook = json.load(sys.stdin)
    except ValueError:
        return 0
    tpath = hook.get("transcript_path")
    if not tpath or not Path(tpath).is_file():
        return 0
    text, users = conversation(tpath)
    if users < MIN_USER_MESSAGES:
        return 0
    brain = brain_dir()
    brain.mkdir(parents=True, exist_ok=True)
    exe = os.environ.get("BRAIN_AUTOSAVE_CLAUDE") or shutil.which("claude")
    log = brain / ".autosave.log"
    if not exe:
        log.open("a").write(f"{date.today()} {hook.get('session_id')}: claude not found on PATH\n")
        return 0
    py = "python" if os.name == "nt" else "python3"     # on Windows `python3` is often a Store stub
    prompt = PROMPT.format(brain=brain, sid=hook.get("session_id", "unknown"), today=date.today().isoformat(),
                           cwd=hook.get("cwd", ""), script=Path(__file__).with_name("brain.py"), py=py)
    cmd = [exe, "-p", prompt, "--permission-mode", "acceptEdits",
           "--allowedTools", "Read,Write,Edit,Bash(python3 *brain.py*),Bash(python *brain.py*)"]
    if os.environ.get("BRAIN_AUTOSAVE_MODEL"):
        cmd += ["--model", os.environ["BRAIN_AUTOSAVE_MODEL"]]
    kw = {"cwd": str(brain), "env": {**os.environ, GUARD: "1"}, "stderr": subprocess.STDOUT}
    with log.open("a", encoding="utf-8") as lg:
        lg.write(f"--- {date.today()} {hook.get('session_id')} ({hook.get('reason', '')})\n")
        lg.flush()
        if os.environ.get("BRAIN_AUTOSAVE_WAIT"):
            subprocess.run(cmd, input=text, text=True, encoding="utf-8", stdout=lg, **kw)
            return 0
        if os.name == "nt":
            kw["creationflags"] = 0x00000008 | 0x00000200      # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        else:
            kw["start_new_session"] = True
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=lg, text=True, encoding="utf-8", **kw)
        p.stdin.write(text)
        p.stdin.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
