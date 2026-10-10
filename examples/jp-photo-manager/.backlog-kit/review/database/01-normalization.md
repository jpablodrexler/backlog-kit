# Normalization
Read when: a migration adds a table or column

## 1. Normalization

🔴 Flag a new column that duplicates data already derivable from a join
(e.g., storing `folder_path` directly on `assets` when `assets.folder_id →
folders.path` already gives it) — the two can drift out of sync on update.

🟡 Flag a repeating group implemented as multiple similarly-named columns
(`tag_1`, `tag_2`, `tag_3`) instead of a join table — the project's own
`tags`/`asset_tags` (`V13__create_tags_tables.sql`) is the reference pattern
for a proper many-to-many.

🟡 Flag a new many-to-many relationship modeled as a comma-separated or JSON
list of IDs in a single column instead of a join table, unless the values are
genuinely never queried/filtered individually (e.g. `albums.filter_json` in
`V18__add_smart_albums.sql` is opaque application-defined criteria, not a set
of foreign keys, so JSONB is the right call there — don't flag that as a
normalization violation).

🟢 Flag over-normalization: a lookup table with a fixed, small (<10), rarely
changing set of values that's only ever referenced from one table might be
better as a `CHECK` constraint or enum column (see `ProcessingStatus`,
`FileType`, `ImageRotation` — all stored as `VARCHAR` + `@Enumerated(STRING)`,
not as separate lookup tables — that's the project's existing convention for
small closed sets).
