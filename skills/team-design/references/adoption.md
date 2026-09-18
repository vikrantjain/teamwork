# Adopting a team already running

Forming starts from a goal. Adopting starts from sessions already working, with
no team root and whatever coordination they improvised. The lanes already exist
implicitly: the work has been carved up by what each session has actually
touched. Read that division. Do not invent a new one.

The plugin is needed only in this session. Members need the files, and a member
that wants the commands too can run `/plugin install teamwork@my-claude-plugins`
then `/reload-plugins` without restarting.

## The procedure

1. **Discover.** `ListAgents` gives the other Claude sessions on this machine,
   and `claude agents --json` gives the background ones. Adoption's usual case is
   separate terminals, so the first is the one that finds them. Name the ones you
   could not reach rather than leaving them out; an unreachable session is still
   editing files.
2. **Observe the division that exists.** Under version control, in order of
   weight: `git status`, recent commits, `git worktree list`. Without it, the
   files modified most recently under each session's working directory. Then, in
   both cases, one `ASK` to each session for the paths it has written and what it
   is working on. Each answers from its own context, so this costs one cheap turn
   each and is far more accurate than reading the disk alone.
3. **Report overlaps first.** Two sessions writing one path is the exact failure
   this plugin exists to prevent, and adoption is the moment it becomes visible.
   Lead with it. Do not quietly pick a winner — the user may know which edit
   matters.
4. **Read the workspace off the sessions, then resolve the team root.** Here the
   workspace is observed rather than chosen: one shared tree when every session
   is in the same directory, one worktree per lane when each has its own
   checkout, separate repositories or separate directories otherwise. Write it on
   the charter's `Workspace:` line, or `[T13]` fails the draft and the lanes'
   globs have no agreed meaning. Then resolve the team root by
   `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/team-root.md`, whose
   ladder keys on that answer. Sessions in different folders is the normal case
   here, not the exception.
5. **Draft the team root at minimum size** — `protocol.md` and `conflicts.md`
   copied verbatim, a charter, one role per session, `tracker.md`, `transport.md`.
6. **Record open work only.** Do not back-fill what is already finished.
   Reconstructing a history into the tracker is the same mistake as putting a log
   in the charter, one file over.
7. **Ratify before enforcing.** Send each member its lane, its `Owns`, its
   `Never`, and one question: what do you own that this missed? **The charter is
   not in force until every reachable member has acked.** Boundaries imposed on
   work in flight invalidate that work, and a member that never agreed to a
   boundary will cross it.
8. **Amend from the replies, validate, commit.** Then the team is adopted, and
   `/teamwork:retro` works exactly as it does on a formed team.

## What adoption cannot do

It cannot undo edits two sessions have already made to one file. It can only name
an owner from here on, and surface the overlap so the user decides.

Inferred ownership is evidence, not truth. A session may have touched a path once
by accident and have no claim to it, or own a path it has not yet written. That
is why step 7 is a gate and not a notification.
