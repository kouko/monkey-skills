"""Structural grep-test guarding `handoff-brief-format.md`'s
`## Current State Evidence` section being anchor-primary (not
line-number-first).

The reference is prose, not executable code. Its correctness is the
PRESENCE of anchor-primary wording within the `### `## Current State
Evidence`` subsection of `## Required sections`, and an anchor-primary
anti-pattern bullet inside `## Anti-patterns`. A line number is optional
precision; the anchor (a verbatim string or a stable heading) is the
required citation.

Stdlib only (pathlib + re). Resolve the reference relative to this test
file.
"""

import re
from pathlib import Path

REFERENCE = (
    Path(__file__).parent
    / ".."
    / "skills"
    / "brainstorming"
    / "references"
    / "handoff-brief-format.md"
).resolve()

SKILL_DIR = REFERENCE.parent.parent

AUTHOR_SURFACES = (
    SKILL_DIR / "SKILL.md",
    SKILL_DIR / "README.md",
    SKILL_DIR / "README.zh-TW.md",
    SKILL_DIR / "README.ja.md",
    REFERENCE.parent / "red-flags.md",
)

LOCALIZED_README_SEMANTICS = {
    "README.zh-TW.md": (
        ("path", "逐字字串", "穩定標題"),
        ("行號", "可選", "歧義"),
    ),
    "README.ja.md": (
        ("path", "逐語文字列", "安定した見出し"),
        ("行番号", "任意", "曖昧"),
    ),
}


def _text() -> str:
    assert REFERENCE.is_file(), f"handoff-brief-format.md is absent at {REFERENCE}"
    return REFERENCE.read_text(encoding="utf-8")


def _section(text: str, heading_pattern: str) -> str:
    """Return the body of the first `##`-level section whose heading matches
    heading_pattern, up to (not including) the next `##`-level heading."""
    match = re.search(
        rf"^##\s+{heading_pattern}\s*$", text, re.MULTILINE
    )
    assert match is not None, f"heading matching {heading_pattern!r} not found"
    rest = text[match.end():]
    next_heading = re.search(r"^##\s+\S", rest, re.MULTILINE)
    return rest[: next_heading.start()] if next_heading else rest


def _subsection(text: str, heading_pattern: str) -> str:
    """Return the body of the first `###`-level subsection whose heading
    matches heading_pattern, up to the next `###`- or `##`-level heading."""
    match = re.search(
        rf"^###\s+{heading_pattern}\s*$", text, re.MULTILINE
    )
    assert match is not None, f"subsection matching {heading_pattern!r} not found"
    rest = text[match.end():]
    next_heading = re.search(r"^(?:##|###)\s+\S", rest, re.MULTILINE)
    return rest[: next_heading.start()] if next_heading else rest


def _flatten(text: str) -> str:
    """Collapse whitespace runs to single spaces for whitespace-insensitive
    substring matching."""
    return re.sub(r"\s+", " ", text)


def test_current_state_evidence_is_anchor_primary():
    text = _text()

    required_sections = _section(text, r"Required sections")
    cse = _subsection(required_sections, r"`## Current State Evidence`")
    flat = _flatten(cse)

    # The section frames the citation as anchor-primary: a path must be paired
    # with either supported anchor form, while a line number is conditional.
    assert "requires a path paired with an anchor" in flat.lower(), (
        "§Current State Evidence must require a path paired with its anchor"
    )
    assert "verbatim string" in flat.lower() and "stable heading" in flat.lower(), (
        "§Current State Evidence must retain both permitted anchor forms"
    )
    assert "line number is optional precision only when the anchor alone is ambiguous" in flat.lower(), (
        "§Current State Evidence must limit optional line precision to cases "
        "where the anchor alone is ambiguous"
    )

    # The five sub-bullets describe their citation as an anchor (not as
    # `file:line`).
    assert "file:line" not in cse, (
        "§Current State Evidence sub-bullets must not keep the line-number-first "
        "`file:line` phrasing as the citation requirement"
    )


def test_copyable_template_current_state_evidence_is_anchor_primary():
    text = _text()
    template_marker = "## Template"
    assert template_marker in text, "handoff brief must retain its copyable template"
    template = text.split(template_marker, 1)[1]
    match = re.search(
        r"^## Current State Evidence\s*$\n(?P<body>.*?)(?=^## \S)",
        template,
        re.MULTILINE | re.DOTALL,
    )
    assert match is not None, "copyable template must contain Current State Evidence"
    flat = _flatten(match.group("body")).lower()

    assert "each item requires a path plus an anchor" in flat, (
        "copyable template must require path-plus-anchor evidence per item"
    )
    assert "verbatim string" in flat and "stable heading" in flat, (
        "copyable template must name both permitted anchor forms"
    )
    assert "line number is optional precision only when the anchor alone is ambiguous" in flat, (
        "copyable template must condition line precision on anchor ambiguity"
    )


