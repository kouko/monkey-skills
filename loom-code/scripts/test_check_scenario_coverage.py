"""Tests for check_scenario_coverage.py — the coverage script that compares
a loom-spec change-folder's `#### Scenario:` set (per
`loom-spec/scripts/validate_spec_output.py`'s heading grammar: `### Requirement:`
/ `#### Scenario:`) against a writing-plans plan's join keys (`<change-id> /
Requirement: <name> / Scenario: <name>`, from each task's `Brief item covered`
field — see `loom-code/skills/writing-plans/references/plan-format.md`).

Exercised as a CLI subprocess (the actual interface: two positional args,
exit 0 / exit 1) rather than importing internals, since the contract this
script must honor is the process boundary.

Stdlib only (subprocess + pathlib).
"""

import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent / "check_scenario_coverage.py"

_ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def _run(change_folder: Path, plan_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(change_folder), str(plan_path)],
        capture_output=True,
        text=True,
        env=_ENV,
    )


def _write_spec(change_folder: Path, body: str) -> None:
    spec_dir = change_folder / "specs" / "widgets"
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text(body, encoding="utf-8")


_TWO_SCENARIO_SPEC = """\
## ADDED Requirements

### Requirement: Users can filter by date
The system MUST allow filtering.

#### Scenario: Empty result set
- GIVEN no records match
- WHEN filter applied
- THEN empty list returned

#### Scenario: Single match
- GIVEN one record matches
- WHEN filter applied
- THEN one item returned
"""


def test_full_coverage_exit_0(tmp_path):
    change_folder = tmp_path / "2026-07-10-my-change"
    _write_spec(change_folder, _TWO_SCENARIO_SPEC)
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Brief item covered: 2026-07-10-my-change / Requirement: Users can filter by date / Scenario: Empty result set\n\n"
        "## Task 2 — bar\n"
        "- Brief item covered: 2026-07-10-my-change / Requirement: Users can filter by date / Scenario: Single match\n",
        encoding="utf-8",
    )
    result = _run(change_folder, plan)
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""


def test_dropped_scenario_named_on_stderr_exit_1(tmp_path):
    change_folder = tmp_path / "2026-07-10-my-change"
    _write_spec(change_folder, _TWO_SCENARIO_SPEC)
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Brief item covered: 2026-07-10-my-change / Requirement: Users can filter by date / Scenario: Empty result set\n",
        encoding="utf-8",
    )
    result = _run(change_folder, plan)
    assert result.returncode == 1
    assert "Single match" in result.stderr
    assert "2026-07-10-my-change" in result.stderr
    assert "Users can filter by date" in result.stderr
    # the covered scenario must NOT be reported as dropped
    assert "Empty result set" not in result.stderr


def test_malformed_plan_prose_only_zero_coverage_exit_1(tmp_path):
    """A plan whose 'Brief item covered' fields are all prose referents
    (kind (a) — no join-key grammar) has zero join keys — treat as zero
    coverage: every scenario is reported dropped."""
    change_folder = tmp_path / "2026-07-10-my-change"
    _write_spec(change_folder, _TWO_SCENARIO_SPEC)
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Brief item covered: \"some unrelated brief prose, not a join key\"\n",
        encoding="utf-8",
    )
    result = _run(change_folder, plan)
    assert result.returncode == 1
    assert "Empty result set" in result.stderr
    assert "Single match" in result.stderr


def test_malformed_plan_no_brief_item_field_at_all_zero_coverage_exit_1(tmp_path):
    change_folder = tmp_path / "2026-07-10-my-change"
    _write_spec(change_folder, _TWO_SCENARIO_SPEC)
    plan = tmp_path / "plan.md"
    plan.write_text("# Plan: x\n\n## Task 1 — foo\n- Description: does stuff\n",
                     encoding="utf-8")
    result = _run(change_folder, plan)
    assert result.returncode == 1
    assert "Empty result set" in result.stderr
    assert "Single match" in result.stderr


def test_empty_change_folder_vacuous_exit_0(tmp_path):
    change_folder = tmp_path / "2026-07-10-empty-change"
    change_folder.mkdir(parents=True)
    plan = tmp_path / "plan.md"
    plan.write_text("# Plan: x\n", encoding="utf-8")
    result = _run(change_folder, plan)
    assert result.returncode == 0, result.stderr
    assert "vacuous" in result.stdout.lower() or "no" in result.stdout.lower()


