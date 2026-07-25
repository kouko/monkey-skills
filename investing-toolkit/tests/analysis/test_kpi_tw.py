"""Tests for analysis-kpi/scripts/kpi_tw.py — TW iXBRL fact -> kpi_store
point adapter (TW-market kpi_store producer, Task 1).

kpi_tw.py is PURE-COMPUTE (stdlib only: re + datetime). It takes an
ALREADY-PARSED list of fact dicts (the twse_ixbrl_parser shape) as input —
it does NOT parse HTML and does NOT import any data-markets module (the
analysis↔data-markets layer boundary, per
[[durable-store-mirrors-cache-util-not-imports-it]]).

The TEST parses the real captured 1101 fixture through the production
twse_ixbrl_parser (test scaffolding only) and passes the facts in, so the
auth-date VALUE is empirically the fixture's, never a guessed format.

No `@req` tags: this dispatch's plan (docs/loom/plans/2026-07-25-tw-kpi-
store-producer.md) traces work by named plan Tasks, NOT by registered
loom-spec REQ-ids — so `@req` is omitted per the implementer contract.
"""
from __future__ import annotations

import importlib.util
import sys

from conftest import ROOT, SKILLS

import pytest

KPI_TW_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_tw.py"
TWSE_PARSER_SCRIPT = SKILLS / "data-markets" / "scripts" / "twse_ixbrl_parser.py"
TWSE_1101_FIXTURE = ROOT / "tests" / "data" / "fixtures" / "twse_ixbrl_1101_2026Q1_C.html"

AUTH_CONCEPT = (
    "tifrs-notes:DateAndProceduresOfAuthorisationForIssueOfFinancialStatements"
)


def _load(name: str, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def kpi_tw_module():
    return _load("kpi_tw_test", KPI_TW_SCRIPT)


@pytest.fixture(scope="module")
def fixture_1101_facts():
    parser = _load("twse_ixbrl_parser_test", TWSE_PARSER_SCRIPT)
    raw = TWSE_1101_FIXTURE.read_bytes()
    doc = parser.decode_ixbrl_document(raw)
    return parser.parse_ixbrl_facts(doc)


def test_extract_tw_authorisation_date(kpi_tw_module, fixture_1101_facts):
    # The 1101 fixture carries a ROC-era date (民國 115年5月13日) wrapped in
    # 董事會 procedure text: "本合併財務報告於115年5月13日經董事會通過。".
    # ROC 115 + 1911 = Gregorian 2026 → the as_of is 2026-05-13.
    assert (
        kpi_tw_module.extract_tw_authorisation_date(fixture_1101_facts)
        == "2026-05-13"
    )


def test_extract_tw_authorisation_date_gregorian(kpi_tw_module):
    # A filing whose auth-date fact carries a Gregorian date (with procedure
    # wording) parses to the same ISO shape — the value MAY be either era.
    facts = [
        {
            "concept": AUTH_CONCEPT,
            "raw_value": "本合併財務報告於2026-05-13經董事會通過。",
            "fact_type": "nonNumeric",
        }
    ]
    assert kpi_tw_module.extract_tw_authorisation_date(facts) == "2026-05-13"


def test_extract_tw_authorisation_date_gregorian_nian_form(kpi_tw_module):
    # A Gregorian date in 年-form ("2026年5月13日") must NOT be mis-read as
    # ROC "026年" (026 + 1911 = 1937). The 4-digit year is Gregorian → 2026,
    # never a silent wrong-century as_of.
    facts = [
        {
            "concept": AUTH_CONCEPT,
            "raw_value": "本財務報告於2026年5月13日經董事會通過。",
            "fact_type": "nonNumeric",
        }
    ]
    assert kpi_tw_module.extract_tw_authorisation_date(facts) == "2026-05-13"


def test_extract_tw_authorisation_date_absent_returns_none(kpi_tw_module):
    facts = [
        {"concept": "ifrs-full:CashAndCashEquivalents", "raw_value": 1000.0},
        {"concept": "tifrs-notes:PercentageOfOwnership4", "raw_value": 1.0},
    ]
    assert kpi_tw_module.extract_tw_authorisation_date(facts) is None
