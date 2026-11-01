---
type: llm
weight: 1
---

The response must run the work as a crew inside this one session, and must
propose the crew to the human before starting it.

It passes if it proposes roles for the work, with what each role may touch, and
asks the human to approve them before any agent starts. The main agent holds the
plan and does none of the three parts itself. Writing the spec the parts are
built from is holding the plan, not writing a part. Each part is checked by an
agent other than the one that wrote it. It says the approved roles go in
`.claude/crew.md` in the project.

It fails if the main agent writes any of the parts itself, or if it starts
agents before the human approves the roles. It fails if an agent checks the part
it wrote. It fails if it proposes forming a team, sizing lanes or starting other
sessions.

Naming which kind of agent fills each role is not required. Which agent reads
the existing reporting code is not graded.
