"""Tests for the skill cross-reference dead-link validator.

The validator (`check-skill-crossrefs.py`) walks every loom-code
`skills/*/SKILL.md`, extracts each RELATIVE markdown link `](path)`,
resolves it against that SKILL.md's directory, and reports any link
whose target is missing on disk. Relative-only: http(s) URLs,
anchor-only `#...` links, and absolute paths are skipped. A trailing
`#anchor` on an otherwise-relative link is stripped before the check.

These tests drive `find_broken_crossrefs(skills_dir) -> list[str]`
directly against HERMETIC temp fixtures (no dependency on the real
tree's current state). Test A = a broken sibling link is reported;
Test B = an existing target passes clean.

Stdlib only (pathlib + tmp_path fixture). The module is loaded by file
path because its filename uses a hyphen (not importable by name).
"""

import importlib.util
from pathlib import Path

_MODULE_PATH = Path(__file__).parent / "check-skill-crossrefs.py"


def _load_checker():
    spec = importlib.util.spec_from_file_location(
        "check_skill_crossrefs", _MODULE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _make_skill(skills_dir: Path, name: str, body: str) -> Path:
    skill_dir = skills_dir / name
    skill_dir.mkdir(parents=True)
    md = skill_dir / "SKILL.md"
    md.write_text(body, encoding="utf-8")
    return md


# --- Test A: a relative link to a MISSING sibling is reported broken ---------

def test_broken_relative_link_is_reported(tmp_path):
    skills = tmp_path / "skills"
    _make_skill(
        skills,
        "alpha",
        "See [the spec](references/missing-spec.md) for details.\n",
    )

    checker = _load_checker()
    broken = checker.find_broken_crossrefs(skills)

    assert len(broken) == 1, f"expected one broken link, got: {broken!r}"
    entry = broken[0]
    assert "references/missing-spec.md" in entry, \
        "the broken-link report must name the unresolved target"
    assert "alpha" in entry, \
        "the report must name the SKILL.md the broken link came from"


# --- Test B: a relative link to an EXISTING target passes clean -------------

def test_existing_relative_link_passes(tmp_path):
    skills = tmp_path / "skills"
    md = _make_skill(
        skills,
        "beta",
        "See [the protocol](protocols/review.md) for the gate.\n",
    )
    target = md.parent / "protocols" / "review.md"
    target.parent.mkdir(parents=True)
    target.write_text("# Review protocol\n", encoding="utf-8")

    checker = _load_checker()
    broken = checker.find_broken_crossrefs(skills)

    assert broken == [], f"expected no broken links, got: {broken!r}"


# --- Guard: non-relative links (http, anchor-only) are skipped --------------

def test_non_relative_links_are_skipped(tmp_path):
    skills = tmp_path / "skills"
    _make_skill(
        skills,
        "gamma",
        "External [site](https://example.com/page.md), "
        "absolute [root](/etc/passwd), "
        "and anchor [here](#section) — none should be checked.\n",
    )

    checker = _load_checker()
    broken = checker.find_broken_crossrefs(skills)

    assert broken == [], \
        f"http/absolute/anchor links must be skipped, got: {broken!r}"


# --- Guard: a trailing #anchor is stripped before the existence check -------

def test_anchor_suffix_is_stripped_before_existence_check(tmp_path):
    skills = tmp_path / "skills"
    md = _make_skill(
        skills,
        "delta",
        "Jump to [the section](references/guide.md#step-2).\n",
    )
    target = md.parent / "references" / "guide.md"
    target.parent.mkdir(parents=True)
    target.write_text("# Guide\n", encoding="utf-8")

    checker = _load_checker()
    broken = checker.find_broken_crossrefs(skills)

    assert broken == [], \
        f"the #anchor suffix must be stripped before checking, got: {broken!r}"
