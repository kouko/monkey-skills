"""Tests for loom_memory.py — the plugin-owned OKF v0.2-compatible Loom
memory profile validator and deterministic `index.md` generator.

WHY this module exists: `scripts/check_loom_memory_integrity.py` hard-codes
`docs/loom/memory`'s legacy README-indexed shape and cannot be installed
standalone (REQ-26 retires it once this module lands). Eight of its test
cases encode format-agnostic invariants this profile still owes — those are
ported here (marked `[ported]`), not copied verbatim, because the concrete
shape (a hand-authored `## Index` section vs a generated `index.md`) no
longer exists.

Fixtures build REAL temporary stores (`tmp_path`) so the module's actual
parsing/generation is exercised, never mocked.
"""

from __future__ import annotations

import subprocess
import sys

import pytest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
SCRIPT = SCRIPTS_DIR / "loom_memory.py"
sys.path.insert(0, str(SCRIPTS_DIR))

import loom_memory as lm  # noqa: E402


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _write(store: Path, rel: str, text: str) -> None:
    path = store / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _concept(name: str, description: str, type_: str = "practice", source: str | None = None) -> str:
    resource = source or f"test fixture for {name}"
    return (
        "---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        f"type: {type_}\n"
        "sources:\n"
        f'  - resource: "{resource}"\n'
        "---\n\n"
        "The lesson body.\n"
    )


def _index_frontmatter() -> str:
    return '---\nokf_version: "0.2"\n---\n\n'


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def _make_valid_store(store: Path) -> None:
    """README guide + two lesson concepts + a correctly generated index.md."""
    store.mkdir()
    _write(
        store,
        "README.md",
        "---\nname: README\ndescription: Charter for this fixture store.\n"
        "type: Memory Store Guide\nsources:\n  - resource: \"commit deadbeef\"\n---\n\n# Guide\n",
    )
    _write(store, "a-gotcha.md", _concept("a-gotcha", "A gotcha description.", type_="gotcha"))
    _write(store, "a-practice.md", _concept("a-practice", "A practice description.", type_="practice"))
    lm.regenerate_index(store)


# ---------------------------------------------------------------------------
# Acceptance: A1 positive `valid-profile` / negative `malformed-reserved-file`
# ---------------------------------------------------------------------------


def test_valid_profile_passes(tmp_path):
    store = tmp_path / "memory"
    _make_valid_store(store)

    assert lm.validate_bundle(store) == []

    result = _run_cli("validate", str(store))
    assert result.returncode == 0, result.stdout + result.stderr


def test_malformed_reserved_file_index_with_extra_key_is_a_violation(tmp_path):
    store = tmp_path / "memory"
    _make_valid_store(store)
    # Corrupt the reserved index.md: clause 6 permits ONLY okf_version.
    _write(
        store,
        "index.md",
        '---\nokf_version: "0.2"\nextra_key: not allowed\n---\n\n# Memory Store Index\n',
    )

    violations = lm.validate_bundle(store)

    assert any(v.invariant == "reserved-index" for v in violations)
    result = _run_cli("validate", str(store))
    assert result.returncode != 0
    assert "reserved-index" in result.stdout


def test_malformed_reserved_file_index_with_wrong_version_is_a_violation(tmp_path):
    store = tmp_path / "memory"
    _make_valid_store(store)
    _write(store, "index.md", '---\nokf_version: "0.1"\n---\n\n# Memory Store Index\n')

    violations = lm.validate_bundle(store)

    assert any(v.invariant == "reserved-index" for v in violations)


# ---------------------------------------------------------------------------
# Acceptance: A2 positive `bounded-index` / negative `drifted-index`
# ---------------------------------------------------------------------------


