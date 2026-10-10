---
name: database-reviewer
description: Reviews database schema and migration changes from files only, never a live database. Checks normalization, naming, data types, constraints and foreign keys, index coverage of FK and filter columns, nullability and defaults, migration mechanics (never edit an applied migration, ordering, idempotence, data-migration safety, locks) and access-control policy coverage where the database enforces it. TRIGGER when a migration, schema file, view, function, policy or database query is added or changed, when a `[[reviews]]` entry names this skill (non-interactive review mode, given a file list), when asked to audit the whole migration history, or to fix findings from an existing database review report.
license: MIT
metadata:
  version: "0.1"
---

Review database changes by reading files. Never connect to, query or modify a live database, and never run a migration tool against one. `<reports_dir>` comes from `.backlog-kit.toml` `[paths] reports_dir` (default `docs/reports`).

## Modes

Pick the mode from how you were invoked. They are separate; do not mix them.

| Mode | When | Interactive |
| --- | --- | --- |
| **Non-interactive review** | Invoked by the review phase (`[[reviews]] skill = "database-reviewer"`) or given a file list | No |
| **Audit** | Asked to audit the whole migration history | Yes |
| **Fix** | Asked to fix or work through findings of an existing report | Yes |

Example configuration:

```toml
[[reviews]]
name  = "database"
focus = "schema and migration safety, index coverage, access policies"
skill = "database-reviewer"
when  = ["**/migrations/**", "**/*.sql", "db/schema*"]
```

## Non-interactive review mode

Input: a list of changed files (passed verbatim), an id (the backlog item or change name), and optional focus text. Ask nothing.

1. Review **exactly the listed files**: migrations, schema files, and queries or model definitions that touch the schema. No full-history audit, no fix workflow, no files outside the list except as read-only context (§0).
2. Gather context by reading (§0), then apply the checklist (§1-§7) to the changed lines. Report only real problems, not a restatement of the diff. A finding must point at a real `<file>:<line>` in the listed files; if the cause is in an unlisted file, cite the listed file that triggers it.
3. Write `<reports_dir>/review/database-<id>-<YYYY-MM-DD>.md` (create the folders; if the file exists append `-2`, `-3`). Start with one line naming the scope and the focus text if any. Every finding is a checkbox line, with no other finding format:

   `- [ ] 🔴|🟡|🔵 <file>:<line> — <what is wrong and why it matters>`

   Group by severity, omit empty groups, and write only what this run found.
4. Hand back exactly one line and nothing else:

   `REVIEW: <n> critical, <n> warning, <n> suggestion — report <path>`

   With no findings, still write the report (state that nothing was found) and hand back the line with zeros.

The reviewer does not fix. The caller fixes, ticks the boxes and re-runs.

## Severity

| Level | Meaning |
| --- | --- |
| 🔴 Critical | Data integrity or data loss risk, an access-control gap that exposes or hides data, an applied migration edited, or a query on a hot path with no usable index. Must be fixed before merging. |
| 🟡 Warning | Violates a project schema standard, causes avoidable query cost or lock time, or invites drift. Should be fixed. |
| 🔵 Suggestion | Style, minor normalization nit, hardening idea. Fix if convenient. |

When a rule below names one level but the project documents a deliberate exception, downgrade or drop the finding and say why in the report.

## 0. Learn the project first

Before judging anything, identify from the repository (not from assumptions):

- how migrations are written, ordered and applied (tool, folder, naming scheme, whether files are checksummed or tracked as applied);
- the project's existing naming, key, timestamp and index conventions (read several earlier migrations; new code follows the established house style, not a textbook);
- what enforces access control, if the database does (row-level access policies, grants, roles, views, functions with elevated privilege) and where the project documents intentional exceptions;
- how the application reaches the database (queries, models, generated clients), to find the filter, join and sort columns each table is actually queried by.

Read the whole migration history for each touched table **in applied order** (use the numeric or timestamp order the tool uses, not alphabetical): a column added in one migration may be altered, re-indexed or have its policy replaced later, and a migration reviewed in isolation misses that. If the project documents an applied-migration list, a lock file or a schema snapshot, compare against it.

## 1. Normalization

- 🔴 A new column that duplicates data derivable through an existing foreign key; the copy can drift on update.
- 🟡 A repeating group in similarly-named columns (`tag_1`, `tag_2`) instead of a child or join table.
- 🟡 A many-to-many relationship stored as a delimited or structured list of ids in one column, unless the values are never queried individually (opaque application-defined criteria in a JSON column are fine).
- 🔵 Over-normalization: a lookup table for a small, fixed, rarely changing value set referenced from one table might be a constraint on a column. Follow how the project already models small closed sets.

## 2. Naming and data types

