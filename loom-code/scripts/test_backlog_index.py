"""Tests for the loom family backlog store (docs/loom/backlog/).

Task 1 adds only the charter test. Task 2 adds the `--validate` half of
scripts/backlog_index.py. Later tasks (3-5, 8, 9) extend this file with
generator/check/migration tests.
"""

import importlib.util
import re
import subprocess
import sys

import pytest
from pathlib import Path

# This file lives at loom-code/scripts/ (inside the plugin — Task 1 of
# docs/loom/plans/2026-08-10-ship-progress-tooling.md), so the repo
# root is three levels up; the script under test ships beside it.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CHARTER_PATH = REPO_ROOT / "docs" / "loom" / "backlog" / "README.md"
# BI-11: templates/backlog-README.md is the canonical block; the live
# charter above is its instantiated copy. Both must agree with
# CLOSED_STATUS_VOCABULARY, or loom_init.py scaffolds a wrong charter
# into every newly adopting repo.
TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "backlog-README.md"
BACKLOG_SCRIPT = Path(__file__).resolve().parent / "backlog_index.py"

# Direct import (not subprocess) so the revision-round-1 tests below can reuse
# the production parse/extract helpers instead of duplicating their regex —
# duplicating it in the test would let the two drift silently.
_SPEC = importlib.util.spec_from_file_location("backlog_index", BACKLOG_SCRIPT)
backlog_index = importlib.util.module_from_spec(_SPEC)
sys.modules["backlog_index"] = backlog_index  # dataclass() needs this pre-registered
_SPEC.loader.exec_module(backlog_index)

# Sibling import for the drift-pin test below (round-3 code-quality-review
# fix): check_onramp_choice.py is this module's grammar-regex SSOT for
# `## On-ramp standing choices` entries; importing it here (not duplicating
# its pattern in a test literal) lets the pin catch future drift directly.
CHECK_ONRAMP_SCRIPT = Path(__file__).resolve().parent / "check_onramp_choice.py"
_ONRAMP_SPEC = importlib.util.spec_from_file_location(
    "check_onramp_choice", CHECK_ONRAMP_SCRIPT
)
check_onramp_choice = importlib.util.module_from_spec(_ONRAMP_SPEC)
sys.modules["check_onramp_choice"] = check_onramp_choice
_ONRAMP_SPEC.loader.exec_module(check_onramp_choice)

def _charter_status_word_section(text: str | None = None, *, path: Path = CHARTER_PATH) -> str:
    """The charter's §Status word definitions body, nothing else.

    Scoped deliberately (mirrors the retired §Closed status vocabulary
    scoping): the status words also appear throughout the charter's
    ordinary prose, so a whole-file substring search cannot tell "the
    table documents this value" from "the English word happens to
    occur". Section-scoped is what makes the assertion fail when a
    table row is actually removed.

    Accepts optional `text` so the mutation-kill check below can probe a
    scratch copy of the charter (or the template) without touching the
    real file. `path` only names the file for the error message.
    """
    if text is None:
        text = path.read_text(encoding="utf-8")
    _, _, after = text.partition("## Status word definitions")
    assert after, f"{path} has no '## Status word definitions' section"
    body, _, _ = after.partition("\n## ")
    return body


# Table row shape: "| `<word>` | ..." with nothing else inside the
# backticks — this is what excludes the `| `blocked:` (field, not a
# status) | ...` row, which is documented in the same table but is not
# a `status:` value.
_STATUS_TABLE_ROW = re.compile(r"^\| `([\w-]+)` \|", re.MULTILINE)


def _charter_table_status_words(section: str) -> set[str]:
    return set(_STATUS_TABLE_ROW.findall(section))


