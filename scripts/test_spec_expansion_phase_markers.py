"""T12 leak-point guard: spec-expansion must announce phases in the
conversation language, not print the internal English phase marker
("— Phase ① USM backbone —") verbatim to chat. The internal phase
identifier stays referenced for the artifact (the spec delta); only
the print-verbatim-to-chat instruction is removed/replaced.

WHY this test exists: users mid-task saw undefined-abbreviation stage
names ("Phase ① USM backbone") printed verbatim to chat — a jargon
leak. The chat announcement must say in plain, conversation-language
words what the step does; the internal marker stays inside the
artifact only (plain-relay rule 6: announce stages in outcome
language, never internal markers).

Discriminator choice: the verbatim chat-marker shape is the
backtick-wrapped em-dash form `` `— Phase `` (backtick immediately
followed by em-dash + space + Phase). This is distinct from the
artifact-internal references at lines 410-422
(`` `## USM backbone` — Phase ① artifact ``), where the em-dash is
preceded by a space (`` ` — Phase ``), not a backtick. So
`` `— Phase `` matches ONLY the 5 chat-print instructions at lines
150/201/237/296/330, and never the internal artifact references that
must remain.

Block scoping: whole-file grep for "Phase" would be false-green-prone
(the internal IDs appear throughout). Scoping to the backtick-em-dash
shape `` `— Phase `` is what makes the check false-green-resistant.

Internal phase identifiers that must REMAIN (the artifact concept
stays; only the print-to-chat instruction goes): "Phase ①",
"Phase ②", "Phase ③", "USM backbone", "OOUX object model",
"auto-expansion matrix".

check(root) takes an arbitrary root so the non-vacuity test can run
against an extracted, perturbed temp copy without touching the real
tree (house pattern; repo memory: mutation/RED limited to extracted
copies).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_REL = "loom-spec/skills/spec-expansion/SKILL.md"

# The verbatim-to-chat phase marker: backtick + em-dash + space + Phase.
# This shape appears ONLY in the 5 print-to-chat instructions; the
# artifact-internal references use " — Phase" (space before em-dash),
# which does not match (no backtick immediately before the em-dash).
VERBATIM_CHAT_MARKER = "`— Phase"

# Internal phase identifiers that must remain referenced for the
# artifact (the spec delta). The phase concept stays; only the
# print-verbatim-to-chat instruction is removed.
INTERNAL_PHASE_IDS = (
    "Phase ①",          # Phase ①
    "Phase ②",          # Phase ②
    "Phase ③",          # Phase ③
    "USM backbone",
    "OOUX object model",
    "auto-expansion matrix",
)


def check(root: Path) -> None:
    """Assert the SKILL.md no longer instructs printing the verbatim
    internal phase marker to chat, AND still references the phase
    internally for the artifact.

    Raises AssertionError naming which invariant is violated — the
    failure message is the sweep list a real edit needs to act on.
    """
    text = (root / SKILL_REL).read_text(encoding="utf-8")

    if VERBATIM_CHAT_MARKER in text:
        raise AssertionError(
            f"spec-expansion SKILL.md still instructs printing the verbatim "
            f"internal phase marker to chat (found {VERBATIM_CHAT_MARKER!r} "
            f"…). Chat must announce the step in the conversation language, "
            f"not print the internal English phase marker. See plain-relay "
            f"rule 6 (loom-pipeline/hooks/plain-relay.md)."
        )

    missing = [pid for pid in INTERNAL_PHASE_IDS if pid not in text]
    if missing:
        raise AssertionError(
            f"spec-expansion SKILL.md lost internal phase identifiers that "
            f"the artifact (spec delta) still needs: {missing}. Only the "
            f"print-verbatim-to-chat instruction is removed; the phase "
            f"concept must stay referenced for the artifact."
        )


def test_no_verbatim_phase_marker_in_chat_instruction():
    check(REPO_ROOT)


def test_check_catches_a_reinserted_print_instruction(tmp_path):
    """Proves check() is load-bearing, not vacuous.

    The real tree currently satisfies check() (after GREEN), so the
    main test alone would stay green even if check() were a no-op. This
    test extracts the SKILL.md into an isolated tmp_path copy, reaches
    a GREEN-like baseline (neutralizing any residual markers so the
    baseline passes regardless of current tree state), then re-inserts
    one verbatim print-to-chat instruction and shows check() actually
    raises, naming the marker. Zero mutation residue in the real tree
    (house RED-on-extracted-copy pattern, mirroring
    test_router_card_rule_tokens.py's non-vacuity test).
    """
    dst = tmp_path / SKILL_REL
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REPO_ROOT / SKILL_REL, dst)

    text = dst.read_text(encoding="utf-8")
    # Neutralize the verbatim chat-marker shape to reach a GREEN-like
    # baseline, so this test proves load-bearing-ness in both RED and
    # GREEN tree states.
    neutralized = text.replace(VERBATIM_CHAT_MARKER, "`• Phase")
    dst.write_text(neutralized, encoding="utf-8")
    check(tmp_path)  # baseline: neutralized copy passes

    # Re-insert one verbatim print-to-chat instruction → check must raise.
    reinserted = neutralized.replace(
        "### Phase ① USM",
        "### Phase ① USM\n\n**Announce:** print `— Phase ① USM backbone —` before you start.\n",
        1,
    )
    dst.write_text(reinserted, encoding="utf-8")

    with pytest.raises(AssertionError) as exc_info:
        check(tmp_path)

    message = str(exc_info.value)
    assert VERBATIM_CHAT_MARKER in message