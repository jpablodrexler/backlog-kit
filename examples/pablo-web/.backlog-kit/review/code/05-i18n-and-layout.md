# Code Reviewer — Localization, Layout & App-Shell Gotchas
Read when: any template/CSS change, a user-facing string or date, a form field, dialog, button group or overlay

## 13. Localization (i18n)

See `angular-developer` §18 for the full pattern this section checks
against: `LanguageService`, `TranslatePipe`/`resolveTranslation()`,
`core/i18n/en.json`/`es.json`, `formatLocalizedDate()`, and
`syncDatepickerLocale()`.

🔴 Flag a hardcoded, user-facing string added directly in a template or
component instead of routed through the `translate` pipe
(`{{ 'tasks.title' | translate }}`) or `resolveTranslation()` — this
includes a string built for a dialog's `MAT_DIALOG_DATA` (e.g. a delete
confirmation message).

🔴 Flag a new translation key added to only one of `core/i18n/en.json` /
`es.json` — a key missing from one file silently falls back to the raw key
string in that language at runtime, with nothing at build time to catch
the omission. Both files should gain the key in the same change.

🔴 Flag a date-only column (`deadline`, `expiry_date`, `notification_date`,
or similar) interpolated directly in a template (`{{ task.deadline }}`) or
formatted with `DatePipe`'s `date:'short'`/`date:'medium'` instead of
`formatLocalizedDate()` — the locale-preset formats don't match this
project's `M/d/yyyy` (en) / `d/M/yyyy` (es) convention, and bypassing
`formatLocalizedDate()`'s forced-UTC handling can roll the displayed date
back a day west of UTC.

