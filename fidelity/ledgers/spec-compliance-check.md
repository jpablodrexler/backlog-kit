kit: skills/spec-compliance-check
sub: JPPhotoManagerWeb/docs/backlog => <backlog>
sub: docs/backlog => <backlog>
sub: JPPhotoManagerWeb/docs/reports => <reports>
sub: docs/reports => <reports>

PARAM | name: spec-compliance-check description: > Verifies that a fully-imple | description rewritten stack-free (TRIGGER structure kept); `scope` removed, `version` is the kit's (D30)
PARAM | Read every file under `openspec/changes/<name>/specs/**/spec.md` (a ch | second project's variant of this text; the kit follows the first project
PARAM | - **WHEN** <action — usually a specific API call or UI interaction> | second project's variant of this text; the kit follows the first project
PARAM | Build a flat list of every Scenario across every spec file for this ch | second project's variant of this text; the kit follows the first project
PARAM | `tasks.md`'s test-writing tasks are usually worded closely enough to a | second project's variant of this text; the kit follows the first project
PARAM | 2. If found, open the test file/class that task's section header names | second project's variant of this text; the kit follows the first project
PARAM | 3. Record the test's fully-qualified name (class#method, or spec file | second project's variant of this text; the kit follows the first project
PARAM | Sometimes a scenario is already covered by a broader existing test (e. | second project's variant of this text; the kit follows the first project
DROPPED | For scenarios with no automated coverage — commonly true-visual claims | second project's variant of this text; the kit follows the first project
DROPPED | - **API-level scenarios:** issue the actual request with `curl`, follo | second project's variant of this text; the kit follows the first project
DROPPED | - **UI-level scenarios:** use the Cypress scratch-spec approach from ` | second project's variant of this text; the kit follows the first project
PARAM | - For a matched automated test (§4.1/§4.2), **run it** — the single te | second project's variant of this text; the kit follows the first project
PARAM | - For a manual check (§4.3), the check **is** the verification — there | second project's variant of this text; the kit follows the first project
PARAM | - **<Requirement title>** → *<Scenario title>* — `ClassName#testMethod | second project's variant of this text; the kit follows the first project
PARAM | - **<Requirement title>** → *<Scenario title>* — manual check: `curl . | second project's variant of this text; the kit follows the first project
PARAM | - **<Requirement title>** → *<Scenario title>* — `ClassName#testMethod #2 | second project's variant of this text; the kit follows the first project
PARAM | - **Running a test is read-only** (`mvn test`, `npx cypress run`) — th | second project's variant of this text; the kit follows the first project
PARAM | Read every file under `openspec/changes/<name>/specs/**/spec.md` (a ch #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | - **WHEN** <action — usually a specific Supabase query/RPC call or UI | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | Build a flat list of every Scenario across every spec file for this ch #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | `tasks.md`'s test-writing tasks are usually worded closely enough to a #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | 2. If found, open the test file that task's section header names (a `* | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | 3. Record the test's fully-qualified name (spec file + `it(...)` descr | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | Sometimes a scenario is already covered by a broader existing test (e. #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | For scenarios with no automated coverage — commonly true-visual claims #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | - **Data/RLS-level scenarios:** issue the actual request against the l | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | - **UI-level scenarios:** use the Cypress scratch-spec approach from ` #2 | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | - For a matched automated test (§4.1/§4.2), **run it** — the single sp | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | - For a manual check (§4.3), the check **is** the verification — there #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | - **<Requirement title>** → *<Scenario title>* — `task-list.cy.ts > it | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | - **<Requirement title>** → *<Scenario title>* — `task-list.cy.ts > it #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | - **Running a test is read-only** (`npx ng test`, `npx cypress run`) — | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
