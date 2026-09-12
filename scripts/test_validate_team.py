#!/usr/bin/env python3
"""Tests for validate_team.py.

Each test builds a well-formed team root, breaks exactly one thing, and asserts
that the matching check is the one that fires. Run: python3 test_validate_team.py
"""

import io
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validate_team  # noqa: E402


PROTOCOL = "# Team protocol\n\nThis file is copied, never edited.\n"
CONFLICTS = "# When a conflict happens\n\nRead this when one actually does.\n"

CHARTER = """# Ship the widget service

Team root: {root}

## Lanes
- api — the service and its migrations
- ui — the console

## Working rules
- A lane that cannot start says so rather than reaching into another lane.

## Human gates
- Anything that writes to production.

## Done
- The console drives the service end to end.
"""

ROLE_API = """# api

## Owns
- src/api/**
- migrations/**

## Never
- Edit src/ui. Two members editing one path lose work silently.

## Hands off to
- ui, once an endpoint answers.

## Done means
- The endpoint answers and its test passes.
"""

ROLE_UI = """# ui

## Owns
- src/ui/**

## Never
- Edit src/api. The api lane owns its own shape.

## Hands off to
- api, when the console needs a field that does not exist.

## Done means
- The console renders against a running service.
"""

TRACKER = """# Where work items live

Backend: GitHub issues
Create: gh issue create --label widget
Claim: gh issue edit <n> --add-assignee @me
Close: gh issue close <n>
"""

TRANSPORT = """# How members reach each other

Substrate: cross-session
Discover: ListAgents
Send: SendMessage to the lane name
"""


def build(root):
    os.makedirs(os.path.join(root, "roles"))
    write(root, "protocol.md", PROTOCOL)
    write(root, "conflicts.md", CONFLICTS)
    write(root, "charter.md", CHARTER.format(root=root))
    write(root, "tracker.md", TRACKER)
    write(root, "transport.md", TRANSPORT)
    write(root, "roles/api.md", ROLE_API)
    write(root, "roles/ui.md", ROLE_UI)
    refs = os.path.join(root, "_plugin_refs")
    os.makedirs(refs)
    with open(os.path.join(refs, "protocol.md"), "w", encoding="utf-8") as fh:
        fh.write(PROTOCOL)
    with open(os.path.join(refs, "conflicts.md"), "w", encoding="utf-8") as fh:
        fh.write(CONFLICTS)
    return refs


def write(root, rel, text):
    path = os.path.join(root, rel)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def append(root, rel, text):
    with open(os.path.join(root, rel), "a", encoding="utf-8") as fh:
        fh.write(text)


