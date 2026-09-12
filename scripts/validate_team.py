#!/usr/bin/env python3
"""Structural checker for a teamwork team root.

Proves that a team root still holds CONTRACTS and has not drifted into a work log
or a task board. It checks shape, never content quality: whether a rule is a GOOD
rule is the contract-auditor agent's job, and whether the work is right is nobody's
job here.

Usage:
    python3 validate_team.py <team-root> [--refs <dir>] [--quiet]

Exit codes:
    0  every check passed (warnings may still be printed)
    1  at least one check failed
    2  the team root does not exist or holds no charter

Checks:
    [T1] budgets          every contract file is within its line budget
    [T2] role-shape       each role file has exactly the four required headings
    [T3] no-log           no date, checkbox, issue id or status marker in a contract
    [T4] roster-closure   lanes named in the charter and role files on disk agree
    [T5] lane-disjoint    no path is owned by two roles
    [T6] tracker-named    tracker.md names one backend and its commands
    [T7] verbatim         protocol.md and conflicts.md still match the plugin
    [T8] friction-cap     warn that a retro is due
    [T9] team-root        the charter names this directory as an absolute path

[T3] and [T5] are the load-bearing ones. [T3] is what stops a charter becoming a
log, and [T5] is what stops two members editing one file.
"""

import argparse
import os
import re
import sys

# --- budgets -----------------------------------------------------------------
# A member reloads these on every context load, so the budget IS the feature.
BUDGETS = {
    "protocol.md": 45,
    "conflicts.md": 30,
    "charter.md": 50,
    "tracker.md": 20,
    "transport.md": 15,
    "decisions.md": 60,
    "roles/*.md": 30,
}

# friction.md is volatile state, not a contract, so reaching its cap calls a
# retro rather than failing the run. A team is not broken for noticing friction.
FRICTION_CAP = 25

ROLE_HEADINGS = ["## Owns", "## Never", "## Hands off to", "## Done means"]

# Files that must read as rules. friction.md and roster.md are excluded: they are
# the team's volatile state, which is why they are gitignored and never loaded.
CONTRACT_FILES = ["protocol.md", "conflicts.md", "charter.md", "tracker.md",
                  "transport.md"]

# Copied from the plugin and never edited, so a member that never loaded the
# skill is still bound by them. A paraphrase is how a shared rule quietly
# stops being shared.
VERBATIM = ["protocol.md", "conflicts.md"]

# --- the tells that a contract has become a log ------------------------------
LOG_TELLS = [
    (re.compile(r"\d{4}-\d{2}-\d{2}"), "a date"),
    (re.compile(r"^\s*[-*]\s*\[[ xX]\]"), "a checkbox"),
    (re.compile(r"^\s*Status\s*:"), "a status field"),
    (re.compile(r"[✅✔✓❌]"), "a status marker"),
    (re.compile(r"\b(completed|finished|shipped)\b", re.I), "a past-tense progress word"),
]
ISSUE_TELL = (re.compile(r"(?:^|\s)#\d+|\b[A-Z]{2,10}-\d+\b"), "an issue id")


class Report:
    def __init__(self, quiet=False):
        self.errors = []
        self.warnings = []
        self.quiet = quiet

    def fail(self, check, path, line, msg):
        where = f"{path}:{line}" if line else path
        self.errors.append(f"[{check}] {where}: {msg}")

    def warn(self, check, path, msg):
        self.warnings.append(f"[{check}] {path}: {msg}")

    def emit(self):
        for w in self.warnings:
            print(f"warning {w}", file=sys.stderr)
        for e in self.errors:
            print(f"FAIL    {e}", file=sys.stderr)
        if not self.errors and not self.quiet:
            print("ok      all checks passed")
        return 1 if self.errors else 0


