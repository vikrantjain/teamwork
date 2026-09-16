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
    [T2] role-shape       each role file has the four headings, a non-empty Owns
                          and Never, and repo-relative Owns globs
    [T3] no-log           no date, checkbox, issue id or status marker in a contract
    [T4] roster-closure   lanes named in the charter and role files on disk agree
    [T5] lane-disjoint    no path is owned by two roles, whether one role's glob
                          contains another's or the two merely intersect
    [T6] tracker-named    tracker.md names one backend and its commands
    [T7] verbatim         protocol.md and conflicts.md still match the plugin
    [T8] friction-cap     warn that a retro is due
    [T9] team-root        the charter names this directory as an absolute path
    [T10] transport-named transport.md names one substrate and how to address it
    [T11] shared-paths    every charter shared path names a lane, that lane's role
                          claims it, and no other lane's role reaches it
    [T12] lane-names      every lane name is usable as an address

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
]
# Standards are written like tickets. Without this list, "UTF-8", "SHA-256",
# "ISO-8601" and "AES-256" all read as issue ids and fail a contract that was
# only naming an encoding. The list is short on purpose: contract-auditor is
# the backstop for an id this cannot tell from a standard.
NOT_A_TICKET = ("UTF", "SHA", "ISO", "RFC", "AES", "RSA", "PKCS", "IEEE",
                "ANSI", "NIST", "CVE", "JPEG", "MPEG", "ECMA", "ETSI",
                "ASCII", "HTTP", "HTTPS", "TLS", "SSL", "CRC", "MD", "EN")
# A six-digit "#336699" is a colour, not an issue. A three-digit "#123" is
# ambiguous and is read as an issue, because a charter naming a colour is
# rarer than one citing a ticket.
ISSUE_TELL = (re.compile(
    r"(?<![\w#])#\d{1,5}(?![\da-fA-F])"
    r"|\b(?!(?:" + "|".join(NOT_A_TICKET) + r")-)[A-Z][A-Z0-9]{1,9}-\d+\b"
), "an issue id")

# Backticked text is an illustration of a command, not a record of one. Only the
# span is exempt: skipping the whole line let one backtick launder a log entry.
CODE_SPAN = re.compile(r"`[^`]*`")


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


# The validator ships inside the plugin, so it finds the files it compares
# against without being told where they are. CLAUDE_PLUGIN_ROOT is substituted
# into command text and never exported to the shell, so depending on it made
# [T7] a warning in every documented invocation instead of a check.
PLUGIN_REFS = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    os.pardir, "skills", "team-member", "references"))


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
        if sorted(found) == sorted(ROLE_HEADINGS) and found != ROLE_HEADINGS:
            rep.fail("T2", rel, 0,
                     "headings are out of order. The order is "
                     + ", ".join(ROLE_HEADINGS)
                     + ". A role that varies in shape cannot be read quickly.")
        if "## Never" in found and not [l for l in section(lines, "## Never") if l.strip()]:
            rep.fail("T2", rel, 0,
                     "'## Never' is empty. A role with no prohibition has no boundary.")
        entries = owns_entries(lines)
        if "## Owns" in found and not entries:
            rep.fail("T2", rel, 0,
                     "'## Owns' is empty. A lane claiming no path is a lane [T5] can "
                     "prove nothing about, so nothing stops it writing where another "
                     "lane works.")
        for entry in entries:
            if entry.startswith("/"):
                rep.fail("T2", rel, 0,
                         f"'## Owns' entry {entry!r} is absolute. Owns are "
                         "repo-relative globs; an absolute path and a relative one "
                         "naming the same file look unequal to [T5], which then "
                         "passes a real collision.")


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
            if line.lstrip().startswith(("|", ">")):
                continue  # tables and quotations are illustration, not record
            scanned = CODE_SPAN.sub(" ", line)
            for pattern, what in tells:
                if pattern.search(scanned):
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


def has_wildcard(pattern):
    return any(ch in pattern for ch in "*?[")


def glob_regex(pattern):
    """A regex matching the paths a glob reaches.

    A pattern with no wildcard names a directory, so it reaches its whole subtree:
    that is what makes `src` and `src/api/**` an overlap rather than two lanes.
    """
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")   # `**/` also matches no directory at all
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        elif pattern[i] == "[":
            close = pattern.find("]", i)
            if close == -1:
                out.append(re.escape(pattern[i]))
                i += 1
            else:
                # glob negates a class with `!`; regex negates it with `^`.
                body = pattern[i + 1:close]
                if body.startswith("!"):
                    body = "^" + body[1:]
                out.append("[" + body + "]")
                i = close + 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    body = "".join(out)
    if not has_wildcard(pattern):
        body = body.rstrip("/") + "(?:/.*)?"
    return re.compile("^" + body + "$")


