# Code Reviewer — Known Project-Specific Pitfalls
Read when: every review

## 10. Known Project-Specific Pitfalls

| Pitfall                                      | What to look for                                                                                          |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Missing RLS policy read as a frontend bug     | A `.select()` call returning an empty array with no thrown error — check the matching migration/policy first, not just the TypeScript |
| Unchecked Supabase `{ error }`                | Any `.from(...)`/`.auth....` call whose `error` isn't checked before using `data`                          |
| Direct `supabase.client` call from a component | Bypasses the `core/` domain service layer                                                                  |
| N+1 Supabase calls in a loop            | A `for`/`.map`/`.forEach` issuing one Supabase read/write per array element instead of a single batched `.in(...)`/join query — see §4.1 for the accepted `buildAccountExport()` exception |
| Second `createClient(...)` call               | Anywhere other than `SupabaseService` — breaks the single-client invariant                                 |
| Secret/service_role key in `environment.ts`   | This file is committed by design and holds only the publishable/anon key — flag it if a `secret`/`service_role` key ever shows up here instead |
| `*ngIf`/`*ngFor` in new templates             | Angular's `@if`/`@for` control flow must be used                                                            |
| `.component.ts` infix reintroduced             | New components should match the existing no-infix naming (`task-list.ts`)                                  |
| Auth state read before `AuthService.ready`     | Guard/initializer logic that assumes a session is known before Supabase's `INITIAL_SESSION` event fires    |
| `jasmine.createSpyObj`/`vi.fn()`/Jest matchers in a `.cy.ts` file | This project uses Cypress Component Testing; `cy.stub()` + Chai assertions instead |
| Hardcoded UI string in a template               | Should be routed through `{{ '...' \| translate }}` and a key added to both `core/i18n/en.json` and `es.json` — see §13 |
| Raw date interpolation (`{{ task.deadline }}`)  | Should be formatted through `formatLocalizedDate()` first — see §13                                        |
| Field not filling its container despite `p-floatlabel` | The global `p-floatlabel > input/textarea/p-select/p-datepicker/p-autocomplete` rule in `styles.css` covers direct children only — a wrapped control, `p-inputnumber`/`p-multiselect`, or a control outside a `p-floatlabel` still needs its own width (BUG-064/068/086/089/091) — see §25 |
| Hint/field capped together, or hint overlapping its input | `max-width` on a wrapper holding input + hint, or global `.field-hint` negative `margin-top` inside a gap-less wrapper (BUG-086) — see §25 |
| Repeated rows whose trailing controls drift left/right | `flex: 1` text column without `min-width: 0`; conditional badge/count with no reserved slot (BUG-074) — see §25 |
| Button group with no deliberate distribution | Bare buttons as direct flex children, mobile-only rule written outside its media query, icon buttons stretched (BUG-049/076/087) — see §25 |
| Required field outlined red on first render | A component whose template uses `[formField]` on an Optimus control but lacks `...FORM_INVALID_GATE` in `imports`, an inline add/edit row with an attempted signal but no `[appFormAttempt]`, or a manual `[invalid]` next to `[formField]` (BUG-094, ADR 0031) — see §25 |
| `p-select`/`p-datepicker`/`p-multiselect`/`p-autocomplete` in a dialog with no `appendTo="body"` | Panel clipped by the dialog's scroll area or closes immediately (BUG-088/092); `npm run overlay-append:check` catches it in dialog templates — see §25 |
| Floating label clipped or truncated | A `p-floatlabel` control first in a scrollable dialog body with no top room (label clipped at the container edge), or hard-sized narrower than its label (ellipsised) — BUG-053 — see §14 |
| New shell scrolls the whole document under a fixed header | Chrome should sit outside a scroll container wrapping only the content (`100dvh` flex column + `overflow-y: auto`, as `app.css` does); `sticky` beats `fixed` if document scroll is kept — BUG-054 — see §14 |
| Function past the cyclomatic complexity threshold | `npm run complexity` reports a function over 15 — see §15                                                |
| Line coverage below 80%                        | `npm run coverage:check` reports under 80% — see §16                                                     |
| Untyped (`any`) identifier                      | `npm run type-coverage:report` lists it — see §17                                                        |
| Unused export/file/dependency                   | `npm run dead-code:report` lists it — see §18                                                            |

---
