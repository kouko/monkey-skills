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


FINISHING_SKILL = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "finishing-a-development-branch"
    / "SKILL.md"
)
ADVERSARIAL_PACKET = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "finishing-a-development-branch"
    / "references"
    / "adversarial-audit-packet.md"
)
COLD_READER_PACKET = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "finishing-a-development-branch"
    / "references"
    / "cold-reader-packet.md"
)
CHECK_ATTACK_CATALOGUE = (
    REPO_ROOT / "loom-code" / "scripts" / "check_attack_catalogue.py"
)


def test_finishing_branch_step_3_5_dispatches_packets_that_exist():
    skill_text = FINISHING_SKILL.read_text(encoding="utf-8")

    assert "Step 3.5" in skill_text or "3.5." in skill_text, (
        "SKILL.md must add a Step 3.5"
    )

    for path in (ADVERSARIAL_PACKET, COLD_READER_PACKET):
        assert path.name in skill_text, f"SKILL.md must name {path.name}"
        assert path.exists(), f"{path} must exist on disk"

    assert "docs/loom/ATTACK-CATALOGUE.md" in skill_text, (
        "SKILL.md must name the target-repo catalogue store path"
    )
    assert "check_attack_catalogue.py" in skill_text
    assert "safety_bearing" in skill_text

    assert "STOP" in skill_text
    assert "attack catalogue: absent" in skill_text
    assert "orchestrator-run" in skill_text

    # `no` + guarded-hit STOP sentence: the header does not override the
    # path signal.
    assert "does not override" in skill_text or "does NOT override" in skill_text

    assert "| 3.5 |" in skill_text, (
        "Cross-skill contract table must carry a 3.5 row"
    )


def test_temptations_heading_match_between_packet_and_checker():
    cold_reader_text = COLD_READER_PACKET.read_text(encoding="utf-8")
    checker_text = CHECK_ATTACK_CATALOGUE.read_text(encoding="utf-8")

    assert cold_reader_text.count("## Prose temptations") >= 1
    assert checker_text.count("## Prose temptations") >= 1