def probe_path(pattern):
    """One concrete path the glob matches, for testing another glob against it."""
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("__any__/")
            i += 3
        elif pattern.startswith("**", i):
            out.append("__any__")
            i += 2
        elif pattern[i] == "*":
            out.append("__any__")
            i += 1
        elif pattern[i] == "?":
            out.append("x")
            i += 1
        elif pattern[i] == "[":
            close = pattern.find("]", i)
            if close == -1:
                out.append(pattern[i])
                i += 1
            else:
                inner = pattern[i + 1:close]
                if inner.startswith(("!", "^")):
                    excluded = inner[1:]
                    out.append("x" if "x" not in excluded else "y")
                else:
                    out.append(inner[0] if inner else "x")
                i = close + 1
        else:
            out.append(pattern[i])
            i += 1
    probe = "".join(out)
    return probe.rstrip("/") if not has_wildcard(pattern) else probe


def covers(pattern, other):
    """True when `pattern` reaches the paths `other` names."""
    return bool(glob_regex(pattern).match(probe_path(other)))


# Characters a witness may be built from. Short on purpose: it only has to
# produce one path both globs match, never every path either of them matches.
ALPHABET = "abcxyz01._-"


def _tokens(pattern):
    """The glob as single-step matchers, so two of them can be unified."""
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**", i):
            out.append(("dstar", None))
            i += 2
        elif pattern[i] == "*":
            out.append(("star", None))
            i += 1
        elif pattern[i] == "?":
            out.append(("cls", re.compile(r"[^/]")))
            i += 1
        elif pattern[i] == "[":
            close = pattern.find("]", i)
            if close == -1:
                out.append(("lit", "["))
                i += 1
            else:
                body = pattern[i + 1:close]
                if body.startswith("!"):
                    body = "^" + body[1:]
                out.append(("cls", re.compile("[" + body + "]")))
                i = close + 1
        else:
            out.append(("lit", pattern[i]))
            i += 1
    return out


def _one_char(token, allow_slash):
    """A character this token can match, or None."""
    kind, value = token
    if kind == "lit":
        return value if (allow_slash or value != "/") else None
    for ch in ALPHABET:
        if value.match(ch):
            return ch
    return None


def _shared_char(ta, tb):
    """A character both tokens match, or None."""
    if ta[0] == "lit" and tb[0] == "lit":
        return ta[1] if ta[1] == tb[1] else None
    if ta[0] == "lit":
        return ta[1] if tb[1].match(ta[1]) else None
    if tb[0] == "lit":
        return tb[1] if ta[1].match(tb[1]) else None
    for ch in ALPHABET:
        if ta[1].match(ch) and tb[1].match(ch):
            return ch
    return None


def _nullable(tokens):
    return all(kind in ("star", "dstar") for kind, _ in tokens)


def _unify(a, b):
    """One concrete path both token lists match, or None.

    Two globs can reach one file without either containing the other:
    `src/a*.py` and `src/*b.py` both reach `src/ab.py`. Comparing each glob
    against a path drawn from the other misses that, because neither drawn path
    happens to satisfy the other's literals. This builds the path from both
    patterns at once instead.
    """
    memo = {}

    def go(i, j):
        if (i, j) in memo:
            return memo[(i, j)]
        memo[(i, j)] = None  # a cycle contributes nothing
        result = None
        if i == len(a) and j == len(b):
            result = ""
        elif i == len(a):
            result = "" if _nullable(b[j:]) else None
        elif j == len(b):
            result = "" if _nullable(a[i:]) else None
        else:
            ta, tb = a[i], b[j]
            if ta[0] in ("star", "dstar") or tb[0] in ("star", "dstar"):
                for ni, nj in ((i + 1, j), (i, j + 1)):
                    skipping = a if ni > i else b
                    if skipping[ni - 1 if ni > i else nj - 1][0] not in ("star", "dstar"):
                        continue
                    tail = go(ni, nj)
                    if tail is not None:
                        result = tail
                        break
                if result is None:
                    # A star absorbs one character the other side produces.
                    for star_in_a in (True, False):
                        wild, other, oj = ((ta, tb, True) if star_in_a
                                           else (tb, ta, False))
                        if wild[0] not in ("star", "dstar"):
                            continue
                        if other[0] in ("star", "dstar"):
                            continue
                        ch = _one_char(other, wild[0] == "dstar")
                        if ch is None:
                            continue
                        tail = go(i, j + 1) if oj else go(i + 1, j)
                        if tail is not None:
                            result = ch + tail
                            break
            else:
                ch = _shared_char(ta, tb)
                if ch is not None:
                    tail = go(i + 1, j + 1)
                    if tail is not None:
                        result = ch + tail
        memo[(i, j)] = result
        return result

    return go(0, 0)


