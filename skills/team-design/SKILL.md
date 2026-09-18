---
name: team-design
description: >
  How to design, form, audit and continuously improve a team of Claude Code
  sessions working one goal. Use when deciding whether a goal needs a team at
  all, how many members it needs, what each may and may not touch, where work
  items and bugs will be recorded, how members address each other, and how the
  rules get better as the work exposes their gaps. Also use to adopt sessions
  that are already collaborating without contracts, to lead one while it runs,
  to run a retro, to park one so a fresh set of sessions can resume it, and to
  audit a team root that has grown. The rule it exists to enforce is that
  every lane, boundary and rule traces to something in the work, and that a
  contract never becomes a log or a task board. NOT for working inside a lane
  once the team exists, which is team-member's job.
---

# Designing a team

**Derive the team from the work. A lane, a rule or a boundary that does not trace
to something in the breakdown is decoration.**

When a case below is not covered, decide it from that sentence. Decoration is not
harmless here: every line is re-read by every member on every context load, so an
unearned rule is a tax charged forever.

## Forming a team

1. **Get the breakdown first**, from the plan the project already has or from
   five questions when it has none. Follow
   `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/discovery.md`. It also
   reads the ground the team will run on, and it ends at a proposal the human
   ratifies before anything is written.
2. **Size the team from the breakdown**, never from the goal's ambition, and
   choose the workspace in the same pass. Follow
   `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/sizing.md` exactly. It
   can return "one session", and when it does, say so and stop.
3. **Resolve the team root** — one absolute path every member can reach. Follow
   `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/team-root.md`; its ladder
   keys on the workspace, which is why step 2 comes first. Ask the user rather
   than guessing; a wrong guess scatters team state where nobody looks for it.
4. **Pick the tracker**, following
   `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/trackers.md`. One backend,
   written into `tracker.md` with its create, claim and close commands.
5. **Record the substrate**, following
   `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/transport.md`. A lane is a
   terminal session a human starts, so this is rarely a choice; write it into
   `transport.md` with how to discover a lane and how to send to it. Every member
   loads this file, so a team without it is a list of strangers.
6. **Write the contracts** from
   `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/charter-template.md` and
   `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/role-template.md`. Copy
   `protocol.md` and `conflicts.md` from
   `${CLAUDE_PLUGIN_ROOT}/skills/team-member/references/` byte for byte.
7. **Create the rest of the team root**, or the validator reports a team that is
   half-built. `decisions.md` holding the workspace choice and its reason, an
   empty `friction.md` and an empty `roster.md`. Add those last two to the
   project's `.gitignore` when the team root is under git, and skip that when it
   is not. `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/team-root.md` says
   why they are not committed.
