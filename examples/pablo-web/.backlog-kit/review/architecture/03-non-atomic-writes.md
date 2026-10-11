# Architecture Reviewer — multi-step writes without a transaction
Read when: every architecture review, and any deep-dive on data access
Maps to: applies under D3 (data access)

The app has no `.rpc()` calls, so a write made of several client calls is not atomic. The project's stance is recorded in `docs/decisions/0034-multi-step-writes-sequential-or-rpc.md` (status: Proposed; read its current status first).

- Any write made of several client calls counts, whether it creates, updates or deletes (for example `updateTask`'s delete-then-reinsert of the recurrence weekdays): judge it by what a failure half-way leaves behind, and by whether a wrapper retries it (`callWithLogging` on `completeTask` can insert a second `task_completion` row).
- A multi-step write that can corrupt counts, dates or logs when it fails half-way (`completeTask`, `createTask`, the medicine and dosage save) and has no documented compensation: 🔴.
- A multi-step write with a documented best-effort or compensation rationale (for example `deleteExam`): list it under Strengths with the documentation cited.
- If the ADR has been Accepted, follow its text; if it was rejected or superseded, follow the newer record.
