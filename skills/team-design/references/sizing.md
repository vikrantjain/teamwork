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
5. **Cap at four lanes.** Coordination messages grow with the square of the
   roster while throughput grows at best linearly, so past four the team spends
   more turns talking than working.
6. **Fold a lane holding fewer than three items** into its nearest neighbour. A
   lane that finishes in one turn spends more on joining than on working.
7. **Team size is lanes plus one lead.** The lead does not take a lane: it holds
   the map, and a lead carrying work becomes the bottleneck the team was formed
   to remove.

## The shape of a good lane

- It owns paths no other lane owns.
- It can reach its own `Done means` without another lane's edit.
- It has enough work that its member is not idle waiting for a handoff.

A lane failing the first test is not a lane; merge it. A lane failing the second
is a lane with a hidden dependency; either sequence it behind the lane it needs,
or move the shared paths to one owner.

## Isolation

Choose one worktree per lane when lanes would share a build directory, a test
runner, a dev server port, or a generated file. Choose one shared tree when they
would not. Record the choice and its reason in `decisions.md`, because the next
retro will otherwise re-litigate it.

Worktrees remove write collisions and cost a merge at the end. A shared tree
costs nothing and removes nothing, so it is right only when the lanes are
genuinely disjoint on disk.

Worktrees also buy enforcement. The boundary hook identifies a lane from
`TEAMWORK_LANE`, and failing that from the working directory's own name, which
only tells lanes apart when each has its own and each is named for its lane. A shared tree with in-process
teammates gives the hook nothing to go on, so it allows every write and the
boundary is back to being a rule a member remembers.
