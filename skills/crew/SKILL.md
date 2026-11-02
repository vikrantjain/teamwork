---
name: crew
description: >
  How to run a crew: the agents that do one session's work, so that the agent
  holding the plan does no part of the work and the agent doing a part never
  checks it. Use whenever a session starts a piece of work, whether it is a
  lane on a team or a session on no team: proposing the roles the work needs
  and what each may touch, saving them once the human approves, starting each
  part, choosing who checks it, and reading the crew back after a restart or a
  compaction. Also use when the main agent finds itself doing a part, or is
  about to call a part done that nobody else checked. NOT for dividing work
  between sessions, which is team-design's job.
---

# Running a crew

**The agent that holds the plan does no part of the work. The agent that does a
part never checks it.**

When a case below is not covered, decide it from those two sentences. Each one
prevents a failure that nobody sees happen. An agent that holds the plan and
also does the work fills its context with every part. A compaction then drops
parts of the plan. Nothing reports the loss. An agent that checks its own part
reads what it meant to write, not what it wrote. Its check passes the mistakes
it made.

Holding the plan includes writing the spec, which says what the finished work
must do. Every part is built from it and checked against it. The agent holding
the plan splits the work into roles from the spec. It decides from the spec
whether a part is done. In a lane, it answers other sessions from the spec. An
agent handed a spec it did not write does all three without understanding the
work. Reading the existing work to write the spec is a part, so another agent
reads it and reports what it found. Read in full, that work fills the context
the plan needs.

Which roles exist, how many agents fill them and what each may touch are
proposed by the agent that holds the plan and approved by its human. Nothing
outside the session depends on them, so nothing outside it needs to see them.

## Setting up the crew

1. **Propose the roles, and wait for the human to approve them** before any
   agent starts. Roles nobody approved split the work along lines the human
   might refuse, and that shows only when the work comes back wrong.
2. **Save them in the crew file once they are approved.** It is
   `.claude/crew-<lane>.md` in the lane's own directory, or `.claude/crew.md`
   in the project when the session is on no team. The lane's name is in the
   file's name because under one shared tree every lane has the same directory.
   Never put it in the team root. The lead does not see a lane's crew, and the
   boundary hook denies a member that write.
3. **Commit it wherever the work is committed.** The human approved it, so it is
   a contract, and a contract outside version control cannot be reviewed.
4. **Change it only with the human.** A role that changes while work is under
   way moves a boundary under that work.

What the file holds beyond that is the session's choice. It names each role,
what the role may touch and which role checks it, because those are what a
restart reads back.

## Running it

**Two agents running at the same time never write the same path.** Two editors
of one file lose work, and neither of them sees it happen. How the crew keeps
them apart is its own choice, such as disjoint paths or one part after another.

## After a restart or a compaction

Read the crew file again. The boundary hook names it at every start and after
every compaction. Then find where the work stands from the tracker, when there
is one, and from the work itself. **A part nobody can show was checked is
checked again**, because a check lost with the context would otherwise pass as
one that happened.

## When the session is a lane

**Only the agent holding the plan speaks for the lane.** A crew member can send
a message to another session, and it goes out under the lane's name. The answer
comes back to the main agent, which never asked the question.

Every subagent the lane starts inherits its environment, so the boundary hook
holds each of them to the lane's `Owns`. The crew divides those paths among its
roles, and nothing outside the lane enforces that division.

## Further detail

- `${CLAUDE_PLUGIN_ROOT}/skills/crew/references/delegation.md` — the ways a
  session hands work to agents, and what each can and cannot do.

Each path is written in full because the working directory at runtime is the
user's project, not this plugin.
