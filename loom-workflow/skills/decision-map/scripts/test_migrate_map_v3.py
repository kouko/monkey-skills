"""Tests for schema-v2 decision-map ticket classification.

WHY: schema-v2 names describe a work style, while schema-v3 names describe
the evidence that can close the ticket. Migration must therefore preserve the
source evidence and classify it without changing source files.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import migrate_map_v3  # noqa: E402


def test_v2_classification_routes_task_and_feasibility_by_closure() -> None:
    # @req: REQ-85
    """Closure evidence, rather than the v2 label, selects the v3 type."""
    cases = {
        "inventory": (
            "task",
            "inventory: all family-hook consumers\n"
            "factual-answer: seven consumers\n"
            "inspectable-evidence: docs/loom/research/consumers.md",
            "research",
        ),
        "machine feasibility": (
            "prototype",
            "machine-measured-feasibility: cold install exits 0\n"
            "inspectable-evidence: prototype-probe/PROTOTYPE_MEASUREMENTS.md\n"
            "user-ratified: kouko, 2026-08-29",
            "research",
        ),
        "shipped slice": (
            "task",
            "delivery-evidence: commit 0123456",
            "delivery",
        ),
        "human candidate": (
            "prototype",
            "candidate-artifact: docs/loom/prototypes/resolver.md\n"
            "evaluation: selected by maintainer\n"
            "user-ratified: kouko, 2026-08-30",
            "prototype",
        ),
        "ratified direction": (
            "task",
            "decision: hooks first\nuser-ratified: kouko, 2026-08-30",
            "grilling",
        ),
    }

    for source_type, source_evidence, target_type in cases.values():
        result = migrate_map_v3.classify_v2_ticket(source_type, source_evidence)
        assert result.target_type == target_type
        assert result.source_type == source_type
        assert result.source_evidence == source_evidence
        assert result.refusal is None

    ambiguous = migrate_map_v3.classify_v2_ticket(
        "task", "Resolution completed without a closure contract."
    )
    assert ambiguous.target_type is None
    assert ambiguous.source_evidence == "Resolution completed without a closure contract."
    assert ambiguous.refusal == migrate_map_v3.CLASSIFICATION_EVIDENCE_GUIDANCE
