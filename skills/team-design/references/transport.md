# How members reach each other

Members address each other by **lane name**. The lane is what `TEAMWORK_LANE`
carries, which is why one agent definition serves every lane: the role file is
looked up from the variable, not from the agent. A lane is not addressable under
that name until it takes it, which is what `## Making a lane addressable` below
is for.
Write the substrate into `<team root>/transport.md`, and every member loads it at
startup.

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

## Making a lane addressable

A session is addressed by **its own name**, and that name defaults to its working
directory. Nothing in the launch command sets it.

`--team-name` and `--agent-name` are real flags and they do not set it either.
Outside the platform's experimental agent-teams mode they are accepted and
ignored; inside it the CLI refuses to start unless `--agent-id` is passed
alongside them, and a human starting a lane by hand has no id to pass. A launch
command built on them produces a lane that is either unaddressable or does not
start, so this plugin does not use them.

So **every lane renames itself at startup**: `/rename <lane>`, before
`/teamwork:join`. Then `ListAgents` shows the lane names the charter uses and a
`SendMessage` reaches exactly one lane. Skip it and one shared tree gives every
lane the same name, so a message reaches whichever of them the platform picks
first and the sender is never told it went to the wrong one.

## When a lane is unreachable anyway

A lane that has renamed itself and still never appears in `ListAgents` is not
messaging at all. That is a degraded team rather than a broken one, and knowing
which saves a run. `protocol.md` rule 3 puts state in the tracker before it is
announced, so an unreachable lane still claims its items, still closes them, and
is still read by the lead exactly as before.

What is lost is **every verb**, not only `ASK` and `READY`. Route them the way
the charter already routes a human member: the lead relays. Three cases need
saying, because each one silently stops the team rather than slowing it.

- **The startup ack.** A member waits for it before taking an item, so with no
  messaging every lane waits forever. The human tells the lane to start, and the
  lead writes the roster from that instead of from an ack.
- **The park drain.** `PARK` is broadcast and answered. The human carries both
  halves, and the lead still names every lane it could not reach — an unparked
  lane is the thing a park exists to prevent.
- **`RELOAD` after a retro.** A member that is not told keeps running the old
  rules. Restart the lanes instead: a restart reloads the files by definition,
  which is why this one is cheap and the other two are not.

Append a friction line when it happens. A lead that quietly works around missing
messaging leaves the next team to discover it the same slow way.

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
`team-lead`. `[T12]` fails a team that uses either, because the refusal would
otherwise arrive hours later when the lane tries to take its name.
