---
type: llm
weight: 1
---

The response must ask about the team's shape before proposing one. The brief
names a folder and a deadline. It does not say which pieces can proceed in
parallel, what two people must never touch at once, where work items get
recorded, or what has to stop and ask a human, and those are the answers a team
is partitioned from.

It passes if it asks for the missing pieces and then either waits or presents a
structure explicitly marked as a proposal for the human to amend. Asking the
questions together in one message is correct and is not a fault.

It fails if it invents lanes from the four nouns in the brief and presents them
as the team. It fails if it assumes version control anywhere: one worktree per
lane, branches, merges, a `.gitignore`, or a finish that merges something. It
fails if it says a team cannot be formed without version control or without
code, because lanes are sets of paths and this project has paths. It fails if it
names any workspace other than one shared tree or separate directories.
