"""RED-first tests for the prose KPI candidate producer (kpi_prose_candidates.py).

Task 4 (Part 1 walking skeleton) pins the ANTI-FABRICATION substring gate: a pure
predicate that a candidate's verbatim matched TOKEN and its verbatim_quote are
substrings of the canonical exhibit text. The NORMALIZED numeric value is DERIVED
from the token and is NEVER itself required to appear in the text — this is what
stops an LLM (or any layer) from committing a value not present in the source.

No `@req` tag: this dispatch's plan (docs/loom/plans/2026-07-19-8k-prose-kpi-
intake-part-1.md) binds tasks by "Brief item covered", not by registered
loom-spec REQ-ids (same convention as test_kpi_8k_candidates_propose.py), so
there is no id in the living-spec namespace to bind to.
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

import pytest

_TESTS_DIR = Path(__file__).resolve().parent
_SCRIPT = (
    _TESTS_DIR.parent
    / "skills"
    / "analysis-kpi"
    / "scripts"
    / "kpi_prose_candidates.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("kpi_prose_candidates", _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_gate_checks_token_rejects_invented():
    module = _load_module()

    # Canonical prose surface (the substring gate index). Note the printed token
    # carries thousands separators; the comma-stripped normalized value does NOT
    # appear anywhere in this text.
    canonical_text = (
        "The company had 1,576,000 full-time employees as of December 31, 2024."
    )

    # A candidate whose verbatim matched token IS present in the source.
    grounded = {
        "matched_token": "1,576,000",
        "verbatim_quote": "had 1,576,000 full-time employees",
        "value": 1576000,  # normalized (comma-stripped) — DERIVED, not verbatim
        "char_offset_span": [16, 25],
    }
    # A candidate whose token was invented — absent from the source text.
    invented = {
        "matched_token": "9,999,999",
        "verbatim_quote": "had 9,999,999 full-time employees",
        "value": 9999999,
        "char_offset_span": [16, 25],
    }

    # Precondition proving the gate cannot be leaning on the normalized value:
    # the comma-stripped "1576000" is genuinely NOT a substring of the source.
    assert str(grounded["value"]) not in canonical_text

    # Grounded token + quote are verbatim substrings -> gate admits it, EVEN
    # THOUGH the normalized numeric value is absent from the text.
    assert module.passes_substring_gate(grounded, canonical_text) is True

    # Invented token is absent from the source -> gate rejects it. This is the
    # load-bearing anti-fabrication rail.
    assert module.passes_substring_gate(invented, canonical_text) is False


_CANON = "The company had 1,576,000 full-time employees as of December 31, 2024."


def test_gate_rejects_missing_or_empty_matched_token():
    # Fail-CLOSED: a candidate with no verbatim token grounds NOTHING. Missing,
    # None, and "" all mean "no grounding" -> reject. The "" case is the fail-OPEN
    # hole (`"" in text` is always True) this pins shut; deleting the guard breaks
    # a test.
    module = _load_module()
    quote = "had 1,576,000 full-time employees"

    missing = {"verbatim_quote": quote}  # no matched_token key at all
    none_tok = {"matched_token": None, "verbatim_quote": quote}
    empty_tok = {"matched_token": "", "verbatim_quote": quote}

    assert module.passes_substring_gate(missing, _CANON) is False
    assert module.passes_substring_gate(none_tok, _CANON) is False
    assert module.passes_substring_gate(empty_tok, _CANON) is False


def test_gate_rejects_missing_or_empty_verbatim_quote():
    # Symmetric fail-CLOSED for the quote field. "" is the fail-OPEN case.
    module = _load_module()
    token = "1,576,000"

    missing = {"matched_token": token}  # no verbatim_quote key at all
    none_quote = {"matched_token": token, "verbatim_quote": None}
    empty_quote = {"matched_token": token, "verbatim_quote": ""}

    assert module.passes_substring_gate(missing, _CANON) is False
    assert module.passes_substring_gate(none_quote, _CANON) is False
    assert module.passes_substring_gate(empty_quote, _CANON) is False


def test_gate_requires_both_token_and_quote_present():
    # AND semantics: BOTH the token AND the quote must be substrings. Each partial
    # case (one present, the other a non-substring) must be rejected -> mutating
    # `and`->`or` at the return breaks this test.
    module = _load_module()

    # Token grounded, quote invented (absent from source).
    token_only = {
        "matched_token": "1,576,000",
        "verbatim_quote": "had 9,999,999 part-time contractors",
    }
    # Quote grounded, token invented (absent from source).
    quote_only = {
        "matched_token": "9,999,999",
        "verbatim_quote": "had 1,576,000 full-time employees",
    }

    assert module.passes_substring_gate(token_only, _CANON) is False
    assert module.passes_substring_gate(quote_only, _CANON) is False


def test_propose_emits_raw_candidate_needs_semantic():
    # Task 3 (Part 1 walking skeleton): the MECHANICAL producer. propose() turns
    # located number tokens (exhibit_prose.locate_numbers) into RAW candidate
    # points carrying ONLY mechanical fields — value DERIVED from the token,
    # verbatim_quote, char_offset_span — with every semantic slot NULL and
    # needs_semantic=True. The anti-fabrication contract: value + coordinates are
    # set mechanically here and NEVER pass through an LLM.
    module = _load_module()

    canonical_text = "The company had 1,576,000 employees as of year end."

    candidates = module.propose(canonical_text)

    # Single number token in the fixture -> exactly one candidate. Asserting the
    # total count (not just the matching subset) means a spurious extra candidate
    # cannot pass silently.
    assert len(candidates) == 1, "one number token -> one candidate"

    matches = [c for c in candidates if c["value"] == 1576000]
    assert len(matches) == 1, "exactly one candidate for the 1,576,000 token"
    candidate = matches[0]

    # Mechanical fields — all SET by propose, DERIVED from the located token.
    assert candidate["matched_token"] == "1,576,000"
    # value is the comma-stripped int, DERIVED from the token (not independently
    # supplied) — structural proof that value is never LLM-produced.
    assert candidate["value"] == 1576000
    assert candidate["value"] == int(candidate["matched_token"].replace(",", ""))
    # char_offset_span anchors back to the source: text[start:end] == token.
    start, end = candidate["char_offset_span"]
    assert canonical_text[start:end] == candidate["matched_token"]
    # CHANGED in Part 2 (T6). Part 1 pinned `verbatim_quote == matched_token` — a
    # walking-skeleton PLACEHOLDER, not an invariant: the spec requires the token
    # span PLUS a bounded context window. The permanent contract is asserted here
    # instead — the quote CONTAINS the token, is a literal substring of the
    # canonical text (contiguous, no elided middle), and fits the budget.
    quote = candidate["verbatim_quote"]
    assert candidate["matched_token"] in quote
    assert quote in canonical_text
    assert len(quote) <= module._MAX_VERBATIM_QUOTE_CHARS
    assert candidate["source_kind"] == "prose"

    # Semantic slots NULL, awaiting the LLM layer -> needs_semantic flagged.
    assert candidate["kpi_id"] is None
    assert candidate["unit"] is None
    assert candidate["period"] is None
    assert candidate["needs_semantic"] is True

    # The mechanically-produced candidate satisfies the EXISTING Task 4 gate:
    # its verbatim token + quote are literal substrings of the source. This ties
    # propose's output to the anti-fabrication rail.
    assert module.passes_substring_gate(candidate, canonical_text) is True


def test_period_label_not_a_candidate():
    # Task 3 (Part 2): a number functioning as a DATE / fiscal-period LABEL is not
    # a KPI value and must be filtered before the LLM/human layer. For the prose
    # "In the first quarter of fiscal 2026, deliveries rose 12%", the fiscal-year
    # token "2026" (a 4-digit year immediately preceded by the period word
    # "fiscal") is DROPPED, while the real KPI number "12" (from "12%") survives —
    # the filter is a targeted false-positive reducer, not general NLP: it does
    # NOT swallow ordinary prose numbers.
    #
    # No `@req` tag: this dispatch's plan binds tasks by "Brief item covered", not
    # a registered loom-spec REQ-id (same convention as the sibling tests above).
    module = _load_module()

    canonical_text = "In the first quarter of fiscal 2026, deliveries rose 12%"

    candidates = module.propose(canonical_text)
    values = [c["value"] for c in candidates]
    tokens = [c["matched_token"] for c in candidates]

    # The fiscal-year label is NOT emitted as a KPI value candidate.
    assert 2026 not in values, "the fiscal-year label 2026 must be filtered"
    assert "2026" not in tokens, "the fiscal-year token is not emitted"

    # The real KPI number (12 from "12%") is unaffected by the period filter, and
    # its surviving candidate keeps the mechanical value/token/offset fields.
    assert 12 in values, "an ordinary prose number is not filtered"
    kept = [c for c in candidates if c["matched_token"] == "12"]
    assert len(kept) == 1
    start, end = kept[0]["char_offset_span"]
    assert canonical_text[start:end] == "12", "surviving anchor is unchanged"


def test_bare_year_without_period_cue_survives():
    # Teeth for the "narrow, no over-reach" guarantee: a bare 4-digit year with NO
    # preceding period word is NOT a label and MUST survive as a candidate. The
    # preceding-word lookback is load-bearing — mutating _is_period_label to reject
    # EVERY 19xx/20xx year (dropping the lookback) breaks this test. Uses the pure
    # build_candidates seam (hermetic, no subprocess) with a candidate at offset 0
    # so its preceding text is empty (no period cue).
    module = _load_module()
    canonical_text = "2020 new stores opened across the region"
    candidates = module.build_candidates(
        [{"token": "2020", "start": 0, "end": 4}], canonical_text
    )
    assert [c["value"] for c in candidates] == [2020], (
        "a bare year with no period cue survives (preceding-word guard is load-bearing)"
    )


def test_bounding_qualifier_flagged():
    # Task 4 (Part 2): SEC prose routinely states a KPI as a BOUND, not an
    # equality — "up to 45,000 deliveries", "approximately 931 warehouses",
    # "more than 3 billion users". Committing those as bare point values would
    # silently convert an upper bound into a fact (a precision the source never
    # claimed), so the candidate must CARRY the qualifier for the human
    # confirming it and for any downstream memo.
    #
    # The qualifier is METADATA ABOUT the candidate, derived from the text
    # immediately preceding the token — it never mutates the verbatim token or
    # its offsets (the anti-fabrication anchor is untouched).
    #
    # No `@req` tag: this dispatch's plan binds tasks by "Brief item covered",
    # not a registered loom-spec REQ-id (same convention as the tests above).
    module = _load_module()

    canonical_text = "We expect deliveries of up to 45,000 vehicles this year"
    candidates = module.propose(canonical_text)
    bounded = [c for c in candidates if c["matched_token"] == "45,000"]
    assert len(bounded) == 1
    assert bounded[0]["value_qualifier"] == "up to", (
        "a bounded figure must carry its qualifier, not read as a bare equality"
    )
    # The anchor is untouched — the qualifier is metadata, not a token mutation.
    start, end = bounded[0]["char_offset_span"]
    assert canonical_text[start:end] == "45,000"
    assert module.passes_substring_gate(bounded[0], canonical_text) is True

    # A PLAIN figure carries no qualifier: the field is present-but-null (the
    # same present-but-null convention as unit_hint/period_hint), so a reader
    # cannot confuse "no bound stated" with "field missing".
    plain = module.build_candidates(
        [{"token": "45,000", "start": 0, "end": 6}], "45,000 vehicles delivered"
    )
    assert plain[0]["value_qualifier"] is None, "a plain figure states an equality"

    # The qualifier vocabulary, case-insensitively, via the pure seam.
    for prefix, expected in (
        ("up to ", "up to"),
        ("Approximately ", "approximately"),
        ("~", "~"),
        ("over ", "over"),
        ("At least ", "at least"),
        ("more than ", "more than"),
    ):
        text = f"{prefix}931 warehouses"
        located = [{"token": "931", "start": len(prefix), "end": len(prefix) + 3}]
        got = module.build_candidates(located, text)
        assert got[0]["value_qualifier"] == expected, f"{prefix!r} is a bound"


def test_bounding_qualifier_survives_to_committed_point(tmp_path, monkeypatch):
    # The bound must survive onto the COMMITTED provenance, not merely live on
    # the in-memory candidate: a bound visible at confirm time but LOST at store
    # time is exactly the failure this task exists to close (the store would then
    # hold "45,000 deliveries" as a fact the filing never asserted).
    #
    # `value_qualifier` is NOT one of kpi_store's required provenance fields, so
    # a null on a plain figure cannot trip the store's falsy-provenance guard —
    # it rides along like source_document/filing_date do.
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))
    scripts_dir = str(_SCRIPT.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    sys.modules.pop("kpi_store", None)
    import kpi_store  # noqa: E402

    module = _load_module()
    candidate = {
        "matched_token": "45,000",
        "verbatim_quote": "up to 45,000 vehicles",
        "value": 45000,
        "value_qualifier": "up to",
        "char_offset_span": [24, 30],
        "source_kind": "prose",
        "kpi_id": "vehicle_deliveries",
        "unit": "count",
        "period": "2024-12-31",
        "needs_semantic": False,
        "source_accession": "0001318605-24-000123",
        "source_document": "8-K/EX-99.1",
        "filing_date": "2024-10-31",
        "as_of": "2024-01-01",
    }
    summary = module.commit_to_store(
        [candidate], company="TSLA",
        confirmer="kouko", confirmed_at="2026-07-20T10:00:00Z", confirmed=True,
    )
    assert summary["committed"] == 1

    point = kpi_store.query_latest("TSLA", "vehicle_deliveries", "2024-12-31")
    assert point["value_qualifier"] == "up to", (
        "the bound must be visible on the stored point, not lost at commit"
    )
    assert point["value"] == 45000, "the derived value itself is unchanged"

    # A plain (unbounded) figure commits with a null qualifier and is NOT
    # rejected by the store's provenance guard.
    plain = dict(candidate, kpi_id="vehicles_produced", value_qualifier=None)
    assert module.commit_to_store(
        [plain], company="TSLA",
        confirmer="kouko", confirmed_at="2026-07-20T10:00:00Z", confirmed=True,
    )["committed"] == 1
    stored = kpi_store.query_latest("TSLA", "vehicles_produced", "2024-12-31")
    assert stored["value_qualifier"] is None


def test_normalize_value_decimal_token_becomes_float():
    # Coverage for the DECIMAL branch of _normalize_value (the integer branch is
    # exercised by the propose/gate tests; the float branch was untested). A
    # decimal token like "3.56" normalizes to the float 3.56 — the comma-stripped
    # value is DERIVED from the token, and a decimal has no thousands separators
    # to strip, so value and token share the same digits but different types.
    module = _load_module()

    assert module._normalize_value("3.56") == 3.56
    assert isinstance(module._normalize_value("3.56"), float)
    # A thousands-separated decimal: commas stripped, then parsed as float.
    assert module._normalize_value("1,234.5") == 1234.5
    assert isinstance(module._normalize_value("1,234.5"), float)
    # The integer branch stays int (not float) — no spurious "." introduced.
    assert module._normalize_value("1,576,000") == 1576000
    assert isinstance(module._normalize_value("1,576,000"), int)


def test_normalize_value_word_scale():
    # Task 2 (Part 2): a token carrying a MAGNITUDE word gets the multiplier
    # applied. Task 1 made the locator absorb the word into the token/span
    # ("3.56 billion" is ONE token), so this is where the numeric value is
    # DERIVED from it. Without the multiplier META's "Family DAP 3.56 billion"
    # commits as 3.56 — off by 1e9. Traced by "Brief item covered" in the plan,
    # not a registered loom-spec REQ-id (same convention as the tests above).
    module = _load_module()

    # Exact integers, not lossy floats. (These particular magnitudes DO compute
    # exactly in binary float — the reason for Decimal is the absent guarantee,
    # not this case; see _normalize_value's docstring.)
    assert module._normalize_value("3.56 billion") == 3560000000
    assert isinstance(module._normalize_value("3.56 billion"), int)
    assert module._normalize_value("500 million") == 500000000
    assert module._normalize_value("1.2 trillion") == 1200000000000
    assert module._normalize_value("40 thousand") == 40000
    # Case-insensitive, matching the locator's re.IGNORECASE token shape.
    assert module._normalize_value("3.56 BILLION") == 3560000000
    # Thousands separators still stripped when a magnitude word follows.
    assert module._normalize_value("1,250 million") == 1250000000
    # A sub-integer scaled result stays a float rather than being truncated.
    assert module._normalize_value("1.5 thousand") == 1500
    assert module._normalize_value("0.0015 thousand") == 1.5

    # PLAIN tokens are UNCHANGED — the multiplier applies only when a magnitude
    # word is present (mutating the parser to always scale breaks these).
    assert module._normalize_value("931") == 931
    assert isinstance(module._normalize_value("931"), int)
    assert module._normalize_value("1,576,000") == 1576000
    assert module._normalize_value("3.56") == 3.56


def test_phrasal_verb_over_is_not_a_bound():
    # "over" doubles as the tail of a common business phrasal verb. "turned over
    # 931 units" states NO bound — tagging it as one fabricates imprecision the
    # filing never claimed, which is the same fabrication this feature exists to
    # refuse, merely inverted. A genuine bounding "over" must still be detected,
    # so this pins both directions; deleting the phrasal-head guard breaks the
    # first half, deleting "over" from the vocabulary breaks the second.
    module = _load_module()

    for phrase in (
        "the warehouse turned over 931 units",
        "the fleet handed over 931 vehicles",
        "management took over 931 stores",
        "inventory was carried over 931 times",
    ):
        start = phrase.index("931")
        assert module._detect_qualifier(start, phrase) is None, phrase

    # A genuine bound is still detected — the guard is narrow, not a blanket
    # removal of "over".
    bounded = "the company operated over 931 warehouses"
    assert module._detect_qualifier(bounded.index("931"), bounded) == "over"

    # Word-boundary guard still holds for the no-space cases.
    turnover = "annual turnover 931 units"
    assert module._detect_qualifier(turnover.index("931"), turnover) is None


def test_magnitude_word_tables_stay_in_lockstep():
    # Cross-file DRIFT guard. The locator (data-markets/exhibit_prose.py) decides
    # which magnitude words get absorbed into a token; this module (analysis-kpi)
    # decides what each one multiplies by. Production crosses that boundary by
    # SUBPROCESS, so neither file can import the other and no runtime check is
    # possible — but a test can load both directly and pin them together.
    #
    # The drift direction that matters is silent: drop a word from the locator
    # while it survives in the multiplier table, and "3.56 billion" tokenizes as
    # plain "3.56", finds no magnitude suffix, and commits UNSCALED — a byte-for-
    # byte resurrection of the META bug this task exists to kill, with no crash
    # and a still-valid-looking verbatim anchor.
    module = _load_module()

    markets_scripts = _TESTS_DIR.parent / "skills" / "data-markets" / "scripts"
    spec = importlib.util.spec_from_file_location(
        "exhibit_prose", markets_scripts / "exhibit_prose.py"
    )
    exhibit_prose = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exhibit_prose)

    assert set(module._MAGNITUDE_MULTIPLIERS) == set(exhibit_prose._MAGNITUDE_WORDS), (
        "locator magnitude words and multiplier table drifted apart — a word the "
        "locator absorbs but this table lacks (or vice versa) silently drops the "
        "multiplier and commits an unscaled KPI value"
    )


def test_commit_requires_confirm():
    # Task 6 (Part 1 walking skeleton): the tier-① trust GATE. A prose candidate
    # is accepted for commit ONLY after an explicit human confirm-all. There is NO
    # auto-commit: confirmed defaults False (fail-CLOSED). Moving a candidate
    # located->committed WITHOUT the human confirm step is ILLEGAL and refused —
    # that is the three-layer boundary (mechanical produce -> LLM propose -> HUMAN
    # confirm) keeping unratified candidates out of the store.
    #
    # Scope: THIS pins the GATE (which candidates MAY commit), not the kpi_store
    # append (Task 7). commit() returns the accepted-for-commit set.
    module = _load_module()

    candidates = [
        {
            "matched_token": "1,576,000",
            "verbatim_quote": "had 1,576,000 full-time employees",
            "value": 1576000,
            "char_offset_span": [16, 25],
            "source_kind": "prose",
            "kpi_id": "employees_full_time",  # LLM-labeled + human-confirmed
            "unit": "count",
            "period": "2024-12-31",
            "needs_semantic": False,
        }
    ]

    # confirmed=False -> NO committed points (nothing accepted for append). The
    # fail-CLOSED, no-auto-commit direction.
    assert module.commit(candidates, confirmed=False) == []

    # confirmed OMITTED -> same refusal. The default must be fail-CLOSED, so a
    # bypass that just calls the accept path without the confirm arg commits
    # nothing (bypass illegal).
    assert module.commit(candidates) == []

    # confirmed=True -> the candidates are accepted for commit. This is the ONLY
    # path a candidate reaches "committed" — through the explicit human confirm.
    accepted = module.commit(candidates, confirmed=True)
    assert accepted == candidates


def test_commit_no_taxonomy_filter_admits_confirmed_candidate():
    # Interim no-taxonomy filter: a human-confirmed candidate is accepted for
    # commit REGARDLESS of its kpi_id — there is NO fixed-taxonomy check gating
    # commit (taxonomy is a deferred hardening). An arbitrary/plausible LLM-labeled
    # kpi_id, absent from any fixed taxonomy, still commits once the human
    # confirmed. The confirm step is the only gate; taxonomy membership is not.
    module = _load_module()

    plausible = [
        {
            "matched_token": "42",
            "verbatim_quote": "shipped 42 gigawatts",
            "value": 42,
            "char_offset_span": [8, 10],
            "source_kind": "prose",
            "kpi_id": "energy_shipped_gw_not_in_any_taxonomy",  # arbitrary id
            "unit": "GW",
            "period": "2024-Q4",
            "needs_semantic": False,
        }
    ]

    accepted = module.commit(plausible, confirmed=True)
    assert accepted == plausible, "no taxonomy check gates a confirmed candidate"


def test_build_candidates_preserves_decimal_matched_token():
    # The pure transform seam (build_candidates) wraps already-crossed located
    # numbers into candidates. A decimal token flows through as a float `value`
    # while `matched_token` stays the VERBATIM printed token "3.56" (the value is
    # NOT required to appear as a substring of the token — 3.56 the float and
    # "3.56" the token happen to share digits, but the contract is verbatim
    # token in / derived value out).
    module = _load_module()

    located = [{"token": "3.56", "start": 4, "end": 8}]
    candidates = module.build_candidates(located)

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate["matched_token"] == "3.56"
    assert candidate["verbatim_quote"] == "3.56"
    assert candidate["value"] == 3.56
    assert isinstance(candidate["value"], float)
    assert candidate["char_offset_span"] == [4, 8]
    assert candidate["source_kind"] == "prose"
    assert candidate["needs_semantic"] is True


def test_zero_value_survives_gate_and_commit(tmp_path, monkeypatch):
    # Task 5 (falsy-zero pin): a prose KPI whose value is exactly 0 ("net
    # additions were 0 in the quarter") must be LOCATED, PASS the substring gate,
    # and remain eligible to COMMIT + STORE — 0 must NOT be read as "no value" and
    # silently dropped. This is the repo's known falsy-zero trap
    # (docs/loom/memory/falsy-guard-rejects-legitimate-zero-provenance.md): a
    # `if not value` / `if not candidate["value"]` guard ANYWHERE on the numeric
    # value path would drop a legitimate 0. By inspection no such guard exists
    # today, so this is a GREEN-on-arrival REGRESSION GUARD, not RED-then-GREEN:
    # it fails the moment a falsy-value guard is introduced on any of the seams
    # below (produce / gate / commit / store).
    #
    # NOTE the guard-DISCRIMINATION: the string grounding fields (matched_token /
    # verbatim_quote) DO legitimately fail-CLOSED on falsy (empty ""); this test
    # pins only that the NUMERIC value is exempt from that treatment — a 0 value
    # with a grounded token "0" flows end-to-end.
    module = _load_module()

    # "0" is a genuine substring of this canonical prose surface (offset 19).
    canonical_text = "Net additions were 0 in the quarter, flat versus prior year."
    assert canonical_text[19:20] == "0"

    # --- PRODUCE seam: _normalize_value("0") -> int 0, build_candidates keeps it.
    # A `if not value` guard added here (skipping the candidate) would empty the
    # list and fail len == 1.
    produced = module.build_candidates([{"token": "0", "start": 19, "end": 20}])
    assert len(produced) == 1, "the 0-token located number -> exactly one candidate"
    zero_candidate = produced[0]
    assert zero_candidate["value"] == 0
    assert zero_candidate["value"] is not None, "0 is a value, not absence"
    assert zero_candidate["matched_token"] == "0"

    # --- GATE seam: token "0" is a substring -> gate admits it. The gate must NOT
    # read the falsy numeric value; a `if not candidate["value"]: return False`
    # added to passes_substring_gate would wrongly reject and fail this assert.
    assert module.passes_substring_gate(zero_candidate, canonical_text) is True

    # A CONFIRMED value-0 candidate (human filled the semantic slots + filing
    # attribution) to exercise the commit + store seams end-to-end.
    confirmed = {
        "matched_token": "0",
        "verbatim_quote": "Net additions were 0 in the quarter",
        "value": 0,
        "char_offset_span": [19, 20],
        "source_kind": "prose",
        "kpi_id": "net_additions",  # LLM-labeled + human-confirmed
        "unit": "count",
        "period": "2024-Q4",
        "needs_semantic": False,
        "source_accession": "0000320193-24-000999",
        "source_document": "8-K/EX-99.1",
        "filing_date": "2024-10-31",
        "as_of": "2024-10-31",  # accession-derived (NOT wall-clock)
    }

    # --- COMMIT-GATE seam: a confirmed value-0 candidate is ACCEPTED, not filtered.
    # A `if not c["value"]: continue` added to commit would drop it -> accepted []
    # and this assert fails.
    accepted = module.commit([confirmed], confirmed=True)
    assert accepted == [confirmed], "the value-0 candidate is accepted for commit"

    # --- STORE-APPEND seam: the value-0 point LANDS in the durable store, not
    # skipped. Hermetic: KPI_STORE_DIR -> tmp_path (mirrors T7) so the real store
    # is never touched.
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))
    scripts_dir = str(_SCRIPT.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    sys.modules.pop("kpi_store", None)
    import kpi_store  # noqa: E402

    summary = module.commit_to_store(
        [confirmed], company="AAPL",
        confirmer="kouko", confirmed_at="2026-07-20T10:00:00Z", confirmed=True,
    )
    assert summary["committed"] == 1, "the value-0 confirmed candidate is appended"

    point = kpi_store.query_latest("AAPL", "net_additions", "2024-Q4")
    assert point is not None, "the value-0 prose point must be in the store, not dropped"
    # The load-bearing assert: the stored value is exactly 0 (not None, not absent).
    # A falsy-value guard on _prose_candidate_to_point / commit_to_store would drop
    # the point (query None) or lose the value here.
    assert point["value"] == 0
    assert point["value"] is not None
    assert point["source_cell_ref"] == "prose:19-20"


def test_empty_and_multi_exhibit_gaps():
    # Task 8 (Part 1 walking skeleton): the anti-fabrication HONESTY rail on the
    # negative paths. Loud gaps, never silent wrong answers.
    #
    # (a) EMPTY-SUCCESS: exactly one exhibit whose prose carries no number token ->
    #     the producer SCANS it, finds nothing, and returns an EXPLICIT empty result
    #     ("0 prose candidates"). gap is None (a successful scan is NOT an error and
    #     NOT a gap), so empty-success is distinguishable from a real gap.
    # (b) MULTI-EXHIBIT GAP: a filing carrying >=2 EX-99 exhibits -> a LOUD
    #     multi_exhibit gap marker and ZERO extraction (inherits Route B's
    #     LOOM-SIMPLIFY >=2-exhibit ceiling — never silently pick one exhibit). The
    #     gap path does NOT scan (no fabrication, no arbitrary pick).
    #
    # No `@req` tag: same as the sibling tests above — this dispatch's plan binds
    # by "Brief item covered", not a registered loom-spec REQ-id.
    module = _load_module()

    # (a) One exhibit, no digits in its prose -> scanned clean -> empty-success.
    no_kpi = "The company reported strong results."
    empty = module.intake([no_kpi])
    assert empty["candidates"] == [], "no number token -> zero candidates"
    assert empty["gap"] is None, "an empty scan is success, not a gap"
    assert empty["note"] == "0 prose candidates", "the explicit 0-found signal"

    # (b) Two EX-99 exhibits (both DO contain numbers) -> ambiguous which to source,
    # so a loud gap and NOTHING extracted. The presence of extractable numbers in
    # the exhibits makes the extract-nothing behaviour load-bearing: the gap must
    # win over any silent pick.
    two_exhibits = [
        "The company had 1,576,000 full-time employees.",
        "The subsidiary shipped 42 units in the quarter.",
    ]
    gap = module.intake(two_exhibits)
    assert gap["candidates"] == [], "a >=2-exhibit filing extracts NOTHING"
    assert gap["gap"] == "multi_exhibit", "the loud >=2-exhibit gap marker"
    assert gap["gap"] is not None
    # Loud/explicit: the note names the exhibit count so the gap is not silent.
    assert "2" in gap["note"]
    # The gap is DISTINGUISHABLE from the empty-but-scanned case.
    assert gap["gap"] != empty["gap"]


def test_intake_empty_list_is_hermetic_empty_success():
    # Task 8 boundary: an EMPTY exhibit list has nothing to scan and must return
    # the empty-success envelope directly — WITHOUT spawning the exhibit_prose
    # subprocess on "" (so it can never surface as a subprocess RuntimeError,
    # which would contradict the honest empty-success promise). This pins the
    # `if not exhibits: return _scanned_result([])` short-circuit; it is hermetic
    # (no subprocess) by construction.
    module = _load_module()
    result = module.intake([])
    assert result["candidates"] == [], "no exhibit -> zero candidates"
    assert result["gap"] is None, "empty list is success, not a gap"
    assert result["note"] == "0 prose candidates", "the explicit 0-found signal"


def test_committed_prose_point_carries_anchor_and_attribution(tmp_path, monkeypatch):
    # Task 7 (Part 1 walking skeleton): the durable store-append path. This closes
    # the three-layer skeleton — mechanical produce (T3) -> LLM propose -> HUMAN
    # confirm (T6) -> DURABLE store append (here). A confirmed prose candidate,
    # committed with an explicit confirmer + confirm timestamp, becomes a
    # schema-valid point in the EXISTING tier-① kpi_store, appended through the
    # UNMODIFIED kpi_store.append (its provenance / accession-derived-as_of guards
    # are honored, never weakened). Queried back, the point must carry:
    #   - source_kind="prose"
    #   - a "prose:{start}-{end}" offset anchor (source_cell_ref-analog) built from
    #     the candidate's char_offset_span — a truthy string, so the store's
    #     falsy-provenance guard admits it (unlike a bare 0)
    #   - the verbatim_quote (so the surfaced number stays citable to source bytes)
    #   - filing attribution (accession / document / filing_date) + confirmer
    #     identity + confirm timestamp
    #   - an as_of that is the ACCESSION-derived filing date, DISTINCT from the
    #     wall-clock confirm timestamp (determinism: both passed IN, never read
    #     from the clock inside the function).
    #
    # Hermetic: KPI_STORE_DIR is redirected to tmp_path (mirrors
    # test_prose_memo_boundary.py) so nothing touches the real durable store.
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    # Share the SAME kpi_store module the producer's lazy sibling-import resolves:
    # put the scripts dir on sys.path and import kpi_store under its real name
    # (mirrors test_prose_memo_boundary._load_modules), so the query-back below
    # reads the very file the append wrote.
    scripts_dir = str(_SCRIPT.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    sys.modules.pop("kpi_store", None)
    import kpi_store  # noqa: E402

    module = _load_module()

    # A CONFIRMED prose candidate: the human filled the semantic slots
    # (kpi_id/unit/period) at confirm, atop the mechanical fields (verbatim token +
    # quote + char_offset_span + value) and the filing attribution + accession-
    # derived as_of carried from the filing fetch.
    candidate = {
        "matched_token": "1,576,000",
        "verbatim_quote": "had 1,576,000 full-time employees",
        "value": 1576000,
        "char_offset_span": [16, 25],
        "source_kind": "prose",
        "kpi_id": "employees_full_time",  # LLM-labeled + human-confirmed
        "unit": "count",
        "period": "2024-12-31",
        "needs_semantic": False,
        "source_accession": "0000320193-24-000999",
        "source_document": "8-K/EX-99.1",
        "filing_date": "2024-10-31",
        "as_of": "2024-01-01",  # accession-derived (NOT wall-clock)
    }

    confirmer = "kouko"
    confirmed_at = "2026-07-20T10:00:00Z"  # wall-clock confirm ts, passed IN

    summary = module.commit_to_store(
        [candidate], company="AAPL",
        confirmer=confirmer, confirmed_at=confirmed_at, confirmed=True,
    )
    assert summary["committed"] == 1, "the one confirmed candidate is appended"

    point = kpi_store.query_latest("AAPL", "employees_full_time", "2024-12-31")
    assert point is not None, "the confirmed prose candidate must be in the store"

    # Prose source marker + the offset anchor (source_cell_ref-analog).
    assert point["source_kind"] == "prose"
    assert point["source_cell_ref"] == "prose:16-25", (
        "the anchor is prose:{start}-{end} from char_offset_span [16, 25]"
    )

    # The verbatim quote is carried so a surfaced number stays citable.
    assert point["verbatim_quote"] == "had 1,576,000 full-time employees"
    assert point["value"] == 1576000

    # Filing attribution.
    assert point["source_accession"] == "0000320193-24-000999"
    assert point["source_document"] == "8-K/EX-99.1"
    assert point["filing_date"] == "2024-10-31"

    # Confirmer identity + confirm timestamp.
    assert point["confirmer"] == confirmer
    assert point["confirmed_at"] == confirmed_at

    # as_of is the ACCESSION-derived filing date, DISTINCT from the confirm ts —
    # the store's non-wall-clock as_of guard is honored.
    assert point["as_of"] == "2024-01-01"
    assert point["as_of"] != confirmed_at

    # Fail-CLOSED: without the explicit confirm, nothing is appended (no bypass).
    other = dict(candidate, kpi_id="employees_part_time")
    unconfirmed = module.commit_to_store(
        [other], company="AAPL",
        confirmer=confirmer, confirmed_at=confirmed_at,  # confirmed omitted
    )
    assert unconfirmed["committed"] == 0
    assert kpi_store.query_latest("AAPL", "employees_part_time", "2024-12-31") is None


def test_bounded_context_window(tmp_path, monkeypatch):
    # Task 6 (Part 2): PII containment. SEC prose sits next to executive names and
    # compensation figures, so the COMMITTED provenance must store the verbatim
    # token span plus a BOUNDED context window — enough for a human to see the
    # number in its clause — and NOT the whole surrounding paragraph. An
    # over-broad quote handed down from an upstream layer is trimmed at the store
    # boundary; the trimmed window stays a LITERAL substring of the canonical text
    # (no elided middle), so the anti-fabrication substring gate still holds, and
    # char_offset_span keeps pointing at the token's TRUE canonical position (it
    # is never re-based onto the window).
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    scripts_dir = str(_SCRIPT.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    sys.modules.pop("kpi_store", None)
    import kpi_store  # noqa: E402

    module = _load_module()

    # A KPI sentence embedded in a paragraph that ALSO names executives and their
    # compensation — exactly the incidental personal data a durable operating-KPI
    # store must not accumulate.
    paragraph = (
        "On October 31, 2024, the Board of Directors approved a special retention "
        "award of $4,250,000 to Jane Q. Ramirez, our Executive Vice President and "
        "Chief Operating Officer, in recognition of her service during the fiscal "
        "year. Separately, the Company reported that it had 1,576,000 full-time "
        "employees as of the end of the fiscal fourth quarter, an increase over "
        "the prior year. The Board also noted that Marcus T. Delgado received a "
        "cash bonus of $1,875,000 under the annual incentive plan."
    )
    token = "1,576,000"
    start = paragraph.index(token)

    candidate = {
        "matched_token": token,
        "verbatim_quote": paragraph,  # over-broad: the WHOLE paragraph
        "value": 1576000,
        "char_offset_span": [start, start + len(token)],
        "source_kind": "prose",
        "kpi_id": "employees_full_time",
        "unit": "count",
        "period": "2024-12-31",
        "needs_semantic": False,
        "source_accession": "0000320193-24-000999",
        "source_document": "8-K/EX-99.1",
        "filing_date": "2024-10-31",
        "as_of": "2024-01-01",
    }

    summary = module.commit_to_store(
        [candidate], company="AAPL",
        confirmer="kouko", confirmed_at="2026-07-20T10:00:00Z", confirmed=True,
    )
    assert summary["committed"] == 1

    point = kpi_store.query_latest("AAPL", "employees_full_time", "2024-12-31")
    assert point is not None
    stored = point["verbatim_quote"]

    # BOUNDED: within the fixed char budget, and materially shorter than the
    # paragraph it was cut from.
    assert len(stored) <= 160, "the stored quote must fit the fixed char budget"
    assert len(stored) < len(paragraph)

    # The personal data that merely NEIGHBORED the KPI never reaches the store.
    for personal in ("Jane Q. Ramirez", "$4,250,000",
                     "Marcus T. Delgado", "$1,875,000"):
        assert personal not in stored, f"{personal!r} must not be committed"

    # Still verifiable: the window carries the number, and remains a LITERAL
    # substring of the canonical text, so the anti-fabrication gate still passes.
    assert token in stored
    assert stored in paragraph, "the window must not be built by eliding a middle"
    assert module.passes_substring_gate(
        {"matched_token": token, "verbatim_quote": stored}, paragraph
    )

    # The offset anchor still points at the token's TRUE position in the canonical
    # text — bounding the quote must not re-base the offsets onto the window.
    assert point["source_cell_ref"] == f"prose:{start}-{start + len(token)}"
    assert paragraph[start:start + len(token)] == token


def test_propose_emits_windowed_context_quote():
    # Task 6 (Part 2), the PRODUCING half. The spec requires the committed
    # provenance to store the minimal verbatim token span PLUS a bounded
    # surrounding context window. A bare-token quote satisfies "not the whole
    # paragraph" trivially while failing the other half — it carries NO context,
    # so a human confirmer cannot read the number against its subject and unit.
    # So the producer itself must emit a WINDOW: the token plus surrounding text
    # sliced CONTIGUOUSLY out of the canonical text, within the same one budget
    # the commit-boundary clamp enforces.
    module = _load_module()

    canonical_text = (
        "On October 31, 2024, the Board approved a special retention award of "
        "$4,250,000 to Jane Q. Ramirez, our Executive Vice President and Chief "
        "Operating Officer, in recognition of her service. Separately, the "
        "Company reported that it had 1,576,000 full-time employees as of the "
        "end of the fourth quarter, an increase over the prior year. The Board "
        "also noted that Marcus T. Delgado received a cash bonus of $1,875,000 "
        "under the annual incentive plan."
    )
    token = "1,576,000"
    start = canonical_text.index(token)

    matches = [c for c in module.propose(canonical_text)
               if c["matched_token"] == token]
    assert len(matches) == 1
    candidate = matches[0]
    quote = candidate["verbatim_quote"]

    # A WINDOW, not the bare token: it carries real surrounding context.
    assert quote != token, "the quote must be a context window, not the bare token"
    assert token in quote
    assert len(quote) > len(token)

    # Bounded by the SAME budget as the commit-boundary clamp — one constant.
    assert len(quote) <= module._MAX_VERBATIM_QUOTE_CHARS
    assert len(quote) < len(canonical_text)

    # CONTIGUOUS slice of the canonical text, so it stays a literal substring and
    # the anti-fabrication gate keeps holding end-to-end.
    assert quote in canonical_text, "never concatenate across an elision"
    assert module.passes_substring_gate(candidate, canonical_text) is True

    # Distant personal data stays out — that is what BOUNDING buys.
    for personal in ("Jane Q. Ramirez", "$4,250,000",
                     "Marcus T. Delgado", "$1,875,000"):
        assert personal not in quote, f"{personal!r} must not be captured"

    # The offset anchor still points at the TOKEN's true canonical position —
    # never at the window's start.
    assert candidate["char_offset_span"] == [start, start + len(token)]
    assert canonical_text[start:start + len(token)] == token


def test_build_candidates_without_canonical_text_keeps_bare_token_quote():
    # The pure-seam contract is unchanged: `canonical_text` stays OPTIONAL, and
    # without it there is no text to slice a window out of. The producer must
    # degrade to the bare token rather than crash — the seam tests that exercise
    # build_candidates in isolation call it exactly this way.
    module = _load_module()

    candidates = module.build_candidates([{"token": "931", "start": 4, "end": 7}])

    assert len(candidates) == 1
    assert candidates[0]["verbatim_quote"] == "931"
    assert candidates[0]["matched_token"] == "931"


def test_context_window_uses_its_full_budget_near_the_right_edge():
    # Budget under-use. The window start is computed by centring the token, but a
    # token sitting near the RIGHT edge of the text makes the symmetric window run
    # past the end, and the overshoot is simply truncated — spending well under
    # budget and discarding usable LEFT-side context for no reason. The window
    # must re-slide LEFT to reclaim that space whenever the text allows, so a
    # confirmer reading a trailing figure still gets a full clause of context.
    module = _load_module()
    budget = module._MAX_VERBATIM_QUOTE_CHARS

    token = "1,576,000"
    # Plenty of text to the LEFT, almost none to the RIGHT.
    canonical_text = "context " * 40 + f"had {token} employees."
    start = canonical_text.index(token)

    quote = module._context_window(start, start + len(token), canonical_text)

    assert len(quote) == budget, "the window must spend its full budget"
    assert token in quote
    assert quote in canonical_text


def test_bounded_quote_refuses_an_over_long_quote_missing_its_token(
    tmp_path, monkeypatch
):
    # Fail-loud on the DURABLE-store path. An over-budget quote that does not
    # contain its own matched_token is malformed: trimming it would have to guess
    # which end to cut, and guessing wrong silently drops the very number being
    # committed. It raises instead — and because the raise happens before the
    # store append, nothing is written.
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    scripts_dir = str(_SCRIPT.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    sys.modules.pop("kpi_store", None)
    import kpi_store  # noqa: E402

    module = _load_module()

    token = "1,576,000"
    malformed = "filler text that never states the number. " * 6  # > budget, no token
    assert len(malformed) > module._MAX_VERBATIM_QUOTE_CHARS
    assert token not in malformed

    with pytest.raises(ValueError, match="does not contain its matched_token"):
        module._bounded_quote(malformed, token)

    candidate = {
        "matched_token": token,
        "verbatim_quote": malformed,
        "value": 1576000,
        "char_offset_span": [10, 19],
        "source_kind": "prose",
        "kpi_id": "employees_full_time",
        "unit": "count",
        "period": "2024-12-31",
        "needs_semantic": False,
        "source_accession": "0000320193-24-000999",
        "as_of": "2024-01-01",
    }
    with pytest.raises(ValueError, match="does not contain its matched_token"):
        module.commit_to_store(
            [candidate], company="AAPL",
            confirmer="kouko", confirmed_at="2026-07-20T10:00:00Z", confirmed=True,
        )
    # Fail-CLOSED: the malformed point never reached the durable store.
    assert kpi_store.query_latest("AAPL", "employees_full_time", "2024-12-31") is None


def test_bounded_quote_degrades_to_the_bare_token_when_token_exceeds_budget():
    # The other unexercised commit-path branch. A single located token longer than
    # the WHOLE budget leaves no room for context, so the quote degrades to just
    # the token: still fully grounded (a literal substring of the source), simply
    # with no context to spare. It must NOT be cut mid-token — a truncated number
    # would be a DIFFERENT number, the exact fabrication this rail prevents.
    module = _load_module()
    budget = module._MAX_VERBATIM_QUOTE_CHARS

    token = "1" + ",000" * ((budget // 4) + 2)  # comma-grouped, longer than budget
    assert len(token) > budget
    quote = f"reported {token} units in the period, a record."

    assert module._bounded_quote(quote, token) == token


def test_magnitude_absorption_does_not_reopen_the_period_label_filter():
    # WHOLE-BRANCH review finding 1 — the CROSS-LAYER interaction the per-task
    # tests structurally could not see. Task 1 (locator) changed what a token IS
    # by absorbing a trailing magnitude word; Task 3's `_is_period_label` gates on
    # `_YEAR_RE.fullmatch(token)`. Composed, a year followed by a magnitude word
    # ("fiscal 2026 billion-dollar...") no longer fullmatches, the period filter
    # never fires, and the LABEL commits as a KPI value scaled by 1e9 — a number
    # whose source anchor holds LITERALLY while being semantically meaningless.
    # Each layer's own tests pass; only their composition fails, so this test
    # exercises BOTH through `propose`.
    #
    # No `@req` tag: this dispatch's plan binds tasks by "Brief item covered", not
    # a registered loom-spec REQ-id (same convention as the sibling tests above).
    module = _load_module()

    for prose, fabricated in (
        ("Our fiscal 2026 billion-dollar cost program expanded.", 2026000000000),
        ("In Q1 2026 million-unit shipments accelerated.", 2026000000),
    ):
        candidates = module.propose(prose)
        values = [c["value"] for c in candidates]
        tokens = [c["matched_token"] for c in candidates]
        assert fabricated not in values, f"period label committed as value: {candidates!r}"
        assert 2026 not in values, f"period label committed as value: {tokens!r}"
        assert not any("2026" in t for t in tokens), tokens

    # Control (already correct before the fix): the same prose WITHOUT a magnitude
    # word is dropped by the period filter, proving the filter itself is intact.
    assert [c["matched_token"] for c in module.propose("Our fiscal 2026 cost program")] == []

    # DEFENSE IN DEPTH, layer (b) alone: even if a FUTURE locator change re-admits
    # a magnitude word onto a year token, `_is_period_label` must strip it before
    # the year test rather than fall open. Driven through the pure seam with a
    # synthetic located token, so it pins the filter independently of the locator.
    text = "Our fiscal 2026 billion-dollar cost program expanded."
    assert text[11:23] == "2026 billion"
    assert module.build_candidates([{"token": "2026 billion", "start": 11, "end": 23}], text) == []

    # ...and the narrowness guarantee still holds: a magnitude-bearing token whose
    # numeric part is NOT a bare year is a real KPI and must survive.
    kpi_text = "We shipped 450 million units in the period."
    survivors = module.build_candidates(
        [{"token": "450 million", "start": 11, "end": 22}], kpi_text
    )
    assert [c["value"] for c in survivors] == [450000000], survivors


def test_qualifier_is_not_detected_across_a_block_boundary():
    # SECOND whole-branch review, finding 3 — the METADATA side of the SAME root
    # cause as the locator's absorption separator: `_QUALIFIER_RE`'s trailing `\s*`
    # matches the `\n` that the prose walker inserts at every block boundary, so a
    # qualifier ending one block stamped the FIRST figure of the next block ("We
    # expect approximately</p><p>931 warehouses"), and it stamped across an EXCISED
    # TABLE too. That asserts imprecision the filing never stated about that figure
    # — the inversion this module's own `_PHRASAL_HEADS_BEFORE_OVER` comment names.
    #
    # No `@req` tag: this dispatch's plan binds tasks by "Brief item covered", not
    # a registered loom-spec REQ-id (same convention as the sibling tests above).
    module = _load_module()

    # The canonical surface renders `</p><p>` (and an excised <table>) as a bare
    # "\n" — written literally here so the test stays hermetic to this module.
    for canonical_text in (
        "We expect approximately\n931 warehouses",
        "We expect approximately\n931 warehouses to open",
    ):
        candidates = module.propose(canonical_text)
        assert [c["value"] for c in candidates] == [931], candidates
        assert candidates[0]["value_qualifier"] is None, (
            f"qualifier stamped across a block boundary: {candidates[0]!r}"
        )

    # TRUE POSITIVE preserved: same-line whitespace still detects the bound, and
    # so does an abutting tilde.
    same_line = module.propose("We expect approximately 931 warehouses")
    assert [c["value_qualifier"] for c in same_line] == ["approximately"], same_line
    assert module._detect_qualifier(len("We opened ~"), "We opened ~931 warehouses") == "~"

    # A qualifier at the START of its own line is still adjacent to ITS figure —
    # only the gap BETWEEN qualifier and figure may not cross the boundary.
    text = "Openings\nup to 45,000 deliveries"
    assert module._detect_qualifier(text.index("45,000"), text) == "up to"


def test_bare_quarter_tag_digit_is_not_a_kpi_value():
    # SECOND whole-branch review, finding 4. The locator emits the "3" of a "Q3"
    # quarter tag as a number token, and `_is_period_label` — whose own docstring
    # names "Q1 2026" as its target — only rejected 4-digit YEARS, so the bare
    # quarter digit committed as a KPI value of 3. Narrow by construction: only a
    # single digit 1-4 IMMEDIATELY preceded by "Q"/"q" (no intervening space) is a
    # quarter tag; ordinary single digits are untouched.
    #
    # No `@req` tag: this dispatch's plan binds tasks by "Brief item covered", not
    # a registered loom-spec REQ-id (same convention as the sibling tests above).
    module = _load_module()

    assert module.propose("Q3 deliveries were strong.") == [], (
        "the quarter tag digit is a period label, not a KPI value"
    )
    assert [c["value"] for c in module.propose("In Q1 2026 we opened 12 stores.")] == [12]

    # NARROWNESS: an ordinary single digit is NOT rejected, including one that
    # merely FOLLOWS a "Q" across a space, and a multi-digit number after a "Q".
    assert [c["value"] for c in module.propose("We opened 3 stores.")] == [3]
    assert [c["value"] for c in module.propose("Each Q 3 stores opened.")] == [3]
    assert [c["value"] for c in module.propose("Model Q7 sales were 45 units.")] == [7, 45]


def test_magnitude_decoder_refuses_a_newline_separated_token():
    # SECOND whole-branch review, ROOT-CAUSE audit (not one of the four findings).
    # `_MAGNITUDE_TOKEN_RE` is the DECODER of the locator's token shape, and it
    # separated number from magnitude word with `\s+` — which matches the block
    # separator "\n" just like the locator's own absorption did. It is the layer
    # that turned the fused "45,000\nMillion" into 4.5e10, so with only the locator
    # fixed this half still falls open the moment a future token-shape change
    # re-admits a newline. Same defense-in-depth stance `_is_period_label` already
    # takes for the same reason: BOTH layers are load-bearing.
    #
    # A malformed newline-bearing token now FAILS LOUD (the int() parse raises)
    # rather than silently returning a plausible-looking 1e9-scaled value.
    #
    # No `@req` tag: this dispatch's plan binds tasks by "Brief item covered", not
    # a registered loom-spec REQ-id (same convention as the sibling tests above).
    module = _load_module()

    with pytest.raises(ValueError):
        module._normalize_value("45,000\nMillion")

    # TRUE POSITIVE preserved: the same-line token still decodes and scales.
    assert module._normalize_value("45,000 million") == 45000000000
    assert module._normalize_value("3.56 billion") == 3560000000


def test_hard_wrapped_source_still_commits_the_scaled_value():
    # THIRD round, the VALUE half of the exhibit_prose fix (see
    # test_source_line_wrap_inside_a_block_still_absorbs_the_magnitude_word). The
    # block-separator guard was safe but cost real recall: EDGAR HTML is hard-
    # wrapped, so "3.56\nbillion" inside one paragraph is a realistic shape, and it
    # silently committed 3.56 — the META Family DAP defect this part exists to fix,
    # on the flagship case. Pinned end-to-end here, across the subprocess boundary,
    # because the surface producer and the multiplier live in different skills and
    # only the composed pipeline shows the committed value.
    #
    # No `@req` tag: this dispatch's plan binds tasks by "Brief item covered", not
    # a registered loom-spec REQ-id (same convention as the sibling tests above).
    module = _load_module()

    markets_scripts = _TESTS_DIR.parent / "skills" / "data-markets" / "scripts"
    spec = importlib.util.spec_from_file_location(
        "exhibit_prose", markets_scripts / "exhibit_prose.py"
    )
    exhibit_prose = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exhibit_prose)

    canonical_text = exhibit_prose.prose_surface(
        "<p>Family daily active people grew to 3.56\nbillion in the quarter.</p>"
    )
    candidates = module.propose(canonical_text)
    assert [c["matched_token"] for c in candidates] == ["3.56 billion"], candidates
    assert [c["value"] for c in candidates] == [3560000000], candidates

    # The anti-fabrication rail still holds over the newly-produced surface: the
    # token spans real adjacent prose, so it is a literal substring of it.
    for candidate in candidates:
        assert module.passes_substring_gate(candidate, canonical_text)


def test_prose_point_carries_period_identity_fields():
    # Slice C, Task 2: period IDENTITY is the raw (period_start, period_end,
    # period_kind) context pair — the thing that recognizes "the same period"
    # across filings — while the human-readable `period` stays a first-class
    # display LABEL. This task adds the identity FIELDS + pass-through onto the
    # committed point; it does NOT derive or validate them (derivation is
    # upstream, reused from _derive_fiscal_label per the brief), and it does NOT
    # change the dedup key (that is Task 3). So the point must carry whatever the
    # candidate carries, verbatim, and default each to None when absent — exactly
    # like the optional source_document/filing_date/value_qualifier pass-throughs
    # already do — without crashing on a prose candidate that has no dates yet.
    #
    # No `@req` tag: this dispatch's plan (docs/loom/plans/2026-07-22-kpi-
    # observation-history.md) binds tasks by "Brief item covered", not a
    # registered loom-spec REQ-id (same convention as the sibling tests above).
    module = _load_module()

    base = {
        "matched_token": "13,000",
        "verbatim_quote": "we hired 13,000 people",
        "value": 13000,
        "char_offset_span": [9, 15],
        "kpi_id": "headcount",
        "unit": "count",
        "period": "FY2024",
        "source_accession": "0001318605-24-000123",
        "as_of": "2024-10-31",
    }

    with_dates = dict(
        base,
        period_start="2024-01-01",
        period_end="2024-12-31",
        period_kind="duration",
    )
    point = module._prose_candidate_to_point(
        with_dates, company="ACME",
        confirmer="kouko", confirmed_at="2026-07-20T10:00:00Z",
    )
    assert point["period_start"] == "2024-01-01"
    assert point["period_end"] == "2024-12-31"
    assert point["period_kind"] == "duration"
    # The identity fields are ADDITIVE — the display label is untouched.
    assert point["period"] == "FY2024", "the display label rides through unchanged"

    # A candidate with no period dates yet (the current prose-lane shape) commits
    # cleanly with all three identity fields defaulting to None — no crash, no
    # fabricated dates — and the label is still whatever the candidate carried.
    without_dates = module._prose_candidate_to_point(
        base, company="ACME",
        confirmer="kouko", confirmed_at="2026-07-20T10:00:00Z",
    )
    assert without_dates["period_start"] is None
    assert without_dates["period_end"] is None
    assert without_dates["period_kind"] is None
    assert without_dates["period"] == "FY2024", "label unchanged when identity absent"


def test_prose_point_carries_integrity_stamp(tmp_path, monkeypatch):
    # Slice C, Task 5: a stored char offset is only meaningful relative to the
    # surface version that produced it, and the ANCHORED TOKEN is the load-bearing
    # datum. This task writes a write-time integrity stamp onto the committed
    # point: integrity = {span_sha256: sha256(matched_token bytes),
    # surface_version: <threaded value>}. The hash is over the TOKEN, not the
    # bounded verbatim_quote — pinned here so a future refactor can't silently
    # switch to hashing the (wider, mutable) quote. surface_version is threaded as
    # a PARAMETER through commit_to_store -> _prose_candidate_to_point, defaulting
    # to None so non-prose / unaware callers are unaffected. Write-time only; no
    # read-time re-verification (that is Part 3).
    #
    # No `@req` tag: this dispatch's plan (docs/loom/plans/2026-07-22-kpi-
    # observation-history.md) binds tasks by "Brief item covered", not a
    # registered loom-spec REQ-id (same convention as the sibling tests above).
    module = _load_module()

    # A candidate whose bounded quote DIFFERS from the matched token, so the two
    # hashes are distinguishable and we can assert the stamp is the token's.
    token = "13,000"
    quote = "we hired 13,000 people"
    assert quote != token, "the quote must differ from the token for this test"
    candidate = {
        "matched_token": token,
        "verbatim_quote": quote,
        "value": 13000,
        "char_offset_span": [9, 15],
        "kpi_id": "headcount",
        "unit": "count",
        "period": "FY2024",
        "source_accession": "0001318605-24-000123",
        "as_of": "2024-10-31",
    }

    surface_version = "prose-surface-2026.07"
    point = module._prose_candidate_to_point(
        candidate, company="ACME",
        confirmer="kouko", confirmed_at="2026-07-20T10:00:00Z",
        surface_version=surface_version,
    )

    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    quote_hash = hashlib.sha256(quote.encode("utf-8")).hexdigest()

    assert point["integrity"]["span_sha256"] == token_hash, (
        "span_sha256 is the sha256 of the ANCHORED TOKEN's bytes"
    )
    # The hash is the TOKEN's, NOT the bounded quote's — a future refactor that
    # hashed the quote instead would flip this assertion.
    assert point["integrity"]["span_sha256"] != quote_hash, (
        "the stamp must hash the token, not the wider verbatim_quote"
    )
    assert point["integrity"]["surface_version"] == surface_version, (
        "surface_version rides through from the threaded parameter"
    )

    # Non-prose / unaware callers are unaffected: surface_version defaults to None
    # (integrity still stamps the token hash; a None version cannot trip the
    # store's falsy-provenance guard — integrity is not a required provenance
    # field).
    default_point = module._prose_candidate_to_point(
        candidate, company="ACME",
        confirmer="kouko", confirmed_at="2026-07-20T10:00:00Z",
    )
    assert default_point["integrity"]["span_sha256"] == token_hash
    assert default_point["integrity"]["surface_version"] is None

    # The parameter threads end-to-end through commit_to_store into the durable
    # store — the "committed point carries the stamp" half of the acceptance.
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))
    scripts_dir = str(_SCRIPT.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    sys.modules.pop("kpi_store", None)
    import kpi_store  # noqa: E402

    stored = dict(
        candidate,
        kpi_id="employees_full_time",
        period="2024-12-31",
        source_kind="prose",
    )
    summary = module.commit_to_store(
        [stored], company="ACME",
        confirmer="kouko", confirmed_at="2026-07-20T10:00:00Z",
        confirmed=True, surface_version=surface_version,
    )
    assert summary["committed"] == 1
    from_store = kpi_store.query_latest("ACME", "employees_full_time", "2024-12-31")
    assert from_store is not None
    assert from_store["integrity"]["span_sha256"] == token_hash
    assert from_store["integrity"]["surface_version"] == surface_version
