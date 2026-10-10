kit: skills/bugs-next
sub: JPPhotoManagerWeb/docs/backlog => <backlog>
sub: docs/backlog => <backlog>

PARAM | name: bugs-next description: Recommends which bug to fix next based on | description: project path removed ('the backlog's bugs-open.md'); `author` removed (the plugin manifest carries it), `version` is the kit's
PARAM | `scripts/rank_bugs.py` owns steps 2-3's mechanical work — collecting O | script run from the skill's base directory; the ranking parenthetical says 'deployed (not local-only) environment' (decision D6: any Environment other than `local` earns the bonus)
PARAM | python3 .claude/skills/bugs-next/scripts/rank_bugs.py <repo-root> | script path is relative to the skill's base directory in a plugin
DROPPED | - `environment` — `local` / `deployed` / `both` | environment values differ (P: local/prod/both, J: local/deployed/both); the bullet says only `local` means not deployed and the backlog's legend defines the rest (decision D6)
PARAM | - `schema` — `true` if the bug's details file `<backlog>/bugs/BUG-NNN. | the schema flag comes from an explicit `- **Schema change:** yes` line in the details file instead of a regex over its text (P: `migration|RLS`, J: `Flyway|migration|JPA entity`) — decision D3
PARAM | **Tier 2 — Environment bonus.** Add +20 if `environment` is `deployed` | the bonus applies to any Environment other than `local` (decision D6)
PARAM | **Tier 4 — No schema change bonus.** Add +5 if `schema` is `false` — n | 'Flyway migration' / 'Supabase migration' becomes 'migration'
PARAM | name: bugs-next description: Recommends which bug to fix next based on #2 | description: project path removed ('the backlog's bugs-open.md'); `author` removed (the plugin manifest carries it), `version` is the kit's
PARAM | `scripts/rank_bugs.py` owns steps 2-3's mechanical work — collecting O #2 | script run from the skill's base directory; the ranking parenthetical says 'deployed (not local-only) environment' (decision D6: any Environment other than `local` earns the bonus)
PARAM | Read `<backlog>/bugs-open.md` in full (the table rows only — per-bug d | P variant of step 1, which mentions the schema flag in a different way; kit follows J (the schema flag is read from the details file, decision D3)
DROPPED | - `id` — the `Bug ID` column value (e.g. `BUG-004`) | P variant of the id bullet; kit follows J, which also says to take the link text
DROPPED | - `environment` — `local` / `prod` / `both` | environment values differ (P: local/prod/both, J: local/deployed/both); the bullet says only `local` means not deployed and the backlog's legend defines the rest (decision D6)
DROPPED | - `schema` — `true` if the bug's details file `<backlog>/bugs/BUG-NNN. #2 | the schema flag comes from an explicit `- **Schema change:** yes` line in the details file instead of a regex over its text (P: `migration|RLS`, J: `Flyway|migration|JPA entity`) — decision D3
PARAM | **Tier 2 — Environment bonus.** Add +20 if `environment` is `prod` or | the bonus applies to any Environment other than `local` (decision D6)
PARAM | **Tier 4 — No schema change bonus.** Add +5 if `schema` is `false` — n #2 | 'Flyway migration' / 'Supabase migration' becomes 'migration'
PARAM | - <tier reason, e.g. "S1 — RLS leak, blocks release" or "S2, reproduce | P variant of the example reason (names an RLS leak); kit follows J (auth bypass / deployed stack)
