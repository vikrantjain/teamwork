---
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Size a team for this goal, and tell me the lanes and what each owns. Do not
write any files yet.

We are adding a usage report to our product. Two streams have to happen, and
both can start today.

The service under `api/`: a `/reports/usage` endpoint, the query behind it, a
cache for the slow aggregates, and their tests.

The console under `web/reports/`: the report page, its date-range filter, a CSV
download button, and the component tests for all three. The page calls the new
endpoint, and the web side will build against a mock until the endpoint is up.

Nobody has written down what the endpoint returns. Each side has read the same
ticket and will work from that.
