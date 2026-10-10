---
name: code-reviewer
description: Reviews a code change against the project's own documented architecture, conventions and known pitfalls, and reports findings by severity (Critical, Warning, Suggestion) with file:line evidence in a dated checkbox report. Has a non-interactive review mode for the backlog-kit review phase (a file list in, one report and one hand-back line out), plus interactive modes for reviewing a PR, branch or path on request and for working through an existing findings report. Reads and reports; edits source only in the interactive fix workflow, never commits. TRIGGER after implementing a feature, fix or refactor, when asked to review a PR, file or change, when a `[[reviews]]` entry names `skill = "code-reviewer"`, or when asked to fix findings from an existing code review report.
license: MIT
metadata:
  version: "0.1"
---

Review a *change* against what the project itself says is right, and write down only what is actually wrong, with evidence. Paths come from `.backlog-kit.toml` (`[paths] reports_dir`, default `docs/reports`); with no file the defaults apply.

This skill reviews a change. For the health of a whole system's shape (layering, shared state, data-access patterns) or a numeric metrics sweep, use a different, purpose-built review; do not stretch this one into that.

## Pick the mode first

| Mode | How it starts | Interactive? |
| --- | --- | --- |
| **Non-interactive review** | The backlog-kit review phase (or any caller) passes `changed_files` (with an `id` and optional `focus`) | **No.** Never asks a question, never edits source |
| **Standalone review** | A person asks to review a PR, branch, file or feature | Yes |
| **Fix workflow** | A person asks to fix / address / work through findings of an existing report | Yes |

If the caller gave a file list, it is the non-interactive mode, whatever else the request says (a missing `id` becomes `adhoc`). The other two modes are never entered from the review phase.

---

## Non-interactive review mode

Used by `[[reviews]] skill = "code-reviewer"` in `.backlog-kit.toml`. The orchestrator fixes findings itself; this mode only reviews and reports. A project wires it like this:

```toml
[[reviews]]
name  = "code"
focus = "correctness, regressions, missing or weak tests, unintended changes"
skill = "code-reviewer"
when  = ["**"]
```

**Input**
- `changed_files`: the files to review, taken verbatim. These are the entire scope.
- `deleted_files` (optional): the subset of `changed_files` that no longer exists. Review what the deletion removes (`git show HEAD:<file>`); do not route it to "Not reviewed".
- `bulk_files` (optional): the subset that is a lockfile, generated, minified or binary file. Do not read these in full; check only what the change implies (a manifest changed with no lockfile change, an unexpected new dependency in a lockfile hunk).
- `id`: the bug id or change name, used in the report filename. Default `adhoc` when absent.
- `focus` (optional): extra text from the review's `focus`; give it extra weight, it does not narrow the scope.
- `self_review` (optional): `yes` when the caller runs you inside its own context, which is always so from the review phase. The report then starts with `Self-reviewed: yes`.
- Review the change, not the files: see the changed lines with `git diff HEAD -- <file>` (an untracked file is new in full). A defect on a line the change did not touch is not a finding; mention it, if at all, in a plain (non-checkbox) "Pre-existing, not counted" bullet in the header.
- A finding cites `<file>[:<line>]`; leave out the line when it has none (a missing test, a lockfile not updated).

**Rules**
1. Review exactly the listed files. No full-codebase sweep, no widening to "related" files except to read a caller, callee, interface or test that is needed to judge a listed file (read it, do not report on it unless the listed change broke it).
2. Never ask the user anything. If something cannot be judged (a file is unreadable, a convention is unclear), say so in a report line under "Not reviewed" and continue.
3. Do not edit source, tests or docs. Do not run the fix workflow.
4. Follow "The review method" below, then write the report and hand back one line.

**Report**: `<reports_dir>/review/code-<id>-<YYYY-MM-DD>.md`. Create the directory if needed; if the file exists, append `-2`, `-3` and so on rather than overwrite. Start with a header (scope = the file list, `focus`, and `Self-reviewed: yes` when `self_review` is `yes`), then one checkbox line per finding, no other format:

