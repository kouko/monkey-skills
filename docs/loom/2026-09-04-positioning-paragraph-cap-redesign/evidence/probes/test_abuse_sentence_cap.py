"""W0-01 adversary-first probes for 2026-09-04-positioning-paragraph-cap-
redesign, written before W1-01/W1-02/W1-03 exist. Every case is RED now
unless its docstring says otherwise; each names the task that should turn
it green.

This file carries its OWN sentence-split implementation (`_sentences`
below), independent of whatever helper W1-01 lands in
`test_review_station_text.py`. That duplication is deliberate (plan.md
Risks #3): two independent implementations must agree on the same
synthetic paragraphs before the split rule counts as an oracle, not an
artifact of one author's regex.

Rule (copied from plan.md `## 單位決定`, not from any code; updated at
branch-end fix to close the quote/ellipsis undercounting hole reported by
both readers and the adversary):
  1. Replace every backtick span with a placeholder token (its contents
     count as one word, and never introduce a sentence terminator).
  2. Periods that close `e.g.`, `i.e.`, `etc.`, `vs.` are not terminators.
  3. Normalise whitespace.
  4. Split on a terminator (one of `.`, `!`, `?`, or the unicode ellipsis
     `…`), optionally followed by one closing quote or bracket character
     (straight or curly double quote, straight or curly single quote,
     `)`, or `]`), then whitespace. The closing character, when present,
     stays attached to the sentence it closes (it is not consumed by the
     split).
  5. Non-empty pieces are sentences; each piece's `len(piece.split())` is
     its word length (the backtick placeholder counts as one word).

Word counts always use `len(str.split())` — never `wc` (BSD/GNU disagree).
"""
from __future__ import annotations

import re
from pathlib import Path

# evidence/probes/test_abuse_sentence_cap.py -> parents[5] is the repo root
# (probes -> evidence -> <change-id> -> loom -> docs -> repo root).
REPO = Path(__file__).resolve().parents[5]

REVIEWER_MD = REPO / "loom-code/agents/reviewer.md"
ADVERSARY_MD = REPO / "loom-code/agents/adversary.md"
STATION_TEXT_TEST = REPO / "loom-code/scripts/test_review_station_text.py"
GRADUATED_PROBES = [
    REPO / "loom-code/scripts/test_probes_positioning.py",
    REPO / "loom-code/scripts/test_probes_positioning_branch_end_r2.py",
    REPO / "loom-code/scripts/test_probes_positioning_branch_end.py",
]
PLUGIN_JSON = REPO / "loom-code/.claude-plugin/plugin.json"
CHANGELOG = REPO / "loom-code/CHANGELOG.md"
SINGLE_CONTRACT_TEST = REPO / "loom-code/scripts/test_reviewer_agent_single_contract.py"

SENTENCE_CAP = 6
SENTENCE_WORD_CAP = 40

_ABBREV = re.compile(r"\b(e\.g|i\.e|etc|vs)\.", re.IGNORECASE)
_BACKTICK = re.compile(r"`[^`]*`")
_TERMINATOR = r"[.!?…]"
_CLOSER = "[\"'’”)\\]]"
_SPLIT = re.compile(
    rf"(?:(?<={_TERMINATOR})|(?<={_TERMINATOR}{_CLOSER}))\s+"
)
_NUL = "\x00"


def _sentences(paragraph: str) -> list[str]:
    """Independent oracle sentence-splitter — see module docstring rule."""
    text = _BACKTICK.sub("BACKTICKSPAN", paragraph)
    text = _ABBREV.sub(lambda m: m.group(1) + _NUL, text)
    text = " ".join(text.split())
    pieces = [p.replace(_NUL, ".") for p in _SPLIT.split(text) if p.strip()]
    return pieces


def _you_own_paragraph(text: str) -> str:
    blocks = [b for b in text.split("\n\n") if b.strip()]
    hits = [b for b in blocks if b.lstrip().startswith("You own")]
    assert hits, "no `You own` paragraph found"
    return hits[0]


