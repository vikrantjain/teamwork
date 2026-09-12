# The role file

One per lane, at `<team root>/roles/<lane>.md`, at most 30 lines. The lane name is
the member's agent name, which is how a member finds its own role without being
told which one it is.

Exactly four headings, in this order. `[T2]` fails on a missing or duplicated one,
because a role that varies in shape cannot be read quickly by a tired member.

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

Every path the lane will write must appear. A path that appears in no role
belongs to the lead, which is a fallback, not a plan.

## Never

At least one line, each naming what goes wrong. This is the most-skipped section
and the most valuable: `Owns` says where the member works, and `Never` is what
stops it helpfully wandering. Write the prohibitions that this lane specifically
is tempted by, not generic ones already in `protocol.md`.

## Hands off to

The lane, and the condition that triggers the handoff. If a lane hands off to
nobody, say so — it means the lane is a leaf, and a reader should not have to
infer that from silence.

## Done means

A condition someone else could check: a command that passes, a file that exists,
an endpoint that answers. Not "the API is finished". A `Done means` that cannot
be checked turns every `DONE` message into a claim nobody can verify.
