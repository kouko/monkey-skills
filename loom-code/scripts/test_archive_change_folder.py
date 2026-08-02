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


def test_stamping_the_last_frontmatter_field_keeps_the_closing_fence(tmp_path):
    """Pins that stamping the FINAL field of a frontmatter block leaves the
    closing `---` on its own line.

    Added 2026-08-02 by Task 7's orchestrator, from a code-quality-reviewer
    finding. Task 7 replaced `_stamp_status`'s `^status\\s*:\\s*(\\S+)\\s*$`
    with `_stamp_field`'s `\\S.*$` to fix a multi-word-value bug, and that
    swap silently fixed a SECOND corruption nobody had noticed: `\\s*`
    matches newlines, so on the old pattern the match ran past the value and
    swallowed the line terminator whenever `status:` was the block's last
    field — the replacement then glued the closing fence onto the value
    (`status: archived---`), destroying the frontmatter block.

    The three sibling stamp tests above all pass against that corrupted
    output (`"status: archived" in text` is true either way), which is how
    the bug survived. This test asserts the fence's own line, so reverting
    `_stamp_field`'s pattern to the `\\s*$` shape turns it red. Verified
    discriminating: run against the pre-Task-7 pattern, this fails with
    `'---\\nstatus: archived---\\n\\n## Why\\n'`.
    """
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(
        tmp_path, "add-widget",
        "---\nstatus: proposed\n---\n\n## Why\nBecause.\n",  # status is LAST
    )

    dest = mod.archive_change_folder(tmp_path, "add-widget", date="2026-07-10")

    text = (dest / "proposal.md").read_text(encoding="utf-8")
    assert text.startswith("---\nstatus: archived\n---\n")
    assert "archived---" not in text  # the fence was not glued to the value


def test_date_prefixed_destination_is_the_current_contract(tmp_path):
    """Pins the CURRENT destination-naming contract: the archived folder's
    name is always `<date>-<change-id>` (date first). This is a
    characterization test over existing behaviour, not new production
    code — it exists so Task 7 (single-file generalization, which makes the
    date prefix a parameter that is OFF for the file-unit caller) must
    consciously touch and re-justify this assertion rather than silently
    changing the naming rule."""
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(tmp_path, "add-widget", "## Why\nBecause.\n")

    dest = mod.archive_change_folder(tmp_path, "add-widget", date="2026-07-10")

    assert dest.name == "2026-07-10-add-widget"
    assert dest.parent == tmp_path / "docs" / "loom" / "archive"


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
    before = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*"))

    with pytest.raises(mod.ArchiveError, match="does not exist"):
        mod.archive_change_folder(tmp_path, "no-such-change", date="2026-07-10")

    after = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*"))
    assert before == after  # refusal is a no-op: no filesystem mutation


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
        "2026-02-30",  # shape-valid, calendar-invalid (February has no 30th)
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


# --- file unit (Task 7 generalization) -------------------------------------

def _make_entry_file(root: Path, name: str, frontmatter_and_body: str) -> Path:
    store = root / "docs" / "loom" / "backlog"
    store.mkdir(parents=True, exist_ok=True)
    path = store / name
    path.write_text(frontmatter_and_body, encoding="utf-8")
    return path


def test_file_unit_archive_keeps_the_filename_unchanged(tmp_path):
    """The file unit must not carry over the folder unit's date-prefixed
    destination naming: prefixing the archive date onto a backlog entry
    (which already carries its creation date in the filename) produces the
    double-date defect observed at
    docs/loom/archive/2026-07-18-2026-07-16-operational-kpi-quarterly/. It
    must also stamp BOTH `status: archived` and `archived: <date>` — the
    second field is required by scripts/backlog_index.py's --write mode
    (mid-execution spec correction recorded in this task's plan entry)."""
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_entry_file(
        tmp_path, "2026-08-01-alpha.md",
        "---\nname: 2026-08-01-alpha\nstatus: OPEN\n---\n\nBody.\n",
    )

    dest = mod.archive_change_folder(
        tmp_path, "2026-08-01-alpha.md", date="2026-08-02", unit="file"
    )

    assert dest == tmp_path / "docs" / "loom" / "backlog" / "archive" / "2026-08-01-alpha.md"
    assert dest.name == "2026-08-01-alpha.md"  # unrenamed: no second date prefix
    text = dest.read_text(encoding="utf-8")
    assert "status: archived" in text
    assert "archived: 2026-08-02" in text


