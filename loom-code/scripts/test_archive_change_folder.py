"""Tests for the deterministic change-folder archive script.

`archive_change_folder(root, change_id, date=...)` moves
`docs/loom/<change-id>/` -> `docs/loom/archive/<date>-<change-id>/` and
stamps a `status: closed` field into the moved `proposal.md`'s YAML
frontmatter (adding a minimal frontmatter block if the file had none).
`archived` is retired vocabulary (plan docs/loom/plans/2026-08-21-
dissolve-direction-layer.md, BI-10) — the closed status vocabulary is
exactly `open` / `bet` / `closed`, and no `archived: <date>` field is
written any more.

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
_BACKLOG_INDEX_PATH = Path(__file__).parent / "backlog_index.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclass() needs this pre-registered
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
    assert "status: closed" in text
    assert "title: Add widget" in text  # existing frontmatter preserved
    assert "## Why" in text  # body preserved


def test_happy_path_adds_minimal_frontmatter_when_absent(tmp_path):
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(tmp_path, "add-widget", "## Why\nBecause.\n")

    dest = mod.archive_change_folder(tmp_path, "add-widget", date="2026-07-10")

    text = (dest / "proposal.md").read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "status: closed" in text
    assert "## Why" in text  # original body preserved


def test_happy_path_stamps_over_existing_non_archived_status(tmp_path):
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(
        tmp_path, "add-widget",
        "---\nstatus: proposed\n---\n\n## Why\nBecause.\n",
    )

    dest = mod.archive_change_folder(tmp_path, "add-widget", date="2026-07-10")

    text = (dest / "proposal.md").read_text(encoding="utf-8")
    assert "status: closed" in text
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
    (`status: closed---`), destroying the frontmatter block.

    The three sibling stamp tests above all pass against that corrupted
    output (`"status: closed" in text` is true either way), which is how
    the bug survived. This test asserts the fence's own line, so reverting
    `_stamp_field`'s pattern to the `\\s*$` shape turns it red. Verified
    discriminating: run against the pre-Task-7 pattern, this fails with
    `'---\\nstatus: closed---\\n\\n## Why\\n'`.
    """
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(
        tmp_path, "add-widget",
        "---\nstatus: proposed\n---\n\n## Why\nBecause.\n",  # status is LAST
    )

    dest = mod.archive_change_folder(tmp_path, "add-widget", date="2026-07-10")

    text = (dest / "proposal.md").read_text(encoding="utf-8")
    assert text.startswith("---\nstatus: closed\n---\n")
    assert "closed---" not in text  # the fence was not glued to the value


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
    assert b"status: closed" in raw


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
    assert text.startswith("---\nstatus: closed\n---\n\n")
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


def test_closed_status_on_a_live_folder_does_not_block_archiving(tmp_path):
    """`status: closed` is legal on a LIVE (not-yet-archived) entry — the
    close-out flip is a separate, earlier step than archiving (docs/loom/
    backlog/README.md's Archive rule). Since `closed` is now ambiguous
    between "live and closed" and "already archived", the frontmatter can
    no longer be the idempotency signal (BI-10, plan DL-13) — a closed
    live folder must archive normally rather than being refused as
    'already archived'."""
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(
        tmp_path, "add-widget",
        "---\nstatus: closed\n---\n\n## Why\nBecause.\n",
    )

    dest = mod.archive_change_folder(tmp_path, "add-widget", date="2026-07-10")

    assert dest.is_dir()
    text = (dest / "proposal.md").read_text(encoding="utf-8")
    assert "status: closed" in text


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


