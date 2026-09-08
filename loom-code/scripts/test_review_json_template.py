"""Generated attestation template contract."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ATTESTATION_TEMPLATE = REPO / "loom-code" / "contract" / "templates" / "attestation.json"


def test_attestation_has_only_generated_evidence_fields() -> None:
    document = json.loads(ATTESTATION_TEMPLATE.read_text(encoding="utf-8"))
    assert list(document) == [
        "schema", "change_id", "content_digest", "executions", "verdicts", "findings"
    ]
    assert not ({"reviewed_sha", "scope", "dispatch", "cost", "questions", "charter"} & document.keys())
