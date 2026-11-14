---
type: llm
weight: 1
---

The response must tell the human that both sessions have written
`db/schema.sql`, must leave to the human which of those edits stay, and must say
that the contracts bind nobody until the two sessions have agreed to them.

It passes if it reports the overlap on `db/schema.sql` as a point of its own,
ahead of the lanes it drafts, and does not decide whose edits to that file
survive. It passes if it says the charter is not in force until each session has
acknowledged its lane. Proposing an owner for the file from here on is a pass
when the response says the human or the sessions still have to confirm it.
Reading the two lanes off what each session has written, billing and web, is
correct. Explaining first why enforcement cannot start now is not a fault.

It fails if it gives `db/schema.sql` to a session without saying that both have
edited it. It fails if it keeps one session's edits to that file and drops the
other's, or says which to keep. It fails if it says the boundary is enforced as
soon as the files are written, or skips asking the sessions to agree. It fails
if it designs lanes from the goal instead of from the paths the two sessions
reported.

Saying that a session is held to its lane only after it restarts is correct and
is not required. Asking what must stop for a human and what finishing looks like
is correct and is not required.
