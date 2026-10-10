---
name: gitflow
description: The branch-and-publish half of the backlog workflow, run only when the user asks for it — start a feature or fix branch, sync it with the base branch, commit the finished work, push it and open the pull request, and clean up branches after the PR has merged. It is the one backlog-kit skill that writes to git (commit, push, PR, branch delete), and it shows exactly what it is about to do and gets a yes before every such write. It never merges a PR, force-pushes, rewrites history or touches the base branch. TRIGGER only when the user explicitly asks to start, sync, commit, or finish a feature or fix branch, to open the PR, or to clean up merged branches ("finish the feature", "commit this", "open the PR", "clean up the branches", "start the fix branch"). Never run it proactively, and no other skill invokes it.
license: MIT
metadata:
  version: "0.1"
---

The loop backlog-kit supports is: plan a feature → select it → branch → develop and verify → **commit → PR** → review → merge → **clean up** → select the next one. The work skills (`feature-development`, `bug-fix`, the batch runners) cover the middle and deliberately leave their result uncommitted. This skill covers the ends of the loop, and only when the user asks.

`<base>` is `[git] base_branch` from `.backlog-kit.toml` (detected from `origin/HEAD` when empty). Topic branches use `[git] feature_prefix` (default `feature/`) and `fix_prefix` (default `fix/`). Run scripts from this skill's base directory, passing the repository root.

**Input**: the action — `start feature|fix <name>`, `sync`, `commit`, `finish`, `cleanup` — inferred from the request. If it is ambiguous, ask once. `finish`, `commit` and `sync` work on the current topic branch unless one is named.

**Every git write here needs a yes.** Before each commit, push, PR creation and branch deletion, show exactly what will happen (the commit message and files, the PR title and body, the branch list) and ask with **AskUserQuestion**. That holds under "auto mode" and similar instructions, and in a subagent without `AskUserQuestion`: stop and say so. A yes covers that one write, not the next one.

## GitHub access

`finish` and `cleanup` talk to GitHub. Run `gh --version`; if it works, use the `gh` CLI. If not, use the GitHub MCP tools (`mcp__github__create_pull_request`, `mcp__github__list_pull_requests`, `mcp__github__pull_request_read`), deriving `owner`/`repo` from `git remote get-url origin`. If neither is available, or the remote is not GitHub, don't improvise REST calls: print the PR title and body ready to paste, plus the exact push command, and stop.

---

## start feature|fix `<name>`

`<branch>` is the prefix plus the name (a bare name gets the prefix; a full branch name is used as is). First run `python3 scripts/flow_plan.py <repo-root> --action start --branch <branch>`.

**If `needs_question` is true** — the checkout is already on a topic branch other than `<branch>`, possibly with work nobody has committed — don't pick for the user. Show the current branch, whether it is pushed, how many commits it has, and whether the tree is dirty, then ask with **AskUserQuestion**: continue on the current branch (nothing to do), rename it to `<branch>` (`git branch -m <branch>`, offered only if it was never pushed), or start `<branch>` fresh from `<base>` (the current branch stays as it is; needs a clean tree). Do exactly the one chosen.

Starting a fresh branch needs a clean working tree (backlog-kit's own files don't count). Run
`python3 scripts/branch_state.py <repo-root> --branch <branch> --fetch` and carry out its `action` exactly:

| `action` | do |
| -------- | -- |
| `resume` | nothing — already on it |
| `fast-forward` | `git merge --ff-only origin/<branch>` |
| `checkout` | `git switch <branch>` |
| `checkout-ff` | `git switch <branch>`, then `git merge --ff-only origin/<branch>` |
| `track-remote` | `git switch -c <branch> --track origin/<branch>` |
| `create` | `git switch -c <branch> --no-track <start_point>` (`--no-track` so a plain `git push` can never aim at the base branch) |
| `blocked` | stop and report the `reason` |

Report the branch and where it started. Starting a branch does not mark a backlog row; the work skills do that.

## sync

On a topic branch with a clean tree. Run `python3 scripts/flow_plan.py <repo-root> --action sync --fetch`. Stop on any `blockers`. With `behind_base` of 0, say it is up to date. Otherwise ask, then `git merge origin/<base>` (a merge, never a rebase). On conflicts, stop and list the conflicted files; resolving them is the user's call. Do not push.

## commit

On a topic branch (never on `<base>`) with changes. Run `python3 scripts/flow_plan.py <repo-root> --action commit` and stop on any `blockers`.

1. Show the changed files grouped as code and backlog/reports (`kind`), the `diff_stat` (it includes new, untracked files), and `backlog_closed` (what this change finishes). **Files flagged `suspicious` are never staged** unless the user says yes to that specific file.
2. Draft the commit message: a subject of at most 72 characters in the imperative, then a short body of the substantive changes (what changed and why, not a file list). Name backlog items as `feature 3` or `BUG-007`, never `#3`: GitHub turns `#<digits>` into a link to an unrelated issue.
3. Ask: "Commit these N files with this message?" — yes / edit the message / change the file list / cancel.
4. Stage by explicit path (`git add -- <paths>`, never `-A` or `.`), then `git commit -m "<message>" -- <the same paths>` so the commit contains exactly those files. If `staged` lists files that are not in the confirmed set, say so and leave them out; never commit a bare index. Never `--no-verify`. If a hook fails, show its output and stop; a fix gets a new commit, not an amend, and only if asked.