def test_bounded_index_lets_an_agent_pick_without_opening_bodies(tmp_path):
    """Generated index carries name + file + description per concept, grouped
    by type with the guide under `Guides` — enough to choose without opening
    any body file."""
    store = tmp_path / "memory"
    _make_valid_store(store)

    text = (store / "index.md").read_text(encoding="utf-8")

    assert text.startswith('---\nokf_version: "0.2"\n---\n')
    assert "## Guides" in text
    assert "[README](README.md) — Charter for this fixture store." in text
    assert "## gotcha" in text
    assert "[a-gotcha](a-gotcha.md) — A gotcha description." in text
    assert "## practice" in text
    assert "[a-practice](a-practice.md) — A practice description." in text


def test_drifted_index_is_a_validation_failure_naming_the_mismatch(tmp_path):
    store = tmp_path / "memory"
    _make_valid_store(store)
    # Hand-edit the committed index so it no longer matches a fresh regen.
    stale = (store / "index.md").read_text(encoding="utf-8").replace(
        "A gotcha description.", "A STALE gotcha description."
    )
    _write(store, "index.md", stale)

    violations = lm.validate_bundle(store)

    drift = [v for v in violations if v.invariant == "index-drift"]
    assert len(drift) == 1
    assert "a-gotcha" in drift[0].detail or "index.md" in drift[0].file


def test_regeneration_is_idempotent_byte_identical_on_second_run(tmp_path):
    store = tmp_path / "memory"
    _make_valid_store(store)
    first = (store / "index.md").read_text(encoding="utf-8")

    lm.regenerate_index(store)
    second = (store / "index.md").read_text(encoding="utf-8")

    assert first == second


def test_regeneration_touches_only_index_md(tmp_path):
    store = tmp_path / "memory"
    _make_valid_store(store)
    readme_before = (store / "README.md").read_text(encoding="utf-8")
    gotcha_before = (store / "a-gotcha.md").read_text(encoding="utf-8")

    lm.regenerate_index(store)

    assert (store / "README.md").read_text(encoding="utf-8") == readme_before
    assert (store / "a-gotcha.md").read_text(encoding="utf-8") == gotcha_before


# ---------------------------------------------------------------------------
# Acceptance: A6 positive `all-offenders` / boundary `unrelated-command-unblocked`
# ---------------------------------------------------------------------------


def test_all_offenders_are_reported_not_just_the_first(tmp_path):
    """Three offenders of three DIFFERENT invariants, none of which blocks
    strict index regeneration on its own (so the drift/broken-target checks
    still run against the concept files that ARE sound), must all show up
    together — not only the first one found."""
    store = tmp_path / "memory"
    _make_valid_store(store)
    # Offender 1: missing 'sources' (a Loom-profile violation regeneration
    # itself does not check, so it cannot mask the other two below).
    _write(
        store,
        "no-sources.md",
        "---\nname: no-sources\ndescription: A fact with no sources at all.\ntype: gotcha\n---\n\nBody.\n",
    )
    # Offender 2 (index-drift) and offender 3 (broken-target): hand-edit the
    # committed index.md so a description is stale AND it links to a file
    # that does not exist in the store.
    stale = (store / "index.md").read_text(encoding="utf-8").replace(
        "A practice description.", "A STALE practice description."
    )
    stale += "- [ghost](ghost.md) — A concept whose file was deleted.\n"
    _write(store, "index.md", stale)

    violations = lm.validate_bundle(store)
    files_named = {v.file for v in violations}

    assert "no-sources.md" in files_named
    assert any(v.invariant == "sources" for v in violations)
    assert any(v.invariant == "index-drift" for v in violations)
    assert any(v.invariant == "broken-target" and v.file == "ghost.md" for v in violations)
    assert len(violations) >= 3


def test_duplicate_concept_identity_is_a_violation(tmp_path):
    """Two concept files sharing the same `name` — necessarily co-occurring
    with a name/stem mismatch on at least one of them, since `name` must
    equal each file's own stem."""
    store = tmp_path / "memory"
    store.mkdir()
    _write(store, "a-gotcha.md", _concept("a-gotcha", "First copy.", type_="gotcha"))
    _write(store, "a-gotcha-dup.md", _concept("a-gotcha", "Second copy, wrong stem.", type_="gotcha"))

    violations = lm.validate_bundle(store)

    duplicate = [v for v in violations if v.invariant == "duplicate-identity"]
    assert {v.file for v in duplicate} == {"a-gotcha.md", "a-gotcha-dup.md"}


