# teamwork

Run several Claude Code sessions as a team on one goal — with rules each member
can actually follow, work items where the project already keeps them, and a
charter that gets smaller as it gets better. One repository, several
repositories, or no version control at all; software or not.

## Why

Claude Code already ships the team *mechanism*: cross-session messaging, idle
notification, worktree isolation, a name per session. What it does not ship is a
*method*. Nothing decides how many members a goal needs, what each may and may
not touch, or how those rules improve once the work exposes their gaps.

Left to improvise, a team fails the same three ways every time. Two members edit
one file and neither notices until work is lost. The shared instructions grow
into a diary nobody reads. And the lead ends up holding every member's context,
becoming the bottleneck the team was formed to remove.

This plugin is the method. One sentence decides everything in it:

> **A contract is read before acting. A work item records what happened. Never
> let one become the other.**

## Install

This repo **is its own plugin marketplace**, so it installs with nothing set up
on your side:

```
/plugin marketplace add vikrantjain/teamwork
/plugin install teamwork@teamwork
```

`teamwork@teamwork` is `<plugin>@<marketplace>`. You add the **repo**, which
registers under the marketplace name `teamwork`, and it holds the plugin of the
same name.

If you already have the `my-claude-plugins` marketplace added, install from
there instead and skip the extra marketplace entry:

```
/plugin marketplace update my-claude-plugins
/plugin install teamwork@my-claude-plugins
```

The plugin is needed in the session that forms or leads a team. Members are
bound by the files in the team root, so a member can be a Claude session without
the plugin, or a person.

## A run, end to end

In the session that will lead:

```
/teamwork:form add rate limiting, search and an audit log
```

It gets the breakdown, sizes the team from the dependency graph, writes the team
root, runs the validator, and prints one launch command per lane:

```
TEAMWORK_LANE=api TEAMWORK_ROOT=/repo/.teamwork claude --agent teamwork:member
```

Open a terminal per lane and run its command. The two variables are what let the
boundary hook tell which lane the session is; a lane started without them runs
unenforced. A lane whose working directory is outside the team root gets
`--add-dir <team root>` as well.

Then type two lines into each lane:

```
/rename api
/teamwork:join api
```

`/rename` is what makes the lane addressable. A session is addressed by its own
name, which defaults to its working directory, so under one shared tree every
lane otherwise answers to the same name and a message reaches whichever the
platform picks first. The lane cannot do it for itself: `/rename` is a built-in
command rather than a skill, so nothing a member can call invokes one, and a
lane told to rename itself emits the text and stays under its old name.

Each lane then reads its five files, announces itself to the lead, and works its
own paths. While the run is live the lead has `/teamwork:status` for one screen
of state and `/teamwork:retro` to turn the friction the rules caused into better
rules. It ends at `/teamwork:finish`, or at `/teamwork:park` when it has to stop
early and be picked up later.

`/teamwork:adopt` is the other way in, for sessions already collaborating
without contracts.

## What it does

- **Starts from the work you already have.** It reads the project's own plan
  under whatever name it carries, and when there is none it asks five questions
  and proposes a structure you amend before anything is written.
- **Sizes the team from that**, not from the goal. Team size is the width of the
  dependency graph, capped at four lanes. When the width is one it says so and
  declines to form a team.
- **Gives every lane a boundary, and enforces it.** Each member owns disjoint
  paths, and a validator fails the team if two lanes claim the same one. A hook
  then denies the write itself, so crossing a boundary fails instead of quietly
  overwriting another lane's work. A lane is a session you start, which is what
  makes the boundary identifiable.
- **Keeps work items in the project's own tracker** — GitHub issues, a plan file
  that already tracks itself, or a file board beside the contracts. One store, so
  there is never a second place to look.
- **Fits the project rather than assuming one.** The charter's `Workspace:` line
  is one shared tree, one worktree per lane, separate repositories or separate
  directories, and everything downstream of it — where the team root goes, what
  `Owns` globs are relative to, what finishing has to merge — follows from that
  one line. Git is used where it exists and never required.
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
  condition, parks every lane, then lands the work the way the workspace says it
  is separated: merges tested with `git merge-tree` and handed to you where there
  are branches, a report of what sits where when there are not. It never merges
  and never removes a worktree, because both destroy something the next turn
  cannot undo.
