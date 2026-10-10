# backlog-kit

[![CI](https://github.com/jpablodrexler/backlog-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/jpablodrexler/backlog-kit/actions/workflows/ci.yml)

**Your backlog is plain markdown in the repo, and Claude works it to done through quality gates. Nothing is committed without you.**

A pack of [Claude Code](https://claude.com/claude-code) skills. Features and bugs live as markdown tables, one file per item, under `docs/backlog/`. Claude plans them, picks the next one, branches, implements with tests, runs *your* gates (tests, lint, build) and reviews, and archives the result. Publishing it (commit, push, PR) happens only when you ask, and only after Claude shows you exactly what it is about to do.

There is no server, no database and no service: the markdown files are the state, so they diff, review and merge like code. It works on any stack because gates and reviews are declared in a config file, not baked into the skills.

## The loop

```
plan ──► select ──► branch ──► develop + verify ──► commit ──► PR ──► review ──► merge ──► clean up ─┐
 ▲   feature-plan  features-next   feature-development   gitflow   gitflow   (you)    (you)   gitflow  │
 │   bug-report    bugs-next       bug-fix                                                            │
 └─────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

The middle of the loop (`feature-development`, `bug-fix`, the batch runners) never commits: it leaves a verified, archived result uncommitted on a branch for you to review. The ends of the loop belong to `gitflow`, which you invoke when you are ready.

## What's in it

| Area | Skills |
| --- | --- |
| Plan and track | `feature-plan`, `features-next`, `features-status`, `features-archive`, `bug-report`, `bugs-next`, `bugs-status`, `bugs-archive`, `decision-record` |
| Work one item | `feature-development`, `bug-fix` (reproduce with a failing test first, then fix), `spec-compliance-check` (proves each scenario with a test it ran and writes the evidence) |
| Branch, commit, PR, clean up | `gitflow` — `start`, `sync`, `commit`, `finish` (push and open the PR), `cleanup`; only when you ask, and it asks before every write |
| Work a list unattended | `features-batch-development`, `bugs-batch-fix` — one shared branch, zero commits, a dated report updated after each item, resumable after a crash |

## Quick start

1. **Install** (see [INSTALL.md](INSTALL.md) for details):
   ```
   /plugin marketplace add jpablodrexler/backlog-kit
   /plugin install backlog-kit@backlog-kit
   ```
2. **Configure** — copy [`backlog-kit.example.toml`](backlog-kit.example.toml) to `.backlog-kit.toml` in your repo and list your gates:
   ```toml
   [[gates]]
   name = "tests"
   run  = "npm test"
   ```
   With no file the defaults apply (`docs/backlog`, no gates; the first run proposes gates and asks before saving them).
3. **Talk to Claude** — the skills trigger on intent:
   - "Plan a feature: dark-mode toggle" → `feature-plan` drafts the row and the brief and asks before writing.
   - "What should I work on next?" → `features-next` / `bugs-next`.
   - "Develop the next feature", "Fix BUG-004" → `feature-development` / `bug-fix`.
   - "Fix BUG-004, BUG-007 and BUG-009 while I'm out" → `bugs-batch-fix`.
   - "Commit this", "finish the feature", "open the PR" → `gitflow`. After you merge: "clean up the branches", then "what's next?".

Each work run ends by saying plainly that nothing was committed, what to review, and which skill to ask for next.

## Principles

- **Nothing is committed, pushed or opened as a PR unless you ask for it.** The work skills' only git writes are branch switching and fast-forward merges. Only `gitflow` can commit, push or open a PR, only when you invoke it, and only after showing the exact commit message, files or PR text and getting a yes for each write. It never merges a PR, force-pushes or rewrites history. Lint tests enforce all of this.
- **Gates are yours.** `[[gates]]` lists the commands to run. Failures are reported as they are: known failures, environment problems and files no gate covers are named, never folded into "pass".
- **Evidence over claims.** Work done by subagents is spot-checked before it is reported; a scenario is verified only by a test that was actually run.
- **Mechanics are code, judgment is Claude.** Ranking, ordering, ids, dependency detection, table checks, branch decisions and PR facts come from small, tested, read-only Python scripts; Claude is asked only for what needs judgment.
- **OpenSpec is optional and never bundled.** Set `[spec] workflow = "openspec"` to use it; the kit only depends on it being installed.

## Configuration

Everything is optional; see [`backlog-kit.example.toml`](backlog-kit.example.toml) for every key. The ones most projects set:

| Section | Keys |
| --- | --- |
| `[paths]` | `backlog_dir`, `decisions_dir`, `reports_dir` |
| `[features]`, `[bugs]` | priority / effort / severity vocabularies, bug id prefix, which environments count as production |
| `[spec]` | `workflow` (`none` or `openspec`), `changes_dir`, `compliance_skill` |
| `[git]` | `base_branch`, `feature_prefix`, `fix_prefix`, `finish_skill` |
| `[work]` | `review_max_rounds`, `gate_max_rounds` |
| `[[gates]]` | `name`, `run`, `cwd`, `when`, `ask_before`, `timeout_minutes`, `known_failures` |
| `[[reviews]]` | `name`, `focus`, `skill`, `when` |

A worked example for an Angular project: [`examples/angular-supabase.toml`](examples/angular-supabase.toml).

## Requirements

Claude Code, git, and Python 3.11 or newer for the helper scripts (standard library only). `gitflow`'s `finish` and `cleanup` use the `gh` CLI or the GitHub MCP tools; on another host it prints the PR text and the push command for you to run. OpenSpec is needed only with `workflow = "openspec"`.

## Limitations

Early software (0.2), exercised live on real repositories but not exhaustively. Be aware of:

- **`gitflow` has been tested against real git repositories, not yet against GitHub.** Opening a PR and deleting remote branches have not been run end to end.
- **The OpenSpec path has run live once** (one feature through propose, apply, archive); the unattended batch runner with OpenSpec has not.
- **Windows and macOS are exercised only in CI as non-blocking jobs.** The scripts force UTF-8 output, but expect rough edges.
- **A review can be a self-review.** Where the implementing subagent cannot spawn another agent, it reviews its own diff after re-reading it cold. The report and the final summary say so; it is not an independent review.
- **Subagent hand-backs are claims.** The orchestrator spot-checks the important ones, but not every statement a subagent makes.
- **Dependency detection is a heuristic.** It finds briefs that name another pending feature or use a symbol that only another brief introduces; it cannot see a dependency described in prose with no named thing.
- **GitHub only for PRs.** No GitLab, Bitbucket or Azure DevOps integration.
- **No release, hotfix, tag or changelog actions.** They are project-specific; point `[git] finish_skill` at your own skill if you need them.
- **Project skills with the same name win.** When installing by copying into `.claude/skills/`, a skill of the same name already in the project shadows the kit's; the plugin install namespaces them (`backlog-kit:bug-fix`).

## Development

```
python3 tools/vendor.py          # refresh the copies of lib/ and shared/ inside each skill
python3 tools/vendor.py --check  # fail if any copy is stale (CI runs this)
python3 -m unittest discover -s tests
```

Each skill is self-contained so it works when installed alone; the single sources of truth are `lib/` (scripts) and `shared/` (phase documents), copied into each skill by `tools/vendor.py`. Edit the sources, never the copies. CI runs the tests on Linux (3.11–3.13) and the manifest checks on every push. Design notes, dogfood findings and the reasoning behind each release: [DESIGN.md](DESIGN.md). Release history: [CHANGELOG.md](CHANGELOG.md).

## License

MIT
