#!/usr/bin/env python3
"""Runtime enforcement of the boundary the contracts only declared.

`validate_team.py` proves the lanes are disjoint before anyone starts. Nothing
watched what a member actually wrote, so the one failure this plugin exists to
prevent was left to a rule a member reads at startup and may deprioritise twenty
turns later. This hook watches the writes.

Events:
    PreToolUse    deny a write to a path another lane owns, or to the team root
    SessionStart  tell a joining session where its team root and role are
    PostCompact   say it again, because compaction is where that is lost

It shares `validate_team`'s glob code on purpose. If the hook and the checker
disagreed about what a glob reaches, a team would be enforced under rules it was
never validated against.

Resolving the lane, first match wins:
    1. $TEAMWORK_LANE, set by the launch command the lead prints.
    2. The working directory's own name, under one worktree per lane.
    3. Nothing, and then it allows every write and says so once.

Resolving the team root, first match wins, as team-root.md resolves it:
    1. $TEAMWORK_ROOT, set by the same launch command.
    2. The MAIN worktree's .teamwork, from `git rev-parse --git-common-dir`.
    3. The nearest .teamwork walking up from the working directory.

`Owns` globs are relative to the workspace, and which directory that is comes
from the charter's `Workspace:` line. Under one worktree per lane it is the
worktree this session is in, because every lane writes the same globs into a
different tree. Under the other three the lanes share one anchor and it is the
team root's parent: the tree itself under one shared tree, and the directory
holding every repository or lane directory under the other two. Git is not
required for any of this; only the team root's second rung uses it.

Rung 2 is what keeps a lane off its own stale copy. Under one worktree per lane
every worktree carries a committed .teamwork, and those copies diverge as soon
as a retro commits on another branch, so walking up finds the copy rather than
the original and the hook would enforce last week's ownership. Rungs 2 and 3
only ever find a directory named .teamwork; a team root the user named anything
else is reachable through rung 1 alone, which is why the launch command sets it.

It fails OPEN. A hook that blocked a session it could not identify would stop
the lead, stop a session that is not on a team at all, and make the plugin
unusable the first time the ladder missed. The cost is that a lane it cannot
identify is a lane it cannot protect, which is why rung 1 is worth setting.

A member's own agents inherit its lane. Resolution reads the environment and the
working directory, and a session passes both to everything it spawns, so a lane
can fan out as widely as its work needs and each agent is held to that lane's
paths. That is why nothing here governs what happens inside a lane.

The lead must never set $TEAMWORK_LANE to a member's lane. Anything spawned in
the lead's own process inherits its environment, so that lane's name would be
handed to the spawned session, which would then be denied its own paths and
allowed the lead's. `lead` is the one safe value: it is the lane a lead holds
when its work is downstream of everyone, and it is the only lane allowed to
write the team root, which protocol.md rule 5 already reserves to the lead.

There is no SessionEnd branch. Naming a lane's uncommitted work as it exits was
the obvious place to catch the third park condition, and the platform prints a
SessionEnd hook's output only when the hook reports failure. A warning had to
pose as a crash to be seen at all, which a hook that fails open must not do. The
condition stays where a member can act on it, in the park procedure.

What it cannot see: a write made through Bash. Parsing a shell command to find
the file it truncates is a losing game, and a hook that catches nine tenths of
them would be trusted for the tenth.
"""

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate_team import (  # noqa: E402
    charter_lanes, glob_regex, owned_paths, read_lines, role_files)

# Write tools name their target in one of these. Bash is deliberately absent.
TARGET_FIELDS = ("file_path", "notebook_path", "path")


def emit(payload):
    print(json.dumps(payload))
    sys.exit(0)


def allow():
    sys.exit(0)


def deny(event, reason):
    emit({"hookSpecificOutput": {"hookEventName": event,
                                 "permissionDecision": "deny",
                                 "permissionDecisionReason": reason}})


