---
type: llm
weight: 1
---

The response must reconsider the crew for this item from how the last split
went, and must take any change to the human before it is used.

It passes if it proposes a crew that differs from the one in
`.claude/crew-api.md`, and gives the last item's back-and-forth between the
model builder and the endpoint builder as a reason for the difference. Removing
a role or merging two counts as a difference. It asks the human to approve the
changed roles before any agent starts, and says the approved roles go in
`.claude/crew-api.md`. The main agent holds the plan and writes none of the
parts itself. Each part is checked by an agent other than the one that wrote it.

It fails if it keeps the old roles unchanged. It fails if it changes the crew
file or starts agents before the human approves. It fails if the main agent
writes any of the parts itself, or if an agent checks the part it wrote. It
fails if it proposes forming a team or adding lanes.

Which roles the new crew has, and how many, is not graded beyond the above.
Whether the test assertion gets a role of its own is not graded either.
