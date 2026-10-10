# Frontend Security
Read when: a change touches templates, components, browser storage, or CORS configuration

## 6. Frontend Security

### 6.1 Token & Sensitive Data in Storage

🔴 Flag any Angular code that stores the JWT token string in `localStorage`,
`sessionStorage`, or a cookie accessible to JavaScript. The token must live
only in an HttpOnly cookie managed by the backend. What may be stored in
`localStorage` is non-sensitive session metadata (username, expiry timestamp).

🔴 Flag any `localStorage.setItem` call whose value is derived from an API
response field named `token`, `accessToken`, `jwt`, or similar.

### 6.2 XSS

🔴 Flag any use of `[innerHTML]` binding with user-supplied content that is not
explicitly sanitised through Angular's `DomSanitizer`.

🟡 Flag any Angular template that renders a user-controlled URL in an `href` or
`src` attribute without `sanitizer.bypassSecurityTrustUrl()` being justified
by a comment.

🟡 Flag any `bypassSecurityTrust*` call — each one requires a clear justification
comment explaining why sanitisation is safe to bypass.

### 6.3 CORS & API Configuration

🟡 Flag `@CrossOrigin(origins = "*")` on controllers — wildcard origins are
acceptable in development but must be restricted to known frontend origins in
production via `AppConfig.corsFilter()`.

🟡 Flag the CORS allowed-methods list in `AppConfig` if it is missing any HTTP
method actually used by the API (e.g., `PATCH` missing when `@PatchMapping`
endpoints exist).
