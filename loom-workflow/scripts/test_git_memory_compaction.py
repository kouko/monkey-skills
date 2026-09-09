from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL = REPO_ROOT / "loom-workflow/skills/git-memory/SKILL.md"
CONTRACT_BEHAVIORS = {
    "protocols/compose-commit.md": [
        "Privacy gate (fail-closed)",
        "conditional semantic judge",
        "Privacy-Bypass-Reason:",
    ],
    "protocols/compose-pr.md": [
        "Privacy gate (fail-closed)",
        "conditional semantic judge",
        "gh pr create",
    ],
    "protocols/recall.md": ["--history", "--path", "--match", "--top"],
    "standards/memory-conventions.md": [
        "Decision:",
        "Learning:",
        "Gotcha:",
        "Supersedes:",
    ],
}


def test_entrypoint_preserves_invocation_privacy_capture_and_recall():
    text = SKILL.read_text(encoding="utf-8")
    normalized_text = " ".join(text.split())

    essence = {
        "mandatory boundaries": [
            "Before `git commit` / `gh pr create` / `gh pr merge`",
            "invocation gate, not a trailer gate",
        ],
        "internal classification": [
            "routine commits exit cleanly with no trailers",
            "classification logic",
        ],
        "durable hierarchy": [
            "authoritative carrier",
            "best-effort, secondary",
        ],
        "privacy stop": [
            "two-layer privacy gate",
            "Layer 2 is conditional",
            "known public identifiers do not dispatch",
            "ambiguous private-party identifying text",
            "fail-closed",
            "BLOCKED",
        ],
        "commit capture verification": [
            "memory-grep.sh --verify <ref>",
            "the committed memory store remains authoritative",
        ],
        "Loom PR ownership": [
            "the caller owns the body schema and publication consent",
            "For Loom, contribute",
            "never add `## Memory`, a second footer contract, or another confirmation",
            "does not create a Loom lifecycle gate",
        ],
        "squash caveat": [
            "mid-body",
            "`%(trailers)` is unreliable",
            "`git log --grep`",
        ],
        "recall routing": [
            "protocols/recall.md",
            "pulled",
            "on demand",
        ],
    }
    for contract, needles in essence.items():
        missing = [needle for needle in needles if needle not in normalized_text]
        assert not missing, f"{contract} missing from entrypoint: {missing}"

    skill_root = SKILL.parent
    for relative, needles in CONTRACT_BEHAVIORS.items():
        contract_text = (skill_root / relative).read_text(encoding="utf-8")
        missing = [needle for needle in needles if needle not in contract_text]
        assert not missing, f"{relative} missing contract behavior: {missing}"


def test_contract_regression_checks_do_not_pin_whole_file_hashes():
    source = Path(__file__).read_text(encoding="utf-8")
    assert "UNCHANGED" + "_CONTRACTS" not in source
    assert "sha" + "256" not in source
