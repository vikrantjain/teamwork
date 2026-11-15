---
type: llm
weight: 1
---

The response must propose two lanes with disjoint paths, and must say that what
the endpoint returns has to be written in a file that one lane owns.

It passes if `api/**` and `web/reports/**` go to two lanes, and it says the
endpoint's response shape must be written down in a file, with one lane as its
owner. Naming a path for that file is a pass, and so is asking the human where
it should live. Giving it to the lane that serves the endpoint is the expected
answer. Saying the other lane asks for a change to it and never edits it is
correct and is not required.

It fails if it proposes the two lanes and says nothing about where the agreed
response shape lives. It fails if it leaves the shape to the ticket or to the
mock. It fails if both lanes own the file, or if no lane does. It fails if it
says one session is right because the page depends on the endpoint. The mock
lets both streams start.

Asking the other discovery questions, such as the human gates and the stop
condition, is correct and is not graded.
