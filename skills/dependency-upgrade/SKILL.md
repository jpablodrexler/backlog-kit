---
name: dependency-upgrade
description: Routine, user-driven dependency upgrade cycle for any stack. Surveys what is outdated with the project's own package manager, classifies each dependency as patch, minor or major with changelog risk notes, proposes groups, applies one group at a time (asking first), runs every configured verification gate after each group, rolls back a group that fails by restoring the manifest and lockfile, and writes a dated report. Majors only on the user's explicit pick, never mixed with other bumps. TRIGGER when asked to upgrade dependencies, bump package versions, check for outdated packages, or do routine dependency maintenance. A known-vulnerable dependency is a security finding, not this skill's job.
license: MIT
metadata:
  version: "0.1"
---

Run one routine upgrade cycle over the project's own dependencies and leave the result uncommitted in the working tree for the user to review. `<reports_dir>` comes from `[paths]` in `.backlog-kit.toml` (default `docs/reports`); gates come from `[[gates]]` in the same file. With no file the defaults apply.

**Input**: optionally a scope (one manifest or folder, one ecosystem, or "everything"). If the repo has several manifests and no scope was given, ask which to cover.

This skill is the routine cadence: keep things current, prove nothing broke. A dependency with a known vulnerability is a security finding (the project's security review owns it, and it may justify an out-of-cycle bump). If the survey happens to show an advisory, name it in the report and tell the user; do not turn this run into a security fix.

## 1. Detect the package manager (only what the project already uses)

Detect from files that already exist. Use only a tool the project demonstrably uses, and never introduce one, suggest switching, or run a command for an ecosystem with no manifest in the repo. If the project uses something not in the table, ask the user for its survey/upgrade/install commands.

| Detected by | Survey (read-only) | Upgrade one package | Install from lockfile (no rewrite) |
| --- | --- | --- | --- |
| `package-lock.json` (npm) | `npm outdated` | `npm install <pkg>@<version>` | `npm ci` |
| `pnpm-lock.yaml` (pnpm) | `pnpm outdated` | `pnpm add <pkg>@<version>` | `pnpm install --frozen-lockfile` |
| `yarn.lock` (yarn) | `yarn outdated` (classic); berry has no built-in non-interactive listing (`upgrade-interactive` is interactive), so ask the user how to get the list | `yarn add <pkg>@<version>` | `yarn install --frozen-lockfile` (classic) or `--immutable` (berry) |
| `requirements*.txt` / `pyproject.toml` with pip | `pip list --outdated` (project venv) | edit the pin, then `pip install -r <file>` | `pip install -r <file>` |
| `uv.lock` (uv) | `uv tree --outdated` | `uv lock --upgrade-package <pkg>` | `uv sync --frozen` |
| `poetry.lock` (poetry) | `poetry show --outdated` | `poetry update <pkg>` (or `poetry add <pkg>@<version>` for a major) | `poetry install --sync` |
| `pom.xml` (Maven) | `mvn versions:display-dependency-updates` (only if the plugin is configured or the user agrees) | edit the version, or `mvn versions:use-latest-versions -Dincludes=<g:a>` | `mvn -B dependency:resolve` / the build |
| `build.gradle(.kts)` (Gradle) | `./gradlew dependencyUpdates` (only if that plugin is configured) | edit the version in the build file / version catalog | `./gradlew build --refresh-dependencies` only when needed |
| `*.csproj` / `*.sln` (dotnet) | `dotnet list package --outdated` | `dotnet add <project> package <pkg> --version <version>` | `dotnet restore` |
| `go.mod` (Go modules) | `go list -u -m all` | `go get <module>@<version>` then `go mod tidy` | `go mod download` |
| `Cargo.lock` / `Cargo.toml` (Cargo) | `cargo outdated` (only if installed) or `cargo update --dry-run` | `cargo update -p <crate>` (within range) or edit `Cargo.toml` for a major | `cargo fetch --locked` |

Notes:
- Run every command from the manifest's own folder, inside the project. Never use a global install, `sudo`, or a system package manager, and never install a missing tool (for example a plugin that provides the outdated listing): say it is unavailable and ask the user how to get the list.
- Network access to the registry is allowed only to survey, upgrade and install this project's own dependencies. Nothing else may use the network.
- Some tools list only what is outdated within the declared range, others the absolute latest. Note which the survey shows, and check the manifest's declared range when it matters.

## 2. Preconditions

1. **Gates.** Read `[[gates]]` from `.backlog-kit.toml`. If none are configured, say so plainly and ask with AskUserQuestion which commands verify the project (tests, build, lint) before applying anything. Do not apply a single bump without a way to verify it; if the user declines, stop after the survey and report.
2. **Working tree.** Stay on the current branch; this skill never switches branches. If the manifests or lockfiles already have uncommitted changes, tell the user, because a rollback restores to the state before the group and they should know what that state includes. Ask whether to continue.
3. **Baseline.** Run the gates once before changing anything so a failure already present is not blamed on the upgrade. A failure matching a gate's `known_failures` pattern is reported as KNOWN FAILURE and is not caused by the upgrade. Any other baseline failure: show it and ask whether to continue.
4. **Snapshot.** Before each group, copy every manifest and lockfile the group will touch into `<reports_dir>/dependency-upgrade/snapshots/<YYYY-MM-DD>/group-<n>/`, keeping their relative paths (a plain file copy, inside the repository, not a git operation), so the group can be rolled back exactly. Nothing is written outside the repository. Delete the snapshot folder when the run ends, after the report is written.

## 3. Survey and classify

Run the survey command(s) for the detected ecosystems. For each outdated dependency record: name, current, wanted, latest, and direct or transitive. Classify by the leftmost non-zero version component that changes: **patch**, **minor** or **major** (for `0.x` versions a minor bump is treated as potentially breaking: mark it "minor (0.x, treat like major)"). Add a risk note for anything beyond a patch, from the changelog or release notes when available (the package's own changelog file, or the registry page); if none is reachable, write "no changelog found" rather than guessing. Flag a dependency that nothing in the code imports as a removal candidate rather than spending a bump on it, but do not remove it in this run.

Also note deliberate version pins (a comment, an exact version, an `overrides`/constraint entry): list them as skipped with the reason, and do not change them unasked.

Show the user the table before proposing anything.

## 4. Propose groups

- **Patch and minor** bumps are proposed by default, grouped by blast radius: dev tooling, test tooling, runtime libraries, and a framework family that must move together (such as packages versioned in lockstep) as one group.
- **Major** bumps are listed but never applied unless the user explicitly picks that package. Each approved major is its own group. **Never mix a major with other bumps in one group**, and never put two majors in one group.
- Prefer the ecosystem's own upgrade tooling for frameworks that ship migration tools, and move one major version at a time, never skipping versions.
- Keep groups small enough that a failure points at a short list.

Present the groups with AskUserQuestion: which groups to apply, and which majors (if any) to attempt. Nothing is applied before this answer.

## 5. Apply one group at a time

For each approved group, in order:

1. Ask with AskUserQuestion before applying it (for a major, name the package, the old and new version and the risk note). "Skip" and "Stop here" are choices.
2. Take the snapshot (section 2.4).
3. Apply the group with the table's upgrade command, then the lockfile-respecting install (for example `npm ci`) so the tree matches the lockfile. Lockfile discipline: only the upgrade command itself may rewrite tracked manifest and lockfile files. Do not use a plain install command that rewrites the lockfile as a way to fix things, and do not touch tracked files for any other reason.
4. Run every gate under `[[gates]]` in order, each with its `run` command from its `cwd`, within its `timeout_minutes`. A failure matching a `known_failures` pattern is reported as KNOWN FAILURE and the gate counts as passed apart from those tests. A gate that cannot run here is `NOT RUN (environment): <reason>`. Never skip, delete or weaken a test to get green.
5. **Pass** (all gates pass apart from known failures): keep the group, record it, move to the next.
6. **Fail** (a new failure): first decide whether it is caused by the bump or by the environment. If caused by the bump, you may make one small, obvious fix to project code or tests that the new version requires (a renamed import, a changed option) only if the user's pick covers it; otherwise do not widen the scope. If the group still fails, **roll back**: restore each manifest and lockfile by copying it back from the group's snapshot folder, re-run the lockfile-respecting install, and re-run the gates once to confirm the tree is back to the baseline. Record the group as ROLLED BACK with the failing gate and test names. If the group had several packages, you may offer to retry it split in two, as a new group with its own question.

A rollback restores only the files the group changed. Never run a destructive git command (`git checkout`, `git reset`, `git stash`) to do it.

## 6. Report

Write `<reports_dir>/dependency-upgrade/DEPENDENCY_UPGRADE_<YYYY-MM-DD>.md` (create the folder if needed; if the file exists use `-2`, `-3` for the same day). Contents:

- **Header**: date, the current branch, package manager(s) and manifests covered, the gates run.
- **Applied**: each dependency, old to new, its bump type, grouped as applied.
- **Rolled back**: each group, the failing gate and tests, and the likely cause.
- **Skipped**: majors not picked (with risk notes), pinned dependencies, removal candidates, anything not applied and why.
- **Gates**: per group, each gate's result, including every KNOWN FAILURE, NOT RUN and FAILED (environment) line. Never fold these into a plain pass.
- **Security**: any advisory the survey surfaced, passed to the user as a finding for the security review.
- **Not verified**: what no gate covers, if the changed manifests belong to a folder with no gate.

Then tell the user plainly: nothing was committed, the changes are in the working tree on the current branch, which files changed (manifests and lockfiles), and the report path.

---

## Guardrails

- **Never run `git commit`, `git push` or open a PR.** This skill edits manifests and lockfiles through the project's package manager, runs the project's gates and writes one report under `<reports_dir>/dependency-upgrade/`; it never switches branches.
- Use only the package manager the project already uses. Never invent or install a tool, never install system packages, never use `sudo` or a global install. Package-manager commands run inside the project.
- Registry network access is for surveying, upgrading and installing the project's own dependencies only.
- Ask with AskUserQuestion before applying each group and before any major. Never apply a major unasked, and never mix a major with other bumps in one group.
- Never apply a bump without gates to verify it. Never skip, delete or weaken a test to get green, and never report a KNOWN FAILURE, NOT RUN or environment failure as a pass.
- Roll back a failing group exactly (manifest and lockfile restored from the snapshot); never leave a half-applied group.
- This skill is routine maintenance. A known-vulnerable dependency is the security review's finding; report it, do not fix it here.
