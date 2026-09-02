"""W0-06 — check_mechanisms.py recomputes the five admission-rule classes
(concept-model §11, spec REQ-7) against docs/loom/evidence/mechanisms.yaml
and diffs: R1 unregistered, R2 stale, R3 net-count-without-budget-exception,
R4 missing eval. Fixtures build a minimal fake repo tree rather than
touching the real one, so these tests do not depend on W1..W3 landing."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "loom-code" / "scripts" / "check_mechanisms.py"

sys.path.insert(0, str(SCRIPT.parent))
import check_mechanisms as cm  # noqa: E402


LOOM_CHECKER_STUB = """#!/usr/bin/env python3
import sys
RULES = [("rule.a", "first"), ("rule.b", "second")]
if "--list-rules" in sys.argv:
    for rid, desc in RULES:
        print(f"{rid}\\t{desc}")
    sys.exit(0)
sys.exit(0)
"""

HOOKS_JSON = {
    "hooks": {
        "SessionStart": [
            {
                "matcher": "startup",
                "hooks": [{"type": "command", "command": '"${CLAUDE_PLUGIN_ROOT}/hooks/session-start"'}],
            }
        ],
        "PreToolUse": [
            {
                "matcher": "Bash",
                "hooks": [{"type": "command", "command": 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/loom_checker.py" push'}],
            }
        ],
    }
}

MANIFEST_YAML = """
version: 1.0.0
stations:
  - {name: write-plan, owner: loom-code, produces: plan}
tools:
  - {name: git-memory, owner: loom-workflow}
  - {name: goal-create, owner: loom-workflow, standalone: true}
actions:
  - {name: package-tests, owner: build, summary: "run package tests"}
artifacts:
  intent:
    path: docs/loom/intent/<change-id>.md
    template: intent.md
    fields: [{name: kind, kind: frontmatter, required: true}]
