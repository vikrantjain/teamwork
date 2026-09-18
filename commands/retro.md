---
description: Improve the team's rules from the friction they caused — group the notes by cause, revert the last rule that failed, make the smallest edit that would have prevented each recurring cause, and broadcast a reload. The only moment contracts change.
argument-hint: [team root path, if this session is outside it]
---

# /teamwork:retro — improve the rules

Team root: **$ARGUMENTS**

Run the `team-design` skill's retro loop. Read both if they are not already
loaded:

```
${CLAUDE_PLUGIN_ROOT}/skills/team-design/SKILL.md
${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/retro.md
```

Three steps are what make this converge instead of accumulate, and all three get
skipped.

**Drop every cause that appears once.** A single occurrence is noise, and a rule
written for noise is charged to every member on every context load, forever.

**Check the last retro's target cause before writing anything new.** If it
recurred, that rule failed — revert it and try a different one. Stacking a second
rule on a failed first is how a charter doubles while getting worse.

**To add a line, remove one.** Budgets are hard. If nothing can go, the edit is
not worth its place and the cause waits for next time.

Then record each decision and its reason in `decisions.md` and **prune it in the
same pass**, or it reaches its budget and `[T1]` blocks the retro that would have
fixed it. Then run the validator, spawn `teamwork:contract-auditor` with fresh
context for the judgement the validator cannot make, clear `friction.md`, commit,
and broadcast `RELOAD` carrying the team root's absolute path. **A member that is not
told keeps running the old rules**, and the whole benefit is lost silently.

With no argument, use the team root named in this session's charter.

Never restructure the breakdown and never reassign in-flight items. Change the
boundary; let the current item finish under the old one. Close by naming the
causes you left unaddressed, so nobody reads a short retro as a quiet team.
