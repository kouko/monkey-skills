"""Tests for schema-v2 decision-map ticket classification.

WHY: schema-v2 names describe a work style, while schema-v3 names describe
the evidence that can close the ticket. Migration must therefore preserve the
source evidence and classify it without changing source files.
"""

from __future__ import annotations

import sys
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import migrate_map_v3  # noqa: E402


def test_migration_preview_digest_apply_and_retry_are_safe(tmp_path: Path) -> None:
    # @req: REQ-91
    """Preview is read-only and a stale or repeated apply cannot duplicate work."""
    map_dir = tmp_path / "family-relocation"
    tickets = map_dir / "tickets"
    tickets.mkdir(parents=True)
    map_path = map_dir / "MAP.md"
    ticket_path = tickets / "inventory.md"
    map_path.write_text(
        "---\nmap-id: family-relocation\nschema_version: 2\nstate: active\n---\n"
        "\n## Destination\n\nA durable outcome.\n\n## Notes\n\n\n"
        "## Decisions-so-far\n\n\n## Not-yet-specified (fog)\n\n\n"
        "## Out-of-scope\n",
        encoding="utf-8",
    )
    ticket_path.write_text(
        "---\ntype: task\nstatus: closed\n---\n\nInventory consumers.\n"
        "\n## Resolution\n\nfactual-answer: seven consumers\n"
        "inspectable-evidence: docs/loom/research/consumers.md\n",
        encoding="utf-8",
    )

    before = {path: path.read_bytes() for path in (map_path, ticket_path)}
    preview = migrate_map_v3.preview_migration(map_dir)
    assert {path: path.read_bytes() for path in (map_path, ticket_path)} == before
    assert preview.classifications["tickets/inventory.md"].target_type == "research"
    assert preview.source_digests["MAP.md"] == sha256(before[map_path]).hexdigest()

    ticket_path.write_text(ticket_path.read_text(encoding="utf-8") + "changed\n", encoding="utf-8")
    try:
        migrate_map_v3.apply_migration(map_dir, preview)
    except migrate_map_v3.MigrationConflict:
        pass
    else:
        raise AssertionError("apply must refuse a changed preview source")

    preview = migrate_map_v3.preview_migration(map_dir)
    result = migrate_map_v3.apply_migration(map_dir, preview)
    assert result.applied is True
    assert "schema_version: 3" in map_path.read_text(encoding="utf-8")
    migrated_ticket = ticket_path.read_text(encoding="utf-8")
    assert "type: research" in migrated_ticket
    assert "factual-answer: seven consumers" in migrated_ticket
    assert "inspectable-evidence: docs/loom/research/consumers.md" in migrated_ticket

    retry = migrate_map_v3.preview_migration(map_dir)
    retried = migrate_map_v3.apply_migration(map_dir, retry)
    assert retry.already_applied is True
    assert retried.applied is False
    assert ticket_path.read_text(encoding="utf-8") == migrated_ticket


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


def test_v2_classification_refuses_malformed_or_competing_closure_evidence() -> None:
    # @req: REQ-85
    """A v2 migration does not treat malformed human approval as closure."""
    malformed_ratifications = (
        (
            "prototype",
            "candidate-artifact: docs/loom/prototypes/resolver.md\n"
            "evaluation: selected by maintainer\nuser-ratified: yes",
        ),
        (
            "grilling",
            "decision: hooks first\nuser-ratified: kouko, 2026-8-30",
        ),
        (
            "grilling",
            "decision: hooks first\nUser-ratified: kouko, 2026-08-30",
        ),
    )
    for source_type, source_evidence in malformed_ratifications:
        result = migrate_map_v3.classify_v2_ticket(source_type, source_evidence)
        assert result.target_type is None
        assert result.source_evidence == source_evidence
        assert result.refusal == migrate_map_v3.CLASSIFICATION_EVIDENCE_GUIDANCE

    competing = migrate_map_v3.classify_v2_ticket(
        "task",
        "factual-answer: seven consumers\n"
        "inspectable-evidence: docs/loom/research/consumers.md\n"
        "delivery-evidence: commit 0123456",
    )
    assert competing.target_type is None
    assert competing.refusal == migrate_map_v3.CLASSIFICATION_EVIDENCE_GUIDANCE
