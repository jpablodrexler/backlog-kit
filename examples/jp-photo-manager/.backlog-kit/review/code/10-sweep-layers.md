# Code Reviewer — Full-Codebase Sweep Layers
Read when: a full-codebase sweep

**The layers:**

| Layer key                | Report suffix          | Directory scope                                                                                                    | Primary checklist sections                                    |
| ------------------------ | ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| Backend domain           | `backend-domain`         | `backend/.../domain/**`                                                                                                                   | §1.1, §5, §8 (domain-model rows)                                 |
| Backend application      | `backend-application`    | `backend/.../application/usecase/**`                                                                                                      | §1.1, §1.2, §2, §4, §7, §8 (use-case rows)                       |
| Backend api               | `backend-api`             | `backend/.../infrastructure/web/**` (controllers, request/response DTOs)                                                                  | §1.1 (controller delegation), §3.4, §6 (DTO/entity drift), §8 (DTO rows) |
| Backend infrastructure   | `backend-infrastructure` | `backend/.../infrastructure/persistence/**`, `infrastructure/service/**`, `infrastructure/kafka/**`, `infrastructure/batch/**`, `infrastructure/config/**` | §1.2, §3.1–3.3, §5, §6, §7                                       |
| Frontend core             | `frontend-core`           | `frontend/src/app/core/**`                                                                                                                | §10.2, §11, §12                                                  |
| Frontend features         | `frontend-features`       | `frontend/src/app/features/**`                                                                                                            | §10.1, §10.3, §11, §12                                           |
| Frontend shared           | `frontend-shared`         | `frontend/src/app/shared/**`                                                                                                              | §1.3, §10.1, §11, §12                                            |
| Cross-cutting             | `cross-cutting`           | Both sub-projects; no single directory                                                                                                    | §9, §13, §14, §18, §19, §20, §21, §22, delegate-only port/adapter or service pairs (§1.2/§10.2), dependency-direction violations, systemic naming patterns |

If only the backend (or only the frontend) is in scope, skip the layers that
don't apply — e.g. a "review the whole backend" request produces 4 reports
(domain, application, api, infrastructure) plus a backend-scoped
cross-cutting report, not all 8.

**What goes in the cross-cutting report:** findings that don't belong to one
file's home layer — backend testing conventions (§9) and Cypress conventions
(§13), comment/code-style patterns (§14) that recur across many files, and
anything whose root cause spans two layers at once (e.g. a delegate-only
port/adapter pair, where the finding is really about the port *and* the
adapter *and* the callers, not just one of them). A naming or architecture
violation that's local to a single file still goes in that file's own layer
report, even if the rule itself is defined in a "cross-cutting" section like
§8/§12.
