kit: skills/features-archive
sub: JPPhotoManagerWeb/docs/backlog => <backlog>
sub: docs/backlog => <backlog>

PARAM | name: features-archive description: Mark features as implemented in <b | description: the project paths become 'the backlog's' files; `version` is the kit's
PARAM | d. **Fallback**: if no matches are found (all archived SDD changes eit | the second project's note about 'the size of this backlog' is project-specific; kit uses the first project's generic wording
PARAM | In the `<backlog>/features-planned.md` table find the matching row: fo | first project's example change name and the added brief-file check are kept (the second project's text lacks the check)
PARAM | Copy the full table row (the `¦` delimited line) for each selected fea | planned and implemented column lists follow the kit's skeleton (D12): planned `... Area | SDD Artifacts | Implementation | Summary | Brief`, implemented `... Area | Details`
PARAM | - **drop** the `Summary`, `Brief` and `Implementation` cells (an imple | second project keeps a trailing `SDD Artifacts` cell in the implemented table; the kit's skeleton (feature-plan, D12) has the 7-column implemented table of the first project, so `SDD Artifacts` is dropped as well
PARAM | - add the `Details` cell: `[brief](features/NNN-<change-name>.md) · [s | the spec link is written relative to the backlog folder (`../../openspec/...` for `docs/backlog`, `../../../openspec/...` for a deeper backlog) instead of the fixed depth of each project; the model computes it from `backlog_dir` (D15: no helper script)
DROPPED | - keep the `SDD Artifacts` cell (placed after `Details`, as the implem | see the drop of `SDD Artifacts` above (D12 skeleton)
PARAM | The finished row reads `¦ N ¦ `name` ¦ P ¦ Schema ¦ Effort ¦ Area ¦ [b | the finished row has no trailing `✅ Created` cell and the spec link is the computed relative path
PARAM | **Compute `IMPLEMENTED_SET`** (needed by steps 7 and 8): every `#` val | the example pair of feature numbers is generic ('Feature 4 → Feature 3') instead of project-specific numbers
PARAM | In the **Deployment (migration) dependencies** table, find the row(s) | 'Flyway migration' / 'Supabase migration' become 'migration' (D13: the table stays a fixed part of the backlog)
DROPPED | At the end of the `## Feature List` table in `<backlog>/features-imple | the first project's insertion rule ('right after its last row — rows are grouped by archive batch') replaces 'directly under the last existing row'
PARAM | - For a non-directional multi-feature heading with no prerequisite/dep | example heading made generic
PARAM | When resolved, apply this project's convention for marking that (`(pre | the annotation is `(prerequisite already implemented)` (D17); 'this project's convention' wording removed
PARAM | - **If an equivalent block already exists here** (a prior archive run | 'the project's convention' → the annotation named in D17; the 'pattern this project actually uses' aside is rephrased generically
PARAM | 2. Delete the dependency/note blocks extracted in step 5 — but **only | example of a multi-feature heading made generic; annotation per D17
PARAM | - **The rewrite happens in step 4's in-memory copy, not in `<backlog>/ | implemented row shape named per D12 (without SDD Artifacts/Implementation/Summary/Brief)
PARAM | - The **Priority**, **Schema Change**, **Effort**, and **Area** column | `SDD Artifacts` is dropped with the other planned-only cells (D12); the second project's note about older rows showing `—` is project history and is dropped
PARAM | name: features-archive description: Mark features as implemented in <b #2 | description: the project paths become 'the backlog's' files; `version` is the kit's
PARAM | d. **Fallback**: if no matches are found (all archived SDD changes eit #2 | the second project's note about 'the size of this backlog' is project-specific; kit uses the first project's generic wording
PARAM | In the `<backlog>/features-planned.md` table find the matching row: fo #2 | first project's example change name and the added brief-file check are kept (the second project's text lacks the check)
PARAM | Copy the full table row (the `¦` delimited line) for each selected fea #2 | planned and implemented column lists follow the kit's skeleton (D12): planned `... Area | SDD Artifacts | Implementation | Summary | Brief`, implemented `... Area | Details`
PARAM | - **drop** the `SDD Artifacts`, `Implementation`, `Summary` and `Brief | wording identical to the first project; listed because the second project's variant differs
PARAM | - add the `Details` cell: `[brief](features/NNN-<change-name>.md) · [s #2 | the spec link is written relative to the backlog folder (`../../openspec/...` for `docs/backlog`, `../../../openspec/...` for a deeper backlog) instead of the fixed depth of each project; the model computes it from `backlog_dir` (D15: no helper script)
PARAM | The finished row reads `¦ N ¦ `name` ¦ P ¦ Schema ¦ Effort ¦ Area ¦ [b #2 | the finished row has no trailing `✅ Created` cell and the spec link is the computed relative path
PARAM | **Compute `IMPLEMENTED_SET`** (needed by steps 7 and 8): every `#` val #2 | the example pair of feature numbers is generic ('Feature 4 → Feature 3') instead of project-specific numbers
PARAM | In the **Deployment (migration) dependencies** table, find the row(s) #2 | 'Flyway migration' / 'Supabase migration' become 'migration' (D13: the table stays a fixed part of the backlog)
PARAM | At the end of the `## Feature List` table in `<backlog>/features-imple #2 | the first project's insertion rule ('right after its last row — rows are grouped by archive batch') replaces 'directly under the last existing row'
DROPPED | - **If an equivalent block (same heading) doesn't already exist here** #2 | first project's shorter variant: it resolves a block only for `A → B` with the prerequisite shipped and writes `(resolved)`; the kit follows the second project's per-kind test and its annotation (D17)
DROPPED | - **If an equivalent block already exists here** (a prior archive run #2 | 'the project's convention' → the annotation named in D17; the 'pattern this project actually uses' aside is rephrased generically
PARAM | 2. Delete the dependency/note blocks extracted in step 5 — but **only #2 | example of a multi-feature heading made generic; annotation per D17
PARAM | - #<n> `<name>` — moved to <backlog>/features-implemented.md (Details: | summary line wording of the second project kept; the first project's '(Details: brief + spec link)' suffix is dropped
PARAM | - **The rewrite to the implemented shape happens in step 4's in-memory | implemented row shape named per D12 (without SDD Artifacts/Implementation/Summary/Brief)
DROPPED | - **Only the row moves.** The brief file `<backlog>/features/NNN-<chan | first project's version of the 'brief file never moves' guardrail; the second project's equivalent bullet is kept
DROPPED | **Otherwise, auto-detect from the archived SDD changes:** | OpenSpec is optional: the heading line is reworded to say so; behaviour unchanged
