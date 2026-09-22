"""Ownership guard for obsidian-markdown's visualization decision guide.

The guide owns ONE question: which presentation form (diagram / table /
callout / list / prose). Mermaid type choice belongs to the
obsidian-mermaid-visualizer skill, delegation rules to SKILL.md §Diagrams,
callout types to SKILL.md §Callouts. Restating those rules in the guide is
how it drifted into contradicting them (2026-09-22), so these tests fail the
build if the guide grows them back.
"""

import re
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent / "skills/obsidian-markdown"
GUIDE = SKILL_DIR / "references/viz-decision-guide.md"
SKILL_MD = SKILL_DIR / "SKILL.md"

MERMAID_TYPE_KEYWORDS = [
    "flowchart", "graph TD", "graph LR", "sequenceDiagram", "stateDiagram",
    "erDiagram", "classDiagram", "C4Context", "gitGraph", "gantt", "timeline",
    "mindmap", "xychart", "pie", "quadrant", "quadrantChart", "quadrant-chart",
    "architecture-beta", "block-beta",
]


def _headings(markdown: str) -> set[str]:
    return {m.group(1).strip() for m in re.finditer(r"^#{1,6} (.+)$", markdown, re.M)}


def test_guide_names_no_mermaid_diagram_type():
    text = GUIDE.read_text(encoding="utf-8").lower()
    found = [k for k in MERMAID_TYPE_KEYWORDS if re.search(rf"\b{re.escape(k.lower())}\b", text)]
    assert not found, f"guide restates Mermaid type choice (owned by the visualizer skill): {found}"


def test_skill_md_points_to_guide_exactly_once():
    count = SKILL_MD.read_text(encoding="utf-8").count("viz-decision-guide.md")
    assert count == 1, f"SKILL.md must have a single entry point to the guide, found {count}"


def test_guide_links_resolve():
    text = GUIDE.read_text(encoding="utf-8")
    skill_headings = _headings(SKILL_MD.read_text(encoding="utf-8"))
    links = re.findall(r"\]\(([^)]+)\)", text)
    assert links, "guide should hand off to its owners via links"
    for link in links:
        path, _, anchor = link.partition("#")
        target = (GUIDE.parent / path).resolve()
        assert target.is_file(), f"broken link target: {link}"
        if anchor and target == SKILL_MD.resolve():
            slugs = {re.sub(r"[^a-z0-9 -]", "", h.lower()).replace(" ", "-") for h in skill_headings}
            assert anchor in slugs, f"anchor #{anchor} not a SKILL.md heading"
