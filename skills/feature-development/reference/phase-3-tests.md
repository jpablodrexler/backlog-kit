# Feature Development — Phase 3 — Tests

_Part of the `feature-development` skill — see `../SKILL.md` for the overview, Phase 0, placeholder substitution, final summary and the cross-phase guardrails. Read this file in full before starting this phase._

## Phase 3 — Tests (run by the orchestrator, optional)

**This phase is optional: skip it when the project has no automated tests.**
Before spawning anything, find out yourself (orchestrator, not a subagent)
what the project has: read its `CLAUDE.md`, `README` and build manifest
(`package.json` scripts, `Makefile`, `pyproject.toml`, `pom.xml`,
`Cargo.toml`, …) for the command that runs its tests — and for a faster
end-to-end "smoke" tier, if CI runs one. If a test command exists but you
cannot tell what it is, ask the user once (**AskUserQuestion**, in your own
context; offer "skip this phase" as an option). If the project has no tests,
record `TESTS: SKIPPED — no automated tests` for the Final Summary and go to
Phase 4.

This phase runs the project's local test suites — the ones that actually
determine whether the PR's CI goes green. A tier CI runs on every PR
unconditionally must be run here unconditionally too: do not skip it based on
`<change-name>`'s scope, the way Phase 4 skips based on touched areas — a
change that looks entirely unrelated (a shared component's translation
string, a relocated file) can still break a test that asserts against it.

**The orchestrator runs this phase itself, not a subagent.** A test suite can take long enough to hang or to crash on memory, and a subagent that starts it and then reports "waiting on my own background work" has reported nothing. Read `reference/long-runs.md` in full before starting: it covers the progress monitor, chunking with a timeout and a log file, stopping a whole process tree, rerunning a crashed chunk file by file, and memory. In short:

1. Start the progress monitor, then run `<TEST_COMMAND>` in chunks, one at a time.
2. **If something fails:** read the failure output and find the root cause (a type error, a missing stub, an assertion mismatch), checking files related to `<change-name>` first. Fix the affected files, preferring test code over production source. If you must modify a production source file, note it as `PROD_CODE_FIXED: <filename> — <reason>`. To save your own context you may spawn a **bounded** subagent to fix one named failing test; it never runs the suite, and you re-run it yourself.
3. **Smoke tier (only if the project has one):** a distinct suite from step 1 (for example end-to-end specs against a dev server with the backend stubbed). Run `<SMOKE_COMMAND>` the same way, even if `<change-name>` looks unrelated to any spec in it. Most failures here are a stale assertion in the spec itself (a hardcoded fixture value or UI string that no longer matches what the component renders), not a regression: check the rendered output before changing any production file, and apply the same `PROD_CODE_FIXED:` rule.
4. Record how the run was split, any chunk that timed out or crashed and how it was rerun, and anything not run, for the Final Summary.

End the phase with exactly one of these lines:

- `TESTS: PASS (<n> tests, <m> smoke tests)`: both tiers pass (omit the smoke count if there is no smoke tier).
- `TESTS: PARTIAL — <what was not run>, by the user's decision`: only when the user chose to skip part of a suite or a tier (ask with **AskUserQuestion** when the run is taking too long or the machine cannot finish it). What did run passed. The Final Summary names what was not run; it is never reported as a plain pass.
- `TESTS: BLOCKED — <brief reason, noting which tier>`: a failure you cannot resolve without human input.

If the phase ends `BLOCKED`, stop the workflow and surface the
failure details to the user before continuing. Do not proceed to Phase 4
until it ends `PASS` or `PARTIAL` (or the phase was skipped).

If any `PROD_CODE_FIXED:` line was recorded,
surface them to the user with a note that those production source changes
were not covered by the Phase 2R review gate. Ask the user whether to:

- **Proceed** — continue to Phase 4 without additional review. If chosen,
  record this (e.g. `UNREVIEWED_PROD_FIXES: <the PROD_CODE_FIXED lines>`) —
  the Final Summary in `../SKILL.md` must surface it.
- **Re-run the review gate** — run the Phase 2R review gate (`reference/review-gate.md`) again over
  the production fixes, then re-run Phase 3 to confirm all tests still pass before continuing to Phase 4.
  If this path is taken, there is nothing left to caveat in the Final
  Summary.

---
