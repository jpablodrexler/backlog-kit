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
python3 tools/install.py /path/to/your/repo             # the 12 core skills
python3 tools/install.py /path/to/your/repo --extras    # also the optional extras
python3 tools/install.py /path/to/your/repo --only bug-fix,bugs-next
```

Copies into `<repo>/.claude/skills/`; refuses to overwrite an existing skill (`--force` to replace). A project skill with the same name shadows the kit's — use Option A in that case.

## After installing

Ask Claude to plan your first feature or file a bug; the backlog files are created on first use. Check: "show feature status" should report an empty backlog without errors.
