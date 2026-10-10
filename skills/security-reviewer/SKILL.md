---
name: security-reviewer
description: Stack-agnostic security review of code changes or a whole repository. Covers dependency vulnerabilities and update hygiene, secrets and credentials in code, config and history, authentication and session handling, authorization and access checks, injection and unsafe input, output encoding and XSS-class issues, logging of sensitive data, error disclosure, transport/CORS/CSP-class configuration, and file handling. Has a non-interactive review mode (a file list in, one dated checkbox report out, one hand-back line) for use as a `[[reviews]]` skill, plus interactive full audit, dependency audit and a fix workflow for an existing findings report. TRIGGER when code touches authentication, authorization, user input, file I/O, secrets or dependencies, when a review phase invokes it with a changed-files list, or when asked for a security review, audit, or to fix findings from a security report.
license: MIT
metadata:
  version: "0.1"
---

Review code for security vulnerabilities, sensitive-data mishandling and insecure patterns, on whatever stack the project uses. Paths come from `.backlog-kit.toml` (`[paths] reports_dir`, default `docs/reports`); with no file the defaults apply.

The skill has four modes. Pick the one that matches how it was invoked and do not mix them:

| Mode | When | Interactive |
| --- | --- | --- |
| **Non-interactive review** | Invoked by a review phase with a file list (`[[reviews]] skill = "security-reviewer"`) | No, never ask questions |
| **Security audit** | The user asks for a security review or audit of a scope or the whole repository | Yes |
| **Dependency audit** | The user asks about vulnerable or outdated dependencies | Yes |
| **Fix workflow** | The user asks to fix or work through findings of an existing report | Yes |

## Project context first

Before judging anything, identify the project's own security model, because the same code is a finding in one architecture and normal in another:

- Look for the project's own security notes (a security or architecture document, an ADR, the contributor guide) and load them if present. Their rules override the generic checks below where they conflict; say so in the finding.
- Identify the authentication mechanism (sessions, tokens, cookies, an identity provider) and where authorization is actually enforced (middleware, handlers, a data layer, the database). Client-side checks are never an authorization boundary when a server or data layer exists behind them.
- Identify which values are intentionally public (for example a client-side identifier documented as public) and which are secrets. Do not flag a documented public value as a leak; do flag anything that holds a privileged credential in code that ships to clients.
- If none of this can be determined, say so in the report header and fall back to the generic checks.

## Severity

| Level | Meaning |
| --- | --- |
| 🔴 Critical | Exploitable now, leaks data or credentials, or lets one user reach another's data or privileges. Fix immediately. |
| 🟡 Warning | Insecure pattern that raises risk. Fix before merging. |
| 🔵 Suggestion | Defence in depth or minor hardening. Fix if convenient. |

Severity discipline: rate by what an attacker can do with the code as written, not by how the pattern looks. Do not inflate a theoretical issue to Critical, and do not downgrade a reachable one. When a finding's severity depends on a project fact (for example whether a session token is readable by page scripts, which raises the stakes of any XSS-class issue), state that fact in the finding.

## Evidence rule

Every finding needs `file:line`, what is wrong, and why it matters (the exploit scenario or the data at risk). Read the code around the line before flagging; a finding you cannot point at is not a finding. Never speculate about files you did not read.

**Never put a secret's actual value in a report, in chat, or in a fix note.** Cite the location (`file:line`), the kind of secret (API key, password, private key, token) and the variable or key name only. If you must show that two values match, say so without printing either.

If the project documents a file as holding real secrets that must not be read (a credentials file, a deployment secrets manifest), do not read it even in a broad sweep; read its example or template counterpart instead and skip only that file.

## Checklist

Apply the sections relevant to the files in scope; skip the rest silently.

### 1. Dependencies and update hygiene

- Identify the package managers in use (manifests and lockfiles). Flag a dependency with a known critical or high advisory that has a fixed version available: 🔴 for a runtime dependency, 🟡 for a build or dev-only dependency.
- 🟡 A security-relevant library (framework, auth, crypto, HTTP, parser) far behind the latest stable release with a known advisory. 🟡 A transitive dependency pinned or overridden to an older version without a recorded reason.
- 🟡 A manifest changed without its lockfile, or a lockfile that is not committed.
- 🔵 Unpinned or wildcard versions where the project otherwise pins.
- Audit commands: see "Dependency audit" below. In non-interactive review mode, judge from the manifests and lockfile in the file list only.

### 2. Secrets and credentials

