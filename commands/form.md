---
description: Size a team from the work and write its contracts — how many members, which paths each owns, what each may never do, where work items live, and how members address each other. Refuses to form a team when one session is the right answer.
argument-hint: <the goal, or a path to a plan the project already has>
---

# /teamwork:form — design the team

Goal: **$ARGUMENTS**

Run the `team-design` skill's procedure on it, without shortcuts. Read it if it
is not already loaded, because a command that fires without the procedure invents
a roster instead of deriving one:

```
${CLAUDE_PLUGIN_ROOT}/skills/team-design/SKILL.md
```

Four steps get skipped under time pressure, and each one changes the result.

**Get the breakdown before sizing anything.** Team size is the width of the
dependency graph, not a feeling about the goal. Use the plan the project already
has, under whatever name it carries, and ask whatever it leaves unanswered from
the five questions in
`${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/discovery.md`, in one
message. A plan lists the pieces. It does not say what two people must never
touch at once, or what has to stop and ask you, so finding one shortens the
interview and never replaces it. Never write a plan to justify a roster: it is a
second source of truth that nobody maintains.

**Be willing to answer "one session".** When the parallel width is one, say so and
stop. Forming a two-member team for serial work buys coordination cost and no
throughput.

**Resolve the team root explicitly, and ask rather than guess.** Members in
different folders cannot read a relative `.teamwork/`. Follow
`${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/team-root.md`; when the
ladder reaches its last rung, ask the user for a path instead of picking one.
Write the `Workspace root:` line in the same pass, naming the directory every
lane's `Owns` globs are read against. Omit that line under one worktree per lane,
where each lane reads its globs against its own tree and the validator fails a
charter naming an anchor nothing uses. That last rung is exactly where it stops
being the team root's parent, and a boundary hook reading globs against the wrong
directory allows every write with nothing said.

**Propose before you write.** The lanes, the paths, the workspace, the tracker
and the gates go to the human first, and nothing lands in the team root until
they accept. A boundary the human never agreed to is one that denies a write
somebody needed, hours later.

With no argument, ask what the goal is. Do not infer it from the project — a team
formed around a guessed goal partitions the wrong work.

Finish by running
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_team.py <team root>` and printing
the per-lane launch commands. Close with what you did **not** decide — the
tracker rung you skipped, the paths you could not assign an owner — so nobody
reads silence as coverage.
