"""Classify schema-v2 ticket evidence for a later schema-v3 migration.

This module only prepares deterministic classification input.  It does not
read, write, or apply a map migration.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


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
