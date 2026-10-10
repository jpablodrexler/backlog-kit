# Column naming and data types
Read when: a migration adds or changes a table, column, key, index or policy

## 2. Column Naming & Data Types

### 2.1 Naming

| Element                | Expected                                          | Example                                    |
| ------------------------ | ---------------------------------------------------- | ---------------------------------------------- |
| Table                   | `snake_case`, singular (this project's existing convention — see `public.task`, not `public.tasks`) | `task`                        |
| Primary key column      | `id`, `uuid DEFAULT gen_random_uuid()`               | `task.id`                                    |
| Foreign key column      | `{referenced_table_singular}_id`                     | `task.user_id` referencing `auth.users (id)` |
| Boolean column          | `is_`/`has_` prefix or a clearly boolean noun         | `is_done`                                    |
| Timestamp column        | `_at` suffix, `timestamp with time zone`              | `created_at`                                 |
| Policy name             | A plain-English sentence in double quotes (Supabase/Postgres convention, not a short identifier) | `"Individuals can view their own tasks"` |
| Index name              | `{table}_{column(s)}_idx` (Postgres/Supabase default naming when unspecified) | `task_user_id_idx`     |

**Known drift to watch for:** the primary-key convention here is bare `id`
(not `task_id`) — this is the Supabase CLI/dashboard default and is fine;
don't flag `id` as a naming violation the way a `{table}_id` convention
elsewhere might suggest. Do flag a *foreign key* column that isn't named
`{referenced_table_singular}_id` (e.g. `task.owner` instead of
`task.user_id`).

### 2.2 Data types

🟡 Flag `timestamp` (no time zone) on a new column — every existing
timestamp column in this schema (`task.created_at`) uses
`timestamp with time zone DEFAULT now()`; stay consistent.

🟡 Flag `text` used for a column with a genuine natural bound where a
`CHECK` constraint on length would catch bad input early — but don't
require `varchar(n)` purely for its own sake; Postgres (and Supabase's own
schema conventions) treat `text` as the default free-form type, unlike a
project with a fixed `varchar(255)` house style.

🟡 Flag a foreign key column whose type doesn't match its referenced PK's
type exactly (e.g. anything other than `uuid` referencing `auth.users.id`,
which is `uuid`).

🟡 Flag a new enum-like status column stored as free-text without a
`CHECK` constraint to constrain its value set (e.g. a hypothetical `status
text` column with no `CHECK (status IN (...))` — invalid strings will
silently persist).
