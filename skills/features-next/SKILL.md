---
name: features-next
description: Recommends which feature to implement next from features-planned.md — priority, hard dependencies, in-progress work and the Recommended implementation order — then asks the user to confirm. Returns the confirmed change name on a final CHANGE_NAME line; it does not start any work. TRIGGER when the user asks which feature to build next, what to work on next, or for a next-feature recommendation.
license: MIT
metadata:
  version: "0.1"
---

Recommend the next feature and return the confirmed change name to the caller. `<backlog>` is `docs/backlog` unless `.backlog-kit.toml` says otherwise.

**Input**: optionally a feature number or name, to skip the recommendation and go straight to confirming that feature. With one, optionally `--confirmed`: the caller (a batch runner) has **already obtained the user's approval of this exact feature** as part of a list the user confirmed, so step 6's question is skipped (see "Confirmed mode" below).

## Script

`scripts/rank_features.py` (run from this skill's base directory) does the mechanical work of steps 2–4 — collecting pending and in-progress rows, resolving dependency blocking from each prerequisite's *live* Implementation status, and applying the scoring below. Use its output instead of re-deriving the ranking:

```
python3 scripts/rank_features.py <repo-root>
```

`--select <number-or-name>` resolves one feature directly (for the optional input or a free-text answer in step 6); `--json` gives raw data. The script never asks the user anything and never decides — the confirmation in step 6 is this skill's job.

## Steps

### 0. Offer an open exploration first (optional; only if the project uses one)

If `<explorations_dir>` (default `docs/explorations`) exists and holds markdown files, read each one's `**Status:**` line and `# ` title. An exploration is **open** unless its status contains `archived`, `superseded`, `proposed`, `done` or `dropped` (no status line counts as open). If none are open, skip this step silently.

Otherwise ask with **AskUserQuestion** — "There's an in-progress exploration. Recommend the next feature, or keep working on one of these?" — options: "Recommend the next feature" (default), then up to three open explorations by title (most recently modified first). If the tool is unavailable, skip this step; don't block on it. If the user picks an exploration, **stop**: emit no `CHANGE_NAME:` line, point them at that file and tell them to continue it with their exploration workflow (with `spec.workflow = "openspec"`, that's `/opsx:explore`).

### 1. Read the backlog

Read `<backlog>/features-planned.md`. If it doesn't exist, tell the user to run `feature-plan` first and stop.

### 2. Collect pending features

Every row of `## Feature List` whose Implementation shows `⬜ Pending` or `🔶 In Progress`, with its number, name, priority, effort, area, in-progress flag, Summary, and the brief file path from its `Brief` link (the brief — never the Summary — is what a later spec/implementation step receives). With `spec.workflow = "openspec"` also record whether its `SDD Artifacts` cell is `✅ Created`. Zero rows → say the backlog is empty and stop.

### 3. Determine which are unblocked

A feature is **blocked** if a hard dependency `**Feature A → Feature B**` (under `### Hard implementation dependencies`) names a prerequisite B that still has a row showing `⬜ Pending` **or** `🔶 In Progress` — a prerequisite being worked on hasn't shipped either. A B with no row in the planned table has been archived, so it no longer blocks. Always judge from B's live row, **never** from the dependency note's own "(still pending)" / "(resolved)" annotation, which can lag.

### 4. Score

Higher is better:

| Tier | Rule | Points |
| ---- | ---- | ------ |
| 0 | In progress — resuming beats starting | +1000 |
| 1 | Priority, by position in the configured list (first = highest): 4 tiers → 400/300/200/100 | n×100 … 100 (unknown/blank: 50) |
| 2 | Spec artifacts already created (`openspec` only) | +20 |
| 3 | Listed in `### Recommended implementation order` | +10 |
| 4 | Smallest configured effort tier (quick to deliver) | +5 |

Ties break by earlier position in the order list (listed beats unlisted), then lower feature number. Tier 1 dominates tier 3, so the order list only sequences *within* a priority tier; tier 0 is the one thing that outranks priority.

### 5. Present

```
## Recommended Next Feature

**#<number> `<name>`**
<Summary>
Full brief: <brief file>

**Priority:** <p>  **Effort:** <e>  **Area:** <a>

**Why this feature:**
- <in progress: "🔶 Already in progress — resuming beats starting something new", always first when true>
- <tier reason>
- <dependency status, e.g. "all prerequisites implemented">
- <order-list position, if listed>
```

Add `**Spec artifacts:** ✅ Created / ⬜ Not yet created` with `openspec`. Repeat any missing-brief warning the script emitted under the `Full brief:` line — the implementation step will stop on a missing brief, so say so now. Show the top 3 runners-up with a one-line reason each.

### 6. Confirm — mandatory

Which feature gets built commits hours of work and a branch, so it is **always the user's call**. Ask with **AskUserQuestion** (2–4 options per question): "Proceed with implementing `<name>`?" (or "Resume implementing `<name>`?" when in progress) with options "Yes, proceed with `<name>`", up to two runners-up, and "Cancel". The tool's built-in "Other" lets the user type any number or name — resolve it with `--select`: it must match a real pending row; if it matches nothing or an implemented feature, say so and ask again. Remind the user that the brief file (not the Summary) is what the next step receives, so edits belong there before confirming.

If `AskUserQuestion` is unavailable (for instance inside a subagent), do **not** fall back to the top pick: end without a `CHANGE_NAME:` line and state plainly that confirmation couldn't be obtained. An autonomous-operation or "auto mode" instruction never substitutes for this question.

On "Cancel", stop with no change name.

### Confirmed mode (`--confirmed`, only with a number or name)

The user approved this feature once, as part of a list, so asking again per feature would defeat an unattended run. In this mode: resolve it with `--select`. If it is a real pending / in-progress row **and not blocked**, skip steps 3–6 — no question — and go straight to step 7. If it resolves to nothing, is already implemented, or is **blocked by a prerequisite that hasn't shipped**, stop with **no** `CHANGE_NAME:` line and say why, naming the prerequisite: a feature whose dependency is unbuilt must never be built, whoever approved the list. `--confirmed` without a number or name is ignored and the normal flow, including step 6, runs: it can never be used to *choose* a feature on the user's behalf.

### 7. Return the name

After confirmation, end with exactly:

```
CHANGE_NAME: <change-name>
```

## Guardrails

- Always read the full planned file (via the script) before recommending; never guess from memory.
- This skill only recommends, confirms and returns a name. It starts no implementation, branch or other skill; the caller decides what's next.
- Never recommend a feature that is already implemented, or one blocked by a prerequisite that isn't implemented — not as the top pick, not as a runner-up, and not in `--confirmed` mode either.
- `--confirmed` skips the question only for a feature the caller says the user already approved, and only after it re-validates against the live backlog. Anything else — no identifier, one that no longer resolves, a blocked one — takes the normal path or stops.
- An in-progress feature is always preferred over a merely pending one, whatever its priority. With several in progress, tiers 1–4 pick among just those.
- If every pending feature is blocked, say which prerequisites must ship first and recommend those instead.
- **Never run `git commit`, `git push` or open a PR.**
