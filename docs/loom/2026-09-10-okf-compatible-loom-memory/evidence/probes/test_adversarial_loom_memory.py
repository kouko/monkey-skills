"""Adversarial probes against the OKF-compatible loom-memory change.

Written by the review station's adversary agent, which implemented none of
the code under attack. Every probe here constructs abusive or boundary
input, runs the real shipped code, and asserts on specific behavior — never
merely on an exit status.

A probe exposing a live defect is marked `xfail(strict=True)`: it runs on
every invocation, documents the exact reproduction, and the day the
defect is fixed it turns RED as XPASS, so the fix cannot land while
still claiming the old behavior. Every probe here has already been fixed
(R3-fixes, see decisions.md D-19) and now carries a plain passing
assertion instead — each docstring records, past tense, the defect the
probe once exposed. Every probe is a live regression detector for its
surface: the eight that were `xfail` for the DEFECT they pinned, the
rest for the abuse/boundary attack the code already SURVIVED.

Run:
    python3 -m pytest docs/loom/2026-09-10-okf-compatible-loom-memory/evidence/probes -rxX
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPTS_DIR = REPO_ROOT / "loom-memory" / "scripts"
SKILL_DIR = REPO_ROOT / "loom-memory" / "skills" / "loom-memory"
sys.path.insert(0, str(SCRIPTS_DIR))

import loom_memory as lm  # noqa: E402
import migrate_legacy_store as mls  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _concept(name: str, description: str, *, type_: str = "gotcha", body: str = "\nBody.\n") -> str:
    return (
        "---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        f"type: {type_}\n"
        "sources:\n"
        "  - resource: an origin string\n"
        "---\n" + body
    )


def _legacy_concept(name: str | None, description: str, *, origin: str | None = "PR#1 verbatim") -> str:
    lines = ["---"]
    if name is not None:
        lines.append(f"name: {name}")
    lines.append(f"description: {description}")
    lines.append("type: gotcha")
    if origin is not None:
        lines.append(f"origin: {origin}")
    lines.append("---")
    return "\n".join(lines) + "\n\nThe lesson body.\n"


def _legacy_store(root: Path, files: dict[str, str]) -> Path:
    """A git-backed legacy README-indexed store at <root>/docs/loom/memory."""
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    for key, value in (("user.email", "probe@example.com"), ("user.name", "Probe"), ("core.autocrlf", "false")):
        subprocess.run(["git", "-C", str(root), "config", key, value], check=True, capture_output=True)
    store = root / "docs" / "loom" / "memory"
    store.mkdir(parents=True)
    index_lines = "\n".join(f"- [{Path(n).stem}]({n}) — d" for n in sorted(files))
    (store / "README.md").write_text(f"# Memory\n\nCharter prose.\n\n## Index\n\n{index_lines}\n", encoding="utf-8")
    for filename, text in files.items():
        (store / filename).write_text(text, encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "seed"], check=True, capture_output=True)
    return store


def _invariants(violations: list[lm.Violation]) -> list[str]:
    return sorted(v.invariant for v in violations)


# ---------------------------------------------------------------------------
# Surface 3 — the migration's byte-fidelity and atomicity claims
# ---------------------------------------------------------------------------


def test_migrate_legacy_file_missing_name_leaves_every_other_file_untouched(tmp_path):
    """FIXED (R4): a legacy concept with no `name` key aborts the migration
    cleanly — a MigrationError naming it, with the store left exactly as it
    was. Previously (DEFECT): migrate() wrote concept files one at a time
    and reached `legacy_fm['name']` unguarded, so a legacy file missing
    'name' raised a bare KeyError after earlier files were already
    rewritten — contradicting the module docstring's 'Either way nothing
    is written'. R4 now stages every rewrite in memory, checking every
    legacy file for the fields it will dereference, before writing
    anything.
    """
    store = _legacy_store(
        tmp_path,
        {
            "aaa-fact.md": _legacy_concept("aaa-fact", "First lesson."),
            "zzz-fact.md": _legacy_concept(None, "No name key."),
        },
    )
    before = (store / "aaa-fact.md").read_bytes()

    with pytest.raises(mls.MigrationError) as excinfo:
        mls.migrate(store, tmp_path)

    assert "zzz-fact.md" in str(excinfo.value), "the failure must name the offending file (REQ-17)"
    assert (store / "aaa-fact.md").read_bytes() == before, "no file may be rewritten when migration fails"


def test_migrate_rerun_after_partial_failure_keeps_the_store_valid(tmp_path):
    """FIXED (R4): recovering from a partial migration does not destroy
    provenance. Reproduction: migrate a store whose last file lacks `name`
    (this no longer rewrites anything, per the fix above), fix that file,
    migrate again. Previously (DEFECT): after a partial migration, a
    rerun re-read already-migrated files as legacy —
    `_migrate_concept_frontmatter`'s pass-through loop did not skip
    'sources', so the derived source was overwritten by the empty scalar
    parsed from the 'sources:' key line, and the verbatim legacy origin
    was demoted to a stray top-level '- resource' key, while migration
    still exited 0. R4 now also refuses outright to treat a file already
    carrying 'sources' as legacy.
    """
    store = _legacy_store(
        tmp_path,
        {
            "aaa-fact.md": _legacy_concept("aaa-fact", "First lesson.", origin="PR#1 verbatim"),
            "zzz-fact.md": _legacy_concept(None, "No name key."),
        },
    )
    with pytest.raises(Exception):
        mls.migrate(store, tmp_path)

    (store / "zzz-fact.md").write_text(_legacy_concept("zzz-fact", "Now fixed."), encoding="utf-8")
    mls.migrate(store, tmp_path)

    frontmatter = lm.parse_frontmatter((store / "aaa-fact.md").read_text(encoding="utf-8"))
    sources = frontmatter.get("sources")
    assert isinstance(sources, list) and sources, "the migrated concept must keep at least one sources entry"
    assert any(entry.get("resource") == "PR#1 verbatim" for entry in sources), (
        "REQ-18 requires the legacy origin string to be retained verbatim"
    )
    assert lm.validate_bundle(store) == [], "a migration that exits 0 must leave a valid store"


def test_migrate_hostile_description_scalars_survive_round_trip(tmp_path):
    """SURVIVED: colons, em dashes, backticks, a trailing quote and non-ASCII.

    These are the shapes the module docstring says real store values contain.
    Migration must preserve the body byte-for-byte and the index must carry
    exactly the description the migrated file holds.
    """
    hostile = 'pin it: the reviewer said `--flag` — and left a stray " here 日本語'
    body = "\nLine one\n\n  indented — 日本語 line\n"
    store = _legacy_store(
        tmp_path,
        {"hostile-fact.md": "---\nname: hostile-fact\ndescription: " + hostile + "\ntype: gotcha\norigin: PR#9\n---\n" + body},
    )
    original_body = body

    mls.migrate(store, tmp_path)

    text = (store / "hostile-fact.md").read_text(encoding="utf-8")
    assert text.endswith(original_body), "REQ-18: the lesson body must survive byte-for-byte"
    frontmatter = lm.parse_frontmatter(text)
    assert frontmatter["description"] == hostile
    assert frontmatter["sources"] == [{"resource": "PR#9"}]
    index_line = next(
        line for line in (store / "index.md").read_text(encoding="utf-8").splitlines() if "hostile-fact" in line
    )
    assert index_line.endswith(hostile), "REQ-8: the index copies the description as stored"
    assert lm.validate_bundle(store) == []


def test_migrate_already_migrated_store_refuses_to_run(tmp_path):
    """SURVIVED: a second migration of a complete store is refused, not rerun."""
    store = _legacy_store(tmp_path, {"a-fact.md": _legacy_concept("a-fact", "A lesson.")})
    mls.migrate(store, tmp_path)
    with pytest.raises(mls.MigrationError) as excinfo:
        mls.migrate(store, tmp_path)
    assert "not a legacy README-indexed store" in str(excinfo.value)


# ---------------------------------------------------------------------------
# Surface 1 & 2 — the hand-rolled parser, the index, and the drift check
# ---------------------------------------------------------------------------


def test_validate_freshly_regenerated_index_with_link_in_description_is_clean(tmp_path):
    """FIXED (R2): a description that quotes a Markdown link no longer
    fakes a broken target. Reproduction: a concept whose description
    contains `[the plan](plan.md)`. Previously (DEFECT):
    `_check_index_targets` was a naive '[..](..)' substring scan over the
    whole index text, so the link inside the description was read as an
    index target — `regenerate-index` exited 0 and `validate` then
    reported `[broken-target] plan.md`, naming a file the store never
    claimed to hold. The check is now anchored to each generated entry's
    own line shape, never a whole-text scan.
    """
    store = tmp_path / "store"
    store.mkdir()
    (store / "one-rule.md").write_text(
        _concept("one-rule", "see [the plan](plan.md) before acting"), encoding="utf-8"
    )
    lm.regenerate_index(store)
    assert lm.validate_bundle(store) == []


def test_validate_concept_filename_with_parentheses_is_clean(tmp_path):
    """FIXED (R2): a parenthesis in a concept filename no longer breaks its
    own index link. Previously (DEFECT): the same naive link scan — a
    concept filename containing '(' truncated the href at the inner ')',
    so validate reported a broken target for a file that exists and that
    the generator itself linked.
    """
    store = tmp_path / "store"
    store.mkdir()
    (store / "a(b)-rule.md").write_text(_concept("a(b)-rule", "a rule"), encoding="utf-8")
    lm.regenerate_index(store)
    assert lm.validate_bundle(store) == []


def test_validate_nested_markdown_document_without_frontmatter_is_reported(tmp_path):
    """FIXED (R5): a malformed Markdown doc one directory deep no longer
    validates as clean. Previously (DEFECT): `iter_concept_files` used
    `store.glob('*.md')`, which is not recursive, so a Markdown document
    nested inside the bundle was invisible to validation — the pinned
    OKF clause 1 requires every non-reserved Markdown document in the
    bundle to have parseable frontmatter. `validate_bundle` now walks the
    bundle recursively and reports any nested Markdown document as its
    own offender (concept identity itself stays flat).
    """
    store = tmp_path / "store"
    (store / "notes").mkdir(parents=True)
    (store / "one-rule.md").write_text(_concept("one-rule", "a rule"), encoding="utf-8")
    (store / "notes" / "hidden.md").write_text("NOT FRONTMATTER AT ALL\n", encoding="utf-8")
    lm.regenerate_index(store)
    violations = lm.validate_bundle(store)
    assert any("hidden.md" in v.file for v in violations), "the nested document must be named as an offender"


def test_validate_crlf_index_that_byte_differs_from_regeneration_is_reported(tmp_path):
    """FIXED (R3): byte drift in the generated index fails validation
    (REQ-9). Previously (DEFECT): `check_index_drift` compared
    `Path.read_text()` output, which translates CRLF to LF, so an
    `index.md` whose bytes differed from a fresh regeneration validated
    clean. The comparison is now unconditionally a byte comparison
    (`read_bytes()`), matching REQ-9's letter.
    """
    store = tmp_path / "store"
    store.mkdir()
    (store / "one-rule.md").write_text(_concept("one-rule", "a rule"), encoding="utf-8")
    expected = lm.generate_index(store)
    (store / "index.md").write_bytes(expected.replace("\n", "\r\n").encode("utf-8"))
    assert (store / "index.md").read_bytes() != expected.encode("utf-8"), "precondition: the bytes really differ"
    assert "index-drift" in _invariants(lm.validate_bundle(store))


def test_validate_absent_store_directory_names_the_store_path(tmp_path):
    """FIXED (R5): pointing the validator at a non-existent store now says
    so. Previously (DEFECT): validate on a path that is not a directory
    (a typo, or a regular file) reported only '[index-missing]
    index.md', misdiagnosing an absent store as a store with a missing
    index — REQ-17 requires the offender to be named. `validate_bundle`
    now checks `store.is_dir()` first and names the store path itself.
    """
    missing = tmp_path / "no-such-store"
    violations = lm.validate_bundle(missing)
    assert any("no-such-store" in v.file or "no-such-store" in v.detail for v in violations)


def test_generate_index_quoted_description_is_copied_byte_identically(tmp_path):
    """FIXED (R1): REQ-8's byte-identical copy no longer silently drops
    quote characters. Previously (DEFECT): `_strip_quotes` removed a
    matching leading/trailing quote pair, so a description that was
    deliberately quoted lost those bytes in the index — REQ-8 permits
    stripping leading and trailing WHITESPACE only. `_strip_quotes` is
    now removed entirely from the frontmatter parser; a scalar value is
    everything after the first `:` separator, byte-preserving.
    """
    store = tmp_path / "store"
    store.mkdir()
    quoted = '"a quoted rule"'
    (store / "one-rule.md").write_text(_concept("one-rule", quoted), encoding="utf-8")
    assert lm.generate_index(store).splitlines()[-1].endswith(quoted)


def test_parse_frontmatter_bom_prefixed_concept_fails_naming_the_file(tmp_path):
    """SURVIVED: a UTF-8 BOM is rejected loudly, with the file named."""
    store = tmp_path / "store"
    store.mkdir()
    (store / "bom-rule.md").write_bytes(b"\xef\xbb\xbf" + _concept("bom-rule", "a rule").encode("utf-8"))
    violations = lm.validate_bundle(store)
    assert any(v.file == "bom-rule.md" and v.invariant == "frontmatter" for v in violations)


def test_parse_frontmatter_unterminated_block_fails_naming_the_file(tmp_path):
    """SURVIVED: frontmatter with no closing `---` is rejected, not half-read."""
    store = tmp_path / "store"
    store.mkdir()
    (store / "open-rule.md").write_text(
        "---\nname: open-rule\ndescription: a rule\ntype: gotcha\nsources:\n  - resource: c\n\nno close\n",
        encoding="utf-8",
    )
    violations = lm.validate_bundle(store)
    assert any(v.file == "open-rule.md" and v.invariant == "frontmatter" for v in violations)


def test_parse_frontmatter_sequence_shaped_description_is_rejected(tmp_path):
    """SURVIVED: a description written as a YAML list is not laundered to text."""
    store = tmp_path / "store"
    store.mkdir()
    (store / "list-rule.md").write_text(
        "---\nname: list-rule\ndescription:\n  - one\n  - two\ntype: gotcha\nsources:\n  - resource: c\n---\n\nB\n",
        encoding="utf-8",
    )
    violations = lm.validate_bundle(store)
    assert any(v.file == "list-rule.md" and v.invariant == "description" for v in violations)
    with pytest.raises(lm.LoomMemoryError):
        lm.generate_index(store)


def test_regenerate_index_broken_concept_metadata_writes_nothing(tmp_path):
    """SURVIVED: regeneration refuses to write, and names every offender."""
    store = tmp_path / "store"
    store.mkdir()
    (store / "good-rule.md").write_text(_concept("good-rule", "a rule"), encoding="utf-8")
    (store / "bad-one.md").write_text(_concept("wrong-stem", "a rule"), encoding="utf-8")
    (store / "bad-two.md").write_text("no frontmatter at all\n", encoding="utf-8")
    with pytest.raises(lm.LoomMemoryError) as excinfo:
        lm.regenerate_index(store)
    named = {v.file for v in excinfo.value.violations}
    assert named == {"bad-one.md", "bad-two.md"}, "REQ-17: every offender, not the first"
    assert not (store / "index.md").exists(), "no index.md may be written when metadata is broken"


def test_regenerate_index_hostile_and_non_ascii_corpus_is_idempotent(tmp_path):
    """SURVIVED: regeneration is byte-stable across runs and locale-independent.

    The corpus mixes ASCII, Japanese and Cyrillic names with descriptions
    holding em dashes, backticks, colons and trailing whitespace.
    """
    store = tmp_path / "store"
    store.mkdir()
    for name, description in (
        ("apple-rule", "plain"),
        ("日本語-rule", "非 ASCII — `--flag` を使う: 理由あり"),
        ("правило-rule", "кириллица — trailing spaces here   "),
        ("Zebra-rule", "capitalised stem sorts by codepoint"),
    ):
        (store / f"{name}.md").write_text(_concept(name, description), encoding="utf-8")
    first = lm.regenerate_index(store)
    second = lm.regenerate_index(store)
    assert first == second, "REQ-9: a second unchanged run must be byte-identical"
    assert lm.validate_bundle(store) == []
    linked = [line.split("](")[0][3:] for line in first.splitlines() if line.startswith("- [")]
    assert linked == sorted(linked), "ordering must be plain codepoint order"
    cyrillic_line = next(line for line in first.splitlines() if "правило-rule.md" in line)
    assert cyrillic_line.endswith("trailing spaces here"), "REQ-8 strips trailing whitespace, stably"


def test_validate_duplicate_concept_name_reports_every_offender(tmp_path):
    """SURVIVED: two files claiming one identity are both named."""
    store = tmp_path / "store"
    store.mkdir()
    (store / "first-rule.md").write_text(_concept("shared-name", "a rule"), encoding="utf-8")
    (store / "second-rule.md").write_text(_concept("shared-name", "a rule"), encoding="utf-8")
    violations = lm.validate_bundle(store)
    offenders = {v.file for v in violations if v.invariant == "duplicate-identity"}
    assert offenders == {"first-rule.md", "second-rule.md"}


def test_validate_crlf_concept_file_is_accepted_with_an_lf_index(tmp_path):
    """SURVIVED: a CRLF-authored concept file parses and indexes normally."""
    store = tmp_path / "store"
    store.mkdir()
    (store / "crlf-rule.md").write_bytes(
        _concept("crlf-rule", "a crlf rule").replace("\n", "\r\n").encode("utf-8")
    )
    lm.regenerate_index(store)
    assert lm.validate_bundle(store) == []
    assert b"\r\n" not in (store / "index.md").read_bytes()


def test_validate_empty_store_with_generated_index_is_clean(tmp_path):
    """SURVIVED: a store with an index and no concepts is a normal empty store."""
    store = tmp_path / "store"
    store.mkdir()
    lm.regenerate_index(store)
    assert lm.validate_bundle(store) == []


def test_validate_store_reached_through_a_symlink_is_clean(tmp_path):
    """SURVIVED: a symlinked store directory validates like the real one."""
    real = tmp_path / "real"
    real.mkdir()
    (real / "one-rule.md").write_text(_concept("one-rule", "a rule"), encoding="utf-8")
    lm.regenerate_index(real)
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)
    assert lm.validate_bundle(link) == []


def test_validate_concept_files_without_index_reports_structural_corruption(tmp_path):
    """SURVIVED: concepts with no index.md is corruption, not an empty result."""
    store = tmp_path / "store"
    store.mkdir()
    (store / "one-rule.md").write_text(_concept("one-rule", "a rule"), encoding="utf-8")
    assert "index-missing" in _invariants(lm.validate_bundle(store))


# ---------------------------------------------------------------------------
# Surface 5 — the shipped skill text's own deletion gate
# ---------------------------------------------------------------------------

NEGATION_TOKENS = ("never", "not", "no", "without", "n't", "cannot", "rather than")

SKILL_TEXTS = ("SKILL.md", "references/operations.md")


def _sentences(text: str) -> list[str]:
    flat = re.sub(r"\s+", " ", text.replace("\n", " "))
    return [s.strip() for s in re.split(r"(?<=[.;])\s+", flat) if s.strip()]


def _affirms(text: str, verbs: str, literal: str) -> bool:
    """True when a sentence states `verbs` ... `literal` affirmatively.

    The affirmative verb must precede the pinned literal. A sentence is
    rejected when a negation token negates that verb — the word immediately
    before it, or any word between the verb and the literal. A negation
    elsewhere in the sentence governs a different clause (a subject such as
    "a store with NO index.md", a trailing "Retire NEVER deletes…") and does
    not undo the affirmation. All three readings are pinned by self-tests.
    """
    pattern = re.compile(rf"\b(?:{verbs})\b[^.;]*?\b(?:{literal})\b", re.IGNORECASE)
    for sentence in _sentences(text):
        match = pattern.search(sentence)
        if not match:
            continue
        preceding = sentence[: match.start()].split()
        window = ([preceding[-1]] if preceding else []) + match.group(0).split()[1:]
        if any(word.strip("`*,;:—-").lower() in NEGATION_TOKENS for word in window):
            continue
        return True
    return False


def test_affirmation_matcher_affirmative_example_is_accepted():
    """Self-test: an affirmative requirement sentence is accepted."""
    assert _affirms("Require explicit user approval before deleting anything.", "require|obtain", "approval")


def test_affirmation_matcher_negated_example_is_rejected():
    """Self-test: the same sentence carrying a negation of the verb is rejected."""
    assert not _affirms(
        "Do not require explicit user approval before deleting anything.", "require|obtain", "approval"
    )


def test_affirmation_matcher_negated_subject_example_is_accepted():
    """Self-test: a negation inside the subject does not negate the statement."""
    assert _affirms("A store with no index.md is structural corruption.", "is|are", "corruption")


def _section(text: str, heading: str) -> str:
    match = re.search(rf"^(#{{2,3}})\s+{re.escape(heading)}\s*$", text, re.MULTILINE)
    assert match, f"no heading {heading!r} in the shipped text"
    level = len(match.group(1))
    rest = text[match.end() :]
    nxt = re.search(rf"^#{{1,{level}}}\s+\S", rest, re.MULTILINE)
    return rest[: nxt.start()] if nxt else rest


def _skill_section(relative: str, heading: str) -> str:
    return _section((SKILL_DIR / relative).read_text(encoding="utf-8"), heading)


def test_skill_text_retire_section_requires_approval_before_deleting():
    """SURVIVED: both shipped files gate Retire's deletion on explicit approval."""
    for relative in SKILL_TEXTS:
        assert _affirms(
            _skill_section(relative, "Retire"), "require|obtain|ask for", "approval"
        ), f"{relative} Retire section states no affirmative approval requirement"


