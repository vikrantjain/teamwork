---
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

You are the `api` lane on a teamwork team, and you own `services/billing/**`.
This session cannot run commands, so this is what it would tell you:
`echo "$TEAMWORK_LANE"` prints `api`, and `.claude/crew-api.md` holds this:

```
# Crew: api

- model-builder: writes services/billing/models/**
- endpoint-builder: writes services/billing/api/**
- test-writer: writes services/billing/tests/**
- checker: writes nothing; checks each builder's part and the tests
```

This crew did your last item, which added refunds. The checker sent the model
builder and the endpoint builder back four times between them. Each time one of
them changed the refund fields, the other's part broke where the two meet.

You have just claimed the next item in your lane: add a `currency` field to the
invoice model in `services/billing/models/invoice.py`, and return it from the
existing endpoint in `services/billing/api/invoices.py`. The tests in
`services/billing/tests/test_invoices.py` need one assertion for it. Tell me how
you will do it.
