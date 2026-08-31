"""Contract tests for the adversarial-audit-station plan
(docs/loom/plans/2026-08-31-adversarial-audit-station.md).

This file starts with Task 12's test
(`test_code_reviewer_reads_attack_catalogue_and_tags_class`). Tasks 10
and 11 will add their own tests here later — do not assume this file's
scope is limited to Task 12.

Stdlib only (pathlib). Paths resolved relative to this test file so the
suite is location-independent inside the repo.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENT = REPO_ROOT / "loom-code" / "agents" / "code-reviewer.md"
CATALOGUE = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "requesting-code-review"
    / "references"
    / "attack-catalogue.md"
)


def _catalogue_class_names() -> list[str]:
    text = CATALOGUE.read_text(encoding="utf-8")
    names = []
    for line in text.splitlines():
        if line.startswith("### Class:"):
            names.append(line[len("### Class:") :].strip())
    assert names, f"no '### Class:' headings found in {CATALOGUE}"
    return names


def test_code_reviewer_reads_attack_catalogue_and_tags_class():
    agent_text = AGENT.read_text(encoding="utf-8")

    assert "attack-catalogue.md" in agent_text, (
        "code-reviewer.md must cite the plugin attack catalogue "
        "(references/attack-catalogue.md)"
    )
    assert "docs/loom/ATTACK-CATALOGUE.md" in agent_text, (
        "code-reviewer.md must cite the target-repo store path "
        "docs/loom/ATTACK-CATALOGUE.md"
    )

    class_names = _catalogue_class_names()
    for name in class_names:
        assert name in agent_text, (
            f"catalogue class {name!r} must appear verbatim in the "
            "agent's class: vocabulary"
        )
