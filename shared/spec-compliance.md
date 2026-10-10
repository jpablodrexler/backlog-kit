# Procedure — spec / acceptance compliance

_Shared by `feature-development` (its close phase) and the `spec-compliance-check` skill. Read this file in full before starting._

Goal: prove, scenario by scenario, that what was built does what the spec (or, without OpenSpec, the brief) says — with evidence you produced by running things, not by reading code and nodding. This procedure only reads, runs tests and writes its report; fixing gaps is the caller's job.

Inputs: `<change-name>`, `<repo-root>`, `<scripts>` (the calling skill's `scripts/` folder), and the mode:

- **openspec** (`spec.workflow = "openspec"`): requirements and scenarios come from `<changes-dir>/<change-name>/specs/**/spec.md`; the task list from `<changes-dir>/<change-name>/tasks.md`.
- **brief** (no OpenSpec): acceptance statements come from the feature's brief (the `Brief` file): every sentence that states an expected behaviour, output, error or limit. If the brief states none, hand back `COMPLIANCE: NO_ACCEPTANCE_CRITERIA` and stop; do not invent criteria.

## 1. Tasks gate (openspec mode)

Read `tasks.md`. Any task still unchecked (`- [ ]`) means the work is not finished: list them and hand back `TASKS_INCOMPLETE — <n> unchecked: <task titles>`, then stop. Don't tick tasks yourself to get past this.

## 2. Build the checklist

One row per scenario (openspec) or per acceptance statement (brief), carrying its requirement title. Keep the spec's own wording; never paraphrase a WHEN/THEN into something easier to satisfy.

## 3. Find, read and run the evidence

For each row:

1. **Find the test(s)** that should exercise it (search test files by the scenario's inputs, outputs and names). Task text and test names are not evidence.
2. **Read the test body.** Does it set up the scenario's WHEN and assert the scenario's THEN, exactly — the same inputs, the same output, the same exit status or error? A test that merely runs the code path, or asserts something weaker, does not count.
3. **Run it.** Use the narrowest command that executes that test with the project's own runner, from the directory of the gate that covers it (`python3 <scripts>/work_scope.py <repo-root>` lists the configured gates and their `cwd`). Record the exact command and the outcome (passed / failed, the counts line). If you cannot determine how to run it, the row is Unverified with that reason; don't guess a runner and don't install anything.

## 4. Classify each row

- **Verified** — a test whose body asserts exactly the scenario ran and passed, and you recorded the command and output.
- **Failing** — the test that pins the scenario ran and failed, or running the program shows it contradicts the scenario.
- **Unverified** — no test covers it, the test asserts something weaker, it could not be run, or the only support is that the code looks right. **Never infer verification from reading the implementation alone.**

## 5. Check the requirement prose

Read each requirement's `SHALL` statement (and its title) next to its own scenarios and the proposal's `What Changes` / `Impact`. A **prose conflict** is a requirement that claims the behaviour is "unchanged", "exactly as before" or "no visible change" while its scenarios or the proposal declare a user-visible change. Report each one with both quotes. (Scenarios can all be Verified and the requirement text still be false.)

## 6. Write the report

Write `<reports_dir>/spec-compliance/SPEC_COMPLIANCE_<change-name>_<YYYY-MM-DD>.md` (add `-2`, `-3` on the same day; never overwrite an earlier report):

```markdown
# Spec compliance — <change-name> (<date>)

Mode: openspec | brief   Result: <verified>/<total> verified, <n> unverified, <n> failing, <n> prose conflict(s)

## Tasks
<n>/<n> complete (openspec mode) — list anything unchecked.

## Scenarios
| Requirement | Scenario | Status | Evidence |
| --- | --- | --- | --- |
| <title> | <scenario> | Verified | `<test path>:<line>` — `<command>` — 12 passed |

## Prose conflicts
- <requirement title>: "<claim>" vs "<scenario or proposal text>"
```

## 7. Hand back

End with exactly one line: `COMPLIANCE: <verified>/<total> verified, <u> unverified, <f> failing, <p> prose conflict(s) — report <path>` (or `TASKS_INCOMPLETE …` / `COMPLIANCE: NO_ACCEPTANCE_CRITERIA`). Never report a count you did not compute from the table.
