---
description: Bring a parked team back in a fresh session — read the charter by absolute path, validate the contracts, re-derive each lane's launch command, and report the open cross-lane edges the tracker still holds.
argument-hint: <team root path>
---

# /teamwork:resume — start the team again from its files

Team root: **$ARGUMENTS**

A resumed team is rebuilt from the charter and the tracker, never from a saved
session. Read the team root by its **absolute path**: it is the one thing this
session cannot derive, which is why the command takes it as an argument.

Do four things, in this order.

**1. Validate before relaunching anyone.** Run
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_team.py <team root>` and report
warnings and failures verbatim. A `[T7]` failure on `protocol.md` or
`conflicts.md` means the team root predates the current plugin. Re-copy both from
`${CLAUDE_PLUGIN_ROOT}/skills/team-member/references/` byte for byte, then say so
in your report. Do not send a `RELOAD`: no member is running yet, and the lanes
you are about to launch read the re-copied files for the first time.

**2. Re-derive each lane's launch command**, by the ladder in:

```
${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/parking.md
```

`roster.md` when it survived, then `git worktree list` when the charter's
`Isolation:` is one worktree per lane, then the charter alone for a shared tree,
then ask. **Never guess a working directory.** A lane started in the wrong tree
edits the wrong files, and the first sign of it is lost work.

**3. Report the open cross-lane edges** from the tracker named in `tracker.md`,
using its own commands: every item blocked on another lane. These are what the
team was in the middle of, and they are the one thing a park is supposed to have
preserved.

**4. Print the launch commands for the human**, one per lane, each carrying
`TEAMWORK_LANE=<lane> TEAMWORK_ROOT=<team root>` in front and `--add-dir <team
root>` when the lane's working directory is not inside it:

    TEAMWORK_LANE=<lane> TEAMWORK_ROOT=<team root> \
      claude --agent teamwork:member --add-dir <team root>

Each member then runs `/rename <lane>` and `/teamwork:join <lane>`. A relaunch
that drops those two variables starts a lane the boundary hook cannot identify,
so it runs unenforced and nothing says so at the time. One that skips the rename
starts a lane nobody can address under the name the charter uses.

**Read the tracker, never the work.** Resuming is not catching up on diffs. The
lanes read their own items; you hold the map.

Close with what you could not re-derive: lanes whose working directory is still a
guess, and blocked edges the tracker does not record. An edge that was only ever
a message is gone, and that is a `FRICTION` line about rule 3 for the next retro.
