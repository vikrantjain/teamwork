#!/usr/bin/env python3
"""Runtime enforcement of the boundary the contracts only declared.

`validate_team.py` proves the lanes are disjoint before anyone starts. It cannot
see what a member writes afterwards, and a rule read at startup may be
deprioritised twenty turns later. This hook watches the writes.

Events:
    PreToolUse    deny a write to a path another lane owns, or to the team root
    SessionStart  tell a joining session where its team root and role are, and
                  say it again after a compaction, which starts the session
                  again with source `compact`

It shares `validate_team`'s glob code on purpose. If the hook and the checker
disagreed about what a glob reaches, a team would be enforced under rules it was
never validated against.

Resolving the lane, first match wins:
    1. $TEAMWORK_LANE, set by the launch command the lead prints, and at every
       later start by the `env` of the lane directory's .claude/settings.local.json.
       Claude Code applies that `env` to the session, so it reaches this hook as
       an ordinary variable and nothing here reads the file.
    2. The working directory's own name, wherever a lane has a tree of its own.
    3. Nothing, and then it allows every write and says so once.

Resolving the team root, first match wins, as team-root.md resolves it:
    1. $TEAMWORK_ROOT, set by the same launch command.
    2. The MAIN worktree's .teamwork, from the repository's common git dir.
    3. The nearest .teamwork walking up from the working directory.

`Owns` globs are relative to the workspace, and which directory that is comes
from the charter. Under one worktree per lane it is the worktree this session is
in: each lane's globs are read against its own tree, so two lanes may name the
same directory and still write different files. That anchor alone left every
other checkout unwatched, so a lane could write into another lane's live tree.
A write into any checkout but the session's own is therefore denied before a
glob is read. Under the other three the lanes
share one anchor and the charter declares it on its `Workspace root:` line. A
team formed before that line existed falls back to the team root's parent, which
is where the ladder puts it unless the user named a path of its own. Git is not
required for any of this; only the team root's second rung uses it. The hook
reads git's own files rather than running git, because it runs on every write
in every project the plugin is installed in.

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

There is no SessionEnd branch. The platform prints a SessionEnd hook's output
only when the hook reports failure, so a warning naming a lane's uncommitted
work would have to pose as a crash to be seen, which a hook that fails open must
not do. The park procedure carries that condition instead.

There is no PostCompact branch. The platform reads no `hookSpecificOutput`
from a PostCompact hook, so context returned from one goes nowhere.
SessionStart already fires after a compaction, with source `compact`, and that
is what re-states the lane.

The startup note is given only while a run is live. Finishing keeps the team
root, so without that test every later session in the project would be told it
is on a team, and pay for the note in context. A run is live when the session
carries either variable, resolves a lane, or the team root holds `roster.md`,
which is this run's state and goes when the run finishes.

What it cannot see: a write made through Bash. Parsing a shell command to find
the file it truncates is a losing game, and a hook that catches nine tenths of
them would be trusted for the tenth.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate_team import (  # noqa: E402
    charter_field, charter_lanes, glob_regex, owned_paths, read_lines, role_files)

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


def enclosing_repo(here):
    """The repository or worktree this directory is in, or None."""
    while True:
        if os.path.exists(os.path.join(here, ".git")):
            return here
        parent = os.path.dirname(here)
        if parent == here:
            return None
        here = parent


def first_line(path):
    try:
        lines = read_lines(path)
    except (OSError, UnicodeDecodeError):
        return None
    return lines[0].strip() if lines else None


def git_dirs(here):
    """(this checkout, the repository's common git dir), or None.

    What `git rev-parse --git-common-dir` prints, read from the files git keeps
    instead of by running git. A main checkout's `.git` is the common dir. A
    linked worktree's `.git` is a file naming its own git dir, and that dir's
    `commondir` names the shared one; a submodule's has none and is its own.
    """
    repo = enclosing_repo(here)
    if not repo:
        return None
    dotgit = os.path.join(repo, ".git")
    if os.path.isdir(dotgit):
        return repo, os.path.realpath(dotgit)
    pointer = first_line(dotgit)
    if not pointer or not pointer.startswith("gitdir:"):
        return None
    gitdir = os.path.join(repo, pointer[len("gitdir:"):].strip())
    common = first_line(os.path.join(gitdir, "commondir")) or "."
    return repo, os.path.realpath(os.path.join(gitdir, common))


def main_worktree(cwd):
    """The repository's main worktree, which is where its `.teamwork` lives.

    Every linked worktree carries its own committed copy of the team root, and
    those copies diverge the moment a retro commits on another branch. Walking
    up from the working directory finds the copy; this finds the original.
    """
    dirs = git_dirs(os.path.realpath(cwd or "."))
    return os.path.dirname(dirs[1]) if dirs else None


def worktrees(common):
    """Every checkout of the repository: the main one, then each linked one."""
    out = [os.path.dirname(common)]
    linked = os.path.join(common, "worktrees")
    names = sorted(os.listdir(linked)) if os.path.isdir(linked) else []
    for name in names:
        dotgit = first_line(os.path.join(linked, name, "gitdir"))
        if dotgit:
            out.append(os.path.dirname(os.path.realpath(
                os.path.join(linked, name, dotgit))))
    return out


def foreign_checkout(path, here):
    """The checkout holding `path` when it is not the one `here` is in, or None.

    The nearest checkout wins, because a linked worktree may sit inside the main
    one, as `claude --worktree` puts it.
    """
    dirs = git_dirs(here)
    if not dirs:
        return None
    own, common = dirs
    holders = [t for t in worktrees(common) if inside(path, t)]
    if not holders:
        return None
    nearest = max(holders, key=len)
    return None if nearest == os.path.realpath(own) else nearest


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


def workspace_line(root):
    """The charter's workspace value, lowercased, or None.

    `Isolation:` is what this line was called when it had two values instead of
    four. The alias stays because a team formed under the old name would
    otherwise lose its second lane rung silently, which reads as a team with no
    boundaries rather than as an error. `Workspace root:` does not match either
    prefix, so the two lines cannot be confused for one another.
    """
    for line in read_lines(os.path.join(root, "charter.md")):
        lowered = line.strip().lower()
        for prefix in ("workspace:", "isolation:"):
            if lowered.startswith(prefix):
                return lowered
    return None


def workspace_is_worktrees(root):
    """Whether each lane has its own checkout, which decides the glob anchor."""
    line = workspace_line(root)
    return bool(line) and "worktree" in line


def lane_has_own_directory(root):
    """Whether a lane's working directory is named for the lane.

    True under worktrees, separate repositories and separate directories: each
    lane sits in a directory of its own, and the charter asks for that directory
    to carry the lane's name, so the name is a second way to identify a lane
    started without $TEAMWORK_LANE.

    False under one shared tree, where every lane's working directory is the
    same one and the name would answer for all of them or for none. False as
    well when the line is missing or unreadable, because a wrong lane here
    denies a lane its own paths and hands it another lane's.
    """
    line = workspace_line(root)
    if not line or "shared tree" in line:
        return False
    return any(word in line for word in ("worktree", "repositor", "director"))


def resolve_lane(root, cwd):
    """The lane this session is, and how it was decided."""
    lanes = lanes_of(root)
    named = os.environ.get("TEAMWORK_LANE")
    if named in lanes:
        return named, "$TEAMWORK_LANE"
    if lane_has_own_directory(root) and cwd:
        base = os.path.basename(os.path.realpath(cwd))
        if base in lanes:
            return base, "the working directory's name"
    return None, None


def inside(path, directory):
    return os.path.commonpath([path, directory]) == directory


def workspace_root(cwd, root):
    """The directory `Owns` globs are relative to.

    Under one worktree per lane each lane has its own tree, so the anchor is the
    tree this session is in and each lane's globs are read against it. Under the
    other three the lanes share one anchor and the charter names it. A derived
    anchor is wrong whenever the team root is not in the directory holding the
    lanes, and then every glob misses and every out-of-lane write is allowed.

    The derivation stays as the fallback, for a charter without the line. It is
    the team root's parent, which is the tree itself under one shared tree and
    the directory holding every repository or lane directory under the other
    two, where a lane owns `payments/**` and is only disjoint from one owning
    `web/**` when both are read from there. The enclosing repository is not the
    fallback: read against `payments/` itself, `payments/**` matches nothing, and
    the team looks unowned.
    """
    here = os.path.realpath(cwd or ".")
    repo = enclosing_repo(here)
    if workspace_is_worktrees(root):
        return repo or os.path.dirname(root)
    declared = charter_field(root, "Workspace root")
    if declared and os.path.isabs(declared) and os.path.isdir(declared):
        return os.path.realpath(declared)
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
    here = os.path.realpath(cwd or ".")
    anchor = workspace_root(cwd, root)
    # A lane's own copy of the team root is guarded too. It is not the team root,
    # but it is what a member reads when it forgets rule 4, so a write that lands
    # there is a contract edit whichever copy it reached.
    repo = enclosing_repo(here)
    copies = {os.path.realpath(os.path.join(d, ".teamwork"))
              for d in (anchor, repo) if d}
    for guarded in [root] + sorted(copies):
        if inside(real, guarded):
            if lane == LEAD_LANE:
                allow()
            deny("PreToolUse",
                 f"{os.path.relpath(real, guarded)} is in the team root. "
                 "protocol.md rule 5: write only the paths your role owns, and "
                 "only the lead writes the team root. Contracts change at a retro "
                 "and nowhere else. Send FRICTION and keep working.")
    if workspace_is_worktrees(root):
        other = foreign_checkout(real, here)
        if other:
            name = os.path.basename(other)
            whose = (f"the {name} lane's worktree" if name in lanes_of(root)
                     else "the main checkout" if other == main_worktree(here)
                     else "another lane's worktree")
            deny("PreToolUse",
                 f"{real} is in {whose}, {other}. Under one worktree per lane you "
                 f"write only your own tree, {repo}. Make the change there if the "
                 "path is yours, or ASK its owner. Two members editing one path "
                 "lose work, and neither of them sees it happen.")
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
    named = os.environ.get("TEAMWORK_LANE")
    live = (lane or named or os.environ.get("TEAMWORK_ROOT")
            or os.path.exists(os.path.join(root, "roster.md")))
    if not live:
        allow()
    lines = [f"This session is on a teamwork team. Team root: {root}",
             "Read it by that absolute path. A relative .teamwork/ may be this "
             "worktree's own stale copy."]
    lanes = lanes_of(root)
    if named and named not in lanes:
        lines.append(
            f"TEAMWORK_LANE is {named!r}, which is not a lane of this team "
            f"({', '.join(sorted(lanes))}), so the boundary hook ignores it.")
    if lane:
        lines.append(
            f"Your lane is {lane} (resolved from {how}). Load exactly five files: "
            f"protocol.md, charter.md, transport.md, tracker.md and roles/{lane}.md. "
            "Never another lane's role file.")
        if lane == LEAD_LANE:
            # The member's JOIN instruction would have the lead join itself. What
            # the lead must check instead is that members can reach it.
            lines.append(
                "You are the lead holding the lead lane, so you are the one session "
                "that may write the team root. Everything outside roles/lead.md's "
                "Owns still belongs to a member: reach it with a message. Members "
                "send their JOIN to the name on transport.md's Lead: line, so check "
                "with ListAgents that it is this session's name, and rewrite the "
                "line if it is not.")
        else:
            lines.append(
                f"Before you send JOIN to the name on transport.md's Lead: line, "
                f"check with ListAgents that this session is named {lane}. If it is "
                f"not, ask your human to run /rename {lane}. You cannot run it "
                "yourself, and until it is done a message meant for you may reach "
                "another lane. Tell the lead if it does not happen.")
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
        elif event == "SessionStart":
            startup(payload, event)
    except SystemExit:
        raise
    except Exception:
        # A hook that crashes must not stop the work it was watching.
        sys.exit(0)
    sys.exit(0)


if __name__ == "__main__":
    main()
