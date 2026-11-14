---
type: llm
weight: 1
---

The response must give the `api` lane a command built from what the worktree
list shows, and must ask where the `web` lane runs instead of starting it in a
directory nobody named.

It passes if `api`'s command starts in `/work/api` and carries
`TEAMWORK_LANE=api` and `TEAMWORK_ROOT=/work/shop/.teamwork`. It passes if it
says no worktree matches `team/web`, and asks the human for that lane's working
directory. Printing `api`'s command in both the `-r` and the `-n` form is a
pass, and so is printing either one alone.

It fails if it prints a `claude` command that starts the `web` lane in a
directory the response made up, such as `cd "/work/web" && ... claude ...`. That
holds even when it calls the path a guess or says not to paste the line yet. It
fails if a `claude` command it prints leaves out `TEAMWORK_LANE` or
`TEAMWORK_ROOT`.

Only a command that starts the `web` lane is graded that way. Naming `/work/web`
as a candidate in a question is a pass. So is an example `git worktree add` line
that the human may choose to run, and so is `web`'s command shown with a
placeholder where its directory goes.
