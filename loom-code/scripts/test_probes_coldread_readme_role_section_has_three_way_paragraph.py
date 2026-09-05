"""W2-02 acceptance probe (arm B): the measured-but-noisy outcome is
written up as prose, not as a contract wording change.

`docs/loom/README.md`'s role-trigger section (`## checkpoint 的三個驗證角色
什麼時候被觸發`) must contain one blank-line-delimited paragraph that
names all three roles (reviewer/adversary/implementer, in Chinese or
English) and the phrase "three-way"/「三方」 — the paragraph the arm-B
task adds explaining who takes what is not theirs.

The intent file for this change must carry a `## Measurement record`
section (added, not replacing any existing section) with at least four
lines each containing a `/80` figure — one per baseline distribution
recomputed in `evidence/baselines.md`.

Fails today: the README section has no such paragraph, and the intent
has no `## Measurement record` heading.
"""
from __future__ import annotations

import re
from pathlib import Path


def _find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "docs" / "loom").is_dir():
            return candidate
    raise RuntimeError(f"could not locate repo root (docs/loom) above {start}")


REPO_ROOT = _find_repo_root(Path(__file__).parent)
CID = "2026-09-04-adversary-three-way-attribution-measured"
README = REPO_ROOT / "docs" / "loom" / "README.md"
INTENT = REPO_ROOT / "docs" / "loom" / "intent" / f"{CID}.md"

SECTION_HEADING = "## checkpoint 的三個驗證角色什麼時候被觸發"
NEXT_HEADING_PREFIX = "## Where a new change starts"

ROLE_MARKERS = [
    ["讀者", "reviewer"],
    ["對抗者", "adversary"],
    ["實作者", "implementer"],
]
THREE_WAY_MARKERS = ["三方", "three-way"]


def _section_body(text: str, heading: str, next_heading: str) -> str:
    start = text.index(heading)
    end = text.index(next_heading, start)
    return text[start + len(heading):end]


def _paragraphs(body: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]


def test_readme_role_section_has_three_way_paragraph() -> None:
    readme_text = README.read_text(encoding="utf-8")
    body = _section_body(readme_text, SECTION_HEADING, NEXT_HEADING_PREFIX)
    paragraphs = _paragraphs(body)

    matching = [
        p
        for p in paragraphs
        if any(marker in p for marker in THREE_WAY_MARKERS)
        and all(any(name in p for name in names) for names in ROLE_MARKERS)
    ]
    assert matching, (
        "expected one paragraph in the role-trigger section naming all "
        "three roles and containing 三方/three-way; found none in: "
        f"{paragraphs!r}"
    )

    intent_text = INTENT.read_text(encoding="utf-8")
    assert "## Measurement record" in intent_text, (
        "intent is missing the `## Measurement record` section"
    )
    record_body = intent_text[
        intent_text.index("## Measurement record") + len("## Measurement record"):
    ]
    numeric_lines = [
        line for line in record_body.splitlines() if "/80" in line
    ]
    assert len(numeric_lines) >= 4, (
        f"expected at least 4 lines with a /80 figure in the Measurement "
        f"record section, found {len(numeric_lines)}: {numeric_lines!r}"
    )
