# The role file

One per lane, at `<team root>/roles/<lane>.md`, at most 30 lines. The file is
named for the lane, and `TEAMWORK_LANE` carries the lane, which is how a member
finds its own role without being told which one it is. A lead holding a
downstream lane gets one too, at `roles/lead.md`.

Exactly four headings, in this order. `[T2]` fails on one that is missing,
duplicated or out of order, because a role that varies in shape cannot be read
quickly by a tired member.

    # <lane>

    ## Owns
    - <path glob>
    - <path glob>

    ## Never
    - <a prohibition, and what goes wrong without it>

    ## Hands off to
    - <lane>, when <condition>

    ## Done means
    - <a verifiable condition>

## Owns

Path globs, one per line, and nothing else. No prose, no topics, no
responsibilities — the validator reads this section to prove no two lanes own the
same path, and a sentence here defeats that check.

Globs are relative to the workspace, never absolute. Which directory that is
comes from the charter's `Workspace:` line: the tree under one shared tree, the
lane's own worktree under one worktree per lane, and the directory holding them
all under separate repositories or separate directories. An absolute path and a
relative one naming the same file look unequal to `[T5]`, which then passes a
real collision, so `[T2]` rejects the absolute one.

Every path the lane will write must appear. A path that appears in no role
belongs to the lead, which is a fallback, not a plan.

## Never

At least one line, each naming what goes wrong. This is the most-skipped section
and the most valuable: `Owns` says where the member works, and `Never` is what
stops it helpfully wandering. Write the prohibitions that this lane specifically
is tempted by, not generic ones already in `protocol.md`.

Every shared path another lane owns belongs here. Those are written by commands —
a package manager, a migration tool, a build — and the boundary hook does not see
a write made through `Bash`, so this line is the only thing standing between two
lanes and one regenerated lockfile.

## Hands off to

The lane, and the condition that triggers the handoff. If a lane hands off to
nobody, say so — it means the lane is a leaf, and a reader should not have to
infer that from silence.

## Done means

A condition someone else could check: a command that passes, a file that exists,
an endpoint that answers. Not "the API is finished". A `Done means` that cannot
be checked turns every `DONE` message into a claim nobody can verify.
