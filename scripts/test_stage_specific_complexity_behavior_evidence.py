"""Require real baseline/candidate evidence for stage complexity behavior."""

import re
import runpy
from pathlib import Path


REPORT = Path(__file__).parents[1] / "docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md"
ROOT = Path(__file__).parents[1]
FINGERPRINT = runpy.run_path(
    str(ROOT / "loom-code/scripts/loom_firing_harness.py")
)["_plugin_tree_fingerprint"]


def test_report_binds_baseline_and_final_candidate():
    text = REPORT.read_text(encoding="utf-8")
    flat_text = " ".join(text.split())
    assert "immutable pre-edit snapshot" in text
    assert "base commit `0a7dcde2`" in text
    assert "final cold-install candidate bytes" in text
    for plugin in ("loom-design", "loom-code"):
        assert f"{plugin} candidate SHA-256" in text
        match = re.search(rf"{plugin} candidate SHA-256: `([0-9a-f]{{64}})`", text)
        assert match, f"report must record a full {plugin} candidate fingerprint"
        assert match.group(1) == FINGERPRINT(ROOT / plugin)
    for case in ("no-upstream", "misleading-upstream", "trivial-exempt", "over-complex"):
        assert f"`{case}`" in text
    for lens in (
        "business-complexity-lens",
        "visual-complexity-lens",
        "interaction-complexity-lens",
        "behavioral-complexity-lens",
        "architecture-complexity-lens",
        "implementation-complexity-lens",
    ):
        assert lens in text
    assert "purpose preservation" in flat_text.lower()
    assert "scope trade-off" in flat_text.lower()
    assert "Pre-existing invariant result: PASS" in text
