from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REVIEW = (ROOT / "loom-code/skills/review/SKILL.md").read_text(encoding="utf-8")
SHIP = (ROOT / "loom-code/skills/ship/SKILL.md").read_text(encoding="utf-8")
BUILD = (ROOT / "loom-code/skills/build/SKILL.md").read_text(encoding="utf-8")


def test_review_generates_attestation_without_ledger_ceremony() -> None:
    assert "finalize-review" in REVIEW
    assert "attestation.json" in REVIEW
    assert "agents never edit that file by hand" in REVIEW
    assert "validates that single\nattestation directly" in REVIEW
    assert "review.json" not in REVIEW


def test_ship_validates_without_replaying_functional_work() -> None:
    assert "does not repeat functional verification" in SHIP
    assert "does not execute package tests or adversarial probes" in SHIP
    assert "Publication-only edits" in SHIP
    assert "repository-local checker scaffold" in SHIP


def test_ship_keeps_publication_safety() -> None:
    assert "destination/refspec safety" in SHIP
    assert "deterministic secrets scan" in SHIP
    assert "cannot be bypassed" in SHIP


def test_ship_uses_one_publish_command_after_acceptance() -> None:
    assert "publish --confirm-authorized" in SHIP
    assert "one publication command" in SHIP
    assert "push --head HEAD --require-live-head" not in SHIP
    assert "canonical `git push` and PR commands" not in SHIP


def test_build_has_no_evidence_accounting() -> None:
    assert "no dispatch ledger is created" in BUILD
    assert "finalize-review" in BUILD
    assert "Build never writes `attestation.json`" in BUILD
    assert "review.json" not in BUILD
