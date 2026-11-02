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
    full.pop("CLAUDE_PROJECT_DIR", None)
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

    def worktree(self, lane, parent=None):
        """A real linked worktree carrying its own committed copy of the root.

        It goes in a fresh directory, or under `parent` when given, which is
        where `claude --worktree` puts one: inside the main checkout.
        """
        if subprocess.run(["git", "rev-parse", "-q", "--verify", "HEAD"],
                          cwd=self.repo, capture_output=True).returncode != 0:
            subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
            subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                            "commit", "-qm", "team"], cwd=self.repo, check=True)
        if parent is None:
            parent = tempfile.mkdtemp()
            self.addCleanup(shutil.rmtree, parent, ignore_errors=True)
        path = os.path.realpath(os.path.join(parent, lane))
        subprocess.run(["git", "worktree", "add", "-q", "-b", lane, path],
                       cwd=self.repo, check=True)
        return path


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


class TestUnreadableGlob(HookCase):
    def test_one_unreadable_glob_leaves_every_other_lane_enforced(self):
        """[T2] fails the glob. The hook skips it rather than give up on the team."""
        self.write(".teamwork/roles/api.md",
                   ROLE_API.replace("db/migrations/**", "db/[]x"))
        out, _ = self.edit("web/app.tsx", lane="api")
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("belongs to the web lane", out["permissionDecisionReason"])


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


class TestLaneFromDirectoryName(HookCase):
    """Rung 2: a lane started without $TEAMWORK_LANE, identified by its directory.

    It applies wherever a lane has a tree of its own and the charter asks for
    that tree to carry the lane's name. Under one shared tree every lane's
    working directory is the same one, so the name answers for all of them and
    the rung must not fire.
    """

    def plain(self, workspace):
        base = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, base, ignore_errors=True)
        root = os.path.join(base, ".teamwork")
        os.makedirs(os.path.join(root, "roles"))
        with open(os.path.join(root, "charter.md"), "w", encoding="utf-8") as fh:
            fh.write(CHARTER.format(root=root).replace(
                "Workspace: one worktree per lane", f"Workspace: {workspace}"))
        for lane, text in (("api", ROLE_API), ("web", ROLE_WEB)):
            with open(os.path.join(root, "roles", f"{lane}.md"), "w",
                      encoding="utf-8") as fh:
                fh.write(text)
        return base, root

    def crossing(self, base, root, lane_dir):
        """The lane named by its directory reaching for the other lane's path."""
        os.makedirs(os.path.join(base, lane_dir), exist_ok=True)
        return run({"hook_event_name": "PreToolUse",
                    "cwd": os.path.join(base, lane_dir),
                    "tool_name": "Write",
                    "tool_input": {"file_path": os.path.join(base, "web/app.tsx")}},
                   env={"TEAMWORK_ROOT": root})

    def test_separate_directories_resolve_by_name(self):
        base, root = self.plain("separate directories")
        out, _ = self.crossing(base, root, "api")
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("You are api", out["permissionDecisionReason"])

    def test_separate_repositories_resolve_by_name(self):
        base, root = self.plain("separate repositories")
        out, _ = self.crossing(base, root, "api")
        self.assertEqual(out.get("permissionDecision"), "deny")

    def test_a_shared_tree_never_resolves_by_name(self):
        """Every lane's directory is the same one, so the name proves nothing."""
        base, root = self.plain("one shared tree")
        out, _ = self.crossing(base, root, "api")
        self.assertEqual(out, {})

    def test_a_directory_matching_no_lane_resolves_nothing(self):
        base, root = self.plain("separate directories")
        out, _ = self.crossing(base, root, "not-a-lane")
        self.assertEqual(out, {})

    def test_the_old_isolation_name_still_carries_the_rung(self):
        base, root = self.plain("separate directories")
        charter = os.path.join(root, "charter.md")
        with open(charter, encoding="utf-8") as fh:
            text = fh.read()
        with open(charter, "w", encoding="utf-8") as fh:
            fh.write(text.replace("Workspace: separate directories",
                                  "Isolation: separate directories"))
        out, _ = self.crossing(base, root, "api")
        self.assertEqual(out.get("permissionDecision"), "deny")

    def test_a_charter_with_no_workspace_line_resolves_nothing(self):
        """A guess here would hand a lane another lane's paths."""
        base, root = self.plain("separate directories")
        charter = os.path.join(root, "charter.md")
        with open(charter, encoding="utf-8") as fh:
            text = fh.read()
        with open(charter, "w", encoding="utf-8") as fh:
            fh.write("\n".join(l for l in text.splitlines()
                                if not l.lower().startswith("workspace:")) + "\n")
        out, _ = self.crossing(base, root, "api")
        self.assertEqual(out, {})


