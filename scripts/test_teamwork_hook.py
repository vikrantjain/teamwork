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
Isolation: one worktree per lane

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


class TestSessionEnd(HookCase):
    def test_uncommitted_work_is_named(self):
        self.write("services/billing/charge.py", "x = 1\n")
        _, err = run({"hook_event_name": "SessionEnd", "cwd": self.repo},
                     env={"TEAMWORK_LANE": "api", "TEAMWORK_ROOT": self.root})
        self.assertIn("uncommitted work", err)
        self.assertIn("api", err)

    def test_a_clean_tree_says_nothing(self):
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                        "commit", "-qm", "x"], cwd=self.repo, check=True)
        _, err = run({"hook_event_name": "SessionEnd", "cwd": self.repo},
                     env={"TEAMWORK_LANE": "api", "TEAMWORK_ROOT": self.root})
        self.assertEqual(err.strip(), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
