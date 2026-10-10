# Test files and running a single test
Read when: matching a scenario to an automated test (§4.1/§4.2) or running a matched test (§5)

## 3. Scale and example

- Example of the §3 multi-capability change: `asset-tagging`'s change also touching `search-and-filter`'s spec.
- A typical feature change has 5–15 scenarios across 5–10 requirements.
- Example of a `WHEN` in this project: usually a specific API call or UI interaction.
- Example of a partially satisfied requirement: the happy path works but a validation-error scenario under the same requirement doesn't.

## 4.1 / 4.2 Test-file kinds

- Example of a task-to-scenario match (this project's own archived changes show the pattern consistently): `star-ratings`' task *"Add test: `PATCH .../rating` with `{"rating":6}` returns `400 Bad Request`"* maps 1:1 to its spec's *"Scenario: Rating above 5 is rejected"*.
- The test file/class a task's section header names is e.g. `AssetControllerTest`, or the relevant `*.cy.ts` spec.
- Test's fully-qualified name: class#method, or spec file + `it(...)` description (e.g. `ClassName#testMethod`).
- §4.2: a general auth test that happens to also cover this endpoint; search test files for the endpoint/component/behavior the scenario describes.

## 5. Running one test

- Run the single test method if the test framework supports that granularity (`mvn test -Dtest=ClassName#method`, `npx cypress run --spec ...`), otherwise the narrowest containing suite.
- "A test exists" and "the test passes" are easy to conflate — say so explicitly when reporting a failing one.
- Running a test is read-only (`mvn test`, `npx cypress run`).
- Partial manual check example: you confirmed the happy path but not the exact error message the scenario specifies.
