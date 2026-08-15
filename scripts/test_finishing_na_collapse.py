"""T15 drift guard: the finishing close-out report must consolidate multiple
N/A check outcomes into ONE summary line AFTER the plain conclusion, not
stack ~4-5 separate 'N/A — checker not present' lines BEFORE it.

WHY this test exists: the checks table (SKILL.md ~187-194) has several rows
whose 'On failure or N/A' column says 'say loudly' for each inapplicable
check (memory-store 'checker not present', archive-on-close 'no
change-folder bound', backlog-close 'index not regenerated', etc.). Left
unconstrained, the agent emits one line per N/A check BEFORE the conclusion,
burying the conclusion under noise. The plain-relay contract (rule 1
conclusion-first) says the conclusion comes first; the N/A noise collapses
into one summary line after it. This test pins that consolidation
instruction so a future edit cannot silently restore the stacking behavior.

Block scoping: the consolidated instruction lives in the close-out region
(between the checks-table header and Step 13's report). Scoping to that
region — rather than whole-file grep — prevents a token match in unrelated
prose from masking a real removal. The two anchor markers are the table
header row ('| Check | When it fires | Action | On failure or N/A |') and
the Step 13 close ('skip the line when the repo has no backlog store').

Non-vacuity: a tmp_path mutation that removes the consolidated-instruction
phrase from an extracted copy makes check() raise — proving the test is
load-bearing, not a no-op.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

SKILL_REL = "loom-code/skills/finishing-a-development-branch/SKILL.md"

# The close-out region anchors. The checks table header opens the region;
# the Step-13 backlog tailer closes it. Text between them is the block the
# consolidated instruction must live inside.
START_MARKER = "| Check | When it fires | Action | On failure or N/A |"
END_MARKER = "skip the line when the repo has no backlog store"

# The distinctive tokens the consolidated instruction must carry. Each is a
# phrase that only the new N/A-collapse instruction contributes — none of
# them appear in the unedited repo, so asserting their presence is a true
# RED on the pre-edit tree.
REQUIRED_TOKENS = (
    "consolidate inapplicable checks",
    "N inapplicable checks skipped",
    "after the plain conclusion",
)


def extract_closeout_block(text: str) -> str:
    """Return the substring between the checks-table header and Step 13's tail.

    Scoping to this substring (not the whole file) is what makes the check
    false-green-resistant: a token match in unrelated prose (e.g. a 'N/A'
    mention in the When-NOT-to-use section) does not satisfy the invariant.
    """
    start = text.find(START_MARKER)
    if start == -1:
        raise ValueError(f"{START_MARKER!r} not found in {SKILL_REL}")
    end = text.find(END_MARKER, start)
    if end == -1:
        raise ValueError(f"{END_MARKER!r} not found in {SKILL_REL}")
    # Include the END_MARKER line itself so a token on that line counts.
    return text[start : end + len(END_MARKER)]


def check(root: Path) -> None:
    """Assert the close-out block carries the consolidated N/A instruction.

    Raises AssertionError naming each missing token — the failure message is
    the sweep list a real edit needs to act on, not a bare 'mismatch'.
    """
    text = (root / SKILL_REL).read_text(encoding="utf-8")
    block = extract_closeout_block(text)

    missing: list[str] = []
    for token in REQUIRED_TOKENS:
        if token not in block:
            missing.append(repr(token))

    if missing:
        raise AssertionError(
            "finishing close-out N/A-collapse instruction missing tokens "
            f"in {SKILL_REL} close-out block:\n  " + "\n  ".join(missing)
        )


def test_na_lines_consolidated():
    """The close-out report consolidates N/A checks into one line after the
    conclusion, not stacked before it.

    RED on the unedited tree: none of the REQUIRED_TOKENS exist yet, so this
    fails until the consolidation instruction is added. GREEN once it is.
    """
    check(REPO_ROOT)


def test_check_catches_a_removed_consolidation_instruction(tmp_path):
    """Proves check() is load-bearing, not vacuous.

    Extracts the REAL SKILL.md into an isolated tmp_path copy (zero mutation
    residue in the real tree — house RED-on-extracted-copy pattern), removes
    the consolidated-instruction phrase from the copy, and shows check()
    actually raises, naming that token.
    """
    # NOTE: this non-vacuity test can only run AFTER the GREEN edit lands the
    # consolidated instruction (the RED tree has no such token to remove).
    # On the unedited tree this test is SKIPPED — it is a guard for future
    # regressions, not a RED driver.
    src = REPO_ROOT / SKILL_REL
    dst = tmp_path / SKILL_REL
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)

    # Baseline: unmutated copy passes (only true once GREEN is in place).
    try:
        check(tmp_path)
    except AssertionError:
        pytest.skip(
            "consolidation instruction not yet present in real tree — "
            "this non-vacuity guard activates after the GREEN edit"
        )

    mutated_path = tmp_path / SKILL_REL
    text = mutated_path.read_text(encoding="utf-8")
    token = REQUIRED_TOKENS[0]
    assert token in text, (
        f"baseline passed but {token!r} absent — invariant inconsistency"
    )
    mutated_path.write_text(
        text.replace(token, "REMOVED", 1), encoding="utf-8"
    )

    with pytest.raises(AssertionError) as exc_info:
        check(tmp_path)

    message = str(exc_info.value)
    assert "REMOVED" in message or token in message