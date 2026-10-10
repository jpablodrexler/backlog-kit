# Doc sections and their source of truth

Read when: every run

## 1. Doc Sections & Their Source of Truth

| Section | File(s) | Source of truth to check against |
|---|---|---|
| Commands, package layout, conventions | `CLAUDE.md` | `pom.xml`/`package.json` scripts, actual package structure, existing code style |
| REST API table | `docs/backend.md` (REST API section) | Every `@RestController` in `backend/.../infrastructure/web/controller/` — one row per `@GetMapping`/`@PostMapping`/`@PutMapping`/`@PatchMapping`/`@DeleteMapping`, auth column cross-checked against `SecurityConfig`'s `permitAll()`/`hasRole()` rules and any method-level `@PreAuthorize` |
| `curl` examples | `docs/curl-reference.md` | Same controllers as above — one example per endpoint, kept in sync with the REST API table's endpoint list |
| Configuration table | `docs/backend.md` (Configuration section) | Every `@Value("${...}")` usage plus `application.yml` defaults |
| Persistence narrative | `docs/backend.md` (Persistence), `docs/architecture.md` (DB diagram) | `@Entity` classes (Postgres), Mongo repository classes, Redis dual-writes/mirrors — grep for a second store's write inside a method that already writes to the primary store |
| Authentication flow | `docs/authentication.md` | `SecurityConfig`, `AuthController`, `JwtTokenServiceAdapter`, `RefreshTokenServiceAdapter`, cookie names/flags |
| Catalog pipeline & Kafka topics | `docs/catalog-process.md` | `infrastructure/batch/**`, `infrastructure/kafka/**`, `config/KafkaTopicConfig.java` — cross-check with `kafka-events-conventions` |
| Server-side caching | `docs/backend.md`/`docs/architecture.md` | `AppConfig.cacheManager()`'s `perCacheConfigurations` — cross-check with `redis-caching-conventions` |
| System/backend/database diagrams | `docs/architecture.md` | Overall package structure, Flyway migration history for the ERD, `app.routes.ts` for the frontend component diagram |
| Frontend structure & routes | `docs/frontend.md` | `frontend/src/app/app.routes.ts`, `features/` directory listing |
| Feature list | `docs/features.md` | What's actually reachable in the UI — cross-check against routes, not aspirational/planned features |
| Docker Compose reference | `docs/docker-compose.md` | `docker-compose.yml`, `.env.example` |
| Kubernetes reference | `docs/kubernetes.md` | `k8s/*.yaml`, `kustomization.yaml`, `scripts/*.sh` |
| **Deploy manifest parity** | `docker-compose.yml` ↔ `k8s/configmap.yaml` + `k8s/backend.yaml`/`k8s/frontend.yaml` env blocks | See §2 |
| **Custom metrics ↔ dashboard** | `grafana/provisioning/dashboards/photomanager.json` | Every `Counter.builder("photomanager_...")`/`Timer.builder(...)`/`Gauge.builder(...)` registration — see §3 |
