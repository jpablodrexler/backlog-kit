# Feature Development — Phase 5 — Build Verification

_Part of the `feature-development` skill — see `../SKILL.md` for the overview, Phase 0, placeholder substitution, final summary and the cross-phase guardrails. Read this file in full before starting this phase._

## Phase 5 — Build Verification (run by the orchestrator, optional)

**This phase is optional: skip it when the project has no build, compile or
type-check step.** Find out yourself (orchestrator) from the project's
`CLAUDE.md`, `README` and build manifest which command that is; if there is
none, record `BUILD: SKIPPED — no build step` and go to Phase 6S. If a build
command probably exists but you cannot tell which, ask the user once
(**AskUserQuestion**, with "skip this phase" as an option).

This skill never deploys anything. What this phase *does* do is run the exact
build command the project's host or CI runs, locally first, so a build failure
is caught before it ever reaches an actual deployment.

**The orchestrator runs the build itself, not a subagent** (see `reference/long-runs.md`: a hung build must be seen and stopped by the one who can). Substitute the command for `<BUILD_COMMAND>`:

1. Run `<BUILD_COMMAND>` from the repo root with a hard timeout of 5 minutes (extend once only if the log shows it is still making progress), writing its output to a log file, never piped through a filter that prints only at the end.
2. **On failure**, read the error (it names the file and cause), fix the affected files, prioritising the ones related to the change, and re-run until it succeeds or you reach a blocker that needs human input. If you must modify a production source file (not a test or a build configuration file), note it `PROD_CODE_FIXED: <file> — <reason>`.
3. If the build produces an output directory or artifact, confirm it exists and is not empty: empty or missing after a "successful" build is itself a failure.

End with `BUILD: PASS` (after any `PROD_CODE_FIXED:` lines) or `BUILD: BLOCKED — <reason>`.

Do not start Phase 6S until this subagent completes (or the phase was
skipped). If it reports `BUILD: BLOCKED`, surface the details to the user and
wait for guidance before continuing.

If the response contains `PROD_CODE_FIXED:` lines, handle them exactly like
Phase 3's (see `reference/phase-3-tests.md`): ask the user to **proceed**
(record `UNREVIEWED_PROD_FIXES`, which the Final Summary must surface) or to
**re-run the Phase 2R review gate** over the fixes and then re-run Phases 3
and 5.

---