def context(event, text):
    emit({"hookSpecificOutput": {"hookEventName": event,
                                 "additionalContext": text}})


# The lane a lead holds when its work is downstream of every other lane. It is
# the one lane allowed inside the team root, because protocol.md rule 5 reserves
# that to the lead and a lead locked out of friction.md cannot lead.
LEAD_LANE = "lead"


def is_team_root(path):
    return bool(path) and os.path.exists(os.path.join(path, "charter.md"))


def main_worktree(cwd):
    """The repository's main worktree, which is where its `.teamwork` lives.

    Every linked worktree carries its own committed copy of the team root, and
    those copies diverge the moment a retro commits on another branch. Walking
    up from the working directory finds the copy; this finds the original.
    """
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=cwd or ".", capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0 or not out.stdout.strip():
        return None
    return os.path.dirname(os.path.realpath(out.stdout.strip()))


def find_team_root(cwd):
    """The team root, by the same ladder team-root.md resolves it with."""
    named = os.environ.get("TEAMWORK_ROOT")
    if is_team_root(named):
        return os.path.realpath(named)
    repo = main_worktree(cwd)
    if repo:
        candidate = os.path.join(repo, ".teamwork")
        if is_team_root(candidate):
            return os.path.realpath(candidate)
    here = os.path.realpath(cwd or ".")
    while True:
        candidate = os.path.join(here, ".teamwork")
        if is_team_root(candidate):
            return os.path.realpath(candidate)
        parent = os.path.dirname(here)
        if parent == here:
            return None
        here = parent


def lanes_of(root):
    return set(charter_lanes(root)) | {
        os.path.basename(p)[:-3] for p in role_files(root)}


def workspace_is_worktrees(root):
    """Whether each lane has a tree of its own.

    `Isolation:` is what this line was called when it had two values instead of
    four. The alias stays because a team formed under the old name would
    otherwise lose its second lane rung silently, which reads as a team with no
    boundaries rather than as an error.
    """
    for line in read_lines(os.path.join(root, "charter.md")):
        lowered = line.strip().lower()
        for prefix in ("workspace:", "isolation:"):
            if lowered.startswith(prefix):
                return "worktree" in lowered
    return False


def resolve_lane(root, cwd):
    """The lane this session is, and how it was decided."""
    lanes = lanes_of(root)
    named = os.environ.get("TEAMWORK_LANE")
    if named in lanes:
        return named, "$TEAMWORK_LANE"
    if workspace_is_worktrees(root) and cwd:
        base = os.path.basename(os.path.realpath(cwd))
        if base in lanes:
            return base, "the working directory's name"
    return None, None


def inside(path, directory):
    return os.path.commonpath([path, directory]) == directory


def enclosing_repo(here):
    """The repository or worktree this directory is in, or None."""
    while True:
        if os.path.exists(os.path.join(here, ".git")):
            return here
        parent = os.path.dirname(here)
        if parent == here:
            return None
        here = parent


def workspace_root(cwd, root):
    """The directory `Owns` globs are relative to.

    Under one worktree per lane each lane has its own tree, so the anchor is the
    tree this session is in and every lane writes the same globs. Under the other
    three the lanes share one anchor: the team root's parent. That is the tree
    itself under one shared tree, and the directory holding every repository or
    lane directory under the other two, where a lane owns `payments/**` and is
    only disjoint from one owning `web/**` when both are read from there.

    Anchoring at the enclosing repository instead would make both of those `**`,
    so every glob would match every file and the team would look unowned.
    """
    here = os.path.realpath(cwd or ".")
    repo = enclosing_repo(here)
    if workspace_is_worktrees(root):
        return repo or os.path.dirname(root)
    parent = os.path.dirname(root)
    if inside(here, parent):
        return parent
    return repo or parent


def owners(root, rel):
    """Every lane whose `## Owns` reaches this workspace-relative path."""
    out = []
    for path in role_files(root):
        lane = os.path.basename(path)[:-3]
        for pattern in owned_paths(path):
            if glob_regex(pattern).match(rel):
                out.append((lane, pattern))
                break
    return out


