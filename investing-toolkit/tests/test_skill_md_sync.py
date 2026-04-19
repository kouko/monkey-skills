"""test_skill_md_sync.py — SKILL.md ↔ MCP server sync check

Two assertions:
  1. Every skill SKILL.md that carries a "Dual-mode execution" blockquote
     has consistent phrasing — prevents silent drift in the canonical
     retrospective language across files.
  2. Any backticked MCP tool name mentioned inside a SKILL.md MCP
     blockquote must exist in the current MCP server registry.

Detects:
  - Forgotten updates: after renaming / removing an MCP tool in
    mcp_server.py, stale names in SKILL.md files are flagged.
  - Drift in the corrected blockquote phrasing.

Not detected (out of scope):
  - Whether Phase 1 subprocess commands in skill bodies cover every
    tool; left to author review.
  - Whether tool descriptions in MCP match what SKILL.md describes;
    requires semantic check, deferred.

Run with:
  cd investing-toolkit
  uv run --with pytest pytest tests/test_skill_md_sync.py -v
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
SERVER = ROOT / "servers" / "mcp_server.py"

# Phrase that every v1.16.1-corrected SKILL.md must carry verbatim.
CANONICAL_PHRASE = "MCP does NOT bypass Cowork sandbox URL allowlist"

# Skills that carry the MCP-aware blockquote (9 affected files).
AFFECTED_SKILLS = {
    "investment-memo-writer",
    "us-stock-snapshot",
    "taiwan-stock-snapshot",
    "japan-stock-snapshot",
    "macro-regime-snapshot",
    "stock-screener",
    "dcf-valuation",
    "invest-portfolio",
    "technical-snapshot",
}

# Pattern matching backticked MCP-looking tool names.
# Must be snake_case with at least one underscore, to avoid matching
# general Python identifiers / script names / file paths.
TOOL_PATTERN = re.compile(r"`([a-z][a-z0-9_]*_[a-z0-9_]+)`")


def _get_registered_mcp_tools() -> set[str]:
    """Run mcp_server.py --self-check, return set of registered tool names."""
    res = subprocess.run(
        ["uv", "run", "--script", str(SERVER), "--self-check"],
        capture_output=True, text=True, timeout=120, cwd=str(ROOT),
    )
    assert res.returncode == 0, f"--self-check failed: {res.stderr[-400:]}"
    lines = [ln for ln in res.stdout.splitlines() if ln.strip()]
    payload = json.loads(lines[-1])
    assert payload["ok"], payload

    # Self-check returns per-client counts, not actual tool names.
    # Use the stdio path to get real names.
    initialize_req = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                   "clientInfo": {"name": "sync-check", "version": "0.1"}},
    }) + "\n"
    initialized = '{"jsonrpc":"2.0","method":"notifications/initialized"}\n'
    list_req = '{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n'

    res = subprocess.run(
        ["uv", "run", "--script", str(SERVER)],
        input=initialize_req + initialized + list_req,
        capture_output=True, text=True, timeout=120, cwd=str(ROOT),
    )
    assert res.returncode == 0, f"stdio tools/list failed: {res.stderr[-400:]}"

    frames = [
        json.loads(ln)
        for ln in res.stdout.splitlines()
        if ln.strip().startswith("{")
    ]
    list_frames = [f for f in frames if f.get("id") == 2]
    assert list_frames, "no tools/list reply"
    tools = list_frames[0]["result"]["tools"]
    return {t["name"] for t in tools}


def _extract_mcp_blockquote(skill_md_text: str) -> str | None:
    """Return the first blockquote paragraph that looks like an MCP-aware
    blockquote (contains 'MCP' and the canonical phrase), else None."""
    # Match a blockquote line (> ...) that contains "MCP".
    for m in re.finditer(r"^> .*$", skill_md_text, flags=re.MULTILINE):
        line = m.group(0)
        if "MCP" in line and "execution" in line:
            return line
    return None


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_affected_skills_have_canonical_phrase():
    """Every skill we corrected in v1.16.1 Commit 2 must carry the
    canonical retrospective phrasing."""
    missing = []
    for skill_name in AFFECTED_SKILLS:
        skill_md = SKILLS_DIR / skill_name / "SKILL.md"
        if not skill_md.exists():
            missing.append(f"{skill_name}: SKILL.md not found")
            continue
        text = skill_md.read_text(encoding="utf-8")
        if CANONICAL_PHRASE not in text:
            missing.append(f"{skill_name}: missing canonical phrase")

    assert not missing, (
        "SKILL.md files drift from v1.16.1 canonical prose:\n"
        + "\n".join(missing)
    )


def test_no_stale_mcp_tool_references_in_skill_mds():
    """Any backticked tool name inside a SKILL.md MCP blockquote must
    be a currently-registered MCP tool."""
    registered = _get_registered_mcp_tools()

    stale: list[str] = []
    for skill_md in SKILLS_DIR.glob("*/SKILL.md"):
        text = skill_md.read_text(encoding="utf-8")
        blockquote = _extract_mcp_blockquote(text)
        if not blockquote:
            continue
        mentioned = set(TOOL_PATTERN.findall(blockquote))
        # Strip tokens that aren't MCP tools (script names, etc.)
        mcp_candidates = {
            name for name in mentioned
            if not name.endswith("_client")
            and not name.endswith(".py")
        }
        unknown = mcp_candidates - registered
        if unknown:
            stale.append(f"{skill_md.relative_to(ROOT)}: unknown tools {sorted(unknown)}")

    assert not stale, (
        "SKILL.md references MCP tools not registered in servers/mcp_server.py:\n"
        + "\n".join(stale)
        + f"\n\nCurrently registered ({len(registered)}): {sorted(registered)}"
    )
