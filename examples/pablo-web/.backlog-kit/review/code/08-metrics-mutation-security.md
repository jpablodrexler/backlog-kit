# Code Reviewer — Mutation Testing, Secrets, Licenses & Dependency Vulnerabilities
Read when: a metrics sweep, or a change touching dependencies or committed secrets

## 21. Mutation Testing

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
npm run mutation:report
```

Writes a dated snapshot to `docs/reports/mutation/` — overall mutation
score, killed/survived/timeout/no-coverage counts, a per-file score table
(worst first), and a table of every surviving mutant's file/line/mutator/
replacement. This is a full Stryker run (can take significant wall-clock
time even at this narrow scope, since it's one full test-command
invocation per mutant) — expect it to run considerably longer than any
other report in this family, and treat a non-zero exit from
`npx stryker run` itself as informational (a low score is exactly the
finding this report exists to surface), not a crash — same tolerance
`code-coverage-report.js` already applies to a failing component run.

🟡 Flag a **survived mutant** on any file touched by the reviewed change.
It means: the mutated line/branch *is* reached by the test suite, but no
assertion actually depends on its specific behavior — the test would pass
identically whether the original or the mutated code ran. Fix by
tightening the test's assertions (assert the actual computed value, not
just "no error was thrown" or that some unrelated side effect happened),
not by trying to kill the mutant some other way. If the mutated line is
genuinely redundant (dead defensive code, an equivalent alternate
expression), it's fine to exclude it with a `// Stryker disable
next-line` comment instead — but confirm that first rather than assuming.

🟢 A survived mutant in a file *not* touched by the reviewed change is
worth a passing mention (it's pre-existing test-quality debt) but isn't
this review's responsibility to fix — note it and move on, the same way
§15/§16/§17's pre-existing findings outside the diff are handled.

🟢 Don't chase 100% — a mutation score gap on a trivial mutant (e.g. a
string literal inside a code comment, or a mutation Stryker's own
equivalent-mutant heuristics already suspect) isn't worth manufacturing a
test around. Focus on survived mutants that represent a real, plausible
regression a future change could introduce silently.

---

## 22. Secrets Scanning

`npm run secrets:report` (`frontend/scripts/secrets-scan-report.js`) scans
the whole repository — not just `frontend/` — with
[secretlint](https://github.com/secretlint/secretlint) for accidentally
committed API keys, private keys, tokens, and other high-confidence secret
patterns. Uses secretlint's `unix` output formatter deliberately, not
`json` — the json formatter dumps every scanned file's full unmasked
content alongside any findings, which is both slow and a real exposure
risk if that output is ever mishandled (this happened once during this
report's own development — see the script's own header comment). Every
credential-shaped file in this repo (`.e2e-credentials.json`) is excluded
via `.secretlintignore` at the repo root, on top of secretlint's own
`.gitignore` respect.

Run from `frontend/`:

```
npm run secrets:report
```

Writes a dated snapshot to `docs/reports/secrets-scan/` — file, line, rule,
and message for each finding.

🔴 Any finding here that turns out to be a real, live secret is a **stop
what you're doing** situation — rotate/revoke it immediately (not just
remove it from the file; git history still has it), then remove it from
the working tree.

🟢 A false positive (a placeholder value, a test fixture, a documentation
example) doesn't need a code change — scope an ignore rule to that specific
file/rule in `frontend/.secretlintrc.json` rather than either accepting the
noise on every future run or disabling the rule project-wide.

---

## 23. License Compliance

`npm run license:report` (`frontend/scripts/license-compliance-report.js`,
via [license-checker-rseidelsohn](https://github.com/RSeidelsohn/license-checker-rseidelsohn))
checks every resolved npm dependency's declared license, flagging the
copyleft family (GPL/AGPL/LGPL/SSPL/EUPL/CC-BY-SA/OSL/CPAL) and anything
with no resolvable license at all. A permissive license (MIT/ISC/
Apache-2.0/BSD/0BSD/Unlicense/CC0/...) is never flagged.

Run from `frontend/`:

```
npm run license:report
```

Writes a dated snapshot to `docs/reports/license-compliance/` — one row
per flagged package with its license and repository.

🟡 Flag a copyleft or unknown license on a **runtime** `dependencies` entry
(something actually shipped in the built app) — most flagged packages will
be devDependencies (build/test tooling never distributed with the app),
which doesn't need the same scrutiny regardless of license family.

🟢 `UNKNOWN` usually just means the package has no `license` field and no
detectable `LICENSE` file, not that it's actually unlicensed — worth a
quick check of the package's own repository before treating it as a real
problem.

---

## 24. Dependency Vulnerability (SCA)

`npm run sca:report` (`frontend/scripts/sca-report.js`, via `npm audit`)
checks every resolved npm dependency against npm's own advisory database.
Distinct from dependency-staleness (§ elsewhere in this skill and the
`dependency-upgrade` skill): staleness tracks *outdated* packages, this
tracks *vulnerable* ones — a package can be current and vulnerable, or
stale and perfectly safe.

Run from `frontend/`:

```
npm run sca:report
```

Writes a dated snapshot to `docs/reports/dependency-vulnerabilities/` —
one row per vulnerable package: severity, vulnerable range, whether a fix
is available, and the advisory title(s).

🔴 Flag any **critical/high** severity finding with a fix available and no
clear reason it hasn't been applied yet.

🟡 Flag a critical/high finding with no fix available yet — worth checking
whether the vulnerable code path is actually reachable in this app (many
advisories are in a devDependency's own build tooling, never shipped or
executed against untrusted input) before treating it as urgent.

🟢 Moderate/low findings are worth a passing mention, not a blocker.

---
