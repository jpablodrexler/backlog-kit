kit: extras/code-reviewer
sub: JPPhotoManagerWeb/docs/backlog => <backlog>
sub: docs/backlog => <backlog>
sub: JPPhotoManagerWeb/docs/reports => <reports>
sub: docs/reports => <reports>
FILE | pablo-web/code-reviewer/reference/architecture-components-routing.md | stack-specific checklist or metrics reference: moved, text unchanged, to the project's `.backlog-kit/review/` files (D30); see examples/
FILE | pablo-web/code-reviewer/reference/frontend-testing-crosscutting.md | stack-specific checklist or metrics reference: moved, text unchanged, to the project's `.backlog-kit/review/` files (D30); see examples/
FILE | pablo-web/code-reviewer/reference/i18n-and-layout.md | stack-specific checklist or metrics reference: moved, text unchanged, to the project's `.backlog-kit/review/` files (D30); see examples/
FILE | pablo-web/code-reviewer/reference/metrics-complexity-coverage-types.md | stack-specific checklist or metrics reference: moved, text unchanged, to the project's `.backlog-kit/review/` files (D30); see examples/
FILE | pablo-web/code-reviewer/reference/metrics-deadcode-lighthouse-a11y.md | stack-specific checklist or metrics reference: moved, text unchanged, to the project's `.backlog-kit/review/` files (D30); see examples/
FILE | pablo-web/code-reviewer/reference/metrics-mutation-security.md | stack-specific checklist or metrics reference: moved, text unchanged, to the project's `.backlog-kit/review/` files (D30); see examples/
FILE | pablo-web/code-reviewer/reference/pitfalls.md | stack-specific checklist or metrics reference: moved, text unchanged, to the project's `.backlog-kit/review/` files (D30); see examples/
FILE | pablo-web/code-reviewer/reference/supabase-auth-state.md | stack-specific checklist or metrics reference: moved, text unchanged, to the project's `.backlog-kit/review/` files (D30); see examples/
FILE | jp-photo-manager/code-reviewer/reference/architecture-layering.md | stack-specific checklist or metrics reference: moved, text unchanged, to the project's `.backlog-kit/review/` files (D30); see examples/
FILE | jp-photo-manager/code-reviewer/reference/backend-async-naming-testing.md | stack-specific checklist or metrics reference: moved, text unchanged, to the project's `.backlog-kit/review/` files (D30); see examples/
FILE | jp-photo-manager/code-reviewer/reference/backend-spring.md | stack-specific checklist or metrics reference: moved, text unchanged, to the project's `.backlog-kit/review/` files (D30); see examples/
FILE | jp-photo-manager/code-reviewer/reference/crosscutting-and-pitfalls.md | stack-specific checklist or metrics reference: moved, text unchanged, to the project's `.backlog-kit/review/` files (D30); see examples/
FILE | jp-photo-manager/code-reviewer/reference/frontend-angular.md | stack-specific checklist or metrics reference: moved, text unchanged, to the project's `.backlog-kit/review/` files (D30); see examples/
FILE | jp-photo-manager/code-reviewer/reference/frontend-typescript-naming-cypress.md | stack-specific checklist or metrics reference: moved, text unchanged, to the project's `.backlog-kit/review/` files (D30); see examples/
FILE | jp-photo-manager/code-reviewer/reference/metrics-complexity-coverage.md | stack-specific checklist or metrics reference: moved, text unchanged, to the project's `.backlog-kit/review/` files (D30); see examples/
FILE | jp-photo-manager/code-reviewer/reference/metrics-mutation-security.md | stack-specific checklist or metrics reference: moved, text unchanged, to the project's `.backlog-kit/review/` files (D30); see examples/
FILE | jp-photo-manager/code-reviewer/reference/metrics-types-deadcode-lighthouse-a11y.md | stack-specific checklist or metrics reference: moved, text unchanged, to the project's `.backlog-kit/review/` files (D30); see examples/

