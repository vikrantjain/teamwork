---
description: Put contracts around Claude sessions that are already collaborating without any — discover them, read the lanes they have already carved out by what they touched, report overlapping paths, and draft a team root they ratify before it binds them.
argument-hint: [names of the running sessions, or nothing to discover them]
---

# /teamwork:adopt — contracts around a team already running

Sessions: **$ARGUMENTS**

Run the `team-design` skill's adoption procedure. Read both if they are not
already loaded:

```
${CLAUDE_PLUGIN_ROOT}/skills/team-design/SKILL.md
${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/adoption.md
```

Two steps carry the whole command, and both are easy to skip.

**Read the division that already exists; do not invent one.** The work has been
carved up by what each session has actually touched. `git status`, recent
commits, `git worktree list`, then one `ASK` to each session for the paths it has
written. A roster designed from the goal instead would cut across work in flight.

**Ratification is a gate, not a notification.** Send each member its lane, its
`Owns`, its `Never`, and one question: what do you own that this missed? The
charter is not in force until every reachable member has acked. A member that
never agreed to a boundary will cross it.

Lead your report with **overlapping paths**. Two sessions writing one path is the
failure this plugin exists to prevent, and this is the moment it becomes visible.
Do not pick a winner; the user may know which edit matters.

With no argument, discover the sessions with `ListAgents`, which reaches the
other Claude sessions on this machine, then `claude agents --json` for the
background ones. Name the ones you could not reach. An unreachable session is
still editing files.

Close with what adoption could not settle: paths whose owner is still a guess,
and edits already made across a boundary that cannot now be undone.