def test_folder_unit_idempotency_survives_a_date_change(tmp_path):
    """Round-3 finding (arm B): the `status: archived` idempotency guard
    was dropped for BOTH units, justified by a property only the FILE
    unit has — its destination is a function of the identifier alone.
    The folder unit's destination interpolates a date, so a re-archive
    on a different day lands beside the first copy instead of refusing.
    The refusal must key on the change-id, not on the dated path."""
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(tmp_path, "add-widget", "## Why\nBecause.\n")

    first = mod.archive_change_folder(tmp_path, "add-widget", date="2026-08-01")
    assert first.is_dir()

    # Re-create the source (the real-world shape: a folder restored, or
    # re-created under the same change-id) and archive again a day later.
    _make_change_folder(tmp_path, "add-widget", "## Why\nBecause.\n")
    with pytest.raises(mod.ArchiveError, match="already exists"):
        mod.archive_change_folder(tmp_path, "add-widget", date="2026-08-02")

    archive_root = tmp_path / "docs" / "loom" / "archive"
    copies = sorted(p.name for p in archive_root.iterdir() if p.is_dir())
    assert copies == ["2026-08-01-add-widget"], (
        f"a second archive copy was created for the same change-id: {copies}"
    )


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
    must stamp `status: closed` — `archived` (and a separate `archived:
    <date>` field) is retired vocabulary; the closed status vocabulary is
    exactly `open` / `bet` / `closed` (BI-10, plan DL-13)."""
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_entry_file(
        tmp_path, "2026-08-01-alpha.md",
        "---\nname: 2026-08-01-alpha\nstatus: closed\n---\n\nBody.\n",
    )

    dest = mod.archive_change_folder(
        tmp_path, "2026-08-01-alpha.md", date="2026-08-02", unit="file"
    )

    assert dest == tmp_path / "docs" / "loom" / "backlog" / "archive" / "2026-08-01-alpha.md"
    assert dest.name == "2026-08-01-alpha.md"  # unrenamed: no second date prefix
    text = dest.read_text(encoding="utf-8")
    assert "status: closed" in text
    assert "archived:" not in text  # retired field is never written


def test_file_unit_stamp_replaces_a_multi_word_value_without_duplicating_the_field(tmp_path):
    """`_stamp_field` is generic over `key` (not status-only), and the
    backlog store's own frontmatter contract requires at least one field —
    `description:` — that is genuinely free-form, multi-word prose on every
    entry (docs/loom/backlog/README.md's Frontmatter contract; enforced by
    scripts/backlog_index.py's `_check_description`). `CLOSED — SUPERSEDED`
    here is NOT a real member of the closed status vocabulary (that
    vocabulary is exactly `open` / `bet` / `closed`,
    `backlog_index.CLOSED_STATUS_VOCABULARY`) — it stands in as an
    arbitrary pre-existing multi-word value on the field being stamped, the
    shape a single-token `(\\S+)` value pattern in the stamp regex would
    miss entirely, causing the stamp to APPEND a second `status:` line
    instead of replacing the first. parse_frontmatter is last-wins, so
    --validate would resolve 'closed' and pass — but any first-match
    reader (`grep -m1 '^status:'`, a human opening the file, a strict YAML
    loader) sees 'CLOSED — SUPERSEDED', a stale value on an archived
    entry. Assert exactly one status: line survives — not just that
    'status: closed' appears somewhere, which passes even with the
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
    assert status_lines == ["status: closed"]


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
        "---\nname: 2026-08-01-alpha\nstatus: closed\n---\n\nBody.\n",
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


def test_file_unit_closed_status_on_a_live_entry_does_not_block_archiving(tmp_path):
    """`status: closed` is the NORMAL pre-archive state for a backlog entry
    (docs/loom/backlog/README.md's Archive rule: the close-out flip is a
    separate, earlier step than archiving). With `archived` retired
    (BI-10, plan DL-13), `closed` is legal on a live entry too, so it can
    no longer be the idempotency signal — a closed live entry must archive
    normally, not be refused as 'already archived'."""
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_entry_file(
        tmp_path, "2026-08-01-alpha.md",
        "---\nname: 2026-08-01-alpha\nstatus: closed\n---\n\nBody.\n",
    )

    dest = mod.archive_change_folder(
        tmp_path, "2026-08-01-alpha.md", date="2026-08-02", unit="file"
    )

    assert dest.is_file()
    assert "status: closed" in dest.read_text(encoding="utf-8")


def test_file_unit_refuses_rearchiving_an_identifier_already_holding_an_archive_copy(tmp_path):
    """The genuine idempotency signal under the shipped model (BI-10, plan
    DL-13): the file unit's destination is deterministic from the
    identifier alone (no date in the path — `test_file_unit_archive_
    keeps_the_filename_unchanged`), so 'does an archive copy already exist
    for this identifier' is exactly the destination-occupancy check, not a
    frontmatter status. This reproduces that scenario end-to-end: archive
    once, recreate a live entry under the same identifier, and the second
    archive attempt must still be refused."""
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_entry_file(
        tmp_path, "2026-08-01-alpha.md",
        "---\nname: 2026-08-01-alpha\nstatus: closed\n---\n\nBody.\n",
    )
    mod.archive_change_folder(
        tmp_path, "2026-08-01-alpha.md", date="2026-08-02", unit="file"
    )
    _make_entry_file(
        tmp_path, "2026-08-01-alpha.md",
        "---\nname: 2026-08-01-alpha\nstatus: closed\n---\n\nBody (recreated).\n",
    )

    with pytest.raises(mod.ArchiveError, match="already exists"):
        mod.archive_change_folder(
            tmp_path, "2026-08-01-alpha.md", date="2026-08-09", unit="file"
        )

    # refusal must be a no-op: the recreated live entry is untouched
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
        "---\nname: 2026-08-01-alpha\nstatus: closed\n---\n\nBody.\n",
    )

    rc = mod.main(
        ["2026-08-01-alpha.md", str(tmp_path), "--date", "2026-08-02", "--unit", "file"]
    )

    assert rc == 0
    dest = tmp_path / "docs" / "loom" / "backlog" / "archive" / "2026-08-01-alpha.md"
    assert dest.is_file()
    text = dest.read_text(encoding="utf-8")
    assert "status: closed" in text
    assert "archived:" not in text  # retired field is never written


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


