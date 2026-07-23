"""test_skill_structure.py — verify all v2.0.0 skills are present with required files.

Cross-cutting structural test (no network). Asserts that the v2.0.0 three-layer
architecture (Data / Analysis / Report) layout matches ADR-0001, as updated by
ADR-0009 (2026-07-11): the 5 per-country data-{us,jp,tw,kr,cn} skills were
consolidated into the single data-markets skill (one pack.py facade, shared
cache_util.py — see docs/adr/0009-data-markets-consolidation-and-cache-util.md).

  Layer 1 (Data, 1 skill):     data-markets
  Layer 2 (Analysis, 5-6):     analysis-dcf / analysis-screener /
                                analysis-technical / analysis-portfolio /
                                analysis-macro-regime
                                (analysis-comps lands in PR 2 — conditional)
  Layer 3 (Report, 4):         report-equity-memo / report-stock-snapshot /
                                report-portfolio-review / report-screener-list
  Router (1):                  using-investing-toolkit

PR 1 expected count: 11 skills (5 data skills merged into 1; no analysis-comps yet).

Each skill must:
  * Live under investing-toolkit/skills/<name>/
  * Contain SKILL.md with valid frontmatter (`name` + `description`)
  * Have a scripts/ subdir, EXCEPT:
      - using-investing-toolkit (pure router)
      - report-equity-memo (pure orchestrator — no script)

Spec compliance:
  * description ≤ 1024 chars (Anthropic skills-spec)
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"

# Post-ADR-0009: the 5 per-country data skills are merged into data-markets.
DATA_SKILLS = ["data-markets"]
ANALYSIS_SKILLS_PR1 = [
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
ROUTER_SKILLS = ["using-investing-toolkit"]

# Skills that legitimately do NOT have a scripts/ subdir.
SKILLS_WITHOUT_SCRIPTS = {"using-investing-toolkit", "report-equity-memo"}

# Optional skills (PR 2+). When present, must still satisfy structural rules.
OPTIONAL_SKILLS = ["analysis-comps", "analysis-xval", "analysis-kpi", "report-kpi-tearsheet"]


def _present(skill: str) -> bool:
    return (SKILLS_DIR / skill / "SKILL.md").is_file()


def _expected_skills() -> list[str]:
    """Return the list of expected v2.0.0 skills, including any optional skills
    that are already shipped (e.g. analysis-comps once PR 2 lands)."""
    base = DATA_SKILLS + ANALYSIS_SKILLS_PR1 + REPORT_SKILLS + ROUTER_SKILLS
    extras = [s for s in OPTIONAL_SKILLS if _present(s)]
    return base + extras


# --------------------------------------------------------------------------- #
# Skill inventory
# --------------------------------------------------------------------------- #


def test_skills_dir_exists():
    assert SKILLS_DIR.is_dir(), f"missing skills dir: {SKILLS_DIR}"


def test_skill_count_pr1_floor():
    """At minimum the 11 post-ADR-0009 PR-1 skills must be present
    (5 per-country data skills merged into 1 data-markets). analysis-comps
    pushed this to 12; analysis-xval (the US SEC financial-table cross-validation
    skill) to 13; analysis-kpi (the operational-KPI bitemporal store) to 14;
    report-kpi-tearsheet (the one-company KPI read surface) to 15 —
    each once its SKILL.md is present."""
    expected = _expected_skills()
    actual = sorted(p.name for p in SKILLS_DIR.iterdir() if p.is_dir())
    # All expected skills must exist
    missing = sorted(set(expected) - set(actual))
    assert not missing, f"missing skills: {missing}"
    # Total is 11 (PR 1), 12 (analysis-comps), 13 (analysis-xval),
    # 14 (analysis-kpi), 15 (report-kpi-tearsheet)
    assert len(expected) in (11, 12, 13, 14, 15), (
        f"unexpected expected-skill count: {len(expected)} (got {expected})"
    )


def test_no_unexpected_skills():
    """Surface any skill dirs we did not explicitly account for."""
    expected = set(_expected_skills())
    # OPTIONAL_SKILLS not yet present are still allowed in the future
    allowed_unknown = set(OPTIONAL_SKILLS) - expected
    actual = {p.name for p in SKILLS_DIR.iterdir() if p.is_dir()}
    extras = actual - expected - allowed_unknown
    assert not extras, (
        f"unexpected skill dirs (not in v2.0.0 inventory): {sorted(extras)}"
    )


# --------------------------------------------------------------------------- #
# Per-skill required files
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("skill", DATA_SKILLS + ANALYSIS_SKILLS_PR1 + REPORT_SKILLS + ROUTER_SKILLS)
def test_skill_md_present(skill):
    skill_md = SKILLS_DIR / skill / "SKILL.md"
    assert skill_md.is_file(), f"missing SKILL.md for {skill}: {skill_md}"


@pytest.mark.parametrize("skill", DATA_SKILLS + ANALYSIS_SKILLS_PR1 + REPORT_SKILLS + ROUTER_SKILLS)
def test_scripts_subdir_present_when_required(skill):
    if skill in SKILLS_WITHOUT_SCRIPTS:
        pytest.skip(f"{skill} legitimately has no scripts/ (orchestrator/router)")
    scripts_dir = SKILLS_DIR / skill / "scripts"
    assert scripts_dir.is_dir(), f"missing scripts/ subdir for {skill}: {scripts_dir}"
    # Must have at least one .py file
    py_files = list(scripts_dir.glob("*.py"))
    assert py_files, f"{skill}/scripts/ has no *.py files"


# --------------------------------------------------------------------------- #
# SKILL.md frontmatter
# --------------------------------------------------------------------------- #

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_frontmatter(skill_md: Path) -> dict:
    """Minimal YAML-ish frontmatter parser (handles the simple
    `name:` / `description:` / `description: >-` forms used by these skills)."""
    text = skill_md.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    assert m, f"no frontmatter in {skill_md}"
    body = m.group(1)
    # Use PyYAML if available — far more robust than ad-hoc parsing.
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        pytest.skip("pyyaml not installed (run via `uv run --with pytest --with pyyaml`)")
    parsed = yaml.safe_load(body)
    assert isinstance(parsed, dict), f"frontmatter in {skill_md} is not a mapping"
    return parsed


@pytest.mark.parametrize("skill", DATA_SKILLS + ANALYSIS_SKILLS_PR1 + REPORT_SKILLS + ROUTER_SKILLS)
def test_skill_frontmatter_required_keys(skill):
    fm = _parse_frontmatter(SKILLS_DIR / skill / "SKILL.md")
    assert "name" in fm, f"{skill}: frontmatter missing 'name'"
    assert "description" in fm, f"{skill}: frontmatter missing 'description'"
    assert fm["name"] == skill, (
        f"{skill}: frontmatter name mismatch — got {fm['name']!r}"
    )


@pytest.mark.parametrize("skill", DATA_SKILLS + ANALYSIS_SKILLS_PR1 + REPORT_SKILLS + ROUTER_SKILLS)
def test_skill_description_length_under_1024(skill):
    """Anthropic skills-spec: description ≤ 1024 chars."""
    fm = _parse_frontmatter(SKILLS_DIR / skill / "SKILL.md")
    desc = fm.get("description", "")
    assert isinstance(desc, str), f"{skill}: description must be a string"
    assert len(desc) <= 1024, (
        f"{skill}: description {len(desc)} chars exceeds skills-spec max 1024"
    )
    assert desc.strip(), f"{skill}: description is empty"
