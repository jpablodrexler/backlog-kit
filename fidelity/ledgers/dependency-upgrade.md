kit: extras/dependency-upgrade
sub: JPPhotoManagerWeb/docs/backlog => <backlog>
sub: docs/backlog => <backlog>
sub: JPPhotoManagerWeb/docs/reports => <reports>
sub: docs/reports => <reports>

PARAM | name: dependency-upgrade description: > Routine dependency-upgrade wor | description rewritten stack-free (TRIGGER structure kept); `scope` removed, `version` is the kit's (D30)
PARAM | Bump outdated Maven and npm dependencies, verify nothing broke, and le | second project's variant of this text; the kit follows the first project
DROPPED | 1. **Scope.** Backend only, frontend only, or both — ask if not specif | second project's variant of this text; the kit follows the first project
PARAM | 3. **Survey.** Run the discovery commands in §1/§2 below and build a l | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | 4. **Decide scope of the bump** (§3): patch and minor bumps apply by d | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | 5. **Apply in groups, testing after each group** (§4) — not all depend | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | 6. **Cross-check against `security-reviewer` §1** (§5) — confirm the b | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | 7. **Report** (§6): what was bumped, what was left for the user to dec | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | 8. **Never commit.** Leave everything staged/unstaged in the working t | second project's variant of this text; the kit follows the first project
PARAM | ## 1. Backend Survey (Maven) | second project's variant of this text; the kit follows the first project
DROPPED | cd JPPhotoManagerWeb/backend | second project's variant of this text; the kit follows the first project
DROPPED | mvn versions:display-dependency-updates | second project's variant of this text; the kit follows the first project
DROPPED | mvn versions:display-plugin-updates | second project's variant of this text; the kit follows the first project
DROPPED | mvn dependency:analyze # or: bash scripts/dead-code-report.sh for a da | second project's variant of this text; the kit follows the first project
DROPPED | The `dependency:analyze` run is a useful pre-check, not a strict prere | second project's variant of this text; the kit follows the first project
DROPPED | Most library versions in this project are inherited from the `spring-b | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag any dependency currently overridden to an older version via `<d | second project's variant of this text; the kit follows the first project
DROPPED | ## 2. Frontend Survey (npm) | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | cd JPPhotoManagerWeb/frontend | second project's variant of this text; the kit follows the first project
DROPPED | npm outdated | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | npm audit --audit-level=high | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | npm run dead-code:report # knip — see <reports>/dead-code/ for the dat | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | Same pre-check reasoning as the backend survey above: a dependency `np | second project's variant of this text; the kit follows the first project
DROPPED | **Angular packages are a special case.** Don't bump `@angular/*` packa | second project's variant of this text; the kit follows the first project
DROPPED | npx ng update # lists available updates, including peer-dependency-saf | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | npx ng update @angular/core @angular/cli # apply one major step at a t | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | Angular's own guidance is to upgrade one major version at a time (not | second project's variant of this text; the kit follows the first project
DROPPED | **`cypress`** is also a plain npm devDependency (not wired through `ng | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | 🔴 Never apply a major-version bump to `spring-boot-starter-parent`, `@ | second project's variant of this text; the kit follows the first project
PARAM | 🟢 A patch/minor bump to a leaf dependency with no direct API usage in | second project's variant of this text; the kit follows the first project
PARAM | Don't bump every dependency and run the suite once at the end — if it | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | 1. **Group 1 — backend patch/minor**, applied via the parent POM bump | second project's variant of this text; the kit follows the first project
DROPPED | cd JPPhotoManagerWeb/backend && mvn clean test | second project's variant of this text; the kit follows the first project
DROPPED | 2. **Group 2 — frontend patch/minor** (`npm update`, or `ng update` fo | second project's variant of this text; the kit follows the first project
DROPPED | cd JPPhotoManagerWeb/frontend && npm test && npm run lint && npm run b | second project's variant of this text; the kit follows the first project
DROPPED | 3. **Group 3+ — each approved major bump, one at a time**, its own tes | second project's variant of this text; the kit follows the first project
PARAM | If a group's test run fails, narrow it down within that group (revert | second project's variant of this text; the kit follows the first project
PARAM | After applying bumps, re-run the vulnerability scan from `security-rev | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | cd JPPhotoManagerWeb/backend && mvn org.owasp:dependency-check-maven:c | second project's variant of this text; the kit follows the first project
DROPPED | cd JPPhotoManagerWeb/frontend && npm audit --audit-level=high | second project's variant of this text; the kit follows the first project
PARAM | If a CVE that motivated this upgrade session is still present, the fix | second project's variant of this text; the kit follows the first project
PARAM | - **Applied** — each bumped dependency, old → new version, grouped by | second project's variant of this text; the kit follows the first project
PARAM | - **Skipped (major, needs approval)** — every major-version bump found | second project's variant of this text; the kit follows the first project
PARAM | name: dependency-upgrade description: > Routine dependency-upgrade wor #2 | description rewritten stack-free (TRIGGER structure kept); `scope` removed, `version` is the kit's (D30)
PARAM | Bump outdated npm dependencies in both `package.json` files this repo | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | 1. **Scope.** Root (`supabase` CLI) only, frontend only, or both — ask | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | 8. **Never commit.** Leave everything staged/unstaged in the working t #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | ## 1. Root Survey (the `supabase` CLI devDependency) | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | The root `package.json` has exactly one devDependency: `supabase` (the | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🟡 Flag a `supabase` CLI version more than one major behind latest — th | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | The `dead-code:report` run is a useful pre-check, not a strict prerequ | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | **Angular packages are a special case.** Don't bump `@angular/*` packa #2 | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | Angular's own guidance is to upgrade one major version at a time — if | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | **`@supabase/supabase-js` is not covered by `ng update`** — it's a pla | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🔴 Never apply a major-version bump to `@angular/core`, `@supabase/supa | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | 🟢 A patch/minor bump to a leaf dependency with no direct API usage in #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | 1. **Group 1 — root devDependency** (`supabase` CLI patch/minor). Then | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | npx supabase --version | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | (there's no automated test suite for the root package — a version chec | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 2. **Group 2 — frontend patch/minor** (`npm update`, or `ng update` fo #2 | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | cd frontend && npm run test && npm run build | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 3. **Group 3+ — each approved major bump, one at a time**, its own tes #2 | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | npm audit --audit-level=high # root | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | cd frontend && npm audit --audit-level=high | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | If a CVE that motivated this upgrade session is still present, the fix #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | - **Applied** — each bumped dependency, old → new version, grouped by #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
