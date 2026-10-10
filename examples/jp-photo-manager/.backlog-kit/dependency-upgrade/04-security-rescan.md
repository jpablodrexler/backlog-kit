# Security re-scan commands
Read when: cross-checking against security findings after applying bumps

## 5. Cross-Check Against Security Findings

```bash
cd JPPhotoManagerWeb/backend && mvn org.owasp:dependency-check-maven:check
cd JPPhotoManagerWeb/frontend && npm audit --audit-level=high
```

The vulnerable dependency, if transitive, needs an explicit
`<dependencyManagement>`/npm `overrides` entry.
