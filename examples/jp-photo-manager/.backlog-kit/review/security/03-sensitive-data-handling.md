# Sensitive Data Handling
Read when: every review

## 3. Sensitive Data Handling

### 3.1 Logging

🔴 Flag any `log.info`, `log.debug`, or `log.error` call that includes:
- Passwords or password hashes
- JWT token values
- Full absolute file paths that contain the user's home directory (e.g.,
  `/home/alice/Pictures/private/...`) — log only relative paths or asset IDs.

🟡 Flag any exception that is caught and re-thrown with the original message
embedded in an API response — stack traces and internal paths must not reach
the client.

### 3.2 API Error Responses

🔴 Flag any `@ExceptionHandler` or catch block that returns a stack trace,
Hibernate error message, or SQL snippet in the response body. Return a safe,
generic message instead:

```java
// Wrong
return ResponseEntity.status(500).body(e.getMessage()); // may expose schema

// Right
log.error("Unexpected error", e);
return ResponseEntity.status(500).body("An internal error occurred.");
```

🟡 Flag 404 responses that confirm the existence of resources the caller
should not know about (e.g., `"Asset 42 exists but you cannot see it"` vs
a plain 404).

### 3.3 Hardcoded Secrets

🔴 Flag any hardcoded password, API key, secret key, or token in Java source,
`application.yml`, `application.properties`, or Angular environment files.
Secrets must come from environment variables or a secrets manager:

```yaml
# Wrong
spring.datasource.password: mysecretpassword

# Right
spring.datasource.password: ${POSTGRES_PASSWORD:postgres}
```

🔴 Flag any secret committed to `application-local.yml` that is **not** in
`.gitignore`.

🚫 **Never read `JPPhotoManagerWeb/k8s/secret.yaml` or
`JPPhotoManagerWeb/k8s/catalog-volumes.yaml`** while hunting for hardcoded
secrets — per `JPPhotoManagerWeb/CLAUDE.md`, both hold real secrets and
machine-specific paths and must never be read under any circumstances, not
even as part of a broad "review all the code" sweep. Both are gitignored by
design (that's the correct pattern, not a finding) and have `.example`
counterparts safe to read instead if you need to reason about their
structure. If a full-codebase sweep would otherwise walk `k8s/`, skip these
two files specifically rather than skipping the whole directory.
