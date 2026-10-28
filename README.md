# teamwork

A Claude Code plugin that runs several Claude Code sessions as one team on one
goal. It sizes the team from the work, gives each session a set of paths it
owns, and denies a session's write to a path another session owns.

It is for anyone running two or more Claude Code sessions in parallel on one
project, and the work does not have to be software. Claude Code already lets
sessions on one machine message each other by name. It does not decide how many
sessions a goal needs, what each may touch, or how those rules improve. Left to
improvise, a team fails in three ways. Two sessions edit one file, and neither
notices until work is lost. The shared instructions grow into a diary nobody
reads. The lead ends up holding every session's context and becomes the
bottleneck. This plugin is the method that prevents all three.

The plugin is pre-1.0. A minor version may change what a team root must
contain. A team formed under an older version can then fail validation until its
lead updates it.

## What it does

- **Sizes the team from the dependency graph of the work**, never from how big
  the goal feels, with four lanes as the default cap. When only one piece can
  progress at a time, it says one session is right and forms no team.
- **Starts from the plan you already have.** It reads the project's own plan,
  asks what the plan leaves open, and proposes a team. Nothing is written until
  you accept it.
- **Gives every lane disjoint paths, and enforces them.** A validator fails the
  team when two lanes' globs reach one path. A hook then denies a write to
  another lane's path and tells the session to ask that lane instead.
- **Keeps work items in the project's own tracker**: GitHub issues, a plan file
  that tracks itself, or a file board when the project has neither.
- **Keeps the rules small enough to reload.** A member reloads five files on
  every context load, 165 lines at most. The validator fails a contract carrying
  a date, a checkbox or an issue id, so the rules cannot turn into a work log.
- **Improves its own rules.** Members report friction as they work. A retro turns
  each recurring cause into the smallest edit that prevents it, and removes a
  line for every line it adds.
- **Parks and resumes.** A park stops every lane at a point the tracker fully
  describes, so a fresh set of sessions resumes from the files alone.
- **Hands the merge to you.** Finishing tests every lane's merge and prints the
  commands. It never merges and never removes a worktree.
- **Gives the lead a status line.** It names a lane that dropped out, a retro
  that is due, or contracts that fail validation.

It works with one repository, with a repository per component, or with no
version control at all.

It has three limits. The hook cannot see a write made through `Bash`, such as a
regenerated lockfile, so the contracts give each such path one owner and every
other lane a rule against it. A session the hook cannot identify as a lane is
allowed every write; a lane started from its printed command is always
identified. Every session runs on one machine.

## Requirements

- Claude Code with cross-session messaging. It is tested against 2.1.312.
- Python 3, standard library only, for the validator and the hook.
- Optional: `git`, for one worktree per lane and for finishing, and `gh`, for
  GitHub issues as the tracker.

The plugin is required in the session that forms and leads the team. Install it
in every member as well. The boundary hook ships with the plugin, so a member
without it is bound by the contracts and checked by nothing.

## Quickstart

This repository is its own plugin marketplace:

```
/plugin marketplace add vikrantjain/teamwork
/plugin install teamwork@teamwork
```

With the `my-claude-plugins` marketplace already added, install
`teamwork@my-claude-plugins` instead.

Then, in the session that will lead:

```
/teamwork:form add rate limiting, search and an audit log
```

It proposes the lanes, the paths each owns and the actions that must stop and
ask you, then waits for you to accept. When the work is serial it says one
session is right and stops there. Once you accept, it writes the team root and
validates it:

```
ok      all checks passed
```

It ends by printing two commands per lane, one to start the lane and one to
restart it. Paste each lane's start command into a terminal of its own.

## Commands

| Command | What it does |
|---|---|
| `/teamwork:form <goal>` | Size the team from the work and write its contracts |
| `/teamwork:adopt` | Put contracts around sessions already working together |
| `/teamwork:join <lane>` | Take a lane in this session; each launch command runs it |
| `/teamwork:status` | One screen: who is up, what each lane holds, what is blocked |
| `/teamwork:retro` | Improve the rules from the friction they caused |
| `/teamwork:park` | Stop where a fresh set of sessions can resume |
| `/teamwork:resume <team root>` | Bring a parked team back and print each lane's commands |
| `/teamwork:finish` | Check the stop condition, park, and hand over the merge |
| `/team-board` | Open the lead's board in a pane |

## How it works

The method lives in two skills. The lead's side is
[`skills/team-design/SKILL.md`](skills/team-design/SKILL.md), with one reference
per step under [`skills/team-design/references/`](skills/team-design/references/).
A member's side is [`skills/team-member/SKILL.md`](skills/team-member/SKILL.md).
[`team-root.md`](skills/team-design/references/team-root.md) lists the files a
team root holds. The boundary hook is described at the top of
[`scripts/teamwork_hook.py`](scripts/teamwork_hook.py), and every validator check
at the top of [`scripts/validate_team.py`](scripts/validate_team.py).
[`docs/intent.md`](docs/intent.md) says what the plugin is for.

## Support

Report bugs and ask questions in the
[issue tracker](https://github.com/vikrantjain/teamwork/issues). Vikrant Jain
maintains the plugin. [`CONTRIBUTING.md`](CONTRIBUTING.md) lists the checks a
change must pass. The plugin is MIT licensed; see [`LICENSE`](LICENSE).