def test_file_unit_stamp_replaces_multi_word_status_without_duplicating_the_field(tmp_path):
    """`CLOSED — SUPERSEDED` (em dash, U+2014) is a real member of the
    backlog store's closed status vocabulary (scripts/backlog_index.py,
    docs/loom/backlog/README.md) — the one member that is not a single
    whitespace-free token. A `(\\S+)` value pattern in the stamp regex
    misses this line entirely, so the stamp APPENDS a second `status:` line
    instead of replacing the first. parse_frontmatter is last-wins, so
    --validate would resolve 'archived' and pass — but any first-match
    reader (`grep -m1 '^status:'`, a human opening the file, a strict YAML
    loader) sees 'CLOSED — SUPERSEDED', a live-looking status on an
    archived entry. Assert exactly one status: line survives — not just
    that 'status: archived' appears somewhere, which passes even with the
    duplicate-line defect present."""
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_entry_file(
        tmp_path, "2026-08-01-alpha.md",
        "---\nname: 2026-08-01-alpha\nstatus: CLOSED — SUPERSEDED\n---\n\nBody.\n",
    )

    dest = mod.archive_change_folder(
        tmp_path, "2026-08-01-alpha.md", date="2026-08-02", unit="file"
    )

    text = dest.read_text(encoding="utf-8")
    status_lines = [line for line in text.splitlines() if line.startswith("status:")]
    assert status_lines == ["status: archived"]


def test_file_unit_refuses_calendar_invalid_date_without_touching_filesystem(tmp_path):
    """Round-2 whole-branch review bug: `_validate_date` checked only
    YYYY-MM-DD SHAPE, so a shape-valid but calendar-invalid date
    (2026-02-30, February has no 30th) passed the guard, the file-unit move
    proceeded, and `archived: 2026-02-30` was stamped into the moved entry
    -- then scripts/backlog_index.py's --validate/--write (which run
    strptime) rejected the already-moved entry, leaving the store
    unregenerable until a human hand-edited the archived file. Refuse the
    date up front, before any filesystem mutation, exactly like a
    traversal-shaped one."""
    mod = _load(_MODULE_PATH, "archive_change_folder")
    source = _make_entry_file(
        tmp_path, "2026-08-01-alpha.md",
        "---\nname: 2026-08-01-alpha\nstatus: OPEN\n---\n\nBody.\n",
    )

    with pytest.raises(mod.ArchiveError):
        mod.archive_change_folder(
            tmp_path, "2026-08-01-alpha.md", date="2026-02-30", unit="file"
        )

    # refusal is a no-op: source untouched, nothing moved to archive/
    assert source.is_file()
    assert not (
        tmp_path / "docs" / "loom" / "backlog" / "archive" / "2026-08-01-alpha.md"
    ).exists()


def test_file_unit_refuses_missing_entry_file(tmp_path):
    mod = _load(_MODULE_PATH, "archive_change_folder")
    (tmp_path / "docs" / "loom" / "backlog").mkdir(parents=True)

    with pytest.raises(mod.ArchiveError, match="does not exist"):
        mod.archive_change_folder(
            tmp_path, "no-such-entry.md", date="2026-08-02", unit="file"
        )


def test_file_unit_refuses_already_archived_status(tmp_path):
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_entry_file(
        tmp_path, "2026-08-01-alpha.md",
        "---\nname: 2026-08-01-alpha\nstatus: archived\narchived: 2026-08-01\n---\n\nBody.\n",
    )

    with pytest.raises(mod.ArchiveError, match="already archived"):
        mod.archive_change_folder(
            tmp_path, "2026-08-01-alpha.md", date="2026-08-02", unit="file"
        )

    assert (tmp_path / "docs" / "loom" / "backlog" / "2026-08-01-alpha.md").is_file()


