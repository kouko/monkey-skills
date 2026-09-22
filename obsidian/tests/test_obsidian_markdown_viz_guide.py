"""Ownership guard for obsidian-markdown's visualization decision guide.

The guide owns ONE question: which presentation form (diagram / table /
callout / list / prose). Mermaid type choice belongs to the
obsidian-mermaid-visualizer skill, delegation rules to SKILL.md §Diagrams,
callout types to SKILL.md §Callouts. Restating those rules in the guide is
how it drifted into contradicting them (2026-09-22).

What these tests check (and only this): the guide names no Mermaid diagram
keyword, SKILL.md links to the guide exactly once, and every link in the
guide resolves (file and SKILL.md heading anchor). Prose restatements such as
"sequence diagram" or "more than 6 nodes" are NOT caught — review for those.
"""

import re
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent / "skills/obsidian-markdown"
GUIDE = SKILL_DIR / "references/viz-decision-guide.md"
SKILL_MD = SKILL_DIR / "SKILL.md"

# Regex patterns (matched case-insensitively on word boundaries).
MERMAID_TYPE_PATTERNS = [
    r"flowchart", r"graph (td|tb|bt|lr|rl)", r"sequencediagram", r"statediagram",
    r"erdiagram", r"classdiagram", r"c4\w+", r"gitgraph", r"gantt", r"timeline",
    r"mindmap", r"xychart", r"pie", r"quadrant", r"quadrantchart", r"quadrant-chart",
    r"architecture-beta", r"block-beta",
]

FENCE = re.compile(r"^(`{3,}|~{3,}).*?^\1[ \t]*$", re.M | re.S)


def _headings(markdown: str) -> set[str]:
    """Headings outside fenced code blocks."""
    body = FENCE.sub("", markdown)
    return {m.group(1).strip() for m in re.finditer(r"^#{1,6} (.+)$", body, re.M)}


def _slug(heading: str) -> str:
    return re.sub(r"[^a-z0-9 -]", "", heading.lower()).replace(" ", "-")


def test_guide_names_no_mermaid_diagram_type():
    text = GUIDE.read_text(encoding="utf-8")
    found = [p for p in MERMAID_TYPE_PATTERNS if re.search(rf"\b{p}\b", text, re.I)]
    assert not found, f"guide restates Mermaid type choice (owned by the visualizer skill): {found}"


def test_skill_md_points_to_guide_exactly_once():
    text = SKILL_MD.read_text(encoding="utf-8")
    count = len(re.findall(r"viz-decision-guide(\.md)?\b", text))
    assert count == 1, f"SKILL.md must have a single entry point to the guide, found {count}"


def test_guide_links_resolve():
    text = GUIDE.read_text(encoding="utf-8")
    links = re.findall(r"\]\(([^)]+)\)", text)
    assert links, "guide should hand off to its owners via links"
    for link in links:
        link = link.strip().split(" ", 1)[0]  # drop an optional "title"
        if re.match(r"^[a-z][a-z0-9+.-]*:", link, re.I):
            continue  # external URL: not a repo file
        path, _, anchor = link.partition("#")
        target = (GUIDE.parent / path).resolve() if path else GUIDE.resolve()
        assert target.is_file(), f"broken link target: {link}"
        if anchor:
            slugs = {_slug(h) for h in _headings(target.read_text(encoding="utf-8"))}
            assert anchor in slugs, f"anchor #{anchor} not a heading in {target.name}"
