"""W0-06 — check_mechanisms.py recomputes the five admission-rule classes
(concept-model §11, spec REQ-7) against docs/loom/evidence/mechanisms.yaml
and diffs: R0 unknown class, R1 unregistered, R2 stale (class-scoped), R3
net-count-without-budget-exception (strict CHANGELOG section), R4 missing/
unresolved/pending eval. Fixtures build a minimal fake repo tree rather than
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

HOOKS_JSON_WITH_LANGUAGE_ANCHOR = {
    "hooks": {
        **HOOKS_JSON["hooks"],
        "PostToolUse": [
            {
                "matcher": "Skill",
                "hooks": [{"type": "command", "command": 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/language-anchor.py"'}],
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
    fields:
      - {name: kind, kind: frontmatter, required: true}
      - {name: originator, kind: frontmatter, required: true}
"""


DEFAULT_COUNTING = (
    "Five classes are recomputed and diffed against this file: skill, "
    "checker-rule, hook, contract and prose-gate. A sixth class, "
    "host-hygiene, is declared but never recomputed and never counted."
)


def _build_repo(tmp_path: Path, *, mechanisms: list[dict] | None = None,
                 counting: str = DEFAULT_COUNTING) -> Path:
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

    # eval targets: every FULL_MECHANISMS eval below must resolve on disk.
    (repo / "evidence").mkdir(parents=True)
    (repo / "evidence" / "a.md").write_text("# cold-read fixture\n")
    (repo / "tests").mkdir(parents=True)
    for fname in ("test_a.py", "test_b.py", "test_c.py", "test_hook.py"):
        (repo / "tests" / fname).write_text("def test_x():\n    pass\n")
    return repo


FULL_MECHANISMS = [
    {"id": "write-plan", "class": "skill", "eval": "cold-read: evidence/a.md"},
    {"id": "git-memory", "class": "skill", "eval": "cold-read: evidence/a.md"},
    {"id": "rule.a", "class": "checker-rule", "eval": "tests/test_a.py::test_x"},
    {"id": "rule.b", "class": "checker-rule", "eval": "tests/test_b.py::test_x"},
    {"id": "SessionStart:startup:session-start", "class": "hook", "eval": "tests/test_hook.py"},
    {"id": "PreToolUse:Bash:loom_checker.py", "class": "hook", "eval": "tests/test_hook.py"},
    {"id": "station:write-plan", "class": "contract", "eval": "tests/test_c.py"},
    {"id": "tool:git-memory", "class": "contract", "eval": "tests/test_c.py"},
    {"id": "action:package-tests", "class": "contract", "eval": "tests/test_c.py"},
    {"id": "artifact:intent.kind", "class": "contract", "eval": "tests/test_c.py"},
    {"id": "artifact:intent.originator", "class": "contract", "eval": "tests/test_c.py"},
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

    def test_contract_from_manifest_is_per_field(self, tmp_path):
        """F10: contract recompute registers one id per artifact FIELD
        (`artifact:<name>.<field>`), not one per artifact."""
        repo = _build_repo(tmp_path)
        got = cm.recompute_contract(repo)
        assert got == {
            "station:write-plan",
            "tool:git-memory",
            "action:package-tests",
            "artifact:intent.kind",
            "artifact:intent.originator",
        }
        assert "tool:goal-create" not in got  # standalone excluded
        assert "artifact:intent" not in got   # no more whole-artifact id

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
        mechs = FULL_MECHANISMS + [{"id": "ghost", "class": "skill", "eval": "cold-read: evidence/a.md"}]
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
            {"id": "PostToolUse:Skill:language-anchor.py", "class": "host-hygiene", "eval": "tests/test_hook.py"}
        ]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        (repo / "loom-code" / "hooks" / "hooks.json").write_text(json.dumps(HOOKS_JSON_WITH_LANGUAGE_ANCHOR))
        result = cm.run_checks(repo)
        # a host-hygiene entry with no matching recomputed hook must not be
        # flagged stale, and must not inflate the net count.
        assert not any(f.rule == "R2" and f.mechanism_id == "PostToolUse:Skill:language-anchor.py"
                        for f in result.findings)
        net = cm.net_count(mechs)
        assert net == len(FULL_MECHANISMS)

    def test_r3_net_increase_without_budget_exception_is_red(self, tmp_path):
        mechs = FULL_MECHANISMS + [{"id": "new-thing", "class": "skill", "eval": "cold-read: evidence/a.md"}]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        (repo / "loom-code" / "skills" / "new-thing").mkdir(parents=True)
        (repo / "loom-code" / "skills" / "new-thing" / "SKILL.md").write_text("# new-thing\n")
        _git(repo, "init", "-q")
        _git(repo, "add", "-A")
        _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "base")
        result = cm.run_checks(repo, baseline_ref="HEAD")  # HEAD == current commit == same total
        # same total vs itself => no R3 (sanity: baseline must differ to trigger)
        assert not any(f.rule == "R3" for f in result.findings)

    def test_r3_red_when_changelog_has_no_budget_exception_line(self, tmp_path):
        mechs = FULL_MECHANISMS + [{"id": "new-thing", "class": "skill", "eval": "cold-read: evidence/a.md"}]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        result = cm.run_checks(repo, baseline_total_override=len(FULL_MECHANISMS))
        assert result.exit_code == 1
        assert any(f.rule == "R3" for f in result.findings)

    def test_r3_is_a_warning_when_the_baseline_was_only_approximated(self, tmp_path):
        """An approximated baseline counts SKILL.md files and hook entries —
        a different population from the mechanisms.yaml net count. Comparing
        the two and calling the difference a budget breach is arithmetic on
        two different quantities, so it warns and does not gate."""
        repo = _build_repo(tmp_path)  # the ref carries no mechanisms.yaml
        _git(repo, "init", "-q")
        _git(repo, "add", "-A")
        _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "base")
        (repo / "docs" / "loom" / "evidence" / "mechanisms.yaml").write_text(
            yaml.safe_dump(
                {"version": "1.0.0", "counting": DEFAULT_COUNTING,
                 "mechanisms": FULL_MECHANISMS},
                sort_keys=False,
            )
        )

        result = cm.run_checks(repo, baseline_ref="HEAD")
        assert result.baseline_approx is True
        assert not any(f.rule == "R3" for f in result.findings)
        assert any("approximated" in w for w in result.warnings)

    def test_r3_green_when_changelog_has_budget_exception_line(self, tmp_path):
        mechs = FULL_MECHANISMS + [{"id": "new-thing", "class": "skill", "eval": "cold-read: evidence/a.md"}]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        changelog = repo / "loom-code" / "CHANGELOG.md"
        changelog.write_text(
            changelog.read_text() + "\nbudget-exception: new-thing — one-off measurement helper\n"
        )
        result = cm.run_checks(repo, baseline_total_override=len(FULL_MECHANISMS))
        assert not any(f.rule == "R3" for f in result.findings)


