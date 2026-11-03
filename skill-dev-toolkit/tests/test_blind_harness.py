"""Full-output inspection preserves blind labels through the real CLI."""

import json
import os
from pathlib import Path
import re
import subprocess
import sys

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "skills/skill-tuning/scripts/ab_harness.py"


def run_round(tmp_path, max_lines, pick="a", stdin=None):
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
        "--max-display-lines", str(max_lines),
        *(["--pick", pick] if pick is not None else []),
    ], input=stdin, capture_output=True, text=True, env={**os.environ, "TMPDIR": str(viewing)})
    record = json.loads(session.read_text()) if session.exists() else None
    paths = {label: Path(path) for label, path in re.findall(
        r"OUTPUT ([A-Z])\n[^\n]+\n.*?\[\.\.\. truncated; full output: ([^\n]+)\]",
        result.stdout, re.DOTALL,
    )}
    return result, record, paths, sources, viewing


@pytest.mark.parametrize("pick,stdin,locked_pick", [
    *[(pick, None, pick) for pick in ["a", "b", "a+b", "n", "r"]],
    (None, "m\ninvalid\na\n", "a"),
    (None, "invalid\nm\na+b\n", "a+b"),
])
def test_blind_full_view_same_choice(tmp_path, pick, stdin, locked_pick):
    result, record, paths, sources, viewing = run_round(tmp_path, 1, pick, stdin)
    assert result.returncode == 0
    assert result.stdout.count("TEST PROMPT") == 1
    assert len(list(viewing.iterdir())) == 1
    if stdin:
        assert result.stdout.count("Your pick:") == 3
        assert result.stderr.count("Pick not locked:") == 2
    pick = locked_pick
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


@pytest.mark.parametrize("max_lines,pick,stdin", [
    (1, "a", None), (2, "a", None), (200, "a", None),
    (1, "invalid", None), (1, "m", None),
    (1, None, ""), (1, None, "m\n"), (1, None, "invalid\n"),
])
def test_identity_path_not_displayed(tmp_path, max_lines, pick, stdin):
    result, record, paths, sources, viewing = run_round(tmp_path, max_lines, pick, stdin)
    pending = pick if pick is not None else stdin.strip()
    if pending in {"invalid", "m"}:
        assert "label_assignment" not in record
        assert record["prompt"] == "Compare"
        assert record["pick"]["type"] == {"invalid": "invalid", "m": "needs_clarification"}[pending]
        assert record["pick"]["reason"]
        assert result.returncode == 2
        assert "Session written to" not in result.stdout
        assert "not locked" in result.stderr
        assert "for retry" not in result.stderr
    elif pick is None:
        assert record is None
        assert result.returncode == 2
        assert "Session written to" not in result.stdout
    else:
        assert result.returncode == 0
    if pick is None:
        assert "error: no input received" in result.stderr
    assert result.stdout.count("TEST PROMPT") == 1
    for identity in sources:
        assert identity not in result.stdout + result.stderr
        if result.returncode:
            assert identity not in json.dumps(record)
        assert str(tmp_path / identity) not in result.stdout
    assert "User-authored baseline wording" in result.stdout
    if max_lines >= 2:
        assert not paths
        assert list(viewing.iterdir()) == []
