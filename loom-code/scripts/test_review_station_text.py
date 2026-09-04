"""RED/GREEN evidence for W1-01 — review station text carries the small
change lane, the docs-lint clause, and consequence-based severity.

Three cheap string-presence assertions; they do not parse or execute the
prose, they only prove the three pieces of text this task adds actually
landed in the files the review station and its reviewer contract read.
"""
from __future__ import annotations

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
    """Split `paragraph` into sentences per the rule documented above."""
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
