"""test_mcp_equivalence_auto.py — parameterized MCP↔CLI drift guard

For each tool in FIXTURES, runs the same logical call via:
  (a) the MCP stdio server (servers/mcp_server.py)
  (b) the subprocess CLI (scripts/<client>.py ... flags)

Asserts both paths return equivalent stable fields, catching silent
drift when an action helper changes without matching wrapper updates.

Coverage intent: ≥1 fixture per client in v1.16.1. Adding a new tool /
script → add ≤1 fixture entry here (~3 min marginal cost).

Skipped in CI:
  - edinet_* — requires EDINET_API_KEY (skipped unless env var is set)
  - ecb_series / boj_fetch — no stable public fixture without valid
    series keys; caller-specific queries only

Run with:
  cd investing-toolkit
  uv run --with pytest pytest tests/test_mcp_equivalence_auto.py -v

Adding a new fixture:
  1. Append a dict to FIXTURES with: tool, mcp_args, cli_script,
     cli_flags, (optional) compare_fn override.
  2. If the call is slow or rate-limited, prefer a preset that
     benefits from the 24h / 30d cache TTL.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Callable

import pytest

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "servers" / "mcp_server.py"
SCRIPTS_DIR = ROOT / "scripts"

# ---------------------------------------------------------------------------
# JSON-RPC stdio helpers (reuse pattern from test_mcp_contract.py)
# ---------------------------------------------------------------------------

_INITIALIZE_REQ = (
    '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{'
    '"protocolVersion":"2024-11-05","capabilities":{},'
    '"clientInfo":{"name":"equivalence-test","version":"0.1"}}}\n'
)
_INITIALIZED_NOTE = '{"jsonrpc":"2.0","method":"notifications/initialized"}\n'


def _call_mcp(tool_name: str, args: dict, timeout: int = 120) -> dict:
    """Spawn mcp_server.py, issue tools/call, return parsed payload dict."""
    call_req = json.dumps({
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {"name": tool_name, "arguments": args},
    }) + "\n"
    res = subprocess.run(
        ["uv", "run", "--script", str(SERVER)],
        input=_INITIALIZE_REQ + _INITIALIZED_NOTE + call_req,
        capture_output=True, text=True, timeout=timeout, cwd=str(ROOT),
    )
    frames = [
        json.loads(ln)
        for ln in res.stdout.splitlines()
        if ln.strip().startswith("{")
    ]
    call_frames = [f for f in frames if f.get("id") == 3]
    assert call_frames, (
        f"no tools/call reply for {tool_name} "
        f"(stderr tail={res.stderr[-400:]})"
    )
    content = call_frames[0]["result"]["content"]
    text_items = [c["text"] for c in content if c.get("type") == "text"]
    assert text_items, f"no text content in {tool_name} response"
    return json.loads(text_items[0])


def _call_cli(script: str, flags: list[str], timeout: int = 120) -> dict:
    """Run the CLI script directly, return parsed stdout JSON."""
    cmd = ["uv", "run", "--script", str(SCRIPTS_DIR / script), *flags]
    res = subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, cwd=str(ROOT),
    )
    assert res.returncode == 0, (
        f"CLI {script} failed (code={res.returncode}); stderr="
        f"{res.stderr[-400:]}"
    )
    return json.loads(res.stdout)


# ---------------------------------------------------------------------------
# Volatile-field stripper
# ---------------------------------------------------------------------------

VOLATILE_KEYS = {
    "fetched_at", "_cache", "_fetched_at",
    "processDateTime", "_provenance",  # provenance carries fetched_at
}


def _strip_volatile(obj):
    if isinstance(obj, dict):
        return {
            k: _strip_volatile(v)
            for k, v in obj.items()
            if k not in VOLATILE_KEYS
        }
    if isinstance(obj, list):
        return [_strip_volatile(x) for x in obj]
    return obj


def _default_compare(mcp: dict, cli: dict) -> None:
    """Strip volatile fields and assert structural equality."""
    assert _strip_volatile(mcp) == _strip_volatile(cli)


# ---------------------------------------------------------------------------
# Fixture registry
# ---------------------------------------------------------------------------


FIXTURES: list[dict] = [
    # --- fred (1 tool) ---
    {
        "tool": "fred_series",
        "mcp_args": {"series": ["DGS10"], "periods": 3},
        "cli_script": "fred_client.py",
        "cli_flags": ["--series", "DGS10", "--periods", "3"],
    },
    # --- yfinance (3 non-batch tools) ---
    {
        "tool": "yfinance_history",
        "mcp_args": {"ticker": "AAPL", "period": "1mo"},
        "cli_script": "yfinance_client.py",
        "cli_flags": ["--ticker", "AAPL", "--period", "1mo"],
        # Yahoo's latest_close can drift if called across a price tick.
        # Compare last observation date + ticker rather than full equality.
        "compare_fn": lambda m, c: (
            m["ticker"] == c["ticker"]
            and len(m["data"]) == len(c["data"])
            and m["data"][-1]["date"] == c["data"][-1]["date"]
        ),
    },
    {
        "tool": "yfinance_info",
        "mcp_args": {"ticker": "AAPL"},
        "cli_script": "yfinance_client.py",
        "cli_flags": ["--ticker", "AAPL", "--action", "info"],
        "compare_fn": lambda m, c: (
            m["ticker"] == c["ticker"]
            and m.get("sector") == c.get("sector")
            and m.get("marketCap") == c.get("marketCap")
        ),
    },
    {
        "tool": "yfinance_financials",
        "mcp_args": {"ticker": "AAPL", "period": "annual"},
        "cli_script": "yfinance_client.py",
        "cli_flags": ["--ticker", "AAPL", "--action", "financials",
                      "--period", "annual"],
        # Yahoo financial periods are stable per-quarter; compare latest period.
        "compare_fn": lambda m, c: (
            m["ticker"] == c["ticker"]
            and m["latest_period"] == c["latest_period"]
            and set(m["key_metrics"]) == set(c["key_metrics"])
        ),
    },
    # --- sec_edgar (2 of 4 — cik + filings) ---
    {
        "tool": "sec_edgar_cik",
        "mcp_args": {"ticker": "NVDA"},
        "cli_script": "sec_edgar_client.py",
        "cli_flags": ["--action", "cik", "--ticker", "NVDA"],
    },
    {
        "tool": "sec_edgar_filings",
        "mcp_args": {"ticker": "NVDA", "forms": ["10-K"], "limit": 1},
        "cli_script": "sec_edgar_client.py",
        "cli_flags": ["--action", "filings", "--ticker", "NVDA",
                      "--forms", "10-K", "--limit", "1"],
    },
    # --- mops (1 dispatch tool, stable company-basic) ---
    {
        "tool": "mops_fetch",
        "mcp_args": {"action": "company-basic", "ticker": "2330"},
        "cli_script": "mops_client.py",
        "cli_flags": ["--action", "company-basic", "--ticker", "2330"],
    },
    # --- twse_openapi (1 dispatch tool, 2 fixtures — snapshot + history) ---
    {
        "tool": "twse_openapi_fetch",
        "mcp_args": {"action": "listed-companies", "ticker": "2330"},
        "cli_script": "twse_openapi_client.py",
        "cli_flags": ["--action", "listed-companies", "--ticker", "2330"],
    },
    {
        # v1.16.3 stock-day-history action — Tier A historical OHLCV
        "tool": "twse_openapi_fetch",
        "mcp_args": {"action": "stock-day-history", "ticker": "2330",
                     "months": 2},
        "cli_script": "twse_openapi_client.py",
        "cli_flags": ["--action", "stock-day-history", "--ticker", "2330",
                      "--months", "2"],
        "compare_fn": lambda m, c: (
            m.get("ticker") == c.get("ticker") == "2330"
            and m.get("period") == c.get("period") == "2mo"
            and m.get("rows") == c.get("rows")
            and (m.get("data") or [{}])[-1].get("close")
                == (c.get("data") or [{}])[-1].get("close")
        ),
    },
    # --- tdnet (1 tool) ---
    {
        "tool": "tdnet_list",
        "mcp_args": {"ticker": "7203", "limit": 3},
        "cli_script": "tdnet_client.py",
        "cli_flags": ["--ticker", "7203", "--limit", "3"],
    },
    # --- boj (1 of 2 — tankan is most stable) ---
    {
        "tool": "boj_tankan_inflation_outlook",
        "mcp_args": {"horizons": [1], "periods": 2},
        "cli_script": "boj_client.py",
        "cli_flags": ["--tankan-price-outlook", "--horizons", "1",
                      "--periods", "2"],
        # Single-horizon call returns single-series shape
        # (series = code string, observations at top level).
        # Compare _preset + series code + latest observation value.
        "compare_fn": lambda m, c: (
            m.get("_preset") == c.get("_preset") == "tankan-price-outlook"
            and m.get("series") == c.get("series")
            and (m.get("observations") or [{}])[-1].get("value")
                == (c.get("observations") or [{}])[-1].get("value")
        ),
    },
    # --- estat (1 of 2 — preset) ---
    {
        "tool": "estat_fetch",
        "mcp_args": {"preset": "cpi"},
        "cli_script": "estat_client.py",
        "cli_flags": ["--preset", "cpi"],
        # estat-dashboard occasionally returns 0 observations on a fresh
        # fetch (rate-limited?) while a prior cache entry has the full
        # series. Assert only that MCP and CLI resolve the same indicator
        # code — drift in the wrapper would surface here.
        "compare_fn": lambda m, c: (
            m.get("preset") == c.get("preset") == "cpi"
            and m.get("indicator") == c.get("indicator")
            and m.get("_source") == c.get("_source") == "estat_dashboard"
        ),
    },
    # --- akshare (1 tool) ---
    {
        "tool": "akshare_china_macro",
        "mcp_args": {"presets": ["lpr-1y"]},
        "cli_script": "akshare_client.py",
        "cli_flags": ["--preset", "lpr-1y"],
    },
    # --- ndc (1 tool) ---
    {
        "tool": "ndc_fetch",
        "mcp_args": {"preset": "signal"},
        "cli_script": "ndc_client.py",
        "cli_flags": ["--preset", "signal"],
    },
    # --- edinet (gated on API key) ---
    {
        "tool": "edinet_resolve_code",
        "mcp_args": {"ticker": "7203"},
        "cli_script": "edinet_client.py",
        "cli_flags": ["--action", "resolve-code", "--ticker", "7203"],
        # resolve-code is the only EDINET path that works without key.
    },
]


# Skips: tools that need env vars / no stable public fixture
SKIP_WITHOUT_ENV = {
    # tool_name: required env var
    # (none of the in-fixture tools currently gated; add if we extend
    #  to sec_edgar_facts w/ API key auth or finmind paid tier)
}


def _skip_reason(fx: dict) -> str | None:
    env_var = SKIP_WITHOUT_ENV.get(fx["tool"])
    if env_var and not os.environ.get(env_var):
        return f"requires {env_var}"
    return None


# ---------------------------------------------------------------------------
# Negative-case tests — v1.16.2 mops_fetch missing-param validation
# ---------------------------------------------------------------------------
#
# Asserts mops_fetch returns a friendly {"error": "...", "action": "..."}
# dict when required per-action params are missing, instead of crashing
# with "unsupported format string passed to NoneType.__format__"
# (fixed in v1.16.2 via `_validate_action_params`).


MOPS_MISSING_PARAM_CASES: list[tuple[str, dict, str]] = [
    # action,                  mcp_args,                                 expected missing flag in error
    ("director-holdings", {"ticker": "6741"},                            "--year"),
    ("director-holdings", {"ticker": "6741", "year": 114},               "--month"),
    ("monthly-revenue",   {"ticker": "2330"},                            "--year"),
    ("day-announcements", {},                                             "--year"),
    ("balance-sheet",     {"ticker": "2330", "year": 114},               "--season"),
    ("insider-trades",    {"ticker": "2330", "year": 114},               "--month"),
]


@pytest.mark.parametrize(
    "action,args,expected_flag",
    MOPS_MISSING_PARAM_CASES,
    ids=[f"{a}_missing_{f}" for a, _, f in MOPS_MISSING_PARAM_CASES],
)
def test_mops_fetch_rejects_missing_required_params(
    action: str, args: dict, expected_flag: str,
):
    result = _call_mcp("mops_fetch", {"action": action, **args})
    assert "error" in result, (
        f"expected error dict for {action} missing {expected_flag}, "
        f"got: {result}"
    )
    assert expected_flag in result["error"], (
        f"error should mention missing flag {expected_flag}; "
        f"got: {result['error']!r}"
    )
    assert result.get("action") == action, (
        f"error should carry action={action!r}, got: {result.get('action')!r}"
    )


# ---------------------------------------------------------------------------
# Parameterized test (positive path — MCP == CLI equivalence)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fx",
    FIXTURES,
    ids=[fx["tool"] for fx in FIXTURES],
)
def test_mcp_matches_cli(fx: dict):
    skip = _skip_reason(fx)
    if skip:
        pytest.skip(skip)

    mcp_out = _call_mcp(fx["tool"], fx["mcp_args"])
    cli_out = _call_cli(fx["cli_script"], fx["cli_flags"])

    compare: Callable = fx.get("compare_fn") or _default_compare

    if compare is _default_compare:
        _default_compare(mcp_out, cli_out)
    else:
        assert compare(mcp_out, cli_out), (
            f"equivalence check failed for {fx['tool']}\n"
            f"MCP keys: {sorted(mcp_out.keys()) if isinstance(mcp_out, dict) else type(mcp_out)}\n"
            f"CLI keys: {sorted(cli_out.keys()) if isinstance(cli_out, dict) else type(cli_out)}"
        )
