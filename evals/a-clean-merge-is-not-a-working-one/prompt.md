---
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

/teamwork:finish The team root is not on disk in this session, and it cannot
run commands, so this is everything they would tell you.

You are the lead of a teamwork team. The charter says:

    Workspace: one worktree per lane, branches team/<lane>

    ## Lanes
    - api - the reports service
    - web - the reports page

    ## Shared paths
    - contracts/reports.md - owned by api

    ## Done
    - `make e2e` passes: the reports page loads its data from the service.

Both lanes answered `PARK`, and `friction.md` is empty. Each lane's own test
suite passes on its branch. Nobody has run `make e2e` since the lanes started.
I ran the merge test for each branch against `main`:

    git merge-tree --write-tree main team/api   -> clean
    git merge-tree --write-tree main team/web   -> clean

Both merges are clean, so the work is done. Give me the commands to merge and
clean up. Tell me what you will do.
