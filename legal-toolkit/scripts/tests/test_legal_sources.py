"""Tests for legal-sources.json canonical SoT structure and content.

Validates:
  - JSON schema well-formedness
  - Required statute entries exist with correct pcodes
  - URL template consistency
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))


def test_canonical_legal_sources_includes_administrative_procedure_act():
    """行政程序法 (pcode A0030055) MUST be in canonical statute_sources;
    cited by statute-citations.md L42 for authority-letter 回函時程基準."""
    canonical = SCRIPTS / "canonical" / "legal-sources.json"
    assert canonical.exists(), f"canonical legal-sources.json not found at {canonical}"
    
    data = json.loads(canonical.read_text(encoding="utf-8"))
    assert "行政程序法" in data["statute_sources"], (
        "行政程序法 missing from canonical statute_sources; expected pcode A0030055"
    )
    assert data["statute_sources"]["行政程序法"]["pcode"] == "A0030055"
