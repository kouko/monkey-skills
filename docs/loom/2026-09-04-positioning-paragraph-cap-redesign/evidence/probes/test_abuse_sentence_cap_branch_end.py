"""Branch-end adversary probes (agent_id adv-branch-end-cap-e3a0) against the
sentence-cap machinery landed for 2026-09-04-positioning-paragraph-cap-
redesign — `loom-code/scripts/test_review_station_text.py::_sentences` (the
shipped helper) and its independent oracle at
`evidence/probes/test_abuse_sentence_cap.py::_sentences` (W0-01's).

Scope per dispatch: differential test the helper against the oracle on
hostile inputs, and stress the mutation helper's `count=1 -> count=0`
change (`test_probes_positioning_branch_end.py::_mutate_paragraph`) for
both directions of weakness (does it still kill every mutant; does
deleting all occurrences make any mutant trivially dead).

Word counts use `len(str.split())`, never `wc` (BSD/GNU disagree).
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

# probes -> evidence -> <change-id> -> loom -> docs -> repo root
REPO = Path(__file__).resolve().parents[5]

STATION_TEXT = REPO / "loom-code/scripts/test_review_station_text.py"
ORACLE = REPO / (
    "docs/loom/2026-09-04-positioning-paragraph-cap-redesign/"
    "evidence/probes/test_abuse_sentence_cap.py"
)
BRANCH_END = REPO / "loom-code/scripts/test_probes_positioning_branch_end.py"
ADVERSARY_MD = REPO / "loom-code/agents/adversary.md"
REVIEWER_MD = REPO / "loom-code/agents/reviewer.md"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader, f"cannot import {path}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


helper_mod = _load(STATION_TEXT, "_adv_be_helper")
oracle_mod = _load(ORACLE, "_adv_be_oracle")
branch_end_mod = _load(BRANCH_END, "_adv_be_branchend")


# ---------------------------------------------------------------------------
# 1. differential test: helper vs. oracle on a corpus of hostile inputs
# ---------------------------------------------------------------------------

HOSTILE_CORPUS = [
    "",  # empty
    "   \n\t  ",  # whitespace-only
    "Claim one; claim two; claim three; claim four, all in one clause.",
    'He said "it is done." Then left the room.',  # sentence ends inside a quote
    "See the docs (already updated). Then proceed.",  # ends after a closing paren
    "This trails off… Then continues here.",  # unicode ellipsis, not in [.!?]
    "This ships to the U.S. market only.",  # abbreviation not in the allow-list
    "This is a `code\nspan with a line break`. Then done.",  # newline inside backticks
    "Is it done? Yes! It ships today.",
    "Multiple    spaces   and\ttabs   collapse.",
    "`" * 5 + " unbalanced backticks stay literal.",
]


@pytest.mark.parametrize("text", HOSTILE_CORPUS, ids=range(len(HOSTILE_CORPUS)))
def test_helper_and_oracle_agree_on_hostile_corpus(text: str) -> None:
    """The shipped helper (`test_review_station_text._sentences`) and the
    W0-01 oracle (`test_abuse_sentence_cap._sentences`) must return the
    IDENTICAL split for every case in the corpus above -- two independently
    authored implementations only count as an oracle pair while they still
    agree; a silent divergence here would mean the sentence cap enforced on
    a `You own` paragraph depends on which file happened to check it."""
    assert helper_mod._sentences(text) == oracle_mod._sentences(text), (
        f"helper/oracle disagree on {text!r}: "
        f"helper={helper_mod._sentences(text)!r} "
        f"oracle={oracle_mod._sentences(text)!r}"
    )


# ---------------------------------------------------------------------------
# 2. abuse/boundary cases against the shared split rule itself
# ---------------------------------------------------------------------------


def test_abuse_semicolon_chain_evades_the_sentence_count_but_not_the_word_cap() -> None:
    """Boundary/hostile: a reader can join several distinct claims with `;`
    into a single grammatical sentence and pay only the SENTENCE_WORD_CAP
    (40 words), never the SENTENCE_CAP (6 sentences) -- the split rule only
    fires on `.!?`. This is plan.md Risks #4's own admitted gap (the
    40-word figure "has no external citation... exists only to block the
    abuse case"), so it is recorded here as a demonstrated (not merely
    theoretical) `held`-by-the-word-cap-only result, not a fresh hole: a
    38-word, five-clause semicolon chain sits under both caps as ONE
    sentence."""
    chain = (
        "Alpha claims one thing; beta claims a second thing; gamma claims a "
        "third thing; delta claims a fourth thing; epsilon claims a fifth "
        "and final thing here today"
    )
    sentences = helper_mod._sentences(chain + ".")
    assert len(sentences) == 1
    assert len(sentences[0].split()) <= helper_mod.SENTENCE_WORD_CAP
    # five independent claims, one counted sentence: the cap does not see them.


@pytest.mark.xfail(strict=True, reason=(
    "REPRODUCED: a sentence that ends `...\"` (period immediately followed "
    "by a closing quote, then whitespace) is not split -- the regex "
    "`(?<=[.!?])\\s+` lookbehind sees the quote character, not the period, "
    "so two sentences are silently merged into one. A `You own` paragraph "
    "editor who happens to end a sentence on a quoted word can add extra "
    "sentences that the SENTENCE_CAP check never counts."
))
def test_abuse_period_before_closing_quote_is_not_recognised_as_terminator() -> None:
    para = 'He said "it is done." Then left the room. Really.'
    sentences = helper_mod._sentences(para)
    assert sentences == ['He said "it is done."', "Then left the room.", "Really."]


@pytest.mark.xfail(strict=True, reason=(
    "REPRODUCED: a unicode ellipsis `…` is not in the terminator class "
    "`[.!?]`, so a sentence ending in `…` is merged with the sentence that "
    "follows it -- the same undercounting failure mode as the quote case "
    "above, via a different character."
))
def test_abuse_unicode_ellipsis_is_not_recognised_as_terminator() -> None:
    para = "This trails off… Then continues here. And ends."
    sentences = helper_mod._sentences(para)
    assert sentences == ["This trails off…", "Then continues here.", "And ends."]


@pytest.mark.xfail(strict=True, reason=(
    "REPRODUCED: the abbreviation allow-list is `e.g.|i.e.|etc.|vs.` only. "
    "Any OTHER dotted abbreviation not on that list (e.g. `U.S.`, `Dr.`, "
    "`Fig.`) is read as a sentence terminator, over-counting a single "
    "sentence as two. This is the opposite-direction bug from the quote/"
    "ellipsis cases: it can make a paragraph LOOK like it exceeds "
    "SENTENCE_CAP when it does not."
))
def test_abuse_unlisted_abbreviation_is_wrongly_treated_as_a_terminator() -> None:
    para = "This ships to the U.S. market only."
    sentences = helper_mod._sentences(para)
    assert sentences == [para]


def test_abuse_backtick_span_containing_a_line_break_still_counts_as_one_word() -> None:
    """Boundary: a backtick span is substituted for a placeholder BEFORE
    whitespace normalisation, so a literal newline inside a span (an
    unusual but legal markdown shape) must not itself introduce a sentence
    break or extra word. Held -- this one does not reproduce."""
    para = "This is a `code\nspan with a line break`. Then done."
    sentences = helper_mod._sentences(para)
    assert sentences == ["This is a BACKTICKSPAN.", "Then done."]


def test_abuse_empty_paragraph_raises_loud_not_silent() -> None:
    """Empty/absent: `_you_own_paragraph`-style lookups must fail loudly on
    an empty or paragraph-less file rather than silently returning an
    empty positioning paragraph that then vacuously satisfies every cap."""
    text = ""
    blocks = [b for b in text.split("\n\n") if b.strip()]
    hits = [b for b in blocks if b.lstrip().startswith("You own")]
    assert hits == []  # confirms the guard clause the real helper relies on
    # the shipped helper's own `_you_own_paragraph` asserts on `hits` being
    # non-empty (test_review_station_text.py, `_you_own_paragraph`); an
    # AssertionError, not a pass, is the correct behaviour here.
    with pytest.raises(AssertionError):
        helper_mod._you_own_paragraph(text)


# ---------------------------------------------------------------------------
# 3. mutation-helper `count=1 -> count=0` change: still-catches / weaker?
# ---------------------------------------------------------------------------


def test_mutation_helper_count_zero_still_kills_every_shipped_drop_token(
    tmp_path,
) -> None:
    """W1-02's `_mutate_paragraph` moved from `count=1` to `count=0`
    (delete ALL occurrences of the drop token, not just the first) to close
    a survivor on `reconcile` (appears twice in adversary.md). Re-run every
    drop token the branch-end file parametrizes over and confirm each still
    kills its case -- i.e. the widening did not accidentally make any of
    the OTHER (single-occurrence) drop tokens trivially or wrongly dead."""
    targets = [
        (ADVERSARY_MD, "negative"),
        (ADVERSARY_MD, "clean tree"),
        (ADVERSARY_MD, "reconcile"),
        (REVIEWER_MD, "omission"),
        (REVIEWER_MD, "overclaim"),
        (REVIEWER_MD, "contradiction"),
        (REVIEWER_MD, "adversary"),
    ]
    for path, drop in targets:
        text = path.read_text(encoding="utf-8")
        blocks = [b for b in re.split(r"\n\s*\n", text) if b.strip()]
        para = [b for b in blocks if b.lstrip().startswith("You own")][0]
        occurrences = len(re.findall(re.escape(drop), para, re.IGNORECASE))
        assert occurrences >= 1, f"{path.name}: drop token {drop!r} not found"
        mutated = branch_end_mod._mutate_paragraph(path, tmp_path, drop)
        mutated_para = branch_end_mod._positioning_paragraph(
            mutated.read_text(encoding="utf-8")
        )
        assert drop.lower() not in mutated_para.lower(), (
            f"{path.name}: count=0 mutation left {drop!r} standing "
            f"({occurrences} occurrence(s) in the source)"
        )


def test_mutation_helper_count_zero_does_not_over_delete_unrelated_text(
    tmp_path,
) -> None:
    """Boundary: `count=0` deletes every occurrence of the drop token
    ANYWHERE in the paragraph, including inside a longer word that happens
    to contain it as a substring. Craft a drop token that IS a substring of
    another word in the paragraph and confirm the mutation does not
    silently corrupt unrelated prose in a way that would make the case
    fail for the wrong reason. `reconcile` is also a substring of
    `reconciles`/`reconciliation`-style forms, but the shipped paragraph
    only contains the bare word `reconcile` twice -- both are the load-
    bearing occurrences, so no over-deletion is possible here. This case
    documents that fact rather than assuming it."""
    text = ADVERSARY_MD.read_text(encoding="utf-8")
    blocks = [b for b in re.split(r"\n\s*\n", text) if b.strip()]
    para = [b for b in blocks if b.lstrip().startswith("You own")][0]
    # every hit of "reconcile" must be the bare word, not a substring of a
    # longer token (e.g. "reconciles") -- otherwise count=0 would delete
    # part of an unrelated word too.
    for m in re.finditer(re.escape("reconcile"), para, re.IGNORECASE):
        start, end = m.start(), m.end()
        before = para[start - 1] if start > 0 else " "
        after = para[end] if end < len(para) else " "
        assert not before.isalpha() and not after.isalpha(), (
            f"'reconcile' at {start}:{end} is a substring of a longer word "
            f"({para[max(0, start-5):end+5]!r}); count=0 would over-delete"
        )