def test_refuses_unrecognized_unit_without_touching_filesystem(tmp_path):
    """The `unit not in _UNITS` guard is production code and needs its own
    driving test (Three Laws of TDD, law 3) — an untested refusal branch is
    how a typo'd `unit="files"` could silently fall through to the folder
    path in a future caller instead of being refused."""
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(tmp_path, "add-widget", "## Why\nBecause.\n")

    with pytest.raises(mod.ArchiveError, match="invalid unit"):
        mod.archive_change_folder(
            tmp_path, "add-widget", date="2026-07-10", unit="files"
        )

    # refusal is a no-op: source folder untouched, nothing moved
    assert (tmp_path / "docs" / "loom" / "add-widget").is_dir()


def test_file_unit_refuses_destination_collision(tmp_path):
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_entry_file(tmp_path, "2026-08-01-alpha.md", "---\nstatus: OPEN\n---\n\nBody.\n")
    archive_dir = tmp_path / "docs" / "loom" / "backlog" / "archive"
    archive_dir.mkdir(parents=True)
    (archive_dir / "2026-08-01-alpha.md").write_text("pre-existing", encoding="utf-8")

    with pytest.raises(mod.ArchiveError, match="already exists"):
        mod.archive_change_folder(
            tmp_path, "2026-08-01-alpha.md", date="2026-08-02", unit="file"
        )

    assert (archive_dir / "2026-08-01-alpha.md").read_text(encoding="utf-8") == "pre-existing"


def test_file_unit_refuses_symlinked_entry_file(tmp_path):
    mod = _load(_MODULE_PATH, "archive_change_folder")
    store = tmp_path / "docs" / "loom" / "backlog"
    store.mkdir(parents=True)
    real_file = tmp_path / "real-elsewhere.md"
    real_file.write_text("---\nstatus: OPEN\n---\n\nBody.\n", encoding="utf-8")
    symlink_source = store / "2026-08-01-alpha.md"
    symlink_source.symlink_to(real_file)

    with pytest.raises(mod.ArchiveError, match="symlink"):
        mod.archive_change_folder(
            tmp_path, "2026-08-01-alpha.md", date="2026-08-02", unit="file"
        )

    assert symlink_source.is_symlink()
    assert real_file.is_file()


def test_file_unit_refuses_unsafe_identifiers_without_touching_filesystem(tmp_path):
    """Obligation-B discriminating test. Task 6's folder-unit parametrize
    (`test_refuses_unsafe_change_ids_without_touching_filesystem`) fails
    closed on all 7 of its cases via the is_dir() existence check alone —
    it never actually exercises the identifier guard once that check is
    branched by unit, so it cannot prove the file-unit path is guarded.

    This test picks a traversal identifier (`../outside.md`) that ESCAPES
    docs/loom/backlog/ to a file that genuinely exists one level up
    (`outside.md`, created below) — so if the identifier guard were
    removed, the existence check would find that file, the move would
    genuinely succeed (relocating it to a wrong, unstamped-as-intended
    location outside the archive/ subtree), and no ArchiveError would be
    raised at all. That is exactly what distinguishes this from Task 6's
    parametrize: here, only the guard stands between the identifier and a
    real filesystem mutation. Verified by temporarily commenting out the
    `_validate_change_id` call: this test goes red (DID NOT RAISE) with
    the guard removed, and green with it restored."""
    mod = _load(_MODULE_PATH, "archive_change_folder")
    (tmp_path / "docs" / "loom" / "backlog").mkdir(parents=True)
    outside = tmp_path / "docs" / "loom" / "outside.md"
    outside.write_text("---\nstatus: OPEN\n---\n\nBody.\n", encoding="utf-8")
    before = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*"))

    with pytest.raises(mod.ArchiveError, match="invalid identifier"):
        mod.archive_change_folder(
            tmp_path, "../outside.md", date="2026-08-02", unit="file"
        )

    after = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*"))
    assert before == after  # no filesystem mutation on a rejected identifier


