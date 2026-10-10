# Manual verification recipes
Read when: a scenario has no automated coverage and needs a manual check (§4.3)

## 4.3 Manual verification (fallback)

- **Data/RLS-level scenarios:** issue the actual request against the linked Supabase project, following the `curl`-against-the-Auth/REST-endpoint pattern in `e2e-testing` §3, or drive it through the Supabase JS client directly in a scratch script, and compare the real response to the scenario's `THEN`.
- **UI-level scenarios:** use the Cypress scratch-spec approach from `e2e-testing` §4 (start the dev server per its §2, sign in per its §4.1) to drive the actual interaction and observe the actual result.
- Record exactly what was run and what was observed as the evidence.
