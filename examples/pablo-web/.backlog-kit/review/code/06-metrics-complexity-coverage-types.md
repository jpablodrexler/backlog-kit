# Code Reviewer — Cyclomatic Complexity, Code Coverage & Type Coverage
Read when: a metrics sweep, a coverage threshold, or `any` usage

## 15. Cyclomatic Complexity

Every reviewed scope gets a McCabe cyclomatic complexity pass, in addition
to the manual checklist above. Complexity is measured per function/method
(each starts at 1; +1 for each `if`, ternary, loop — `for`/`for-in`/
`for-of`/`while`/`do-while` —, `catch`, switch `case`, and short-circuit
operator — `&&`, `||`, `??`), the same rule ESLint's built-in `complexity`
rule uses. **Max allowed complexity is 15 per function.**

Don't count this by hand — run the checked-in analyzer from `frontend/`:

```
npm run complexity
```

(equivalent to `node scripts/cyclomatic-complexity.js src/app`, which walks
every non-test `.ts` file under a given directory via the TypeScript
compiler API — see `frontend/scripts/cyclomatic-complexity.js`). It exits
non-zero and lists every offending function (file, line, name, complexity)
when anything exceeds the threshold. For a scoped review (single file/PR),
either run it against the whole tree and filter the output to the changed
files, or pass the narrower directory directly, e.g.
`node scripts/cyclomatic-complexity.js src/app/expenses`.

🟡 Flag any function reported over complexity 15 — this is a maintainability
problem (deep, hard-to-test branching), not a correctness bug, so it's a
WARNING rather than CRITICAL, but it should be fixed: extract guard clauses,
split the function by responsibility, or replace a long `if`/`else if`
chain with a lookup table/strategy map. Note the reported complexity number
and location in the finding so a fix can be verified by re-running the
script.

🟢 A function in the 10–15 range is worth a passing mention if an obvious,
low-effort split exists, but isn't required to be flagged — the threshold
that matters is 15.

For a full-codebase sweep, also run `npm run complexity:report` — unlike
`npm run complexity`'s pass/fail gate, it writes a dated snapshot to
`docs/reports/complexity/` ranking every function by complexity and every
file by line count, so a file/function trending toward the threshold (but
not yet over it) is visible before it becomes an actual violation worth
flagging next time.

---

## 16. Code Coverage

Every reviewed scope gets a line-coverage pass, in addition to the manual
checklist above. **Minimum line coverage is 80%**, whether the check runs
over the whole frontend or is scoped to just the files a change touched.

Don't estimate this by eye — the coverage tooling is already wired
(`cypress-unit-test-developer` §15); this section only adds the enforced
threshold and how to scope the check.

Run from `frontend/` (collect coverage, then check the threshold):

```
npm run test:coverage
npm run coverage:check
```

`test:coverage` (`cypress run --component --env coverage=true`) re-runs the
Component Testing suite with `babel-plugin-istanbul` instrumentation active
and writes `html`/`lcov`/text-summary reports to `coverage/` (gitignored).
`coverage:check` (`nyc check-coverage`) reads the `lines`/`branches`/
`functions`/`statements` thresholds (80 each) from `.nycrc.json` and fails
(non-zero exit), naming the metric(s) that fell short, when any falls under
threshold.

For a **scoped review** (a single component, service, or feature directory
rather than the whole frontend), don't rely on the whole-project number —
narrow the check with `--include`, which filters the already-collected
coverage map down to matching paths before the threshold is evaluated:

```
npx nyc check-coverage --include "src/app/expenses/**" --lines 80 --branches 80 --functions 80 --statements 80
```

(`test:coverage` still needs to have run first — `--include` only filters
which already-collected files count toward the ratio, it doesn't limit
which specs execute.)

🟡 Flag any coverage run — whole-project or scoped to the reviewed change —
that reports under 80% line coverage. This is a test-adequacy problem, not
a correctness bug, so it's a WARNING rather than CRITICAL, matching how
§15's complexity threshold is treated — but it should be fixed before the
review is considered clean: add the missing test cases for the uncovered
lines/branches the report lists, then re-run the check to confirm it now
clears 80%.

🟢 A scope in the 75–80% range is worth a passing mention if the gap is a
small, easily-covered handful of lines, but isn't required to be flagged —
the threshold that matters is 80%.

For a full-codebase sweep, `npm run coverage:trend-report` wraps the same suite
run into a dated snapshot under `docs/reports/code-coverage/` — the
project-wide percentages plus a per-file table naming every file still
below 80% on any of the four metrics (excluding type-only `.model.ts`
files, which have no executable statements). Useful for spotting a file
that quietly backslid even while the project-wide number stays above
threshold.

---

## 17. Type Coverage

Every reviewed scope also gets a type-coverage pass — how much of the
TypeScript identifier surface has a real, non-`any` type, as opposed to
`any` reached via an explicit annotation, an untyped third-party return
value, or TypeScript's own inference giving up. This is the quantitative
backstop for §7's "flag any use of `any`" rule: that rule catches an `any`
a reviewer happens to read past, this catches one that slipped through
review entirely (most commonly a Supabase `.select()`/`.insert()` call
whose returned `data` isn't cast to the domain type before being used).

Run from `frontend/`:

```
npx type-coverage --project tsconfig.app.json --detail
```

(or `npm run type-coverage:report` for a dated snapshot under
`docs/reports/type-coverage/`, listing every uncovered identifier grouped
by file — useful for a full-codebase sweep rather than a single scoped
review).

🟡 Flag any identifier the tool reports as untyped that isn't already
caught by §7's manual `any` check — most commonly an unannotated Supabase
query result flowing into a service method's return type. This is the same
severity as §7's rule, not a separate threshold-based gate like §15/§16,
since a single untyped identifier is exactly as fixable (add the missing
cast/annotation) regardless of the project-wide percentage.

🟢 Don't chase the last fraction of a percent in files that are
overwhelmingly typed already — note the project-wide percentage in the
review but only flag specific uncovered identifiers actually touched by
the reviewed change (or, for a full sweep, the files with the most
uncovered identifiers per the report's file-grouped table).

---
