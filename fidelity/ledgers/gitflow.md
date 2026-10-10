kit: skills/gitflow
sub: JPPhotoManagerWeb/docs/backlog => <backlog>
sub: docs/backlog => <backlog>

PARAM | name: gitflow description: >- Encapsulates the Gitflow workflow for th | description: the project and its tools are not named (no package.json, no e2e-suite); it names the release phases folder instead; `author` removed, `version` is the kit's
PARAM | Use `fix/` for a bug fix, `doc/` for a documentation-only change (`JPP | the `skill/` example names this plugin's `docs-sync` instead of a project skill; project docs paths are generic
PARAM | 2. `git checkout <base>` | second project's variant (it has no develop bootstrap step, so steps are numbered one less); the kit follows the first project, which bootstraps `develop`
DROPPED | 2. **Run the maintained E2E suite** (see the `e2e-suite` skill) before | project-specific: replaced by 'run the project's release phases' (D28)
PARAM | 3. Push the branch (including the changelog commit from step 1, if the | step numbers shift by one: the version bump and the e2e gate are project release phases (D28)
PARAM | 4. Build the PR description (see "Writing the PR description" below) — | step numbers shift by one (D28); the test-plan note names the release phases' checks instead of the e2e suite
PARAM | Note in the summary: once the PR into `main` is merged, run the **tag | the changelog entry (and whatever release phases committed) is what is already merged; step numbers per D28
PARAM | 1-2. Run `python3 .claude/skills/gitflow/scripts/list_merge_candidates | script path: the script ships next to the skill, relative to its base directory
PARAM | - **Never push a `release/`/`hotfix/` branch or open its PRs while the | reworded: a blocked project release phase (D28) replaces the e2e-suite failure
PARAM | name: gitflow description: >- Encapsulates the Gitflow workflow for pa | description: the project and its tools are not named (no package.json, no e2e-suite); it names the release phases folder instead; `author` removed, `version` is the kit's
PARAM | Use `fix/` for a bug fix, `doc/` for a documentation-only change (`doc | the `skill/` example names this plugin's `docs-sync` instead of a project skill; project docs paths are generic
DROPPED | 1. Bump the app version on the current `release/`/`hotfix/` branch, us | project-specific (D28): the version bump is a project release phase (`.backlog-kit/release/`), e.g. `examples/pablo-web`
DROPPED | 3. **Run the maintained E2E suite** (see the `e2e-suite` skill) before | project-specific (D28): the e2e gate is a project release phase
DROPPED | - **If it exists**: invoke the `e2e-suite` skill (or run `cd frontend | project-specific (D28): part of the e2e gate, now a project release phase
DROPPED | - **If it doesn't exist**: the suite can't run without a live test acc | project-specific (D28): part of the e2e gate, now a project release phase
PARAM | 4. Push the branch (including the version-bump commit from step 1 and | step numbers shift and the version-bump commit is a release-phase commit (D28)
PARAM | 5. Build the PR description (see "Writing the PR description" below) — | step numbers shift and the version-bump/e2e notes are generic (D28)
PARAM | Note in the summary: once the PR into `main` is merged, run the **tag #2 | the changelog entry (and whatever release phases committed) is what is already merged; step numbers per D28
PARAM | - **Never push a `release/`/`hotfix/` branch or open its PRs while the #2 | reworded: a blocked project release phase (D28) replaces the e2e-suite failure
