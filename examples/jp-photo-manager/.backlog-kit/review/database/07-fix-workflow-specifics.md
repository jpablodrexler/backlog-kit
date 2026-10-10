# Fix workflow specifics
Read when: fixing findings of an existing database review report

## 8. Fix Workflow (project specifics)

### 8.3 Fix loop

2. Apply the fix:
   - **A fix to an already-applied migration is never "edit the file"** —
     per §5, create a new `V{n+1}__*.sql` that performs the correction
     (e.g. `CREATE INDEX CONCURRENTLY` for a missing index, an `ALTER TABLE`
     for a data-type/nullability fix). Determine the next version number
     from the actual highest `V{n}` present, not a guess.
   - If the finding is purely on the JPA entity side (e.g. `@Table(indexes =
     ...)` drift from §3.4) and requires no schema change, editing the entity
     directly is fine — no new migration needed.
   - A finding that requires backfilling a large existing table
     (`assets`) needs a decision on batching/locking strategy; if it isn't
     obvious, stop and ask the user rather than picking one unilaterally
     (same rule as `code-reviewer` §17.3.3 / `security-reviewer` §9.3.3).
3. Verify the fix: run `mvn clean test-compile` at minimum; if the change
   affects schema applied to a Testcontainers-backed integration test, run
   the relevant integration test class (requires Docker) so Flyway actually
   applies the new migration against a real PostgreSQL instance rather than
   just compiling.
4. Update any repository tests whose expectations depended on the old
   schema/index shape.

### 8.4 Continue until done

After finishing the selected scope, run the widest verification available
(`mvn clean test` at minimum; `mvn verify -Pintegration-tests` if any
migration file changed, since only the Testcontainers-backed integration
suite actually exercises Flyway against real PostgreSQL) once before asking
what's next. Then:
