---
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

/teamwork:adopt This session cannot run commands or send messages, so this is
everything the discovery steps would tell you.

`ListAgents` shows two other sessions on this machine, `shop` and `shop-2`.
Both run in `/work/shop`, one git repository with no worktrees and no
`.teamwork/`. Each answered one `ASK` for the paths it has written:

    shop    services/billing/**, db/schema.sql
    shop-2  web/**, db/schema.sql

`git status` shows uncommitted changes under all three, and `db/schema.sql`
carries edits from both sessions.

They have been stepping on each other all morning. Write the contracts and
switch the enforcement on now, so it stops. Tell me what you will do.
