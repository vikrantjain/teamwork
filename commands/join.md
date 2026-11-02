---
description: Adopt a lane on an existing team in this session — read the team root by absolute path, load only this lane's rules, announce to the lead, and start working the lane under the team's protocol.
argument-hint: <lane name> [team root path, if this session is outside it]
---

# /teamwork:join — take a lane

Lane, and team root if given: **$ARGUMENTS**

Follow `## Starting` in the `team-member` skill, then work by the rest of it.
Read it if it is not already loaded, because a session that joins without it
works the project instead of the lane:

```
${CLAUDE_PLUGIN_ROOT}/skills/team-member/SKILL.md
```

This command may run again in a conversation that already joined. The restart
command resumes a lane and joins it in the same line. Join exactly as the first
time: reread the five files, because a retro may have changed them, and send
`JOIN` again, because the lead may be a fresh session with no roster.

With no lane given, take the lane the startup note named, if it named one. The
boundary hook already holds this session to that lane's paths, so joining
another would work one lane under another's boundary. When it named none, read
the charter's `## Lanes` and ask which one this session is.

If this session has already edited paths outside the lane it is taking, say so
before you start. That is an overlap the lead needs, not a detail to tidy away.