```
- [ ] 🔴 src/orders/total.py:42 — <what is wrong and why it matters>
- [ ] 🟡 src/orders/total.py — <a finding with no line, such as a missing test>
- [ ] 🟡 src/orders/total.py:77 — <what is wrong and why it matters>
- [ ] 🔵 src/orders/total.py:90 — <what is wrong and why it matters>
```

Severity:

| Level | Meaning |
| --- | --- |
| 🔴 Critical | Breaks correctness or data integrity, loses data, or is a security or access-control gap. Must be fixed before merging |
| 🟡 Warning | A likely bug, a missing test for changed behaviour, a risky pattern, or a violation of a documented project standard that will cause maintenance problems |
| 🔵 Suggestion | Style, naming, a nit or a minor improvement. Fix if convenient |

Group by severity, then by file. Omit empty groups. With no findings, write the header and `No findings.`

**Hand-back**: as the last thing you say, exactly one line, counts computed from the report's checkbox lines:

```
REVIEW: <n> critical, <n> warning, <n> suggestion — report <path>
```

---

## The review method (all modes)

1. **Read every file in scope in full** before forming an opinion (bulk files excepted). For a diff, read the whole file around each hunk, not the hunk alone, but report only what the change introduced or made worse.
2. **Load the project's own conventions**, and judge against those, not against rules of your own: `CLAUDE.md`, `CONTRIBUTING.md`, `docs/architecture*`, `docs/decisions/` or other decision records, lint and formatter configuration, the test conventions document, and existing code near the change (how its neighbours name, layer, handle errors and write tests). A convention you cannot point to in one of those places is at most a 🔵 Suggestion.
3. **Work through the checklist** below for what the change touches. Skip headings that do not apply; do not pad.
4. **Scan the known-pitfalls list** the project documents (a "pitfalls", "gotchas" or "lessons learned" section, past bug reports and their regression tests, review reports from earlier runs). Finish every review with this pass.
5. **Run the project's own checks if they are cheap and read-only** and the lint or analysis commands are documented (complexity, type or lint report, coverage threshold). A check qualifies only if it reports and writes nothing tracked: never an auto-fix, formatter-in-place or snapshot-update flag, and not in the non-interactive mode if you cannot tell. Quote the command and the offending location in the finding. Never install anything to do it; if a tool is missing, note it under "Not reviewed".
6. **Write the report** and, in an interactive mode, summarise it.

### Checklist (apply what the change touches)

- **Correctness**: logic errors, off-by-one, wrong condition, unhandled null/empty/error result, an error or failure value ignored before its data is used, state not reset, race or ordering assumptions, resource not released or left open.
- **Data integrity and security**: unvalidated input at a boundary, an access-control or ownership check missing or weakened, a secret or credential committed, sensitive data logged, a query that silently returns less than it should because an authorization rule hides rows (check the rule, not just the calling code), a migration or write that can lose data.
- **Layering and structure**: dependencies pointing the wrong way against the project's documented layers, business logic in an entry point or view that belongs in the layer the project reserves for it, a new second way of doing something the project already has one way to do (a second client or connection, a hand-written mapper where a generator is standard), a wrapper or adapter that only forwards to another and adds nothing of its own (judge by whether it contributes logic, not by whether it currently has callers; existing callers mean repoint them, not that the wrapper earns a reprieve).
- **Performance traps**: a query or remote call issued once per element of a collection in a loop where a batched call exists; an unbounded result for data that grows, where the project paginates.
- **Naming and style**: against the project's naming table and lint config only; anything that the formatter or linter already enforces is not worth a finding.
- **Tests**: changed or new behaviour without a test; a test that runs the code but asserts nothing meaningful about the result; a test written in a style the project's test conventions forbid; stale test names or references left after a rename; a test that cannot fail. Use the project's own test stack and matchers, not another one's.
- **Comments and dead weight**: comments that restate the code (only *why* comments are wanted), long comment blocks on internal code where the project prefers terse ones, an unused export, import or file introduced by the change, leftover debug output.
- **User-facing text and layout** (when the project has such conventions): hard-coded strings where the project localises, raw values where it formats, layout rules documented for a minimum device or viewport.
- **Dependencies**: a new or bumped dependency checked against the project's licence and vulnerability policy, if it has one.

