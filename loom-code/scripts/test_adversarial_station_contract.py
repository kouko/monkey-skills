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
    assert "attack-class:" in agent_text, (
        "code-reviewer.md's finding field must be attack-class:, not the "
        "bare class: field docs-reviewer's class: instruction|evidence "
        "already owns"
    )
    assert "resources.attack_catalogue" in agent_text, (
        "code-reviewer.md must read the plugin catalogue via "
        "resources.attack_catalogue, not a derived plugin path"
    )

    class_names = _catalogue_class_names()
    for name in class_names:
        assert name in agent_text, (
            f"catalogue class {name!r} must appear verbatim in the "
            "agent's attack-class: vocabulary"
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
    assert "check_attack_catalogue.py signal" in skill_text, (
        "Step 3.5 must invoke the signal subcommand, not name a Python "
        "function"
    )
    assert "scripts/check_attack_catalogue.py" in skill_text, (
        "repo-root two-form path variant must be present"
    )
    assert '${CLAUDE_PLUGIN_ROOT}/scripts/check_attack_catalogue.py' in skill_text, (
        "plugin-root two-form path variant must be present"
    )
    assert "not-applicable" in skill_text

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


def _close_out_table_rows(skill_text: str) -> list[str]:
    return [
        line
        for line in skill_text.splitlines()
        if line.strip().startswith("|") and "---" not in line
    ]


def test_close_out_card_has_audit_and_cold_reader_rows():
    skill_text = FINISHING_SKILL.read_text(encoding="utf-8")
    rows = _close_out_table_rows(skill_text)

    audit_rows = [r for r in rows if "adversarial audit:" in r]
    assert audit_rows, "close-out table must carry an adversarial-audit row"
    assert any("fired —" in r for r in audit_rows), (
        "adversarial-audit row must show the fired — form"
    )
    assert any("N/A —" in r for r in audit_rows), (
        "adversarial-audit row must show the N/A — form"
    )
    assert any("header=" in r for r in audit_rows), (
        "adversarial-audit N/A form must carry the computed header= evidence"
    )
    assert any("guarded-hits=" in r for r in audit_rows), (
        "adversarial-audit N/A form must carry the computed guarded-hits= evidence"
    )
    assert any("check_attack_catalogue.py" in r for r in audit_rows), (
        "adversarial-audit row must name check_attack_catalogue.py "
        "among the close-out gate lines"
    )

    cold_rows = [r for r in rows if "cold reader:" in r]
    assert cold_rows, "close-out table must carry a cold-reader row"
    assert any("fired —" in r for r in cold_rows), (
        "cold-reader row must show the fired — form"
    )
    assert any("N/A —" in r for r in cold_rows), (
        "cold-reader row must show the N/A — form"
    )
    assert any("prose-hits=" in r for r in cold_rows), (
        "cold-reader N/A form must carry the computed prose-hits= evidence"
    )


def _step_3_5_slice(skill_text: str) -> str:
    start = skill_text.index("3.5. Adversarial-audit station")
    end = skill_text.index("5. Dispatch verification-before-completion", start)
    return skill_text[start:end]


def test_step_3_5_stop_sentences_are_inside_the_step():
    skill_text = FINISHING_SKILL.read_text(encoding="utf-8")
    slice_text = _step_3_5_slice(skill_text)
    flat = " ".join(slice_text.split())

    assert "STOP until a RED test" in flat
    assert "attack catalogue: absent" in flat
    assert "continue to Step 5" in flat
    assert "attack catalogue: base unresolved" in flat
    # the `no` + guarded-hit STOP sentence must live inside the step, not
    # merely somewhere in the file
    assert "does not override" in flat
    assert "STOP naming both" in flat
    assert "orchestrator-run" in flat

    # the ONLY computation is the `signal` command — no inline merge-base
    # shell, no Python function names.
    assert "check_attack_catalogue.py signal" in flat
    assert "scripts/check_attack_catalogue.py" in flat, (
        "repo-root two-form path variant must live inside the step"
    )
    assert '${CLAUDE_PLUGIN_ROOT}/scripts/check_attack_catalogue.py' in flat, (
        "plugin two-form path variant must live inside the step"
    )
    assert "git merge-base" not in flat, (
        "Step 3.5 must not compute the base via inline shell"
    )
    assert "safety_bearing(" not in flat, (
        "Step 3.5 must not name the Python function directly"
    )
    assert "guarded_path_globs" not in flat, (
        "Step 3.5 must not name the Python function directly"
    )

    # exit-2 / exit-3 handling words
    assert "STOP" in flat

    # the resumption clause: only the user resumes a `no` + guarded-hit
    # STOP, never the orchestrator alone — quoted exactly.
    assert (
        "only the user (flip the header, or narrow `## Guarded paths`) "
        "resumes it, never the orchestrator alone."
    ) in flat


PROSE_CONTRACT_GLOBS = [
    "**/SKILL.md",
    "**/agents/*.md",
    "**/hooks/*.md",
    "**/references/*-packet.md",
    "**/references/*-prompt.md",
    "rules/*.md",
]


def test_prose_signal_enumerates_all_six_globs():
    skill_text = FINISHING_SKILL.read_text(encoding="utf-8")
    slice_text = _step_3_5_slice(skill_text)
    flat = " ".join(slice_text.split())

    for glob in PROSE_CONTRACT_GLOBS:
        assert glob in flat, (
            f"Step 3.5's prose signal must enumerate {glob!r}, not just "
            "say 'a prose-shaped glob in the store'"
        )


def test_close_out_na_lines_carry_base_and_changed():
    skill_text = FINISHING_SKILL.read_text(encoding="utf-8")
    rows = _close_out_table_rows(skill_text)

    audit_rows = [r for r in rows if "adversarial audit:" in r and "N/A —" in r]
    assert audit_rows, "adversarial-audit N/A row must exist"
    assert any("base=" in r and "changed=" in r for r in audit_rows), (
        "adversarial-audit N/A line must carry base=<sha> so changed=<n> "
        "is recomputable"
    )

    cold_rows = [r for r in rows if "cold reader:" in r and "N/A —" in r]
    assert cold_rows, "cold-reader N/A row must exist"
    assert any("base=" in r and "changed=" in r for r in cold_rows), (
        "cold-reader N/A line must carry base=<sha> so changed=<n> is "
        "recomputable"
    )
