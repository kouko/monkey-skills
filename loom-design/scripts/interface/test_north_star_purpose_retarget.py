"""Guards Task 9 of docs/loom/plans/2026-08-20-north-star-serves-link.md:
the loom-design skills that derive from or check against the retired
`## North Star` section must instead name `PURPOSE.md`.

Task 2 retired `## North Star` from PRINCIPLES.md's authoring contract
(loom-design/skills/product-principles/). This test guards the sibling
consumers of that section: they must no longer instruct reading a
North Star section out of PRINCIPLES.md, and must each name PURPOSE.md
where they previously named the section.

Excluded on purpose: `product-principles/references/canon-product.md`
cites Amplitude's "North Star Framework" as a named external methodology —
a different thing, left alone (Task 2 already drew this line).

Stdlib only (pathlib + re). Resolve paths relative to this test file.
"""

from pathlib import Path

SKILLS_DIR = Path(__file__).parents[2] / "skills"

# Four files consumed the retired section; loom 1.0 deleted two of them
# (`using-loom-design` and `completeness-critic`), so the guard now covers
# the two that survive. It is deliberately NOT widened to the new stations:
# `capture-intent` and `write-spec` never read a North Star, so requiring
# them to name PURPOSE.md would assert something this test never asserted.
FILES = [
    SKILLS_DIR / "design-system" / "SKILL.md",
    SKILLS_DIR / "design-system" / "references" / "design-md-schema.md",
]

# Any surviving mention of "North Star" in these files would mean a
# consumer still instructs readers to look for a section that Task 2
# retired from PRINCIPLES.md's authoring contract.
_FORBIDDEN = "North Star"
_REQUIRED = "PURPOSE.md"


def test_no_loom_design_skill_reads_north_star_out_of_principles():
    for path in FILES:
        assert path.is_file(), f"expected file missing: {path}"
        text = path.read_text(encoding="utf-8")
        assert _FORBIDDEN not in text, (
            f"{path} still instructs reading a North Star section "
            f"(retired from PRINCIPLES.md by Task 2)"
        )


def test_each_file_names_purpose_md_instead():
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        assert _REQUIRED in text, (
            f"{path} does not name PURPOSE.md where it previously named "
            f"the North Star section"
        )