class TestTeamRootResolution(HookCase):
    """Which copy of the team root the hook enforces against."""

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


class TestWorktreeCrossing(HookCase):
    """Under one worktree per lane, a lane writes its own checkout and no other."""

    def write_from(self, tree, lane, target):
        return run({"hook_event_name": "PreToolUse", "cwd": tree,
                    "tool_name": "Write", "tool_input": {"file_path": target}},
                   env={"TEAMWORK_LANE": lane, "TEAMWORK_ROOT": self.root})

    def test_a_lane_may_not_write_into_another_lanes_worktree(self):
        """The web lane is editing that tree right now."""
        api, web = self.worktree("api"), self.worktree("web")
        out, _ = self.write_from(api, "api", os.path.join(web, "web/app.tsx"))
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("the web lane's worktree", out["permissionDecisionReason"])

    def test_not_even_at_a_path_it_owns(self):
        """Its own path in another tree lands on another lane's branch."""
        api, web = self.worktree("api"), self.worktree("web")
        out, _ = self.write_from(api, "api",
                                 os.path.join(web, "services/billing/x.py"))
        self.assertEqual(out.get("permissionDecision"), "deny")

    def test_a_lane_may_not_write_into_the_main_checkout(self):
        api = self.worktree("api")
        out, _ = self.write_from(api, "api",
                                 os.path.join(self.repo, "services/billing/x.py"))
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("the main checkout", out["permissionDecisionReason"])

    def test_a_worktree_inside_the_main_checkout_is_judged_by_the_nearest(self):
        """`claude --worktree` nests worktrees inside the main checkout."""
        nest = os.path.join(self.repo, ".claude", "worktrees")
        os.makedirs(nest)
        api, web = self.worktree("api", nest), self.worktree("web", nest)
        out, _ = self.write_from(api, "api",
                                 os.path.join(api, "services/billing/x.py"))
        self.assertEqual(out, {})
        out, _ = self.write_from(api, "api", os.path.join(web, "web/app.tsx"))
        self.assertIn("the web lane's worktree", out["permissionDecisionReason"])
        out, _ = self.write_from(web, "web", os.path.join(self.repo, "web/app.tsx"))
        self.assertIn("the main checkout", out["permissionDecisionReason"])

    def test_the_lead_lane_still_writes_the_team_root_from_its_own_tree(self):
        """The team root sits in the main checkout, which is not the lead's."""
        self.write(".teamwork/charter.md",
                   CHARTER.format(root=self.root).replace(
                       "- web - the dashboard",
                       "- web - the dashboard\n- lead - integration and docs"))
        self.write(".teamwork/roles/lead.md", ROLE_LEAD)
        lead = self.worktree("lead")
        out, _ = self.write_from(lead, "lead", os.path.join(self.root, "friction.md"))
        self.assertEqual(out, {})


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

    def test_the_lead_writes_a_lanes_launch_files_inside_its_owned_directory(self):
        """`payments/**` reaches the settings file and the repository's exclude."""
        base, root = self.plain("separate repositories", lanes=(
            ("api", ROLE_API.replace("services/billing/**", "payments/**")
                            .replace("db/migrations/**", "payments/db/**")),
            ("web", ROLE_WEB), ("lead", ROLE_LEAD)))
        charter = os.path.join(root, "charter.md")
        with open(charter, encoding="utf-8") as fh:
            text = fh.read()
        with open(charter, "w", encoding="utf-8") as fh:
            fh.write(text.replace("- web - the dashboard",
                                  "- web - the dashboard\n- lead - integration and docs"))
        payments = os.path.join(base, "payments")
        os.makedirs(payments)
        subprocess.run(["git", "init", "-q"], cwd=payments, check=True)
        for target in ("payments/.claude/settings.local.json",
                       "payments/.git/info/exclude"):
            with self.subTest(target=target):
                out, _ = run({"hook_event_name": "PreToolUse",
                              "cwd": os.path.join(base, "docs"),
                              "tool_name": "Write",
                              "tool_input": {"file_path": os.path.join(base, target)}},
                             env={"TEAMWORK_LANE": "lead", "TEAMWORK_ROOT": root})
                self.assertEqual(out, {})
        out, _ = run({"hook_event_name": "PreToolUse",
                      "cwd": os.path.join(base, "docs"),
                      "tool_name": "Write",
                      "tool_input": {"file_path": os.path.join(base, "payments/x.py")}},
                     env={"TEAMWORK_LANE": "lead", "TEAMWORK_ROOT": root})
        self.assertEqual(out.get("permissionDecision"), "deny")

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


