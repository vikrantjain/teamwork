# teamwork

Run several Claude Code sessions as a team on one goal — with rules each member
can actually follow, work items where the project already keeps them, and a
charter that gets smaller as it gets better.

## Why

Claude Code already ships the team *mechanism*: named teammates, per-teammate
mailboxes, cross-session messaging, idle notification, worktree isolation. What
it does not ship is a *method*. Nothing decides how many members a goal needs,
what each may and may not touch, or how those rules improve once the work exposes
their gaps.

Left to improvise, a team fails the same three ways every time. Two members edit
one file and neither notices until work is lost. The shared instructions grow
into a diary nobody reads. And the lead ends up holding every member's context,
becoming the bottleneck the team was formed to remove.

This plugin is the method. One sentence decides everything in it:

> **A contract is read before acting. A work item records what happened. Never
> let one become the other.**

## What it does

- **Sizes the team from the work**, not the goal. Team size is the width of the
  dependency graph, capped at four lanes. When the width is one it says so and
  declines to form a team.
- **Gives every lane a boundary, and enforces it.** Each member owns disjoint
  paths, and a validator fails the team if two lanes claim the same one. A hook
  then denies the write itself, so crossing a boundary fails instead of quietly
  overwriting another lane's work. A lane is a session you start, which is what
  makes the boundary identifiable.
- **Keeps work items in the project's own tracker** — GitHub issues, an existing
  `IMPLEMENTATION_PLAN.md`, or a file board. One store, so there is never a
  second place to look.
- **Improves its own rules.** Members file friction and keep working; a retro
  groups it by cause, reverts the last rule that failed, and makes the smallest
  edit that would have prevented each recurring cause. To add a line you must
  remove one, which is what makes it converge rather than accumulate.
- **Parks the team where it can be picked up.** A park stops every lane at a
  point the tracker fully describes: nothing claimed by a session that no longer
  exists, every blocked edge recorded, every tree clean or accounted for. A fresh
  set of sessions then resumes from the charter and the tracker alone, on this
  machine or on a clone that never saw the original run.
- **Lands the work when it is done.** Finishing checks the charter's stop
  condition, parks every lane, then tests each merge with `git merge-tree` and
  hands the merges and worktree removals to you. It never merges and never
  removes a worktree, because both destroy something the next turn cannot undo.
- **Adopts a team already running.** Sessions collaborating without contracts get
  their lanes read from what they have actually touched, overlaps reported, and a
  charter they ratify before it binds them.

## What's in it

| File | Role |
|---|---|
| `commands/form.md` | `/teamwork:form` — size the team and write the contracts |
| `commands/adopt.md` | `/teamwork:adopt` — put contracts around a running team |
| `commands/join.md` | `/teamwork:join` — this session takes a lane |
| `commands/status.md` | `/teamwork:status` — one screen of live state |
| `commands/retro.md` | `/teamwork:retro` — improve the rules from friction |
| `commands/park.md` | `/teamwork:park` — stop where a fresh session can resume |
| `commands/resume.md` | `/teamwork:resume` — bring a parked team back |
| `commands/finish.md` | `/teamwork:finish` — land the work and disband |
| `skills/team-design/` | Lead side: sizing, team root, trackers, transport, templates, leading, parking, retro, adoption |
| `skills/team-member/` | Member side: the procedure, the protocol, conflicts, context discipline |
| `agents/member.md` | One generic lane; finds its role from `TEAMWORK_LANE` |
| `agents/contract-auditor.md` | Fresh-context check that the contracts are still rules |
| `scripts/validate_team.py` | Twelve structural checks over a team root |
| `scripts/teamwork_hook.py` | Denies an out-of-lane write; re-states the lane after a compaction |
| `hooks/hooks.json` | Which events that script runs on |

## What a team looks like on disk

`/teamwork:form` writes a **team root** — one absolute path every member can
reach, inside the project or at a location you name. Never in your home folder.

```
.teamwork/
  protocol.md     the constitution: eight verbs, nine rules. Copied, never edited.
  conflicts.md    what to do when a conflict happens. Read then, not at startup.
  charter.md      this team's own law: lanes, shared paths, human gates, done.
  roles/<lane>.md Owns / Never / Hands off to / Done means.
  tracker.md      the one backend, with its create, claim and close commands.
  transport.md    the one substrate, and how to address a lane.
  decisions.md    settled choices, with the reasons, so retros stop reopening them.
  backlog.md      the file board, and only when the project has no tracker.
  friction.md     what the rules cost. At its cap, a retro is due.
  roster.md       which lane is up, where, and whether it has acked.
```

