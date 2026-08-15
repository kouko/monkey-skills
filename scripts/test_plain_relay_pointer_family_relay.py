"""T3 — family-relay.md must point at the plain-relay contract.

WHY: family-relay.md is the SSOT for relay mechanics; readers of the
relay rules must not miss the family-wide plain-language contract
(7 rules + glossary) in plain-relay.md. This test asserts a one-line
pointer naming plain-relay.md exists in the relay-discipline block,
and is load-bearing (removing it from an isolated tmp copy makes
check() raise, naming the file).

Block-scope grep idiom mirrors scripts/test_router_card_rule_tokens.py
(lines 62-99 extract_rules_block + 106-139 tmp_path non-vacuity).
The block is scoped to the "## Family relay discipline" section so a
token match in unrelated prose elsewhere cannot mask a real removal.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

TARGET = "loom-pipeline/hooks/family-relay.md"

# The pointer must name plain-relay.md (the contract file from Task 1).
POINTER_TOKEN = "plain-relay.md"

START_MARKER = "## Family relay discipline"


def extract_relay_block(text: str, rel_path: str) -> str:
    """Return the substring from the section header to end of file.

    Scoping to this substring (rather than the whole file) is what makes
    the check false-green-resistant: a token match outside the relay
    block does not count. family-relay.md is a single-section file, so
    the block runs from the header to EOF.
    """
    start = text.find(START_MARKER)
    if start == -1:
        raise ValueError(f"{START_MARKER!r} not found in {rel_path}")
    return text[start:]


def check(root: Path) -> None:
    """Assert family-relay.md's relay block carries a pointer to plain-relay.md.

    Raises AssertionError naming the file + missing token if the pointer
    is absent — the failure message is the actionable sweep item, not a
    bare mismatch.
    """
    text = (root / TARGET).read_text(encoding="utf-8")
    block = extract_relay_block(text, TARGET)
    if POINTER_TOKEN not in block:
        raise AssertionError(
            f"family-relay.md relay block does not point at the plain-relay "
            f"contract: expected a reference to {POINTER_TOKEN!r} in the "
            f"## Family relay discipline section of {TARGET}"
        )


def test_family_relay_points_at_plain_relay():
    check(REPO_ROOT)


def test_check_catches_a_removed_pointer(tmp_path):
    """Proves check() is load-bearing, not vacuous.

    The real tree currently satisfies check(), so the test above alone
    would stay green even if check() were a no-op. This test copies the
    REAL file into an isolated tmp_path (zero mutation residue in the
    real tree — house RED-on-extracted-copy pattern), removes the
    pointer line naming plain-relay.md from the copy, and shows check()
    actually raises, naming the file + token.
    """
    src = REPO_ROOT / TARGET
    dst = tmp_path / TARGET
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)

    check(tmp_path)  # baseline: unmutated copy passes

    mutated_path = tmp_path / TARGET
    text = mutated_path.read_text(encoding="utf-8")
    assert POINTER_TOKEN in text
    # Remove the line that carries the pointer (first occurrence line).
    lines = text.splitlines(keepends=True)
    kept = [ln for ln in lines if POINTER_TOKEN not in ln]
    mutated_path.write_text("".join(kept), encoding="utf-8")

    with pytest.raises(AssertionError) as exc_info:
        check(tmp_path)

    message = str(exc_info.value)
    assert POINTER_TOKEN in message
    assert TARGET in message