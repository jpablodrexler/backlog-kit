# Code Reviewer — Architecture, Components & Routing
Read when: new/moved files, layer boundaries, a component's metadata/imports, or `app.routes.ts`

## 1. Architecture & Layering

```
core/            → SupabaseService, one @Service() per table/domain area, auth state, guards, models, i18n. No UI.
<feature>/       → page-level routed components (login/, task-list/, documents/, …) and the dialogs only they open;
                   use core services and shared components. Lives directly under app/.
shared/          → reusable components, directives and utilities with 2+ consumers; no core service injection.
```

See `angular-developer` §3 for the full directory description. There is no
`app/features/` folder — feature folders sit directly under `app/`.

### 1.1 Core layer

🔴 Flag any file under `core/` that renders UI (a component, a template) —
`core/` is services, guards, and models only.

🔴 Flag any service anywhere in the app that constructs its own
`SupabaseClient` via `createClient(...)` — there must be exactly one, built
in `SupabaseService`; every other service injects `SupabaseService` and
calls `.client`.

🟡 Flag a service placed in a feature folder — it belongs in `core/`.

🟡 Flag a new service declared with `@Injectable({ providedIn: 'root' })`, or
any class using constructor-parameter injection — this codebase uses
`@Service()` and `inject()` fields (ADR 0029). Likewise flag new
`FormBuilder`/`FormGroup`/`ReactiveFormsModule` code: forms are Signal Forms
(`@angular/forms/signals`; see `angular-developer` §14).

### 1.2 Features layer

🟡 Flag a routed page that is not registered lazily (`loadComponent`) in
`app.routes.ts`, and a feature folder that imports another feature's
internals instead of promoting the shared piece to `shared/`.

🔴 Flag a feature component that injects `SupabaseService` directly
instead of going through a domain service in `core/` (e.g. calling
`this.supabase.client.from('task')...` straight from a component instead of
`TasksService.getTasks()`).

### 1.3 Shared layer

🔴 Flag any component in `shared/` that injects a `core` service — shared
components must be purely presentational, driven by `@Input()`/`@Output()`.
Narrow carve-out (see `docs/decisions/0006-shared-patient-switcher-service-injection.md`
and `docs/decisions/0018-medical-location-directory-dialog-shared-service-injection.md`):
`HouseholdMemberSwitcher`/`HouseholdMemberFormDialog` (ADR 0006 predates
their rename from `PatientSwitcher`/`PatientFormDialog`) and
`MedicalLocationDirectoryDialog` are accepted exceptions — each a self-contained widget already proven across
≥2 features, owning its own service calls rather than being split into a
dumb shell duplicated per consumer. Don't flag those specifically;
still flag any *other* `shared/` component injecting a `core` service
unless it earns the same bar (genuinely reused by ≥2 features as one
coherent unit, not just convenient for a single new feature) — and record
its own ADR the same way, rather than assuming this list pre-approves it.

🟡 Flag a component duplicated across two feature folders instead of being
promoted to `shared/` once it has a second consumer (see `angular-developer`
§3 — don't flag a single-consumer component for *not* being in `shared/`
yet, that's premature).

---

## 2. Standalone Components

🔴 Flag any `NgModule`, or an explicit `standalone: true` in `@Component(...)`
metadata — the flag is Angular 22's default and should be omitted (see
`angular-developer` §5).

🔴 Flag `*ngIf` or `*ngFor` in templates — use `@if` / `@for`.

🟡 Flag `@for` without a `track` expression.

🟡 Flag a component's `imports: []` that includes a module the template
doesn't actually use.

🟡 Flag `.component.ts`/`.component.html`/`.component.css` filenames on a
**new** component — this project's convention omits the `.component.`
infix (`task-list.ts`, not `task-list.component.ts`; see `angular-developer`
§4). Don't flag the absence of the infix — that's correct; flag its
presence on new files as inconsistent with the rest of the codebase.

🟡 Flag a `.scss` file — this project uses plain `.css` throughout
(component styles, `styles.css`, `optimus-theme.css`; see `angular-developer` §5).

---

## 3. Routing

🟡 Flag a direct (eager) import of a feature component in `app.routes.ts`
for any route other than the `login`/`register` entry points — every page
behind `authGuard` is lazy-loaded with `loadComponent` (see `angular-developer`
§6).

🔴 Flag a route that should be behind `authGuard` (any page showing
user-owned data) but isn't.

🟡 Flag a new class-based route guard (`implements CanActivate`) instead of
a functional `CanActivateFn` — this project's guards are functions using
`inject()` (see `angular-developer` §7).

---
