---
description: Adopt a lane on an existing team in this session — read the team root by absolute path, load only this lane's rules, announce to the lead, and start working the lane under the team's protocol.
argument-hint: <lane name> [team root path, if this session is outside it]
---

# /teamwork:join — take a lane

Lane, and team root if given: **$ARGUMENTS**

Run the `team-member` skill's procedure. Read it if it is not already loaded,
because a session that joins without it works the project instead of the lane:

```
${CLAUDE_PLUGIN_ROOT}/skills/team-member/SKILL.md
```

Two rules decide whether this goes well.

**Read the team root by its absolute path.** The charter's `Team root:` line
names it. A relative `.teamwork/` may be this worktree's own stale copy, and you
would run last week's rules with nothing announcing it.

**Load five files and stop**: `protocol.md`, `charter.md`, `transport.md`,
`tracker.md`, and `roles/<lane>.md`. Never another lane's role file — you cannot
act on it, and the context budget is the reason this team exists.

Then check this session's name: `ListAgents` opens with it. When it is not the
lane, ask your human to run `/rename <lane>`. You cannot run `/rename` yourself,
and a lane under the wrong name is one nobody can reach under the name the
charter uses. Then send the lead `JOIN <lane>` with your working directory and
the paths you own, and wait for the lead's `JOIN` before taking an item. If the
lead cannot be reached at all, say so and start anyway.

This command may run again in a conversation that already joined. The restart
command resumes a lane and joins it in the same line. Join exactly as the first
time: reread the five files, because a retro may have changed them, and send
`JOIN` again, because the lead may be a fresh session with no roster.

With no lane given, read the charter's `## Lanes` and ask which one this session
is. Do not infer it from the working directory; a worktree name is a convention,
not a claim.

If this session has already edited paths outside the lane it is taking, say so
before you start. That is an overlap the lead needs, not a detail to tidy away.
