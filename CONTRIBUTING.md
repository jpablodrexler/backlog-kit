# Contributing

Issues and pull requests are welcome. The kit is deliberately small; the best contributions fix a wrong behaviour, a confusing sentence in a skill, or a case the scripts get wrong.

## Before you open a PR

```
python3 tools/vendor.py --check
python3 -m unittest discover -s tests
```

- **The README diagram is generated.** Edit the table in `tools/diagram.py` and run `python3 tools/diagram.py` to rewrite `docs/loop.svg` (a new skill must be added to the table; a test fails otherwise).
- **Edit sources, not copies.** `lib/*.py` is copied into each skill by `tools/vendor.py` (run it without `--check` after editing `lib/`).
- **Skills are markdown.** Keep a skill free of stack-specific words (the tests enforce it) and keep the no-commit promise: only `gitflow` may push, open a PR or tag. Skills other than `gitflow` carry the line `**Never run `git commit`, `git push` or open a PR.**`
- **New settings need a reason.** The kit has two (`[paths] backlog_dir` and `[viewports]`). Prefer a sentence in a skill that tells Claude to ask or to look at the project's docs.
- **Describe the change** in `CHANGELOG.md` (version bump in `.claude-plugin/plugin.json`).

## Reporting a problem

Say which skill, what you asked, what Claude did, and what you expected. A copy of the signal line or the report the skill produced helps most. For anything security-related see [SECURITY.md](SECURITY.md).