- 🔴 A hardcoded password, API key, private key, token or connection string with embedded credentials in source, config, scripts, fixtures or examples that look real. Secrets belong in environment variables or a secrets manager.
- 🔴 A secret in a file that is not ignored by version control, or a config file meant to hold local secrets that is missing from the ignore list.
- 🔴 A privileged or server-side credential referenced anywhere in code that ships to clients.
- Secrets in history: only in an interactive audit, and only by listing which commits and files are affected (kind and location, never the value), using read-only history commands. The remedy is rotation first, history rewriting second.
- Not a finding: a documented public identifier, and a placeholder in an example or template file.

### 3. Authentication and session handling

- 🔴 Passwords stored or compared in plaintext, or hashed with a fast or broken algorithm (MD5, SHA-1, unsalted hashes) instead of a slow password hash with adequate cost.
- 🔴 A token or session identifier in a URL or query string (it lands in logs and history), or a credential written to a second storage location beyond the one the auth mechanism manages.
- 🔴 Hand-rolled token parsing or signature handling where the project's auth library provides it, or token verification that can be skipped or accepts an unsigned or "none" algorithm.
- 🟡 Cookies carrying session credentials without the protective attributes the stack offers (HttpOnly, Secure over HTTPS, a SameSite policy), or a session without expiry or invalidation on logout and password change.
- 🟡 An authentication error path that is swallowed, leaving the UI or caller in a signed-in-looking state with no real session.
- 🟡 Login, reset or sign-up responses that reveal whether an account exists, and no rate limiting or lockout on credential endpoints.
- 🟡 State-changing requests authenticated by an ambient credential (cookie) with no CSRF protection, or CSRF protection disabled without a comment explaining why it is safe.
- 🟡 A new redirect-based flow (password reset, email confirmation, OAuth callback) whose allowed redirect targets are configured outside the repository: note that the configuration step is needed.

### 4. Authorization and access checks

- Identify where authorization is enforced, then check that it is enforced there for the code in scope.
- 🔴 A route, endpoint or operation returning or changing user-owned data with no authentication or ownership check; a write operation reachable without authentication.
- 🔴 An object looked up by a client-supplied id with no check that the caller may access it (insecure direct object reference), including privilege fields a client can set on itself (mass assignment).
- 🔴 Data hidden or filtered only in client code (a filter in the UI layer) as the means of keeping other users' data safe, when the underlying query returns it.
- 🟡 A new data-access method whose scoping intent is not backed by a corresponding access rule in the same change.
- 🟡 Administrative or diagnostic endpoints (health detail, environment dump, metrics, debug) reachable without authentication in production configuration.
- 🟡 A privileged-execution construct (a function or service running with elevated rights) with no comment justifying why it bypasses the normal access model.
- 🟡 A 404 versus 403 distinction that confirms the existence of resources the caller must not know about.

### 5. Injection and unsafe input handling

- 🔴 User input concatenated into a SQL, query-language, LDAP, template or expression string instead of bound parameters.
- 🔴 User input reaching a shell or process invocation through a shell string; arguments must be passed separately and validated.
- 🔴 Deserialization of untrusted data into arbitrary types, or evaluation of user-supplied code or expressions.
- 🟡 Missing validation of type, length, range or format at the trust boundary; unbounded request sizes, page sizes or pagination limits.
- 🟡 Server-side requests to a user-supplied URL with no allow-list (SSRF), and regular expressions with catastrophic backtracking on user input.
- 🟡 Redirects to a user-supplied target with no allow-list.

### 6. Output encoding and XSS-class issues

- 🔴 User-controlled content written into HTML, script, style or attribute context without encoding or sanitization, or via an "insert raw HTML" API. If the session credential is readable by page scripts, say so: it raises the stakes of every finding in this section.
- 🟡 A user-controlled URL in a link or source attribute with no scheme allow-list (javascript: and data: schemes).
- 🟡 Every use of an API that disables the framework's built-in sanitization needs an adjacent comment justifying it; flag the ones without.
- 🟡 User input embedded in a response header, a log line or a generated file format (header, log or CSV/formula injection).

### 7. Logging of sensitive data

- 🔴 Passwords, password hashes, tokens, session objects, keys or full payment or identity data written to logs, analytics or crash reports, even at debug level.
- 🟡 Personal data or absolute paths containing a user's home directory in logs; log identifiers or relative paths instead.
- 🔵 Logs and error reports lacking a redaction step for request bodies and headers.

### 8. Error disclosure

- 🔴 Stack traces, query text, internal paths or schema details returned to the client in an error response body.
- 🟡 A caught exception re-thrown with its original message embedded in a response; return a generic message to the client and log the detail server-side.
- 🟡 Debug or verbose-error mode enabled in a production configuration.

