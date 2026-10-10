# Known Project-Specific Security Pitfalls
Read when: every review

## 7. Known Project-Specific Security Pitfalls

| Pitfall | What to look for |
| ------- | ---------------- |
| Path traversal in `StorageServiceAdapter` | `folderPath` or `fileName` used in `Paths.get(...)` without containment check |
| Thumbnail URL leaks absolute path | API response includes raw filesystem path instead of opaque `/api/assets/{id}/thumbnail` |
| JWT in query param for SSE | `EventSource` URL contains `?token=...` — use HttpOnly cookie instead |
| BCrypt work factor too low | `new BCryptPasswordEncoder()` with default or factor < 10 |
| Actuator endpoints open | `/actuator/health`, `/actuator/env` accessible without auth in prod |
| Hardcoded DB password | `application.yml` with literal `postgres` password not overridden by env var |
| CSRF disabled without SameSite | `csrf().disable()` when using HttpOnly cookies — verify `SameSite=Strict` is set |
| Stack trace in 500 response | `e.getMessage()` or `e.toString()` returned directly in response body |
| Decompression bomb | Image decoded without dimension check before allocating pixel buffer |
| User-supplied filename on disk | `fileName` used directly in `Files.write(Paths.get(dir, fileName))` without sanitisation |