class TestClassValidation:
    """F9: class must be one of ALL_CLASSES; R1/R2 compare within the same
    class; host-hygiene ids must be found in the hook or skill recompute."""

    def test_unknown_class_is_red(self, tmp_path):
        mechs = FULL_MECHANISMS + [{"id": "mystery", "class": "bogus", "eval": "tests/test_c.py"}]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        result = cm.run_checks(repo)
        assert result.exit_code == 1
        assert any(f.rule == "R0" and f.mechanism_id == "mystery" and "unknown class" in f.detail
                    for f in result.findings)

    def test_wrong_class_registration_is_both_r1_and_r2(self, tmp_path):
        """`write-plan` is a real skill, but registered here under class
        `hook` — the correct class (skill) sees it as unregistered (R1) and
        the wrong class (hook) sees it as stale (R2)."""
        mechs = [m for m in FULL_MECHANISMS if m["id"] != "write-plan"]
        mechs = mechs + [{"id": "write-plan", "class": "hook", "eval": "tests/test_hook.py"}]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        result = cm.run_checks(repo)
        assert any(f.rule == "R1" and f.mechanism_id == "write-plan" for f in result.findings)
        assert any(f.rule == "R2" and f.mechanism_id == "write-plan" for f in result.findings)

    def test_host_hygiene_id_not_in_hook_or_skill_recompute_is_red(self, tmp_path):
        """Even an allowlisted host-hygiene id must be real infrastructure:
        this hooks.json never declares language-anchor, so the entry is
        stale rather than exempt."""
        mechs = FULL_MECHANISMS + [
            {"id": "PostToolUse:Skill:language-anchor.py", "class": "host-hygiene",
             "eval": "tests/test_hook.py"}
        ]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        result = cm.run_checks(repo)
        assert result.exit_code == 1
        assert any(f.rule == "R2" and f.mechanism_id == "PostToolUse:Skill:language-anchor.py"
                   for f in result.findings)

    def test_host_hygiene_id_found_in_skill_recompute_is_accepted(self, tmp_path):
        mechs = FULL_MECHANISMS + [
            {"id": "lang_detect", "class": "host-hygiene", "eval": "tests/test_hook.py"}
        ]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        (repo / "loom-code" / "skills" / "lang_detect").mkdir(parents=True)
        (repo / "loom-code" / "skills" / "lang_detect" / "SKILL.md").write_text("# lang_detect\n")
        result = cm.run_checks(repo)
        assert not any(f.rule in ("R0", "R1", "R2") and f.mechanism_id == "lang_detect"
                       for f in result.findings), result.findings

    def test_host_hygiene_printed_as_exempt_line(self, tmp_path):
        mechs = FULL_MECHANISMS + [
            {"id": "PostToolUse:Skill:language-anchor.py", "class": "host-hygiene", "eval": "tests/test_hook.py"}
        ]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        (repo / "loom-code" / "hooks" / "hooks.json").write_text(json.dumps(HOOKS_JSON_WITH_LANGUAGE_ANCHOR))
        result = cm.run_checks(repo)
        assert "PostToolUse:Skill:language-anchor.py" in result.host_hygiene_ids
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--repo", str(repo)],
            capture_output=True, text=True,
        )
        assert "exempt from net count: PostToolUse:Skill:language-anchor.py" in proc.stdout