class TestWorkspaceRootDeclared(HookCase):
    """The team root does not have to sit in the directory holding the lanes.

    team-root.md's last rung lets the user name a path of its own. Deriving the
    anchor from the team root's parent then pointed at a directory the work was
    not in, so every glob missed and every out-of-lane write was allowed.
    """

    def off_parent(self, workspace="separate directories", anchor=True):
        """Lanes in one directory, the team root deliberately in another."""
        base = os.path.realpath(tempfile.mkdtemp())
        away = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, base, ignore_errors=True)
        self.addCleanup(shutil.rmtree, away, ignore_errors=True)
        root = os.path.join(away, "myteam")
        os.makedirs(os.path.join(root, "roles"))
        line = f"Workspace: {workspace}"
        charter = CHARTER.format(root=root).replace(
            "Workspace: one worktree per lane", line)
        if anchor:
            declared = anchor if isinstance(anchor, str) else base
            charter = charter.replace(line, f"{line}\nWorkspace root: {declared}")
        with open(os.path.join(root, "charter.md"), "w", encoding="utf-8") as fh:
            fh.write(charter)
        for lane, text in (("api", ROLE_API), ("web", ROLE_WEB)):
            with open(os.path.join(root, "roles", f"{lane}.md"), "w",
                      encoding="utf-8") as fh:
                fh.write(text)
        return base, root

    def crossing(self, base, root):
        return run({"hook_event_name": "PreToolUse",
                    "cwd": os.path.join(base, "web"),
                    "tool_name": "Write",
                    "tool_input": {"file_path": os.path.join(
                        base, "services/billing/rates.py")}},
                   env={"TEAMWORK_LANE": "web", "TEAMWORK_ROOT": root})

    def test_the_declared_anchor_holds_the_boundary(self):
        base, root = self.off_parent()
        out, _ = self.crossing(base, root)
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("belongs to the api lane", out["permissionDecisionReason"])

    def test_a_lane_still_writes_its_own_paths(self):
        base, root = self.off_parent()
        out, _ = run({"hook_event_name": "PreToolUse",
                      "cwd": os.path.join(base, "web"),
                      "tool_name": "Write",
                      "tool_input": {"file_path": os.path.join(base, "web/app.tsx")}},
                     env={"TEAMWORK_LANE": "web", "TEAMWORK_ROOT": root})
        self.assertEqual(out, {})

    def test_separate_repositories_too(self):
        """Without the line this anchors at the lane's own repo and every glob misses."""
        base, root = self.off_parent("separate repositories")
        for component in ("services", "web"):
            os.makedirs(os.path.join(base, component), exist_ok=True)
            subprocess.run(["git", "init", "-q"],
                           cwd=os.path.join(base, component), check=True)
        out, _ = self.crossing(base, root)
        self.assertEqual(out.get("permissionDecision"), "deny")

    def test_without_the_line_it_falls_back_and_cannot_anchor_off_parent(self):
        """The fallback derivation, kept so a charter without the line still enforces.

        It cannot reach this team, which is why [T14] refuses to validate one
        formed without the line rather than leaving it to be discovered here.
        """
        base, root = self.off_parent(anchor=False)
        out, _ = self.crossing(base, root)
        self.assertEqual(out, {})

    def test_an_anchor_that_is_not_there_falls_back_rather_than_crashing(self):
        base, root = self.off_parent(anchor="/no/such/directory")
        out, _ = self.crossing(base, root)
        self.assertEqual(out, {})

    def test_worktrees_ignore_the_line_and_use_the_session_tree(self):
        """Each lane reads its globs against its own tree, so no line overrides it."""
        self.write(".teamwork/charter.md",
                   CHARTER.format(root=self.root).replace(
                       "Workspace: one worktree per lane",
                       "Workspace: one worktree per lane\nWorkspace root: /tmp"))
        out = self.edit("web/app.tsx", lane="api")
        self.assertEqual(out[0].get("permissionDecision"), "deny")


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

    def test_the_lead_may_not_write_a_stale_copy_of_the_team_root(self):
        """Its own worktree carries a committed copy that no member reads."""
        lead = self.worktree("lead")
        out, _ = run({"hook_event_name": "PreToolUse", "cwd": lead,
                      "tool_name": "Write",
                      "tool_input": {"file_path": os.path.join(
                          lead, ".teamwork", "charter.md")}},
                     env={"TEAMWORK_LANE": "lead", "TEAMWORK_ROOT": self.root})
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("a copy of the team root", out["permissionDecisionReason"])
        self.assertIn(self.root, out["permissionDecisionReason"])

    def test_the_lead_writes_the_files_that_launch_a_lane(self):
        """A resume rewrites them while the lane they belong to is not up to ask."""
        api, lead = self.worktree("api"), self.worktree("lead")
        for target in (os.path.join(api, ".claude", "settings.local.json"),
                       os.path.join(self.repo, ".git", "info", "exclude")):
            with self.subTest(target=target):
                out, _ = run({"hook_event_name": "PreToolUse", "cwd": lead,
                              "tool_name": "Write",
                              "tool_input": {"file_path": target}},
                             env={"TEAMWORK_LANE": "lead", "TEAMWORK_ROOT": self.root})
                self.assertEqual(out, {})

    def test_a_member_may_not_write_another_lanes_settings_file(self):
        """It would decide which lane that directory starts as."""
        api, web = self.worktree("api"), self.worktree("web")
        out, _ = run({"hook_event_name": "PreToolUse", "cwd": api,
                      "tool_name": "Write",
                      "tool_input": {"file_path": os.path.join(
                          web, ".claude", "settings.local.json")}},
                     env={"TEAMWORK_LANE": "api", "TEAMWORK_ROOT": self.root})
        self.assertEqual(out.get("permissionDecision"), "deny")

    def test_the_lead_lane_is_not_told_to_join_itself(self):
        """The member's JOIN line would have the lead message, and rename, itself."""
        out, _ = run({"hook_event_name": "SessionStart", "cwd": self.repo},
                     env={"TEAMWORK_LANE": "lead", "TEAMWORK_ROOT": self.root})
        text = out.get("additionalContext", "")
        self.assertIn("Lead: line", text)
        self.assertNotIn("Before you send JOIN", text)
        self.assertNotIn("/rename", text)

    def test_a_member_is_pointed_at_the_join_steps_not_handed_a_copy(self):
        """The steps live in the member skill; a copy here drifted from it."""
        out, _ = run({"hook_event_name": "SessionStart", "cwd": self.repo},
                     env={"TEAMWORK_LANE": "api", "TEAMWORK_ROOT": self.root})
        text = out.get("additionalContext", "")
        self.assertIn("'## Starting'", text)
        self.assertIn(os.path.join("skills", "team-member", "SKILL.md"), text)
        self.assertNotIn("/rename", text)


