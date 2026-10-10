# Manual verification recipes
Read when: a scenario has no automated coverage and needs a manual check (§4.3)

## 4.3 Manual verification (fallback)

- Commonly true-visual claims, e.g. "the toolbar SHALL display 5 clickable star icon buttons".
- **API-level scenarios:** issue the actual request with `curl`, following the patterns in `docs/curl-reference.md`, against a running backend (start one per `e2e-testing` skill §1–§4 if none is running), and compare the real response to the scenario's `THEN`.
- **UI-level scenarios:** use the Cypress scratch-spec approach from `e2e-testing` §7 (start the stack per its §1–§4, sign in per its §7.1) to drive the actual interaction and observe the actual result.
- Record exactly what was run and what was observed as the evidence — a specific command/action and its specific output (e.g. `curl ...`).
