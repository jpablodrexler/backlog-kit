kit: skills/bugs-status
sub: JPPhotoManagerWeb/docs/backlog => <backlog>
sub: docs/backlog => <backlog>

PARAM | name: bugs-status description: Reports bug-backlog progress by countin | description: the project paths become 'the backlog's' files; `version` is the kit's. The P variant of the description lists fewer checks; kit follows J (D16 applies to bugs-status too)
PARAM | `scripts/status_report.py` owns every part of this skill that is pure | paths via <backlog>; kit follows J's checks (resolved bugs of every kind need a Resolution line; a row needs its file whatever its status)
PARAM | python3 .claude/skills/bugs-status/scripts/status_report.py <repo-root | script path is relative to the skill's base directory in a plugin
PARAM | Prints the finished `## Bug Tracker Status` report (summary table, per | the environment split is described as 'local and whatever other values the backlog uses' (D6): the script counts the values that occur instead of the fixed local/deployed/both (or local/prod/both) lines
PARAM | name: bugs-status description: Reports bug-backlog progress by countin #2 | description: the project paths become 'the backlog's' files; `version` is the kit's. The P variant of the description lists fewer checks; kit follows J (D16 applies to bugs-status too)
DROPPED | `scripts/status_report.py` owns every part of this skill that is pure #2 | paths via <backlog>; kit follows J's checks (resolved bugs of every kind need a Resolution line; a row needs its file whatever its status)
PARAM | Prints the finished `## Bug Tracker Status` report (summary table, per #2 | the environment split is described as 'local and whatever other values the backlog uses' (D6): the script counts the values that occur instead of the fixed local/deployed/both (or local/prod/both) lines
