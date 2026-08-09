"""Guards the frozen spec key sets in `design_md_spec_keys.py`.

`design_md_spec_keys` is the in-repo frozen copy of `@google/design.md`'s
closed key sets (frozen-copy pattern per `loom-code/scripts/canonical/README.md`,
chosen because the spec format is `alpha` with no compatibility promise and CI
must not depend on the network). This test pins the three frozen sets and the
module's provenance record so any accidental edit to either is caught here
rather than surfacing as silent token loss downstream.

Stdlib only. No network, no `npx` invocation — the whole point of freezing
the sets in-repo is that CI needs neither.
"""

import pathlib
import re

import pytest

import design_md_spec_keys

SCHEMA_PATH = (
    pathlib.Path(__file__).resolve().parent.parent
    / "skills"
    / "design-system"
    / "references"
    / "design-md-schema.md"
)


def _schema_text() -> str:
    return SCHEMA_PATH.read_text(encoding="utf-8")


def _section(text: str, start_heading: str, end_heading: str) -> str:
    """Slice `text` from `start_heading` up to (not including) `end_heading`."""
    start = text.index(start_heading)
    end = text.index(end_heading, start)
    return text[start:end]


def _fenced_yaml_block(section: str) -> str:
    """Return the contents of the section's first fenced ```yaml block."""
    match = re.search(r"```yaml\n(.*?)```", section, re.DOTALL)
    assert match, "section has no fenced ```yaml block"
    return match.group(1)


def _nested_mapping(yaml_block: str, top_key: str) -> dict:
    """Parse `top_key:`'s two-level nested mapping into {name: {key: value}}.

    LOOM-SIMPLIFY: hand-rolled indentation walker, not a full YAML parser
    (no PyYAML — loom-siblings-ci.yml installs pytest only, matching the
    stdlib-only constraint `design_md_spec_keys.py` already documents for
    this plugin's scripts/). Handles exactly the two-level shape this
    reference emits (`top_key:` -> name -> `key: value`); a third nesting
    level, YAML lists, or multiline scalars under `top_key:` are unsupported.
    A property line indented off the level's established property indent
    (deeper OR shallower) raises `AssertionError` instead of being
    silently dropped — closed 2026-08-10 after T2's code-quality review
    found the drop.
    | ceiling: the fenced yaml block under `typography:` or `components:`
    grows a list, anchor, multiline scalar, or a third nesting level
    (indentation drift within the two supported levels is no longer a
    ceiling — it now raises) | upgrade: add
    `python3 -m pip install pyyaml` to loom-siblings-ci.yml's install step
    and replace this walker with `yaml.safe_load(block)[top_key]`
    | ref: docs/loom/plans/2026-08-10-design-md-spec-conformance.md Task 3
    """
    lines = [line for line in yaml_block.splitlines() if line.strip()]
    top_idx = next(
        (i for i, line in enumerate(lines) if line.strip() == f"{top_key}:"),
        None,
    )
    assert top_idx is not None, f"no `{top_key}:` mapping in yaml block"
    top_indent = len(lines[top_idx]) - len(lines[top_idx].lstrip(" "))

    result: dict = {}
    level_indent = None
    prop_indent = None
    current_name = None
    for line in lines[top_idx + 1 :]:
        indent = len(line) - len(line.lstrip(" "))
        if indent <= top_indent:
            break
        stripped = line.strip()
        if level_indent is None:
            level_indent = indent
        if indent == level_indent:
            current_name = stripped.rstrip(":")
            result[current_name] = {}
            prop_indent = None
        elif indent > level_indent and current_name is not None and ":" in stripped:
            if prop_indent is None:
                prop_indent = indent
            assert indent == prop_indent, (
                f"inconsistent property indentation under '{current_name}': "
                f"expected indent {prop_indent}, got {indent} for line {stripped!r}"
            )
            prop_key, _, prop_value = stripped.partition(":")
            result[current_name][prop_key.strip()] = prop_value.strip()
    return result


