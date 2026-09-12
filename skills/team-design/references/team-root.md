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

## Why worktrees are the case that bites

`claude --worktree` gives each member its own checkout, so each gets its own
committed copy of the team root, and those copies diverge the moment a retro
commits on another branch. A member reading its own copy runs last week's rules
and nothing announces it.

That is why `protocol.md` rule 4 says to address the team root by absolute path,
why every `RELOAD` repeats that path, and why `[T9]` fails when the charter's
`Team root:` is not the directory being validated.

## Separate machines

There is no shared filesystem, so no path is shared. The team root is committed
and git is the sync: `RELOAD` means pull, then re-read. When the members are
separate repos on separate machines, rung 4 applies and the user names which repo
carries the contract.
