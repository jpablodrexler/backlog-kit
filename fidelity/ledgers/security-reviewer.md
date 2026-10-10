kit: skills/security-reviewer
sub: JPPhotoManagerWeb/docs/backlog => <backlog>
sub: docs/backlog => <backlog>
sub: JPPhotoManagerWeb/docs/reports => <reports>
sub: docs/reports => <reports>

PARAM | name: security-reviewer description: > Security review skill for the J | description rewritten stack-free (TRIGGER structure kept); `scope` removed, `version` is the kit's (D30)
DROPPED | Review code in the JPPhotoManager project for security vulnerabilities | second project's variant of this text; the kit follows the first project
PARAM | 1. Identify the **scope**: a full-codebase sweep of the whole web appl | second project's variant of this text; the kit follows the first project
PARAM | - **Scoped review** → follow steps 2–7 below as a single pass, produci | second project's variant of this text; the kit follows the first project
DROPPED | 2. Identify which sub-project(s) are affected: **backend** (Java), **f | second project's variant of this text; the kit follows the first project
DROPPED | 3. Scan for dependency changes (`pom.xml`, `package.json`, `package-lo | second project's variant of this text; the kit follows the first project
PARAM | 4. Read every changed file that touches auth, file I/O, user input, or | second project's variant of this text; the kit follows the first project
DROPPED | 5. Work through the relevant checklist(s) below, section by section. | second project's variant of this text; the kit follows the first project
DROPPED | When asked to review the whole web application's security (or the enti | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Layer key ¦ Report suffix ¦ Directory scope ¦ Primary checklist sect | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ ------------------------ ¦ ------------------------- ¦ ------------- | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Backend domain ¦ `backend-domain` ¦ `backend/.../domain/**` ¦ §3.3 ( | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Backend application ¦ `backend-application` ¦ `backend/.../applicati | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Backend api ¦ `backend-api` ¦ `backend/.../infrastructure/web/**` (c | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Backend infrastructure ¦ `backend-infrastructure` ¦ `backend/.../inf | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Frontend core ¦ `frontend-core` ¦ `frontend/src/app/core/**` ¦ §6.1 | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Frontend features ¦ `frontend-features` ¦ `frontend/src/app/features | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Frontend shared ¦ `frontend-shared` ¦ `frontend/src/app/shared/**` ¦ | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Cross-cutting ¦ `cross-cutting` ¦ Both sub-projects; no single direc | second project's variant of this text; the kit follows the first project
DROPPED | If only the backend (or only the frontend) is in scope, skip the layer | second project's variant of this text; the kit follows the first project
DROPPED | Each layer's review runs in its own subagent (`Agent` tool, `subagent_ | second project's variant of this text; the kit follows the first project
PARAM | 2. The remaining applicable layers are independent of each other (no l | second project's variant of this text; the kit follows the first project
PARAM | - The layer key, its directory scope, and its primary checklist sectio | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | - An instruction to first read `.claude/skills/security-reviewer/SKILL | second project's variant of this text; the kit follows the first project
DROPPED | - **A reminder never to read `JPPhotoManagerWeb/k8s/secret.yaml` or `J | second project's variant of this text; the kit follows the first project
PARAM | - A short return-message instruction: report back the Critical/Warning | second project's variant of this text; the kit follows the first project
PARAM | 5. Once every dispatched subagent has completed, give a short in-chat | second project's variant of this text; the kit follows the first project
PARAM | ¦ 🔴 **CRITICAL** ¦ Exploitable vulnerability, data leak, or privilege | second project's variant of this text; the kit follows the first project
DROPPED | ### 1.1 Backend (Maven) | second project's variant of this text; the kit follows the first project
DROPPED | Run the OWASP dependency check and review the output: | second project's variant of this text; the kit follows the first project
DROPPED | cd JPPhotoManagerWeb/backend | second project's variant of this text; the kit follows the first project
DROPPED | mvn org.owasp:dependency-check-maven:check | second project's variant of this text; the kit follows the first project
DROPPED | Alternatively, audit with the Maven Versions plugin: | second project's variant of this text; the kit follows the first project
DROPPED | mvn versions:display-dependency-updates | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any dependency with a known CVE rated **CRITICAL** or **HIGH** | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag any Spring Boot, Spring Security, or Flyway version that is mor | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag any transitive dependency that is being overridden with an olde | second project's variant of this text; the kit follows the first project
DROPPED | ### 1.2 Frontend (npm) | second project's variant of this text; the kit follows the first project
DROPPED | cd JPPhotoManagerWeb/frontend | second project's variant of this text; the kit follows the first project
DROPPED | npm audit --audit-level=high | second project's variant of this text; the kit follows the first project
PARAM | 🔴 Flag any package with a `critical` or `high` severity audit finding | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | 🟡 Flag packages that are significantly outdated and have known securit | second project's variant of this text; the kit follows the first project
PARAM | 🟢 Flag `devDependencies` with audit findings — lower risk but still wo | second project's variant of this text; the kit follows the first project
DROPPED | ## 2. File System Security (Critical for a Photo Manager) | second project's variant of this text; the kit follows the first project
DROPPED | The application reads, writes, and thumbnails arbitrary file paths sup | second project's variant of this text; the kit follows the first project
DROPPED | ### 2.1 Path Traversal | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any file operation that uses a user-supplied path directly with | second project's variant of this text; the kit follows the first project
DROPPED | Path base = Paths.get(allowedRootDirectory).toRealPath(); | second project's variant of this text; the kit follows the first project
DROPPED | Path target = base.resolve(userSuppliedRelativePath).normalize(); | second project's variant of this text; the kit follows the first project
DROPPED | if (!target.startsWith(base)) { | second project's variant of this text; the kit follows the first project
DROPPED | throw new SecurityException("Path traversal attempt: " + target); | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any endpoint that returns file contents (bytes, streams) when t | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any thumbnail URL or file URL that embeds an absolute filesyste | second project's variant of this text; the kit follows the first project
DROPPED | ### 2.2 File Type Validation | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any file-upload or file-read path that relies **only** on the f | second project's variant of this text; the kit follows the first project
DROPPED | // Apache Commons Imaging already does this for supported formats | second project's variant of this text; the kit follows the first project
DROPPED | // For a generic check, use Tika or Files.probeContentType() | second project's variant of this text; the kit follows the first project
DROPPED | String detectedType = tika.detect(inputStream); | second project's variant of this text; the kit follows the first project
DROPPED | if (!ALLOWED_MIME_TYPES.contains(detectedType)) { | second project's variant of this text; the kit follows the first project
DROPPED | throw new IllegalArgumentException("Unsupported file type: " + detecte | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag any code that writes a user-supplied filename directly to disk | second project's variant of this text; the kit follows the first project
DROPPED | ### 2.3 Thumbnail Generation | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag thumbnail generation code that does not set limits on image dim | second project's variant of this text; the kit follows the first project
DROPPED | 🟢 Flag any temporary file created during thumbnail generation that is | second project's variant of this text; the kit follows the first project
DROPPED | ## 3. Sensitive Data Handling | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ### 3.1 Logging | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🔴 Flag any `log.info`, `log.debug`, or `log.error` call that includes: | second project's variant of this text; the kit follows the first project
DROPPED | - Passwords or password hashes | second project's variant of this text; the kit follows the first project
DROPPED | - JWT token values | second project's variant of this text; the kit follows the first project
DROPPED | - Full absolute file paths that contain the user's home directory (e.g | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag any exception that is caught and re-thrown with the original me | second project's variant of this text; the kit follows the first project
DROPPED | ### 3.2 API Error Responses | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any `@ExceptionHandler` or catch block that returns a stack tra | second project's variant of this text; the kit follows the first project
DROPPED | return ResponseEntity.status(500).body(e.getMessage()); // may expose | second project's variant of this text; the kit follows the first project
DROPPED | log.error("Unexpected error", e); | second project's variant of this text; the kit follows the first project
DROPPED | return ResponseEntity.status(500).body("An internal error occurred."); | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag 404 responses that confirm the existence of resources the calle | second project's variant of this text; the kit follows the first project
DROPPED | ### 3.3 Hardcoded Secrets | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any hardcoded password, API key, secret key, or token in Java s | second project's variant of this text; the kit follows the first project
DROPPED | spring.datasource.password: mysecretpassword | second project's variant of this text; the kit follows the first project
DROPPED | spring.datasource.password: ${POSTGRES_PASSWORD:postgres} | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any secret committed to `application-local.yml` that is **not** | second project's variant of this text; the kit follows the first project
DROPPED | 🚫 **Never read `JPPhotoManagerWeb/k8s/secret.yaml` or `JPPhotoManagerW | second project's variant of this text; the kit follows the first project
DROPPED | ## 4. Authentication & JWT / Cookie Security | second project's variant of this text; the kit follows the first project
DROPPED | ### 4.1 HttpOnly Cookie (not Authorization header) | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any code that reads the JWT from a query parameter (`?token=... | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any `ResponseCookie` that is missing `.httpOnly(true)`, `.sameS | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag any `ResponseCookie` that sets `secure: false` when the app is | second project's variant of this text; the kit follows the first project
DROPPED | ### 4.2 Spring Security Filter Chain | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any `SecurityFilterChain` that does not include `.dispatcherTyp | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any endpoint that handles write operations (`POST`, `PUT`, `PAT | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag `http.csrf().disable()` without a comment explaining why — CSRF | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag Spring Boot Actuator endpoints (`/actuator/**`) that are expose | second project's variant of this text; the kit follows the first project
DROPPED | Before doing the endpoint-by-endpoint cross-check above by hand, run ` | second project's variant of this text; the kit follows the first project
DROPPED | ### 4.3 Password Storage | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any code that stores or compares passwords in plaintext. | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any use of MD5 or SHA-1 for password hashing. Use BCrypt with a | second project's variant of this text; the kit follows the first project
DROPPED | new BCryptPasswordEncoder(12) | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag any `UserDetailsService` that loads users from a hardcoded in-m | second project's variant of this text; the kit follows the first project
DROPPED | ## 5. Injection Vulnerabilities | second project's variant of this text; the kit follows the first project
DROPPED | ### 5.1 SQL / JPQL Injection | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any `@Query` that concatenates user input into the JPQL or SQL | second project's variant of this text; the kit follows the first project
DROPPED | @Query("SELECT a FROM Asset a WHERE a.fileName = '" + fileName + "'") | second project's variant of this text; the kit follows the first project
DROPPED | @Query("SELECT a FROM Asset a WHERE a.fileName = :fileName") | second project's variant of this text; the kit follows the first project
DROPPED | List<Asset> findByFileName(@Param("fileName") String fileName); | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag any `EntityManager.createNativeQuery()` call that uses string c | second project's variant of this text; the kit follows the first project
DROPPED | ### 5.2 OS Command Injection | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any call to `Runtime.exec()`, `ProcessBuilder`, or similar that | second project's variant of this text; the kit follows the first project
DROPPED | // Wrong — user supplies folderPath | second project's variant of this text; the kit follows the first project
DROPPED | Runtime.getRuntime().exec("ls " + folderPath); | second project's variant of this text; the kit follows the first project
DROPPED | // Right — pass as separate argument, never via shell string | second project's variant of this text; the kit follows the first project
DROPPED | new ProcessBuilder("ls", folderPath).start(); | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any image-processing library invocation (e.g., ImageMagick via | second project's variant of this text; the kit follows the first project
DROPPED | ## 6. Frontend Security | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ### 6.1 Token & Sensitive Data in Storage | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🔴 Flag any Angular code that stores the JWT token string in `localStor | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any `localStorage.setItem` call whose value is derived from an | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag any use of `[innerHTML]` binding with user-supplied content tha | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag any Angular template that renders a user-controlled URL in an ` | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🟡 Flag any `bypassSecurityTrust*` call — each one requires a clear jus | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ### 6.3 CORS & API Configuration | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag `@CrossOrigin(origins = "*")` on controllers — wildcard origins | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag the CORS allowed-methods list in `AppConfig` if it is missing a | second project's variant of this text; the kit follows the first project
DROPPED | ## 7. Known Project-Specific Security Pitfalls | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Pitfall ¦ What to look for ¦ | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | ¦ ------- ¦ ---------------- ¦ | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Path traversal in `StorageServiceAdapter` ¦ `folderPath` or `fileNam | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Thumbnail URL leaks absolute path ¦ API response includes raw filesy | second project's variant of this text; the kit follows the first project
DROPPED | ¦ JWT in query param for SSE ¦ `EventSource` URL contains `?token=...` | second project's variant of this text; the kit follows the first project
DROPPED | ¦ BCrypt work factor too low ¦ `new BCryptPasswordEncoder()` with defa | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Actuator endpoints open ¦ `/actuator/health`, `/actuator/env` access | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Hardcoded DB password ¦ `application.yml` with literal `postgres` pa | second project's variant of this text; the kit follows the first project
DROPPED | ¦ CSRF disabled without SameSite ¦ `csrf().disable()` when using HttpO | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Stack trace in 500 response ¦ `e.getMessage()` or `e.toString()` ret | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Decompression bomb ¦ Image decoded without dimension check before al | second project's variant of this text; the kit follows the first project
DROPPED | ¦ User-supplied filename on disk ¦ `fileName` used directly in `Files. | second project's variant of this text; the kit follows the first project
PARAM | - `path/to/File.java:42` — <vulnerability description and exploit scen | second project's variant of this text; the kit follows the first project
PARAM | - `path/to/file.ts:15` — <insecure pattern and recommended fix> | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | - `path/to/File.java:88` — <hardening improvement> | second project's variant of this text; the kit follows the first project
PARAM | - **Path:** `<reports>/security-review/SECURITY_REVIEW_FINDINGS_{YYYY- #2 | second project's variant of this text; the kit follows the first project
PARAM | - **Content:** the same Critical/Warnings/Suggestions grouping as the | second project's variant of this text; the kit follows the first project
PARAM | - **Scope of content:** write only what was actually found in *this* r | second project's variant of this text; the kit follows the first project
PARAM | - **Never quote secret values in a report.** If a finding involves an | second project's variant of this text; the kit follows the first project
PARAM | 2. List every report file for that date (there may be several `-2`/`-3 | second project's variant of this text; the kit follows the first project
PARAM | 3. **If exactly one report remains**, use it directly — don't make the | second project's variant of this text; the kit follows the first project
DROPPED | 1. Read the full report before asking anything, so the menu of categor | second project's variant of this text; the kit follows the first project
DROPPED | 2. Do not silently pick a starting point or scope. Ask the user whethe | second project's variant of this text; the kit follows the first project
DROPPED | - An entire severity category (🔴 Critical, 🟡 Warning, or 🟢 Suggestion) | second project's variant of this text; the kit follows the first project
DROPPED | - A specific finding — let them name it, or list the still-unchecked f | second project's variant of this text; the kit follows the first project
DROPPED | Only offer categories/findings that still have unchecked (`- [ ]`) box | second project's variant of this text; the kit follows the first project
DROPPED | 1. Read the affected file(s) and understand the finding in the full co | second project's variant of this text; the kit follows the first project
DROPPED | 2. Apply the fix. The report tells you what's wrong; the checklist sec | second project's variant of this text; the kit follows the first project
DROPPED | 3. If a fix hinges on a real design decision rather than just applying | second project's variant of this text; the kit follows the first project
DROPPED | 4. Verify the fix before moving on: compile/build, then run the narrow | second project's variant of this text; the kit follows the first project
DROPPED | 5. Update tests for the new shape of the code (renamed types/methods, | second project's variant of this text; the kit follows the first project
PARAM | 6. Mark the finding complete in the report file immediately, not batch | second project's variant of this text; the kit follows the first project
DROPPED | - `**Evaluated, no change made:** <rationale>` — for findings where, a | second project's variant of this text; the kit follows the first project
DROPPED | 7. If fixing one finding incidentally resolves another still-unchecked | second project's variant of this text; the kit follows the first project
DROPPED | After finishing the selected scope, run the widest verification availa | second project's variant of this text; the kit follows the first project
DROPPED | - If the current report still has unchecked findings, repeat from §9.2 | second project's variant of this text; the kit follows the first project
DROPPED | - If the current report is now fully checked off, go back to §9.1 — re | second project's variant of this text; the kit follows the first project
PARAM | name: security-reviewer description: > Security review skill for pablo | description rewritten stack-free (TRIGGER structure kept); `scope` removed, `version` is the kit's (D30)
DROPPED | Review code in the pablo-web project for security vulnerabilities, sen | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | 1. Identify the **scope**: a full-codebase sweep of the whole frontend | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | 2. Scan for dependency changes (`frontend/package.json`, root `package | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | 3. Read every changed file that touches auth, RLS policies (under `sup | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | 4. Work through the relevant checklist(s) below, section by section. | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ ------------------- ¦ -------------------- ¦ ----------------------- | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Frontend core ¦ `frontend-core` ¦ `frontend/src/app/core/**` ¦ §2, § | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Frontend features ¦ `frontend-features` ¦ `frontend/src/app/features #2 | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Supabase migrations ¦ `supabase-migrations` ¦ `supabase/migrations/* | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Cross-cutting ¦ `cross-cutting` ¦ Whole repo; no single directory ¦ | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | If only the frontend (or only the Supabase schema) is in scope, skip t | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | - An instruction to first read `.claude/skills/security-reviewer/SKILL #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | - A reminder that `frontend/src/environments/environment.ts` is commit | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | ¦ 🔴 **CRITICAL** ¦ Exploitable vulnerability, data leak, RLS/access-co | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | npm audit --audit-level=high # root (supabase CLI devDependency) | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | cd frontend && npm audit --audit-level=high | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | 🟡 Flag `@angular/*`, `@angular/material`, or `@supabase/supabase-js` v | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | 🟢 Flag `devDependencies` with audit findings — lower risk but still wo #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | ## 2. Row Level Security — the Actual Authorization Boundary | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | There is no server-side controller, filter chain, or middleware in thi | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🔴 Flag any new table or column exposed to `anon`/`authenticated` via ` | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🔴 Flag any frontend code that filters or hides data purely in TypeScri | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🟡 Flag a new service method whose data-scoping intent isn't obviously | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🔴 Flag any `console.log`/`console.error` call that includes a full Sup | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🟡 Flag any error surfaced to the user (via the `error` signal pattern | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ### 3.2 Auth error responses | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🟡 Flag any custom error-message logic that reveals whether a specific | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ### 3.3 Keys and Secrets — read this before flagging anything key-rela | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | This project has exactly two kinds of Supabase key, with **opposite** | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | - **`publishable`/anon key** (`environment.ts`'s `supabaseKey`, used b | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | - **`secret`/`service_role` key** — this key **bypasses RLS entirely** | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | `environment.ts` is committed to the repo by design (see `CLAUDE.md`'s | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🔴 Flag any hardcoded Supabase project ref, URL, or key inlined directl | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ## 4. Authentication & Session Security | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ### 4.1 Supabase-managed session, not a custom cookie | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | This app does not implement its own token issuance/storage — Supabase' | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🔴 Flag any code that reads the Supabase session/access token and write | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🔴 Flag any code that manually parses or decodes the JWT's payload for | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ### 4.2 XSS is more consequential here than in a cookie-based app | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | Because Supabase's session lives in storage that's readable by JavaScr | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ### 4.3 Auth flow correctness | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🔴 Flag a route that shows user-owned data but isn't behind `authGuard` | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🟡 Flag a sign-up/sign-in/sign-out flow that doesn't handle Supabase's | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🟡 Flag reliance on `AuthService.isAuthenticated()` before `AuthService | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ## 5. Row Level Security & Migration-Specific Checks | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | This section is a pointer, not a duplicate: **all detailed RLS/migrati | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🔴 Flag a `SECURITY DEFINER` function (if one is ever introduced) with | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🔴 Flag any Angular code that stores anything session-related outside w | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🔴 Flag any use of `[innerHTML]` binding with user-supplied content tha #2 | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ### 6.3 Supabase Auth Redirect/CORS Configuration | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | There is no custom CORS config in this codebase (no backend to configu | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | 🟡 If a change adds a new auth flow that relies on a redirect URL (e.g. | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | ¦ ------------------------------------------------- ¦ ---------------- | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | ¦ `service_role` key anywhere under `frontend/` ¦ Immediate 🔴 — this k | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Anon key flagged as a "leak" ¦ False positive — the anon/publishable | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Client-side-only data filtering ¦ `array.filter(...)` used as if it | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Missing/mis-scoped RLS policy ¦ A table reachable by a frontend quer | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Second session/token copy ¦ Anything writing the Supabase session/to | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Hand-rolled JWT parsing ¦ Reading claims out of the access token dir | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ `environment.ts` committed ¦ Expected — committed by design; only fl | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ `[innerHTML]` without `DomSanitizer` ¦ Treat as 🔴 here, not 🟡 — see | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ New auth redirect flow, no dashboard note ¦ A password-reset/email-c | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | - `path/to/file.ts:42` — <vulnerability description and exploit scenar | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | - `path/to/file.ts:88` — <hardening improvement> | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | - **Never quote a secret value in a report.** If a finding involves an | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | 2. Apply the fix. §1–§7 above tell you what "right" looks like for tha | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | 4. Verify the fix: run `npx ng test --include='**/affected.spec.ts'`, | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | After finishing the selected scope, run the widest verification availa #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
