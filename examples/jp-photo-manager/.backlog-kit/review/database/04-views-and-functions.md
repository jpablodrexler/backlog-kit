# Views and functions
Read when: a migration creates or changes a view or function

## 4. Views & Functions

The schema currently has **no** `CREATE VIEW`/`CREATE OR REPLACE VIEW` or
`CREATE FUNCTION` in any migration — every derived/aggregated read (home
dashboard stats, duplicate grouping, storage-by-folder, format breakdown) is
done via JPQL projections in `JpaAssetRepository` (`FolderAssetCount`,
`FormatProjection`, `MonthlyCountProjection`, `RatingProjection`,
`FolderStorageProjection`) instead. If a migration introduces the first
view/function, apply:

🔴 Flag a `CREATE FUNCTION` written in `PL/pgSQL` when the same logic could be
a plain JPQL/native `@Query` — functions move logic out of version-controlled
Java into the database, which this project's existing style deliberately
avoids (see the projection interfaces above). Only justify a DB function for
something a query genuinely cannot express (e.g. recursive CTEs for a folder
tree, which the current `LIKE :parentPath%` approach in `JpaFolderRepository`
approximates without one).

🔴 Flag any function created `SECURITY DEFINER` without an explicit,
commented justification — it executes with the privileges of the function's
owner, not the caller.

🟡 Flag a `CREATE VIEW` that is not `CREATE OR REPLACE VIEW` — plain
`CREATE VIEW` fails on a rerun/rollback-and-reapply and can't be
version-bumped in place; every later migration touching it must re-issue
`CREATE OR REPLACE VIEW` with the full definition, since Postgres has no
`ALTER VIEW ... ADD COLUMN`.

🟡 Flag a materialized view added without a corresponding refresh strategy
(a scheduled job, or a trigger) — an unrefreshed materialized view silently
serves stale data forever.

🟢 Flag a view or function name that doesn't follow `snake_case` matching the
table naming convention in §2.1.
