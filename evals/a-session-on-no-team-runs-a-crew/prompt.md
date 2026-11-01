---
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

This is a single session with the teamwork plugin installed, and it is on no
team. It cannot run commands, so this is what it would tell you:
`echo "$TEAMWORK_LANE"` prints nothing, and `.claude/crew.md` does not exist.

I want to add a CSV export to our reporting script. It needs a change to the
parser in `report/parse.py`, a new writer in `report/export.py`, and tests in
`tests/test_export.py`. Tell me how you will do it.
