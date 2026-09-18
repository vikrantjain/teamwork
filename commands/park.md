---
description: Stop at a point the tracker fully describes, so a fresh set of sessions resumes exactly there. Run by the lead to drain the whole team, or by one lane to park itself while the team runs on.
argument-hint: [team root path, if this session is outside it]
---

# /teamwork:park — stop where the work can be picked up

Team root: **$ARGUMENTS**

Read the team root by its absolute path first. A relative `.teamwork/` may be
this worktree's own stale copy, and you would park against last week's rules.

## If this session is a lane

Follow `## Parking your lane` in the member skill, reading it if it is not
already loaded:

```
${CLAUDE_PLUGIN_ROOT}/skills/team-member/SKILL.md
```

Four conditions, all of them, before you answer `PARK`: your claimed item closed
or released, every `BLOCKED` you opened recorded against its item, your tree
clean or the item naming where the unfinished work is, and your last `FRICTION`
sent. **A claim left behind by a session that no longer exists is an item nobody
can take and nobody can see is stuck.**

## If this session is the lead

Follow the drain in:

```
${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/parking.md
```

**Broadcast `PARK` and then wait to be answered.** Do not poll the lanes. A park
that is chased costs a turn in every lane to learn what each was going to say.

**Do not verify anyone's `Done means`, and do not read the work.** This is a
stop, not a review, and a lead that reviews becomes the bottleneck the team was
formed to remove.

Finish by running
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_team.py <team root>` and
reporting it verbatim. Commit the team root only when it is under version control
and the tracker is a file inside it; everything else there was already
committed.

Close by naming **every lane that did not answer `PARK`**. An unparked lane left
work in a state only the human can go and look at, and silence here reads as
success.

With no argument, use the team root named in this session's charter. If this
session has no charter, say so rather than searching the filesystem for one.
