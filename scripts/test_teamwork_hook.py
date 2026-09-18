#!/usr/bin/env python3
"""Tests for teamwork_hook.py.

Each test builds a team root inside a git repo, sends the hook one real event
payload, and asserts on the decision. Run: python3 test_teamwork_hook.py
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "teamwork_hook.py")

CHARTER = """# Ship billing

Team root: {root}
Team name: billing
Workspace: one worktree per lane

## Lanes
- api - the billing service
- web - the dashboard

## Working rules
- The flag defaults off, or an unfinished feature reaches users.

## Human gates
- Any migration against production.

## Done
- Both lanes' tests pass.
"""

ROLE_API = """# api

## Owns
- services/billing/**
- db/migrations/**

## Never
- Edit web/. Two members editing one path lose work silently.

## Hands off to
- web, when a response shape changes.

## Done means
- `pytest services/billing` passes.
"""

ROLE_WEB = """# web

## Owns
- web/**

## Never
- Edit a migration. Schema is api's.

## Hands off to
- Nobody; this lane is a leaf.

## Done means
- `npm test` passes.
"""


def run(payload, env=None):
    full = dict(os.environ)
    full.pop("TEAMWORK_LANE", None)
    full.pop("TEAMWORK_ROOT", None)
    full.update(env or {})
    p = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                       capture_output=True, text=True, env=full)
    out = {}
    if p.stdout.strip():
        out = json.loads(p.stdout)
    return out.get("hookSpecificOutput", {}), p.stderr


class HookCase(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.root = os.path.join(self.repo, ".teamwork")
        os.makedirs(os.path.join(self.root, "roles"))
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        self.write(".teamwork/charter.md", CHARTER.format(root=self.root))
        self.write(".teamwork/roles/api.md", ROLE_API)
        self.write(".teamwork/roles/web.md", ROLE_WEB)

    def tearDown(self):
        shutil.rmtree(self.repo, ignore_errors=True)

    def write(self, rel, text):
        path = os.path.join(self.repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    def edit(self, rel, lane="api", tool="Write"):
        return run({"hook_event_name": "PreToolUse", "cwd": self.repo,
                    "tool_name": tool,
                    "tool_input": {"file_path": os.path.join(self.repo, rel)}},
                   env={"TEAMWORK_LANE": lane, "TEAMWORK_ROOT": self.root})


class TestBoundary(HookCase):
    def test_a_lane_may_write_its_own_path(self):
        out, _ = self.edit("services/billing/charge.py", lane="api")
        self.assertEqual(out, {})

    def test_a_lane_may_not_write_another_lanes_path(self):
        out, _ = self.edit("web/dashboard.tsx", lane="api")
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("belongs to the web lane", out["permissionDecisionReason"])
        self.assertIn("ASK web", out["permissionDecisionReason"])

    def test_the_other_direction_too(self):
        out, _ = self.edit("db/migrations/003.sql", lane="web")
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("belongs to the api lane", out["permissionDecisionReason"])

    def test_an_unowned_path_is_allowed(self):
        """conflicts.md gives an unowned path to the lead, not to a blocker."""
        out, _ = self.edit("README.md", lane="api")
        self.assertEqual(out, {})

    def test_no_member_writes_the_team_root(self):
        out, _ = self.edit(".teamwork/charter.md", lane="api")
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("rule 5", out["permissionDecisionReason"])

    def test_edit_and_notebook_targets_are_read_too(self):
        out, _ = self.edit("web/app.tsx", lane="api", tool="Edit")
        self.assertEqual(out.get("permissionDecision"), "deny")
        out, _ = run({"hook_event_name": "PreToolUse", "cwd": self.repo,
                      "tool_name": "NotebookEdit",
                      "tool_input": {"notebook_path": os.path.join(self.repo, "web/x.ipynb")}},
                     env={"TEAMWORK_LANE": "api", "TEAMWORK_ROOT": self.root})
        self.assertEqual(out.get("permissionDecision"), "deny")

    def test_a_path_outside_the_repo_is_allowed(self):
        out, _ = run({"hook_event_name": "PreToolUse", "cwd": self.repo,
                      "tool_name": "Write",
                      "tool_input": {"file_path": "/tmp/scratch-note.txt"}},
                     env={"TEAMWORK_LANE": "api", "TEAMWORK_ROOT": self.root})
        self.assertEqual(out, {})


class TestFailsOpen(HookCase):
    def test_a_session_with_no_lane_is_never_blocked(self):
        """The lead, and any session not on a team, must not be stopped."""
        out, _ = run({"hook_event_name": "PreToolUse", "cwd": self.repo,
                      "tool_name": "Write",
                      "tool_input": {"file_path": os.path.join(self.repo, "web/x.tsx")}},
                     env={"TEAMWORK_ROOT": self.root})
        self.assertEqual(out, {})

    def test_a_session_with_no_team_root_is_never_blocked(self):
        plain = tempfile.mkdtemp()
        try:
            out, _ = run({"hook_event_name": "PreToolUse", "cwd": plain,
                          "tool_name": "Write",
                          "tool_input": {"file_path": os.path.join(plain, "x.py")}})
            self.assertEqual(out, {})
        finally:
            shutil.rmtree(plain, ignore_errors=True)

    def test_malformed_input_is_never_blocking(self):
        p = subprocess.run([sys.executable, HOOK], input="not json",
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(p.stdout.strip(), "")

    def test_an_unknown_lane_name_does_not_resolve(self):
        out, _ = self.edit("web/x.tsx", lane="nosuchlane")
        self.assertEqual(out, {})


class TestLaneResolution(HookCase):
    def test_the_worktree_name_resolves_a_lane(self):
        worktree = os.path.join(self.repo, "web")
        os.makedirs(worktree, exist_ok=True)
        subprocess.run(["git", "init", "-q"], cwd=worktree, check=True)
        out, _ = run({"hook_event_name": "PreToolUse", "cwd": worktree,
                      "tool_name": "Write",
                      "tool_input": {"file_path": os.path.join(worktree, "db/migrations/1.sql")}},
                     env={"TEAMWORK_ROOT": self.root})
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("You are web", out["permissionDecisionReason"])

    def test_a_shared_tree_does_not_resolve_by_directory(self):
        self.write(".teamwork/charter.md",
                   CHARTER.format(root=self.root).replace(
                       "one worktree per lane", "one shared tree"))
        worktree = os.path.join(self.repo, "web")
        os.makedirs(worktree, exist_ok=True)
        subprocess.run(["git", "init", "-q"], cwd=worktree, check=True)
        out, _ = run({"hook_event_name": "PreToolUse", "cwd": worktree,
                      "tool_name": "Write",
                      "tool_input": {"file_path": os.path.join(worktree, "db/migrations/1.sql")}},
                     env={"TEAMWORK_ROOT": self.root})
        self.assertEqual(out, {})


class TestTeamRootResolution(HookCase):
    """Which copy of the team root the hook enforces against."""

    def worktree(self, lane):
        """A real linked worktree carrying its own committed copy of the root."""
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                        "commit", "-qm", "team"], cwd=self.repo, check=True)
        path = os.path.join(tempfile.mkdtemp(), lane)
        subprocess.run(["git", "worktree", "add", "-q", "-b", lane, path],
                       cwd=self.repo, check=True)
        self.addCleanup(shutil.rmtree, os.path.dirname(path), ignore_errors=True)
        return path

    def test_teamwork_root_wins_over_anything_on_disk(self):
        """Rung 1. The launch command sets it, and nothing overrides it."""
        out, _ = run({"hook_event_name": "SessionStart", "cwd": tempfile.gettempdir()},
                     env={"TEAMWORK_LANE": "api", "TEAMWORK_ROOT": self.root})
        self.assertIn(self.root, out.get("additionalContext", ""))

    def test_a_worktree_is_enforced_against_the_main_copy(self):
        """Rung 2. Its own copy is last week's rules; the main one is the law."""
        tree = self.worktree("web")
        stale = os.path.join(tree, ".teamwork", "roles", "web.md")
        with open(stale, "w", encoding="utf-8") as fh:
            fh.write(ROLE_WEB.replace("- web/**", "- db/migrations/**"))
        out, _ = run({"hook_event_name": "PreToolUse", "cwd": tree,
                      "tool_name": "Write",
                      "tool_input": {"file_path": os.path.join(tree, "db/migrations/1.sql")}})
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("belongs to the api lane", out["permissionDecisionReason"])

    def test_the_startup_note_names_the_main_copy(self):
        tree = self.worktree("web")
        out, _ = run({"hook_event_name": "SessionStart", "cwd": tree})
        self.assertIn(self.root, out.get("additionalContext", ""))

    def test_a_worktrees_own_copy_is_not_writable_either(self):
        """It is not the team root, but editing it is still editing a contract."""
        tree = self.worktree("web")
        out, _ = run({"hook_event_name": "PreToolUse", "cwd": tree,
                      "tool_name": "Write",
                      "tool_input": {"file_path": os.path.join(tree, ".teamwork/charter.md")}},
                     env={"TEAMWORK_LANE": "web"})
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("in the team root", out["permissionDecisionReason"])

    def test_walking_up_still_finds_a_root_outside_git(self):
        """Rung 3. A team root can sit where git knows nothing about it."""
        plain = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, plain, ignore_errors=True)
        root = os.path.join(plain, ".teamwork")
        os.makedirs(os.path.join(root, "roles"))
        with open(os.path.join(root, "charter.md"), "w", encoding="utf-8") as fh:
            fh.write(CHARTER.format(root=root))
        with open(os.path.join(root, "roles", "api.md"), "w", encoding="utf-8") as fh:
            fh.write(ROLE_API)
        nested = os.path.join(plain, "src", "deep")
        os.makedirs(nested)
        out, _ = run({"hook_event_name": "SessionStart", "cwd": nested},
                     env={"TEAMWORK_LANE": "api"})
        self.assertIn(root, out.get("additionalContext", ""))


ROLE_LEAD = """# lead

## Owns
- docs/**

## Never
- Take an item another lane waits on. The lead becomes the bottleneck.

## Hands off to
- Nobody; this lane is downstream of every other.

## Done means
- `docs/` describes every shipped endpoint.
"""


class TestWorkspaces(HookCase):
    """The four values of `Workspace:` decide what Owns globs are relative to."""

    def plain(self, workspace, lanes=(("api", ROLE_API), ("web", ROLE_WEB))):
        """A team root with no git anywhere, holding `lanes`."""
        base = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, base, ignore_errors=True)
        root = os.path.join(base, ".teamwork")
        os.makedirs(os.path.join(root, "roles"))
        charter = CHARTER.format(root=root).replace(
            "Workspace: one worktree per lane", f"Workspace: {workspace}")
        with open(os.path.join(root, "charter.md"), "w", encoding="utf-8") as fh:
            fh.write(charter)
        for lane, text in lanes:
            with open(os.path.join(root, "roles", f"{lane}.md"), "w",
                      encoding="utf-8") as fh:
                fh.write(text)
        return base, root

    def test_separate_directories_anchor_at_the_team_roots_parent(self):
        """No git at all, and the boundary still holds."""
        base, root = self.plain("separate directories")
        out, _ = run({"hook_event_name": "PreToolUse",
                      "cwd": os.path.join(base, "services"),
                      "tool_name": "Write",
                      "tool_input": {"file_path": os.path.join(base, "web/app.tsx")}},
                     env={"TEAMWORK_LANE": "api", "TEAMWORK_ROOT": root})
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("belongs to the web lane", out["permissionDecisionReason"])

    def test_a_lane_still_writes_its_own_paths_without_git(self):
        base, root = self.plain("separate directories")
        out, _ = run({"hook_event_name": "PreToolUse", "cwd": base,
                      "tool_name": "Write",
                      "tool_input": {"file_path": os.path.join(base,
                                                               "services/billing/x.py")}},
                     env={"TEAMWORK_LANE": "api", "TEAMWORK_ROOT": root})
        self.assertEqual(out, {})

    def test_separate_repositories_are_read_from_the_shared_parent(self):
        """Anchoring at the enclosing repo would make every glob match nothing."""
        base, root = self.plain("separate repositories", lanes=(
            ("api", ROLE_API.replace("services/billing/**", "payments/**")
                            .replace("db/migrations/**", "payments/db/**")),
            ("web", ROLE_WEB)))
        for component in ("payments", "web"):
            os.makedirs(os.path.join(base, component), exist_ok=True)
            subprocess.run(["git", "init", "-q"],
                           cwd=os.path.join(base, component), check=True)
        out, _ = run({"hook_event_name": "PreToolUse",
                      "cwd": os.path.join(base, "payments"),
                      "tool_name": "Write",
                      "tool_input": {"file_path": os.path.join(base, "web/app.tsx")}},
                     env={"TEAMWORK_LANE": "api", "TEAMWORK_ROOT": root})
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("belongs to the web lane", out["permissionDecisionReason"])
        out, _ = run({"hook_event_name": "PreToolUse",
                      "cwd": os.path.join(base, "payments"),
                      "tool_name": "Write",
                      "tool_input": {"file_path": os.path.join(base,
                                                               "payments/charge.py")}},
                     env={"TEAMWORK_LANE": "api", "TEAMWORK_ROOT": root})
        self.assertEqual(out, {})

    def test_the_old_isolation_line_still_resolves_a_worktree_lane(self):
        """A team formed before the rename keeps its second lane rung."""
        self.write(".teamwork/charter.md",
                   CHARTER.format(root=self.root).replace(
                       "Workspace: one worktree per lane",
                       "Isolation: one worktree per lane"))
        worktree = os.path.join(self.repo, "web")
        os.makedirs(worktree, exist_ok=True)
        subprocess.run(["git", "init", "-q"], cwd=worktree, check=True)
        out, _ = run({"hook_event_name": "PreToolUse", "cwd": worktree,
                      "tool_name": "Write",
                      "tool_input": {"file_path": os.path.join(worktree,
                                                               "db/migrations/1.sql")}},
                     env={"TEAMWORK_ROOT": self.root})
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("You are web", out["permissionDecisionReason"])


class TestLeadLane(HookCase):
    """A lead may hold a downstream lane, and it is the only one in the root."""

    def setUp(self):
        super().setUp()
        self.write(".teamwork/charter.md",
                   CHARTER.format(root=self.root).replace(
                       "- web - the dashboard",
                       "- web - the dashboard\n- lead - integration and docs"))
        self.write(".teamwork/roles/lead.md", ROLE_LEAD)

    def test_the_lead_lane_may_write_the_team_root(self):
        out, _ = self.edit(".teamwork/friction.md", lane="lead")
        self.assertEqual(out, {})

    def test_no_other_lane_may(self):
        out, _ = self.edit(".teamwork/friction.md", lane="api")
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("rule 5", out["permissionDecisionReason"])

    def test_the_lead_is_still_held_to_its_own_paths(self):
        out, _ = self.edit("web/app.tsx", lane="lead")
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("belongs to the web lane", out["permissionDecisionReason"])

    def test_a_member_may_not_write_the_leads_paths(self):
        """This is what the role file buys; without it docs/ is unowned."""
        out, _ = self.edit("docs/api.md", lane="api")
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("belongs to the lead lane", out["permissionDecisionReason"])

    def test_the_lead_writes_its_own_lane(self):
        out, _ = self.edit("docs/api.md", lane="lead")
        self.assertEqual(out, {})


class TestStartup(HookCase):
    def test_session_start_names_the_root_and_the_lane(self):
        out, _ = run({"hook_event_name": "SessionStart", "cwd": self.repo},
                     env={"TEAMWORK_LANE": "api", "TEAMWORK_ROOT": self.root})
        text = out.get("additionalContext", "")
        self.assertIn(self.root, text)
        self.assertIn("roles/api.md", text)

    def test_post_compact_says_it_again(self):
        out, _ = run({"hook_event_name": "PostCompact", "cwd": self.repo},
                     env={"TEAMWORK_LANE": "api", "TEAMWORK_ROOT": self.root})
        self.assertIn(self.root, out.get("additionalContext", ""))

    def test_a_session_with_no_lane_is_told_enforcement_is_off(self):
        out, _ = run({"hook_event_name": "SessionStart", "cwd": self.repo},
                     env={"TEAMWORK_ROOT": self.root})
        self.assertIn("allows every write", out.get("additionalContext", ""))

    def test_a_session_off_a_team_is_told_nothing(self):
        plain = tempfile.mkdtemp()
        try:
            out, _ = run({"hook_event_name": "SessionStart", "cwd": plain})
            self.assertEqual(out, {})
        finally:
            shutil.rmtree(plain, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
