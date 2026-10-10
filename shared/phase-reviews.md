# Phase — Review and fix

_Shared by `bug-fix` and `feature-development`. Read this file in full before starting the phase._

Work in `<repo-root>`. Runs inside the implement subagent, after the change is complete, so that review findings are fixed by the same agent that holds the context. Reviews come from `[[reviews]]` in `.backlog-kit.toml`; with none configured, one built-in general `code` review applies.

**What to review is always the current diff, recomputed fresh.** Run `python3 <scripts>/work_scope.py <repo-root>` right before *every* review step — it lists changed files (untracked included, which `git diff` misses) and says which reviews apply to them. A fix round changes the tree, so a cached list goes stale. Never review the whole codebase and never use a branch-to-branch diff (nothing is committed, so it shows zero).

For each review where `applies` is true, in config order:

1. **Run it.**
   - If the entry names a `skill`, invoke that skill via the Skill tool in its non-interactive review mode, scoped to `changed_files`, and let it write its own report.
   - Otherwise spawn (or act as) a **fresh reviewer** that sees only the changed files and the review's `focus`, and writes `<reports_dir>/review/<name>-<id>-<YYYY-MM-DD>.md`. Each finding is a checkbox line `- [ ] 🔴|🟡|🔵 <file>:<line> — <what is wrong and why it matters>` — 🔴 Critical (correctness, data loss, security), 🟡 Warning (likely bug, missing test, risky), 🔵 Suggestion (style, nit). A reviewer should look for things that are actually wrong, not restate the diff.
2. **Fix.** No 🔴/🟡 findings → this review is clean. Otherwise fix each in source, tick it (`- [x]`, with a `**Fixed:** <how>` note), recompute the scope, and run the review again to confirm nothing new appeared. 🔵 Suggestions are optional; apply the plainly correct ones cheaply and list the rest in the report.
3. **Cap.** After `review_max_rounds` rounds (from `work_scope.py`; default 3) without a clean result, end with `REVIEW_BLOCKED — repeated review cycles on <name>`. A finding that cannot be fixed without a human decision → `REVIEW_BLOCKED — <reason>`.

When any later fix touches files a finished review covered, recompute the scope and re-run just the reviews whose `when` now matches. Do not report `REVIEW: PASS` until every applicable review is clean on the final tree.

Review reports are working files left uncommitted like everything else; the human decides whether they belong in the PR.
