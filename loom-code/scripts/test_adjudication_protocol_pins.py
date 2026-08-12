"""Pin test for the adjudication-view protocol SSOT.

Task 0 of docs/loom/plans/2026-08-12-adjudication-view.md. The protocol
file (`loom-code/skills/using-loom-code/protocols/adjudication-view.md`)
is the SSOT every later task (splitter/lint/renderer/wiring) implements
against — this test pins its load-bearing content literally, so a
future edit cannot silently drop a contract clause the other tasks
depend on.
"""

from pathlib import Path

PROTOCOL_PATH = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "using-loom-code"
    / "protocols"
    / "adjudication-view.md"
)


def test_protocol_carries_modality_table_and_unit_rule():
    """The protocol file must exist and pin: the fixed modality mapping
    (all five arrow pairs), the unit-1:1 rule, the units-JSON schema
    field list, and both firing conditions — each of these is a
    contract clause a downstream task (split/lint/render/wiring)
    implements against, so a silent drop must fail this test."""
    assert PROTOCOL_PATH.exists(), f"protocol file missing: {PROTOCOL_PATH}"
    text = PROTOCOL_PATH.read_text(encoding="utf-8")

    # Fixed modality mapping table — five arrow pairs, verbatim.
    for pair in ("must→必須", "should→應", "may→可", "must not→不得", "should not→不應"):
        assert pair in text, f"modality mapping missing: {pair}"

    # unit-1:1 rule — one rendition unit per source unit.
    assert "one rendition unit per source unit" in text, "unit-1:1 rule missing"

    # units-JSON schema field list.
    assert (
        "unit id`, `heading`, `source_text`, `anchors`, `rendition`" in text
    ), "units-JSON schema field list missing"

    # Firing conditions — both.
    assert (
        "fires only when live conversation language is not English" in text
    ), "language firing condition missing"
    assert (
        "verdict mode fires only when findings" in text
        and "1" in text
    ), "verdict-mode firing condition missing"
