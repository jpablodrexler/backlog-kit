# Column naming and data types
Read when: a migration adds or changes a table, column, key, index or constraint name or type

## 2. Column Naming & Data Types

### 2.1 Naming

| Element                | Expected                                        | Example                                  |
| ---------------------- | ------------------------------------------------ | ----------------------------------------- |
| Table                  | `snake_case`, plural                              | `assets`, `refresh_tokens`, `album_assets` |
| Join/association table | `{singular_a}_{singular_b}` (alphabetical or natural read order) | `asset_tags`, `album_assets` |
| Primary key column     | `{table_singular}_id`, `BIGSERIAL`/`SERIAL`       | `asset_id`, `folder_id`, `album_id`       |
| Foreign key column     | Same name as the referenced table's PK column     | `folder_id` referencing `folders.folder_id` |
| Boolean column         | `is_`/`has_` prefix or a clearly boolean noun      | `is_video`, `revoked`, `include_sub_folders` |
| Timestamp column       | `_at` suffix                                      | `created_at`, `deleted_at`, `hash_completed_at` |
| Index name             | `ix_{table}_{column(s)}`                          | `ix_assets_folder_id`, `ix_assets_processing_status` |
| Unique index name      | `uq_{table}_{column(s)}`                          | `uq_refresh_tokens_token`                 |
| Foreign key constraint | inline `REFERENCES` is fine; named constraints use `fk_{table}_{column}` | — |
| Composite PK constraint | `pk_{table}`                                     | `pk_album_assets`                         |

🟡 Flag any new table whose primary key column is bare `id` instead of
`{table_singular}_id`. **Known drift:** `users.id` (`V4__add_users.sql`) is
already inconsistent with every other table (`asset_id`, `folder_id`,
`album_id`, `token_id`, …) — don't propagate that pattern to new tables, and
call it out as a pre-existing `🟢 Suggestion` (not a blocking finding) if it
resurfaces in a full audit, since renaming a live PK used as an FK target
(`refresh_tokens.user_id`, `albums.user_id`, `user_preferences.user_id`, …)
is a breaking, multi-migration change, not a quick fix.

🔴 Flag any new index or constraint that doesn't follow the `ix_`/`uq_`/`fk_`/
`pk_` prefix convention above.

### 2.2 Data types

🔴 Flag `TIMESTAMP` (no time zone) on a **new** table when every other
recently-added table uses `TIMESTAMPTZ` (`refresh_tokens`, `user_preferences`,
`albums`, `album_assets` all use `TIMESTAMPTZ NOT NULL DEFAULT NOW()`).
**Known drift:** `assets.*_date_time` and `folders`/early tables predate this
convention and use bare `TIMESTAMP` — don't require a data migration to fix
retroactively, but never add a new `TIMESTAMP` column going forward.

🟡 Flag `VARCHAR` without an explicit length (`VARCHAR(255)` etc.) when the
column has a genuine natural bound (usernames, enum-backed status columns,
theme names) — unbounded `TEXT` is fine for free-form content (`description`,
`path`, `token`) but an unbounded `VARCHAR` with no length is neither.

🟡 Flag a foreign key column whose type doesn't match its referenced PK's
type exactly (e.g. an `INTEGER` FK pointing at a `BIGSERIAL`/`BIGINT` PK, or a
`VARCHAR` FK pointing at a `UUID` PK).

🟡 Flag a new enum-like status/rotation/rating column stored as free-text
`VARCHAR` without a `CHECK` constraint **and** without a corresponding
`@Enumerated(EnumType.STRING)` domain enum on the entity — one of the two
must constrain the value set, or invalid strings will silently persist.

🟢 Flag `SERIAL`/`INTEGER` primary keys on a new table expected to grow large
(anything asset-scoped) — prefer `BIGSERIAL`/`BIGINT` to avoid a future
int32-overflow migration. (`tags.tag_id` is `SERIAL` — acceptable since the
tag vocabulary is inherently small and bounded, unlike `assets`.)
