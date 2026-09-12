# Context discipline

A team is worth its coordination cost only when each member carries less than one
session would have carried alone. Break these and you have paid for a team and
bought a slower single session.

## What you load

- **The startup load is five files and nothing else**: `protocol.md`,
  `charter.md`, `transport.md`, `tracker.md`, and your own role. That is about
  160 lines. Every line budget in the team root exists to keep it there.
- **Never read another lane's role file.** You cannot act on it. It is cost with
  no possible benefit.
- **Never read the whole repo.** Your role names the paths you own; that list is
  the answer to "where do I look", and it is deliberately short.

## What you send

- **Pointers, not payloads.** Write the finding to a file, send the path. A
  pasted diff lands in every reader's context, and most readers did not need it.
- **Ten lines is the ceiling.** A message that wants more is a file.
- **The first line carries the whole message.** Your teammate's human sees only
  that line until they expand it, so a first line that says nothing costs them a
  click and you a turn.

## What you delegate

- **Any read spanning more than about three files goes to an Explore subagent.**
  The fan-out then lands in a throwaway context instead of yours. This is the
  single largest saving available to you, and the one most often skipped.
- **Ask the subagent for the conclusion, not the excerpts**, unless you need to
  quote them. Excerpts you do not quote are the same waste one level down.

## What you never do

- **Never poll.** No loop over ListAgents, no "are you done?". Subscribe with
  notify_when_idle. A poll spends a turn on both sides to learn nothing.
- **Never re-derive what the tracker already says.** It is the memory. Reading it
  costs one call; reconstructing it from your transcript costs the transcript.

## If you are the lead

**Hold the map, not the work.** The roster, the lanes, and the open cross-lane
edges are yours. Diffs, files and findings are not: a lead that reviews the work
becomes the context bottleneck the team was formed to remove. Send the review to
the owning lane, or to a subagent.
