# How many members

Team size is computed from the breakdown. It is never chosen from how big the
goal feels, because ambition does not parallelize — dependency structure does.

## The procedure

1. **List the items** from the breakdown, each with the paths it will write.
2. **Group items that write overlapping paths into one lane.** Path overlap
   decides a boundary, not topic similarity. Two "frontend" items that never
   touch the same file are two lanes; two unrelated items that both edit the
   schema are one.
3. **Parallel width** is the number of lanes that can start without waiting on
   another lane.
4. **If the width is one, do not form a team.** Say one session is the right
   answer and stop. A team-forming skill that always forms a team is a hammer,
   and a second member on serial work adds coordination cost for no throughput.
5. **Four lanes is the default cap.** Coordination messages grow with the
   square of the roster while throughput grows at best linearly, so past four the
   team spends more turns talking than working. Go past it only when the human
   asks and the graph is genuinely that wide, and write the reason in
   `decisions.md`, or the next retro folds lanes it cannot see the point of.
6. **Fold a lane holding fewer than three items** into its nearest neighbour. A
   lane that finishes in one turn spends more on joining than on working.
7. **Team size is lanes plus one lead**, and the lead may hold one of those lanes
   when it is downstream. See below.

## The shape of a good lane

- It owns paths no other lane owns.
- It can reach its own `Done means` without another lane's edit.
- It has enough work that its member is not idle waiting for a handoff.

A lane failing the first test is not a lane; merge it. A lane failing the second
is a lane with a hidden dependency; either sequence it behind the lane it needs,
or move the shared paths to one owner.

## Whether the lead holds a lane

**The default is no lane.** A lead that holds only the map is a complete lead,
and it is what most teams want. It assigns nothing either, because the lanes were
partitioned before anyone started and each member takes its own next item. Leave
this section alone and the team is well formed.

It may also own a lane, on one condition: **no other lane waits on its output.**
Integration testing, deployment, documentation and review are downstream of
everyone by definition, and a lead doing one of them is not in anybody's way.

**One lane, and it may carry several of those duties at once.** A lane is a set
of paths, so a lead that integrates, documents and deploys writes one
`roles/lead.md` whose `## Owns` is the union of those paths. The condition limits
where that lane sits in the graph. It does not limit how many jobs sit inside
it.

A lead holding work that others wait on is the bottleneck the team was formed to
remove, and it arrives gradually enough that nobody notices until the lead is the
slowest member. That is the rule. "The lead takes no lane" was the old form of
it, and it refused the integration-tester lead for no gain.

Never invent a lane so that the lead has one. That is the same bottleneck
arriving by another route.

A lane the lead does hold gets a role file like any other, at `roles/lead.md`,
and its name under the charter's `## Lanes`. Without one, its paths are owned by nobody
and `[T5]` proves nothing about them, so every member may write the lead's
integration tests and the hook allows it.

## Workspace

Lanes have to be separated on disk before they can be separated by contract.
Choose one of four, write it on the charter's `Workspace:` line in the spelling
below, and record why in `decisions.md` so the next retro does not re-litigate
it. `[T13]` fails a charter that names none of them, and fails one whose wording
reads as two, because the hook matches this line by keyword and would pick one.

- **one shared tree** — every lane works in the same directory. Costs nothing and
  removes nothing, so it is right only when the lanes are genuinely disjoint on
  disk.
- **one worktree per lane** — under git, when lanes would share a build
  directory, a test runner, a dev server port or a generated file. Removes write
  collisions and costs a merge at the end. Name the branch convention on the same
  line, and name each worktree directory for its lane.
- **separate repositories** — one repository per component, already checked out
  side by side. The lanes are separated by the checkout, so `Owns` globs are
  written relative to the directory holding them all, as `payments/**`.
- **separate directories** — the same, without version control. Finishing has
  nothing to merge, because the work is already in place.

Under the three that are not worktrees, name the anchor on the charter's
`Workspace root:` line as well. It is the directory every lane's `Owns` globs are
read against, `[T14]` fails a charter without it, and
`${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/team-root.md` says what a
derived anchor cost.

Enforcement does not depend on the choice. Every lane is a session the human
starts from the printed launch command, which sets `TEAMWORK_LANE`, so the
boundary hook identifies the lane under any of the four. The hook's second rung,
the working directory's own name, is a backstop for a lane someone started
without that variable. It works under the three that give a lane a directory of
its own, so name each of those directories for its lane. It cannot work under one
shared tree, where every lane's directory is the same one and its name would
answer for all of them.

So choose worktrees for the reasons above and for the branch each lane needs at
the end, not to buy a boundary you already have.