### Evidence and scope discipline

- Every finding names a real `file:line` in scope and says what is wrong and why it matters. Findings are things that are actually wrong, not a restatement of the diff or a summary of what the change does.
- A finding you cannot support from the code you read, a documented convention, or the output of a command you ran is not a finding. Do not report "might be" without saying what you checked.
- No praise sections, no padding, no duplicates of the same root cause across many lines (one finding, list the other locations in it).
- Do not carry forward unresolved items from an earlier dated report; write only what this run found.
- Schema or migration files, and security-focused or architecture-wide audits, belong to the project's own specialised reviews if it configures them; mention in "Not reviewed" that they were out of scope rather than half-reviewing them.

---

## Standalone review mode (interactive)

Use when a person asks to review a PR, branch, file or feature.

1. **Scope.** A named path, a PR number, a branch (diff against its base), or a feature. For a PR or branch, get the file list from the project's hosting tool or read-only version-control commands; confirm the scope in one line if it is ambiguous.
2. Follow "The review method" for one scoped pass, producing one report.
3. Show the in-chat summary:

```
## Review: <file, branch or PR title>

### 🔴 Critical
- `path/to/file:42` — <issue>

### 🟡 Warnings
- `path/to/file:15` — <issue>

### 🔵 Suggestions
- `path/to/file:88` — <issue>

### Verdict
<One or two sentences: overall quality, whether it is safe to merge, and the single most important thing to fix first.>
```

Omit empty severity groups.
4. Write the full report to `<reports_dir>/code-review/CODE_REVIEW_FINDINGS_<YYYY-MM-DD>.md` (`-2`, `-3` if the date exists; never overwrite or delete an earlier report) using the checkbox format above, with a header naming the scope and the state reviewed (branch or commit if known). Do this on every run.

### Large sweeps, one layer at a time

If asked to review a whole codebase or a whole sub-project rather than a change, do not produce one consolidated report and do not review inline. Split it by the project's architectural layers or top-level areas (derive them from its architecture document), one subagent per layer, each told to read this skill, review only its own directory scope, and write its own report `CODE_REVIEW_FINDINGS_<YYYY-MM-DD>_<layer>.md`, returning only counts and the path. Before dispatching, skip layers that already have a report dated today. Dispatch the remaining layers together, in one message. Finish with a short summary of reports written and counts per layer. If you cannot spawn subagents, say so and propose the layer list instead of reviewing everything inline.

---

## Fix workflow (interactive)

Details and the exact steps are in `reference/report-and-fix.md`. Summary: locate the report (or reports) for a date, work on exactly one at a time, ask which severity or finding to fix, then for each finding read the code, fix it, stop and ask if the fix hinges on a real design decision, run the narrowest relevant tests, update tests for the new shape of the code, and tick the report line immediately with a `**Fixed:**` or `**Evaluated, no change made:**` note. Run the widest available verification once a scope is done. It edits source and the report only.

---

## Guardrails

- **Never run `git commit`, `git push` or open a PR.** This skill reviews, writes reports under `<reports_dir>`, and in the fix workflow only, edits source; every change stays uncommitted for the person to review.
- In the non-interactive mode never ask a question and never edit source, tests, docs or the backlog.
- Never review beyond the given scope in the non-interactive mode, and never replace the given file list with a description or a recomputed one.
- Never invent a rule the project does not state; a personal preference is a 🔵 Suggestion at most.
- Never install system packages or change anything outside the repository to run a check; a check that cannot run is reported as not run.
- Never read a hand-maintained credentials file; never print a secret you find, cite its location only.
- Report counts are computed from the report's checkbox lines, not from memory, and the hand-back line is exactly the format above.
- Never overwrite or delete an earlier dated report; each run is a point-in-time snapshot.
