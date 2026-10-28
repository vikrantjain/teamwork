# Parking a team, and resuming it

A run ends either at the charter's `## Done` or at a park. A park is a stop at a
point the tracker fully describes, so a fresh set of sessions picks the work up
where it was left.

**A park writes no new file.** It makes the tracker true. A snapshot of where
everyone got to would duplicate the tracker, drift from it, and be the work log
`[T3]` keeps out of the team root.

## What a logical point is

A lane is parked when all four hold. Anything less is a stop, not a park.

1. **Its claimed item is closed under its `Done means`, or released.** A claim
   held by a session that no longer exists is an item nobody can take and nobody
   can see is stuck.
2. **Every `BLOCKED` it opened is recorded against the item in the tracker.** An
   edge living only in a message dies with the run, and the team resumes without
   knowing what it was waiting for.
3. **Its work is where the team can find it, or the item says where it is** — the
   branch, the worktree, the stash, the directory. Under version control that
   means nothing uncommitted is left unnamed. Without it, it means no half-file
   is left somewhere only this session knew about. A workflow or any other
   background run still going counts here too, and it is saved nowhere at all:
   the lane finishes it or stops it before answering. Nobody else finds any of
   this by looking.
4. **Its outstanding `FRICTION` has been sent and appended.** Friction that was
   never written is a retro that never happens.

## The drain

1. Broadcast `PARK` carrying the team root's absolute path, as `RELOAD` does.
2. Do not poll. Each lane answers `PARK` when it is drained, and a broadcast
   sent with `notify_when_idle` also tells you when one exits without answering.
3. Append the friction that arrives, and refresh `roster.md` from the answers.
4. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_team.py "<team root>"`.
5. Commit the team root only when it is under version control and the tracker is
   a file inside it. The contracts are already committed, and nothing else in a
   park is new.
6. **Name every lane that did not answer.** An unparked lane left work in a state
   only the human can now go and look at.

A lane may park itself while the team runs on. The lead marks it in `roster.md`
and stops expecting it.

## What a park never does

- **Never verify a lane's `Done means` yourself.** It is a park, not a review, and
  reading the work undoes the saving the team was formed for.
- **Never reassign an in-flight item.** Boundaries change at a retro, never here.
- **Never write a "where we are" note.** Whatever you would put in it belongs on
  the item, where the lane that resumes will actually look.

## Finding the launch commands again, first match wins

Launch commands are re-derived, never persisted, which is what lets a team resume
from a fresh clone that never saw the original terminal.

1. **`roster.md`, when it is still on disk.** It names each lane's working
   directory already.
2. **`git worktree list --porcelain`**, matched against the branch convention on
   the charter's `Workspace:` line, when that line is one worktree per lane. A
   lane matching no worktree is rung 4, not a guess.
3. **The charter alone**, for the other three workspaces. Under one shared tree
   every lane's working directory is the tree. Under separate repositories or
   separate directories it is the directory that lane owns, which is the leading
   segment of its `Owns` globs. Either way there is nothing to look up.
4. **Ask the user.** A guessed working directory starts a lane in the wrong tree,
   and it will edit the wrong files before anyone notices.

The lanes and the team root come from the charter on every rung,
and every relaunch carries `TEAMWORK_LANE` and `TEAMWORK_ROOT` so the boundary
hook can still tell which lane it is watching.

Write each lane's settings file again before printing anything, as
`${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/launching.md` says. A
fresh clone has none, and a team root that moved has changed `TEAMWORK_ROOT`. The file is derived from the
charter like the commands are, so rewriting it loses nothing.

Print the restart command, with `-r <lane>`, for a lane whose session still
exists on this machine. It resumes that conversation under the name the charter
uses. Print the launch command, with `-n <lane>`, for a lane whose session is
gone, as after a fresh clone. There, `-r` would open an empty picker instead of
starting the lane. When you cannot tell which case a lane is in, print both and
say which one to try first.

A lane that ran in the background restarts by its session id, as that
reference shows. `claude agents --json --all` says which lanes those are.
`-r` there starts a copy that loses the lane's name.
