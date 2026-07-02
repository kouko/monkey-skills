"""Structural tests for driver_00_header.js — the head module of the
build-assembled Workflow driver (see docs/loom/plans/2026-07-03-loom-pipeline-conductor.md
Task 5). This file is source-only; the concat-build lands in a later task
(Task 6), so this test only checks the module in isolation via `node --check`.
"""
import subprocess
from pathlib import Path

MODULE_PATH = Path(__file__).parent / "driver_00_header.js"

FORBIDDEN_TOKENS = ["Date.now(", "Math.random(", "new Date()"]


def _executable_compressed(source: str) -> str:
    """Comment-stripped, whitespace-free view of the JS source.

    Robust against the two dodges a naive line filter misses: /* */ block
    comments quoting a token in prose (false positive), and a forbidden
    call split across lines like `Date\\n.now()` (false negative).
    """
    import re

    no_blocks = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    no_line_comments = "\n".join(
        line for line in no_blocks.splitlines() if not line.strip().startswith("//")
    )
    return re.sub(r"\s+", "", no_line_comments)


def test_meta_literal():
    # @req: REQ-LOOM-PIPELINE-DRIVER-HEADER
    assert MODULE_PATH.exists(), f"module missing: {MODULE_PATH}"

    source = MODULE_PATH.read_text(encoding="utf-8")

    # node --check must pass (valid JS syntax, no runtime execution)
    result = subprocess.run(
        ["node", "--check", str(MODULE_PATH)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"node --check failed: {result.stderr}"

    # meta export present
    assert "export const meta" in source

    # no imports — assembled script must stay self-contained
    assert "import " not in source

    # forbidden non-deterministic tokens that break Workflow resume —
    # comments may *document* these tokens in prose, so strip comments
    # first; then strip ALL whitespace so a split-across-lines rewrite
    # (`Date\n  .now()`) cannot dodge the substring match.
    for token in FORBIDDEN_TOKENS:
        compressed = token.replace(" ", "")
        assert compressed not in _executable_compressed(source), (
            f"forbidden token present in executable code: {token}"
        )

    # phases array covers all three pipeline segments
    assert source.count("title:") >= 3, "expected phases entries for all 3 segments"
