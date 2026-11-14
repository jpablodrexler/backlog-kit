# personal-brain

A personal memory for Claude: a folder of markdown notes plus a `brain` skill that searches it and writes to it. Independent of the rest of backlog-kit.

```
~/brain/                    # your notes (data); on Windows: <OneDrive>\brain — its own private repo, if you want history
  INDEX.md                  # generated map of every note
  projects/<project>/*.md
  topics/  decisions/  people/  journal/  inbox/

~/.claude/skills/brain/     # the skill (code) — installed by install.sh
  SKILL.md
  scripts/brain.py          # search, recent, index, check (standard library only)
```

## Install

```
./install.sh                       # skill -> ~/.claude/skills/brain, folders -> the default brain location
BRAIN_DIR=~/Documents/brain ./install.sh    # another location (export it in your shell profile too)
```

Default location: `$BRAIN_DIR` if set; on Windows, a `brain` folder inside your OneDrive folder (read from `%OneDrive%`, then `%OneDriveConsumer%`, `%OneDriveCommercial%`, then `~/OneDrive`), so the notes sync across your devices; anywhere else (or on Windows without OneDrive), `~/brain`. `brain.py where` shows what it resolved.

The skill lives in your user folder, so it works from any project. The brain is outside every repo on purpose: it holds personal context. OneDrive keeps a version history, but a private git repo gives you a better one. To keep history, `git init` it as a private repo; the skill never commits.

## Use

- Recall: "¿qué decidimos sobre la autenticación de acme?" — Claude searches the brain and reads the notes before answering.
- Capture: "guarda esto en el brain" — Claude updates the existing note or creates one, appends to the journal, rebuilds the index and tells you what changed. Without being asked it only offers.
- Tidy: "revisa el brain" — runs `check` and fixes the mechanical problems.

## Auto-save of each session

```
./install.sh --auto-save       # adds a SessionEnd hook to ~/.claude/settings.json
./install.sh --no-auto-save    # removes it
```

When a session ends, `scripts/session_end.py` reads the transcript (only what you and Claude said, not tool output), skips sessions with fewer than two of your messages, and starts a detached headless `claude -p` inside the brain folder. That run searches the brain, appends an entry to `journal/<date>.md` (marked with the session id, so a resumed session updates its entry), updates the project notes that deserve it, and rebuilds the index. Its tools are limited to Read, Write, Edit and `brain.py`; it never runs git.

Things to know:
- It needs the `claude` CLI on your PATH and uses your usage like any other `claude -p` call. `BRAIN_AUTOSAVE_MODEL=haiku` makes it cheaper.
- The session text is sent to the model to summarise it, as in any session. The prompt forbids saving credentials, but read the journal now and then.
- Progress and failures go to `<brain>/.autosave.log`.
- It runs on the machine where you use Claude Code, with its own `~/.claude`. In cloud sessions the brain on your OneDrive is not reachable, so there is nothing to save to.
- It is meant for the terminal CLI. If a session never ends cleanly (killed terminal), the hook may not fire; say "guarda esto" before closing.

## Tests

`python3 -m unittest discover -s tests`

## Limits

Search is keyword-based with weights (title, tags, summary, path, body) and ignores accents; it does not understand synonyms, so the skill has Claude try more than one term. If the brain grows to thousands of notes, an embeddings index can sit behind `brain.py search` without changing the skill.
