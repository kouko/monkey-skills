"""Tests for citecheck.py — cite-check schemas + support-verdict logic.

Flat import (pytest.ini sets pythonpath = .).
"""
import json
import subprocess
import sys

from citecheck import (
    EXTRACT_CITED_CLAIMS,
    SUPPORT_VERDICT,
    classify_support,
    summarize,
)


# --- EXTRACT_CITED_CLAIMS schema shape -------------------------------------

def test_extract_cited_claims_is_array_of_claim_objects():
    assert EXTRACT_CITED_CLAIMS["type"] == "object"
    claims = EXTRACT_CITED_CLAIMS["properties"]["claims"]
    assert claims["type"] == "array"
    item = claims["items"]
    # binding output shape: a claim string + a cited source + a locator
    assert "claim" in item["properties"]
    assert "citedUrl" in item["properties"]
    assert "citedRef" in item["properties"]
    assert "locator" in item["properties"]
    assert "claim" in item["required"]


# --- SUPPORT_VERDICT schema shape ------------------------------------------

def test_support_verdict_enum_is_three_way():
    enum = SUPPORT_VERDICT["properties"]["support"]["enum"]
    assert enum == ["supported", "partial", "unsupported"]


def test_support_verdict_has_flags_and_evidence():
    props = SUPPORT_VERDICT["properties"]
    assert props["misattributed"]["type"] == "boolean"
    assert props["unresolvable"]["type"] == "boolean"
    assert props["evidence"]["type"] == "string"
    assert "support" in SUPPORT_VERDICT["required"]


# --- classify_support normalization ----------------------------------------

def test_classify_support_passes_through_three_way():
    for s in ("supported", "partial", "unsupported"):
        out = classify_support({"support": s})
        assert out["support"] == s
        assert out["flags"] == []


def test_classify_support_unresolvable_overrides_support():
    # a dead/paywalled cited source is unresolvable regardless of support guess
    out = classify_support({"support": "unsupported", "unresolvable": True})
    assert out["support"] == "unresolvable"
    assert "unresolvable" in out["flags"]


def test_classify_support_misattributed_is_a_flag_not_a_support_state():
    out = classify_support({"support": "partial", "misattributed": True})
    assert out["support"] == "partial"
    assert "misattributed" in out["flags"]


def test_classify_support_missing_support_defaults_unsourced():
    # no support field + no flags → claim had no resolvable citation
    out = classify_support({})
    assert out["support"] == "unsourced"


def test_classify_support_none_object_fails_loud():
    import pytest as _pytest
    with _pytest.raises((TypeError, ValueError)):
        classify_support(None)


def test_classify_support_invalid_support_value_fails_loud():
    import pytest as _pytest
    with _pytest.raises(ValueError):
        classify_support({"support": "definitely-true"})


# --- summarize roll-up -----------------------------------------------------

def test_unresolvable_counted_separately_from_unsupported():
    rows = [
        {"support": "unsupported"},
        {"unresolvable": True},
    ]
    out = summarize(rows)
    assert out["counts"]["unsupported"] == 1
    assert out["counts"]["unresolvable"] == 1


def test_summarize_rolls_up_mixed_input():
    rows = [
        {"support": "supported"},
        {"support": "supported"},
        {"support": "partial"},
        {"support": "unsupported", "misattributed": True},
        {"unresolvable": True},
        {},  # unsourced
    ]
    out = summarize(rows)
    assert out["total"] == 6
    c = out["counts"]
    assert c["supported"] == 2
    assert c["partial"] == 1
    assert c["unsupported"] == 1
    assert c["misattributed"] == 1
    assert c["unresolvable"] == 1
    assert c["unsourced"] == 1


# --- __main__ verdict subcommand -------------------------------------------

def test_cli_verdict_prints_summary_json():
    payload = '[{"support":"supported"},{"support":"unsupported"},{"unresolvable":true}]'
    proc = subprocess.run(
        [sys.executable, "citecheck.py", "verdict"],
        input=payload,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)
    assert out["total"] == 3
    assert out["counts"]["supported"] == 1
    assert out["counts"]["unsupported"] == 1
    assert out["counts"]["unresolvable"] == 1


def test_cli_unknown_subcommand_fails_loud():
    proc = subprocess.run(
        [sys.executable, "citecheck.py", "bogus"],
        input="[]",
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
