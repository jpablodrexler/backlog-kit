# Architecture Reviewer — the case that motivated the review
Read when: every architecture review (use it as the model for the "hunt the broadcast" finding)

Assess whether the pablo-web Angular frontend's overall structure — not a
specific diff or PR, but the shape of the system as a whole — still
follows recommended Angular practice and the project's own documented
conventions. This skill exists because the kind of issue it looks for
rarely shows up in a single-PR `code-reviewer` pass: it's the sort of
implicit coupling that accretes gradually, one individually-reasonable
change at a time, across many separate reviews that each only saw its own
diff. The worked example that motivated this skill: `ActiveHouseholdMemberService`
(`core/active-household-member.service.ts`) started as a household-member
selection preference and quietly became the cross-feature "something
changed, refetch" broadcast bus for Medications, Appointments, and Exams —
9 `.refresh()` call sites and 8 `.version()`-reading effects, none of it
visible from the service's own name, and no single PR that added a call
site would have looked wrong in isolation. Filed as **BUG-077**
(`docs/backlog/bugs/BUG-077.md`); read it for the full write-up this skill's
own report format is modeled on.
