# Survey commands and special packages
Read when: every run

## 1. Root Survey (the `supabase` CLI devDependency)

```bash
npm outdated
npm audit --audit-level=high
```

The root `package.json` has exactly one devDependency: `supabase` (the CLI,
run via `npx` per `CLAUDE.md` — never installed globally). A bump here is
almost always safe to apply automatically (it's a CLI tool, not a runtime
dependency of the shipped app), but still run `npx supabase --version`
after bumping and confirm `npx supabase db pull`/`db push` still behave as
documented in `CLAUDE.md` before calling it done — a CLI major version can
change command flags or migration file format.

🟡 Flag a `supabase` CLI version more than one major behind latest — the
CLI and the remote platform APIs it talks to evolve together, and a very
stale CLI can eventually stop working against the current hosted Supabase
API version.

---

## 2. Frontend Survey (npm)

```bash
cd frontend
npm outdated
npm audit --audit-level=high
npm run dead-code:report   # knip — see docs/reports/dead-code/ for the dated snapshot
```

The `dead-code:report` run is a useful pre-check, not a strict
prerequisite: a dependency `npm outdated` lists but `dead-code:report`
reports as genuinely unused (not one of `frontend/knip.jsonc`'s documented,
name-resolved exceptions) is a candidate for removal instead of upgrade —
no point spending a bump on a package nothing imports anymore. Cross-check
`knip.jsonc`'s `ignoreDependencies` comments before assuming a flagged
dependency is truly dead, though — several (`@angular-devkit/build-angular`,
`babel-plugin-istanbul`) are resolved by name by other tooling, not import,
and are already excluded there for that reason.

**Angular packages are a special case.** Don't bump `@angular/*` packages
with a raw `npm install <pkg>@latest` — Angular major versions ship
migration schematics that codemod breaking changes. Use the Angular CLI's
own updater instead, which also validates that the whole `@angular/*`
family stays on matching versions:

```bash
npx ng update                     # lists available updates, including peer-dependency-safe ordering
npx ng update @angular/core @angular/cli   # apply one major step at a time
```

Angular's own guidance is to upgrade one major version at a time — if
`npm outdated` shows Angular is more than one major behind, plan multiple
sequential `ng update` passes, each with its own test run (§4).

**`@supabase/supabase-js` is not covered by `ng update`** — it's a plain
npm package, bump it with `npm install @supabase/supabase-js@latest` and
re-run the full test suite plus a manual sign-in/task-list smoke check
(this package's API surface — `auth.signInWithPassword`, `.from().select()`,
etc. — is what every `core/*.service.ts` file is built directly on top of,
so a breaking change here has no schematic to codemod it away).

**`cypress`** is also a plain npm devDependency (not wired through `ng
update`) — bump it independently and re-run `npm run test` (component
suite) and `npm run test:e2e` (E2E suite) to confirm both still work; a
Cypress major can change config/CLI flags, and its Angular Component
Testing preset (`@angular-devkit/build-angular`, kept only for that
preset — see `angular-developer` §16) may need a matching bump too.
