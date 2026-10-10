# Indexes
Read when: a migration adds a table, a foreign key or an index, or a query's filter or sort changes

## 3. Indexes

### 3.1 Coverage for foreign keys

🔴 Flag any new foreign-key column that has no index. Postgres does **not**
auto-index FK columns. **Known gap in this schema:** `task.user_id`
(`REFERENCES auth.users (id)`, added in `task_user_scoping.sql`) currently
has no index — since every RLS policy on `task` filters `WHERE auth.uid() =
user_id` (see §4), **every single query against this table is an implicit
`user_id` filter**, and without an index it's a full table scan under RLS
even for a query that looks unfiltered from the frontend's point of view
(`TasksService.getTasks()`'s plain `.select('*')` still gets `user_id =
auth.uid()` appended by Postgres via the policy). Flag this as 🔴 if still
true when reviewing this table, and treat "add a foreign-key column with no
index" as a standing 🔴 for any future table, not just this one.

### 3.2 Coverage for query predicates

🔴 Flag a column that appears in a service's `.eq()`/`.match()`/`.order()`
call (or, equivalently, in an RLS policy's `USING`/`WITH CHECK` expression
— see §3.1) on a table with a non-trivial expected row count, with no
supporting index.

🟡 Flag a query that filters or sorts on a column covered only by a
*composite* index where the queried column isn't the leftmost member.

🟡 Flag a `.ilike()`/`.like()` prefix query (`value%`, no leading `%`)
against an unindexed `text` column — a plain B-tree index still helps a
left-anchored pattern.

🟢 Flag a `.ilike()` query with a leading wildcard (`%value%`) and note
that a plain B-tree index cannot help it — a `pg_trgm` GIN index would be
the fix, but only worth flagging as a suggestion since it's a bigger
infrastructure change than a routine index addition.

### 3.3 Partial and covering indexes

🟢 Suggest a partial index (`WHERE` clause on the `CREATE INDEX` itself)
when a boolean/nullable column is queried almost exclusively for one value.

🟢 Flag redundant indexes: two indexes on the same table where one's column
list is a strict prefix of the other's.
