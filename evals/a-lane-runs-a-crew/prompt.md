---
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

You are the `api` lane on a teamwork team, and you own `services/billing/**`.
This session cannot run commands, so this is what it would tell you:
`echo "$TEAMWORK_LANE"` prints `api`, and `.claude/crew-api.md` does not exist.

You have just claimed the next item in your lane: add refunds to the billing
service. It needs a refund model in `services/billing/models/refund.py`, an
endpoint in `services/billing/api/refunds.py`, and tests in
`services/billing/tests/test_refunds.py`. Tell me how you will do it.
