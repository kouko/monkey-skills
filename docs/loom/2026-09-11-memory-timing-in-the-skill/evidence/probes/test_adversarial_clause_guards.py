"""Adversarial probes for 2026-09-11-memory-timing-in-the-skill.

Acceptance 4 claims the deletion of either half of the Record contract turns
a test red, and that a rewording keeping both halves does not. Acceptance 5
claims the review station's paragraph sits between convergence and Finalize,
carries no gate marker, and names no plugin.

Every one of those claims is about what happens to a test under a mutation
nobody has performed. So perform them: copy the real tree, mutate the shipped
prose, run the real test module against the mutant, and assert on the
subprocess exit code — not on a claim about it.

Run: python3 -m pytest <this file> -q
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
MEMORY_SKILL = Path("loom-workflow/skills/loom-memory")
MEMORY_TEST = MEMORY_SKILL / "scripts" / "test_skill_contract.py"
REVIEW_SKILL = Path("loom-code/skills/review/SKILL.md")
REVIEW_TEST = Path("loom-code/scripts/test_review_convergence_contract.py")


def _sandbox(tmp_path: Path, *trees: Path) -> Path:
    """Copy the paths a test module reads into an isolated tree.

    The modules resolve their targets relative to their own location, so the
    directory shape has to be preserved, not just the files.
    """
    root = tmp_path / "repo"
    for rel in trees:
        src = REPO_ROOT / rel
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
    return root


def _run(root: Path, test_rel: Path, selector: str = "") -> subprocess.CompletedProcess:
    target = str(root / test_rel) + selector
    return subprocess.run(
        [sys.executable, "-m", "pytest", target, "-q", "-p", "no:cacheprovider"],
        capture_output=True,
        text=True,
        cwd=root / test_rel.parent,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"},
    )


def _memory_sandbox(tmp_path: Path) -> Path:
    root = _sandbox(
        tmp_path,
        MEMORY_SKILL / "SKILL.md",
        MEMORY_SKILL / "references",
        MEMORY_SKILL / "scripts",
        Path("loom-workflow/.claude-plugin/plugin.json"),
    )
    (root / MEMORY_SKILL / "evals").mkdir(parents=True, exist_ok=True)
    return root


# --- Acceptance 4: deletion is caught ---------------------------------------


@pytest.mark.parametrize(
    "clause, label, node",
    [
        ("**When:** before the branch closes.", "timing",
         "::test_record_contract_states_when_to_record"),
        ("**How much:** almost nothing qualifies.", "scarcity",
         "::test_record_contract_states_how_much_to_record"),
    ],
)
def test_deleting_either_half_turns_the_pin_red(tmp_path, clause, label, node) -> None:
    """Cut the paragraph that opens with `clause` out of the shipped SKILL.md
    and both references; the pin must fail, not pass."""
    root = _memory_sandbox(tmp_path)
    skill_md = root / MEMORY_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    assert clause in text, f"probe anchor missing: {clause!r}"
    start = text.index(clause)
    end = text.index("\n\n", start) + 2
    skill_md.write_text(text[:start] + text[end:], encoding="utf-8")

    ops = root / MEMORY_SKILL / "references" / "operations.md"
    ops_text = ops.read_text(encoding="utf-8")
    for sentence in ("Record runs while the branch is still open.", "Almost nothing reaches step 3."):
        if sentence in ops_text:
            s = ops_text.index(sentence)
            e = ops_text.index("\n\n", s) + 2
            ops_text = ops_text[:s] + ops_text[e:]
    ops.write_text(ops_text, encoding="utf-8")

    result = _run(root, MEMORY_TEST, node)
    assert result.returncode != 0, (
        f"deleting the {label} half left the pin green:\n{result.stdout}{result.stderr}"
    )


def test_the_failure_message_tells_the_deleter_what_they_are_deleting(tmp_path) -> None:
    """A red pin whose message is just an assertion error invites the edit
    that made it green. The message must carry the reason and the history."""
    root = _memory_sandbox(tmp_path)
    skill_md = root / MEMORY_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    start = text.index("**When:** before the branch closes.")
    end = text.index("\n\n", start) + 2
    skill_md.write_text(text[:start] + text[end:], encoding="utf-8")
    ops = root / MEMORY_SKILL / "references" / "operations.md"
    ops_text = ops.read_text(encoding="utf-8")
    s = ops_text.index("Record runs while the branch is still open.")
    e = ops_text.index("\n\n", s) + 2
    ops.write_text(ops_text[:s] + ops_text[e:], encoding="utf-8")

    out = _run(root, MEMORY_TEST, "::test_record_contract_states_when_to_record").stdout
    assert "needs an intent" in out, f"failure message does not say removal needs an intent:\n{out}"
    assert "loom 1.0" in out, f"failure message does not carry the deletion history:\n{out}"


# --- Acceptance 4 boundary: rewording is NOT caught --------------------------


def test_rewording_that_keeps_both_halves_stays_green(tmp_path) -> None:
    """The pin must survive legitimate editing. A pin that fires on a
    faithful rewrite trains its reader to ignore it."""
    root = _memory_sandbox(tmp_path)
    skill_md = root / MEMORY_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    # Rewrap every paragraph onto one physical line and re-punctuate lightly.
    reflowed = "\n\n".join(
        " ".join(block.split()) if not block.lstrip().startswith(("#", "-", "|", "`"))
        else block
        for block in text.split("\n\n")
    )
    assert reflowed != text, "probe did not actually reword anything"
    skill_md.write_text(reflowed, encoding="utf-8")

    result = _run(root, MEMORY_TEST, "::test_record_contract_states_when_to_record")
    assert result.returncode == 0, (
        f"a whitespace-only rewrap turned the pin red:\n{result.stdout}{result.stderr}"
    )


# --- Acceptance 5: placement, inertness, no mechanism ------------------------


def _review_sandbox(tmp_path: Path) -> Path:
    return _sandbox(
        tmp_path,
        REVIEW_SKILL,
        REVIEW_TEST,
        Path("loom-code/agents/reviewer.md"),
    )


def test_moving_the_paragraph_past_finalize_turns_the_pin_red(tmp_path) -> None:
    """After Finalize the attestation exists, and a store edit then
    invalidates it — which is the excuse the whole change exists to remove."""
    root = _review_sandbox(tmp_path)
    md = root / REVIEW_SKILL
    text = md.read_text(encoding="utf-8")
    start = text.index("Convergence is also the last moment")
    end = text.index("\n## 5. Finalize")
    paragraph = text[start:end]
    moved = text[:start] + text[end:]
    moved = moved.replace("\n## Handoff", "\n" + paragraph + "\n## Handoff")
    md.write_text(moved, encoding="utf-8")

    result = _run(root, REVIEW_TEST)
    assert result.returncode != 0, (
        f"the paragraph moved past Finalize and nothing noticed:\n{result.stdout}{result.stderr}"
    )


def test_marking_the_paragraph_as_a_gate_turns_the_pin_red(tmp_path) -> None:
    """The charter forbids a prose-only gate, and this rule's criterion is a
    judgement. A gate marker here would also add a mechanism silently."""
    root = _review_sandbox(tmp_path)
    md = root / REVIEW_SKILL
    text = md.read_text(encoding="utf-8")
    text = text.replace(
        "Convergence is also the last moment",
        "<!-- gate: review.record-the-lesson -->\nConvergence is also the last moment",
    )
    md.write_text(text, encoding="utf-8")

    result = _run(root, REVIEW_TEST)
    assert result.returncode != 0, (
        f"a gate marker was added to the paragraph and the pin stayed green:\n"
        f"{result.stdout}{result.stderr}"
    )


def test_naming_a_plugin_in_the_paragraph_turns_the_pin_red(tmp_path) -> None:
    """The paragraph points at a store path anyone can check for existence.
    Naming a plugin would make one station depend on another's install."""
    root = _review_sandbox(tmp_path)
    md = root / REVIEW_SKILL
    text = md.read_text(encoding="utf-8")
    text = text.replace(
        "that is where such a lesson belongs.",
        "that is where such a lesson belongs, via loom-memory.",
    )
    md.write_text(text, encoding="utf-8")

    result = _run(root, REVIEW_TEST)
    assert result.returncode != 0, (
        f"the paragraph named a plugin and the pin stayed green:\n"
        f"{result.stdout}{result.stderr}"
    )
