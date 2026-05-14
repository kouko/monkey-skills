"""Tests for legal-incident-response/scripts/grade_response.py.

grade_response.py is a deterministic structural grader. Per-path branch
on top of common structural floor (2-file present / ISO timeline /
TBD canonical / Path A anti-patterns).
"""
from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "legal-toolkit" / "skills" / "legal-incident-response" / "scripts"
FIXTURES = REPO / "legal-toolkit" / "tests" / "fixtures-incident-response"


def _load():
    spec = importlib.util.spec_from_file_location("grade_response", SCRIPTS / "grade_response.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _copy_sample(tmp_path: Path, name: str) -> Path:
    target = tmp_path / "2026-05-13T1430-incident-pii-breach"
    shutil.copytree(FIXTURES / name, target)
    return target


# ---------------------------------------------------------- T-IR-GR-1: complete pii-breach PASS
def test_complete_pii_breach_passes(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path, "draft-output-sample-pii-breach")
    result = grade.grade_response(output_dir, path_type="pii-breach")
    assert result.passed is True, f"expected PASS, got reasons: {result.reasons}"


# ---------------------------------------------------------- T-IR-GR-2: missing legal.md FAIL
def test_missing_legal_md_fails(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path, "draft-output-sample-pii-breach")
    (output_dir / "legal.md").unlink()
    result = grade.grade_response(output_dir, path_type="pii-breach")
    assert result.passed is False
    assert any("legal.md" in r and "missing" in r.lower() for r in result.reasons)


# ---------------------------------------------------------- T-IR-GR-3: missing business.md FAIL
def test_missing_business_md_fails(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path, "draft-output-sample-pii-breach")
    (output_dir / "business.md").unlink()
    result = grade.grade_response(output_dir, path_type="pii-breach")
    assert result.passed is False
    assert any("business.md" in r and "missing" in r.lower() for r in result.reasons)


# ---------------------------------------------------------- T-IR-GR-4: unknown path_type FAIL
def test_unknown_path_type_fails(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path, "draft-output-sample-pii-breach")
    result = grade.grade_response(output_dir, path_type="bogus-path")
    assert result.passed is False
    assert any("unknown path_type" in r.lower() for r in result.reasons)


# ---------------------------------------------------------- T-IR-GR-5: missing timeline section FAIL
def test_missing_timeline_fails(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path, "draft-output-sample-pii-breach")
    legal = output_dir / "legal.md"
    text = legal.read_text(encoding="utf-8")
    text = text.replace("## §時間軸", "## §[REDACTED]")
    legal.write_text(text, encoding="utf-8")
    result = grade.grade_response(output_dir, path_type="pii-breach")
    assert result.passed is False
    assert any("timeline" in r.lower() or "時間軸" in r for r in result.reasons)


# ---------------------------------------------------------- T-IR-GR-6: fabricated TBD FAIL
def test_fabricated_tbd_fails(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path, "draft-output-sample-pii-breach")
    legal = output_dir / "legal.md"
    text = legal.read_text(encoding="utf-8")
    text += "\n\n- TBD_FAKE_ID — 虛構的 TBD\n"
    legal.write_text(text, encoding="utf-8")
    result = grade.grade_response(output_dir, path_type="pii-breach")
    assert result.passed is False
    assert any("tbd" in r.lower() and ("fabricated" in r.lower() or "canonical" in r.lower()) for r in result.reasons)


# ---------------------------------------------------------- T-IR-GR-7..10: Path A anti-pattern
@pytest.mark.parametrize(
    "leak,fragment",
    [
        ("age_20", "未滿二十歲限制行為能力人"),
        ("breach_72hr", "72 小時內通報"),
        ("gdpr_controller", "controller-processor model"),
        ("gdpr_zh", "依資料控管者規定"),
    ],
)
def test_path_a_antipattern_in_legal_md_fails(tmp_path, leak, fragment):
    grade = _load()
    output_dir = _copy_sample(tmp_path, "draft-output-sample-pii-breach")
    legal = output_dir / "legal.md"
    legal.write_text(legal.read_text(encoding="utf-8") + f"\n\n## 違規測試 ({leak})\n{fragment}\n", encoding="utf-8")
    result = grade.grade_response(output_dir, path_type="pii-breach")
    assert result.passed is False
    assert any("path a violation" in r.lower() for r in result.reasons)


# ---------------------------------------------------------- T-IR-GR-11: authority-letter PASS
def test_complete_authority_letter_passes(tmp_path):
    grade = _load()
    target = tmp_path / "2026-05-13T1430-incident-authority-letter"
    shutil.copytree(FIXTURES / "draft-output-sample-authority-letter", target)
    result = grade.grade_response(target, path_type="authority-letter")
    assert result.passed is True, f"expected PASS, got reasons: {result.reasons}"


# ---------------------------------------------------------- T-IR-GR-12: contract-breach handoff present PASS
def test_complete_contract_breach_passes(tmp_path):
    grade = _load()
    target = tmp_path / "2026-05-13T1430-incident-contract-breach"
    shutil.copytree(FIXTURES / "draft-output-sample-contract-breach", target)
    result = grade.grade_response(target, path_type="contract-breach")
    assert result.passed is True, f"expected PASS, got reasons: {result.reasons}"


# ---------------------------------------------------------- T-IR-GR-13: contract-breach missing handoff FAIL
def test_contract_breach_missing_handoff_fails(tmp_path):
    grade = _load()
    target = tmp_path / "2026-05-13T1430-incident-contract-breach"
    shutil.copytree(FIXTURES / "draft-output-sample-contract-breach", target)
    (target / "handoff-context.json").unlink()
    result = grade.grade_response(target, path_type="contract-breach")
    assert result.passed is False
    assert any("handoff" in r.lower() for r in result.reasons)


# ---------------------------------------------------------- T-IR-GR-14: truncated business.md FAIL
def test_truncated_business_md_fails(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path, "draft-output-sample-pii-breach")
    (output_dir / "business.md").write_text("# tiny\n太短了。", encoding="utf-8")  # < 200 bytes
    result = grade.grade_response(output_dir, path_type="pii-breach")
    assert result.passed is False
    assert any("business.md" in r.lower() and ("truncat" in r.lower() or "byte" in r.lower()) for r in result.reasons)


# ---------------------------------------------------------- T-IR-GR-15: fabricated TBD in business.md FAIL
def test_fabricated_tbd_in_business_md_fails(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path, "draft-output-sample-pii-breach")
    business = output_dir / "business.md"
    business.write_text(business.read_text(encoding="utf-8") + "\n\n- TBD_FAKE_BUSINESS — 業務側虛構 TBD\n", encoding="utf-8")
    result = grade.grade_response(output_dir, path_type="pii-breach")
    assert result.passed is False
    assert any("fabricated" in r.lower() or "canonical" in r.lower() for r in result.reasons)


# ---------------------------------------------------------- T-IR-GR-16: contract-breach handoff missing urgency_level FAIL
def test_contract_breach_handoff_missing_urgency_fails(tmp_path):
    import json
    grade = _load()
    target = tmp_path / "2026-05-13T1430-incident-contract-breach"
    shutil.copytree(FIXTURES / "draft-output-sample-contract-breach", target)
    handoff_path = target / "handoff-context.json"
    data = json.loads(handoff_path.read_text(encoding="utf-8"))
    data.pop("urgency_level")
    handoff_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    result = grade.grade_response(target, path_type="contract-breach")
    assert result.passed is False
    assert any("urgency_level" in r for r in result.reasons)


# ---------------------------------------------------------- T-IR-GR-17: Path A anti-pattern in business.md FAIL
def test_path_a_antipattern_in_business_md_fails(tmp_path):
    """Anti-patterns in business.md must also fail (SP3b checks both files,
    no compliance.md carve-out unlike SP3a)."""
    grade = _load()
    output_dir = _copy_sample(tmp_path, "draft-output-sample-pii-breach")
    business = output_dir / "business.md"
    business.write_text(business.read_text(encoding="utf-8") + "\n\n## 違規測試\n72 小時內通報\n", encoding="utf-8")
    result = grade.grade_response(output_dir, path_type="pii-breach")
    assert result.passed is False
    assert any("path a violation" in r.lower() for r in result.reasons)


# ---------------------------------------------------------- T-GR-ORPHAN-1: orphan token detected
def test_grade_response_detects_template_orphan_in_legal_md():
    """If legal.md or business.md contains an un-substituted {{token}}, grader
    must FAIL with reason mentioning 'orphan' or 'template'. Closes the silent-
    shipping path that v0.4.3 dogfood audit found (dpo_phone workaround would
    have produced this state under v0.4.2 schema)."""
    grade = _load()
    fixture_dir = FIXTURES / "orphan-token"

    result = grade.grade_response(fixture_dir, "pii-breach")

    assert result.passed is False
    assert any(
        ("orphan" in reason.lower() or "template" in reason.lower())
        and "{{" in reason
        for reason in result.reasons
    ), f"expected orphan-token failure, got: {result.reasons}"