def test_file_unit_stamp_write_failure_restores_source_file(tmp_path, monkeypatch):
    """When the stamp write fails, the file unit must fail loudly and roll
    the move back rather than leave an unstamped file at the destination —
    an unstamped archived entry reads as live to any agent that greps the
    store. (This test does NOT pin unconditionality — after the move, dest
    is always a file, so a hypothetical `if dest.is_file():` wrapper around
    the file-unit stamp would stay green here too; unconditionality is a
    code-shape property, not something a missing-child fixture can
    distinguish for this unit.)"""
    mod = _load(_MODULE_PATH, "archive_change_folder")
    source = _make_entry_file(
        tmp_path, "2026-08-01-alpha.md", "---\nstatus: OPEN\n---\n\nBody.\n"
    )

    original_write_text = Path.write_text

    def failing_write_text(self, *args, **kwargs):
        if self.name == "2026-08-01-alpha.md" and "archive" in self.parts:
            raise OSError("disk full (simulated)")
        return original_write_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", failing_write_text)

    with pytest.raises(mod.ArchiveError, match="stamp"):
        mod.archive_change_folder(
            tmp_path, "2026-08-01-alpha.md", date="2026-08-02", unit="file"
        )

    # source restored, dest gone — no stranded moved-but-unstamped state
    assert source.is_file()
    assert not (
        tmp_path / "docs" / "loom" / "backlog" / "archive" / "2026-08-01-alpha.md"
    ).exists()


# --- CLI --unit selector (Finding 4: the file unit was reachable only via
# the Python API; the docs arm's README.md Archive rule now documents a
# manual mv + hand-edit instead of this script, which is exactly the unsafe
# path the module docstring's OpenSpec #412 citation argues against). Pinned
# shape: `archive_change_folder.py <identifier> [root] [--date YYYY-MM-DD]
# [--unit folder|file]`, --unit defaulting to folder so every existing
# caller keeps working unchanged. -----------------------------------------

def test_cli_unit_file_exit_zero_on_success(tmp_path):
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_entry_file(
        tmp_path, "2026-08-01-alpha.md",
        "---\nname: 2026-08-01-alpha\nstatus: OPEN\n---\n\nBody.\n",
    )

    rc = mod.main(
        ["2026-08-01-alpha.md", str(tmp_path), "--date", "2026-08-02", "--unit", "file"]
    )

    assert rc == 0
    dest = tmp_path / "docs" / "loom" / "backlog" / "archive" / "2026-08-01-alpha.md"
    assert dest.is_file()
    text = dest.read_text(encoding="utf-8")
    assert "status: archived" in text
    assert "archived: 2026-08-02" in text


def test_cli_unit_file_exit_one_on_missing_entry_with_actionable_stderr(tmp_path, capsys):
    mod = _load(_MODULE_PATH, "archive_change_folder")
    (tmp_path / "docs" / "loom" / "backlog").mkdir(parents=True)

    rc = mod.main(
        ["no-such-entry.md", str(tmp_path), "--date", "2026-08-02", "--unit", "file"]
    )

    assert rc == 1
    captured = capsys.readouterr()
    assert "no-such-entry.md" in captured.err
    assert "does not exist" in captured.err


def test_cli_rejects_invalid_unit_value_without_touching_filesystem(tmp_path, capsys):
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(tmp_path, "add-widget", "## Why\nBecause.\n")
    before = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*"))

    rc = mod.main(["add-widget", str(tmp_path), "--date", "2026-07-10", "--unit", "bogus"])

    assert rc == 1
    captured = capsys.readouterr()
    assert "invalid unit" in captured.err
    after = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*"))
    assert before == after  # refusal is a no-op: no filesystem mutation


def test_cli_unit_omitted_defaults_to_folder(tmp_path):
    """Every existing caller (finishing-a-development-branch, AGENTS.md's
    prior declared command surface) invokes this script with no --unit flag
    at all; the CLI must keep archiving a change-folder by default."""
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(tmp_path, "add-widget", "## Why\nBecause.\n")

    rc = mod.main(["add-widget", str(tmp_path), "--date", "2026-07-10"])

    assert rc == 0
    assert (tmp_path / "docs" / "loom" / "archive" / "2026-07-10-add-widget").is_dir()


def test_cli_unit_requires_a_value(tmp_path, capsys):
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(tmp_path, "add-widget", "## Why\nBecause.\n")

    rc = mod.main(["add-widget", str(tmp_path), "--unit"])

    assert rc == 1
    captured = capsys.readouterr()
    assert "--unit" in captured.err
    assert (tmp_path / "docs" / "loom" / "add-widget").is_dir()  # untouched


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
