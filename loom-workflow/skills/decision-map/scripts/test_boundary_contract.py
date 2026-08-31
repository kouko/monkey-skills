"""Regression tests for the map↔backlog boundary contract (governance R6).

The three boundary rules — promotion close-and-cite, release-only
map→backlog travel, and reopen-promoted-entries-on-archive — are defined
at exactly ONE point (map-format.md) and cited, never copied, on the
skill side; the loom-code backlog charter keeps its own store-side copy,
and these tests pin both sides so the contract cannot silently vanish
again (it was deleted wholesale by the Outcome Map v3 rewrite).
"""

from pathlib import Path


def _flat(text: str) -> str:
    """Collapse all whitespace so line-wrapped prose still matches."""
    return " ".join(text.split())


SKILL_DIR = Path(__file__).resolve().parent.parent
MAP_FORMAT_MD = SKILL_DIR / "references" / "map-format.md"
SKILL_MD = SKILL_DIR / "SKILL.md"
REPO_ROOT = SKILL_DIR.parents[2]
BACKLOG_CHARTER_MD = (
    REPO_ROOT / "loom-code" / "scripts" / "templates" / "backlog-README.md"
)

BOUNDARY_SECTION = "## Backlog boundary contract"

# The three rules, as load-bearing phrases pinned on the map side (SSOT).
CLOSE_AND_CITE = (
    "Promotion is close-and-cite: close the backlog entry and write "
    "`origin: promoted to <ticket>` before creating the Ticket."
)
RELEASE_ONLY = "Map-to-backlog travel is release-only."
REOPEN_ON_ARCHIVE = (
    "On archive, reopen every backlog entry whose Ticket is still "
    "non-closed and whose frontmatter says `origin: promoted to "
    "<ticket>`; the map then remains a historical record, not a "
    "stranded-promotion target."
)

# The backlog charter's own store-side wording of the same contract.
CHARTER_CLOSE_AND_CITE = (
    "close the backlog entry and write `origin: promoted to <ticket>` "
    "before creating the ticket"
)
CHARTER_REOPEN = (
    "If a map is archived with unclosed tickets, reopen the entries "
    "promoted to those tickets."
)


def test_map_format_defines_all_three_boundary_rules():
    """map-format.md is the single definition point of the boundary rules."""
    text = _flat(MAP_FORMAT_MD.read_text(encoding="utf-8"))
    assert BOUNDARY_SECTION in text
    assert CLOSE_AND_CITE in text
    assert RELEASE_ONLY in text
    assert REOPEN_ON_ARCHIVE in text


def test_skill_cites_the_boundary_section_without_copying_it():
    """SKILL.md points at the section; it never restates the rules."""
    skill = _flat(SKILL_MD.read_text(encoding="utf-8"))
    map_format = _flat(MAP_FORMAT_MD.read_text(encoding="utf-8"))

    # The citation exists and names the section.
    assert BOUNDARY_SECTION in skill
    assert "references/map-format.md" in skill

    # None of the three rules' load-bearing wording appears on the skill
    # side — a copy here would be a second definition point that drifts.
    for rule in (CLOSE_AND_CITE, RELEASE_ONLY, REOPEN_ON_ARCHIVE):
        assert rule in map_format
        assert rule not in skill, f"SKILL.md restates a boundary rule: {rule}"


def test_backlog_charter_keeps_its_store_side_copy():
    """The loom-code backlog charter still carries the backlog-side copy.

    The two stores each own their side of the boundary; this pins that the
    charter copy survived and agrees with the map-side SSOT on the two
    mechanically checkable commitments: the `origin: promoted to <ticket>`
    close-and-cite step and the reopen-on-archive duty.
    """
    charter = _flat(BACKLOG_CHARTER_MD.read_text(encoding="utf-8"))
    map_format = _flat(MAP_FORMAT_MD.read_text(encoding="utf-8"))

    assert CHARTER_CLOSE_AND_CITE in charter
    assert CHARTER_REOPEN in charter

    # Consistency: both sides bind promotion to the same origin marker.
    assert "origin: promoted to <ticket>" in charter
    assert "origin: promoted to <ticket>" in map_format


def test_citation_checker_scans_loom_workflow():
    """The contract-citation gate covers the loom-workflow plugin tree."""
    import importlib.util

    checker_path = REPO_ROOT / "loom-code" / "scripts" / "check_contract_citations.py"
    spec = importlib.util.spec_from_file_location("ccc", checker_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert ("loom-workflow/skills", True) in module._SCOPE_DIRS