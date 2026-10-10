---
name: spec-compliance-check
description: Proves, scenario by scenario, that what was built satisfies its spec — or, without OpenSpec, the acceptance criteria stated in the feature's brief. Checks the task list is complete, reads each matching test's body, runs it, classifies every scenario as Verified, Unverified or Failing from that evidence (never from reading the code alone), flags requirement prose that contradicts its own scenarios, and writes a dated report with the exact commands and results. Read-only apart from the report; it never fixes anything or commits. TRIGGER when asked to verify a change against its spec, check spec compliance, or confirm a feature meets its acceptance criteria before archiving; feature-development runs the same procedure in its close phase.
license: MIT
metadata:
  version: "0.1"
---

Verify one change against its spec and write the evidence down. `<backlog>` and the other paths come from `.backlog-kit.toml`; with no file the defaults apply.

**Input**: a change name (the `Change name` of a backlog row, which is also the OpenSpec change name), optionally the mode. With `[spec] workflow = "openspec"` the mode is `openspec`; otherwise `brief`. If no name is given and exactly one backlog row is `🔶 In Progress`, use it; otherwise ask.

Follow `reference/spec-compliance.md` with `<scripts>` = this skill's `scripts/` folder. It does the whole job: tasks gate, checklist, find-read-run the evidence, classify, prose check, report, hand-back line.

Then show the user the result and what is left to close:

```
## Spec Compliance — <change-name>

<COMPLIANCE line>
Report: <path>

Failing: <scenarios with the failing evidence>
Unverified: <scenarios and why>
Prose conflicts: <requirement titles>
```

Offer the next step in words only: Failing scenarios belong back in implementation; Unverified ones need a test written (then re-run this check); a prose conflict needs the requirement reworded in the change's delta spec if the change is intentional. This skill does none of those itself.

---

## Guardrails

- **Never run `git commit`, `git push` or open a PR.** This skill reads files, runs the project's tests and writes one report under `<reports_dir>/spec-compliance/`; nothing else.
- Don't edit code, tests, specs or the backlog, and never tick a task in `tasks.md`.
- Never classify a scenario Verified without having run its test and recorded the command and output, and never from reading the implementation alone.
- Never install system packages or change anything outside the repository to get a test to run; an unrunnable test makes its scenario Unverified, with the reason.
- Report counts computed from the table, not from memory.
