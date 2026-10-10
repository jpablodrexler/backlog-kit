kit: skills/features-next
sub: JPPhotoManagerWeb/docs/explorations => <explorations>
sub: JPPhotoManagerWeb/docs/backlog => <backlog>
sub: docs/explorations => <explorations>
sub: docs/backlog => <backlog>

PARAM | name: features-next description: Recommends which feature to implement | description: the project paths become 'the backlog's features-planned.md' and 'the explorations folder' (a description is shown where <backlog> is undefined); `author` removed (the plugin manifest carries it), `version` is the kit's
PARAM | `scripts/rank_features.py` owns steps 2-4's mechanical work — collecti | adds 'from this skill's base directory': a plugin skill runs from its own folder, not .claude/skills/
PARAM | python3 .claude/skills/features-next/scripts/rank_features.py <repo-ro | script path is relative to the skill's base directory in a plugin
PARAM | 6. If the user picks an exploration, **stop here.** Do not collect or | explore command: `/opsx:explore` in P, `/openspec-explore` in J; the kit names both and says which one the project has (decision D10)
PARAM | - `area` — the **Area** column value (`Backend`/`Frontend`/`Full-stack | Area values differ between the projects; the backlog's own legend defines them (decision D5)
PARAM | - `brief` — the **Summary** column text (a short hand-written summary, | J variant of the Summary bullet; kit follows P (250-character limit)
DROPPED | - `brief_file` — the path of the feature's full brief, `<backlog>/feat | J variant of the brief_file bullet; kit follows P's wording, same meaning
PARAM | The `### Recommended implementation order` subsection lists features i | J variant of the Tier 3 paragraph (without the bullet-format detail); kit follows P
PARAM | name: features-next description: Recommends which feature to implement #2 | description: the project paths become 'the backlog's features-planned.md' and 'the explorations folder' (a description is shown where <backlog> is undefined); `author` removed (the plugin manifest carries it), `version` is the kit's
PARAM | 6. If the user picks an exploration, **stop here.** Do not collect or #2 | explore command: `/opsx:explore` in P, `/openspec-explore` in J; the kit names both and says which one the project has (decision D10)
PARAM | - `area` — the **Area** column value (`Frontend`/`Supabase`/`Full-stac | Area values differ between the projects; the backlog's own legend defines them (decision D5)
