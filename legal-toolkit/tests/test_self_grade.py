#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["jsonschema>=4.20", "pyyaml>=6.0", "pytest>=7.0"]
# ///
"""Tests for self_grade.py — deterministic-tier rubric.

Strategy: build a "golden" findings.json + outputs-dir that should pass
every deterministic ANS / SRC check, then mutate one field per test to
verify the corresponding criterion fires.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "legal-contract-review"
    / "scripts"
    / "self_grade.py"
)


@pytest.fixture(scope="session")
def self_grade():
    spec = importlib.util.spec_from_file_location("self_grade", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["self_grade"] = module
    spec.loader.exec_module(module)
    return module


DISCLAIMER_BLOCK = """
---

## ⚠️ 重要聲明（Disclaimer）

本文件由 AI 工具（legal-toolkit skill）產出，**非律師意見**：
"""

OVERRIDE_BLOCK = """# Override headed file

> [!danger] ⚠️ 高風險議題——本工具強烈建議諮詢執業律師
>
> 本次 review 偵測到以下高風險訊號：
"""


def _write_outputs(out_dir: Path, *, include_override: bool = True):
    """v0.3.4+ (Phase 1.8): outputs consolidated 5 .md → 2 .md.

    legal.md absorbs former issues + redline + memo-legal + escalation +
    self-grade summary; business.md is the non-lawyer audience file.
    Override banner now lives in legal.md head, not escalation.md.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in ("legal.md", "business.md"):
        content = ""
        if name == "legal.md" and include_override:
            content = OVERRIDE_BLOCK + "\n"
        content += f"# {name}\n\nbody\n" + DISCLAIMER_BLOCK
        (out_dir / name).write_text(content, encoding="utf-8")


def _golden_findings() -> dict:
    """A findings.json that passes every deterministic check."""
    return {
        "contract_metadata": {
            "contract_name": "acme-saas-msa",
            "contract_type": "SaaS",
            "jurisdiction": "TW",
            "mode": "review",
            "pipeline_path": "L0a → L0b → L1 → L2 → L3 → L4 → L5 → L6 → L6.5 → L7",
        },
        "findings": [
            {
                "clause_id": "confidentiality",
                "source_type": "user_playbook",
                "severity": "yellow",
                "walk_away_triggered": False,
                "summary_zh_tw": "雙向保密，期限 3 年，需加 carve-out。",
                "playbook_trace": {
                    "matched_entry_path": "legal-playbook/confidentiality.md",
                },
                "flags": {},
            },
            {
                "clause_id": "limitation-of-liability",
                "variant_id": "mid-deal",
                "source_type": "user_playbook",
                "severity": "red",
                "walk_away_triggered": True,
                "summary_zh_tw": "Cap 太低，僅 3 個月服務費；觸發 mid-deal walk-away。",
                "playbook_trace": {
                    "matched_entry_path": "legal-playbook/limitation-of-liability/mid-deal.md",
                    "matched_variant_outcome": "single",
                },
                "flags": {},
            },
        ],
        "escalations": [
            {
                "clause_id": "limitation-of-liability",
                "escalate_to": "GC",
                "trigger_reason": "walk_away_triggered",
            },
        ],
        "override_triggered": True,
        "placeholder_warnings": [],
        "redlines": [
            {
                "clause_id": "limitation-of-liability",
                "proposed_text_source": "playbook_body",
                "rationale_zh_tw": "提升 cap 至 12 個月服務費並加 carve-out",
            }
        ],
        "crac": {
            "conclusion": "本合約 LoL 條款需修改。",
            "rule": "民法 §247-1 + WorldCC 業界 baseline 12 個月。",
            "analysis": "合約現 cap = 3 個月，低於 baseline。",
            "conclusion_again": "建議改為 12 個月服務費 + IP carve-out。",
        },
        "citations": [
            {
                "citation": "民法 §247-1",
                "type": "statute",
                "supports": "rule",
                "verified": True,
                "url": "https://law.moj.gov.tw/LawClass/LawSingle.aspx?Pcode=B0000001&FLNO=247-1",
            },
            {
                "citation": "智慧財產法院 99 年度民營訴字第 8 號",
                "type": "case",
                "supports": "analysis",
                "verified": True,
            },
        ],
        "summary_business": {
            "why": "對方草擬的合約對我方責任上限過低。",
            "what": "把 LoL cap 從 3 個月提升到 12 個月。",
            "what_if": "若不改，IP 侵權索賠可能讓我方扛 9 個月服務費差額。",
        },
        "cycle_check": {
            "termination_condition": "gaps_zero_at_cycle_2",
        },
        "anatomy": {
            "party_consistency": {"inconsistencies": []},
        },
    }


