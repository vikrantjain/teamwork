# The charter

At most 50 lines, at `<team root>/charter.md`. It is the team's own law, and the
only contract file a retro may edit. Every member re-reads it on every context
load, so a line that does not change what someone does is a line that costs the
team forever.

    # <the goal, in one sentence>

    Team root: /absolute/path/to/.teamwork
    Team name: <what this team is called; it names the run, not a CLI flag>
    Isolation: <one shared tree | one worktree per lane, branches <prefix>/<lane>>

    ## Lanes
    - <lane> — <what it covers, in a phrase>
    - <lane> — <what it covers, in a phrase>

    ## Shared paths
    - <path no single lane can own> — owned by <lane>

    ## Working rules
    - <a rule this team needs, and what goes wrong without it>

    ## Human gates
    - <an action that stops and asks, every time>

    ## Done
    - <the condition that disbands the team>

The charter names no other file. A member loads `tracker.md` and `transport.md`
by name at startup, `protocol.md` says it is copied and never edited and points
at `conflicts.md` itself, and `[T7]` proves both. A pointers section would spend
four of these fifty lines telling a member what it has already read.

## The required lines

`Team root:` must be absolute and must be the directory itself; `[T9]` fails
otherwise, which is what catches a member editing its own stale worktree copy.

`## Lanes` entries must start with the lane name, because `[T4]` matches them
against the files in `roles/`. A lane named here with no role file, or a role file
named in no lane, is a team where somebody has no rules or nobody has that lane.

`## Shared paths` entries name an owner, and that lane's role must claim the path
under its own `## Owns`; `[T11]` fails otherwise. The boundary hook reads role
files and nothing else, so a path the charter hands to a lane that never claims
it is a path the hook attributes to nobody and lets every lane write.

Give every other lane a `## Never` line for each shared path as well. A shared
path is usually written by a command rather than by an edit — a lockfile by the
package manager, a schema by a migration tool, build output by the build — and
the hook cannot see a write made through `Bash`. So for the one class of path the
charter works hardest to give an owner, the prohibition in the other lanes' roles
is the whole of the enforcement.

`Isolation:` names the branch convention when lanes get worktrees. A resume and a
finish both have to find a lane's branch again, and without the convention
written down they match on a directory name and call a guess a lookup. Name each
worktree directory for its lane as well. The boundary hook's second rung matches
that directory's own name against the lane names, so a worktree named anything
else leaves the lane unidentified and every write allowed.

## Working rules

Only rules this team needs. Anything true of every team is already in
`protocol.md`, and repeating it there is how a 50-line charter becomes a 200-line
one. Three to six rules is normal. Each names its failure mode.

## Human gates

The actions that stop and ask, every time: publishing, deleting, touching
production, spending money, changing scope. Be specific enough that a member can
tell whether it is at one. "Use judgement" is not a gate.

## Done

What finishing looks like, checkable by someone who was not here. A team with no
stop condition keeps working, and the cost of a team that will not stop is paid
in tokens for as long as nobody notices.