def test_unrelated_command_unblocked_by_a_broken_store(tmp_path):
    """A structural failure in one store must not affect another, nor crash
    the process (REQ-17: "shall not ... block unrelated ... work")."""
    broken = tmp_path / "broken"
    broken.mkdir()
    _write(broken, "bare.md", "No frontmatter at all.\n")

    clean = tmp_path / "clean"
    _make_valid_store(clean)

    broken_result = _run_cli("validate", str(broken))
    assert broken_result.returncode != 0
    assert "Traceback" not in broken_result.stderr

    clean_result = _run_cli("validate", str(clean))
    assert clean_result.returncode == 0, clean_result.stdout + clean_result.stderr


def test_unrelated_command_unblocked_regenerate_index_failure_is_clean_exit(tmp_path):
    store = tmp_path / "memory"
    _make_valid_store(store)
    _write(store, "broken.md", "No frontmatter at all.\n")

    result = _run_cli("regenerate-index", str(store))

    assert result.returncode != 0
    assert "Traceback" not in result.stderr


# ---------------------------------------------------------------------------
# [ported] format-agnostic invariants from
# scripts/test_check_loom_memory_integrity.py (see REQ-26)
# ---------------------------------------------------------------------------


def test_filename_frontmatter_name_mismatch_is_a_violation(tmp_path):
    """[ported] legacy :98 — name != filename stem is a violation whose
    message repr()s both sides (legacy :147/:156) so invisible-byte drift
    is visible, not just 'differs'."""
    store = tmp_path / "memory"
    store.mkdir()
    _write(store, "mismatched-fact.md", _concept("wrong-slug", "A description that never matches its filename."))

    violations = lm._validate_concept_file(store / "mismatched-fact.md")

    name_violations = [v for v in violations if v.invariant == "name"]
    assert len(name_violations) == 1
    assert "mismatched-fact.md" == name_violations[0].file
    assert repr("wrong-slug") in name_violations[0].detail
    assert repr("mismatched-fact") in name_violations[0].detail


def test_description_containing_colon_parses_and_compares_correctly(tmp_path):
    """[ported] legacy :165 — a description with a colon must not confuse
    the `key: value` parser (first-colon partition only)."""
    store = tmp_path / "memory"
    store.mkdir()
    desc = "GitHub Actions paths: filters changed behavior in this fact."
    _write(store, "colon-fact.md", _concept("colon-fact", desc, type_="gotcha"))

    frontmatter = lm.parse_frontmatter((store / "colon-fact.md").read_text(encoding="utf-8"))

    assert frontmatter["description"] == desc
    assert lm._validate_concept_file(store / "colon-fact.md") == []


def test_body_file_with_no_frontmatter_is_a_violation_not_a_crash(tmp_path):
    """[ported] legacy :194."""
    store = tmp_path / "memory"
    store.mkdir()
    _write(store, "bare-fact.md", "No frontmatter here, just prose.\n")

    violations = lm._validate_concept_file(store / "bare-fact.md")

    assert len(violations) == 1
    assert violations[0].invariant == "frontmatter"
    assert violations[0].file == "bare-fact.md"


def test_body_file_missing_name_key_is_a_violation(tmp_path):
    """[ported] legacy :225."""
    store = tmp_path / "memory"
    store.mkdir()
    _write(
        store,
        "nameless-fact.md",
        '---\ndescription: A fact whose frontmatter never declares a name.\ntype: gotcha\n'
        'sources:\n  - resource: "fixture"\n---\n\nBody.\n',
    )

    violations = lm._validate_concept_file(store / "nameless-fact.md")

    assert any(v.invariant == "name" for v in violations)


