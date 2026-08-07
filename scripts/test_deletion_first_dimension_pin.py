"""T5 (loom arc-2 deletion-first-dimension plan): pin the deletion-first
dimension's two hand-authored copies — loom-code/agents/code-quality-reviewer.md
(per-task) and loom-code/agents/code-reviewer.md (whole-branch) — so an edit
to one that forgets the other is caught, not silently drifted.

WHY this test exists: Task 2 and Task 3 hand-transcribed the SAME pinned
table row and enum line into two separate agent files (per Notes pin in
docs/loom/plans/2026-08-07-loom-arc2-deletion-first-dimension.md — "transcribe
VERBATIM from Notes pin"). Nothing else keeps the two copies in lockstep;
this test is that lock.

Two things are pinned per file:
  (a) the three anchor tokens ("deletion-first", "smaller shape",
      "≥2 concrete users") appear somewhere in the file's hand-authored
      Dimensions-table + D-section region (NOT a whole-file grep — see
      block-scoping note below);
  (b) the `dimension_scores:` block carries the bracket-free enum line
      `  deletion-first: PASS | PASS_WITH_NOTES | NEEDS_REVISION` verbatim
      (Decision Log, wave 1: angle brackets deliberately dropped to match
      both files' sibling enum lines and avoid weak-tier literalization —
      repo memory: worked-example-is-prescriptive).

Block scoping: whole-file grep is false-green-prone — e.g. a token could
survive in unrelated prose while the actual table row / D-section got
mangled. The two files do not share one heading spelling (per-task file's
heading is "### Dimensions — what each one means"; whole-branch file's is
"### Dimensions — what each one means at branch scope"), so this test
scopes PER FILE to that file's own dimensions-region start marker through
its own next top-level heading — mirroring test_router_card_rule_tokens.py's
anchor-extraction pattern, adapted because these two files don't share
identical anchor text.

check(root) takes an arbitrary root so RED verification (and the
mutation-catch test below) can run against an extracted, perturbed temp
copy without touching the real tree (house pattern; repo memory:
mutation/RED limited to extracted copies, zero residue in the real tree).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Pinned anchor tokens (Notes pin, docs/loom/plans/2026-08-07-...md).
ANCHOR_TOKENS = ("deletion-first", "smaller shape", "≥2 concrete users")

# Pinned bracket-free enum line (Decision Log, wave 1 amendment).
ENUM_LINE = "  deletion-first: PASS | PASS_WITH_NOTES | NEEDS_REVISION"

# Per-file dimensions-region markers. Dict insertion order matters for the
# mutation-catch test below: code-quality-reviewer.md is the FIRST-iterated
# (baseline) file; code-reviewer.md is the NON-first file the mutation test
# perturbs (arc-1 round-3 lesson: never perturb the file the check treats
# as its baseline/first-iterated).
FILES = {
    "loom-code/agents/code-quality-reviewer.md": {
        "dims_start": "### Dimensions — what each one means",
        "dims_end": "### Anti-patterns the orchestrator will reject",
    },
    "loom-code/agents/code-reviewer.md": {
        "dims_start": "### Dimensions — what each one means at branch scope",
        "dims_end": "## Anti-patterns the orchestrator will reject",
    },
}

DIMENSION_SCORES_START = "dimension_scores:"
DIMENSION_SCORES_END = "findings:"


def _extract(text: str, start_marker: str, end_marker: str, rel_path: str, label: str) -> str:
    """Return the substring between two markers, or raise naming the gap."""
    start = text.find(start_marker)
    if start == -1:
        raise ValueError(f"{label} start marker {start_marker!r} not found in {rel_path}")
    end = text.find(end_marker, start + len(start_marker))
    if end == -1:
        raise ValueError(f"{label} end marker {end_marker!r} not found in {rel_path}")
    return text[start:end]


def check(root: Path) -> None:
    """Assert both files carry the pinned anchor tokens + bracket-free enum line.

    Raises AssertionError naming every (file, missing-thing) pair — the
    failure message is the sweep list a real edit needs to act on.
    """
    missing: list[str] = []
    for rel_path, markers in FILES.items():
        text = (root / rel_path).read_text(encoding="utf-8")

        dims_block = _extract(
            text, markers["dims_start"], markers["dims_end"], rel_path, "dimensions region"
        )
        for token in ANCHOR_TOKENS:
            if token not in dims_block:
                missing.append(f"anchor token {token!r} missing from {rel_path} dimensions region")

        enum_block = _extract(
            text, DIMENSION_SCORES_START, DIMENSION_SCORES_END, rel_path, "dimension_scores block"
        )
        if ENUM_LINE not in enum_block:
            missing.append(
                f"bracket-free enum line {ENUM_LINE!r} missing from {rel_path} dimension_scores block"
            )

    if missing:
        raise AssertionError("deletion-first dimension pin mismatch:\n" + "\n".join(missing))


def test_deletion_first_pin_present_in_both_files():
    check(REPO_ROOT)


def test_check_catches_a_perturbed_non_baseline_file(tmp_path):
    """Proves check() is load-bearing, not vacuous.

    The real tree currently satisfies check() exactly, so the test above
    alone would stay green even if check() were broken (e.g. always a
    no-op). This test extracts FILES' REAL content into an isolated
    tmp_path copy (zero mutation residue in the real tree — house
    RED-on-extracted-copy pattern), removes one anchor token from the
    copy's code-reviewer.md, and shows check() actually raises, naming
    that file.

    File choice is deliberate: FILES is iterated in dict-insertion order,
    so code-quality-reviewer.md is the first-iterated (baseline) file and
    code-reviewer.md is the second/non-first one — this test perturbs
    code-reviewer.md, never the baseline (arc-1 round-3 lesson: a mutant
    on the baseline file can pass unnoticed if the check's own iteration
    silently favors whatever it saw first).
    """
    for rel_path in FILES:
        src = REPO_ROOT / rel_path
        dst = tmp_path / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)

    check(tmp_path)  # baseline: unmutated copy passes

    baseline_rel, mutated_rel = FILES.keys()
    assert baseline_rel == "loom-code/agents/code-quality-reviewer.md"
    assert mutated_rel == "loom-code/agents/code-reviewer.md"

    mutated_path = tmp_path / mutated_rel
    text = mutated_path.read_text(encoding="utf-8")
    token = "≥2 concrete users"
    occurrences = text.count(token)
    assert occurrences >= 1
    # Replace every occurrence (not just the first) — the token repeats once
    # inside the dims-table row and once in D-section prose; a partial
    # replace would leave the region still satisfying check() and produce
    # a false-green mutation test.
    mutated_path.write_text(text.replace(token, "REMOVED-TOKEN"), encoding="utf-8")

    with pytest.raises(AssertionError) as exc_info:
        check(tmp_path)

    message = str(exc_info.value)
    assert mutated_rel in message
    assert token in message
    # The untouched baseline file must NOT be named as the failure source.
    assert baseline_rel not in message