### 9. Transport, CORS and CSP-class configuration

- 🟡 Wildcard cross-origin access (`*`) on endpoints that use credentials or return private data; the allow-list should name the known frontend origins in production. 🟡 An allowed-methods or allowed-headers list that does not match what the API actually uses.
- 🟡 Plain HTTP for anything carrying credentials, TLS verification disabled, or missing transport-security headers where the project controls them.
- 🔵 Missing content-security-policy, frame-ancestors, content-type-sniffing and referrer headers where the project controls response headers.
- 🔵 Secure defaults overridden in framework configuration with no comment.

### 10. File handling

- 🔴 A file operation using a user-supplied path without canonicalization and a containment check against an allowed root (path traversal), including endpoints that return file contents for a path derived from a request.
- 🔴 A user-supplied filename written to disk without sanitizing separators, parent-directory segments, null bytes and leading dots.
- 🔴 An API response that exposes an absolute filesystem path; hand callers an opaque id.
- 🟡 An upload or read path that trusts the extension alone to determine content type; verify the content as well, and enforce size limits.
- 🟡 Decoding of images, archives or documents with no limit on dimensions or expanded size (decompression bombs, zip slip).
- 🔵 Temporary files not cleaned up on every path, or created with predictable names or broad permissions.

## Non-interactive review mode

Used when a review phase invokes the skill with a file list (`[[reviews]] skill = "security-reviewer"`). No sweep, no questions, no edits to source. A project wires it like this:

```toml
[[reviews]]
name  = "security"
focus = "authentication, authorization, input handling, secrets, dependencies"
skill = "security-reviewer"
when  = ["**/auth/**", "**/*.env*", "**/package.json", "**/requirements*.txt", "**/pom.xml"]
```

**Input**
- `changed_files`: the files to review, taken verbatim. These are the entire scope.
- `deleted_files` (optional): the subset of `changed_files` that no longer exists. Review what the deletion removes (`git show HEAD:<file>`); do not route it to "Not reviewed".
- `bulk_files` (optional): the subset that is a lockfile, generated, minified or binary file. Do not read these in full; check only what the change implies (a manifest changed with no lockfile change, an unexpected new dependency in a lockfile hunk).
- `id`: the bug id or change name, used in the report filename. Default `adhoc` when absent.
- `focus` (optional): extra text from the review's `focus`; give it extra weight, it does not narrow the scope.
- `self_review` (optional): `yes` when the caller runs you inside its own context, which is always so from the review phase. The report then starts with `Self-reviewed: yes`.
- Review the change, not the files: see the changed lines with `git diff HEAD -- <file>` (an untracked file is new in full). A defect on a line the change did not touch is not a finding; mention it, if at all, in a plain (non-checkbox) "Pre-existing, not counted" bullet in the header.
- A finding cites `<file>[:<line>]`; leave out the line when it has none (a missing test, a lockfile not updated).

1. Review exactly the listed files. Read each one fully, plus the minimum surrounding code needed to judge a finding (a caller, a config it reads). Lockfiles and manifests are in scope only if they are in the list. Do not widen the scope to the rest of the repository and do not review files that are not listed.
2. Load the project context (see "Project context first"); apply the checklist sections that fit the files, and weight the optional focus text. In this mode, project facts you cannot determine without asking become a stated assumption in the report header, not a question.
3. Write `<reports_dir>/review/security-<id>-<YYYY-MM-DD>.md` (create the folder if needed; if the name exists, append `-2`, `-3`). Start with a header line naming the scope (the files reviewed, the focus) and the assumptions made. When `self_review` is `yes`, the report starts with `Self-reviewed: yes`. Then one checkbox line per finding, and nothing else per finding:

   ```
   - [ ] 🔴|🟡|🔵 <file>[:<line>] — <what is wrong and why it matters>
   ```

   Group by severity, Critical first. No findings: write the header and the line `No findings.` Never include a secret's actual value, only its file:line and kind.
4. Hand back exactly one line and no other text:

   ```
   REVIEW: <n> critical, <n> warning, <n> suggestion — report <path>
   ```

   Counts are computed from the checkbox lines in the report just written, not from memory. A review that could not read some listed file says so in the report header; it does not silently skip it.

The caller fixes the findings and may invoke the review again; each round writes a fresh report. Do not tick boxes or edit source in this mode.

Example `.backlog-kit.toml` entry:

