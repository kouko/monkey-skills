"""Executable contract for the `charter` sub-command (plan W0-01).

`artifacts.<name>.charter` in `loom-code/contract/manifest.yaml` is the
single copy of what each per-change artifact answers, must/must-not
carry, who signs it off and what edits it after; `loom_checker.py
charter` renders it as a markdown table and recomputes
`contract.charter-complete` over every row. These tests pin the shape of
that render against the real, committed manifest -- not a copy built by
this file -- so a future edit to the charter content or the render code
is caught here rather than only by the adversary's probes.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "loom-code" / "scripts" / "loom_checker.py"
MANIFEST = REPO_ROOT / "loom-code" / "contract" / "manifest.yaml"

EXPECTED_ARTIFACTS = [
    "intent", "spec", "plan", "review", "attestation",
    "blind-run-report", "memory", "kickoff-defaults",
]


def run_charter(*extra_args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), "charter", *extra_args],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )


def _data_rows(stdout: str) -> list[list[str]]:
    lines = [ln for ln in stdout.splitlines() if ln.strip().startswith("|")]
    rows = [ln for ln in lines if not set(ln.replace("|", "").strip()) <= {"-", " "}]
    rows = [ln for ln in rows if "artifact" not in ln.split("|")[1].lower()]
    return [[c.strip() for c in row.strip().strip("|").split("|")] for row in rows]


def test_charter_command_on_real_manifest_exits_zero() -> None:
    result = run_charter()
    assert result.returncode == 0, result.stderr


def test_charter_command_renders_a_row_per_manifest_artifact_in_order() -> None:
    result = run_charter()
    rows = _data_rows(result.stdout)
    assert [row[0] for row in rows] == EXPECTED_ARTIFACTS


def test_charter_command_every_column_of_every_row_is_non_empty() -> None:
    result = run_charter()
    rows = _data_rows(result.stdout)
    for row in rows:
        assert len(row) >= 7
        assert all(row), f"an empty column in row: {row!r}"


def test_charter_command_answers_and_readers_columns_are_non_empty() -> None:
    """wave-end:0-02: the rendered table must carry `answers` and `readers`
    columns (positions 1 and 2, right after `artifact`), both non-empty for
    every artifact."""
    result = run_charter()
    rows = {row[0]: row for row in _data_rows(result.stdout)}
    for artifact, row in rows.items():
        assert row[1].strip(), f"{artifact}: answers column is empty"
        assert row[2].strip(), f"{artifact}: readers column is empty"


def test_charter_command_must_not_cell_uses_arrow_goes_to_format() -> None:
    result = run_charter()
    rows = {row[0]: row for row in _data_rows(result.stdout)}
    # every row's must_not cell should read "<kind> → <goes_to>", joined by "; "
    for artifact, row in rows.items():
        must_not_cell = row[4]
        for entry in must_not_cell.split("; "):
            assert " → " in entry, f"{artifact}: malformed must_not entry {entry!r}"


def test_charter_command_missing_manifest_path_fails_closed() -> None:
    result = run_charter("--manifest", "/nonexistent/does-not-exist.yaml")
    assert result.returncode == 2
    assert "no contract manifest" in result.stderr


def test_charter_command_unexpected_argument_is_a_usage_error() -> None:
    result = run_charter("--bogus")
    assert result.returncode == 2


def test_charter_command_artifacts_key_absent_is_blocked(tmp_path) -> None:
    """A manifest with no `artifacts:` mapping at all -- absent, not just
    empty -- must never render zero rows and exit 0; it is a
    `contract.charter-complete` failure that exits 1 (wave-end:0-01)."""
    manifest_path = tmp_path / "manifest.yaml"
    manifest_path.write_text("version: 1.0.0\nstations: []\n", encoding="utf-8")
    result = run_charter("--manifest", str(manifest_path))
    assert result.returncode == 1
    assert "contract.charter-complete" in result.stderr


def test_list_rules_includes_contract_charter_complete() -> None:
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--list-rules"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0
    rule_ids = {line.split("\t", 1)[0] for line in result.stdout.splitlines()}
    assert "contract.charter-complete" in rule_ids


def test_charter_row_pipe_or_newline_in_a_cell_is_blocked(tmp_path) -> None:
    """wave-end:0-06: a `|` or a newline inside any charter string field
    would render as extra table cells or rows; `check_charter_row` rejects
    it with a `contract.charter-complete` failure, so the command exits 1
    and the table still carries exactly one physical row per artifact."""
    doc = {
        "version": "1.0.0",
        "stations": [{"name": "build"}],
        "artifacts": {
            "intent": {
                "charter": {
                    "answers": "x", "readers": ["a"],
                    "must": ["a | injected"],
                    "must_not": [{"kind": "z", "goes_to": "spec"}],
                    "signoff": "build", "edits_after": ["c"],
                }
            },
            "spec": {
                "charter": {
                    "answers": "y", "readers": ["a"], "must": ["b"],
                    "must_not": [{"kind": "z", "goes_to": "intent"}],
                    "signoff": "build", "edits_after": ["c"],
                }
            },
        },
    }
    import yaml as _yaml

    manifest_path = tmp_path / "manifest.yaml"
    manifest_path.write_text(_yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    result = run_charter("--manifest", str(manifest_path))
    assert result.returncode == 1
    assert "intent.must" in result.stderr


def test_manifest_every_must_not_goes_to_names_another_real_artifact() -> None:
    """A direct check on the committed manifest content, independent of the
    checker's own recompute: every must_not.goes_to in every artifact's
    charter names one of the eight artifacts, and never itself."""
    import yaml

    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    names = set(data["artifacts"].keys())
    for name, entry in data["artifacts"].items():
        charter = entry.get("charter")
        if not charter:
            continue
        for item in charter.get("must_not", []):
            goes_to = item.get("goes_to")
            assert goes_to in names, f"{name}.must_not names unknown artifact {goes_to!r}"
            assert goes_to != name, f"{name}.must_not names itself"


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-q"]))
