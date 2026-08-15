"""T5 SSOT drift guard: family-reception.md carries the canonical
`## Brief before a complex fork` section that the 6 scattered copies
(T6-T11) will point to.

WHY this test exists: the brief-before-fork trigger template was
copy-pasted across 6 router/skill files with wording drift. T5
establishes one SSOT section in the reception; the rest point at it.
This test pins the SSOT section's presence and its load-bearing tokens,
so a silent removal or drift here is caught before the pointers
orphan.

Block scoping: whole-file grep is false-green-prone (a token could
appear in unrelated prose elsewhere in the file and mask a real
removal from the SSOT section itself). extract_section scopes the
token search to the text between the `## Brief before a complex fork`
heading and the next `## ` heading — so a token match outside the
section does not count.

check(root) takes an arbitrary root so RED verification can run against
an extracted, perturbed temp copy without touching the real tree
(house pattern; mutation/RED limited to extracted copies).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

RECEPTION = "loom-pipeline/hooks/family-reception.md"

SECTION_HEADING = "## Brief before a complex fork"

# Load-bearing tokens the SSOT section must carry. The threshold triple
# is the trigger; brief-before-asking is the action; stakes-first is the
# framing the brainstorming copy adds (the consolidated, non-drifted form).
SECTION_TOKENS = (
    "≥3 trade-offs",
    "≥2 implementation paths",
    "architectural blast radius",
    "brief-before-asking",
)


def extract_section(text: str) -> str:
    """Return the `## Brief before a complex fork` section body.

    Scoping to this substring (rather than the whole file) is what makes
    the check false-green-resistant: a token match outside the section
    does not count. Raises ValueError if the heading is absent.
    """
    start = text.find(SECTION_HEADING)
    if start == -1:
        raise ValueError(f"{SECTION_HEADING!r} heading not found")
    # next `## ` heading after the section heading (excludes the heading
    # line itself, which is the start anchor).
    next_heading = text.find("\n## ", start + len(SECTION_HEADING))
    if next_heading == -1:
        section = text[start:]
    else:
        section = text[start:next_heading]
    return section


def check(root: Path) -> None:
    """Assert the SSOT section exists and carries every load-bearing token.

    Raises AssertionError naming each missing token — the failure message
    is the sweep list a real edit needs to act on, not just a bare
    "missing".
    """
    text = (root / RECEPTION).read_text(encoding="utf-8")
    section = extract_section(text)

    missing: list[str] = []
    for token in SECTION_TOKENS:
        if token not in section:
            missing.append(f"token {token!r} missing from SSOT section")

    if missing:
        raise AssertionError(
            "brief-before-fork SSOT section token presence mismatch:\n"
            + "\n".join(missing)
        )


def test_reception_has_brief_before_fork_section():
    check(REPO_ROOT)


def test_check_catches_a_removed_token(tmp_path):
    """Proves check() is load-bearing, not vacuous.

    The real tree currently satisfies check() exactly, so the test above
    alone would stay green even if check() were a no-op. This test copies
    family-reception.md into an isolated tmp_path (zero mutation residue
    in the real tree — house RED-on-extracted-copy pattern), removes the
    `≥3 trade-offs` token from the SSOT section, and shows check()
    actually raises, naming that token.
    """
    src = REPO_ROOT / RECEPTION
    dst = tmp_path / RECEPTION
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)

    check(tmp_path)  # baseline: unmutated copy passes

    text = dst.read_text(encoding="utf-8")
    token = SECTION_TOKENS[0]
    assert token in text
    dst.write_text(text.replace(token, "REMOVED", 1), encoding="utf-8")

    with pytest.raises(AssertionError) as exc_info:
        check(tmp_path)

    message = str(exc_info.value)
    assert token in message


def test_check_catches_a_removed_section(tmp_path):
    """Proves check() raises when the whole SSOT section is deleted — not
    just when a token drifts. A section deletion is the dedup-undoing
    failure mode this guard exists to catch.
    """
    src = REPO_ROOT / RECEPTION
    dst = tmp_path / RECEPTION
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)

    check(tmp_path)  # baseline: unmutated copy passes

    text = dst.read_text(encoding="utf-8")
    start = text.find(SECTION_HEADING)
    assert start != -1
    next_heading = text.find("\n## ", start + len(SECTION_HEADING))
    if next_heading == -1:
        mutated = text[:start]
    else:
        mutated = text[:start] + text[next_heading:]
    dst.write_text(mutated, encoding="utf-8")

    with pytest.raises((AssertionError, ValueError)):
        check(tmp_path)