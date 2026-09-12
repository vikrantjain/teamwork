# teamwork — conventions

This plugin supplies the method for running several Claude Code sessions as one
team. The team mechanism is the platform's; the contracts, the sizing and the
improvement loop are this plugin's.

## Rules

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
- **The validator checks shape; the auditor agent checks judgement.** Never add a
  check to `validate_team.py` that needs to read for meaning, and never ask the
  auditor to re-report what a check already proved.
- **Nothing this plugin authors goes in the user's home folder.** Team roots live
  in the project, at a shared location, or at a path the user gave.
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

- **The team root is a project path, never `~/.claude/teams/`.** The platform's
  team directory is readable without a prompt and would have been convenient, but
  contracts that live outside the repo are not versioned with the code, not
  reviewable in a pull request, and do not travel with the project.
- **The platform's `~/.claude/tasks/` board is not a tracker rung.** It offers
  atomic claiming and reassignment on death, which no file board does. It is
  still refused: it lives in the home folder, it is deleted as items complete,
  and it is scoped to one team, so it is coordination rather than a record.
- **Lanes are partitioned before anyone starts, so claiming needs no atomicity.**
  This is why losing the platform board's atomic claim costs nothing.
- **Only the lead writes the team root.** Single-writer discipline: contract files
  having one author is what the retro assumes, and two members appending to
  `friction.md` at once would silently lose a line.
- **`conflicts.md` is a separate file from `protocol.md`.** Both are verbatim, but
  the conflict table is read when a conflict happens and the protocol is read at
  every startup. Merging them would put the rarely-needed half in the budget that
  is paid every turn.
- **One `member` agent serves every lane**, because the lane is the agent's name
  and the role file is looked up from it. Generating an agent per lane would put
  a copy of the role in a second place.
- **The plugin is required only in the lead session.** Members are bound by the
  files, which is what lets a member be a session without the plugin, a session
  on another machine, or a person.
