"""T16 plain-relay pointer guard: verification-before-completion/SKILL.md must
reference the plain-relay contract AND instruct conclusion-first phrasing for
the "done" announcement.

WHY this test exists: "Done" is the moment the user most needs one plain line.
Before this task, verification-before-completion had NO relay/phrasing rule at
all — a confirmed coverage hole. This test pins the one-line pointer to
loom-code/hooks/plain-relay.md plus the conclusion-first /
one-sentence-test-result instruction so the hole does not silently reopen.

Block scoping: whole-file grep is false-green-prone (plain-relay.md could be
named in an unrelated section, masking removal of the actual pointer).
extract_done_block scopes the search to the Process section's step-5 region
(the "return verdict with evidence" block — the "done" announcement site),
mirroring test_router_card_rule_tokens.py's anchor-extraction pattern.

check(root) takes an arbitrary root so RED verification can run against an
extracted, perturbed temp copy without touching the real tree (house pattern;
repo memory: mutation/RED limited to extracted copies).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

SKILL_REL = "loom-code/skills/verification-before-completion/SKILL.md"

# Anchor lines that delimit the "done"-announcement block (Process step 5).
# Confirmed present in the unedited file (line 56 region).
START_MARKER = "If pass"
END_MARKER = "Boundaries & related skills"

# The load-bearing substrings the pointer + instruction must carry.
POINTER_TOKEN = "plain-relay.md"
CONCLUSION_FIRST_TOKEN = "conclusion-first"
ONE_SENTENCE_TOKEN = "one sentence"


def extract_done_block(text: str, rel_path: str) -> str:
    """Return the substring of the Process step-5 / "done" announcement region.

    Scoping to this substring (rather than the whole file) is what makes the
    check false-green-resistant: a token match elsewhere in the file does not
    count. The block runs from the "If pass" step-5 line through the end of the
    Process section (just before "## Boundaries & related skills").
    """
    start = text.find(START_MARKER)
    if start == -1:
        raise ValueError(f"{START_MARKER!r} not found in {rel_path}")
    end = text.find(END_MARKER, start)
    if end == -1:
        raise ValueError(f"{END_MARKER!r} not found in {rel_path}")
    return text[start:end]


def check(root: Path) -> None:
    """Assert the done-announcement block carries the plain-relay pointer and
    the conclusion-first / one-sentence-test-result instruction.

    Raises AssertionError naming each missing token — the failure message is
    the sweep list a real edit needs to act on, not a bare "mismatch".
    """
    text = (root / SKILL_REL).read_text(encoding="utf-8")
    block = extract_done_block(text, SKILL_REL)

    missing: list[str] = []
    for label, token in (
        ("plain-relay pointer", POINTER_TOKEN),
        ("conclusion-first instruction", CONCLUSION_FIRST_TOKEN),
        ("one-sentence-test-result instruction", ONE_SENTENCE_TOKEN),
    ):
        if token not in block:
            missing.append(f"{label} ({token!r}) missing from {SKILL_REL}")

    if missing:
        raise AssertionError(
            "verification-before-completion plain-relay pointer mismatch:\n"
            + "\n".join(missing)
        )


def test_verification_points_at_plain_relay():
    check(REPO_ROOT)


def test_check_catches_a_removed_pointer(tmp_path):
    """Proves check() is load-bearing, not vacuous.

    The real tree currently satisfies check() exactly, so the test above
    alone would stay green even if check() were a no-op. This test extracts
    the REAL SKILL.md into an isolated tmp_path copy (zero mutation residue
    in the real tree — house RED-on-extracted-copy pattern), removes the
    pointer token from the copy's done-announcement block, and shows check()
    actually raises, naming that token + file.
    """
    src = REPO_ROOT / SKILL_REL
    dst = tmp_path / SKILL_REL
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)

    check(tmp_path)  # baseline: unmutated copy passes

    text = dst.read_text(encoding="utf-8")
    assert POINTER_TOKEN in text
    dst.write_text(text.replace(POINTER_TOKEN, "REMOVED", 1), encoding="utf-8")

    with pytest.raises(AssertionError) as exc_info:
        check(tmp_path)

    message = str(exc_info.value)
    assert "plain-relay pointer" in message
    assert POINTER_TOKEN in message
    assert SKILL_REL in message