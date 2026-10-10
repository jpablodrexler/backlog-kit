# Documentation tiers

Read when: every run

`JPPhotoManagerWeb` documents itself in two tiers, and both need active
upkeep:

- **`CLAUDE.md`** — a lean quick-start for an agent working in the code:
  commands, package layout, coding conventions, and pointers to the tier
  below for anything detailed. It should **never** carry a REST API table,
  a full config table, or long narrative paragraphs inline — those belong
  in `docs/`. If you find one growing back in `CLAUDE.md`, move it out; this
  file was restructured once already (see its own "Documentation" section)
  specifically because unrestrained inline detail drifted silently for a
  long time before anyone re-derived it from the code.
- **`JPPhotoManagerWeb/docs/*.md`** — the actual reference material,
  indexed from `JPPhotoManagerWeb/README.md`. This is comprehensive and, as
  of the last full sweep, considerably more accurate and detailed than
  `CLAUDE.md` ever was — it includes mermaid diagrams, troubleshooting
  sections, and provenance notes. Nothing else in the repo maintains it
  automatically; that's this skill's job.

Both modes also apply small, targeted config/dashboard edits directly
(rather than only reporting them) for the manifest-parity and metrics rows
(§1, §2, §3): they are low-risk enough to apply directly.
