# Architecture Reviewer — the case that motivated the review
Read when: every architecture review (the model for the "hunt the broadcast" finding)

> Status: this case (BUG-077) is already fixed — the household-member bus was split, and `MedicationsRefreshService` now keeps its producers and consumers inside `medications/`. It is kept as the model of the finding, not as something to expect to find again.

`ActiveHouseholdMemberService` (`core/active-household-member.service.ts`) started as a household-member selection preference and quietly became the cross-feature "something changed, refetch" broadcast bus for Medications, Appointments, and Exams — 9 `.refresh()` call sites and 8 `.version()`-reading effects, none of it visible from the service's own name, and no single PR that added a call site would have looked wrong in isolation. Filed as **BUG-077** (`docs/backlog/bugs/BUG-077.md`); read it for the full write-up the review's report format is modeled on.
