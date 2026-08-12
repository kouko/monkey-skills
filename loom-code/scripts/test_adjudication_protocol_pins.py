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


def _firing_conditions_section(text: str) -> str:
    """Slice out just the ## Firing conditions section body. Assertions
    that pin the firing-condition promise MUST run against this slice,
    not the whole document -- tokens like "supported", "zh-Hant", and
    "`ja`" also occur in other sections (the modality tables, the
    negation-tier table), so a document-wide `in text` check keeps
    passing even when the Firing-conditions section itself is reverted
    to the old, retired "not English" wording. (Revision round 1: both
    reviewers found exactly this via mutation probe.)"""
    return text.split("## Firing conditions", 1)[1].split("\n## ", 1)[0]


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

    # Firing conditions — both. The language condition was rewritten in
    # Task 4 to name supported profiles instead of the unkeepable "not
    # English" promise (see test_protocol_names_supported_languages_and_tiers
    # for the full pin on the new wording); this assertion now checks the
    # supported-profile phrasing, not the retired wording. Sliced to the
    # section itself -- see _firing_conditions_section.
    firing = _firing_conditions_section(text)
    assert (
        "supported" in firing and "zh-Hant" in firing
    ), "language firing condition missing"
    assert (
        "verdict mode fires only when findings" in firing
        and "1" in firing
    ), "verdict-mode firing condition missing"


def test_protocol_names_supported_languages_and_tiers():
    """The rewritten firing condition must name the two supported
    profiles (zh-Hant, ja) instead of the unkeepable "not English"
    promise, state each language's negation tier, carry a ja modality
    table, and record both JIS caveats -- "derived from" (never "per")
    plus the 参考 (reference, not normative) label. This pins Task 4's
    honest-firing-condition rewrite so a later edit cannot silently
    re-widen the promise back to "any non-English language"."""
    text = PROTOCOL_PATH.read_text(encoding="utf-8")
    firing = _firing_conditions_section(text)

    # Both supported language tags named in the firing condition itself
    # (sliced -- see _firing_conditions_section).
    assert "zh-Hant" in firing and "`ja`" in firing, "supported language tags missing"

    # The N/A-loud promise: a non-English, non-profile language says so
    # and produces nothing, rather than silently dropping the bullet.
    assert "N/A-loud" in firing, "N/A-loud promise missing"

    # Per-language negation tier, both directions.
    assert "hard-fail" in text, "zh-Hant negation tier missing"
    assert "warning" in text, "ja negation tier missing"

    # A ja modality table -- at least one JIS-derived form present.
    assert "しなければならない" in text, "ja modality table missing"

    # "derived from", never "per"/"conformant" for the JIS caveat.
    assert "derived from" in text, "'derived from' wording missing"

    # The 参考 caveat, stated plainly.
    assert "参考" in text, "参考 (reference-only) caveat missing"
    assert (
        "この規格で規定する事項ではない" in text
    ), "JIS verbatim 参考 quote missing"
