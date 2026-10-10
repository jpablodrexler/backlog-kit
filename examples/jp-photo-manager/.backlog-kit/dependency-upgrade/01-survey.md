# Survey commands and special packages
Read when: every run

## 1. Backend Survey (Maven)

```bash
cd JPPhotoManagerWeb/backend
mvn versions:display-dependency-updates
mvn versions:display-plugin-updates
mvn dependency:analyze   # or: bash scripts/dead-code-report.sh for a dated snapshot under docs/reports/dead-code/
```

The `dependency:analyze` run is a useful pre-check, not a strict
prerequisite: a dependency the survey lists as outdated but
`dependency:analyze` also reports as genuinely unused is a candidate for
removal instead of upgrade — no point spending a bump on a package nothing
references anymore. Ignore every `spring-boot-starter-*` entry under
"Unused declared dependencies" though — that's expected noise from
bytecode-based analysis missing umbrella POMs with no classes of their
own, not a real finding (see `code-reviewer` skill §21.2).

Most library versions in this project are inherited from the
`spring-boot-starter-parent` BOM (see `java-developer` §1) rather than
pinned individually — check the parent POM version itself
(`spring-boot-starter-parent`) as the primary lever; a Spring Boot patch/minor
bump usually moves every managed dependency's version together in a tested,
compatible set. Only bump an individual `<dependency>` version directly when
it's declared outside the BOM (not managed by `spring-boot-starter-parent`).

🟡 Flag any dependency currently overridden to an older version via
`<dependencyManagement>` that the survey shows is now behind — verify
whether the override reason (check the POM for a comment) still applies
before removing it.

---

## 2. Frontend Survey (npm)

```bash
cd JPPhotoManagerWeb/frontend
npm outdated
npm audit --audit-level=high
npm run dead-code:report   # knip — see docs/reports/dead-code/ for the dated snapshot
```

Same pre-check reasoning as the backend survey above: a dependency
`npm outdated` lists but `dead-code:report` reports as genuinely unused
(and not one of `knip.jsonc`'s documented, name-resolved exceptions like
`@angular-devkit/build-angular`/`babel-plugin-istanbul`) is a candidate
for removal instead of upgrade.

**Angular packages are a special case.** Don't bump `@angular/*` packages
with a raw `npm install <pkg>@latest` — Angular major versions ship
migration schematics that codemod breaking changes (standalone-components
migration, control-flow syntax, etc.). Use the Angular CLI's own updater
instead, which also validates that the whole `@angular/*` family stays on
matching versions:

```bash
npx ng update                     # lists available updates, including peer-dependency-safe ordering
npx ng update @angular/core @angular/cli   # apply one major step at a time
```

Angular's own guidance is to upgrade one major version at a time (not skip
versions) — if `npm outdated` shows Angular is more than one major behind,
plan multiple sequential `ng update` passes, each with its own test run
(§4), rather than jumping straight to latest.

**`cypress`** is also a plain npm devDependency (not wired through `ng
update`) — bump it independently and re-run `npm run test` (component
suite) and `npm run test:e2e` (E2E suite) to confirm both still work; a
Cypress major can change config/CLI flags, and its Angular Component
Testing preset (`@angular-devkit/build-angular`, kept only for that
preset — see `angular-developer` §16) may need a matching bump too.
