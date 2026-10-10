# Sensitive Data Handling and Keys
Read when: every review

## 3. Sensitive Data Handling

### 3.1 Logging

🔴 Flag any `console.log`/`console.error` call that includes a full
Supabase session object, access token, or refresh token — even for
debugging, these are live credentials for the signed-in session.

🟡 Flag any error surfaced to the user (via the `error` signal pattern —
see `angular-developer` §10) that passes through a raw Supabase/Postgres
error message containing more detail than necessary (e.g. a Postgres
constraint name or internal schema detail) — prefer `err.message` as
Supabase already returns it (generally safe, user-facing) but don't add
custom code that surfaces additional internal detail beyond what Supabase
itself chose to return.

### 3.2 Auth error responses

🟡 Flag any custom error-message logic that reveals whether a specific
email address has an account (e.g. distinguishing "wrong password" from
"no such user" in the UI) — Supabase's own `signInWithPassword` already
returns a generic `Invalid login credentials` error for both cases; don't
add code that re-derives or exposes the distinction.

### 3.3 Keys and Secrets — read this before flagging anything key-related

This project has exactly two kinds of Supabase key, with **opposite**
handling rules, and conflating them is the single most likely false
positive or false negative in a review here:

- **`publishable`/anon key** (`environment.ts`'s `supabaseKey`, used by
  `SupabaseService`) — **this key is meant to be public.** It ships inside
  every Angular bundle served to every visitor's browser; there is no way
  to "hide" it, and that's by design — Supabase's security model puts all
  enforcement in RLS (§2), not in keeping this key secret. **Do not flag
  its presence in frontend code, in a built bundle, or in browser dev tools
  as a leak** — that's the intended architecture, not a mistake.
- **`secret`/`service_role` key** — this key **bypasses RLS entirely** and
  must **never** appear anywhere in `frontend/`, in a Vercel build, in
  `environment.ts`, or in any file that ships to the browser. 🔴 Flag any
  occurrence of this key (or a variable clearly intended to hold it —
  named `serviceRole`, `secretKey`, or similar) anywhere under `frontend/`,
  full stop. There is currently no legitimate use for this key anywhere in
  this codebase (no server exists to hold it) — its presence anywhere is
  itself the finding, not a starting point for a "is it exposed" analysis.

`environment.ts` is committed to the repo by design (see `CLAUDE.md`'s
environment-configuration section) — its presence in a diff is expected,
not a finding. Only flag it if it contains a `secret`/`service_role` key
instead of the publishable/anon key (§3.3's real finding), or if a diff
points it at a different Supabase project without the user having said
that's intentional.

🔴 Flag any hardcoded Supabase project ref, URL, or key inlined directly in
application code (a component, a service) instead of read from
`environment.ts` — even for the anon key, which isn't secret, hardcoding it
outside the one sanctioned `SupabaseService` construction point (see
`code-reviewer` §1.1's "second `createClient()` call" rule) breaks the
single-client invariant and makes swapping environments (dev/Vercel)
impossible without a code change.