def _forms(pattern):
    """The spellings a pattern reaches, so a bare directory reaches its subtree."""
    if has_wildcard(pattern):
        return [pattern]
    bare = pattern.rstrip("/")
    return [bare, bare + "/**"]


def witness(a, b):
    """A concrete path both globs match, or None.

    Every candidate is checked against `glob_regex`, which is the same code the
    boundary hook enforces with. A witness that does not survive that check is
    discarded, so [T5] never fails a team over a collision that cannot happen.
    """
    ra, rb = glob_regex(a), glob_regex(b)
    for fa in _forms(a):
        for fb in _forms(b):
            found = _unify(_tokens(fa), _tokens(fb))
            if not found or not ra.match(found) or not rb.match(found):
                continue
            if found.endswith("/"):
                # A witness naming a directory reads as a typo in the failure.
                named = found + "file"
                if ra.match(named) and rb.match(named):
                    return named
            return found
    return None


def overlap(a, b):
    """'equal', 'a' when a contains b, 'b' when b contains a, 'partial', or None."""
    if a == b:
        return "equal"
    a_covers_b = covers(a, b)
    b_covers_a = covers(b, a)
    if a_covers_b and b_covers_a:
        return "equal"
    if a_covers_b:
        return "a"
    if b_covers_a:
        return "b"
    return "partial" if witness(a, b) else None


def normalise(pattern):
    """One spelling per path.

    `./src/**` and `src/**` reach the same files and compared as unequal, so two
    lanes owning one tree passed [T5] whenever they spelled it differently.
    """
    p = re.sub(r"/{2,}", "/", pattern.strip().strip("`"))
    while p.startswith("./"):
        p = p[2:]
    return p.rstrip("/") or p


def owns_entries(lines):
    """The raw text of each bullet under `## Owns`, before normalisation."""
    out = []
    for line in section(lines, "## Owns"):
        m = re.match(r"^\s*[-*]\s+(\S+)", line)
        if m:
            out.append(m.group(1).strip("`"))
    return out


def owned_paths(path):
    return [normalise(e) for e in owns_entries(read_lines(path))]


LOST_WORK = "Two members editing one path lose work silently."


def check_lane_disjoint(root, rep):
    owned = []
    for path in role_files(root):
        lane = os.path.basename(path)[:-3]
        for pattern in owned_paths(path):
            owned.append((lane, pattern))
    for i, (lane_a, pat_a) in enumerate(owned):
        for lane_b, pat_b in owned[i + 1:]:
            if lane_a == lane_b:
                continue
            verdict = overlap(pat_a, pat_b)
            if verdict is None:
                continue
            if verdict == "equal":
                rep.fail("T5", "roles/", 0,
                         f"{sorted([lane_a, lane_b])} both own {pat_a!r}. {LOST_WORK}")
            elif verdict == "partial":
                rep.fail("T5", "roles/", 0,
                         f"{pat_a!r} ({lane_a}) and {pat_b!r} ({lane_b}) both reach "
                         f"{witness(pat_a, pat_b)!r}. Neither contains the other, so "
                         f"the overlap is only the files in between. {LOST_WORK}")
            else:
                outer, inner = ((pat_a, lane_a), (pat_b, lane_b))
                if verdict == "b":
                    outer, inner = inner, outer
                rep.fail("T5", "roles/", 0,
                         f"{outer[0]!r} ({outer[1]}) contains {inner[0]!r} "
                         f"({inner[1]}). {LOST_WORK}")


SHARED_OWNER = re.compile(
    r"^\s*[-*]\s+(\S+).*?\bowned by\s+([A-Za-z0-9][A-Za-z0-9_-]*)", re.I)


def check_shared_paths(root, rep):
    """A shared path is owned by exactly one lane, and [T5] never sees it.

    [T5] compares role against role. The charter can hand a lockfile to `api`
    while `web`'s role owns `**/*.json`, and both files pass on their own.

    The owner's role must claim the path too. The boundary hook reads role files
    and nothing else, so a shared path named only in the charter is a path the
    hook attributes to no lane and therefore lets every lane write.
    """
    charter = os.path.join(root, "charter.md")
    if not os.path.exists(charter):
        return
    lanes = set(charter_lanes(root))
    by_lane = {os.path.basename(p)[:-3]: owned_paths(p) for p in role_files(root)}
    for line in section(read_lines(charter), "## Shared paths"):
        if not re.match(r"^\s*[-*]\s+\S", line):
            continue
        m = SHARED_OWNER.match(line)
        if not m:
            rep.fail("T11", "charter.md", 0,
                     f"shared path line {line.strip()!r} names no owner. Write it as "
                     "'- <path> \u2014 owned by <lane>'. An unowned shared path is where "
                     "two lanes collide first.")
            continue
        pattern, owner = normalise(m.group(1)), m.group(2)
        if owner not in lanes:
            rep.fail("T11", "charter.md", 0,
                     f"shared path {pattern!r} is owned by {owner!r}, which is not a "
                     "lane under '## Lanes'. Nobody owns it.")
        elif not any(covers(claimed, pattern) for claimed in by_lane.get(owner, [])):
            rep.fail("T11", "charter.md", 0,
                     f"shared path {pattern!r} is owned by {owner!r}, but "
                     f"roles/{owner}.md does not claim it under '## Owns'. The "
                     "boundary hook reads role files only, so it attributes this "
                     "path to no lane and allows every lane to write it. Declaring "
                     "an owner is not giving one.")
        for lane in sorted(by_lane):
            if lane == owner:
                continue
            for claimed in by_lane[lane]:
                if overlap(claimed, pattern):
                    rep.fail("T11", "charter.md", 0,
                             f"shared path {pattern!r} is owned by {owner!r}, but "
                             f"roles/{lane}.md owns {claimed!r}, which reaches it. "
                             + LOST_WORK)


