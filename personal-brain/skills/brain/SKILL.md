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
  "memoria", on setting up or tidying the brain, and on migrating Claude Code's
  own memory into the brain. Does not store credentials.
license: MIT
metadata:
  author: Juan Pablo Drexler
---

The brain is a folder of markdown notes. You read it to avoid asking the user for context they already gave you, and you write to it so the next session starts informed. Notes are written for a future you with no memory of this conversation.

**Never run `git commit`, `git push` or open a PR.** The brain may be a git repository of the user's own; they commit it.

`<brain>` is `$BRAIN_DIR`; else, on Windows, the `brain` folder inside the OneDrive folder (so it syncs); else `~/brain`. `<scripts>` is `scripts/` next to this file; run it from this skill's base directory. The script does the searching and bookkeeping; the writing is yours. Commands below say `python3`; if that fails (on Windows it is often a Microsoft Store stub that prints "Python was not found"), use `python` or `py -3` instead.

```
python3 <scripts>/brain.py where                      # where the brain is, and whether it exists
python3 <scripts>/brain.py init                       # create the folders, once
python3 <scripts>/brain.py search <terms> [--area A] [--tag T] [--limit N]
python3 <scripts>/brain.py recent                     # what changed last
python3 <scripts>/brain.py index                      # rebuild INDEX.md after writing notes
python3 <scripts>/brain.py check                      # missing front matter, broken links, stale index
python3 <scripts>/brain.py memory [--project PATH]    # read-only: list a project's Claude Code memory files
python3 <scripts>/brain.py journal                    # today's journal file for THIS machine
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
| `journal/` | `YYYY-MM-DD-<machine>.md`: one file per day and machine (`journal` prints the name), one dated entry per work session, newest at the bottom. Older `YYYY-MM-DD.md` files stay valid |
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
3. When the session itself is worth recording, append a short entry to this machine's journal file (the path `journal` prints): what was done, what was decided, what is left, with links to the notes you touched.
4. `index`, then tell the user in one or two lines which files you created or changed.

When the user asks explicitly, save directly. Without an ask, offer in one line at the end of significant work ("¿Lo guardo en el brain?") and wait; do not write unprompted. The exception is auto-save: when the user enabled it (`install.sh --auto-save`), a SessionEnd hook runs `scripts/session_end.py`, which starts a headless `claude -p` that applies these same steps to the finished session. Its journal entries start with `<!-- session: <id> -->`; update the entry with the same id rather than adding another. Treat such entries as machine summaries: useful for orientation, to be checked against the code before relying on them.

## Migrate Claude Code memory into the brain

Claude Code keeps its own auto-memory per project (`~/.claude/projects/<project path with every non-alphanumeric character turned into "-">/memory/`: a `MEMORY.md` index plus one file per memory). The two differ in a way that decides how to migrate: **`MEMORY.md` is loaded into every session of that project on its own; the brain is read only when a search runs.** So the migration is a hybrid: the brain becomes the home of the content (it syncs through OneDrive, so every PC shares it), and the memory keeps one short file with the rules that must apply before any search. Do it **once per PC and project**, only when the user asks (it replaces files that shape every future session). Typical ask: "migrate your memory to the brain", on a new PC.

1. **Inventory.** `memory --project <repo folder>` lists the memory folder and each file's name, type and description. Read every file in full. `search` the brain for each subject first, to merge into an existing note instead of duplicating.
2. **Move the content.** Write one brain note per project, `topics/claude-working-rules-<project>.md`: one section per rule, each with the rule, the *why* (keep the user's own words and the date) and *how to apply*. Link to the topic notes that already cover a rule (for example a long-runs or skills note) instead of copying them. No credentials or private data.
3. **Trim the memory** (this deletes the user's files, so the migration request must have been explicit). Check that the brain note holds every migrated file's rule, why and how-to-apply, then replace the migrated files with **one** memory file, `feedback_working_rules_live_in_brain.md`: a line per rule that must apply before any search, and the path of the brain note and a `search` hint to read the rest. Reduce `MEMORY.md` to the single index line of that file. Never delete a memory file the brain note does not cover; say what you removed.
4. **Auto-save.** Check `~/.claude/settings.json` for a `SessionEnd` hook that runs the brain's `session_end.py`. If it is missing, run `./install.sh --auto-save` from the kit's `personal-brain/` folder (the script is `scripts/hook_install.py`; `--remove` undoes it). Tell the user it edits their settings file and keeps everything else.
5. **Close.** `index`, then `check`; tell the user which notes you wrote, which memory files you removed and which one remains.

**On another PC** (for example a gaming PC): install the skill there (`./install.sh --auto-save` from the kit's `personal-brain/`), point it at the same synced brain (OneDrive, or `BRAIN_DIR`), and run steps 1-5 for that PC's own memory folders. Step 2 is mostly a merge, since the shared brain already holds the rules written on the first PC.

## Several PCs, one brain

The brain is plain files, so two PCs share it through the sync client (OneDrive, Dropbox, Syncthing). A sync client does not merge: when both PCs change the same file it keeps one and writes the other as a "conflicted copy" next to it, and a note written on one PC reaches the other after a delay. So:

- Each machine writes its own journal file (`journal` prints `journal/<date>-<machine>.md`); never append to another machine's.
- Do not have two sessions edit the same note at once; split the work by project or note.
- `INDEX.md` is generated: after a sync, run `index`; a conflicted copy of it can be deleted.
- Run `check` after a sync: it flags files that look like a conflicted copy of a note that is still there.

## Maintain

`check` reports missing `title`/`summary`, broken links, duplicate titles, a stale index and **possible sync conflict copies**. For a conflict copy, show the user both files, merge what differs by hand into the original and delete the copy only when they say so (a copy of the generated `INDEX.md` is the exception: delete it and run `index`). Fix what is mechanical (index, links); for merging or deleting notes, show the user what you would change and wait. Never delete a note without being asked.
