"""Tests for framework_audit.py — FRAMEWORK_AUDIT_SCHEMA shape + CLI.

Mirrors test_scope_vs.py style: flat imports (`from framework_audit import
...`) plus subprocess CLI round-trip tests.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent

# CJK-block ranges (U+ boundaries, in regex order):
#   U+3000–303F CJK punctuation/symbols (incl 〔〕「」、。)
#   U+3040–30FF kana · U+3400–4DBF CJK Ext-A · U+4E00–9FFF CJK unified
#   U+FF00–FFEF fullwidth forms · U+2460–24FF enclosed alphanumerics (①②…)
# Starts at U+3000 / U+2460 so ASCII-safe typography the doc uses
# (→ U+2192, × U+00D7, ≈ U+2248, ⊂ U+2282, — U+2014, … U+2026) is NOT matched.
_CJK = re.compile(r"[　-〿぀-ヿ㐀-䶿一-鿿＀-￯①-⓿]")


def test_module_source_is_english_only():
    # The classify→audit→library walk must stay consistent in one language;
    # this module's prompts route into the now-English library, so any
    # residual CJK is a cross-language drift bug (the task's load-bearing
    # acceptance criterion: grep CJK == 0).
    src = (SCRIPTS_DIR / "framework_audit.py").read_text(encoding="utf-8")
    leftover = _CJK.findall(src)
    assert leftover == [], f"residual CJK in framework_audit.py: {leftover}"


def test_classify_prompt_uses_canonical_routing_labels():
    # classify_prompt's example route keys MUST be drawn from the library's
    # routing-table row labels verbatim, or the agent classifies into a key
    # the library can't route. Spot-check the canonical English labels.
    from framework_audit import classify_prompt

    prompt = classify_prompt("any question")
    for label in (
        "Investment / single stock",
        "Macro / industry",
        "Policy / regulation",
        "Product / UX",
        "Risk / safety",
    ):
        assert label in prompt, f"missing canonical routing label: {label!r}"


def test_schema_subcommand_emits_gap_schema():
    from framework_audit import FRAMEWORK_AUDIT_SCHEMA

    # Top-level: {question, gaps}
    assert set(FRAMEWORK_AUDIT_SCHEMA["required"]) == {"question", "gaps"}

    gaps = FRAMEWORK_AUDIT_SCHEMA["properties"]["gaps"]
    assert gaps["type"] == "array"

    item = gaps["items"]
    # Gap items require the SCOPE_SCHEMA angle fields plus framework + cell.
    assert set(item["required"]) == {"label", "query", "framework", "cell"}
    # rationale is present but optional (mirrors SCOPE_SCHEMA angle shape).
    assert "rationale" in item["properties"]
    assert "rationale" not in item["required"]
    for prop in ("label", "query", "framework", "cell", "rationale"):
        assert item["properties"][prop]["type"] == "string"

    # CLI round-trip: `schema` prints valid JSON equal to the dict, exit 0.
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "framework_audit.py"), "schema"],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 0
    assert json.loads(proc.stdout) == FRAMEWORK_AUDIT_SCHEMA


def test_classify_prompt_contains_question_and_routes():
    from framework_audit import classify_prompt

    q = "Is NVDA a buy at current valuation given AI capex cycle risk?"
    prompt = classify_prompt(q)

    # (a) the question text is interpolated verbatim.
    assert q in prompt

    # (b) instructs consulting the routing table to pick frameworks.
    lower = prompt.lower()
    assert "routing table" in lower
    assert "framework-audit-library.md" in prompt

    # (c) asks for 2–3 frameworks (covers the en-dash and hyphen forms).
    assert ("2–3" in prompt or "2-3" in prompt)
    assert "framework" in lower

    # (d) text-only — positively pins the no-web-search constraint the prompt
    # claims (a "fetch" not-in check would be vacuous: the prompt never emits it).
    assert "no web search" in lower or "no retrieval" in lower

    # CLI round-trip: classify-prompt prints the prompt, exit 0.
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "framework_audit.py"),
            "classify-prompt",
            "--question",
            q,
        ],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 0
    assert q in proc.stdout
    assert "routing table" in proc.stdout.lower()


def test_audit_prompt_walks_cells_and_proposes_gaps():
    from framework_audit import audit_prompt

    q = "Is NVDA a buy at current valuation given AI capex cycle risk?"
    angles = [
        {"label": "Moat durability", "query": "NVDA moat CUDA lock-in"},
        {"label": "Valuation multiples", "query": "NVDA forward P/E vs peers"},
    ]
    frameworks = ["Porter Five Forces", "DCF + Comparables"]
    prompt = audit_prompt(q, angles, frameworks)

    lower = prompt.lower()

    # (a) the question text is interpolated verbatim.
    assert q in prompt

    # (b) the existing angle set is interpolated (a label substring appears).
    assert "Moat durability" in prompt
    # (c) the chosen frameworks are named in the prompt.
    assert "DCF + Comparables" in prompt

    # (d) instructs per-cell walking of each framework.
    assert "cell" in lower
    assert "uncovered" in lower

    # (e) asks for gap angles tagged with framework + cell.
    assert "framework" in lower and "cell" in lower
    assert "label" in lower and "query" in lower

    # (f) instructs dedup against the existing angles (don't re-propose).
    assert "dedup" in lower or "already cover" in lower or "re-propose" in lower

    # (g) references the 12 collective blind-spots meta-check.
    assert "blind-spot" in lower or "blind spot" in lower
    assert "12" in prompt

    # (h) text-only — positively pins the no-fetch constraint.
    assert "no web search" in lower or "no retrieval" in lower

    # CLI round-trip: audit-prompt prints the prompt, exit 0.
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "framework_audit.py"),
            "audit-prompt",
            "--angles",
            json.dumps(angles),
            "--question",
            q,
        ],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 0
    assert q in proc.stdout
    assert "Moat durability" in proc.stdout
    assert "uncovered" in proc.stdout.lower()


def test_cli_unknown_subcommand():
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "framework_audit.py"), "bogus"],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 1
    assert proc.stdout.strip() == ""
    assert "bogus" in proc.stderr


def test_cli_missing_subcommand():
    # Empty argv → name "(none)" path (carry-forward gap from Task 1: only the
    # bogus-subcommand path was covered, never the no-subcommand path).
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "framework_audit.py")],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 1
    assert proc.stdout.strip() == ""
    assert "(none)" in proc.stderr or "expected one of" in proc.stderr


def test_select_gaps_dedups_and_caps():
    from framework_audit import select_gaps

    existing = [
        {"label": "Moat durability", "query": "NVDA moat CUDA lock-in"},
        {"label": "Valuation multiples", "query": "NVDA forward P/E vs peers"},
    ]
    gaps = [
        # (1) duplicates an existing angle by case-folded label → dropped.
        {"label": "moat durability", "query": "something else entirely",
         "framework": "Porter", "cell": "Rivalry"},
        # (2) duplicates an existing angle by normalized query → dropped.
        {"label": "Different label", "query": "NVDA forward P/E vs peers",
         "framework": "DCF", "cell": "Multiple"},
        # (3..5) three genuinely novel gaps that survive dedup.
        {"label": "Supplier power", "query": "NVDA TSMC supplier concentration",
         "framework": "Porter", "cell": "Supplier", "rationale": "single-fab risk"},
        {"label": "Time decay", "query": "NVDA AI capex cycle peak timing",
         "framework": "collective-blind-spot", "cell": "time-decay"},
        {"label": "Base rates", "query": "semiconductor cycle base rate drawdown",
         "framework": "collective-blind-spot", "cell": "base-rates"},
        # (6) intra-gap duplicate of (3) by label → dropped (earlier-gap dedup).
        {"label": "supplier power", "query": "a totally different query string",
         "framework": "Porter", "cell": "Supplier"},
    ]

    # fetch_slots caps survivors. 3 novel gaps survive; cap to 2.
    out = select_gaps(gaps, existing, fetch_slots=2)
    assert len(out) == 2
    # Survivors are the first two novel gaps in input order (Supplier, Time decay).
    assert out[0]["label"] == "Supplier power"
    assert out[1]["label"] == "Time decay"
    # Each output is stripped to the SCOPE_SCHEMA angle shape: framework/cell gone.
    for angle in out:
        assert set(angle.keys()) <= {"label", "query", "rationale"}
        assert "framework" not in angle
        assert "cell" not in angle
    # rationale preserved when present (Supplier power had one).
    assert out[0]["rationale"] == "single-fab risk"
    # rationale omitted when absent (Time decay had none).
    assert "rationale" not in out[1]

    # A higher cap admits all 3 distinct novel gaps (the two dupes + intra-dup
    # stay dropped regardless of slots).
    out_all = select_gaps(gaps, existing, fetch_slots=10)
    assert [a["label"] for a in out_all] == ["Supplier power", "Time decay", "Base rates"]

    # Empty gaps → [] (valid; caller proceeds with original angles).
    assert select_gaps([], existing, fetch_slots=5) == []

    # fetch_slots <= 0 → [] (no budget).
    assert select_gaps(gaps, existing, fetch_slots=0) == []
    assert select_gaps(gaps, existing, fetch_slots=-1) == []


def test_backfill_check_flags_unlanded():
    from framework_audit import backfill_check

    gaps = [
        # (1) label absent from confirmed_labels → UNLANDED, tags preserved.
        {"label": "Supplier power", "query": "NVDA TSMC supplier concentration",
         "framework": "Porter", "cell": "Supplier"},
        # (2) label present (case-INSENSITIVE: confirmed has lowercase) → LANDED.
        {"label": "DCF Intrinsic Value", "query": "NVDA DCF WACC terminal growth",
         "framework": "DCF", "cell": "Intrinsic"},
        # (3) label present with surrounding whitespace on confirmed side → LANDED.
        {"label": "Base rates", "query": "semiconductor cycle base rate drawdown",
         "framework": "collective-blind-spot", "cell": "base-rates"},
    ]
    confirmed = ["dcf intrinsic value", "  base rates  ", "Some other landed angle"]

    result = backfill_check(gaps, confirmed)

    # landed_count + unlanded_count sums to total gaps (the conservation rule).
    assert result["landed_count"] + result["unlanded_count"] == len(gaps)
    # Exactly one gap (Supplier power) is unlanded; two landed (case-insensitive).
    assert result["unlanded_count"] == 1
    assert result["landed_count"] == 2

    # The single unlanded entry is Supplier power, with framework + cell preserved.
    unlanded = result["unlanded"]
    assert len(unlanded) == 1
    assert unlanded[0]["label"] == "Supplier power"
    assert unlanded[0]["framework"] == "Porter"
    assert unlanded[0]["cell"] == "Supplier"
    assert unlanded[0]["query"] == "NVDA TSMC supplier concentration"

    # Empty gap_angles → empty unlanded, both counts zero.
    empty = backfill_check([], confirmed)
    assert empty == {"unlanded": [], "landed_count": 0, "unlanded_count": 0}

    # Empty confirmed_labels → ALL gaps unlanded.
    none_landed = backfill_check(gaps, [])
    assert none_landed["unlanded_count"] == len(gaps)
    assert none_landed["landed_count"] == 0
    assert [g["label"] for g in none_landed["unlanded"]] == [
        "Supplier power", "DCF Intrinsic Value", "Base rates"
    ]


def test_backfill_check_preserves_only_present_keys():
    from framework_audit import backfill_check

    # A gap missing `query` carries through only the keys it has — no invented keys.
    gaps = [{"label": "No query gap", "framework": "MECE", "cell": "Branch"}]
    result = backfill_check(gaps, [])
    assert result["unlanded_count"] == 1
    entry = result["unlanded"][0]
    assert entry["label"] == "No query gap"
    assert entry["framework"] == "MECE"
    assert entry["cell"] == "Branch"
    assert "query" not in entry


def test_backfill_subcommand_cli_roundtrip():
    from framework_audit import backfill_check

    payload = {
        "gap_angles": [
            {"label": "Supplier power", "query": "NVDA TSMC supplier concentration",
             "framework": "Porter", "cell": "Supplier"},
            {"label": "DCF Intrinsic Value", "query": "NVDA DCF WACC",
             "framework": "DCF", "cell": "Intrinsic"},
        ],
        "confirmed_labels": ["dcf intrinsic value"],
    }
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "framework_audit.py"), "backfill"],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    assert set(out.keys()) == {"unlanded", "landed_count", "unlanded_count"}
    # The DCF gap landed (case-insensitive); only Supplier power is unlanded.
    assert out["landed_count"] == 1
    assert out["unlanded_count"] == 1
    assert [a["label"] for a in out["unlanded"]] == ["Supplier power"]
    # CLI result matches the in-process function exactly.
    assert out == backfill_check(
        payload["gap_angles"], payload["confirmed_labels"]
    )


def test_select_subcommand_cli_roundtrip():
    from framework_audit import select_gaps

    payload = {
        "gap_angles": [
            {"label": "Supplier power", "query": "NVDA TSMC supplier concentration",
             "framework": "Porter", "cell": "Supplier"},
            {"label": "Moat durability", "query": "dup by label",
             "framework": "Porter", "cell": "Rivalry"},
        ],
        "existing_angles": [
            {"label": "Moat durability", "query": "NVDA moat CUDA lock-in"},
        ],
        "fetch_slots": 5,
    }
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "framework_audit.py"), "select"],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    # stdout shape is {angles: [...]}, mirroring vs_select.py.
    assert set(out.keys()) == {"angles"}
    # The label-dup gap was dropped; only the novel Supplier gap survives.
    assert [a["label"] for a in out["angles"]] == ["Supplier power"]
    # CLI result matches the in-process function exactly.
    assert out["angles"] == select_gaps(
        payload["gap_angles"], payload["existing_angles"], payload["fetch_slots"]
    )
