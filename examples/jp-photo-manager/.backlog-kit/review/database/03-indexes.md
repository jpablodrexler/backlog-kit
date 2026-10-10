# Indexes
Read when: a migration adds a table, a foreign key or an index, a repository query changes, or an entity's index annotations change

## 3. Indexes

### 3.1 Coverage for foreign keys

🔴 Flag any new `FOREIGN KEY`/`REFERENCES` column that has no index. Postgres
does **not** auto-index FK columns (only the referenced side gets one via its
PK); every FK in this schema needs an explicit `CREATE INDEX` — see
`ix_assets_folder_id`, `ix_albums_user_id`, `ix_refresh_tokens_user_id`,
`ix_search_presets_user_id` for the existing pattern.

### 3.2 Coverage for query predicates

🔴 Flag a column that appears in a repository's `WHERE`, `JOIN ... ON`, or
`GROUP BY` clause on a table with non-trivial expected row count (`assets`
above all — this is a photo catalog, rows are expected in the tens/hundreds
of thousands) and has no supporting index. Concretely check every `@Query` in
`JpaAssetRepository`/`JpaFolderRepository` against the indexes actually
created by migrations, not against what `@Table(indexes=...)` claims (§3.4).
Known example to verify hasn't regressed: `AssetEntity.hash` is queried by
`findByHash` (`WHERE a.hash = :hash`) and by the duplicate-detection queries
(`GROUP BY a.hash HAVING COUNT(a) > 1`, and the correlated subquery in
`countDuplicates`) but as of this schema has **no index** — flag this as 🔴 if
still true, since duplicate detection runs a full sequential scan of `assets`
on every call.

🟡 Flag a query that filters or joins on a column covered only by a
*composite* index where the queried column isn't the leftmost member (a
leftmost-prefix violation) — e.g. a hypothetical lookup by `tag_id` alone
against `asset_tags`, whose only index is the composite PK
`(asset_id, tag_id)` — the PK covers "find tags for an asset" but not "find
assets for a tag" without a sequential scan.

🟡 Flag a `LIKE`/`ILIKE` prefix query (`... LIKE :value%`, no leading `%`)
against an unindexed `TEXT`/`VARCHAR` column — a plain B-tree index still
helps a left-anchored pattern. Known example to verify: `JpaFolderRepository`
has both `findByPath(String path)` and a prefix query
(`WHERE f.path LIKE :parentPath%`) against `folders.path`, which has no index
beyond the `folder_id` primary key — flag as 🟡 (not 🔴, since the `folders`
table itself is small; escalate to 🔴 only if it's joined against a
large table in the same query).

🟢 Flag a `LIKE '%value%'` (leading wildcard) query and note that a plain
B-tree index cannot help it — a `pg_trgm` GIN index would be the fix, but
only worth flagging as a suggestion since it's a bigger infrastructure change
(new extension) than a routine index addition.

### 3.3 Partial and covering indexes

🟢 Suggest a partial index (`WHERE` clause on the `CREATE INDEX` itself) when
a boolean/nullable column is queried almost exclusively for one value — the
existing `ix_albums_filter_json_not_null` (`V18`, indexing rows only `WHERE
filter_json IS NOT NULL`) and the implicit pattern behind
`ix_assets_deleted_at`/`ix_assets_processing_status` (queried mostly for
"active" or "pending" rows) are the reference examples. Don't insist on
converting an existing full index to partial unless a review specifically
asks for an index optimization pass — this is a suggestion, not a defect.

🟢 Flag redundant indexes: two indexes on the same table where one's column
list is a strict prefix of the other's — the shorter one adds write overhead
with no read benefit Postgres wouldn't get from the longer index alone.

### 3.4 Entity/migration index drift

🟡 Flag any `@Index`/`@Table(indexes = ...)` entry on a JPA entity that has
**no** corresponding `CREATE INDEX` in any migration — since `ddl-auto` is
`validate`/`none` here, the annotation creates nothing; it's misleading
documentation at best, and a developer reading only the entity will believe
an index exists that doesn't.

🟡 Flag the reverse: a migration-created index on a column with no matching
`@Index` entry on the entity — not wrong, but worth surfacing so the entity's
index list stays a trustworthy mirror of the real schema. Known example to
verify hasn't regressed: `AssetEntity`'s `@Table(indexes = ...)` currently
lists `ix_assets_folder_id` and `ix_assets_processing_status` but omits
`ix_assets_deleted_at` and `ix_assets_rating`, both of which exist in
migrations (`V10`, `V11`) — flag as 🟡 if still missing.