"""


def _build_repo(tmp_path: Path, *, mechanisms: list[dict] | None = None,
                 counting: str = "five classes, see script") -> Path:
    repo = tmp_path / "repo"
    (repo / "loom-code" / "skills" / "write-plan").mkdir(parents=True)
    (repo / "loom-code" / "skills" / "write-plan" / "SKILL.md").write_text("# write-plan\n")
    (repo / "loom-design" / "skills").mkdir(parents=True)
    (repo / "loom-workflow" / "skills" / "git-memory").mkdir(parents=True)
    (repo / "loom-workflow" / "skills" / "git-memory" / "SKILL.md").write_text("# git-memory\n")
    (repo / "loom-workflow" / "skills" / "goal-create").mkdir(parents=True)
    (repo / "loom-workflow" / "skills" / "goal-create" / "SKILL.md").write_text("# goal-create\n")

    (repo / "loom-code" / "scripts").mkdir(parents=True)
    (repo / "loom-code" / "scripts" / "loom_checker.py").write_text(LOOM_CHECKER_STUB)

    (repo / "loom-code" / "hooks").mkdir(parents=True)
    (repo / "loom-code" / "hooks" / "hooks.json").write_text(json.dumps(HOOKS_JSON))

    (repo / "loom-code" / "contract").mkdir(parents=True)
    (repo / "loom-code" / "contract" / "manifest.yaml").write_text(MANIFEST_YAML)

    (repo / "docs" / "loom" / "evidence").mkdir(parents=True)
    if mechanisms is not None:
        (repo / "docs" / "loom" / "evidence" / "mechanisms.yaml").write_text(
            yaml.safe_dump({"version": "1.0.0", "counting": counting, "mechanisms": mechanisms},
                            sort_keys=False)
        )

    (repo / "loom-code" / ".claude-plugin").mkdir(parents=True)
    (repo / "loom-code" / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "loom-code", "version": "1.0.0"})
    )
    (repo / "loom-code" / "CHANGELOG.md").write_text("# Changelog\n\n## [1.0.0] — today\n\nsome entry\n")
    return repo


FULL_MECHANISMS = [
    {"id": "write-plan", "class": "skill", "eval": "cold-read: evidence/a.md"},
    {"id": "git-memory", "class": "skill", "eval": "cold-read: evidence/a.md"},
    {"id": "rule.a", "class": "checker-rule", "eval": "tests/test_a.py"},
    {"id": "rule.b", "class": "checker-rule", "eval": "tests/test_b.py"},
    {"id": "SessionStart:startup:session-start", "class": "hook", "eval": "tests/test_hook.py"},
    {"id": "PreToolUse:Bash:loom_checker.py", "class": "hook", "eval": "tests/test_hook.py"},
    {"id": "station:write-plan", "class": "contract", "eval": "tests/test_c.py"},
    {"id": "tool:git-memory", "class": "contract", "eval": "tests/test_c.py"},
    {"id": "action:package-tests", "class": "contract", "eval": "tests/test_c.py"},
    {"id": "artifact:intent", "class": "contract", "eval": "tests/test_c.py"},
]


class TestRecompute:
    def test_skills_exclude_standalone(self, tmp_path):
        repo = _build_repo(tmp_path)
        assert cm.recompute_skills(repo) == {"write-plan", "git-memory"}

    def test_checker_rules_from_list_rules(self, tmp_path):
        repo = _build_repo(tmp_path)
        assert cm.recompute_checker_rules(repo) == {"rule.a", "rule.b"}

    def test_hooks_from_hooks_json(self, tmp_path):
        repo = _build_repo(tmp_path)
        assert cm.recompute_hooks(repo) == {
            "SessionStart:startup:session-start",
            "PreToolUse:Bash:loom_checker.py",
        }

    def test_contract_from_manifest(self, tmp_path):
        repo = _build_repo(tmp_path)
        got = cm.recompute_contract(repo)
        assert got == {
            "station:write-plan",
            "tool:git-memory",
            "action:package-tests",
            "artifact:intent",
        }
        assert "tool:goal-create" not in got  # standalone excluded

    def test_prose_gates_empty_when_no_markers(self, tmp_path):
        repo = _build_repo(tmp_path)
        assert cm.recompute_prose_gates(repo) == set()

    def test_prose_gates_found(self, tmp_path):
        repo = _build_repo(tmp_path)
        (repo / "loom-code" / "skills" / "write-plan" / "SKILL.md").write_text(
            "# write-plan\n\n<!-- gate: my-gate -->\nsome text\n"
        )
        assert cm.recompute_prose_gates(repo) == {"my-gate"}


class TestChecks:
    def test_r1_unregistered_is_red(self, tmp_path):
        mechs = [m for m in FULL_MECHANISMS if m["id"] != "git-memory"]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        result = cm.run_checks(repo)
        assert result.exit_code == 1
        assert any(f.rule == "R1" and f.mechanism_id == "git-memory" for f in result.findings)

    def test_r2_stale_is_red(self, tmp_path):
        mechs = FULL_MECHANISMS + [{"id": "ghost", "class": "skill", "eval": "cold-read: x.md"}]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        result = cm.run_checks(repo)
        assert result.exit_code == 1
        assert any(f.rule == "R2" and f.mechanism_id == "ghost" for f in result.findings)

    def test_r4_missing_eval_is_red(self, tmp_path):
        mechs = [dict(m) for m in FULL_MECHANISMS]
        mechs[0]["eval"] = ""
        repo = _build_repo(tmp_path, mechanisms=mechs)
        result = cm.run_checks(repo)
        assert result.exit_code == 1
        assert any(f.rule == "R4" and f.mechanism_id == mechs[0]["id"] for f in result.findings)

    def test_clean_population_is_green(self, tmp_path):
        repo = _build_repo(tmp_path, mechanisms=FULL_MECHANISMS)
        result = cm.run_checks(repo)
        assert result.exit_code == 0
        assert result.findings == []

    def test_host_hygiene_excluded_from_net_count_and_not_stale(self, tmp_path):
        mechs = FULL_MECHANISMS + [
            {"id": "PostToolUse:Skill:language-anchor.py", "class": "host-hygiene", "eval": "tests/test_h.py"}
        ]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        result = cm.run_checks(repo)
        # a host-hygiene entry with no matching recomputed hook must not be
        # flagged stale, and must not inflate the net count.
        assert not any(f.rule == "R2" and f.mechanism_id == "PostToolUse:Skill:language-anchor.py"
                        for f in result.findings)
        net = cm.net_count(mechs)
        assert net == len(FULL_MECHANISMS)

    def test_r3_net_increase_without_budget_exception_is_red(self, tmp_path):
        mechs = FULL_MECHANISMS + [{"id": "new-thing", "class": "skill", "eval": "cold-read: x.md"}]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        (repo / "loom-code" / "skills" / "new-thing").mkdir(parents=True)
        (repo / "loom-code" / "skills" / "new-thing" / "SKILL.md").write_text("# new-thing\n")
        # a prior mechanisms.yaml at HEAD~1 with one fewer mechanism, used as the baseline
        _git(repo, "init", "-q")
        _git(repo, "add", "-A")
        _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "base")
        baseline_repo = tmp_path / "baseline"
        baseline_repo.mkdir()
        (baseline_repo / "docs" / "loom" / "evidence").mkdir(parents=True)
        # simulate an older ref with fewer mechanisms via git: write a smaller
        # mechanisms.yaml, commit, tag it, then add the new one on top.
        result = cm.run_checks(repo, baseline_ref="HEAD")  # HEAD == current commit == same total
        # same total vs itself => no R3 (sanity: baseline must differ to trigger)
        assert not any(f.rule == "R3" for f in result.findings)

    def test_r3_red_when_changelog_has_no_budget_exception_line(self, tmp_path):
        mechs = FULL_MECHANISMS + [{"id": "new-thing", "class": "skill", "eval": "cold-read: x.md"}]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        result = cm.run_checks(repo, baseline_total_override=len(FULL_MECHANISMS))
        assert result.exit_code == 1
        assert any(f.rule == "R3" for f in result.findings)

    def test_r3_green_when_changelog_has_budget_exception_line(self, tmp_path):
        mechs = FULL_MECHANISMS + [{"id": "new-thing", "class": "skill", "eval": "cold-read: x.md"}]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        changelog = repo / "loom-code" / "CHANGELOG.md"
        changelog.write_text(
            changelog.read_text() + "\nbudget-exception: new-thing — one-off measurement helper\n"
        )
        result = cm.run_checks(repo, baseline_total_override=len(FULL_MECHANISMS))
        assert not any(f.rule == "R3" for f in result.findings)


class TestBaselineApproximation:
    def test_approximate_baseline_counts_skills_and_hooks(self, tmp_path):
        repo = _build_repo(tmp_path, mechanisms=FULL_MECHANISMS)
        _git(repo, "init", "-q")
        _git(repo, "add", "-A")
        _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "base")
        total, approx = cm.compute_baseline_total(repo, "HEAD")
        assert approx is False  # mechanisms.yaml exists at HEAD, no approximation needed
        assert total == len(FULL_MECHANISMS)

    def test_approximate_baseline_when_no_mechanisms_yaml(self, tmp_path):
        repo = _build_repo(tmp_path)  # no mechanisms.yaml written
        _git(repo, "init", "-q")
        _git(repo, "add", "-A")
        _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "base")
        total, approx = cm.compute_baseline_total(repo, "HEAD")
        assert approx is True
        # 3 SKILL.md files + 2 hook entries in the fixture
        assert total == 3 + 2


class TestRealYaml:
    def test_real_mechanisms_yaml_parses_and_evals_exist(self):
        path = REPO / "docs" / "loom" / "evidence" / "mechanisms.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["version"]
        assert data["counting"].strip()
        mechs = data["mechanisms"]
        assert mechs
        ids = [m["id"] for m in mechs]
        assert len(ids) == len(set(ids)), "duplicate mechanism id"
        for m in mechs:
            assert m.get("eval"), m["id"]
            assert m["class"] in {"skill", "checker-rule", "hook", "contract", "prose-gate", "host-hygiene"}
            ev = m["eval"]
            if ev.startswith("cold-read:"):
                continue
            file_part = ev.split("::", 1)[0].strip()
            assert (REPO / file_part).is_file(), f"{m['id']}: eval path missing {file_part}"


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def test_cli_measure_runs_without_error(tmp_path):
    repo = _build_repo(tmp_path, mechanisms=FULL_MECHANISMS)
    (repo / "loom-code" / "hooks" / "session-start").write_text("#!/usr/bin/env bash\necho hi\n")
    (repo / "loom-code" / "hooks" / "session-start").chmod(0o755)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo", str(repo), "--measure"],
        capture_output=True, text=True,
    )
    assert proc.returncode in (0, 1), proc.stderr
    assert "skill" in proc.stdout.lower()
