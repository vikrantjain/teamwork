---
description: One screen of the team's live state for the human — who is up, which lane holds what, which cross-lane edges are open, and whether a retro is due. Reads the tracker and the roster; never the work itself.
argument-hint: [team root path, if this session is outside it]
---

# /teamwork:status — the lead's one screen

Team root: **$ARGUMENTS**

Read the team root by absolute path, then report. Keep the whole thing to one
screen: this is a map for the human, and a status that scrolls is a status nobody
reads.

Gather, in this order:

1. **Who is up** — `ListAgents`, matched against the charter's `## Lanes`. Name
   every lane that is not up; a missing lane is the most useful line here. Then
   `roster.md` for where each lane is running and whether it has acked or parked.
   `ListAgents` says a session exists; only the roster says which tree it is in,
   and a lane running in the wrong tree edits the wrong files. A lane the roster
   names as acked and `ListAgents` does not show is running without messaging
   rather than stopped, which is a different problem with a different remedy in
   `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/transport.md`.
2. **What each lane holds** — from the tracker named in `tracker.md`, using its
   own commands. One line per lane: the item it owns and nothing more.
3. **Open cross-lane edges** — every `BLOCKED` that has not been answered with a
   `READY`. These are where the team is actually losing time.
4. **Whether a retro is due** — run
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_team.py <team root>` and
   report its warnings and failures verbatim.

The rest of the lead's duties, and the ones it is tempted into and should not do,
are in `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/leading.md`.

**Read the tracker, never the work.** Do not open diffs, do not summarize what
lanes have built, and do not verify anyone's `Done means`. A lead that reviews
the work becomes the context bottleneck the team was formed to remove, and this
command is where that starts.

**Do not message anyone to build this report.** Every field above comes from
files and from `ListAgents`. Asking four lanes for a status costs four turns and
tells you what the tracker already says.

With no argument, use the team root named in this session's charter. If this
session has no charter, say so rather than searching the filesystem for one.

Close with what you could not see: lanes that did not appear in `ListAgents`,
tracker fields the backend does not expose, and lanes the roster does not name.
`roster.md` is gitignored, so a fresh clone has none and every working directory
in this report is then a lane's own claim rather than a record.