def test_body_file_missing_description_key_is_a_violation(tmp_path):
    """[ported] legacy :243."""
    store = tmp_path / "memory"
    store.mkdir()
    _write(
        store,
        "descriptionless-fact.md",
        '---\nname: descriptionless-fact\ntype: gotcha\nsources:\n  - resource: "fixture"\n---\n\nBody.\n',
    )

    violations = lm._validate_concept_file(store / "descriptionless-fact.md")

    assert any(v.invariant == "description" for v in violations)


def test_generate_index_aborts_on_broken_frontmatter_without_touching_file(tmp_path):
    """[ported] legacy :404 — regeneration must refuse (nonzero), name the
    offender, and leave index.md untouched."""
    store = tmp_path / "memory"
    _make_valid_store(store)
    original = (store / "index.md").read_text(encoding="utf-8")
    _write(store, "broken-fact.md", "No frontmatter at all here.\n")

    try:
        lm.regenerate_index(store)
        raised = False
    except lm.LoomMemoryError as exc:
        raised = True
        assert any(v.file == "broken-fact.md" for v in exc.violations)

    assert raised
    assert (store / "index.md").read_text(encoding="utf-8") == original


def test_generate_index_aborts_on_name_stem_mismatch_without_touching_file(tmp_path):
    """[ported] legacy :425."""
    store = tmp_path / "memory"
    _make_valid_store(store)
    original = (store / "index.md").read_text(encoding="utf-8")
    _write(store, "mismatched-fact.md", _concept("wrong-slug", "A description."))

    try:
        lm.regenerate_index(store)
        raised = False
    except lm.LoomMemoryError as exc:
        raised = True
        assert any(v.file == "mismatched-fact.md" and v.invariant == "name" for v in exc.violations)

    assert raised
    assert (store / "index.md").read_text(encoding="utf-8") == original


def test_generate_index_aborts_on_missing_description_without_touching_file(tmp_path):
    """[ported] legacy :443."""
    store = tmp_path / "memory"
    _make_valid_store(store)
    original = (store / "index.md").read_text(encoding="utf-8")
    _write(
        store,
        "bare-desc-fact.md",
        '---\nname: bare-desc-fact\ntype: gotcha\nsources:\n  - resource: "fixture"\n---\n\nBody.\n',
    )

    try:
        lm.regenerate_index(store)
        raised = False
    except lm.LoomMemoryError as exc:
        raised = True
        assert any(v.file == "bare-desc-fact.md" and v.invariant == "description" for v in exc.violations)

    assert raised
    assert (store / "index.md").read_text(encoding="utf-8") == original


# ---------------------------------------------------------------------------
# REQ-10 minimum schema / REQ-12 unknown metadata stays optional
# ---------------------------------------------------------------------------


def test_missing_sources_is_a_violation(tmp_path):
    store = tmp_path / "memory"
    store.mkdir()
    _write(
        store,
        "no-sources.md",
        "---\nname: no-sources\ndescription: A fact with no sources at all.\ntype: gotcha\n---\n\nBody.\n",
    )

    violations = lm._validate_concept_file(store / "no-sources.md")

    assert any(v.invariant == "sources" for v in violations)


def test_unknown_optional_metadata_is_never_a_profile_failure(tmp_path):
    store = tmp_path / "memory"
    store.mkdir()
    _write(
        store,
        "with-extra.md",
        "---\nname: with-extra\ndescription: A fact carrying an unrecognized key.\ntype: gotcha\n"
        'sources:\n  - resource: "fixture"\n'
        "type_note: legacy carryover, not part of the schema\n"
        "---\n\nBody.\n",
    )

    violations = lm._validate_concept_file(store / "with-extra.md")

    assert violations == []
    frontmatter = lm.parse_frontmatter((store / "with-extra.md").read_text(encoding="utf-8"))
    assert frontmatter["type_note"] == "legacy carryover, not part of the schema"


