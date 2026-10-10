# Code Reviewer — Supabase Service Usage, Auth & Component State
Read when: a `core/*.service.ts`, anything reading `AuthService` or calling Supabase, or signals/state in a component

## 4. Supabase Service Usage

🔴 Flag any service method that calls `.from(...)`/`.auth....` on Supabase
and does **not** check the returned `error` before using `data` — Supabase's
JS client never throws on a failed query; it resolves with
`{ data, error }`, and a missed `error` check silently propagates `null`/
stale data downstream instead of surfacing the real failure (see
`angular-developer` §8).

🔴 Flag a component that calls `this.supabase.client...` directly instead
of going through a `core/` domain service (same rule as §1.2, called out
again here because it's specifically a Supabase-usage violation, not just a
layering one).

🟡 Flag a domain service method that wraps a Supabase call in an
`Observable` (`of(...)`, `from(...)`) instead of returning the `Promise`
directly — there is no RxJS-based HTTP layer here to match; introducing one
adds indirection with no benefit (see `angular-developer` §8).

🟡 Flag a new table-backed query added to a service with no corresponding
mention of the RLS policy it depends on (in the PR description, a comment,
or the accompanying migration) — a missing `SELECT` policy makes the query
return an empty array with no error, which is easy to misdiagnose as a
frontend bug (see `CLAUDE.md`'s RLS gotcha, and `database-reviewer` for the
migration-side check).

### 4.1 N+1 Query Verification

Because this app has no backend to batch or cache requests, an N+1 issued
straight from the frontend costs one real round trip to the remote Supabase
project per row — on a page load this is directly user-visible latency, not
just an inefficiency. Check every changed service method and every changed
component for this shape:

🔴 Flag a loop (`for`/`for-of`, `.forEach`, `.map`) — in a `core/` service
**or** directly in a component — that issues one Supabase call
(`.from(...).select/insert/update/delete/upsert(...)`, or a call to another
service method that itself does one of those) per element of an
already-fetched array, where a single batched call would do:
  - Fetching each parent row's children one at a time in a loop instead of
    one `.in('parent_id', parentIds)` query (or a single join via nested
    `.select('*, child_table(*)')`) followed by an in-memory group-by.
  - Calling a `getX(id)`-shaped service method once per id from a `@for`
    loop in a template's `ngOnInit`/loader instead of adding (or reusing) a
    batched `getXByIds(ids)`/`getAllX()` variant and filtering/grouping the
    result client-side.
  - Re-running the *same* unbounded query (e.g. `getAllX()` with no
    filter) inside a loop instead of hoisting it above the loop and reusing
    the one result — this is worse than a classic N+1, since it repeats
    identical work rather than distinct per-row work (see the case below).

This is a distinct pitfall from §16's line-coverage gate and §21's mutation
score — a loop like this can be 100% covered and every mutant killed while
still being a real live-traffic performance bug, because nothing in the
test asserts on *how many times* the stubbed service/Supabase call fires.

**Accepted exception, don't blanket-flag:** `buildAccountExport()`
(`core/account-export.util.ts`) sequentially awaits per-household-member
calls (`getDosagesByHouseholdMember`, `getAppointments`, `getExams`) inside
a `for...of` loop over `householdMembers` — this is deliberate, documented
in the file's own comment immediately above the loop, and justified because
the whole-account export is a rare, user-initiated download action, not a
page load; a `household_member` list is also bounded by real-world family
size (see `CLAUDE.md`'s pagination section), so the fan-out is small and
one-time. Don't re-flag that specific loop. **Do** flag it if a future
change adds it to a page-load path, or if a *new* per-household-member
sequential loop appears somewhere that runs on every page render rather
than an explicit export action — the exception is scoped to that one call
site's justification, not a blanket pass for every household-member loop.
Note also that `buildAccountExport()`'s loop currently re-calls
`services.medicinesService.getAllMedicinesIncludingDeleted()` (an
unfiltered, non-household-member-scoped query) on every iteration instead
of once before the loop — if touching this function, flag that specific
redundant re-fetch as a 🟡 WARNING (wasted round trips even under the
loop's own accepted exception) even though the per-member calls themselves
are accepted.

🟡 Flag a paginated list component (per `CLAUDE.md`'s pagination section —
`TaskList`, `DocumentList`, `ExpenseList`, `FixedTermList`, `Medications`,
the `NotificationsService` consumer, etc.) whose row template or a
`fetchX()`/`loadAll()` follow-up triggers a **separate** Supabase read per
rendered row (e.g. resolving each row's `expense_type_id`/`document_type_id`
to a name via a per-row lookup call) instead of a single batched lookup
fetched once per page and joined/mapped client-side — the whole point of a
bounded page size is that a page's fan-out stays constant regardless of how
many total rows exist, and a per-row lookup call defeats that.

🟢 A loop that only does in-memory computation over an already-fetched
array (filtering, grouping, `classifyPendingPayment`-style pure functions —
see `expenses.service.ts`'s `computePendingPayments()`) is not an N+1 issue
and shouldn't be flagged just for containing a `for`/`.map` — the concern
here is specifically repeated *network* calls, not iteration itself.

---

## 5. Auth & Session State

🔴 Flag any code that reads or stores the Supabase session/JWT itself in
`localStorage`, a custom cookie, or anywhere outside `AuthService`/
Supabase's own client-managed storage — `AuthService`'s signal-backed
`session`/`user`/`isAuthenticated` (see `angular-developer` §11) is the only
sanctioned source of auth state.

🔴 Flag a guard or component that reads `AuthService.isAuthenticated()`
before `AuthService.ready` has resolved, in a code path where that
ordering actually matters (e.g. an app initializer or `main.ts` change) —
reading it too early can see a false "logged out" state before Supabase has
restored a persisted session.

🟡 Flag a new sign-in/sign-up/sign-out flow that doesn't handle the
`{ error }` Supabase returns (e.g. swallowing it instead of surfacing a
message to the user).

---

## 6. Component State & Signals

🔴 Flag component state stored as plain mutable class fields where a
`signal()` should be used instead (anything read in a template that changes
after initial render) — see `angular-developer` §10.

🟡 Flag a `computed()` that isn't `readonly`, or a private backing signal
that isn't `private readonly`.

🟡 Flag an `async ngOnInit()` (or any async data load) that doesn't set a
`loading` signal to `false` in a `finally` block — a thrown error without a
`finally` leaves the UI stuck showing a spinner.

🟡 Flag introduction of NgRx or any other global state library — this
project's state is local component signals plus services; there's no
documented need for one yet.

---