class TeamRootCase(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.refs = build(self.root)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def run_validator(self):
        buf = io.StringIO()
        with redirect_stderr(buf):
            code = validate_team.main([self.root, "--refs", self.refs, "--quiet"])
        return code, buf.getvalue()


class TestValid(TeamRootCase):
    def test_well_formed_root_passes(self):
        code, out = self.run_validator()
        self.assertEqual(code, 0, out)
        self.assertNotIn("FAIL", out)

    def test_missing_charter_is_exit_two(self):
        os.remove(os.path.join(self.root, "charter.md"))
        code, _ = self.run_validator()
        self.assertEqual(code, 2)


class TestT1Budgets(TeamRootCase):
    def test_oversized_charter_fails(self):
        append(self.root, "charter.md", "\n".join("- filler" for _ in range(60)))
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("[T1]", out)
        self.assertIn("budget 50", out)

    def test_oversized_role_fails(self):
        append(self.root, "roles/api.md", "\n".join("- filler" for _ in range(40)))
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("[T1]", out)
        self.assertIn("roles/api.md", out)


class TestT2RoleShape(TeamRootCase):
    def test_missing_heading_fails(self):
        write(self.root, "roles/ui.md", ROLE_UI.replace("## Never", "## Avoid"))
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("[T2]", out)
        self.assertIn("## Never", out)

    def test_empty_never_fails(self):
        write(self.root, "roles/ui.md",
              ROLE_UI.replace("- Edit src/api. The api lane owns its own shape.\n", ""))
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("[T2]", out)
        self.assertIn("no prohibition", out)


class TestT3NoLog(TeamRootCase):
    def test_date_fails(self):
        append(self.root, "charter.md", "\nLane api started on 2026-09-12.\n")
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("[T3]", out)
        self.assertIn("a date", out)

    def test_checkbox_fails(self):
        append(self.root, "charter.md", "\n- [x] endpoint answers\n")
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("a checkbox", out)

    def test_issue_id_fails(self):
        append(self.root, "charter.md", "\nThe api lane is working on #412 now.\n")
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("an issue id", out)

    def test_past_tense_progress_fails(self):
        append(self.root, "charter.md", "\nThe ui lane completed the console shell.\n")
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("past-tense", out)

    def test_decisions_may_cite_a_ticket(self):
        write(self.root, "decisions.md",
              "# Decisions\n\nOne worktree per lane, because PROJ-88 showed a "
              "shared build dir collides.\n")
        code, out = self.run_validator()
        self.assertEqual(code, 0, out)

    def test_decisions_may_not_carry_a_date(self):
        write(self.root, "decisions.md", "# Decisions\n\nDecided on 2026-09-12.\n")
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("a date", out)

    def test_backticked_example_is_not_a_tell(self):
        append(self.root, "tracker.md", "\nExample: `gh issue view #412`\n")
        code, out = self.run_validator()
        self.assertEqual(code, 0, out)

    def test_a_backtick_cannot_launder_the_rest_of_the_line(self):
        """One backticked word used to exempt the whole line from every tell."""
        append(self.root, "charter.md",
               "\nThe api lane `shipped` the endpoint on 2026-09-01.\n")
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("[T3]", out)
        self.assertIn("a date", out)

    def test_a_status_field_outside_backticks_is_still_a_tell(self):
        append(self.root, "charter.md", "\nStatus: ui is `blocked` on api.\n")
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("a status field", out)


class TestT4RosterClosure(TeamRootCase):
    def test_lane_without_role_file_fails(self):
        append(self.root, "charter.md", "")
        write(self.root, "charter.md",
              CHARTER.format(root=self.root).replace(
                  "- ui — the console", "- ui — the console\n- worker — the queue"))
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("[T4]", out)
        self.assertIn("roles/worker.md", out)

    def test_role_file_not_in_charter_fails(self):
        write(self.root, "roles/worker.md", ROLE_UI.replace("src/ui", "src/worker"))
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("[T4]", out)
        self.assertIn("not listed", out)


class TestT5LaneDisjoint(TeamRootCase):
    def test_two_roles_owning_one_path_fails(self):
        write(self.root, "roles/ui.md", ROLE_UI.replace("src/ui/**", "src/api/**"))
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("[T5]", out)
        self.assertIn("src/api", out)

    def test_containment_fails(self):
        write(self.root, "roles/ui.md", ROLE_UI.replace("src/ui/**", "src/**"))
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("[T5]", out)
        self.assertIn("contains", out)

    def test_sibling_paths_pass(self):
        code, out = self.run_validator()
        self.assertEqual(code, 0, out)

    def test_globs_with_no_literal_prefix_do_not_collide(self):
        """Two lanes owning `**/*.sql` and `**/*.css` are disjoint.

        Truncating each glob at its first wildcard made both of them the empty
        prefix, which failed a valid team and named no path to fix.
        """
        write(self.root, "roles/api.md", ROLE_API.replace("- migrations/**", "- **/*.sql"))
        write(self.root, "roles/ui.md", ROLE_UI.replace("- src/ui/**", "- src/ui/**\n- **/*.css"))
        code, out = self.run_validator()
        self.assertEqual(code, 0, out)

    def test_a_leading_wildcard_glob_still_catches_a_real_overlap(self):
        write(self.root, "roles/api.md", ROLE_API.replace("- migrations/**", "- **/*.sql"))
        write(self.root, "roles/ui.md",
              ROLE_UI.replace("- src/ui/**", "- src/ui/**\n- migrations/schema.sql"))
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("[T5]", out)
        self.assertIn("migrations/schema.sql", out)

    def test_a_negated_class_is_read_as_a_negation(self):
        """`[!a]` excludes `a` in a glob; passing it to regex unchanged included it."""
        write(self.root, "roles/api.md", ROLE_API.replace("- migrations/**", "- log[!s]/**"))
        write(self.root, "roles/ui.md", ROLE_UI.replace("- src/ui/**", "- src/ui/**\n- logs/**"))
        code, out = self.run_validator()
        self.assertEqual(code, 0, out)

    def test_a_bare_directory_contains_a_glob_beneath_it(self):
        write(self.root, "roles/ui.md", ROLE_UI.replace("- src/ui/**", "- src"))
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("contains", out)


class TestT2HeadingOrder(TeamRootCase):
    def test_headings_out_of_order_fails(self):
        write(self.root, "roles/ui.md", """# ui

## Done means
- The console renders against a running service.

## Owns
- src/ui/**

## Never
- Edit src/api. The api lane owns its own shape.

## Hands off to
- api, when the console needs a field that does not exist.
""")
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("[T2]", out)
        self.assertIn("out of order", out)


class TestT6TrackerNamed(TeamRootCase):
    def test_missing_tracker_fails(self):
        os.remove(os.path.join(self.root, "tracker.md"))
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("[T6]", out)

    def test_missing_claim_line_fails(self):
        write(self.root, "tracker.md",
              TRACKER.replace("Claim: gh issue edit <n> --add-assignee @me\n", ""))
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("Claim:", out)

    def test_label_without_a_command_fails(self):
        write(self.root, "tracker.md",
              "Backend: GitHub issues\nCreate:\nClaim: gh issue edit <n>\n"
              "Close: gh issue close <n>\n")
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("Create:", out)
        self.assertIn("carrying a command", out)

    def test_two_backends_fail(self):
        append(self.root, "tracker.md", "Backend: a file board\n")
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("two places to look", out)


class TestT7Verbatim(TeamRootCase):
    def test_paraphrased_protocol_fails(self):
        write(self.root, "protocol.md", PROTOCOL + "\nAlso, be nice.\n")
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("[T7]", out)

    def test_missing_reference_warns_but_passes(self):
        buf = io.StringIO()
        with redirect_stderr(buf):
            code = validate_team.main([self.root, "--quiet"])
        out = buf.getvalue()
        self.assertEqual(code, 0, out)
        self.assertIn("warning [T7]", out)

    def test_missing_protocol_fails(self):
        os.remove(os.path.join(self.root, "protocol.md"))
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("[T7]", out)

    def test_paraphrased_conflicts_fails(self):
        write(self.root, "conflicts.md", CONFLICTS + "\nOr just talk it out.\n")
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("[T7]", out)
        self.assertIn("conflicts.md", out)

    def test_missing_conflicts_fails(self):
        os.remove(os.path.join(self.root, "conflicts.md"))
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("conflicts.md", out)


class TestT10TransportNamed(TeamRootCase):
    def test_missing_transport_fails(self):
        os.remove(os.path.join(self.root, "transport.md"))
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("[T10]", out)

    def test_missing_send_line_fails(self):
        write(self.root, "transport.md",
              TRANSPORT.replace("Send: SendMessage to the lane name\n", ""))
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("Send:", out)

    def test_two_substrates_fail(self):
        append(self.root, "transport.md", "Substrate: claude-chat\n")
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("unreachable", out)


class TestT8FrictionCap(TeamRootCase):
    def test_friction_at_cap_warns_without_failing(self):
        write(self.root, "friction.md",
              "\n".join(f"- rule {i} cost a turn" for i in range(30)))
        code, out = self.run_validator()
        self.assertEqual(code, 0, out)
        self.assertIn("warning [T8]", out)
        self.assertIn("retro is due", out)

    def test_short_friction_is_silent(self):
        write(self.root, "friction.md", "- one note\n")
        code, out = self.run_validator()
        self.assertEqual(code, 0, out)
        self.assertNotIn("[T8]", out)


class TestT9TeamRoot(TeamRootCase):
    def test_missing_team_root_line_fails(self):
        write(self.root, "charter.md",
              CHARTER.format(root=self.root).replace(f"Team root: {self.root}\n", ""))
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("[T9]", out)

    def test_relative_team_root_fails(self):
        write(self.root, "charter.md",
              CHARTER.format(root=self.root).replace(
                  f"Team root: {self.root}", "Team root: .teamwork"))
        code, out = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("resolves differently in every worktree", out)

    def test_stale_worktree_copy_fails(self):
        other = tempfile.mkdtemp()
        try:
            write(self.root, "charter.md",
                  CHARTER.format(root=self.root).replace(
                      f"Team root: {self.root}", f"Team root: {other}"))
            code, out = self.run_validator()
            self.assertEqual(code, 1)
            self.assertIn("editing a copy", out)
        finally:
            shutil.rmtree(other, ignore_errors=True)


PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestPluginPaths(unittest.TestCase):
    """Every ${CLAUDE_PLUGIN_ROOT}/... path the plugin prints must exist.

    A path written for a reader to follow is a promise, and the working directory
    at runtime is the user's project, so a broken one fails silently there.
    """

    def test_every_plugin_path_resolves(self):
        import re
        pattern = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]+)")
        missing = []
        for dirpath, dirnames, filenames in os.walk(PLUGIN_ROOT):
            dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
            for name in filenames:
                if not name.endswith((".md", ".py", ".json")):
                    continue
                full = os.path.join(dirpath, name)
                with open(full, encoding="utf-8") as fh:
                    text = fh.read()
                for rel in pattern.findall(text):
                    if "..." in rel:
                        continue  # a placeholder in prose, not a path
                    if not os.path.exists(os.path.join(PLUGIN_ROOT, rel)):
                        missing.append(f"{os.path.relpath(full, PLUGIN_ROOT)} -> {rel}")
        self.assertEqual(missing, [], "plugin paths that do not resolve: " + repr(missing))

    def test_verbatim_files_are_within_their_budgets(self):
        for name, budget in (("protocol.md", 45), ("conflicts.md", 30)):
            path = os.path.join(PLUGIN_ROOT, "skills", "team-member", "references", name)
            with open(path, encoding="utf-8") as fh:
                n = len(fh.read().splitlines())
            self.assertLessEqual(n, budget, f"{name} is {n} lines, budget {budget}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