def test_unknown_metadata_round_trips_through_parse_and_dump():
    """REQ-12: unknown/unrecognized shape survives read AND round-trip write."""
    text = (
        "---\nname: foo\ndescription: A description.\ntype: gotcha\n"
        'sources:\n  - resource: "a commit"\n    kind: commit\n'
        "custom_nested:\n  inner: value\n---\n"
    )

    parsed = lm.parse_frontmatter(text)
    dumped = lm.dump_frontmatter(parsed)
    reparsed = lm.parse_frontmatter(dumped)

    assert reparsed == parsed
    assert reparsed["custom_nested"] == {"inner": "value"}
    assert reparsed["sources"][0]["kind"] == "commit"


# ---------------------------------------------------------------------------
# R1 — frontmatter scalars are byte-preserving (no quote-stripping at parse)
# ---------------------------------------------------------------------------


def test_parse_frontmatter_does_not_strip_a_quoted_scalar():
    text = '---\nname: n\ndescription: "a quoted rule"\ntype: gotcha\nsources:\n  - resource: c\n---\n'
    parsed = lm.parse_frontmatter(text)
    assert parsed["description"] == '"a quoted rule"'


def test_generate_index_copies_a_quoted_description_byte_identically(tmp_path):
    store = tmp_path / "memory"
    store.mkdir()
    quoted = '"a quoted rule"'
    _write(store, "one-rule.md", _concept("one-rule", quoted, type_="gotcha"))
    assert lm.generate_index(store).splitlines()[-1].endswith(quoted)


# ---------------------------------------------------------------------------
# R2 — index-target checking is line-anchored, not a whole-text substring scan
# ---------------------------------------------------------------------------


def test_regenerated_index_with_link_inside_description_validates_clean(tmp_path):
    store = tmp_path / "memory"
    store.mkdir()
    _write(store, "one-rule.md", _concept("one-rule", "see [the plan](plan.md) before acting", type_="gotcha"))
    lm.regenerate_index(store)
    assert lm.validate_bundle(store) == []


def test_concept_filename_with_parentheses_validates_clean(tmp_path):
    store = tmp_path / "memory"
    store.mkdir()
    _write(store, "a(b)-rule.md", _concept("a(b)-rule", "a rule", type_="gotcha"))
    lm.regenerate_index(store)
    assert lm.validate_bundle(store) == []


def test_check_index_targets_still_flags_a_hand_edited_broken_link(tmp_path):
    store = tmp_path / "memory"
    store.mkdir()
    _write(store, "one-rule.md", _concept("one-rule", "a rule", type_="gotcha"))
    lm.regenerate_index(store)
    stale = (store / "index.md").read_text(encoding="utf-8") + "- [ghost](ghost.md) — deleted.\n"
    _write(store, "index.md", stale)
    violations = lm._check_index_targets(store, store / "index.md")
    assert any(v.invariant == "broken-target" and v.file == "ghost.md" for v in violations)


# ---------------------------------------------------------------------------
# R3 — index drift comparison is byte-for-byte
# ---------------------------------------------------------------------------


def test_crlf_index_that_byte_differs_from_regeneration_is_drift(tmp_path):
    store = tmp_path / "memory"
    store.mkdir()
    _write(store, "one-rule.md", _concept("one-rule", "a rule", type_="gotcha"))
    expected = lm.generate_index(store)
    (store / "index.md").write_bytes(expected.replace("\n", "\r\n").encode("utf-8"))
    violations = lm.validate_bundle(store)
    assert any(v.invariant == "index-drift" for v in violations)


# ---------------------------------------------------------------------------
# R5 — recursive walk for clause-1 conformance; a named absent store
# ---------------------------------------------------------------------------


def test_nested_markdown_document_is_reported_not_silently_skipped(tmp_path):
    store = tmp_path / "memory"
    (store / "notes").mkdir(parents=True)
    _write(store, "one-rule.md", _concept("one-rule", "a rule", type_="gotcha"))
    _write(store, "notes/hidden.md", "NOT FRONTMATTER AT ALL\n")
    lm.regenerate_index(store)
    violations = lm.validate_bundle(store)
    assert any("hidden.md" in v.file for v in violations)


