"""Structural contract test for the portable reviewer context packet.

Every verdict-producing agent consumes one immutable packet produced by
``review_context.py``.  This test scopes its assertions to each agent's input
contract so a historic path in explanatory prose cannot mask a dispatch that
still derives plugin resources from the consumer repository.
"""
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).parents[1]
REVIEWERS = {
    "code-reviewer": ROOT / "agents" / "code-reviewer.md",
    "docs-reviewer": ROOT / "agents" / "docs-reviewer.md",
    "spec-reviewer": ROOT / "agents" / "spec-reviewer.md",
    "code-quality-reviewer": ROOT / "agents" / "code-quality-reviewer.md",
}
DISCIPLINE = ROOT / "scripts" / "_reviewer-discipline.md"
PACKET_FIELDS = ("target_repo", "reviewed_sha", "plugin_version", "resources")


def _input_contract(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.index("## Input contract")
    end = text.index("## Output contract", start)
    return text[start:end]


def test_all_reviewer_roles_require_portable_context_packet():
    """Every reviewer receives the same packet and never derives paths.

    Rule R1 is shared by all four agents.  Therefore every input contract,
    not merely the code-reviewer contract, must name all packet fields and
    constrain plugin-resource reads to the packet's approved absolute paths.
    """
    for name, path in REVIEWERS.items():
        contract = _input_contract(path)
        normalized = re.sub(r"\s+", " ", contract)
        assert "### Immutable review context" in contract, (
            f"{name} has no immutable context packet in its input contract"
        )
        for field in PACKET_FIELDS:
            assert field in contract, (
                f"{name} input contract omits packet field {field!r}"
            )
        assert "approved absolute" in normalized, (
            f"{name} must constrain resource reads to approved absolute paths"
        )
        assert "never derive" in contract, (
            f"{name} must forbid consumer-relative plugin-path derivation"
        )


def test_docs_reviewer_verdict_sha_comes_only_from_immutable_packet():
    """Docs review must not permit a second SHA input beside the packet."""
    docs = REVIEWERS["docs-reviewer"].read_text(encoding="utf-8")
    input_contract = _input_contract(REVIEWERS["docs-reviewer"])
    output_start = docs.index("## Output contract")
    output_contract = docs[output_start:]

    assert "### HEAD sha" not in input_contract, (
        "docs-reviewer must not accept a separate HEAD-sha header that can "
        "diverge from immutable context reviewed_sha"
    )
    assert "immutable review context packet's `reviewed_sha`" in output_contract, (
        "docs-reviewer verdict provenance must name the immutable packet "
        "reviewed_sha as its only source"
    )
    assert "packet's `### HEAD sha`" not in output_contract, (
        "docs-reviewer must not retain the retired independent HEAD-sha "
        "output branch"
    )


def test_docs_reviewer_rejects_invalid_packet_reviewed_sha():
    """A docs verdict requires a real SHA from the immutable packet."""
    docs = REVIEWERS["docs-reviewer"].read_text(encoding="utf-8")
    output_contract = re.sub(
        r"\s+", " ", docs[docs.index("## Output contract"):].lower()
    )

    assert "missing, non-sha, or `unresolved`" in output_contract, (
        "docs-reviewer must classify every absent or invalid packet "
        "reviewed_sha as malformed"
    )
    assert "verdict: malformed_packet" in output_contract, (
        "docs-reviewer must refuse observably (MALFORMED_PACKET) rather "
        "than emit a quality verdict for an invalid packet reviewed_sha"
    )


def test_all_reviewer_outputs_echo_only_packet_reviewed_sha():
    """Every verdict needs the same immutable SHA provenance."""
    for name in REVIEWERS:
        reviewer = REVIEWERS[name].read_text(encoding="utf-8")
        input_contract = _input_contract(REVIEWERS[name])
        output_contract = reviewer[reviewer.index("## Output contract"):]
        normalized = re.sub(r"\s+", " ", output_contract.lower())

        assert "<reviewed_sha>" in input_contract, (
            f"{name} artifact/diff input must be bound to the packet SHA"
        )
        assert "immutable review context packet's `reviewed_sha`" in output_contract, (
            f"{name} must identify packet reviewed_sha as verdict provenance"
        )
        assert "missing, non-sha, or `unresolved`" in normalized, (
            f"{name} must reject an invalid packet reviewed_sha"
        )
        assert "verdict: malformed_packet" in normalized, (
            f"{name} must refuse observably (MALFORMED_PACKET) without a "
            "valid packet reviewed_sha"
        )


def test_malformed_packet_refusal_is_observable():
    """A malformed packet yields MALFORMED_PACKET + missing_fields, never silence.

    Live tests (n=2) showed a "return no verdict" silence instruction is both
    violated in practice and indistinguishable from a dead agent.  The refusal
    must therefore be an observable output: ``verdict: MALFORMED_PACKET`` plus
    a ``missing_fields:`` list naming each absent/invalid packet field.
    """
    shared = re.sub(r"\s+", " ", DISCIPLINE.read_text(encoding="utf-8"))
    assert "return no verdict" not in shared, (
        "shared discipline must not instruct silent refusal — silence is "
        "indistinguishable from a dead agent"
    )
    assert "verdict: MALFORMED_PACKET" in shared, (
        "shared discipline must require the observable MALFORMED_PACKET refusal"
    )
    assert "missing_fields:" in shared, (
        "shared discipline must require a missing_fields: list naming each "
        "absent or invalid packet field"
    )
    for name, path in REVIEWERS.items():
        text = path.read_text(encoding="utf-8")
        assert "return no verdict" not in text, (
            f"{name} still carries the silent-refusal instruction"
        )
        output_contract = re.sub(
            r"\s+", " ", text[text.index("## Output contract"):]
        )
        assert "MALFORMED_PACKET" in output_contract, (
            f"{name} output contract must define the MALFORMED_PACKET "
            "packet-refusal state"
        )
        assert "never mintable" in output_contract.lower(), (
            f"{name} must state MALFORMED_PACKET is never mintable as a "
            "gate marker"
        )


def test_all_reviewers_read_only_the_immutable_snapshot():
    """No reviewer can inspect a mutable worktree for path artifacts."""
    for name in REVIEWERS:
        contract = _input_contract(REVIEWERS[name])
        assert "git diff <base>..<reviewed_sha>" in contract, (
            f"{name} must bind its diff scope's right endpoint to reviewed_sha"
        )
        assert "git show <reviewed_sha>:<path>" in contract, (
            f"{name} must load path artifacts from the immutable snapshot"
        )
        assert "never the mutable working tree" in contract, (
            f"{name} must reject mutable-worktree artifact reads"
        )


def test_reviewer_artifact_paths_are_repo_relative_before_sha_reads():
    """Reviewed repository evidence cannot name a mutable absolute path."""
    required = (
        "Repository artifact paths are repository-relative",
        "Reject an absolute repository artifact path as malformed",
        'git -C "<target_repo>" show <reviewed_sha>:<path>',
        "Never read it from the mutable working tree",
    )
    shared = re.sub(r"\s+", " ", DISCIPLINE.read_text(encoding="utf-8")).lower()
    for phrase in required:
        assert phrase.lower() in shared, (
            "shared discipline must require immutable repo-relative paths"
        )

    forbidden_packet_paths = (
        "absolute path to tech-spec",
        "absolute path to product-spec",
        "absolute paths to changed files",
        "absolute paths to task description",
    )
    for name, path in REVIEWERS.items():
        text = re.sub(r"\s+", " ", _input_contract(path)).lower()
        assert "git show <reviewed_sha>:<path>" in text, (
            f"{name} input contract must bind path artifacts to reviewed_sha"
        )
        assert "never the mutable working tree" in text, (
            f"{name} input contract must prohibit a mutable path fallback"
        )
        for forbidden in forbidden_packet_paths:
            assert forbidden not in text, (
                f"{name} input contract must not accept {forbidden!r}"
            )

    for name in ("spec-reviewer", "code-quality-reviewer"):
        contract = _input_contract(REVIEWERS[name]).lower()
        assert "repository-relative paths to changed files" in contract, (
            f"{name} must make changed-file packet paths repository-relative"
        )
    assert "repository-relative path to tech-spec" in _input_contract(
        REVIEWERS["spec-reviewer"]
    ).lower()


def test_all_reviewer_cross_reads_use_the_immutable_snapshot():
    """Citation cross-reads of repository files cannot read a live tree."""
    required = (
        "repository-path cross-read",
        'git -c "<target_repo>" show <reviewed_sha>:<path>',
        "never read it from the mutable working tree",
    )
    for name, path in REVIEWERS.items():
        reviewer = re.sub(r"\s+", " ", path.read_text(encoding="utf-8").lower())
        for phrase in required:
            assert phrase in reviewer, (
                f"{name} must bind repository citation cross-reads to "
                f"the reviewed_sha snapshot: {phrase!r}"
            )


def test_code_reviewer_principles_and_simplifications_use_reviewed_sha():
    """D8/D9 must never derive evidence from the mutable worktree."""
    reviewer = REVIEWERS["code-reviewer"].read_text(encoding="utf-8")
    d8 = reviewer[reviewer.index("#### D8"):reviewer.index("#### D9")]
    d9 = reviewer[reviewer.index("#### D9"):reviewer.index("#### D10")]
    d8_commands = re.search(r"```bash\n(.*?)```", d8, re.DOTALL).group(1)
    d9_commands = re.search(r"```bash\n(.*?)```", d9, re.DOTALL).group(1)

    assert (
        'git -C "<target_repo>" cat-file -e '
        '"<reviewed_sha>:docs/loom/PRINCIPLES.md"' in d8_commands
    ), "D8 must test PRINCIPLES.md existence in the reviewed snapshot"
    assert (
        'git -C "<target_repo>" show '
        '"<reviewed_sha>:docs/loom/PRINCIPLES.md"' in d8_commands
    ), "D8 must read PRINCIPLES.md from the reviewed snapshot"
    for mutable_probe in (
        "git rev-parse",
        "test -e",
        "test -f",
        "[ -e",
        "[ -f",
        "HEAD:docs/loom/PRINCIPLES.md",
    ):
        assert mutable_probe not in d8_commands, (
            f"D8 must not derive PRINCIPLES evidence through {mutable_probe!r}"
        )

    assert 'git -C "<target_repo>" diff --name-only -z ' in d9_commands, (
        "D9 must enumerate branch files through Git"
    )
    assert 'git -C "<target_repo>" show "<reviewed_sha>:$path"' in d9_commands, (
        "D9 must read each changed file from the reviewed snapshot"
    )
    assert "xargs grep" not in d9_commands, "D9 must not grep mutable worktree files"
    assert "cat <diff-path>" not in d9_commands, "D9 must not read mutable diff files"
    for mutable_read in (
        "git show HEAD:",
        "git show <base>:",
    ):
        assert mutable_read not in d9_commands, (
            f"D9 must not derive marker evidence through {mutable_read!r}"
        )
