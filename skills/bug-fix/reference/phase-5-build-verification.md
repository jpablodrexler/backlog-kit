# Bug Fix — Phase 5 — Build Verification

_Part of the `bug-fix` skill — see `../SKILL.md` for the overview, Phase 0, placeholder substitution, final summary and the cross-phase guardrails. Read this file in full before starting this phase._

## Phase 5 — Build Verification (run by the orchestrator, optional)

Skip this phase — recording `BUILD: SKIPPED — no build step` — when the project
has no build, compile or type-check step (find out yourself from its
`CLAUDE.md`, `README` and build manifest; if unsure, ask once with "skip" as an
option). This skill never deploys anything; the build runs locally only so a
failure is caught before CI or the host would.

**The orchestrator runs the build itself, not a subagent** (see `reference/long-runs.md`: a hung build must be seen and stopped by the one who can). Substitute the command for `<BUILD_COMMAND>`:

1. Run `<BUILD_COMMAND>` from the repo root with a hard timeout of 5 minutes (extend once only if the log shows it is still making progress), writing its output to a log file, never piped through a filter that prints only at the end.
2. **On failure**, read the error (it names the file and cause), fix the affected files, prioritising the ones related to the change, and re-run until it succeeds or you reach a blocker that needs human input. If you must modify a production source file (not a test or a build configuration file), note it `PROD_CODE_FIXED: <file> — <reason>`.
3. If the build produces an output directory or artifact, confirm it exists and is not empty: empty or missing after a "successful" build is itself a failure.

End with `BUILD: PASS` (after any `PROD_CODE_FIXED:` lines) or `BUILD: BLOCKED — <reason>`.

Do not start Phase 6 until `BUILD: PASS` (or the phase was skipped). On one or
more `PROD_CODE_FIXED:` lines, handle them as Phase 3's: ask the user to
**proceed** (record `UNREVIEWED_PROD_FIXES:` for the Final Summary) or to
**re-run the review gate** (Phase 2R over the fixes, then Phases 3 and 5 again).
