"""test_path_conventions.py — verify SKILL.md path conventions (Phase 2 fix).

Phase 2 Wave 4 of the v2.0.0 refactor fixed cross-skill path drift:
  * Cross-skill executable refs (e.g. report-* → data-*/scripts/) must use
    `${CLAUDE_PLUGIN_ROOT}/skills/<other-skill>/scripts/...`
  * Self-references (within the same skill) must use
    `${CLAUDE_SKILL_DIR}/scripts/...`
  * No SKILL.md may use absolute filesystem paths (e.g. /Users/kouko/...).
  * No SKILL.md may use the `${CLAUDE_SKILL_DIR}/../` escape pattern that
    pre-Phase-2 drift produced.

This test file is the regression net for that fix. Failures here mean a
SKILL.md re-introduced one of the old anti-patterns.

Scope of "executable cross-skill ref":
  A line like `uv run ${CLAUDE_PLUGIN_ROOT}/skills/<X>/scripts/<Y>.py ...`
  inside a fenced bash block. We do NOT police plain prose mentions of
  "<other-skill>/scripts/<file>.py" — those are documentation, not commands,
  and editing them to add path vars would distort the prose.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"

# Post-ADR-0009: the 5 per-country data skills are merged into data-markets.
DATA_SKILLS = ["data-markets"]
ANALYSIS_SKILLS = [
    "analysis-dcf",
    "analysis-screener",
    "analysis-technical",
    "analysis-portfolio",
    "analysis-macro-regime",
]
REPORT_SKILLS = [
    "report-equity-memo",
    "report-stock-snapshot",
    "report-portfolio-review",
    "report-screener-list",
]
ALL_SKILLS = DATA_SKILLS + ANALYSIS_SKILLS + REPORT_SKILLS


def _skill_md(skill: str) -> Path:
    return SKILLS_DIR / skill / "SKILL.md"


# --------------------------------------------------------------------------- #
# Anti-pattern: absolute filesystem paths
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_no_absolute_user_paths(skill):
    """No SKILL.md may embed absolute filesystem paths like /Users/kouko/..."""
    text = _skill_md(skill).read_text(encoding="utf-8")
    bad_lines = [
        ln for ln in text.splitlines()
        if "/Users/" in ln or ln.strip().startswith("/home/")
    ]
    assert not bad_lines, (
        f"{skill}/SKILL.md contains absolute filesystem paths:\n"
        + "\n".join(bad_lines)
    )


# --------------------------------------------------------------------------- #
# Anti-pattern: ${CLAUDE_SKILL_DIR}/../ escape (Phase 2 drift)
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_no_skill_dir_parent_escape(skill):
    """Phase 2 fix: ${CLAUDE_SKILL_DIR}/../ was the v1 drift pattern. Nothing
    should hop out of the skill dir via parent traversal — cross-skill refs
    must use ${CLAUDE_PLUGIN_ROOT}/skills/<other>/ instead."""
    text = _skill_md(skill).read_text(encoding="utf-8")
    pattern = re.compile(r"\$\{CLAUDE_SKILL_DIR\}\s*/\s*\.\.")
    matches = pattern.findall(text)
    assert not matches, (
        f"{skill}/SKILL.md uses ${{CLAUDE_SKILL_DIR}}/../ — "
        f"Phase 2 forbade this. Use ${{CLAUDE_PLUGIN_ROOT}}/skills/<other>/ instead. "
        f"Matches: {matches}"
    )


# --------------------------------------------------------------------------- #
# Cross-skill executable refs in report-*/SKILL.md must use CLAUDE_PLUGIN_ROOT
# --------------------------------------------------------------------------- #

# Match any executable line that runs another skill's scripts/ via uv run /
# python / bash. We only flag lines that include `uv run` + a path with
# `skills/<other>/scripts/`.
EXEC_LINE_RE = re.compile(
    r"^\s*(?:uv\s+run|python3?|bash)\b.*?/skills/[\w-]+/scripts/",
    re.MULTILINE,
)


@pytest.mark.parametrize("skill", REPORT_SKILLS)
def test_report_cross_skill_refs_use_plugin_root(skill):
    """In report-*/SKILL.md, every executable cross-skill ref to another
    skill's scripts/ must be prefixed with ${CLAUDE_PLUGIN_ROOT}."""
    md = _skill_md(skill)
    if not md.is_file():
        pytest.skip(f"{skill}/SKILL.md not present")
    text = md.read_text(encoding="utf-8")
    bad: list[str] = []
    for m in EXEC_LINE_RE.finditer(text):
        line = m.group(0)
        # Allow ${CLAUDE_PLUGIN_ROOT}/skills/<other>/scripts/...
        if "${CLAUDE_PLUGIN_ROOT}/skills/" in line:
            continue
        # Allow self-refs that legitimately stay inside the skill (rare; a
        # report-* skill calling its own scripts is normally formatted via
        # ${CLAUDE_SKILL_DIR}/scripts/, not /skills/<self>/scripts/).
        bad.append(line.strip())
    assert not bad, (
        f"{skill}/SKILL.md has cross-skill exec lines NOT using "
        f"${{CLAUDE_PLUGIN_ROOT}}:\n  " + "\n  ".join(bad)
    )


