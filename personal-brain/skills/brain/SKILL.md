---
name: brain
description: >-
  Personal long-term memory: a folder of markdown notes (default: a "brain" folder in OneDrive on
  Windows, else ~/brain; or $BRAIN_DIR) that holds the context of what the user works on with Claude, so
  it can be searched later. RECALL: search the brain before answering when the
  user refers to earlier work, a project, a decision, a person or "what we did
  / what I said about X", and when starting work on a project that may have
  notes. CAPTURE: save durable context (state of a project, decisions and why,
  things learned, gotchas, next steps) when asked ("guarda esto", "anota",
  "remember this", "save to my brain") or offer to when a significant piece of
  work ends. TRIGGER on any of those, on "brain", "mi cerebro", "second brain",
  "memoria", and on setting up or tidying the brain. Does not store credentials.
license: MIT
---

The brain is a folder of markdown notes. You read it to avoid asking the user for context they already gave you, and you write to it so the next session starts informed. Notes are written for a future you with no memory of this conversation.

**Never run `git commit`, `git push` or open a PR.** The brain may be a git repository of the user's own; they commit it.

`<brain>` is `$BRAIN_DIR`; else, on Windows, the `brain` folder inside the OneDrive folder (so it syncs); else `~/brain`. `<scripts>` is `scripts/` next to this file; run it from this skill's base directory. The script does the searching and bookkeeping; the writing is yours.

```
python3 <scripts>/brain.py where                      # where the brain is, and whether it exists
python3 <scripts>/brain.py init                       # create the folders, once
python3 <scripts>/brain.py search <terms> [--area A] [--tag T] [--limit N]
python3 <scripts>/brain.py recent                     # what changed last
python3 <scripts>/brain.py index                      # rebuild INDEX.md after writing notes
python3 <scripts>/brain.py check                      # missing front matter, broken links, stale index
```

Input: what the user wants: recall something, save something, or set up / tidy the brain. Map it to **Recall**, **Capture** or **Maintain**.

If `where` says the brain is missing, tell the user where it would be created and run `init` only after they agree (they may want another location: then set `BRAIN_DIR`).

---

## Layout

| Folder | What goes in it |
|---|---|
| `projects/<project>/` | State, decisions, gotchas, next steps of one project; one note per subject |
| `topics/` | What was learned about a subject, reusable across projects |
| `decisions/` | A choice, the alternatives rejected and why |
| `people/` | Who someone is, what they own, how to work with them |
| `journal/` | `YYYY-MM-DD.md`: one dated entry per work session, newest at the bottom |
| `inbox/` | Raw captures not filed yet |

Add a folder when none fits; do not force a note into the wrong one. File names are lowercase, hyphenated slugs (`projects/acme-api/auth-flow.md`).

## Note format

```markdown
---
title: Auth flow of the acme API
summary: One line saying what is in the note, in the words you would search for.
tags: [auth, acme-api]
project: acme-api
created: 2026-11-11
updated: 2026-11-11
---

# Auth flow of the acme API
...
```

`title` and `summary` are required: the search and `INDEX.md` are built on them. Write in the language the user uses with you. Link related notes with relative markdown links (`[decision](../../decisions/jwt-vs-session.md)`).

---

## Recall

1. Pick 1-3 terms from the request: the project, the subject, a name. Use the user's words and one synonym.
2. `search` them. For a vague ask ("what was I doing last week"), use `recent` and read `journal/`.
3. Read the best 1-3 notes in full; do not answer from the snippets alone.
4. Answer from the notes and name the files you used. Say which parts are old: a note's `updated` date tells how stale it may be, and the code or the world may have moved on.
5. Nothing found: say so and ask. Never fill the gap with a guess dressed as a memory.

Recall silently when the user clearly refers to past work. When you start work on a project and have not searched yet, one `search` on the project name is cheap and worth it.

## Capture

Save what a future session would otherwise have to ask again or rediscover:

- the state of a project and the next step
- a decision, the alternatives rejected and the reason
- something learned the hard way, and the symptom that would lead back to it
- how the user likes to work, a person's role, a convention

Do not save: transcripts, anything the code or the repo docs already say, passing details, credentials, tokens or private data about third parties. If the user hands you one, leave it out and say so.

Steps:

1. **Search first** (`search`) for an existing note on the subject. Update it rather than create a duplicate; keep it a current picture, not a log. Replace what is no longer true, and bump `updated`.
2. For a new note, choose the folder, write the front matter and a body of short sections or bullets. Include the date and the *why*, not only the what.
3. When the session itself is worth recording, append a short entry to `journal/<today>.md`: what was done, what was decided, what is left, with links to the notes you touched.
4. `index`, then tell the user in one or two lines which files you created or changed.

When the user asks explicitly, save directly. Without an ask, offer in one line at the end of significant work ("¿Lo guardo en el brain?") and wait; do not write unprompted. The exception is auto-save: when the user enabled it (`install.sh --auto-save`), a SessionEnd hook runs `scripts/session_end.py`, which starts a headless `claude -p` that applies these same steps to the finished session. Its journal entries start with `<!-- session: <id> -->`; update the entry with the same id rather than adding another. Treat such entries as machine summaries: useful for orientation, to be checked against the code before relying on them.

## Maintain

`check` reports missing `title`/`summary`, broken links, duplicate titles and a stale index. Fix what is mechanical (index, links); for merging or deleting notes, show the user what you would change and wait. Never delete a note without being asked.
