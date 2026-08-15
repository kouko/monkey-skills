"""Structural grep-test guarding Task 18's validate-before-fan-out step in
spec-expansion SKILL.md §"Consuming a ui-flows.md seed" (docs/loom/plans/
2026-07-18-loop-convergence-fixes.md Task 18; design SSOT §4c Fix-4).

Before consuming a ui-flows.md seed, spec-expansion must run loom-spec's
`mint_critic_verdict.py validate` for `design-critic` over `DESIGN.md,
ui-flows.md`, proceed only on exit 0, and on non-zero STOP with a
per-exit-code routing (2 = never ran → design-critic; 3 = blocked →
design writer; 4 = stale → re-run design-critic). It must also follow the
existing Step-8-style path-resolution convention (script lives in the
PLUGIN repo, artifact in the CONSUMER project — absolute script path, cd
to consumer root), mirrored from loom-discovery/skills/user-insights/
SKILL.md Step 6 (shipped this branch, Task 3).

These checks assert on load-bearing PHRASES (intent), tolerant of wording
variation, so the test guards meaning without being brittle.

Stdlib only (pathlib + re). Resolve SKILL.md relative to this test file.
"""

import re
from pathlib import Path

SKILL = Path(__file__).parents[1] / "skills" / "spec-expansion" / "SKILL.md"


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _seed_section() -> str:
    """Just the '## Consuming a `ui-flows.md` seed' section body, so
    assertions don't accidentally pass by matching unrelated content
    elsewhere in the file."""
    text = _text()
    m = re.search(
        r"^## Consuming a `ui-flows\.md` seed.*?(?=\n## )",
        text,
        re.M | re.S,
    )
    assert m, "SKILL.md is missing the '## Consuming a `ui-flows.md` seed' section"
    return m.group(0)


def test_seed_section_documents_validate_before_fan_out_step():
    section = _seed_section()
    assert "mint_critic_verdict.py" in section
    assert "validate" in section
    # Some phrase gating the fan-out on the validate step running first.
    assert re.search(r"before .*fan.?out|fan.?out only after", section, re.I)


def test_invocation_names_design_critic_and_the_two_files():
    section = _seed_section()
    assert "--critic design-critic" in section or re.search(
        r"--critic\s+design-critic", section
    )
    assert "DESIGN.md,ui-flows.md" in section or re.search(
        r"DESIGN\.md,\s*ui-flows\.md", section
    )


def test_proceed_only_on_exit_0():
    section = _seed_section()
    assert re.search(r"exit(?:\s*code)?\s*0", section)
    assert re.search(r"proceed only on|only on exit 0", section, re.I)


def _bullet_block(section: str, pattern: str) -> str:
    """The bullet paragraph starting with `pattern`, up to the next
    top-level `- **exit` bullet or the end of the section — tolerates the
    routing sentence wrapping onto a following line."""
    m = re.search(pattern + r".*?(?=\n- \*\*exit|\Z)", section, re.I | re.S)
    return m.group(0) if m else ""


def test_all_three_nonzero_exit_codes_have_distinct_routing():
    section = _seed_section()
    # exit 2: design-critic never ran -> route to design-critic
    b2 = _bullet_block(section, r"exit\s*2")
    assert b2, "no documented routing for exit 2"
    assert re.search(r"never ran", b2, re.I)
    assert re.search(r"design-critic", b2)

    # exit 3: critic blocked the draft -> route back to the design writer
    b3 = _bullet_block(section, r"exit\s*3")
    assert b3, "no documented routing for exit 3"
    assert re.search(r"block", b3, re.I)
    assert re.search(r"design writer|interaction-flows", b3, re.I)

    # exit 4: artifacts edited since the verdict -> re-run design-critic
    b4 = _bullet_block(section, r"exit\s*4")
    assert b4, "no documented routing for exit 4"
    assert re.search(r"stale|edited|changed since", b4, re.I)
    assert re.search(r"re-run design-critic|re-run the critic", b4, re.I)

    # The three routings must be distinct from one another (not the same
    # sentence copy-pasted three times).
    assert len({b2, b3, b4}) == 3


def test_path_resolution_convention_documented():
    section = _seed_section()
    assert re.search(r"PLUGIN repo", section, re.I)
    assert re.search(r"CONSUMER project", section, re.I)
    assert re.search(r"absolute", section, re.I)
    assert re.search(r"cd\s", section)
