---
name: team-design
description: >
  How to design, form, audit and continuously improve a team of Claude Code
  sessions working one goal. Use when deciding whether a goal needs a team at
  all, how many members it needs, what each may and may not touch, where work
  items and bugs will be recorded, how members address each other, and how the
  rules get better as the work exposes their gaps. Also use to adopt sessions
  that are already collaborating without contracts, to lead one while it runs,
  to run a retro, to park one so a fresh set of sessions can resume it, to
  finish one by landing its branches or worktrees when its work is done, and
  to audit a team root that has grown. The rule it exists to enforce is that
  every lane, boundary and rule traces to something in the work, and that a
  contract never becomes a log or a task board. Finishing never merges and
  never removes a worktree: it reports what will not land cleanly and hands
  the commands to the human. NOT for working inside a lane
  once the team exists, which is team-member's job.
---

# Designing a team

**Derive the team from the work. A lane, a rule or a boundary that does not trace
to something in the breakdown is decoration.**

When a case below is not covered, decide it from that sentence. Decoration is not
harmless here: every line is re-read by every member on every context load, so an
unearned rule is a tax charged forever.

## Forming a team

1. **Get the breakdown first**, from the plan the project already has and from
   the questions it does not answer. A plan says what the pieces are and almost
   never says who may touch what or when the team stops, so finding one shortens
   the interview rather than replacing it. Follow
   `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/discovery.md`. It also
   reads the ground the team will run on, and it ends at a proposal the human
   ratifies before anything is written.
2. **Size the team from the breakdown**, never from the goal's ambition, and
   choose the workspace in the same pass. Follow
   `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/sizing.md` exactly. It
   can return "one session", and when it does, say so and stop.
3. **Resolve the team root** — one absolute path every member can reach. Follow
   `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/team-root.md`; its ladder
   keys on the workspace, which is why step 2 comes first. Ask the user rather
   than guessing; a wrong guess scatters team state where nobody looks for it.
   Resolve the **workspace root** in the same pass, which is the directory every
   lane's `Owns` globs are read against, and write it on the charter under the
   three workspaces that are not worktrees. It is usually the team root's parent,
   and `[T14]` still fails a charter that leaves it to be derived from that.
4. **Pick the tracker**, following
   `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/trackers.md`. One backend,
   written into `tracker.md` with its create, claim and close commands.
5. **Record the substrate**, following
   `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/transport.md`. A lane is a
   session of its own on this machine, so this is rarely a choice; write it into
   `transport.md` with how to discover a lane, how to send to it, and this
   session's own name as the `Lead:`. Every member loads this file, so a team
   without it is a list of strangers.
6. **Write the contracts** from
   `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/charter-template.md` and
   `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/role-template.md`. Copy
   `protocol.md` and `conflicts.md` from
   `${CLAUDE_PLUGIN_ROOT}/skills/team-member/references/` byte for byte.
7. **Create the rest of the team root**, or the validator reports a team that is
   half-built. `decisions.md` holding the workspace choice and its reason, an
   empty `friction.md` and an empty `roster.md`. Add those last two to the
   project's `.gitignore` when the team root is under git, and skip that when it
   is not. `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/team-root.md` says
   why they are not committed.
