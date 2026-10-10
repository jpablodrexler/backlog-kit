# Fix workflow specifics
Read when: fixing findings of an existing database review report

## 8. Fix Workflow (project specifics)

### 8.3 Fix loop

2. Apply the fix:
   - **A fix to an already-applied migration is never "edit the file"** —
     per §6, create a new migration (`npx supabase migration new
     <description>`, which generates the correctly-timestamped filename)
     that performs the correction (a new `CREATE POLICY`, an `ALTER TABLE
     ... ADD COLUMN`, a `CREATE INDEX CONCURRENTLY`, etc.).
   - A finding that requires backfilling a large existing table needs a
     decision on batching strategy; if it isn't obvious, stop and ask the
     user rather than picking one unilaterally.
3. Push the new migration to actually apply it: `npx supabase db push`.
   This requires the project to be linked (`npx supabase link
   --project-ref <project-ref>`); if it isn't, stop and tell the user
   rather than attempting to link on their behalf.
4. Update any frontend service/tests whose expectations depended on the
   old schema/policy shape.

### 8.4 Continue until done

After finishing the selected scope, run the widest verification available —
`npm run test` in `frontend/`, and manually re-check the affected RLS
policy from the frontend (sign in as a test user, confirm the expected
rows are visible/hidden) — once before asking what's next. Then:

