# Frontend Security
Read when: a change touches templates, components, browser storage, or an auth redirect flow

## 6. Frontend Security

### 6.1 Token & Sensitive Data in Storage

🔴 Flag any Angular code that stores anything session-related outside what
Supabase's client itself manages — see §4.1. What may be stored elsewhere
(e.g. a future addition) is non-sensitive UI state, never a token/session
value.

### 6.2 XSS

🔴 Flag any use of `[innerHTML]` binding with user-supplied content that is
not explicitly sanitised through Angular's `DomSanitizer` — treat as 🔴
here regardless of the usual severity, per §4.2's reasoning.

🟡 Flag any Angular template that renders a user-controlled URL in an
`href` or `src` attribute without `sanitizer.bypassSecurityTrustUrl()`
being justified by a comment.

🟡 Flag any `bypassSecurityTrust*` call — each one requires a clear
justification comment explaining why sanitisation is safe to bypass.

### 6.3 Supabase Auth Redirect/CORS Configuration

There is no custom CORS config in this codebase (no backend to configure
it on) — Supabase's own dashboard (Authentication → URL Configuration)
controls which redirect URLs are allowed after email confirmation/password
reset flows, and this isn't something reviewable from the repo's source
code.

🟡 If a change adds a new auth flow that relies on a redirect URL (e.g.
password reset, email confirmation), note in the review that the
corresponding URL needs to be allow-listed in the Supabase dashboard — this
is a deployment/configuration step outside version control, easy to miss
entirely if only the code diff is reviewed.