PARAM | name: code-reviewer description: > Code review skill for the JPPhotoMa | description rewritten stack-free (TRIGGER structure kept); `scope` removed, `version` is the kit's (D30)
DROPPED | Review code in the JPPhotoManager project against its documented archi | second project's variant of this text; the kit follows the first project
PARAM | 1. Identify the **scope**: a full-codebase sweep of the whole web appl | second project's variant of this text; the kit follows the first project
PARAM | - **Scoped review** → follow steps 2–6 below as a single pass, produci | second project's variant of this text; the kit follows the first project
DROPPED | 2. Identify which sub-project(s) are affected: **backend** (Java), **f | second project's variant of this text; the kit follows the first project
DROPPED | 4. Load the reference file(s) from the index at the end of this file t | second project's variant of this text; the kit follows the first project
DROPPED | 6. Summarise with a short verdict and the top action items. | second project's variant of this text; the kit follows the first project
PARAM | When asked to review all the code in the web application (or the entir | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Layer key ¦ Report suffix ¦ Directory scope ¦ Primary checklist sect | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ ------------------------ ¦ ----------------------- ¦ --------------- | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Backend domain ¦ `backend-domain` ¦ `backend/.../domain/**` ¦ §1.1, | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Backend application ¦ `backend-application` ¦ `backend/.../applicati | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Backend api ¦ `backend-api` ¦ `backend/.../infrastructure/web/**` (c | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Backend infrastructure ¦ `backend-infrastructure` ¦ `backend/.../inf | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Frontend core ¦ `frontend-core` ¦ `frontend/src/app/core/**` ¦ §10.2 | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Frontend features ¦ `frontend-features` ¦ `frontend/src/app/features | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Frontend shared ¦ `frontend-shared` ¦ `frontend/src/app/shared/**` ¦ | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Cross-cutting ¦ `cross-cutting` ¦ Both sub-projects; no single direc | second project's variant of this text; the kit follows the first project
DROPPED | If only the backend (or only the frontend) is in scope, skip the layer | second project's variant of this text; the kit follows the first project
DROPPED | **What goes in the cross-cutting report:** findings that don't belong | second project's variant of this text; the kit follows the first project
DROPPED | Each layer's review runs in its own subagent (`Agent` tool, `subagent_ | second project's variant of this text; the kit follows the first project
PARAM | 2. The remaining applicable layers are independent of each other (no l | second project's variant of this text; the kit follows the first project
PARAM | - The layer key, its directory scope, and its primary checklist sectio | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | - An instruction to first read `.claude/skills/code-reviewer/SKILL.md` | second project's variant of this text; the kit follows the first project
PARAM | - A short return-message instruction: report back the Critical/Warning | second project's variant of this text; the kit follows the first project
PARAM | 5. Once every dispatched subagent has completed, give a short in-chat | second project's variant of this text; the kit follows the first project
PARAM | ¦ 🔴 **CRITICAL** ¦ Breaks correctness, data integrity, or security. Mu | second project's variant of this text; the kit follows the first project
PARAM | ## Reference index | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | The checklist sections live under `reference/`, split so a review load | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | ¦ Sections ¦ Read when you're reviewing… ¦ File ¦ | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | ¦ -------- ¦ ---------------------------- ¦ ---- ¦ | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | ¦ §1 Architecture & layering (backend and frontend) ¦ new/moved files | second project's variant of this text; the kit follows the first project
DROPPED | ¦ §2-6 Backend: Spring proxy pitfalls, annotations & boilerplate, tran | second project's variant of this text; the kit follows the first project
DROPPED | ¦ §7-9 Backend: async & SSE, naming conventions, testing ¦ `@Async`/SS | second project's variant of this text; the kit follows the first project
DROPPED | ¦ §10 Frontend: Angular conventions (including Material layout gotchas | second project's variant of this text; the kit follows the first project
DROPPED | ¦ §11-13 Frontend: TypeScript conventions, naming, Cypress tests ¦ fro | second project's variant of this text; the kit follows the first project
DROPPED | ¦ §14-15 Cross-cutting comments & code style, known project-specific p | second project's variant of this text; the kit follows the first project
DROPPED | ¦ §18-19 Cyclomatic complexity, code coverage (both sub-projects) ¦ a | second project's variant of this text; the kit follows the first project
DROPPED | ¦ §20-23 Type coverage, dead code, performance & accessibility (Lighth | second project's variant of this text; the kit follows the first project
DROPPED | ¦ §24-25 Mutation testing, secrets scanning, license compliance, depen | second project's variant of this text; the kit follows the first project
PARAM | _Part of the `code-reviewer` skill — see `../SKILL.md` for the topic i | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | - `path/to/File.java:42` — <issue description> | second project's variant of this text; the kit follows the first project
PARAM | - `path/to/file.ts:15` — <issue description> | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | - `path/to/File.java:88` — <issue description> | second project's variant of this text; the kit follows the first project
PARAM | - **Path:** `<reports>/code-review/CODE_REVIEW_FINDINGS_{YYYY-MM-DD}.m | second project's variant of this text; the kit follows the first project
PARAM | - **Path:** `<reports>/code-review/CODE_REVIEW_FINDINGS_{YYYY-MM-DD}_{ | second project's variant of this text; the kit follows the first project
PARAM | - **Content:** the same Critical/Warnings/Suggestions grouping as the | second project's variant of this text; the kit follows the first project
PARAM | - **Scope of content:** write only what was actually found in *this* r | second project's variant of this text; the kit follows the first project
PARAM | ## 17. Fix Workflow | second project's variant of this text; the kit follows the first project
PARAM | 2. List every report file for that date (there may be several `-2`/`-3 | second project's variant of this text; the kit follows the first project
PARAM | 3. **If exactly one report remains**, use it directly — don't make the | second project's variant of this text; the kit follows the first project
DROPPED | 1. Read the full report before asking anything, so the menu of categor | second project's variant of this text; the kit follows the first project
DROPPED | 2. Do not silently pick a starting point or scope. Ask the user whethe | second project's variant of this text; the kit follows the first project
DROPPED | - An entire severity category (🔴 Critical, 🟡 Warning, or 🟢 Suggestion) | second project's variant of this text; the kit follows the first project
DROPPED | - A specific finding — let them name it, or list the still-unchecked f | second project's variant of this text; the kit follows the first project
DROPPED | Only offer categories/findings that still have unchecked (`- [ ]`) box | second project's variant of this text; the kit follows the first project
PARAM | ### 17.3 Fix loop | second project's variant of this text; the kit follows the first project
DROPPED | 1. Read the affected file(s) and understand the finding in the full co | second project's variant of this text; the kit follows the first project
DROPPED | 2. Apply the fix. The report tells you what's wrong; the checklist sec | second project's variant of this text; the kit follows the first project
PARAM | 3. If a fix hinges on a real design decision rather than just applying | second project's variant of this text; the kit follows the first project
DROPPED | 4. Verify the fix before moving on: compile/build, then run the narrow | second project's variant of this text; the kit follows the first project
PARAM | 6. Mark the finding complete in the report file immediately, not batch | second project's variant of this text; the kit follows the first project
DROPPED | - `**Evaluated, no change made:** <rationale>` — for findings where, a | second project's variant of this text; the kit follows the first project
PARAM | 7. If fixing one finding incidentally resolves another still-unchecked | second project's variant of this text; the kit follows the first project
DROPPED | After finishing the selected scope, run the widest verification availa | second project's variant of this text; the kit follows the first project
DROPPED | - If the current report still has unchecked findings, repeat from §17. | second project's variant of this text; the kit follows the first project
DROPPED | - If the current report is now fully checked off, go back to §17.1 — r | second project's variant of this text; the kit follows the first project
PARAM | ### 17.5 Never commit | second project's variant of this text; the kit follows the first project
PARAM | name: code-reviewer description: > Code review skill for the pablo-web | description rewritten stack-free (TRIGGER structure kept); `scope` removed, `version` is the kit's (D30)
DROPPED | Review code in the pablo-web project against its documented architectu | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | 1. Identify the **scope**: a full-codebase sweep of the whole frontend | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | 3. Load the reference file(s) from the index at the end of this file t | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | When asked to review all the frontend code, don't produce one giant co | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | ¦ ---------------- ¦ ------------------ ¦ ---------------------------- | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Frontend core ¦ `frontend-core` ¦ `frontend/src/app/core/**` ¦ §1.1, | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Frontend features ¦ `frontend-features` ¦ `frontend/src/app/<feature | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Frontend shared ¦ `frontend-shared` ¦ `frontend/src/app/shared/**` ¦ #2 | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Cross-cutting ¦ `cross-cutting` ¦ Whole frontend; no single director | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | - An instruction to first read `.claude/skills/code-reviewer/SKILL.md` #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | ¦ 🔴 **CRITICAL** ¦ Breaks correctness or data integrity (including an | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | ¦ §1-3 Architecture & layering, standalone components, routing ¦ new/m | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ §4-6 Supabase service usage, auth/session state, component state & s | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ §7-9 Frontend conventions, testing (Cypress), cross-cutting style ¦ | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ §10 Known pitfalls table ¦ **every review** — scan it as the final p | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ §13, §14, §25 Localization (i18n), layout & app-shell gotchas (Optim | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ §15-17 Cyclomatic complexity, code coverage, type coverage ¦ a metri | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ §18-20 Dead code, performance & accessibility (Lighthouse), deep acc | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ §21-24 Mutation testing, secrets scanning, license compliance, depen | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | - `path/to/file.ts:42` — <issue description> | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | - `path/to/file.ts:88` — <issue description> | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | - **Path:** `<reports>/code-review/CODE_REVIEW_FINDINGS_{YYYY-MM-DD}.m #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | 4. Verify the fix: run the narrowest relevant test scope (`npx ng test | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | After finishing the selected scope, run the widest verification availa #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
