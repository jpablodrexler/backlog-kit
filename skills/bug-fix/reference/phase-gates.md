<!-- VENDORED from shared/phase-gates.md — do not edit here; edit the source and run `python3 tools/vendor.py`. -->
# Phase — Verification gates

_Shared by `bug-fix` and `feature-development`. Read this file in full before starting the phase._

Gates are the project's own verification commands — tests, type-check, lint, build, an end-to-end suite — configured as `[[gates]]` in `.backlog-kit.toml` and run in order after the work and its reviews are done. They are the "evidence before done" step: a change is not finished because the code looks right.

## Orchestrator steps before spawning (needs the user, so never inside a subagent)

1. **Get the scope.** Run `python3 <scripts>/work_scope.py <repo-root>`. It lists only the files *you* changed (backlog-kit's own bookkeeping files are excluded) and which gates apply to them. If `gates_configured` is `false`, do the one-time setup:
   - Run `python3 <scripts>/detect_gates.py <repo-root>`. It proposes gates by sniffing the repo (package.json scripts, pytest, Maven/Gradle, dotnet, Go, Cargo, `make test`) up to three folders deep.
   - Show the proposal and say which proposed gates you expect **cannot run on this machine** (a Windows-only solution on Linux, a suite needing a service that isn't up). Ask with **AskUserQuestion**: "No verification gates are configured. Run these on every change?" — "Yes, and save them to `.backlog-kit.toml`", "Yes, but just this run", "No gates — skip verification" (then say plainly in the summary that nothing was verified), "Let me specify them" (take the commands from the reply). If nothing was detected, ask for the commands instead; never guess a command.
   - To save, add the confirmed `[[gates]]` blocks to `.backlog-kit.toml` (create it if needed). That is an edit to a config file, not a commit.
   - Saved gates only cover the folders they run in. Whenever `uncovered_files` is non-empty (checked again in the next step), the change touched code that **no gate verifies**.
2. **Note what no gate covers.** If `work_scope.py` lists `uncovered_files` (changed files outside every configured gate's `cwd` / `when`), a `GATES: PASS` only vouches for the rest. Carry the list into the final summary as `⚠ NOT VERIFIED BY ANY GATE: <count> files (<areas>)` — plainly, never folded into "passed" — and, when the user is present, offer once to add a gate for it. Documentation and backlog files appear here too; mention them only briefly.
3. **Ask about gated gates.** For every applicable gate with a non-empty `ask_before` (a gate that touches a live service, spends money, or is slow), ask its question with **AskUserQuestion** — "Run it" / "Skip it this run". A skipped gate is recorded as `NOT RUN` and shown in the final summary; it is never silently dropped.

Then spawn the subagent below (foreground), with `<gate-list>` = the applicable, not-skipped gates (name, `run`, `cwd`, `timeout_minutes`, and any `known_failures`).

> Validate the change for `<id>`. Work in `<repo-root>` (cd there first; every gate's `cwd` is relative to it). Run these gates in order, each from its `cwd` and within its timeout:
>
> `<gate-list>`
>
> For each gate: run it and read the result. **On failure, diagnose before touching anything.** Decide whether the failure is (a) a real defect in the change, (b) a stale or wrong test/fixture/assertion that no longer matches intended behaviour, or (c) the environment (a missing dependency, a port in use, no network, a tool that cannot work on this OS, a test that depends on the host's permissions).
>
> - **(a) and (b):** fix them and re-run the gate until it passes. A failing test is evidence, not an obstacle: never skip, delete, disable or weaken a test to get green, never mark one expected-to-fail, and **never "fix" a test that is unrelated to the change** — an unrelated failing test is not yours to repair.
> - **(c):** try the obvious remedy **once**, and **only a remedy that stays inside the repository** — installing the project's own dependencies with a command that does **not rewrite tracked files** (`npm ci`, not `npm install` — which rewrites the lockfile and sneaks churn into the diff; letting Maven resolve), freeing a port. If a remedy did modify a tracked file, say so in your hand-back and leave the file for the orchestrator to restore. **Never install system packages, never use `sudo`, `apt`, `brew` or any package manager outside the project, and never change global or user-level configuration.** If the remedy would need any of that, or it did not work, do **not** stop the run — record the gate and carry on with the next one:
>   - a gate that cannot run here → `NOT RUN (environment): <reason>`
>   - a gate that ran and whose failures are environmental and unrelated to the change → `FAILED (environment): <failing test names and the cause>`
> - **`known_failures`:** if a gate lists patterns and a failing test matches one, it is a failure the user already knows about. Don't touch it; report it as `KNOWN FAILURE: <test>` and treat the gate as passed *apart from those tests*. Any failure that does **not** match is new and is yours to diagnose as above.
>
> Prefer fixing test code over production source when the *test* is what's wrong. If you must change production source to get a gate green, note each such change as `PROD_CODE_FIXED: <file> — <reason>` — that code was not covered by the review phase. After a fix, re-run the gates that ran before the failing one too.
>
> End with exactly one of:
> - `GATES: PASS (<gate>: ok, …)` — every gate passed (known failures excepted, and listed)
> - `GATES: PARTIAL (<gate>: ok, …; NOT RUN: <gate> — <reason>; FAILED (environment): <gate> — <tests>)` — every gate that is not a plain pass is listed with its reason
> - `GATES_BLOCKED — <gate>: <reason>` — only for a real defect you could not fix

After the subagent returns:
- `GATES: PASS` → continue. Show any `KNOWN FAILURE` lines in the final summary.
- `GATES: PARTIAL` → **the user decides; never wave it through.** Show each unverified gate and its reason, then ask with **AskUserQuestion**: "Accept and continue — these are recorded as not verified" / "Accept, and remember the failing tests as known failures" (for `FAILED (environment)` entries: add their test names to that gate's `known_failures` in `.backlog-kit.toml`) / "Stop here". Whatever the answer, the final summary lists every `NOT RUN` and `FAILED (environment)` gate.
- `GATES_BLOCKED` → surface it and wait. Don't assume it belongs back in implementation without the user saying so.
- `PROD_CODE_FIXED:` lines → surface them and ask with **AskUserQuestion**: "Proceed (note them as unreviewed)" or "Re-run the review phase over those changes first". On proceed, record `UNREVIEWED_PROD_FIXES` for the final summary; on re-run, repeat the review phase and then this one.
- No signal → treat as `GATES_BLOCKED` and surface the raw response.
