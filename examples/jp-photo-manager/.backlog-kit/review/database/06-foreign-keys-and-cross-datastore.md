# Foreign key, cascade and cross-datastore consistency
Read when: a migration adds or changes a foreign key or cascade rule, or touches a table that is also stored in another datastore

## 6. Foreign Key & Cascade Behavior

🔴 Flag a foreign key with no `ON DELETE` clause where the parent row can
legitimately be deleted while children exist — Postgres defaults to
`ON DELETE NO ACTION`, which will throw at delete time instead of failing
the migration review. Every FK in this schema currently uses
`ON DELETE CASCADE` explicitly (`folders`→`assets`, `users`→`albums`/
`refresh_tokens`/`search_presets`/`user_preferences`, `assets`/`tags`→
`asset_tags`, `albums`/`assets`→`album_assets`) — match that unless the
relationship genuinely needs `RESTRICT`/`SET NULL` instead, and say why in
the migration if it deviates.

🟡 Flag `ON DELETE CASCADE` on a relationship where cascading would silently
destroy data the user would expect to survive (e.g. cascading an asset
delete into audit/history data) — cross-check against
`java-developer`/`CLAUDE.md`'s note that MongoDB `asset_exif`/
`asset_audit_log` deletion is handled explicitly in application code
precisely *because* Postgres cascade can't reach them; a new Postgres-side
cascade that duplicates or conflicts with an existing explicit-delete code
path is worth flagging.

### 6.3 Cross-Datastore Consistency

This project's data isn't confined to Postgres: `asset_audit_log` lives in
MongoDB, `refresh_tokens` is dual-written into Redis alongside its Postgres
table, and `asset_exif` has already migrated between Postgres and MongoDB
once (`mongodb-exif-store` → `revert-exif-postgres-jsonb`). A schema change
that touches a table with a presence in another store needs the same
scrutiny as an index or cascade change — a review that only checks the SQL
side can miss a consistency bug entirely.

🔴 Flag a migration or entity change to a table that is also mirrored into
another store (Redis, Mongo) when the change doesn't identify **which store
is authoritative for reads** post-change. `refresh_tokens` is explicit about
this today — Postgres remains authoritative for `findByToken`/
`deleteByUserId`/`deleteById` even though every write is mirrored into Redis
— a change that alters the write path without restating (or deliberately
changing) which side reads trust is a correctness risk, not just a
documentation gap.

🟡 Flag a new dual-write (a repository method that writes to Postgres and
also calls out to a Redis/Mongo store in the same method) that has no
comment or design-doc reference explaining why the mirror exists — every
existing one (`RedisRefreshTokenStore`, the Redis L2 thumbnail cache) is
tied to a named change (`redis-refresh-tokens`, `redis-thumbnail-cache`) with
a stated reason. An undocumented dual-write is hard for a future migration to
reason about — nobody can tell if dropping the Postgres column would break
the Redis mirror's contract, or vice versa.

🟡 Flag a schema change to a table whose data has previously lived in a
different store (per the migration history called out in
`JPPhotoManagerWeb/CLAUDE.md`) without checking whether the change should
also update that narrative — see the `web-docs-sync` skill. A reviewer
who only checks the migration file in isolation can miss that the change
continues or contradicts a documented prior migration between stores.

🟢 Suggest a `MongoIndexInitializer`-style startup-ensured index (compound
key + TTL, as used for `asset_audit_log`) when a new Mongo-backed collection
is introduced without one — Mongo has no Flyway-equivalent migration
tracking, so indexes need an explicit ensure-on-startup mechanism or they
simply won't exist outside whatever environment they were manually created
in.
