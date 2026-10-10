kit: skills/decision-record
sub: JPPhotoManagerWeb/docs/decisions => <decisions>
sub: docs/decisions => <decisions>

PARAM | name: decision-record description: >- Records a lightweight Architectu | description: the decisions folder is not named by path, the example ADR is neutral (no project or tool names), and the closing reference points at the section 'Relationship to reference docs' (second project's wording; the first names its own docs-sync skill); `author` removed, `version` is the kit's
PARAM | JPPhotoManagerWeb — what was decided, what alternatives were rejected | the README skeleton says 'this project' instead of the project's name
PARAM | current-state reference material (that's `docs/architecture.md`, | reference docs are named generically ('the reference docs under docs/') instead of listing each project's files
PARAM | `docs/backend.md`, etc.); a decision recorded here stays as-written ev | see the previous entry
PARAM | Short, descriptive, no filler words — e.g. `keep-zone-based-cypress-mo | example slugs are neutral (`reject-library-x-licensing`, `no-environment-split`) instead of either project's own decisions
PARAM | `<decisions>/` is out of scope for the reference docs under `JPPhotoMa | path of the reference docs made generic
PARAM | - **The reference docs** (`docs/architecture.md`, `docs/backend.md`, ` | the list of reference docs is generic ('for example docs/architecture.md')
PARAM | name: decision-record description: >- Records a lightweight Architectu #2 | description: the decisions folder is not named by path, the example ADR is neutral (no project or tool names), and the closing reference points at the section 'Relationship to reference docs' (second project's wording; the first names its own docs-sync skill); `author` removed, `version` is the kit's
PARAM | pablo-web — what was decided, what alternatives were rejected and why, | same: 'this project'; the first project's pointer to its own documentation table is project-specific
DROPPED | reference material (that's `docs/architecture.md`, `docs/database.md`, | first project's variant of the same sentence; kit follows the second project's generic wording
DROPPED | etc. — see the root `README.md`'s Documentation table); a decision rec | first project's variant of the same sentence (its own documentation table)
PARAM | Short, descriptive, no filler words — e.g. `reject-primeng-licensing`, | example slugs are neutral (`reject-library-x-licensing`, `no-environment-split`) instead of either project's own decisions
PARAM | about the topic, run `web-docs-sync` separately — this skill only reco | first project names its own docs-sync skill; the kit says 'sync those files separately' (second project's wording)
PARAM | ## Relationship to `web-docs-sync` | heading follows the second project: 'Relationship to reference docs'
PARAM | `<decisions>/` is **out of scope for `web-docs-sync`**, the same way ` | second project's generic wording
PARAM | - **`web-docs-sync`** keeps the *current-state* narrative in `CLAUDE.m | second project's generic wording ('The reference docs')
