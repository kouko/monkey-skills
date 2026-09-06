"""RED/GREEN evidence for W1-01 — review station text carries the small
change lane, the docs-lint clause, and consequence-based severity.

Three cheap string-presence assertions; they do not parse or execute the
prose, they only prove the three pieces of text this task adds actually
landed in the files the review station and its reviewer contract read.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def test_review_skill_md_documents_small_lane() -> None:
    text = (REPO / "loom-code/skills/review/SKILL.md").read_text(encoding="utf-8")
    assert "small lane" in text


def test_review_skill_md_tests_only_is_name_or_location() -> None:
    """Branch-end fix: the small-lane 'tests only' class is name/location
    only (test_*.py, *_test.py, tests/ segment), never content-verified,
    and distinct from the §6 artifact-type table (which still maps a
    tests/-relocated production file to `code`)."""
    text = (REPO / "loom-code/skills/review/SKILL.md").read_text(encoding="utf-8")
    assert "name or location only" in text


def test_reviewer_agent_documents_docs_lint() -> None:
    text = (REPO / "loom-code/agents/reviewer.md").read_text(encoding="utf-8")
    assert "docs-lint" in text


def test_reviewer_agent_settlement_threshold_matches_lenses_verbatim() -> None:
    """wave-end:2-04: reviewer.md's compressed user-judgment-leak paragraph
    must state the same settlement threshold lenses.md defines in full --
    'zero obligation and is reversible' -- not a paraphrase like 'free and
    reversible', which reads differently to a cold reviewer deciding
    whether an agent-decided mark settles a one-way-door choice."""
    reviewer_text = (REPO / "loom-code/agents/reviewer.md").read_text(encoding="utf-8")
    lenses_text = (
        REPO / "loom-code/skills/review/references/lenses.md"
    ).read_text(encoding="utf-8")
    threshold = "carries zero obligation and is reversible"
    assert threshold in lenses_text, f"lenses.md no longer states {threshold!r}"
    assert threshold in reviewer_text, (
        f"reviewer.md's user-judgment-leak paragraph no longer matches "
        f"lenses.md's settlement threshold ({threshold!r})"
    )


def test_lenses_severity_section_defines_act_wrongly() -> None:
    text = (REPO / "loom-code/skills/review/references/lenses.md").read_text(encoding="utf-8")
    start = text.index("## Severity and verdict")
    section = text[start:]
    assert "act wrongly" in section


def _you_own_paragraph(text: str) -> str:
    """Return the block whose first non-blank line starts `You own`."""
    blocks = [b for b in text.split("\n\n") if b.strip()]
    hits = [b for b in blocks if b.lstrip().startswith("You own")]
    assert hits, "no `You own` paragraph found"
    return hits[0]


# --- W1-01: word cap -> sentence cap ----------------------------------------
#
# The old 80-word cap on the two `You own` positioning paragraphs was a
# just-fits budget: it capped LENGTH, not the number of distinct claims a
# paragraph makes, and left no room to add a sentence without either
# rewriting existing prose or blowing the cap. plan.md `## 單位決定` replaces
# it with a SENTENCE cap plus a per-sentence word-length guard:
#
#   SENTENCE_CAP = 6        -- a paragraph may hold at most 6 sentences.
#   SENTENCE_WORD_CAP = 40  -- and no single sentence may run past 40 words.
#
# Rationale (plan.md `## 單位決定`, citing evidence/research-paragraph-cap-
# unit.md): GOV.UK's content design guidance gives a documented, sourced
# rule of thumb -- a paragraph should hold <= 5 sentences, and any sentence
# over 25 words should be split. This repo's cap is set ABOVE that standard
# on both axes, deliberately, so the cap guards against drift rather than
# just barely accommodating today's prose (the same "cap well above current
# need" principle that motivated moving off the old just-fits 80-word
# budget in the first place): 6 sentences (not GOV.UK's 5) is ASD-STE100's
# secondhand-summarized "about 6 sentences" figure, chosen so both
# paragraphs keep >= 1 sentence of headroom after W1-01 adds a sentence to
# adversary.md (3/6 and 5/6, not 5/5 or 4/5). 40 words (not GOV.UK's 25) is
# set from today's longest existing sentence (31 words) plus about 30%
# headroom, because GOV.UK's 25-word figure would force a rewrite of
# reader.md's or adversary.md's prose this change does not otherwise touch;
# the 40-word figure has no external citation of its own (plan.md Risks #4)
# — it exists only to block the abuse case (a dash-stuffed run-on sentence
# smuggling several claims past the sentence cap), and is expected to be
# revisited by a future adversarial pass, not the reason to trust this cap.
#
# Sentence-split rule (identical to the independent oracle in
# evidence/probes/test_abuse_sentence_cap.py -- two separate implementations
# agreeing on the same synthetic inputs is what makes the rule an oracle
# rather than one author's regex):
#   1. Replace every backtick span with a placeholder token (its contents
#      count as one word, and never introduce a sentence terminator).
#   2. Periods that close `e.g.`, `i.e.`, `etc.`, `vs.` are not terminators.
#   3. Normalise whitespace.
#   4. Split on a terminator (one of `.`, `!`, `?`, or the unicode ellipsis
#      `…`), optionally followed by one closing quote or bracket character
#      (straight or curly double quote, straight or curly single quote,
#      `)`, or `]`), then whitespace. The closing character, when present,
#      stays attached to the sentence it closes (it is not consumed by the
#      split).
#   5. Non-empty pieces are sentences; each piece's `len(piece.split())` is
#      its word length (the backtick placeholder counts as one word).

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
    """Split `paragraph` into sentences per the rule documented above.

    Known, accepted limitation (branch-end nit, 2026-09-04): only the four
    abbreviations in `_ABBREV` are exempt. A dotted abbreviation outside that
    list (`U.S.`, `Dr.`) is split as a sentence end and OVERcounts — the
    safe direction for a cap, so the list is not extended speculatively; add
    an entry when a contract paragraph actually needs it."""
    text = _BACKTICK.sub("BACKTICKSPAN", paragraph)
    text = _ABBREV.sub(lambda m: m.group(1) + _NUL, text)
    text = " ".join(text.split())
    pieces = [p.replace(_NUL, ".") for p in _SPLIT.split(text) if p.strip()]
    return pieces


def _assert_within_sentence_caps(para: str) -> None:
    sentences = _sentences(para)
    assert len(sentences) <= SENTENCE_CAP, (
        f"paragraph has {len(sentences)} sentences, cap is {SENTENCE_CAP}: "
        f"{sentences!r}"
    )
    for s in sentences:
        words = len(s.split())
        assert words <= SENTENCE_WORD_CAP, (
            f"sentence {s!r} is {words} words, cap is {SENTENCE_WORD_CAP}"
        )


def test_reviewer_agent_owns_reconciliation_paragraph_within_sentence_caps() -> None:
    """W1-01: reviewer.md carries a `You own` positioning paragraph, <= 6
    sentences and every sentence <= 40 words (see the rationale block above
    this test; never `wc` — BSD/GNU disagree, use `len(str.split())`)."""
    text = (REPO / "loom-code/agents/reviewer.md").read_text(encoding="utf-8")
    para = _you_own_paragraph(text)
    _assert_within_sentence_caps(para)


def test_adversary_agent_owns_negative_paragraph_within_sentence_caps() -> None:
    """W1-01: adversary.md carries a `You own` positioning paragraph, <= 6
    sentences and every sentence <= 40 words (see the rationale block above
    the reviewer test)."""
    text = (REPO / "loom-code/agents/adversary.md").read_text(encoding="utf-8")
    para = _you_own_paragraph(text)
    _assert_within_sentence_caps(para)


def test_reviewer_agent_paragraph_names_output_as_claim_fix_round_confirms() -> None:
    """Branch-end fix (branch-end-02): intent Proposed outcome 2 requires the
    reviewer positioning paragraph to say its output is a claim the fix
    round confirms, without pushing the paragraph past the sentence caps."""
    text = (REPO / "loom-code/agents/reviewer.md").read_text(encoding="utf-8")
    para = _you_own_paragraph(text)
    assert "a claim the fix round confirms" in " ".join(para.split())
    _assert_within_sentence_caps(para)


def test_reviewer_agent_paragraph_has_symmetric_three_way_attribution_sentence() -> None:
    """Branch-end fix round 2 (branch-end-02, plan.md Risks #6 / Questions
    asked #3, option A): two independent cold reads of reviewer.md alone
    both wrongly claimed item 3 ('./probe.py and probe.py counted as two
    artifacts', the adversary's own-artifact-path class) and item 8 ('the
    new function's happy path has no unit test', the implementer's RED
    class) as the reviewer's -- see evidence/coldread-reviewer.txt. One
    sentence in the `You own` paragraph must, in the SAME sentence, name
    BOTH the adversary (a probe's own artifact is not the reviewer's) and
    the implementer (a missing test is the implementer's RED to write)."""
    text = (REPO / "loom-code/agents/reviewer.md").read_text(encoding="utf-8")
    para = _you_own_paragraph(text)
    sentences = _sentences(para)
    hits = [
        s
        for s in sentences
        if "adversary" in s.lower()
        and "implementer" in s.lower()
        and "artifact" in s.lower()
        and ("test" in s.lower() or "RED" in s)
    ]
    assert hits, (
        "no sentence in reviewer.md's You-own paragraph names both the "
        "adversary and the implementer alongside artifact/test-or-RED"
    )
    _assert_within_sentence_caps(para)


def test_adversary_agent_paragraph_owns_probe_artifact_bookkeeping() -> None:
    """Branch-end fix (branch-end-01): cold-read trial 2 showed the class
    'same artifact recorded under two spellings/paths counted twice' was
    claimed by neither role. The adversary paragraph must claim a probe's
    own artifact path (spelling/count) while explicitly leaving a
    cross-document count to the reviewer, within the sentence caps."""
    text = (REPO / "loom-code/agents/adversary.md").read_text(encoding="utf-8")
    para = _you_own_paragraph(text)
    assert "artifact path" in para
    assert "reviewer's" in para
    assert "cross-document" in para
    _assert_within_sentence_caps(para)


_ATTRIBUTION_READER_WORDS = ("omission", "overclaim", "contradiction")
_ATTRIBUTION_IMPLEMENTER_WORDS = ("RED", "implementer")


def test_adversary_agent_paragraph_has_three_way_attribution_sentence() -> None:
    """W1-01: one sentence in adversary.md's `You own` paragraph must, in
    the SAME sentence, hand reconciliation-class findings (>= 2 of
    omission/overclaim/contradiction) to the reader (reviewer) AND positive
    executable findings (RED or 'implementer') to the implementer -- the
    cold-read residual from #787 (report exaggeration and doc omission both
    defaulted to 'implementer' when read alone; see the three-way
    attribution scores in plan.md's Current State Evidence). Matches the
    same judgment as evidence/probes/test_abuse_sentence_cap.py case3."""
    text = (REPO / "loom-code/agents/adversary.md").read_text(encoding="utf-8")
    para = _you_own_paragraph(text)
    sentences = _sentences(para)
    hits = [
        s for s in sentences
        if sum(w.lower() in s.lower() for w in _ATTRIBUTION_READER_WORDS) >= 2
        and any(w in s for w in _ATTRIBUTION_IMPLEMENTER_WORDS)
    ]
    assert hits, (
        "no sentence in adversary.md's You-own paragraph assigns >= 2 of "
        f"{_ATTRIBUTION_READER_WORDS} to the reader AND names "
        f"{_ATTRIBUTION_IMPLEMENTER_WORDS} for the implementer in the same "
        "sentence"
    )


def test_fix_rounds_reader_finding_to_probe_sentence_under_60_words() -> None:
    """W1-01: fix-rounds.md gains a block naming `important`, the adversary,
    and a probe, <= 60 words counted with `len(str.split())`."""
    text = (
        REPO / "loom-code/skills/review/references/fix-rounds.md"
    ).read_text(encoding="utf-8")
    blocks = [b for b in text.split("\n\n") if b.strip()]
    hits = [
        b
        for b in blocks
        if "important" in b.lower()
        and "adversary" in b.lower()
        and "probe" in b.lower()
    ]
    assert hits, "no block naming `important` + adversary + probe found"
    assert len(hits[0].split()) <= 60


# --- W1-01: tool-preference passage in the four contracts + build ----------

_TOOL_PREFERENCE_ANCHOR = "apply_patch"
_TOOL_PREFERENCE_CONTRACTS = {
    "implementer": REPO / "loom-code/agents/implementer.md",
    "reviewer": REPO / "loom-code/agents/reviewer.md",
    "blind-runner": REPO / "loom-code/agents/blind-runner.md",
    "adversary": REPO / "loom-code/agents/adversary.md",
}
_BUILD_SKILL = REPO / "loom-code/skills/build/SKILL.md"


def _list_items(text: str) -> list[str]:
    """Every top-level markdown list item in `text`, continuation lines
    joined into one logical string per item (branch-end fix N3: the old
    version only recognised an item when its anchor sat on the FIRST
    physical line; a re-wrap that pushes a word to a continuation line
    must still be found)."""
    lines = text.splitlines()
    items: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r"^\s*[-*]\s+", line):
            bullet = [line.strip()]
            j = i + 1
            while j < len(lines) and lines[j].strip() and re.match(r"^\s+\S", lines[j]):
                bullet.append(lines[j].strip())
                j += 1
            items.append(" ".join(bullet))
            i = j
        else:
            i += 1
    return items


def _tool_preference_bullet(text: str) -> str:
    """The single list item naming `apply_patch`, continuation lines joined.

    Searches every item's full joined text, not just its first physical
    line (N3). Requires there be exactly one such item in the whole file:
    a second item naming `apply_patch` anywhere (an earlier decoy bullet,
    say) makes the anchor ambiguous rather than silently picking the first
    match (branch-end fix, closes the P7 anchor-hijack class)."""
    hits = [item for item in _list_items(text) if _TOOL_PREFERENCE_ANCHOR in item]
    if not hits:
        raise AssertionError(f"no list item names `{_TOOL_PREFERENCE_ANCHOR}`")
    if len(hits) > 1:
        raise AssertionError(
            f"{len(hits)} list items name `{_TOOL_PREFERENCE_ANCHOR}`; the "
            "tool-preference passage must be stated exactly once per file"
        )
    return hits[0]


def test_four_contracts_carry_a_capped_tool_preference_passage() -> None:
    """W1-01: each of the four agent contracts names the host edit tool,
    `apply_patch`, and `sed -i`/heredoc, in <= 40 words (`len(str.split())`).
    """
    for name, path in _TOOL_PREFERENCE_CONTRACTS.items():
        bullet = _tool_preference_bullet(path.read_text(encoding="utf-8"))
        assert "sed -i" in bullet or "heredoc" in bullet, (
            f"{name}.md tool-preference passage never names sed -i/heredoc"
        )
        assert re.search(r"\bEdit\b|\bWrite\b", bullet), (
            f"{name}.md tool-preference passage never names the host edit tool"
        )
        words = len(bullet.split())
        assert words <= 40, f"{name}.md tool-preference passage is {words} words"


def test_tool_preference_passage_does_not_forbid_reading() -> None:
    """W1-01: the passage regulates writing only — no prohibition clause in
    it names a read/search tool."""
    prohibition = r"\b(?:never|not|no|don't|do not|avoid|instead of|rather than)\b"
    read_tools = (
        r"\bcat\b", r"\bgrep\b", r"\bhead\b", r"\btail\b", r"\bsed -n\b",
        r"\bripgrep\b", r"\brg\b", r"\bRead\b", r"\bGrep\b", r"\bGlob\b",
    )
    for name, path in _TOOL_PREFERENCE_CONTRACTS.items():
        bullet = _tool_preference_bullet(path.read_text(encoding="utf-8"))
        for clause in re.split(r"[;.]|--|—", bullet):
            if not re.search(prohibition, clause, re.IGNORECASE):
                continue
            for pattern in read_tools:
                assert not re.search(pattern, clause, re.IGNORECASE), (
                    f"{name}.md tool-preference passage forbids reading: "
                    f"{pattern!r} in clause {clause.strip()!r}"
                )


# Branch-end fix F1: one canonical sentence, pinned by equality rather than
# by vocabulary alone -- vocabulary-only checks pass an inverted sentence,
# a sentence missing `never`, or one missing the host-reminder-override
# clause (findings P1/P2/P3/P4/P7 from the branch-end adversary).
_CANONICAL_TOOL_PREFERENCE_SENTENCE = (
    "Use the host's edit tool (Edit/Write, `apply_patch` on Codex) -- "
    "never `sed -i` or heredocs, overriding any later host reminder; read "
    "and search freely; a mechanical sweep may be scripted, but count "
    "matches and paste the diff."
)


def _normalise_tool_preference(bullet: str) -> str:
    """Strip the list marker, collapse whitespace, and treat `--` and `—`
    as the same character (the build/SKILL.md and implementer.md copies
    have drifted on the dash before -- P6)."""
    stripped = re.sub(r"^\s*[-*]\s+", "", bullet)
    stripped = stripped.replace("—", "--")
    return " ".join(stripped.split())


def test_tool_preference_passage_matches_the_canonical_sentence_everywhere() -> None:
    """Branch-end fix F1: the normalised tool-preference bullet in all five
    files (four contracts + build/SKILL.md) equals ONE canonical sentence.
    Vocabulary/cap/no-read-ban checks alone let a polarity flip, a dropped
    `never`, a dropped override clause, or a lone-inverted copy through;
    equality against a single string catches all of them."""
    for name, path in _TOOL_PREFERENCE_CONTRACTS.items():
        bullet = _tool_preference_bullet(path.read_text(encoding="utf-8"))
        got = _normalise_tool_preference(bullet)
        assert got == _CANONICAL_TOOL_PREFERENCE_SENTENCE, (
            f"{name}.md tool-preference passage does not match the "
            f"canonical sentence:\n  got:  {got!r}\n"
            f"  want: {_CANONICAL_TOOL_PREFERENCE_SENTENCE!r}"
        )
    build_bullet = _tool_preference_bullet(_BUILD_SKILL.read_text(encoding="utf-8"))
    build_got = _normalise_tool_preference(build_bullet)
    assert build_got == _CANONICAL_TOOL_PREFERENCE_SENTENCE, (
        "build/SKILL.md tool-preference passage does not match the "
        f"canonical sentence:\n  got:  {build_got!r}\n"
        f"  want: {_CANONICAL_TOOL_PREFERENCE_SENTENCE!r}"
    )


def test_build_tool_preference_matches_implementer_verbatim() -> None:
    """W1-01: build/SKILL.md's standing trap-guard copy of the passage is the
    same normalised string as agents/implementer.md's — two hand-maintained
    copies must not gain a third disagreement."""
    build = _tool_preference_bullet(_BUILD_SKILL.read_text(encoding="utf-8"))
    impl = _tool_preference_bullet(
        _TOOL_PREFERENCE_CONTRACTS["implementer"].read_text(encoding="utf-8")
    )
    build_norm = " ".join(re.sub(r"^[-*]\s+", "", build).split())
    impl_norm = " ".join(re.sub(r"^[-*]\s+", "", impl).split())
    assert build_norm == impl_norm, (
        "the tool-preference passage differs between build/SKILL.md and "
        f"agents/implementer.md:\n  build: {build_norm!r}\n  impl:  {impl_norm!r}"
    )


def test_trap_heading_inventory_the_review_pointers_rely_on() -> None:
    """Branch-end fix N1: the §3/§4 pointer sentence tells the dispatcher to
    carry "that contract's own `## Traps` section" verbatim. reviewer.md,
    blind-runner.md, and adversary.md each carry a heading literally named
    `## Traps`; implementer.md deliberately carries `## Trap-guards`
    instead (its own pointer line reads differently — build/SKILL.md names
    it directly rather than through review/SKILL.md's generic pointer).
    Pinning the inventory here means a rename silently breaking the
    pointer sentence fails loudly in this file, not only in prose."""
    headings = {
        name: re.findall(r"^## .+$", path.read_text(encoding="utf-8"), re.M)
        for name, path in _TOOL_PREFERENCE_CONTRACTS.items()
    }
    for name in ("reviewer", "blind-runner", "adversary"):
        assert "## Traps" in headings[name], (
            f"{name}.md lost its `## Traps` heading; the §3/§4 pointer "
            "sentence in review/SKILL.md no longer resolves for it"
        )
    assert "## Traps" not in headings["implementer"], (
        "implementer.md gained a `## Traps` heading; update this test "
        "deliberately if that was the intent"
    )
    assert "## Trap-guards" in headings["implementer"], (
        "implementer.md lost its `## Trap-guards` heading"
    )


# Branch-end fix N2: the exact pointer sentence, so a reworded no-op that
# merely keeps the substring "trap" is caught rather than waved through by
# a bare `re.search(r"[Tt]rap", ...)`.
_TRAP_POINTER_SENTENCE = (
    "The dispatch carries that contract's own `## Traps` section verbatim; "
    "do not restate it here."
)


def test_blind_run_and_adversary_sections_point_at_the_contract_trap_section() -> None:
    """W1-02: §3 (blind run) and §4 (adversarial) each carry one line telling
    the dispatcher to carry the contract's `## Traps` section (which holds
    the tool-preference passage) — pointing at it, not re-pasting the
    sentence a third time (surface 8b)."""
    text = (REPO / "loom-code/skills/review/SKILL.md").read_text(encoding="utf-8")
    assert "apply_patch" not in text, (
        "review/SKILL.md pastes the tool-preference sentence itself instead "
        "of pointing at the contract's trap section"
    )

    def section(heading: str, next_heading: str) -> str:
        start = text.index(heading)
        end = text.index(next_heading, start)
        return text[start:end]

    blind_run = section("## 3. Blind run", "## 4. Adversarial")
    adversarial = section("## 4. Adversarial", "## 5. Package tests")
    for name, sect in (("§3 blind run", blind_run), ("§4 adversarial", adversarial)):
        normalised = " ".join(sect.split())
        assert _TRAP_POINTER_SENTENCE in normalised, (
            f"{name} never carries the exact pointer sentence telling the "
            "dispatcher to carry the contract's Traps section verbatim "
            "(branch-end fix N2: a `[Tt]rap` substring match let a reworded "
            "no-op sentence through as long as it kept the word `trap`)"
        )


# --- W2-01: round numbering continuity, and who a fix round resumes --------

from prose_pin import NEGATION_RE as _NEGATION_RE  # shared matcher, one place to widen


def _has_negation(sentence: str) -> bool:
    """True iff `sentence` contains a word-boundary negation token — 'not',
    'never' or 'no' as whole words, or an "n't" contraction."""
    return bool(_NEGATION_RE.search(sentence))


def _flat_sentences(text: str) -> list[str]:
    """Split text into sentences after collapsing newlines to spaces, so a
    sentence that line-wraps in the SKILL.md source still reads as one
    unit here."""
    flat = " ".join(text.split())
    return [p for p in re.split(r"(?<=[.!?])\s+", flat) if p.strip()]


def test_review_round_numbers_continue_across_checkpoints() -> None:
    """W2-01: review/SKILL.md §7 states round numbers continue across a
    change's checkpoints rather than restarting at each one — a branch-end
    round after a required spec round uses the next number — because the
    checker scores the highest round within the checkpoint's own scope.
    Affirmative, un-negated."""
    text = (REPO / "loom-code/skills/review/SKILL.md").read_text(encoding="utf-8")
    start = text.index("## 7. Write the record")
    end = text.index("Every finding `text`, review note")
    section = text[start:end]
    sentences = _flat_sentences(section)
    assert any(
        "continue" in s.lower()
        and "checkpoint" in s.lower()
        and not _has_negation(s)
        for s in sentences
    )
    assert any(
        "required spec round" in s.lower()
        and "next number" in s.lower()
        and not _has_negation(s)
        for s in sentences
    )


def test_review_fix_round_resumes_the_raising_reader() -> None:
    """W2-01: review/SKILL.md §8a states a fix round resumes the reader(s)
    who raised the still-open findings, and a reader who raised none keeps
    its previous PASS standing when the fix stays inside those findings'
    anchors — `push.verdicts-ge-2` recomputes this. Affirmative,
    un-negated."""
    text = (REPO / "loom-code/skills/review/SKILL.md").read_text(encoding="utf-8")
    start = text.index("## 8a. Fix rounds")
    section = text[start:]
    hits = [
        s for s in _flat_sentences(section)
        if "resumes the reader" in s.lower()
        and "still-open findings" in s.lower()
        and "push.verdicts-ge-2" in s.lower()
        and not _has_negation(s)
    ]
    assert hits, (
        "review/SKILL.md §8a has no affirmative resumes-the-raising-reader "
        "sentence naming push.verdicts-ge-2"
    )


def test_matcher_round_numbers_sentence_negated_rejected() -> None:
    sentence = (
        "Round numbers never continue across a change's checkpoints — a "
        "branch-end round after wave-end rounds 1-3 is round 4."
    )
    assert _has_negation(sentence)


def test_matcher_fix_round_resume_sentence_negated_rejected() -> None:
    sentence = (
        "A fix round does not resume the reader who raised the still-open "
        "findings (push.verdicts-ge-2)."
    )
    assert _has_negation(sentence)


def test_matcher_round_numbers_sentence_affirmative_accepted() -> None:
    sentence = (
        "Round numbers continue across a change's checkpoints — a branch-end "
        "round after wave-end rounds 1-3 is round 4."
    )
    assert "continue" in sentence.lower()
    assert not _has_negation(sentence)


def test_matcher_fix_round_resume_sentence_affirmative_accepted() -> None:
    sentence = (
        "A fix round resumes the reader who raised the still-open findings "
        "(push.verdicts-ge-2)."
    )
    assert "resumes the reader" in sentence.lower()
    assert "still-open findings" in sentence.lower()
    assert "push.verdicts-ge-2" in sentence.lower()
    assert not _has_negation(sentence)


# --- W1-02: batched reader records, cap-bump reason, cost block, ----------
# --- third-round design re-look line ---------------------------------------


def test_review_records_batched_before_any_of_the_three_is_dispatched() -> None:
    """W1-02: SS2 states this round's adversary, blind-runner and reviewer
    `dispatch[]` entries are appended once and committed once, together,
    before any of the three is dispatched -- merging the two record-keeping
    rules that used to batch adversary+blind-runner separately from
    reviewers (plan.md Current State Evidence). Affirmative, un-negated."""
    text = (REPO / "loom-code/skills/review/SKILL.md").read_text(encoding="utf-8")
    start = text.index("## 2. Read")
    end = text.index("## 3. Blind run")
    section = text[start:end]
    hits = [
        s for s in _flat_sentences(section)
        if "adversary" in s.lower()
        and "blind-runner" in s.lower()
        and "reviewer" in s.lower()
        and "appended once" in s.lower()
        and "committed once" in s.lower()
        and "before" in s.lower()
        and "dispatched" in s.lower()
        and not _has_negation(s)
    ]
    assert hits, (
        "review/SKILL.md SS2 has no affirmative sentence batching the "
        "adversary, blind-runner and reviewer dispatch[] records into one "
        "commit before any of the three is dispatched"
    )


def test_matcher_batched_records_sentence_negated_rejected() -> None:
    sentence = (
        "This round's adversary, blind-runner and reviewer dispatch[] "
        "entries are never appended once and committed once before any of "
        "the three is dispatched."
    )
    assert _has_negation(sentence)


def test_matcher_batched_records_sentence_affirmative_accepted() -> None:
    sentence = (
        "This round's adversary, blind-runner and reviewer dispatch[] "
        "entries are appended once and committed once, together, before "
        "any of the three is dispatched."
    )
    assert "adversary" in sentence.lower()
    assert "blind-runner" in sentence.lower()
    assert "reviewer" in sentence.lower()
    assert "appended once" in sentence.lower()
    assert "committed once" in sentence.lower()
    assert "before" in sentence.lower()
    assert "dispatched" in sentence.lower()
    assert not _has_negation(sentence)


def _section7(text: str) -> str:
    start = text.index("## 7. Write the record")
    end = text.index("## 8. Hand back")
    return text[start:end]


def test_review_cap_bump_commit_records_one_line_reason() -> None:
    """W1-02: SS7 states a commit that raises a `*_CAP` constant is recorded
    with a one-line reason in this round's notes. Affirmative, un-negated."""
    text = (REPO / "loom-code/skills/review/SKILL.md").read_text(encoding="utf-8")
    section = _section7(text)
    hits = [
        s for s in _flat_sentences(section)
        if "*_cap" in s.lower()
        and "reason" in s.lower()
        and "notes" in s.lower()
        and not _has_negation(s)
    ]
    assert hits, (
        "review/SKILL.md SS7 has no affirmative sentence recording a "
        "one-line reason for a *_CAP bump in this round's notes"
    )


def test_matcher_cap_bump_reason_sentence_negated_rejected() -> None:
    sentence = (
        "A commit that raises a `*_CAP` constant is never recorded with a "
        "one-line reason in this round's notes."
    )
    assert _has_negation(sentence)


def test_matcher_cap_bump_reason_sentence_affirmative_accepted() -> None:
    sentence = (
        "A commit that raises a `*_CAP` constant is recorded with a "
        "one-line reason in this round's notes."
    )
    assert "*_cap" in sentence.lower()
    assert "reason" in sentence.lower()
    assert "notes" in sentence.lower()
    assert not _has_negation(sentence)


def test_review_cost_block_updated_every_checkpoint() -> None:
    """W1-02: SS7 states the record's top-level `cost` block (rounds,
    dispatches, cap changes, hours from the plan commit to the PR) is
    updated at every checkpoint. Affirmative, un-negated."""
    text = (REPO / "loom-code/skills/review/SKILL.md").read_text(encoding="utf-8")
    section = _section7(text)
    hits = [
        s for s in _flat_sentences(section)
        if "cost" in s.lower()
        and "rounds" in s.lower()
        and "dispatches" in s.lower()
        and "cap changes" in s.lower()
        and "hours" in s.lower()
        and "checkpoint" in s.lower()
        and not _has_negation(s)
    ]
    assert hits, (
        "review/SKILL.md SS7 has no affirmative sentence stating the cost "
        "block is updated at every checkpoint"
    )


def test_review_worked_record_shows_cost_key() -> None:
    """W1-02: the SS7 worked JSON record carries the `cost` key with the
    shape rounds/dispatches/cap_changes/hours_plan_to_pr."""
    text = (REPO / "loom-code/skills/review/SKILL.md").read_text(encoding="utf-8")
    section = _section7(text)
    start = section.index("A worked record:")
    fence_start = section.index("```json", start)
    fence_end = section.index("```", fence_start + 7)
    block = section[fence_start + len("```json"):fence_end]
    record = json.loads(block)
    assert "cost" in record, "worked record has no top-level `cost` key"
    cost = record["cost"]
    for key in ("rounds", "dispatches", "cap_changes", "hours_plan_to_pr"):
        assert key in cost, f"worked record cost block is missing {key!r}"


def test_matcher_cost_block_sentence_negated_rejected() -> None:
    sentence = (
        "The record's top-level cost block is never updated at every "
        "checkpoint, this round included."
    )
    assert _has_negation(sentence)


def test_matcher_cost_block_sentence_affirmative_accepted() -> None:
    sentence = (
        "The record's top-level cost block -- rounds, dispatches, cap "
        "changes and hours from the plan commit to the PR -- is updated "
        "at every checkpoint, this round included."
    )
    assert "cost" in sentence.lower()
    assert "rounds" in sentence.lower()
    assert "dispatches" in sentence.lower()
    assert "cap changes" in sentence.lower()
    assert "hours" in sentence.lower()
    assert "checkpoint" in sentence.lower()
    assert not _has_negation(sentence)


def test_fix_rounds_third_round_carries_design_relook_line() -> None:
    """W1-02: fix-rounds.md's "Third round" section states this round's
    notes carry a `design re-look:` line (continue fixing / change the
    design / accept as nit), and the verdict completes only with that line
    present. Affirmative, un-negated."""
    text = (
        REPO / "loom-code/skills/review/references/fix-rounds.md"
    ).read_text(encoding="utf-8")
    start = text.index("## Third round")
    section = text[start:]
    hits = [
        s for s in _flat_sentences(section)
        if "design re-look:" in s
        and "continue fixing" in s.lower()
        and "change the design" in s.lower()
        and "accept as nit" in s.lower()
        and not _has_negation(s)
    ]
    assert hits, (
        "fix-rounds.md 'Third round' section has no affirmative sentence "
        "requiring a design re-look: line in this round's notes"
    )


def test_matcher_design_relook_sentence_negated_rejected() -> None:
    sentence = (
        "This round's notes never carry a design re-look: line -- continue "
        "fixing, change the design, or accept as nit."
    )
    assert _has_negation(sentence)


def test_matcher_design_relook_sentence_affirmative_accepted() -> None:
    sentence = (
        "This round's notes carry a design re-look: line -- continue "
        "fixing, change the design, or accept as nit -- and this round's "
        "verdict completes only when that line is present."
    )
    assert "design re-look:" in sentence
    assert "continue fixing" in sentence.lower()
    assert "change the design" in sentence.lower()
    assert "accept as nit" in sentence.lower()
    assert not _has_negation(sentence)


# --- W1-04: three declared lanes, reader floors, blind-run/adversary by lane


def _review_skill_text() -> str:
    return (REPO / "loom-code/skills/review/SKILL.md").read_text(encoding="utf-8")


def _section_1_scope_and_type() -> str:
    text = _review_skill_text()
    start = text.index("## 1. Scope and artifact type")
    end = text.index("## 2. Read")
    return text[start:end]


def _section_2_read() -> str:
    text = _review_skill_text()
    start = text.index("## 2. Read")
    end = text.index("## 3. Blind run")
    return text[start:end]


def _section_3_blind_run() -> str:
    text = _review_skill_text()
    start = text.index("## 3. Blind run")
    end = text.index("## 4. Adversarial")
    return text[start:end]


def _section_4_adversarial() -> str:
    text = _review_skill_text()
    start = text.index("## 4. Adversarial")
    end = text.index("## 5. Package tests")
    return text[start:end]


def test_lane_paragraph_names_three_declared_lanes_at_branch_end() -> None:
    hits = [
        s for s in _flat_sentences(_section_1_scope_and_type())
        if "`full`" in s
        and "`express`" in s
        and "`gate-only`" in s
        and "branch-end" in s.lower()
        and "only the probes and package tests" in s.lower()
        and not _has_negation(s)
    ]
    assert hits, (
        "review/SKILL.md §1's Lane paragraph has no affirmative sentence "
        "naming full/express/gate-only and what each drops"
    )


def test_matcher_three_lane_sentence_negated_rejected() -> None:
    sentence = (
        "The three declared lanes are `full`, which never drops a reader; "
        "`express`, which cannot keep two readers; and `gate-only`, which "
        "has no readers at all."
    )
    assert _has_negation(sentence)


def test_matcher_three_lane_sentence_affirmative_accepted() -> None:
    sentence = (
        "At branch-end the three declared lanes are `full`, keeping two or "
        "more readers and every run; `express`, keeping one reader; and "
        "`gate-only`, keeping zero readers and "
        "only the probes and package tests as evidence."
    )
    assert "`full`" in sentence
    assert "`express`" in sentence
    assert "`gate-only`" in sentence
    assert "branch-end" in sentence.lower()
    assert "only the probes and package tests" in sentence.lower()
    assert not _has_negation(sentence)


def test_review_has_no_build_time_runtime_scope() -> None:
    section = _section_1_scope_and_type()
    assert "| `after-task:<id>` |" not in section
    assert "| `wave-end:<n>` |" not in section
    assert "| `branch-end` |" in section


def test_required_spec_review_is_one_combined_reader_without_runs() -> None:
    section = _section_1_scope_and_type().lower()
    assert "spec+adversarial" in section
    assert "one independent reviewer" in section
    assert "no blind run" in section
    assert "no separate adversary" in section


def test_claude_is_named_as_the_selected_second_vendor() -> None:
    section = _section_2_read().lower()
    assert "second vendor" in section
    assert "claude" in section


def test_claude_second_vendor_adapter_is_no_tools_and_extracts_result() -> None:
    section = " ".join(_section_2_read().split())
    assert 'claude -p --tools "" --output-format json' in section
    assert "Claude Code 2.1.263" in section
    assert "JSON envelope's `result`" in section


def test_reader_floor_sentence_names_all_four_lanes() -> None:
    hits = [
        s for s in _flat_sentences(_section_2_read())
        if "full two" in s.lower()
        and "small one" in s.lower()
        and "express one" in s.lower()
        and "gate-only zero" in s.lower()
        and not _has_negation(s)
    ]
    assert hits, (
        "review/SKILL.md §2 has no affirmative sentence stating the reader "
        "floors for all four lanes"
    )


def test_matcher_floor_sentence_negated_rejected() -> None:
    sentence = (
        "Reader floors are never full two, small one, express one, and "
        "gate-only zero -- nobody recomputes them."
    )
    assert _has_negation(sentence)


def test_matcher_floor_sentence_affirmative_accepted() -> None:
    sentence = (
        "Reader floors are full two, small one, express one, and "
        "gate-only zero -- the checker's `push.verdicts-ge-2` recomputes "
        "each floor from the effective lane every round."
    )
    assert "full two" in sentence.lower()
    assert "small one" in sentence.lower()
    assert "express one" in sentence.lower()
    assert "gate-only zero" in sentence.lower()
    assert not _has_negation(sentence)


def test_blindrun_by_lane_sentences_present() -> None:
    section = _section_3_blind_run()
    hits = [
        s for s in _flat_sentences(section)
        if "express" in s.lower()
        and "resists a mechanical check" in s.lower()
        and not _has_negation(s)
    ]
    assert hits, (
        "review/SKILL.md §3 has no affirmative sentence on express's blind-"
        "run trigger"
    )
    hits2 = [
        s for s in _flat_sentences(section)
        if "gate-only" in s.lower()
        and "skips the blind run always" in s.lower()
        and not _has_negation(s)
    ]
    assert hits2, (
        "review/SKILL.md §3 has no affirmative sentence on gate-only "
        "skipping the blind run"
    )


def test_matcher_blindrun_express_sentence_negated_rejected() -> None:
    sentence = (
        "Express never runs the blind run unless an Acceptance line "
        "cannot be settled mechanically."
    )
    assert _has_negation(sentence)


def test_matcher_blindrun_express_sentence_affirmative_accepted() -> None:
    sentence = (
        "Express triggers the blind run only for an Acceptance line that "
        "resists a mechanical check, matching the small lane's trigger; "
        "every mechanical line skips it."
    )
    assert "express" in sentence.lower()
    assert "resists a mechanical check" in sentence.lower()
    assert not _has_negation(sentence)


def test_matcher_blindrun_gateonly_sentence_negated_rejected() -> None:
    sentence = "Gate-only never runs the blind run, no matter what."
    assert _has_negation(sentence)


def test_matcher_blindrun_gateonly_sentence_affirmative_accepted() -> None:
    sentence = (
        "Gate-only skips the blind run always, relying on probes and "
        "package tests alone as its evidence."
    )
    assert "gate-only" in sentence.lower()
    assert "skips the blind run always" in sentence.lower()
    assert not _has_negation(sentence)


def test_adversary_once_at_branchend_sentence_present() -> None:
    hits = [
        s for s in _flat_sentences(_section_4_adversarial())
        if "express" in s.lower()
        and "gate-only" in s.lower()
        and "once" in s.lower()
        and "branch-end" in s.lower()
        and not _has_negation(s)
    ]
    assert hits, (
        "review/SKILL.md §4 has no affirmative sentence stating express/"
        "gate-only run the adversary once, at branch-end"
    )


def test_matcher_adversary_once_sentence_negated_rejected() -> None:
    sentence = (
        "Express and gate-only never run the adversary more than once, "
        "and cannot run it before branch-end."
    )
    assert _has_negation(sentence)


def test_matcher_adversary_once_sentence_affirmative_accepted() -> None:
    sentence = (
        "Express and gate-only run the adversary once, at branch-end, "
        "keeping the probe floor of three regardless of lane."
    )
    assert "express" in sentence.lower()
    assert "gate-only" in sentence.lower()
    assert "once" in sentence.lower()
    assert "branch-end" in sentence.lower()
    assert not _has_negation(sentence)


# --- W1-04: user-judgment-leak lens catches an agent-written `lane:` line --


def _lenses_user_judgment_leak_row() -> str:
    text = (REPO / "loom-code/skills/review/references/lenses.md").read_text(
        encoding="utf-8"
    )
    start = text.index("| user-judgment-leak |")
    end = text.index("\n", start)
    return text[start:end]


def test_lens_names_agent_written_lane_line_as_finding() -> None:
    row = _lenses_user_judgment_leak_row()
    hits = [
        s for s in _flat_sentences(row)
        if "`lane:`" in s
        and "written by an agent" in s.lower()
        and "user-judgment-leak" in s.lower()
        and "finding" in s.lower()
        and not _has_negation(s)
    ]
    assert hits, (
        "lenses.md's user-judgment-leak row has no affirmative sentence "
        "naming an agent-written `lane:` line as a finding"
    )


def test_matcher_lane_line_sentence_negated_rejected() -> None:
    sentence = (
        "A `lane:` line written by an agent is never a "
        "`user-judgment-leak` finding, no matter who wrote it."
    )
    assert _has_negation(sentence)


def test_matcher_lane_line_sentence_affirmative_accepted() -> None:
    sentence = (
        "A `lane:` line written by an agent, missing `by <user name>`, or "
        "appearing in a plan, is a `user-judgment-leak` finding -- the "
        "lane is a user's decision only."
    )
    assert "`lane:`" in sentence
    assert "written by an agent" in sentence.lower()
    assert "user-judgment-leak" in sentence.lower()
    assert "finding" in sentence.lower()
    assert not _has_negation(sentence)

# --- W2-02: build, review, fix-rounds and the docs lens recompute from the
# --- charter rows ------------------------------------------------------


def test_review_record_section_names_charter_accretion_recompute() -> None:
    """W2-02: SS7 replaces the prose 'add to what is there; never
    drop/rewrite' with an affirmative sentence citing the review charter
    row and the `review-edits <change-id>` recompute
    (`review.round-append-only`)."""
    text = (REPO / "loom-code/skills/review/SKILL.md").read_text(encoding="utf-8")
    section = _section7(text)
    hits = [
        s for s in _flat_sentences(section)
        if "artifacts.review.charter" in s
        and "review-edits" in s
        and "review.round-append-only" in s
        and not _has_negation(s)
    ]
    assert hits, (
        "review/SKILL.md SS7 has no affirmative sentence naming the review "
        "charter row and the review-edits recompute"
    )


def test_matcher_review_charter_accretion_sentence_negated_rejected() -> None:
    sentence = (
        "The review charter row never names which keys gain entries, and "
        "`review-edits <change-id>` does not recompute that accretion at "
        "push (review.round-append-only)."
    )
    assert _has_negation(sentence)


def test_matcher_review_charter_accretion_sentence_affirmative_accepted() -> None:
    sentence = (
        "The review charter row (artifacts.review.charter) names which "
        "keys gain entries at every round, and `review-edits <change-id>` "
        "recomputes that accretion at push (review.round-append-only)."
    )
    assert "artifacts.review.charter" in sentence
    assert "review-edits" in sentence
    assert "review.round-append-only" in sentence
    assert not _has_negation(sentence)


def test_fix_rounds_names_where_the_fix_round_is_recorded() -> None:
    """W2-02: fix-rounds.md's 'Where the fix round is recorded' paragraph
    names the fix commits' reason, review.json as the record for
    previous_findings and verdicts, and the plan charter's edits_after
    list as the only exception to the plan staying as its commit left
    it."""
    text = (
        REPO / "loom-code/skills/review/references/fix-rounds.md"
    ).read_text(encoding="utf-8")
    start = text.index("## Where the fix round is recorded")
    end = text.index("## Third round")
    section = text[start:end]
    hits = [
        s for s in _flat_sentences(section)
        if "review.json" in s
        and "previous_findings" in s
        and "edits_after" in s
        and not _has_negation(s)
    ]
    assert hits, (
        "fix-rounds.md 'Where the fix round is recorded' section has no "
        "affirmative sentence naming review.json, previous_findings and "
        "the plan charter's edits_after list"
    )


def test_matcher_fix_round_record_sentence_negated_rejected() -> None:
    sentence = (
        "The fix commits carry no reason, previous_findings and this "
        "round's verdicts never live in review.json, and the plan does "
        "not keep the text its plan commit left."
    )
    assert _has_negation(sentence)


def test_matcher_fix_round_record_sentence_affirmative_accepted() -> None:
    sentence = (
        "The fix commits carry the reason for the fix; the resumed "
        "reader's previous_findings and this round's verdicts live in "
        "review.json; and the plan keeps the exact text its plan commit "
        "left, the plan charter's edits_after list naming the only "
        "exceptions."
    )
    assert "review.json" in sentence
    assert "previous_findings" in sentence
    assert "edits_after" in sentence
    assert not _has_negation(sentence)


# --- W2-02: lenses.md plan-omission sharpening block, gated -----------------


def _plan_omission_gate_block() -> str:
    text = (
        REPO / "loom-code/skills/review/references/lenses.md"
    ).read_text(encoding="utf-8")
    start = text.index("<!-- gate: charter.plan-omission-narrow -->")
    end = text.index("<!-- /gate -->", start) + len("<!-- /gate -->")
    return text[start:end]


def test_lenses_plan_omission_narrow_gate_present() -> None:
    block = _plan_omission_gate_block()
    assert "<!-- gate: charter.plan-omission-narrow -->" in block
    assert "<!-- /gate -->" in block


def test_lenses_plan_omission_narrow_names_implementer_cannot_start() -> None:
    flat = " ".join(_plan_omission_gate_block().split()).lower()
    assert "the implementer" in flat
    assert "unable to start" in flat or "cannot start" in flat


def test_lenses_plan_omission_narrow_scores_must_not_content_inconsistency() -> None:
    flat = " ".join(_plan_omission_gate_block().split())
    assert "must_not" in flat
    assert "`inconsistency`" in flat
    assert "goes_to" in flat


def test_lenses_plan_omission_narrow_within_sentence_caps() -> None:
    """W2-02: the sharpening block reads <= 120 words and, per the plan's
    Test line, <= 6 sentences of <= 40 words each -- the same cap rule as
    test_probes_sentence_cap.py."""
    block = _plan_omission_gate_block()
    inner = block.split("-->", 1)[1].rsplit("<!--", 1)[0]
    assert len(inner.split()) <= 120
    _assert_within_sentence_caps(inner)
