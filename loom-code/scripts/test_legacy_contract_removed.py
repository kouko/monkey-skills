"""The 2.0 runtime has one publication contract: generated attestation."""

from pathlib import Path
import subprocess

import yaml


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "loom-code/scripts/loom_checker.py"
MANIFEST = ROOT / "loom-code/contract/manifest.yaml"


def test_manifest_declares_no_review_ledger() -> None:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    assert "review" not in manifest["artifacts"]
    assert not (ROOT / "loom-code/contract/templates/review.json").exists()


def test_public_rule_inventory_has_only_attestation_for_publication() -> None:
    result = subprocess.run(
        ["python3", str(CHECKER), "--list-rules"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    push_rules = {
        line.split("\t", 1)[0]
        for line in result.stdout.splitlines()
        if line.startswith("push.")
    }
    assert push_rules == {"push.attestation"}


def test_removed_package_replay_flag_is_rejected() -> None:
    result = subprocess.run(
        ["python3", str(CHECKER), "push", "--skip-package-tests"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 2
    assert "unexpected argument '--skip-package-tests'" in result.stderr


def test_live_consumers_require_contract_two() -> None:
    consumers = [
        ROOT / "loom-code/skills/write-plan/SKILL.md",
        *(ROOT / "loom-design/skills").glob("*/SKILL.md"),
    ]
    for path in consumers:
        text = path.read_text(encoding="utf-8")
        if "contract --require" in text:
            assert "contract --require 2.0" in text, path
            assert "contract --require 1.0" not in text, path
