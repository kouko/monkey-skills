"""T4 drift guard: relay-phrasing.md must point at the family-wide
plain-relay contract (loom-pipeline/hooks/plain-relay.md).

WHY this test exists: the review-report phrasing rules in
relay-phrasing.md (rules 2/4 + the ✅/❌ pair) are ONE instance of the
family-wide plain-language contract. Without a pointer, a reader
treats them as a local-only rule and misses the shared glossary /
hard caps / conclusion-first discipline. This test asserts the pointer
is present so a future edit that drops it fails loud.

Non-vacuity: the real tree currently does NOT carry the pointer (pre-T4),
so test_relay_phrasing_points_at_plain_relay is RED until T4 adds it.
test_check_catches_a_removed_pointer proves the check is load-bearing by
removing the pointer from an extracted tmp_path copy and showing check()
raises, naming the file + the missing pointer token.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

RELAY_PHRASING = "loom-code/skills/requesting-code-review/references/relay-phrasing.md"
POINTER_TOKEN = "plain-relay.md"


def check(root: Path) -> None:
    """Assert relay-phrasing.md references the family plain-relay contract.

    Raises AssertionError naming the file + missing token when the pointer
    is absent — the failure message is the action a real edit must take,
    not a bare mismatch.
    """
    text = (root / RELAY_PHRASING).read_text(encoding="utf-8")
    if POINTER_TOKEN not in text:
        raise AssertionError(
            f"pointer to family plain-relay contract ({POINTER_TOKEN!r}) "
            f"missing from {RELAY_PHRASING}"
        )


def test_relay_phrasing_points_at_plain_relay():
    check(REPO_ROOT)


def test_check_catches_a_removed_pointer(tmp_path):
    """Proves check() is load-bearing, not vacuous.

    Copies the REAL relay-phrasing.md into an isolated tmp_path, confirms
    check() passes on the unmutated copy (post-T4 baseline), then strips
    the pointer token and shows check() raises, naming the file + token.
    Zero mutation residue in the real tree (house RED-on-extracted-copy
    pattern, mirroring test_router_card_rule_tokens.py's non-vacuity test).
    """
    src = REPO_ROOT / RELAY_PHRASING
    dst = tmp_path / RELAY_PHRASING
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)

    # baseline: unmutated copy passes (post-T4)
    check(tmp_path)

    # strip the pointer token from the copy
    text = dst.read_text(encoding="utf-8")
    assert POINTER_TOKEN in text, "precondition: copy must carry the pointer"
    dst.write_text(text.replace(POINTER_TOKEN, "REMOVED"), encoding="utf-8")

    with pytest.raises(AssertionError) as exc_info:
        check(tmp_path)

    message = str(exc_info.value)
    assert POINTER_TOKEN in message
    assert RELAY_PHRASING in message