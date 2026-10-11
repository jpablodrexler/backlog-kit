# Architecture Reviewer — multi-step writes without a transaction
Read when: every architecture review, and any deep-dive on data access

The app has no `.rpc()` calls, so a write made of several client calls is not atomic. The project's stance is recorded in `docs/decisions/0034-multi-step-writes-sequential-or-rpc.md` (status: Proposed; read its current status first).

- A multi-step write that can corrupt counts, dates or logs when it fails half-way (`completeTask`, `createTask`, the medicine and dosage save) and has no documented compensation: 🔴.
- A multi-step write with a documented best-effort or compensation rationale (for example `deleteExam`): list it under Strengths with the documentation cited.
- If the ADR has been Accepted, follow its text; if it was rejected or superseded, follow the newer record.
