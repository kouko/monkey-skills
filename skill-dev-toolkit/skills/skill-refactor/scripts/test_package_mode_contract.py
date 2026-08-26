import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[4]
SKILL_DIR = ROOT / "skill-dev-toolkit" / "skills" / "skill-refactor"
SCRIPT = SKILL_DIR / "scripts" / "package_gate.py"


def test_package_mode_is_conditional_and_keeps_entrypoint_threshold() -> None:
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    assert "bundled resource" in skill.lower()
    assert "only when" in skill.lower()
    assert "package-resource-mode.md" in skill
    assert "≥10%" in skill
    assert "isolated candidate" in skill.lower()
    assert "discard" in skill.lower()


def test_verdict_contract_requires_both_behavior_gates_and_never_reverts() -> None:
    skill = " ".join((SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").split())
    protocol = " ".join(
        (SKILL_DIR / "references" / "package-resource-mode.md")
        .read_text(encoding="utf-8")
        .split()
    )

    assert "Q1 and Q3 pass, Q2 marginal" in skill
    assert "Or revert" not in skill
    assert "overall `PROCEED` verdict" in protocol


def test_package_mode_fails_closed_until_its_protocol_is_loaded() -> None:
    skill = " ".join((SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").split())

    for rule in (
        "PACKAGE-MODE LOAD GATE",
        "before explaining, planning, or capturing a baseline",
        "read `references/package-resource-mode.md` whole",
        "STOP with `UNGRADABLE`",
        "Do not reconstruct package mode from this entrypoint",
    ):
        assert rule in skill


def test_package_resource_protocol_names_all_gate_capabilities() -> None:
    protocol = (SKILL_DIR / "references" / "package-resource-mode.md").read_text(
        encoding="utf-8"
    )

    for capability in (
        "export",
        "verify",
        "account",
        "reduce",
        "PASS",
        "FAIL",
        "UNGRADABLE",
        "isolated candidate",
    ):
        assert capability in protocol


def test_package_protocol_resolves_its_bundled_cli_without_repo_runtime() -> None:
    protocol = " ".join(
        (SKILL_DIR / "references" / "package-resource-mode.md")
        .read_text(encoding="utf-8")
        .split()
    )

    for rule in (
        "relative to the loaded `skill-refactor` skill directory",
        "absolute `<package-gate>` path",
        'python3 "<package-gate>" export',
        'python3 "<package-gate>" verify',
        'python3 "<package-gate>" account',
        'python3 "<package-gate>" reduce',
        "Never derive this path from the target repository or current working directory",
        "no Claude-only environment variable or runtime dependency",
    ):
        assert rule in protocol


def test_package_protocol_defines_whole_package_q2_and_combines_verdicts() -> None:
    protocol = (SKILL_DIR / "references" / "package-resource-mode.md").read_text(
        encoding="utf-8"
    )

    for rule in (
        "whole-package words",
        "≥10%",
        "PROCEED",
        "5–10%",
        "RESHAPE",
        "user decides",
        "<5%",
        "increase",
        "REJECT",
        "Bytes are report-only",
        "layered behavioral evidence",
        "Q2 and the reducer verdict",
    ):
        assert rule in protocol


def test_package_protocol_keeps_git_provenance_available_for_verification() -> None:
    protocol = " ".join(
        (SKILL_DIR / "references" / "package-resource-mode.md")
        .read_text(encoding="utf-8")
        .split()
    )

    assert "original Git repository and pinned commit" in protocol
    assert "external manifest digest" in protocol
    assert "Never recompute" in protocol
    assert "canonical manifest path" in protocol
    assert "verified snapshot" in protocol
    assert protocol.count("--manifest-sha256") >= 2


def test_skill_distinguishes_entrypoint_and_package_round_scope() -> None:
    skill = " ".join((SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").split())

    for rule in (
        "Entrypoint mode: split a round",
        "Package mode: one isolated package round may change",
        "directly supporting bundled resources",
        "Unrelated bundled resources remain split",
    ):
        assert rule in skill


def test_q3_bundled_contents_row_preserves_mode_specific_cascade_scope() -> None:
    row = next(
        line
        for line in (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").splitlines()
        if "Bundled file *contents*" in line
    )

    for rule in (
        "Entrypoint mode: each cascade is its own round",
        "Package mode follows §Round scope",
        "isolated package round",
        "target + directly supporting bundled resources",
        "unrelated resources split",
    ):
        assert rule in row


def test_package_gate_cli_reduces_json_evidence() -> None:
    evidence = {
        "accounting": {"verdict": "PASS"},
        "resource": [{"verdict": "PASS"}],
        "owning-skill": [{"verdict": "PASS"}],
        "package": [{"verdict": "PASS"}],
        "host_evidence": [],
    }

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "reduce"],
        input=json.dumps(evidence),
        capture_output=True,
        text=True,
        check=True,
    )

    assert json.loads(result.stdout)["verdict"] == "PASS"


def test_agents_declares_the_tested_package_gate_cli() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "skill-refactor/scripts/package_gate.py" in agents
    assert "{export|verify|account|reduce}" in agents
