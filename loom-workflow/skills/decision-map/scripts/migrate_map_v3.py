"""Preview and apply deterministic schema-v2 decision-map migrations."""

from __future__ import annotations

import re
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

import map_store


CLASSIFICATION_EVIDENCE_GUIDANCE = (
    "refusing to classify v2 ticket: add factual-answer plus "
    "inspectable-evidence for research, delivery-evidence for delivery, "
    "candidate-artifact plus evaluation plus user-ratified for prototype, "
    "or decision plus user-ratified for grilling"
)


@dataclass(frozen=True)
class V2TicketClassification:
    """One non-mutating schema-v3 classification decision or refusal."""

    source_type: str
    source_evidence: str
    target_type: str | None
    refusal: str | None


class MigrationConflict(Exception):
    """A preview source changed before its candidate could be applied."""


@dataclass(frozen=True)
class MigrationPreview:
    """A read-only migration proposal tied to exact source bytes."""

    map_dir: Path
    source_digests: dict[str, str]
    source_texts: dict[str, str]
    classifications: dict[str, V2TicketClassification]
    candidates: dict[str, str]
    already_applied: bool = False


@dataclass(frozen=True)
class MigrationResult:
    """Whether this invocation committed a v2-to-v3 candidate."""

    applied: bool


def _relative_key(map_dir: Path, path: Path) -> str:
    return path.relative_to(map_dir).as_posix()


def _replace_frontmatter_value(text: str, key: str, value: str) -> str:
    pattern = re.compile(rf"^(?P<prefix>{re.escape(key)}:\s*).*?$", re.MULTILINE)
    replaced, count = pattern.subn(
        lambda match: f"{match.group('prefix')}{value}", text, count=1
    )
    if count != 1:
        raise MigrationConflict(f"migration source is missing {key!r} frontmatter")
    return replaced


def _ticket_paths(map_dir: Path) -> list[Path]:
    return sorted((map_dir / "tickets").glob("*.md"))


def _source_digest(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def preview_migration(map_dir: Path) -> MigrationPreview:
    """Build a zero-write v2 candidate and pin every source byte digest."""
    map_dir = Path(map_dir)
    map_path = map_dir / "MAP.md"
    map_text = map_path.read_text(encoding="utf-8")
    map_document = map_store.parse_map_document(map_text, map_path)
    if map_document.frontmatter.schema_version == 3:
        return MigrationPreview(map_dir, {}, {}, {}, {}, already_applied=True)
    if map_document.frontmatter.schema_version != 2:
        raise MigrationConflict("migration accepts schema_version 2 maps only")

    digests = {_relative_key(map_dir, map_path): _source_digest(map_text)}
    source_texts = {_relative_key(map_dir, map_path): map_text}
    candidates = {
        _relative_key(map_dir, map_path): _replace_frontmatter_value(
            map_text, "schema_version", "3"
        )
    }
    classifications: dict[str, V2TicketClassification] = {}
    for ticket_path in _ticket_paths(map_dir):
        ticket_text = ticket_path.read_text(encoding="utf-8")
        ticket = map_store.parse_ticket_document(ticket_text, ticket_path)
        classification = classify_v2_ticket(
            ticket.frontmatter.type, ticket.resolution or ""
        )
        key = _relative_key(map_dir, ticket_path)
        classifications[key] = classification
        if classification.refusal is not None:
            raise MigrationConflict(f"{key}: {classification.refusal}")
        digests[key] = _source_digest(ticket_text)
        source_texts[key] = ticket_text
        candidates[key] = _replace_frontmatter_value(
            ticket_text, "type", classification.target_type or ""
        )
    return MigrationPreview(
        map_dir, digests, source_texts, classifications, candidates
    )


def apply_migration(map_dir: Path, preview: MigrationPreview) -> MigrationResult:
    """CAS-apply a preview; ticket writes precede the schema-version flip.

    A retry after an interrupted ticket batch re-previews the remaining v2
    map and converges on the same type replacements.  The map flip is last,
    so a complete map is never reported as v3 with v2 ticket types.
    """
    map_dir = Path(map_dir)
    if map_dir != preview.map_dir:
        raise MigrationConflict("preview belongs to a different map directory")
    if preview.already_applied:
        return MigrationResult(applied=False)
    for key, digest in preview.source_digests.items():
        current = (map_dir / key).read_text(encoding="utf-8")
        if _source_digest(current) != digest:
            raise MigrationConflict(f"source changed after preview: {key}")
    ordered_keys = sorted(key for key in preview.candidates if key != "MAP.md")
    for key in ordered_keys + ["MAP.md"]:
        path = map_dir / key
        map_store._atomic_write(
            path,
            preview.candidates[key],
            expected=preview.source_texts[key].encode("utf-8"),
        )
    return MigrationResult(applied=True)


def _evidence_fields(source_evidence: str) -> set[str]:
    """Return lower-cased names of non-empty ``key: value`` evidence lines."""
    fields = set()
    for line in source_evidence.splitlines():
        key, separator, value = line.partition(":")
        if separator and value.strip():
            fields.add(key.strip().lower())
    return fields


def _has_ratification(source_evidence: str) -> bool:
    ratification = re.compile(
        r"^user-ratified:\s*[^,\s][^,]*,\s*\d{4}-\d{2}-\d{2}\s*$",
    )
    return any(
        ratification.fullmatch(line.strip()) is not None
        for line in source_evidence.splitlines()
    )


def classify_v2_ticket(
    source_type: str, source_evidence: str
) -> V2TicketClassification:
    """Classify a v2 ticket from its closure evidence without guessing.

    ``source_evidence`` is returned verbatim so a future preview/apply layer
    can preserve provenance.  Multiple closure contracts refuse because v3
    ticket types are closure-exclusive.
    """
    fields = _evidence_fields(source_evidence)
    has_inspectable_evidence = "inspectable-evidence" in fields
    machine_feasibility = bool(
        {"machine-measured-feasibility", "measured-feasibility"} & fields
    ) and has_inspectable_evidence
    research = machine_feasibility or (
        has_inspectable_evidence
        and bool({"factual-answer", "inventory"} & fields)
    )
    candidates = {
        "research": research,
        "delivery": "delivery-evidence" in fields,
        "prototype": (
            "candidate-artifact" in fields
            and "evaluation" in fields
            and _has_ratification(source_evidence)
        ),
        "grilling": "decision" in fields and _has_ratification(source_evidence),
    }
    matches = [ticket_type for ticket_type, matched in candidates.items() if matched]
    if len(matches) != 1:
        return V2TicketClassification(
            source_type=source_type,
            source_evidence=source_evidence,
            target_type=None,
            refusal=CLASSIFICATION_EVIDENCE_GUIDANCE,
        )
    return V2TicketClassification(
        source_type=source_type,
        source_evidence=source_evidence,
        target_type=matches[0],
        refusal=None,
    )
