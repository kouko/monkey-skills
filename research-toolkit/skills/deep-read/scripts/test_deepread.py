"""Tests for deepread.py — READ_SCHEMA, merge_chunks, render_report, CLI."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from deepread import (
    CHUNK_EXTRACT_SCHEMA,
    READ_SCHEMA,
    merge_chunks,
    render_report,
)

SCRIPT = Path(__file__).resolve().parent / "deepread.py"


# --------------------------------------------------------------------------
# Schemas
# --------------------------------------------------------------------------


def test_read_schema_has_seven_named_fields():
    props = READ_SCHEMA["properties"]
    for field in (
        "sourceQuality",
        "sections",
        "claims",
        "methodology",
        "caveats",
        "openQuestions",
        "argumentStructure",
    ):
        assert field in props, f"READ_SCHEMA missing {field!r}"


def test_read_schema_claim_item_carries_section_provenance():
    claim_item = READ_SCHEMA["properties"]["claims"]["items"]["properties"]
    for field in ("claim", "quote", "importance", "section"):
        assert field in claim_item, f"claim item missing {field!r}"


def test_chunk_extract_schema_is_richer_than_plain_extract():
    props = CHUNK_EXTRACT_SCHEMA["properties"]
    # per-chunk section role + claims + optional methodology/caveats
    assert "section" in props
    assert "claims" in props
    assert "methodology" in props
    assert "caveats" in props


# --------------------------------------------------------------------------
# merge_chunks
# --------------------------------------------------------------------------


def _chunk(section, claims, **extra):
    return {"section": section, "claims": claims, **extra}


def test_merge_dedups_claim_repeated_across_two_chunks():
    chunks = [
        _chunk(
            "Intro",
            [{"claim": "The sky is blue.", "quote": "q1", "importance": "high"}],
        ),
        _chunk(
            "Body",
            [
                # near-duplicate of the Intro claim (whitespace / case)
                {"claim": "the   SKY is BLUE.", "quote": "q2", "importance": "low"},
                {"claim": "Grass is green.", "quote": "q3", "importance": "medium"},
            ],
        ),
    ]
    out = merge_chunks(chunks)
    claim_texts = [c["claim"] for c in out["claims"]]
    # the sky claim collapses to ONE; grass claim survives → 2 total
    assert len(out["claims"]) == 2, claim_texts
    assert "Grass is green." in claim_texts


def test_merge_preserves_section_order():
    chunks = [
        _chunk("First", [{"claim": "a", "quote": "qa", "importance": "high"}]),
        _chunk("Second", [{"claim": "b", "quote": "qb", "importance": "high"}]),
        _chunk("Third", [{"claim": "c", "quote": "qc", "importance": "high"}]),
    ]
    out = merge_chunks(chunks)
    assert out["sections"] == ["First", "Second", "Third"]
    assert out["argumentStructure"] == ["First", "Second", "Third"]


def test_merge_keeps_per_claim_section_provenance():
    chunks = [
        _chunk("Alpha", [{"claim": "x", "quote": "qx", "importance": "high"}]),
        _chunk("Beta", [{"claim": "y", "quote": "qy", "importance": "high"}]),
    ]
    out = merge_chunks(chunks)
    by_claim = {c["claim"]: c["section"] for c in out["claims"]}
    assert by_claim["x"] == "Alpha"
    assert by_claim["y"] == "Beta"


def test_merge_collects_methodology_and_caveats():
    chunks = [
        _chunk(
            "M",
            [{"claim": "a", "quote": "qa", "importance": "high"}],
            methodology="RCT n=100",
            caveats="small sample",
        ),
        _chunk(
            "N",
            [{"claim": "b", "quote": "qb", "importance": "high"}],
            caveats="single site",
        ),
    ]
    out = merge_chunks(chunks)
    assert "RCT n=100" in out["methodology"]
    assert "small sample" in out["caveats"]
    assert "single site" in out["caveats"]


def test_merge_rejects_non_list():
    with pytest.raises(TypeError):
        merge_chunks({"section": "x"})


# --------------------------------------------------------------------------
# render_report
# --------------------------------------------------------------------------


def _understanding():
    return {
        "sourceQuality": "peer-reviewed",
        "sections": ["Intro", "Methods"],
        "claims": [
            {
                "claim": "Coffee boosts focus.",
                "quote": "participants improved",
                "importance": "high",
                "section": "Intro",
            }
        ],
        "methodology": "double-blind trial",
        "caveats": "industry-funded",
        "openQuestions": ["long-term effects?"],
        "argumentStructure": ["Intro", "Methods"],
    }


def test_render_emits_outline_table_and_blocks():
    md = render_report(_understanding())
    assert "Intro" in md and "Methods" in md  # sections outline
    assert "| Claim |" in md or "| claim |" in md.lower()  # claims table header
    assert "Coffee boosts focus." in md
    assert "double-blind trial" in md  # methodology
    assert "industry-funded" in md  # caveats
    assert "long-term effects?" in md  # open questions


def test_render_escapes_pipe_and_newline_in_quote():
    u = _understanding()
    u["claims"][0]["quote"] = "a | b\nc"
    md = render_report(u)
    # locate the table row holding the claim
    row = next(
        line
        for line in md.splitlines()
        if "Coffee boosts focus." in line and line.lstrip().startswith("|")
    )
    # split on UNescaped pipes only — a 4-col row yields 6 fields (2 empty ends)
    fields = re.split(r"(?<!\\)\|", row)
    assert len(fields) == 6, fields
    assert "\\|" in row  # the quote's pipe was escaped, not a column break
    # the newline was folded — the claim and quote stay on the same single row
    assert row.endswith("|")


def test_render_rejects_non_dict():
    with pytest.raises(TypeError):
        render_report(["not", "a", "dict"])


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def _run(args, stdin):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=stdin,
        capture_output=True,
        text=True,
    )


def test_cli_report_prints_markdown():
    proc = _run(["report"], json.dumps(_understanding()))
    assert proc.returncode == 0, proc.stderr
    assert "Coffee boosts focus." in proc.stdout


def test_cli_merge_prints_merged_json():
    chunks = [
        _chunk("S1", [{"claim": "a", "quote": "qa", "importance": "high"}]),
    ]
    proc = _run(["merge"], json.dumps(chunks))
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)
    assert out["sections"] == ["S1"]


def test_cli_unknown_subcommand_fails_loud():
    proc = _run(["banana"], "")
    assert proc.returncode == 1
    assert proc.stderr.strip()
