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


def test_skill_distinguishes_entrypoint_and_package_round_scope() -> None:
    skill = " ".join((SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").split())

    for rule in (
        "Entrypoint mode: split a round",
        "Package mode: one isolated package round may change",
        "directly supporting bundled resources",
        "Unrelated bundled resources remain split",
    ):
        assert rule in skill


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
