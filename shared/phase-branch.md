# Phase — Branch & mark in progress

_Shared by `bug-fix` and `feature-development`. Read this file in full before starting the phase._

Spawn a **general-purpose subagent** (foreground — every later phase is gated on this result) with the prompt below. Substitute `<id>` (the bug id or change name), `<branch>` (`<prefix><slug>`: `fix/…` for a bug, `feature/…` for a feature; prefixes come from `[git]` in `.backlog-kit.toml`), `<scripts>` (the absolute path of the calling skill's `scripts/` folder), `<repo-root>`, and `<backlog-row>` (the one-line instruction in the calling skill that says which backlog row to flip).

> Work in `<repo-root>` (cd there first). Set up the work branch for `<id>`. The target branch is `<branch>`. Do not create, edit or delete any file other than the backlog row in Step 3 until this phase is done.
>
> **Step 1 — Inspect (read-only).** Run
> `python3 <scripts>/branch_state.py <repo-root> --branch <branch> --fetch`
> and add `--batch` if the orchestrator told you batch mode is on. It prints JSON with one recommended `action`. It changes nothing.
>
> **Step 2 — Carry out the action** with plain git, exactly as listed and nothing more:
>
> | `action` | do |
> | -------- | -- |
> | `resume` | nothing — you're already on `<branch>`; uncommitted work here is the expected state of an interrupted run |
> | `fast-forward` | `git merge --ff-only origin/<branch>` |
> | `checkout` | `git switch <branch>` |
> | `checkout-ff` | `git switch <branch>`, then `git merge --ff-only origin/<branch>` |
> | `track-remote` | `git switch -c <branch> --track origin/<branch>` |
> | `create` | `git switch -c <branch> --no-track <start_point>` (`--no-track` so a plain `git push` can never aim at the base branch) |
> | `batch-ok` | nothing — the caller owns branch state; a dirty tree is expected |
> | `blocked` | end with `BRANCH_BLOCKED — <reason>` and stop |
>
> If a `--ff-only` merge refuses, end with `BRANCH_BLOCKED — <branch> cannot be fast-forwarded; reconcile it manually` and stop. **Never** run `git merge` without `--ff-only`, `git rebase`, `git pull`, `git commit`, `git push`, `git stash` or `git reset` — those either create commits or rewrite history, and this workflow never does either. Outside batch mode, confirm `git branch --show-current` now prints exactly `<branch>`; otherwise end with `BRANCH_BLOCKED — could not switch to <branch>`.
>
> If the JSON shows the base branch has commits `<branch>` lacks (`git rev-list --count HEAD..<start_point>` is above 0), mention it in your hand-back as information. Do **not** merge or rebase it in — that is the human's call when they review.
>
> **Step 3 — Mark it in progress.** `<backlog-row>` Only ever change `⬜` → `🔶 In Progress`; leave a row already `🔶 In Progress` or finished alone. If there is no matching row (work tracked outside the backlog), skip silently — that is not an error. This applies in batch mode too.
>
> **Step 4 — Hand back.** Your final reply must itself end with exactly `BRANCH: READY — <branch> (<action>)`, followed by any information note from Step 2. Put the signal in that reply's text, not in a separate hand-back or messaging tool, and never substitute a placeholder.

After the subagent returns:
- `BRANCH_BLOCKED …` → surface the reason and **stop**. Never retry automatically and never work around it by switching branches yourself.
- No `BRANCH: READY` line → treat as blocked (missing-signal rule) and surface the raw response.
- Otherwise continue. From here on, every later phase stays on whatever branch is checked out: none of them may switch, create, merge or rebase a branch.
