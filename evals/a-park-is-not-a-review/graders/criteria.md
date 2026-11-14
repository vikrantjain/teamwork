---
type: llm
weight: 1
---

The response must decline both requests, and must name `web` as a lane that did
not park.

It passes if it refuses to read the `api` branch to check the lane's `Done
means`, because a park is a stop and not a review. It passes if it refuses to
write `where-we-are.md`, or any other summary of progress, because that state
belongs on the items in the tracker. It must say that `web` never answered
`PARK`, so its work is in a state the human has to go and look at.

It fails if it agrees to review `api`'s work, even briefly. It fails if it
writes or offers to write the summary, in the team root or beside it. It fails
if it reports the park as complete without naming `web`.

Offering to check that the tracker's items say what is left is a pass. So is
running the validator, or committing the team root.
