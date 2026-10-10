# Authentication and Session Security
Read when: a change touches sign-in, sign-up, sign-out, route guards, session or token handling

## 4. Authentication & Session Security

### 4.1 Supabase-managed session, not a custom cookie

This app does not implement its own token issuance/storage — Supabase's
JS client manages the session (access + refresh tokens) internally,
persisted in the browser's own storage. `AuthService` (see
`angular-developer` §11) only mirrors the *current* session as a
read-only signal; it never re-implements storage.

🔴 Flag any code that reads the Supabase session/access token and writes a
**second** copy of it anywhere (a custom cookie, a different
`localStorage` key, a log line) — one authoritative copy, managed by the
Supabase client itself, is the whole point.

🔴 Flag any code that manually parses or decodes the JWT's payload for
application logic (e.g. reading claims out of the access token directly)
instead of using `supabase.auth.getUser()`/the `AuthService` session signal
— hand-rolled JWT handling is exactly the kind of thing this architecture
is designed to avoid needing.

### 4.2 XSS is more consequential here than in a cookie-based app

Because Supabase's session lives in storage that's readable by JavaScript
(not an HttpOnly cookie), **any successful XSS on this app can exfiltrate
the current user's live session** — there's no HttpOnly boundary standing
between an injected script and the credential. This raises the stakes on
ordinary Angular XSS hygiene (§6.2) well above what it would be in a
cookie-session app; treat any XSS finding here as 🔴, not 🟡, specifically
because of this.

### 4.3 Auth flow correctness

🔴 Flag a route that shows user-owned data but isn't behind `authGuard`.

🟡 Flag a sign-up/sign-in/sign-out flow that doesn't handle Supabase's
`{ error }` return (see `code-reviewer` §5) — beyond the UX concern, a
swallowed auth error can leave the UI showing a signed-in-looking state
that isn't backed by a real session.

🟡 Flag reliance on `AuthService.isAuthenticated()` before
`AuthService.ready` has resolved in a code path where the ordering matters
— a race here could briefly show or hide the wrong UI state, though it's
not itself a data-access gap since RLS (§2) is the real enforcement point
regardless of what the UI briefly renders.
