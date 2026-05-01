"""conftest.py — shared fixtures + marker registration for data-{country} tests.

Registers the `network` marker so live-API tests can be selected/skipped:

    pytest tests/data/ -m network        # opt-in: run live API calls
    pytest tests/data/ -m "not network"  # offline-safe (CI default)

All tests that hit yfinance / FRED / NBS / EDINET / TDnet / MOPS / TWSE /
FinanceDataReader / akshare are decorated with @pytest.mark.network.

Pure-logic tests (ROC quarter math, ticker auto-suffix) are unmarked and
always run, including in offline CI.
"""
from __future__ import annotations

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "network: requires external API calls (skip in offline CI)",
    )
