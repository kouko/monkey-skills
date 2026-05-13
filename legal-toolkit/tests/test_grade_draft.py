"""Tests for legal-document-draft/scripts/grade_draft.py.

grade_draft.py runs deterministic structural checks on an output
directory and emits PASS / FAIL with a reason list.
"""
from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "legal-toolkit" / "skills" / "legal-document-draft" / "scripts"
FIXTURES = REPO / "legal-toolkit" / "tests" / "fixtures-document-draft"
SAMPLE = FIXTURES / "draft-output-sample-privacy"


def _load():
    spec = importlib.util.spec_from_file_location("grade_draft", SCRIPTS / "grade_draft.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _copy_sample(tmp_path: Path) -> Path:
    target = tmp_path / "2026-05-13T120000-privacy"
    shutil.copytree(SAMPLE, target)
    return target


# ---------------------------------------------------------- T-G-1: complete draft PASS
def test_complete_draft_passes(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path)

    result = grade.grade_draft(output_dir, mode="privacy")

    assert result.passed is True, f"expected PASS, got reasons: {result.reasons}"


# ---------------------------------------------------------- T-G-2: unresolved variable FAIL
def test_orphan_variable_fails(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path)
    doc = output_dir / "privacy.md"
    doc.write_text(doc.read_text(encoding="utf-8") + "\n\n## 11. 額外 {{unfilled_section}}", encoding="utf-8")

    result = grade.grade_draft(output_dir, mode="privacy")

    assert result.passed is False
    assert any("orphan" in r.lower() or "{{" in r for r in result.reasons)


# ---------------------------------------------------------- T-G-3: missing verdict FAIL
def test_missing_checklist_verdict_fails(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path)
    compliance = output_dir / "compliance.md"
    # Strip one PASS verdict from a checklist line
    text = compliance.read_text(encoding="utf-8")
    text = text.replace("§8 第一項第一款 — 公開揭露蒐集者 (公司) 名稱 — **PASS**", "§8 第一項第一款 — 公開揭露蒐集者 (公司) 名稱")
    compliance.write_text(text, encoding="utf-8")

    result = grade.grade_draft(output_dir, mode="privacy")

    assert result.passed is False
    assert any("verdict" in r.lower() for r in result.reasons)


# ---------------------------------------------------------- T-G-4: fabricated TBD FAIL
def test_fabricated_tbd_fails(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path)
    compliance = output_dir / "compliance.md"
    text = compliance.read_text(encoding="utf-8")
    # Insert a TBD that doesn't match the canonical OPEN list
    text = text.replace(
        "- [ ] §20-1 — Audit framework 段落 — **TBD_PDPA_audit_framework**",
        "- [ ] §99 — 某虛構條文 — **TBD_FABRICATED_ITEM**",
    )
    compliance.write_text(text, encoding="utf-8")

    result = grade.grade_draft(output_dir, mode="privacy")

    assert result.passed is False
    assert any("tbd" in r.lower() and ("fabricated" in r.lower() or "canonical" in r.lower()) for r in result.reasons)


# ---------------------------------------------------------- T-G-5: truncated document FAIL
def test_truncated_document_fails(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path)
    doc = output_dir / "privacy.md"
    doc.write_text("# 隱私權政策\n\n太短了。", encoding="utf-8")  # < min_bytes

    result = grade.grade_draft(output_dir, mode="privacy")

    assert result.passed is False
    assert any("truncat" in r.lower() or "byte" in r.lower() for r in result.reasons)


# ---------------------------------------------------------- T-G-6: missing output file
def test_missing_output_file_fails(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path)
    (output_dir / "compliance.md").unlink()

    result = grade.grade_draft(output_dir, mode="privacy")

    assert result.passed is False
    assert any("compliance" in r.lower() and ("missing" in r.lower() or "not found" in r.lower()) for r in result.reasons)


# ---------------------------------------------------------- T-G-7: Path A anti-pattern (民法 §12 age 20 legacy)
@pytest.mark.parametrize(
    "leak,fragment",
    [
        ("age_20_full_width", "未滿二十歲限制行為能力人"),
        ("age_20_arabic", "未滿 20 歲限制行為能力人"),
        ("breach_72hr_chinese", "本公司於 72 小時內通報"),
        ("breach_72hr_english", "notify within 72 hours"),
        ("gdpr_controller_processor", "controller-processor model"),
        ("gdpr_data_controller_zh", "依資料控管者規定"),
    ],
)
def test_path_a_antipattern_fails(tmp_path, leak, fragment):
    grade = _load()
    output_dir = _copy_sample(tmp_path)
    doc = output_dir / "privacy.md"
    doc.write_text(doc.read_text(encoding="utf-8") + f"\n\n## 違規測試 ({leak})\n{fragment}\n", encoding="utf-8")

    result = grade.grade_draft(output_dir, mode="privacy")

    assert result.passed is False, f"expected FAIL for leak={leak}"
    assert any("path a violation" in r.lower() for r in result.reasons), (
        f"expected 'Path A violation' message for leak={leak}, got: {result.reasons}"
    )


# ---------------------------------------------------------- T-G-8: anti-pattern only fails on doc, not compliance
def test_antipattern_in_compliance_only_does_not_fail(tmp_path):
    """compliance.md is the internal review — it MAY cite anti-patterns
    in explanatory 'NOT X' form (e.g., 'use 即時 (NOT 72hr GDPR)')."""
    grade = _load()
    output_dir = _copy_sample(tmp_path)
    compliance = output_dir / "compliance.md"
    compliance.write_text(
        compliance.read_text(encoding="utf-8") + "\n\nNOTE: confirmed 即時 used; NOT 72 小時 GDPR.\n",
        encoding="utf-8",
    )

    result = grade.grade_draft(output_dir, mode="privacy")

    assert result.passed is True, f"compliance-only anti-pattern citation should pass; got reasons: {result.reasons}"
