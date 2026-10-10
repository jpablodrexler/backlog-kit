# Database context and workflow specifics
Read when: every review

Review the PostgreSQL schema of the JPPhotoManager web backend: Flyway
migrations (`backend/src/main/resources/db/migration/`), JPA entities
(`infrastructure/persistence/entity/`), and the queries issued against them
(`infrastructure/persistence/jpa/*Repository.java`,
`infrastructure/persistence/adapter/*RepositoryImpl.java`). `asset_exif` and
`asset_audit_log` live in MongoDB and `refresh_tokens` is mirrored into Redis
— both are out of scope for this skill (schema-less/NoSQL); review those with
`java-developer`'s conventions instead, not this one.

## Workflow (project specifics)

2. Read every migration file in scope **in filename order** (`V{n}__*.sql`,
   sorted numerically, not alphabetically — `V9` comes before `V10`) — schema
   history is cumulative, so a column added in `V7` may be altered in `V14`
   and indexed in `V32`; reviewing a migration in isolation misses that.
3. For each table touched, find every repository method (`@Query`,
   Spring-Data derived query, or native query) that reads or writes it, and
   check whether the query's `WHERE`/`JOIN`/`ORDER BY`/`GROUP BY` columns are
   covered by an actual index (§3) — not just plausible-looking ones.
4. Cross-check `@Table(indexes = ...)` / `@Index` annotations on the JPA
   entity against what the migrations actually created (§3.4) — Hibernate
   `ddl-auto` is `validate`/`none` in this project, so entity-level index
   annotations are metadata only; they do not create anything, and can drift
   silently from the real schema.

## Severity levels (project wording)

| Level             | Meaning                                                                                     |
| ----------------- | --------------------------------------------------------------------------------------------- |
| 🔴 **CRITICAL**   | Data integrity risk, a query that will corrupt or silently drop data, or a full table scan on a hot path at current/expected row counts. Must be fixed before merging. |
