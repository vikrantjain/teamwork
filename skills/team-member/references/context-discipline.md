# Context discipline

A team is worth its coordination cost only when each member carries less than one
session would have carried alone. Break these and you have paid for a team and
bought a slower single session.

The startup load is five files. Every line budget in the team root exists to keep
it small, and everything below is about not spending more.

Nothing here repeats `protocol.md`. Its rule 1 already covers pointers over
payloads and its rule 2 covers never polling, and a rule written in two places
drifts in one of them.

## What you send

- **The first line carries the whole message.** Your teammate's human sees only
  that line until they expand it, so a first line that says nothing costs them a
  click and you a turn.

## What you delegate

- **Any read spanning more than about three files goes to an Explore subagent.**
  The fan-out then lands in a throwaway context instead of yours. This is the
  single largest saving available to you, and the one most often skipped.
- **Ask the subagent for the conclusion, not the excerpts**, unless you need to
  quote them. Excerpts you do not quote are the same waste one level down.

## What you never re-derive

- **What the tracker already says.** It is the memory. Reading it costs one call;
  reconstructing it from your transcript costs the transcript.
- **What your role already names.** Your `## Owns` is the answer to "where do I
  look", and it is deliberately short. Reading the tree to find out is reading
  the tree.
