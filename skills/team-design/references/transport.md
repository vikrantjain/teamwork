# How members reach each other

Members address each other by **lane name**: the lane is the agent name, which is
why one agent definition serves every lane. Write the substrate into
`<team root>/transport.md`, and every member loads it at startup.

## A lane is a session a human starts

There is one kind of member. A lane is a terminal session, started by a human
from the launch command the lead prints, running on the same machine as every
other lane.

That is not a preference. The boundary hook identifies a lane from
`TEAMWORK_LANE`, which the launch command sets, and failing that from the working
directory's own name. A lane spawned inside the lead's process has neither: it
inherits the lead's environment, which must never carry a lane name, and it
starts in the lead's working directory. Such a lane cannot be identified, so
every write it makes is allowed and the boundary is back to a rule a member
remembers. A lane spawned that way also has no worktree and no branch of its own,
which is what a park re-derives a launch command from and what a finish merges.

The one case that is not a session is **a human member**. There is no transport
at all. The lead relays, and the charter names that lane as relayed so nobody
waits on a mailbox nobody reads.

## What a lane does inside itself

Anything it needs. A member may fan out to subagents, spawn teammates of its own,
or run a workflow, and none of that is the team's business. The team governs the
boundary between lanes and says nothing about what happens within one.

This is safe because of how the hook resolves a lane. It reads the environment
and the working directory, and a member session passes both to everything it
spawns, so a lane's own agents resolve to that same lane and are denied the same
out-of-lane writes. The boundary extends to them at no cost.

Say this plainly in the charter when a lane is likely to want it. A member that
thinks delegation needs permission either asks before every fan-out or stops
fanning out, and the second one spends the context budget the team was formed to
protect.

## What `transport.md` must contain

Three lines, each something a member can act on without asking. `[T1]` budgets
the whole file at 15 lines, so the reasoning for the choice goes in
`decisions.md` instead:

    Substrate: <the one substrate>
    Discover: <how to see who is up>
    Send: <how to address one lane>

`[T10]` fails without them. The failure it prevents is a member that knows what
it owes another lane and has no way to say so, which ends as a `DONE` nobody
receives.

## Naming

Lane names are addresses, so use lowercase letters, digits and hyphens. Case and
underscores survive in some places and not others, and a name that avoids both is
the same name everywhere it appears.

Two names are reserved by the platform and cannot be lanes: `main` and
`team-lead`.