class TestStartup(HookCase):
    def test_session_start_names_the_root_and_the_lane(self):
        out, _ = run({"hook_event_name": "SessionStart", "cwd": self.repo},
                     env={"TEAMWORK_LANE": "api", "TEAMWORK_ROOT": self.root})
        text = out.get("additionalContext", "")
        self.assertIn(self.root, text)
        self.assertIn("roles/api.md", text)

    def test_a_compaction_says_it_again(self):
        """A compaction starts the session again, with source `compact`."""
        out, _ = run({"hook_event_name": "SessionStart", "source": "compact",
                      "cwd": self.repo},
                     env={"TEAMWORK_LANE": "api", "TEAMWORK_ROOT": self.root})
        self.assertIn(self.root, out.get("additionalContext", ""))

    def test_a_finished_team_tells_a_new_session_nothing(self):
        """Finishing keeps the contracts, and a later session is not on a team."""
        out, _ = run({"hook_event_name": "SessionStart", "cwd": self.repo})
        self.assertEqual(out, {})

    def test_a_live_run_tells_an_unnamed_session_where_its_root_is(self):
        """roster.md is this run's state, so it is there while the run is."""
        self.write(".teamwork/roster.md", "")
        out, _ = run({"hook_event_name": "SessionStart", "cwd": self.repo})
        self.assertIn(self.root, out.get("additionalContext", ""))
        self.assertIn("allows every write", out.get("additionalContext", ""))

    def test_a_misspelled_lane_is_named(self):
        """Otherwise the session is told to set the variable it already set."""
        out, _ = run({"hook_event_name": "SessionStart", "cwd": self.repo},
                     env={"TEAMWORK_LANE": "apii", "TEAMWORK_ROOT": self.root})
        text = out.get("additionalContext", "")
        self.assertIn("'apii'", text)
        self.assertIn("api, web", text)

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