One commit by default; if the user asks for one commit per feature or per concern, split the staged paths accordingly and confirm each.

## finish

On a topic branch with a clean tree and at least one commit ahead of `<base>`. Run `python3 scripts/flow_plan.py <repo-root> --action finish --fetch` and stop on any `blockers`; show the `warnings` (a base that moved on suggests `sync` first).

1. If a PR for this head branch already exists, report its URL and stop; don't open a duplicate.
2. If the branch is not on the remote (or is ahead of it), ask, then `git push -u origin <branch>` (a plain `git push` afterwards). Never `--force`.
3. Write the PR description from the real diff, not from the branch name: read `commits`, `diff_stat`, `backlog_closed` and the files in `reports` (review reports, batch reports). Structure it as **Summary** (2–4 bullets: behaviour changed and why; name the backlog items finished), **Changes** (grouped by area when the diff spans several), and **Test plan** (only what the reports and commits actually show: gates run, tests, known failures and `NOT RUN` gates stated plainly; omit the section rather than invent one). Same `#<digits>` rule as above, and also when copying from earlier commit messages: a commit that says `feature #3` goes into the PR body as `feature 3`. The title is `title` from the plan (`Feature <name>` or `Fix <name>`).
4. Show the title and body and ask "Open this PR into `<base>`?" — yes / edit / cancel.
5. Open it with `base: <base>`, `head: <branch>`, and report the URL.

This opens the PR and nothing more. Review and merging are the human's. Say what comes next: once it is merged, `cleanup`, then `features-next` or `bugs-next` for the next item.

## cleanup

Run `python3 scripts/flow_plan.py <repo-root> --action cleanup --fetch`. `candidates` are topic branches other than the current one and the protected branches (`protected_branches`: `<base>`, `main`, `master`, `develop`, `trunk`), which are never deleted, whatever anyone asks.

- `merged_into_base: true` means the branch has diverged and everything on it, including the `origin/<branch>` copy, is now in `<base>`. `remote_has_unmerged_commits: true` means the remote copy has a commit the base lacks: never offer to delete it, even if the local copy looks merged. A shallow-clone warning means these answers cannot be trusted until `git fetch --unshallow`.
- `just_started: true` means the branch sits on the base tip: it has not diverged, so nothing says it is finished (someone may have just created it). Never list it as merged; offer it only if the user names it.
- Otherwise the branch may have been squash-merged: check through GitHub (`gh pr list --state merged --head <branch> --base <base> --json number,mergedAt,headRefOid`, or the MCP equivalent with `head: "<owner>:<branch>"` and `state: "closed"`, counting only PRs with a `merged_at`). It counts as merged only if the PR's head commit equals the branch tip (`git rev-parse <branch>`); a branch that got commits after its PR merged holds unmerged work. No merged PR, or a tip that differs, means **unmerged work, never deleted**; list it as kept.
- A branch that exists only on the remote is somebody's work until shown otherwise: show `last_author` and require a separate yes naming it.

Show the branches that will go (local and/or remote, with the evidence) and ask. Delete each local one with `git branch -d <branch>` only; `-d` refuses when the branch is not merged, and then the branch stays (never `-D`). Delete a remote one with `git push origin --delete <branch>` only after a separate yes. Finally, if you are on a deleted branch or want the base current: `git switch <base>` then `git merge --ff-only origin/<base>` (clean tree only).

---

## Guardrails

- **Only run a git write the user asked for in this invocation and confirmed.** No other backlog-kit skill commits, pushes or opens PRs, and none invokes this one; it never runs from another skill's hand-off, only when the user asks.
- Never merge a PR (no `gh pr merge`, no merge tool), never `--force` / `--force-with-lease`, never amend, rebase, reset, stash or cherry-pick, never commit or push to `<base>`, never delete a branch with unmerged work, never delete `<base>`, a protected branch or the current branch, never `git branch -D`, never `--no-verify`.
- `sync` and `cleanup` need a clean working tree, and so does starting a fresh branch: if it is dirty, stop and report; never stash or discard.
- A request to merge or pull a branch into a topic branch is `sync`: it merges `origin/<base>` and nothing else. Never merge any other branch (for example `main` when `<base>` is `develop`) into a topic branch, even when the two look identical at that moment: the next release can fork them apart before the branch is finished and carry content that never went through `<base>`.
- Never change git configuration (name, email, signing). Commit with whatever identity the repository already has.
- Don't assert a repo-state claim from memory ("merged", "up to date", "diverged"): run the check (`flow_plan.py`, `git log A..B`, the PR lookup) in the moment.
- The plan script is read-only; everything written to git is written by you, after a yes.
