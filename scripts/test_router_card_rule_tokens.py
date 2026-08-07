"""T3 (D2) drift guard: the five load-bearing rules' distinctive anchor
tokens must appear in BOTH loom-code/hooks/router-card.md's rules block and
loom-code/skills/using-loom-code/SKILL.md's rules block.

WHY this test exists: router-card.md is the SessionStart-injected compressed
pull-pointer; using-loom-code/SKILL.md is the full router. session-start's
comment (loom-code/hooks/session-start:6-11) documents this as a deliberate
compression — the two copies are NOT byte-identical (SKILL.md carries extra
citations/prose per rule) — so this test does NOT assert byte-equality. It
asserts a weaker, still load-bearing invariant: each rule's distinctive
anchor token (the skill-id or verbatim clause a reader/hook keys off) is
present in both blocks. Losing a token from one side silently breaks that
side's rule binding while the other side stays intact — this is the drift
this test catches.

Block scoping: whole-file grep is false-green-prone (e.g. a token could
appear in unrelated prose elsewhere in either file and mask a real removal
from the rules block itself). Both files carry the same two anchor lines
verbatim — "Five load-bearing rules" opens the block, "Skipping any of
these = violation." closes it (confirmed identical substrings in both
files) — so extract_rules_block scopes the token search to the text between
them, mirroring test_brief_clause_lockstep.py's anchor-extraction pattern.

Plan Kickoff decision (amended during wave 1, NEEDS_CONTEXT round 1): rule
5's anchor token is "Research before asking" (the rule's verbatim title, per
both files' rule 5 line) — NOT "brief-before-asking", which never appears in
using-loom-code/SKILL.md's rule 5 text.

check(root) takes an arbitrary root so RED verification can run against an
extracted, perturbed temp copy without touching the real tree (house
pattern; repo memory: mutation/RED limited to extracted copies).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# The two files whose rules blocks must both carry every rule's anchor token.
FILES = (
    "loom-code/hooks/router-card.md",
    "loom-code/skills/using-loom-code/SKILL.md",
)

# rule number -> distinctive anchor token (Kickoff decision, amended wave 1).
RULE_TOKENS = {
    1: "Brainstorm before implementing",
    2: "tdd-iron-law",
    3: "subagent-driven-development",
    4: "finishing-a-development-branch",
    5: "Research before asking",
}

START_MARKER = "Five load-bearing rules"
END_MARKER = "Skipping any of these = violation."


def extract_rules_block(text: str, rel_path: str) -> str:
    """Return the substring between the two shared anchor lines.

    Scoping to this substring (rather than the whole file) is what makes the
    check false-green-resistant: a token match outside the rules block does
    not count.
    """
    start = text.find(START_MARKER)
    if start == -1:
        raise ValueError(f"{START_MARKER!r} not found in {rel_path}")
    end = text.find(END_MARKER, start)
    if end == -1:
        raise ValueError(f"{END_MARKER!r} not found in {rel_path}")
    return text[start:end]


def check(root: Path) -> None:
    """Assert every rule's anchor token appears in both files' rules blocks.

    Raises AssertionError naming each (rule, file) pair that is missing its
    token — the failure message is the sweep list a real edit needs to act
    on, not just a bare "mismatch".
    """
    blocks: dict[str, str] = {}
    for rel_path in FILES:
        text = (root / rel_path).read_text(encoding="utf-8")
        blocks[rel_path] = extract_rules_block(text, rel_path)

    missing: list[str] = []
    for rule_num, token in RULE_TOKENS.items():
        for rel_path, block in blocks.items():
            if token not in block:
                missing.append(f"rule {rule_num} ({token!r}) missing from {rel_path}")

    if missing:
        raise AssertionError(
            "router-card rule-token presence mismatch:\n" + "\n".join(missing)
        )


def test_router_card_rule_tokens_present_in_both_files():
    check(REPO_ROOT)


def test_check_catches_a_removed_rule_token(tmp_path):
    """Proves check() is load-bearing, not vacuous.

    The real tree currently satisfies check() exactly, so the test above
    alone would stay green even if check() were broken (e.g. always a
    no-op). This test extracts FILES' REAL content into an isolated
    tmp_path copy (zero mutation residue in the real tree — house
    RED-on-extracted-copy pattern, mirroring
    test_state_anchor_carrier_inventory.py's non-vacuity test), removes
    rule 2's anchor token from the copy's router-card.md, and shows
    check() actually raises, naming that rule + file.
    """
    for rel_path in FILES:
        src = REPO_ROOT / rel_path
        dst = tmp_path / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)

    check(tmp_path)  # baseline: unmutated copy passes

    mutated_rel = "loom-code/hooks/router-card.md"
    mutated_path = tmp_path / mutated_rel
    text = mutated_path.read_text(encoding="utf-8")
    token = RULE_TOKENS[2]
    assert token in text
    mutated_path.write_text(text.replace(token, "REMOVED", 1), encoding="utf-8")

    with pytest.raises(AssertionError) as exc_info:
        check(tmp_path)

    message = str(exc_info.value)
    assert "rule 2" in message
    assert token in message
    assert mutated_rel in message
