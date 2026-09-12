# The retro — how the rules get better

The only moment contracts change. Everything between retros is work under the
rules as they stand, because a rule that changes under way is a rule nobody can
rely on.

## When it runs

When `friction.md` reaches its cap of 25 notes, or on `/teamwork:retro`. The cap
is the trigger, not a limit: the file filling up is the team telling you its rules
cost more than they earn.

## The loop

1. **Read `friction.md` and group by cause, not by symptom.** Three notes saying
   "had to ask who owns the schema" are one cause. Grouping by symptom produces
   three rules where one boundary was missing.
2. **Drop every cause appearing once.** A single occurrence is noise, and a rule
   written for noise is pure cost charged to every member forever. This step is
   skipped more than any other.
3. **Check the last retro's target cause first.** If it recurred, that rule
   failed: **revert it**, and try a different one. Stacking a second rule on a
   failed first is how a charter doubles while getting worse. This is the only
   step that makes the loop converge.
4. **For each surviving cause, write the smallest edit that would have prevented
   it.** Usually a path moving between two lanes, a missing `Never` line, or a
   shared path gaining an owner. Rarely a new rule.
5. **To add a line, remove one.** Budgets are hard. If nothing can go, the edit is
   not worth its place and the cause goes back on the list for next time.
6. **Record the decision and its reason in `decisions.md`** — the reason, not just
   the conclusion, so the next retro does not reopen it without new evidence.
7. **Run the validator.** `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_team.py
   <team root>` must pass before anything is announced.
8. **Spawn `teamwork:contract-auditor`** with fresh context to answer the one
   question the validator cannot: is every line still a rule, or has something
   become a record of what happened? It flags; you decide.
9. **Clear `friction.md`, commit, and broadcast `RELOAD`** carrying the team
   root's absolute path. A member that is not told keeps running the old rules,
   and the retro's whole benefit is lost silently.

## What a retro never does

- **Never restructure the breakdown.** Re-planning is a planning activity. If the
  work is wrong, stop and say so rather than fixing it mid-flight.
- **Never reassign in-flight items.** Change the boundary; let the current item
  finish under the old one.
- **Never add a rule without a failure mode.** If you cannot say what goes wrong
  without it, the friction had another cause and you have not found it yet.
