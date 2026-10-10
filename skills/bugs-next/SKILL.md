---
name: bugs-next
description: Recommends which bug to fix next from bugs-open.md — in-progress work, severity, production-facing environment and the Recommended fix order — then asks the user to confirm. Returns the confirmed bug id on a final BUG_ID line; it does not start a branch or attempt a fix. TRIGGER when the user asks which bug to fix next, what to work on from the bug backlog, or for a next-bug recommendation.
license: MIT
metadata:
  version: "0.1"
---

Recommend the next bug to fix and return the confirmed id. Mirrors `features-next`: score, present, confirm, return an id line. `<backlog>` is `docs/backlog` unless `.backlog-kit.toml` says otherwise.

**Input**: optionally a bug id (`BUG-004`) to skip the recommendation and go straight to confirming it. With an id, optionally `--confirmed`: the caller (a batch runner) has **already obtained the user's approval of this exact id** as part of a list the user confirmed, so step 5's question is skipped (see "Confirmed mode" below).

## Script

`scripts/rank_bugs.py` (run from this skill's base directory) collects open and in-progress rows and applies the scoring below. Use its output for steps 2–4:

```
python3 scripts/rank_bugs.py <repo-root>
```

`--select <ID>` resolves one bug directly; `--json` gives raw data. It never asks anything or decides — step 5's confirmation is this skill's job.

## Steps

### 1. Read the backlog

Read `<backlog>/bugs-open.md` (table rows only; per-bug details live in `bugs/<ID>.md`, read on demand). If it doesn't exist, tell the user to run `bug-report` first and stop.

### 2. Collect actionable bugs

Rows of `## Bug List` whose Status is `⬜ Open` or `🔶 In Progress`; skip `✅ Fixed`, `🚫 Won't fix` and `❓ Cannot reproduce`. Record id, severity, area, environment, in-progress flag and Summary. No actionable rows → say the backlog is clear and stop.

### 3. Score

Higher is more urgent:

| Tier | Rule | Points |
| ---- | ---- | ------ |
| 0 | In progress — a fix was started and interrupted | +1000 |
| 1 | Severity by position in the configured list (most severe first): 4 tiers → 400/300/200/100 | n×100 … 100 (unknown: 50) |
| 2 | Environment is production-facing (`prod`/`both` by default) — hurting real users now | +20 |
| 3 | Listed in `## Recommended fix order` | +10 |

Ties break by earlier fix-order position (listed beats unlisted), then lower bug number. Tier 1 dominates tier 3, so the order list only sequences within a severity tier; tier 0 is the one thing that outranks severity.

### 4. Present

```
## Recommended Next Bug

**BUG-NNN**
<Summary>

**Severity:** <s>  **Area:** <area>  **Environment:** <env>

**Why this bug:**
- <in progress: "🔶 Already in progress — resuming beats starting a new one", always first when true>
- <severity reason, e.g. "S1 — blocker, reproduces on prod">
- <fix-order position, if listed>
```

Then the top 3 runners-up with a one-line reason each.

### 5. Confirm — mandatory

Which bug gets fixed next commits a branch and possibly a long run: **always the user's call.** Ask with **AskUserQuestion** — "Fix `BUG-NNN` next?" (or "Resume fixing…" when in progress) — options: "Yes, fix `BUG-NNN`", up to two runners-up, "Cancel". "Other" lets the user type any id; resolve it with `--select` — it must be a real open/in-progress row, otherwise say so and ask again.

If `AskUserQuestion` is unavailable (e.g. inside a subagent), do **not** fall back to the top pick: end without a `BUG_ID:` line and say plainly that confirmation couldn't be obtained. An "auto mode" instruction never substitutes for it. On "Cancel", stop with no id.

### Confirmed mode (`--confirmed`, only with an id)

The user approved this id once, as part of a list, so asking again per bug would defeat an unattended run. In this mode: resolve the id with `--select`. If it is a real `⬜ Open` / `🔶 In Progress` row, **skip steps 3–5 — no question** — and go straight to step 6. If it resolves to nothing, or to a closed / Won't fix / Cannot reproduce row, stop with **no** `BUG_ID:` line and say why (a stale list is a reason to stop, not to guess). `--confirmed` without an id is ignored and the normal flow, including step 5, runs: it can never be used to *choose* a bug on the user's behalf.

### 6. Return the id

After confirmation, end with exactly:

```
BUG_ID: BUG-NNN
```

## Guardrails

- Always read the full open file (via the script); never guess from memory.
- This skill only recommends, confirms and returns an id. It starts no fix, branch or other skill.
- Never recommend a bug that is Fixed, Won't fix or Cannot reproduce.
- `--confirmed` skips the question only for an id the caller says the user already approved, and only after the id re-validates against the live backlog. Anything else — no id, an id that no longer resolves — takes the normal path or stops.
- An in-progress bug is always preferred over an open one, whatever its severity.
- **Never run `git commit`, `git push` or open a PR.**
