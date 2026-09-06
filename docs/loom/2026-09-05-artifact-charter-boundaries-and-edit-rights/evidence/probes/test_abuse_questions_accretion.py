"""Adversarial probes against the `questions-gain-entries` branch of
`review.round-append-only` (loom-code/scripts/loom_checker.py,
`_compare_review_round`, function containing `allow_questions_gain`),
landed at 8805d3a4. The charter's edits_after policy id changed from
`questions-written-once` to `questions-gain-entries`: the earlier
`questions` list must be a byte-equal prefix of the later one; anything
else must block naming `questions`.

These probes attack the accretion check itself, not the design: a
middle insertion, a prepended entry, a reorder, a combined
append-plus-mutate, a type swap, a duplicated entry, a fail-closed
check with the policy id removed from a scratch manifest, and a
grandfathered (no-charter) round.

Each test is independently re-runnable from the repo root:
    python3 -m pytest docs/loom/2026-09-05-artifact-charter-boundaries-and-edit-rights/evidence/probes/test_abuse_questions_accretion.py -q -k <name>
"""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[5]
CHECKER = REPO / "loom-code" / "scripts" / "loom_checker.py"
CHANGE_ID = "2099-05-05-abuse-questions-accretion"

QUESTIONS_GAIN_LINE = (
    '        - {id: questions-gain-entries,                          '
    'text: "questions gains entries, one per decision-point question asked; '
    'earlier entries unchanged"}\n'
)


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def run_review_edits(repo: Path, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), "review-edits", CHANGE_ID],
        capture_output=True, text=True, env=env, cwd=str(repo),
    )


def blocked_rule_ids(result: subprocess.CompletedProcess) -> set[str]:
    return {
        line.split(":", 1)[0].removeprefix("BLOCK ").strip()
        for line in result.stderr.splitlines()
        if line.startswith("BLOCK ")
    }


def review_path(repo: Path) -> Path:
    return repo / "docs" / "loom" / CHANGE_ID / "review.json"


def base_review_doc(*, charter: str | None = "1.0", questions: list | None = None) -> dict[str, Any]:
    doc: dict[str, Any] = {
        "reviewed_sha": "aaaaaaa1",
        "scope": "wave-end:1",
        "vendors": ["anthropic"],
        "verdicts": [
            {
                "reviewer": "r1", "vendor": "anthropic", "model": "sonnet",
                "lens": "code", "scope": "wave-end:1", "round": 1,
                "verdict": "PASS", "dimension_scores": {"tests": 5}, "findings": [],
                "sha": "aaaaaaa1",
            }
        ],
        "probes": [
            {
                "kind": "package-tests", "command": "pytest -q",
                "sha": "aaaaaaa1", "result": "pass", "artifact": "tests/test_z.py",
            }
        ],
        "questions": list(questions) if questions is not None else [],
        "open_findings": [
            {"id": "g1", "anchor": "z.py:1", "origin_sha": "aaaaaaa1", "raised_by": "r1"}
        ],
        "dispatch": [
            {
                "task": "W1", "role": "implementer", "agent_id": "i1",
                "model": "sonnet", "started": "2026-01-01T00:00:00Z", "fresh_context": True,
            }
        ],
        "cost": {"rounds": 1, "dispatches": 1, "cap_changes": [], "hours_plan_to_pr": None},
    }
    if charter is not None:
        doc["charter"] = charter
    return doc


def init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "adv@example.com")
    git(repo, "config", "user.name", "Adversary")
    return repo


def write_and_commit(repo: Path, doc: dict[str, Any], message: str) -> str:
    path = review_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


Q1 = {"decision_point": 1, "text": "Is this what you want?", "type": "what"}
Q2 = {"decision_point": 1, "text": "Use Codex as a second reader?", "type": "what"}
Q3 = {"decision_point": 3, "text": "Line 1 works as shown — OK?", "type": "done"}


# ---------------------------------------------------------------------------
# Abuse cases -- must all BLOCK.
# ---------------------------------------------------------------------------


