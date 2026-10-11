# Product Scope Roaster — examples already visible in this project's scope
Read when: every product scope review; test each example on its merits, do not assume it holds

## The dimensions

### 1. Merge candidates
Two or more features (shipped, planned, or one of each) that are close
enough in purpose or interaction shape that a user would reasonably expect
one screen, one concept, one place to look — not two nav entries they have
to learn are actually different things. A near-mirror pair is the
strongest signal: e.g. planned `savings-goals` (#60) is documented as
"Mirrors Budgets, but toward a cumulative target rather than a monthly
cap" — that's two full CRUD screens, two nav entries, and two things to
discover, for what a user would think of as one idea ("a money target")
with a toggle. Look for this pattern across the whole scope, not just
Finance: shared shape, separate surface, no toggle.

### 2. Split candidates
A feature (shipped or planned) whose scope has grown, or is proposed to
grow, past what a user would recognize as "one thing" — usually visible as
a single backlog area quietly accumulating unrelated sub-capabilities over
several rows. The meal planner is the clearest existing case: dish
catalog → daily log → a suggestion engine → per-user preferences →
household-member overrides (#69) → an ingredient/shopping-list layer (#55)
→ full recipe content (#86). Ask, for any such area: would a new user
recognize all of this as "logging what we ate," or has it become three or
four separate products sharing one nav entry? Also flag a single planned
row whose own description reads as multiple unrelated deliverables bolted
together (a schema addition plus an unrelated UI relocation, say) — that's
a scope-split candidate at the row level, not just the feature-area level.

### 3. Missing functionality — gaps in an existing story
Somewhere an area tells half a story: it solves the "remember this exists"
half but not the "and here's what to do about it" half, or it covers every
sibling case but one. Ground each gap in the feature's own stated
non-goals and deferrals where possible — `docs/features.md`/`features-planned.md`
are unusually explicit about what was deliberately left out ("Deliberately
out of scope: ..."), which is exactly where a PO should ask "was that the
right call, or is that the thing a real user will ask for first?" Concrete
examples already visible in this scope: Vehicles (`docs/features.md`
"Vehicles") explicitly gets no daily-notification source for coming-due
registration/insurance and no Expenses-module link for a logged service
cost — meaning the one module modeling recurring compliance deadlines and
real spending is the one place in the entire app that doesn't participate
in either the reminder system or the expense ledger every sibling feature
already plugs into. Look for that shape elsewhere: an area that reuses
every established convention (reference-table pattern, soft-delete,
CSV export) except the one that would have made it actually useful
day-to-day.

### 4. Cross-feature consistency & everyday friction
Patterns a user would learn once and then expect to hold everywhere, that
instead quietly differ feature to feature — each instance individually
defensible, the sum of them a trap:
- **Delete reversibility with no visible signal.** Tasks/Documents/Expense
  Types/Medicines (and several planned areas) soft-delete into "Deleted
  Items," recoverable. Expenses/Fixed Terms/Appointments/Exams/Gas
  Canister Replacements/Vehicles/Budgets/Savings Goals hard-delete,
  gone forever — through the *same generic confirm dialog wording* in
  both cases. A user who has recovered a deleted task once will
  reasonably assume the same "undo" safety net exists everywhere, and
  find out otherwise only by losing an appointment record permanently.
- **A fragmented "who/where do I reach" model.** This app independently
  reinvents "a person or place I need to contact" at least four times —
  `household_member` (Medications/Appointments/Exams/Vaccinations),
  `contact` (a general personal directory, planned #65, with its own
  phone/address/important-dates/gift-ideas), `doctor` (a medical-only
  directory), and `pharmacy`/`emergency_service`/`medical_location`
  (institution directories). None of these interoperate — a doctor's
  phone number, once entered, is not discoverable from Contacts; an
  emergency service is a completely separate add flow from a Contact even
  though both are "a phone number I might need in a hurry." A real user
  will ask "didn't I already enter this person somewhere?" and be right
  to.
- **Scattered configuration surfaces.** `Settings` already hosts six
  unrelated sections (password, notification timing, data export,
  statement-import rules, meal planning, household members) with more
  explicitly invited ("structured to allow further account-settings
  sections"), while several planned features add yet another
  *module-specific* "Manage X" dialog (doctors, locations, dishes,
  pharmacies, emergency services) reachable only from that module's own
  toolbar. A user looking for "where do I edit X" has no single rule to
  follow — sometimes Settings, sometimes a toolbar button on an unrelated
  page.
- Any other "I learned the pattern here, it's different two features
  over" case surfaced while reading — name the two features and the
  exact behavioral difference.

### 5. Scope coherence — what is this product actually for?
Step back from individual features and ask whether the backlog as a whole
is still one coherent thing or is drifting into "whatever seemed buildable
next." The planned list's own top-priority (P1) tier is the sharpest
evidence to weigh here: `personal-command-center` (#87), `cross-module-projects`
(#88), and `rules-and-automations-engine` (#89) are three large,
cross-cutting, infrastructure-flavored features proposed back to back,
for an app whose actual daily use is a household remembering tasks,
bills, and medications. A generic rules engine and a Zapier-style
automation builder are the kind of feature a *platform* needs, not
obviously what a family tracking their own pills and payments asked for.
Say plainly whether the roadmap still reads as "help me not forget
things" or has started reading as "build a personal ops platform," and
name which specific planned rows are the evidence either way.