Check against the conventions found in §0. Do not impose a convention the project does not use, and do not flag a historical inconsistency in unchanged code as blocking (mention a pre-existing one as 🔵 only in an audit).

- Tables, columns, keys, booleans, timestamps, indexes, constraints and policies each follow the established pattern (case, singular or plural, key and foreign key naming, boolean and timestamp affixes, index and constraint prefixes). A new object that breaks the pattern is 🟡; a new foreign key column named inconsistently with what it references is 🟡.
- 🟡 A timestamp column without a time zone where the project's recent tables use zone-aware timestamps; never introduce a new inconsistent timestamp type.
- 🟡 Unbounded or arbitrarily sized character columns where the value has a natural bound and the project bounds such columns; free-form text is fine unbounded.
- 🟡 A foreign key column whose type does not exactly match the referenced key's type.
- 🟡 An enum-like status column stored as free text with no constraint (and no enum type) limiting its values; invalid strings persist silently.
- 🔵 A small integer key on a table expected to grow large; prefer a type that will not overflow.

## 3. Constraints, keys and nullability

- 🔴 A foreign key relationship that is only implied: a column that references another table's key with no declared foreign key, where the project declares them elsewhere.
- 🔴 A foreign key with no explicit delete behaviour where parents can legitimately be deleted while children exist (the default blocks the delete at runtime). Match the project's usual behaviour and require a stated reason for a deviation.
- 🟡 A cascading delete that would silently destroy data users expect to survive (history, audit rows), or one that duplicates or conflicts with deletion already done in application code.
- 🟡 A missing primary key, unique constraint or check constraint where the data model clearly requires one (natural-key uniqueness, non-negative amounts, bounded ranges).
- 🔴 Application-side nullability and the column's real nullability disagree (a model says required, the column allows null, or the reverse).
- 🟡 A nullable column that should never be null, or a `NOT NULL` column with no default and no way for existing writers to supply it.

## 4. Indexes

Postgres-style databases do not auto-index the referencing side of a foreign key; check what the project's engine does and verify against the migrations that actually exist, not against annotations or comments claiming an index.

- 🔴 A new foreign key column with no index.
- 🔴 A column used in a `WHERE`, `JOIN ... ON`, `ORDER BY` or `GROUP BY` of a query on a table expected to grow, with no supporting index. This includes columns referenced by access-policy conditions, since every query then carries that filter implicitly.
- 🟡 A filter or join on a column that appears only in a composite index and is not its leftmost member.
- 🟡 A left-anchored text pattern search on an unindexed text column.
- 🔵 A leading-wildcard text search: an ordinary index cannot help, a specialized index type could, but it is a larger change.
- 🔵 A partial index would fit a column queried almost only for one value.
- 🔵 Redundant indexes: one column list is a strict prefix of another's.
- 🟡 Drift between index declarations in application models and the indexes the migrations really create, in either direction, when the models are documentation only.
- Weigh severity by expected table size; escalate when a small table is joined against a large one.

## 5. Access-control policies (where the database enforces access)

Identify what enforces access control for this project. If the database does (row-level policies plus grants, roles, or similar), verify the change is covered; if only application code does, skip this section.

**Silent-failure warning: a missing or too-narrow policy usually does not raise an error; reads return an empty result and writes affect zero rows.** Never assume a policy exists because a table obviously needs one; find it in the migrations.

- 🔴 A table with enforcement enabled and **no** policy for an operation (read, insert, update, delete) that the application performs.
- 🔴 A table reachable by client roles with enforcement **not** enabled, exposing every row.
- 🔴 A policy whose condition does not scope by the authenticated identity where per-user ownership is the intent; the new table should follow the project's existing ownership shape.
- 🔴 A policy using the wrong clause for its operation: an update needs both the row-visibility condition and the new-row check; an insert has no existing row, so only the new-row check applies.
- 🔴 A write policy that lets a user attach their own row to a parent row they do not own (missing ownership check per parent foreign key).
- 🟡 A policy granted to broader roles than intended (for example anonymous as well as authenticated) when the current intent is authenticated-only.
- 🟡 A policy that is unconditionally true on a table holding anything user-specific; correct only for genuinely public data.
- 🟡 A policy for a role that lacks the table-level grant (or default privilege) needed for the operation at all.
- 🟡 A revoked grant not paired with dropping the now-pointless policies, or the reverse; leaves a confusing half-dead state.
- A table deliberately deviating from the standard shape (shared reference data, system-written tables, append-only logs) is fine when the project documents it; if undocumented, report 🔵 asking for the note.

## 6. Views and functions

