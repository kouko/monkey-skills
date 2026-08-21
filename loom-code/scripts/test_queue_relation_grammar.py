"""Behavioral tests for `check_queue_relation.py` (plan docs/loom/
plans/2026-08-21-dissolve-direction-layer.md Task 4). `in-queue:`/
`displaces:` names resolve against live `status: bet` backlog entries;
the old per-repo "now" list and its unlanded-change advisory are gone,
and a repo with no `docs/loom/backlog/` store reports a loud N/A at
exit 0 rather than gating.

Stdlib only.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from check_queue_relation import (
    QueueRelationResult,
    build_queue_relation_question,
    live_bet_names,
    resolve_queue_relation,
)

_SCRIPT = Path(__file__).parent / "check_queue_relation.py"


def _write_bet_entry(store: Path, name: str) -> None:
    store.mkdir(parents=True, exist_ok=True)
    (store / f"{name}.md").write_text(
        f"---\nname: {name}\nstatus: bet\n---\n\nBody.\n",
        encoding="utf-8",
    )


def test_in_queue_resolves_against_bet_entry_without_direction_md(
    tmp_path: Path,
) -> None:
    repo = tmp_path
    store = repo / "docs" / "loom" / "backlog"
    _write_bet_entry(store, "ship-the-widget")
    assert not (repo / "docs" / "loom" / "DIRECTION.md").exists()

    brief = repo / "brief.md"
    brief.write_text(
        "## Queue relation\n\nin-queue: ship-the-widget\n", encoding="utf-8"
    )

    result = subprocess.run(
        [sys.executable, str(_SCRIPT), str(brief), "--repo-root", str(repo)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_no_store_exits_zero_with_na_line(tmp_path: Path) -> None:
    repo = tmp_path
    assert not (repo / "docs" / "loom" / "backlog").exists()

    brief = repo / "brief.md"
    brief.write_text("## Queue relation\n\npending\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(_SCRIPT), str(brief), "--repo-root", str(repo)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "queue-relation: N/A" in result.stdout
    assert "docs/loom/backlog/ absent" in result.stdout


def test_unresolved_output_lists_live_bet_names_not_placeholder(
    tmp_path: Path,
) -> None:
    repo = tmp_path
    store = repo / "docs" / "loom" / "backlog"
    _write_bet_entry(store, "alpha-arc")
    _write_bet_entry(store, "beta-arc")

    brief = repo / "brief.md"
    brief.write_text("## Queue relation\n\npending\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(_SCRIPT), str(brief), "--repo-root", str(repo)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "alpha-arc" in result.stderr
    assert "beta-arc" in result.stderr
    assert "<entry-name>" not in result.stderr


def test_unqueued_resolves_against_empty_bet_set(tmp_path: Path) -> None:
    repo = tmp_path
    store = repo / "docs" / "loom" / "backlog"
    store.mkdir(parents=True)

    brief = repo / "brief.md"
    brief.write_text(
        "## Queue relation\n\nunqueued — nothing live yet\n", encoding="utf-8"
    )

    result = subprocess.run(
        [sys.executable, str(_SCRIPT), str(brief), "--repo-root", str(repo)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_in_queue_unresolvable_against_empty_bet_set(tmp_path: Path) -> None:
    repo = tmp_path
    store = repo / "docs" / "loom" / "backlog"
    store.mkdir(parents=True)

    brief = repo / "brief.md"
    brief.write_text(
        "## Queue relation\n\nin-queue: anything\n", encoding="utf-8"
    )

    result = subprocess.run(
        [sys.executable, str(_SCRIPT), str(brief), "--repo-root", str(repo)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2


def test_live_bet_names_excludes_non_bet_and_archived(tmp_path: Path) -> None:
    store = tmp_path / "backlog"
    store.mkdir(parents=True)
    (store / "one.md").write_text(
        "---\nname: one\nstatus: bet\n---\n\nBody.\n", encoding="utf-8"
    )
    (store / "two.md").write_text(
        "---\nname: two\nstatus: open\n---\n\nBody.\n", encoding="utf-8"
    )
    archive = store / "archive"
    archive.mkdir()
    (archive / "three.md").write_text(
        "---\nname: three\nstatus: closed\n---\n\nBody.\n", encoding="utf-8"
    )

    assert live_bet_names(store) == ["one"]


def test_resolve_queue_relation_typo_is_unresolved_not_silently_passed() -> None:
    brief_text = "## Queue relation\n\nin-queue: typo-name\n"
    result = resolve_queue_relation(brief_text, ["real-name"])
    assert result.status == "unresolved"
    assert result.named_entry == "typo-name"


def test_build_question_lists_names_when_named_entry_unresolved() -> None:
    result = QueueRelationResult(
        "unresolved", "in-queue names 'typo'", named_entry="typo"
    )
    question = build_queue_relation_question(result, ["real-one", "real-two"])
    assert "real-one" in question
    assert "real-two" in question
    assert "<entry-name>" not in question


def test_missing_brief_file_exits_one(tmp_path: Path) -> None:
    repo = tmp_path
    (repo / "docs" / "loom" / "backlog").mkdir(parents=True)

    result = subprocess.run(
        [
            sys.executable,
            str(_SCRIPT),
            str(repo / "does-not-exist.md"),
            "--repo-root",
            str(repo),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1


def test_no_advisory_output_on_resolved_brief(tmp_path: Path) -> None:
    """Half A (the unlanded-direction-change advisory) is deleted — a
    resolved run must print only the resolution line, never an
    'Unlanded direction change:' line."""
    repo = tmp_path
    store = repo / "docs" / "loom" / "backlog"
    _write_bet_entry(store, "an-entry")

    brief = repo / "brief.md"
    brief.write_text("## Queue relation\n\nin-queue: an-entry\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(_SCRIPT), str(brief), "--repo-root", str(repo)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Unlanded direction change" not in result.stdout
