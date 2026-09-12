# Leading a team while it runs

Forming is a burst of work. Leading is everything after it, and it is mostly
restraint: **hold the map, not the work.** The roster, the lanes and the open
cross-lane edges are yours. Diffs, files and findings are not.

A lead that reviews the work becomes the context bottleneck the team was formed
to remove, and it happens gradually enough that nobody notices until the lead is
the slowest member.

## What only you do

- **Append `FRICTION` to `friction.md`.** Members send, you write. Two members
  appending at once lose a line and neither sees it happen.
- **Write `roster.md` from the acks**, so there is one place that says which lane
  is up and where it is running.
- **Assign the item when two members want one.** It means the partition was
  wrong, so file a friction line as well as assigning it.
- **Own every shared path no lane owns**, until a retro gives it an owner.
- **Broadcast `RELOAD` after a retro**, carrying the team root's absolute path. A
  member that is not told keeps running the old rules.
- **Call the retro** when `friction.md` reaches its cap. The cap is the team
  telling you its rules cost more than they earn.

## What you never do

- **Never verify a lane's `Done means` yourself.** That is what made it a
  checkable condition. Reading the work to confirm it undoes the saving.
- **Never take a lane.** A lead carrying work cannot hold the map, and the map is
  the only thing no one else can hold.
- **Never poll.** Run `/teamwork:status`, which reads files and `ListAgents`.
  Asking four lanes for a status costs four turns and tells you less.
- **Never settle a rule dispute in messages.** Precedence is fixed in
  `conflicts.md`, and anything it does not settle waits for the retro.

## When a member goes quiet

Check `ListAgents`, then the tracker. A member that died mid-item left its state
in the tracker, because recording comes before announcing. Relaunch it under the
**same lane name** so it finds its own role file, and it resumes from files
alone. Do not replay messages at it; they are gone by design.

## When a lane runs dry

An idle lane is information, not a failure. Either its remaining work is blocked,
in which case the open edge is on your map already, or the lane is finished and
should be folded at the next retro. Never invent work to keep a member busy: work
that was not in the breakdown was not partitioned, so it has no owner.
