"""Tests for the deterministic change-folder archive script.

`archive_change_folder(root, change_id, date=...)` moves
`docs/loom/<change-id>/` -> `docs/loom/archive/<date>-<change-id>/` and
stamps a `status: archived` field into the moved `proposal.md`'s YAML
frontmatter (adding a minimal frontmatter block if the file had none).

Path-safety is the test focus (mirrors OpenSpec issue #412's bug class:
a change-id that is not a single path segment must never be allowed to
escape `docs/loom/` via `../` traversal or an absolute path).

Also pins the `check-living-spec-index.py` interaction: after an
archive, the living-spec structural gate must still exit 0 over the
same root (an archived change-folder's markdown is not a
`test_*.py`/`*_test.py` file, so the structural scanner never walks
it — this test locks that in rather than leaving it as an assumption).

Stdlib only (pathlib, subprocess, importlib for the hyphenated sibling
module — mirrors `test_check_living_spec_index.py`).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MODULE_PATH = Path(__file__).parent / "archive_change_folder.py"
_INDEX_CHECKER_PATH = Path(__file__).parent / "check-living-spec-index.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _make_change_folder(root: Path, change_id: str, proposal_text: str) -> Path:
    folder = root / "docs" / "loom" / change_id
    (folder / "specs" / "some-capability").mkdir(parents=True)
    (folder / "proposal.md").write_text(proposal_text, encoding="utf-8")
    (folder / "specs" / "some-capability" / "spec.md").write_text(
        "## ADDED Requirements\n", encoding="utf-8"
    )
    return folder


# --- happy path --------------------------------------------------------

def test_happy_path_moves_folder_to_dated_archive_dir(tmp_path):
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(
        tmp_path, "add-widget",
        "---\ntitle: Add widget\n---\n\n## Why\nBecause.\n",
    )

    dest = mod.archive_change_folder(tmp_path, "add-widget", date="2026-07-10")

    assert dest == tmp_path / "docs" / "loom" / "archive" / "2026-07-10-add-widget"
    assert not (tmp_path / "docs" / "loom" / "add-widget").exists()
    assert (dest / "proposal.md").is_file()
    assert (dest / "specs" / "some-capability" / "spec.md").is_file()


def test_happy_path_stamps_status_into_existing_frontmatter(tmp_path):
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(
        tmp_path, "add-widget",
        "---\ntitle: Add widget\n---\n\n## Why\nBecause.\n",
    )

    dest = mod.archive_change_folder(tmp_path, "add-widget", date="2026-07-10")

    text = (dest / "proposal.md").read_text(encoding="utf-8")
    assert "status: archived" in text
    assert "title: Add widget" in text  # existing frontmatter preserved
    assert "## Why" in text  # body preserved


def test_happy_path_adds_minimal_frontmatter_when_absent(tmp_path):
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(tmp_path, "add-widget", "## Why\nBecause.\n")

    dest = mod.archive_change_folder(tmp_path, "add-widget", date="2026-07-10")

    text = (dest / "proposal.md").read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "status: archived" in text
    assert "## Why" in text  # original body preserved


def test_happy_path_stamps_over_existing_non_archived_status(tmp_path):
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(
        tmp_path, "add-widget",
        "---\nstatus: proposed\n---\n\n## Why\nBecause.\n",
    )

    dest = mod.archive_change_folder(tmp_path, "add-widget", date="2026-07-10")

    text = (dest / "proposal.md").read_text(encoding="utf-8")
    assert "status: archived" in text
    assert "status: proposed" not in text


def test_crlf_proposal_normalizes_to_lf_on_write(tmp_path):
    """Pins current behavior: Path.read_text/write_text apply universal
    newline translation, so a CRLF-authored proposal.md is NOT left
    byte-for-byte untouched — it normalizes to LF."""
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(
        tmp_path, "add-widget",
        "---\r\ntitle: Add widget\r\n---\r\n\r\n## Why\r\nBecause.\r\n",
    )

    dest = mod.archive_change_folder(tmp_path, "add-widget", date="2026-07-10")

    raw = (dest / "proposal.md").read_bytes()
    assert b"\r\n" not in raw
    assert b"status: archived" in raw


def test_unclosed_frontmatter_treated_as_plain_body(tmp_path):
    """Pins current behavior: an opening '---' with no closing '---' line
    does not match the frontmatter regex at all, so it is treated as plain
    body and a NEW minimal frontmatter block is prepended ahead of it."""
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(
        tmp_path, "add-widget",
        "---\ntitle: Add widget\n## Why\nBecause.\n",  # no closing '---'
    )

    dest = mod.archive_change_folder(tmp_path, "add-widget", date="2026-07-10")

    text = (dest / "proposal.md").read_text(encoding="utf-8")
    assert text.startswith("---\nstatus: archived\n---\n\n")
    assert "title: Add widget" in text  # original (unclosed) text preserved as body


# --- refusal cases -------------------------------------------------------

def test_refuses_missing_change_folder(tmp_path):
    mod = _load(_MODULE_PATH, "archive_change_folder")
    (tmp_path / "docs" / "loom").mkdir(parents=True)

    with pytest.raises(mod.ArchiveError, match="does not exist"):
        mod.archive_change_folder(tmp_path, "no-such-change", date="2026-07-10")


def test_refuses_already_archived_status(tmp_path):
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(
        tmp_path, "add-widget",
        "---\nstatus: archived\n---\n\n## Why\nBecause.\n",
    )

    with pytest.raises(mod.ArchiveError, match="already archived"):
        mod.archive_change_folder(tmp_path, "add-widget", date="2026-07-10")

    # refusal must be a no-op: the source folder is untouched
    assert (tmp_path / "docs" / "loom" / "add-widget").is_dir()


def test_refuses_destination_collision(tmp_path):
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(tmp_path, "add-widget", "## Why\nBecause.\n")
    dest = tmp_path / "docs" / "loom" / "archive" / "2026-07-10-add-widget"
    dest.mkdir(parents=True)
    (dest / "sentinel.txt").write_text("pre-existing", encoding="utf-8")

    with pytest.raises(mod.ArchiveError, match="already exists"):
        mod.archive_change_folder(tmp_path, "add-widget", date="2026-07-10")

    # refusal must not clobber the pre-existing destination
    assert (dest / "sentinel.txt").read_text(encoding="utf-8") == "pre-existing"


# --- path-safety (OpenSpec #412 bug class) --------------------------------

@pytest.mark.parametrize(
    "bad_change_id",
    [
        "../escape",
        "foo/../../etc",
        "sub/dir",
        "/etc/passwd",
        "",
        ".",
        "..",
    ],
)
def test_refuses_unsafe_change_ids_without_touching_filesystem(tmp_path, bad_change_id):
    mod = _load(_MODULE_PATH, "archive_change_folder")
    (tmp_path / "docs" / "loom").mkdir(parents=True)
    before = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*"))

    with pytest.raises(mod.ArchiveError):
        mod.archive_change_folder(tmp_path, bad_change_id, date="2026-07-10")

    after = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*"))
    assert before == after  # no filesystem mutation on a rejected id


@pytest.mark.parametrize(
    "bad_date",
    [
        "../../../../tmp/x",
        "../escape",
        "not-a-date",
        "2026/07/10",
        "",
        "2026-07-10-extra",
    ],
)
def test_refuses_unsafe_or_malformed_dates_without_touching_filesystem(tmp_path, bad_date):
    """The `date` stamp is interpolated straight into the destination path
    (`docs/loom/archive/<date>-<change-id>/`) — a traversal-shaped or simply
    malformed value must be refused before any filesystem mutation, exactly
    like an unsafe change-id."""
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(tmp_path, "add-widget", "## Why\nBecause.\n")
    before = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*"))

    with pytest.raises(mod.ArchiveError):
        mod.archive_change_folder(tmp_path, "add-widget", date=bad_date)

    after = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*"))
    assert before == after  # no filesystem mutation on a rejected date


def test_cli_refuses_traversal_date_with_actionable_stderr(tmp_path, capsys):
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(tmp_path, "add-widget", "## Why\nBecause.\n")

    rc = mod.main(["add-widget", str(tmp_path), "--date", "../../../../tmp/x"])

    assert rc == 1
    captured = capsys.readouterr()
    assert "date" in captured.err
    # refusal is a no-op: source folder untouched, nothing escaped tmp_path
    assert (tmp_path / "docs" / "loom" / "add-widget").is_dir()


# --- symlinked change-folder ------------------------------------------------

def test_refuses_symlinked_change_folder(tmp_path):
    """A symlinked `docs/loom/<change-id>` must never be 'archived' as a live
    symlink pointing elsewhere — refuse it explicitly rather than letting
    shutil.move relocate the link target's contents."""
    mod = _load(_MODULE_PATH, "archive_change_folder")
    (tmp_path / "docs" / "loom").mkdir(parents=True)
    real_dir = tmp_path / "real-elsewhere"
    real_dir.mkdir()
    (real_dir / "proposal.md").write_text("## Why\nBecause.\n", encoding="utf-8")

    symlink_source = tmp_path / "docs" / "loom" / "add-widget"
    symlink_source.symlink_to(real_dir, target_is_directory=True)

    with pytest.raises(mod.ArchiveError, match="symlink"):
        mod.archive_change_folder(tmp_path, "add-widget", date="2026-07-10")

    # refusal is a no-op: the symlink and its real target are both untouched
    assert symlink_source.is_symlink()
    assert real_dir.is_dir()
    assert (real_dir / "proposal.md").is_file()


