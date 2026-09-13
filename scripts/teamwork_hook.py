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
    SessionEnd    name uncommitted work, which is one of the four park conditions

It shares `validate_team`'s glob code on purpose. If the hook and the checker
disagreed about what a glob reaches, a team would be enforced under rules it was
never validated against.

Resolving the lane, first match wins:
    1. $TEAMWORK_LANE, set by the launch command the lead prints.
    2. The working directory's own name, under one worktree per lane.
    3. Nothing, and then it allows every write and says so once.

It fails OPEN. A hook that blocked a session it could not identify would stop
the lead, stop a session that is not on a team at all, and make the plugin
unusable the first time the ladder missed. The cost is that a lane it cannot
identify is a lane it cannot protect, which is why rung 1 is worth setting.

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
    charter_lanes, glob_regex, owned_paths, read_lines, role_files, section)

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


def find_team_root(cwd):
    named = os.environ.get("TEAMWORK_ROOT")
    if named and os.path.exists(os.path.join(named, "charter.md")):
        return os.path.realpath(named)
    here = os.path.realpath(cwd or ".")
    while True:
        candidate = os.path.join(here, ".teamwork")
        if os.path.exists(os.path.join(candidate, "charter.md")):
            return candidate
        parent = os.path.dirname(here)
        if parent == here:
            return None
        here = parent


def lanes_of(root):
    return set(charter_lanes(root)) | {
        os.path.basename(p)[:-3] for p in role_files(root)}


def isolation_is_worktrees(root):
    for line in read_lines(os.path.join(root, "charter.md")):
        if line.strip().lower().startswith("isolation:"):
            return "worktree" in line.lower()
    return False


def resolve_lane(root, cwd):
    """The lane this session is, and how it was decided."""
    lanes = lanes_of(root)
    named = os.environ.get("TEAMWORK_LANE")
    if named in lanes:
        return named, "$TEAMWORK_LANE"
    if isolation_is_worktrees(root) and cwd:
        base = os.path.basename(os.path.realpath(cwd))
        if base in lanes:
            return base, "the working directory's name"
    return None, None


def repo_root(cwd, root):
    here = os.path.realpath(cwd or ".")
    while True:
        if os.path.exists(os.path.join(here, ".git")):
            return here
        parent = os.path.dirname(here)
        if parent == here:
            return os.path.dirname(root)
        here = parent


def inside(path, directory):
    return os.path.commonpath([path, directory]) == directory


def owners(root, rel):
    """Every lane whose `## Owns` reaches this repo-relative path."""
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
    if inside(real, root):
        deny("PreToolUse",
             f"{os.path.relpath(real, root)} is in the team root. protocol.md rule 5: "
             "write only the paths your role owns, and never the team root. Contracts "
             "change at a retro and nowhere else. Send FRICTION and keep working.")

    repo = repo_root(cwd, root)
    if not inside(real, repo):
        allow()
    rel = os.path.relpath(real, repo)
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
        lines.append(
            "Writes to a path another lane owns are denied by a hook, so a boundary "
            "crossing fails rather than silently losing someone's work.")
    else:
        lines.append(
            "No lane resolved for this session, so the boundary hook allows every "
            "write. Set TEAMWORK_LANE to the lane name if this session is a member.")
    context(event, " ".join(lines))


def session_end(payload):
    """Condition 3 of a park: the tree is clean, or the item says where the work is."""
    cwd = payload.get("cwd")
    root = find_team_root(cwd)
    if not root:
        allow()
    lane, _ = resolve_lane(root, cwd)
    if not lane:
        allow()
    try:
        dirty = subprocess.run(
            ["git", "status", "--porcelain"], cwd=cwd, capture_output=True,
            text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        allow()
    if not dirty:
        allow()
    files = [l[3:] for l in dirty.splitlines()][:10]
    print(f"teamwork: lane {lane} is ending with uncommitted work in {len(dirty.splitlines())} "
          f"file(s): {', '.join(files)}. A park needs the tree clean, or the item naming "
          "the branch, worktree or stash that holds this. Nobody else can find it by "
          "looking.", file=sys.stderr)
    sys.exit(0)


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
        elif event == "SessionEnd":
            session_end(payload)
    except SystemExit:
        raise
    except Exception:
        # A hook that crashes must not stop the work it was watching.
        sys.exit(0)
    sys.exit(0)


if __name__ == "__main__":
    main()
