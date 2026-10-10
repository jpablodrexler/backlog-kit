# Security re-scan commands
Read when: cross-checking against security findings after applying bumps

## 5. Cross-Check Against Security Findings

```bash
npm audit --audit-level=high        # root
cd frontend && npm audit --audit-level=high
```

The vulnerable dependency, if transitive, needs an explicit npm `overrides`
entry.
