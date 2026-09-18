# When a conflict happens

Copied into the team root verbatim, like protocol.md. Read it when a conflict
actually occurs. It is not part of the startup load.

Most of these cannot arise by construction: lanes own disjoint paths, and items
are partitioned by lane before anyone starts. So a conflict reaching you means a
boundary is wrong. Resolve it by the table, then send FRICTION.

| Conflict | Rule |
|---|---|
| You need a change in a path you do not own | You do not make it. ASK the owner, and the owner makes it. |
| Two members want one item | The partition is wrong. The lead assigns it. Where the tracker has an assignee, the first write wins and the other takes the next item without arguing. |
| Merge conflict between two lanes' branches | Whoever merges second resolves it. If the resolution touches another lane's owned path, stop and ASK. |
| Two rules disagree | Precedence is fixed: protocol.md, then charter.md, then your own role file. There is nothing to negotiate. |
| A waits on B and B waits on A | Neither of you resolves it. The lead splits one item. Never restructure the breakdown while working it. |
| A shared path has no owner | It belongs to the lead until a retro assigns it. Do not adopt it yourself. |
| Your role and the work disagree | The role wins for now. Send FRICTION so the retro can fix the role. |
| Anything still unresolved | Escalate to the human. Never settle it by whoever messaged last. |
