# Known Project-Specific Security Pitfalls
Read when: every review

## 7. Known Project-Specific Security Pitfalls

| Pitfall                                        | What to look for                                                                                          |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `service_role` key anywhere under `frontend/`     | Immediate 🔴 — this key must never reach the browser; see §3.3                                              |
| Anon key flagged as a "leak"                      | False positive — the anon/publishable key is meant to be public; see §3.3                                   |
| Client-side-only data filtering                   | `array.filter(...)` used as if it were an access-control boundary instead of an RLS policy; see §2          |
| Missing/mis-scoped RLS policy                     | A table reachable by a frontend query with no matching `CREATE POLICY` — see `database-reviewer` §4         |
| Second session/token copy                         | Anything writing the Supabase session/token to a place other than the client's own managed storage; see §4.1 |
| Hand-rolled JWT parsing                           | Reading claims out of the access token directly instead of `supabase.auth.getUser()`                        |
| `environment.ts` committed                        | Expected — committed by design; only flag if it holds a `secret`/`service_role` key instead of the publishable/anon key |
| `[innerHTML]` without `DomSanitizer`              | Treat as 🔴 here, not 🟡 — see §4.2/§6.2                                                                     |
| New auth redirect flow, no dashboard note          | A password-reset/email-confirm flow added with no mention of the Supabase dashboard allow-list step         |
