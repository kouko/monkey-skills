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