def test_missing_plan_file_treated_as_zero_coverage_exit_1(tmp_path):
    change_folder = tmp_path / "2026-07-10-my-change"
    _write_spec(change_folder, _TWO_SCENARIO_SPEC)
    plan = tmp_path / "does-not-exist.md"
    result = _run(change_folder, plan)
    assert result.returncode == 1
    assert "Empty result set" in result.stderr
    assert "Single match" in result.stderr


_HASH_IN_BODY_SPEC = """\
## ADDED Requirements

### Requirement: Users can filter by date
The system MUST allow filtering.

#### Scenario: Empty result set
- GIVEN no records match
- WHEN filter applied
- THEN empty list returned

```python
# a comment inside an example code fence
x = 1
```

#### Scenario: Single match
- GIVEN one record matches
- WHEN filter applied
- THEN one item returned
"""


def test_single_hash_comment_in_scenario_body_does_not_truncate(tmp_path):
    """A `# comment` line inside a scenario body's example code fence must
    NOT be treated as a section boundary — parity with
    validate_spec_output.py's `_ANY_HEADER = re.compile(r"^#{2,4}\\s")`,
    which deliberately excludes single-#. If the boundary wrongly matches
    the `# comment` line, the requirement's scope truncates before the
    second `#### Scenario:` header, and that scenario silently vanishes
    from the folder scan — undetectable as 'dropped' since the script never
    knew it existed. Here the plan does NOT cover 'Single match', so a
    correct scanner must report it dropped (exit 1)."""
    change_folder = tmp_path / "2026-07-10-my-change"
    _write_spec(change_folder, _HASH_IN_BODY_SPEC)
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Brief item covered: 2026-07-10-my-change / Requirement: Users can filter by date / Scenario: Empty result set\n",
        encoding="utf-8",
    )
    result = _run(change_folder, plan)
    assert result.returncode == 1
    assert "Single match" in result.stderr


_DUPLICATE_SCENARIO_SPEC = """\
## ADDED Requirements

### Requirement: Users can filter by date
The system MUST allow filtering.

#### Scenario: Empty result set
- GIVEN no records match
- WHEN filter applied
- THEN empty list returned

#### Scenario: Empty result set
- GIVEN no records match again
- WHEN filter applied
- THEN empty list returned
"""


def test_duplicate_scenario_key_warns_on_stderr(tmp_path):
    """Duplicate (requirement, scenario) name pairs collapse into one set
    entry — an uncovered duplicate instance would otherwise be
    undetectable. The script must warn on stderr naming the duplicated
    key (without changing the join-key format) and still proceed."""
    change_folder = tmp_path / "2026-07-10-my-change"
    _write_spec(change_folder, _DUPLICATE_SCENARIO_SPEC)
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1 — foo\n"
        "- Brief item covered: 2026-07-10-my-change / Requirement: Users can filter by date / Scenario: Empty result set\n",
        encoding="utf-8",
    )
    result = _run(change_folder, plan)
    assert result.returncode == 0, result.stderr
    assert "duplicate" in result.stderr.lower()
    assert "Empty result set" in result.stderr


def test_multiple_requirements_and_scenarios_all_paired_correctly(tmp_path):
    change_folder = tmp_path / "2026-07-10-my-change"
    spec = """\
## ADDED Requirements

### Requirement: First requirement
The system MUST do A.

#### Scenario: First scenario of first requirement
- GIVEN a
- WHEN b
- THEN c

### Requirement: Second requirement
The system MUST do B.

#### Scenario: Only scenario of second requirement
- GIVEN a
- WHEN b
- THEN c
"""
    _write_spec(change_folder, spec)
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan: x\n\n"
        "## Task 1\n"
        "- Brief item covered: 2026-07-10-my-change / Requirement: First requirement / Scenario: First scenario of first requirement\n\n"
        "## Task 2\n"
        "- Brief item covered: 2026-07-10-my-change / Requirement: Second requirement / Scenario: Only scenario of second requirement\n",
        encoding="utf-8",
    )
    result = _run(change_folder, plan)
    assert result.returncode == 0, result.stderr
