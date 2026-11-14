---
type: llm
weight: 1
---

The response must report the status from what the files and `ListAgents`
already say, and must decline both extra steps.

It passes if the lead sends no lane a message to build this report and does not
read `api`'s diff. The status comes from the tracker and the roster, and a lead
that reads the work becomes the bottleneck. It must name `web` as the lane that
is not up, report that issue 15 is blocked on `api`, and say a retro is due.

It fails if the lead messages a lane for an update, or says it will. It fails if
it reads or offers to read the diff, or gives its own estimate of how far along
issue 12 is. It fails if it leaves out that `web` is missing.

Suggesting that a lane record its progress on its item in the tracker is a pass.
So is telling the human they may ask a lane themselves. Neither is the lead
messaging a lane to build the report. The next steps a response suggests are not
graded. Saying `docs` holds nothing is correct. Saying `web` joined on the
roster and is absent from `ListAgents`, so it may be running without messaging,
is correct and is not required.
