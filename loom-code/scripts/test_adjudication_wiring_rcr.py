"""Pin test: requesting-code-review wires to the adjudication-view protocol.

Task 7 of docs/loom/plans/2026-08-12-adjudication-view.md — asserts the two
pointer lines (SKILL.md Step 5, references/relay-phrasing.md) exist, and that
the machine-precise verdict-block fence wording in SKILL.md is byte-unchanged.
"""

import pathlib

SKILL_PATH = pathlib.Path(__file__).parent.parent / "skills" / "requesting-code-review" / "SKILL.md"
RELAY_PATH = (
    pathlib.Path(__file__).parent.parent
    / "skills"
    / "requesting-code-review"
    / "references"
    / "relay-phrasing.md"
)

# Verbatim fence wording pinned near the top of SKILL.md (§Asking the user
# boundary paragraph) — must survive the additive pointer edit unchanged.
FENCE_PHRASE = (
    "MUST stay machine-precise and keep every evidence citation"
)


def test_rcr_pointers_present_and_fence_intact():
    # @req: none (task-scoped wiring pin, not bound to a registered REQ-id)
    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    relay_text = RELAY_PATH.read_text(encoding="utf-8")

    assert "protocols/adjudication-view.md" in skill_text, (
        "SKILL.md missing pointer to adjudication-view.md"
    )
    assert "protocols/adjudication-view.md" in relay_text, (
        "relay-phrasing.md missing pointer to adjudication-view.md"
    )
    assert FENCE_PHRASE in skill_text, (
        "machine-precise fence wording changed or removed in SKILL.md"
    )
