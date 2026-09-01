"""Tests for check-skill-structure.py: the CHK-SKL-011-exempt marker, and the
scope of CHK-SKL-012's rules.

WHY the CHK-SKL-011 tests exist: copywriting-toolkit legitimately cites its
`domain-teams/skills/copywriting-team/...` provenance source in prose (its
Tier-1 byte-identical policy, see copywriting-toolkit/CLAUDE.md §Provenance &
Divergence Principle). CHK-SKL-011 exists to catch REAL plugin-rooted path
drift (a path that breaks when the plugin moves), not to flag an intentional
citation. The `<!-- CHK-SKL-011-exempt: ... -->` marker lets a single line opt
out of CHK-SKL-011 only — this test proves (a) a marked line is exempted and
(b) an unmarked violation anywhere still fails, so the marker cannot be used
to silently widen the exemption beyond the one line it sits on.

WHY the CHK-SKL-012 tests exist: that rule enforced the domain-teams
four-subdirectory taxonomy against every plugin, although the standard it
implements scopes itself to domain-team skills. The suite below pins both
halves of the split — what is now relaxed outside domain-teams, and what stays
fatal inside it — plus the `main()` derivation that decides which side a
plugin is on. See the block comments above each group.

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


# ---------------------------------------------------------------------------
# CHK-SKL-012 scope: the four-subdirectory taxonomy is a domain-teams
# convention, not a repo-wide one.
#
# WHY these tests exist: `check_chk_skl_012` enforced
# `domain-teams/skills/skill-team/standards/file-conventions.md` against every
# plugin. That standard's own first line scopes it to "a domain-team skill",
# and its Primary Sources name repo CLAUDE.md §Skill Structure as the repo
# convention SSOT. CLAUDE.md states one structural rule: SKILL.md plus any
# number of single-level subdirectories, no subdirectory inside a
# subdirectory, and its subfolder list ends in 「等」 — illustrative, not an
# allowlist. Applying the narrower taxonomy everywhere produced 39 name
# findings across 9 of 24 plugins for directories like `glossary/`, `corpus/`
# and `tests/` — which buried the one genuine nesting violation in the repo.
#
# These tests pin both halves: the taxonomy still binds inside domain-teams,
# and the nesting rule still binds everywhere.
# ---------------------------------------------------------------------------


# `is_router_skill` treats a SKILL.md with no worker-launch template as a
# router and waives the required-four check on its own. A fixture using this
# body is therefore NOT a router, so a required-four assertion about it tests
# the team_taxonomy gate rather than the pre-existing router exemption.
_WORKER_TEMPLATE_SKILL_MD = "### Task\nfixture\n\n### Resource Paths\nfixture\n"

# Frontmatter with a description is what CHK-SKL-001 needs; without a
# worker-launch template the fixture is a router, so the description word
# floor does not apply. Tests that drive `main()` run every rule, not just
# CHK-SKL-012, so the default fixture has to be clean under all of them.
_ROUTER_SKILL_MD = "---\nname: t\ndescription: fixture skill\n---\n\nfixture\n"


def _skill(
    tmp_path: Path,
    name: str,
    subdirs: tuple[str, ...] = (),
    *,
    skill_md: str = _ROUTER_SKILL_MD,
) -> Path:
    skill_dir = tmp_path / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    for sub in subdirs:
        (skill_dir / sub).mkdir()
    return skill_dir


def _plugin(tmp_path: Path, plugin_name: str, skill_name: str = "t") -> Path:
    """A minimal plugin tree `main()` can be pointed at."""
    plugin_dir = tmp_path / plugin_name
    _skill(plugin_dir / "skills", skill_name, ("glossary",))
    (plugin_dir / "skills" / skill_name / "glossary" / "ja").mkdir()
    return plugin_dir


def _details(errors) -> list[str]:
    return [e.detail for e in errors]


def test_non_team_plugin_allows_any_subdirectory_name(tmp_path: Path) -> None:
    """Outside domain-teams a skill may name its subdirectories freely.

    Real instances this unblocks: translation-toolkit's glossary/, corpus/
    and typography/; four-dx-coach's worksheets/; every skill's tests/.
    """
    skill_dir = _skill(tmp_path, "translation-audit", ("glossary", "corpus", "typography"))

    assert check_skill_structure.check_chk_skl_012(skill_dir, team_taxonomy=False) == []


def test_non_team_plugin_still_rejects_nested_subdirectory(tmp_path: Path) -> None:
    """The one rule CLAUDE.md actually states stays enforced everywhere.

    Real instance this must keep catching: investing-toolkit's
    analysis-macro-regime/scripts/calibrations/.
    """
    skill_dir = _skill(tmp_path, "analysis-macro-regime", ("scripts",))
    (skill_dir / "scripts" / "calibrations").mkdir()

    errors = check_skill_structure.check_chk_skl_012(skill_dir, team_taxonomy=False)

    assert _details(errors) == ["nested subdirectory not allowed: scripts/calibrations"]


def test_non_team_plugin_rejects_nesting_under_an_off_taxonomy_name(tmp_path: Path) -> None:
    """Relaxing the name allowlist must not stop the nesting check running.

    Before this change a directory outside the allowlist was reported as
    'unexpected subdirectory' and never descended into, so a nested directory
    inside it was invisible. Freeing the name must not also free the nesting.
    """
    skill_dir = _skill(tmp_path, "translation-audit", ("glossary",))
    (skill_dir / "glossary" / "ja").mkdir()

    errors = check_skill_structure.check_chk_skl_012(skill_dir, team_taxonomy=False)

    assert _details(errors) == ["nested subdirectory not allowed: glossary/ja"]


def test_non_team_plugin_allows_extra_top_level_file(tmp_path: Path) -> None:
    """The top-level file allowlist is part of the same domain-teams standard.

    Real instances: tsundoku's book-distill/ATTRIBUTION.md, obsidian's
    obsidian-compatibility.md.
    """
    skill_dir = _skill(tmp_path, "book-distill")
    (skill_dir / "ATTRIBUTION.md").write_text("fixture\n", encoding="utf-8")

    assert check_skill_structure.check_chk_skl_012(skill_dir, team_taxonomy=False) == []


def test_non_team_plugin_does_not_require_the_four_subdirectories(tmp_path: Path) -> None:
    """A non-team skill with protocols/ is not thereby a domain-team skill.

    The router-skill heuristic (`no protocols/`) already waived this check for
    most non-team skills by accident. Scoping it makes that explicit rather
    than dependent on whether a plugin happens to use the word 'protocols'.
    """
    skill_dir = _skill(
        tmp_path, "translation-doc", ("protocols",), skill_md=_WORKER_TEMPLATE_SKILL_MD
    )
    # Guard the guard: if this fixture were a router, the assertion below would
    # pass without the team_taxonomy gate doing anything.
    assert check_skill_structure.is_router_skill(skill_dir) is False
    assert check_skill_structure.check_chk_skl_012(skill_dir, team_taxonomy=True) != []

    assert check_skill_structure.check_chk_skl_012(skill_dir, team_taxonomy=False) == []


def test_non_team_plugin_does_not_enforce_research_filenames(tmp_path: Path) -> None:
    """grounding-v{X.Y.Z}.md is the domain-teams grounding-audit convention.

    investing-toolkit files its grounding notes per region
    (grounding-tw-2026-05.md), which is a different scheme, not a broken one.
    """
    skill_dir = _skill(tmp_path, "analysis-macro-regime", ("research",))
    (skill_dir / "research" / "grounding-tw-2026-05.md").write_text("x\n", encoding="utf-8")

    assert check_skill_structure.check_chk_skl_012(skill_dir, team_taxonomy=False) == []


def test_team_taxonomy_still_binds_inside_domain_teams(tmp_path: Path) -> None:
    """Every rule relaxed above stays fatal where the standard applies."""
    skill_dir = _skill(tmp_path, "code-team", ("standards", "protocols", "checklists", "rubrics", "glossary"))
    (skill_dir / "ATTRIBUTION.md").write_text("fixture\n", encoding="utf-8")
    (skill_dir / "research").mkdir()
    (skill_dir / "research" / "notes.md").write_text("x\n", encoding="utf-8")

    details = _details(check_skill_structure.check_chk_skl_012(skill_dir, team_taxonomy=True))

    assert "unexpected subdirectory: glossary/" in details
    assert "unexpected top-level file: ATTRIBUTION.md" in details
    assert "research/ filename does not match grounding-v{X.Y.Z}.md: notes.md" in details


def test_team_taxonomy_defaults_on(tmp_path: Path) -> None:
    """Fail closed: an omitted argument must not silently relax the check."""
    skill_dir = _skill(tmp_path, "code-team", ("standards", "protocols", "checklists", "rubrics", "glossary"))

    assert check_skill_structure.check_chk_skl_012(skill_dir) == check_skill_structure.check_chk_skl_012(
        skill_dir, team_taxonomy=True
    )
    assert check_skill_structure.check_chk_skl_012(skill_dir) != []


def test_domain_teams_is_the_only_taxonomy_plugin() -> None:
    """Pin the scope set itself, so widening it is a deliberate edit."""
    assert check_skill_structure.TEAM_TAXONOMY_PLUGINS == {"domain-teams"}


def test_domain_teams_still_passes_end_to_end() -> None:
    """The plugin the taxonomy describes must not be loosened by this change."""
    repo_root = Path(__file__).resolve().parent.parent
    assert check_skill_structure.main([("check"), str(repo_root / "domain-teams")]) == 0


# ---------------------------------------------------------------------------
# The scoping decision itself.
#
# WHY these tests exist: every test above calls `check_chk_skl_012` directly,
# which leaves the one line that decides the flag —
# `team_taxonomy = plugin_dir.name in TEAM_TAXONOMY_PLUGINS` in `main` — and
# its threading through `run_all_checks` completely unexercised. A review pass
# showed three mutations surviving the suite: hardcoding that flag True (the
# repo-wide taxonomy this change removes), hardcoding it False (domain-teams
# silently stops being checked), and dropping the keyword in `run_all_checks`.
# Asserting `main(...) == 0` on an already-clean real plugin cannot tell
# "domain-teams passes" from "domain-teams is no longer examined", so these
# drive `main` over fixture plugins that DO carry a finding.
# ---------------------------------------------------------------------------


def test_main_relaxes_names_for_a_non_team_plugin(tmp_path: Path, capsys) -> None:
    plugin_dir = _plugin(tmp_path, "translation-toolkit")

    assert check_skill_structure.main(["check", str(plugin_dir)]) == 1
    out = capsys.readouterr().out
    assert "nested subdirectory not allowed: glossary/ja" in out
    assert "unexpected subdirectory" not in out


def test_main_enforces_the_taxonomy_for_domain_teams(tmp_path: Path, capsys) -> None:
    plugin_dir = _plugin(tmp_path, "domain-teams")

    assert check_skill_structure.main(["check", str(plugin_dir)]) == 1
    out = capsys.readouterr().out
    assert "unexpected subdirectory: glossary/" in out


def test_main_passes_a_clean_non_team_plugin(tmp_path: Path) -> None:
    """The relaxation must still be able to return 0 — otherwise the two tests
    above would pass under an implementation that simply always fails."""
    plugin_dir = tmp_path / "translation-toolkit"
    _skill(plugin_dir / "skills", "t", ("glossary", "corpus", "tests"))

    assert check_skill_structure.main(["check", str(plugin_dir)]) == 0


def test_domain_teams_off_taxonomy_directory_is_not_descended_into(tmp_path: Path) -> None:
    """Documents a deliberate asymmetry rather than asserting it is ideal.

    Inside domain-teams an off-taxonomy directory is reported once and skipped,
    so nesting under it stays invisible there until the name finding is fixed.
    Outside, where the name is legal, the nesting is reported. Pinning it means
    a future change to that `continue` has to be deliberate.
    """
    team = _skill(tmp_path / "team", "t", ("glossary",))
    (team / "glossary" / "ja").mkdir()
    other = _skill(tmp_path / "other", "t", ("glossary",))
    (other / "glossary" / "ja").mkdir()

    assert _details(check_skill_structure.check_chk_skl_012(team, team_taxonomy=True)) == [
        "unexpected subdirectory: glossary/"
    ]
    assert _details(check_skill_structure.check_chk_skl_012(other, team_taxonomy=False)) == [
        "nested subdirectory not allowed: glossary/ja"
    ]