# --- (1) split-rule oracle -------------------------------------------------


def test_case1_oracle_backtick_period_is_not_a_terminator():
    """Attack: a backtick span holding a literal `.` must not split the
    sentence it sits inside. RED/GREEN: this exercises only this file's own
    oracle, so it is GREEN now — it documents the arithmetic W1-01/W1-02
    must match, not behaviour of unwritten code."""
    para = "The rule is written as `re.split(r\"a.b.c\")` in the helper."
    sentences = _sentences(para)
    assert len(sentences) == 1, (
        f"backtick-internal periods split the sentence: {sentences!r}"
    )
    assert sentences == ["The rule is written as BACKTICKSPAN in the helper."]


def test_case1_oracle_eg_ie_etc_vs_periods_are_not_terminators():
    """Attack: `e.g.`, `i.e.`, `etc.`, `vs.` must not fire a sentence
    boundary. GREEN now (own-oracle documentation, see case1 note above)."""
    para = (
        "Cover hostile input (e.g. wrong type, i.e. non-ASCII, etc.) vs. "
        "the happy path once."
    )
    assert len(_sentences(para)) == 1


def test_case1_oracle_decimal_period_is_not_a_terminator():
    """Attack: a decimal number's period (no following whitespace before
    the next digit) must not split. GREEN now (own-oracle documentation)."""
    para = "The cap is set to 3.14 exactly for this synthetic case."
    assert len(_sentences(para)) == 1


def test_case1_oracle_dash_clause_does_not_split_a_sentence():
    """Attack: an em-dash aside must not be counted as its own sentence —
    the split-rule sentence unit is intentionally >= a clause; the SENTENCE
    _WORD_CAP guard, not the splitter, is what should catch a dash-stuffed
    run-on. GREEN now (own-oracle documentation)."""
    para = "He said — deliberately, and more than once — that it works."
    assert len(_sentences(para)) == 1


def test_case1_oracle_question_and_exclamation_marks_terminate():
    """Attack: `?` and `!` must terminate a sentence exactly like `.`.
    GREEN now (own-oracle documentation)."""
    para = "Is it done? Yes! It ships today."
    assert _sentences(para) == ["Is it done?", "Yes!", "It ships today."]


def test_case1_oracle_six_sentences_pass_seven_sentences_would_not():
    """Attack: the boundary the new cap sits on — a 6-sentence paragraph is
    within SENTENCE_CAP, a 7th sentence pushes it over. GREEN now (own-
    oracle documentation of the arithmetic W1-01/W1-02 must match)."""
    six = " ".join(f"Sentence number {i} ends here." for i in range(1, 7))
    seven = six + " Sentence number seven ends here."
    assert len(_sentences(six)) == SENTENCE_CAP
    assert len(_sentences(seven)) == SENTENCE_CAP + 1
    assert len(_sentences(six)) <= SENTENCE_CAP
    assert len(_sentences(seven)) > SENTENCE_CAP


def test_case1_oracle_forty_words_pass_forty_one_words_would_not():
    """Attack: the per-sentence word-length boundary — 40 words in one
    sentence is within SENTENCE_WORD_CAP, 41 is not. GREEN now (own-oracle
    documentation)."""
    forty = "word " * 39 + "word."
    forty_one = "word " * 40 + "word."
    assert len(forty.split()) == SENTENCE_WORD_CAP
    assert len(forty_one.split()) == SENTENCE_WORD_CAP + 1


# --- (2) both `You own` paragraphs obey the new caps -----------------------


