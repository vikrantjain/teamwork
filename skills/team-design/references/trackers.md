# Choosing one work-item backend

Tasks and bugs found while working are recorded where the project already keeps
them. Pick **one** backend and write it into `tracker.md`. One store, because two
means two places to look, and an item in the place nobody checks is a lost item.

## The ladder, first match wins

1. **The project's own issue tracker**, when one is reachable. GitHub issues when
   `gh auth status` succeeds and a remote exists — reuse `github-automation`'s
   epic, feature, story and bug lifecycle rather than inventing labels. Likewise
   any other tracker the project already uses.
2. **`IMPLEMENTATION_PLAN.md`**, when `backlog-refiner` produced one. It is
   self-tracking by design, so use its own pickability and roll-up rules as
   written. Do not restate them in the charter.
3. **`<team root>/backlog.md`**, a minimal fallback beside the contracts. One
   item per line: id, one-line outcome, owning lane, and what done means.

## What is never the backend

**The platform's `~/.claude/tasks/` board.** It is real and it is good at
in-flight coordination — atomic claiming, dependency edges, reassignment when a
member dies — but it lives in the home folder, it is deleted as items complete,
and it is scoped to one team. It is coordination, not a record. Work items must
outlive the run, so they go where the project keeps its work.

## What `tracker.md` must contain

Four lines, each a real command a member can run without asking:

    Backend: <the one store>
    Create: <command that files a new item>
    Claim:  <command that marks it yours>
    Close:  <command that closes it>

`[T6]` fails without them. The failure it prevents is quiet and expensive: a
member that cannot file a bug in one step will describe it in a message instead,
and the message is gone after the next restart.

## Bugs found while working

A bug outside your lane is filed, not fixed. File it, note which lane owns the
path, and carry on. Fixing it yourself crosses a boundary, and stopping to hand
it over turns every discovery into an interruption for two members.