def test_skill_text_reconcile_section_confines_replacement_to_the_existing_file():
    """SURVIVED: Reconcile is not a deletion path an agent can use to skip Retire.

    The attack is to reach a no-approval deletion by calling it a Reconcile.
    Both files close it affirmatively: the replacement is of the entry's
    content, in place — neither section authorizes deleting a concept file.
    """
    for relative in SKILL_TEXTS:
        section = _skill_section(relative, "Reconcile")
        assert _affirms(section, "update|updating|edit|editing|replac\\w*", "place|content"), (
            f"{relative} Reconcile section does not affirmatively confine replacement to the existing file"
        )
        assert not re.search(r"\bdelet", section, re.IGNORECASE), (
            f"{relative} Reconcile section mentions deletion outside the approval gate"
        )


def test_skill_text_recall_section_calls_a_missing_index_structural_corruption():
    """SURVIVED: a store with concepts and no index is not readable as empty.

    The attack is to have an agent treat a corrupt store as a normal empty
    recall. Both files affirmatively name that state structural corruption.
    """
    for relative in SKILL_TEXTS:
        assert _affirms(
            _skill_section(relative, "Recall"), "is|are|treat\\w*|report\\w*", "corruption"
        ), f"{relative} Recall section does not affirmatively name a missing index as corruption"