class TestCrew(HookCase):
    def start(self, cwd, env, source="startup"):
        out, _ = run({"hook_event_name": "SessionStart", "source": source,
                      "cwd": cwd}, env=env)
        return out.get("additionalContext", "")

    def test_a_lane_is_told_its_crew_file(self):
        self.write(".claude/crew-api.md", "# api crew\n")
        text = self.start(self.repo, {"TEAMWORK_LANE": "api",
                                      "TEAMWORK_ROOT": self.root,
                                      "CLAUDE_PROJECT_DIR": self.repo})
        self.assertIn(os.path.join(self.repo, ".claude", "crew-api.md"), text)
        self.assertIn(os.path.join("skills", "crew", "SKILL.md"), text)

    def test_a_compaction_names_it_again(self):
        self.write(".claude/crew-api.md", "# api crew\n")
        text = self.start(self.repo, {"TEAMWORK_LANE": "api",
                                      "TEAMWORK_ROOT": self.root,
                                      "CLAUDE_PROJECT_DIR": self.repo},
                          source="compact")
        self.assertIn("crew-api.md", text)

    def test_a_lane_is_never_told_another_lanes_crew(self):
        """Under one shared tree every lane's crew file sits in one directory."""
        self.write(".claude/crew-web.md", "# web crew\n")
        self.write(".claude/crew.md", "# solo crew\n")
        text = self.start(self.repo, {"TEAMWORK_LANE": "api",
                                      "TEAMWORK_ROOT": self.root,
                                      "CLAUDE_PROJECT_DIR": self.repo})
        self.assertIn(self.root, text)
        self.assertNotIn("crew", text)

    def test_it_is_found_from_where_the_session_started_not_from_cwd(self):
        """After a `cd`, the payload's cwd is the subdirectory."""
        self.write(".claude/crew-api.md", "# api crew\n")
        sub = os.path.join(self.repo, "services")
        os.makedirs(sub)
        text = self.start(sub, {"TEAMWORK_LANE": "api",
                                "TEAMWORK_ROOT": self.root,
                                "CLAUDE_PROJECT_DIR": self.repo})
        self.assertIn("crew-api.md", text)

    def test_a_session_on_no_team_is_told_its_crew_file(self):
        plain = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, plain, ignore_errors=True)
        os.makedirs(os.path.join(plain, ".claude"))
        with open(os.path.join(plain, ".claude", "crew.md"), "w") as fh:
            fh.write("# crew\n")
        text = self.start(plain, {"CLAUDE_PROJECT_DIR": plain})
        self.assertIn(os.path.join(plain, ".claude", "crew.md"), text)
        self.assertNotIn("team root", text.lower())

    def test_a_finished_team_still_names_a_solo_crew(self):
        """Finishing keeps the team root, and the session after it is on no team."""
        self.write(".claude/crew.md", "# crew\n")
        text = self.start(self.repo, {"CLAUDE_PROJECT_DIR": self.repo})
        self.assertIn("crew.md", text)
        self.assertNotIn(self.root, text)

    def test_the_lead_holding_no_lane_is_not_told_a_solo_crew(self):
        self.write(".teamwork/roster.md", "")
        self.write(".claude/crew.md", "# crew\n")
        text = self.start(self.repo, {"CLAUDE_PROJECT_DIR": self.repo})
        self.assertIn(self.root, text)
        self.assertNotIn("crew.md", text)

    def test_no_crew_file_adds_nothing(self):
        plain = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, plain, ignore_errors=True)
        out, _ = run({"hook_event_name": "SessionStart", "cwd": plain},
                     env={"CLAUDE_PROJECT_DIR": plain})
        self.assertEqual(out, {})


