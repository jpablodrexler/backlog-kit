# Apply and test groups
Read when: applying bumps (the groups and the command that verifies each)

## 4. Apply & Test, In Groups

1. **Group 1 — backend patch/minor**, applied via the parent POM bump plus
   any individually-managed dependencies from §1. Then:
   ```bash
   cd JPPhotoManagerWeb/backend && mvn clean test
   ```
2. **Group 2 — frontend patch/minor** (`npm update`, or `ng update` for any
   `@angular/*` minor). Then:
   ```bash
   cd JPPhotoManagerWeb/frontend && npm test && npm run lint && npm run build:prod
   ```
3. **Group 3+ — each approved major bump, one at a time**, its own test run
   immediately after. For a Spring Boot major/minor jump, also skim the
   official release notes' "breaking changes"/migration guide section before
   applying — don't rely on the test suite alone to catch a removed
   auto-configuration the tests don't happen to exercise.

If a group's test run fails, narrow it down within that group — the goal is
to land as much of the safe upgrade as possible, not to give up on the first
failure.
