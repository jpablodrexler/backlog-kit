kit: skills/feature-plan
sub: JPPhotoManagerWeb/docs/backlog => <backlog>
sub: docs/backlog => <backlog>

PARAM | name: feature-plan description: Adds a new feature to <backlog>/featur | description: the project path becomes 'the backlog's features-planned.md' (a description is shown where <backlog> is undefined); `version` is the kit's
DROPPED | **Layout**: `features-planned.md` and `features-implemented.md` hold o | J-only paragraph; it spells out J's column order (Summary, Brief before SDD Artifacts), which D12 replaces by the other project's order. The same facts are in the skeleton and step 2
DROPPED | **If `features-planned.md` doesn't exist yet**, create it before conti | J variant of the 'create the file' paragraph; kit follows the other project, which gives the full skeleton inline (D12 order)
DROPPED | **If `features-implemented.md` doesn't exist yet either**, create it w | J variant; kit follows the other project's full skeleton, which includes the migration table (D13)
PARAM | Both are needed to pick a non-colliding number and name (step 3) and t | J variant of the closing sentence of step 2; kit follows the other project's wording
PARAM | Run `python3 .claude/skills/feature-plan/scripts/next_id.py <repo-root | script path is relative to the skill's base directory in a plugin
DROPPED | - **Area** (`Backend`/`Frontend`/`Full-stack`/`Infra`) | Area values differ between the projects; the legend of the backlog file defines them (D5)
PARAM | If the user explicitly gave a value for any of these, use it as-is (st | the example inference is rephrased without stack names ('Supabase migration', 'Angular component', 'RLS'); J's version cites project history ('the 37 rows added when these columns were introduced')
PARAM | **Full brief.** Write one dense paragraph in the same style as existin | stack names removed from the examples (tables/columns, endpoints, components, libraries) and the project's documented conventions are read from CLAUDE.md/README instead of being listed here
PARAM | ### 9. Display confirmation | J has no recommended-order step (D14), so its confirmation step is numbered 9; the kit keeps the other project's step 9 and numbers this one 10
PARAM | **#<number> `<change-name>`** added to features-planned.md, brief writ | J's confirmation line has no 'inserted into the recommended implementation order' part (D14)
PARAM | - Never edit `features-implemented.md` — this skill only adds rows to | J variant; kit follows the other project, which also allows creating the skeleton
PARAM | - Never write to `features-planned.md` or `features/` before the user | J's stricter wording (the brief file is a write too), merged into the other project's sentence that keeps the skeleton exception
PARAM | - Do not add a row to the **Deployment (migration) dependencies** tabl | 'which Supabase migration timestamp implements it' becomes 'which migration implements it'
PARAM | name: feature-plan description: Adds a new feature to <backlog>/featur #2 | description: the project path becomes 'the backlog's features-planned.md' (a description is shown where <backlog> is undefined); `version` is the kit's
PARAM | - **Schema Change**: `Yes` if the feature adds/alters a Supabase migra | legend wording without stack names: 'a database migration, a schema definition or an access policy'
DROPPED | - **Area**: `Frontend` (Angular-only change) · `Supabase` (migration/R | Area legend of the first project is tied to its stack; the scaffold default is the generic four-value list (Backend, Frontend, Full-stack, Infra) from the other project's backlog legend (D5)
PARAM | Run `python3 .claude/skills/feature-plan/scripts/next_id.py <repo-root #2 | script path is relative to the skill's base directory in a plugin
DROPPED | - **Area** (`Frontend`/`Supabase`/`Full-stack`) — there is no separate | project-specific explanation of the Area values (no backend service in that project); step 4 says the legend defines the values (D5)
PARAM | If the user explicitly gave a value for any of these, use it as-is (st #2 | the example inference is rephrased without stack names ('Supabase migration', 'Angular component', 'RLS'); J's version cites project history ('the 37 rows added when these columns were introduced')
PARAM | **Full brief.** Write one dense paragraph in the same style as existin #2 | stack names removed from the examples (tables/columns, endpoints, components, libraries) and the project's documented conventions are read from CLAUDE.md/README instead of being listed here
PARAM | - Never write to `features-planned.md` before the user has confirmed t | also covers the brief file under features/ (J's stricter wording)
PARAM | - Do not add a row to the **Deployment (migration) dependencies** tabl #2 | 'which Supabase migration timestamp implements it' becomes 'which migration implements it'
