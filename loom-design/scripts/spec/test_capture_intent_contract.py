"""capture-intent station contract (plan W2-01).

The station is loom-design's entry point, so its SKILL.md is the one
document a cold reader gets for Task B ("CLI todo gains a due date, both
plugins, Claude Code", spec REQ-9). These tests pin what that reader must
be able to find without guessing, plus the two cross-plugin invariants:
the `## Station summary` section is byte-identical to loom-code's copy of
it (a reader who lands on either station sees the same whole-flow table),
and the plugin declares the contract version it needs.

Reading loom-code's file from a loom-design TEST is deliberate: the ban on
cross-plugin references is a RUNTIME portability rule for prose contracts
(a dispatched agent only has the repo it stands in). A test runs in this
repository, where both plugins are checked out side by side.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SKILL = REPO / "loom-design/skills/capture-intent/SKILL.md"
WRITE_PLAN = REPO / "loom-code/skills/write-plan/SKILL.md"
PLUGIN_JSON = REPO / "loom-design/.claude-plugin/plugin.json"
MECHANISMS = REPO / "docs/loom/evidence/mechanisms.yaml"

WORD_CAP = 3500
DESCRIPTION_CAP = 400

# Vocabulary the redesign deletes (concept-model §10). A station written
# after the cut must not reintroduce any of it.
DELETED_VOCABULARY = (
    "brief",
    "seed",
    "pipeline",
    "conductor",
    "on-ramp",
    "onramp",
    "reception",
    "critic",
    "batch",
    "waiver",
)

GATE_IDS = (
    "capture-intent.no-confirmed-without-restatement",
    "capture-intent.product-problem-plain-words",
)


def _text() -> str:
    return SKILL.read_text(encoding="utf-8")


def _body(text: str) -> str:
    """The SKILL.md body, frontmatter stripped."""
    parts = text.split("---\n", 2)
    return parts[2] if len(parts) == 3 else text


def _section(text: str, heading: str) -> str:
    m = re.search(rf"^{re.escape(heading)}$.*?(?=^## |\Z)", text, re.M | re.S)
    assert m, f"section {heading!r} missing"
    return m.group(0)


def test_skill_file_exists() -> None:
    assert SKILL.is_file(), f"{SKILL} does not exist"


def test_frontmatter_name_and_version() -> None:
    text = _text()
    assert re.search(r"^name: capture-intent$", text, re.M)
    assert re.search(r"^version: 1\.0\.0$", text, re.M)


def test_description_within_cap() -> None:
    m = re.search(r"^description: \|\n((?:  .*\n)+)", _text(), re.M)
    assert m, "description must be a block scalar"
    description = " ".join(line.strip() for line in m.group(1).splitlines())
    assert len(description) <= DESCRIPTION_CAP, len(description)


def test_body_within_word_cap() -> None:
    words = len(_body(_text()).split())
    assert words <= WORD_CAP, words


def test_station_summary_is_byte_identical_to_write_plan() -> None:
    ours = _section(_text(), "## Station summary")
    theirs = _section(WRITE_PLAN.read_text(encoding="utf-8"), "## Station summary")
    assert ours == theirs


def test_what_you_will_be_asked_list_present() -> None:
    section = _section(_text(), "## What you will be asked, in plain words")
    # Both install shapes are named, so the user knows which questions are
    # this station's and which belong downstream.
    assert "loom-code" in section


def test_gate_markers_present() -> None:
    text = _text()
    for gate_id in GATE_IDS:
        assert f"<!-- gate: {gate_id} -->" in text, gate_id


def test_gate_markers_registered_in_mechanisms() -> None:
    registry = MECHANISMS.read_text(encoding="utf-8")
    for gate_id in GATE_IDS:
        assert f'id: "{gate_id}"' in registry, gate_id


def test_no_deleted_vocabulary() -> None:
    body = _body(_text()).lower()
    found = [w for w in DELETED_VOCABULARY if re.search(rf"\b{re.escape(w)}\b", body)]
    assert not found, found


def test_referenced_relative_paths_exist() -> None:
    """Every `references/...` or `assets/...` path is skill-dir-relative."""
    skill_dir = SKILL.parent
    cited = set(re.findall(r"`((?:references|assets|scripts)/[^`]+)`", _text()))
    assert cited, "the station cites no bundled file"
    missing = [p for p in cited if not (skill_dir / p).exists()]
    assert not missing, missing


def test_task_b_worked_example_present() -> None:
    text = _text()
    assert "CLI surface changes, no ui-flows cover due dates" in text


_NEGATION = re.compile(r"\b(?:not|never|no)\b|n't")
_OPENING_SENTENCE = (
    "Before building a product feature, this repo needs a set of product "
    "principles first."
)


def _opening_line_passage_ok(text: str) -> bool:
    """True when ONE paragraph both instructs, affirmatively and without a
    negation token in that sentence, to open with the template's line
    translated into the user's language, AND quotes the English source
    sentence. Whitespace is collapsed and blockquote markers stripped first
    (the file wraps at 80 columns and quotes the sentence as a blockquote)."""
    paras = re.split(r"\n\s*\n", text)
    flats = []
    for para in paras:
        flat = " ".join(line.lstrip("> ") for line in para.splitlines())
        flats.append(" ".join(flat.split()))
    # the instruction and the blockquoted sentence are adjacent paragraphs
    for i, flat in enumerate(flats):
        window = " ".join(flats[i : i + 2])
        if _OPENING_SENTENCE not in window:
            continue
        for sentence in re.split(r"(?<=[.!?:])\s+", flat):
            if (
                "translated into the user's language" in sentence
                and "opening line" in sentence
                and not _NEGATION.search(sentence)
            ):
                return True
    return False


def test_ui_flow_six_sentence_present() -> None:
    """The PRINCIPLES interview opening line: since artifact-language-policy
    (loom-design 1.0.4) the station quotes the template's English sentence
    and translates it into the user's language at run time, so the pin is
    the English source plus an affirmative, un-negated translation
    instruction in the same passage — not a fixed Chinese rendering."""
    assert _opening_line_passage_ok(_text())


def test_openingLinePin_negatedInstruction_rejected() -> None:
    """Synthetic contradiction: the same vocabulary with the instruction
    negated must fail the pin, so the pin checks the relationship, not the
    presence of the words."""
    bad = (
        "Open with the template's opening line, which is not translated into "
        "the user's language — the template's current English sentence is:\n"
        f"\n> \"{_OPENING_SENTENCE}\"\n"
    )
    assert not _opening_line_passage_ok(bad)
    good = (
        "Open with the template's opening line, translated into the user's "
        "language — the template's current English sentence is:\n"
        f"\n> \"{_OPENING_SENTENCE}\"\n"
    )
    assert _opening_line_passage_ok(good)


def test_second_vendor_evidence_number_present() -> None:
    text = _text()
    assert "five of the seven" in text


def test_plugin_declares_requires_contract() -> None:
    data = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    assert data["requires-contract"] == ">=1.0"


def test_interview_reference_within_word_cap() -> None:
    ref = SKILL.parent / "references/interview.md"
    assert ref.is_file()
    assert len(ref.read_text(encoding="utf-8").split()) <= 1200
