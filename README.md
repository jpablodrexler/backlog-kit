# backlog-kit

**Your backlog is plain markdown in the repo, and Claude works it to done through quality gates. Nothing is committed without you.**

A pack of [Claude Code](https://claude.com/claude-code) skills. Features and bugs live as markdown tables and one file per item under `docs/backlog/`. Claude plans them, picks the next one, implements it on a branch, runs *your* gates (tests, lint, build) and reviews, then archives it. It never runs `git commit`, `git push` or opens a PR. You review the diff and commit.

No server, no database, no service: the markdown files are the state. It works on any stack, because gates and reviews are declared in a config file, not baked in.

## What's in it

| Area | Skills |
| --- | --- |
| Plan & track | `feature-plan`, `features-next`, `features-status`, `features-archive`, `bug-report`, `bugs-next`, `bugs-status`, `bugs-archive`, `decision-record` |
| Work one item | `feature-development`, `bug-fix` (reproduce with a failing test first, then fix) |
| Work a list unattended | `features-batch-development`, `bugs-batch-fix` — one shared branch, zero commits, a dated report updated after each item, resumable after a crash |

## Principles

- **Nothing is committed without you.** The only git writes are branch switching and fast-forward merges; a lint test enforces this.
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

Each run ends by telling you plainly that nothing was committed and what to review.

## Development

```
python3 tools/vendor.py          # refresh the copies of lib/ and shared/ inside each skill
python3 -m unittest discover -s tests
```

Edit `lib/` and `shared/`, never the vendored copies; the tests fail on drift. Design notes and dogfood findings: [DESIGN.md](DESIGN.md).

## Status

Early (0.1). Exercised live on two real repositories (a bug batch and a feature batch with a resume). Not yet exercised live: the OpenSpec path and a fully blocked gate set.

## License

MIT
