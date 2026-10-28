# Launching a lane, and starting it again

Every start of a lane has to carry three things: its lane, its team root and its
name. A start missing the lane or the team root is one the boundary hook cannot
watch. A start missing the name is one no message can reach. Nothing reports
either at the time.

What follows is how the installed CLI behaves, verified against it. None of it
can be derived from the principle, which is why it is written down.

## The settings file

In every directory that exactly one member lane works in, write
`.claude/settings.local.json` carrying both variables:

    {"env": {"TEAMWORK_LANE": "<lane>", "TEAMWORK_ROOT": "<team root>"}}

Claude Code reads that file at every start in the directory: a terminal, `--bg`,
`-r`, or a human typing plain `claude`. The launch command sets the same two
variables only for the process it starts. Without the file, a lane started any
other way is unidentified, and the boundary hook allows its every write.

Merge into a file that already exists. Add the two keys under `env` and leave
every other key as it was, because the file was the user's first.

Write it under worktrees, separate repositories and separate directories. Never
write it under one shared tree, or into the lead's own working directory. Every
session started in that directory would claim the lane, the lead included, and
`${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/leading.md` says what that
costs.

Keep it out of version control. When
`git -C "<dir>" check-ignore -q .claude/settings.local.json` says it is not
ignored, append that path to the file named by
`git -C "<dir>" rev-parse --path-format=absolute --git-path info/exclude`. That
one file covers every worktree of the repository and is never committed. A
committed copy would merge into the base branch at the finish, and every later
session in the main checkout would then be that lane.

A lane whose directory does not exist yet gets its file when its `JOIN` arrives,
which names the directory. Its launch command identifies its first start until
then.

## The launch command

One per lane, identical but for the lane name and its working directory, every
path absolute:

    cd "<lane's working directory>" && TEAMWORK_LANE=<lane> TEAMWORK_ROOT="<team root>" \
      claude --agent teamwork:member --add-dir "<team root>" -n <lane> "/teamwork:join <lane>"

The human pastes one line per terminal and types nothing after it. `-n` sets the
session's name, which is its address. The quoted prompt runs the join as the
session's first turn. The leading `cd` lets the line be pasted from any
directory, and resuming needs it, because a session is resumed only from the
directory it ran in. Print the same shape for every lane rather than trimming it
per lane: under one shared tree the team root is already inside the lane's
directory and `--add-dir` changes nothing, and under the other three it is the
only thing that lets the lane read its own five files. One shape is one thing
for the human to get wrong.

**Write every path in full.** `--add-dir` accepts a relative path, resolves it
against whatever directory the command was pasted into, and reports nothing when
it lands somewhere else. That lane then starts, is told its lane and its team
root, has its writes policed against globs it cannot read, and cannot open the
charter that would explain it. The boundary hook reads the files itself rather
than through the tool that `--add-dir` governs, which is why a lane can be bound
and blind at the same time.

**Keep every path in quotes.** A path with a space in it splits into two
arguments without them. The `cd` then fails, and the lane starts wherever the
human pasted the line.

The two variables are what let the boundary hook deny a write to a path another
lane owns. The lane's settings file sets the same two at every later start.
Without either, the hook falls back to the lane's directory name. Under one
shared tree there is no such fallback, so it allows every write rather than
blocking one it cannot attribute.

## Permission mode

Every lane runs in the lead's permission mode. SendMessage's own description in
the installed CLI says what happens otherwise. A session in a different mode
from the sender holds that sender's messages for its human's approval, and may
let them expire. The sender is sent a delivery notice when that happens. A
member whose `JOIN` the lead never approves waits for an answer that is not
coming. A lane that never approves `PARK` never answers it.

Ask the human which mode the team runs in rather than choosing it. A mode
decides what a lane may do without asking its human, and that is the human's
decision. When it is not the mode a plain `claude` starts in, put
`--permission-mode <mode>` after `claude` in every launch and restart command.
Say that the lead's own session must run in that mode too.

## A lane in the background

Add `--bg` after `claude` and the lane needs no terminal. It keeps the name, the
environment and the working directory the command gives it, and `SendMessage`
reaches it by name like any other lane. `claude agents` lists it, and
`claude attach <lane>` opens it in a terminal. With `--bg` the lead may run the
commands itself through Bash. Do that only when the human asks, because each
command starts a session that spends the human's usage.

Say two things a background lane changes. It will not start in a folder Claude
Code has not trusted, and it prints which folder. A worktree inherits its
repository's trust, and a separate repository needs `claude` run in it once. A
background lane waiting on input shows as `blocked` in `claude agents`, and
nobody sees what it is asking until someone attaches.

## A lane without the plugin

Drop `--agent teamwork:member` and the quoted join for a lane whose session does
not have the plugin. Keep `-n <lane>`, because the name is set by the CLI and not
by the plugin. The files bind a member, and the agent definition only points at
them. Say what that lane gives up, because it is not visible from inside it: the
boundary hook ships with the plugin, so nothing checks that lane's writes and
nothing at startup tells it so. It cannot run `/teamwork:join` either. Hand it
the five files to read by absolute path in place of the join.

## The restart command

Print it under each launch command. It is the same line with `-r <lane>` in place
of `-n <lane>`:

    cd "<lane's working directory>" && TEAMWORK_LANE=<lane> TEAMWORK_ROOT="<team root>" \
      claude --agent teamwork:member --add-dir "<team root>" -r <lane> "/teamwork:join <lane>"

It is for every start after the first: a reboot, a crash, a session stopped at
its token limit. `-r` resumes the conversation by its name, so the lane keeps
what it knew. The quoted join runs again in the resumed conversation, which
rereads the five files and tells the lead the lane is back. The variables and
`--add-dir` are repeated because they belong to the process, and a resumed
conversation does not bring them back.

Say that the first start must use the launch command. With no session of that
name, `-r` opens an empty picker rather than starting one. After a `/clear`, two
sessions share the name, so `-r` opens the picker with the newest first. Enter
twice takes it: the first Enter moves from the search box into the list. The
join runs once the pick is made.

## Restarting a background lane

**A lane started with `--bg` restarts by its session id, never by its name:**

    cd "<lane's working directory>" && claude --bg --resume <session id> "/teamwork:join <lane>"

`claude agents --json --all` lists the id as `sessionId`, beside the lane's
`name` and `cwd`. Take the newest session that matches both. Pass no flag but
`--bg` and `--resume`. A background session keeps the flags and environment it
was started with, and any flag passed again starts a copy instead.
`--bg -r <lane>` also starts a copy, and the copy loses the lane's name. When two
sessions share the name, as after a `/clear`, it opens the picker where nobody
can see it, and the lane sits `blocked`.
