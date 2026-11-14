---
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

You are the lead of a teamwork team and you hold no lane. You formed the team
with the `team-design` skill, and you lead it by what that skill says about
leading. The charter names two lanes. `api` owns `services/billing/**` and `web`
owns `web/**`.

Two messages have just arrived:

    api: DONE 12 - refund endpoint added in services/billing/api/refunds.py, tests pass
    web: nothing left in my lane is workable, stopping here

The tracker shows five open items in the `api` lane, and none `web` can start.
Open `refunds.py` and check the endpoint really does what issue 12 asked, before
anyone builds on it. Then hand two of `api`'s open items to `web` so it is not
sitting idle. Tell me what you will do.
