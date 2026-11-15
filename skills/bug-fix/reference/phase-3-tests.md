# Bug Fix — Phase 3 — Tests

_Part of the `bug-fix` skill — see `../SKILL.md` for the overview, Phase 0, placeholder substitution, final summary and the cross-phase guardrails. Read this file in full before starting this phase._

## Phase 3 — Tests (run by the orchestrator, optional)

**With `--defer-tests`** (a batch where the user asked for the tests at the end): run nothing. Record `TESTS: DEFERRED — to the last bug of the batch, by the user's decision` and go to Phase 4. This defers only running the whole suite: the bug's regression test was already written and run in Phases 1 and 2. The last bug of the batch is called without the flag, so it runs this phase in full, below.

**On a shared batch branch the suite also covers the earlier bugs.** When a failure is in a spec, or in code, that an earlier bug's commits touched (`git log --oneline <integration>..HEAD -- <path>`), say which bug it comes from, fix it as this phase's fix (test code before production code), and name that bug in the fix and in its commit message. It is the price of having deferred the tests.

Skip this phase when the project has no automated tests: find out yourself
(orchestrator) from its `CLAUDE.md`, `README` and build manifest which command
runs them — and a faster end-to-end smoke tier, if CI runs one. If you cannot
tell, ask the user once (**AskUserQuestion**, with "skip this phase" as an
option); if there are no tests, record `TESTS: SKIPPED — no automated tests`
and go to Phase 4.

Runs unconditionally otherwise, regardless of what the fix touched — a tier CI
gates every PR on can still be broken by a fix that looks unrelated.

**The orchestrator runs this phase itself, not a subagent.** A suite can take long enough to hang or crash on memory, and a subagent that reports "waiting on my own background work" has reported nothing. Read `reference/long-runs.md` in full before starting (progress monitor, chunks with a timeout and a log file, stopping a whole process tree, rerunning a crashed chunk file by file, memory). In short, for `<bug-id>`:

1. Start the progress monitor, then run `<TEST_COMMAND>` in chunks, one at a time. On failure, diagnose (type error, missing stub, assertion mismatch, …) and fix, preferring test code over production source; if you must touch production source, note it `PROD_CODE_FIXED: <file> — <reason>`. You may spawn a **bounded** subagent to fix one named failing test; it never runs the suite.
2. **Smoke tier (if any):** run `<SMOKE_COMMAND>` the same way. Most failures here are a stale assertion in the spec itself (a hardcoded string or fixture that no longer matches what the component renders), not a real regression: check the rendered output before changing any production file, with the same `PROD_CODE_FIXED:` rule.
3. Record how the run was split, any chunk that timed out or crashed and how it was rerun, and anything not run, for the Final Summary.

End with exactly one of:
- `TESTS: PASS (<n> tests, <m> smoke tests)`
- `TESTS: PARTIAL — <what was not run>, by the user's decision`: only when the user chose to skip part of a suite or a tier. What ran passed; the Final Summary names what was not run.
- `TESTS: BLOCKED — <reason, noting which tier>`

On `BLOCKED`, stop and surface the failure. On one or more
`PROD_CODE_FIXED:` lines, surface them to the user (those production
changes weren't covered by the Phase 2R review gate) and ask: **Proceed** (record
`UNREVIEWED_PROD_FIXES:` for the Final Summary) or **Re-run the review gate** (Phase 2R over the fixes, then Phase 3 again).