def test_frozen_sets_carry_provenance():
    assert design_md_spec_keys.TOKEN_GROUPS == {
        "colors",
        "typography",
        "rounded",
        "spacing",
        "components",
    }
    assert design_md_spec_keys.TYPOGRAPHY_PROPERTIES == {
        "fontFamily",
        "fontSize",
        "fontWeight",
        "lineHeight",
        "letterSpacing",
        "fontFeature",
        "fontVariation",
    }
    assert design_md_spec_keys.COMPONENT_SUB_TOKENS == {
        "backgroundColor",
        "textColor",
        "typography",
        "rounded",
        "padding",
        "size",
        "height",
        "width",
    }
    assert "0.4.0" in design_md_spec_keys.PROVENANCE
    assert "npx @google/design.md@0.4.0 spec" in design_md_spec_keys.PROVENANCE


def test_nested_mapping_raises_on_indentation_drift():
    """A property indented deeper than its siblings must not vanish silently.

    Task-2 code-quality review found `_nested_mapping` captured property
    lines only at a level's first-observed indent, so a key indented
    deeper than its siblings was silently dropped from the extracted set
    — a hole that would let T3's exclusivity assertion pass without ever
    grading the dropped key. This pins the fix: a deeper-indented sibling
    must surface as a loud failure, not vanish quietly.
    """
    yaml_block = (
        "components:\n"
        "  button:\n"
        "    backgroundColor: \"{colors.primary}\"\n"
        "      textColor: \"{colors.background}\"\n"  # deeper than sibling
        "    rounded: \"{rounded.md}\"\n"
    )
    with pytest.raises(AssertionError):
        _nested_mapping(yaml_block, "components")


def test_typography_properties_are_all_spec_recognised():
    text = _schema_text()
    section = _section(text, "## Typography", "## Layout")
    yaml_block = _fenced_yaml_block(section)
    levels = _nested_mapping(yaml_block, "typography")

    # (a) structure present: at least one typography level name carries
    # nested keys. This also guards against (b) passing vacuously on an
    # empty extraction.
    assert any(props for props in levels.values()), (
        "no typography level carries nested property keys"
    )

    # (b) properties whitelisted: every key extracted at the nested-under-a-
    # level depth is a member of TYPOGRAPHY_PROPERTIES. Level NAMES
    # themselves are never inspected — the spec leaves that position open.
    extracted_properties = {key for props in levels.values() for key in props}
    unrecognised = extracted_properties - design_md_spec_keys.TYPOGRAPHY_PROPERTIES
    assert not unrecognised, (
        f"typography properties not in the spec whitelist: {unrecognised}"
    )


def test_component_sub_tokens_are_complete_and_exclusive():
    text = _schema_text()
    section = _section(text, "## Components", "## Do's & Don'ts")

    # (a) completeness: every member of COMPONENT_SUB_TOKENS is named
    # somewhere in the ## Components section.
    missing = {
        token
        for token in design_md_spec_keys.COMPONENT_SUB_TOKENS
        if token not in section
    }
    assert not missing, (
        f"component sub-tokens not documented in ## Components: {missing}"
    )

    yaml_block = _fenced_yaml_block(section)
    components = _nested_mapping(yaml_block, "components")

    # (b) extraction non-empty: the `components:` mapping yields at least
    # one component with nested keys. This guards against (c) passing
    # vacuously on an empty extraction.
    assert any(props for props in components.values()), (
        "no component carries nested property keys"
    )

    # (c) exclusivity: every key at the nested-under-a-component depth is
    # a member of COMPONENT_SUB_TOKENS. Component/variant NAMES
    # themselves (`button`, `button-primary`, `button-primary-hover`, …)
    # and `{...}` brace-reference VALUES are outside the extracted set by
    # construction.
    extracted_keys = {key for props in components.values() for key in props}
    unrecognised = extracted_keys - design_md_spec_keys.COMPONENT_SUB_TOKENS
    assert not unrecognised, (
        f"component keys not in the spec whitelist: {unrecognised}"
    )
