# Guardrails and scope

Read when: every run

- Never document behavior you haven't verified in the actual code — no
  inferring a config default from a variable name, no guessing an
  endpoint's auth requirement from the URL shape. Read `SecurityConfig`'s
  rule list (and any method-level `@PreAuthorize`) directly for auth
  columns.
- Never read `JPPhotoManagerWeb/k8s/secret.yaml` or
  `JPPhotoManagerWeb/k8s/catalog-volumes.yaml` while doing this — same rule
  as `security-reviewer`/`database-reviewer`/`incident-response`. Secret
  *keys* (not values) can be checked via the `.example` templates.
- Don't let `CLAUDE.md` regrow the content this skill's first run extracted
  out of it — a REST API table, a full config table, or a multi-paragraph
  persistence/caching narrative appearing there again is itself a finding
  to fix (move it to `docs/`), not just a staleness issue to patch in place.
- Manifest-parity and dashboard-panel fixes (§2, §3) are config edits, not
  prose — call them out distinctly in the chat summary rather than folding
  them silently into the same list as a typo fix in `docs/features.md`.
- This skill's scope is `CLAUDE.md`, `README.md`, and the files directly
  under `docs/` (§1's table), plus the manifest-parity and metrics checks
  (§2, §3). It does not touch `docs/decisions/*.md` (owned by
  `decision-record` — an append-only decision history, not current-state
  reference material this skill keeps synced against the code) or any of
  the gitignored `docs/reports/{code-review,security-review,database-review,spec-compliance,incident-response}/`
  report directories (owned by their respective skills) — those are
  tracked/managed elsewhere, not part of this skill's "keep the docs
  honest" job.

Full-sweep note: for the REST API / config / curl-reference rows in
particular, grep every controller / every `@Value` usage directly — don't
sample a few and assume the rest are current (this is exactly how
`CLAUDE.md`'s REST API table ended up covering 6 of 15 controllers before
the doc restructuring that created this skill).
