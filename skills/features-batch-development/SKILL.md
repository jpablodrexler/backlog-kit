---
name: features-batch-development
description: Runs feature-development unattended across an ordered list of named features — or the whole pending backlog — one feature at a time on a single shared branch, with zero git commits. Built for long unattended stretches over several small features, checking in only when a blocker needs a human decision. Writes a dated report updated after each feature completes (not batched at the end), so progress survives a cutoff, crash or power outage, and can resume an interrupted run. TRIGGER when asked to batch-develop or unattended-develop a list of named features or the whole backlog ("develop features 13, 16 and 19 while I'm away", "develop the whole planned backlog unattended").
license: MIT
metadata:
  version: "0.1"
---

Run `feature-development` in a loop over a list of features, all on one shared branch, never committing, writing progress to a resumable report as each feature finishes. The loop, the report and the guardrails are shared with the bug runner and live in `reference/batch-runner.md` — **read it in full before starting**, along with `reference/pipeline-guardrails.md`. This file supplies the feature-specific parts.

`<backlog>` is `docs/backlog` unless `.backlog-kit.toml` says otherwise.

**Input**: either (a) an ordered list of features, by `#` number or change name from `<backlog>/features-planned.md` — "13, 16, 19" or "task-postpone, expense-charts" — or (b) a request for **the whole planned backlog** ("everything that's pending"). Optionally a branch name to use or resume; with none, one is proposed and confirmed.

## Parameters for `reference/batch-runner.md`

| | |
| --- | --- |
| `<kind>` / `<work-skill>` | `features` / `feature-development` |
| `<id>` | the change name (the plan also shows the `#` number) |
| `<done>` | `completed` |
| `<branch-prefix>` | `[git] feature_prefix` (default `feature/`) — default branch `feature/batch-<YYYY-MM-DD>` |
| whole-backlog set | every row of `features-planned.md` — that file only ever holds not-yet-implemented rows, so no filtering is needed |
| whole-backlog order | the same ranking `features-next` uses: features already `🔶 In Progress` first, then priority tier, with a hard prerequisite always before its dependents; the `### Recommended implementation order` breaks ties within a tier, then table order. A stale order list never reorders a higher tier; `batch_plan.py` warns when it disagrees. |

Each feature's full brief lives in `<backlog>/features/NNN-<change-name>.md`. The runner does not read it: `feature-development` reads it itself in its plan phase.

## Outcome mapping (loop step 3)

After `feature-development <change-name> --skip-branch-setup --confirmed` returns:

| What `feature-development` did | Report status |
| ------------------------------ | ------------- |
| Showed its "Feature Development Complete" summary — the feature was archived and marked implemented | `completed`, with a ≤2-sentence summary of what was built. Read the implemented row `features-archive` just wrote and the work's own summary. |
| Refused at selection — `features-next --confirmed` returned no `CHANGE_NAME:` line because the feature is **blocked by a prerequisite that hasn't shipped**, is already implemented, or no longer exists | `blocked`, with the reason and the prerequisite named; ask Retry now / Skip and continue / Stop (loop step 4). The approval of the list never overrides an unbuilt prerequisite. |
| Stopped on `PLAN_NEEDS_DEPENDENCY_DECISION` and the user chose "stop" | `blocked` with the dependency named; ask whether to continue with the next feature or stop the run |
| Stopped on any other `*_BLOCKED` reason | ask Retry now / Skip and continue / Stop (loop step 4) → `blocked` with the reason |

A feature that depends on one *later* in the list, or on one that isn't in the run at all, is flagged by the `warnings` from `batch_plan.py` in step 1 — show them, because `features-next` will refuse to select a feature whose prerequisite hasn't shipped, and the run would stall on it.

## Final report

When the run ends, show the counts from `batch_report.py finish` plus, for each feature, its status and summary. Then say plainly: **nothing was committed**; every completed feature's code, tests and review reports sit uncommitted on the shared branch — review with `git status` / `git diff`, then commit and open the PR yourself (or, if `[git] finish_skill` is set in `.backlog-kit.toml`, say the branch can be handed to that skill; never invoke it yourself).

## Guardrails (feature-specific; the rest are in `reference/batch-runner.md`)

- **Never run `git commit`, `git push` or open a PR.** The branch step's `git switch` / `git switch -c` / `git merge --ff-only` are the only git writes, and every `feature-development` call passes `--skip-branch-setup`.
- Invoke `feature-development <name> --skip-branch-setup --confirmed` through the Skill tool directly — never in a backgrounded Agent call. The list you confirmed in step 1 *is* the per-feature approval; `feature-development` still raises the dependency decision, the gate setup, a partial-gates result and blocker prompts, and each must reach the user live.
- Process features strictly one at a time, in the resolved order. Later features' reviews will see earlier features' uncommitted files; that is expected.
- A feature already implemented is only offered "skip" or "stop", never silently dropped.
- With `spec.workflow = "openspec"`, each feature's spec change is archived as that feature completes — OpenSpec is a dependency, never bundled.