def test_questions_accretion_middle_insertion_blocks_as_changed(tmp_path: Path) -> None:
    """Inserting a new entry in the MIDDLE of `questions` (list grows by
    one, but the earlier list is no longer a prefix) must block naming
    `questions` -- growth alone is not enough, the shared prefix must be
    byte-equal."""
    repo = init_repo(tmp_path)
    doc = base_review_doc(questions=[Q1, Q3])
    write_and_commit(repo, doc, "chore(loom): checkpoint review — round 1")
    doc2 = copy.deepcopy(doc)
    doc2["questions"] = [Q1, Q2, Q3]  # Q2 inserted between Q1 and Q3
    write_and_commit(repo, doc2, "chore(loom): checkpoint review — quietly insert mid-list")
    result = run_review_edits(repo)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rule_ids(result)
    assert "questions" in result.stderr


def test_questions_accretion_prepended_entry_blocks_as_changed(tmp_path: Path) -> None:
    """Prepending a new entry ahead of the existing list (list grows by
    one, existing entries shift index) must block -- the earlier list is
    no longer a prefix of the later one even though every original entry
    still appears verbatim."""
    repo = init_repo(tmp_path)
    doc = base_review_doc(questions=[Q1])
    write_and_commit(repo, doc, "chore(loom): checkpoint review — round 1")
    doc2 = copy.deepcopy(doc)
    doc2["questions"] = [Q3, Q1]
    write_and_commit(repo, doc2, "chore(loom): checkpoint review — quietly prepend a question")
    result = run_review_edits(repo)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rule_ids(result)
    assert "questions" in result.stderr


def test_questions_accretion_reordered_same_entries_blocks_as_changed(tmp_path: Path) -> None:
    """Swapping the order of two existing entries (same length, same set
    of entries, different order) is not an append and must block --
    order carries meaning (what was asked first) that a set-equality
    check would silently discard."""
    repo = init_repo(tmp_path)
    doc = base_review_doc(questions=[Q1, Q2])
    write_and_commit(repo, doc, "chore(loom): checkpoint review — round 1")
    doc2 = copy.deepcopy(doc)
    doc2["questions"] = [Q2, Q1]
    write_and_commit(repo, doc2, "chore(loom): checkpoint review — quietly reorder questions")
    result = run_review_edits(repo)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rule_ids(result)
    assert "questions" in result.stderr


def test_questions_accretion_append_and_mutate_earlier_same_commit_blocks(tmp_path: Path) -> None:
    """A commit that both appends a legitimate new entry AND rewrites an
    earlier entry in the same breath must still block -- gaining an
    entry never grandfathers a simultaneous mutation elsewhere in the
    list."""
    repo = init_repo(tmp_path)
    doc = base_review_doc(questions=[Q1])
    write_and_commit(repo, doc, "chore(loom): checkpoint review — round 1")
    doc2 = copy.deepcopy(doc)
    doc2["questions"][0] = dict(Q1, text="a quietly rewritten first question")
    doc2["questions"].append(Q3)
    write_and_commit(repo, doc2, "chore(loom): checkpoint review — append plus mutate")
    result = run_review_edits(repo)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rule_ids(result)
    assert "questions" in result.stderr


def test_questions_accretion_list_replaced_by_dict_blocks_as_changed(tmp_path: Path) -> None:
    """`questions` retyped from a list to a mapping between two committed
    rounds is neither empty growth nor a prefix relationship -- it must
    block, never silently pass because the isinstance(list) guard makes
    `grown` False."""
    repo = init_repo(tmp_path)
    doc = base_review_doc(questions=[Q1])
    write_and_commit(repo, doc, "chore(loom): checkpoint review — round 1")
    doc2 = copy.deepcopy(doc)
    doc2["questions"] = {"decision_point": 1, "text": "smuggled as an object"}
    write_and_commit(repo, doc2, "chore(loom): checkpoint review — quietly retype questions")
    result = run_review_edits(repo)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rule_ids(result)
    assert "questions" in result.stderr


