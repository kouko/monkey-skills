#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0", "pytest>=7.0"]
# ///
"""Tests for abac_filter.py — 12 deal_context cases per Phase 1.5 gate.

Phase 1.5 ROADMAP quality gate (ABAC subset): ≥ 11/12 deal_context
variant-match outcomes must be correct.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "legal-contract-review"
    / "scripts"
    / "abac_filter.py"
)


@pytest.fixture(scope="session")
def abac():
    spec = importlib.util.spec_from_file_location("abac_filter", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["abac_filter"] = module
    spec.loader.exec_module(module)
    return module


# LoL deal-size 3-variant set (small / mid / large) per design note §4.4.2
LOL_VARIANTS = [
    {
        "variant_id": "small-deal",
        "gates": {"deal_size": {"lt": 100000}},
    },
    {
        "variant_id": "mid-deal",
        "gates": {"deal_size": {"gte": 100000, "lt": 1000000}},
    },
    {
        "variant_id": "large-deal",
        "gates": {"deal_size": {"gte": 1000000}},
    },
]

# DPA jurisdiction-overlay 3-variant set (tw-only / gdpr-overlay / cross-border)
DPA_VARIANTS = [
    {
        "variant_id": "tw-only",
        "gates": {"data_subjects_jurisdiction": {"eq": "TW"}},
    },
    {
        "variant_id": "gdpr-overlay",
        "gates": {"data_subjects_jurisdiction": {"any_of": ["EU", "UK", "EEA"]}},
    },
    {
        "variant_id": "cross-border",
        "gates": {"data_transfer_destinations": {"any_of": ["US", "CN", "JP"]}},
    },
]


# -- 12 Phase 1.5 gate cases ------------------------------------------------

PHASE_1_5_CASES = [
    # LoL — deal-size numeric range matching
    (
        "lol/small-clearly",
        LOL_VARIANTS,
        {"deal_size": 50000},
        "single",
        "small-deal",
    ),
    (
        "lol/mid-boundary-low",
        LOL_VARIANTS,
        {"deal_size": 100000},
        "single",
        "mid-deal",
    ),
    (
        "lol/mid-boundary-high",
        LOL_VARIANTS,
        {"deal_size": 999999},
        "single",
        "mid-deal",
    ),
    (
        "lol/large-clear",
        LOL_VARIANTS,
        {"deal_size": 2500000},
        "single",
        "large-deal",
    ),
    (
        "lol/exact-1m",
        LOL_VARIANTS,
        {"deal_size": 1000000},
        "single",
        "large-deal",
    ),
    (
        "lol/missing-context",
        LOL_VARIANTS,
        {"deal_size": None},
        "advisory",
        None,
    ),
    # DPA — enum matching
    (
        "dpa/tw-only-hit",
        DPA_VARIANTS,
        {"data_subjects_jurisdiction": "TW"},
        "single",
        "tw-only",
    ),
    (
        "dpa/gdpr-uk",
        DPA_VARIANTS,
        {"data_subjects_jurisdiction": "UK"},
        "single",
        "gdpr-overlay",
    ),
    (
        "dpa/cross-border-us",
        DPA_VARIANTS,
        {"data_transfer_destinations": "US"},
        "single",
        "cross-border",
    ),
    (
        "dpa/multi-match",
        DPA_VARIANTS,
        # TW data subjects + US transfer destination → matches BOTH tw-only AND cross-border
        {"data_subjects_jurisdiction": "TW", "data_transfer_destinations": "US"},
        "multi",
        "tw-only",  # first match wins
    ),
    (
        "dpa/no-match",
        DPA_VARIANTS,
        {"data_subjects_jurisdiction": "CA"},
        "advisory",
        None,
    ),
    # Mixed wildcard / multi-key
    (
        "wildcard-always-matches",
        [
            {"variant_id": "default", "gates": {"counterparty_type": "any"}},
        ],
        {"counterparty_type": "enterprise"},
        "single",
        "default",
    ),
]


@pytest.mark.parametrize("name,variants,ctx,expected_outcome,expected_id", PHASE_1_5_CASES, ids=[c[0] for c in PHASE_1_5_CASES])
def test_abac_phase_1_5_case(abac, name, variants, ctx, expected_outcome, expected_id):
    outcome, chosen, matched = abac.match_variant(ctx, variants)
    assert outcome == expected_outcome, f"{name}: outcome {outcome} != {expected_outcome}"
    chosen_id = (chosen or {}).get("variant_id")
    assert chosen_id == expected_id, f"{name}: chosen {chosen_id} != {expected_id}"


def test_phase_1_5_quality_gate(abac):
    """≥ 11/12 cases must match expected outcome."""
    correct = 0
    for name, variants, ctx, expected_outcome, expected_id in PHASE_1_5_CASES:
        outcome, chosen, _matched = abac.match_variant(ctx, variants)
        chosen_id = (chosen or {}).get("variant_id")
        if outcome == expected_outcome and chosen_id == expected_id:
            correct += 1
    assert correct >= 11, f"Phase 1.5 ABAC gate failed: {correct}/12 (require >= 11)"


# -- additional invariants --------------------------------------------------


def test_check_gate_eq_string(abac):
    assert abac.check_gate({"eq": "enterprise"}, "enterprise") is True
    assert abac.check_gate({"eq": "enterprise"}, "startup") is False


def test_check_gate_numeric_strict_lt(abac):
    assert abac.check_gate({"lt": 100}, 99) is True
    assert abac.check_gate({"lt": 100}, 100) is False


def test_check_gate_any_of(abac):
    g = {"any_of": ["A", "B", "C"]}
    assert abac.check_gate(g, "B") is True
    assert abac.check_gate(g, "Z") is False


def test_check_gate_combined_range(abac):
    g = {"gte": 10, "lt": 20}
    assert abac.check_gate(g, 10) is True
    assert abac.check_gate(g, 15) is True
    assert abac.check_gate(g, 19.999) is True
    assert abac.check_gate(g, 20) is False
    assert abac.check_gate(g, 9.99) is False


def test_check_gate_missing_context_does_not_match_non_wildcard(abac):
    assert abac.check_gate({"gte": 1}, None) is False


def test_check_gate_wildcard_always_matches(abac):
    assert abac.check_gate("any", "literally anything") is True
    assert abac.check_gate("any", None) is True
    assert abac.check_gate("any", 0) is True
