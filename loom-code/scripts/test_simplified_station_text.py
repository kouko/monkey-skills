from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REVIEW = (ROOT / "loom-code/skills/review/SKILL.md").read_text(encoding="utf-8")
SHIP = (ROOT / "loom-code/skills/ship/SKILL.md").read_text(encoding="utf-8")
BUILD = (ROOT / "loom-code/skills/build/SKILL.md").read_text(encoding="utf-8")
CAPTURE = (ROOT / "loom-design/skills/capture-intent/SKILL.md").read_text(encoding="utf-8")
PLAN = (ROOT / "loom-code/skills/write-plan/SKILL.md").read_text(encoding="utf-8")
MEMORY_PR = (
    ROOT / "loom-workflow/skills/git-memory/protocols/compose-pr.md"
).read_text(encoding="utf-8")
SHIP_PROSE = " ".join(SHIP.split())
CAPTURE_PROSE = " ".join(CAPTURE.split())
PLAN_PROSE = " ".join(PLAN.split())


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


def test_ship_owns_one_self_contained_contextual_pr_body() -> None:
    for heading in (
        "## Context",
        "## Intended outcome",
        "## Scope",
        "## Decisions",
        "## Implementation",
        "## Behaviour change",
        "## Verification",
        "## Risks and rollback",
        "## Follow-ups",
    ):
        assert SHIP.count(heading) == 1
    for source in ("intent", "plan", "Git change", "attestation", "available CI evidence"):
        assert source in SHIP
    assert "one top-level PR body schema" in SHIP
    assert "review.json" not in SHIP
    assert "probe ledger" not in SHIP


def test_ship_requires_auditable_decisions_without_hidden_reasoning() -> None:
    for field in ("chosen option", "material alternatives", "trade-offs", "evidence", "outcome"):
        assert field in SHIP
    assert "private or hidden chain-of-thought" in SHIP
    assert "unsupported claims" in SHIP


def test_ship_uses_mermaid_only_when_relationships_carry_information() -> None:
    for relationship in (
        "meaningful decision branches",
        "component interactions",
        "state transitions",
        "before-and-after behaviour flows",
    ):
        assert relationship in SHIP_PROSE
    assert "Mermaid" in SHIP
    assert "Simple changes must omit Mermaid diagrams" in SHIP_PROSE


def test_git_memory_contributes_without_competing_top_level_schema() -> None:
    assert "Ship owns the top-level PR body schema" in MEMORY_PR
    assert "Decision, Learning, and Gotcha" in MEMORY_PR
    assert "does not own" in MEMORY_PR
    assert "Claude Code's standard" not in MEMORY_PR
    contextual = (
        "## Context", "## Intended outcome", "## Scope", "## Decisions",
        "## Implementation", "## Behaviour change", "## Verification",
        "## Risks and rollback", "## Follow-ups",
    )
    assert not all(any(line == heading for line in MEMORY_PR.splitlines())
                   for heading in contextual)
    assert "For a non-Loom caller" in MEMORY_PR


def test_ship_diagram_contract_has_mutually_exclusive_outcomes() -> None:
    assert "Graph-bearing changes require a Mermaid diagram" in SHIP_PROSE
    assert "Simple changes must omit Mermaid diagrams" in SHIP_PROSE
    assert "exactly one of those outcomes applies" in SHIP_PROSE


def test_current_surfaces_do_not_restore_legacy_publication_ledgers() -> None:
    for surface in (SHIP, MEMORY_PR):
        assert "review.json" not in surface
        assert "probe ledger" not in surface


def test_git_memory_defers_loom_consent_and_schema_to_ship() -> None:
    assert "git-memory never re-confirms a Loom publication" in MEMORY_PR
    assert "canonical intent authorization" in MEMORY_PR
    assert "single legacy Ship decision" in MEMORY_PR
    assert "loom-code:finishing-a-development-branch" not in MEMORY_PR
    assert "For a Loom change" in MEMORY_PR
    assert "follow Ship's conditional Mermaid rule" in MEMORY_PR


def test_intent_confirmation_discloses_publication_and_separate_merge() -> None:
    assert "non-forced push" in CAPTURE_PROSE
    assert "Ready PR" in CAPTURE_PROSE
    assert "merge remains a separate decision" in CAPTURE_PROSE
    assert "publication: automatic — authorized <date> by <name>" in CAPTURE


def test_station_summaries_distinguish_current_and_legacy_ship_ownership() -> None:
    expected = (
        "automatic for canonical intent authorization; one user decision for a "
        "legacy intent; merge is separate"
    )
    assert expected in CAPTURE_PROSE
    assert expected in PLAN_PROSE


def test_build_has_no_evidence_accounting() -> None:
    assert "no dispatch ledger is created" in BUILD
    assert "finalize-review" in BUILD
    assert "Build never writes `attestation.json`" in BUILD
    assert "review.json" not in BUILD
