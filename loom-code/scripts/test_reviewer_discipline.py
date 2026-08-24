"""Structural contract test for the portable reviewer context packet.

Every verdict-producing agent consumes one immutable packet produced by
``review_context.py``.  This test scopes its assertions to each agent's input
contract so a historic path in explanatory prose cannot mask a dispatch that
still derives plugin resources from the consumer repository.
"""
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).parents[1]
REVIEWERS = {
    "code-reviewer": ROOT / "agents" / "code-reviewer.md",
    "docs-reviewer": ROOT / "agents" / "docs-reviewer.md",
    "spec-reviewer": ROOT / "agents" / "spec-reviewer.md",
    "code-quality-reviewer": ROOT / "agents" / "code-quality-reviewer.md",
}
PACKET_FIELDS = ("target_repo", "reviewed_sha", "plugin_version", "resources")


def _input_contract(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.index("## Input contract")
    end = text.index("## Output contract", start)
    return text[start:end]


def test_all_reviewer_roles_require_portable_context_packet():
    """Every reviewer receives the same packet and never derives paths.

    Rule R1 is shared by all four agents.  Therefore every input contract,
    not merely the code-reviewer contract, must name all packet fields and
    constrain plugin-resource reads to the packet's approved absolute paths.
    """
    for name, path in REVIEWERS.items():
        contract = _input_contract(path)
        normalized = re.sub(r"\s+", " ", contract)
        assert "### Immutable review context" in contract, (
            f"{name} has no immutable context packet in its input contract"
        )
        for field in PACKET_FIELDS:
            assert field in contract, (
                f"{name} input contract omits packet field {field!r}"
            )
        assert "approved absolute" in normalized, (
            f"{name} must constrain resource reads to approved absolute paths"
        )
        assert "never derive" in contract, (
            f"{name} must forbid consumer-relative plugin-path derivation"
        )


def test_docs_reviewer_verdict_sha_comes_only_from_immutable_packet():
    """Docs review must not permit a second SHA input beside the packet."""
    docs = REVIEWERS["docs-reviewer"].read_text(encoding="utf-8")
    input_contract = _input_contract(REVIEWERS["docs-reviewer"])
    output_start = docs.index("## Output contract")
    output_contract = docs[output_start:]

    assert "### HEAD sha" not in input_contract, (
        "docs-reviewer must not accept a separate HEAD-sha header that can "
        "diverge from immutable context reviewed_sha"
    )
    assert "immutable review context packet's `reviewed_sha`" in output_contract, (
        "docs-reviewer verdict provenance must name the immutable packet "
        "reviewed_sha as its only source"
    )
    assert "packet's `### HEAD sha`" not in output_contract, (
        "docs-reviewer must not retain the retired independent HEAD-sha "
        "output branch"
    )


def test_docs_reviewer_rejects_invalid_packet_reviewed_sha():
    """A docs verdict requires a real SHA from the immutable packet."""
    docs = REVIEWERS["docs-reviewer"].read_text(encoding="utf-8")
    output_contract = re.sub(
        r"\s+", " ", docs[docs.index("## Output contract"):].lower()
    )

    assert "missing, non-sha, or `unresolved`" in output_contract, (
        "docs-reviewer must classify every absent or invalid packet "
        "reviewed_sha as malformed"
    )
    assert "do not produce a verdict" in output_contract, (
        "docs-reviewer must refuse rather than emit a verdict for an "
        "invalid packet reviewed_sha"
    )
