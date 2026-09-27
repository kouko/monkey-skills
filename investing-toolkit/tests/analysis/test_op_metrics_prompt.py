"""Tests for analysis-kpi/scripts/extract_operational_metrics.py — the
Level 2 LLM operational-metrics extractor's prompt assembly.

Focus: `get_llm_prompt` truncation. The live TSLA test (2026-09-27) proved
the failure mode: a 52,845-char 8-K Item 2.02 puts the deliveries total
("497,099") at char offset 8013 — the blanket 8000-char truncation dropped
it while keeping the production total ("447,450"), so the LLM received a
prompt with half the operational summary and silently under-extracted.

The fix: select the metric-bearing regions (lines containing operational
numbers and their context) instead of a blind head-truncation, with a
generous char budget. The prompt must contain every metric-bearing line
from the source text; it may drop unrelated boilerplate.

extract_operational_metrics.py is PURE-COMPUTE (stdlib only) — no network,
no LLM call here; we test prompt assembly only, same importlib convention
as test_kpi_parse.py.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from conftest import KPI_OP_METRICS_SCRIPT

import pytest


@pytest.fixture(scope="module")
def op_metrics_module():
    spec = importlib.util.spec_from_file_location("op_metrics_test", KPI_OP_METRICS_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["op_metrics_test"] = module
    spec.loader.exec_module(module)
    return module


# Real shape from TSLA's 8-K Item 2.02 (000162828026049270): header noise
# first, the Operational Summary table past char 8000.
_TSLA_8K_SHAPE = (
    "UNITED STATES SECURITIES AND EXCHANGE COMMISSION\n"
    "Washington, D.C. 20549\n\n"
    "FORM 8-K\n\n"
    "Tesla, Inc. announces financial results for the third quarter of 2025.\n"
) + ("Forward-looking statements language. " * 300) + "\n\n" + (
    "Vehicle Production & Deliveries and certain other key metrics\n"
    "(units)\n"
    "                      Q3-2025      Q3-2024       YoY\n"
    "Total production      447,450      469,796       (5)%\n"
    "Total deliveries      497,099      462,890        7%\n"
)


def test_prompt_keeps_metric_lines_beyond_8000_chars(op_metrics_module):
    """The live-documented failure: deliveries at char 8013 must survive
    prompt assembly. A blind 8000-char head-truncation drops it.
    """
    text = _TSLA_8K_SHAPE
    assert text.find("497,099") > 8000, "fixture precondition: metric past 8000"

    _system, user = op_metrics_module.get_llm_prompt(text)

    assert "447,450" in user
    assert "497,099" in user
    assert "Total production" in user
    assert "Total deliveries" in user


def test_prompt_keeps_million_scaled_prose(op_metrics_module):
    """10-K Item 7 prose ("produced approximately 1.66 million consumer
    vehicles") uses million-scaled wording with no comma digits — the
    selector must keep those lines too.
    """
    text = (
        "Item 7. Management's Discussion and Analysis.\n\n"
        "In 2025, we produced approximately 1.66 million consumer vehicles "
        "and delivered approximately 1.64 million consumer vehicles.\n\n"
        "The remainder of this section discusses liquidity in depth. " * 300
    )
    assert len(text) > 8000

    _system, user = op_metrics_module.get_llm_prompt(text)

    assert "1.66 million" in user
    assert "1.64 million" in user
    assert "produced approximately" in user


def test_prompt_respects_char_budget(op_metrics_module):
    """Selection is bounded: a huge filing must not produce an unbounded
    prompt. Budget is generous (operational sections are small) but finite.
    """
    filler = "Risk factor boilerplate sentence. " * 2100  # ~70K chars
    text = filler + "\nTotal production 447,450 vehicles.\n" + filler

    _system, user = op_metrics_module.get_llm_prompt(text)

    assert "447,450" in user
    assert len(user) <= 60_000, f"prompt budget exceeded: {len(user)} chars"


def test_prompt_small_text_passthrough(op_metrics_module):
    """Short texts (under any truncation threshold) pass through whole."""
    text = "Total production 12,345 vehicles. Total deliveries 12,000 vehicles."

    _system, user = op_metrics_module.get_llm_prompt(text)

    assert "12,345" in user
    assert "12,000" in user


def test_prompt_system_prompt_unchanged_contract(op_metrics_module):
    """System prompt must still demand explicit-numeric-only extraction
    with the metrics JSON schema."""
    system, _user = op_metrics_module.get_llm_prompt("Total production 100 vehicles.")

    assert "EXPLICITLY stated" in system
    assert '"metrics"' in system
