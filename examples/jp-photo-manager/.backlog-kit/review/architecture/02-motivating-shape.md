# Architecture Reviewer — the shape the review hunts for
Read when: every architecture review

Assess whether the system's overall structure — not a specific diff or PR,
but the shape of the whole frontend and/or backend — still follows recommended
Angular and Spring practice and the project's own documented conventions. This
skill exists because the kind of issue it looks for rarely shows up in a
single-PR `code-reviewer` pass: it is implicit coupling that accretes
gradually, one individually-reasonable change at a time, across many separate
reviews that each only saw their own diff.

The motivating shape, on either side: a unit that starts as one narrow concern
(a preference, a playback state, a sync status, a cache-invalidation hook, one
Kafka topic) and quietly becomes the cross-feature "something changed, react"
channel for several unrelated features. Nothing about its name says so, and no
single PR that added one more consumer would have looked wrong in isolation.
The backend has its own classic drift on top of that: the hexagonal dependency
rule eroding one convenient import at a time.