def test_current_state_evidence_selects_anchors_by_artifact_type():
    text = _text()
    required_sections = _section(text, r"Required sections")
    explanatory = _flatten(
        _subsection(required_sections, r"`## Current State Evidence`")
    ).lower()

    template_marker = "## Template"
    template = text.split(template_marker, 1)[1]
    match = re.search(
        r"^## Current State Evidence\s*$\n(?P<body>.*?)(?=^## \S)",
        template,
        re.MULTILINE | re.DOTALL,
    )
    assert match is not None, "copyable template must contain Current State Evidence"
    copyable = _flatten(match.group("body")).lower()

    for surface_name, surface in (
        ("explanatory guidance", explanatory),
        ("copyable template", copyable),
    ):
        assert "prose" in surface and "stable heading" in surface and "distinctive phrase" in surface, (
            f"{surface_name} must select prose anchors by stable heading or distinctive phrase"
        )
        assert all(term in surface for term in ("code", "function", "class", "method", "signature", "constant", "distinctive message")), (
            f"{surface_name} must select code anchors by signature, constant, or distinctive message"
        )
        assert all(term in surface for term in ("config/data", "key path", "distinctive value fragment")), (
            f"{surface_name} must select config/data anchors by key path plus value fragment"
        )


def test_anti_pattern_bullet_is_anchor_primary():
    text = _text()
    anti = _section(text, r"Anti-patterns")
    flat = _flatten(anti)

    # The anti-pattern bullet that was previously "bullets without `file:line`
    # citations defeat the purpose" must invert to anchor-primary.
    assert "anchor" in flat.lower(), (
        "§Anti-patterns must carry an anchor-primary anti-pattern bullet"
    )
    # The old line-number-first anti-pattern wording must be gone.
    assert "without `file:line` citations" not in flat, (
        "§Anti-patterns must drop the line-number-first 'without `file:line` "
        "citations' wording"
    )


def test_brief_author_surfaces_are_anchor_primary():
    english_surfaces = tuple(
        path for path in AUTHOR_SURFACES if path.name not in LOCALIZED_README_SEMANTICS
    )
    for path in english_surfaces:
        assert path.is_file(), f"brainstorming author surface is absent at {path}"
        low = _flatten(path.read_text(encoding="utf-8")).lower()

        assert "path" in low and "verbatim string" in low and "stable heading" in low, (
            f"{path.name} must require a path plus a verbatim-string or "
            "stable-heading anchor"
        )
        assert "line number" in low and "optional" in low and "ambiguous" in low, (
            f"{path.name} must make a line number optional precision only when "
            "the anchor is ambiguous"
        )

    for filename, (anchor_terms, precision_terms) in LOCALIZED_README_SEMANTICS.items():
        path = SKILL_DIR / filename
        assert path.is_file(), f"brainstorming author surface is absent at {path}"
        text = _flatten(path.read_text(encoding="utf-8"))
        assert all(term in text for term in anchor_terms), (
            f"{filename} must require a path plus a localized verbatim-string "
            "or stable-heading anchor"
        )
        assert all(term in text for term in precision_terms), (
            f"{filename} must make a line number optional precision only when "
            "the anchor is ambiguous"
        )

    stale = (
        "each citing file:line",
        "every bullet cites `file:line`",
        "grounded `file:line` citations",
        "same `file:line` citations often serve both",
        "每個 bullet 都附 `file:line` 引用",
        "各ブレットは `file:line` を引用",
    )
    combined = "\n".join(path.read_text(encoding="utf-8") for path in AUTHOR_SURFACES)
    for phrase in stale:
        assert phrase not in combined, f"stale line-primary wording remains: {phrase}"

    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    match = re.search(
        r"^## Output Contract — the brief.*?^## Current State Evidence\s*\n"
        r"(?P<body>.*?)(?=^## \S)",
        skill,
        re.MULTILINE | re.DOTALL,
    )
    assert match is not None, "Output Contract must retain its Current State Evidence entry"
    current_state_evidence = _flatten(match.group("body")).lower()

    assert "path plus an anchor" in current_state_evidence, (
        "the brief entry must require a path plus an anchor"
    )
    assert "line number is optional precision only when the anchor is ambiguous" in current_state_evidence, (
        "the brief entry must restrict line precision to ambiguous anchors"
    )
    assert "handoff-brief-format.md" in current_state_evidence and "artifact type" in current_state_evidence, (
        "the brief entry must point anchor selection by artifact type to the canonical format"
    )
    assert "file:line" not in current_state_evidence, (
        "the brief entry must not retain retired line-primary citation wording"
    )