🟡 Flag a new `p-datepicker` added to a form without `[appDatepickerField]`
(use it instead of `[formField]` — the datepicker's typed text is wiped by
Signal Forms' `writeValue()` echo) and without `[dateFormat]` bound to
`syncDatepickerLocale()` in the containing component — otherwise the picker
keeps showing `mm/dd/yy` order even after the user switches the UI to Spanish.

🟢 Don't flag a `shared/` component's template for using `| translate` —
`TranslatePipe` lives in `core/` and injects `LanguageService` internally,
but a `shared/` component declaring it in `imports: []` and using it in
the template (as `ConfirmDialog` does) isn't the component's own class
injecting a `core` service, so it doesn't violate the `shared/` layering
rule in §1.3.

---

## 14. Layout & App-Shell Gotchas (Optimus UI)

For the recurring layout families — control not filling its container,
misaligned rows, accidental button-group distribution, clipped overlays, error
state before interaction — see §25 below. See `angular-developer` §12 and §21
for the full pattern each check here is judged against, plus the CSS to apply.

🟡 Flag a `p-floatlabel` control whose floating label can be **clipped or
truncated** (BUG-053, the dish catalog dialog):
- Placed as the first element inside a dialog body (or any
  `overflow: auto/hidden` container) with no top room — the floated label sits
  above the control's border box and the container clips it at its padding box
  once the content scrolls.
- Hard-sized narrower than its label needs (`width: 7rem` / `flex: 0 0 7rem`
  under a longer label) — the label renders with an ellipsis. A labelled field
  should use `min-width` plus a growable `flex`, size to content, or carry a
  shorter label; a fixed pixel width is CLAUDE.md's "avoid fixed pixel widths"
  rule violated at a specific spot. Check it (and any *existing* fixed-width
  field in the same view) at the Samsung S23 Ultra viewport per
  `angular-developer` §19.

🟡 Flag a form field, textarea, or dialog whose width was left to a library
default rather than an explicit rule, when checking it at a desktop viewport
(1920×1080, `angular-developer` §20) shows it rendering narrow and
mobile-sized while the rest of its container sits empty (BUG-068, the medicine
form dialog's Nombre/Notas fields) — the opposite failure mode of the
fixed-pixel-width flag above. This is common inside a dialog opened via
`dialogService.open()` with no `width`/`style`/`breakpoints` option: the
panel's width then comes entirely from the dialog library's default sizing.
Confirm any new or touched dialog/form was actually checked at the desktop
viewport per `angular-developer` §20, not just at the mobile size.

🟡 Flag an app-shell or full-page layout that pins its `p-toolbar` with
`position: fixed` plus a compensating `margin-top` on the content. The shell
(`app.css`) is a `height: 100dvh` flex column: a fixed-size toolbar row, then a
content region with `flex: 1; min-height: 0; overflow-y: auto` — so only the
content scrolls, the window scrollbar never runs behind the toolbar (BUG-054)
and no sibling needs an offset. A new shell restructure follows the same
shape; if document scroll is genuinely kept, `position: sticky` beats `fixed`
since it needs no `margin-top` offset. Also flag toolbar colours set with a
raw `background` instead of the `--p-toolbar-background`/`-color` component
tokens, and a flyout `<p-popover>` opened from the toolbar, nav rail or bottom
nav without `styleClass="app-chrome-menu-panel"` (BUG-026/028).

🟡 Flag a row-like flex container (a list row, a card's action bar, any
element packing an icon/name/secondary-text/count/buttons on one line)
whose CSS gives it `display: flex` with no `flex-wrap` and no
narrow-viewport fallback (a media query, a container query, or a
restructure into a two-line layout below a breakpoint). At full width
this looks fine; at a real phone width the flex children fight over
too little space, and a shrinking text child (`min-width: 0` or similar)
can visually overlap a fixed-width sibling instead of the row wrapping
cleanly — this is what BUG-043 (`/medications`' as-needed rows,
`.med-row` in `daily-schedule.css`) and BUG-015 (action-button rows
overflowing) both were. Confirm the change was actually checked at the
Samsung S23 Ultra viewport (CSS 384×824 @3.75x) per `angular-developer`
§19/CLAUDE.md's Mobile-first CSS convention, not just eyeballed at
desktop width or a wider handset preset.

🟡 Flag a toolbar action-button row (Export/Add/Import/Print, …) with no
shared width rule on its buttons below the handset breakpoint — whether
the buttons currently sit side by side on one row or wrap onto separate
lines via `flex-wrap: wrap` (the BUG-015 fix, which stops the
horizontal-scroll problem but not the sizing one). Each `pButton` still
sizes to its own icon+label content by default, so a short label ends up
visibly narrower than a long one, reading as a ragged, misaligned toolbar
(BUG-047 fixed this for `/medications`'s `.toolbar-actions`; BUG-067 tracks
the identical unfixed pattern still present on every other list route's
toolbar — `task-list`, `document-list`, `expense-type-list`,
`expense-list`, `fixed-term-list`, `budget-list`, `appointment-list`,
`exam-list`, `meal-log-list`, and any list route added since). This is a
standing convention, not a one-off: **any new or touched list-route
toolbar must give its action buttons a uniform width on mobile** —
stacking each one full-width (`flex-direction: column; align-items:
stretch` + `width: 100%` per button) below the handset breakpoint is the
simplest correct fix, mirroring `medications.css`'s
`@media (max-width: 37.5rem)` block. Confirm at the Samsung S23 Ultra
viewport per `angular-developer` §19.

🟡 Flag an error state shown before the user has edited or attempted
anything — a validated add-row or optional field that outlines red or shows
its "required" message on a bare focus-then-blur or on first render (BUG-019,
BUG-052, BUG-094). The app-wide fix is `FORM_INVALID_GATE`; see §25 and
`angular-developer` §14/§21.5a.

---

## 25. Layout Consistency: Field Width, Row Alignment, Button Groups, Overlays

Layout defects are the single largest family of bugs filed against this app
(BUG-015, 016, 043, 047, 049, 053, 064, 067, 068, 074, 076, 086, 087, 088,
089, 091, 092, …). They repeat the same four mistakes, and each one passes a
"does it render?" glance at desktop width. For any changed template/CSS, work
through these; the construction rules and CSS are in `angular-developer` §21
(`reference/layout-patterns.md`) — cite it in the finding instead of
re-explaining.

🟡 **Control doesn't fill its container.** `frontend/src/styles.css` now sizes
every **direct child** of a `p-floatlabel` (`input`, `textarea`, `p-select`,
`p-datepicker`, `p-autocomplete`) to `width: 100%`, so a normal
`<p-floatlabel><input pInputText/></p-floatlabel>` needs no per-form rule —
**flag a newly added per-component `p-floatlabel input { width: 100% }`** as
unnecessary (🟢). The bug class (BUG-064, 068, 086, 089, 091) is still possible
where the global rule does not reach, so look for: a control wrapped in an
extra element (not a direct child of `p-floatlabel`) or rendered by another
component's template; a `p-inputnumber`/`p-multiselect` inside a
`p-floatlabel` (not in the global rule or its test); a control outside any
`p-floatlabel` (filter bars, inline `pInputText` next to a button) with no
explicit width; a class-based narrow width that was meant to apply to the
control but is on a wrapper that also holds the field's hint; a form class
reused for a second form; a fixed `width`/`flex: 0 0 Nrem` narrower than the
longest label in `es.json`/`en.json`; a floated label as first child of a
scroll container with no top room.

🟡 **Rows that should align don't.** In a repeated row/card, a `flex: 1`
text column without `min-width: 0` (BUG-074); trailing controls whose x
depends on whether an optional badge/count rendered; sibling fields with
different heights/`appearance`; a hint on one field pushing its neighbour
out of line. Repeated rows meant to read as columns should use shared grid
tracks. Also flag **divergent row shapes** for the same concept — a new
section/state that adds a parallel layout instead of extending the existing
row class (BUG-016, BUG-076), or action controls placed differently per
state.

🟡 **Button group with accidental distribution.** Two or more buttons with
no wrapping container (each wraps independently, last icon ends up alone);
a handset-only rule (`flex: 1 1 100%`, `width: 100%`) written outside
`@media (max-width: 37.5rem)` so it applies on desktop (BUG-087); icon-only
buttons caught by a stretch rule; a toolbar group without a uniform-width
handset rule (see the toolbar finding in §14); a loading spinner replacing a
label with no sized `.button-spinner` (button resizes on click, BUG-061).
For every button group in the diff, ask the reviewee: "what does this look
like at 384px, and at 1920px?" If the answer isn't in the CSS, flag it.

🟡 **Overlay not escaping its container.** `p-select`, `p-datepicker`,
`p-multiselect`, `p-autocomplete` (and any popover) inside a `DynamicDialog`
or `overflow: auto/hidden` region without `appendTo="body"` — clipped
panel, stray scrollbars, or a panel that closes immediately (BUG-088,
BUG-092). Also flag a `dialogService.open()` with no explicit `width` /
`breakpoints`.

🟡 **Error state shown before any interaction.** The invalid look
(`p-invalid` / red border) of an Optimus control bound with `[formField]` is
gated app-wide by `FORM_INVALID_GATE` (`shared/invalid-gate/`, ADR 0031) to
`invalid() && (dirty() || attempted)`. Flag: a component whose template uses
`[formField]` but whose `imports` lack `...FORM_INVALID_GATE` (run the grep in
`angular-developer` §21.5a — it lists such components); an inline add/edit row
(not inside `<form [formRoot]>`) that keeps an `xAttempted` signal but does not
pass it as `[appFormAttempt]="xAttempted()"`, so the outline never appears or
the error text and outline disagree; a manual `[invalid]` binding next to
`[formField]` (two writers to one signal input), a CSS override of
`.p-invalid`, or `touched()` used as the "attempted" signal (a bare blur makes
the root touched). Also flag a new form with a required field and no
first-render / failed-submit check at both viewports. (BUG-019, BUG-052,
BUG-094.)

🟡 **Run `npm run overlay-append:check`, don't rely on spotting it.** For any
changed dialog template that contains `<p-select|datepicker|multiselect|autocomplete>`,
run the check from `frontend/` (`scripts/overlay-append-check.js`; see
`angular-developer` §21.4). It fails with `file:line` for every overlay control
in a dialog template without `appendTo`, so "I didn't see a problem" is not
evidence. Each such control needs `appendTo="body"`; a deliberate exception
carries `<!-- overlay-append-ok: reason -->` and the reason should make sense.
The script does not cover non-dialog templates or a dialog it cannot recognise
(not opened via `dialogService.open(` and not named `*-dialog.html`): for
those, check for an `overflow: auto/hidden` ancestor by hand. Also flag a
dialog test that types into a `p-datepicker` with `appendTo="body"` and then
clicks Save without dismissing the panel (`{esc}`) — the calendar covers the
button.

🟡 **No layout regression test.** A CSS/template fix or a new
multi-field/multi-button UI with no `cy.viewport(384, 824)` **and**
`cy.viewport(1920, 1080)` geometry assertion (`getBoundingClientRect`) in the
component's `.cy.ts`, per `cypress-unit-test-developer` §16.2–16.6. Also
flag a layout test whose `mountDialog()`/`mount` helper doesn't call
`provideOptimus()` — it measures browser-default 16px fonts, not the app's
real design-token sizes, and can pass while the real UI is broken (found in
BUG-053).

🟢 Mark "verified at both viewports and both locales" only if the PR/report
says so — when it doesn't, say the layout is unverified rather than
approving it.
