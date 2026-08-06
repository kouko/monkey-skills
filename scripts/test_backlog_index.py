"""Tests for the loom family backlog store (docs/loom/backlog/).

Task 1 adds only the charter test. Task 2 adds the `--validate` half of
scripts/backlog_index.py. Later tasks (3-5, 8, 9) extend this file with
generator/check/migration tests.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHARTER_PATH = REPO_ROOT / "docs" / "loom" / "backlog" / "README.md"
BACKLOG_SCRIPT = REPO_ROOT / "scripts" / "backlog_index.py"

# Direct import (not subprocess) so the revision-round-1 tests below can reuse
# the production parse/extract helpers instead of duplicating their regex —
# duplicating it in the test would let the two drift silently.
_SPEC = importlib.util.spec_from_file_location("backlog_index", BACKLOG_SCRIPT)
backlog_index = importlib.util.module_from_spec(_SPEC)
sys.modules["backlog_index"] = backlog_index  # dataclass() needs this pre-registered
_SPEC.loader.exec_module(backlog_index)

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


def test_entry_missing_description_key_is_rejected(tmp_path):
    """Charter (docs/loom/backlog/README.md:16) lists `description` with no
    `<optional; ...>` marker -- it is contractual, like `name`/`status`. An
    entry that omits it entirely must fail --validate, not pass clean and
    then render a dangling `- [name](...) -- ` line at --write."""
    store = tmp_path / "backlog"
    store.mkdir()
    _write(
        store,
        "2026-08-01-alpha.md",
        "---\nname: 2026-08-01-alpha\nstatus: OPEN\n---\n\nBody text.\n",
    )

    result = _run_validate(store)

    assert result.returncode == 1
    assert "2026-08-01-alpha.md" in result.stdout


def test_entry_with_blank_description_is_rejected(tmp_path):
    """A present-but-empty `description:` value renders the exact same
    dangling-em-dash line as a missing key, so it is rejected the same way."""
    store = tmp_path / "backlog"
    store.mkdir()
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "OPEN", description=""))

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
    """Task 5 landed: docs/loom/backlog/ now holds the 73 migrated entries and
    docs/loom/BACKLOG.md was regenerated from them with `--write`. Regenerating
    the index again and comparing it against the committed file must therefore
    show NO drift (exit 0) -- this is the post-migration steady state the CI
    pytest step (loom-code-ci.yml:98) gates on every future PR.

    Inverted from the pre-Task-5 assertion (`== 1`, expected drift while the
    store was still empty) per that assertion's own docstring instruction.
    """
    real_store = REPO_ROOT / "docs" / "loom" / "backlog"
    real_output = REPO_ROOT / "docs" / "loom" / "BACKLOG.md"

    result = _run_check(real_store, real_output)

    assert result.returncode == 0, result.stdout + result.stderr


# ---------------------------------------------------------------------------
# Task 5 -- migrate the 73 docs/loom/BACKLOG.md entries into docs/loom/backlog/
# ---------------------------------------------------------------------------


def test_real_store_has_every_migrated_entry_and_validates_clean():
    """RED while docs/loom/backlog/ holds no entry files (only README.md):
    Task 5 splits BACKLOG.md's 73 `## ` entries into one file per entry, so
    the real store must hold at least 73 entry files and `--validate` over
    it must exit 0 (every migrated entry's frontmatter is well-formed).
    Task 9 adds the store's first hand-authored entry (the
    institution-maintenance.md follow-up), bumping the floor to 74.

    Deliberately a floor (`>=`), not `== 74`: this same branch ships two
    workflows that legitimately change the count going forward --
    loom-memory (loom-pipeline/skills/loom-memory/SKILL.md) routes a new
    backlog-shaped fact to a new entry file, and
    archive_change_folder.py's file unit MOVES a live entry into
    backlog/archive/. An exact-equality assertion would turn either
    legitimate action into a CI failure that reads as a defect report.
    The invariant worth pinning is migration completeness (no entry went
    missing), not a specific cardinality -- so entries are counted via
    `backlog_index._entry_files()`, which walks BOTH the live tier and
    archive/. Archiving moves a file between those two tiers without
    deleting it, so the combined total across both can only grow or hold
    steady from a legitimate archive; only real entry loss (corruption,
    accidental deletion) can drop it below the migration baseline."""
    real_store = REPO_ROOT / "docs" / "loom" / "backlog"

    entry_files = backlog_index._entry_files(real_store)
    assert len(entry_files) >= 74, (
        f"expected at least 74 entry files (73 migrated + Task 9's "
        f"hand-authored entry) across the live tier and archive/ under "
        f"{real_store}, found {len(entry_files)} -- entries appear to have "
        f"gone missing from the store"
    )

    result = _run_validate(real_store)
    assert result.returncode == 0, result.stdout + result.stderr


# ---------------------------------------------------------------------------
# Revision round 1 — GAP 1 (migration completeness sweep) + DECISION (a 5th
# --validate invariant: a frontmatter field and its matching body bullet must
# agree, when both are present).
# ---------------------------------------------------------------------------


def test_real_store_entries_with_a_body_bullet_have_the_matching_frontmatter_field():
    """GAP 1: two migrated entries carried a substantive `- Origin`/`- Start`
    body bullet but no matching frontmatter field at all (Task 5's own rule:
    "Origin and Start map to their fields where present"). Sweep the full
    73-entry corpus for the same class of gap -- this must find nothing once
    the two named entries are fixed to carry the field."""
    real_store = REPO_ROOT / "docs" / "loom" / "backlog"
    entry_files = sorted(p for p in real_store.glob("*.md") if p.name != "README.md")

    missing = []
    for path in entry_files:
        text = path.read_text(encoding="utf-8")
        frontmatter = backlog_index.parse_frontmatter(text)
        body = backlog_index._body_text(text)
        for field_key, field_label in (("origin", "Origin"), ("start", "Start")):
            if (
                backlog_index._find_body_bullet(body, field_label) is not None
                and frontmatter.get(field_key) is None
            ):
                missing.append(
                    f"{path.name}: has a '- {field_label}' bullet but no "
                    f"'{field_key}:' frontmatter field"
                )

    assert not missing, "\n".join(missing)


def _entry_with_body(name: str, status: str, extra_frontmatter: str, body: str) -> str:
    return (
        "---\n"
        f"name: {name}\n"
        "description: A fixture entry for field-agreement tests.\n"
        f"status: {status}\n"
        f"{extra_frontmatter}"
        "---\n\n"
        f"{body}\n"
    )


def test_origin_field_matching_a_line_wrapped_body_bullet_is_accepted(tmp_path):
    """The comparison must normalize whitespace: the frontmatter value is a
    single line, but the body bullet it was transcribed from typically wraps
    across several lines (exactly the shape of the two GAP-1 fixed entries)."""
    store = tmp_path / "backlog"
    store.mkdir()
    text = _entry_with_body(
        "2026-08-01-alpha",
        "OPEN",
        "origin: found during the whole-branch review of feat-x (PR #999).\n",
        "- Origin: found during the whole-branch review of feat-x\n  (PR #999).",
    )
    _write(store, "2026-08-01-alpha.md", text)

    result = _run_validate(store)

    assert result.returncode == 0, result.stdout + result.stderr


def test_origin_field_disagreeing_with_its_body_bullet_is_rejected(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    text = _entry_with_body(
        "2026-08-01-alpha",
        "OPEN",
        "origin: a DIFFERENT origin than the body states.\n",
        "- Origin: found during the whole-branch review of feat-x (PR #999).",
    )
    _write(store, "2026-08-01-alpha.md", text)

    result = _run_validate(store)

    assert result.returncode == 1
    assert "2026-08-01-alpha.md" in result.stdout


def test_start_field_matching_body_bullet_ignoring_parenthetical_qualifier_is_accepted(tmp_path):
    """The bullet's `(re-trigger)`-style parenthetical qualifier is metadata
    about the field, not part of its value, and must be stripped on both
    sides of the comparison (same rule the migration used to populate the
    field from the bullet in the first place)."""
    store = tmp_path / "backlog"
    store.mkdir()
    text = _entry_with_body(
        "2026-08-01-alpha",
        "PARKED",
        "start: a third real thing happens (Rule of Three).\n",
        "- Start (re-trigger): a third real thing happens\n  (Rule of Three).",
    )
    _write(store, "2026-08-01-alpha.md", text)

    result = _run_validate(store)

    assert result.returncode == 0, result.stdout + result.stderr


def test_start_field_disagreeing_with_its_body_bullet_is_rejected(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    text = _entry_with_body(
        "2026-08-01-alpha",
        "PARKED",
        "start: a DIFFERENT re-trigger condition entirely.\n",
        "- Start (re-trigger): a third real thing happens (Rule of Three).",
    )
    _write(store, "2026-08-01-alpha.md", text)

    result = _run_validate(store)

    assert result.returncode == 1
    assert "2026-08-01-alpha.md" in result.stdout


# ---------------------------------------------------------------------------
# Task 8 -- loom-pipeline's loom-memory skill must route a backlog-shaped item
# to the store (docs/loom/backlog/), not to the now-generated
# docs/loom/BACKLOG.md. Scoped to the "## record" section's classification
# step, not a whole-file substring search, so a stray historical mention
# elsewhere in the file cannot mask a live write-instruction, and so this
# test would still fail if someone reverted the wording back to naming the
# generated file as a write target.
# ---------------------------------------------------------------------------


LOOM_MEMORY_SKILL_PATH = (
    REPO_ROOT / "loom-pipeline" / "skills" / "loom-memory" / "SKILL.md"
)


def _loom_memory_record_section() -> str:
    text = LOOM_MEMORY_SKILL_PATH.read_text(encoding="utf-8")
    _, _, after = text.partition("## record")
    assert after, "loom-memory SKILL.md has no '## record' section"
    body, _, _ = after.partition("\n## ")
    return body


def test_loom_memory_skill_does_not_route_writes_to_the_generated_index():
    section = _loom_memory_record_section()
    assert "docs/loom/BACKLOG.md" not in section, (
        "loom-memory's '## record' step still instructs writing to the "
        "generated index docs/loom/BACKLOG.md -- it must route a "
        "backlog-shaped item to the docs/loom/backlog/ store instead"
    )
    assert "docs/loom/backlog/" in section, (
        "loom-memory's '## record' step does not name docs/loom/backlog/ "
        "(the store's entry-per-file directory) as the routing target for "
        "a backlog-shaped item"
    )


def test_origin_field_matching_bullet_followed_by_trailing_prose_is_accepted(tmp_path):
    """Round-2 whole-branch review bug: `_FIELD_BULLET_PATTERNS`'s capture
    group ran to `(?=\\n-\\s|\\Z)` under DOTALL -- everything up to the next
    column-0 bullet or end of body -- so ordinary prose that follows the
    bullet (separated by a blank line) got swallowed into the captured
    value, even though the bullet itself is byte-identical to its
    frontmatter twin. Worse, the store charter's own escape hatch --
    'fold the same information into ordinary prose instead' -- produces
    exactly this failing layout. Pinned semantics: the captured value ends
    at the FIRST of (1) a blank line, (2) a column-0 '- ' bullet, (3) end of
    text."""
    store = tmp_path / "backlog"
    store.mkdir()
    text = _entry_with_body(
        "2026-08-01-alpha",
        "OPEN",
        "origin: the CI lane drops coverage\n",
        "- Origin: the CI lane drops coverage\n\n"
        "Then a paragraph that follows the bullet.",
    )
    _write(store, "2026-08-01-alpha.md", text)

    result = _run_validate(store)

    assert result.returncode == 0, result.stdout + result.stderr


def test_agreement_check_is_a_noop_when_body_has_no_matching_bullet(tmp_path):
    """The invariant fires only when BOTH copies are present. An entry whose
    frontmatter carries `origin:` but whose body never restates it as a
    `- Origin:` bullet has nothing to disagree with -- this is not GAP 1's
    class (that is a missing-field gap, not an agreement gap) and is out of
    this invariant's scope by the orchestrator's own ruling."""
    store = tmp_path / "backlog"
    store.mkdir()
    text = _entry_with_body(
        "2026-08-01-alpha",
        "OPEN",
        "origin: found during a review, not restated in the body.\n",
        "- What: some unrelated bullet with no Origin/Start label at all.",
    )
    _write(store, "2026-08-01-alpha.md", text)

    result = _run_validate(store)

    assert result.returncode == 0, result.stdout + result.stderr


# ---------------------------------------------------------------------------
# Task 9 -- the store's first hand-authored entry (the store's own authoring
# dogfood): a REQUIRED follow-up recording that institution-maintenance.md's
# BACKLOG.md-header pointer is now stale, tracked outside this repo.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# --ready — the store's single READ surface (plan
# docs/loom/plans/2026-08-06-backlog-ready-verb-and-close-loop.md, Task 1).
# COMMITTED-NEXT first (filename order), then OPEN; excluded statuses
# (PARKED / UPSTREAM / SHIPPED / CLOSED — SUPERSEDED / archived) never
# listed; closing `ready: N committed / M open / K excluded by status` line.
# ---------------------------------------------------------------------------


def _ready_store(tmp_path: Path) -> Path:
    """One entry per status — two OPEN entries (with and without `start:`)
    so assertion (c) can check both the rendered and the absent case —
    plus one archive-tier entry. Shared by all five --ready assertions."""
    store = tmp_path / "backlog"
    store.mkdir()
    _write(
        store,
        "2026-08-01-committed.md",
        _entry("2026-08-01-committed", "COMMITTED-NEXT", description="Committed marker."),
    )
    _write(
        store,
        "2026-08-02-open-with-start.md",
        _entry(
            "2026-08-02-open-with-start", "OPEN", description="Open-with-start marker."
        ).replace("status: OPEN\n", "status: OPEN\nstart: a third real thing happens\n"),
    )
    _write(
        store,
        "2026-08-03-open-plain.md",
        _entry("2026-08-03-open-plain", "OPEN", description="Open-plain marker."),
    )
    _write(store, "2026-08-04-parked.md", _entry("2026-08-04-parked", "PARKED"))
    _write(store, "2026-08-05-upstream.md", _entry("2026-08-05-upstream", "UPSTREAM"))
    _write(store, "2026-08-06-shipped.md", _entry("2026-08-06-shipped", "SHIPPED"))
    _write(
        store,
        "2026-08-07-superseded.md",
        _entry("2026-08-07-superseded", "CLOSED — SUPERSEDED"),
    )
    _write(
        store,
        "archive/2026-07-01-archived.md",
        _archived_entry("2026-07-01-archived", "2026-07-15"),
    )
    return store


def _run_ready(store: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(BACKLOG_SCRIPT), "--ready", "--store", str(store)],
        capture_output=True,
        text=True,
    )


def test_ready_prints_committed_next_section_before_open(tmp_path):
    """(a) COMMITTED-NEXT is the 'now' queue — it must render before OPEN,
    and each section must actually contain its own entries (section-scoped,
    not whole-output substring)."""
    result = _run_ready(_ready_store(tmp_path))

    assert result.returncode == 0, result.stdout + result.stderr
    out = result.stdout
    assert "## COMMITTED-NEXT" in out and "## OPEN" in out, out
    assert out.index("## COMMITTED-NEXT") < out.index("## OPEN")
    committed_section = _section(out, "## COMMITTED-NEXT")
    assert "- 2026-08-01-committed — Committed marker." in committed_section
    open_section = _section(out, "## OPEN")
    assert "- 2026-08-02-open-with-start — Open-with-start marker." in open_section
    assert "- 2026-08-03-open-plain — Open-plain marker." in open_section


def test_ready_excludes_non_actionable_statuses(tmp_path):
    """(b) PARKED / UPSTREAM / SHIPPED / CLOSED — SUPERSEDED / archived are
    not actionable — none of their entries may appear anywhere in the
    output (they are only tallied in the count line)."""
    result = _run_ready(_ready_store(tmp_path))

    assert result.returncode == 0, result.stdout + result.stderr
    for excluded_name in (
        "2026-08-04-parked",
        "2026-08-05-upstream",
        "2026-08-06-shipped",
        "2026-08-07-superseded",
        "2026-07-01-archived",
    ):
        assert excluded_name not in result.stdout, (
            f"excluded-status entry {excluded_name} leaked into --ready output"
        )


def test_ready_start_line_rendered_only_for_entries_that_have_the_field(tmp_path):
    """(c) an entry whose frontmatter carries `start:` gets a second
    indented line directly under its own entry line; entries without the
    field get none (exactly one start line in the whole fixture output)."""
    result = _run_ready(_ready_store(tmp_path))

    assert result.returncode == 0, result.stdout + result.stderr
    lines = result.stdout.splitlines()
    idx = lines.index("- 2026-08-02-open-with-start — Open-with-start marker.")
    assert lines[idx + 1] == "  start: a third real thing happens", lines[idx + 1]
    assert result.stdout.count("  start:") == 1, result.stdout


def test_ready_count_line_reports_exact_numbers(tmp_path):
    """(d) the output ends with the exact tally: 1 committed, 2 open,
    5 excluded (parked + upstream + shipped + superseded + archived)."""
    result = _run_ready(_ready_store(tmp_path))

    assert result.returncode == 0, result.stdout + result.stderr
    non_empty = [line for line in result.stdout.splitlines() if line.strip()]
    assert non_empty[-1] == "ready: 1 committed / 2 open / 5 excluded by status"


def test_ready_is_a_mode_on_its_own_and_joins_the_no_mode_error(tmp_path):
    """(e) `--ready` is accepted with no other mode flag; and the no-mode
    parser error now names it alongside --validate/--write/--check."""
    store = _ready_store(tmp_path)

    result = _run_ready(store)
    assert result.returncode == 0, result.stdout + result.stderr

    no_mode = subprocess.run(
        [sys.executable, str(BACKLOG_SCRIPT), "--store", str(store)],
        capture_output=True,
        text=True,
    )
    assert no_mode.returncode == 2, no_mode.stdout + no_mode.stderr
    assert "--ready" in no_mode.stderr, no_mode.stderr


def test_the_deferred_rules_follow_up_is_tracked_in_the_store():
    """A future agent must find and understand this follow-up by grepping
    the store alone -- no plan reference required. Discriminating: fails if
    the entry is deleted (no match), if it is given a non-live status (it
    would render under no live section), or if it drops out of the
    regenerated index (present as a file but not surfaced)."""
    real_store = REPO_ROOT / "docs" / "loom" / "backlog"
    entry_files = [p for p in real_store.glob("*.md") if p.name != "README.md"]

    # Substring-match on "institution-maintenance.md" alone is not
    # discriminating: 2026-07-25-dev-workflow-loom-workflow-rename-evaluated-
    # not-recommended.md already cites that path incidentally, for an
    # unrelated rename-blast-radius concern (RED-run finding -- the first
    # draft of this test passed on a store with no follow-up entry at all).
    # Requiring BOTH markers together -- the rules file AND the generated
    # index it wrongly still claims defines the format -- is what pins the
    # match to THIS follow-up.
    matches = []
    for path in entry_files:
        text = path.read_text(encoding="utf-8")
        body = backlog_index._body_text(text)
        if "institution-maintenance.md" in body and "docs/loom/backlog/README.md" in body:
            matches.append(path)

    assert matches, (
        "no live entry under docs/loom/backlog/ has a body naming both "
        "'institution-maintenance.md' and 'docs/loom/backlog/README.md' -- "
        "the deferred rules-file follow-up is not tracked in the store"
    )
    assert len(matches) == 1, (
        f"expected exactly one entry to track this follow-up, found "
        f"{[p.name for p in matches]}"
    )
    entry_path = matches[0]

    frontmatter = backlog_index.parse_frontmatter(entry_path.read_text(encoding="utf-8"))
    status = frontmatter.get("status")
    assert status in backlog_index.STATUS_SECTION_ORDER, (
        f"{entry_path.name}: status {status!r} is not a live status -- it "
        "would not render under any live section of the generated index"
    )

    violations = [
        v for v in backlog_index.find_violations(real_store) if v.file == entry_path.name
    ]
    assert not violations, f"{entry_path.name} fails --validate: {violations}"

    generated = backlog_index.build_index(real_store)
    name = frontmatter.get("name", entry_path.stem)
    assert f"## {status}\n" in generated, f"generated index has no '## {status}' section at all"
    _, _, after_heading = generated.partition(f"## {status}\n")
    next_heading = after_heading.find("\n## ")
    section_body = after_heading if next_heading == -1 else after_heading[:next_heading]
    assert f"[{name}](backlog/{name}.md)" in section_body, (
        f"{name} does not appear under its '## {status}' section in the "
        "regenerated index -- present as a file but not surfaced"
    )


# ---------------------------------------------------------------------------
# Fix round 1 (whole-branch review) -- build_ready() must honor the
# archive tier, not just the frontmatter status.
# ---------------------------------------------------------------------------


def test_ready_excludes_archive_tier_entry_regardless_of_status(tmp_path):
    """A file physically under `archive/` that (incorrectly, or from a
    stale migration) still carries an actionable status like OPEN must
    NOT leak into the actionable output -- the archive tier overrides
    the frontmatter status. It must instead be counted in the excluded
    tally."""
    store = tmp_path / "backlog"
    store.mkdir()
    _write(
        store,
        "2026-08-01-open-plain.md",
        _entry("2026-08-01-open-plain", "OPEN", description="Legit open marker."),
    )
    _write(
        store,
        "archive/2026-07-01-mis-tiered.md",
        _entry(
            "2026-07-01-mis-tiered",
            "OPEN",
            description="Should never render -- physically archived.",
        ),
    )

    result = _run_ready(store)

    assert result.returncode == 0, result.stdout + result.stderr
    out = result.stdout
    assert "2026-07-01-mis-tiered" not in out, (
        "archive-tier entry leaked into --ready output despite a "
        "non-archived status"
    )
    open_section = _section(out, "## OPEN")
    assert "- 2026-08-01-open-plain — Legit open marker." in open_section
    assert "2026-07-01-mis-tiered" not in open_section
    non_empty = [line for line in out.splitlines() if line.strip()]
    assert non_empty[-1] == "ready: 0 committed / 1 open / 1 excluded by status", non_empty[-1]


def test_ready_fails_loudly_on_status_outside_closed_vocabulary(tmp_path):
    """(a) An entry with a status outside the closed vocabulary must fail
    --ready loudly (exit 1) with the FAIL message, mirroring --write /
    --check's behavior for the same malformed input -- never silently
    laundered into the excluded tally."""
    store = tmp_path / "backlog"
    store.mkdir()
    _write(
        store,
        "2026-08-01-bogus.md",
        _entry("2026-08-01-bogus", "NOT-A-REAL-STATUS"),
    )

    result = subprocess.run(
        [sys.executable, str(BACKLOG_SCRIPT), "--ready", "--store", str(store)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1, result.stdout + result.stderr
    assert "backlog_index --ready: FAIL —" in result.stdout, result.stdout
    assert "NOT-A-REAL-STATUS" in result.stdout, result.stdout


def test_ready_on_empty_store_prints_zero_count_line_only(tmp_path):
    """(c) A store holding only README.md (no entry files at all) has
    nothing actionable and nothing excluded -- `--ready` must exit 0
    printing exactly the zero-tally count line, with no section
    heading at all (not even an empty one)."""
    store = tmp_path / "backlog"
    store.mkdir()
    _write(store, "README.md", "# fixture store, no entries\n")

    result = _run_ready(store)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == "ready: 0 committed / 0 open / 0 excluded by status\n"


def test_ready_omits_committed_next_heading_when_empty(tmp_path):
    """(b) A store with no COMMITTED-NEXT entries at all must omit the
    '## COMMITTED-NEXT' heading entirely (not print an empty section),
    while the count line still reports the correct numbers -- this is
    the real store's current shape."""
    store = tmp_path / "backlog"
    store.mkdir()
    _write(
        store,
        "2026-08-01-open-plain.md",
        _entry("2026-08-01-open-plain", "OPEN", description="Open-plain marker."),
    )
    _write(store, "2026-08-02-parked.md", _entry("2026-08-02-parked", "PARKED"))

    result = _run_ready(store)

    assert result.returncode == 0, result.stdout + result.stderr
    out = result.stdout
    assert "## COMMITTED-NEXT" not in out, out
    assert "## OPEN" in out
    non_empty = [line for line in out.splitlines() if line.strip()]
    assert non_empty[-1] == "ready: 0 committed / 1 open / 1 excluded by status"
