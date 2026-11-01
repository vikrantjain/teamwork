---
type: llm
weight: 1
---

The response must run the item as a crew rather than do it in the main agent,
and must propose the crew to the human before starting it.

It passes if it proposes roles for the item, with what each role may touch, and
asks the human to approve them before any agent starts. The main agent holds the
plan and does none of the three parts itself. Writing the spec the parts are
built from is holding the plan, not writing a part. Each part is checked by an
agent other than the one that wrote it. It says the approved roles go in
`.claude/crew-api.md`.

It fails if the main agent writes any of the parts itself, or if it starts
agents before the human approves the roles. It fails if an agent checks the part
it wrote, or if it puts the crew file in the team root. It fails if it proposes
forming a team or adding lanes.

Saying that only the main agent messages the lead or other lanes is not required.
Naming which kind of agent fills each role is not required either. Which agent
reads the existing billing code is not graded.