Everything down to `backlog.md` is committed, because a contract that is not
versioned with the code cannot be reviewed in a pull request. The last two are
gitignored: they are this run's state, not the team's law.

A member loads the protocol, the charter, its own role, the transport and the
tracker: about 160 lines. Every line budget exists to keep it there.

## Two rules that carry the rest

**Contracts never record what happened.** No dates, no checkboxes, no statuses,
no issue ids. `validate_team.py` fails on all of them, because a charter that
absorbs a work log stops being read, and unread rules are not rules.

**Lanes own disjoint paths.** The validator fails a team where two roles claim
one path, where one role's glob contains another's, or where two globs merely
intersect — `src/a*.py` and `src/*b.py` both reach `src/ab.py`, and neither
contains the other. It names the file they collide on. This is the collision that
loses work silently, and the cheapest time to catch it is before anyone starts.

Declaring a boundary is not enforcing one, so a `PreToolUse` hook denies a write
to a path another lane owns and tells the member to `ASK` its owner instead. It
identifies the lane from `TEAMWORK_LANE`, which every lane's launch command sets,
and failing that from the working directory under one worktree per lane. A
session it cannot identify is allowed every write, because a hook that blocked
what it could not attribute would stop the lead and every session that is not on
a team at all.

A lane inherits its own enforcement. The hook reads the environment and the
working directory, and a member passes both to every agent it spawns, so a lane
can fan out to subagents as widely as its work needs and each of them is held to
that lane's paths. What a lane does inside itself is its own business.

A lane is **addressed by its session's own name**, which defaults to its working
directory, so every lane renames itself to its lane name at startup. The flags
that look as though they would do this do not: outside the platform's
experimental agent-teams mode `--team-name` and `--agent-name` are accepted and
ignored, and inside it the CLI refuses to start unless an `--agent-id` is passed
with them, which a human starting a lane by hand has no way to supply. So the
launch command carries neither, and `/rename <lane>` is what makes a lane
reachable under the name the charter uses.

The hook does not see writes made through `Bash`: parsing a shell command for the
file it truncates is a losing game, and a check that caught nine tenths of them
would be trusted for the tenth. That gap lands hardest on shared paths, which are
usually written by a command rather than an edit — a lockfile by the package
manager, a schema by a migration tool. So the charter gives every shared path an
owner and every other lane a `Never` line for it, and on that one class of path
the `Never` line is the whole of the enforcement.

## Install

This repo **is its own plugin marketplace**, so it installs with nothing set up
on your side:

```
/plugin marketplace add vikrantjain/teamwork
/plugin install teamwork@teamwork
```

`teamwork@teamwork` is `<plugin>@<marketplace>`: you add the **repo**, and it
registers under the marketplace name `teamwork`, which contains the plugin of the
same name.

If you already have the `my-claude-plugins` marketplace added, install from there
instead and skip the extra marketplace entry:

```
/plugin marketplace update my-claude-plugins
/plugin install teamwork@my-claude-plugins
```

The plugin is needed in the session that forms or leads a team. Members need only
the files in the team root, so a member can be a Claude session without the
plugin, or a person.

## Requirements

Python 3 for the validator and the hook, standard library only, no build step.
`git` for worktree isolation and for the team root in a multi-repo layout. `gh`
only if you want GitHub issues as the tracker.

Two sibling plugins are used when they are installed and skipped when they are
not: `backlog-refiner`, whose `IMPLEMENTATION_PLAN.md` is the second tracker
rung, and `github-automation`, whose issue lifecycle the first rung reuses rather
than inventing labels of its own.

Run the checks by hand at any time:

```
python3 scripts/validate_team.py <team root>
python3 scripts/test_validate_team.py
python3 scripts/test_teamwork_hook.py
```

The behaviour that is prose rather than code has its own suite. These four cases
are read-only, and they cover the claims no unit test can reach: that a serial
goal is refused, that lanes come from the dependency graph, that a member routes
a cross-lane fix instead of making it, and that a cause appearing once produces
no rule.

```
claude plugin eval .
```

## License

MIT
