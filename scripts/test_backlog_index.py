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
        # Charter requires `archived: <date>` on every archive-tier entry
        # (docs/loom/backlog/README.md:20,24-27); a "clean" fixture must
        # carry it or --validate now correctly rejects it (GAP 1 below).
        _archived_entry("2026-07-01-closed-thing", "2026-07-15"),
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


# ---------------------------------------------------------------------------
# Revision round 1, GAP 1 — the charter (docs/loom/backlog/README.md:20,24-27)
# requires `archived: <YYYY-MM-DD>` on every archive-tier entry and forbids
# it on a live entry. Without these, a store could pass --validate clean and
# then fail loudly at --write — the two modes must agree on what "clean"
# means. `_archived_entry` is defined further below (Task 3 section); Python
# resolves it at call time, not at file-scan time, so forward reference here
# is safe.
# ---------------------------------------------------------------------------


def test_archive_tier_entry_missing_archived_date_field_is_rejected(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    _write(
        store,
        "archive/2026-07-01-closed-thing.md",
        _entry("2026-07-01-closed-thing", "archived"),  # no `archived:` field
    )

    result = _run_validate(store)

    assert result.returncode == 1
    assert "2026-07-01-closed-thing.md" in result.stdout


def test_archive_tier_entry_with_malformed_archived_date_is_rejected(tmp_path):
    """Presence alone is not enough — `archived: yesterday` would otherwise
    pass validation and render a nonsense '## Archived' line."""
    store = tmp_path / "backlog"
    store.mkdir()
    _write(
        store,
        "archive/2026-07-01-closed-thing.md",
        _archived_entry("2026-07-01-closed-thing", "yesterday"),
    )

    result = _run_validate(store)

    assert result.returncode == 1
    assert "2026-07-01-closed-thing.md" in result.stdout


def test_live_entry_carrying_archived_field_is_rejected(tmp_path):
    """Charter (README.md:27): 'archived' carries no meaning on a live entry
    and must not be set on one."""
    store = tmp_path / "backlog"
    store.mkdir()
    text = _entry("2026-08-01-alpha", "OPEN").replace(
        "status: OPEN\n", "status: OPEN\narchived: 2026-07-15\n"
    )
    _write(store, "2026-08-01-alpha.md", text)

    result = _run_validate(store)

    assert result.returncode == 1
    assert "2026-08-01-alpha.md" in result.stdout


# ---------------------------------------------------------------------------
# Task 3 — scripts/backlog_index.py --write
#
# Archived-date design decision: the pinned index shape's "## Archived" line
# needs a date with no source in the frontmatter contract as originally
# pinned. This task adds an `archived: <YYYY-MM-DD>` frontmatter field
# (stamped at archive time), documented in docs/loom/backlog/README.md
# alongside the pinned contract, rather than shelling out to git — the
# generator stays a pure function of the entry files' text, which is what
# keeps two --write runs over unchanged input byte-identical.
# ---------------------------------------------------------------------------


def _archived_entry(
    name: str,
    archived: str,
    description: str = "Should never appear in the Archived line.",
) -> str:
    return (
        "---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        "status: archived\n"
        f"archived: {archived}\n"
        "---\n\n"
        "Body text.\n"
    )


def _run_write(store: Path, output: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(BACKLOG_SCRIPT),
            "--write",
            "--store",
            str(store),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
    )


def _section(text: str, heading: str) -> str:
    """Text between `heading` and the next '## ' (or end of string).

    Section-scoped like the charter test's helper above — a heading can
    appear as a link target or prose elsewhere, so a whole-text substring
    check cannot tell "this entry is IN this section" from "the string
    occurs somewhere in the file".
    """
    _, _, after = text.partition(heading)
    assert after, f"expected heading {heading!r} not found in:\n{text}"
    body, _, _ = after.partition("\n## ")
    return body


def test_write_groups_live_entries_by_status_and_compacts_archived(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    _write(
        store,
        "2026-08-01-alpha.md",
        _entry("2026-08-01-alpha", "OPEN", description="Alpha unique marker description."),
    )
    _write(
        store,
        "2026-08-02-beta.md",
        _entry("2026-08-02-beta", "OPEN", description="Beta unique marker description."),
    )
    _write(
        store,
        "2026-08-03-gamma.md",
        _entry("2026-08-03-gamma", "PARKED", description="Gamma unique marker description."),
    )
    _write(
        store,
        "archive/2026-07-01-closed-thing.md",
        _archived_entry("2026-07-01-closed-thing", "2026-07-15"),
    )

    output = tmp_path / "BACKLOG.md"
    result = _run_write(store, output)
    assert result.returncode == 0, result.stdout + result.stderr

    text = output.read_text(encoding="utf-8")

    open_section = _section(text, "## OPEN")
    assert "Alpha unique marker description." in open_section
    assert "Beta unique marker description." in open_section

    parked_section = _section(text, "## PARKED")
    assert "Gamma unique marker description." in parked_section

    archived_section = _section(text, "## Archived")
    assert "2026-07-01-closed-thing (archived 2026-07-15)" in archived_section
    assert "Should never appear" not in archived_section

    # Kickoff-decision hard contract: COMMITTED-NEXT -> OPEN -> PARKED ->
    # UPSTREAM -> SHIPPED -> CLOSED — SUPERSEDED -> Archived.
    assert text.index("## OPEN") < text.index("## PARKED") < text.index("## Archived")


def test_write_omits_empty_status_sections(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "OPEN"))

    output = tmp_path / "BACKLOG.md"
    result = _run_write(store, output)
    assert result.returncode == 0, result.stdout + result.stderr

    text = output.read_text(encoding="utf-8")
    for heading in (
        "## COMMITTED-NEXT",
        "## PARKED",
        "## UPSTREAM",
        "## SHIPPED",
        "## CLOSED — SUPERSEDED",
        "## Archived",
    ):
        assert heading not in text, f"{heading} should be omitted when it has no entries"
    assert "## OPEN" in text


def test_write_is_idempotent_byte_identical_across_two_runs(tmp_path):
    """GAP 2 fix (revision round 1): a group of size 1 has only one possible
    ordering, so a single-entry-per-section fixture cannot exercise
    within-section ordering at all — it would pass unchanged even if
    build_index() collected entries via a non-deterministic set/dict-order
    path instead of sorting. This fixture carries 5 entries in one live
    section (OPEN) and 3 archived entries, so a within-section ordering
    regression has room to manifest. The two --write calls are independent
    `subprocess.run` process launches (not two in-process calls), which
    matters because CPython randomizes string hashing per process
    (PYTHONHASHSEED) — a set-based (order-losing) collection path would
    likely differ between the two subprocesses even though it might look
    stable across two in-process calls sharing one hash seed."""
    store = tmp_path / "backlog"
    store.mkdir()
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "OPEN", description="Alpha."))
    _write(store, "2026-08-02-beta.md", _entry("2026-08-02-beta", "OPEN", description="Beta."))
    _write(store, "2026-08-03-gamma.md", _entry("2026-08-03-gamma", "OPEN", description="Gamma."))
    _write(store, "2026-08-04-delta.md", _entry("2026-08-04-delta", "OPEN", description="Delta."))
    _write(store, "2026-08-05-epsilon.md", _entry("2026-08-05-epsilon", "OPEN", description="Epsilon."))
    _write(store, "2026-08-06-zeta.md", _entry("2026-08-06-zeta", "COMMITTED-NEXT"))
    _write(
        store,
        "archive/2026-07-01-closed-thing.md",
        _archived_entry("2026-07-01-closed-thing", "2026-07-15"),
    )
    _write(
        store,
        "archive/2026-06-01-older-thing.md",
        _archived_entry("2026-06-01-older-thing", "2026-06-10"),
    )
    _write(
        store,
        "archive/2026-05-01-oldest-thing.md",
        _archived_entry("2026-05-01-oldest-thing", "2026-05-05"),
    )

    result_a = _run_write(store, tmp_path / "BACKLOG_a.md")
    result_b = _run_write(store, tmp_path / "BACKLOG_b.md")

    assert result_a.returncode == 0, result_a.stdout + result_a.stderr
    assert result_b.returncode == 0, result_b.stdout + result_b.stderr
    assert (tmp_path / "BACKLOG_a.md").read_bytes() == (tmp_path / "BACKLOG_b.md").read_bytes()