def test_case2_reviewer_you_own_paragraph_is_within_sentence_and_word_caps():
    """Attack: reviewer.md's positioning paragraph, measured by THIS file's
    own oracle, must be <= 6 sentences and every sentence <= 40 words.
    GREEN now — today's paragraph is already 3 sentences (21/31/27 words),
    well inside the new cap by design (plan.md: the cap is set well above
    current need, not just-fits); this case stays green through W1-01 and
    guards against W1-01 accidentally widening the paragraph past the cap
    while adding the attribution sentence."""
    text = REVIEWER_MD.read_text(encoding="utf-8")
    para = _you_own_paragraph(text)
    sentences = _sentences(para)
    assert len(sentences) <= SENTENCE_CAP, (
        f"reviewer.md You-own paragraph has {len(sentences)} sentences, "
        f"cap is {SENTENCE_CAP}"
    )
    for s in sentences:
        assert len(s.split()) <= SENTENCE_WORD_CAP, (
            f"reviewer.md sentence {s!r} is {len(s.split())} words, "
            f"cap is {SENTENCE_WORD_CAP}"
        )


def test_case2_adversary_you_own_paragraph_is_within_sentence_and_word_caps():
    """Attack: same as above for adversary.md. GREEN now — today's
    paragraph is already 4 sentences (12/25/14/29 words); stays green
    through W1-01 (adding one ~20-word attribution sentence keeps it at
    5/6 sentences per plan.md), guarding against the new sentence pushing
    past the cap."""
    text = ADVERSARY_MD.read_text(encoding="utf-8")
    para = _you_own_paragraph(text)
    sentences = _sentences(para)
    assert len(sentences) <= SENTENCE_CAP, (
        f"adversary.md You-own paragraph has {len(sentences)} sentences, "
        f"cap is {SENTENCE_CAP}"
    )
    for s in sentences:
        assert len(s.split()) <= SENTENCE_WORD_CAP, (
            f"adversary.md sentence {s!r} is {len(s.split())} words, "
            f"cap is {SENTENCE_WORD_CAP}"
        )


def test_case2_station_text_test_carries_no_le_80_assertion():
    """Attack: `test_review_station_text.py` must not keep the old <= 80
    word-count assertion alive alongside the new sentence cap (intent
    Acceptance 1: 'not並存'). RED until W1-01 removes it."""
    text = STATION_TEXT_TEST.read_text(encoding="utf-8")
    assert "<= 80" not in text, (
        "test_review_station_text.py still contains a `<= 80` assertion; "
        "the old word cap must be removed, not kept alongside the new one"
    )


# --- (3) adversary paragraph carries a three-way attribution sentence ------


_READER_WORDS = ("omission", "overclaim", "contradiction")
_IMPLEMENTER_WORDS = ("RED", "implementer")


def test_case3_adversary_paragraph_has_a_three_way_attribution_sentence():
    """Attack: one sentence in adversary.md's You-own paragraph must, in
    the SAME sentence, hand reconciliation-class findings (>= 2 of
    omission/overclaim/contradiction) to the reader (reviewer) AND
    positive executable findings (RED or 'implementer') to the
    implementer — the cold-read residual from #787 (report exaggeration
    and doc omission both defaulted to 'implementer' when read alone).
    RED until W1-01 adds the sentence."""
    text = ADVERSARY_MD.read_text(encoding="utf-8")
    para = _you_own_paragraph(text)
    sentences = _sentences(para)
    hits = [
        s for s in sentences
        if sum(w.lower() in s.lower() for w in _READER_WORDS) >= 2
        and any(w in s for w in _IMPLEMENTER_WORDS)
    ]
    assert hits, (
        "no sentence in adversary.md's You-own paragraph assigns >= 2 of "
        f"{_READER_WORDS} to the reader AND names {_IMPLEMENTER_WORDS} for "
        "the implementer in the same sentence"
    )


# --- (4) neither paragraph cites a docs/ path ------------------------------


def test_case4_neither_you_own_paragraph_cites_a_docs_path():
    """Attack: a `docs/<change-id>/...` citation in a runtime prose
    contract only resolves inside this repo (CLAUDE.md portability rule).
    GREEN now for both files (they already avoid it); guards against a
    W1-01 regression that leans on this change's own evidence path for
    the attribution sentence instead of stating the rule generically."""
    for path in (REVIEWER_MD, ADVERSARY_MD):
        text = path.read_text(encoding="utf-8")
        para = _you_own_paragraph(text)
        assert "docs/" not in para, f"{path.name} You-own paragraph cites docs/"


