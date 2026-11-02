"""Full-output inspection preserves blind labels through the real CLI."""

import json
import os
from pathlib import Path
import re
import subprocess
import sys

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "skills/skill-tuning/scripts/ab_harness.py"


def run_round(tmp_path, max_lines, pick="a"):
    sources = {}
    for identity, tail in [("baseline-private-name", "first"), ("variant-private-name", "second")]:
        source = tmp_path / identity / "output.md"
        source.parent.mkdir(exist_ok=True)
        source.write_bytes(f"User-authored baseline wording\r\n{tail}\r\n".encode())
        sources[identity] = source.read_bytes()
    viewing = tmp_path / "viewing"
    viewing.mkdir(exist_ok=True)
    session = tmp_path / "session.json"
    result = subprocess.run([
        sys.executable, str(SCRIPT), "--variants-dir", str(tmp_path),
        "--prompt", "Compare", "--session-out", str(session),
        "--max-display-lines", str(max_lines), "--pick", pick,
    ], capture_output=True, text=True, env={**os.environ, "TMPDIR": str(viewing)})
    record = json.loads(session.read_text())
    paths = {label: Path(path) for label, path in re.findall(
        r"OUTPUT ([A-Z])\n[^\n]+\n.*?\[\.\.\. truncated; full output: ([^\n]+)\]",
        result.stdout, re.DOTALL,
    )}
    return result, record, paths, sources, viewing


@pytest.mark.parametrize("pick", ["a", "b", "a+b", "n", "r"])
def test_blind_full_view_same_choice(tmp_path, pick):
    result, record, paths, sources, viewing = run_round(tmp_path, 1, pick)
    assert result.returncode == 0
    assert set(paths) == {"A", "B"}
    assert len({path.parent for path in paths.values()}) == 1
    for label, path in paths.items():
        assert path.name == f"{label}.md"
        assert path.is_file() and not path.is_symlink()
        assert path.parent.parent == viewing
        assert path.read_bytes() == sources[record["label_assignment"][label]]
    if pick in {"a", "b"}:
        assert record["pick"] == {
            "type": "single", "label": pick.upper(),
            "identity": record["label_assignment"][pick.upper()],
        }
    elif pick == "a+b":
        assert record["pick"] == {
            "type": "multiple", "labels": ["A", "B"],
            "identities": [record["label_assignment"][label] for label in ["A", "B"]],
        }
    else:
        assert record["pick"] == {"type": {"n": "none", "r": "refine"}[pick]}
    assert all((tmp_path / name / "output.md").read_bytes() == data for name, data in sources.items())
    _, _, next_paths, _, _ = run_round(tmp_path, 1, pick)
    assert paths["A"].parent != next_paths["A"].parent


@pytest.mark.parametrize("max_lines,pick", [(1, "a"), (2, "a"), (200, "a"), (1, "invalid"), (1, "m")])
def test_identity_path_not_displayed(tmp_path, max_lines, pick):
    result, record, paths, sources, viewing = run_round(tmp_path, max_lines, pick)
    if pick in {"invalid", "m"}:
        assert "label_assignment" not in record
        assert record["prompt"] == "Compare"
        assert record["pick"]["type"] == {"invalid": "invalid", "m": "needs_clarification"}[pick]
        assert record["pick"]["reason"]
        assert result.returncode == 2
        assert "Session written to" not in result.stdout
        assert "not locked" in result.stderr
    else:
        assert result.returncode == 0
    for identity in sources:
        assert identity not in result.stdout
        assert str(tmp_path / identity) not in result.stdout
    assert "User-authored baseline wording" in result.stdout
    if max_lines >= 2:
        assert not paths
        assert list(viewing.iterdir()) == []
