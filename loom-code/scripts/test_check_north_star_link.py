"""Tests for check_north_star_link.py — the betting-moment checker that
every COMMITTED-NEXT backlog entry carries a well-formed `serves:` line
against `docs/loom/PURPOSE.md` (grammar SSOT:
`backlog_index._is_well_formed_serves`).

Exercised as a CLI subprocess (the actual interface) — same convention
as `test_check_onramp_choice.py` / `test_check_direction_freshness.py`.

Stdlib only (subprocess + pathlib).
"""

import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent / "check_north_star_link.py"

_ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def _run(store_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(store_path)],
        capture_output=True,
        text=True,
        env=_ENV,
    )


def _write_entry(store: Path, name: str, status: str, serves: str | None) -> Path:
    store.mkdir(parents=True, exist_ok=True)
    lines = ["---", f"name: {name}", f"status: {status}"]
    if serves is not None:
        lines.append(f"serves: {serves}")
    lines.append("---")
    lines.append("")
    lines.append("body.")
    entry = store / f"{name}.md"
    entry.write_text("\n".join(lines), encoding="utf-8")
    return entry


def test_source_does_not_parse_bold_labels():
    """The brief's Boundary evidence: no label inside PURPOSE.md is
    mechanically enforced — this script must read the file as opaque
    text and never key on any of the four bold sub-labels sketched
    elsewhere. A checker keying on them would break on the second repo
    that adopts a different sub-structure."""
    source = SCRIPT.read_text(encoding="utf-8")
    assert "**Why:**" not in source
    assert "**Done when:**" not in source
    assert "**Goal:**" not in source
    assert "**Success:**" not in source


def test_exit_0_when_every_committed_next_entry_is_well_formed(tmp_path):
    store = tmp_path / "docs" / "loom" / "backlog"
    store.mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "loom" / "PURPOSE.md").write_text(
        "Some long-horizon purpose.\n", encoding="utf-8"
    )
    _write_entry(store, "entry-a", "COMMITTED-NEXT", "ships the thing")
    _write_entry(store, "entry-b", "OPEN", None)

    result = _run(store)

    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


def test_exit_0_when_no_committed_next_entries_and_no_purpose_md(tmp_path):
    """A fresh repo with nothing committed yet must not be blocked —
    the Decision's 'never block a fresh repo with nothing in it yet.'"""
    store = tmp_path / "docs" / "loom" / "backlog"
    _write_entry(store, "entry-a", "OPEN", None)

    result = _run(store)

    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


def test_exit_1_on_missing_store_path(tmp_path):
    missing = tmp_path / "does" / "not" / "exist"

    result = _run(missing)

    assert result.returncode == 1
    assert str(missing) in result.stderr


def test_exit_2_names_offending_entry_and_question(tmp_path):
    store = tmp_path / "docs" / "loom" / "backlog"
    store.mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "loom" / "PURPOSE.md").write_text(
        "Some long-horizon purpose.\n", encoding="utf-8"
    )
    _write_entry(store, "entry-c", "COMMITTED-NEXT", None)

    result = _run(store)

    assert result.returncode == 2, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "entry-c" in result.stderr
    assert "serves" in result.stderr


def test_exit_2_asks_for_purpose_md_when_absent_but_entries_exist(tmp_path):
    """Absent PURPOSE.md is no longer a silent exemption — it becomes a
    prompt, and its message must be distinguishable from the
    offending-serves-entry exit 2 (a single ambiguous message is a
    defect per the task brief)."""
    store = tmp_path / "docs" / "loom" / "backlog"
    purpose_path = tmp_path / "docs" / "loom" / "PURPOSE.md"
    _write_entry(store, "entry-a", "COMMITTED-NEXT", "ships the thing")

    result = _run(store)

    assert result.returncode == 2, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert str(purpose_path) in result.stderr
    assert "entry-a" not in result.stderr
