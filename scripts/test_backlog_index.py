"""Tests for the loom family backlog store (docs/loom/backlog/).

Task 1 adds only the charter test. Task 2 adds the `--validate` half of
scripts/backlog_index.py. Later tasks (3-5, 8, 9) extend this file with
generator/check/migration tests.
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHARTER_PATH = REPO_ROOT / "docs" / "loom" / "backlog" / "README.md"
BACKLOG_SCRIPT = REPO_ROOT / "scripts" / "backlog_index.py"

# Transcribed VERBATIM from the plan's §Pinned frontmatter contract
# (docs/loom/plans/2026-08-01-backlog-one-entry-per-file.md, ## Notes).
CLOSED_STATUS_VOCABULARY = [
    "COMMITTED-NEXT",
    "OPEN",
    "PARKED",
    "UPSTREAM",
    "SHIPPED",
    "CLOSED — SUPERSEDED",
    "archived",
]


def _charter_vocabulary_section() -> str:
    """The charter's §Closed status vocabulary body, nothing else.

    Scoped deliberately: the bare word "archived" also appears ~8 times in
    the charter's ordinary archive-rule prose, so a whole-file substring
    search cannot tell "the enum documents this value" from "the English
    word happens to occur". Section-scoped + backtick-fenced is what makes
    the assertion fail when an enum entry is actually removed.
    """
    text = CHARTER_PATH.read_text(encoding="utf-8")
    _, _, after = text.partition("## Closed status vocabulary")
    assert after, "charter has no '## Closed status vocabulary' section"
    body, _, _ = after.partition("\n## ")
    return body


def test_charter_documents_the_closed_status_vocabulary():
    assert CHARTER_PATH.is_file(), f"charter missing at {CHARTER_PATH}"
    section = _charter_vocabulary_section()
    for status in CLOSED_STATUS_VOCABULARY:
        assert f"- `{status}`" in section, (
            f"charter's vocabulary section does not LIST status {status!r} "
            f"as an enum bullet (prose mentioning it does not count)"
        )


# ---------------------------------------------------------------------------
# Task 2 — scripts/backlog_index.py --validate
# ---------------------------------------------------------------------------


def _entry(name: str, status: str, description: str = "A fixture entry for backlog_index tests.") -> str:
    return (
        "---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        f"status: {status}\n"
        "---\n\n"
        "Body text.\n"
    )


def _write(store: Path, rel: str, text: str) -> None:
    path = store / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _run_validate(store: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(BACKLOG_SCRIPT), "--validate", "--store", str(store)],
        capture_output=True,
        text=True,
    )


def test_rejects_entry_whose_filename_does_not_match_frontmatter_name(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    # Filename stem is "2026-08-01-alpha" but frontmatter claims a different name.
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-beta", "OPEN"))

    result = _run_validate(store)

    assert result.returncode == 1
    assert "2026-08-01-alpha.md" in result.stdout


def test_clean_store_passes(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "OPEN"))
    _write(
        store,
        "archive/2026-07-01-closed-thing.md",
        _entry("2026-07-01-closed-thing", "archived"),
    )

    result = _run_validate(store)

    assert result.returncode == 0, result.stdout + result.stderr


def test_empty_store_passes(tmp_path):
    """Pinned decision: a store holding no entries (only README.md, or nothing
    at all) has nothing to violate, so --validate exits 0. This is the state
    the real docs/loom/backlog/ store is in until Task 5 migrates entries."""
    store = tmp_path / "backlog"
    store.mkdir()
    _write(store, "README.md", "# fixture store, no entries\n")

    result = _run_validate(store)

    assert result.returncode == 0, result.stdout + result.stderr


def test_live_entry_carrying_status_archived_is_rejected(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    # Directly under the store (NOT under archive/), yet claims archived status.
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "archived"))

    result = _run_validate(store)

    assert result.returncode == 1
    assert "2026-08-01-alpha.md" in result.stdout


def test_archived_entry_carrying_a_live_status_is_rejected(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    _write(
        store,
        "archive/2026-07-01-closed-thing.md",
        _entry("2026-07-01-closed-thing", "OPEN"),
    )

    result = _run_validate(store)

    assert result.returncode == 1
    assert "2026-07-01-closed-thing.md" in result.stdout


def test_status_outside_the_closed_vocabulary_is_rejected(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "BOGUS-STATUS"))

    result = _run_validate(store)

    assert result.returncode == 1
    assert "2026-08-01-alpha.md" in result.stdout


def test_readme_md_directly_under_store_is_never_treated_as_an_entry(tmp_path):
    """README.md carries no frontmatter at all; it must be excluded from
    scanning, not reported as a violation."""
    store = tmp_path / "backlog"
    store.mkdir()
    _write(store, "README.md", "# not an entry\n")
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "OPEN"))

    result = _run_validate(store)

    assert result.returncode == 0, result.stdout + result.stderr