# --------------------------------------------------------------------------- #
# Self-references in data-*/analysis-* must use ${CLAUDE_SKILL_DIR}
# --------------------------------------------------------------------------- #

# Match `uv run scripts/<file>.py` (bare-relative) or
# `uv run skills/<self>/scripts/<file>.py` (absolute via /skills/) inside an
# executable line. Both are anti-patterns for self-references — should be
# `${CLAUDE_SKILL_DIR}/scripts/<file>.py`.
SELF_BARE_RE = re.compile(
    r"^\s*(?:uv\s+run|python3?|bash)\b[^\n]*?(?<![/${\w])scripts/[\w-]+\.py",
    re.MULTILINE,
)


@pytest.mark.parametrize("skill", DATA_SKILLS + ANALYSIS_SKILLS)
def test_data_analysis_self_refs_no_cross_skill_drift(skill):
    """In data-*/SKILL.md and analysis-*/SKILL.md, any executable example that
    DOES use a path variable for self-refs must use ${CLAUDE_SKILL_DIR} (not
    ${CLAUDE_PLUGIN_ROOT}/skills/<self>/...).

    Bare relative `uv run scripts/foo.py` is permitted at this layer (the
    convention is "run from the skill directory"); the strict invariant that
    matters is no cross-skill drift via wrong path var.
    """
    md = _skill_md(skill)
    if not md.is_file():
        pytest.skip(f"{skill}/SKILL.md not present")
    text = md.read_text(encoding="utf-8")
    # Look for self-ref via PLUGIN_ROOT pointing at this same skill — this is
    # drift (should be SKILL_DIR for self).
    self_via_plugin_root = re.search(
        r"\$\{CLAUDE_PLUGIN_ROOT\}/skills/" + re.escape(skill) + r"/scripts/",
        text,
    )
    assert self_via_plugin_root is None, (
        f"{skill}/SKILL.md uses ${{CLAUDE_PLUGIN_ROOT}}/skills/{skill}/scripts/ "
        f"for a self-ref — should be ${{CLAUDE_SKILL_DIR}}/scripts/ instead. "
        f"Match: {self_via_plugin_root.group(0)!r}"
    )


# --------------------------------------------------------------------------- #
# Mixed-suffix sanity: a SKILL.md that uses ${CLAUDE_SKILL_DIR} in /skills/<X>
# pattern would imply an X != self self-ref (subtle drift) — flag it.
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_skill_dir_not_followed_by_skills_subpath(skill):
    """${CLAUDE_SKILL_DIR}/skills/... is nonsensical (CLAUDE_SKILL_DIR already
    points INTO the specific skill). This catches a copy-paste drift."""
    text = _skill_md(skill).read_text(encoding="utf-8")
    pattern = re.compile(r"\$\{CLAUDE_SKILL_DIR\}\s*/\s*skills/")
    matches = pattern.findall(text)
    assert not matches, (
        f"{skill}/SKILL.md uses ${{CLAUDE_SKILL_DIR}}/skills/... "
        f"(nonsensical — drift). Use ${{CLAUDE_PLUGIN_ROOT}}/skills/... instead."
    )
