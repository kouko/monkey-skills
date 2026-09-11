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


# --- Acceptance 4 boundary: what the literal pin does and does not tolerate ---
#
# The first version of this section claimed to prove "a rewording that keeps
# both halves stays green" and proved nothing of the sort: it rewrapped
# whitespace without changing a single word. The real boundary is narrower and
# is written out here rather than papered over — a literal-phrase pin tolerates
# reflowing and nothing else.


def test_reflowing_the_whole_skill_stays_green(tmp_path) -> None:
    """Prose wraps. The pin flattens whitespace first, so rewrapping every
    paragraph onto one physical line must not turn it red."""
    root = _memory_sandbox(tmp_path)
    skill_md = root / MEMORY_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    reflowed = "\n\n".join(
        " ".join(block.split()) if not block.lstrip().startswith(("#", "-", "|", "`"))
        else block
        for block in text.split("\n\n")
    )
    assert reflowed != text, "probe did not actually reflow anything"
    skill_md.write_text(reflowed, encoding="utf-8")

    result = _run(root, MEMORY_TEST, "::test_record_contract_states_when_to_record")
    assert result.returncode == 0, (
        f"a whitespace-only rewrap turned the pin red:\n{result.stdout}{result.stderr}"
    )


def test_a_faithful_synonym_rewrite_does_turn_the_pin_red(tmp_path) -> None:
    """The honest half of the boundary.

    This rewrite preserves the clause exactly — same rule, same exception,
    same bar — and changes only the wording. The pin goes red anyway, because
    it matches literal phrases. That is the known cost of the only mechanism
    available for this, and the test asserts it so no future reader mistakes
    the pin for something smarter than it is.

    When this fires in real life the answer is in the test module's header:
    confirm the clause survived, then update the phrase list in the same
    commit. It is NOT to delete the assertion.
    """
    root = _memory_sandbox(tmp_path)
    skill_md = root / MEMORY_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    rewrites = {
        "belongs in\nthat same branch": "goes into that same branch",
        "pure overhead": "wasted work",
        "only\nconfirmable by observing": "verifiable only by watching",
    }
    for before, after in rewrites.items():
        assert before in text, f"probe anchor missing: {before!r}"
        text = text.replace(before, after)
    skill_md.write_text(text, encoding="utf-8")

    result = _run(root, MEMORY_TEST, "::test_record_contract_states_when_to_record")
    assert result.returncode != 0, (
        "a synonym rewrite left the pin green — the pin is not the literal "
        "matcher this project documents it to be:\n"
        f"{result.stdout}{result.stderr}"
    )
    assert "needs an intent" in result.stdout, (
        "the red gave no guidance, which is how a legitimate reword becomes a "
        f"deleted assertion:\n{result.stdout}"
    )


def test_editing_the_record_section_demands_the_eval_be_rerun(tmp_path) -> None:
    """A literal pin cannot see dilution. The digest test is what makes a
    clause edit visible to the cold-reader eval at all, so prove it fires and
    that it names the eval."""
    root = _memory_sandbox(tmp_path)
    (root / MEMORY_SKILL / "evals").mkdir(parents=True, exist_ok=True)
    skill_md = root / MEMORY_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    softened = text.replace(
        "belongs in\nthat same branch, never a separate post-merge branch",
        "should usually go in that same branch rather than a post-merge branch",
    )
    assert softened != text, "probe anchor missing"
    skill_md.write_text(softened, encoding="utf-8")

    node = "::test_record_section_matches_the_digest_the_cold_reader_eval_was_run_against"
    result = _run(root, MEMORY_TEST, node)
    assert result.returncode != 0, (
        f"the Record section was softened and the digest stayed green:\n"
        f"{result.stdout}{result.stderr}"
    )
    assert "record-timing" in result.stdout, (
        f"the red does not name the eval that must be re-run:\n{result.stdout}"
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
    start = text.index("Convergence is where a lesson")
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
        "Convergence is where a lesson",
        "<!-- gate: review.record-the-lesson -->\nConvergence is where a lesson",
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


def test_naming_a_plugin_in_the_SCARCITY_paragraph_turns_the_pin_red(tmp_path) -> None:
    """The Round 1 gap was here, and nothing committed exercised it.

    The inertness guard used to select one `\n\n` block — the first — so the
    scarcity paragraph was unguarded and a plugin name or a gate marker could
    be added to it with every test green. The guard now spans the whole
    passage, but until this probe existed, narrowing it back would have left
    all nine probes passing. The fix and the evidence for the fix are not the
    same artifact.
    """
    root = _review_sandbox(tmp_path)
    md = root / REVIEW_SKILL
    text = md.read_text(encoding="utf-8")
    mutated = text.replace(
        "Almost nothing qualifies. Most of what a review surfaces",
        "<!-- gate: review.record -->\nAlmost nothing qualifies. Invoke the "
        "loom-workflow loom-memory skill. Most of what a review surfaces",
    )
    assert mutated != text, "probe anchor missing in the scarcity paragraph"
    md.write_text(mutated, encoding="utf-8")

    result = _run(root, REVIEW_TEST)
    assert result.returncode != 0, (
        "a gate marker and a plugin invocation were added to the scarcity "
        f"paragraph and every test stayed green:\n{result.stdout}{result.stderr}"
    )


def test_widening_an_assertion_to_the_whole_station_file_is_caught(tmp_path) -> None:
    """The defect this episode kept producing, in probe form.

    `functional content` occurs four times in the station text outside the
    passage. Asserted against the whole file, the test passed while the
    sentence it names was deleted — found by mutation in Round 2, in a test
    written by the commit that had just fixed the same defect elsewhere.
    Replace the passage's sentence and the scoped assertion must red.
    """
    root = _review_sandbox(tmp_path)
    md = root / REVIEW_SKILL
    text = md.read_text(encoding="utf-8")
    mutated = text.replace(
        "A recorded lesson is functional content like anything else committed",
        "A recorded lesson is an ordinary commit",
    )
    assert mutated != text, "probe anchor missing"
    md.write_text(mutated, encoding="utf-8")

    node = "::test_convergence_forbids_spending_an_extra_digest_on_a_lesson"
    result = _run(root, REVIEW_TEST, node)
    assert result.returncode != 0, (
        "the passage's sentence was replaced and the assertion stayed green — "
        "it is reading the whole station file again:\n"
        f"{result.stdout}{result.stderr}"
    )
