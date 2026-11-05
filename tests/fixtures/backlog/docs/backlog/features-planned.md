# Planned Features

## Feature List

| # | Change name | Priority | Schema Change | Effort | Area | SDD Artifacts | Implementation | Summary | Brief |
| - | ----------- | -------- | ------------- | ------ | ---- | ------------- | -------------- | ------- | ----- |
| 2 | `dark-mode` | P1 | No | 3 | Frontend | ⬜ Pending | ⬜ Pending | Toggle between light and dark themes. | [brief](features/002-dark-mode.md) |
| 3 | `export-csv` | P2 | No | 5 | Backend | ⬜ Pending | 🔶 In Progress | Export the task list as CSV. | [brief](features/003-export-csv.md) |
| 4 | `team-sharing` | P0 | Yes | 8 | Backend | ⬜ Pending | ⬜ Pending | Share a list with other users. | [brief](features/004-team-sharing.md) |
| 5 | `share-links` | P1 | No | 2 | Frontend | ⬜ Pending | ⬜ Pending | Public read-only link to a list. | [brief](features/005-share-links.md) |

## Dependencies

### Hard implementation dependencies

**Feature 5 → Feature 4** (hard)

share-links needs team-sharing's permission model.

### Recommended implementation order

- `team-sharing` (#4)
- `dark-mode` (#2)
