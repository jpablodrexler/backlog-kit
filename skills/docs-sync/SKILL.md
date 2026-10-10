---
name: docs-sync
description: Keeps a project's documentation (README, the lean agent-facing file such as CLAUDE.md or AGENTS.md, and reference docs under docs/) in sync with the code, after a change or as a full audit. Driven by an optional `[[docs.map]]` in .backlog-kit.toml; works without one. TRIGGER after implementing a feature or fix that changes commands, file layout, configuration keys, public interfaces or setup steps; when a close phase runs the configured `[docs] sync_skill`; or when asked to check, audit or sync the docs against the code.
license: MIT
metadata:
  version: "0.1"
---

Make the documentation say what the code does, **never the other way round**. Documentation drifts silently because nothing re-derives it; this skill re-derives only the facts a change could have invalidated, checks them against the docs, and fixes the docs.

**Input**: optional mode and scope. Default is **change mode**. The user may ask for a **sweep** ("audit the docs", "check for drift"), or name a doc file or section to scope either mode.

---

## How docs are tiered

Most projects keep documentation in up to three tiers; find out which exist before editing.

- **Agent-facing file** (`CLAUDE.md`, `AGENTS.md` or similar): a lean quick-start for someone working in the code. Commands, repo layout, a few short rules, and **pointers** into the reference docs. It never carries a full table, a route or endpoint list, a configuration reference, a long runbook or a per-feature narrative. If one of those has grown back here, move it to `docs/` and leave a one-line pointer; that move is itself a finding.
- **Reference docs** (`docs/**`): the comprehensive, current-state detail. This is where facts live, once each.
- **README**: a short intro plus an index of the reference docs. It stays an index and does not regrow the content that lives in `docs/`.

One source of truth per fact: the detail goes in one reference doc, and every other file points to it instead of copying it.

---

## The documentation map

### With a map: `[[docs.map]]` in `<repo-root>/.backlog-kit.toml`

Read the file directly (plain read, no script). Each `[[docs.map]]` table links one documented section to the code that is its source of truth:

```toml
[[docs.map]]
doc     = "docs/api.md"            # required: the documentation file, relative to the repo root
section = "Endpoints"              # optional: a heading inside it; omit to cover the whole file
source  = ["src/routes/**"]        # required: globs of the code that section documents
check   = "every route has an entry with its method, path and auth requirement"   # required: what "in sync" means
```

- `doc` and `source` are required, `check` is required, `section` is optional. `source` is a list of globs relative to the repo root (`**` crosses folders; a glob may name a single file such as `package.json`).
- Several entries may share one `doc` (one per section) and several docs may share a source.
- A map entry that lacks a required key, or whose `doc` file does not exist, is reported as a map problem, not silently skipped. A `source` glob that matches nothing is also reported (the code may have moved).
- `check` is the acceptance statement for that section. Verify it literally, item by item, against the code.

### Without a map

The skill still works. Discover the documentation set: `README.md`, the agent-facing file (`CLAUDE.md` / `AGENTS.md`), and every Markdown file under `docs/`, skipping the backlog folder, the decisions folder, the reports folder (`[paths] reports_dir`, default `docs/reports`) and any other generated or append-only history; those belong to other skills. Then check only these fact classes against the code:

1. **Commands** the docs tell people to run (build, test, lint, run, deploy): does each still exist in the project's manifest or scripts, with the same name and flags?
2. **File and folder layout** the docs describe: do the named paths exist, and does a new top-level folder appear nowhere in the docs?
3. **Configuration keys and environment variables**: are the ones the docs list still read by the code, with the same defaults, and is any new one undocumented?
4. **Public interfaces**: routes, endpoints, exported functions, CLI flags, events or message topics that the docs enumerate.
5. **Setup and prerequisite steps**: versions, required tools, install order.
6. **The documentation index itself**: every reference doc exists, and each index line still describes its file.

**When no map exists, propose one; do not write it.** After the run, offer a draft `[[docs.map]]` for the user's project built from what you found (one entry per reference section that clearly tracks a code area), in a fenced block the user can paste into `.backlog-kit.toml`. Say plainly that you have not written it. Tracked mappings make future runs faster and sharper, but the file is the user's to change.

---

## Mode 1: change mode (default)

This is the mode the close phase of `feature-development` and `bug-fix` uses when `[docs] sync_skill = "docs-sync"`.