def pre_tool_use(payload):
    target = None
    for field in TARGET_FIELDS:
        value = payload.get("tool_input", {}).get(field)
        if isinstance(value, str) and value:
            target = value
            break
    if not target:
        allow()
    cwd = payload.get("cwd")
    root = find_team_root(cwd)
    if not root:
        allow()
    lane, _ = resolve_lane(root, cwd)
    if not lane:
        allow()

    real = os.path.realpath(os.path.join(cwd or ".", target))
    anchor = workspace_root(cwd, root)
    # A lane's own copy of the team root is guarded too. It is not the team root,
    # but it is what a member reads when it forgets rule 4, so a write that lands
    # there is a contract edit whichever copy it reached.
    repo = enclosing_repo(os.path.realpath(cwd or "."))
    copies = {os.path.realpath(os.path.join(d, ".teamwork"))
              for d in (anchor, repo) if d}
    if lane != LEAD_LANE:
        for guarded in [root] + sorted(copies):
            if inside(real, guarded):
                deny("PreToolUse",
                     f"{os.path.relpath(real, guarded)} is in the team root. "
                     "protocol.md rule 5: write only the paths your role owns, and "
                     "only the lead writes the team root. Contracts change at a retro "
                     "and nowhere else. Send FRICTION and keep working.")
    if not inside(real, anchor):
        allow()
    rel = os.path.relpath(real, anchor)
    claims = owners(root, rel)
    if not claims or any(owner == lane for owner, _ in claims):
        allow()
    owner, pattern = claims[0]
    deny("PreToolUse",
         f"{rel} belongs to the {owner} lane, which owns {pattern!r}. You are {lane}. "
         f"Reach across a boundary with a message, never with an edit: ASK {owner} and "
         "let it make the change. Two members editing one path lose work, and neither "
         "of them sees it happen.")


def startup(payload, event):
    root = find_team_root(payload.get("cwd"))
    if not root:
        allow()
    lane, how = resolve_lane(root, payload.get("cwd"))
    lines = [f"This session is on a teamwork team. Team root: {root}",
             "Read it by that absolute path. A relative .teamwork/ may be this "
             "worktree's own stale copy."]
    if lane:
        lines.append(
            f"Your lane is {lane} (resolved from {how}). Load exactly five files: "
            f"protocol.md, charter.md, transport.md, tracker.md and roles/{lane}.md. "
            "Never another lane's role file.")
        if lane == "lead":
            lines.append(
                "You are the lead holding the lead lane, so you are the one session "
                "that may write the team root. Everything outside roles/lead.md's "
                "Owns still belongs to a member: reach it with a message.")
        lines.append(
            f"Ask your human to run /rename {lane} before you announce yourself. You "
            "cannot run it yourself, and until it is done a message meant for you may "
            "reach another lane. Tell the lead if it does not happen.")
        lines.append(
            "Writes to a path another lane owns are denied by a hook, so a boundary "
            "crossing fails rather than silently losing someone's work.")
    else:
        lines.append(
            "No lane resolved for this session, so the boundary hook allows every "
            "write. If this session is a member, relaunch it with TEAMWORK_LANE set "
            "to its lane. If it is the lead, this is correct. A lead that holds a "
            "downstream lane may relaunch with TEAMWORK_LANE=lead; it must never be "
            "set to a member's lane, because anything spawned here inherits the "
            "value and would then be denied its own paths and allowed the lead's.")
    context(event, " ".join(lines))


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)
    event = payload.get("hook_event_name")
    try:
        if event == "PreToolUse":
            pre_tool_use(payload)
        elif event in ("SessionStart", "PostCompact"):
            startup(payload, event)
    except SystemExit:
        raise
    except Exception:
        # A hook that crashes must not stop the work it was watching.
        sys.exit(0)
    sys.exit(0)


if __name__ == "__main__":
    main()
