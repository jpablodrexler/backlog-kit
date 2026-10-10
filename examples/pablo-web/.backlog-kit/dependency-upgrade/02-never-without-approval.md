# Majors never applied without approval
Read when: every run

## 3. Classify & Decide

🔴 Never apply a major-version bump to `@angular/core`, `@supabase/supabase-js`,
or `supabase` (the CLI) without explicit user approval for that specific
package — these are the three dependencies this whole app is built on top
of, and a major bump to any of them routinely carries breaking changes this
project's small test suite may not fully cover.

🟢 A patch/minor bump to a leaf dependency with no direct API usage in this
codebase (e.g. `tslib`) is lower risk than a direct, heavily-used one
(`@angular/material`, `@supabase/supabase-js`) — note this distinction in
the report (§6) but the automatic/manual split above still applies
uniformly by bump type, not by usage weight.