# ----------------------------------------------------------- golden path


def test_golden_passes_all(self_grade, tmp_path):
    out = tmp_path / "out"
    _write_outputs(out)
    data = _golden_findings()
    report = self_grade.grade(data, out)
    assert report["failed_criteria"] == [], (
        f"Golden findings should pass all deterministic checks; "
        f"failures: {report['failed_criteria']}"
    )
    assert report["answer_score"]["passed"] == report["answer_score"]["total"]
    assert report["source_score"]["passed"] == report["source_score"]["total"]


# ----------------------------------------------------------- ANS failure cases


def test_ans_01_missing_layer(self_grade, tmp_path):
    out = tmp_path / "out"
    _write_outputs(out)
    data = _golden_findings()
    data["contract_metadata"]["pipeline_path"] = "L1 → L2 → L3 → L4 → L5 → L6 → L7"  # drops L0a/L0b/L6.5
    report = self_grade.grade(data, out)
    failed = [f["criterion_id"] for f in report["failed_criteria"]]
    assert "ANS-01" in failed


def test_ans_02_invalid_source_type(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    data["findings"][0]["source_type"] = "external"
    report = self_grade.grade(data, out)
    assert "ANS-02" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_ans_03_no_matched_entry_path(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    data["findings"][0]["playbook_trace"]["matched_entry_path"] = None
    report = self_grade.grade(data, out)
    assert "ANS-03" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_ans_04_high_risk_no_escalation(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    data["escalations"] = []  # red finding present but no escalation
    report = self_grade.grade(data, out)
    assert "ANS-04" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_ans_05_override_missing_banner(self_grade, tmp_path):
    out = tmp_path / "out"
    _write_outputs(out, include_override=False)  # no [!danger] in escalation.md
    data = _golden_findings()  # override_triggered=True
    report = self_grade.grade(data, out)
    assert "ANS-05" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_ans_06_disclaimer_missing(self_grade, tmp_path):
    """v0.3.4+ (Phase 1.8): ANS-06 now checks 2 files (legal.md + business.md)."""
    out = tmp_path / "out"
    out.mkdir()
    for name in ("legal.md", "business.md"):
        (out / name).write_text("# stub\n\nNo footer.\n", encoding="utf-8")
    data = _golden_findings()
    report = self_grade.grade(data, out)
    assert "ANS-06" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_ans_07_placeholder_no_warning(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    data["findings"][0]["flags"]["escalate_to_is_placeholder"] = True
    data["placeholder_warnings"] = []  # missing warning
    report = self_grade.grade(data, out)
    assert "ANS-07" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_ans_08_empty_summary(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    data["findings"][1]["summary_zh_tw"] = "TBD"
    report = self_grade.grade(data, out)
    assert "ANS-08" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_ans_09_invalid_proposed_text_source(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    data["redlines"][0]["proposed_text_source"] = "some_other"
    report = self_grade.grade(data, out)
    assert "ANS-09" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_ans_10_summary_too_long(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    data["summary_business"]["what_if"] = "x" * 200
    report = self_grade.grade(data, out)
    assert "ANS-10" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_ans_12_cycle_max_hit(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    data["cycle_check"]["termination_condition"] = "max_cycles_hit"
    report = self_grade.grade(data, out)
    assert "ANS-12" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_ans_13_no_party_consistency(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    data["anatomy"].pop("party_consistency")
    report = self_grade.grade(data, out)
    assert "ANS-13" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_ans_14_missing_payload(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    data.pop("redlines")
    report = self_grade.grade(data, out)
    assert "ANS-14" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_ans_15_variant_outcome_missing(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    # Strip ABAC variant outcome from variant finding
    data["findings"][1]["playbook_trace"].pop("matched_variant_outcome")
    report = self_grade.grade(data, out)
    assert "ANS-15" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_ans_16_tw_layer_missing(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()  # jurisdiction == TW
    data["contract_metadata"]["pipeline_path"] = "L1 → L2 → L3 → L4 → L5 → L6 → L7"  # no TW overlays
    report = self_grade.grade(data, out)
    assert "ANS-16" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_ans_16_non_tw_skips(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    data["contract_metadata"]["jurisdiction"] = "US"
    data["contract_metadata"]["pipeline_path"] = "L1 → L2 → L3 → L4 → L5 → L6 → L7"
    report = self_grade.grade(data, out)
    failed = {f["criterion_id"] for f in report["failed_criteria"]}
    assert "ANS-16" not in failed  # non-TW jurisdiction skips this check
    assert "ANS-01" not in failed  # also passes because non-TW required layers are L1-L7


def test_ans_17_external_share_not_stripped(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    # Findings have matched_entry_path but external_share_strip_id is unset
    report = self_grade.grade(data, out, external_share=True)
    assert "ANS-17" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_ans_17_external_share_off_skips(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    report = self_grade.grade(data, out, external_share=False)
    assert "ANS-17" not in {f["criterion_id"] for f in report["failed_criteria"]}


# ----------------------------------------------------------- SRC failure cases


def test_src_01_missing_supports(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    data["citations"][0]["supports"] = ""
    report = self_grade.grade(data, out)
    assert "SRC-01" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_src_02_duplicate(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    data["citations"].append({
        "citation": "民法 §247-1",
        "type": "statute",
        "supports": "rule",
        "verified": True,
    })
    report = self_grade.grade(data, out)
    assert "SRC-02" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_src_03_bad_url(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    data["citations"][0]["url"] = "https://random-blog.example.com/post"
    report = self_grade.grade(data, out)
    assert "SRC-03" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_src_04_bad_case_number(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    data["citations"][1]["citation"] = "Some Random Case"
    report = self_grade.grade(data, out)
    assert "SRC-04" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_src_04_blacklist_fabricated_sub_article(self_grade, tmp_path):
    """v0.3.1: fabricated sub-article (民法 §11-1) caught by SRC-04 blacklist."""
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    data["citations"][0]["citation"] = "民法 §11-1"  # does not exist
    report = self_grade.grade(data, out)
    assert "SRC-04" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_src_04_blacklist_yingyemimi_11_1(self_grade, tmp_path):
    """v0.3.1: fabricated 營業秘密法 §11-1 (the actual v0.3.0 dogfood trap)."""
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    data["citations"][0]["citation"] = "營業秘密法 §11-1"
    report = self_grade.grade(data, out)
    failed = {f["criterion_id"] for f in report["failed_criteria"]}
    assert "SRC-04" in failed


def test_src_04_blacklist_deprecated_pdpa_27(self_grade, tmp_path):
    """v0.3.1: deprecated 個資法 §27 (deleted 2025-11-11) caught by blacklist."""
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    data["citations"][0]["citation"] = "個資法 §27"
    report = self_grade.grade(data, out)
    assert "SRC-04" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_src_04_blacklist_long_name_pdpa_27(self_grade, tmp_path):
    """v0.3.1: long name '個人資料保護法 §27' also caught."""
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    data["citations"][0]["citation"] = "個人資料保護法 §27"
    report = self_grade.grade(data, out)
    assert "SRC-04" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_src_04_whitespace_tolerant_blacklist_match(self_grade, tmp_path):
    """v0.3.1: blacklist matching strips whitespace ('民法§11-1' also blocked)."""
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    data["citations"][0]["citation"] = "民法§11-1"  # no space — should still hit
    report = self_grade.grade(data, out)
    assert "SRC-04" in {f["criterion_id"] for f in report["failed_criteria"]}


def test_src_04_valid_statute_passes_through(self_grade, tmp_path):
    """v0.3.1: regression — valid 民法 §247-1 (in blacklist applicability_notes
    but not in blacklist proper) still passes SRC-04."""
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    # Golden already uses 民法 §247-1 — verify it passes
    report = self_grade.grade(data, out)
    assert "SRC-04" not in {f["criterion_id"] for f in report["failed_criteria"]}


def test_src_04_unknown_statute_passes_through(self_grade, tmp_path):
    """v0.3.1: statute not in blacklist (e.g. 海商法 §123) passes format-only check."""
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    data["citations"][0]["citation"] = "海商法 §123"
    report = self_grade.grade(data, out)
    assert "SRC-04" not in {f["criterion_id"] for f in report["failed_criteria"]}


def test_src_05_verified_no_supports(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    # SRC-05 only complains if supports is empty AND verified=true.
    # We need to bypass SRC-01 by NOT making it structurally invalid.
    # Whitespace-only supports counts as empty per the check, while
    # SRC-01 only checks truthy. Add space.
    data["citations"][0]["supports"] = " "
    report = self_grade.grade(data, out)
    failed = {f["criterion_id"] for f in report["failed_criteria"]}
    # Either SRC-01 OR SRC-05 might fire (both are about supports field)
    assert "SRC-05" in failed or "SRC-01" in failed


# ----------------------------------------------------------- self-consistency


def test_ans_11_self_consistency_when_no_failures(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    report = self_grade.grade(data, out)
    # No failures, no failed_criteria list — ANS-11 should pass
    ans_11 = next(r for r in report["answer_score"]["criteria_results"] if r["criterion_id"] == "ANS-11")
    assert ans_11["result"] == "pass"


def test_ans_11_consistency_when_failures(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    data["findings"][0]["source_type"] = "external"  # cause an ANS-02 failure
    report = self_grade.grade(data, out)
    ans_11 = next(r for r in report["answer_score"]["criteria_results"] if r["criterion_id"] == "ANS-11")
    assert ans_11["result"] == "pass"  # has_failures and has_failed_list both True


# ----------------------------------------------------------- markdown rendering


def test_render_markdown_includes_scores(self_grade, tmp_path):
    out = tmp_path / "out"; _write_outputs(out)
    data = _golden_findings()
    report = self_grade.grade(data, out)
    md = self_grade.render_markdown(report, metadata=data["contract_metadata"])
    assert "answer_score" in md
    assert "source_score" in md
    assert "acme-saas-msa" in md
    assert "all deterministic checks pass" in md


# ----------------------------------------------------------- v0.3.4 self_grade JSON update


def test_main_default_writes_self_grade_into_findings_json(self_grade, tmp_path, capsys):
    """v0.3.4+ (Phase 1.8): default behavior updates findings.json#self_grade
    block in-place; does NOT create self-grade.md."""
    import json as _json

    out = tmp_path / "out"
    _write_outputs(out)

    findings_path = tmp_path / "findings.json"
    findings_path.write_text(
        _json.dumps(_golden_findings(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    rc = self_grade.main(
        [
            "--input",
            str(findings_path),
            "--outputs-dir",
            str(out),
        ]
    )
    assert rc == 0

    # findings.json should now have self_grade block
    updated = _json.loads(findings_path.read_text(encoding="utf-8"))
    assert "self_grade" in updated
    assert updated["self_grade"]["answer_score"]["passed"] == updated["self_grade"]["answer_score"]["total"]
    assert updated["self_grade"]["source_score"]["passed"] == updated["self_grade"]["source_score"]["total"]
    assert updated["self_grade"]["failed_criteria"] == []

    # legacy self-grade.md file should NOT be written
    assert not (out / "self-grade.md").exists()


def test_main_format_markdown_prints_no_file(self_grade, tmp_path, capsys):
    """v0.3.4+: --format markdown prints to stdout, does NOT write self-grade.md."""
    import json as _json

    out = tmp_path / "out"
    _write_outputs(out)

    findings_path = tmp_path / "findings.json"
    findings_path.write_text(
        _json.dumps(_golden_findings(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # main() invoked from importable interface uses sys.argv parsing
    rc = self_grade.main(
        [
            "--input",
            str(findings_path),
            "--outputs-dir",
            str(out),
            "--format",
            "markdown",
        ]
    )
    assert rc == 0

    captured = capsys.readouterr()
    assert "answer_score" in captured.out
    assert "source_score" in captured.out

    # findings.json should NOT be mutated (only --format text does that)
    untouched = _json.loads(findings_path.read_text(encoding="utf-8"))
    assert "self_grade" not in untouched

    # And no self-grade.md file written
    assert not (out / "self-grade.md").exists()


def test_ans_05_override_uses_legal_md(self_grade, tmp_path):
    """v0.3.4+: ANS-05 now checks legal.md head for [!danger] (was escalation.md)."""
    out = tmp_path / "out"
    out.mkdir()
    # Write legal.md WITH override banner, business.md without
    (out / "legal.md").write_text(
        "# legal.md\n\n" + OVERRIDE_BLOCK + "\n\nbody\n" + DISCLAIMER_BLOCK,
        encoding="utf-8",
    )
    (out / "business.md").write_text(
        "# business.md\n\nbody\n" + DISCLAIMER_BLOCK, encoding="utf-8"
    )
    data = _golden_findings()  # override_triggered=True
    report = self_grade.grade(data, out)
    failed = {f["criterion_id"] for f in report["failed_criteria"]}
    assert "ANS-05" not in failed  # banner correctly in legal.md head


def test_ans_05_override_missing_in_legal_md_fails(self_grade, tmp_path):
    """v0.3.4+: when override triggered but legal.md lacks the banner."""
    out = tmp_path / "out"
    out.mkdir()
    (out / "legal.md").write_text(
        "# legal.md\n\nbody (no banner)\n" + DISCLAIMER_BLOCK, encoding="utf-8"
    )
    (out / "business.md").write_text(
        "# business.md\n\nbody\n" + DISCLAIMER_BLOCK, encoding="utf-8"
    )
    data = _golden_findings()
    report = self_grade.grade(data, out)
    failed = {f["criterion_id"] for f in report["failed_criteria"]}
    assert "ANS-05" in failed
