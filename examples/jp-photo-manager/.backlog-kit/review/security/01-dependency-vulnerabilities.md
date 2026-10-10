# Dependency Vulnerabilities
Read when: a dependency manifest or lockfile changed, or a full-codebase sweep reaches the cross-cutting layer

## 1. Dependency Vulnerabilities

### 1.1 Backend (Maven)

Run the OWASP dependency check and review the output:

```bash
cd JPPhotoManagerWeb/backend
mvn org.owasp:dependency-check-maven:check
```

Alternatively, audit with the Maven Versions plugin:

```bash
mvn versions:display-dependency-updates
```

🔴 Flag any dependency with a known CVE rated **CRITICAL** or **HIGH** in the
NVD database.

🟡 Flag any Spring Boot, Spring Security, or Flyway version that is more than
two minor versions behind the latest stable release — these libraries receive
frequent security patches.

🟡 Flag any transitive dependency that is being overridden with an older version
via `<dependencyManagement>` — verify the override is intentional.

### 1.2 Frontend (npm)

```bash
cd JPPhotoManagerWeb/frontend
npm audit --audit-level=high
```

🔴 Flag any package with a `critical` or `high` severity audit finding that has
a fix available (`npm audit fix`).

🟡 Flag packages that are significantly outdated and have known security advisories
(check https://security.snyk.io or the npm advisory database).

🟢 Flag `devDependencies` with audit findings — lower risk but still worth
updating, since build tools can be exploited in CI.
