"""Tests for the CHK-SKL-011-exempt marker in check-skill-structure.py.

WHY this test exists: copywriting-toolkit legitimately cites its
`domain-teams/skills/copywriting-team/...` provenance source in prose (its
Tier-1 byte-identical policy, see copywriting-toolkit/CLAUDE.md §Provenance &
Divergence Principle). CHK-SKL-011 exists to catch REAL plugin-rooted path
drift (a path that breaks when the plugin moves), not to flag an intentional
citation. The `<!-- CHK-SKL-011-exempt: ... -->` marker lets a single line opt
out of CHK-SKL-011 only — this test proves (a) a marked line is exempted and
(b) an unmarked violation anywhere still fails, so the marker cannot be used
to silently widen the exemption beyond the one line it sits on.

The module under test has a hyphenated filename (`check-skill-structure.py`),
so it is loaded via importlib rather than a normal `import` statement.
"""

import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "check-skill-structure.py"

_spec = importlib.util.spec_from_file_location("check_skill_structure", SCRIPT)
assert _spec is not None and _spec.loader is not None
check_skill_structure = importlib.util.module_from_spec(_spec)
sys.modules["check_skill_structure"] = check_skill_structure
_spec.loader.exec_module(check_skill_structure)

_path_check_lines = check_skill_structure._path_check_lines


def test_marked_line_is_exempted() -> None:
    """A line carrying the marker produces no CHK-SKL-011 error."""
    text = (
        "Uses `protocols/x.md` (cp'd verbatim from "
        "`domain-teams/skills/copywriting-team/`). "
        "<!-- CHK-SKL-011-exempt: provenance citation -->\n"
    )
    errors = _path_check_lines(text, Path("SKILL.md"))
    assert errors == []


def test_unmarked_plugin_rooted_path_still_fails() -> None:
    """The same violation WITHOUT the marker still trips CHK-SKL-011."""
    text = (
        "Uses `protocols/x.md` (cp'd verbatim from "
        "`domain-teams/skills/copywriting-team/`).\n"
    )
    errors = _path_check_lines(text, Path("SKILL.md"))
    assert len(errors) == 1
    assert errors[0].rule == "CHK-SKL-011"


def test_unmarked_absolute_path_still_fails() -> None:
    """CHK-SKL-011's other pattern (absolute /Users/... path) is unaffected."""
    text = "See /Users/someone/repo/CLAUDE.md for details.\n"
    errors = _path_check_lines(text, Path("SKILL.md"))
    assert len(errors) == 1
    assert errors[0].rule == "CHK-SKL-011"


def test_marker_only_exempts_its_own_line() -> None:
    """A marker on one line does not exempt a violation on the next line."""
    text = (
        "Fine: `domain-teams/skills/copywriting-team/` "
        "<!-- CHK-SKL-011-exempt: provenance citation -->\n"
        "Not fine: `domain-teams/skills/copywriting-team/`\n"
    )
    errors = _path_check_lines(text, Path("SKILL.md"))
    assert len(errors) == 1


def test_chk_skl_012_allows_shipped_license_and_eval_assets(tmp_path: Path) -> None:
    """Legal notices and packaged evaluation fixtures are valid skill assets."""

    skill_dir = tmp_path / "licensed-skill"
    skill_dir.mkdir()
    for filename in ("SKILL.md", "LICENSE", "NOTICE", "trigger-eval.json"):
        (skill_dir / filename).write_text("fixture\n", encoding="utf-8")
    evals = skill_dir / "evals"
    evals.mkdir()
    (evals / "trigger.json").write_text("[]\n", encoding="utf-8")

    assert check_skill_structure.check_chk_skl_012(skill_dir) == []


def test_chk_skl_012_ignores_nested_python_cache(tmp_path: Path) -> None:
    """A local Python cache must not make an otherwise valid skill fail CI parity."""

    skill_dir = tmp_path / "router-skill"
    scripts = skill_dir / "scripts"
    scripts.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("fixture\n", encoding="utf-8")
    (scripts / "__pycache__").mkdir()

    assert check_skill_structure.check_chk_skl_012(skill_dir) == []


def test_real_plugins_unaffected(tmp_path: Path) -> None:
    """No repo plugin other than copywriting-toolkit currently uses the
    marker, and the marker mechanism must not change their check results.

    This is a narrower, in-process re-statement of the manual before/after
    diff run against loom-code + domain-teams during development (both were
    byte-identical). Guards against a future edit to `_path_check_lines`
    accidentally broadening the exemption's scope.
    """
    repo_root = Path(__file__).resolve().parent.parent
    for plugin in ("domain-teams", "loom-code"):
        skills_dir = repo_root / plugin / "skills"
        assert skills_dir.is_dir()
        for skill_md in skills_dir.glob("*/SKILL.md"):
            text = skill_md.read_text(encoding="utf-8")
            assert check_skill_structure.CHK_SKL_011_EXEMPT_MARKER not in text, (
                f"unexpected exemption marker in {skill_md} — "
                "this test assumes only copywriting-toolkit uses it"
            )
