#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["jsonschema>=4.20", "pyyaml>=6.0"]
# ///
"""self_grade — run the deterministic tier of answer-criteria +
source-criteria rubrics against a legal-contract-review output set.

Input:
  --input <findings.json>           the structured intermediate the
                                    contract-review pipeline emits
                                    alongside the 6 .md outputs.
                                    Shape: { contract_metadata,
                                             findings[], summary,
                                             redlines[], crac, citations[],
                                             summary_business, escalations[],
                                             override_triggered }
  --outputs-dir <dir>               directory containing issues.md /
                                    redline.md / memo-legal.md /
                                    memo-business.md / escalation.md
                                    (used for file-level checks like
                                    Disclaimer footer presence)

Output:
  - prints summary to stdout
  - writes <outputs-dir>/self-grade.md with full per-criterion result
  - exits 0 if all criteria pass, 1 otherwise

The semantic-tier criteria (ANS-18~20, SRC-06~10) are NOT evaluated here
— the protocol-driven session evaluates those and merges results into
self-grade.md before emit.

Usage:
    self_grade.py --input <path> --outputs-dir <path>
    self_grade.py --input <path> --outputs-dir <path> --format json
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

import yaml


DISCLAIMER_MARKER = "## ⚠️ 重要聲明"
OVERRIDE_MARKER = "[!danger]"

CASE_NUMBER_RE = re.compile(
    r"(最高法院|智慧財產法院|最高行政法院|高等法院|.+地方法院)\s*\d+\s*年度.+第\s*\d+\s*號"
)
STATUTE_RE = re.compile(r"^[一-鿿]+\s*§[0-9-]+(\s*[款項目])?$")
URL_ALLOWLIST_RE = re.compile(
    r"^https?://(law\.moj\.gov\.tw|judgment\.judicial\.gov\.tw|[a-z0-9.-]+\.gov\.tw|mops\.twse\.com\.tw)/"
)

# v0.3.1 — statute blacklist loaded once at module import (assets/statute-articles.json)
_STATUTE_ARTICLES_PATH = (
    Path(__file__).resolve().parent.parent / "assets" / "statute-articles.json"
)
try:
    _STATUTE_BLACKLIST: dict[str, dict] = json.loads(
        _STATUTE_ARTICLES_PATH.read_text(encoding="utf-8")
    ).get("blacklist", {})
except (FileNotFoundError, json.JSONDecodeError):
    _STATUTE_BLACKLIST = {}


def _blacklisted_statute(citation_text: str) -> dict | None:
    """Return blacklist entry if citation matches a known fabrication / deprecated article.

    Matching is whitespace-tolerant: '民法 §11-1' and '民法§11-1' both match
    the key '民法 §11-1' in the blacklist JSON.
    """
    normalised = "".join(citation_text.split())
    for key, entry in _STATUTE_BLACKLIST.items():
        if "".join(key.split()) == normalised:
            return entry
    return None
PIPELINE_LAYERS_TW = {"L0a", "L0b", "L1", "L2", "L3", "L4", "L5", "L6", "L6.5", "L7"}
PIPELINE_LAYERS_NON_TW = {"L1", "L2", "L3", "L4", "L5", "L6", "L7"}
PIPELINE_LAYERS_NDA = {"L1", "L4", "L5", "L6", "L7"}

SOURCE_TYPE_ENUM = {"user_playbook", "bundled_fallback", "advisory"}
RISK_ENUM = {"green", "yellow", "red"}
PROPOSED_TEXT_SOURCE_ENUM = {"playbook_body", "llm_generated"}
CITATION_TYPE_ENUM = {"statute", "case", "regulation", "authority_letter", "scholarly"}


# ----------------------------------------------------------- I/O helpers


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _emit(criterion_id: str, criterion_zh_tw: str, tier: str, ok: bool, evidence: str) -> dict:
    return {
        "criterion_id": criterion_id,
        "criterion_zh_tw": criterion_zh_tw,
        "tier": tier,
        "result": "pass" if ok else "fail",
        "evidence": evidence,
    }


# ----------------------------------------------------------- answer-criteria checks


def _check_ans_01(findings_data: dict) -> dict:
    """All pipeline layers run per mode rules."""
    meta = findings_data.get("contract_metadata", {})
    mode = (meta.get("mode") or "review").lower()
    jurisdiction = (meta.get("jurisdiction") or "TW").upper()
    pipeline_path = meta.get("pipeline_path", "")
    if mode == "nda":
        required = PIPELINE_LAYERS_NDA
    elif jurisdiction == "TW":
        required = PIPELINE_LAYERS_TW
    else:
        required = PIPELINE_LAYERS_NON_TW
    missing = [layer for layer in required if layer not in pipeline_path]
    return _emit(
        "ANS-01",
        "全部 7 層依照 mode 規則執行",
        "deterministic",
        not missing,
        f"missing: {missing}" if missing else f"pipeline_path covers required {sorted(required)}",
    )


def _check_ans_02(findings_data: dict) -> dict:
    findings = findings_data.get("findings", [])
    invalid = [
        i for i, f in enumerate(findings)
        if f.get("source_type") not in SOURCE_TYPE_ENUM
    ]
    return _emit(
        "ANS-02",
        "每條 finding 都帶 valid source_type",
        "deterministic",
        not invalid,
        f"invalid indices: {invalid}" if invalid else f"all {len(findings)} findings have valid source_type",
    )


def _check_ans_03(findings_data: dict) -> dict:
    findings = findings_data.get("findings", [])
    leaks = []
    for i, f in enumerate(findings):
        if f.get("source_type") != "advisory":
            path = (f.get("playbook_trace") or {}).get("matched_entry_path")
            if not path:
                leaks.append(i)
    return _emit(
        "ANS-03",
        "non-advisory finding 都有 matched_entry_path",
        "deterministic",
        not leaks,
        f"missing matched_entry_path on findings: {leaks}" if leaks else "all non-advisory findings traced",
    )


def _is_high_risk(f: dict) -> bool:
    if f.get("severity") == "red":
        return True
    if f.get("walk_away_triggered") is True:
        return True
    if (f.get("flags") or {}).get("low_confidence") is True:
        return True
    return False


def _check_ans_04(findings_data: dict) -> dict:
    findings = findings_data.get("findings", [])
    escalations = findings_data.get("escalations", [])
    escalation_ids = {e.get("clause_id") for e in escalations}
    missing = [
        f.get("clause_id") for f in findings
        if _is_high_risk(f) and f.get("clause_id") not in escalation_ids
    ]
    return _emit(
        "ANS-04",
        "高風險 finding 都有 escalation row",
        "deterministic",
        not missing,
        f"missing escalation rows for clause_ids: {missing}" if missing else "all high-risk findings have escalation rows",
    )


def _check_ans_05(outputs_dir: Path, findings_data: dict) -> dict:
    triggered = findings_data.get("override_triggered", False) is True
    f = outputs_dir / "escalation.md"
    if not triggered:
        return _emit("ANS-05", "Escalation Override 紅字 banner 出現", "deterministic", True, "override not required")
    if not f.exists():
        return _emit("ANS-05", "Escalation Override 紅字 banner 出現", "deterministic", False, "escalation.md missing")
    head = "\n".join(_read_text(f).splitlines()[:30])
    ok = OVERRIDE_MARKER in head
    return _emit(
        "ANS-05",
        "Escalation Override 紅字 banner 出現在高風險輸出檔頭",
        "deterministic",
        ok,
        "[!danger] callout found in header" if ok else "[!danger] missing from header",
    )


OUTPUT_FILES = ["issues.md", "redline.md", "memo-legal.md", "memo-business.md", "escalation.md"]


def _check_ans_06(outputs_dir: Path) -> dict:
    missing = []
    for name in OUTPUT_FILES:
        f = outputs_dir / name
        if not f.exists():
            missing.append(f"{name}:missing")
            continue
        tail = "\n".join(_read_text(f).splitlines()[-50:])
        if DISCLAIMER_MARKER not in tail:
            missing.append(f"{name}:no_disclaimer")
    return _emit(
        "ANS-06",
        "每份輸出檔尾含 Mandatory Disclaimer",
        "deterministic",
        not missing,
        ", ".join(missing) if missing else "all 5 outputs have Disclaimer footer",
    )


def _check_ans_07(findings_data: dict) -> dict:
    findings = findings_data.get("findings", [])
    has_placeholder = any(
        (f.get("flags") or {}).get("escalate_to_is_placeholder") is True
        for f in findings
    )
    warnings = findings_data.get("placeholder_warnings", []) or []
    if not has_placeholder:
        return _emit("ANS-07", "placeholder warning 顯示", "deterministic", True, "no placeholder findings")
    ok = len(warnings) > 0
    return _emit(
        "ANS-07",
        "placeholder warning 顯示給使用者",
        "deterministic",
        ok,
        "warning emitted" if ok else "placeholder finding present but no warning emitted",
    )


def _check_ans_08(findings_data: dict) -> dict:
    findings = findings_data.get("findings", [])
    placeholders = ("TBD", "[REPLACE_ME]", "")
    bad = [
        i for i, f in enumerate(findings)
        if (f.get("summary_zh_tw") or "").strip() in placeholders
    ]
    return _emit(
        "ANS-08",
        "每條 finding 含 zh-TW summary",
        "deterministic",
        not bad,
        f"empty / placeholder summary on findings: {bad}" if bad else "all findings have substantive summary",
    )


def _check_ans_09(findings_data: dict) -> dict:
    redlines = findings_data.get("redlines", [])
    bad = [
        i for i, r in enumerate(redlines)
        if r.get("proposed_text_source") not in PROPOSED_TEXT_SOURCE_ENUM
    ]
    return _emit(
        "ANS-09",
        "redline.md proposed_text_source 明確標示",
        "deterministic",
        not bad,
        f"missing/invalid source on redlines: {bad}" if bad else "all redlines have source tag",
    )


def _check_ans_10(findings_data: dict) -> dict:
    summary = findings_data.get("summary_business", {}) or {}
    required_keys = ("why", "what", "what_if")
    missing = [k for k in required_keys if not (summary.get(k) or "").strip()]
    too_long = [k for k in required_keys if len((summary.get(k) or "")) > 80]
    bad = missing + [f"{k}:>80chars" for k in too_long]
    return _emit(
        "ANS-10",
        "memo-business.md 三句結構完整",
        "deterministic",
        not bad,
        ", ".join(bad) if bad else "Why/What/What-if all present and ≤80 chars",
    )


def _check_ans_11(report: dict) -> dict:
    """Self-consistency: failed_criteria non-empty iff scores < total."""
    answer_passed = report["answer_score"]["passed"]
    answer_total = report["answer_score"]["total"]
    source_passed = report["source_score"]["passed"]
    source_total = report["source_score"]["total"]
    has_failures = (answer_passed < answer_total) or (source_passed < source_total)
    has_failed_list = len(report.get("failed_criteria", [])) > 0
    ok = has_failures == has_failed_list
    return _emit(
        "ANS-11",
        "self-grade.md 不藏 failed_criteria",
        "deterministic",
        ok,
        f"has_failures={has_failures} has_failed_list={has_failed_list}",
    )


def _check_ans_12(findings_data: dict) -> dict:
    cyc = (findings_data.get("cycle_check") or {})
    term = cyc.get("termination_condition", "")
    ok = term.startswith("gaps_zero_at_cycle_")
    return _emit(
        "ANS-12",
        "Pipeline 沒跳步 — L6 cycle 收斂",
        "deterministic",
        ok,
        term or "no cycle_check.termination_condition recorded",
    )


def _check_ans_13(findings_data: dict) -> dict:
    anatomy = findings_data.get("anatomy") or {}
    pc = anatomy.get("party_consistency")
    ok = pc is not None
    return _emit(
        "ANS-13",
        "Party-consistency check ran (L2)",
        "deterministic",
        ok,
        f"inconsistencies recorded: {len((pc or {}).get('inconsistencies', []))}" if ok else "L2 party_consistency missing",
    )


def _check_ans_14(findings_data: dict) -> dict:
    """We can't deeply re-validate every output schema here without the
    full structured payload — but verify the top-level shape of
    findings_data carries the expected keys for the 6 outputs."""
    required_top = ("contract_metadata", "findings", "redlines", "crac", "summary_business", "escalations")
    missing = [k for k in required_top if k not in findings_data]
    return _emit(
        "ANS-14",
        "output-schema 驗證通過",
        "deterministic",
        not missing,
        f"top-level keys missing: {missing}" if missing else "all 6 output payloads present",
    )


def _check_ans_15(findings_data: dict) -> dict:
    findings = findings_data.get("findings", [])
    # only findings that came from variant-folder entries need an outcome
    variant_findings = [
        f for f in findings
        if f.get("variant_id") is not None
    ]
    missing = []
    for f in variant_findings:
        if not (f.get("playbook_trace") or {}).get("matched_variant_outcome"):
            missing.append(f.get("clause_id"))
    return _emit(
        "ANS-15",
        "ABAC pre-filter logged variant decision",
        "deterministic",
        not missing,
        f"missing matched_variant_outcome on: {missing}" if missing else f"all {len(variant_findings)} variant findings logged",
    )


def _check_ans_16(findings_data: dict) -> dict:
    meta = findings_data.get("contract_metadata") or {}
    jurisdiction = (meta.get("jurisdiction") or "").upper()
    if jurisdiction != "TW":
        return _emit("ANS-16", "TW jurisdiction → L0a + L0b + L6.5 all fired", "deterministic", True, f"non-TW jurisdiction: {jurisdiction}")
    pipeline_path = meta.get("pipeline_path", "")
    missing = [layer for layer in ("L0a", "L0b", "L6.5") if layer not in pipeline_path]
    return _emit(
        "ANS-16",
        "TW jurisdiction → L0a + L0b + L6.5 all fired",
        "deterministic",
        not missing,
        f"TW overlay layers missing: {missing}" if missing else "all 3 TW overlays fired",
    )


def _check_ans_17(findings_data: dict, external_share: bool) -> dict:
    if not external_share:
        return _emit("ANS-17", "external-share strip applied", "deterministic", True, "--external-share not set")
    findings = findings_data.get("findings", [])
    not_stripped = []
    for f in findings:
        trace = f.get("playbook_trace") or {}
        if trace.get("matched_entry_path") and not trace.get("external_share_strip_id"):
            not_stripped.append(f.get("clause_id"))
    return _emit(
        "ANS-17",
        "--external-share flag 正確 strip",
        "deterministic",
        not not_stripped,
        f"matched_entry_path not stripped on: {not_stripped}" if not_stripped else "all paths stripped",
    )


# ----------------------------------------------------------- source-criteria checks


def _check_src_01(findings_data: dict) -> dict:
    citations = findings_data.get("citations", []) or []
    bad = []
    for i, c in enumerate(citations):
        if not c.get("citation"):
            bad.append(f"#{i}:no_citation")
        if c.get("type") not in CITATION_TYPE_ENUM:
            bad.append(f"#{i}:bad_type({c.get('type')})")
        if not c.get("supports"):
            bad.append(f"#{i}:no_supports")
    return _emit(
        "SRC-01",
        "citation 結構符合 schema",
        "deterministic",
        not bad,
        ", ".join(bad) if bad else f"all {len(citations)} citations structurally OK",
    )


def _check_src_02(findings_data: dict) -> dict:
    citations = findings_data.get("citations", []) or []
    seen = set()
    dups = []
    for c in citations:
        key = (c.get("citation"), c.get("supports"))
        if key in seen and key != (None, None):
            dups.append(key)
        else:
            seen.add(key)
    return _emit(
        "SRC-02",
        "citation 沒有重複",
        "deterministic",
        not dups,
        f"duplicates: {dups}" if dups else "all citations unique",
    )


def _check_src_03(findings_data: dict) -> dict:
    citations = findings_data.get("citations", []) or []
    bad = []
    for c in citations:
        url = c.get("url")
        if url and not URL_ALLOWLIST_RE.match(url):
            bad.append(url)
    return _emit(
        "SRC-03",
        "URL 指向已知主管機關 domain",
        "deterministic",
        not bad,
        f"out-of-allowlist URLs: {bad}" if bad else "all URLs from gov / judicial domains",
    )


def _check_src_04(findings_data: dict) -> dict:
    """Format check + v0.3.1 statute blacklist (known fabricated / deprecated articles).

    Statutes not in blacklist pass through to format check only — v0.3.1 ships
    a minimum viable blacklist (assets/statute-articles.json); comprehensive
    whitelist deferred to Phase 1.7+.
    """
    citations = findings_data.get("citations", []) or []
    bad = []
    for i, c in enumerate(citations):
        t = c.get("type")
        text = (c.get("citation") or "").strip()
        if t == "case" and not CASE_NUMBER_RE.search(text):
            bad.append(f"#{i}:case_format({text!r})")
        elif t == "statute":
            if not STATUTE_RE.match(text):
                bad.append(f"#{i}:statute_format({text!r})")
                continue
            blacklisted = _blacklisted_statute(text)
            if blacklisted is not None:
                reason = blacklisted.get("reason", "blacklisted")
                alt = blacklisted.get("correct_alternative", "")
                bad.append(
                    f"#{i}:statute_blacklist({text!r}: {reason}; correct: {alt})"
                )
    return _emit(
        "SRC-04",
        "citation 沒有 obvious 結構失敗 + 沒踩 blacklist (fabricated / deprecated)",
        "deterministic",
        not bad,
        ", ".join(bad) if bad else "case + statute formats all OK; no blacklist hits",
    )


def _check_src_05(findings_data: dict) -> dict:
    citations = findings_data.get("citations", []) or []
    bad = []
    for i, c in enumerate(citations):
        if c.get("verified") is True and not (c.get("supports") or "").strip():
            bad.append(i)
    return _emit(
        "SRC-05",
        "verified citation 有 supports",
        "deterministic",
        not bad,
        f"verified-but-no-supports: {bad}" if bad else "all verified citations have supports",
    )


# ----------------------------------------------------------- top-level orchestration


ANS_CHECKS = [
    ("ans_01", lambda data, out, esh: _check_ans_01(data)),
    ("ans_02", lambda data, out, esh: _check_ans_02(data)),
    ("ans_03", lambda data, out, esh: _check_ans_03(data)),
    ("ans_04", lambda data, out, esh: _check_ans_04(data)),
    ("ans_05", lambda data, out, esh: _check_ans_05(out, data)),
    ("ans_06", lambda data, out, esh: _check_ans_06(out)),
    ("ans_07", lambda data, out, esh: _check_ans_07(data)),
    ("ans_08", lambda data, out, esh: _check_ans_08(data)),
    ("ans_09", lambda data, out, esh: _check_ans_09(data)),
    ("ans_10", lambda data, out, esh: _check_ans_10(data)),
    ("ans_12", lambda data, out, esh: _check_ans_12(data)),
    ("ans_13", lambda data, out, esh: _check_ans_13(data)),
    ("ans_14", lambda data, out, esh: _check_ans_14(data)),
    ("ans_15", lambda data, out, esh: _check_ans_15(data)),
    ("ans_16", lambda data, out, esh: _check_ans_16(data)),
    ("ans_17", lambda data, out, esh: _check_ans_17(data, esh)),
]

SRC_CHECKS = [
    ("src_01", _check_src_01),
    ("src_02", _check_src_02),
    ("src_03", _check_src_03),
    ("src_04", _check_src_04),
    ("src_05", _check_src_05),
]


def grade(findings_data: dict, outputs_dir: Path, external_share: bool = False) -> dict:
    """Run all deterministic checks; return grade report dict."""
    answer_results = [fn(findings_data, outputs_dir, external_share) for _, fn in ANS_CHECKS]
    source_results = [fn(findings_data) for _, fn in SRC_CHECKS]

    answer_total = len(answer_results)
    answer_passed = sum(1 for r in answer_results if r["result"] == "pass")
    source_total = len(source_results) if (findings_data.get("citations") or []) else 0
    source_passed = sum(1 for r in source_results if r["result"] == "pass") if source_total else 0

    failed = []
    for r in answer_results:
        if r["result"] == "fail":
            failed.append({"domain": "answer", "criterion_id": r["criterion_id"], "explanation_zh_tw": r["evidence"]})
    if source_total:
        for r in source_results:
            if r["result"] == "fail":
                failed.append({"domain": "source", "criterion_id": r["criterion_id"], "explanation_zh_tw": r["evidence"]})

    report = {
        "answer_score": {
            "passed": answer_passed,
            "total": answer_total,
            "criteria_results": answer_results,
        },
        "source_score": {
            "passed": source_passed,
            "total": source_total,
            "criteria_results": source_results if source_total else [],
        },
        "failed_criteria": failed,
        "external_share": external_share,
    }
    # Run ANS-11 self-consistency check now that totals are in
    ans_11 = _check_ans_11(report)
    report["answer_score"]["criteria_results"].append(ans_11)
    report["answer_score"]["total"] += 1
    if ans_11["result"] == "pass":
        report["answer_score"]["passed"] += 1
    else:
        report["failed_criteria"].append(
            {"domain": "answer", "criterion_id": "ANS-11", "explanation_zh_tw": ans_11["evidence"]}
        )
    return report


def render_markdown(report: dict, metadata: dict | None = None) -> str:
    """Render the report as a self-grade.md document."""
    md_lines = ["# self-grade.md", ""]
    if metadata:
        md_lines.extend([
            f"**Contract**: {metadata.get('contract_name', '<unknown>')}",
            f"**Contract type**: {metadata.get('contract_type', '<unknown>')}",
            f"**Jurisdiction**: {metadata.get('jurisdiction', '<unknown>')}",
            f"**Pipeline path**: {metadata.get('pipeline_path', '<unknown>')}",
            f"**Generated**: {_dt.datetime.now().isoformat(timespec='seconds')}",
            "",
        ])
    md_lines.extend([
        "## Scores (deterministic tier only — semantic tier filled by session evaluator)",
        "",
        f"- **answer_score**: {report['answer_score']['passed']} / {report['answer_score']['total']}",
        f"- **source_score**: {report['source_score']['passed']} / {report['source_score']['total']}",
        "",
        "## Failed criteria",
        "",
    ])
    if not report["failed_criteria"]:
        md_lines.append("(none — all deterministic checks pass)")
    else:
        for fc in report["failed_criteria"]:
            md_lines.append(f"- **{fc['criterion_id']}** ({fc['domain']}): {fc['explanation_zh_tw']}")
    md_lines.extend([
        "",
        "## Full per-criterion breakdown",
        "",
        "### answer_score (deterministic)",
        "",
        "| ID | tier | result | evidence |",
        "|---|---|---|---|",
    ])
    for r in report["answer_score"]["criteria_results"]:
        md_lines.append(f"| {r['criterion_id']} | {r['tier']} | {r['result']} | {r['evidence']} |")
    md_lines.extend([
        "",
        "### source_score (deterministic)",
        "",
        "| ID | tier | result | evidence |",
        "|---|---|---|---|",
    ])
    for r in report["source_score"]["criteria_results"]:
        md_lines.append(f"| {r['criterion_id']} | {r['tier']} | {r['result']} | {r['evidence']} |")
    md_lines.extend([
        "",
        "---",
        "",
        "> **Note**: This file currently contains ONLY the deterministic-tier",
        "> rubric results. The semantic-tier (ANS-18~20, SRC-06~10) is",
        "> filled in by the protocol-driven session evaluator and merged",
        "> into this file before final emit.",
        "",
    ])
    return "\n".join(md_lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", required=True, type=Path, help="path to findings.json")
    parser.add_argument("--outputs-dir", required=True, type=Path, help="directory with .md outputs")
    parser.add_argument(
        "--external-share",
        action="store_true",
        help="signal that --external-share was passed at contract-review time",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json", "markdown"),
        default="text",
        help="text (summary), json (full report), markdown (writes self-grade.md)",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        print(f"self_grade: input missing: {args.input}", file=sys.stderr)
        return 2
    if not args.outputs_dir.is_dir():
        print(f"self_grade: outputs-dir missing: {args.outputs_dir}", file=sys.stderr)
        return 2

    findings_data = _read_json(args.input)
    report = grade(findings_data, args.outputs_dir, external_share=args.external_share)

    if args.format == "json":
        json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    elif args.format == "markdown":
        md = render_markdown(report, metadata=findings_data.get("contract_metadata"))
        out_file = args.outputs_dir / "self-grade.md"
        out_file.write_text(md, encoding="utf-8")
        print(f"wrote {out_file}")
    else:
        print(
            f"answer_score: {report['answer_score']['passed']}/{report['answer_score']['total']}"
        )
        print(
            f"source_score: {report['source_score']['passed']}/{report['source_score']['total']}"
        )
        if report["failed_criteria"]:
            print(f"\nFailed criteria ({len(report['failed_criteria'])}):")
            for fc in report["failed_criteria"]:
                print(f"  {fc['criterion_id']} ({fc['domain']}): {fc['explanation_zh_tw']}")
        else:
            print("\nAll deterministic checks PASS.")
    return 0 if not report["failed_criteria"] else 1


if __name__ == "__main__":
    sys.exit(main())