def test_questions_accretion_policy_id_removed_blocks_pure_append(tmp_path: Path) -> None:
    """Fail-closed check: with `questions-gain-entries` stripped from a
    scratch copy of the manifest, a PURE append (previously the
    textbook-legitimate case) must now block -- the allowance is not a
    checker-side default, it lives entirely in the charter's declared
    policy id."""
    manifest_path = REPO / "loom-code" / "contract" / "manifest.yaml"
    original = manifest_path.read_text(encoding="utf-8")
    assert QUESTIONS_GAIN_LINE in original, "expected edits_after line not found in manifest.yaml"
    patched = original.replace(QUESTIONS_GAIN_LINE, "")
    assert patched != original

    repo = init_repo(tmp_path)
    doc = base_review_doc(questions=[Q1])
    write_and_commit(repo, doc, "chore(loom): checkpoint review — round 1")
    doc2 = copy.deepcopy(doc)
    doc2["questions"].append(Q3)
    write_and_commit(repo, doc2, "chore(loom): checkpoint review — pure append, policy removed")

    scratch = tmp_path / "manifest.yaml"
    scratch.write_text(patched, encoding="utf-8")
    result = run_review_edits(repo, env={**os.environ, "LOOM_MANIFEST_PATH": str(scratch)})
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rule_ids(result)
    assert "questions" in result.stderr


def test_questions_accretion_grandfathered_round_skips_rewritten_question(tmp_path: Path) -> None:
    """A round with no top-level `charter` key is grandfathered entirely
    (per `_compare_review_round`'s own early return): an earlier round's
    `questions` list rewritten wholesale between two commits, neither of
    which carries `charter`, must pass clean -- the accretion check never
    even runs."""
    repo = init_repo(tmp_path)
    doc = base_review_doc(charter=None, questions=[Q1, Q2])
    write_and_commit(repo, doc, "chore(loom): checkpoint review — pre-charter round")
    doc2 = copy.deepcopy(doc)
    doc2["questions"] = [Q3]  # both entries dropped, one unrelated entry substituted
    write_and_commit(repo, doc2, "chore(loom): checkpoint review — quietly rewrite, no charter")
    result = run_review_edits(repo)
    assert result.returncode == 0, result.stderr


# ---------------------------------------------------------------------------
# Boundary cases documenting behaviour that is not a defect -- still run
# and pinned so a future regression in either direction is caught.
# ---------------------------------------------------------------------------


def test_questions_accretion_duplicate_entry_appended_passes(tmp_path: Path) -> None:
    """Appending a byte-identical duplicate of an already-present entry is
    still a valid prefix relationship (the earlier list unchanged, one
    more entry tacked on) -- the accretion check imposes no uniqueness
    requirement on `questions`, so this passes. Documented here as a
    boundary rather than assumed: uniqueness of questions is out of this
    rule's charter and is not this rule's job to enforce."""
    repo = init_repo(tmp_path)
    doc = base_review_doc(questions=[Q1])
    write_and_commit(repo, doc, "chore(loom): checkpoint review — round 1")
    doc2 = copy.deepcopy(doc)
    doc2["questions"].append(dict(Q1))
    write_and_commit(repo, doc2, "chore(loom): checkpoint review — duplicate entry appended")
    result = run_review_edits(repo)
    assert result.returncode == 0, result.stderr


def test_questions_accretion_appended_entry_missing_type_field_passes(tmp_path: Path) -> None:
    """An appended `questions` entry missing its `type` field is still a
    byte-equal-prefix-preserving growth from `review.round-append-only`'s
    own point of view -- this rule does not validate entry schema (that
    is push.review-schema's job), so it passes here. Pinned so a future
    change does not silently fold schema validation into this rule (or
    vice versa) without a visible test failure."""
    repo = init_repo(tmp_path)
    doc = base_review_doc(questions=[Q1])
    write_and_commit(repo, doc, "chore(loom): checkpoint review — round 1")
    doc2 = copy.deepcopy(doc)
    schemaless_entry = {"decision_point": 3, "text": "Line 1 works as shown — OK?"}
    doc2["questions"].append(schemaless_entry)
    write_and_commit(repo, doc2, "chore(loom): checkpoint review — append entry missing type")
    result = run_review_edits(repo)
    assert result.returncode == 0, result.stderr


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
