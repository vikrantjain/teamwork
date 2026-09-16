# Finishing a run

A run ends at the charter's `## Done` or at a park. A park preserves the work;
finishing lands it. The two are different and the plugin used to describe only
the first, so a team that reached `## Done` had worktrees, branches and a team
root that nobody was told what to do with.

**Finishing prepares the integration. It never performs it.** Merging lane work
into the base branch changes the product, and removing a worktree destroys
anything uncommitted inside it. Both are human gates by the charter's own
definition, so this procedure reports and hands over.

## The order

1. **Check the charter's `## Done`, and nothing else.** It was written to be
   checkable by someone who was not here. If it is not met, say which part and
   stop: a run that finishes early leaves lanes holding claims nobody takes.
   This is the team's stop condition, not a lane's `Done means`. Never verify
   those yourself, for the same reason a park does not.
2. **Park every lane first.** Follow the drain in
   `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/parking.md`. A lane that has
   not parked still holds a claim, and integrating around it merges a branch
   whose owner thinks it is still working.
3. **Read `friction.md`.** If it holds notes, a retro's worth of evidence is
   about to be deleted with the run. Either run `/teamwork:retro` or report what
   is in it, so the next team does not rediscover the same costs.
4. **Find each lane's branch**, from the charter's `Isolation:` line, which
   records the convention, then `git worktree list --porcelain`. A lane whose
   branch you cannot name is one to ask about, never to guess at.
5. **Test each merge without performing it.** `git merge-tree --write-tree <base>
   <lane branch>` reports conflicts and writes nothing. Do this for every lane
   before proposing an order, because the first clean merge changes what the
   second one conflicts with.
6. **Propose an order**, dependencies first: a lane that others handed work to
   lands before the lanes that waited on it. Say why the order is what it is.
7. **Print the commands and stop.** The merges, then `git worktree remove` for
   each lane, then the branch deletions. The human runs them.

## What finishing never does

- **Never merge.** It is the one action in a run that cannot be undone by the
  next turn, and the charter's `## Human gates` already covers it.
- **Never remove a worktree.** An uncommitted file inside one is gone with it,
  and step 2 is the only thing that was supposed to have caught that.
- **Never delete the team root.** The contracts are committed and reviewable,
  which is the reason they were put in the repository. `friction.md` and
  `roster.md` go, because they are this run's state and gitignored already.

## What to report

Lead with **what will not merge cleanly**, naming the lane and the files. That is
the cost of the isolation the team chose, and it is the only part of finishing
the human cannot see from the tracker.

Close with what you could not settle: a lane whose branch you could not find, a
`## Done` clause you could not check, and friction nobody has read.
