"""test_mcp_contract.py — MCP surface contract tests (v1.14.0+)

Asserts that:
  1. `mcp_server.py --self-check` returns a canonical JSON shape with
     ok=True, the expected total tool count, and per-client breakdown.
  2. Spawning the MCP stdio server and performing a real initialize +
     tools/list roundtrip returns all expected tools with non-empty schemas.
  3. For a stable, cache-friendly tool (`fred_series`), calling via MCP
     and via the subprocess CLI returns the same `latest.value` — the
     contract we rely on when skills' SKILL.md prose tells Claude "MCP
     and CLI return identical JSON".

Current surface (v1.15.0): 19 tools across 10 clients.

Run with:
    uv run --script servers/mcp_server.py --self-check   # sanity
    uv run pytest tests/test_mcp_contract.py -q

Requires the MCP server deps to be resolvable by uv (first run pulls
them via the same cache warmed by setup.sh).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "servers" / "mcp_server.py"
FRED_CLI = ROOT / "scripts" / "fred_client.py"


def _run_uv_script(args: list[str], stdin: str | None = None, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", "--script", *args],
        input=stdin,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(ROOT),
    )


# ---------------------------------------------------------------------------
# 1. self-check contract
# ---------------------------------------------------------------------------


def test_self_check_returns_expected_summary():
    res = _run_uv_script([str(SERVER), "--self-check"])
    assert res.returncode == 0, res.stderr
    # Last non-empty line of stdout is the JSON summary
    lines = [ln for ln in res.stdout.splitlines() if ln.strip()]
    payload = json.loads(lines[-1])
    assert payload["ok"] is True
    assert payload["tools"] == 19  # v1.15.0: +4 edinet +1 tdnet +1 yfinance_financials
    assert set(payload["tools_per_client"]) == {
        "yfinance", "akshare", "nbs", "fred",
        "sec_edgar", "mops", "twse_openapi", "finmind",
        "edinet", "tdnet",
    }
    assert payload["tools_per_client"]["sec_edgar"] == 4
    assert payload["tools_per_client"]["edinet"] == 4
    assert payload["tools_per_client"]["yfinance"] == 4  # v1.15.0: + financials
    assert payload["tools_per_client"]["mops"] == 1
    assert payload["tools_per_client"]["tdnet"] == 1


# ---------------------------------------------------------------------------
# 2. stdio handshake + tools/list contract
# ---------------------------------------------------------------------------


_INITIALIZE_REQ = (
    '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{'
    '"protocolVersion":"2024-11-05","capabilities":{},'
    '"clientInfo":{"name":"contract-test","version":"0.1"}}}\n'
)
_INITIALIZED_NOTE = '{"jsonrpc":"2.0","method":"notifications/initialized"}\n'
_LIST_TOOLS_REQ = '{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n'


def test_mcp_stdio_exposes_all_19_tools():
    res = _run_uv_script(
        [str(SERVER)],
        stdin=_INITIALIZE_REQ + _INITIALIZED_NOTE + _LIST_TOOLS_REQ,
        timeout=60,
    )
    # FastMCP logs go to stderr; stdout holds JSON-RPC frames.
    frames = [json.loads(ln) for ln in res.stdout.splitlines() if ln.strip().startswith("{")]
    init_frames = [f for f in frames if f.get("id") == 1]
    list_frames = [f for f in frames if f.get("id") == 2]
    assert init_frames, f"no initialize reply (stderr={res.stderr[-500:]})"
    assert list_frames, f"no tools/list reply (stderr={res.stderr[-500:]})"

    init_result = init_frames[0]["result"]
    assert init_result["protocolVersion"] == "2024-11-05"
    assert init_result["serverInfo"]["name"] == "investing-toolkit"

    tools = list_frames[0]["result"]["tools"]
    assert len(tools) == 19
    names = {t["name"] for t in tools}
    expected = {
        # yfinance (4 — v1.15.0 added financials)
        "yfinance_history", "yfinance_info", "yfinance_batch", "yfinance_financials",
        # macro + regulator (6)
        "akshare_china_macro", "nbs_china_macro", "fred_series",
        "mops_fetch", "twse_openapi_fetch", "finmind_fetch",
        # sec_edgar (4)
        "sec_edgar_cik", "sec_edgar_facts", "sec_edgar_filings",
        "sec_edgar_narrative",
        # edinet (4 — NEW v1.15.0)
        "edinet_resolve_code", "edinet_list_filings",
        "edinet_fetch_statements", "edinet_filing_summary",
        # tdnet (1 — NEW v1.15.0)
        "tdnet_list",
    }
    assert names == expected, sorted(names - expected) + sorted(expected - names)

    # Every tool must carry a non-empty inputSchema so Claude can render it.
    for t in tools:
        assert t.get("inputSchema"), f"{t['name']} missing inputSchema"
        assert t.get("description"), f"{t['name']} missing description"


# ---------------------------------------------------------------------------
# 3. MCP == CLI equivalence (fred_series / DGS10)
# ---------------------------------------------------------------------------


def _call_fred_via_mcp(series: str, periods: int) -> dict:
    call_req = (
        '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":'
        f'{{"name":"fred_series","arguments":{{"series":["{series}"],"periods":{periods}}}}}}}\n'
    )
    res = _run_uv_script(
        [str(SERVER)],
        stdin=_INITIALIZE_REQ + _INITIALIZED_NOTE + call_req,
        timeout=90,
    )
    frames = [json.loads(ln) for ln in res.stdout.splitlines() if ln.strip().startswith("{")]
    call_frames = [f for f in frames if f.get("id") == 3]
    assert call_frames, f"no tools/call reply (stderr={res.stderr[-500:]})"
    content = call_frames[0]["result"]["content"]
    # FastMCP wraps plain-dict return values as a text content item
    # containing the JSON payload.
    text_items = [c["text"] for c in content if c.get("type") == "text"]
    assert text_items, "no text content in tool response"
    return json.loads(text_items[0])


def _call_fred_via_cli(series: str, periods: int) -> dict:
    res = _run_uv_script(
        [str(FRED_CLI), "--series", series, "--periods", str(periods)],
        timeout=60,
    )
    assert res.returncode == 0, res.stderr
    return json.loads(res.stdout)


@pytest.mark.parametrize("series,periods", [("DGS10", 3)])
def test_fred_mcp_matches_cli(series, periods):
    mcp_out = _call_fred_via_mcp(series, periods)
    cli_out = _call_fred_via_cli(series, periods)

    # Both paths should share the same series ID, the same number of
    # observations, and the same latest value.
    assert mcp_out.get("series") == cli_out.get("series") == series
    assert len(mcp_out["observations"]) == len(cli_out["observations"]) == periods
    assert mcp_out["observations"][-1]["value"] == cli_out["observations"][-1]["value"]
    assert mcp_out["observations"][-1]["date"] == cli_out["observations"][-1]["date"]
