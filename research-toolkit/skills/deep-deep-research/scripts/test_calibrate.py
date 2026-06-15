"""Tests for calibrate.py — CALIBRATION_BLOCK constant + calibration_block() function.

Mirrors test_mode_route.py style: flat imports (`from calibrate import ...`)
plus SCRIPTS_DIR anchor for subprocess CLI tests (Task 2 will add CLI tests).
"""
from __future__ import annotations

from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent


def test_calibration_block_encodes_three_rules():
    """The calibration_block() return value must encode all 3 anti-laundering rules.

    Rule 1 — merged finding confidence = weakest load-bearing claim.
      Signal: "weakest" AND ("load-bearing" OR "load bearing").

    Rule 2 — summary confidence must not exceed body confidence.
      Signal: "summary" AND ("not exceed" OR "must not" OR "<=").

    Rule 3 — split/tied votes and conflicting confirmed claims must not be
      labelled consensus.
      Signal: "consensus" AND ("conflict" OR "contested" OR "split" OR "tied").
    """
    from calibrate import calibration_block

    block = calibration_block().lower()

    # Rule 1: weakest-link anti-averaging
    assert "weakest" in block, "Rule 1: 'weakest' missing from calibration_block"
    assert "load-bearing" in block or "load bearing" in block, (
        "Rule 1: 'load-bearing' (or 'load bearing') missing from calibration_block"
    )

    # Rule 2: summary must not exceed body confidence
    assert "summary" in block, "Rule 2: 'summary' missing from calibration_block"
    assert (
        "not exceed" in block or "must not" in block or "<=" in block
    ), "Rule 2: no 'not exceed'/'must not'/'<=' in calibration_block"

    # Rule 3: no false consensus over split/conflicting claims
    assert "consensus" in block, "Rule 3: 'consensus' missing from calibration_block"
    assert (
        "conflict" in block
        or "contested" in block
        or "split" in block
        or "tied" in block
    ), "Rule 3: none of 'conflict'/'contested'/'split'/'tied' in calibration_block"


def test_calibration_block_constant_equals_function():
    """calibration_block() must return the module-level CALIBRATION_BLOCK constant."""
    from calibrate import CALIBRATION_BLOCK, calibration_block

    assert calibration_block() == CALIBRATION_BLOCK


def test_calibration_block_is_nonempty_string():
    """CALIBRATION_BLOCK must be a non-empty string (no accidental None or empty)."""
    from calibrate import CALIBRATION_BLOCK

    assert isinstance(CALIBRATION_BLOCK, str)
    assert len(CALIBRATION_BLOCK) > 50, "CALIBRATION_BLOCK is suspiciously short"
