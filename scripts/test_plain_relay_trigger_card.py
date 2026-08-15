"""Task 2 drift guard: the <PLAIN-RELAY> trigger card must be present verbatim
in loom-pipeline/hooks/family-reception.md so the SessionStart bash script
(hooks/session-start cats the whole file at line 37) preloads it every session.

WHY this test exists: a local A/B proved an imperative short card preloaded
every session beats a descriptive long doc (2/2 vs 0/2). The card is a contract
surface — its wording must not drift. This test asserts the literal opener and
the four bullet lines are present inside the card block.

Block scoping: whole-file grep is false-green-prone. The check scopes to the
<PLAIN-RELAY> ... </PLAIN-RELAY> block so a token match outside the card does
not count (mirrors test_router_card_rule_tokens.py:62-99).

Non-vacuity: a tmp_path-mutation test removes one bullet from an isolated copy
and shows check() raises naming that bullet (mirrors
test_router_card_rule_tokens.py:106-139).
"""

import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RECEPTION_REL = "loom-pipeline/hooks/family-reception.md"

CARD_OPEN = "<PLAIN-RELAY>"
CARD_CLOSE = "</PLAIN-RELAY>"

# The four bullet lines — verbatim substrings that must appear inside the card.
BULLET_LINES = [
    "1st line = plain-language conclusion, in the conversation language.",
    "Translate every internal token (PASS_WITH_NOTES, Axis, Wave,",
    "Default reply ≤10 lines; ONE decision per ask (≤3 options + a recommended default).",
    "Never lead with a raw gate/error string — plain words first.",
]


def extract_card_block(text: str, rel_path: str) -> str:
    """Return the substring inside <PLAIN-RELAY> ... </PLAIN-RELAY>.

    Scoping to this substring (not the whole file) is what makes the check
    false-green-resistant: a bullet appearing in unrelated prose outside the
    card does not count.
    """
    start = text.find(CARD_OPEN)
    if start == -1:
        raise ValueError(f"{CARD_OPEN!r} not found in {rel_path}")
    end = text.find(CARD_CLOSE, start)
    if end == -1:
        raise ValueError(f"{CARD_CLOSE!r} not found in {rel_path}")
    return text[start : end + len(CARD_CLOSE)]


def check(root: Path) -> None:
    """Assert the <PLAIN-RELAY> card with all four bullet lines is present."""
    reception = root / RECEPTION_REL
    text = reception.read_text(encoding="utf-8")
    block = extract_card_block(text, RECEPTION_REL)

    missing: list[str] = []
    for bullet in BULLET_LINES:
        if bullet not in block:
            missing.append(f"bullet {bullet!r} missing from the PLAIN-RELAY card in {RECEPTION_REL}")

    if missing:
        raise AssertionError(
            "PLAIN-RELAY card bullet-line presence mismatch:\n" + "\n".join(missing)
        )


def test_reception_contains_plain_relay_card():
    check(REPO_ROOT)


def test_check_catches_a_removed_bullet(tmp_path):
    """Proves check() is load-bearing, not vacuous.

    Copies the real reception into an isolated tmp_path, confirms the
    unmutated copy passes, then removes one bullet line from the card block
    and shows check() raises naming that bullet.
    """
    src = REPO_ROOT / RECEPTION_REL
    dst = tmp_path / RECEPTION_REL
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)

    check(tmp_path)  # baseline: unmutated copy passes

    mutated_text = dst.read_text(encoding="utf-8")
    removed = BULLET_LINES[0]
    assert removed in mutated_text
    dst.write_text(mutated_text.replace(removed, "REMOVED", 1), encoding="utf-8")

    with pytest.raises(AssertionError) as exc_info:
        check(tmp_path)

    message = str(exc_info.value)
    assert removed in message
    assert RECEPTION_REL in message