def test_write_fails_loudly_when_archived_entry_missing_archived_date(tmp_path):
    """Design decision pinned above: the archived date comes from a new
    `archived:` frontmatter field, stamped at archive time. An entry under
    archive/ that lacks it cannot render its '## Archived' line — fail
    loudly rather than emitting a blank or fabricated date."""
    store = tmp_path / "backlog"
    store.mkdir()
    _write(
        store,
        "archive/2026-07-01-closed-thing.md",
        _entry("2026-07-01-closed-thing", "archived"),  # no `archived:` field
    )

    output = tmp_path / "BACKLOG.md"
    result = _run_write(store, output)

    assert result.returncode == 1
    assert "2026-07-01-closed-thing" in result.stdout + result.stderr
    assert not output.exists()


def test_write_rejects_a_malformed_archived_date_not_only_a_missing_one(tmp_path):
    """`--write` is documented as usable on its own, so presence alone is not
    enough: a malformed value would be rendered verbatim into the committed
    index, and `--check` would then regenerate the same string and call the
    file clean — laundering the bad value into the baseline."""
    store = tmp_path / "backlog"
    store.mkdir()
    _write(
        store,
        "archive/2026-07-01-closed-thing.md",
        _entry("2026-07-01-closed-thing", "archived").replace(
            "---\n\n", "archived: yesterday\n---\n\n", 1
        ),
    )

    output = tmp_path / "BACKLOG.md"
    result = _run_write(store, output)

    assert result.returncode == 1
    assert "2026-07-01-closed-thing" in result.stdout + result.stderr
    assert not output.exists()


