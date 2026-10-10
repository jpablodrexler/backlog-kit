# Majors never applied without approval
Read when: every run

## 3. Classify & Decide

🔴 Never apply a major-version bump to `spring-boot-starter-parent`,
`@angular/core`, or any other framework-defining dependency without explicit
user approval for that specific package — these routinely carry breaking
changes this project's tests may not fully cover (e.g. a removed
auto-configuration, a changed default).

🟢 A patch/minor bump to a leaf dependency with no direct API usage in this
codebase (a transitive-only dependency bumped for a CVE fix) is lower risk
than a direct, heavily-used dependency (Spring Data JPA, MapStruct, Angular
Material) — note this distinction in the report (§6) but the automatic/
manual split above still applies uniformly by bump type, not by usage
weight.