# --- backlog_index --validate interaction (BI-10, plan DL-13) -------------
#
# The corruption the archiver's writer half shipped: `--unit file` stamped
# `status: archived` (not in `backlog_index.CLOSED_STATUS_VOCABULARY`) plus
# a stray `archived: <date>` field onto every moved entry, so the store
# the archiver produces immediately failed its own validator with an
# `[archive-tier]` AND a `[status]` violation. No prior test in this file
# caught it because every test above checks the archiver's own output
# shape ("status: archived" in text) rather than whether that output is
# legal input to backlog_index.py — this is the assertion that closes that
# gap.

def test_file_unit_archiving_a_blocked_open_entry_passes_backlog_index_validate(tmp_path):
    """DL-13 re-run with the new field: `blocked:` is legal only on an
    `open` entry (backlog_index._check_blocked, invariant iv). The archiver
    stamps `status: closed` but, before this fix, left `blocked:` in place
    -- so archiving any blocked entry produced a store that failed its own
    `--validate` immediately after the archive that is supposed to leave it
    clean. This is the RED test: it fails pre-fix with a `[blocked]`
    violation ('blocked' field is only legal on 'open' entries, not
    'closed')."""
    archive_mod = _load(_MODULE_PATH, "archive_change_folder")
    backlog_index_mod = _load(_BACKLOG_INDEX_PATH, "backlog_index")
    _make_entry_file(
        tmp_path, "2026-08-01-alpha.md",
        "---\nname: 2026-08-01-alpha\nstatus: open\n"
        "blocked: waiting on upstream\n"
        "description: An example entry.\n---\n\nBody.\n",
    )

    dest = archive_mod.archive_change_folder(
        tmp_path, "2026-08-01-alpha.md", date="2026-08-02", unit="file"
    )

    text = dest.read_text(encoding="utf-8")
    assert "status: closed" in text
    assert "blocked:" not in text  # dropped when the entry is closed

    store = tmp_path / "docs" / "loom" / "backlog"
    violations = backlog_index_mod.find_violations(store)
    assert violations == []