# --- stamp-write failure recovery ------------------------------------------

def test_stamp_write_failure_restores_source_folder(tmp_path, monkeypatch):
    """If the post-move stamp write fails, the moved folder must not be left
    stranded (moved-but-unstamped) with no recovery path — the implementation
    must move it back to its original location and raise ArchiveError naming
    both the stamp failure and the restore outcome."""
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(tmp_path, "add-widget", "## Why\nBecause.\n")

    original_write_text = Path.write_text

    def failing_write_text(self, *args, **kwargs):
        if self.name == "proposal.md" and "archive" in self.parts:
            raise OSError("disk full (simulated)")
        return original_write_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", failing_write_text)

    with pytest.raises(mod.ArchiveError, match="stamp"):
        mod.archive_change_folder(tmp_path, "add-widget", date="2026-07-10")

    # source restored, dest gone — no stranded moved-but-unstamped state
    assert (tmp_path / "docs" / "loom" / "add-widget").is_dir()
    assert not (tmp_path / "docs" / "loom" / "archive" / "2026-07-10-add-widget").exists()


def test_cli_stamp_write_failure_exit_one_actionable_stderr(tmp_path, monkeypatch, capsys):
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(tmp_path, "add-widget", "## Why\nBecause.\n")

    original_write_text = Path.write_text

    def failing_write_text(self, *args, **kwargs):
        if self.name == "proposal.md" and "archive" in self.parts:
            raise OSError("disk full (simulated)")
        return original_write_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", failing_write_text)

    rc = mod.main(["add-widget", str(tmp_path), "--date", "2026-07-10"])

    assert rc == 1
    captured = capsys.readouterr()
    assert "stamp" in captured.err
    assert (tmp_path / "docs" / "loom" / "add-widget").is_dir()
    assert not (tmp_path / "docs" / "loom" / "archive" / "2026-07-10-add-widget").exists()


