#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["jsonschema>=4.20", "pytest>=7.0"]
# ///
"""Schema syntax + example-fixture validation tests.

Runs against the JSON Schema at
`legal-toolkit/skills/legal-playbook-author/assets/schema.json`.
Phase 1.5 quality gate (Validator subset): >= 22/24 broken
fixtures must be flagged as invalid.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "legal-playbook-author"
    / "assets"
    / "schema.json"
)


@pytest.fixture(scope="session")
def schema():
    return json.loads(SCHEMA_PATH.read_text())


@pytest.fixture(scope="session")
def validator(schema):
    return jsonschema.Draft202012Validator(schema)


def test_schema_syntax_is_valid(schema):
    jsonschema.Draft202012Validator.check_schema(schema)


# -- valid fixtures ---------------------------------------------------------


VALID_FLAT_MINIMAL = {
    "clause_id": "confidentiality",
    "walk_away_triggers": ["one-sided"],
    "escalate_to": "GC",
    "risk_default": "yellow",
    "source_type": "user_playbook",
}

VALID_FLAT_FULL = {
    "clause_id": "auto-renewal",
    "contract_types_applicable": ["SaaS", "MSA"],
    "walk_away_triggers": ["no notice", "notice < 30d"],
    "escalate_to": "法務主管",
    "escalate_to_hint": "通常是 法務主管 / GC",
    "risk_default": "yellow",
    "currency": "USD",
    "last_updated": "2026-05-12",
    "owner": "kouko",
    "source_type": "bundled_fallback",
    "source_attribution": "WorldCC 2024 Benchmark",
}

VALID_VARIANT_FILE = {
    "clause_id": "limitation-of-liability",
    "variant_id": "mid-deal",
    "gates": {"deal_size": {"gte": 100000, "lt": 1000000}},
    "walk_away_triggers": ["cap < 12mo fees"],
    "escalate_to": "GC",
    "risk_default": "yellow",
    "source_type": "user_playbook",
}

VALID_CLAUSE_CONTAINER = {
    "clause_id": "limitation-of-liability",
    "contract_types_applicable": ["SaaS", "MSA"],
    "has_variants": True,
    "market_data": "WorldCC 2024: median = 12mo fees",
    "last_updated": "2026-05-12",
}


@pytest.mark.parametrize(
    "fixture",
    [VALID_FLAT_MINIMAL, VALID_FLAT_FULL, VALID_VARIANT_FILE, VALID_CLAUSE_CONTAINER],
)
def test_valid_fixtures(validator, fixture):
    errors = list(validator.iter_errors(fixture))
    assert errors == [], f"Expected valid, got: {errors}"


# -- broken fixtures (Phase 1.5 quality gate: >= 22/24 caught) -------------
#
# Each fixture below is intentionally invalid. The test enforces that
# the schema flags it as invalid. We track exactly 24 fixtures so the
# overall metric maps to the Phase 1.5 ROADMAP gate.

BROKEN_FIXTURES = [
    # 1: flat missing clause_id
    {"walk_away_triggers": ["x"], "escalate_to": "GC", "risk_default": "yellow", "source_type": "user_playbook"},
    # 2: flat clause_id wrong casing
    {"clause_id": "Confidentiality", "walk_away_triggers": ["x"], "escalate_to": "GC", "risk_default": "yellow", "source_type": "user_playbook"},
    # 3: flat clause_id wrong start (digit)
    {"clause_id": "1-confidentiality", "walk_away_triggers": ["x"], "escalate_to": "GC", "risk_default": "yellow", "source_type": "user_playbook"},
    # 4: flat walk_away empty list
    {"clause_id": "confidentiality", "walk_away_triggers": [], "escalate_to": "GC", "risk_default": "yellow", "source_type": "user_playbook"},
    # 5: flat walk_away non-array
    {"clause_id": "confidentiality", "walk_away_triggers": "one-sided", "escalate_to": "GC", "risk_default": "yellow", "source_type": "user_playbook"},
    # 6: flat escalate_to empty
    {"clause_id": "confidentiality", "walk_away_triggers": ["x"], "escalate_to": "", "risk_default": "yellow", "source_type": "user_playbook"},
    # 7: flat risk_default unknown enum
    {"clause_id": "confidentiality", "walk_away_triggers": ["x"], "escalate_to": "GC", "risk_default": "magenta", "source_type": "user_playbook"},
    # 8: flat currency unknown enum
    {"clause_id": "confidentiality", "walk_away_triggers": ["x"], "escalate_to": "GC", "risk_default": "yellow", "currency": "JPY", "source_type": "user_playbook"},
    # 9: flat last_updated wrong format
    {"clause_id": "confidentiality", "walk_away_triggers": ["x"], "escalate_to": "GC", "risk_default": "yellow", "last_updated": "May 12, 2026", "source_type": "user_playbook"},
    # 10: flat source_type unknown
    {"clause_id": "confidentiality", "walk_away_triggers": ["x"], "escalate_to": "GC", "risk_default": "yellow", "source_type": "external"},
    # 11: flat carrying variant_id (cross-shape contamination)
    {"clause_id": "confidentiality", "variant_id": "x", "walk_away_triggers": ["x"], "escalate_to": "GC", "risk_default": "yellow", "source_type": "user_playbook"},
    # 12: flat carrying gates
    {"clause_id": "confidentiality", "gates": {"deal_size": {"gte": 1}}, "walk_away_triggers": ["x"], "escalate_to": "GC", "risk_default": "yellow", "source_type": "user_playbook"},
    # 13: flat carrying has_variants
    {"clause_id": "confidentiality", "has_variants": True, "walk_away_triggers": ["x"], "escalate_to": "GC", "risk_default": "yellow", "source_type": "user_playbook"},
    # 14: variant missing variant_id
    {"clause_id": "lol", "gates": {"deal_size": {"gte": 1}}, "walk_away_triggers": ["x"], "escalate_to": "GC", "risk_default": "yellow", "source_type": "user_playbook"},
    # 15: variant missing gates
    {"clause_id": "lol", "variant_id": "mid", "walk_away_triggers": ["x"], "escalate_to": "GC", "risk_default": "yellow", "source_type": "user_playbook"},
    # 16: variant empty gates
    {"clause_id": "lol", "variant_id": "mid", "gates": {}, "walk_away_triggers": ["x"], "escalate_to": "GC", "risk_default": "yellow", "source_type": "user_playbook"},
    # 17: variant gate-value malformed (no recognised key)
    {"clause_id": "lol", "variant_id": "mid", "gates": {"deal_size": {"unknown_op": 1}}, "walk_away_triggers": ["x"], "escalate_to": "GC", "risk_default": "yellow", "source_type": "user_playbook"},
    # 18: variant carrying has_variants
    {"clause_id": "lol", "variant_id": "mid", "has_variants": True, "gates": {"deal_size": {"gte": 1}}, "walk_away_triggers": ["x"], "escalate_to": "GC", "risk_default": "yellow", "source_type": "user_playbook"},
    # 19: variant carrying contract_types_applicable (must live on _clause.md)
    {"clause_id": "lol", "variant_id": "mid", "contract_types_applicable": ["SaaS"], "gates": {"deal_size": {"gte": 1}}, "walk_away_triggers": ["x"], "escalate_to": "GC", "risk_default": "yellow", "source_type": "user_playbook"},
    # 20: _clause missing has_variants
    {"clause_id": "lol", "contract_types_applicable": ["SaaS"]},
    # 21: _clause has_variants=false (must be true)
    {"clause_id": "lol", "contract_types_applicable": ["SaaS"], "has_variants": False},
    # 22: _clause missing contract_types_applicable
    {"clause_id": "lol", "has_variants": True},
    # 23: _clause carrying walk_away_triggers (must live on variant files)
    {"clause_id": "lol", "contract_types_applicable": ["SaaS"], "has_variants": True, "walk_away_triggers": ["x"]},
    # 24: _clause carrying escalate_to
    {"clause_id": "lol", "contract_types_applicable": ["SaaS"], "has_variants": True, "escalate_to": "GC"},
]


@pytest.mark.parametrize("idx,fixture", list(enumerate(BROKEN_FIXTURES, start=1)))
def test_broken_fixture_is_caught(validator, idx, fixture):
    errors = list(validator.iter_errors(fixture))
    assert errors, f"Fixture #{idx} should have produced errors but did not"


def test_phase_1_5_quality_gate(validator):
    """Phase 1.5 quality gate: >= 22 of 24 broken fixtures must be flagged.

    This test cross-checks the ROADMAP gate. If passes drop below 22 the
    rubric has regressed and the gate fails.
    """
    caught = sum(
        1 for fx in BROKEN_FIXTURES if list(validator.iter_errors(fx))
    )
    assert caught >= 22, f"Phase 1.5 gate failed: caught {caught}/24 (require >= 22)"
