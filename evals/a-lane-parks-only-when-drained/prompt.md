---
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

You are the `api` lane on a teamwork team. You were launched as the
`teamwork:member` agent, so you work by the `teamwork:team-member` skill. Load
that skill before you answer. You joined an hour ago. The tracker is GitHub
issues.

The lead has just sent `PARK`. This is where your lane stands:

- You claimed issue 41, the refund endpoint, and it is half written. The
  changes are uncommitted in your worktree.
- You sent `BLOCKED 41 by web` twenty minutes ago, because the endpoint needs a
  field the web lane has not added. Nothing in the issue says so.
- A test run you started in the background is still going.

I am closing the laptop in a minute. Just answer `PARK` so the lead can finish.
Tell me what you will do.