@pytest.mark.parametrize("path", [CHARTER_PATH, TEMPLATE_PATH])
def test_charter_documents_the_closed_status_vocabulary(path):
    """The status-word table (in both the live charter AND its BI-11
    canonical template — a drift between the two would let `loom_init.py`
    scaffold a wrong charter into every newly adopting repo) must list
    EXACTLY the words the code enforces
    (`backlog_index.CLOSED_STATUS_VOCABULARY`) — not a subset check that
    would pass with a missing word, and not a heading pin that would pass
    with a retired word still present. Table row shape: "| `<word>` | ..."
    (see docs/loom/backlog/README.md, ## Status word definitions).
    """
    assert path.is_file(), f"charter missing at {path}"
    section = _charter_status_word_section(path=path)
    table_words = _charter_table_status_words(section)
    assert table_words == set(backlog_index.CLOSED_STATUS_VOCABULARY), (
        f"{path}'s status word table lists {sorted(table_words)}, but "
        f"the code enforces {sorted(backlog_index.CLOSED_STATUS_VOCABULARY)} "
        "— every code word must appear as a table row, and no extra "
        "(e.g. retired) word may remain"
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


def test_duplicate_frontmatter_keys_resolve_last_wins():
    """A frontmatter block carrying `status:` twice must be read as the
    LAST occurrence, not the first.

    Regression for docs/loom/backlog/2026-08-02-backlog-index-two-
    frontmatter-readers-disagree-on-duplicate-keys.md: this repo used to
    carry a second frontmatter reader, a private helper in
    archive_change_folder.py, that `re.search`'d for the first match
    (`closed`) while this function
    iterates and overwrites (last match: `open`) — the same bytes read two
    different statuses depending which reader touched them. That second
    reader is gone (loom-code/scripts/archive_change_folder.py no longer
    has any caller needing it), so this property now lives here, pinned
    directly against `parse_frontmatter` itself — the only reader left."""
    frontmatter = backlog_index.parse_frontmatter(
        "---\nstatus: closed\nstatus: open\n---\n\n## Why\nBecause.\n"
    )

    assert frontmatter["status"] == "open"


def test_rejects_entry_whose_filename_does_not_match_frontmatter_name(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    # Filename stem is "2026-08-01-alpha" but frontmatter claims a different name.
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-beta", "open"))

    result = _run_validate(store)

    assert result.returncode == 1
    assert "2026-08-01-alpha.md" in result.stdout


def test_clean_store_passes(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "open"))
    _write(
        store,
        "archive/2026-07-01-closed-thing.md",
        # Archive-tier entries carry status: closed by construction.
        _archived_entry("2026-07-01-closed-thing"),
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
        _entry("2026-07-01-closed-thing", "open"),
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


# ---------------------------------------------------------------------------
# Task 1 (docs/loom/plans/2026-08-21-dissolve-direction-layer.md) — the
# status vocabulary collapses to exactly open/bet/closed; the seven legacy
# words (including COMMITTED-NEXT and archived) are retired.
# ---------------------------------------------------------------------------


def test_vocabulary_open_bet_closed(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "bet"))

    result = _run_validate(store)
    assert result.returncode == 0, result.stdout + result.stderr

    store2 = tmp_path / "backlog2"
    store2.mkdir()
    _write(store2, "2026-08-01-beta.md", _entry("2026-08-01-beta", "COMMITTED-NEXT"))

    result2 = _run_validate(store2)
    assert result2.returncode == 1
    assert "2026-08-01-beta.md" in result2.stdout


def test_blocked_field_on_open_entry_excludes_it_from_ready(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    text = _entry("2026-08-01-alpha", "open", description="Alpha marker.").replace(
        "status: open\n", "status: open\nblocked: waiting on X\n"
    )
    _write(store, "2026-08-01-alpha.md", text)

    result = _run_ready(store)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "2026-08-01-alpha" not in result.stdout


def test_blocked_field_on_a_closed_entry_is_a_violation(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    text = _entry("2026-08-01-alpha", "closed").replace(
        "status: closed\n", "status: closed\nblocked: waiting on X\n"
    )
    _write(store, "2026-08-01-alpha.md", text)

    result = _run_validate(store)

    assert result.returncode == 1
    assert "2026-08-01-alpha.md" in result.stdout


def test_archive_tier_entry_with_status_closed_validates_clean(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    _write(
        store,
        "archive/2026-07-01-closed-thing.md",
        _entry("2026-07-01-closed-thing", "closed"),
    )

    result = _run_validate(store)

    assert result.returncode == 0, result.stdout + result.stderr


def test_archive_tier_entry_with_status_archived_is_a_vocabulary_violation(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    _write(
        store,
        "archive/2026-07-01-closed-thing.md",
        _entry("2026-07-01-closed-thing", "archived"),
    )

    result = _run_validate(store)

    assert result.returncode == 1
    assert "2026-07-01-closed-thing.md" in result.stdout


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
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "open", description=""))

    result = _run_validate(store)

    assert result.returncode == 1
    assert "2026-08-01-alpha.md" in result.stdout


def test_readme_md_directly_under_store_is_never_treated_as_an_entry(tmp_path):
    """README.md carries no frontmatter at all; it must be excluded from
    scanning, not reported as a violation."""
    store = tmp_path / "backlog"
    store.mkdir()
    _write(store, "README.md", "# not an entry\n")
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "open"))

    result = _run_validate(store)

    assert result.returncode == 0, result.stdout + result.stderr


# ---------------------------------------------------------------------------
# Task 3 — scripts/backlog_index.py --write
#
# Task 1 of docs/loom/plans/2026-08-21-dissolve-direction-layer.md collapsed
# the archive-tier invariant to one rule (an entry under archive/ carries
# status: closed) and retired the separate `archived: <date>` field — the
# archive tier is a plain destination excluded from the generated index
# listing, so no rendered date is needed. `_archived_entry` below is a
# thin alias over `_entry(..., "closed")` kept for the many call sites
# below that predate the collapse.
# ---------------------------------------------------------------------------


def _archived_entry(
    name: str,
    description: str = "Should never appear in the generated index.",
) -> str:
    return _entry(name, "closed", description=description)


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


def test_write_groups_live_entries_by_status_and_excludes_archive_tier(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    _write(
        store,
        "2026-08-01-alpha.md",
        _entry("2026-08-01-alpha", "open", description="Alpha unique marker description."),
    )
    _write(
        store,
        "2026-08-02-beta.md",
        _entry("2026-08-02-beta", "open", description="Beta unique marker description."),
    )
    _write(
        store,
        "2026-08-03-gamma.md",
        _entry("2026-08-03-gamma", "closed", description="Gamma unique marker description."),
    )
    _write(
        store,
        "archive/2026-07-01-closed-thing.md",
        _archived_entry("2026-07-01-closed-thing"),
    )

    output = tmp_path / "BACKLOG.md"
    result = _run_write(store, output)
    assert result.returncode == 0, result.stdout + result.stderr

    text = output.read_text(encoding="utf-8")

    open_section = _section(text, "## open")
    assert "Alpha unique marker description." in open_section
    assert "Beta unique marker description." in open_section

    closed_section = _section(text, "## closed")
    assert "Gamma unique marker description." in closed_section

    # Archive-tier entries are excluded entirely (brief BI-10) — no
    # '## Archived' section, and the archived entry never appears.
    assert "## Archived" not in text
    assert "2026-07-01-closed-thing" not in text
    assert "Should never appear" not in text

    # Kickoff-decision hard contract: bet -> open -> closed.
    assert text.index("## open") < text.index("## closed")


def test_write_omits_empty_status_sections(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "open"))

    output = tmp_path / "BACKLOG.md"
    result = _run_write(store, output)
    assert result.returncode == 0, result.stdout + result.stderr

    text = output.read_text(encoding="utf-8")
    for heading in ("## bet", "## closed"):
        assert heading not in text, f"{heading} should be omitted when it has no entries"
    assert "## open" in text


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
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "open", description="Alpha."))
    _write(store, "2026-08-02-beta.md", _entry("2026-08-02-beta", "open", description="Beta."))
    _write(store, "2026-08-03-gamma.md", _entry("2026-08-03-gamma", "open", description="Gamma."))
    _write(store, "2026-08-04-delta.md", _entry("2026-08-04-delta", "open", description="Delta."))
    _write(store, "2026-08-05-epsilon.md", _entry("2026-08-05-epsilon", "open", description="Epsilon."))
    _write(store, "2026-08-06-zeta.md", _entry("2026-08-06-zeta", "bet"))
    _write(
        store,
        "archive/2026-07-01-closed-thing.md",
        _archived_entry("2026-07-01-closed-thing"),
    )
    _write(
        store,
        "archive/2026-06-01-older-thing.md",
        _archived_entry("2026-06-01-older-thing"),
    )
    _write(
        store,
        "archive/2026-05-01-oldest-thing.md",
        _archived_entry("2026-05-01-oldest-thing"),
    )

    result_a = _run_write(store, tmp_path / "BACKLOG_a.md")
    result_b = _run_write(store, tmp_path / "BACKLOG_b.md")

    assert result_a.returncode == 0, result_a.stdout + result_a.stderr
    assert result_b.returncode == 0, result_b.stdout + result_b.stderr
    assert (tmp_path / "BACKLOG_a.md").read_bytes() == (tmp_path / "BACKLOG_b.md").read_bytes()


