# Security

The kit is markdown and small read-only Python scripts (standard library only); it runs with the permissions you give Claude Code. The relevant risks are a skill doing something outside its promise, or leaking something it should not.

## What the skills promise

- Work skills never run `git commit`, `git push` or open a PR; only `gitflow` can, and only when you ask, with confirmations before the first push of a branch, a tag and any deletion. It never force-pushes or merges a PR.
- A skill never reads a credentials file and never puts credentials in a prompt or a report.
- Subagent hand-backs are claims: the orchestrator spot-checks the important ones.

## Reporting a vulnerability

Please do not open a public issue. Use GitHub's private vulnerability reporting for this repository (Security tab → "Report a vulnerability"). Include which skill or script, what happens, and how to reproduce it. I aim to answer within a week.

## Supported versions

Only the latest release.
