---
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Size a team for this goal, and tell me the lanes and what each owns. Do not write
any files yet.

We are adding CSV export to our product. Three things have to happen and none of
them needs another to start: a new `exporters/` package that serialises a record
set, a `docs/export.md` page describing the format for users, and a
`web/settings/export.tsx` panel that lets a user pick columns. The panel calls an
endpoint that already exists and already returns the column list.
