"""Behavioral tests for `check_queue_relation.py` (plan docs/loom/
plans/2026-08-21-dissolve-direction-layer.md Task 4). `in-queue:`/
`displaces:` names resolve against live `status: bet` backlog entries;
the old per-repo "now" list and its unlanded-change advisory are gone,
and a repo with no `docs/loom/backlog/` store reports a loud N/A at
exit 0 rather than gating.

Also carries the three stable `## Queue relation` prose pins against
`handoff-brief-format.md` (the Grammar SSOT this script's own docstring
cites) — the fourth pin ("cited name must exist in the queue") is
deliberately NOT restored here; its wording changes when Task 8
rewrites that prose (plan DL-12).

Stdlib only.
"""

from __future__ import annotations

import re
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
_REFERENCE = (
    Path(__file__).parent
    / ".."
    / "skills"
    / "brainstorming"
    / "references"
    / "handoff-brief-format.md"
).resolve()

_CANONICAL_FORMS = ["in-queue:", "unqueued —", "displaces:"]


def _reference_text() -> str:
    assert _REFERENCE.is_file(), f"handoff-brief-format.md is absent at {_REFERENCE}"
    return _REFERENCE.read_text(encoding="utf-8")


def _section(text: str, heading_pattern: str) -> str:
    match = re.search(rf"^##\s+{heading_pattern}\s*$", text, re.MULTILINE)
    assert match is not None, f"heading matching {heading_pattern!r} not found"
    rest = text[match.end():]
    next_heading = re.search(r"^##\s+\S", rest, re.MULTILINE)
    return rest[: next_heading.start()] if next_heading else rest


def _queue_relation_subsection(text: str) -> str:
    required_sections = _section(text, r"Required sections")
    heading_match = re.search(
        r"^###\s+`## Queue relation`\s*$", required_sections, re.MULTILINE
    )
    assert heading_match is not None, (
        "Required sections must declare a '### `## Queue relation`' subsection"
    )
    rest = required_sections[heading_match.end():]
    next_subsection = re.search(r"^###\s+\S", rest, re.MULTILINE)
    return rest[: next_subsection.start()] if next_subsection else rest


def _overview_paragraph(text: str) -> str:
    required_sections = _section(text, r"Required sections")
    first_subsection = re.search(r"^###\s+\S", required_sections, re.MULTILINE)
    return (
        required_sections[: first_subsection.start()]
        if first_subsection
        else required_sections
    )


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


def test_unreadable_entry_file_prints_one_actionable_line_not_a_traceback(
    tmp_path: Path,
) -> None:
    """Round-2 finding: `live_bet_names` reads entry files the same way
    `find_bet_entries` in check_north_star_link.py does, so an unreadable
    entry must be reported the same way — one actionable line on stderr,
    never a raw traceback. Mirrors check_north_star_link.py's OSError
    handling (its module docstring names this exact same-bytes guard)."""
    repo = tmp_path
    store = repo / "docs" / "loom" / "backlog"
    _write_bet_entry(store, "unreadable-entry")
    entry = store / "unreadable-entry.md"
    entry.chmod(0o000)

    brief = repo / "brief.md"
    brief.write_text("## Queue relation\n\nunqueued — nothing to queue\n", encoding="utf-8")

    try:
        result = subprocess.run(
            [sys.executable, str(_SCRIPT), str(brief), "--repo-root", str(repo)],
            capture_output=True,
            text=True,
        )
    finally:
        entry.chmod(0o644)

    assert result.returncode == 1, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "Traceback" not in result.stderr
    assert "unreadable" in result.stderr
    assert str(store) in result.stderr


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


# --- Finding 1: `displaces:` coverage + separator guards -----------------


def test_displaces_resolves_against_live_bet_entry() -> None:
    brief_text = "## Queue relation\n\ndisplaces: alpha-arc — supersedes it\n"
    result = resolve_queue_relation(brief_text, ["alpha-arc"])
    assert result.status == "resolved"


def test_displaces_unresolved_against_name_not_a_bet() -> None:
    brief_text = "## Queue relation\n\ndisplaces: ghost-arc — supersedes it\n"
    result = resolve_queue_relation(brief_text, ["alpha-arc"])
    assert result.status == "unresolved"
    assert result.named_entry == "ghost-arc"


