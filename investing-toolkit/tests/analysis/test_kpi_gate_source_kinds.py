#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Pins the `TRUSTED_SOURCE_KINDS` naming convention (Task 11, arc
company-total-revenue): every trusted kind is `<trust-class>-<lane>`
where the trust-class segment is `xbrl-`. Also confirms admitting
`xbrl-topline` does not accidentally trust either untrusted lane
(`llm-located` / `prose`).
"""
from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "skills"
    / "analysis-kpi"
    / "scripts"
)
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
import kpi_gate  # noqa: E402


def test_topline_kind_is_trusted_and_convention_pinned():
    assert "xbrl-topline" in kpi_gate.TRUSTED_SOURCE_KINDS

    # Mechanical pin: no future trusted kind can be minted outside the
    # `xbrl-` trust class by prose discipline alone.
    for kind in kpi_gate.TRUSTED_SOURCE_KINDS:
        assert kind.startswith("xbrl-"), (
            f"{kind!r} in TRUSTED_SOURCE_KINDS does not start with the "
            "xbrl- trust-class segment"
        )

    # Untrusted lanes stay outside the trusted set.
    assert "llm-located" not in kpi_gate.TRUSTED_SOURCE_KINDS
    assert "prose" not in kpi_gate.TRUSTED_SOURCE_KINDS
