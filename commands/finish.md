---
description: End a run at the charter's Done — check the stop condition, park every lane, then prepare the integration and hand it over. Reports what will not merge cleanly; never merges, never removes a worktree.
argument-hint: [team root path, if this session is outside it]
---

# /teamwork:finish — land the work and disband

Team root: **$ARGUMENTS**

Read the team root by its absolute path first, then follow:

```
${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/finishing.md
```

Five things carry this command, and three of them are refusals.

**Check the charter's `## Done` before anything else.** It is the team's stop
condition and it was written to be checkable by someone who was not here. If it
is not met, name the part that is not and stop. Do not check any lane's `Done
means`: that is what made it a lane's, and a lead that reads the work becomes the
bottleneck the team was formed to remove.

**Park every lane first**, by the drain in
`${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/parking.md`. A lane that has
not parked still holds a claim, and landing around it integrates work whose owner
believes it is still in progress.

**Read `friction.md` before you land anything.** Finishing deletes this run's
state, so a retro's worth of evidence goes with it unless somebody reads it
first. Either run `/teamwork:retro` on it or report what is in it.

**Land it the way the charter's `Workspace:` line says it is separated**, not the
way the disk looks. Under one worktree per lane or separate repositories, test
every merge without performing it: `git merge-tree --write-tree <base> <lane
branch>` reports conflicts and writes nothing. Run it for every lane before
proposing an order, because the first merge changes what the second conflicts
with. Under one shared tree or separate directories there is nothing to merge;
report what is uncommitted or unsaved and where each lane's work sits.

**Print the commands and stop.** The merges, the `git worktree remove` calls and
the branch deletions are the human's to run. Merging changes the product and
removing a worktree destroys whatever is uncommitted inside it, and both are
human gates by the charter's own definition.

Lead your report with **what will not land cleanly**, naming the lane and the
files. That is the bill for the workspace the team chose, and it is the one part
of finishing the human cannot read off the tracker.

With no argument, use the team root named in this session's charter. If this
session has no charter, say so rather than searching the filesystem for one.