8. **Run the validator** before telling anyone the team exists:
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_team.py "<team root>"`.
9. **Write each lane's settings file**, so the lane is identified however it is
   next started. In every directory that exactly one member lane works in, write
   `.claude/settings.local.json` carrying both variables:

       {"env": {"TEAMWORK_LANE": "<lane>", "TEAMWORK_ROOT": "<team root>"}}

   Claude Code reads that file at every start in the directory: a terminal,
   `--bg`, `-r`, or a human typing plain `claude`. The launch command sets the
   same two variables only for the process it starts. Without the file, a lane
   started any other way is unidentified, and the boundary hook allows its every
   write.

   Merge into a file that already exists. Add the two keys under `env` and leave
   every other key as it was, because the file was the user's first.

   Write it under worktrees, separate repositories and separate directories.
   Never write it under one shared tree, or into the lead's own working
   directory. Every session started in that directory would claim the lane, the
   lead included, and
   `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/leading.md` says what
   that costs.

   Keep it out of version control. When
   `git -C "<dir>" check-ignore -q .claude/settings.local.json` says it is not
   ignored, append that path to the file named by
   `git -C "<dir>" rev-parse --path-format=absolute --git-path info/exclude`. That
   one file covers every worktree of the repository and is never committed. A
   committed copy would merge into the base branch at the finish, and every
   later session in the main checkout would then be that lane.

   A lane whose directory does not exist yet gets its file when its `JOIN`
   arrives, which names the directory. Its launch command identifies its first
   start until then.
10. **Print the launch commands** for the user, one per lane, identical but for
   the lane name and its working directory, every path absolute:

       cd "<lane's working directory>" && TEAMWORK_LANE=<lane> TEAMWORK_ROOT="<team root>" \
         claude --agent teamwork:member --add-dir "<team root>" -n <lane> "/teamwork:join <lane>"

   The human pastes one line per terminal and types nothing after it. `-n` sets
   the session's name, which is its address. The quoted prompt runs the join as
   the session's first turn. The leading `cd` lets the line be pasted from any
   directory, and resuming needs it, because a session is resumed only from the
   directory it ran in. Print the same shape for
   every lane rather than trimming it per lane: under one shared tree the team
   root is already inside the lane's directory and `--add-dir` changes nothing,
   and under the other three it is the only thing that lets the lane read its own
   five files. One shape is one thing for the human to get wrong.

   **A lane may run in the background.** Add `--bg` after `claude` and the lane
   needs no terminal. It keeps the name, the environment and the working
   directory the command gives it, and `SendMessage` reaches it by name like any
   other lane. `claude agents` lists it, and `claude attach <lane>` opens it in a
   terminal. With `--bg` the lead may run the commands itself through Bash. Do
   that only when the human asks, because each command starts a session that
   spends the human's usage.

   Say two things a background lane changes. It will not start in a folder
   Claude Code has not trusted, and it prints which folder. A worktree inherits
   its repository's trust, and a separate repository needs `claude` run in it
   once. A background lane waiting on input shows as `blocked` in
   `claude agents`, and nobody sees what it is asking until someone attaches.

   **Write every path in full.** `--add-dir` accepts a relative path, resolves it
   against whatever directory the command was pasted into, and reports nothing
   when it lands somewhere else. That lane then starts, is told its lane and its
   team root, has its writes policed against globs it cannot read, and cannot
   open the charter that would explain it. The boundary hook reads the files
   itself rather than through the tool that `--add-dir` governs, which is why a
   lane can be bound and blind at the same time.

   **Keep every path in quotes.** A path with a space in it splits into two
   arguments without them. The `cd` then fails, and the lane starts wherever the
   human pasted the line.

   The two variables are what let the boundary hook deny a write to a path
   another lane owns. The lane's settings file sets the same two at every later
   start. Without either, the hook falls back to the lane's directory name.
   Under one shared tree there is no such fallback, so it allows every write
   rather than blocking one it cannot attribute.

   Drop `--agent teamwork:member` and the quoted join for a lane whose session
   does not have the plugin. Keep `-n <lane>`, because the name is set by the CLI
   and not by the plugin. The files bind a member, and the agent definition only
   points at them. Say what that lane gives up, because it is not visible from
   inside it: the boundary hook ships with the plugin, so nothing checks that
   lane's writes and nothing at startup tells it so. It cannot run
   `/teamwork:join` either. Hand it the five files to read by absolute path in
   place of the join.

11. **Print the restart command under each launch command.** It is the same line
   with `-r <lane>` in place of `-n <lane>`:

       cd "<lane's working directory>" && TEAMWORK_LANE=<lane> TEAMWORK_ROOT="<team root>" \
         claude --agent teamwork:member --add-dir "<team root>" -r <lane> "/teamwork:join <lane>"

   It is for every start after the first: a reboot, a crash, a session stopped
   at its token limit. `-r` resumes the conversation by its name, so the lane
   keeps what it knew. The quoted join runs again in the resumed conversation,
   which rereads the five files and tells the lead the lane is back. The
   variables and `--add-dir` are repeated because they belong to the process,
   and a resumed conversation does not bring them back.

   Say that the first start must use the launch command. With no session of
   that name, `-r` opens an empty picker rather than starting one. After a
   `/clear`, two sessions share the name, so `-r` opens the picker with the
   newest first. Enter twice takes it: the first Enter moves from the search box
   into the list. The join runs once the pick is made.

   **A lane started with `--bg` restarts by its session id, never by its name:**

       cd "<lane's working directory>" && claude --bg --resume <session id> "/teamwork:join <lane>"

   `claude agents --json --all` lists the id as `sessionId`, beside the lane's
   `name` and `cwd`. Take the newest session that matches both. Pass no flag but
   `--bg` and `--resume`. A background session keeps the flags and environment
   it was started with, and any flag passed again starts a copy instead.
   `--bg -r <lane>` also starts a copy, and the copy loses the lane's name. When
   two sessions share the name, as after a `/clear`, it opens the picker where
   nobody can see it, and the lane sits `blocked`.

## What belongs in a contract

1. **A rule earns its line by naming its failure mode.** Say what goes wrong
   without it. A rule that cannot name one is advice, and advice is not followed.
2. **No record of anything that happened.** No dates, no checkboxes, no statuses,
   no issue ids, no "what we tried". Those belong in the tracker. This is what
   `[T3]` enforces, and it is the difference between a charter that gets read and
   one that gets skimmed.
3. **No task assignments.** The charter says which lane owns which paths. Which
   item a lane is working right now is the tracker's business and changes hourly.
4. **Every lane's `Never` is filled in.** A role with no prohibition has no
   boundary, and a boundary nobody wrote down is one nobody will respect.
5. **Name an owner for every shared path, and put the path in that lane's
   `Owns`** — lockfiles, schemas, CI config, build output. An unowned shared path
   is where two lanes collide first, and the boundary hook reads role files only,
   so a path named in the charter alone is one every lane may still write.
6. **Budgets are hard.** To add a line at a retro you must remove one. Without
   that rule, "keep improving the rules" becomes accretion, and an accreted
   charter destroys the context budget that justified the team.

## Leading it once it runs

Forming is a burst; leading is the rest, and it is mostly restraint. Most leads
hold no lane and assign nothing, because the lanes were partitioned before anyone
started and each member takes its own next item. A lead may also hold one lane of
its own when nothing waits on it, as a lane like any other, with a role file and
a name under `## Lanes`. That one lane may carry several downstream duties at
once, because a lane is a set of paths and `roles/lead.md` owns their union.

