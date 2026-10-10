kit: skills/bug-report
sub: JPPhotoManagerWeb/docs/backlog => <backlog>
sub: docs/backlog => <backlog>

PARAM | name: bug-report description: >- Adds a bug to <backlog>/bugs-open.md: | description: the project paths become 'the backlog's' files; `version` is the kit's
PARAM | A useful bug row needs, at minimum: what the user did, what they expec | the example symptom ('the gallery/expenses page is broken') is project-specific; kit says 'the page is broken'
PARAM | - **Severity**: `S1` (blocker — app unusable, data loss, security hole | legend without the stack-specific examples ('RLS leak', 'auth bypass'): 'security hole'
PARAM | - **Area**: the affected route, component, or backend area — e.g. `/ga | Area legend default without project names: route, component or backend area, with `db` for migration/schema/query bugs (combines both projects' legends); the backlog's own legend rules afterwards (D5)
PARAM | - **Environment**: `local` (reproduces on a local dev run only) · `dep | Environment legend default: `local` / `deployed` / `both` (the second project's generic wording); the backlog's own legend rules afterwards (D6)
PARAM | Bug ids are `BUG-NNN` with a zero-padded 3-digit sequence (`BUG-001`, | script path relative to the skill's base directory; the first project's 'historical quirk' note about BUG-070/071 is project history and is dropped
PARAM | - **Environment:** <local / deployed / both> — <browser / viewport / a | `prod` / `deployed` in the details-file template: kit uses `deployed` (D6); a `Schema change` line follows (D3)
PARAM | 2. If the list still reads `_No open bugs to order._`, the new bug bec | second project's numbered-list variant; kit follows the first project's plain bullet list (the second project's data also uses bullets)
DROPPED | 3. Renumber `1.`, `2.`, `3.`, … after inserting. | second project's skill text keeps a numbered list and renumbers; its data and the first project's skill use plain bullets, so there is nothing to renumber
PARAM | Before reporting success, run `python3 .claude/skills/bugs-status/scri | cross-skill script path: relative to this skill's base directory (`../bugs-status/scripts/...`) instead of `.claude/skills/...`
PARAM | **BUG-NNN — <title>** added to bugs-open.md (Severity <S?>, Area <area | second project's confirmation line; kit follows the first project's wording
PARAM | name: bug-report description: >- Adds a bug to <backlog>/bugs-open.md: #2 | description: the project paths become 'the backlog's' files; `version` is the kit's
PARAM | A useful bug row needs, at minimum: what the user did, what they expec #2 | the example symptom ('the gallery/expenses page is broken') is project-specific; kit says 'the page is broken'
PARAM | - **Severity**: `S1` (blocker — app unusable, data loss, security hole #2 | legend without the stack-specific examples ('RLS leak', 'auth bypass'): 'security hole'
PARAM | - **Area**: the affected route or module — e.g. `/expenses`, `/tasks`, | Area legend default without project names: route, component or backend area, with `db` for migration/schema/query bugs (combines both projects' legends); the backlog's own legend rules afterwards (D5)
PARAM | - **Environment**: `local` (reproduces on the dev server only) · `prod | Environment legend default: `local` / `deployed` / `both` (the second project's generic wording); the backlog's own legend rules afterwards (D6)
PARAM | Bug ids are `BUG-NNN` with a zero-padded 3-digit sequence (`BUG-001`, #2 | script path relative to the skill's base directory; the first project's 'historical quirk' note about BUG-070/071 is project history and is dropped
PARAM | - **Environment:** <local / prod / both> — <browser / viewport / accou | `prod` / `deployed` in the details-file template: kit uses `deployed` (D6); a `Schema change` line follows (D3)
