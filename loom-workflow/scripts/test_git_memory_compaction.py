from hashlib import sha256
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL = REPO_ROOT / "loom-workflow/skills/git-memory/SKILL.md"
UNCHANGED_CONTRACTS = {
    "protocols/compose-commit.md": "eba707ef71a7d019f3aca4029a5ceb72db885ebeb3bfe0bfd2663fbc01d2786f",
    "protocols/compose-pr.md": "1dd7cc63dacbcb61dabe876263ef957b29ce546438dfe28622e5a6a2930d2ab6",
    "protocols/recall.md": "47844bd6ac0084495ef5ee342b1562d3b3de620ad240767711e34303286209b6",
    "standards/memory-conventions.md": "585ca6c1205d12311f90f836ad08a2fa08253f765a8f2fe4d754fe98630d96c2",
}


def test_entrypoint_preserves_invocation_privacy_capture_and_recall():
    text = SKILL.read_text(encoding="utf-8")

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
            "fail-closed",
            "BLOCKED",
        ],
        "capture verification": [
            "memory-grep.sh --verify <ref>",
            "Confirm the PR `## Memory` section",
            "An empty result is a flag to fix **before** merge",
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
        missing = [needle for needle in needles if needle not in text]
        assert not missing, f"{contract} missing from entrypoint: {missing}"

    skill_root = SKILL.parent
    for relative, digest in UNCHANGED_CONTRACTS.items():
        assert sha256((skill_root / relative).read_bytes()).hexdigest() == digest
