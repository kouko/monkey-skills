#!/usr/bin/env python3
"""Tests for distribute.py — TDD iron-law RED before GREEN."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

# Load distribute module for TARGETS / OBSIDIAN_ROOT / distribute()
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

import distribute  # type: ignore[import]

# The SSOT marker string every functional copy must contain in its header
SSOT_MARKER = "managed by obsidian/scripts/distribute.py"


# ── Tests ─────────────────────────────────────────────────────────────────────


def test_distribute_idempotent(tmp_path: Path) -> None:
    """Running distribute() twice must produce identical files (idempotency)."""
    # Clone relevant tree into tmp_path to avoid mutating worktree
    obs_src = distribute.OBSIDIAN_ROOT
    obs_tmp = tmp_path / "obsidian"

    # Copy the canonical SSOT and the script itself so distribute can read them
    canonical_rel = Path("skills/wiki-ingest/references/language-policy.md")
    src_canonical = obs_src / canonical_rel
    dst_canonical = obs_tmp / canonical_rel
    dst_canonical.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_canonical, dst_canonical)

    # Also copy existing target dirs so distribute can overwrite them
    for rel in distribute.TARGETS:
        dst = obs_tmp / rel
        dst.parent.mkdir(parents=True, exist_ok=True)

    # Monkey-patch OBSIDIAN_ROOT + CANONICAL in the module to point at tmp clone
    original_root = distribute.OBSIDIAN_ROOT
    original_canonical = distribute.CANONICAL
    try:
        distribute.OBSIDIAN_ROOT = obs_tmp
        distribute.CANONICAL = obs_tmp / canonical_rel

        # First run
        distribute.distribute()
        snapshots_first = {
            rel: (obs_tmp / rel).read_bytes() for rel in distribute.TARGETS
        }

        # Second run — must produce identical bytes
        distribute.distribute()
        snapshots_second = {
            rel: (obs_tmp / rel).read_bytes() for rel in distribute.TARGETS
        }
    finally:
        distribute.OBSIDIAN_ROOT = original_root
        distribute.CANONICAL = original_canonical

    assert snapshots_first == snapshots_second, (
        "distribute() is not idempotent — second run produced different bytes"
    )


def test_ssot_header_present() -> None:
    """After distribute(), every target file's header must contain the SSOT marker."""
    for rel in distribute.TARGETS:
        target = distribute.OBSIDIAN_ROOT / rel
        assert target.is_file(), f"Target missing: {rel}"
        header = target.read_text(encoding="utf-8", errors="replace")[:500]
        assert SSOT_MARKER in header, (
            f"SSOT marker {SSOT_MARKER!r} not found in header of {rel}"
        )


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