```toml
[[reviews]]
name  = "security"
focus = "authentication, authorization, user input, file handling, secrets, dependencies"
skill = "security-reviewer"
when  = ["src/**/auth*", "src/**/api/**", "**/*.sql", "package.json", "package-lock.json", "requirements*.txt"]
```

## Security audit (interactive)

1. Agree the scope with the user: the whole repository, a directory, a pull request or a feature. For a whole-repository audit, split it by architecture layer or top-level area (for example one pass per source area plus one cross-cutting pass for dependencies, configuration and anything spanning two layers) and write one report per pass, so each is small and the user can fix one at a time. If the host can run subagents, run the passes in parallel with self-contained prompts (area, checklist sections, output path, "write the report yourself and return only the counts and the path"); otherwise run them one after another.
2. Read every file in scope that touches authentication, authorization, input handling, file I/O, secrets or persistence before forming an opinion. Load the project context first.
3. Apply the checklist and write the report to `<reports_dir>/security-review/SECURITY_REVIEW_FINDINGS_<YYYY-MM-DD>[_<area>].md` (append `-2`, `-3` on collision; never overwrite an earlier report). Use the same checkbox line format as above, grouped by severity, with a short header naming the scope and the repository state reviewed. Write only what this run found.
4. Show the user a short summary: counts per severity, the single most important issue, a verdict on whether it is safe to merge, and the report path. Omit empty severity groups.

## Dependency audit (interactive)

1. List the manifests and lockfiles and the package managers they imply.
2. Use the project's own package-manager audit command (for example the manager's `audit` or `outdated` subcommand) only if it is already installed and needs no installation and no network write (no auto-fix, no lockfile modification). If it needs installation, an account, or would modify anything, report `NOT RUN` with the reason and fall back to reading the manifests and lockfile against what is known.
3. Report advisories by severity with the fixed version if one exists, then outdated security-relevant libraries, then hygiene issues (checklist section 1). Write the report as in the security audit, with suffix `_dependencies`. Upgrading is not done here; offer the fix workflow or the project's own dependency-upgrade process.

## Fix workflow (interactive)

For an existing findings report. **This workflow never commits**; changes stay uncommitted in the working tree.

1. **Locate.** Use the report the user names; otherwise the most recent date with any `SECURITY_REVIEW_FINDINGS_*` or `review/security-*` report under `<reports_dir>`. Drop reports with no unchecked boxes. If several remain, show each with its scope and severity counts and ask which to do first; work on one report at a time, Critical-heavy first by default. If none exist, say so and stop.
2. **Read and ask.** Read the whole report, then ask whether to fix a whole severity group or a specific finding; offer only those with unchecked boxes.
3. **Fix loop**, one finding at a time:
   1. Read the affected file in full context before changing anything.
   2. If the fix hinges on a real decision (a breaking change to an auth flow, several valid remediations, a credential that needs rotating), stop and ask the user. A leaked credential is rotated by the user; the fix here removes it from code and says rotation is needed.
   3. Apply the fix and update or add tests for the new shape of the code.
   4. Verify with the project's own tests for the affected area. Run only commands that need no installation; if one cannot run, record `NOT RUN` with the reason.
   5. Tick the box immediately (`- [x]`) and append `**Fixed:** <what changed and why>` or `**Evaluated, no change made:** <rationale>`. A fix that incidentally resolves another unchecked finding ticks it too, with a note.
   6. Never write a secret's value into a fix note or report.
4. **Continue.** After the selected scope, run the widest verification available once (the project's full tests and build, if configured in `[[gates]]`), then ask what is next. Stop when the user says to or every report is fully ticked.
5. Say plainly at the end that nothing was committed and what to review.

---

## Guardrails

- **Never run `git commit`, `git push` or open a PR.** This skill reads code and writes reports under `<reports_dir>`; only the fix workflow edits source, and only with the user driving it.
- Non-interactive review mode asks no questions, reviews only the listed files, edits no source and writes exactly one report.
- Never print, quote or copy a secret's value into a report, chat message, commit-style note or tool argument; location and kind only.
- Do not read files the project documents as holding real secrets; use their example counterparts.
- Every finding carries file:line evidence from code that was actually read. No speculative findings, and no severity inflation.
- Never install system packages or change anything outside the repository. A dependency audit runs the project's own audit command only if it needs no installation and no network write; otherwise report `NOT RUN`.
- Use read-only history commands when inspecting history; never rewrite it.
- Do not invent rules beyond the checklist and the project's own security notes. If the project's notes conflict with a generic check, follow the notes and say so.
- Keep the modes separate: a review phase invocation never starts a sweep, a fix, or a question.