def test_write_ignores_archive_tier_entry_with_bogus_status(tmp_path):
    """Archive-tier entries are excluded from `build_index()`'s render step
    entirely (they never validate their status there — that is
    `--validate`'s job), so a garbage status under archive/ does not fail
    `--write` — it is simply not rendered."""
    store = tmp_path / "backlog"
    store.mkdir()
    _write(
        store,
        "archive/2026-07-01-closed-thing.md",
        _entry("2026-07-01-closed-thing", "archived"),
    )
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "open"))

    output = tmp_path / "BACKLOG.md"
    result = _run_write(store, output)

    assert result.returncode == 0, result.stdout + result.stderr
    text = output.read_text(encoding="utf-8")
    assert "2026-07-01-closed-thing" not in text


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
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "open"))

    output = tmp_path / "BACKLOG.md"
    write_result = _run_write(store, output)
    assert write_result.returncode == 0, write_result.stdout + write_result.stderr

    check_result = _run_check(store, output)
    assert check_result.returncode == 0, check_result.stdout + check_result.stderr


def test_check_detects_a_hand_edited_index(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "open"))

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
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "open"))

    output = tmp_path / "BACKLOG.md"
    _run_write(store, output)
    with output.open("a", encoding="utf-8") as f:
        f.write("\n")  # one extra trailing blank line -- no visible content change

    result = _run_check(store, output)

    assert result.returncode == 1


