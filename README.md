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
- **Gives every lane a boundary.** Each member owns disjoint paths, and a
  validator fails the team if two lanes claim the same one. Crossing a boundary
  is a message, never an edit.
- **Keeps work items in the project's own tracker** — GitHub issues, an existing
  `IMPLEMENTATION_PLAN.md`, or a file board. One store, so there is never a
  second place to look.
- **Improves its own rules.** Members file friction and keep working; a retro
  groups it by cause, reverts the last rule that failed, and makes the smallest
  edit that would have prevented each recurring cause. To add a line you must
  remove one, which is what makes it converge rather than accumulate.
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
| `skills/team-design/` | Lead side: sizing, team root, trackers, templates, retro, adoption |
| `skills/team-member/` | Member side: the procedure, the protocol, conflicts, context discipline |
| `agents/member.md` | One generic lane; finds its role by its own agent name |
| `agents/contract-auditor.md` | Fresh-context check that the contracts are still rules |
| `scripts/validate_team.py` | Nine structural checks over a team root |

## What a team looks like on disk

`/teamwork:form` writes a **team root** — one absolute path every member can
reach, inside the project or at a location you name. Never in your home folder.

```
.teamwork/
  protocol.md     the constitution: seven verbs, nine rules. Copied, never edited.
  conflicts.md    what to do when a conflict happens. Read then, not at startup.
  charter.md      this team's own law: lanes, shared paths, human gates, done.
  roles/<lane>.md Owns / Never / Hands off to / Done means.
  tracker.md      the one backend, with its create, claim and close commands.
  transport.md    how members address each other.
  decisions.md    settled choices, with the reasons, so retros stop reopening them.
  friction.md     what the rules cost. At its cap, a retro is due.
```

A member loads the protocol, the charter, its own role, the transport and the
tracker: about 160 lines. Every line budget exists to keep it there.

## Two rules that carry the rest

**Contracts never record what happened.** No dates, no checkboxes, no statuses,
no issue ids. `validate_team.py` fails on all of them, because a charter that
absorbs a work log stops being read, and unread rules are not rules.

**Lanes own disjoint paths.** The validator fails a team where two roles claim
one path, or where one role's glob contains another's. This is the collision that
loses work silently, and the only reliable time to catch it is before anyone
starts.

## Install

```
/plugin marketplace add vikrantjain/my-claude-plugins
/plugin install teamwork@my-claude-plugins
```

The plugin is needed in the session that forms or leads a team. Members need only
the files in the team root, so a member can be a Claude session without the
plugin, a session on another machine, or a person.

## Requirements

Python 3 for the validator, standard library only, no build step. `git` for
worktree isolation and for the team root in a multi-repo layout. `gh` only if you
want GitHub issues as the tracker.

Run the checks by hand at any time:

```
python3 scripts/validate_team.py <team root>
python3 scripts/test_validate_team.py
```

## License

MIT
