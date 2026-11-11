# personal-brain

A personal memory for Claude: a folder of markdown notes plus a `brain` skill that searches it and writes to it. Independent of the rest of backlog-kit.

```
~/brain/                    # your notes (data) — its own private repo, if you want history
  INDEX.md                  # generated map of every note
  projects/<project>/*.md
  topics/  decisions/  people/  journal/  inbox/

~/.claude/skills/brain/     # the skill (code) — installed by install.sh
  SKILL.md
  scripts/brain.py          # search, recent, index, check (standard library only)
```

## Install

```
./install.sh                       # skill -> ~/.claude/skills/brain, folders -> ~/brain
BRAIN_DIR=~/Documents/brain ./install.sh    # another location (export it in your shell profile too)
```

The skill lives in your user folder, so it works from any project. The brain is outside every repo on purpose: it holds personal context. To keep history, `git init` it as a private repo; the skill never commits.

## Use

- Recall: "¿qué decidimos sobre la autenticación de acme?" — Claude searches the brain and reads the notes before answering.
- Capture: "guarda esto en el brain" — Claude updates the existing note or creates one, appends to the journal, rebuilds the index and tells you what changed. Without being asked it only offers.
- Tidy: "revisa el brain" — runs `check` and fixes the mechanical problems.

## Tests

`python3 -m unittest discover -s tests`

## Limits

Search is keyword-based with weights (title, tags, summary, path, body) and ignores accents; it does not understand synonyms, so the skill has Claude try more than one term. If the brain grows to thousands of notes, an embeddings index can sit behind `brain.py search` without changing the skill.
