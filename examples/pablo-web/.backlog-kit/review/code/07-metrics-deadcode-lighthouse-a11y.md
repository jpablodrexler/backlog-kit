# Code Reviewer — Dead Code, Lighthouse & Accessibility Audits
Read when: a metrics sweep touching unused code, route performance or accessibility

## 18. Dead Code

Every full-codebase sweep also gets an unused-code pass, via `knip`
(configured in `frontend/knip.jsonc` — see that file's comments for why
Cypress config/spec files and a handful of name-resolved devDependencies
need explicit entries/ignores on this Angular + Cypress hybrid project
before the tool's findings are trustworthy). This is the automated
counterpart to the "reuse/simplification" concerns the `/code-review`
command's own description calls out — an unused export or a dependency
nothing imports anymore is exactly that, just invisible to a manual read
of any single file since the *absence* of a reference elsewhere is what
makes it dead.

Run from `frontend/`:

```
npx knip
```

(or `npm run dead-code:report` for a dated snapshot under
`docs/reports/dead-code/`, split into unused files/exports/types/
dependencies/unlisted-dependencies — better for a full-codebase sweep than
a scoped review, since a single changed file rarely reveals whether its
exports are used *elsewhere*).

🟡 Flag an unused file — never imported from any entry point (`main.ts`,
a route's `loadComponent`, a `.cy.ts`/E2E spec). Confirm it's genuinely
dead (not, say, a script invoked standalone via `node <path>` that
`knip.jsonc` hasn't been told about yet) before recommending deletion.

🟡 Flag an unused exported symbol (function, const, type/interface) —
either it should be un-exported (module-private) or, if nothing in the
codebase needs it anymore, deleted outright per this project's own
"don't leave half-finished implementations" convention.

🟡 Flag an unused `dependencies`/`devDependencies` entry in `package.json`
— dead weight in the install and a wider (if unused) attack surface for
`security-reviewer` §1's vulnerability scan to worry about. Before
flagging, check `knip.jsonc`'s `ignoreDependencies` list and comments —
several devDependencies here are real but resolved by *name* rather than
`import`/`require` (e.g. `@angular-devkit/build-angular`, needed only to
satisfy Cypress's webpack-based Angular preset — see
`cypress-unit-test-developer` §1) and are already excluded for that
reason; don't re-flag those.

🟢 Flag an `unlisted` dependency (imported in source but only present
transitively, not declared directly in `package.json`) as a suggestion —
it works today only because some other direct dependency happens to pull
it in, which is fragile across dependency-tree changes.

---

## 19. Performance & Accessibility (Lighthouse)

Scoped narrowly today: `npm run lighthouse:report` (self-builds the
production bundle and audits it — see `frontend/scripts/lighthouse-report.mjs`)
only covers `/login` and `/register`, the two routes reachable without an
authenticated Supabase session. There's no equivalent to the mocked E2E
tier's `seedSession()` trick for Lighthouse, so this doesn't run against
any authenticated route yet — keep that gap in mind rather than treating a
clean report as whole-app coverage.

Run from `frontend/`:

```
npm run lighthouse:report
```

Writes a dated snapshot to `docs/reports/lighthouse/` — Performance,
Accessibility, Best Practices, and SEO scores (0–100) for each scanned
route, plus every failed accessibility audit by name.

🟡 Flag any accessibility audit failure on a route touched by the reviewed
change — Optimus UI components don't guarantee WCAG compliance for free, and
this is the only automated a11y signal this project has.

🟢 A performance/SEO score regression is worth a passing mention (note the
before/after numbers if both are available) but isn't a hard gate the way
§15/§16's thresholds are — there's no established baseline yet for either
score.

---

## 20. Deep Accessibility Audit (per-route, axe-core)

§19's Lighthouse score is a single aggregate number for `/login`/`/register`
only — useful as a trend line, but not actionable, and it never reaches an
authenticated route. `npm run a11y:report` is the deep complement: it drives
[cypress-axe](https://github.com/component-driven/cypress-axe)/
[axe-core](https://github.com/dequelabs/axe-core) against every
authenticated route (`/home`, `/tasks`, `/documents`, `/expense-types`,
`/expenses`, `/fixed-terms`, `/medications`, `/notifications`), reusing the
mocked E2E tier's session-seeding/request-stubbing machinery
(`cypress/support/mocked/seed-session.ts`) so it needs no live Supabase
project or credentials — see `frontend/cypress/a11y/a11y-audit.cy.ts` and
`frontend/scripts/a11y-report.js`. Deliberately its own third Cypress config
(`cypress.a11y.config.ts`) with the spec living at `cypress/a11y/` (a
sibling of `cypress/e2e/`, not a child of it) so it can never be picked up by
`npm run test:e2e` or `npm run test:e2e:mocked`'s own `specPattern`s.

§16's code-coverage gate only proves a line *executed* during the test
suite, not that any test would actually notice if its behavior changed —
a line can be 100% covered by a test that calls it and asserts nothing
meaningful about the result. Mutation testing closes that gap: StrykerJS
(`@stryker-mutator/core`, configured in `frontend/stryker.conf.json`)
systematically rewrites small pieces of a target file (flips a `<` to
`<=`, negates a condition, swaps a `&&` for `||`, changes a string/number
literal, etc.) one at a time and re-runs the test suite against each
mutated copy. A mutant that makes a test fail was **killed** — proof the
suite would catch that exact regression. A mutant where every test still
passes **survived** — the mutated line is covered, but nothing actually
asserts on it.

Cypress Component Testing has no native Stryker test-runner plugin (only
Jest/Mocha/Karma/Jasmine are officially supported), so this project uses
Stryker's **command runner** instead: each mutant re-runs
`npm run test:mutation-scope`, a deliberately narrow `cypress run
--component --spec "..."` invocation covering only the `.cy.ts` files that
actually exercise the mutated source (not the whole 50+-spec suite) — even
so, one full Cypress process launch per mutant is still slow (roughly a
minute each on a quiet machine, more under load), so `stryker.conf.json`'s
`mutate` list is deliberately narrow — today just the four pure
`core/*.util.ts` files with real branching (`date-format.util.ts`,
`iso-date.util.ts`, `translate.util.ts`, `subtask-progress.util.ts`), not
the whole `frontend/src/app` tree. Broader business-logic candidates (the
expense dashboard's chart-config builders, the meatier `*.service.ts`
files) were deliberately left out of this first pass — see that file's
`mutate` array for the current, authoritative scope, and widen it
incrementally rather than assuming it already covers those files.

Run from `frontend/`:

```
npm run a11y:report
```

(manages its own `ng serve` dev server lifecycle — no `start-server-and-test`
wrapper needed, unlike the E2E-run reports in §19's neighborhood). Writes a
dated snapshot to `docs/reports/a11y/` — total violation count broken down
by impact level (critical/serious/moderate/minor), then per route: rule ID,
impact, description, affected element count, help URL, and the affected
selectors.

🟡 Flag any accessibility violation on a route touched by the reviewed
change, same severity as §19's Lighthouse a11y flag — this is report-only
(`cy.checkA11y(..., skipFailures: true)`), not a CI gate, so treat a finding
as something to fix, not something already blocking the build.

🟢 Violation counts can shift slightly between runs of `npm run a11y:report`
— `ng serve`'s on-demand compilation of each lazy-loaded route's chunk means
the exact DOM state axe sees on a route's first visit can vary run to run.
Don't chase exact-count parity between two reports; treat a rule that shows
up consistently (e.g. a missing `<h1>` or landmark region) as the real
finding.

---
