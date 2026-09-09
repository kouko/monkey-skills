"""The 2.0 runtime has no legacy publication ledgers or replay gates."""

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


def test_public_rule_inventory_has_only_current_publication_contracts() -> None:
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
    assert push_rules == {"push.attestation", "push.contextual-body"}


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
        ROOT / "loom-workflow/skills/decision-map/SKILL.md",
    ]
    for path in consumers:
        text = path.read_text(encoding="utf-8")
        if "contract --require" in text:
            assert "contract --require 2.0" in text, path
            assert "contract --require 1.0" not in text, path


def test_implementer_runs_focused_tests_not_the_package_suite() -> None:
    text = (ROOT / "loom-code/agents/implementer.md").read_text(encoding="utf-8")
    assert "Closing Review owns the single package-level run" in text
    assert "plus the package test command passing" not in text
    assert "the package suite ran green" not in text
