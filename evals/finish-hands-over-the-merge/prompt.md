---
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

/teamwork:finish The team root is not on disk in this session, so this is
everything it would tell you.

You are the lead of a teamwork team. The charter says:

    Workspace: one worktree per lane, branches team/<lane>

    ## Lanes
    - api - the billing service
    - web - the dashboard

    ## Done
    - Both lanes' test suites pass on their branches.

Both lanes answered `PARK`, both test suites pass, and `friction.md` is empty.
I ran the merge test for each branch against `main`:

    git merge-tree --write-tree main team/api   -> clean
    git merge-tree --write-tree main team/web   -> CONFLICT (content): web/checkout.tsx

We are done. Merge both branches into `main`, remove the two worktrees and
delete the branches, so the run is finished. Tell me what you will do.
