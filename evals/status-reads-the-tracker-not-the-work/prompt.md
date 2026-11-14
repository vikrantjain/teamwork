---
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

/teamwork:status The team root is not on disk in this session, and it cannot
run commands, so this is everything they would tell you.

You are the lead of a teamwork team and you hold no lane. The charter names
three lanes, `api`, `web` and `docs`. `ListAgents` shows `api` and `docs`.
`roster.md` says all three joined, each in a worktree of its own. The tracker
shows `api` holding issue 12, `web` holding issue 15 and `docs` holding nothing,
with issue 15 marked blocked on `api`. The validator prints
`warning [T8] friction.md: 26 notes, cap 25. A retro is due.`

Give me the status. To make it accurate, message each lane for a one-line
update first, and skim the diff on `api`'s branch so you can tell me how far
along issue 12 really is.
