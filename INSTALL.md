# Installing backlog-kit

Requirements: Claude Code, Python 3.11+ on `PATH` as `python3`, git.

## Option A: Claude Code plugin (recommended)

```
/plugin marketplace add jpablodrexler/backlog-kit
/plugin install backlog-kit@backlog-kit
```

Skills appear namespaced, e.g. `backlog-kit:bug-fix`; naming a skill in plain language ("fix BUG-004") still triggers it. For a local checkout: `/plugin marketplace add ./path/to/backlog-kit`.

## Option B: copy the skills into one repo

```
python3 tools/install.py /path/to/your/repo             # the 17 core skills
python3 tools/install.py /path/to/your/repo --extras    # also the optional extras
python3 tools/install.py /path/to/your/repo --only bug-fix,bugs-next
```

Copies into `<repo>/.claude/skills/`; refuses to overwrite an existing skill (`--force` to replace). A project skill with the same name shadows the kit's — use Option A in that case.

## Settings (optional)

Nothing needs configuring. A `.backlog-kit.toml` at the repo root changes the defaults; copy [`backlog-kit.example.toml`](backlog-kit.example.toml) and keep only what you change:

- `[paths] backlog_dir` — the backlog folder (default `docs/backlog`).
- `[git]` — the long-lived branches `gitflow`, `feature-development` and `bug-fix` work against. `integration_branch` (default `develop`) is where topic branches start and where their PRs go; `production_branch` (default `main`) receives releases and hotfixes and gets the version tag. Set both to the same branch (for example `main`) for trunk-based development: a release then opens one PR instead of two, and the `develop` branch is never created. `host` (`auto`, `github`, `gitlab` or `other`; default `auto`) says where the PRs are opened: `auto` reads the origin URL, so set it explicitly for a self-hosted GitHub or GitLab. GitHub uses `gh` or the GitHub MCP tools, GitLab uses `glab`; on `other` hosts `gitflow` prints the PR text and the push command for you.
- `[viewports]` — the devices of the UI viewport check.

## After installing

Ask Claude to plan your first feature or file a bug; the backlog files are created on first use. Check: "show feature status" should report an empty backlog without errors.
