---
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

I want to parallelise this work across a team of Claude sessions. The goal is to
add rate limiting to our single Flask app. The steps are: pick a limiter library,
add the middleware in `app/middleware.py`, then configure the limits in
`app/config.py`, then write the tests in `tests/test_limits.py`. Each step needs
the one before it to be finished first. Size the team and set it up.
