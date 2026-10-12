# Extras

Optional skills. Install them with `python3 tools/install.py <repo> --extras` (or `--all`); the core works without them.

Eight of them are stack-neutral in their *frame* (workflow, severities, report format) and take the stack-specific knowledge from your project. They all work the same way:

1. **Project notes (optional, precise).** Markdown files under `.backlog-kit/<folder>/` at the repo root. Each file starts with a `# Title`, and its second line is `Read when: …` — either `every run` / `every review`, or a short condition ("a migration file changed"). The skill reads the files whose condition matches the task and follows them.
2. **No notes? It still works.** If the folder does not exist or is empty, the skill works from its frame plus what your `CLAUDE.md`, `README` and `docs/` already say, and states in its report that no project notes were found. You write nothing to start.

| Extra | Folder it reads | What the notes hold |
| --- | --- | --- |
| `code-reviewer` | the `Code review checks` section of `docs/frontend.md` / `docs/backend.md` | checklists: layering, naming, state, tests, known pitfalls, metrics, the sweep layers |
| `security-reviewer` | the `Security review checks` section of `docs/security.md` | checklists: dependencies, the authorization boundary, sensitive data and keys, authentication and sessions, frontend security, known pitfalls, the sweep layers |
| `database-reviewer` | the `Database review checks` section of `docs/database.md` | checklists: naming, data types, indexes, access rules, migrations, the fix workflow |
| `docs-sync` | `.backlog-kit/docs/` | which doc section follows which source of truth |
| `spec-compliance-check` | `.backlog-kit/spec-compliance/` | where the tests live, how a scenario is verified by hand |
| `dependency-upgrade` | `.backlog-kit/dependency-upgrade/` | package manager commands, packages never bumped without approval |
| `architecture-reviewer` | the `Architecture review checks` section of `docs/architecture.md` | the project's own dimensions and checks, the files that look cross-cutting, the case that motivated the review |
| `product-scope-roaster` | the `Product scope review checks` section of `docs/product.md` | the project's own examples of merge / split / gap / inconsistency to test on their merits |

The batch runners need no notes: `features-batch-development`, `bugs-batch-fix`.

A note file, in full:

```markdown
# Migrations must be reversible
Read when: a file under supabase/migrations changed

- Every `CREATE TABLE` has a matching drop in the rollback note.
- …
```

Start without notes; add one when a review keeps missing something your project cares about. The text each skill uses for this is in its `SKILL.md` (search for "Project checklists" or "Project notes").