8. **Run the validator** before telling anyone the team exists:
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_team.py <team root>`.
9. **Print the launch commands** for the user, one per lane, each carrying
   `TEAMWORK_LANE` and `TEAMWORK_ROOT` in front, and `--add-dir <team root>` when
   the lane's working directory is not inside it:

       TEAMWORK_LANE=<lane> TEAMWORK_ROOT=<team root> \
         claude --agent teamwork:member --add-dir <team root>

   The human starts every lane from these commands, and the two variables are
   what let the boundary hook deny a write to a path another lane owns. Without
   them the hook cannot tell which lane the session is, and it allows every write
   rather than blocking one it cannot attribute.

   Drop `--agent teamwork:member` for a lane whose session does not have the
   plugin. The files bind a member; the agent definition only points at them.

10. **Print the two lines the human types into each lane** once its session is
   open, in this order:

       /rename <lane>
       /teamwork:join <lane>

   `/rename` is a built-in command, so only the person at that terminal can run
   it. A member told to run it emits the text, nothing happens, and it never
   learns that nothing did. A session is addressed by its own name, which
   defaults to its working directory, so under one shared tree every lane answers
   to the same name and a `SendMessage` reaches whichever one the platform picks
   first. `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/transport.md`
   carries the rest.

## What belongs in a contract

1. **A rule earns its line by naming its failure mode.** Say what goes wrong
   without it. A rule that cannot name one is advice, and advice is not followed.
2. **No record of anything that happened.** No dates, no checkboxes, no statuses,
   no issue ids, no "what we tried". Those belong in the tracker. This is what
   `[T3]` enforces, and it is the difference between a charter that gets read and
   one that gets skimmed.
3. **No task assignments.** The charter says which lane owns which paths. Which
   item a lane is working right now is the tracker's business and changes hourly.
4. **Every lane's `Never` is filled in.** A role with no prohibition has no
   boundary, and a boundary nobody wrote down is one nobody will respect.
5. **Name an owner for every shared path, and put the path in that lane's
   `Owns`** — lockfiles, schemas, CI config, build output. An unowned shared path
   is where two lanes collide first, and the boundary hook reads role files only,
   so a path named in the charter alone is one every lane may still write.
6. **Budgets are hard.** To add a line at a retro you must remove one. Without
   that rule, "keep improving the rules" becomes accretion, and an accreted
   charter destroys the context budget that justified the team.

## Leading it once it runs

Forming is a burst; leading is the rest, and it is mostly restraint. A lead may
hold one lane of its own when nothing waits on it — integration, deployment,
documentation, review — and it is a lane like any other, with a role file and a
name under `## Lanes`.

The duties that belong to nobody else — appending friction, writing the roster,
assigning the contested item, owning the unowned shared path, broadcasting
`RELOAD` — are in
`${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/leading.md`, with the ones a
lead is tempted into and should not do. **Hold the map, not the work**, or the
lead becomes the bottleneck the team was formed to remove.

## Stopping it, and starting it again

A run ends at the charter's `## Done` or at a park. **A park is a stop at a point
the tracker fully describes**, so a fresh set of sessions resumes exactly there.
The drain, the four conditions a lane meets before it is parked, and the ladder
that re-derives each lane's launch command are in
`${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/parking.md`.

A park writes no new file into the team root. Its work is making the tracker
true, because a snapshot of where everyone got to drifts from the tracker and is
the log `[T3]` exists to keep out.

**A run that reaches `## Done` is finished, not parked.**
`${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/finishing.md` checks the
stop condition, parks every lane, and then lands the work the way the charter's
`Workspace:` line says it is separated. Under worktrees or separate repositories
that means testing each merge and handing the merges and removals to the human;
under one shared tree or separate directories there is nothing to merge and the
report says where the work is. It never merges and never removes a worktree,
because both are human gates by the charter's own definition and a park is the
only thing that was protecting the uncommitted work inside them.

## Improving the rules while the work runs

The loop is in `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/retro.md`.
Two parts of it are load-bearing and get skipped: a cause appearing **once** is
noise and must not produce a rule, and a
rule whose target cause **recurred** has failed and must be reverted rather than
supplemented. Without those two, the team accumulates rules instead of better
ones.

## Adopting a team already running

When sessions are already collaborating without contracts, the lanes exist
implicitly and must be read from what each session has actually touched, not
invented. Follow
`${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/adoption.md`. Its
ratification step is a gate, not a notification: boundaries imposed on work in
flight invalidate that work.

## Further detail

- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/discovery.md` — finding the work, and the five questions when there is no plan.
- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/sizing.md` — how many members, which workspace, and when the answer is none.
- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/team-root.md` — where the shared files live, and when to ask.
- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/trackers.md` — choosing one work-item backend.
- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/transport.md` — the one kind of member, and how lanes are addressed.
- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/charter-template.md` — the charter, with its required lines.
- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/role-template.md` — the four headings and what fills them.
- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/leading.md` — the lead's duties while the work runs.
- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/parking.md` — stopping where a fresh session can resume.
- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/finishing.md` — landing the work and disbanding.
- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/retro.md` — the optimization loop.
- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/adoption.md` — putting contracts around a running team.

Each path is written in full because the working directory at runtime is the
user's project, not this plugin.
