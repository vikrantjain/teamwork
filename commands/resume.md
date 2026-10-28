---
description: Bring a parked team back in a fresh session — read the charter by absolute path, validate the contracts, re-derive each lane's launch command, and report the open cross-lane edges the tracker still holds.
argument-hint: <team root path>
---

# /teamwork:resume — start the team again from its files

Team root: **$ARGUMENTS**

A resumed team is rebuilt from the charter and the tracker, never from a saved
session. Each lane may resume its own conversation, but nothing here depends on
what that conversation remembers. Read the team root by its **absolute path**: it is the one thing this
session cannot derive, which is why the command takes it as an argument.

Do four things, in this order.

**1. Validate before relaunching anyone.** Run
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_team.py "<team root>"` and report
warnings and failures verbatim. A `[T7]` failure on `protocol.md` or
`conflicts.md` means the team root predates the current plugin. Re-copy both from
`${CLAUDE_PLUGIN_ROOT}/skills/team-member/references/` byte for byte, then say so
in your report. Do not send a `RELOAD`: no member is running yet, and the lanes
you are about to launch read the re-copied files for the first time.

A `[T9]` failure says the charter names a different directory from the one you
are validating, and its two causes need opposite answers. When the directory it
names is still a team root, you are in a stale copy: resume from the one the
charter names and change nothing. When it is not there, this team root has
moved, by a clone or a rename or a new machine. Rewrite `Team root:` and
`Workspace root:` to the paths this copy and this workspace actually have. You
are the lead, so those two lines are yours to write, and a charter left naming
the old ones points the boundary hook at a tree nobody is editing, where every
glob misses and every write is allowed.

Then rewrite `transport.md`'s `Lead:` line to this session's name, which
`ListAgents` opens with. This session is a new lead, and every lane you relaunch
sends its `JOIN` to that line and waits for the answer. A team formed before the
line existed fails `[T10]` until you add it.

**2. Re-derive each lane's launch command**, by the ladder in:

```
${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/parking.md
```

`roster.md` when it survived, then `git worktree list` when the charter's
`Workspace:` is one worktree per lane, then the charter alone for the other three
workspaces, then ask. **Never guess a working directory.** A lane started in the
wrong tree edits the wrong files, and the first sign of it is lost work.

Then write each lane's settings file again, as that reference says. A fresh
clone has none, and a team root that moved has changed what it must name.

**3. Report the open cross-lane edges** from the tracker named in `tracker.md`,
using its own commands: every item blocked on another lane. These are what the
team was in the middle of, and they are the one thing a park is supposed to have
preserved.

**4. Print the restart commands for the human**, one per lane, identical but for
the lane name and its working directory, every path absolute and `--add-dir` on
all of them. A relative path resolves against whatever directory the command is
pasted into and says nothing when it misses, which starts a lane that cannot read
its own contracts:

    cd "<lane's working directory>" && TEAMWORK_LANE=<lane> TEAMWORK_ROOT="<team root>" \
      claude --agent teamwork:member --add-dir "<team root>" -r <lane> "/teamwork:join <lane>"

`-r <lane>` resumes the lane's own conversation by its name, and the quoted join
runs in it. For a lane whose session is gone, such as after a fresh clone, print
`-n <lane>` instead. `-r` finds no session there and opens an empty picker. The
parking reference above says how to tell the two apart. A relaunch that drops the
two variables starts a lane the boundary hook cannot identify, so it runs
unenforced and nothing says so at the time. One that drops both `-r` and `-n`
starts a lane nobody can address under the name the charter uses.

A lane that ran in the background restarts by its session id, never by `-r`.
`${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/launching.md` shows the
command. `-r` there starts a copy of the conversation that has lost the lane's
name.

**Read the tracker, never the work.** Resuming is not catching up on diffs. The
lanes read their own items; you hold the map.

Close with what you could not re-derive: lanes whose working directory is still a
guess, and blocked edges the tracker does not record. An edge that was only ever
a message is gone, and that is a `FRICTION` line about rule 3 for the next retro.
