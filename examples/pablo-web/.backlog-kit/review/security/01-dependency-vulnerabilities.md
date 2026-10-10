# Dependency Vulnerabilities
Read when: a dependency manifest or lockfile changed, or a full-codebase sweep reaches the cross-cutting layer

## 1. Dependency Vulnerabilities

```bash
npm audit --audit-level=high            # root (supabase CLI devDependency)
cd frontend && npm audit --audit-level=high
```

🔴 Flag any package with a `critical` or `high` severity audit finding that
has a fix available (`npm audit fix`).

🟡 Flag `@angular/*`, `@angular/material`, or `@supabase/supabase-js`
versions significantly behind latest with a known security advisory.

🟢 Flag `devDependencies` with audit findings — lower risk but still worth
updating, since build tools can be exploited in CI/Vercel's build
environment.
