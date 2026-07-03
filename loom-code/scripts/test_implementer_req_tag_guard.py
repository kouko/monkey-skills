"""Structural grep-test guarding Rule 11's @req namespace guard.

The agent contract is a prompt artifact, not executable code. The contract
under guard: the implementer's `@req` Definition-of-Done (role-contract
rule 11) must be NAMESPACE-AWARE. Observed failures: PR #479 CI —
implementers pattern-matched the `# @req:` tag convention and minted
unregistered ids, producing 33 dangling-tag failures against
`check-living-spec-index.py`; confirmed live again on the v1.1 batch-mode
branch (2026-07-03), where the first dispatched implementer tagged
`REQ-BATCH-QUEUE-PARSE` into a repo whose living-spec namespace does not
contain it, and every subsequent dispatch needed a hand-carried standing
exemption. An unconditional "every test MUST carry @req" rule plus a CI
that rejects unregistered ids is a contract conflict — the guard resolves
it in the contract itself.

These checks assert on the load-bearing PHRASES (intent), tolerant of
surrounding wording, so the test guards meaning without being brittle.

Stdlib only (pathlib). Resolve files relative to this test file.
"""

from pathlib import Path

_ROOT = Path(__file__).parents[1]

AGENT = _ROOT / "agents" / "implementer.md"


def _text(p: Path) -> str:
    assert p.is_file(), f"file is absent at {p}"
    return p.read_text(encoding="utf-8")


def _rule_11_block(text: str) -> str:
    """Slice rule 11 from the role contract (up to the managed baseline)."""
    # Anchor on the rule's bold lead-in, not a bare "11." (which a future
    # version number or list elsewhere in the file could shadow).
    start = text.find("**`@req` Definition-of-Done")
    assert start != -1, "role-contract rule 11 lead-in is absent from implementer.md"
    end = text.find("<!-- BEGIN baseline-v1", start)
    return text[start:end] if end != -1 else text[start:]


def test_rule_11_requires_preexisting_namespace_id():
    """Tagging is conditional on the id already existing in the namespace."""
    block = _rule_11_block(_text(AGENT))
    assert "already exists in the living-spec namespace" in block, (
        "rule 11 must gate @req tagging on the id ALREADY existing in the "
        "living-spec namespace — the unconditional form re-creates the "
        "PR #479 dangling-tag failure"
    )


def test_rule_11_forbids_minting_ids():
    """The implementer must never invent a plausible-looking REQ-id."""
    block = _rule_11_block(_text(AGENT))
    assert "never mint" in block.lower(), (
        "rule 11 must explicitly forbid minting new REQ-ids — "
        "pattern-matched ids are exactly what produced the 33 dangling-tag "
        "CI failures on PR #479"
    )


def test_rule_11_names_the_per_test_escape():
    """A test matching none of the dispatch's registered ids is also untagged."""
    block = _rule_11_block(_text(AGENT))
    assert "corresponds to none" in block and "never stretch" in block.lower(), (
        "rule 11 must cover the mixed cell — dispatch HAS registered ids "
        "but one test maps to none of them — with the same omit-and-note "
        "escape, or an implementer is left with no legal move for a "
        "defensive edge-case test"
    )


def test_rule_11_names_the_no_namespace_escape():
    """With no registered ids in scope, omitting tags is the correct move."""
    block = _rule_11_block(_text(AGENT))
    assert "omit" in block.lower() and "not incomplete" in block.lower(), (
        "rule 11 must state that when the dispatch carries no registered "
        "REQ-ids, tests are written WITHOUT @req tags and are NOT "
        "incomplete for it — otherwise every dispatch into a namespace-less "
        "repo needs a hand-carried exemption"
    )
