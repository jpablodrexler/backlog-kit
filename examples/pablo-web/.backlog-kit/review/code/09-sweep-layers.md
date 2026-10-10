# Code Reviewer — Full-Codebase Sweep Layers
Read when: a full-codebase sweep

**The layers:**

| Layer key       | Report suffix    | Directory scope             | Primary checklist sections |
| ---------------- | ------------------ | ------------------------------ | ----------------------------- |
| Frontend core     | `frontend-core`     | `frontend/src/app/core/**`     | §1.1, §4, §5, §13               |
| Frontend features | `frontend-features` | `frontend/src/app/<feature>/**` — every top-level folder under `app/` except `core/` and `shared/` | §1.2, §2, §3, §4.1, §6, §7, §13, §14 |
| Frontend shared   | `frontend-shared`   | `frontend/src/app/shared/**`   | §1.3, §6, §7, §13, §14          |
| Cross-cutting     | `cross-cutting`     | Whole frontend; no single directory | §8, §9, §13, §14, §15, §16, §17, §18, §19, systemic naming patterns, dependency-direction violations |
