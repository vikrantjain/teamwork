# How members reach each other

Members address each other by **lane name**: the lane is the agent name, which is
why one agent definition serves every lane. Resolve **one** substrate, write it
into `<team root>/transport.md`, and every member loads it at startup.

One substrate, not two. A team split across two of them has members that cannot
reach each other, and neither half can tell that the other is still working.

## The ladder, first match wins

1. **Built-in teammates** — the lead spawns each lane itself with
   `Agent({name: "<lane>", agent_type: "teamwork:member"})`. The platform carries
   the messages, so nothing has to be set up.
2. **Separate terminal sessions, one machine** — a member starts its own session
   and joins by name, which is right when a lane needs its own terminal, its own
   permissions, or a human watching it. Same discovery, same sending.
3. **A human member** — there is no transport. The lead relays, and the charter
   names that lane as relayed so nobody waits on a mailbox nobody reads.

## What rung 1 costs

Rung 1 turns the boundary hook off. It identifies a lane from `TEAMWORK_LANE`,
and failing that from the working directory's own name. A teammate spawned in
the lead's process inherits the lead's environment, which must not carry a lane
name, and it starts in the lead's working directory, so neither rung resolves.
Every write is then allowed and the boundary is back to a rule a member
remembers. Rung 1 also gives a lane no worktree and no branch of its own, which
is what a park re-derives a launch command from and what a finish merges.

Choose rung 1 when the lanes are genuinely disjoint on disk and the run is short.
Choose rung 2 when the boundary has to hold, or when the run will be parked.

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
