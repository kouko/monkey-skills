"""W1-05 — `docs/loom/KICKOFF-DEFAULTS.md`'s `package-tests` line covers
`loom-design/scripts/`, and its trailing note stops claiming CI runs the
identical path set.

#791 went red in CI twice because the recorded package-tests command
(the one `push.probes-package-tests` compares a recorded run against) never
ran loom-design's own tests -- CI runs those in a separate job
(`.github/workflows/loom-design-ci.yml`, `python3 -m pytest
loom-design/scripts/ -q`), not the loom-code job KICKOFF used to claim
parity with.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
KICKOFF = REPO / "docs" / "loom" / "KICKOFF-DEFAULTS.md"

EXPECTED_COMMAND = (
    "python3 scripts/run_package_tests.py loom-code/scripts/ scripts/ "
    ".claude/hooks/ -q -n auto --then loom-design/scripts/ -q"
)


def _command_and_note() -> tuple[str, str]:
    for line in KICKOFF.read_text(encoding="utf-8").splitlines():
        if line.startswith("- package-tests:"):
            value = line[len("- package-tests:"):]
            command, _, note = value.partition("—")
            return command.strip(), note.strip()
    raise AssertionError("KICKOFF-DEFAULTS.md carries no `- package-tests:` line")


def test_package_tests_command_covers_loom_design_scripts() -> None:
    command, _ = _command_and_note()
    assert command == EXPECTED_COMMAND


def test_trailing_note_no_longer_claims_ci_runs_the_same_paths() -> None:
    _, note = _command_and_note()
    assert "CI runs the same test paths" not in note
    assert "loom-design" in note
    # the `-n auto` rationale and the dbt-wiki abort note must survive.
    assert "pytest-xdist" in note
    assert "dbt-wiki" in note
