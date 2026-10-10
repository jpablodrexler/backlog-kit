---
name: bugs-batch-fix
description: Runs bug-fix unattended across an ordered list of bug ids — or the whole open backlog — one bug at a time on a single shared fix branch, with zero git commits. Built for long unattended stretches, checking in only when a bug genuinely needs a human decision. Writes a dated, incrementally updated report so progress survives a cutoff or crash, and can resume an interrupted run. TRIGGER when asked to batch-fix bugs, work through the bug backlog unattended, or fix a list of named bugs in one run ("fix BUG-004, BUG-007 and BUG-009 while I'm out"), or when several fresh bugs are handed over to fix in one session — file each with bug-report first, then run this skill.
license: MIT
metadata:
  version: "0.1"
---

Run `bug-fix` in a loop over a list of bugs, all on one shared fix branch, never committing, writing progress to a resumable report as each bug closes. The loop, the report and the guardrails are shared with the feature runner and live in `reference/batch-runner.md` — **read it in full before starting**, along with `reference/pipeline-guardrails.md`. This file supplies the bug-specific parts.

`<backlog>` is `docs/backlog` unless `.backlog-kit.toml` says otherwise.

**Input**: either (a) an ordered list of bug ids — "BUG-004, BUG-007, BUG-009" (`4` and `bug-4` are accepted) — or (b) a request for **the whole open backlog** ("fix every open bug"). Optionally a branch name to use or resume; with none, one is proposed and confirmed.

## Parameters for `reference/batch-runner.md`

| | |
| --- | --- |
| `<kind>` / `<work-skill>` | `bugs` / `bug-fix` |
| `<id>` | the bug id; each bug's write-up is `<backlog>/bugs/<id>.md` (the work skill reads it) |
| `<done>` | `closed` |
| `<branch-prefix>` | `[git] fix_prefix` (default `fix/`) — default branch `fix/bug-batch-<YYYY-MM-DD>` |
| whole-backlog set | rows of `bugs-open.md` whose Status is `⬜ Open` or `🔶 In Progress` |
| whole-backlog order | the same ranking `bugs-next` uses: bugs already `🔶 In Progress` first, then severity (most severe first); the `## Recommended fix order` breaks ties within a severity, then bug number. A stale fix-order list never reorders a higher severity; `batch_plan.py` warns when it disagrees. |

## Outcome mapping (loop step 3)

After `bug-fix <id> --skip-branch-setup --confirmed` returns:

| What `bug-fix` did | Report status |
| ------------------ | ------------- |
| Showed its "Bug Fix Complete" summary — the bug was closed through `bugs-archive` | `closed`, with a ≤2-sentence summary: the root cause and what the fix changed. Read the row `bugs-archive` just wrote to `bugs-fixed.md` and the Resolution line it appended to `bugs/<id>.md`. |
| Couldn't reproduce it and the user chose "mark it Cannot reproduce" | `cannot-reproduce` with a short note |
| Couldn't reproduce it and the user chose "keep it open" | `left-open` — the report entry reads "Left open", and the row stays `🔶 In Progress` for the user to add repro detail |
| Refused at selection — `bugs-next --confirmed` returned no `BUG_ID:` line because the bug is no longer open (closed, Won't fix, Cannot reproduce) or no longer exists | `blocked`, with the reason; ask Retry now / Skip and continue / Stop (loop step 4) |
| Stopped on a `*_BLOCKED` reason | ask Retry now / Skip and continue / Stop (loop step 4) → `blocked` with the reason |

## Final report

When the run ends, show the counts from `batch_report.py finish` plus, for each bug, its status and summary. Then say plainly: **nothing was committed**; every closed bug's fix and regression test sits uncommitted on the shared branch — review with `git status` / `git diff`, then ask for `gitflow` (the skill named by `[git] finish_skill`, default `gitflow`; empty means do it by hand): its `commit` and `finish` actions commit the work and open the PR after asking; say so by name and never invoke it yourself.

## Guardrails (bug-specific; the rest are in `reference/batch-runner.md`)

- **Never run `git commit`, `git push` or open a PR.** The branch step's `git switch` / `git switch -c` / `git merge --ff-only` are the only git writes, and every `bug-fix` call passes `--skip-branch-setup`.
- Invoke `bug-fix <id> --skip-branch-setup --confirmed` through the Skill tool directly — never in a backgrounded Agent call. The list you confirmed in step 1 *is* the per-bug approval; `bug-fix` still raises the cannot-reproduce decision, the gate setup, a partial-gates result and blocker prompts, and each must reach the user live.
- Process bugs strictly one at a time, in order. A later bug's regression test and reviews will see earlier bugs' uncommitted files; that is expected.
- A bug closed earlier in the same run is never re-run; a `🚫 Won't fix` / `❓ Cannot reproduce` bug is only offered "skip" or "stop", never silently dropped.
