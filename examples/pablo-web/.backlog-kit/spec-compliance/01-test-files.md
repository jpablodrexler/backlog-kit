# Test files and running a single test
Read when: matching a scenario to an automated test (§4.1/§4.2) or running a matched test (§5)

## 4.1 / 4.2 Test-file kinds

- Test files for a scenario are `*.cy.ts` files: a Cypress component test, or an E2E spec (see `cypress-unit-test-developer`/`e2e-suite`).
- Example of the §3 multi-capability change: a change to task filtering that also touches the existing task-list display spec.
- Example of a `WHEN` in this project: usually a specific Supabase query/RPC call or UI interaction.
- Example of a partially satisfied requirement: the happy path works but a validation-error or RLS-denial scenario under the same requirement doesn't.
- Example of a task-to-scenario match: a task *"Add test: signed-out user's `getTasks()` call rejects with an RLS error"* maps 1:1 to a spec's *"Scenario: Unauthenticated request is denied"*.
- §4.2: search `*.cy.ts` files for the component/service/behavior the scenario describes.
- Test's fully-qualified name: spec file + `it(...)` description (e.g. `task-list.cy.ts > it('...')`).

## 5. Running one test

- Run the single spec file: `npx cypress run --component --spec ...`, or `--e2e --spec ...` for an E2E spec.
- Running a test is read-only (`npx ng test`, `npx cypress run`).
- For an RLS scenario, the exact denial error is what the scenario specifies for the denied case.
