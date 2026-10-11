kit: extras/database-reviewer
sub: JPPhotoManagerWeb/docs/backlog => <backlog>
sub: docs/backlog => <backlog>
sub: JPPhotoManagerWeb/docs/reports => <reports>
sub: docs/reports => <reports>

PARAM | name: database-reviewer description: > Database review skill for the J | description rewritten stack-free (TRIGGER structure kept); `author`/`scope` removed, `version` is the kit's (D30)
DROPPED | Review the PostgreSQL schema of the JPPhotoManager web backend: Flyway | second project's variant of this text; the kit follows the first project
PARAM | 1. Identify the **scope**: a full audit of every migration under `db/m | second project's variant of this text; the kit follows the first project
DROPPED | 2. Read every migration file in scope **in filename order** (`V{n}__*. | second project's variant of this text; the kit follows the first project
PARAM | 3. For each table touched, find every repository method (`@Query`, Spr | second project's variant of this text; the kit follows the first project
DROPPED | 4. Cross-check `@Table(indexes = ...)` / `@Index` annotations on the J | second project's variant of this text; the kit follows the first project
DROPPED | ¦ 🔴 **CRITICAL** ¦ Data integrity risk, a query that will corrupt or s | second project's variant of this text; the kit follows the first project
PARAM | 🔴 Flag a new column that duplicates data already derivable from a join | second project's variant of this text; the kit follows the first project
PARAM | 🟡 Flag a repeating group implemented as multiple similarly-named colum | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag a new many-to-many relationship modeled as a comma-separated or | second project's variant of this text; the kit follows the first project
PARAM | 🟢 Flag over-normalization: a lookup table with a fixed, small (<10), r | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Element ¦ Expected ¦ Example ¦ | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ ---------------------- ¦ ------------------------------------------- | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Table ¦ `snake_case`, plural ¦ `assets`, `refresh_tokens`, `album_as | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Join/association table ¦ `{singular_a}_{singular_b}` (alphabetical o | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Primary key column ¦ `{table_singular}_id`, `BIGSERIAL`/`SERIAL` ¦ ` | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Foreign key column ¦ Same name as the referenced table's PK column ¦ | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Boolean column ¦ `is_`/`has_` prefix or a clearly boolean noun ¦ `is | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Timestamp column ¦ `_at` suffix ¦ `created_at`, `deleted_at`, `hash_ | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Index name ¦ `ix_{table}_{column(s)}` ¦ `ix_assets_folder_id`, `ix_a | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Unique index name ¦ `uq_{table}_{column(s)}` ¦ `uq_refresh_tokens_to | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Foreign key constraint ¦ inline `REFERENCES` is fine; named constrai | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Composite PK constraint ¦ `pk_{table}` ¦ `pk_album_assets` ¦ | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag any new table whose primary key column is bare `id` instead of | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any new index or constraint that doesn't follow the `ix_`/`uq_` | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag `TIMESTAMP` (no time zone) on a **new** table when every other | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag `VARCHAR` without an explicit length (`VARCHAR(255)` etc.) when | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag a foreign key column whose type doesn't match its referenced PK | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag a new enum-like status/rotation/rating column stored as free-te | second project's variant of this text; the kit follows the first project
DROPPED | 🟢 Flag `SERIAL`/`INTEGER` primary keys on a new table expected to grow | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any new `FOREIGN KEY`/`REFERENCES` column that has no index. Po | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag a column that appears in a repository's `WHERE`, `JOIN ... ON`, | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag a query that filters or joins on a column covered only by a *co | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag a `LIKE`/`ILIKE` prefix query (`... LIKE :value%`, no leading ` | second project's variant of this text; the kit follows the first project
PARAM | 🟢 Flag a `LIKE '%value%'` (leading wildcard) query and note that a pla | second project's variant of this text; the kit follows the first project
DROPPED | 🟢 Suggest a partial index (`WHERE` clause on the `CREATE INDEX` itself | second project's variant of this text; the kit follows the first project
PARAM | 🟢 Flag redundant indexes: two indexes on the same table where one's co | second project's variant of this text; the kit follows the first project
DROPPED | ### 3.4 Entity/migration index drift | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag any `@Index`/`@Table(indexes = ...)` entry on a JPA entity that | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag the reverse: a migration-created index on a column with no matc | second project's variant of this text; the kit follows the first project
DROPPED | ## 4. Views & Functions | second project's variant of this text; the kit follows the first project
DROPPED | The schema currently has **no** `CREATE VIEW`/`CREATE OR REPLACE VIEW` | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag a `CREATE FUNCTION` written in `PL/pgSQL` when the same logic c | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any function created `SECURITY DEFINER` without an explicit, co | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag a `CREATE VIEW` that is not `CREATE OR REPLACE VIEW` — plain `C | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag a materialized view added without a corresponding refresh strat | second project's variant of this text; the kit follows the first project
DROPPED | 🟢 Flag a view or function name that doesn't follow `snake_case` matchi | second project's variant of this text; the kit follows the first project
PARAM | ## 5. Migration Mechanics | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any modification to an **existing, already-applied** migration | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag a migration filename that doesn't follow `V{n}__{Description}.s | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag a new version number that isn't the next sequential integer aft | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag a new `@Column(nullable = false)` on an entity with no matching | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag a migration that adds a `NOT NULL` column to an existing popula | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag a single migration that both alters schema **and** performs a l | second project's variant of this text; the kit follows the first project
DROPPED | 🟢 Flag a migration that could have used `CREATE INDEX IF NOT EXISTS` ( | second project's variant of this text; the kit follows the first project
DROPPED | ## 6. Foreign Key & Cascade Behavior | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag a foreign key with no `ON DELETE` clause where the parent row c | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag `ON DELETE CASCADE` on a relationship where cascading would sil | second project's variant of this text; the kit follows the first project
DROPPED | ### 6.3 Cross-Datastore Consistency | second project's variant of this text; the kit follows the first project
DROPPED | This project's data isn't confined to Postgres: `asset_audit_log` live | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag a migration or entity change to a table that is also mirrored i | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag a new dual-write (a repository method that writes to Postgres a | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag a schema change to a table whose data has previously lived in a | second project's variant of this text; the kit follows the first project
DROPPED | 🟢 Suggest a `MongoIndexInitializer`-style startup-ensured index (compo | second project's variant of this text; the kit follows the first project
PARAM | - `db/migration/V33__....sql:5` — <issue description> | second project's variant of this text; the kit follows the first project
PARAM | - `entity/AssetEntity.java:16` — <issue description> | second project's variant of this text; the kit follows the first project
PARAM | - `jpa/JpaFolderRepository.java:18` — <issue description> | second project's variant of this text; the kit follows the first project
PARAM | - **Path:** `<reports>/database-review/DATABASE_REVIEW_FINDINGS_{YYYY- | second project's variant of this text; the kit follows the first project
PARAM | - **Content:** the same Critical/Warnings/Suggestions grouping as the | second project's variant of this text; the kit follows the first project
PARAM | 1. Read the affected migration/entity/repository file(s) in full conte | second project's variant of this text; the kit follows the first project
DROPPED | - **A fix to an already-applied migration is never "edit the file"** — | second project's variant of this text; the kit follows the first project
DROPPED | - If the finding is purely on the JPA entity side (e.g. `@Table(indexe | second project's variant of this text; the kit follows the first project
DROPPED | 3. Verify the fix: run `mvn clean test-compile` at minimum; if the cha | second project's variant of this text; the kit follows the first project
PARAM | 4. Update any repository tests whose expectations depended on the old | second project's variant of this text; the kit follows the first project
PARAM | - `**Evaluated, no change made:** <rationale>` — for findings where th | second project's variant of this text; the kit follows the first project
PARAM | 6. If fixing one finding incidentally resolves another still-unchecked | second project's variant of this text; the kit follows the first project
DROPPED | After finishing the selected scope, run the widest verification availa | second project's variant of this text; the kit follows the first project
PARAM | name: database-reviewer description: > Database review skill for the p | description rewritten stack-free (TRIGGER structure kept); `author`/`scope` removed, `version` is the kit's (D30)
DROPPED | Review the PostgreSQL schema of the pablo-web Supabase project: migrat | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | 1. Identify the **scope**: a full audit of every migration under `supa | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | 2. Read every migration file in scope **in filename order** (`{YYYYMMD | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | 3. For each table touched, find every service method under `frontend/s | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | 4. **For every table with RLS enabled, enumerate its actual policies** | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | ¦ 🔴 **CRITICAL** ¦ Data integrity risk, an RLS gap that exposes or hid | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | ¦ ------------------------ ¦ ----------------------------------------- | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Table ¦ `snake_case`, singular (this project's existing convention — | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Primary key column ¦ `id`, `uuid DEFAULT gen_random_uuid()` ¦ `task. | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Foreign key column ¦ `{referenced_table_singular}_id` ¦ `task.user_i | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Boolean column ¦ `is_`/`has_` prefix or a clearly boolean noun ¦ `is #2 | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Timestamp column ¦ `_at` suffix, `timestamp with time zone` ¦ `creat | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Policy name ¦ A plain-English sentence in double quotes (Supabase/Po | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Index name ¦ `{table}_{column(s)}_idx` (Postgres/Supabase default na | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | **Known drift to watch for:** the primary-key convention here is bare | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🟡 Flag `timestamp` (no time zone) on a new column — every existing tim | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🟡 Flag `text` used for a column with a genuine natural bound where a ` | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | 🟡 Flag a foreign key column whose type doesn't match its referenced PK #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | 🟡 Flag a new enum-like status column stored as free-text without a `CH | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | 🔴 Flag any new foreign-key column that has no index. Postgres does **n | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | 🔴 Flag a column that appears in a service's `.eq()`/`.match()`/`.order | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | 🟡 Flag a `.ilike()`/`.like()` prefix query (`value%`, no leading `%`) | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | 🟢 Flag a `.ilike()` query with a leading wildcard (`%value%`) and note | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | ## 4. Row Level Security — the primary access-control layer | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | This is the highest-value section in this skill for this project. Ther | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ### 4.1 A table must have policies covering every operation the fronte | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🔴 Flag any table with `ENABLE ROW LEVEL SECURITY` that has **zero** po | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | Before doing this cross-check by hand, run `npm run rls-route-coverage | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🔴 Flag a table with RLS **not** enabled (`ALTER TABLE ... ENABLE ROW L | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ### 4.2 Policy correctness | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🔴 Flag a policy whose `USING`/`WITH CHECK` expression doesn't actually | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | - A `SELECT`/`UPDATE`/`DELETE` policy using only `USING (...)` when th | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | - An `INSERT` policy using `USING (...)` instead of `WITH CHECK (...)` | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | - A policy scoped `TO anon, authenticated` when the operation should b | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🟡 Flag a policy whose `USING`/`WITH CHECK` is literally `true` (fully | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ### 4.3 Grants alongside policies | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🟡 Flag a migration that adds a `CREATE POLICY` for a role that has no | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🟡 Flag a `REVOKE` that isn't paired with removing the now-pointless po | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ## 5. Views & Functions | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | No `CREATE VIEW` or `CREATE FUNCTION` exists in this schema yet. If a | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🔴 Flag any function created `SECURITY DEFINER` without an explicit, co #2 | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🟡 Flag a `CREATE VIEW` that is not `CREATE OR REPLACE VIEW` — plain `C #2 | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🟡 Flag a view built on a table with RLS enabled where the view itself | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | ## 6. Migration Mechanics (Supabase CLI) | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | 🔴 Flag any modification to an **existing, already-applied** migration #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | 🟡 Flag a new migration filename that doesn't follow the Supabase CLI's | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | 🟡 Flag a migration that adds a `NOT NULL` column to an existing popula #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | 🟡 Flag a migration that both alters schema **and** performs a large da | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | 🟢 Flag a migration missing a header comment explaining *why* a non-obv | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | - `supabase/migrations/{file}.sql:5` — <issue description> | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | - `frontend/src/app/core/tasks.service.ts:16` — <issue description> | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | - `supabase/migrations/{file}.sql:18` — <issue description> | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | - **Path:** `<reports>/database-review/DATABASE_REVIEW_FINDINGS_{YYYY- #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | - **Content:** the same Critical/Warnings/Suggestions grouping as the #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | 1. Read the affected migration/service file(s) in full context before | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | - **A fix to an already-applied migration is never "edit the file"** — #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | 3. Push the new migration to actually apply it: `npx supabase db push` | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | 4. Update any frontend service/tests whose expectations depended on th | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | 6. If fixing one finding incidentally resolves another still-unchecked #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | After finishing the selected scope, run the widest verification availa #2 | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