# Verified against the platform: it refuses these two as teammate names, and it
# does so at spawn time, hours after the team was declared valid.
RESERVED_LANES = {"main", "team-lead"}
LANE_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def check_lane_names(root, rep):
    lanes = set(charter_lanes(root)) | {
        os.path.basename(p)[:-3] for p in role_files(root)}
    for lane in sorted(lanes):
        if lane in RESERVED_LANES:
            rep.fail("T12", "charter.md", 0,
                     f"lane {lane!r} is reserved by the platform and cannot be a "
                     "teammate name. The spawn fails, and the member cannot diagnose "
                     "it from the contracts.")
        elif not LANE_NAME.match(lane):
            rep.fail("T12", "charter.md", 0,
                     f"lane {lane!r} is not usable as an address. Lane names are "
                     "lowercase letters, digits and hyphens: case and underscores "
                     "survive in some places and not others.")


def check_tracker_named(root, rep):
    path = os.path.join(root, "tracker.md")
    if not os.path.exists(path):
        rep.fail("T6", "tracker.md", 0, "missing. Work items need one named home.")
        return
    text = "\n".join(read_lines(path))
    for field in ("Backend:", "Create:", "Claim:", "Close:"):
        if not re.search(rf"^[ \t]*{re.escape(field)}[ \t]*\S", text, re.M):
            rep.fail("T6", "tracker.md", 0,
                     f"no {field!r} line carrying a command. A member that cannot "
                     "file a bug in one step will drop it.")
    backends = re.findall(r"^[ \t]*Backend:", text, re.M)
    if len(backends) > 1:
        rep.fail("T6", "tracker.md", 0,
                 "more than one 'Backend:'. One store, or there are two places to look.")


def check_transport_named(root, rep):
    path = os.path.join(root, "transport.md")
    if not os.path.exists(path):
        rep.fail("T10", "transport.md", 0,
                 "missing. Every member loads it at startup to learn how to reach "
                 "the others, so without it the team is a list of strangers.")
        return
    text = "\n".join(read_lines(path))
    for field in ("Substrate:", "Discover:", "Send:"):
        if not re.search(rf"^[ \t]*{re.escape(field)}[ \t]*\S", text, re.M):
            rep.fail("T10", "transport.md", 0,
                     f"no {field!r} line carrying a value. A member that cannot "
                     "address the others will write prose instead of a message.")
    if len(re.findall(r"^[ \t]*Substrate:", text, re.M)) > 1:
        rep.fail("T10", "transport.md", 0,
                 "more than one 'Substrate:'. One substrate, or the members that "
                 "chose the other one are unreachable.")


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
                     "edited: a paraphrase is how a shared rule stops being shared. "
                     f"Re-copy it from {ref}. A member that already loaded the old "
                     "copy needs a RELOAD to pick this one up; a member not yet "
                     "launched reads it for the first time and needs nothing.")


def check_friction_cap(root, rep):
    path = os.path.join(root, "friction.md")
    if not os.path.exists(path):
        rep.warn("T8", "friction.md",
                 "missing. A team with no friction file and a team whose lead never "
                 "opened one look identical, and the retro trigger is the second one.")
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
        refs_dir = (os.path.join(plugin_root, "skills", "team-member", "references")
                    if plugin_root else PLUGIN_REFS)

    rep = Report(args.quiet)
    check_budgets(root, rep)
    check_role_shape(root, rep)
    check_no_log(root, rep)
    check_roster_closure(root, rep)
    check_lane_disjoint(root, rep)
    check_tracker_named(root, rep)
    check_transport_named(root, rep)
    check_verbatim(root, rep, refs_dir)
    check_friction_cap(root, rep)
    check_team_root(root, rep)
    check_shared_paths(root, rep)
    check_lane_names(root, rep)
    return rep.emit()


if __name__ == "__main__":
    sys.exit(main())
