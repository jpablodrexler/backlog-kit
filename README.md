# backlog-kit

[![CI](https://github.com/jpablodrexler/backlog-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/jpablodrexler/backlog-kit/actions/workflows/ci.yml)

**Your backlog is plain markdown in the repo, and Claude works it to done through quality gates. Nothing is committed without you.**

A pack of [Claude Code](https://claude.com/claude-code) skills. Features and bugs live as markdown tables, one file per item, under `docs/backlog/`. Claude plans them, picks the next one, branches, implements with tests, runs *your* phases (tests, lint, build, E2E) and reviews, and archives the result. Publishing it (push, PR, tag) happens only when you ask; you commit your own work.

There is no server, no database and no service: the markdown files are the state, so they diff, review and merge like code. It works on any stack because what "verified" and "reviewed" mean is written by you as markdown files in the project, not baked into the skills.

## The loop

```
plan ──► select ──► branch ──► develop + verify ──► you commit ──► PR ──► review ──► merge ──► clean up ─┐
 ▲   feature-plan  features-next   feature-development   (you)       gitflow   (you)    (you)   gitflow  │
 │   bug-report    bugs-next       bug-fix                                                            │
 └─────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

The middle of the loop (`feature-development`, `bug-fix`, the batch runners) never commits: it leaves a verified, archived result uncommitted on a branch for you to review. You commit it yourself; the ends of the loop (starting and syncing branches, pushing and opening the PR, tagging, cleaning up) belong to `gitflow`, which you invoke when you are ready.

## What's in it

| Area | Skills |
| --- | --- |
| Plan and track | `feature-plan`, `features-next`, `features-status`, `features-archive`, `bug-report`, `bugs-next`, `bugs-status`, `bugs-archive`, `decision-record` |
| Work one item | `feature-development`, `bug-fix` (reproduce with a failing test first, then fix), `spec-compliance-check` (read-only: matches each spec scenario to a passing test or a manual check and reports Verified, Failing or Unverified). Both run your own phase files from `.backlog-kit/feature/` and `.backlog-kit/bug/` for everything project-specific: tests, E2E, build, conditional reviews |
| Review a change | `code-reviewer`, `security-reviewer`, `database-reviewer` — the frame (workflow, severities, dated report, fix workflow) is the kit's; the stack-specific checklists are yours, as files in `.backlog-kit/review/<code\|security\|database>/` that each start with a `Read when:` line. `examples/` has the two source projects' |
| Review the whole | `architecture-reviewer` (qualitative, grounded system health check), `product-scope-roaster` (harsh product-owner critique of the whole backlog) |
| Keep things current | `docs-sync` (docs follow the code; the map of doc sections to their source of truth is a project file in `.backlog-kit/docs/`), `dependency-upgrade` (grouped, tested after each group; the ecosystem's commands and rules are project files in `.backlog-kit/dependency-upgrade/`) |
| Branch, PR, release, clean up | `gitflow` — start and sync `feature/`, `fix/`, `doc/`, `skill/`, `chore/` branches, `finish` (push and open the PR), `release`/`hotfix` (changelog, your own release phases from `.backlog-kit/release/`, two PRs, tag), `cleanup`; only when you ask, with the confirmations of the original skills (first push, tag, delete) |
| Work a list unattended | `features-batch-development`, `bugs-batch-fix` — one shared branch, zero commits, a dated report updated after each item, resumable after a crash (plain skills, no helper scripts) |

## Quick start

1. **Install** (see [INSTALL.md](INSTALL.md) for details):
   ```
   /plugin marketplace add jpablodrexler/backlog-kit
   /plugin install backlog-kit@backlog-kit
   ```
2. **Configure** — with no file the defaults apply (`docs/backlog`). To change the backlog folder, copy [`backlog-kit.example.toml`](backlog-kit.example.toml) to `.backlog-kit.toml`. To say what "verified" means in your project, add phase files: one markdown file per step in `.backlog-kit/feature/` (for `feature-development`) and `.backlog-kit/bug/` (for `bug-fix`), run in filename order — see [`shared/project-phases.md`](shared/project-phases.md) for the format and [`examples/`](examples/) for the two projects the kit comes from.
3. **Talk to Claude** — the skills trigger on intent:
   - "Plan a feature: dark-mode toggle" → `feature-plan` drafts the row and the brief and asks before writing.
   - "What should I work on next?" → `features-next` / `bugs-next`.
   - "Develop the next feature", "Fix BUG-004" → `feature-development` / `bug-fix`.
   - "Fix BUG-004, BUG-007 and BUG-009 while I'm out" → `bugs-batch-fix`.
   - "Finish the feature", "open the PR", "start a release" → `gitflow` (you commit your own work). After you merge: "clean up the branches", then "what's next?".

Each work run ends by saying plainly that nothing was committed, what to review, and which skill to ask for next.

## Principles

- **Nothing is committed, pushed or opened as a PR unless you ask for it.** The work skills never commit, push or open a PR; their only git writes are creating, switching and syncing the branch through `gitflow`. Only `gitflow` can push, open a PR or tag, only when you invoke it, and it asks before the first push of a branch, before a tag and before deleting a branch. It never merges a PR, force-pushes or rewrites history. Lint tests enforce the work skills' side of this.
- **Verification is yours.** What counts as tested, built or reviewed is written by you as project phase files; the kit runs them in order and stops on a `PHASE: BLOCKED`. A phase that did not apply says `SKIPPED`, and one that could not check everything says `PARTIAL` — neither is folded into "pass".
- **Evidence over claims.** Work done by subagents is spot-checked before it is reported; a scenario is verified only by a test that was actually run.
- **Mechanics are code, judgment is Claude.** Ranking, ordering, ids, dependency detection, table checks, branch decisions and PR facts come from small, tested, read-only Python scripts; Claude is asked only for what needs judgment.
- **OpenSpec is required and never bundled.** `feature-development` expects the `openspec` CLI and `openspec/changes`; install it separately.

## Configuration

There is one setting, `[paths] backlog_dir` (default `docs/backlog`; the decisions, explorations and reports folders sit next to it), and the whole `.backlog-kit.toml` is optional — see [`backlog-kit.example.toml`](backlog-kit.example.toml). Everything else about your project is markdown in `.backlog-kit/`:

| Folder | Read by |
| --- | --- |
| `feature/NN-*.md`, `bug/NN-*.md` | `feature-development`, `bug-fix`: the phases after implementing (tests, E2E, build, conditional reviews), in filename order |
| `release/NN-*.md` | `gitflow`: what runs before a release or hotfix is pushed |
| `review/code/`, `review/security/`, `review/database/` | the reviewers' checklists, each file with a `Read when:` line |
| `spec-compliance/`, `docs/`, `dependency-upgrade/` | the project's knowledge for those skills, same file shape |

[`examples/`](examples/) holds the two projects the kit comes from, converted.

## Requirements

Claude Code, git, and Python 3.11 or newer for the helper scripts (standard library only). `gitflow`'s `finish` and `cleanup` use the `gh` CLI or the GitHub MCP tools; on another host it prints the PR text and the push command for you to run. OpenSpec is needed only with `workflow = "openspec"`.

## Limitations

Early software (0.2), exercised live on real repositories but not exhaustively. Be aware of:

- **`gitflow` has been tested against real git repositories, not yet against GitHub.** Opening a PR and deleting remote branches have not been run end to end.
- **The OpenSpec path has run live once** (one feature through propose, apply, archive); the unattended batch runner with OpenSpec has not.
- **Windows and macOS are exercised only in CI as non-blocking jobs.** The scripts force UTF-8 output, but expect rough edges.
- **Subagent hand-backs are claims.** The orchestrator spot-checks the important ones, but not every statement a subagent makes.
- **The review, docs and upgrade skills are first versions.** They are generalized from two projects' skills, covered by structural tests only, and not yet run live: expect to tune their checklists to your stack through the project's own conventions documents.
- **Dependency detection is a heuristic.** It finds briefs that name another pending feature or use a symbol that only another brief introduces; it cannot see a dependency described in prose with no named thing.
- **GitHub only for PRs.** No GitLab, Bitbucket or Azure DevOps integration.
- **Release steps beyond the changelog, PRs and tag are yours.** Bumping a version or running a release regression suite goes in `.backlog-kit/release/NN-*.md` phase files; `examples/` has the two source projects'.
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