class TestSessionDirectory(HookCase):
    """The lane is judged from where the session started, not where its shell went."""

    def write_as(self, lane, project, shell, target, extra=None):
        return run({"hook_event_name": "PreToolUse", "cwd": shell,
                    "tool_name": "Write", "tool_input": {"file_path": target}},
                   env={"TEAMWORK_LANE": lane, "TEAMWORK_ROOT": self.root,
                        "CLAUDE_PROJECT_DIR": project, **(extra or {})})[0]

    def test_a_cd_into_the_team_root_keeps_the_lane_in_its_own_tree(self):
        """The launch command adds the team root, and under worktrees it is in main."""
        api = self.worktree("api")
        own = self.write_as("api", api, self.root,
                            os.path.join(api, "services/billing/x.py"))
        self.assertEqual(own, {})
        main = self.write_as("api", api, self.root,
                             os.path.join(self.repo, "services/billing/x.py"))
        self.assertEqual(main.get("permissionDecision"), "deny")
        self.assertIn("the main checkout", main["permissionDecisionReason"])

    def test_a_cd_into_another_lanes_tree_does_not_make_it_yours(self):
        api, web = self.worktree("api"), self.worktree("web")
        for target in ("README.md", "services/billing/x.py"):
            with self.subTest(target=target):
                out = self.write_as("api", api, web, os.path.join(web, target))
                self.assertEqual(out.get("permissionDecision"), "deny")
                self.assertIn("the web lane's worktree", out["permissionDecisionReason"])

    def test_a_cd_does_not_lose_a_lane_named_by_its_directory(self):
        """Rung 2 reads the name of the directory the session started in."""
        api = self.worktree("api")
        os.makedirs(os.path.join(api, "web"))
        out, _ = run({"hook_event_name": "PreToolUse",
                      "cwd": os.path.join(api, "web"), "tool_name": "Write",
                      "tool_input": {"file_path": os.path.join(api, "web/app.tsx")}},
                     env={"CLAUDE_PROJECT_DIR": api})
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("You are api", out["permissionDecisionReason"])

    def test_an_isolated_agents_worktree_inside_the_lane_is_the_lanes(self):
        """EnterWorktree puts it under the lane's .claude/worktrees/ and moves there."""
        api = self.worktree("api")
        agent = self.worktree("agent-1", parent=os.path.join(api, ".claude", "worktrees"))
        own = self.write_as("api", api, agent, os.path.join(agent, "services/billing/x.py"))
        self.assertEqual(own, {})
        crossing = self.write_as("api", api, agent, os.path.join(agent, "web/app.tsx"))
        self.assertEqual(crossing.get("permissionDecision"), "deny")
        self.assertIn("belongs to the web lane", crossing["permissionDecisionReason"])
        copy = self.write_as("api", api, agent, os.path.join(agent, ".teamwork/charter.md"))
        self.assertEqual(copy.get("permissionDecision"), "deny")

    def test_a_lane_worktree_inside_the_leads_checkout_is_still_the_lanes(self):
        """`claude --worktree` nests lanes in main; nesting gives the lead nothing."""
        self.write(".teamwork/charter.md",
                   CHARTER.format(root=self.root).replace(
                       "- web - the dashboard",
                       "- web - the dashboard\n- lead - integration and docs"))
        self.write(".teamwork/roles/lead.md", ROLE_LEAD)
        web = self.worktree("web", parent=os.path.join(self.repo, ".claude", "worktrees"))
        out = self.write_as("lead", self.repo, self.repo, os.path.join(web, "docs/x.md"))
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("the web lane's worktree", out["permissionDecisionReason"])

    def test_a_relative_target_is_still_read_from_the_shell(self):
        api = self.worktree("api")
        os.makedirs(os.path.join(api, "web"))
        out, _ = run({"hook_event_name": "PreToolUse",
                      "cwd": os.path.join(api, "web"), "tool_name": "Write",
                      "tool_input": {"file_path": "app.tsx"}},
                     env={"TEAMWORK_LANE": "api", "TEAMWORK_ROOT": self.root,
                          "CLAUDE_PROJECT_DIR": api})
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("web/app.tsx", out["permissionDecisionReason"])


