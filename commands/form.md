---
description: Size a team from the work and write its contracts — how many members, which paths each owns, what each may never do, where work items live, and how members address each other. Refuses to form a team when one session is the right answer.
argument-hint: <the goal, or a path to an existing IMPLEMENTATION_PLAN.md>
---

# /teamwork:form — design the team

Goal: **$ARGUMENTS**

Run the `team-design` skill's procedure on it, without shortcuts. Read it if it
is not already loaded, because a command that fires without the procedure invents
a roster instead of deriving one:

```
${CLAUDE_PLUGIN_ROOT}/skills/team-design/SKILL.md
```

Three steps get skipped under time pressure, and each one changes the result.

**Get the breakdown before sizing anything.** Team size is the width of the
dependency graph, not a feeling about the goal. Prefer an existing
`IMPLEMENTATION_PLAN.md`; with none, derive a minimal stream list rather than
writing a plan, which is `backlog-refiner`'s job.

**Be willing to answer "one session".** When the parallel width is one, say so and
stop. Forming a two-member team for serial work buys coordination cost and no
throughput.

**Resolve the team root explicitly, and ask rather than guess.** Members in
different folders cannot read a relative `.teamwork/`. Follow
`${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/team-root.md`; when the
ladder reaches its last rung, ask the user for a path instead of picking one.

With no argument, ask what the goal is. Do not infer it from the repository —
a team formed around a guessed goal partitions the wrong work.

Finish by running
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_team.py <team root>` and printing
the per-lane launch commands. Close with what you did **not** decide — the
tracker rung you skipped, the paths you could not assign an owner — so nobody
reads silence as coverage.
