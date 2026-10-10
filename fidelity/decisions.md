# Fidelity decisions

Every point where the kit's skills differ from the source projects' skills because something became
configurable, was removed, or was changed on purpose is recorded here with the owner's answer.
`fidelity/ledgers/<skill>.md` links each edited paragraph to one of these ids.

| Id | Question | Answer | Date |
| --- | --- | --- | --- |
| D1 | `Schema Change` (Yes/No) column in the planned and implemented tables: fixed or optional? | **Fixed**, as in both source projects. No config key. | 2026-10-10 |
| D2 | `features-next` tier 4: the original +5 for "no schema change", or the kit's own +5 for smallest effort? | **Original.** The effort bonus is removed. | 2026-10-10 |
| D3 | How `bugs-next` knows a bug's fix needs a schema change (the projects use different regexes over the details file) | **An explicit line** `- **Schema change:** yes\|no` in the bug's details file; no regex. `bug-report` writes it (done when `bug-report` is converted). | 2026-10-10 |
| D4 | Priority (P0–P3), Effort (S/M/L) and Severity (S1–S4) vocabularies: configurable or fixed? | **Fixed**, as in both projects. The config keys `priorities`, `priority_labels`, `efforts`, `severities`, `severity_labels` go away once every planning skill that reads them is converted. | 2026-10-10 |
| D5 | Area vocabulary (differs between the projects) | **The legend of the backlog file defines it.** No config key. | 2026-10-10 |
| D6 | Environment vocabulary (`prod` vs `deployed`) and the +20 bonus | **Any Environment other than `local`** earns the bonus. No config keys. | 2026-10-10 |
| D7 | A hard dependency whose prerequisite has no row in the planned table | **As the originals:** counts as shipped; the script also checks features-implemented.md and **warns** when the number is in neither file. | 2026-10-10 |
| D8 | `--confirmed` batch mode (skips the per-item question) | **Removed.** Every item is confirmed by the user, also inside a batch, as in the source projects. | 2026-10-10 |
| D9 | Where the snapshots of the originals live | **In the kit while it is private**; revisit before publishing (the text of the projects' skills must not be published without the owner's say). | 2026-10-10 |
| D10 | Explore command named in `features-next` (`/opsx:explore` in one project, `/openspec-explore` in the other) | Both are named; the skill says "whichever your OpenSpec install generated". Wording only, no config key. | 2026-10-10 |

Not asked (not configurable, taken from the more complete original): order lists accept numbered and
link forms (J's `bugs-next`); `features-next` reads `SDD Artifacts` from the cell only (no disk check).