def test_displaces_ascii_hyphen_separator_does_not_resolve() -> None:
    """`displaces:` requires an em dash (—) before the reason. An ASCII
    hyphen (-) must NOT resolve — this is what the deleted
    `_no_skip.py` probe existed to stop from passing vacuously."""
    brief_text = "## Queue relation\n\ndisplaces: alpha-arc - supersedes it\n"
    result = resolve_queue_relation(brief_text, ["alpha-arc"])
    assert result.status == "unresolved"


def test_unqueued_ascii_hyphen_separator_does_not_resolve() -> None:
    brief_text = "## Queue relation\n\nunqueued - nothing live yet\n"
    result = resolve_queue_relation(brief_text, ["alpha-arc"])
    assert result.status == "unresolved"


def test_no_queue_relation_section_at_all_is_unresolved() -> None:
    result = resolve_queue_relation("Some brief with no such section.\n", ["alpha-arc"])
    assert result.status == "unresolved"


# --- Finding 2: stable prose pins against handoff-brief-format.md --------
# Restores 3 of the 4 tests deleted in round 1, plus the 4th ("cited name
# must exist") below — its wording changes from '## Now' to a live
# `status: bet` entry under Task 8 (plan DL-12), which is why it lands
# here rather than in Task 4.


def test_handoff_format_states_three_canonical_queue_forms() -> None:
    text = _reference_text()
    body = _queue_relation_subsection(text)
    for form in _CANONICAL_FORMS:
        assert form in body, (
            f"'## Queue relation' section missing canonical form {form!r}"
        )


def test_required_sections_overview_names_queue_relation_as_required() -> None:
    text = _reference_text()
    overview = _overview_paragraph(text)

    assert "## Queue relation" in overview, (
        "'## Required sections' overview paragraph must name "
        "'## Queue relation' by name"
    )
    mention_index = overview.index("## Queue relation")
    clause = overview[max(0, mention_index - 20) : mention_index + 80]
    assert "always present" in clause, (
        "'## Queue relation' mention in the overview paragraph must state "
        "it is always present (required)"
    )
    assert "optional" not in clause, (
        "'## Queue relation' mention in the overview paragraph must not be "
        "phrased as optional"
    )


def test_queue_relation_states_empty_now_guidance() -> None:
    """Empty-queue resting-state guidance — reworded under Task 8 from
    '## Now is empty' to 'no live bet entries' (the direction-layer file
    this prose used to point at no longer exists)."""
    text = _reference_text()
    body = _queue_relation_subsection(text)

    assert re.search(r"no live bet entries", body), (
        "'## Queue relation' section must state what an author does "
        "when there are no live bet entries"
    )
    assert "## Now" not in body, (
        "'## Queue relation' section must no longer reference the "
        "deleted direction-layer file's '## Now' section"
    )
    assert "unqueued" in body, (
        "the empty-queue guidance must point the author at "
        "'unqueued — <reason>' as the usable form"
    )


def test_queue_relation_names_cited_must_exist_as_live_bet_entry() -> None:
    """The fourth prose pin (DL-12): a name cited by `in-queue:` or
    `displaces:` must resolve against a live `status: bet` entry under
    `docs/loom/backlog/` — the deleted direction-layer file's `## Now`
    section this rule used to point at is gone."""
    text = _reference_text()
    body = _queue_relation_subsection(text)

    assert re.search(
        r"must also exist as a live `status: bet` entry under "
        r"`docs/loom/backlog/`",
        body,
    ), (
        "'## Queue relation' section must state the must-exist rule "
        "against a live 'status: bet' entry under docs/loom/backlog/"
    )


# --- Finding 3: an out-of-vocabulary status must not vanish silently -----


def test_live_bet_names_raises_on_out_of_vocabulary_status(tmp_path: Path) -> None:
    store = tmp_path / "backlog"
    store.mkdir(parents=True)
    (store / "mystery.md").write_text(
        "---\nname: mystery\nstatus: COMMITTED-NEXT\n---\n\nBody.\n",
        encoding="utf-8",
    )
    try:
        live_bet_names(store)
    except ValueError as exc:
        assert "mystery" in str(exc)
    else:
        raise AssertionError(
            "live_bet_names silently dropped an entry with an "
            "out-of-vocabulary status instead of failing loudly"
        )