# --- CLI ------------------------------------------------------------------

def test_cli_exit_zero_on_success(tmp_path):
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(tmp_path, "add-widget", "## Why\nBecause.\n")

    rc = mod.main(["add-widget", str(tmp_path), "--date", "2026-07-10"])

    assert rc == 0
    assert (tmp_path / "docs" / "loom" / "archive" / "2026-07-10-add-widget").is_dir()


def test_cli_exit_one_on_missing_folder_with_actionable_stderr(tmp_path, capsys):
    mod = _load(_MODULE_PATH, "archive_change_folder")
    (tmp_path / "docs" / "loom").mkdir(parents=True)

    rc = mod.main(["no-such-change", str(tmp_path), "--date", "2026-07-10"])

    assert rc == 1
    captured = capsys.readouterr()
    assert "no-such-change" in captured.err
    assert "does not exist" in captured.err


# --- living-spec-index interaction ----------------------------------------

def test_living_spec_index_still_green_after_archive(tmp_path):
    """archive/ folders hold only markdown (proposal.md, specs/*/spec.md),
    never a `test_*.py`/`*_test.py` file, so the living-spec structural
    scanner's test-file glob never walks into them. Pin that finding: after
    an archive, `check-living-spec-index.py` over the same root still
    exits 0 with no structural violations."""
    archive_mod = _load(_MODULE_PATH, "archive_change_folder")
    index_mod = _load(_INDEX_CHECKER_PATH, "check_living_spec_index")

    _make_change_folder(tmp_path, "add-widget", "## Why\nBecause.\n")
    archive_mod.archive_change_folder(tmp_path, "add-widget", date="2026-07-10")

    rc = index_mod.main([str(tmp_path)])

    assert rc == 0
