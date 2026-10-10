# Phases 3–5 — Project phases

_Part of the `feature-development` and `bug-fix` skills — see `../SKILL.md` for the overview, Phase 0, placeholder substitution, final summary and the cross-phase guardrails. Read this file in full before starting this phase._

## Phases 3–5 — Project phases (one subagent per file)

What a project verifies after the implementation — component and E2E tests, a build, a database or security review that only applies when certain files changed, a viewport check — differs from one project to the next, so it is not written in this skill. It lives in the project, as one markdown file per phase in `.backlog-kit/feature/` (for `feature-development`) or `.backlog-kit/bug/` (for `bug-fix`), named `NN-name.md` (e.g. `03-tests.md`, `04-e2e.md`, `05-build.md`). This phase runs them **in filename order**, each one fully (orchestrator step, subagent, hand-back) before the next starts.

**If the folder does not exist or holds no `*.md` file:** tell the user `No project phases found in .backlog-kit/<feature|bug>/ — tests, reviews beyond the code review, and the build are not run`, and go straight to Phase 6. This is a warning, not a blocker.

### File format

A phase file has a first-level heading (its title, used in the Final Summary) and up to two sections:

- `## Orchestrator` *(optional)* — steps the **orchestrator itself** runs in its own context before spawning the subagent: reading the changed files to decide whether the phase applies, or any decision that needs `AskUserQuestion` (e.g. which credential source to use). Never delegate an `AskUserQuestion` to the subagent. If the orchestrator step concludes the phase does not apply, it records `PHASE: SKIPPED — <reason>` and moves to the next file without spawning anything. Anything it decides is passed to the subagent by substituting it into the `## Subagent` text.
- `## Subagent` — the prompt for a **general-purpose subagent** (spawned via the Agent tool with `run_in_background: false`). It may use the placeholders `<CHANGED_FILES>` and — for `feature-development` — `<change-name>`, or — for `bug-fix` — `<bug-id>`, `<slug>`, `<repro-details>` and `<repro-test-path>`; see below.

### Running one file

1. Read the file in full. Recompute `CHANGED_FILES` (see below) and run its `## Orchestrator` section, if any.
2. Substitute the skill's placeholders and the freshly computed `CHANGED_FILES` list into the `## Subagent` text, plus anything the orchestrator step decided, and spawn the subagent.
3. The subagent must end its response with exactly one line:
   - `PHASE: PASS` — the phase's checks passed; optionally followed on the next line by `SUMMARY: <one line for the Final Summary>` and, if part of what the phase covers could not be checked, `PARTIAL: <what wasn't covered>`.
   - `PHASE: SKIPPED — <reason>` — the phase did not apply.
   - `PHASE: BLOCKED — <reason>` — it could not complete.
   It may also report `PROD_CODE_FIXED: <file> — <what and why>` lines for production code it changed while chasing a failing test.
4. Handle the result as the guardrails in `../SKILL.md` say: continue on `PASS`/`SKIPPED`, surface `BLOCKED` and `PROD_CODE_FIXED:` to the user and wait, and treat a missing signal as `BLOCKED`. Record the phase's title and its `SUMMARY`/`PARTIAL` text for the Final Summary.

### `CHANGED_FILES`

A phase that triggers on, or reviews, "the files this change touched" must use the same definition as Phase 2: run `git status --porcelain` and parse every path, including untracked (`??`) entries, recomputed fresh immediately before each use — never `git diff --name-only HEAD`, never a branch-to-branch diff (nothing is committed during this workflow, so it shows zero files). A review a project phase runs follows the same rules as Phase 2's Step 2: the skill's **Review** workflow, scoped to `CHANGED_FILES`, never its interactive Fix Workflow, findings fixed and checked off in the report, at most 3 rounds before `PHASE: BLOCKED`, and a final `code-reviewer` pass over fixes it applied.

Do not start a project phase until the previous one reports `PASS` or `SKIPPED`, and do not start Phase 6 until the last one has. In `bug-fix`, the regression test at `<repro-test-path>` must keep passing throughout.

---