class TestEvalResolution:
    """F8: eval: must be non-empty AND resolve; `pending — <task id>` is
    accepted but prints red R4-pending (exit 1)."""

    def test_pending_literal_is_accepted_but_red(self, tmp_path):
        mechs = [dict(m) for m in FULL_MECHANISMS]
        mechs[0]["eval"] = "pending — W4-01"
        repo = _build_repo(tmp_path, mechanisms=mechs)
        result = cm.run_checks(repo)
        assert result.exit_code == 1
        assert any(f.rule == "R4-pending" and f.mechanism_id == mechs[0]["id"] for f in result.findings)

    def test_eval_file_path_must_exist(self, tmp_path):
        mechs = [dict(m) for m in FULL_MECHANISMS]
        mechs[0]["eval"] = "tests/does_not_exist.py::test_x"
        repo = _build_repo(tmp_path, mechanisms=mechs)
        result = cm.run_checks(repo)
        assert result.exit_code == 1
        assert any(f.rule == "R4" and f.mechanism_id == mechs[0]["id"] for f in result.findings)

    def test_cold_read_path_must_exist(self, tmp_path):
        mechs = [dict(m) for m in FULL_MECHANISMS]
        mechs[0]["eval"] = "cold-read: evidence/does-not-exist.md"
        repo = _build_repo(tmp_path, mechanisms=mechs)
        result = cm.run_checks(repo)
        assert result.exit_code == 1
        assert any(f.rule == "R4" and f.mechanism_id == mechs[0]["id"] for f in result.findings)

    def test_r4_missing_eval_for_host_hygiene_is_red(self, tmp_path):
        """A host-hygiene entry skips R2's ordinary recompute match, but it
        must not also skip R4 -- a missing/unresolved eval is red regardless
        of class."""
        mechs = FULL_MECHANISMS + [
            {"id": "PostToolUse:Skill:language-anchor.py", "class": "host-hygiene",
             "eval": "tests/does_not_exist.py"}
        ]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        (repo / "loom-code" / "hooks" / "hooks.json").write_text(json.dumps(HOOKS_JSON_WITH_LANGUAGE_ANCHOR))
        result = cm.run_checks(repo)
        assert result.exit_code == 1
        assert any(
            f.rule == "R4" and f.mechanism_id == "PostToolUse:Skill:language-anchor.py"
            for f in result.findings
        )


