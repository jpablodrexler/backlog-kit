# Feature Development — Phase 2 — Implement & Review

_Part of the `feature-development` skill — see `../SKILL.md` for the overview, Phase 0, placeholder substitution, final summary and the cross-phase guardrails. Read this file in full before starting this phase._

## Phase 2 — Implement & Review (Subagent 2)

Spawn a **general-purpose subagent** via the Agent tool, with
`run_in_background: false` (the first project phase cannot start until this subagent
returns `IMPLEMENT: DONE` — see the foreground guardrail in `../SKILL.md`), with the
following prompt:

> Perform these steps in sequence:
>
> **Step 1 — Implement**
> Use the Skill tool to invoke `openspec-apply-change <change-name>`.
> Work through all pending tasks until implementation is complete.
> Do not stop until all tasks show `[x]` or you encounter a blocker that
> requires user guidance.
> When `openspec-apply-change` completes, do NOT invoke `code-reviewer`
> proactively — it is handled explicitly in Step 2.
> If you encounter a blocker during implementation, end your response with
> `IMPLEMENT_BLOCKED — <brief reason>` and stop.
>
> **Never materialize a generated secret's raw value anywhere in this
> response, a report file, a tasks.md checkbox note, or any implementation
> file.** If a task requires generating a credential (a private key, API
> token, password, signing key, or similar), you may generate it and
> use it only to complete the narrowly-required local action — e.g. writing
> its *public* half to a committed file, when the scheme has one. Do not
> write, log, or echo the secret half anywhere this session's transcript,
> a report, or a repo file would capture it. Treat actually supplying that
> value to a secrets store (a secrets-manager command, a Vault insert, an env
> var) as an out-of-band action only the user performs, in their own
> terminal, outside this workflow — never something you run with the value
> passed as a visible argument. Leave that task's checkbox unchecked with a
> note naming the required manual command (never the value) — e.g. "Store
> the private key as a deployment secret (`<secrets tool> set
> PRIVATE_KEY=...`) — run manually by the user, value never
> committed." Do this even under this workflow's general "keep going
> until done or blocked" instruction — a task that can only be finished by
> exposing a secret's raw value is, by definition, blocked. This applies
> equally to any skill invoked from within this step (e.g. `decision-record`
> writing an ADR that describes the credential) — a description of *which*
> secret and *how* it's stored is fine; the value itself is never fine.
>
> **Determining "the files changed by `<change-name>`" — recompute fresh immediately before every single use, never cache one snapshot**
> Run `git status --porcelain` and parse every line's file path —
> including untracked (`??`) entries, not just modified/staged ones — into
> a concrete list; call it `CHANGED_FILES`. Do not use
> `git diff --name-only HEAD` for this, alone or as an alternative: it only
> reports changes to already-tracked files, so it silently misses any
> brand-new file — and a brand-new migration or configuration file is exactly the case
> a later review most needs to catch. Never substitute a branch-to-branch
> diff like `git diff main..HEAD` either: per this skill's "No git commits
> at any point" guardrail nothing gets committed during this workflow, so
> the branch's committed history stays identical to its base branch
> throughout — a branch-to-branch diff would always show zero files.
>
> **Do not compute this once and reuse it across Steps 2–4.** The working
> tree keeps changing throughout Phase 2 — Step 2's fix-and-re-review loop
> (up to 3 rounds) modifies or creates files, and a fix can easily be
> exactly the kind of file a *later* review's trigger check needs to see
> (e.g. a Step 2 fix that adds a new migration must be visible to a project
> phase's database-review trigger). A `CHANGED_FILES` snapshot taken once
> before Step 2 and reused afterward would silently miss all of that. Instead, re-run `git status --porcelain` and recompute
> `CHANGED_FILES` fresh immediately before **every** point below marked
> "(recompute `CHANGED_FILES`)", and pass that freshly computed list as an
> explicit argument each time. Never just describe scope in prose as "the
> files changed by `<change-name>`" and let the invoked skill re-derive it
> itself.
>
> **Step 2 — Code review**
> (recompute `CHANGED_FILES`) Invoke `code-reviewer` via the Skill tool
> using its **Review** workflow, passing the freshly recomputed
> `CHANGED_FILES` as the explicit scope (this subagent runs unattended — do
> not invoke the skill's interactive Fix Workflow, which is designed for a
> human to steer turn-by-turn across a conversation). This is a scoped
> review of one change, not a full-codebase sweep — do not request or
> expect multiple reports or additional subagents here. Every invocation
> writes a single dated `<reports>/code-review/CODE_REVIEW_FINDINGS_*.md` report. After the review completes, examine the findings:
>
> - If the report contains **no 🔴 Critical or 🟡 Warning findings**: proceed.
> - If the report contains any 🔴 Critical or 🟡 Warning findings: fix every
>   one of them in the source files. As you fix each finding, check it off in
>   that report file (`- [ ]` → `- [x]`) with a `**Fixed:** <one-sentence
summary of what changed>` note appended to the same line. Then (recompute
>   `CHANGED_FILES` — the fixes just applied changed the working tree)
>   re-invoke `code-reviewer`, passing the freshly recomputed list, to
>   confirm no new findings were introduced; this writes a fresh report for
>   the re-check. Repeat until the re-check report is clean.
>   If after 3 rounds of fix-and-re-review findings are still present, end
>   your response with `REVIEW_BLOCKED — repeated review cycles` and stop.
> - If you encounter a finding you cannot fix without human input: end your
>   response with `REVIEW_BLOCKED — <brief reason>` and stop.
>
> Do not proceed to Step 3 until all Critical and Warning code-review
> findings are resolved.
>
> **Step 3 — Signal completion**
> End your response with exactly this line:
> `IMPLEMENT: DONE`

Do not start this phase until Phase 1 subagent has confirmed artifacts are
ready. Do not start the first project phase until this subagent returns `IMPLEMENT: DONE`.

---