The duties that belong to nobody else — appending friction, writing the roster,
assigning the contested item, owning the unowned shared path, broadcasting
`RELOAD` — are in
`${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/leading.md`, with the ones a
lead is tempted into and should not do. **Hold the map, not the work**, or the
lead becomes the bottleneck the team was formed to remove.

## Stopping it, and starting it again

A run ends at the charter's `## Done` or at a park. **A park is a stop at a point
the tracker fully describes**, so a fresh set of sessions resumes exactly there.
The drain, the four conditions a lane meets before it is parked, and the ladder
that re-derives each lane's launch command are in
`${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/parking.md`.

A park writes no new file into the team root. Its work is making the tracker
true, because a snapshot of where everyone got to drifts from the tracker and is
the log `[T3]` exists to keep out.

**A run that reaches `## Done` is finished, not parked.**
`${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/finishing.md` checks the
stop condition, parks every lane, and then lands the work the way the charter's
`Workspace:` line says it is separated. Under worktrees or separate repositories
that means testing each merge and handing the merges and removals to the human;
under one shared tree or separate directories there is nothing to merge and the
report says where the work is. It never merges and never removes a worktree,
because both are human gates by the charter's own definition and a park is the
only thing that was protecting the uncommitted work inside them.

## Improving the rules while the work runs

The loop is in `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/retro.md`.
Two parts of it are load-bearing and get skipped: a cause appearing **once** is
noise and must not produce a rule, and a
rule whose target cause **recurred** has failed and must be reverted rather than
supplemented. Without those two, the team accumulates rules instead of better
ones.

## Adopting a team already running

When sessions are already collaborating without contracts, the lanes exist
implicitly and must be read from what each session has actually touched, not
invented. Follow
`${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/adoption.md`. Its
ratification step is a gate, not a notification: boundaries imposed on work in
flight invalidate that work.

## Further detail

- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/discovery.md` — finding the work, and the five questions when there is no plan.
- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/sizing.md` — how many members, which workspace, and when the answer is none.
- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/team-root.md` — where the shared files live, and when to ask.
- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/trackers.md` — choosing one work-item backend.
- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/transport.md` — the one kind of member, and how lanes are addressed.
- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/charter-template.md` — the charter, with its required lines.
- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/role-template.md` — the four headings and what fills them.
- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/leading.md` — the lead's duties while the work runs.
- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/parking.md` — stopping where a fresh session can resume.
- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/finishing.md` — landing the work and disbanding.
- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/retro.md` — the optimization loop.
- `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/adoption.md` — putting contracts around a running team.

Each path is written in full because the working directory at runtime is the
user's project, not this plugin.
