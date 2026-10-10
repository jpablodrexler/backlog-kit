# Code Reviewer — Frontend Conventions, Testing & Cross-cutting
Read when: templates/TypeScript style or naming, a `*.cy.ts` file, or comment/code-style patterns

## 7. Frontend: TypeScript Conventions & Naming

🔴 Flag any use of `any` — use a typed interface, `unknown` with a type
guard, or `Partial<T>`.

🔴 Flag `console.log` / `console.error` left in committed code — errors
should surface via the component's `error` signal (see `angular-developer`
§10/§13), not the console.

🟡 Flag `!` (non-null assertion) that could be replaced with optional
chaining (`?.`) or a null check.

🟡 Flag an interface defined inline in a component — move it to `core/`.

| Element            | Expected                   | Example                        |
| ------------------ | ---------------------------- | --------------------------------- |
| File               | `kebab-case.ts`             | `task-list.ts`, `auth.service.ts` |
| Component class    | PascalCase, no `Component` suffix | `TaskList`, `Login`        |
| Service/guard      | PascalCase + role suffix / camelCase function | `TasksService`, `authGuard` |
| Interface          | PascalCase                 | `Task`                          |
| Property / method  | camelCase                  | `tasks`, `getTasks()`           |
| Component selector | `app-kebab-case`           | `app-task-list`                 |
| Test suite         | `describe('ClassName')`    | `describe('TaskList')`          |
| Test case          | `it('should <behaviour>')` | `it('should render each task')` |

🟡 Flag any violation of the above.

---

## 8. Testing (Cypress Component Testing)

🔴 Flag a test that mocks a service with `jasmine.createSpyObj`, `vi.fn()`,
or any Jest/Vitest matcher (`toBe`, `toEqual`, `toHaveBeenCalledWith`,
...) — this project uses Cypress Component Testing exclusively (see the
`cypress-unit-test-developer` skill): stub services with a
`Partial<ServiceType>` object using `cy.stub()` per method, and assert
with Chai (`expect(x).to.equal(y)`, `cy.wrap(fn).should('have.been.calledWith', ...)`).

🔴 Flag `cy.wrap(aPromise).then(onFulfilled, onRejected)` used to assert a
rejection — `cy.wrap()` fails the test the instant the wrapped promise
rejects, before the second callback ever runs. The fix is the
`rejectionOf()` pattern in `cypress-unit-test-developer` §6 (pre-resolve
the rejection into a plain value, then wrap that).

🟡 Flag a test that mutates a component's plain (non-signal) field
directly (e.g. calling `component.setDisabledState(true)` from test code)
and asserts on the resulting DOM state via only `fixture.detectChanges()`
— in this zoneless app that needs an explicit
`fixture.componentRef.injector.get(ChangeDetectorRef).markForCheck()`
first, or the view is never rechecked (see `cypress-unit-test-developer`
§12).

🟡 Flag a component test that omits `provideNoopAnimations()`, or that
omits `provideRouter([])` when the component injects `Router` or uses
`RouterLink`.

🟡 Flag a `.cy.ts` file placed outside the source tree instead of
co-located next to its source file.

🟡 Flag `import { mount } from 'cypress/angular'` (or
`'cypress/angular-zoneless'`) in a test file — `cy.mount` is a global
command already registered in `cypress/support/component.ts`; a test file
should never import `mount` directly.

---

## 9. Cross-cutting: Comments & Code Style

🟢 Flag comments that restate what the code does. Only comments explaining
**why** (a non-obvious constraint, workaround, or invariant — e.g. the RLS
silent-empty-array gotcha) are kept.

🟢 Flag multi-line comment blocks on internal methods — terse single-line
comments are preferred, and only when necessary.

🟢 Flag large imperative loops that could be replaced by an array method
(`.map`/`.filter`/`.find`).

---
