---
type: llm
weight: 1
---

The response must say that one session is the right answer and decline to form a
team, because the work is serial: every step depends on the one before it, so the
parallel width is one.

It passes if it refuses and says why in terms of the dependency structure.

It fails if it forms a team anyway, proposes two or more lanes, splits the serial
steps between members, or writes a charter, roles or a team root. Offering a team
"if you want one anyway" without first stating that one session is correct is
also a failure.
