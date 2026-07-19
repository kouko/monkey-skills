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

import importlib.util
from pathlib import Path

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
    # In Part 1 the verbatim_quote IS the matched token.
    assert candidate["verbatim_quote"] == candidate["matched_token"]
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
