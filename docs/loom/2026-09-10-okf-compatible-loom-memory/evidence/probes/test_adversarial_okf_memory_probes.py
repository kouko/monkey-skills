"""Adversarial probes against loom-memory/scripts/loom_memory.py and
migrate_legacy_store.py for change 2026-09-10-okf-compatible-loom-memory.

Each probe builds a real temporary store (never mocked), runs the actual
module code, and asserts on specific observable behavior — never only an
exit code. Two probes (marked FATAL DEFECT / DEFECT below) currently FAIL
against the shipped code: they pin the behavior the module's own docstring
promises and demonstrate where the code does not deliver it. The rest
exercise boundary/abuse input the shipped code survives correctly and pin
that surviving behavior as a regression guard.

Run:
    python3 -m pytest docs/loom/2026-09-10-okf-compatible-loom-memory/evidence/probes/test_adversarial_okf_memory_probes.py -v
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPTS_DIR = REPO_ROOT / "loom-memory" / "scripts"
SKILL_MD = REPO_ROOT / "loom-memory" / "skills" / "loom-memory" / "SKILL.md"

sys.path.insert(0, str(SCRIPTS_DIR))

import loom_memory as lm  # noqa: E402


def _concept(name: str, description: str, type_: str = "gotcha", resource: str = "test fixture") -> str:
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


def _run_cli(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / script), *args],
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------------------
# 1. FATAL DEFECT — nested-block "---" line truncates frontmatter silently
#    (attacks the hand-rolled parser: "a literal `---` on its own line")
#    Anchor: loom-memory/scripts/loom_memory.py:152
# ---------------------------------------------------------------------------


def test_parse_frontmatter_nested_dash_only_line_does_not_drop_trailing_keys():
    """FATAL DEFECT. `parse_frontmatter`'s closing-delimiter search
    (`lines[i].strip() == "---"`) ignores indentation, so an INDENTED line
    that is literally three dashes — a normal thing for a lesson body to
    contain in a nested block (a lesson *about* frontmatter/markdown, or a
    multi-line note quoting a page-break) — is treated as the frontmatter's
    own closing `---`. Every key physically written after that line is
    silently dropped from the parsed dict instead of raising any error.
    This test pins the correct contract (every declared key round-trips)
    and currently fails: `sources` disappears even though it is present,
    unquoted, in the source text.
    """
    text = (
        "---\n"
        "name: dash-in-notes\n"
        "description: A lesson about markdown page breaks\n"
        "type: gotcha\n"
        "notes:\n"
        "  ---\n"
        'sources:\n'
        '  - resource: "test fixture"\n'
        "---\n\n"
        "Body text here.\n"
    )
    parsed = lm.parse_frontmatter(text)
    assert parsed is not None, "a well-formed --- ... --- block must parse"
    assert "sources" in parsed, (
        "'sources' is written verbatim inside the frontmatter block but was "
        f"silently dropped by the indentation-blind closing-delimiter scan; parsed={parsed!r}"
    )
    assert parsed["sources"] == [{"resource": "test fixture"}]


def test_validate_bundle_nested_dash_only_line_reports_true_offender_not_phantom_missing_sources():
    """Same defect, exercised through the public `validate` surface. A
    concept file whose frontmatter is fully well-formed (name, description,
    type, sources all present and correct) is misreported as missing
    'sources' — a phantom violation caused by mis-scanning, not by the
    author's actual mistake. REQ-17 promises every violation names the
    real offender; a violation whose named defect does not exist in the
    source text fails that promise. Currently fails.
    """
    import tempfile

    store = Path(tempfile.mkdtemp())
    (store / "dash-in-notes.md").write_text(
        "---\n"
        "name: dash-in-notes\n"
        "description: A lesson about markdown page breaks\n"
        "type: gotcha\n"
        "notes:\n"
        "  ---\n"
        "sources:\n"
        '  - resource: "test fixture"\n'
        "---\n\n"
        "Body text here.\n",
        encoding="utf-8",
    )
    violations = lm._validate_concept_file(store / "dash-in-notes.md")
    sources_violations = [v for v in violations if v.invariant == "sources"]
    assert not sources_violations, (
        "the file's frontmatter genuinely contains a non-empty 'sources' list; "
        f"reporting it missing is a phantom violation caused by mis-scanning: {violations!r}"
    )


# ---------------------------------------------------------------------------
# 2. DEFECT — index-target check has no store boundary (path traversal)
#    Anchor: loom-memory/scripts/loom_memory.py (_check_index_targets)
# ---------------------------------------------------------------------------


def test_check_index_targets_rejects_href_that_escapes_the_store():
    """DEFECT. `_check_index_targets` resolves `store / href` and calls
    `.exists()` with no check that the resolved path stays inside `store`.
    A link such as `../../../../../../etc/passwd` (which exists on every
    POSIX reviewer's machine) is therefore reported as NOT broken, even
    though it plainly is not a concept file this store owns. This test
    pins the correct contract — any href resolving outside `store` is
    flagged — and currently fails.
    """
    import tempfile

    store = Path(tempfile.mkdtemp())
    (store / "index.md").write_text(
        '---\nokf_version: "0.2"\n---\n\n'
        "# Memory Store Index\n\n"
        "## Guides\n\n"
        "- [escape](../../../../../../etc/passwd) — escapes the store\n",
        encoding="utf-8",
    )
    violations = lm._check_index_targets(store, store / "index.md")
    assert violations, (
        "a link that resolves outside the store directory must be flagged as "
        "broken/out-of-store, even when the traversal target happens to exist "
        "on the host filesystem"
    )


# ---------------------------------------------------------------------------
# 3. Boundary/abuse cases the shipped code survives — regression guards
# ---------------------------------------------------------------------------


def test_parse_frontmatter_crlf_line_endings_parses_same_as_lf():
    """Abuse: a concept file saved with CRLF line endings (a real-world
    Windows-authored lesson file). `Path.read_text` does universal-newline
    translation, so CRLF must parse identically to LF. Written as raw
    bytes (not committed to git) so this probe is independent of any git
    autocrlf setting.
    """
    import tempfile

    store = Path(tempfile.mkdtemp())
    lf_text = _concept("crlf-lesson", "A CRLF-authored lesson: still parses")
    crlf_bytes = lf_text.replace("\n", "\r\n").encode("utf-8")
    path = store / "crlf-lesson.md"
    path.write_bytes(crlf_bytes)

    text = path.read_text(encoding="utf-8")
    parsed = lm.parse_frontmatter(text)
    assert parsed is not None
    assert parsed["name"] == "crlf-lesson"
    assert parsed["description"] == "A CRLF-authored lesson: still parses"
    violations = lm._validate_concept_file(path)
    assert violations == [], f"a CRLF-encoded but otherwise valid concept file must validate cleanly: {violations!r}"


def test_parse_frontmatter_utf8_bom_prefix_reported_as_violation_not_crash():
    """Abuse: a UTF-8 BOM (`\\ufeff`) prepended to the file — common output
    of some Windows editors. `read_text(encoding='utf-8')` does not strip
    a BOM, so the very first line becomes `\\ufeff---`, which never equals
    the literal `---` the parser requires. The module must fail closed
    (report a violation) rather than crash or silently accept malformed
    input.
    """
    import tempfile

    store = Path(tempfile.mkdtemp())
    path = store / "bom-lesson.md"
    body = _concept("bom-lesson", "A BOM-prefixed lesson file")
    path.write_bytes(("﻿" + body).encode("utf-8"))

    text = path.read_text(encoding="utf-8")
    parsed = lm.parse_frontmatter(text)
    assert parsed is None, "a BOM-corrupted opening delimiter must not parse as valid frontmatter"

    violations = lm._validate_concept_file(path)
    assert any(v.invariant == "frontmatter" for v in violations), (
        f"a BOM-corrupted file must be reported as a frontmatter violation, not silently ignored: {violations!r}"
    )


def test_parse_frontmatter_non_ascii_name_and_description_round_trip():
    """Non-ASCII throughout: CJK description text and a CJK filename stem
    used verbatim as the frontmatter `name`. Must parse and validate
    cleanly — Unicode content is not a boundary the profile is allowed to
    special-case.
    """
    import tempfile

    store = Path(tempfile.mkdtemp())
    name = "重試三次後升級模型"
    description = "遇到相同錯誤三次時應升級模型層級,而非重複相同提示 — 這是段落中含全形破折號的敘述。"
    path = store / f"{name}.md"
    path.write_text(_concept(name, description, resource="來源:第三方會議紀錄"), encoding="utf-8")

    violations = lm._validate_concept_file(path)
    assert violations == [], f"non-ASCII name/description/source content must validate cleanly: {violations!r}"

    frontmatter = lm.parse_frontmatter(path.read_text(encoding="utf-8"))
    assert frontmatter["name"] == name
    assert frontmatter["description"] == description


def test_generate_index_empty_store_produces_valid_zero_concept_index():
    """Boundary: a store with zero concept files (absence past the empty
    boundary, not merely one item). `generate_index` must not crash and
    must produce a document whose own reserved frontmatter still validates.
    """
    import tempfile

    store = Path(tempfile.mkdtemp())
    text = lm.generate_index(store)
    assert lm.parse_frontmatter(text) == lm.INDEX_FRONTMATTER
    assert "# Memory Store Index" in text
    # No group headings should appear when there are no concepts.
    assert "## Guides" not in text


def test_validate_concept_file_duplicate_frontmatter_key_last_value_wins_deterministically():
    """Abuse: a concept file with the SAME top-level key written twice
    (`name:` appears twice) — a hostile or careless hand-edit. The parser
    does not detect the duplicate (documented scope: a scoped mapping
    reader, not a general YAML validator with duplicate-key detection),
    but it must behave deterministically (always take the last value, never
    crash, never silently mix the two) rather than something unpredictable.
    """
    import tempfile

    store = Path(tempfile.mkdtemp())
    path = store / "dup-key.md"
    path.write_text(
        "---\n"
        "name: wrong-stem-first\n"
        "description: d\n"
        "type: t\n"
        "name: dup-key\n"
        "sources:\n"
        '  - resource: "r"\n'
        "---\n\n"
        "Body.\n",
        encoding="utf-8",
    )
    frontmatter_1 = lm.parse_frontmatter(path.read_text(encoding="utf-8"))
    frontmatter_2 = lm.parse_frontmatter(path.read_text(encoding="utf-8"))
    assert frontmatter_1 == frontmatter_2, "parsing the same duplicate-key text twice must be deterministic"
    assert frontmatter_1["name"] == "dup-key", "last value must win, matching ordinary last-wins mapping semantics"
    # And validation must agree with that same deterministic reading (name == stem passes).
    violations = lm._validate_concept_file(path)
    name_violations = [v for v in violations if v.invariant == "name"]
    assert name_violations == [], f"the deterministic last-value name must satisfy the stem check: {violations!r}"


def test_migrate_legacy_store_unterminated_frontmatter_refuses_without_writing():
    """Abuse against the migration's byte-fidelity claim: a legacy concept
    file missing its closing `---` delimiter. `migrate_legacy_store` must
    raise before writing ANYTHING (README.md untouched, no index.md
    created) rather than partially migrating the store.
    """
    import tempfile

    import migrate_legacy_store as mls

    store = Path(tempfile.mkdtemp())
    readme = (
        "---\n"
        "name: README\n"
        "description: Charter.\n"
        "type: Memory Store Guide\n"
        "origin: commit deadbeef\n"
        "---\n\n"
        "# Guide\n\n"
        "## Index\n\n"
        "- [broken-lesson](broken-lesson.md) — a lesson\n"
    )
    (store / "README.md").write_text(readme, encoding="utf-8")
    # Missing closing '---' entirely.
    (store / "broken-lesson.md").write_text(
        "---\nname: broken-lesson\ndescription: d\norigin: c\n\nBody with no closing delimiter.\n",
        encoding="utf-8",
    )
    readme_before = (store / "README.md").read_text(encoding="utf-8")
    lesson_before = (store / "broken-lesson.md").read_text(encoding="utf-8")

    raised = False
    try:
        # repo_root only needs to make `store` resolvable via relative_to();
        # the broken lesson must raise before any git subprocess call runs.
        mls.migrate(store, store.parent)
    except mls.MigrationError:
        raised = True

    assert raised, "an unterminated legacy frontmatter block must refuse migration, not silently skip the file"
    assert not (store / "index.md").exists(), "a refused migration must not have written index.md"
    assert (store / "README.md").read_text(encoding="utf-8") == readme_before, "README.md must be untouched on refusal"
    assert (store / "broken-lesson.md").read_text(encoding="utf-8") == lesson_before, (
        "the broken lesson file itself must be untouched on refusal"
    )


# ---------------------------------------------------------------------------
# 4. Prose-pin probes (REQ-16 approval gate / "absence never blocks")
#    Each carries an affirmative self-test and a rejected-negation self-test.
# ---------------------------------------------------------------------------


def _sentence_containing(text: str, literal: str) -> str | None:
    # Split on sentence-ending punctuation AND on an em-dash clause break —
    # SKILL.md pins its requirement/negation pairs across an em-dash, and a
    # negation on the far side of one must not contaminate the clause being
    # pinned (that would make the checker reject correct, unhedged prose).
    for sentence in re.split(r"(?<=[.!?])\s+|\s*—\s*", text.replace("\n", " ")):
        if literal in sentence:
            return sentence
    return None


_NEGATION_TOKENS = {"never", "not", "no", "n't", "without", "cannot", "can't"}
_AFFIRMATIVE_VERBS = {"require", "requires", "must", "is", "are"}


def _pins_affirmative_sentence(sentence: str, literal: str) -> bool:
    if literal not in sentence:
        return False
    words = re.findall(r"[a-zA-Z']+", sentence.lower())
    idx = None
    for i, w in enumerate(words):
        if w in _AFFIRMATIVE_VERBS:
            idx = i
            break
    if idx is None:
        return False
    # An affirmative verb must appear before the pinned literal's first word,
    # and no negation token anywhere in the same sentence.
    literal_first_word = re.findall(r"[a-zA-Z']+", literal.lower())[0]
    try:
        literal_idx = words.index(literal_first_word)
    except ValueError:
        literal_idx = len(words)
    has_negation = any(w in _NEGATION_TOKENS for w in words)
    return idx < literal_idx and not has_negation


def test_retire_approval_gate_sentence_is_pinned_affirmatively_in_skill_md():
    """Pins SKILL.md's Retire approval-gate sentence: deleting a concept
    requires explicit user approval. Surface 5 attack: find a reading of
    the shipped text under which an agent could delete without approval.
    The sentence as shipped states the requirement affirmatively
    ('Require explicit user approval before deleting anything'); this test
    fails if that sentence is ever softened, hedged, or reworded as a
    negation ('never requires approval', etc. — see self-tests below).
    """
    text = SKILL_MD.read_text(encoding="utf-8")
    sentence = _sentence_containing(text, "explicit user approval before deleting")
    assert sentence is not None, "the approval-gate sentence must exist verbatim in SKILL.md"
    assert _pins_affirmative_sentence(sentence, "explicit user approval before deleting"), (
        f"the approval-gate sentence must be an affirmative requirement, not a hedge/negation: {sentence!r}"
    )


def test_retire_approval_gate_self_test_affirmative_example_passes():
    """Synthetic self-test: an affirmative rendering of the rule passes the checker."""
    affirmative = "Require explicit user approval before deleting anything from the store."
    assert _pins_affirmative_sentence(affirmative, "explicit user approval before deleting")


def test_retire_approval_gate_self_test_negated_example_is_rejected():
    """Synthetic self-test: a negated rendering of the same words must be rejected
    by the checker, proving it does not just substring-match the literal."""
    negated = "Retire never requires explicit user approval before deleting anything from the store."
    assert not _pins_affirmative_sentence(negated, "explicit user approval before deleting")


def test_absence_never_blocks_sentence_is_pinned_affirmatively_in_skill_md():
    """Pins SKILL.md's Recall step 4: an absent store or empty result is a
    normal, non-error outcome. Surface 4 attack: find a reading under which
    absence is treated as an error that blocks the task.
    """
    text = SKILL_MD.read_text(encoding="utf-8")
    sentence = _sentence_containing(text, "normal no-memory result")
    assert sentence is not None, "the absence-is-normal sentence must exist verbatim in SKILL.md"
    words = re.findall(r"[a-zA-Z']+", sentence.lower())
    assert "is" in words, f"sentence must affirmatively state absence IS normal: {sentence!r}"
    # "not an error" is a permitted local negation of "error" (the sentence's whole
    # point is to deny error-status) — but no negation of the affirmative "is a
    # normal" clause itself is allowed before that clause.
    is_idx = words.index("is")
    normal_idx = next(i for i, w in enumerate(words) if w == "normal")
    pre_words = words[is_idx:normal_idx]
    assert not any(w in ("not", "never", "no") for w in pre_words), (
        f"the 'is a normal...result' clause itself must not be negated: {sentence!r}"
    )


def test_absence_never_blocks_self_test_negated_example_is_rejected():
    """Synthetic self-test: a negated rendering ('is not a normal...result') must fail
    the same check that a genuine rewording of SKILL.md's sentence would need to pass."""
    text = "An absent store or an empty result is not a normal no-memory result, it is an error."
    sentence = _sentence_containing(text, "normal no-memory result")
    assert sentence is not None
    words = re.findall(r"[a-zA-Z']+", sentence.lower())
    is_idx = words.index("is")
    normal_idx = next(i for i, w in enumerate(words) if w == "normal")
    pre_words = words[is_idx:normal_idx]
    assert any(w in ("not", "never", "no") for w in pre_words), "self-test fixture must itself contain the negation"


if __name__ == "__main__":
    sys.exit(subprocess := __import__("pytest").main([__file__, "-v"]))
