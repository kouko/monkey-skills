"""RED/GREEN test for onramp-explicit-choice-gate Task 2.

Pins the reworded on-ramp criteria section of
loom-code/hooks/family-reception.md: a standalone ask, a `pending`
brief state, an explicit never-record-for-the-user rule, and a repo-
level standing-choices grammar.

No REQ-id is registered in the living-spec namespace for this arc
(brief item BI-5 is not a REQ-<n>), so no `@req` tag is applied here
per the implementer contract's namespace guard.
"""
from pathlib import Path

RECEPTION_PATH = (
    Path(__file__).resolve().parent.parent / "hooks" / "family-reception.md"
)


def test_reception_requires_standalone_ask_pending_and_standing_choices():
    text = RECEPTION_PATH.read_text(encoding="utf-8")

    for must_contain in (
        "standalone ask",
        "pending",
        "never record",
        "## On-ramp standing choices",
        "standing <direct|detour>",
    ):
        assert must_contain in text, f"missing required substring: {must_contain!r}"

    for must_not_contain in (
        "proceed either way",
        "never blocking prerequisites",
        "fold the on-ramp recommendation",
    ):
        assert must_not_contain not in text, (
            f"stale substring still present: {must_not_contain!r}"
        )