def read_lines(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read().splitlines()


def role_files(root):
    roles_dir = os.path.join(root, "roles")
    if not os.path.isdir(roles_dir):
        return []
    return sorted(
        os.path.join(roles_dir, n)
        for n in os.listdir(roles_dir)
        if n.endswith(".md")
    )


def section(lines, heading):
    """Lines under `heading`, stopping at the next heading of the same level."""
    depth = len(heading) - len(heading.lstrip("#"))
    out, collecting = [], False
    for line in lines:
        if line.strip() == heading:
            collecting = True
            continue
        if collecting:
            stripped = line.strip()
            if stripped.startswith("#"):
                this_depth = len(stripped) - len(stripped.lstrip("#"))
                if this_depth <= depth:
                    break
            out.append(line)
    return out


def check_budgets(root, rep):
    for name, budget in BUDGETS.items():
        if name == "roles/*.md":
            targets = role_files(root)
        else:
            p = os.path.join(root, name)
            targets = [p] if os.path.exists(p) else []
        for path in targets:
            n = len(read_lines(path))
            if n > budget:
                rep.fail("T1", os.path.relpath(path, root), n,
                         f"{n} lines, budget {budget}. To add a line, remove one.")


def check_role_shape(root, rep):
    for path in role_files(root):
        lines = read_lines(path)
        rel = os.path.relpath(path, root)
        found = [l.strip() for l in lines if l.strip() in ROLE_HEADINGS]
        for heading in ROLE_HEADINGS:
            if heading not in found:
                rep.fail("T2", rel, 0, f"missing required heading {heading!r}")
        for heading in ROLE_HEADINGS:
            if found.count(heading) > 1:
                rep.fail("T2", rel, 0, f"duplicate heading {heading!r}")
        if "## Never" in found and not [l for l in section(lines, "## Never") if l.strip()]:
            rep.fail("T2", rel, 0,
                     "'## Never' is empty. A role with no prohibition has no boundary.")


def check_no_log(root, rep):
    targets = [(os.path.join(root, n), n) for n in CONTRACT_FILES]
    targets += [(p, os.path.relpath(p, root)) for p in role_files(root)]
    decisions = os.path.join(root, "decisions.md")
    if os.path.exists(decisions):
        targets.append((decisions, "decisions.md"))
    for path, rel in targets:
        if not os.path.exists(path):
            continue
        # A decision may cite the ticket that prompted it; it may not carry a log.
        tells = list(LOG_TELLS)
        if rel != "decisions.md":
            tells.append(ISSUE_TELL)
        for i, line in enumerate(read_lines(path), 1):
            if line.lstrip().startswith(("|", ">")) or "`" in line:
                continue  # tables and quoted examples are illustration, not record
            for pattern, what in tells:
                if pattern.search(line):
                    rep.fail("T3", rel, i,
                             f"{what} in a contract. Contracts are read before acting; "
                             "records of what happened belong in the tracker.")
                    break


def charter_lanes(root):
    charter = os.path.join(root, "charter.md")
    if not os.path.exists(charter):
        return []
    lanes = []
    for line in section(read_lines(charter), "## Lanes"):
        m = re.match(r"^\s*[-*]\s+([A-Za-z0-9][A-Za-z0-9_-]*)\b", line)
        if m:
            lanes.append(m.group(1))
    return lanes


def check_roster_closure(root, rep):
    named = set(charter_lanes(root))
    on_disk = {os.path.basename(p)[:-3] for p in role_files(root)}
    for lane in sorted(named - on_disk):
        rep.fail("T4", "charter.md", 0,
                 f"lane {lane!r} has no roles/{lane}.md")
    for lane in sorted(on_disk - named):
        rep.fail("T4", f"roles/{lane}.md", 0,
                 f"role {lane!r} is not listed under '## Lanes' in charter.md")


def literal_prefix(pattern):
    """The part of a glob before its first wildcard: what it actually reaches."""
    cut = len(pattern)
    for ch in "*?[":
        i = pattern.find(ch)
        if i != -1:
            cut = min(cut, i)
    return pattern[:cut].rstrip("/")


def owned_paths(path):
    out = []
    for line in section(read_lines(path), "## Owns"):
        m = re.match(r"^\s*[-*]\s+(\S+)", line)
        if m:
            out.append(m.group(1).strip("`"))
    return out


def check_lane_disjoint(root, rep):
    owners = {}
    for path in role_files(root):
        lane = os.path.basename(path)[:-3]
        for pattern in owned_paths(path):
            owners.setdefault(literal_prefix(pattern), []).append((lane, pattern))
    prefixes = sorted(owners)
    for i, a in enumerate(prefixes):
        for b in prefixes[i:]:
            if a == b:
                lanes = {lane for lane, _ in owners[a]}
                if len(lanes) > 1:
                    rep.fail("T5", "roles/", 0,
                             f"{sorted(lanes)} both own {a!r}. "
                             "Two members editing one path lose work silently.")
                continue
            if b.startswith(a + "/"):
                la = {lane for lane, _ in owners[a]}
                lb = {lane for lane, _ in owners[b]}
                if la != lb and not la & lb:
                    rep.fail("T5", "roles/", 0,
                             f"{sorted(la)} owns {a!r}, which contains "
                             f"{b!r} owned by {sorted(lb)}.")


def check_tracker_named(root, rep):
    path = os.path.join(root, "tracker.md")
    if not os.path.exists(path):
        rep.fail("T6", "tracker.md", 0, "missing. Work items need one named home.")
        return
    text = "\n".join(read_lines(path))
    for field in ("Backend:", "Create:", "Claim:", "Close:"):
        if not re.search(rf"^\s*{re.escape(field)}", text, re.M):
            rep.fail("T6", "tracker.md", 0,
                     f"no {field!r} line. A member that cannot file a bug will drop it.")
    backends = re.findall(r"^\s*Backend:", text, re.M)
    if len(backends) > 1:
        rep.fail("T6", "tracker.md", 0,
                 "more than one 'Backend:'. One store, or there are two places to look.")


def check_verbatim(root, rep, refs_dir):
    for name in VERBATIM:
        local = os.path.join(root, name)
        if not os.path.exists(local):
            rep.fail("T7", name, 0, "missing. It is copied from the plugin, not authored.")
            continue
        ref = os.path.join(refs_dir, name) if refs_dir else None
        if not ref or not os.path.exists(ref):
            rep.warn("T7", name,
                     "plugin copy not found, so verbatim could not be proved. "
                     "Pass --refs or set CLAUDE_PLUGIN_ROOT.")
            continue
        if read_lines(local) != read_lines(ref):
            rep.fail("T7", name, 0,
                     "differs from the plugin's copy. These files are copied, never "
                     "edited: a paraphrase is how a shared rule stops being shared.")


def check_friction_cap(root, rep):
    path = os.path.join(root, "friction.md")
    if not os.path.exists(path):
        return
    lines = [l for l in read_lines(path) if l.strip() and not l.startswith("#")]
    if len(lines) >= FRICTION_CAP:
        rep.warn("T8", "friction.md",
                 f"{len(lines)} notes, cap {FRICTION_CAP}. A retro is due.")


def check_team_root(root, rep):
    charter = os.path.join(root, "charter.md")
    if not os.path.exists(charter):
        return
    text = "\n".join(read_lines(charter))
    m = re.search(r"^\s*Team root:\s*(\S+)", text, re.M)
    if not m:
        rep.fail("T9", "charter.md", 0,
                 "no 'Team root:' line. Members in other folders need an absolute path.")
        return
    declared = m.group(1).strip("`")
    if not os.path.isabs(declared):
        rep.fail("T9", "charter.md", 0,
                 f"team root {declared!r} is relative. A relative path resolves "
                 "differently in every worktree, so a member reads a stale charter.")
        return
    if os.path.realpath(declared) != os.path.realpath(root):
        rep.fail("T9", "charter.md", 0,
                 f"team root is {declared!r} but this is {root!r}. You are editing a "
                 "copy, not the team root.")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", help="the team root directory")
    ap.add_argument("--refs", help="the plugin's skills/team-member/references dir")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"FAIL    {root}: not a directory", file=sys.stderr)
        return 2
    if not os.path.exists(os.path.join(root, "charter.md")):
        print(f"FAIL    {root}: no charter.md, so this is not a team root",
              file=sys.stderr)
        return 2

    refs_dir = args.refs
    if not refs_dir:
        plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
        if plugin_root:
            refs_dir = os.path.join(
                plugin_root, "skills", "team-member", "references")

    rep = Report(args.quiet)
    check_budgets(root, rep)
    check_role_shape(root, rep)
    check_no_log(root, rep)
    check_roster_closure(root, rep)
    check_lane_disjoint(root, rep)
    check_tracker_named(root, rep)
    check_verbatim(root, rep, refs_dir)
    check_friction_cap(root, rep)
    check_team_root(root, rep)
    return rep.emit()


if __name__ == "__main__":
    sys.exit(main())
