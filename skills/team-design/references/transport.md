# How members reach each other

Members address each other by **lane name**. Write the substrate into
`<team root>/transport.md`, and every member loads it at startup.

The first two sections are all that forming needs. The rest is read when it
applies.

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

`lead` means the lane the lead holds and nothing else. It is the one lane the
boundary hook lets write the team root, so a member given that name is a member
that may rewrite the contracts.

## Making a lane addressable

A session is addressed by **its own name**, and that name defaults to its working
directory. Nothing in the launch command sets it, and neither do `--team-name`
and `--agent-name`, which is why this plugin does not use them.

So **the human at each lane types `/rename <lane>`** before `/teamwork:join`.
Then `ListAgents` shows the lane names the charter uses and a `SendMessage`
reaches exactly one lane. Skip it and one shared tree gives every lane the same
name, so a message reaches whichever of them the platform picks first and the
sender is never told it went to the wrong one.

The member cannot do this for itself. `/rename` is a built-in command, not a
skill, and nothing a member can call invokes one, so a lane instructed to rename
itself emits the text and stays under its old name. That is why every other file
names the person rather than the lane, and why a member that has not been renamed
says so to the lead instead of assuming it worked.

## Waiting without polling

`protocol.md` rule 2 forbids polling and names the mechanism that replaces it. A
send carries `notify_when_idle: true`, and exactly one notice comes back when
that lane next goes idle or exits. It is one-shot, so it is subscribed again each
time it is needed, and it reaches only sessions on this machine, which is where
every lane already is.

It is available from a session's own main conversation and not from a subagent,
so a lane subscribes before it fans out rather than inside the fan-out. The
lead's park drain is what it is worth most for: a lane that exits without
answering `PARK` still fires the notice, and without it the lead waits on an
answer that is never coming.

## A lane is a session a human starts

There is one kind of member: a terminal session, started by a human from the
launch command the lead prints, on the same machine as every other lane. The
boundary hook identifies a lane from `TEAMWORK_LANE`, which that command sets,
and failing that from the working directory's own name. A lane spawned inside the
lead's process has neither, so every write it makes is allowed. It also has no
worktree and no branch, which is what a park re-derives a launch command from and
what a finish merges.

The one case that is not a session is **a human member**. There is no transport
at all. The lead relays, and the charter names that lane as relayed so nobody
waits on a mailbox nobody reads.

## What a lane does inside itself

Anything it needs. A member may fan out to subagents, spawn teammates of its own,
or run a workflow, and none of that is the team's business. The hook reads the
environment and the working directory, and a member passes both to everything it
spawns, so a lane's own agents are held to that lane's paths at no cost.

A workflow is safe for that reason and one more: it starts only when the human at
that terminal asks for it, so a lane cannot drift into one. What it does change
is stopping. A workflow reports when it finishes rather than within the turn, so
a lane that answers `PARK` with one still running has work held nowhere, and
closing the terminal takes it. That is the third park condition, and
`${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/parking.md` names it.

Say this plainly in the charter when a lane is likely to want it. A member that
thinks delegation needs permission either asks before every fan-out or stops
fanning out, and the second one spends the context budget the team was formed to
protect.

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