def test_write_fails_loudly_on_live_entry_with_unrecognized_status(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "BOGUS-STATUS"))

    output = tmp_path / "BACKLOG.md"
    result = _run_write(store, output)

    assert result.returncode == 1
    assert "2026-08-01-alpha.md" in (result.stdout + result.stderr)
    assert not output.exists()


# ---------------------------------------------------------------------------
# Task 4 — scripts/backlog_index.py --check
#
# doctoc --dryrun pattern: regenerate the index in memory and compare it
# against the committed docs/loom/BACKLOG.md. Exit 1 with a diff summary on
# drift, 0 when identical. Never writes --output.
# ---------------------------------------------------------------------------


def _run_check(store: Path, output: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(BACKLOG_SCRIPT),
            "--check",
            "--store",
            str(store),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
    )


def test_check_passes_on_a_freshly_generated_index(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "OPEN"))

    output = tmp_path / "BACKLOG.md"
    write_result = _run_write(store, output)
    assert write_result.returncode == 0, write_result.stdout + write_result.stderr

    check_result = _run_check(store, output)
    assert check_result.returncode == 0, check_result.stdout + check_result.stderr


def test_check_detects_a_hand_edited_index(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "OPEN"))

    output = tmp_path / "BACKLOG.md"
    _run_write(store, output)
    # Hand-edit: append a line a human might add directly to the generated
    # index instead of authoring a new entry file.
    with output.open("a", encoding="utf-8") as f:
        f.write("- a hand-added line that did not come from any entry file\n")

    result = _run_check(store, output)

    assert result.returncode == 1
    assert "drift" in result.stdout.lower()


def test_check_detects_whitespace_only_drift(tmp_path):
    """A trailing-newline difference is exactly what a hand-edit or an
    editor's save-on-exit produces. --check must compare byte-for-byte, not
    a whitespace-normalized form, or this exact drift shape would silently
    pass."""
    store = tmp_path / "backlog"
    store.mkdir()
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "OPEN"))

    output = tmp_path / "BACKLOG.md"
    _run_write(store, output)
    with output.open("a", encoding="utf-8") as f:
        f.write("\n")  # one extra trailing blank line -- no visible content change

    result = _run_check(store, output)

    assert result.returncode == 1


def test_check_does_not_write_anything(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "OPEN"))

    output = tmp_path / "BACKLOG.md"
    _run_write(store, output)
    with output.open("a", encoding="utf-8") as f:
        f.write("- hand edit\n")
    drifted_text = output.read_text(encoding="utf-8")
    mtime_before = output.stat().st_mtime_ns

    result = _run_check(store, output)

    assert result.returncode == 1
    assert output.read_text(encoding="utf-8") == drifted_text, (
        "--check must never rewrite --output, even when it finds drift"
    )
    assert output.stat().st_mtime_ns == mtime_before


def test_check_fails_loudly_when_output_is_missing(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "OPEN"))

    output = tmp_path / "BACKLOG.md"  # never written

    result = _run_check(store, output)

    assert result.returncode == 1
    assert not output.exists()


def test_check_fails_loudly_on_build_error_without_writing(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    _write(
        store,
        "archive/2026-07-01-closed-thing.md",
        _entry("2026-07-01-closed-thing", "archived"),  # no `archived:` field
    )

    output = tmp_path / "BACKLOG.md"
    output.write_text("placeholder\n", encoding="utf-8")

    result = _run_check(store, output)

    assert result.returncode == 1
    assert output.read_text(encoding="utf-8") == "placeholder\n"


def test_check_against_real_store_reflects_current_migration_phase():
    """docs/loom/backlog/ holds no entries yet -- Task 5 migrates the 73
    docs/loom/BACKLOG.md entries into it. Regenerating the index from the
    currently-empty store and comparing it against the current hand-written
    2500+-line monolith is REAL drift, not a false negative caused by test
    scaffolding, so --check must currently report FAIL (exit 1).

    Task 5 must invert this assertion to `== 0` once the store is populated
    and docs/loom/BACKLOG.md is regenerated from it -- do not delete this
    test and do not leave it asserting drift once the migration lands; a
    test that still says "expect drift" after Task 5 ships is itself a bug.
    """
    real_store = REPO_ROOT / "docs" / "loom" / "backlog"
    real_output = REPO_ROOT / "docs" / "loom" / "BACKLOG.md"

    result = _run_check(real_store, real_output)

    assert result.returncode == 1, (
        "expected drift while docs/loom/backlog/ is still empty (pre-Task-5); "
        "if this now returns 0, Task 5 has landed -- invert this assertion to "
        "`== 0` per Task 5's own acceptance criteria, per this test's docstring"
    )
