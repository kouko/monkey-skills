"""Tests for validate_design_output.py — the DESIGN.md structure check.

The gap this closes (W2 adversary P08): `design_md_spec_keys.py` froze the
spec's `TOKEN_GROUPS` and then nothing ever compared a DESIGN.md against
them, so a file keeping one group out of five and inventing a sixth was
accepted everywhere.
"""

from pathlib import Path

import pytest
from design_md_spec_keys import TOKEN_GROUPS
from validate_design_output import validate

_VALID = """\
# Design system
ratified-by: Alex Rivera 2026-09-02

## colors
- background: "#101014"
- text: "#f2f2f5"

## typography
- fontFamily: Inter
- fontSize: 16px

## rounded
- md: 8px

## spacing
- md: 12px

## components
- button.backgroundColor: colors.text
"""


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "DESIGN.md"
    path.write_text(text, encoding="utf-8")
    return path


def test_a_complete_design_md_passes(tmp_path):
    ok, problems = validate(_write(tmp_path, _VALID))
    assert ok, problems


def test_missing_file_fails(tmp_path):
    ok, problems = validate(tmp_path / "nope.md")
    assert not ok
    assert any("does not exist" in p for p in problems)


@pytest.mark.parametrize("group", sorted(TOKEN_GROUPS))
def test_every_token_group_is_required(tmp_path, group):
    text = _VALID.replace(f"## {group}", "## vibes")
    ok, problems = validate(_write(tmp_path, text))
    assert not ok
    assert any(group in p for p in problems)


def test_an_empty_group_section_fails(tmp_path):
    text = _VALID.replace('- md: 8px\n', "")
    ok, problems = validate(_write(tmp_path, text))
    assert not ok
    assert any("rounded" in p and "no items" in p for p in problems)


def test_the_p08_shape_is_caught(tmp_path):
    """One group kept, a sixth invented — exactly the probe's file."""
    text = (
        "# Design system\nratified-by: kouko 2026-09-02\n\n"
        '## colors\n- background: "#8a8a8a"\n- text: "#9c9c9c"\n\n'
        "## vibes\n- energy: high\n"
    )
    ok, problems = validate(_write(tmp_path, text))
    assert not ok


def test_a_missing_ratified_by_is_a_valid_draft(tmp_path):
    text = _VALID.replace("ratified-by: Alex Rivera 2026-09-02\n", "")
    ok, problems = validate(_write(tmp_path, text))
    assert ok, problems


@pytest.mark.parametrize("bad_line", [
    "ratified-by: Alex Rivera\n",
    "ratified-by: 2026-09-02\n",
    "ratified-by: Alex Rivera 09-02-2026\n",
    "ratified-by: Alex Rivera 2026-13-45\n",
    "ratified-by:\n",
])
def test_a_malformed_ratified_by_fails(tmp_path, bad_line):
    text = _VALID.replace("ratified-by: Alex Rivera 2026-09-02\n", bad_line)
    ok, problems = validate(_write(tmp_path, text))
    assert not ok


def test_cli_exits_zero_on_a_valid_file(tmp_path):
    from validate_design_output import main
    assert main([str(_write(tmp_path, _VALID))]) == 0


def test_cli_exits_one_on_an_invalid_file(tmp_path):
    from validate_design_output import main
    assert main([str(_write(tmp_path, _VALID.replace("## spacing", "## vibes")))]) == 1