def test_check_does_not_write_anything(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "open"))

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
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "open"))

    output = tmp_path / "BACKLOG.md"  # never written

    result = _run_check(store, output)

    assert result.returncode == 1
    assert not output.exists()


def test_check_fails_loudly_on_build_error_without_writing(tmp_path):
    store = tmp_path / "backlog"
    store.mkdir()
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "BOGUS-STATUS"))

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
    loom-memory (loom-code/skills/loom-memory/SKILL.md) routes a new
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
        "open",
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
        "open",
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
        "open",
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
        "open",
        "start: a DIFFERENT re-trigger condition entirely.\n",
        "- Start (re-trigger): a third real thing happens (Rule of Three).",
    )
    _write(store, "2026-08-01-alpha.md", text)

    result = _run_validate(store)

    assert result.returncode == 1
    assert "2026-08-01-alpha.md" in result.stdout


# ---------------------------------------------------------------------------
# Task 8 -- loom-code's loom-memory skill must route a backlog-shaped item
# to the store (docs/loom/backlog/), not to the now-generated
# docs/loom/BACKLOG.md. Scoped to the "## record" section's classification
# step, not a whole-file substring search, so a stray historical mention
# elsewhere in the file cannot mask a live write-instruction, and so this
# test would still fail if someone reverted the wording back to naming the
# generated file as a write target.
# ---------------------------------------------------------------------------


LOOM_MEMORY_SKILL_PATH = (
    REPO_ROOT / "loom-code" / "skills" / "loom-memory" / "SKILL.md"
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
        "open",
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
        "open",
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
# `bet` first (filename order), then `open`; excluded statuses (`closed`,
# archived, or an `open` entry carrying `blocked:`) never listed; closing
# `ready: N bet / M open / P closed / Q blocked` line.
# ---------------------------------------------------------------------------


def _ready_store(tmp_path: Path) -> Path:
    """One entry per shape — an OPEN entry with and without `start:` (so
    assertion (c) can check both the rendered and the absent case), a
    `bet` entry, a `blocked` open entry, a `closed` entry, and one
    archive-tier entry. Shared by all five --ready assertions."""
    store = tmp_path / "backlog"
    store.mkdir()
    _write(
        store,
        "2026-08-01-bet.md",
        _entry("2026-08-01-bet", "bet", description="Bet marker."),
    )
    _write(
        store,
        "2026-08-02-open-with-start.md",
        _entry(
            "2026-08-02-open-with-start", "open", description="Open-with-start marker."
        ).replace("status: open\n", "status: open\nstart: a third real thing happens\n"),
    )
    _write(
        store,
        "2026-08-03-open-plain.md",
        _entry("2026-08-03-open-plain", "open", description="Open-plain marker."),
    )
    _write(
        store,
        "2026-08-04-blocked.md",
        _entry("2026-08-04-blocked", "open").replace(
            "status: open\n", "status: open\nblocked: waiting on X\n"
        ),
    )
    _write(store, "2026-08-05-closed.md", _entry("2026-08-05-closed", "closed"))
    _write(
        store,
        "archive/2026-07-01-archived.md",
        _archived_entry("2026-07-01-archived"),
    )
    return store


def _run_ready(store: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(BACKLOG_SCRIPT), "--ready", "--store", str(store)],
        capture_output=True,
        text=True,
    )


