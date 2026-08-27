"""Require real baseline/candidate evidence for stage complexity behavior."""

import re
import runpy
from pathlib import Path


REPORT = Path(__file__).parents[1] / "docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md"
ROOT = Path(__file__).parents[1]
FINGERPRINT = runpy.run_path(
    str(ROOT / "loom-code/scripts/loom_firing_harness.py")
)["_plugin_tree_fingerprint"]
BASELINE_FINGERPRINTS = {
    "loom-design": "084299e0537bee45a2f2c559472d6a6e4651ce814bebb2755b70daca1a1afe3c",
    "loom-code": "73c552397959a13770d61769189e2945a6dba7aff74f46774a44b5fd6c3126f5",
}
REQUIRED_LENS_EVIDENCE = {
    "business-complexity-lens": "live hard case",
    "visual-complexity-lens": "live hard case",
    "interaction-complexity-lens": "live hard case",
    "behavioral-complexity-lens": "contract test",
    "architecture-complexity-lens": "live hard case",
    "implementation-complexity-lens": "contract test",
}


def test_report_binds_baseline_and_final_candidate():
    text = REPORT.read_text(encoding="utf-8")
    flat_text = " ".join(text.split())
    assert "immutable pre-edit snapshot" in text
    assert "base commit `0a7dcde2`" in text
    assert "final cold-install candidate bytes" in text
    for plugin in ("loom-design", "loom-code"):
        baseline_match = re.search(
            rf"{plugin} baseline SHA-256: `([0-9a-f]{{64}})`", text
        )
        assert baseline_match, f"report must record a full {plugin} baseline fingerprint"
        assert baseline_match.group(1) == BASELINE_FINGERPRINTS[plugin]
        assert f"{plugin} candidate SHA-256" in text
        match = re.search(rf"{plugin} candidate SHA-256: `([0-9a-f]{{64}})`", text)
        assert match, f"report must record a full {plugin} candidate fingerprint"
        assert match.group(1) == FINGERPRINT(ROOT / plugin)
    for case in ("no-upstream", "misleading-upstream", "trivial-exempt", "over-complex"):
        assert f"`{case}`" in text
    coverage_rows = dict(
        re.findall(r"^\| `([^`]+-complexity-lens)` \| ([^|]+?) \| PASS \|$", text, re.MULTILINE)
    )
    assert coverage_rows == REQUIRED_LENS_EVIDENCE
    assert "purpose preservation" in flat_text.lower()
    assert "scope trade-off" in flat_text.lower()
    assert "Pre-existing invariant result: PASS" in text
