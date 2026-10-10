# Apply and test groups
Read when: applying bumps (the groups and the command that verifies each)

## 4. Apply & Test, In Groups

1. **Group 1 — root devDependency** (`supabase` CLI patch/minor). Then:
   ```bash
   npx supabase --version
   ```
   (there's no automated test suite for the root package — a version check
   plus a manual `db pull`/`db push` sanity check if either command's
   behavior is in question is the practical verification here.)
2. **Group 2 — frontend patch/minor** (`npm update`, or `ng update` for any
   `@angular/*` minor, plus any plain-npm package like
   `@supabase/supabase-js`/`cypress` if only a minor/patch is available).
   Then:
   ```bash
   cd frontend && npm run test && npm run build
   ```
3. **Group 3+ — each approved major bump, one at a time**, its own test run
   immediately after. For an `@angular/core` major, skim the official
   Angular update guide (angular.dev's "Update Angular" tool output) for
   that specific version jump before applying — don't rely on the test
   suite alone to catch a removed API the tests don't happen to exercise.
   For a `@supabase/supabase-js` major, skim its changelog for renamed
   methods on `auth`/the query builder, since every `core/*.service.ts`
   file calls into that API directly with no adapter layer in between.