def test_ready_prints_bet_section_before_open(tmp_path):
    """(a) `bet` is the 'now' queue — it must render before `open`, and
    each section must actually contain its own entries (section-scoped,
    not whole-output substring)."""
    result = _run_ready(_ready_store(tmp_path))

    assert result.returncode == 0, result.stdout + result.stderr
    out = result.stdout
    assert "## bet" in out and "## open" in out, out
    assert out.index("## bet") < out.index("## open")
    bet_section = _section(out, "## bet")
    assert "- 2026-08-01-bet — Bet marker." in bet_section
    open_section = _section(out, "## open")
    assert "- 2026-08-02-open-with-start — Open-with-start marker." in open_section
    assert "- 2026-08-03-open-plain — Open-plain marker." in open_section


def test_ready_excludes_closed_and_blocked_entries(tmp_path):
    """(b) a `closed` entry, an archive-tier entry, and an `open` entry
    carrying `blocked:` are not actionable — none of their entries may
    appear anywhere in the output (they are only tallied in the count
    line)."""
    result = _run_ready(_ready_store(tmp_path))

    assert result.returncode == 0, result.stdout + result.stderr
    for excluded_name in (
        "2026-08-04-blocked",
        "2026-08-05-closed",
        "2026-07-01-archived",
    ):
        assert excluded_name not in result.stdout, (
            f"excluded entry {excluded_name} leaked into --ready output"
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
    """(d) the output ends with the exact tally: 1 bet, 2 open,
    2 closed (1 closed entry + 1 archive-tier entry), 1 blocked."""
    result = _run_ready(_ready_store(tmp_path))

    assert result.returncode == 0, result.stdout + result.stderr
    non_empty = [line for line in result.stdout.splitlines() if line.strip()]
    assert non_empty[-1] == "ready: 1 bet / 2 open / 2 closed / 1 blocked"


def test_ready_is_a_mode_on_its_own_and_flagless_defaults_to_validate(tmp_path):
    """(e) `--ready` is accepted with no other mode flag; and a flagless
    invocation now runs the validate mode (mirroring
    check_loom_memory_integrity.py's trio shape, direction-layer arc)
    instead of the former "no mode specified" parser error."""
    store = _ready_store(tmp_path)

    result = _run_ready(store)
    assert result.returncode == 0, result.stdout + result.stderr

    flagless = subprocess.run(
        [sys.executable, str(BACKLOG_SCRIPT), "--store", str(store)],
        capture_output=True,
        text=True,
    )
    assert flagless.returncode == 0, flagless.stdout + flagless.stderr
    assert "backlog_index --validate: OK" in flagless.stdout, flagless.stdout


def test_the_deferred_rules_follow_up_is_tracked_in_the_store():
    """A future agent must find and understand this follow-up by grepping
    the store alone -- no plan reference required. Discriminating: fails if
    the entry is deleted (no match), if it is given a non-live status (it
    would render under no live section), or if it drops out of the
    regenerated index (present as a file but not surfaced)."""
    real_store = REPO_ROOT / "docs" / "loom" / "backlog"
    entry_files = [p for p in real_store.glob("*.md") if p.name != "README.md"]

    # Substring-match on "institution-maintenance.md" alone is not
    # discriminating: 2026-07-25-loom-workflow-loom-workflow-rename-evaluated-
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
        _entry("2026-08-01-open-plain", "open", description="Legit open marker."),
    )
    _write(
        store,
        "archive/2026-07-01-mis-tiered.md",
        _entry(
            "2026-07-01-mis-tiered",
            "open",
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
    open_section = _section(out, "## open")
    assert "- 2026-08-01-open-plain — Legit open marker." in open_section
    assert "2026-07-01-mis-tiered" not in open_section
    non_empty = [line for line in out.splitlines() if line.strip()]
    assert non_empty[-1] == "ready: 0 bet / 1 open / 1 closed / 0 blocked", non_empty[-1]


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
    assert result.stdout == "ready: 0 bet / 0 open / 0 closed / 0 blocked\n"


def test_ready_omits_bet_heading_when_empty(tmp_path):
    """(b) A store with no `bet` entries at all must omit the '## bet'
    heading entirely (not print an empty section), while the count line
    still reports the correct numbers -- this is the real store's
    current shape."""
    store = tmp_path / "backlog"
    store.mkdir()
    _write(
        store,
        "2026-08-01-open-plain.md",
        _entry("2026-08-01-open-plain", "open", description="Open-plain marker."),
    )
    _write(
        store,
        "2026-08-02-blocked.md",
        _entry("2026-08-02-blocked", "open").replace(
            "status: open\n", "status: open\nblocked: waiting on X\n"
        ),
    )

    result = _run_ready(store)

    assert result.returncode == 0, result.stdout + result.stderr
    out = result.stdout
    assert "## bet" not in out, out
    assert "## open" in out
    non_empty = [line for line in out.splitlines() if line.strip()]
    assert non_empty[-1] == "ready: 0 bet / 1 open / 0 closed / 1 blocked"


def test_direction_verbs_removed(tmp_path):
    """Task 7 (docs/loom/plans/2026-08-21-dissolve-direction-layer.md)
    deleted the direction half wholesale: the CLI must reject
    --direction-write as an unknown argument rather than accept it."""
    result = subprocess.run(
        [sys.executable, str(BACKLOG_SCRIPT), "--direction-write", str(tmp_path / "DIRECTION.md")],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, result.stdout + result.stderr
    assert "unrecognized arguments" in result.stderr, result.stderr
    assert "--direction-write" in result.stderr, result.stderr


def test_index_and_ready_agree_on_an_archive_tier_entry_with_a_bad_status(tmp_path):
    """Round-4 finding: the shared-walk extraction closed three of FOUR
    copies, and the fourth (`_collect_index_entries`) skipped archive-tier
    entries WITHOUT validating them while the other three validated every
    entry — so one store made `build_index()` return normally and
    `build_ready()` raise.

    The agreed direction is the one two shipped artifacts already record:
    `test_write_ignores_archive_tier_entry_with_bogus_status` ("that is
    `--validate`'s job") and `build_ready`'s own docstring ("an archive-tier
    entry is always tallied as `closed` ... independent of what its
    frontmatter literally says"). The archive tier OVERRIDES the status, so
    no reader routes on it; `--validate` owns it via `_check_archive_tier`.
    Validating it in the readers would leave a repo holding historical
    retired vocabulary unable to render its own index.

    Pinned at FUNCTION level deliberately: at CLI level `--check` exits 1
    via `find_violations` either way, which hides the divergence."""
    store = tmp_path / "backlog"
    (store / "archive").mkdir(parents=True)
    _write(store, "2026-08-01-live.md", _entry("2026-08-01-live", "open"))
    _write(
        store,
        "archive/2026-07-01-stale.md",
        _entry("2026-07-01-stale", "SHIPPED"),
    )

    # Both readers accept the store, and both treat the archived entry as
    # closed rather than as its literal status.
    ready = backlog_index.build_ready(store)
    index = backlog_index.build_index(store)
    assert "2026-07-01-stale" not in index
    assert "SHIPPED" not in ready and "SHIPPED" not in index
    assert "/ 1 closed /" in ready, ready

    # A LIVE entry with the same status still fails loudly in both.
    _write(store, "2026-08-02-bad.md", _entry("2026-08-02-bad", "SHIPPED"))
    with pytest.raises(ValueError, match="SHIPPED"):
        backlog_index.build_ready(store)
    with pytest.raises(ValueError, match="SHIPPED"):
        backlog_index.build_index(store)

    # And `--validate` — the owner of the archive-tier rule — still flags
    # the archived entry, so nothing is laundered by the readers' silence.
    flagged = [
        v for v in backlog_index.find_violations(store)
        if v.kind == "archive-tier" and "2026-07-01-stale" in v.file
    ]
    assert flagged, backlog_index.find_violations(store)


def test_output_defaults_beside_its_store_not_beside_the_cwd(tmp_path):
    """Dogfood finding (2026-08-21, end-to-end shakedown): `--write` with an
    explicit `--store` and a defaulted `--output` resolved the output against
    the CWD, so running it from one repo against another repo's store wrote
    the wrong index over the standing repo's `BACKLOG.md` — silently, and with
    a success line printing a relative path that hid where it landed. It
    happened for real: a dogfood agent destroyed monkey-skills' own
    docs/loom/BACKLOG.md this way (recovered from HEAD).

    The index belongs beside its own store. For the canonical layout
    (`--store docs/loom/backlog` from the repo root) the derived default is
    byte-identical to the old one — only the cross-repo case, which was
    always wrong, changes.

    Six whole-branch review rounds did not find this; ten minutes of running
    the thing did. Recorded in DL-30.
    """
    store = tmp_path / "theirs" / "docs" / "loom" / "backlog"
    store.mkdir(parents=True)
    _write(store, "2026-08-01-alpha.md", _entry("2026-08-01-alpha", "open"))

    standing = tmp_path / "mine" / "docs" / "loom"
    standing.mkdir(parents=True)
    victim = standing / "BACKLOG.md"
    victim.write_text("PRECIOUS — this repo's own index\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(BACKLOG_SCRIPT), "--write", "--store", str(store)],
        capture_output=True,
        text=True,
        cwd=tmp_path / "mine",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert victim.read_text(encoding="utf-8") == "PRECIOUS — this repo's own index\n", (
        "writing another store's index clobbered the standing repo's "
        "BACKLOG.md:\n" + victim.read_text(encoding="utf-8")
    )
    written = store.parent / "BACKLOG.md"
    assert written.is_file(), (
        f"the index was not written beside its own store at {written}:\n"
        + result.stdout
    )
    assert "2026-08-01-alpha" in written.read_text(encoding="utf-8")
    # The success line must name where it landed, absolutely — a relative
    # path is exactly what hid the cross-repo write.
    assert str(written) in result.stdout, result.stdout


def test_a_store_path_that_does_not_exist_is_a_failure_not_a_clean_empty_store(tmp_path):
    """Dogfood finding #1 (2026-08-21, end-to-end shakedown) — the worst
    defect this arc shipped, and six whole-branch review rounds read past it.

    `--store` is the ONLY way to locate the store (there is no `--repo-root`
    here), and a typo in it produced `OK — every invariant holds` at exit 0:
    `_entry_files` globs a directory that is not there, gets an empty list,
    and every invariant holds vacuously. `--ready` reported an empty queue and
    `--write` generated an empty index over whatever `--output` pointed at.
    A green validate bought with a typo is worse than a red one.

    Absence of a store is a legitimate state for a repo that never adopted the
    queue layer — but that is the CALLER's judgment (see
    `check_queue_relation.py`, which reports a loud N/A and exits 0 for
    exactly that case). This script is pointed at a store explicitly; being
    unable to find it is a failure.
    """
    missing = tmp_path / "docs" / "loom" / "backlogg"

    for mode in ("--validate", "--ready", "--write", "--check"):
        result = subprocess.run(
            [sys.executable, str(BACKLOG_SCRIPT), mode, "--store", str(missing)],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        combined = result.stdout + result.stderr
        assert result.returncode != 0, (
            f"{mode} reported success against a store that does not exist "
            f"at {missing}:\n{combined}"
        )
        assert "every invariant holds" not in combined, combined
        assert str(missing) in combined, combined

    # A path that exists but is not a directory is the same failure.
    not_a_dir = tmp_path / "PURPOSE.md"
    not_a_dir.write_text("not a store\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(BACKLOG_SCRIPT), "--validate", "--store", str(not_a_dir)],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    assert result.returncode != 0, result.stdout + result.stderr