# --- (5) graduated probes no longer pin the old 80-word unit ---------------


def test_case5_graduated_probes_carry_no_word_cap_80_constant():
    """Attack: the three graduated probe files must drop `WORD_CAP = 80`
    and any `== 80` / `== WORD_CAP` (at-the-cap) assertion once the unit
    is sentences+sentence-length, not raw words. RED until W1-02 — today
    `test_probes_positioning.py` and `..._branch_end_r2.py` both still
    define `WORD_CAP = 80`."""
    offenders = []
    for path in GRADUATED_PROBES:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"WORD_CAP\s*=\s*80\b", text) or re.search(r"==\s*WORD_CAP\b", text) or re.search(r"==\s*80\b", text):
            offenders.append(path.name)
    assert not offenders, (
        f"still pin the old 80-word unit: {offenders}; expected them to "
        "import the sentence/word-length constants instead"
    )


def test_case5_graduated_probes_import_the_shared_sentence_helper():
    """Attack: per plan.md W1-02, the graduated probes must import
    `test_review_station_text._sentences` via `sys.path` rather than
    re-implementing the split rule a third time. RED until W1-02."""
    offenders = []
    for path in GRADUATED_PROBES:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if "SENTENCE_CAP" in text or "_sentences" in text:
            continue
        offenders.append(path.name)
    # branch_end.py never carried an 80-word assertion (plan.md Current
    # State Evidence), so it is allowed to stay untouched; the other two
    # must show evidence of the new unit.
    must_touch = {"test_probes_positioning.py", "test_probes_positioning_branch_end_r2.py"}
    still_untouched = must_touch & set(offenders)
    assert not still_untouched, (
        f"expected the new sentence/word-length unit in {still_untouched}"
    )


# --- (6) version bump + changelog ------------------------------------------


def test_case6_plugin_version_is_above_1_2_2_and_changelog_has_it():
    """Attack: plugin.json must be bumped past 1.2.2, and CHANGELOG.md must
    carry an entry for that exact version. RED until W1-03 (today
    plugin.json is still 1.2.2)."""
    import json

    manifest = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    version = manifest["version"]
    parts = tuple(int(p) for p in version.split("."))
    assert parts > (1, 2, 2), f"plugin.json version is {version}, expected > 1.2.2"

    changelog = CHANGELOG.read_text(encoding="utf-8")
    assert f"[{version}]" in changelog, (
        f"CHANGELOG.md has no entry for [{version}]"
    )


# --- (7) body caps unchanged -------------------------------------------------


def test_case7_adversary_and_reviewer_body_caps_are_unchanged():
    """Attack: adding the attribution sentence must not blow the standing
    body caps (adversary.md <= 600 words, reviewer.md <= 1300 words,
    `body_of()` measured — frontmatter excluded). GREEN now (current
    bodies: adversary ~502/600, reviewer 1300/1300); stays GREEN through
    W1-01, which is the whole point of moving the paragraph off a
    just-fits cap first."""
    import sys

    sys.path.insert(0, str(SINGLE_CONTRACT_TEST.parent))
    try:
        contract_mod = __import__("test_reviewer_agent_single_contract")
    finally:
        sys.path.pop(0)

    reviewer_words = len(contract_mod.body_of(REVIEWER_MD.read_text(encoding="utf-8")).split())
    adversary_words = len(contract_mod.body_of(ADVERSARY_MD.read_text(encoding="utf-8")).split())

    assert adversary_words <= contract_mod.AGENT_CAPS["adversary.md"], (
        f"adversary.md body is {adversary_words} words, cap is "
        f"{contract_mod.AGENT_CAPS['adversary.md']}"
    )
    assert reviewer_words <= contract_mod.AGENT_CAPS["reviewer.md"], (
        f"reviewer.md body is {reviewer_words} words, cap is "
        f"{contract_mod.AGENT_CAPS['reviewer.md']}"
    )