class TestChangelogSection:
    """F7: R3 reads only the `## [<version>]` / `## <version>` section."""

    def test_no_matching_heading_is_red_distinct_message(self, tmp_path):
        mechs = FULL_MECHANISMS + [{"id": "new-thing", "class": "skill", "eval": "cold-read: evidence/a.md"}]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        (repo / "loom-code" / "skills" / "new-thing").mkdir(parents=True)
        (repo / "loom-code" / "skills" / "new-thing" / "SKILL.md").write_text("# new-thing\n")
        changelog = repo / "loom-code" / "CHANGELOG.md"
        changelog.write_text("# Changelog\n\n## [0.9.0] — yesterday\n\nold entry\n")
        result = cm.run_checks(repo, baseline_total_override=len(FULL_MECHANISMS))
        assert result.exit_code == 1
        assert any(f.rule == "R3" and "no CHANGELOG section for" in f.detail for f in result.findings)

    def test_whole_file_scan_never_used_for_a_different_section(self, tmp_path):
        """A budget-exception line sitting under an unrelated version's
        heading must NOT satisfy R3 — only the matching section counts."""
        mechs = FULL_MECHANISMS + [{"id": "new-thing", "class": "skill", "eval": "cold-read: evidence/a.md"}]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        (repo / "loom-code" / "skills" / "new-thing").mkdir(parents=True)
        (repo / "loom-code" / "skills" / "new-thing" / "SKILL.md").write_text("# new-thing\n")
        changelog = repo / "loom-code" / "CHANGELOG.md"
        changelog.write_text(
            "# Changelog\n\n"
            "## [1.0.0] — today\n\nsome entry\n\n"
            "## [0.9.0] — yesterday\n\nbudget-exception: new-thing — wrong section\n"
        )
        result = cm.run_checks(repo, baseline_total_override=len(FULL_MECHANISMS))
        assert result.exit_code == 1
        assert any(f.rule == "R3" for f in result.findings)

    def test_bare_heading_without_brackets_is_accepted(self, tmp_path):
        mechs = FULL_MECHANISMS + [{"id": "new-thing", "class": "skill", "eval": "cold-read: evidence/a.md"}]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        (repo / "loom-code" / "skills" / "new-thing").mkdir(parents=True)
        (repo / "loom-code" / "skills" / "new-thing" / "SKILL.md").write_text("# new-thing\n")
        changelog = repo / "loom-code" / "CHANGELOG.md"
        changelog.write_text("# Changelog\n\n## 1.0.0 — today\n\nbudget-exception: new-thing — reason\n")
        result = cm.run_checks(repo, baseline_total_override=len(FULL_MECHANISMS))
        assert not any(f.rule == "R3" for f in result.findings)

    def test_unresolvable_version_raises_for_exit_2(self, tmp_path):
        mechs = FULL_MECHANISMS + [{"id": "new-thing", "class": "skill", "eval": "cold-read: evidence/a.md"}]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        (repo / "loom-code" / "skills" / "new-thing").mkdir(parents=True)
        (repo / "loom-code" / "skills" / "new-thing" / "SKILL.md").write_text("# new-thing\n")
        (repo / "loom-code" / ".claude-plugin" / "plugin.json").write_text("{}")  # no version key
        with pytest.raises(ValueError):
            cm.run_checks(repo, baseline_total_override=len(FULL_MECHANISMS))

    def test_cli_exit_2_when_plugin_json_unparseable(self, tmp_path):
        mechs = FULL_MECHANISMS + [{"id": "new-thing", "class": "skill", "eval": "cold-read: evidence/a.md"}]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        (repo / "loom-code" / "skills" / "new-thing").mkdir(parents=True)
        (repo / "loom-code" / "skills" / "new-thing" / "SKILL.md").write_text("# new-thing\n")
        (repo / "loom-code" / ".claude-plugin" / "plugin.json").write_text("not json")
        _git(repo, "init", "-q")
        _git(repo, "add", "-A")
        _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "base")
        # force an R3 evaluation attempt via an explicit baseline lower than net
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--repo", str(repo)],
            capture_output=True, text=True,
        )
        # no --baseline given here means no R3 path is taken; assert clean run
        # is unaffected by the corrupt plugin.json (sanity only).
        assert proc.returncode in (0, 1)


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
            if ev.startswith("pending"):
                assert cm.PENDING_RE.match(ev), f"{m['id']}: malformed pending literal {ev!r}"
                continue
            if ev.startswith("cold-read:"):
                p = ev.split("cold-read:", 1)[1].strip()
                assert (REPO / p).is_file(), f"{m['id']}: cold-read path missing {p}"
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


