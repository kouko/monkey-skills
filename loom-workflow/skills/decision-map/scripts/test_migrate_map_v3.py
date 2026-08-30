"""Tests for schema-v2 decision-map ticket classification.

WHY: schema-v2 names describe a work style, while schema-v3 names describe
the evidence that can close the ticket. Migration must therefore preserve the
source evidence and classify it without changing source files.
"""

from __future__ import annotations

import sys
from dataclasses import replace
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import migrate_map_v3  # noqa: E402


def _write_v2_research_map(map_dir: Path) -> tuple[Path, Path]:
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
    return map_path, ticket_path


def test_migration_delivery_requires_existing_reciprocal_brief(tmp_path: Path) -> None:
    # @req: REQ-85
    """A delivery classification refuses absent or non-reciprocal Brief evidence."""
    map_dir = tmp_path / "docs" / "loom" / "maps" / "family-relocation"
    map_path, ticket_path = _write_v2_research_map(map_dir)
    ticket_path.write_text(
        ticket_path.read_text(encoding="utf-8")
        .replace("factual-answer: seven consumers\ninspectable-evidence: docs/loom/research/consumers.md", "delivery-evidence: commit 0123456"),
        encoding="utf-8",
    )
    before = {path: path.read_bytes() for path in (map_path, ticket_path)}
    try:
        migrate_map_v3.preview_migration(map_dir)
    except migrate_map_v3.MigrationConflict as exc:
        assert "brief" in str(exc).lower()
    else:
        raise AssertionError("delivery migration must require a canonical Brief")
    assert {path: path.read_bytes() for path in (map_path, ticket_path)} == before


def test_migration_apply_refuses_ticket_membership_drift_without_writes(
    tmp_path: Path,
) -> None:
    # @req: REQ-91
    """Adding a ticket after preview invalidates the whole read set."""
    map_path, ticket_path = _write_v2_research_map(tmp_path / "family-relocation")
    preview = migrate_map_v3.preview_migration(map_path.parent)
    added = ticket_path.parent / "later.md"
    added.write_text(ticket_path.read_text(encoding="utf-8"), encoding="utf-8")
    before = {path: path.read_bytes() for path in (map_path, ticket_path, added)}
    try:
        migrate_map_v3.apply_migration(map_path.parent, preview)
    except migrate_map_v3.MigrationConflict as exc:
        assert "membership" in str(exc).lower()
    else:
        raise AssertionError("apply must refuse a changed tickets read set")
    assert {path: path.read_bytes() for path in before} == before


def test_migration_apply_rejects_forged_preview_key_without_writes(tmp_path: Path) -> None:
    # @req: REQ-91
    """A preview cannot smuggle a path outside MAP.md or tickets/<slug>.md."""
    map_path, ticket_path = _write_v2_research_map(tmp_path / "family-relocation")
    preview = migrate_map_v3.preview_migration(map_path.parent)
    outside = tmp_path / "outside.md"
    outside.write_text("unchanged\n", encoding="utf-8")
    forged = replace(
        preview,
        source_digests={**preview.source_digests, "../outside.md": "forged"},
        source_texts={**preview.source_texts, "../outside.md": "unchanged\n"},
        candidates={**preview.candidates, "../outside.md": "mutated\n"},
    )
    before = {path: path.read_bytes() for path in (map_path, ticket_path, outside)}
    try:
        migrate_map_v3.apply_migration(map_path.parent, forged)
    except migrate_map_v3.MigrationConflict as exc:
        assert "preview key" in str(exc).lower()
    else:
        raise AssertionError("forged preview key must be rejected")
    assert {path: path.read_bytes() for path in before} == before


def _write_v2_delivery_map(tmp_path: Path) -> tuple[Path, Path, Path]:
    map_dir = tmp_path / "docs/loom/maps/family-relocation"
    map_path, ticket_path = _write_v2_research_map(map_dir)
    ticket_relative = ticket_path.relative_to(tmp_path).as_posix()
    brief = tmp_path / "docs/loom/specs/relocate-hooks.md"
    brief.parent.mkdir(parents=True)
    brief.write_text(f"# Brief\n\nOutcome Map ticket: {ticket_relative}\n", encoding="utf-8")
    ticket_path.write_text(
        ticket_path.read_text(encoding="utf-8")
        .replace("type: task", "type: task\nbrief: docs/loom/specs/relocate-hooks.md")
        .replace("factual-answer: seven consumers\ninspectable-evidence: docs/loom/research/consumers.md", "delivery-evidence: commit 0123456"),
        encoding="utf-8",
    )
    return map_path, ticket_path, brief


def test_delivery_migration_accepts_canonical_brief_with_relative_map_dir(
    tmp_path: Path, monkeypatch
) -> None:
    # @req: REQ-85
    """A valid existing join migrates when the caller supplies a relative map path."""
    map_path, ticket_path, brief = _write_v2_delivery_map(tmp_path)
    monkeypatch.chdir(tmp_path)
    relative_map = map_path.parent.relative_to(tmp_path)
    preview = migrate_map_v3.preview_migration(relative_map)
    result = migrate_map_v3.apply_migration(relative_map, preview)
    assert result.applied is True
    assert "type: delivery" in ticket_path.read_text(encoding="utf-8")
    assert brief.read_text(encoding="utf-8").startswith("# Brief")


def test_delivery_migration_refuses_changed_brief_or_candidate_population(
    tmp_path: Path,
) -> None:
    # @req: REQ-91
    """Binding evidence and every inspected candidate ticket remain CAS-covered."""
    map_path, ticket_path, brief = _write_v2_delivery_map(tmp_path)
    preview = migrate_map_v3.preview_migration(map_path.parent)
    brief.write_text("# Changed\n", encoding="utf-8")
    before = {path: path.read_bytes() for path in (map_path, ticket_path, brief)}
    try:
        migrate_map_v3.apply_migration(map_path.parent, preview)
    except migrate_map_v3.MigrationConflict as exc:
        assert "binding" in str(exc).lower()
    else:
        raise AssertionError("changed Brief must invalidate preview")
    assert {path: path.read_bytes() for path in before} == before

    brief.write_text(
        f"# Brief\n\nOutcome Map ticket: {ticket_path.relative_to(tmp_path).as_posix()}\n",
        encoding="utf-8",
    )
    preview = migrate_map_v3.preview_migration(map_path.parent)
    other = tmp_path / "docs/loom/maps/other/tickets/other.md"
    other.parent.mkdir(parents=True)
    other.write_text("---\ntype: research\nstatus: open\n---\n", encoding="utf-8")
    before = {path: path.read_bytes() for path in (map_path, ticket_path, brief, other)}
    try:
        migrate_map_v3.apply_migration(map_path.parent, preview)
    except migrate_map_v3.MigrationConflict as exc:
        assert "binding" in str(exc).lower()
    else:
        raise AssertionError("candidate membership must invalidate preview")
    assert {path: path.read_bytes() for path in before} == before


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
