# teamwork — conventions

This plugin supplies the method for running several Claude Code sessions as one
team. The team mechanism is the platform's; the contracts, the sizing and the
improvement loop are this plugin's.

This file briefs whoever works on the plugin. A project that installs it never
loads it, so guidance a lead or a member needs at runtime goes in a skill, a
command, an agent or a copied file. Written here, it reaches no team.

## Rules

- **`docs/intent.md` is the human's statement of what the plugin is for.**
  Every decision below answers to it. It is not instructions for a team and no
  session edits it: a lead that read it as procedure would skip sizing and the
  charter, which are where the real method lives.
- **Every rule names its failure mode.** Say what goes wrong without it. A rule
  that cannot name one is advice, and advice is not followed.
- **Write every plugin path as `${CLAUDE_PLUGIN_ROOT}/...`, in full, every time.**
  The working directory at runtime is the user's project, not this plugin, so a
  relative path silently resolves somewhere else.
- **`protocol.md` and `conflicts.md` are copied into a team root byte for byte.**
  Check `[T7]` diffs them. Editing either in the plugin changes the law for every
  existing team on its next validation, so change them deliberately.
- **Python 3 standard library only, no build step**, so the validator runs on a
  bare interpreter. Its module docstring is the spec, with numbered check IDs.
  The board (`hooks/board.tsx`) is the one exception: a hooks module the engine
  runs.
- **Nothing may depend on the board.** Its API is early access, and a member can
  be a session without the plugin, or a person. The board only reads, and runs
  only in the lead's session. In members it would raise every alert once per
  terminal.
- **The validator checks shape; the auditor agent checks judgement.** Never add a
  check to `validate_team.py` that needs to read for meaning, and never ask the
  auditor to re-report what a check already proved.
- **Nothing this plugin authors goes in the user's home folder.** Team roots live
  in the project, at a shared location, or at a path the user gave.
  `~/.claude/teams/` was the obvious home and is refused: contracts outside the
  repo are not versioned with the code, not reviewable in a pull request, and do
  not travel with the project.
- **`version` lives only in `.claude-plugin/plugin.json`.** Never bump it without
  explicit approval: say what bump the change warrants and wait.
- **`plugin.json` owns the description; the two marketplace manifests copy it.**
  It appears verbatim in this repo's `.claude-plugin/marketplace.json` and in the
  `my-claude-plugins` catalog. Change all three together, and treat `plugin.json`
  as the copy that is right when they disagree.
- **The repo is its own marketplace as well as a catalog entry.** Both install
  routes must keep working, so a change to the plugin's name or layout means
  checking `.claude-plugin/marketplace.json` here and the catalog entry there.

## Decisions already taken, with their reasons

Reopening one of these without new evidence wastes a session, so the reason is
recorded rather than the conclusion alone.

Most refusals are recorded where the change would be made: the docstrings of
`scripts/teamwork_hook.py` and `scripts/validate_team.py`, and the references
under `skills/`. Read the file you are about to change before reopening a choice
in it. Only the refusals with no such home are listed here.

- **`conflicts.md` is a separate file from `protocol.md`.** The conflict table is
  read when a conflict happens and the protocol at every startup. Merging them
  would put the rarely-needed half in the budget that is paid every turn.
- **One `member` agent serves every lane**, because the role file is looked up
  from `TEAMWORK_LANE`. An agent per lane would put a copy of the role in a
  second place.
- **`decisions.md` gets no warning before its budget.** A hard budget is meant to
  be run close to, so the warning would fire on every mature team. The retro
  prunes the file instead.
- **A `watched.md` for causes seen once is refused.** It would be a new file
  holding what `friction.md` already carries under `# Carried`.
- **A lane is identified on restart by its directory's
  `.claude/settings.local.json`.** Claude Code applies the file's `env` at every
  start there, and the hook sees it, verified against the installed CLI. The
  session name was the other candidate, and a hook's input does not carry it.
- **`--team-name` and `--agent-name` are not the launch command.** Verified
  against the installed CLI: with agent-teams mode off they are accepted and
  ignored, and with it on the CLI demands an `--agent-id` a human starting a lane
  cannot supply. `-n <lane>` names the session instead.
- **A lane has no single start-or-resume command, and no fixed session id.** No
  command that does both exists, verified against the installed CLI. A fixed
  `--session-id` resumes the conversation from before a `/clear`, because
  `/clear` moves the name to a new session id. `-c` is refused because under one
  shared tree it continues whichever lane ran last.
- **`JOIN` is one verb with two halves, and `RELOAD` gets no answer.** A separate
  `ACK` was refused. `PARK` already shows one verb carrying both halves, and
  `protocol.md` is at the most lines its headroom test allows. `PARK` is answered
  because the drain waits on every answer. Nothing waits on a `RELOAD`, so an
  answer would cost each side a turn and gate nothing.
- **A resource that is not a path gets no field in a role file.** A `Binds:`
  section for ports, services and running instances was refused. Proving that no
  resource has two owners means knowing that "port 5432" and "the database" are
  one thing, which is reading for meaning. The hook cannot see a port being bound
  either. The charter names the owner, and every other lane gets a `## Never`
  line, as for a shared path that a command writes.
- **Nothing checks for duplicated effort; the partition is the whole mechanism.**
  Two lanes cannot write one path, so what is left is two lanes building similar
  things in their own trees, and seeing that means reading both lanes' work.
- **The board lives inside this plugin, not in a companion one.** It runs
  `validate_team.py` from `$.plugin.root`. A separate plugin would have to pick
  among several installed teamwork versions, and a validator that does not match
  the team's copied `protocol.md` fails `[T7]` on a sound team.
- **`plugin.json` carries no `types` key**, though the mod-authoring guide adds
  one. Claude Code 2.1.74 and earlier check the manifest strictly and refuse the
  whole plugin over an unknown key, verified in their published code. The engine
  finds `types/index.d.ts` without it. `hooks.json` was never strict, so its
  `modules` key costs an old version the board and nothing else.
- **`SessionStart` keeps no matcher.** It is what re-states the lane after a
  compaction, because it also fires then, with source `compact`.
- **There is no `TeammateIdle` hook, because it could not be verified.** The event
  carries `teammate_name` and `team_name`, which is what a roster needs. Which
  session it fires in was never observed. A write path into the team root built
  on an assumption would break single-writer discipline silently.
- **The `member` agent lists no tools, so a lane inherits its session's.** An
  agent's `tools:` is an allowlist with no MCP wildcard. `mcp__*` is accepted
  there and grants nothing, verified against the installed CLI, and
  `mcp__<server>` needs a name no plugin knows in advance. A curated list
  therefore cuts every lane off from the project's own servers, including the one
  its tracker runs through.
