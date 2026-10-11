# Contributing

Issues and pull requests are welcome. The kit is deliberately small; the best contributions fix a wrong behaviour, a confusing sentence in a skill, or a case the scripts get wrong.

## Before you open a PR

```
python3 tools/vendor.py --check
python3 -m unittest discover -s tests
```

- **Edit sources, not copies.** `lib/*.py` is copied into each skill by `tools/vendor.py` (run it without `--check` after editing `lib/`).
- **Skills are markdown.** Keep a skill free of stack-specific words (the tests enforce it) and keep the no-commit promise: only `gitflow` may push, open a PR or tag. Skills other than `gitflow` carry the line `**Never run `git commit`, `git push` or open a PR.**`
- **New settings need a reason.** The kit has two (`[paths] backlog_dir` and `[viewports]`). Prefer a sentence in a skill that tells Claude to ask or to look at the project's docs.
- **Describe the change** in `CHANGELOG.md` (patch version bump in `.claude-plugin/plugin.json`).

The fidelity tool (`tools/fidelity.py`) compares skills with the two source projects' originals, which are not in this repository; you can ignore it unless you work on those conversions (`fidelity/SOURCES.md`).

## Reporting a problem

Say which skill, what you asked, what Claude did, and what you expected. A copy of the signal line or the report the skill produced helps most. For anything security-related see [SECURITY.md](SECURITY.md).