def test_cli_names_the_bad_file_on_out_of_vocabulary_status(tmp_path: Path) -> None:
    repo = tmp_path
    store = repo / "docs" / "loom" / "backlog"
    store.mkdir(parents=True)
    (store / "mystery.md").write_text(
        "---\nname: mystery\nstatus: COMMITTED-NEXT\n---\n\nBody.\n",
        encoding="utf-8",
    )

    brief = repo / "brief.md"
    brief.write_text("## Queue relation\n\nin-queue: mystery\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(_SCRIPT), str(brief), "--repo-root", str(repo)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "mystery" in result.stderr
    assert "no live bet entries exist yet" not in result.stderr


# --- Round-3 finding: round 2 guarded ONE of this function's three reads ---


def test_unreadable_store_parent_exits_1_not_a_traceback_and_never_claims_na(
    tmp_path: Path,
) -> None:
    """Round-3 finding (arm B): round 2 added the OSError guard at the
    `live_bet_names()` call site but not at the `store.is_dir()` probe
    above it. The failure mode is worse than a traceback: without a
    guard the raise is the ONLY thing keeping an unreadable store out of
    the `N/A — no queue layer in this repo` branch, which exits 0. So
    this pins both halves — exit 1, and the N/A line absent.
    check_north_star_link.py already guards its own `is_dir()` probe
    this way; this is the untouched half of that twinned pair."""
    repo = tmp_path
    store = repo / "docs" / "loom" / "backlog"
    _write_bet_entry(store, "some-entry")

    brief = repo / "brief.md"
    brief.write_text("## Queue relation\n\nunqueued — nothing to queue\n", encoding="utf-8")

    parent = repo / "docs" / "loom"
    parent.chmod(0o000)
    try:
        result = subprocess.run(
            [sys.executable, str(_SCRIPT), str(brief), "--repo-root", str(repo)],
            capture_output=True,
            text=True,
        )
    finally:
        parent.chmod(0o755)

    assert result.returncode == 1, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "Traceback" not in result.stderr
    assert "unreadable" in result.stderr
    assert "N/A" not in result.stdout, (
        "an unreadable store was reported as 'no queue layer in this repo' — "
        "absence and unreadability are different facts"
    )


def test_unreadable_brief_file_exits_1_not_a_traceback(tmp_path: Path) -> None:
    """Round-3 finding (arm A): the brief read sits three lines ABOVE the
    guard round 2 added, and is itself unguarded. `is_file()` covers the
    common missing-brief case, so only an existing-but-unreadable brief
    escapes — but it escapes as a raw traceback."""
    repo = tmp_path
    store = repo / "docs" / "loom" / "backlog"
    _write_bet_entry(store, "some-entry")

    brief = repo / "brief.md"
    brief.write_text("## Queue relation\n\nunqueued — nothing to queue\n", encoding="utf-8")
    brief.chmod(0o000)

    try:
        result = subprocess.run(
            [sys.executable, str(_SCRIPT), str(brief), "--repo-root", str(repo)],
            capture_output=True,
            text=True,
        )
    finally:
        brief.chmod(0o644)

    assert result.returncode == 1, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "Traceback" not in result.stderr
    assert "unreadable" in result.stderr


# --- Dogfood finding #2: the ASCII near-miss deserves its own sentence ---


def test_ascii_double_hyphen_near_miss_names_the_character(tmp_path: Path) -> None:
    """A newcomer wrote `unqueued -- this is exploratory spike work` and got
    the same generic grammar message as someone using the wrong form
    entirely. They re-read it several times before suspecting the dash
    character itself. The form was right; only the character was wrong, and
    the message must say so."""
    repo = tmp_path
    (repo / "docs" / "loom" / "backlog").mkdir(parents=True)
    brief = repo / "brief.md"
    brief.write_text(
        "## Queue relation\n\nunqueued -- this is exploratory spike work\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(_SCRIPT), str(brief), "--repo-root", str(repo)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2, result.stdout + result.stderr
    assert "ASCII '--'" in result.stderr, result.stderr
    assert "em dash" in result.stderr, result.stderr


def test_a_genuinely_wrong_form_does_not_get_the_dash_hint(tmp_path: Path) -> None:
    """The hint must not fire on every unresolved line — it is earned by
    re-matching a dash-swapped copy against the grammar, so it says 'this
    line would have resolved' rather than 'I saw two hyphens'."""
    repo = tmp_path
    (repo / "docs" / "loom" / "backlog").mkdir(parents=True)
    brief = repo / "brief.md"
    brief.write_text("## Queue relation\n\npending -- decide later\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(_SCRIPT), str(brief), "--repo-root", str(repo)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2, result.stdout + result.stderr
    assert "ASCII" not in result.stderr, result.stderr