- 🔴 A function with elevated (definer) privileges and no commented justification; it can bypass the access model in §5.
- 🟡 A view created with a plain create instead of an idempotent replace form, where the engine supports one.
- 🟡 A view over a table with access policies that does not inherit the caller's restrictions; verify how the engine evaluates policies for views before assuming it is safe.
- 🟡 A materialized view with no refresh strategy; it serves stale data forever.
- 🟡 Business logic moved into a database function where the project keeps such logic in application code, unless the query genuinely cannot express it.
- 🔵 A view or function name that breaks the project's naming convention.

## 7. Migration mechanics

- 🔴 Any modification, rename or deletion of an **already-applied** migration. Its content or checksum is fixed once applied; editing history desyncs environments. Any change goes in a new migration. Decide "applied" from the project's tracking (applied list, lock file, release tags, or the file existing on the base branch); if unsure, treat a file present on the base branch as applied.
- 🟡 A new migration whose name or version breaks the project's scheme, or is not ordered after the highest existing one (compare numerically or by timestamp, not alphabetically), or collides with another new migration.
- 🟡 A migration that adds a `NOT NULL` column to a populated table with neither a default nor a backfill in the same migration. The safe shape: add nullable (or with a default), backfill, then set `NOT NULL`, before anything relies on it.
- 🟡 A large data backfill or delete (`UPDATE`/`DELETE` over many rows) mixed with schema change, without considering lock duration, batching or whether the delete is safe at production scale. Prefer a default over rewriting every row when the outcome is equivalent. If the strategy is not obvious, report it for a human decision.
- 🟡 Schema change that takes a long exclusive lock on a large table (rewrite on type change, non-concurrent index build) where the engine offers a lock-friendlier form, or a concurrent-only statement placed inside a transaction.
- 🟡 Not reversible or not re-runnable where the project expects it: no down/rollback step in a tool that wants one, or a bare create that fails on re-run where the project uses guarded forms. Destructive steps (drop column or table, narrowing a type) with no note about data loss or a prior backup are 🔴.
- 🟡 Application code changed in a way that needs the schema first (or the reverse) with no ordering or compatibility note, so a deploy between the two breaks.
- 🔵 A non-obvious step with no header comment explaining why (why a column starts nullable, why old rows are deleted).

## Audit mode (interactive)

1. Ask for the scope if unclear: the whole migration history, one table, or one area.
2. Follow §0 and read all of it in applied order, then work through §1-§7 for every table, including queries that read it.
3. Write `<reports_dir>/database-review/DATABASE_REVIEW_FINDINGS_<YYYY-MM-DD>.md` (append `-2`, `-3` for reruns; never overwrite an earlier report). Header: scope and the latest migration reviewed. Findings use the same checkbox line format as above, grouped by severity.
4. Show the user a summary: findings by severity, a one or two sentence verdict (health, safe to merge or not, the single most important fix), and the report path.

## Fix workflow (interactive, existing report only)

Use only when asked to fix findings of an existing report. It edits files; it never touches a live database.

1. **Locate the report**: the one the user names, else the most recent `DATABASE_REVIEW_FINDINGS_*.md` under `<reports_dir>/database-review/` or `database-*.md` under `<reports_dir>/review/` with unchecked boxes. None: say so and stop. If several reruns remain unchecked, ask which first, with counts per severity.
2. **Read it fully**, then ask whether to fix a whole severity group or one finding; offer only groups with unchecked boxes.
3. **Fix one finding at a time**: read the affected files in context first. A fix to an already-applied migration is never an edit to that file; write a **new** migration with the next correct name or version (compare the highest existing one), using the project's own generator convention if it has one. A finding that needs a large backfill with no obvious strategy: stop and ask. Update application code or tests whose expectations depended on the old schema.
4. **Tick it immediately**: `- [ ]` to `- [x]` plus `**Fixed:** <what changed and why>.` or `**Evaluated, no change made:** <rationale>`. If a fix resolves another unchecked finding, tick that too with a note.
5. **Verify** with the widest check the project already provides for migrations and tests (read its documented commands; run only what is local and safe). Say plainly what could not be run, such as anything that needs a live database. Applying the new migration to any real environment is the user's step: say so.
6. Repeat until the user stops or the report is fully ticked.

## Guardrails

- **Never run `git commit`, `git push` or open a PR.** Leave all changes uncommitted for the user to review.
- Read files only. Never connect to, query, migrate or modify a live database, and never run a command that would apply a migration to a real environment.
- Review modes write exactly one report and edit nothing else. Only the fix workflow edits files, and then only code, tests, new migrations and the report being worked.
- Never edit an already-applied migration; a fix is always a new migration.
- Never install system packages or change anything outside the repository to run a check; an unrunnable check is reported as not run, with the reason.
- Do not invent rules the project has not adopted; where a convention is unclear, say what you looked at and ask in interactive modes or note it as 🔵 in non-interactive mode.
- Report counts computed from the report's checkboxes, not from memory.
