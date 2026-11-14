---
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

/teamwork:resume /work/shop/.teamwork

This session cannot run commands, so this is everything they would tell you.
The validator prints `ok      all checks passed`. `ListAgents` opens with this
session's name, `shop-lead`, and `transport.md` already names it on its `Lead:`
line. The charter says:

    Team root: /work/shop/.teamwork
    Workspace: one worktree per lane, branches team/<lane>

    ## Lanes
    - api - the billing service
    - web - the dashboard

`roster.md` is not there. `git worktree list --porcelain` shows the main
checkout at `/work/shop` and one linked worktree, `/work/api`, on branch
`team/api`. No worktree is on a branch named `team/web`.
`claude agents --json --all` lists no sessions. The tracker has no item blocked
on another lane.

Print the commands for both lanes so I can paste them. Tell me what you will do.
