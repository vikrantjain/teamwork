# Finding the work before sizing anything

Sizing reads a breakdown. This is how the breakdown is obtained, and it is the
step that decides whether the team partitions the real work or a guess at it.

**Never write a plan here.** Planning is a separate job with its own tools, and a
plan written to justify a roster is a second source of truth that nobody
maintains. What is needed is a list of pieces and the paths each one writes.

## 1. Find the plan the project already has

Look for what this project actually keeps, in this order, first match wins:

1. **A plan file**, under whatever name it carries. `IMPLEMENTATION_PLAN.md`,
   `PLAN.md`, `ROADMAP.md`, a design doc, a spec, a numbered task list in the
   README. The name is not the thing; a file listing the pieces of the work is.
2. **The project's issue tracker**, when its open items already describe the
   work. `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/trackers.md` finds
   it, and the same store then becomes the team's tracker.
3. **Nothing.** Go to the interview.

A plan that exists wins over anything you would derive. Deriving a second
breakdown beside an existing one gives two answers to "what are the pieces", and
the lanes get drawn from whichever one you happened to read.

## 2. With no plan, interview

Five questions. Ask them **in one message**, because one turn answers all five
and five turns answer them no better.

1. **What is the goal, and how will you know it is finished?** The first line of
   the charter and its `## Done`. A team with no stop condition does not stop.
2. **What are the pieces, and which of them could progress at the same time?**
   These are the candidate lanes. Ask for pieces, not people.
3. **What must never be touched by two people at once?** Shared paths, and who
   should own each. This is the question whose absence costs the most: an unowned
   shared path is where two lanes collide first.
4. **Where do work items and bugs already get recorded?** The tracker. Naming an
   existing store beats inventing one, because items filed where nobody looks are
   lost items.
5. **What should stop and ask you, every time?** The human gates. Publishing,
   deleting, production, money, scope.

Take the answers as given. A member will discover the breakdown is wrong soon
enough, and `FRICTION` plus a retro is how that gets fixed. Arguing it now spends
the session before the team exists.

## 3. Read the ground

Three facts decide the mechanics, and all three are observed rather than assumed.

- **Version control, or none.** Whether the work is under git changes where the
  team root goes, whether the contracts are committed, and whether finishing has
  anything to merge. Check, do not presume:
  `git rev-parse --is-inside-work-tree`.
- **One root, or several.** One tree, several repositories, or several plain
  directories. This is the `Workspace:` line, and
  `${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/sizing.md` chooses it.
- **Whether the work produces files at all.** Almost all of it does, including
  writing, research and operations. Where it genuinely does not, say so: see
  below.

Record the answers in `decisions.md` with their reasons, or the next retro
re-derives them from scratch and may answer differently.

## 4. Propose, then ratify

Print the proposal before writing anything into the team root: the lanes, what
each owns, the shared paths and their owners, the workspace, the tracker, the
gates. Twenty lines at most.

**The human amends it, and nothing is written until they accept.** A team formed
from a guess partitions the wrong work, and the first anyone learns of it is a
boundary denying a write somebody needed. This is the same gate
`${CLAUDE_PLUGIN_ROOT}/skills/team-design/references/adoption.md` puts in front
of a running team, for the same reason.

## When the work produces no files

Lanes are sets of paths. That is what `[T5]` proves disjoint and what the
boundary hook denies on, so work that writes nothing has no boundary to enforce.

Say that plainly rather than forming a team that looks enforced and is not. The
contracts still do their other jobs: they say who covers what, who hands off to
whom, and when to stop. Nothing checks them, and a member that crosses a
boundary is told by nobody.
