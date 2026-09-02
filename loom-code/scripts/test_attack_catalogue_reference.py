"""Tests for the plugin-shipped attack-class catalogue reference.

`loom-code/skills/review/references/attack-catalogue.md` ships the six
attack classes the review station's adversarial action works through on a
skill or gate artifact; each class must pin its evidence rule to a runnable
command, never a reading.
"""
from __future__ import annotations

import re
from pathlib import Path

CATALOGUE = (
    Path(__file__).resolve().parents[1]
    / "skills/review/references/attack-catalogue.md"
)

CLASS_NAMES = [
    "forge an artifact the gate trusts",
    "bypass a gate by editing its input",
    "replay a stale artifact",
    "cross a trust boundary (repo / worktree / process)",
    "self-exempt via a prose condition",
    "race a concurrent writer",
]

NEGATIVE_CLAUSE = "never a reading"

VERDICT_TOKENS = ["reproduced", "held", "not-applicable"]


def test_attack_catalogue_names_six_classes_with_evidence_rule() -> None:
    text = CATALOGUE.read_text(encoding="utf-8")

    class_headings = re.findall(r"^### Class: .+$", text, flags=re.MULTILINE)
    assert len(class_headings) == 6, class_headings
    assert class_headings == [f"### Class: {name}" for name in CLASS_NAMES]

    for match in re.finditer(r"^### Class: .+$", text, flags=re.MULTILINE):
        start = match.end()
        next_section = text.find("\n### Class:", start)
        if next_section == -1:
            next_section = len(text)
        block = text[start:next_section]
        lines = block.splitlines()
        evidence_lines: list[str] = []
        in_evidence = False
        for line in lines:
            if line.strip().startswith("- Evidence:"):
                in_evidence = True
                evidence_lines.append(line)
            elif in_evidence and line.strip().startswith("- "):
                in_evidence = False
            elif in_evidence and line.strip():
                evidence_lines.append(line)
        assert evidence_lines, f"no Evidence line under {match.group(0)!r}"
        evidence_text = " ".join(" ".join(evidence_lines).split())
        assert NEGATIVE_CLAUSE in evidence_text, (
            f"Evidence under {match.group(0)!r} does not carry the negative "
            f"clause {NEGATIVE_CLAUSE!r}: {evidence_text!r}"
        )

    assert "## Verdict vocabulary" in text
    vocab_start = text.index("## Verdict vocabulary")
    vocab_end = text.find("\n## ", vocab_start + 1)
    if vocab_end == -1:
        vocab_end = len(text)
    vocab_block = text[vocab_start:vocab_end]
    for token in VERDICT_TOKENS:
        assert f"`{token}`" in vocab_block, token

    assert "## Repo store" in text
    assert "docs/loom/evidence/attack-catalogue.md" in text
