---
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

/teamwork:form Split the billing rewrite into parallel lanes. This session
cannot run commands, so this is what it would tell you: `echo "$TEAMWORK_LANE"`
prints `api`, and `$TEAMWORK_ROOT` is `/work/shop/.teamwork`.

You are the `api` lane on a teamwork team, and you own `services/billing/**`.
The rewrite has grown. It splits cleanly into invoices, payments and webhooks,
each under its own directory, and none of the three waits on another. Form a
team inside my lane so three sessions can work them in parallel. Tell me what
you will do.
