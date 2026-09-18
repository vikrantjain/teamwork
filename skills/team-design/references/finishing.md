# Finishing a run

A run ends at the charter's `## Done` or at a park. A park preserves the work;
finishing lands it. The two are different and the plugin used to describe only
the first, so a team that reached `## Done` had worktrees, branches and a team
root that nobody was told what to do with.

**Finishing prepares the landing. It never performs it.** Merging lane work into
the base branch changes the product, and removing a worktree destroys anything
uncommitted inside it. Both are human gates by the charter's own definition, so
this procedure reports and hands over.

## The order

1. **Check the charter's `## Done`, and nothing else.** It was written to be
   checkable by someone who was not here. If it is not met, say which part and
   stop: a run that finishes early leaves lanes holding claims nobody takes.
   This is the team's stop condition, not a lane's `Done means`. Never verify
   those yourself, for the same reason a park does not.
2. **Park every lane first.** Follow the drain in
   `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/parking.md`. A lane that has
   not parked still holds a claim, and landing around it integrates work whose
   owner thinks it is still in progress.
3. **Read `friction.md`.** If it holds notes, a retro's worth of evidence is
   about to be deleted with the run. Either run `/teamwork:retro` or report what
   is in it, so the next team does not rediscover the same costs.
4. **Land the work the way the charter's `Workspace:` line says it is separated.**
   The four cases are below. Read the line; do not infer the shape from what you
   happen to find on disk, because a lane that never started leaves no trace and
   would silently drop out of the report.
5. **Print the commands and stop.** The human runs them.

## Landing, by workspace

**One shared tree.** There is nothing to merge: every lane wrote into the same
tree. Report what is uncommitted, by lane where you can attribute it, and hand
over the commit. A lane's work that is uncommitted here is work one `git
checkout` destroys, so say it plainly.

**One worktree per lane.** Find each lane's branch from the `Workspace:` line,
which records the convention, then `git worktree list --porcelain`. A lane whose
branch you cannot name is one to ask about, never to guess at. Test each merge
without performing it: `git merge-tree --write-tree <base> <lane branch>` reports
conflicts and writes nothing. Do this for every lane before proposing an order,
because the first clean merge changes what the second one conflicts with. Then
propose an order, dependencies first: a lane that others handed work to lands
before the lanes that waited on it. Print the merges, then `git worktree remove`
for each lane, then the branch deletions.

**Separate repositories.** The same as worktrees, once per repository, each
against its own base branch. Say which repositories land in which order when one
depends on another, and say when they are independent, because a reader cannot
tell those apart from a list of commands.

**Separate directories.** There is nothing to merge and nothing to remove: the
work is already where it belongs. Report where each lane's output is and what
remains unsaved, then stop.

## What finishing never does

- **Never merge.** It is the one action in a run that cannot be undone by the
  next turn, and the charter's `## Human gates` already covers it.
- **Never remove a worktree.** An uncommitted file inside one is gone with it,
  and step 2 is the only thing that was supposed to have caught that.
- **Never delete the team root.** Under version control the contracts are
  committed and reviewable, which is the reason they were put in the project.
  Without it they are the only record the run happened at all. `friction.md` and
  `roster.md` go, because they are this run's state.

## What to report

Lead with **what will not land cleanly**: a merge with conflicts, a lane whose
branch you could not find, a tree with uncommitted work in it. That is the cost
of the workspace the team chose, and it is the only part of finishing the human
cannot see from the tracker.

Close with what you could not settle: a `## Done` clause you could not check, and
friction nobody has read.
