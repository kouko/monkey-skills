from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REVIEW = (ROOT / "loom-code/skills/review/SKILL.md").read_text(encoding="utf-8")
SHIP = (ROOT / "loom-code/skills/ship/SKILL.md").read_text(encoding="utf-8")
BUILD = (ROOT / "loom-code/skills/build/SKILL.md").read_text(encoding="utf-8")
CAPTURE = (ROOT / "loom-design/skills/capture-intent/SKILL.md").read_text(encoding="utf-8")
PLAN = (ROOT / "loom-code/skills/write-plan/SKILL.md").read_text(encoding="utf-8")
CODEX_FIRST_CONTACT = (
    ROOT / "loom-code/skills/write-plan/references/codex-first-contact.md"
).read_text(encoding="utf-8")
PRINCIPLES = (ROOT / "PRINCIPLES.md").read_text(encoding="utf-8")
MEMORY_PR = (
    ROOT / "loom-workflow/skills/git-memory/protocols/compose-pr.md"
).read_text(encoding="utf-8")
SHIP_PROSE = " ".join(SHIP.split())
CAPTURE_PROSE = " ".join(CAPTURE.split())
PLAN_PROSE = " ".join(PLAN.split())
INTENT_TEMPLATE = (ROOT / "loom-code/contract/templates/intent.md").read_text(encoding="utf-8")
CONTRACT_MANIFEST = (ROOT / "loom-code/contract/manifest.yaml").read_text(encoding="utf-8")


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
    for station, prose in ((CAPTURE, CAPTURE_PROSE), (PLAN, PLAN_PROSE)):
        assert "automatic publication is the default" in prose
        assert "non-forced push" in prose
        assert "Ready PR" in prose
        assert "explicitly opt out" in prose
        assert "merge remains a separate decision" in prose
        assert "publication: automatic — authorized <date> by <name>" in station
        assert "only after that informed yes" in prose


def test_host_specific_skill_guidance_uses_each_native_contract() -> None:
    assert "`${CLAUDE_PLUGIN_ROOT}` is substituted by Claude Code" in PLAN
    assert "`PLUGIN_ROOT` is provided to Codex plugin hook commands" in PLAN
    assert "not a general skill-shell variable" in " ".join(PLAN.split())
    assert "hooks/hooks-codex.json" in CODEX_FIRST_CONTACT
    assert "`${PLUGIN_ROOT}`" in CODEX_FIRST_CONTACT
    assert "does not also load `hooks/hooks.json`" in CODEX_FIRST_CONTACT


def test_principles_name_installed_hooks_for_both_hosts() -> None:
    assert "Host-installed plugin hooks (Claude Code and Codex)" in PRINCIPLES
    assert "Codex `.codex/hooks.json`" not in PRINCIPLES


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


def test_capture_intent_boundaries_are_shared_with_code_only_intake() -> None:
    for phrase in (
        "ask only for missing required-field content",
        "observable delivery outcome",
        "complete scenarios",
        "Keep, neutralize, defer, reopen, or delete",
        "must remain `open`",
        "explicit answer",
        "decision points remain unchanged",
        "move it to Open questions",
        "before confirmation",
    ):
        assert phrase in CAPTURE_PROSE
        assert phrase in PLAN_PROSE

    assert "question quota" in CAPTURE_PROSE
    assert "question quota" in PLAN_PROSE


def test_shared_intent_contract_names_altitude_without_new_schema() -> None:
    assert "observable delivery outcomes, not scenarios or implementation" in INTENT_TEMPLATE
    assert "unsupported product decisions" in CONTRACT_MANIFEST
    assert "why this change exists, the value when needed" in CONTRACT_MANIFEST
    assert "source-id" not in CONTRACT_MANIFEST
    assert "question-id" not in CONTRACT_MANIFEST
