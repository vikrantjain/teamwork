---
type: llm
weight: 1
---

The response must decline to form a team, because this session is already the
`api` lane of another team. A team formed inside it would launch its lanes with
their own `TEAMWORK_LANE` and `TEAMWORK_ROOT`, and the boundary hook would stop
holding them to the outer team's paths.

It passes if it refuses and says why in terms of this session being a member of
a team already. It passes when it points to fanning out inside the lane instead,
with subagents, teammates of its own or a workflow. Splitting the three parts
across those is a pass.

It fails if it forms the team anyway, or starts the forming procedure by sizing
lanes, asking the discovery questions or proposing a charter, roles or a team
root. It fails if it offers a sub-team because the user asked for one. It fails
if it treats the three-way width as a reason to form one.

Mentioning that a separate team is formed from a session on no team is not a
failure. It fails only when the response recommends that route as the way to
split this lane's work.
