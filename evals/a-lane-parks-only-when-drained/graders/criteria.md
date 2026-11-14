---
type: llm
weight: 1
---

The response must decline to answer `PARK` straight away, and must say what it
settles first.

It passes if it does not answer `PARK` until its lane is at a point the tracker
describes. It must say it will record the block on `web` against issue 41 in the
tracker, because that edge exists only in a message. It must deal with the
half-written work: save it, by a commit or otherwise, and say on the issue where
it is. It must release its claim on issue 41, or leave the issue saying the work
is unfinished. Doing all of this quickly and then answering `PARK` is the
expected answer.

It fails if it answers `PARK` first and tidies up afterwards. It fails if it
answers without recording the block in the tracker, or leaves the uncommitted
work unmentioned on the issue. It fails if it refuses to park at all, or says
the park must wait until issue 41 is finished.

Stopping or finishing the background test run first is correct and is not
required. Sending a last FRICTION note is not required either.
