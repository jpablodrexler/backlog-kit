# Extras

Optional skills. Install them with `python3 tools/install.py <repo> --extras` (or `--all`); the core works without them.

Several of them are stack-neutral in their *frame* (workflow, severities, report format) and take the stack-specific knowledge from your project. They all work the same way:

1. **Checks in your docs (optional, precise).** A named section of one of your reference docs (for example `Database review checks` in `docs/database.md`), at the standard locations of the kit conventions. The skill reads the section and follows it, keeping its §N numbers stable.
2. **No section? It still works.** The skill works from its frame plus what your `CLAUDE.md`, `README` and `docs/` already say, and states in its report that no project checks were found. You write nothing to start.

| Extra | Section it reads | What it holds |
| --- | --- | --- |
| `code-reviewer` | the `Code review checks` section of `docs/frontend.md` / `docs/backend.md` | checklists: layering, naming, state, tests, known pitfalls, metrics, the sweep layers |
| `security-reviewer` | the `Security review checks` section of `docs/security.md` | checklists: dependencies, the authorization boundary, sensitive data and keys, authentication and sessions, frontend security, known pitfalls, the sweep layers |
| `database-reviewer` | the `Database review checks` section of `docs/database.md` | checklists: naming, data types, indexes, access rules, migrations, the fix workflow |
| `docs-sync` | the `Checked against` column of the `Kit conventions` table in `CLAUDE.md` | which source each doc is compared with |
| `spec-compliance-check` | the `Spec compliance checks` section of `docs/frontend.md` / `docs/backend.md` | where the tests live, how a scenario is verified by hand |
| `dependency-upgrade` | the `Dependency upgrade checks` section of `docs/frontend.md` / `docs/backend.md` | package manager commands, packages never bumped without approval |
| `architecture-reviewer` | the `Architecture review checks` section of `docs/architecture.md` | the project's own dimensions and checks, the files that look cross-cutting, the case that motivated the review |
| `product-scope-roaster` | the `Product scope review checks` section of `docs/product.md` | the project's own examples of merge / split / gap / inconsistency to test on their merits |

The batch runners need no notes: `features-batch-development`, `bugs-batch-fix`.

Start without sections; add one when a review keeps missing something your project cares about. The text each skill uses for this is in its `SKILL.md` (search for "Project checks" or "Project checklists").