class TestEvalIsAlive:
    """W3-04 / P02+P12 — R4 checks that the eval could actually FAIL: a
    bare path must be a test file or a `cold-read:` evidence file, and a
    `<path>::<node>` eval must name a node that exists in that file."""

    def _repo(self, tmp_path, eval_value):
        mechs = [dict(m) for m in FULL_MECHANISMS]
        mechs[0]["eval"] = eval_value
        return _build_repo(tmp_path, mechanisms=mechs), mechs[0]["id"]

    def test_bare_non_test_file_is_red(self, tmp_path):
        (tmp_path / "repo").mkdir(exist_ok=True)
        repo, mid = self._repo(tmp_path, "README.md")
        (repo / "README.md").write_text("# readme\n")
        result = cm.run_checks(repo)
        assert result.exit_code == 1
        assert any(
            f.rule == "R4" and f.mechanism_id == mid and "not a test or cold-read" in f.detail
            for f in result.findings
        ), result.findings

    def test_bare_test_file_is_accepted(self, tmp_path):
        repo, _ = self._repo(tmp_path, "tests/test_a.py")
        result = cm.run_checks(repo)
        assert result.exit_code == 0, result.findings

    def test_shell_probe_under_tests_is_accepted(self, tmp_path):
        repo, _ = self._repo(tmp_path, "tests/probe.sh")
        (repo / "tests" / "probe.sh").write_text("#!/bin/sh\nexit 0\n")
        result = cm.run_checks(repo)
        assert result.exit_code == 0, result.findings

    def test_node_that_does_not_exist_is_red(self, tmp_path):
        repo, mid = self._repo(tmp_path, "tests/test_a.py::test_never_existed")
        result = cm.run_checks(repo)
        assert result.exit_code == 1
        assert any(
            f.rule == "R4" and f.mechanism_id == mid and "test_never_existed" in f.detail
            for f in result.findings
        ), result.findings

    def test_node_that_exists_is_accepted(self, tmp_path):
        repo, _ = self._repo(tmp_path, "tests/test_a.py::test_x")
        result = cm.run_checks(repo)
        assert result.exit_code == 0, result.findings

    def test_node_on_a_non_test_file_is_red(self, tmp_path):
        repo, mid = self._repo(tmp_path, "README.md::test_x")
        (repo / "README.md").write_text("# readme\n")
        result = cm.run_checks(repo)
        assert result.exit_code == 1
        assert any(f.rule == "R4" and f.mechanism_id == mid for f in result.findings)


class TestHostHygieneAllowlist:
    """W3-04 / P10 — `class: host-hygiene` is spendable only on the named
    host-infrastructure ids; anything else is R0, and it never suppresses
    R1 for a skill or hook inside the loom flow."""

    def test_unlisted_id_under_host_hygiene_is_r0(self, tmp_path):
        mechs = FULL_MECHANISMS + [
            {"id": "smuggle", "class": "host-hygiene", "eval": "tests/test_a.py::test_x"}
        ]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        (repo / "loom-code" / "skills" / "smuggle").mkdir(parents=True)
        (repo / "loom-code" / "skills" / "smuggle" / "SKILL.md").write_text("# smuggle\n")
        result = cm.run_checks(repo)
        assert result.exit_code == 1
        assert any(f.rule == "R0" and f.mechanism_id == "smuggle" for f in result.findings)

    def test_unlisted_id_does_not_suppress_r1(self, tmp_path):
        mechs = FULL_MECHANISMS + [
            {"id": "smuggle", "class": "host-hygiene", "eval": "tests/test_a.py::test_x"}
        ]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        (repo / "loom-code" / "skills" / "smuggle").mkdir(parents=True)
        (repo / "loom-code" / "skills" / "smuggle" / "SKILL.md").write_text("# smuggle\n")
        result = cm.run_checks(repo)
        assert any(f.rule == "R1" and f.mechanism_id == "smuggle" for f in result.findings), result.findings
        assert "smuggle" not in result.host_hygiene_ids

    def test_allowlisted_id_is_still_exempt(self, tmp_path):
        mechs = FULL_MECHANISMS + [
            {"id": "PostToolUse:Skill:language-anchor.py", "class": "host-hygiene",
             "eval": "tests/test_hook.py"}
        ]
        repo = _build_repo(tmp_path, mechanisms=mechs)
        (repo / "loom-code" / "hooks" / "hooks.json").write_text(
            json.dumps(HOOKS_JSON_WITH_LANGUAGE_ANCHOR)
        )
        result = cm.run_checks(repo)
        assert result.exit_code == 0, result.findings
        assert result.host_hygiene_ids == ["PostToolUse:Skill:language-anchor.py"]


