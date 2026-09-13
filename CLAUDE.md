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
- **`[T5]` compares globs by matching, never by truncating them at the first
  wildcard.** Truncation is simpler and was tried: it collapsed every
  leading-wildcard glob to the empty prefix, so two lanes owning `**/*.sql` and
  `**/*.css` failed a valid team while a real overlap against a literal path went
  unseen. Each glob is now turned into a regex and tested against a concrete path
  drawn from the other.
- **`decisions.md` is the one contract file pruned on a schedule.** Every other
  file is bounded by the remove-a-line-to-add-one rule, but this one gains a line
  at every retro. Left alone it reaches its budget and `[T1]` then blocks the
  retro that would have fixed it.
- **A park writes no new file into the team root.** A "where we are" snapshot was
  the obvious design and is refused: it duplicates the tracker, drifts from it the
  moment either changes, and is exactly the work log `[T3]` keeps out. The park
  procedure's job is to leave the tracker true, so resuming is an ordinary start.
- **Launch commands are re-derived at resume, never persisted.** Persisting them
  would pin a team to the terminals that formed it. The charter already carries
  the team name, the lanes and the isolation, and `git worktree list` carries the
  rest, so a run whose every terminal is gone can still be brought back.
- **The plugin is required only in the lead session.** Members are bound by the
  files, which is what lets a member be a session without the plugin, or a person.
- **A team lives on one filesystem; members never span machines.** Cross-machine
  coordination was offered and is removed. It cannot hold `protocol.md` rule 4,
  because no absolute path is shared, so `[T9]` failed for every member that was
  not on the machine that formed the team and the remedy was documented nowhere.
  Its transport was a second plugin, which broke the property that a member is
  bound by the files alone, and its sync was git, so a `RELOAD` meant "everyone
  pull" with nothing to make that happen. Resuming from a fresh clone is a
  different feature and it stays.
