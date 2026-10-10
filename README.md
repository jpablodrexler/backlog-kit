# backlog-kit

**Your backlog is plain markdown in the repo, and Claude works it to done through quality gates. Nothing is committed without you.**

A pack of [Claude Code](https://claude.com/claude-code) skills. Features and bugs live as markdown tables and one file per item under `docs/backlog/`. Claude plans them, picks the next one, implements it on a branch, runs *your* gates (tests, lint, build) and reviews, then archives it. The work skills never run `git commit`, `git push` or open a PR: you review the diff. When you ask for it, the `gitflow` skill commits, pushes and opens the PR, showing you each step first.

No server, no database, no service: the markdown files are the state. It works on any stack, because gates and reviews are declared in a config file, not baked in.

## What's in it

| Area | Skills |
| --- | --- |
| Plan & track | `feature-plan`, `features-next`, `features-status`, `features-archive`, `bug-report`, `bugs-next`, `bugs-status`, `bugs-archive`, `decision-record` |
| Work one item | `feature-development`, `bug-fix` (reproduce with a failing test first, then fix), `spec-compliance-check` (proves each scenario with a test it ran, writes the evidence) |
| Branch, commit, PR, clean up | `gitflow` — `start`, `sync`, `commit`, `finish` (push + PR), `cleanup`; only when you ask, and it asks before every write |
| Work a list unattended | `features-batch-development`, `bugs-batch-fix` — one shared branch, zero commits, a dated report updated after each item, resumable after a crash |

## Principles

- **Nothing is committed, pushed or opened as a PR unless you ask for it.** The work skills' only git writes are branch switching and fast-forward merges. Only `gitflow` can commit, push or open a PR, only when you invoke it, and only after showing the exact commit message, files or PR text and getting a yes for each write. It never merges a PR, force-pushes or rewrites history. Lint tests enforce all of this.
- **Gates are yours.** `[[gates]]` in `.backlog-kit.toml` lists the commands to run. Failures are reported as they are: known failures, environment problems and files no gate covers are named, never folded into "pass".
- **Hand-backs are claims.** Work done by subagents is spot-checked before it is reported.
- **OpenSpec is optional and never bundled.** Set `[spec] workflow = "openspec"` to use it; the kit only depends on it being installed.
- **Python stdlib only** (3.11+, for `tomllib`) for the helper scripts.

## Install

See [INSTALL.md](INSTALL.md): as a Claude Code plugin, or by copying the skills into a repo.

## Configure

Copy [`backlog-kit.example.toml`](backlog-kit.example.toml) to `.backlog-kit.toml` in your repo root and edit. With no file, defaults apply (`docs/backlog`, no gates). A worked example for an Angular project is in [`examples/angular-supabase.toml`](examples/angular-supabase.toml).

## Use

Say what you want; the skills trigger on intent:

- "Plan a feature: dark-mode toggle" → `feature-plan` drafts the row and brief and asks before writing.
- "What should I work on next?" → `features-next` / `bugs-next`.
- "Develop the next feature" → `feature-development`. "Fix BUG-004" → `bug-fix`.
- "Fix BUG-004, BUG-007 and BUG-009 while I'm out" → `bugs-batch-fix`.
- "Commit this", "finish the feature", "open the PR" → `gitflow`. After the PR merges: "clean up the branches", then "what's next?".

Each work run ends by telling you plainly that nothing was committed and what to review, and names `gitflow` for the next step.

## Development

```
python3 tools/vendor.py          # refresh the copies of lib/ and shared/ inside each skill
python3 -m unittest discover -s tests
```

Edit `lib/` and `shared/`, never the vendored copies; the tests fail on drift. Design notes and dogfood findings: [DESIGN.md](DESIGN.md).

## Status

Early (0.2). Exercised live on real repositories (bug and feature batches, a resume, the OpenSpec path). `gitflow` is covered by tests against real git repositories but has not been run live against GitHub yet; release/hotfix flows are not included.

## License

MIT