- **Lets the lead work when nothing waits on it.** A lead may hold one downstream
  lane — integration, deployment, documentation, review — with a role file and a
  boundary like any other. It may not hold work another lane is waiting for.
- **Adopts a team already running.** Sessions collaborating without contracts get
  their lanes read from what they have actually touched, overlaps reported, and a
  charter they ratify before it binds them.

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

Everything down to `backlog.md` is committed when the project is under version
control, because a contract that is not versioned with the code cannot be
reviewed in a pull request. The last two are gitignored: they are this run's
state, not the team's law. With no version control the same files still bind
every member, because a member reads them by absolute path.

A member loads the protocol, the charter, its own role, the transport and the
tracker. That is 165 lines with every budget spent to its ceiling, and fewer in
practice. The budgets exist to keep it there.

## Two rules that carry the rest

**Contracts never record what happened.** No dates, no checkboxes, no statuses,
no issue ids. `validate_team.py` fails on all of them, because a charter that
absorbs a work log stops being read, and unread rules are not rules.

**Lanes own disjoint paths.** This is the floor everything else stands on, and it
needs files, not git. The validator fails a team where two roles claim one path,
where one role's glob contains another's, or where two globs merely intersect — `src/a*.py` and `src/*b.py` both reach `src/ab.py`, and neither
contains the other. It names the file they collide on. This is the collision that
loses work silently, and the cheapest time to catch it is before anyone starts.

## How the boundary is enforced

Declaring a boundary is not enforcing one, so a `PreToolUse` hook denies the
write. A member reaching for a path another lane owns is refused and told to
`ASK` its owner. A member reaching for the team root is refused and told that
contracts change at a retro and nowhere else. The lead's own lane is the one
exception there, because protocol rule 5 gives it that file to write.

Paths are read relative to the workspace: each lane's own tree under one worktree
per lane, and the directory holding them all under the other three. The hook
identifies the lane from `TEAMWORK_LANE`, which every launch command sets, and
failing that from the working directory's own name under one worktree per lane. A session it cannot identify is allowed every write, because a hook
that blocked what it could not attribute would stop the lead and every session
not on a team at all. It finds the team root the way a member must: the variable
first, then the **main** worktree's copy, never the lane's own checkout of one,
which diverges the moment a retro commits on another branch.

A lane inherits its own enforcement. The hook reads the environment and the
working directory, and a member passes both to every agent it spawns, so a lane
can fan out to subagents as widely as its work needs and each of them is held to
that lane's paths. What a lane does inside itself is its own business.

The hook does not see writes made through `Bash`: parsing a shell command for the
file it truncates is a losing game, and a check that caught nine tenths of them
would be trusted for the tenth. That gap lands hardest on shared paths, which are
usually written by a command rather than an edit — a lockfile by the package
manager, a schema by a migration tool. So the charter gives every shared path an
owner and every other lane a `Never` line for it, and on that one class of path
the `Never` line is the whole of the enforcement.

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
| `skills/team-design/` | Lead side: discovery, sizing, team root, trackers, transport, templates, leading, parking, retro, adoption |
| `skills/team-member/` | Member side: the procedure, the protocol, conflicts, context discipline |
| `agents/member.md` | One generic lane; finds its role from `TEAMWORK_LANE` |
| `agents/contract-auditor.md` | Fresh-context check that the contracts are still rules |
| `scripts/validate_team.py` | Thirteen structural checks over a team root |
| `scripts/teamwork_hook.py` | Denies an out-of-lane write; re-states the lane after a compaction |
| `hooks/hooks.json` | Which events that script runs on |

## Requirements

Python 3 for the validator and the hook, standard library only, no build step.

Nothing else is required. `git` is used when the project has it — for one
worktree per lane, for resolving the team root from the main worktree, and for
the merges finishing hands over — and every one of those has a path that works
without it. `gh` only if you want GitHub issues as the tracker.

## Checks

```
python3 scripts/validate_team.py <team root>   # one team root
python3 scripts/test_validate_team.py          # the validator
python3 scripts/test_teamwork_hook.py          # the hook
claude plugin validate .                       # the manifests
```

Leave `--strict` off that last one. It flags `CLAUDE.md` at the repository root
as plugin context that will not load, which is true and is not a problem: the
file is this repository's conventions for people working on the plugin.

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
