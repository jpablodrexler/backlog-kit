# backlog-kit

[![CI](https://github.com/jpablodrexler/backlog-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/jpablodrexler/backlog-kit/actions/workflows/ci.yml)

**Your backlog is plain markdown in the repo, and Claude works it to done through quality gates. Nothing is committed without you.**

A small set of [Claude Code](https://claude.com/claude-code) skills that take a feature (or a bug) from idea to a verified, archived result: features and bugs live as markdown tables plus one brief per item under `docs/backlog/`, and the work follows git-flow branches. No server, no database, no config required.

## Quick start

```
/plugin marketplace add jpablodrexler/backlog-kit
/plugin install backlog-kit@backlog-kit
```

Then just talk to Claude:

- "Plan a feature: dark-mode toggle" → `feature-plan` drafts the row and the brief (a user story with acceptance criteria), asks before writing.
- "What should I work on next?" → `features-next` / `bugs-next`.
- "Develop the next feature" / "Fix BUG-004" → `feature-development` / `bug-fix`.
- "Finish the feature, open the PR" → `gitflow`. After merging: "clean up the branches".

That is all the setup there is. Backlog files are created on first use in `docs/backlog/`.

## The core (12 skills)

| Skill | What it does |
| --- | --- |
| `feature-plan`, `bug-report` | add an item to the backlog (row + brief) |
| `features-next`, `bugs-next` | recommend what to do next |
| `features-status`, `bugs-status` | show the state of the backlog |
| `features-archive`, `bugs-archive` | move finished items to the implemented / fixed tables |
| `feature-development`, `bug-fix` | do one item end to end (below) |
| `gitflow` | branches, PR, release, tag, clean up |
| `decision-record` | record a design decision as a short numbered note |

**`feature-development` phases** — each runs in a subagent, and the ones that do not apply to your project are skipped (you are asked, or it is stated plainly):

1. Propose — pick the feature, create the branch, write the spec (the brief `features/NNN-name.md` is the spec; [OpenSpec](https://github.com/Fission-AI/OpenSpec) is used only if the repo has an `openspec/` folder).
2. Implement, then a review gate run by the orchestrator — a code review always; database / security / viewport reviews only when the change touches those; each in its own subagent, each report checked before the next step.
3. Tests *(optional)*  4. E2E *(optional)*  5. Build *(optional)*
6. Prove each requirement against the spec (its own subagent), then sync docs, archive the change and move the item to implemented.
7. Commit *(only when you ask)*.

`bug-fix` is the same shape, starting from a failing regression test. You ask in plain words ("develop X", "stay on this branch", "commit as you go"); by default both leave the result **uncommitted** on the branch for you to review.

## The loop

```
plan ──► select ──► branch ──► develop + verify ──► commit ──► PR ──► review ──► merge ──► clean up ─┐
 ▲   feature-plan  features-next   feature-development   (you)       gitflow   (you)    (you)   gitflow  │
 │   bug-report    bugs-next       bug-fix                                                            │
 └─────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

The middle of the loop (`feature-development`, `bug-fix`) commits nothing unless you ask: by default it leaves a verified, archived result uncommitted on a branch for you to review, and when you ask for commits (one at the end, or as the work goes) `gitflow` makes them. You commit it yourself otherwise; the ends of the loop (starting and syncing branches, pushing and opening the PR, tagging, cleaning up) belong to `gitflow`, which you invoke when you are ready. It never commits, pushes or opens a PR unless you ask, and it confirms before the first push of a branch, a tag and any deletion.

## Extras (optional)

Install them when you want them: `python3 tools/install.py <repo> --extras` (or `--all`). The reviewers, `docs-sync`, `spec-compliance-check` and `dependency-upgrade` work out of the box from your `CLAUDE.md` and docs, and get sharper if you add review-check sections to your docs — see [docs/extras.md](docs/extras.md).

`code-reviewer`, `security-reviewer`, `database-reviewer`, `architecture-reviewer`, `product-scope-roaster`, `docs-sync`, `dependency-upgrade`, `spec-compliance-check`, `features-batch-development`, `bugs-batch-fix`.

## Where things live

The skills share a few fixed locations, so every project that uses the kit looks the same: the backlog and its briefs in `docs/backlog/`, decisions in `docs/decisions/`, dated reports in `docs/reports/`, and reference docs in `docs/*.md` (`architecture.md`, `features.md`, `frontend.md`, `backend.md`, `database.md`, `security.md`). The full table is [`shared/conventions.md`](shared/conventions.md); [`docs/conventions.md`](docs/conventions.md) explains it, says which documents are mandatory (only `CLAUDE.md`) and which are optional, and shows a filled-in example. A project carries it as a `## Kit conventions` section in its `CLAUDE.md`, with a "Checked against" column that tells `docs-sync` what each doc is compared with; `docs-sync` checks the section and offers to add it.

## Adapting it

If your project fits the workflow, use it as is. If not, take ideas from the skills: fork the repo, or copy the `SKILL.md` files into `.claude/skills/` and edit them. They are plain markdown.

Everything is optional. `.backlog-kit.toml` at the repo root has two settings, both documented in [`backlog-kit.example.toml`](backlog-kit.example.toml): the backlog folder (`[paths] backlog_dir`, default `docs/backlog`) and the devices the UI viewport check uses (`[viewports]`, default Galaxy S23 Ultra 384×824 and desktop 1920×1080).

## Requirements

Claude Code, git, Python 3.11+ for the helper scripts (standard library only). `gitflow` uses the `gh` CLI or the GitHub MCP tools; on another host it prints the PR text and push command for you to run.

## Limitations

Early software (0.2), exercised on real repositories but not exhaustively. `gitflow` has been tested against real git repositories, not yet against GitHub (PR creation, remote deletion). Subagent hand-backs are claims: the orchestrator spot-checks the important ones. GitHub only for PRs. A skill of the same name in your project shadows the kit's when you install by copying (the plugin namespaces them).

## For maintainers

[INSTALL.md](INSTALL.md) · [CONTRIBUTING.md](CONTRIBUTING.md) · [SECURITY.md](SECURITY.md) · [CHANGELOG.md](CHANGELOG.md) · [DESIGN.md](DESIGN.md) (design) · [MIGRATING.md](MIGRATING.md) (replacing a project's own copies of these skills)

```
python3 tools/vendor.py --check
python3 -m unittest discover -s tests
```

## License

MIT
