"""T1 drift guard: the plain-relay contract file must carry all 7 rule
lead-ins, the shared glossary header, and both calibration markers (✅/❌).

WHY this test exists: `loom-code/hooks/plain-relay.md` is the family-wide
single source every relay pointer and the SessionStart trigger card reference.
A silent removal of one rule (or of the glossary / calibration pair) from this
file breaks every downstream pointer without any signal. This test asserts the
load-bearing invariants survive.

Block scoping: the file is a single-purpose contract, so the whole file IS
the contract block — but we still scope to the substring between the H1 header
and the end of file to avoid matching unrelated prose elsewhere. Mirrors
test_router_card_rule_tokens.py's block-scope + tmp_path-mutation non-vacuity
idiom (house pattern; mutation/RED limited to extracted copies).

check(root) takes an arbitrary root so RED verification can run against an
extracted, perturbed temp copy without touching the real tree.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

CONTRACT_REL = "loom-code/hooks/plain-relay.md"

# Each rule's distinctive lead-in (the verbatim opening clause a reader/hooks
# keys off). Losing one from the contract silently breaks the pointers.
RULE_LEADINS = {
    1: "FIRST LINE = plain conclusion",
    2: "TRANSLATE every internal token via the glossary",
    3: "HARD CAPS",
    4: "ONE decision per ask",
    5: "NEVER lead with a raw gate/error string",
    6: "ANNOUNCE stages in outcome language",
    7: "STATUS SYMBOLS carry their meaning inline",
}

GLOSSARY_HEADER = "Shared glossary"
CALIBRATION_GOOD = "✅"
CALIBRATION_BAD = "❌"

START_MARKER = "# Plain-Relay Contract"


def extract_contract_block(text: str, rel_path: str) -> str:
    """Return the substring from the H1 header to end of file (the contract)."""
    start = text.find(START_MARKER)
    if start == -1:
        raise ValueError(f"{START_MARKER!r} not found in {rel_path}")
    return text[start:]


def check(root: Path) -> None:
    """Assert the contract file exists and carries every load-bearing token.

    Raises AssertionError naming each missing token — the failure message is
    the sweep list a real edit needs to act on, not a bare "mismatch".
    """
    contract_path = root / CONTRACT_REL
    if not contract_path.exists():
        raise AssertionError(f"contract file missing: {CONTRACT_REL}")

    text = contract_path.read_text(encoding="utf-8")
    block = extract_contract_block(text, CONTRACT_REL)

    missing: list[str] = []

    for rule_num, leadin in RULE_LEADINS.items():
        if leadin not in block:
            missing.append(f"rule {rule_num} lead-in ({leadin!r}) missing from {CONTRACT_REL}")

    if GLOSSARY_HEADER not in block:
        missing.append(f"glossary header ({GLOSSARY_HEADER!r}) missing from {CONTRACT_REL}")
    if CALIBRATION_GOOD not in block:
        missing.append(f"calibration good marker ({CALIBRATION_GOOD!r}) missing from {CONTRACT_REL}")
    if CALIBRATION_BAD not in block:
        missing.append(f"calibration bad marker ({CALIBRATION_BAD!r}) missing from {CONTRACT_REL}")

    if missing:
        raise AssertionError(
            "plain-relay contract presence mismatch:\n" + "\n".join(missing)
        )


def test_contract_has_seven_rules_and_glossary():
    check(REPO_ROOT)


def test_check_catches_a_removed_rule_leadin(tmp_path):
    """Proves check() is load-bearing, not vacuous.

    Extracts the REAL contract into an isolated tmp_path copy (zero mutation
    residue in the real tree — house RED-on-extracted-copy pattern), removes
    rule 3's lead-in from the copy, and shows check() actually raises, naming
    that rule + file.
    """
    src = REPO_ROOT / CONTRACT_REL
    dst = tmp_path / CONTRACT_REL
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)

    check(tmp_path)  # baseline: unmutated copy passes

    text = dst.read_text(encoding="utf-8")
    token = RULE_LEADINS[3]
    assert token in text
    dst.write_text(text.replace(token, "REMOVED", 1), encoding="utf-8")

    with pytest.raises(AssertionError) as exc_info:
        check(tmp_path)

    message = str(exc_info.value)
    assert "rule 3" in message
    assert token in message
    assert CONTRACT_REL in message