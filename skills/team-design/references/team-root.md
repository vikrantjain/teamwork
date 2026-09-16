# Where the shared files live

Members do not always share a working directory, so "read `.teamwork/`" is not a
sufficient instruction. Resolve **one absolute path**, write it on the charter's
`Team root:` line, and put it in every launch command as `--add-dir`.

Nothing goes in the user's home folder. The team root is inside the project, at a
location the projects genuinely share, or at a path the user gives.

## The ladder, first match wins

1. **One shared tree** — `<repo>/.teamwork`. Members are already inside it and
   need no `--add-dir`.
2. **Worktrees of one repo** — the **main** worktree's `.teamwork`, found from
   any worktree as the parent of
   `git rev-parse --path-format=absolute --git-common-dir`. It computes the same
   from everywhere, so nothing is asked.
3. **Several repos under a shared parent** — `<common ancestor>/.teamwork`, but
   only when that ancestor is meaningful: not the home directory, not a
   filesystem root, and either carrying a workspace marker (a superproject
   `.git`, `pnpm-workspace.yaml`, `go.work`, a Cargo or Maven workspace, a
   `.code-workspace`) or holding every member's root as a direct child.
4. **Anything else — ask the user.** A shallow common ancestor is a coincidence,
   not a shared location, and guessing one scatters team state where nobody
   thinks to look for it.

Record the answer in the charter so it is asked once and never re-derived.

Rungs 3 and 4 can land outside any repository. Say so when they do: nothing there
is committed, so the contracts are not reviewable in a pull request and do not
travel with the project, which were the two reasons for writing them down. A park
then has nothing to commit either.

## What the team root holds

Committed, because a contract that is not versioned with the code cannot be
reviewed in a pull request and does not travel with the project:

    protocol.md      copied from the plugin, never edited
    conflicts.md     copied from the plugin, never edited
    charter.md       this team's own law
    roles/<lane>.md  one per lane, named for the lane
    tracker.md       the one work-item backend and its commands
    transport.md     the one substrate and how to address a lane
    decisions.md     settled choices with their reasons
    backlog.md       only when tracker.md's rung 3 put the board here

`[T1]` budgets them, because a member reloads them on every context load:
protocol.md 50 lines, conflicts.md 30, charter.md 50, each role file 30,
tracker.md 20, transport.md 15, decisions.md 60. `backlog.md` has none: it is the
tracker, and a tracker is a record rather than a rule.

`decisions.md` has no template. One bullet per settled choice, each carrying its
reason rather than its conclusion alone, so the next retro does not reopen it
without new evidence. It is the one file that gains a line at every retro, which
is why `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/retro.md` prunes it in
the same pass.

Gitignored, because it is this run's state rather than the team's law:

    friction.md      what the rules cost, appended by the lead only
    roster.md        which lane is up, where, and whether it has acked

Add both to the project's `.gitignore` when you create the team root. Committing
them puts a churning file in every member's next pull, and `roster.md` is wrong
for everyone the moment one member restarts.

`roster.md` has no template and no budget: it is a scratch list the lead writes
from the acks, one line per lane giving the lane, its working directory, and
whether it has acked or parked. Nobody but the lead, `/teamwork:status` and
`/teamwork:resume` reads it. Losing it costs nothing: a resume re-derives each
lane's working directory from the charter and from `git worktree list`.

## Why worktrees are the case that bites

`claude --worktree` gives each member its own checkout, so each gets its own
committed copy of the team root, and those copies diverge the moment a retro
commits on another branch. A member reading its own copy runs last week's rules
and nothing announces it.

That is why `protocol.md` rule 4 says to address the team root by absolute path,
why every `RELOAD` repeats that path, and why `[T9]` fails when the charter's
`Team root:` is not the directory being validated.

The boundary hook resolves the root by this same ladder: `$TEAMWORK_ROOT`, then
the main worktree's `.teamwork` from `git rev-parse --git-common-dir`, then the
nearest one walking up. A hook that read a lane's own copy would enforce last
week's ownership, which is worse than not enforcing at all.

## One filesystem

Every member resolves the same path on the same machine. That is what lets
`[T9]` prove the charter you are reading is the team root rather than a copy of
it, and a stale copy read as law is the failure this whole file exists to
prevent. A team whose members cannot share a path is not a team this plugin
forms.
