# Migration mechanics
Read when: a migration file is added, changed or renamed, or an entity's nullability changes

## 5. Migration Mechanics

🔴 Flag any modification to an **existing, already-applied** migration file
under `db/migration/` — once applied, a migration's content and checksum are
fixed; Flyway will refuse to start if a checksum mismatches. Any change goes
in a new `V{n+1}__*.sql` instead. (This mirrors `code-reviewer` §6 — restated
here because it's the single most consequential mistake in this area.)

🟡 Flag a migration filename that doesn't follow `V{n}__{Description}.sql`
(two underscores after the version, `Description` in `Snake_Case` or
`lower_snake_case` matching the existing files — e.g.
`V14__add_file_type_to_assets.sql`, not `V14_addFileTypeToAssets.sql`).

🟡 Flag a new version number that isn't the next sequential integer after the
highest existing `V{n}` in `db/migration/` — check the actual highest version
present (not just the highest-numbered file matching a guess), since this
schema's versions are not contiguous by *filename sort* alone (e.g. `V1` sorts
after `V10`–`V19` alphabetically; always compare the numeric value).

🔴 Flag a new `@Column(nullable = false)` on an entity with no matching
`NOT NULL` (or a `NOT NULL` added via a follow-up `ALTER TABLE ... SET NOT
NULL`) in a migration, or the reverse — entity nullability and the actual
column constraint must agree, or Hibernate will either reject valid nulls
the DB allows, or let invalid nulls through that the DB would have rejected
had `ddl-auto` been more than `validate`.

🟡 Flag a migration that adds a `NOT NULL` column to an existing populated
table without either a `DEFAULT` or a backfill `UPDATE` in the same
migration — this project's own `V32__add_asset_processing_status.sql` shows
the right shape (`ADD COLUMN processing_status VARCHAR(20) NOT NULL DEFAULT
'COMPLETED'`), avoiding a separate backfill step entirely.

🟡 Flag a single migration that both alters schema **and** performs a
large data backfill via `UPDATE` on a large table (`assets`) without
considering lock duration — prefer a `DEFAULT` (as above) over an
`UPDATE ... SET` touching every row when the two are equivalent in outcome.

🟢 Flag a migration that could have used `CREATE INDEX IF NOT EXISTS` (as
`V1__initial_schema.sql` does for `ix_assets_folder_id`) instead of a bare
`CREATE INDEX`, for migrations whose idempotency matters for re-run
resilience — not required project-wide, but consistent with the one
precedent that exists.