def test_file_unit_archiving_leaves_unrelated_frontmatter_fields_intact(tmp_path):
    """The `blocked:` strip must be scoped to that one key -- a sibling
    field must survive unchanged."""
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_entry_file(
        tmp_path, "2026-08-01-alpha.md",
        "---\nname: 2026-08-01-alpha\nstatus: open\n"
        "blocked: waiting on upstream\n"
        "description: An example entry.\n---\n\nBody.\n",
    )

    dest = mod.archive_change_folder(
        tmp_path, "2026-08-01-alpha.md", date="2026-08-02", unit="file"
    )

    text = dest.read_text(encoding="utf-8")
    assert "description: An example entry." in text
    assert "name: 2026-08-01-alpha" in text


def test_file_unit_archiving_a_non_blocked_entry_is_unaffected(tmp_path):
    """No `blocked:` field present -> the strip is a no-op, not an error."""
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_entry_file(
        tmp_path, "2026-08-01-alpha.md",
        "---\nname: 2026-08-01-alpha\nstatus: open\n"
        "description: An example entry.\n---\n\nBody.\n",
    )

    dest = mod.archive_change_folder(
        tmp_path, "2026-08-01-alpha.md", date="2026-08-02", unit="file"
    )

    text = dest.read_text(encoding="utf-8")
    assert "status: closed" in text
    assert "description: An example entry." in text


def test_file_unit_archived_entry_passes_backlog_index_validate(tmp_path):
    """Archive a backlog entry, then run backlog_index.find_violations
    (the same check `--validate` runs) over the resulting store: it must
    report zero violations. This is the RED test for BI-10/DL-13 — it
    fails on the pre-fix code with an `[archive-tier]` violation
    ("status is 'archived', not 'closed'") and a `[status]` violation
    ("status 'archived' is not in the closed vocabulary")."""
    archive_mod = _load(_MODULE_PATH, "archive_change_folder")
    backlog_index_mod = _load(_BACKLOG_INDEX_PATH, "backlog_index")
    _make_entry_file(
        tmp_path, "2026-08-01-alpha.md",
        "---\nname: 2026-08-01-alpha\nstatus: closed\n"
        "description: An example entry.\n---\n\nBody.\n",
    )

    archive_mod.archive_change_folder(
        tmp_path, "2026-08-01-alpha.md", date="2026-08-02", unit="file"
    )

    store = tmp_path / "docs" / "loom" / "backlog"
    violations = backlog_index_mod.find_violations(store)
    assert violations == []


def test_unrelated_archive_directory_does_not_false_refuse(tmp_path):
    """Round-4 finding (arm B, 🟢): the folder unit's date-independent
    idempotency check compared `name[11:]` to the change-id without
    checking the first ten characters are actually a date, so an
    unrelated `archive/my-archive-foo/` refused change-id `foo`."""
    mod = _load(_MODULE_PATH, "archive_change_folder")
    _make_change_folder(tmp_path, "foo", "## Why\nBecause.\n")
    decoy = tmp_path / "docs" / "loom" / "archive" / "my-archive-foo"
    decoy.mkdir(parents=True)

    dest = mod.archive_change_folder(tmp_path, "foo", date="2026-08-21")
    assert dest.name == "2026-08-21-foo"
    assert decoy.is_dir()


def test_help_prints_usage_instead_of_archiving_a_folder_named_help(tmp_path):
    """Dogfood finding #5 (2026-08-21): this script hand-rolls its argv
    parsing, so `--help` fell through to the positional identifier and the
    user got `change-folder does not exist: .../docs/loom/--help` — a
    domain-specific error for the most ordinary first reflex there is."""
    import subprocess
    import sys as _sys

    for flag in ("--help", "-h"):
        result = subprocess.run(
            [_sys.executable, str(_MODULE_PATH), flag],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        combined = result.stdout + result.stderr
        assert result.returncode == 0, combined
        assert "does not exist" not in combined, combined
        assert "usage" in combined.lower(), combined
        assert "--unit" in combined and "--date" in combined, combined
