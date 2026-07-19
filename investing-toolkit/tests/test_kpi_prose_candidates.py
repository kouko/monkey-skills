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
