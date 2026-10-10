# Authentication and JWT / Cookie Security
Read when: a change touches login, token or cookie handling, the security filter chain, or password storage

## 4. Authentication & JWT / Cookie Security

### 4.1 HttpOnly Cookie (not Authorization header)

🔴 Flag any code that reads the JWT from a query parameter
(`?token=...`) or a custom header for `EventSource` or `<img>` endpoints.
Tokens in URLs appear in server logs and browser history. The project uses
HttpOnly cookies — see `java-developer` skill §15.1 for the correct pattern.

🔴 Flag any `ResponseCookie` that is missing `.httpOnly(true)`, `.sameSite("Strict")`,
or `.path("/")`.

🟡 Flag any `ResponseCookie` that sets `secure: false` when the app is deployed
over HTTPS.

### 4.2 Spring Security Filter Chain

🔴 Flag any `SecurityFilterChain` that does not include
`.dispatcherTypeMatchers(DispatcherType.ASYNC).permitAll()` as the **first**
rule. Missing this causes `AuthorizationDeniedException` on `SseEmitter` async
dispatch threads (see `java-developer` skill §15.2).

🔴 Flag any endpoint that handles write operations (`POST`, `PUT`, `PATCH`,
`DELETE`) but is permitted without authentication.

🟡 Flag `http.csrf().disable()` without a comment explaining why — CSRF
protection should only be disabled when the API is stateless (JWT-based) and
does not use cookie-based session auth. If the project switches to HttpOnly
cookies, CSRF protection via `SameSite=Strict` must be verified.

🟡 Flag Spring Boot Actuator endpoints (`/actuator/**`) that are exposed
without authentication in production profiles.

Before doing the endpoint-by-endpoint cross-check above by hand, run
`bash scripts/auth-coverage-report.sh` from `backend/` — it parses
`SecurityConfig.java`'s ordered `requestMatchers` rules and every
`@RestController`'s mapping annotations, then writes a dated table under
`JPPhotoManagerWeb/docs/reports/auth-coverage/` showing exactly which rule
governs every endpoint (plus any method-level `@PreAuthorize`, a separate,
tighter restriction the table doesn't try to merge into the same column).
It is a factual snapshot, not a judgment call — an endpoint resolving only
to the `anyRequest` fallback isn't automatically wrong (the fallback
itself is `permitAll()`, and some endpoints are intentionally public), but
it's exactly the kind of gap this cross-check is meant to catch: a new
controller silently inheriting a broader rule than intended because
`SecurityConfig`'s ordered matcher list is easy to lose track of as
controllers are added. The regex-based path matching it uses is an
approximation of Spring's real `PathPattern` matcher, so treat a
surprising row as a prompt to go read `SecurityConfig.java` directly, not
as ground truth on its own.

### 4.3 Password Storage

🔴 Flag any code that stores or compares passwords in plaintext.

🔴 Flag any use of MD5 or SHA-1 for password hashing. Use BCrypt with a work
factor ≥ 10:

```java
new BCryptPasswordEncoder(12)
```

🟡 Flag any `UserDetailsService` that loads users from a hardcoded in-memory
list in a non-test profile — production must load from the repository.