1. **Find what changed, read-only.** Run `git status` and `git diff` (add `--stat` first for a big change; `git diff <base>...HEAD --stat` when the work is already on a branch and the base is known). Include untracked files from `git status`. These are the only git commands this skill runs, and only to read.
2. **Pick the sections at stake.**
   - With a map: keep the entries whose `source` globs match a changed file.
   - Without: classify each changed file into the fact classes above (a changed manifest or script means commands; a new or moved file means layout; a changed config reader means configuration; a changed public surface means interfaces; and so on).
   - Skip everything else. Do not re-verify untouched sections in change mode.
3. **Compare doc and code side by side.** Read the current doc text and the changed code, and decide what is missing, stale or wrong. Read the code itself; never infer a default, a route's auth rule or a flag's meaning from a name.
4. **Edit the documentation only.** Make the smallest edit that makes the doc true, one section at a time, matching that file's existing style (heading level, table versus list, diagram conventions).
5. **Keep the tiers honest.**
   - New detail goes in the reference doc, not in the agent-facing file. If a fix would put detail in the agent-facing file, write it in `docs/` and point to it.
   - If a reference doc changed enough that its one-line description in the README or agent-facing file index is now wrong, update that index line too.
   - If you find misplaced detail already sitting in the agent-facing file, move it to `docs/` and leave a pointer.
6. **Report.** In chat, a short summary: sections checked, files updated, one line of reason per update, and anything you could not fix without a decision (see guardrails).
7. **End with exactly one hand-back line** as the last line of your reply:
   - `DOCS: <n> file(s) updated`, where `<n>` counts the documentation files you edited, or
   - `DOCS: nothing to sync` when every relevant fact was already true.

---

## Mode 2: sweep mode (on request)

Use when asked to audit, or when a long time has passed since the last check. It reports first and changes docs only after the user confirms.

1. Load the map (or, without one, discover the documentation set as above) and read every mapped doc and section in full.
2. For each map entry, re-derive the current state from the code independently, reading every file the `source` globs match rather than sampling a few. Without a map, do the same for each fact class. Do not trust the doc's existing text as a starting point.
3. Collect **every** discrepancy before editing anything. Classify each as: **Missing** (code has it, doc does not), **Stale** (doc describes something that changed), **Dead** (doc describes something that no longer exists), **Misplaced** (detail in the agent-facing file that belongs in `docs/`), **Index** (a pointer or description that no longer fits), or **Map problem** (see above).
4. Write the dated report to `<reports_dir>/docs-sync/DOCS_SYNC_<YYYY-MM-DD>.md` (`<reports_dir>` is `[paths] reports_dir`, default `docs/reports`; create the folder if needed; if a report for today exists, append a numbered suffix instead of overwriting). Contents: scope and mode, the map entries or fact classes audited, then a table of findings (id, doc and section, class, what the docs say, what the code does, proposed fix), then a count of sections that were already in sync. A report is a record of the audit, not a substitute for the fix.
5. Show the user the findings summary and **ask before fixing**. They may approve all, some, or none. Apply only the approved fixes, with the same editing rules as change mode.
6. Update the report with what was applied and what was declined, then end with the hand-back line `DOCS: <n> file(s) updated` (or `DOCS: nothing to sync` when the sweep found no drift, or none was approved).

---

## Guardrails

- **Never run `git commit`, `git push` or open a PR.** Syncing docs edits files only; the user commits.
- **Documentation files only.** Never edit source code, tests, configuration, the backlog, decision records, generated files or another skill's reports. Anything outside Markdown documentation is read, not changed. When the code looks wrong, say so in the summary; do not change it to match the docs. The only file this skill creates besides edits is the sweep report.
- **The code is the truth.** Never document behaviour you have not verified in the code, and never document intended or planned behaviour as if it exists (a roadmap is not documentation). Remove or correct text that claims something the code does not do.
- **Never delete a documentation section silently.** If a section describes something that no longer exists, you may remove it, but name the section and the reason in your summary. If you cannot tell whether something was removed or only moved, ask rather than delete.
- **Detail goes in `docs/`, pointers go in the agent-facing file.** Do not copy a table, list or narrative into a second place; link to it. Do not let the README or agent-facing file regrow what the reference docs hold.
- **One source of truth per fact.** When the same fact appears in several places, fix the canonical one and reduce the others to a pointer.
- **Stay scoped in change mode.** Do not rewrite sections the change cannot have affected, and do not restyle docs while syncing them.
- **Do not read secrets.** Skip credential, key and environment files that hold real values; example or template files are fine to read when a configuration key's existence is the question.
- **No scripts.** This skill ships none; inspect changes with plain read-only `git status` / `git diff` and read files directly.
- If an edit would need a product or wording decision you cannot derive from the code (for example two docs disagree and the code supports neither), leave it, list it in the summary, and do not count it in the hand-back number.
