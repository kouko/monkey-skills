"""T2 (C2) drift guard: the shared `brief-before-asking` anchor clause must
stay byte-identical (after whitespace normalization) across the four
design-side router SKILL.md files.

WHY this test exists: the audit's C2 finding was that a semantic edit to
the shared "≥3 trade-offs, ≥2 implementation paths, or architectural blast
radius — run `dev-workflow:brief-before-asking`…" clause in any one router
can silently drift from its three siblings. Each router's own test already
pins its OWN copy of the trigger triple verbatim (e.g.
loom-discovery/scripts/test_using_skill.py:146-149 and its three
siblings) — but those four pins are independent single-file assertions;
nothing asserted the four copies stay EQUAL to each other, or pinned the
tail clause after the triple (brief §Current State Evidence, Error). This
test adds that cross-file equality lockstep. Per-router lead-in / fork-noun
wording ("discovery fork" / "product/principle fork" / "design fork" /
"spec fork") is a DELIBERATE localization and stays out of scope (brief
§Out of Scope) — extraction anchors on the byte-stable fragment
"≥3 trade-offs" (Kickoff decision) so only the shared clause is compared.

`check(root)` takes an arbitrary root so RED verification can run against
an extracted, perturbed temp copy without touching the real tree (house
pattern; repo memory: mutation/RED limited to extracted copies).
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# The four design-side routers that carry the shared brief-before-asking
# clause (brief §Context paths / §Current State Evidence, Data).
ROUTER_FILES = (
    "loom-discovery/skills/using-loom-discovery/SKILL.md",
    "loom-product-principles/skills/using-loom-product-principles/SKILL.md",
    "loom-interface-design/skills/using-loom-interface-design/SKILL.md",
    "loom-spec/skills/using-loom-spec/SKILL.md",
)

# Byte-stable fragment present verbatim in all 4 routers (Kickoff decision).
ANCHOR = "≥3 trade-offs"  # "≥3 trade-offs"


def extract_anchor_sentence(text: str, rel_path: str) -> str:
    """Extract the shared clause starting at ANCHOR through the next period,
    with whitespace runs collapsed to single spaces.

    Starting AT the anchor (not at the enclosing sentence's start) is what
    excludes the per-router fork-noun lead-in that precedes it — that
    lead-in is deliberate localization, not drift (brief §Problem, C2).
    """
    count = text.count(ANCHOR)
    if count != 1:
        raise ValueError(
            f"anchor fragment {ANCHOR!r} must appear exactly once in "
            f"{rel_path}, found {count}"
        )
    idx = text.find(ANCHOR)
    end = text.find(".", idx)
    if end == -1:
        raise ValueError(f"no sentence-ending period after anchor in {rel_path}")
    fragment = text[idx : end + 1]
    return re.sub(r"\s+", " ", fragment).strip()


def check(root: Path) -> dict[str, str]:
    """Return {rel_path: normalized_sentence} for every router under root.

    Raises AssertionError naming the diverging file(s) when any router's
    normalized clause differs from the first router's.
    """
    sentences: dict[str, str] = {}
    for rel_path in ROUTER_FILES:
        text = (root / rel_path).read_text(encoding="utf-8")
        sentences[rel_path] = extract_anchor_sentence(text, rel_path)

    baseline_path, baseline = next(iter(sentences.items()))
    diverging = [
        rel_path for rel_path, sentence in sentences.items() if sentence != baseline
    ]
    if diverging:
        raise AssertionError(
            "brief-before-asking anchor clause diverges from "
            f"{baseline_path} in: {diverging}"
        )
    return sentences


def test_anchor_sentence_lockstep_across_routers():
    check(REPO_ROOT)


def test_extract_anchor_sentence_rejects_duplicate_anchor():
    """A router file where ANCHOR appears more than once is ambiguous — which
    occurrence is the shared clause? Must fail loud naming the file, not
    silently extract from the first match."""
    text = f"lead-in. {ANCHOR} first occurrence. more text. {ANCHOR} second occurrence."
    with pytest.raises(ValueError, match="dummy.md"):
        extract_anchor_sentence(text, "dummy.md")


def test_check_catches_a_perturbed_router(tmp_path):
    """Proves check() is load-bearing, not vacuous.

    The real tree currently satisfies check() exactly, so
    test_anchor_sentence_lockstep_across_routers alone would stay green even
    if check() were broken (e.g. always a no-op). This test extracts
    ROUTER_FILES' REAL content into an isolated tmp_path copy (zero mutation
    residue in the real tree — house RED-on-extracted-copy pattern,
    mirroring test_router_card_rule_tokens.py's non-vacuity test), perturbs
    one word AFTER the anchor in one router's copy, and shows check()
    actually raises, naming that router.
    """
    for rel_path in ROUTER_FILES:
        src = REPO_ROOT / rel_path
        dst = tmp_path / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)

    check(tmp_path)  # baseline: unmutated copy passes

    mutated_rel = ROUTER_FILES[0]
    mutated_path = tmp_path / mutated_rel
    text = mutated_path.read_text(encoding="utf-8")
    assert "architectural blast radius" in text
    mutated_path.write_text(
        text.replace("architectural blast radius", "PERTURBED blast radius", 1),
        encoding="utf-8",
    )

    with pytest.raises(AssertionError) as exc_info:
        check(tmp_path)

    message = str(exc_info.value)
    assert mutated_rel in message
