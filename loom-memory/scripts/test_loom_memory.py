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
