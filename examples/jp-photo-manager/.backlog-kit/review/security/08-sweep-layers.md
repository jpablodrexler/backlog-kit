# Full-Codebase Sweep Layers
Read when: a full-codebase sweep

| Layer key               | Report suffix            | Directory scope                                                                                                                                            | Primary checklist sections                                    |
| ------------------------ | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| Backend domain           | `backend-domain`          | `backend/.../domain/**`                                                                                                                                   | §3.3 (low surface — pure POJOs/interfaces, few findings expected) |
| Backend application      | `backend-application`     | `backend/.../application/usecase/**`, `application/exception/**`                                                                                          | §3.1, §3.2 (custom exceptions), §3.3, §4.3                      |
| Backend api               | `backend-api`              | `backend/.../infrastructure/web/**` (controllers, DTOs, exception handlers, filters)                                                                      | §2.1 (endpoints returning file contents), §3.2, §3.3, §4.1, §6.3 (`@CrossOrigin` on controllers) |
| Backend infrastructure   | `backend-infrastructure`  | `backend/.../infrastructure/persistence/**`, `infrastructure/service/**`, `infrastructure/kafka/**`, `infrastructure/batch/**`, `infrastructure/config/**`, `infrastructure/adapter/**` | §2 (full), §3.3, §4.2, §4.3 (encoder bean), §5.1, §5.2, §6.3 (`AppConfig`) |
| Frontend core             | `frontend-core`            | `frontend/src/app/core/**`                                                                                                                                | §6.1                                                             |
| Frontend features         | `frontend-features`        | `frontend/src/app/features/**`                                                                                                                            | §6.1, §6.2                                                       |
| Frontend shared           | `frontend-shared`          | `frontend/src/app/shared/**`                                                                                                                              | §6.2                                                             |
| Cross-cutting             | `cross-cutting`            | Both sub-projects; no single directory                                                                                                                    | §1 (dependency vulnerabilities — `pom.xml`/`package.json` are project-wide, not per-layer), §7, any finding whose root cause spans two layers at once (e.g. JWT-in-URL: a backend controller emitting the URL and a frontend `EventSource` consuming it) |

If only the backend (or only the frontend) is in scope, skip the layers that
don't apply — e.g. a "review the whole backend's security" request produces
4 reports (domain, application, api, infrastructure) plus a backend-scoped
cross-cutting report, not all 8.

## Subagent reminders

Include in each subagent's prompt, where it applies to that layer:

   - **A reminder never to read `JPPhotoManagerWeb/k8s/secret.yaml` or
     `JPPhotoManagerWeb/k8s/catalog-volumes.yaml`** (relevant to the
     `backend-infrastructure` and `cross-cutting` subagents in particular,
     since they're the ones most likely to touch config/deployment files) —
     see §3.3.