class TestLaneIdentity(HookCase):
    """No lane but the lead changes the variables that say which lane starts where."""

    def settings_write(self, lane, tool_input, existing=None):
        api = self.worktree("api")
        path = os.path.join(api, ".claude", "settings.local.json")
        if existing is not None:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(existing)
        return run({"hook_event_name": "PreToolUse", "cwd": api, "tool_name": "Edit",
                    "tool_input": {"file_path": path, **tool_input}},
                   env={"TEAMWORK_LANE": lane, "TEAMWORK_ROOT": self.root,
                        "CLAUDE_PROJECT_DIR": api})[0]

    SETTINGS = ('{"env": {"TEAMWORK_LANE": "api", "TEAMWORK_ROOT": "/r"},\n'
                ' "permissions": {"allow": []}}\n')

    def test_a_lane_may_not_rename_itself_in_its_own_settings_file(self):
        out = self.settings_write("api", {"old_string": '"TEAMWORK_LANE": "api"',
                                          "new_string": '"TEAMWORK_LANE": "lead"'},
                                  existing=self.SETTINGS)
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("Only the lead", out["permissionDecisionReason"])

    def test_nor_drop_its_lane_by_rewriting_the_file(self):
        out = self.settings_write("api", {"content": '{"env": {}}'},
                                  existing=self.SETTINGS)
        self.assertEqual(out.get("permissionDecision"), "deny")

    def test_a_lane_still_edits_the_rest_of_its_settings_file(self):
        out = self.settings_write("api", {"old_string": '"allow": []',
                                          "new_string": '"allow": ["Bash(make:*)"]'},
                                  existing=self.SETTINGS)
        self.assertEqual(out, {})

    def test_a_new_settings_file_naming_a_lane_is_denied(self):
        out = self.settings_write("api", {"content": '{"env": {"TEAMWORK_LANE": "lead"}}'})
        self.assertEqual(out.get("permissionDecision"), "deny")


class TestCrewFiles(HookCase):
    """A lane's crew file is its own, whatever any Owns says."""

    def setUp(self):
        super().setUp()
        self.write(".teamwork/charter.md",
                   CHARTER.format(root=self.root).replace(
                       "Workspace: one worktree per lane",
                       f"Workspace: one shared tree\nWorkspace root: {self.repo}"))
        self.write(".teamwork/roles/web.md",
                   ROLE_WEB.replace("- web/**", "- web/**\n- .claude/**"))

    def crew(self, lane, owner):
        return run({"hook_event_name": "PreToolUse", "cwd": self.repo,
                    "tool_name": "Write",
                    "tool_input": {"file_path": os.path.join(
                        self.repo, ".claude", f"crew-{owner}.md")}},
                   env={"TEAMWORK_LANE": lane, "TEAMWORK_ROOT": self.root,
                        "CLAUDE_PROJECT_DIR": self.repo})[0]

    def test_a_lane_writes_its_own_crew_file_inside_another_lanes_owns(self):
        self.assertEqual(self.crew("api", "api"), {})

    def test_no_lane_writes_another_lanes_crew_file(self):
        for lane, owner in (("web", "api"), ("api", "web")):
            with self.subTest(lane=lane, owner=owner):
                out = self.crew(lane, owner)
                self.assertEqual(out.get("permissionDecision"), "deny")
                self.assertIn(f"the {owner} lane's crew file",
                              out["permissionDecisionReason"])

    def test_a_crew_file_for_no_lane_is_an_ordinary_path(self):
        out = self.crew("api", "ghost")
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("belongs to the web lane", out["permissionDecisionReason"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
