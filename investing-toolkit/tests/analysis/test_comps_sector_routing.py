"""Tests for analysis-comps/scripts/sector_classifier.py — pure-function
(ticker, sector, industry) → schema_id routing for v2.2.0-c sector-aware
multiples.

Offline only (no network, no yfinance). The classifier loads two yaml SoT
files (sector-routing.yaml + sector-overrides.yaml) at module import time,
then resolves classifications via override → industry_match → sector_default
→ unknown_sector_fallback. See spec §4 + §10.1.

Tests cover:
  * Spec §10.1 routing acceptance table (12 fixed cases).
  * Drift guards: KNOWN_SCHEMA_IDS ↔ schema-*.json files,
    routing.yaml schemas ⊆ KNOWN_SCHEMA_IDS, overrides.yaml schemas ⊆
    KNOWN_SCHEMA_IDS + non-empty notes.
  * `classify_pack` round-trip + missing-info graceful fallback.
  * Loud-failure validation: malformed overrides yaml rejected at first call.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import textwrap
from pathlib import Path

import pytest

# pyyaml is required by sector_classifier itself; mirror existing test
# convention (tests/test_skill_structure.py:144-148) and skip if absent so
# CI without `--with pyyaml` doesn't false-fail.
yaml = pytest.importorskip("yaml", reason="pyyaml required by sector_classifier; run with `uv run --with pyyaml`")


# Locate the script under test. Path layout:
#   tests/analysis/test_comps_sector_routing.py
#     parents[0] = tests/analysis
#     parents[1] = tests
#     parents[2] = investing-toolkit (== ROOT in conftest.py)
SECTOR_CLASSIFIER_PATH = (
    Path(__file__).resolve().parents[2]
    / "skills" / "analysis-comps" / "scripts" / "sector_classifier.py"
)
REFERENCES_DIR = (
    Path(__file__).resolve().parents[2]
    / "skills" / "analysis-comps" / "references"
)


@pytest.fixture(scope="session")
def sector_classifier():
    """Load sector_classifier.py as a fresh, isolated module.

    importlib avoids polluting sys.path and lets us reset _ROUTING /
    _OVERRIDES caches between tests that monkeypatch the yaml paths.
    """
    spec = importlib.util.spec_from_file_location(
        "sector_classifier_test", SECTOR_CLASSIFIER_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["sector_classifier_test"] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Spec §10.1 routing acceptance table
# ---------------------------------------------------------------------------

# (ticker, sector, industry, expected_schema_id, expected_source)
ROUTING_CASES = [
    ("AAPL", "Technology",         "Consumer Electronics",            "default",       "sector_default"),
    ("MSFT", "Technology",         "Software - Infrastructure",       "tech-saas",     "industry_match"),
    ("TSM",  "Technology",         "Semiconductors",                  "tech-semis",    "industry_match"),
    ("JPM",  "Financial Services", "Banks - Diversified",             "bank",          "industry_match"),
    ("MET",  "Financial Services", "Insurance - Diversified",         "insurance",     "industry_match"),
    ("BLK",  "Financial Services", "Asset Management",                "asset-manager", "industry_match"),
    ("O",    "Real Estate",        "REIT - Retail",                   "reit",          "industry_match"),
    ("LEN",  "Consumer Cyclical",  "Residential Construction",        "default",       "sector_default"),
    ("XOM",  "Energy",             "Oil & Gas Integrated",            "energy",        "sector_default"),
    ("NEE",  "Utilities",          "Utilities - Regulated Electric",  "utilities",     "sector_default"),
    ("BRK-B", "Financial Services", "Insurance - Diversified",        "default",       "override"),
    ("FOO",  None,                  None,                             "default",       "unknown_sector"),
]


@pytest.mark.parametrize(
    "ticker,sector,industry,expected_schema,expected_source",
    ROUTING_CASES,
    ids=[c[0] for c in ROUTING_CASES],
)
def test_routing_acceptance_table(
    sector_classifier, ticker, sector, industry, expected_schema, expected_source,
):
    """Spec §10.1 — every row must classify to (schema_id, source)."""
    result = sector_classifier.classify(ticker=ticker, sector=sector, industry=industry)
    assert result.schema_id == expected_schema, (
        f"{ticker} ({sector}/{industry}) → schema_id={result.schema_id!r}, "
        f"expected {expected_schema!r}; matched_rule={result.matched_rule!r}"
    )
    assert result.source == expected_source, (
        f"{ticker} ({sector}/{industry}) → source={result.source!r}, "
        f"expected {expected_source!r}; matched_rule={result.matched_rule!r}"
    )
    if ticker == "BRK-B":
        # Override entries MUST carry an audit note explaining why yfinance's
        # auto-routing is wrong. Asserted both at load time (validator) and
        # here at the classify-result level.
        assert result.note, "BRK-B override result must surface a non-empty note"


# ---------------------------------------------------------------------------
# Drift guards: KNOWN_SCHEMA_IDS ↔ schema-*.json files
# ---------------------------------------------------------------------------

def test_known_schema_ids_match_schema_files(sector_classifier):
    """Every id in KNOWN_SCHEMA_IDS must have a `schema-<id>.json` companion.

    Drift guard — adding a schema_id without the JSON file (or vice versa)
    fails here.
    """
    for sid in sector_classifier.KNOWN_SCHEMA_IDS:
        schema_path = REFERENCES_DIR / f"schema-{sid}.json"
        assert schema_path.exists(), (
            f"KNOWN_SCHEMA_IDS includes {sid!r} but {schema_path.name} is missing"
        )
        try:
            payload = json.loads(schema_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            pytest.fail(f"{schema_path.name} is not valid JSON: {exc}")
        assert isinstance(payload, dict), (
            f"{schema_path.name} top-level must be a JSON object"
        )
        assert payload.get("schema_id") == sid, (
            f"{schema_path.name} schema_id={payload.get('schema_id')!r} "
            f"does not match filename {sid!r}"
        )


def test_routing_yaml_only_uses_known_schemas(sector_classifier):
    """Every schema referenced in sector-routing.yaml ∈ KNOWN_SCHEMA_IDS.

    Drift guard at the yaml level — sector_classifier's _validate_routing
    enforces the same invariant at load time, but this duplicates it as a
    pre-load assertion (e.g. fails earlier in pytest -x runs).
    """
    routing_path = REFERENCES_DIR / "sector-routing.yaml"
    payload = yaml.safe_load(routing_path.read_text(encoding="utf-8"))
    assert "routes" in payload, "sector-routing.yaml missing top-level `routes:`"

    known = set(sector_classifier.KNOWN_SCHEMA_IDS)
    fallback = payload.get("unknown_sector_fallback")
    assert fallback in known, (
        f"unknown_sector_fallback={fallback!r} not in KNOWN_SCHEMA_IDS"
    )

    for sector, rules in payload["routes"].items():
        for idx, rule in enumerate(rules):
            if "_default" in rule:
                schema = rule["_default"]
            elif "industry_contains" in rule:
                schema = rule.get("schema")
            else:
                pytest.fail(f"routes[{sector!r}][{idx}] has neither `_default` nor `industry_contains`")
            assert schema in known, (
                f"routes[{sector!r}][{idx}] schema={schema!r} not in KNOWN_SCHEMA_IDS"
            )


def test_overrides_yaml_only_uses_known_schemas(sector_classifier):
    """Every override entry references a known schema AND carries a non-empty note."""
    overrides_path = REFERENCES_DIR / "sector-overrides.yaml"
    payload = yaml.safe_load(overrides_path.read_text(encoding="utf-8"))
    assert "overrides" in payload, "sector-overrides.yaml missing top-level `overrides:`"

    known = set(sector_classifier.KNOWN_SCHEMA_IDS)
    for ticker, entry in payload["overrides"].items():
        assert isinstance(entry, dict), (
            f"overrides[{ticker!r}] must be a mapping"
        )
        assert entry.get("schema") in known, (
            f"overrides[{ticker!r}] schema={entry.get('schema')!r} not in KNOWN_SCHEMA_IDS"
        )
        assert entry.get("note"), (
            f"overrides[{ticker!r}] missing non-empty `note` (audit policy)"
        )


# ---------------------------------------------------------------------------
# classify_pack convenience wrapper
# ---------------------------------------------------------------------------

def test_classify_pack_round_trip(sector_classifier):
    """Pack with `info[ticker].sector` + `.industry` → routes the same as classify()."""
    pack = {
        "ticker": "JPM",
        "info": {
            "JPM": {
                "sector": "Financial Services",
                "industry": "Banks - Diversified",
            }
        },
    }
    result = sector_classifier.classify_pack(pack)
    assert result.schema_id == "bank"
    assert result.source == "industry_match"


def test_classify_pack_with_missing_info(sector_classifier):
    """Pack lacking `info[ticker]` block must fall back to unknown_sector — no crash."""
    pack = {"ticker": "ZZZ", "info": {}}
    result = sector_classifier.classify_pack(pack)
    assert result.schema_id == "default"
    assert result.source == "unknown_sector"


# ---------------------------------------------------------------------------
# Loud-failure validation: malformed overrides yaml
# ---------------------------------------------------------------------------

def _reload_classifier(name: str) -> "object":
    """Helper: load a fresh copy of sector_classifier so monkeypatched module
    constants take effect (the module caches _ROUTING / _OVERRIDES at first
    call; we need a clean instance per validation test).

    The fresh instance must be registered in sys.modules under a unique name
    before exec_module runs, otherwise dataclass field-resolution falls over
    (cpython#3.9 dataclasses.py:660 indexes sys.modules[cls.__module__])."""
    spec = importlib.util.spec_from_file_location(name, SECTOR_CLASSIFIER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_unknown_schema_override_rejected_at_load(tmp_path, monkeypatch):
    """Override referencing a non-existent schema must raise ValueError on first classify."""
    bad = tmp_path / "sector-overrides-bad.yaml"
    bad.write_text(textwrap.dedent("""\
        version: 1
        overrides:
          BADTICKER:
            schema: not-a-real-schema
            note: "intentionally malformed for test"
    """), encoding="utf-8")

    module = _reload_classifier("sector_classifier_bad_schema")
    monkeypatch.setattr(module, "_OVERRIDES_PATH", bad)
    monkeypatch.setattr(module, "_OVERRIDES", None)

    with pytest.raises(ValueError, match="not in KNOWN_SCHEMA_IDS"):
        module.classify(ticker="BADTICKER", sector="Technology", industry="Software")


def test_override_without_note_rejected_at_load(tmp_path, monkeypatch):
    """Override missing the audit `note` field must raise ValueError on first classify."""
    bad = tmp_path / "sector-overrides-no-note.yaml"
    bad.write_text(textwrap.dedent("""\
        version: 1
        overrides:
          NONOTE:
            schema: default
    """), encoding="utf-8")

    module = _reload_classifier("sector_classifier_no_note")
    monkeypatch.setattr(module, "_OVERRIDES_PATH", bad)
    monkeypatch.setattr(module, "_OVERRIDES", None)

    with pytest.raises(ValueError, match="missing required `note`"):
        module.classify(ticker="NONOTE", sector="Technology", industry="Software")
