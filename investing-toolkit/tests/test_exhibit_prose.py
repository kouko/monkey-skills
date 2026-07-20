"""test_exhibit_prose.py — canonical PROSE surface (exhibit_prose.py).

Offline unit tests for `exhibit_prose.prose_surface`, the stdlib
`html.parser`-based flattener that turns a raw 8-K earnings-exhibit HTML
document into ONE canonical prose-text surface: the flattened non-table text
that the downstream prose-KPI producer indexes with substring offsets. It is
the inverse of Route B's exhibit_tables.py — that walker EXTRACTS `<table>`
content; this one EXCLUDES it, keeping only the letter/narrative prose.

This is a text-surface layer only: NO number tokenization / parsing (that is
Task 2). Deterministic — the same input bytes always yield the same surface.

@req: this dispatch traces work by the plan's Task items, NOT registered
loom-spec REQ-ids, so per the implementer contract @req tags are omitted on
every test here (see report). No id is minted to fill the gap. Mirrors sibling
test_exhibit_tables.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"

if str(MARKETS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(MARKETS_SCRIPTS))


def test_prose_surface_excludes_table_text():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    import exhibit_prose

    html = (
        "<html><body>"
        "<p>employees 1,576,000</p>"
        "<table><tr><td>999</td></tr></table>"
        "</body></html>"
    )
    prose = exhibit_prose.prose_surface(html)
    assert "employees 1,576,000" in prose
    assert "999" not in prose


def test_table_boundary_separates_flanking_prose():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # An excised <table> must leave a break so the prose runs on either side
    # cannot concatenate into one corrupt token — the substring surface the
    # downstream anti-fabrication confirm gate depends on.
    import exhibit_prose

    html = "<div>revenue of<table><tr><td>9</td></tr></table>$5.2B</div>"
    prose = exhibit_prose.prose_surface(html)
    # The two runs stay separated (no merged token) and the cell is excised.
    assert "revenue of$5.2B" not in prose
    assert "9" not in prose
    tokens = prose.split()
    assert "revenue" in tokens
    assert "of" in tokens
    assert "$5.2B" in tokens


def test_nested_table_stays_suppressed_until_outermost_closes():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # A boolean flag would un-suppress "C" once the INNER table closes; the
    # depth counter keeps every cell (A, B, C) suppressed until the OUTERMOST
    # table closes. This test FAILS under a boolean-depth regression.
    import exhibit_prose

    html = (
        "<p>outer prose</p>"
        "<table><tr><td>A<table><tr><td>B</td></tr></table>C</td></tr></table>"
        "<p>tail prose</p>"
    )
    prose = exhibit_prose.prose_surface(html)
    assert "outer prose" in prose
    assert "tail prose" in prose
    assert "A" not in prose
    assert "B" not in prose
    assert "C" not in prose


def test_self_closing_block_break_separates_flanking_prose():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # A self-closing block tag (<br/>) between two runs is a prose break, so
    # the flanking text cannot concatenate into one token.
    import exhibit_prose

    html = "<div>first run<br/>second run</div>"
    prose = exhibit_prose.prose_surface(html)
    assert "first runsecond run" not in prose
    tokens = prose.split()
    assert "first" in tokens
    assert "second" in tokens


def test_locate_returns_token_span_quote():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # The number locator returns each candidate with a verbatim token and a
    # char_offset_span [start, end] into the canonical text. The load-bearing
    # invariant is the anchor the anti-fabrication gate verifies against:
    # text[start:end] must equal the token EXACTLY (byte-for-byte substring).
    import exhibit_prose

    text = "...the company had 1,576,000 employees at year end..."
    candidates = exhibit_prose.locate_numbers(text)

    match = [c for c in candidates if c["token"] == "1,576,000"]
    assert match, f"expected a 1,576,000 candidate, got {candidates!r}"
    cand = match[0]
    start, end = cand["start"], cand["end"]
    # Exact-substring invariant, asserted explicitly.
    assert text[start:end] == "1,576,000"
    assert text[start:end] == cand["token"]


def test_locate_absorbs_magnitude_word():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # Word-scale magnitude parsing (Part 2): a trailing magnitude word
    # (thousand/million/billion/trillion, case-insensitive, whitespace-
    # separated) is ABSORBED into the matched token so the anchor spans the
    # whole phrase. META's "3.56 billion" was captured as "3.56" (off by 1e9)
    # before this — the magnitude word was dropped. A NON-magnitude word
    # ("warehouses") is NOT absorbed; a plain number is unchanged. The
    # exact-substring invariant text[start:end]==token must hold over the
    # (possibly extended) span — the load-bearing anti-fabrication anchor.
    import exhibit_prose

    # Magnitude word absorbed into the token, span covers the whole phrase.
    text = "Family DAP was 3.56 billion on average"
    candidates = exhibit_prose.locate_numbers(text)
    match = [c for c in candidates if c["token"] == "3.56 billion"]
    assert match, f"expected a '3.56 billion' candidate, got {candidates!r}"
    cand = match[0]
    start, end = cand["start"], cand["end"]
    assert text[start:end] == "3.56 billion"
    assert text[start:end] == cand["token"]

    # A following NON-magnitude word is NOT absorbed — only the digits.
    text2 = "operates 931 warehouses"
    tokens2 = [c["token"] for c in exhibit_prose.locate_numbers(text2)]
    assert "931" in tokens2, tokens2
    assert "931 warehouses" not in tokens2

    # Plain number with a non-magnitude trailing word is unchanged.
    text3 = "1,576,000 employees"
    tokens3 = [c["token"] for c in exhibit_prose.locate_numbers(text3)]
    assert "1,576,000" in tokens3, tokens3


def test_magnitude_word_boundary_and_case_guards():
    # Pins the two load-bearing guards the docstring sells but the absorb test
    # doesn't exercise (a mutation would otherwise pass the suite silently):
    #  (a) the `\b` after the magnitude alternation blocks a LONGER word that
    #      merely starts with a magnitude prefix ("3.5 billionaire" must NOT
    #      absorb "billion");
    #  (b) IGNORECASE makes an UPPERCASE magnitude word absorb ("3.56 BILLION").
    import exhibit_prose

    # (a) `\b` guard: "billionaire" is not the word "billion" -> no absorb.
    tokens_a = [c["token"] for c in exhibit_prose.locate_numbers("worth 3.5 billionaire vibes")]
    assert "3.5 billionaire" not in tokens_a
    assert "3.5 billion" not in tokens_a  # not even the bare "billion" prefix
    assert "3.5" in tokens_a, tokens_a

    # (b) IGNORECASE: an uppercase magnitude word is absorbed, anchor holds.
    text_b = "DAP was 3.56 BILLION on average"
    match_b = [c for c in exhibit_prose.locate_numbers(text_b) if c["token"] == "3.56 BILLION"]
    assert match_b, "uppercase BILLION should be absorbed under IGNORECASE"
    cb = match_b[0]
    assert text_b[cb["start"]:cb["end"]] == "3.56 BILLION"


def test_nbsp_separated_number_located():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # Real SEC EX-99 HTML uses a non-breaking space (U+00A0) as a THOUSANDS
    # separator ("3<nbsp>560<nbsp>000") specifically to keep the grouped number
    # unbreakable. Before this, whitespace normalization turned the nbsp into a
    # plain space, so the number split into THREE tokens (3 / 560 / 000) and its
    # value was wrong. The surface producer must normalize the nbsp grouping so
    # the number locates as ONE candidate with a valid anchor span.
    import exhibit_prose

    html = "<p>reached 3\u00a0560\u00a0000 subscribers</p>"
    prose = exhibit_prose.prose_surface(html)
    candidates = exhibit_prose.locate_numbers(prose)
    tokens = [c["token"] for c in candidates]
    # ONE number, comma-normalized to the canonical form — NOT split 3/560/000.
    assert tokens == ["3,560,000"], tokens
    cand = candidates[0]
    # Anchor invariant asserted explicitly against the CANONICAL surface.
    assert prose[cand["start"]:cand["end"]] == cand["token"]


def test_thin_space_grouping_and_comma_and_magnitude_coexist():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # A thin space (U+2009) is the other in-the-wild thousands separator; it
    # must normalize the same way as nbsp. Regression: a plain comma number and
    # a magnitude phrase (Task 1) still tokenize exactly as before.
    import exhibit_prose

    # Thin-space grouping normalizes to ONE comma-grouped token, anchor holds.
    prose = exhibit_prose.prose_surface("<p>3\u2009560\u2009000 subs</p>")
    thin = exhibit_prose.locate_numbers(prose)
    assert [c["token"] for c in thin] == ["3,560,000"], thin
    assert prose[thin[0]["start"]:thin[0]["end"]] == thin[0]["token"]

    # Regression: a plain comma number is still ONE token, unchanged.
    tks2 = [c["token"] for c in exhibit_prose.locate_numbers("had 1,576,000 employees")]
    assert tks2.count("1,576,000") == 1, tks2

    # Regression: magnitude-word absorption (Task 1) is untouched.
    tks3 = [c["token"] for c in exhibit_prose.locate_numbers("DAP was 3.56 billion")]
    assert "3.56 billion" in tks3, tks3


def test_long_digit_run_adjacent_to_nbsp_group_does_not_fuse():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # MIRROR IMAGE of the trailing-group guard: without a LEADING guard the
    # grouping regex can begin matching INSIDE a >=4-digit run that sits
    # directly against the nbsp, fusing two independent numbers into one
    # fabricated value ("2026" + "560" -> "2026,560"; "2026" + "250,000" ->
    # "2026,250,000", ~3 orders of magnitude wrong). The exact-substring anchor
    # text[start:end]==token still HOLDS for such a token — it is guaranteed by
    # construction — so the anchor gives ZERO protection here. That is what
    # makes this class fabrication wearing a valid-looking source anchor, the
    # precise failure this whole feature exists to prevent. A legitimately
    # grouped number's LEAD group is always 1-3 digits, so guarding the lead
    # has no false-negative cost.
    import exhibit_prose

    # Probe 1: a 4-digit year immediately against an nbsp + 3-digit run.
    prose = exhibit_prose.prose_surface("<p>as of 2026 560 registered holders</p>")
    tokens = [c["token"] for c in exhibit_prose.locate_numbers(prose)]
    assert "2026,560" not in tokens, f"fused fabricated value: {tokens!r}"
    assert tokens == ["2026", "560"], tokens

    # Probe 2: the same lead against an already-comma-grouped number — the
    # fusion is ~1000x wrong ("2026,250,000" instead of 2026 and 250,000).
    prose2 = exhibit_prose.prose_surface(
        "<p>Fiscal 2026 250,000 units were sold in Q4.</p>"
    )
    tokens2 = [c["token"] for c in exhibit_prose.locate_numbers(prose2)]
    assert "2026,250,000" not in tokens2, f"fused fabricated value: {tokens2!r}"
    assert "2026" in tokens2 and "250,000" in tokens2, tokens2
    # Anchors still hold for the (now correct) tokens.
    for cand in exhibit_prose.locate_numbers(prose2):
        assert prose2[cand["start"]:cand["end"]] == cand["token"]

    # Regression: a legitimate lead group (1-3 digits) still groups.
    prose3 = exhibit_prose.prose_surface("<p>reached 3 560 000 subs</p>")
    assert [c["token"] for c in exhibit_prose.locate_numbers(prose3)] == ["3,560,000"]


def test_full_width_digits_normalize_and_locate():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # Spec Requirement "Consistent text normalization" names full-width digits
    # as part of the ONE normalization policy. Full-width U+FF10-FF19 fold to
    # ASCII 0-9, and the full-width comma / full stop fold too, so a
    # full-width-formatted grouped number normalizes COHERENTLY rather than
    # half-converted. Every fold is LENGTH-PRESERVING (one char -> one char),
    # so char offsets and the anchor invariant survive untouched.
    import exhibit_prose

    prose = exhibit_prose.prose_surface(
        "<p>employees １２３，４５６ total</p>"
    )
    candidates = exhibit_prose.locate_numbers(prose)
    tokens = [c["token"] for c in candidates]
    assert tokens == ["123,456"], tokens
    assert prose[candidates[0]["start"]:candidates[0]["end"]] == candidates[0]["token"]

    # Full-width full stop folds so a decimal reads as one number.
    prose2 = exhibit_prose.prose_surface("<p>EPS of ３．５６ diluted</p>")
    assert [c["token"] for c in exhibit_prose.locate_numbers(prose2)] == ["3.56"]

    # ORDER: folding runs BEFORE grouping detection, so full-width digits
    # separated by an nbsp participate in grouping like ASCII ones.
    prose3 = exhibit_prose.prose_surface(
        "<p>reached ３ ５６０ ０００ subs</p>"
    )
    assert [c["token"] for c in exhibit_prose.locate_numbers(prose3)] == ["3,560,000"]


def test_arabic_indic_digits_normalize_and_locate():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # The other digit family the spec's normalization policy names. U+0660-0669
    # fold to ASCII 0-9, length-preserving, so the anchor invariant holds.
    import exhibit_prose

    prose = exhibit_prose.prose_surface("<p>total ١٢٣٤ units</p>")
    candidates = exhibit_prose.locate_numbers(prose)
    assert [c["token"] for c in candidates] == ["1234"], candidates
    assert prose[candidates[0]["start"]:candidates[0]["end"]] == "1234"


def test_smart_quotes_normalize_without_shifting_offsets():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # Smart quotes are the last member of the spec's ONE normalization policy.
    # Curly single/double quotes (U+2018/2019/201C/201D) fold to ASCII ' and ",
    # so a downstream verbatim quote compares against one stable surface form.
    # The fold is one char -> one char, so a number appearing AFTER the quote
    # keeps its offset and its anchor.
    import exhibit_prose

    prose = exhibit_prose.prose_surface(
        "<p>the company’s “best” year: 1,576,000 employees</p>"
    )
    assert "’" not in prose and "“" not in prose and "”" not in prose
    assert "company's" in prose
    assert '"best"' in prose

    candidates = exhibit_prose.locate_numbers(prose)
    match = [c for c in candidates if c["token"] == "1,576,000"]
    assert match, f"expected 1,576,000 after the quotes, got {candidates!r}"
    cand = match[0]
    # Anchor holds across the folded quotes — no offset drift.
    assert prose[cand["start"]:cand["end"]] == "1,576,000"


def test_locate_cli_emits_located_numbers_json(tmp_path):
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # The --locate CLI mode is the SUBPROCESS surface analysis-kpi crosses to
    # reach this data-markets locator (the analysis->data-markets boundary is
    # crossed by process, never in-process import). It reads the already-
    # canonical prose text from --text and emits a JSON list of located numbers
    # ({token,start,end}) to --out, mirroring exhibit_tables.py's --out JSON.
    # Because it runs locate_numbers on the given text WITHOUT re-flattening,
    # the char offsets stay relative to the input — the anchor the downstream
    # anti-fabrication gate verifies against.
    import exhibit_prose

    text = "The company had 1,576,000 employees and 3.56 diluted EPS."
    text_file = tmp_path / "canonical.txt"
    out_file = tmp_path / "located.json"
    text_file.write_text(text, encoding="utf-8")

    rc = exhibit_prose.main(
        ["--locate", "--text", str(text_file), "--out", str(out_file)]
    )
    assert rc == 0

    located = json.loads(out_file.read_text(encoding="utf-8"))
    tokens = [item["token"] for item in located]
    assert "1,576,000" in tokens
    assert "3.56" in tokens
    # Offset invariant preserved end-to-end through the CLI: text[start:end]
    # equals the token byte-for-byte for every located number.
    for item in located:
        assert text[item["start"]:item["end"]] == item["token"]


def test_magnitude_word_not_absorbed_in_hyphenated_compound():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # WHOLE-BRANCH review finding 1(a). Task 1's absorption alternation ends in
    # `\b`, which is satisfied by a HYPHEN — so "billion-dollar" / "million-unit"
    # were read as the magnitude word "billion" / "million". In a hyphenated
    # compound the word is ADJECTIVAL: it modifies the following noun ("dollar",
    # "unit"), it does not scale the figure. Absorbing it both mis-spans the
    # anchor and (via the downstream multiplier) invents a value ~1e9 too large,
    # while the exact-substring anchor keeps holding BY CONSTRUCTION — fabrication
    # wearing a valid-looking source anchor, the class this feature exists to kill.
    import exhibit_prose

    # A hyphen after the magnitude word blocks absorption; the number still
    # tokenizes PLAIN (degrading to digits is the safe direction).
    tokens = [
        c["token"]
        for c in exhibit_prose.locate_numbers("a 3.56 billion-dollar program")
    ]
    assert "3.56 billion" not in tokens, f"adjectival compound absorbed: {tokens!r}"
    assert tokens == ["3.56"], tokens

    tokens2 = [
        c["token"]
        for c in exhibit_prose.locate_numbers("450 million-unit shipments")
    ]
    assert tokens2 == ["450"], tokens2

    # TRUE POSITIVE preserved: a magnitude word followed by PUNCTUATION (the
    # sentence-final case) still absorbs — the guard rejects only the hyphen,
    # not every non-word char, so "3.56 billion." keeps its multiplier.
    cands = exhibit_prose.locate_numbers("Family DAP was 3.56 billion.")
    assert [c["token"] for c in cands] == ["3.56 billion"], cands
    text = "Family DAP was 3.56 billion."
    assert text[cands[0]["start"]:cands[0]["end"]] == "3.56 billion"

    # TRUE POSITIVE preserved: magnitude word followed by a comma, and mid-clause.
    tokens3 = [
        c["token"]
        for c in exhibit_prose.locate_numbers("was 500 million, up from 400 million")
    ]
    assert tokens3 == ["500 million", "400 million"], tokens3


def test_nbsp_word_separator_after_comma_grouped_number_does_not_fuse():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # WHOLE-BRANCH review finding 2. The T5 grouping guard `(?<!\d)` stops a match
    # from STARTING inside a longer digit run, but an nbsp used as a plain
    # non-breaking WORD separator after a COMMA-grouped number slips past it: in
    # "1,428<nbsp>500-mile trucks" the char before the "428" run is a comma, so
    # the lookbehind passes and "428<nbsp>500" canonicalizes to "428,500",
    # yielding the fabricated 1,428,500 with a valid-looking anchor. Widening the
    # lookbehind to `(?<![\d,])` closes it: a legitimately grouped number's LEAD
    # group is never preceded by a comma, so the widening costs no true positive.
    import exhibit_prose

    prose = exhibit_prose.prose_surface(
        "<p>We deployed 1,428 500-mile trucks.</p>"
    )
    tokens = [c["token"] for c in exhibit_prose.locate_numbers(prose)]
    assert "428,500" not in tokens, f"fused fabricated grouping: {tokens!r}"
    assert "1,428,500" not in tokens, f"fused fabricated value: {tokens!r}"
    assert tokens == ["1,428", "500"], tokens

    # TRUE POSITIVE: a SENTENCE comma before the group is not the failure case —
    # the char immediately adjacent to the digit run is a SPACE, so a genuine
    # nbsp grouping after a comma+space still normalizes.
    prose2 = exhibit_prose.prose_surface("<p>In 2024, 428 500 units shipped.</p>")
    tokens2 = [c["token"] for c in exhibit_prose.locate_numbers(prose2)]
    assert "428,500" in tokens2, tokens2

    # Regression: ordinary groupings (no preceding comma) are untouched.
    prose3 = exhibit_prose.prose_surface("<p>reached 3 560 000 subs</p>")
    assert [c["token"] for c in exhibit_prose.locate_numbers(prose3)] == ["3,560,000"]
    for cand in exhibit_prose.locate_numbers(prose3):
        assert prose3[cand["start"]:cand["end"]] == cand["token"]


def test_magnitude_word_not_absorbed_across_a_block_boundary():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # SECOND whole-branch review, finding 1. Task 1's absorption separator was
    # `\s+`, and `\s` matches the `\n` that `_ProseWalker` inserts at EVERY block
    # boundary — the separator that exists specifically to stop cross-block fusion
    # (see exhibit_prose module docstring / _BLOCK_TAGS). So a block whose text
    # merely BEGINS with a magnitude word fused into the previous block's trailing
    # number: "45,000</li><li>Million Air..." tokenized as "45,000\nMillion"
    # (4.5e10), and the fusion could even cross an EXCISED TABLE. The token is a
    # literal substring by construction, so the anchor holds while the phrase it
    # spans does not exist as prose in the document — the fabrication-wearing-a-
    # valid-anchor class again, now spanning text the source never made adjacent.
    import exhibit_prose

    # Two sibling list items: "Million Air" is a COMPANY NAME opening the next
    # block, not the scale of the previous block's 45,000.
    prose = exhibit_prose.prose_surface(
        "<li>Vehicles delivered: 45,000</li>"
        "<li>Million Air partnerships signed: 12</li>"
    )
    assert prose == "Vehicles delivered: 45,000\nMillion Air partnerships signed: 12"
    tokens = [c["token"] for c in exhibit_prose.locate_numbers(prose)]
    assert "45,000\nMillion" not in tokens, f"fused across block boundary: {tokens!r}"
    assert tokens == ["45,000", "12"], tokens

    # The worst case: the fusion crossing an EXCISED TABLE, joining two runs of
    # prose that are not adjacent in the source document at all.
    prose2 = exhibit_prose.prose_surface(
        "<p>Total headcount was 1,576</p>"
        "<table><tr><td>irrelevant</td></tr></table>"
        "<p>million reasons follow</p>"
    )
    assert prose2 == "Total headcount was 1,576\nmillion reasons follow"
    tokens2 = [c["token"] for c in exhibit_prose.locate_numbers(prose2)]
    assert "1,576\nmillion" not in tokens2, f"fused across excised table: {tokens2!r}"
    assert tokens2 == ["1,576"], tokens2

    # Anchors still hold for what IS emitted.
    for cand in exhibit_prose.locate_numbers(prose2):
        assert prose2[cand["start"]:cand["end"]] == cand["token"]

    # NO LOSS: this assertion previously pinned the opposite result, and the
    # behavior it pinned is the thing the next test removes. The guard used to be
    # CONSERVATIVE because a surface "\n" was ambiguous (walker boundary vs. a
    # newline inside one source run), so it declined a legitimate hard wrap too and
    # "3.56\nbillion" degraded to "3.56". The walker now folds source-run newlines
    # on entry, so the separator is unambiguous and this guard rejects exactly the
    # cross-block fusion — see
    # test_source_line_wrap_inside_a_block_still_absorbs_the_magnitude_word.
    wrapped = exhibit_prose.prose_surface("<p>Family DAP was 3.56\nbillion.</p>")
    assert wrapped == "Family DAP was 3.56 billion."
    assert [c["token"] for c in exhibit_prose.locate_numbers(wrapped)] == [
        "3.56 billion"
    ]

    # TRUE POSITIVE preserved: same-line whitespace still absorbs, including a
    # run of it (a tab or multiple spaces is not a block boundary).
    assert [c["token"] for c in exhibit_prose.locate_numbers("was 3.56 billion")] == [
        "3.56 billion"
    ]
    assert [c["token"] for c in exhibit_prose.locate_numbers("was 3.56 \t billion")] == [
        "3.56 \t billion"
    ]


def test_magnitude_word_absorbed_in_an_ascii_hyphen_range():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # SECOND whole-branch review, finding 2. The compound-joiner guard rejected
    # absorption after ANY of the three hyphen joiners — but ASCII hyphen-minus is
    # the commonest RANGE mark in an ASCII-encoded filing, so "2 billion-3 billion"
    # lost the first bound's scale and committed 2 for a source that says 2 billion:
    # the compound defect INVERTED (an under-scaled value, same valid-looking
    # anchor). Discriminator: after a joiner, a RANGE continues with a DIGIT, a
    # COMPOUND with a LETTER.
    import exhibit_prose

    text = "guidance of 2 billion-3 billion users"
    cands = exhibit_prose.locate_numbers(text)
    assert [c["token"] for c in cands] == ["2 billion", "3 billion"], cands
    for cand in cands:
        assert text[cand["start"]:cand["end"]] == cand["token"]

    text2 = "revenue of 3.5 billion-4.0 billion"
    assert [c["token"] for c in exhibit_prose.locate_numbers(text2)] == [
        "3.5 billion",
        "4.0 billion",
    ]

    # The COMPOUND case stays rejected — the discriminator must not undo finding 1(a).
    assert [c["token"] for c in exhibit_prose.locate_numbers("a 3.56 billion-dollar program")] == [
        "3.56"
    ]
    assert [c["token"] for c in exhibit_prose.locate_numbers("450 million-unit shipments")] == [
        "450"
    ]

    # DISCLOSED RESIDUAL, pinned so the guard's comment cannot overstate it: the
    # discriminator reads the ONE character after the joiner, so a range whose
    # upper bound is not written digit-first ("2 billion-$3 billion") still reads
    # as a compound and degrades to plain digits.
    assert [c["token"] for c in exhibit_prose.locate_numbers("2 billion-$3 billion")] == [
        "2",
        "3 billion",
    ]


def test_source_line_wrap_inside_a_block_still_absorbs_the_magnitude_word():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # THIRD round. The block-separator guard (test above) was correct but had to be
    # paid for with a real loss, because a "\n" on the canonical surface had TWO
    # possible origins: a walker-inserted block boundary, or a newline that was
    # simply INSIDE one source text run. EDGAR HTML is hard-wrapped, so a wrap
    # between a number and its magnitude word is a realistic shape — and in that
    # shape the value silently reverted to 3.56, re-introducing the very META
    # Family DAP defect this part exists to fix, on the flagship case.
    #
    # The fix removes the ambiguity instead of paying for it: `_ProseWalker`
    # collapses source-text newlines AS THEY ENTER, so after the walk a "\n" on the
    # canonical surface means block boundary and NOTHING else. The `[^\S\n]` guards
    # then become EXACT rather than conservative.
    import exhibit_prose

    # A hard wrap INSIDE one <p> — one block, no boundary. The number and its
    # magnitude word are adjacent prose, so the token must span the whole phrase.
    prose = exhibit_prose.prose_surface(
        "<p>Revenue grew to 3.56\nbillion in the quarter</p>"
    )
    assert prose == "Revenue grew to 3.56 billion in the quarter", repr(prose)
    cands = exhibit_prose.locate_numbers(prose)
    assert [c["token"] for c in cands] == ["3.56 billion"], cands

    # The anchor invariant holds over the newly-produced surface, as for any other.
    for cand in cands:
        assert prose[cand["start"]:cand["end"]] == cand["token"]

    # A wrap ANYWHERE inside a block is now ordinary same-line whitespace: it
    # collapses like any other run, and a wrap on the far side of the number is
    # equally harmless.
    assert exhibit_prose.prose_surface("<p>a\nb</p>") == "a b"
    assert exhibit_prose.prose_surface("<p>up to\n45,000 units</p>") == (
        "up to 45,000 units"
    )

    # A "\n" surviving onto the surface therefore marks a RENDERED break. Both
    # block-boundary shapes from the guard test still produce it and still block.
    assert exhibit_prose.prose_surface("<p>x 45,000</p>\n<p>Million Air</p>") == (
        "x 45,000\nMillion Air"
    )


def test_newline_inside_pre_is_a_rendered_break_and_does_not_fuse():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # FOURTH round, sixth instance of the fabrication-wearing-a-valid-anchor class.
    # The previous round's newline fold made "a surface \n is a rendered break"
    # TRUE, but the design also assumed the CONVERSE — that every RENDERED break
    # becomes a surface "\n". That fails inside the render-significant-whitespace
    # family (`pre`/`xmp`/`listing`/`plaintext`/`textarea`), where the newline IS
    # the rendered break and there is no tag to mark it. Folding it to a space
    # made "<pre>45,000\nMillion Air deliveries</pre>" tokenize as
    # "45,000 Million" -> 4.5e10, with the substring anchor holding by
    # construction over a phrase the document never rendered as adjacent prose.
    import exhibit_prose

    # END-TO-END through the real pipeline (prose_surface -> locate_numbers), not
    # at the walker: `_normalize_whitespace` runs AFTER the walk and re-splits on
    # "\n", so a walker-level assertion alone would not prove the fix survives.
    prose = exhibit_prose.prose_surface(
        "<pre>45,000\nMillion Air deliveries</pre>"
    )
    assert prose == "45,000\nMillion Air deliveries", repr(prose)
    tokens = [c["token"] for c in exhibit_prose.locate_numbers(prose)]
    assert "45,000\nMillion" not in tokens, f"fused inside <pre>: {tokens!r}"
    assert tokens == ["45,000"], tokens

    # Anchors still hold over the preserved-newline surface.
    for cand in exhibit_prose.locate_numbers(prose):
        assert prose[cand["start"]:cand["end"]] == cand["token"]

    # A SECOND family member, to pin the family rather than the one tag. `listing`
    # is also not in `_BLOCK_TAGS` at origin, so this covers the boundary half too.
    prose2 = exhibit_prose.prose_surface(
        "<listing>1,576\nmillion reasons follow</listing>"
    )
    assert prose2 == "1,576\nmillion reasons follow", repr(prose2)
    assert [c["token"] for c in exhibit_prose.locate_numbers(prose2)] == ["1,576"]

    # `textarea` likewise — HTMLParser delivers its content through handle_data
    # (only script/style are CDATA elements), so it reaches the same fold.
    prose3 = exhibit_prose.prose_surface("<textarea>2\nbillion</textarea>")
    assert prose3 == "2\nbillion", repr(prose3)
    assert [c["token"] for c in exhibit_prose.locate_numbers(prose3)] == ["2"]

    # NESTING is depth-tracked, not boolean: text after an INNER close is still
    # inside the outer element, so its newlines are still rendered breaks.
    prose4 = exhibit_prose.prose_surface(
        "<pre>a<pre>b</pre>45,000\nMillion Air</pre>"
    )
    assert "45,000\nMillion Air" in prose4, repr(prose4)

    # And the element's OWN boundary is a break as well, so prose flanking a
    # family member cannot fuse across it either.
    prose5 = exhibit_prose.prose_surface("<p>x 45,000</p><listing>Million Air</listing>")
    assert prose5 == "x 45,000\nMillion Air", repr(prose5)
    assert [c["token"] for c in exhibit_prose.locate_numbers(prose5)] == ["45,000"]


def test_ordinary_block_newline_fold_survives_the_pre_family_exemption():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # The trade the pre-family fix must NOT undo: OUTSIDE the family, a hard
    # source-line wrap is still ordinary whitespace and still absorbs its
    # magnitude word (the META Family DAP case bought back last round).
    import exhibit_prose

    wrapped = exhibit_prose.prose_surface("<p>Family DAP was 3.56\nbillion.</p>")
    assert wrapped == "Family DAP was 3.56 billion."
    assert [c["token"] for c in exhibit_prose.locate_numbers(wrapped)] == [
        "3.56 billion"
    ]

    # A wrap AFTER a closed `<pre>` is outside it again — depth returned to zero.
    after = exhibit_prose.prose_surface("<pre>x</pre><p>grew to 3.56\nbillion</p>")
    assert after == "x\ngrew to 3.56 billion", repr(after)
