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
- **One `member` agent serves every lane**, because the role file is looked up
  from `TEAMWORK_LANE` rather than from the agent's name. Generating an agent per
  lane would put a copy of the role in a second place.
- **`[T5]` compares globs by matching, never by truncating them at the first
  wildcard.** Truncation is simpler and was tried: it collapsed every
  leading-wildcard glob to the empty prefix, so two lanes owning `**/*.sql` and
  `**/*.css` failed a valid team while a real overlap against a literal path went
  unseen. Each glob is turned into a regex instead.
- **`[T5]` decides overlap by building a path from both globs at once, not by
  drawing one from either.** Drawing a path from one glob and testing it against
  the other proves containment and nothing else: `src/a*.py` and `src/*b.py`
  collide on every `src/a…b.py` and passed, because neither drawn path satisfied
  the other's literals. The unifier returns a concrete witness, and the witness is
  checked back against the same `glob_regex` the boundary hook enforces with, so
  a reported collision is one that can actually happen and the failure names the
  file.
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
  the lanes and the workspace, and `git worktree list` carries the
  rest, so a run whose every terminal is gone can still be brought back.
- **A lane is a terminal session a human starts, and there is no other kind.**
  Spawning lanes as in-process teammates was the easiest substrate and is
  removed. Such a lane inherits the lead's environment, which must never carry a
  lane name, and the lead's working directory, so the boundary hook can identify
  neither and allows every write. It also has no worktree and no branch, which is
  what a park re-derives a launch command from and what a finish merges. One kind
  of member is what makes enforcement, parking, resuming and finishing hold
  without a caveat about which substrate was chosen.
- **What a lane does inside itself is not the team's business.** A member may fan
  out to subagents, spawn teammates, or run a workflow. The hook reads the
  environment and the working directory, and a member passes both to everything
  it spawns, so its own agents are held to its own lane at no cost. Governing
  that too would buy nothing and would cost the fan-out the context budget
  depends on.
- **A lane is addressed by its session name, not by `--team-name` and
  `--agent-name`.** Those flags were the launch command and they never worked:
  with the platform's experimental agent-teams mode off they are accepted and
  ignored, and with it on the CLI exits with `--agent-id, --agent-name, and
  --team-name must all be provided together`, which a human starting a lane has
  no id to satisfy. Both states were reproduced against the installed CLI. The
  launch command is now `claude --agent teamwork:member`, which is a documented
  flag, and the human types `/rename <lane>` into each lane. The lane cannot do
  that for itself: `/rename` is a built-in command rather than a skill, so
  nothing a member can call invokes one, and a lane told to rename itself emits
  the text and stays under its old name.

- **The charter's `Workspace:` line replaced `Isolation:`, and has four values.**
  Worktree-or-shared-tree assumed one git repository: a project with a repository
  per component formed a team that could not be landed, and a project with no
  version control failed at the `.gitignore` step. The line also decides what
  `Owns` globs are relative to — each lane's own tree under worktrees, the
  directory holding them all otherwise. Anchoring at the enclosing repository
  instead made every multi-repo glob match every file. The hook still reads
  `Isolation:`, or a team formed under the old name loses its second lane rung
  and is not told.
- **The lead may hold one lane, when no other lane waits on it.** "The lead takes
  no lane" refused the integration-tester, deployer and documenter leads for no
  gain, and left the lead's paths owned by nobody, so `[T5]` proved nothing about
  them and every member could write them. What survives is the failure mode: a
  lead holding work in the critical path becomes the bottleneck. `lead` is now a
  meaningful lane name, because it is the one lane the hook lets write the team
  root, which `protocol.md` rule 5 already reserves to the lead.

- **The plugin is required only in the lead session.** Members are bound by the
  files, which is what lets a member be a session without the plugin, or a person.
- **The boundary hook fails open, never closed.** A hook that denied a write it
  could not attribute would stop the lead, stop every session that is not on a
  team, and break the plugin the first time lane resolution missed. An
  unidentified lane is an unprotected lane, and that is the price of never being
  the reason someone's unrelated session cannot write a file.
- **There is no `SessionEnd` branch in the hook.** Naming a lane's uncommitted
  work as the session exits is the obvious way to catch the third park condition,
  and it was shipped and then removed. The platform writes a `SessionEnd` hook's
  output only when the hook reports failure, so an exit-zero warning goes
  nowhere, and the only way to be seen was to exit non-zero and pose as a crash.
  A hook that fails open must not do that. The condition stays in the park
  procedure, where a member can act on it.
- **There is no `TeammateIdle` hook, because it could not be verified.** The
  event exists and carries `teammate_name` and `team_name`, which is exactly what
  a roster needs. `Agent({name: ...})` was not available in a headless session,
  so which session the event fires in was never observed. Shipping a write path
  into the team root on an assumption would break single-writer discipline
  silently, and the roster is the one file that is wrong for everyone the moment
  it is wrong at all.
- **A team lives on one filesystem; members never span machines.** Cross-machine
  coordination was offered and is removed. It cannot hold `protocol.md` rule 4,
  because no absolute path is shared, so `[T9]` failed for every member that was
  not on the machine that formed the team and the remedy was documented nowhere.
  Its transport was a second plugin, which broke the property that a member is
  bound by the files alone, and its sync was git, so a `RELOAD` meant "everyone
  pull" with nothing to make that happen. Resuming from a fresh clone is a
  different feature and it stays.