def test_absent_store_directory_names_the_store_path(tmp_path):
    missing = tmp_path / "no-such-store"
    violations = lm.validate_bundle(missing)
    assert any("no-such-store" in v.file or "no-such-store" in v.detail for v in violations)


def test_a_file_passed_as_store_names_the_store_path(tmp_path):
    not_a_dir = tmp_path / "just-a-file"
    not_a_dir.write_text("not a store\n", encoding="utf-8")
    violations = lm.validate_bundle(not_a_dir)
    assert any("just-a-file" in v.file or "just-a-file" in v.detail for v in violations)


# ---------------------------------------------------------------------------
# CLI wiring
# ---------------------------------------------------------------------------


def test_cli_validate_exit_codes(tmp_path):
    store = tmp_path / "memory"
    _make_valid_store(store)
    assert _run_cli("validate", str(store)).returncode == 0

    _write(store, "broken.md", "no frontmatter\n")
    assert _run_cli("validate", str(store)).returncode == 1


def test_cli_regenerate_index_exit_codes(tmp_path):
    store = tmp_path / "memory"
    _make_valid_store(store)
    result = _run_cli("regenerate-index", str(store))
    assert result.returncode == 0
    assert "wrote" in result.stdout


# --- R1 corollary: writing is byte-preserving too --------------------------
#
# R1 stopped the parser from stripping quotes. The serialiser kept adding
# them for any value containing a colon, so a description written by Record
# came back quoted and gained another pair on every rewrite. Both directions
# must preserve bytes, or neither does.

DIFFICULT_DESCRIPTIONS = [
    'a rule: with a colon and a "quote"',
    "plain colon: here",
    'ends with a quote"',
    'starts with "a quote',
    "no colon at all",
    "has --- inside",
    "em — dash: and `backticks`",
]


@pytest.mark.parametrize("description", DIFFICULT_DESCRIPTIONS)
def test_dump_then_parse_returns_the_same_bytes(description: str) -> None:
    concept = {
        "name": "x",
        "description": description,
        "type": "gotcha",
        "sources": [{"resource": "PR #1: the colon belongs to the value"}],
    }
    dumped = lm.dump_frontmatter(concept)
    parsed = lm.parse_frontmatter(dumped + "\nbody\n")
    if isinstance(parsed, tuple):
        parsed = parsed[0]
    assert parsed["description"] == description
    assert parsed["sources"][0]["resource"] == concept["sources"][0]["resource"]
    # and a second write is stable, so a rewrite cannot accumulate quoting
    assert lm.dump_frontmatter(parsed) == dumped


@pytest.mark.parametrize("value", ["", "  padded  "])
def test_dump_refuses_a_value_with_no_faithful_unquoted_form(value: str) -> None:
    with pytest.raises(ValueError) as excinfo:
        lm.dump_frontmatter({"name": "x", "description": value})
    assert "description" in str(excinfo.value)
    assert repr(value) in str(excinfo.value)


def test_okf_version_round_trips_without_gaining_a_quote_pair() -> None:
    """REQ-7 fixes the reserved index frontmatter's exact text, quotes included,
    so the constant holds `"0.2"` with them and the parser reads them back. The
    serialiser used to add its own pair on top, turning valid metadata into
    `""0.2""` — the validator then rejected a file its own writer produced.
    Found by the second-vendor reviewer."""
    value = {"okf_version": '"0.2"'}
    dumped = lm.dump_frontmatter(value)
    assert 'okf_version: "0.2"' in dumped
    parsed = lm.parse_frontmatter(dumped)
    if isinstance(parsed, tuple):
        parsed = parsed[0]
    assert parsed == value
    assert lm.dump_frontmatter(parsed) == dumped