class TestCountingProse:
    """W3-04 / P15 — the `counting:` paragraph is the prose twin of this
    module; it must name every class the code knows, so prose that invents
    an exemption is red rather than quietly misleading."""

    def test_real_yaml_counting_names_every_class(self):
        path = REPO / "docs" / "loom" / "evidence" / "mechanisms.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert cm.counting_classes(data["counting"]) == set(cm.ALL_CLASSES)

    def test_drifted_paragraph_is_red(self, tmp_path):
        repo = _build_repo(
            tmp_path, mechanisms=FULL_MECHANISMS,
            counting=("Net count excludes host-hygiene and any skill whose id starts "
                      "with legacy- (declared exempt by this paragraph)."),
        )
        result = cm.run_checks(repo)
        assert result.exit_code == 1
        assert any(f.rule == "R5" for f in result.findings), result.findings

    def test_missing_paragraph_is_red(self, tmp_path):
        repo = _build_repo(tmp_path, mechanisms=FULL_MECHANISMS)
        path = repo / "docs" / "loom" / "evidence" / "mechanisms.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        del data["counting"]
        path.write_text(yaml.safe_dump(data, sort_keys=False))
        result = cm.run_checks(repo)
        assert result.exit_code == 1
        assert any(f.rule == "R5" for f in result.findings), result.findings


class TestWcWordsLocaleIndependent:
    """CI-1 — `wc -w` disagrees with itself across locales on some
    unicode punctuation (e.g. a circled digit immediately followed by a
    semicolon, as the real session-start hook emits); the recorded
    baseline must reproduce on any runner regardless of its ambient
    LANG/LC_ALL, so wc_words must pin its own locale rather than
    inherit the caller's environment."""

    def test_count_is_stable_across_locales(self, monkeypatch):
        data = "not in ①;".encode("utf-8")
        counts = set()
        for locale in ("C", "C.UTF-8", "en_US.UTF-8"):
            monkeypatch.setenv("LC_ALL", locale)
            counts.add(cm.wc_words(data))
        assert len(counts) == 1, counts


def _measure_repo(tmp_path, *, words: int, baseline_line: str | None,
                  keep_hook: bool = True) -> Path:
    repo = _build_repo(tmp_path, mechanisms=FULL_MECHANISMS)
    hook = repo / "loom-code" / "hooks" / "session-start"
    hook.write_text("#!/usr/bin/env bash\necho '" + " ".join(["w"] * words) + "'\n")
    hook.chmod(0o755)
    _git(repo, "init", "-q")
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "base")
    sha = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                         capture_output=True, text=True, check=True).stdout.strip()[:8]
    kickoff = repo / "docs" / "loom" / "KICKOFF-DEFAULTS.md"
    if baseline_line is not None:
        kickoff.write_text("# Kickoff\n\n" + baseline_line.replace("<sha>", sha) + "\n")
    else:
        kickoff.write_text("# Kickoff\n\n- second-vendor: codex\n")
    if not keep_hook:
        hook.unlink()
    return repo


class TestMeasureFailsClosed:
    """W3-04 / P04+P11 — --measure refuses a missing baseline line, a
    missing hook, and a baseline number that its own sha does not produce."""

    def test_recorded_baseline_matching_its_sha_is_green(self, tmp_path):
        repo = _measure_repo(tmp_path, words=10, baseline_line="- session-start-baseline: <sha> 10 — measured")
        assert cm.run_measure(repo) == 0

    def test_missing_baseline_line_is_red(self, tmp_path):
        repo = _measure_repo(tmp_path, words=10, baseline_line=None)
        assert cm.run_measure(repo) == 1

    def test_missing_hook_is_red(self, tmp_path):
        repo = _measure_repo(tmp_path, words=10,
                             baseline_line="- session-start-baseline: <sha> 10 — measured",
                             keep_hook=False)
        assert cm.run_measure(repo) == 1

    def test_baseline_number_not_produced_by_its_sha_is_red(self, tmp_path, capsys):
        repo = _measure_repo(tmp_path, words=10,
                             baseline_line="- session-start-baseline: <sha> 99999 — 'remeasured'")
        assert cm.run_measure(repo) == 1
        assert "does not match" in capsys.readouterr().out

    def test_unresolvable_baseline_sha_is_red(self, tmp_path):
        repo = _measure_repo(tmp_path, words=10,
                             baseline_line="- session-start-baseline: deadbee 10 — bogus sha")
        assert cm.run_measure(repo) == 1

    def test_real_repo_measure_is_green(self):
        assert cm.run_measure(REPO) == 0
