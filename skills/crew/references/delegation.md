# Handing work to agents

A session hands a part to a crew member in one of three ways. What follows is
how the installed CLI behaves, verified against Claude Code 2.1.316. None of it
can be derived from the principle, which is why it is written down.

## Subagents

- **A subagent inherits its session's environment and working directory.** The
  boundary hook reads both, so a lane's subagents are held to the lane's paths
  at no cost.
- **A subagent has the `Agent` tool**, so a crew member can start agents of its
  own.
- **A subagent has `SendMessage` and no `ListAgents`.** A message it sends to
  another session goes out under its session's name. The answer is delivered to
  the session's main conversation, not to the subagent.

## Teammates

- **Teammates exist only in agent-teams mode**, which
  `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` or `--agent-teams` turns on. A lane's
  launch command sets neither, so a lane started from it has no teammates.
- **A teammate cannot start teammates of its own**, and an in-process teammate
  cannot start a background agent.
- **Whether a teammate inherits its session's environment is not verified.**
  Until it is, a lane cannot count on the boundary hook holding a teammate to
  the lane's paths.

## Workflows

- **A workflow starts only when the session's human asks for one**, so a crew
  cannot drift into one.
- **A workflow reports when it finishes, not within the turn.** A lane that
  answers `PARK` with one still running has work held nowhere, and stopping the
  session takes it. That is the third park condition, and
  `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/parking.md` names it.
