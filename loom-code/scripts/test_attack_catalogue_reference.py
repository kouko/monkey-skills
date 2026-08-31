"""Tests for the plugin-shipped attack-class catalogue reference.

`loom-code/skills/requesting-code-review/references/attack-catalogue.md`
ships six attack classes an adversarial auditor works through; each class
must pin its evidence rule to a runnable command, never a reading (plan
`docs/loom/plans/2026-08-31-adversarial-audit-station.md` Task 1
Acceptance).
"""
from __future__ import annotations

import re
from pathlib import Path

CATALOGUE = (
    Path(__file__).resolve().parents[1]
    / "skills/requesting-code-review/references/attack-catalogue.md"
)


def test_attack_catalogue_names_six_classes_with_evidence_rule() -> None:
    # @req: none — no registered REQ-ids in this dispatch's plan/spec.
    text = CATALOGUE.read_text(encoding="utf-8")

    class_headings = re.findall(r"^### Class: .+$", text, flags=re.MULTILINE)
    assert len(class_headings) == 6, class_headings

    for match in re.finditer(r"^### Class: .+$", text, flags=re.MULTILINE):
        start = match.end()
        next_section = text.find("\n### Class:", start)
        if next_section == -1:
            next_section = len(text)
        block = text[start:next_section]
        evidence_lines = [
            line for line in block.splitlines() if line.strip().startswith("- Evidence:")
        ]
        assert evidence_lines, f"no Evidence line under {match.group(0)!r}"
        assert "command" in evidence_lines[0], (
            f"Evidence line under {match.group(0)!r} does not name a command: "
            f"{evidence_lines[0]!r}"
        )

    assert "## Verdict vocabulary" in text
    assert "## Repo store" in text
    assert "docs/loom/ATTACK-CATALOGUE.md" in text
