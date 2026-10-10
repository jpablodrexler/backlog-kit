# Phase — Review and fix

_Shared by `bug-fix` and `feature-development`. Read this file in full before starting the phase._

Work in `<repo-root>`. Runs inside the implement subagent, after the change is complete, so that review findings are fixed by the same agent that holds the context. Reviews come from `[[reviews]]` in `.backlog-kit.toml`; with none configured, one built-in general `code` review applies.

**What to review is always the current diff, recomputed fresh.** Run `python3 <scripts>/work_scope.py <repo-root>` right before *every* review step — it lists changed files (untracked included, which `git diff` misses) and says which reviews apply to them. A fix round changes the tree, so a cached list goes stale. Never review the whole codebase and never use a branch-to-branch diff (nothing is committed, so it shows zero).

For each review where `applies` is true, in config order:

1. **Run it.**
   - If the entry names a `skill`, invoke that skill via the Skill tool in its non-interactive review mode, passing the `changed_files` list from `work_scope.py` verbatim (never describe the scope in prose), and let it write its own report. A review skill is asked for a review of exactly those files: no full-codebase sweep and no interactive fix workflow; you do the fixing in step 2.
   - Otherwise spawn a **fresh reviewer** subagent that sees only the changed files (the verbatim list) and the review's `focus`, and writes `<reports_dir>/review/<name>-<id>-<YYYY-MM-DD>.md`. Each finding is a checkbox line `- [ ] 🔴|🟡|🔵 <file>:<line> — <what is wrong and why it matters>` — 🔴 Critical (correctness, data loss, security), 🟡 Warning (likely bug, missing test, risky), 🔵 Suggestion (style, nit). A reviewer should look for things that are actually wrong, not restate the diff. Where the implement subagent cannot spawn a subagent of its own, it reviews its own diff instead — after re-reading every changed file cold — and says so: the report starts with `Self-reviewed: yes`, and the `REVIEWS:` hand-back line marks it `(self-reviewed)` so the orchestrator can tell the user. Never present a self-review as an independent one.
2. **Fix.** No 🔴/🟡 findings → this review is clean. Otherwise fix each in source, tick it (`- [x]`, with a `**Fixed:** <how>` note), recompute the scope, and run the review again to confirm nothing new appeared. 🔵 Suggestions are optional; apply the plainly correct ones cheaply and list the rest in the report.
3. **Cap.** After `review_max_rounds` rounds (from `work_scope.py`; default 3) without a clean result, end with `REVIEW_BLOCKED — repeated review cycles on <name>`. A finding that cannot be fixed without a human decision → `REVIEW_BLOCKED — <reason>`.

When any later fix touches files a finished review covered, recompute the scope and re-run just the reviews whose `when` now matches. Do not report a review as clean until it is clean on the final tree.

## Re-review of specific files

The orchestrator uses this when a later phase changed files no review covered (for example `PROD_CODE_FIXED` changes made to get a gate green). Spawn a **fresh reviewer** subagent (foreground) whose prompt names exactly those files, the applicable reviews' `focus` text (from `python3 <scripts>/work_scope.py <repo-root> --files <those files>`), and the finding format above; it writes the usual report, you apply steps 2 and 3 to its findings (fixing in the orchestrator's own context or in a new subagent), and the gates phase then runs again over the final tree.

Review reports are working files left uncommitted like everything else; the human decides whether they belong in the PR.
