---
name: dependency-upgrade
description: Routine, user-driven dependency upgrade cycle for any stack. Surveys what is outdated and what is vulnerable with the project's own package manager, classifies each dependency as patch, minor or major with changelog risk notes, proposes groups (a BOM or parent first, a framework family together), applies one group at a time (asking first), runs every configured verification gate after each group, rolls back a group that fails from a snapshot kept inside the git directory, re-runs the vulnerability check at the end, and writes a dated report. Majors only on the user's explicit pick, never mixed with other bumps; a group whose tool rewrites source files is declared first because it cannot be rolled back. TRIGGER when asked to upgrade dependencies, bump package versions, check for outdated packages, or do routine dependency maintenance. A known-vulnerable dependency is a security finding, not this skill's job to fix unasked.
license: MIT
metadata:
  version: "0.2"
---

Run one routine upgrade cycle over the project's own dependencies and leave the result uncommitted in the working tree for the user to review. `<reports_dir>` comes from `[paths]` in `.backlog-kit.toml` (default `docs/reports`); gates come from `[[gates]]` in the same file. With no file the defaults apply.

**Input**: optionally a scope (one manifest or folder, one ecosystem, or "everything"). If the repo has several manifests and no scope was given, ask which to cover.

This skill is the routine cadence: keep things current, prove nothing broke, and confirm the vulnerability picture did not get worse. A dependency with a known vulnerability is a security finding (the project's security review owns it, and it may justify an out-of-cycle bump). This skill surveys and re-checks advisories (section 6) and reports them; it does not turn the run into a security fix, and it does not mark an upgrade complete if an advisory that motivated it is still present.

## 1. Detect the package manager (only what the project already uses)

Detect from files that already exist. Use only a tool the project demonstrably uses, and never introduce one, suggest switching, or run a command for an ecosystem with no manifest in the repo. If the project uses something not in the table, ask the user for its survey/upgrade/install/audit commands.

| Detected by | Survey (read-only) | Upgrade one package | Install from lockfile (no rewrite) | Vulnerability check (read-only) |
| --- | --- | --- | --- | --- |
| `package-lock.json` (npm) | `npm outdated` | `npm install <pkg>@<version>` (writes `^<version>`; add `--save-exact` if the manifest pins exact versions, and keep a `~` range by editing the manifest instead) | `npm ci` | `npm audit` |
| `pnpm-lock.yaml` (pnpm) | `pnpm outdated` | `pnpm add <pkg>@<version>` | `pnpm install --frozen-lockfile` | `pnpm audit` |
| `yarn.lock` (yarn) | classic: `yarn outdated`. Berry has no built-in non-interactive listing (`upgrade-interactive` is interactive), so ask the user how to get the list | `yarn add <pkg>@<version>` | classic `yarn install --frozen-lockfile`; berry `yarn install --immutable` | classic `yarn audit`; berry `yarn npm audit` |
| `requirements*.txt` / `pyproject.toml` with pip | `pip list --outdated` (project venv) | edit the pin, then `pip install -r <file>` | `pip install -r <file>` | `pip-audit` only if already installed, else say it is unavailable |
| `uv.lock` (uv) | `uv tree --outdated` | within the declared range: `uv lock --upgrade-package <pkg>`; a major needs the constraint edited in `pyproject.toml` first, then `uv lock` | `uv sync --frozen` | `pip-audit` only if installed |
| `poetry.lock` (poetry) | `poetry show --outdated` | `poetry update <pkg>` (in range) or `poetry add <pkg>@<version>` for a major | `poetry install --sync` | `pip-audit` only if installed |
| `pom.xml` (Maven) | `mvn versions:display-dependency-updates` (only if the plugin is configured or the user agrees) | edit the version or the property that holds it by hand. Do not use `versions:use-latest-versions`: it ignores the version you chose and leaves `pom.xml.versionsBackup` files. If the versions plugin is already used, `versions:use-dep-version -Dincludes=<g:a> -DdepVersion=<v> -DgenerateBackupPoms=false` pins one | `mvn -B dependency:resolve` / the build | `mvn org.owasp:dependency-check-maven:check` only if configured; else unavailable |
| `build.gradle(.kts)` (Gradle) | `./gradlew dependencyUpdates` (only if that plugin is configured) | edit the version in the build file / version catalog | `./gradlew build --refresh-dependencies` only when needed | unavailable unless the project configures a scanner |
| `*.csproj` / `*.sln` (dotnet) | `dotnet list package --outdated` | `dotnet add <project> package <pkg> --version <version>` | `dotnet restore --locked-mode` when `packages.lock.json` exists (a plain `dotnet restore` can rewrite it) | `dotnet list package --vulnerable` |
| `go.mod` (Go modules) | `go list -u -m all` | `go get <module>@<version>` then `go mod tidy` | `go mod download` | `govulncheck ./...` only if installed |
| `Cargo.lock` / `Cargo.toml` (Cargo) | `cargo outdated` (only if installed) or `cargo update --dry-run` | in range: `cargo update -p <crate>`; a major needs `Cargo.toml` edited first, then `cargo update -p <crate>` | `cargo fetch --locked` | `cargo audit` only if installed |

Notes:
- Run every command from the manifest's own folder, inside the project. Never use a global install, `sudo`, or a system package manager, and never install a missing tool (for example a plugin that provides the outdated listing): say it is unavailable and ask the user how to get the list.
- **Yarn flavour**: berry if `.yarnrc.yml` exists or `package.json`'s `packageManager` names yarn 2 or later; classic otherwise. If neither tells, ask.
- **Workspaces** (a `workspaces` field, `pnpm-workspace.yaml`, a Maven multi-module parent, a Cargo workspace): the lockfile is shared. Survey from the root, treat the lockfile as one file to snapshot, and apply with the manager's own workspace selector. A bump in one member can change another's resolution, so run the gates for every member that depends on it.
- A tool that reports nothing is not proof of nothing: if a vulnerability check is unavailable, say "not checked" in the report, never "clean".
- Network access to the registry is allowed only to survey, upgrade, install and audit this project's own dependencies. Nothing else may use the network.
- Some tools list only what is outdated within the declared range, others the absolute latest. Note which the survey shows, and check the manifest's declared range when it matters.

## 2. Preconditions

1. **Gates.** Read `[[gates]]` from `.backlog-kit.toml`. If none are configured, say so plainly and ask with AskUserQuestion which commands verify the project (tests, build, lint) before applying anything. Do not apply a single bump without a way to verify it; if the user declines, stop after the survey and report. A gate with `ask_before` is asked about before each run (section 5), exactly as the work skills do.
2. **Branch and working tree.** Stay on the current branch; this skill never switches branches. If the current branch is the base branch (`[git] base_branch`, or whichever of `main`, `master`, `develop`, `trunk` it is on), say so and recommend starting a topic branch first (ask for `gitflow`'s `start` by name; never invoke it yourself); ask whether to continue anyway. If manifests, lockfiles or source files already have uncommitted changes, tell the user, because a rollback restores to the state before the group and they should know what that state includes. Ask whether to continue.
3. **Baseline.** Run the gates once before changing anything so a failure already present is not blamed on the upgrade, and run the vulnerability check once to record the advisories already present. A failure matching a gate's `known_failures` pattern is reported as KNOWN FAILURE and is not caused by the upgrade. Any other baseline failure: show it and ask whether to continue.
4. **Snapshot location.** Before each group, copy every file the group will touch into `<git-dir>/backlog-kit/dependency-upgrade/snapshots/<YYYY-MM-DD>/group-<n>/`, keeping relative paths. `<git-dir>` is the output of `git rev-parse --git-dir`: a plain file copy into the repository's own git directory, so the snapshot never shows in `git status`, is never tracked and cannot collide with the project's tooling. Nothing is written outside the repository. Delete the snapshot folder when the run ends, after the report is written.

## 3. Survey and classify

Run the survey command(s) for the detected ecosystems. For each outdated dependency record: name, current, wanted, latest, and direct or transitive. Classify by the leftmost non-zero version component that changes: **patch**, **minor** or **major** (for `0.x` versions a minor bump is treated as potentially breaking: mark it "minor (0.x, treat like major)"). Add a risk note for anything beyond a patch, from the changelog or release notes when available (the package's own changelog file, or the registry page); if none is reachable, write "no changelog found" rather than guessing. Say which bumps touch a dependency the code uses directly and heavily and which are leaf packages with no direct use: the split of automatic versus asked-about stays by bump type, but the report notes the difference.

**Version-managing parents come first.** Where a dependency's version is managed by a BOM, a parent project, a platform or a version catalog (a Maven parent or BOM, a Gradle platform, a framework's starter parent), that parent is the primary lever: bump it as its own group, and leave the individually managed dependencies it controls alone. Only dependencies declared outside the parent's management are bumped one by one. A parent's major or minor jump gets its release notes' migration or breaking-changes section read before the user is asked.

**Unused dependencies.** Flag a dependency that nothing in the code imports as a removal candidate rather than spending a bump on it, but do not remove it in this run. Be careful: some packages are resolved by name by other tooling (a build plugin, a test-runner preset, a type-definition package) and never imported, so check the project's own unused-dependency report and its documented exceptions before calling one dead. Say "candidate", never "unused".

Also note deliberate version pins (a comment, an exact version, an `overrides`/constraint entry): list them as skipped with the reason, and do not change them unasked.

Show the user the table before proposing anything.

## 4. Propose groups

- **Patch and minor** bumps are proposed by default, grouped by blast radius: a version-managing parent first; then dev tooling, test tooling, runtime libraries, and a framework family that must move together (packages versioned in lockstep) as one group.
- **Major** bumps are listed but never applied unless the user explicitly picks that package. Each approved major is its own group. **Never mix a major with other bumps in one group**, and never put two majors in one group. A major bump to a framework, the data-access client or the platform CLI the project is built on gets its release notes read first.
- Move one major version at a time, never skipping versions.
- **Declare source-rewriting groups.** If a group would use a tool that rewrites source files (a framework's migration tool, a codemod, a `--fix` option), mark it so in the proposal: this skill cannot roll such a group back (section 5). Prefer the ecosystem's own migration tool for frameworks that ship one, because it also keeps a framework family consistent, but say what it will touch.
- Keep groups small enough that a failure points at a short list.

Present the groups with AskUserQuestion: which groups to apply, and which majors (if any) to attempt. Nothing is applied before this answer.

## 5. Apply one group at a time

For each approved group, in order:

1. Ask with AskUserQuestion before applying it (for a major, name the package, the old and new version and the risk note; for a source-rewriting group, say it cannot be rolled back by this skill and recommend committing first by asking for `gitflow` (never invoke it yourself) so the tree is recoverable). "Skip" and "Stop here" are choices.
2. Take the snapshot (section 2.4). For a source-rewriting group, also record `git status --porcelain` so the files it changed can be named afterwards.
3. Apply the group with the table's upgrade command, then the lockfile-respecting install (for example `npm ci`) so the tree matches the lockfile. Lockfile discipline: only the upgrade command itself may rewrite tracked manifest and lockfile files. Do not use a plain install command that rewrites the lockfile as a way to fix things, and do not touch tracked files for any other reason.
4. Run every gate under `[[gates]]` in order, each with its `run` command from its `cwd`, within its `timeout_minutes`. Ask a gate's `ask_before` question first ("Run it" / "Skip it this run"); a skipped gate is `NOT RUN`, never silently dropped. A failure matching a `known_failures` pattern is reported as KNOWN FAILURE and the gate counts as passed apart from those tests. A gate that cannot run here is `NOT RUN (environment): <reason>`. Never skip, delete or weaken a test to get green.
5. **Pass** (all gates pass apart from known failures): keep the group, record it, move to the next.
6. **Fail** (a new failure): first decide whether it is caused by the bump or by the environment. If caused by the bump, you may make one small, obvious fix to project code or tests that the new version requires (a renamed import, a changed option) only if the user's pick covers it; **before editing any file, copy it into the group's snapshot folder**, so the edit is rollbackable too. If the group still fails, **roll back**:
   - *Manifest-and-lockfile group* (no source-rewriting tool, no fix beyond files you snapshotted): copy every file back from the snapshot, re-run the lockfile-respecting install, and re-run the gates once to confirm the tree is back to the baseline. Record the group as ROLLED BACK with the failing gate and test names. If the group had several packages, offer to retry it split in two, as a new group with its own question.
   - *Source-rewriting group*: do not attempt a partial restore. Restoring only the manifests would leave source changed for versions that are gone, which is worse than either end state. Stop, list exactly which files the tool changed (compare `git status --porcelain` with the recorded one), record the group as FAILED, NOT ROLLED BACK, and tell the user how to undo it themselves (for example review and `git restore` the listed files, or discard the branch). Ask whether to continue with other groups only after that.

Never run a destructive git command (`git checkout`, `git reset`, `git stash`, `git clean`) to roll back. Never leave a half-applied group without saying so.

## 6. Re-check vulnerabilities

After the last group, run the vulnerability check again (the same commands as the baseline) for every ecosystem covered. Compare:

- Advisories present at the baseline and gone now: say which bump resolved them.
- Advisories still present: say why, if it can be told (the fixed version needs a major the user did not pick; the vulnerable package is transitive and needs an explicit override or constraint entry; no fixed version exists). Do not report the upgrade as complete for an advisory that motivated it until this is established one way or the other; an override or constraint is proposed to the user, not added.
- New advisories introduced by a bump: flag them prominently; the group that introduced them is named.
- A check that could not run: "not checked", never "clean".

This is a re-check and a report. Fixing a vulnerability the cycle did not cause is the security review's work.

## 7. Report

Write `<reports_dir>/dependency-upgrade/DEPENDENCY_UPGRADE_<YYYY-MM-DD>.md` (create the folder if needed; if the file exists use `-2`, `-3` for the same day). Contents:

- **Header**: date, the current branch, package manager(s) and manifests covered, the gates run.
- **Applied**: each dependency, old to new, its bump type, grouped as applied; note direct-use versus leaf where it matters.
- **Rolled back / failed**: each group, the failing gate and tests, the likely cause, and for a source-rewriting group the files it changed and that it was NOT ROLLED BACK.
- **Skipped**: majors not picked (with risk notes), pinned dependencies, removal candidates (as candidates), anything not applied and why.
- **Gates**: per group, each gate's result, including every KNOWN FAILURE, NOT RUN and FAILED (environment) line. Never fold these into a plain pass.
- **Security**: the before and after comparison from section 6, including "not checked" where a check was unavailable.
- **Not verified**: what no gate covers, if the changed manifests belong to a folder with no gate.

Then tell the user plainly: nothing was committed, the changes are in the working tree on the current branch, which files changed (manifests, lockfiles and any source a tool rewrote), and the report path. Tell them to ask for `gitflow`, whose `commit` and `finish` publish the work after asking (never invoke it yourself).

---

## Guardrails

- **Never run `git commit`, `git push` or open a PR.** This skill edits manifests and lockfiles through the project's package manager, runs the project's gates and writes one report under `<reports_dir>/dependency-upgrade/`, plus a temporary snapshot inside the git directory; it never switches branches.
- Use only the package manager the project already uses. Never invent or install a tool, never install system packages, never use `sudo` or a global install. Package-manager commands run inside the project.
- Registry network access is for surveying, upgrading, installing and auditing the project's own dependencies only.
- Ask with AskUserQuestion before applying each group and before any major. Never apply a major unasked, and never mix a major with other bumps in one group.
- Never apply a bump without gates to verify it. Never skip, delete or weaken a test to get green, and never report a KNOWN FAILURE, NOT RUN or environment failure as a pass.
- Roll back a failing manifest-and-lockfile group exactly, from its snapshot. Never run a destructive git command to roll back; a group whose tool rewrote source is declared beforehand and, if it fails, reported with the files it changed instead of being half-restored.
- This skill is routine maintenance. A known-vulnerable dependency is the security review's finding; report it, do not fix it here.
