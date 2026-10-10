# Installing backlog-kit

Requirements: Claude Code, Python 3.11+ on `PATH` as `python3`, git. [OpenSpec](https://github.com/Fission-AI/OpenSpec) only if you set `[spec] workflow = "openspec"`.

## Option A: Claude Code plugin (recommended)

The repo is both a plugin and a one-plugin marketplace.

```
/plugin marketplace add jpablodrexler/backlog-kit
/plugin install backlog-kit@backlog-kit
```

Skills then appear namespaced, e.g. `backlog-kit:bug-fix`. Naming a skill in plain language ("fix BUG-004") still triggers it. The namespace is what keeps the kit from clashing with a skill of the same name in your project.

For a local checkout instead of a published repo: `/plugin marketplace add ./path/to/backlog-kit`.

## Option B: copy the skills into one repo

```
python3 tools/install.py /path/to/your/repo
```

This copies every skill to `<repo>/.claude/skills/`. It refuses to overwrite a skill that already exists (`--force` to replace; `--only bug-fix,bugs-next` to take a subset). Each skill is self-contained, so nothing else is required.

**Name clashes.** A project-level skill with the same name wins over, or is confused with, the kit's. If your repo already has `bug-fix`, `feature-plan`, etc., use Option A, or install into a repo that doesn't.

## After installing

1. Copy `backlog-kit.example.toml` to `<repo>/.backlog-kit.toml`; set at least `[[gates]]` for your build and tests.
2. Ask Claude to plan your first feature or file a bug; the backlog files are created on first use.
3. Add `docs/reports/` to `.gitignore` if you don't want batch reports committed (your choice).

Check the install: ask "show feature status" — `features-status` should report an empty backlog without errors.
