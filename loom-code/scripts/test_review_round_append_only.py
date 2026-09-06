"""Permanent tests for the `review.round-append-only` rule and its
`loom_checker.py review-edits <change-id>` sub-command (W1-03).

These are written independently of the adversary's RED probes at
docs/loom/2026-09-05-artifact-charter-boundaries-and-edit-rights/evidence/
probes/test_abuse_review_edits.py -- same interface, different fixtures --
so the rule stays covered once that evidence file is archived.
"""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

CHECKER = Path(__file__).resolve().parent / "loom_checker.py"
CHANGE_ID = "2099-03-03-permanent-review-edits-check"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def run_review_edits(repo: Path, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), "review-edits", CHANGE_ID],
        capture_output=True, text=True, env=env, cwd=str(repo),
    )


def review_path(repo: Path) -> Path:
    return repo / "docs" / "loom" / CHANGE_ID / "review.json"


def base_review_doc(*, charter: str | None = "1.0") -> dict[str, Any]:
    doc: dict[str, Any] = {
        "reviewed_sha": "1111111a",
        "scope": "wave-end:1",
        "vendors": ["anthropic"],
        "verdicts": [
            {
                "reviewer": "r1", "vendor": "anthropic", "model": "sonnet",
                "lens": "code", "scope": "wave-end:1", "round": 1,
                "verdict": "PASS", "dimension_scores": {"tests": 5}, "findings": [],
                "sha": "1111111a",
            }
        ],
        "probes": [
            {
                "kind": "package-tests", "command": "pytest -q",
                "sha": "1111111a", "result": "pass", "artifact": "tests/test_z.py",
            }
        ],
        "questions": [],
        "open_findings": [
            {"id": "g1", "anchor": "z.py:1", "origin_sha": "1111111a", "raised_by": "r1"}
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
    git(repo, "config", "user.email", "perm@example.com")
    git(repo, "config", "user.name", "Permanent")
    return repo


def write_and_commit(repo: Path, doc: dict[str, Any], message: str) -> str:
    path = review_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def blocked_rule_ids(result: subprocess.CompletedProcess) -> set[str]:
    return {
        line.split(":", 1)[0].removeprefix("BLOCK ").strip()
        for line in result.stderr.splitlines()
        if line.startswith("BLOCK ")
    }


def test_review_edits_missing_file_exits_two_with_no_data_read(tmp_path: Path) -> None:
    """A change-id with no review.json at all exits 2 -- never a silent 0
    or a rule BLOCK on data that does not exist."""
    repo = init_repo(tmp_path)
    git(repo, "commit", "-q", "--allow-empty", "-m", "chore: empty seed")
    result = run_review_edits(repo)
    assert result.returncode == 2


def test_review_edits_second_round_appends_only_exits_zero(tmp_path: Path) -> None:
    """A second round that appends one new verdict, probe, open finding
    and dispatch entry -- every earlier entry byte-for-byte unchanged --
    passes clean."""
    repo = init_repo(tmp_path)
    doc = base_review_doc()
    write_and_commit(repo, doc, "chore(loom): checkpoint review — round 1")
    doc2 = copy.deepcopy(doc)
    doc2["verdicts"].append({
        "reviewer": "r2", "vendor": "anthropic", "model": "opus",
        "lens": "code", "scope": "wave-end:1", "round": 2,
        "verdict": "PASS", "dimension_scores": {"tests": 5}, "findings": [],
        "sha": "2222222b",
    })
    doc2["probes"].append({
        "kind": "adversarial", "command": "pytest -q -k y", "sha": "2222222b",
        "result": "pass", "artifact": "tests/test_y_abuse.py",
    })
    doc2["open_findings"].append(
        {"id": "g2", "anchor": "z.py:9", "origin_sha": "2222222b", "raised_by": "r2"}
    )
    doc2["dispatch"].append({
        "task": "W2", "role": "reviewer", "agent_id": "r2",
        "model": "opus", "started": "2026-01-02T00:00:00Z", "fresh_context": True,
    })
    write_and_commit(repo, doc2, "chore(loom): checkpoint review — round 2")
    result = run_review_edits(repo)
    assert result.returncode == 0, result.stderr


def test_open_finding_null_resolution_can_gain_evidence(tmp_path: Path) -> None:
    """The review template represents an unresolved finding as null.

    Closing that placeholder with evidence is the same append-only action as
    adding an absent ``resolved`` key; rewriting non-null evidence remains
    forbidden by the existing immutable-resolution probes.
    """
    repo = init_repo(tmp_path)
    doc = base_review_doc()
    doc["open_findings"][0]["resolved"] = None
    write_and_commit(repo, doc, "chore(loom): checkpoint review — unresolved finding")
    doc2 = copy.deepcopy(doc)
    doc2["open_findings"][0]["resolved"] = "closed by abc1234 — regression covered"
    write_and_commit(repo, doc2, "chore(loom): checkpoint review — finding closed")

    result = run_review_edits(repo)

    assert result.returncode == 0, result.stderr


def _assert_sequential_double_close_blocks(
    tmp_path: Path, first_key: str, second_key: str
) -> None:
    repo = init_repo(tmp_path)
    doc = base_review_doc()
    doc["open_findings"][0][first_key] = "existing evidence by r1"
    doc["open_findings"][0][second_key] = None
    write_and_commit(repo, doc, "chore(loom): checkpoint review — finding already closed")
    doc2 = copy.deepcopy(doc)
    doc2["open_findings"][0][second_key] = "later evidence by r2"
    write_and_commit(repo, doc2, "chore(loom): checkpoint review — double close")

    result = run_review_edits(repo)

    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rule_ids(result)


def test_dismissed_finding_cannot_later_gain_resolution(tmp_path: Path) -> None:
    _assert_sequential_double_close_blocks(tmp_path, "dismissed", "resolved")


def test_resolved_finding_cannot_later_gain_dismissal(tmp_path: Path) -> None:
    _assert_sequential_double_close_blocks(tmp_path, "resolved", "dismissed")


def test_review_edits_ungrandfathered_verdict_flip_blocks_naming_rewrite(tmp_path: Path) -> None:
    """Once charter-stamped, flipping an earlier verdict's own `verdict`
    value is not an append -- must block naming "earlier round
    rewritten"."""
    repo = init_repo(tmp_path)
    doc = base_review_doc()
    doc["verdicts"][0]["verdict"] = "NEEDS_REVISION"
    write_and_commit(repo, doc, "chore(loom): checkpoint review — round 1")
    doc2 = copy.deepcopy(doc)
    doc2["verdicts"][0]["verdict"] = "PASS"
    write_and_commit(repo, doc2, "chore(loom): checkpoint review — quiet flip")
    result = run_review_edits(repo)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rule_ids(result)
    assert "earlier round rewritten" in result.stderr


def test_review_edits_no_charter_stamp_skips_a_rewritten_verdict(tmp_path: Path) -> None:
    """A pre-charter round (no top-level `charter` key) is skipped
    entirely -- grandfathered even when an earlier verdict is rewritten."""
    repo = init_repo(tmp_path)
    doc = base_review_doc(charter=None)
    doc["verdicts"][0]["verdict"] = "NEEDS_REVISION"
    write_and_commit(repo, doc, "chore(loom): checkpoint review — pre-charter round")
    doc2 = copy.deepcopy(doc)
    doc2["verdicts"][0]["verdict"] = "PASS"
    write_and_commit(repo, doc2, "chore(loom): checkpoint review — quiet flip, no charter")
    result = run_review_edits(repo)
    assert result.returncode == 0, result.stderr


def test_review_edits_working_tree_edit_after_commit_blocks(tmp_path: Path) -> None:
    """An uncommitted working-tree rewrite of an earlier open finding's
    `anchor` (not its resolved/dismissed key) is checked the same as a
    committed pair and must block."""
    repo = init_repo(tmp_path)
    doc = base_review_doc()
    write_and_commit(repo, doc, "chore(loom): checkpoint review — round 1")
    doc2 = copy.deepcopy(doc)
    doc2["open_findings"][0]["anchor"] = "z.py:999"
    review_path(repo).write_text(json.dumps(doc2, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = run_review_edits(repo)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rule_ids(result)


def test_review_edits_second_vendor_set_once_then_immutable(tmp_path: Path) -> None:
    """`second_vendor` moving from absent to a value passes once; a
    further commit changing it again must block."""
    repo = init_repo(tmp_path)
    doc = base_review_doc()
    write_and_commit(repo, doc, "chore(loom): checkpoint review — round 1")
    doc2 = copy.deepcopy(doc)
    doc2["second_vendor"] = "codex"
    write_and_commit(repo, doc2, "chore(loom): checkpoint review — record second vendor")
    result = run_review_edits(repo)
    assert result.returncode == 0, result.stderr

    doc3 = copy.deepcopy(doc2)
    doc3["second_vendor"] = "gemini"
    write_and_commit(repo, doc3, "chore(loom): checkpoint review — quietly swap second vendor")
    result = run_review_edits(repo)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rule_ids(result)


def test_review_edits_charter_stamp_changed_blocks(tmp_path: Path) -> None:
    """The `charter` stamp itself is immutable once present -- changing
    its value between two committed rounds must block, naming "charter
    stamp changed", never treated as a replaceable field."""
    repo = init_repo(tmp_path)
    doc = base_review_doc()
    write_and_commit(repo, doc, "chore(loom): checkpoint review — round 1")
    doc2 = copy.deepcopy(doc)
    doc2["charter"] = "2.0"
    write_and_commit(repo, doc2, "chore(loom): checkpoint review — quietly bump charter")
    result = run_review_edits(repo)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rule_ids(result)
    assert "charter stamp changed" in result.stderr


def test_review_edits_verdicts_replaced_by_object_blocks_array_type_changed(tmp_path: Path) -> None:
    """`verdicts` turning from a list into an object between two committed
    rounds is neither a shrink nor a gain -- the exhaustive comparison
    must block it as an array type change, never silently skip it
    because one side is no longer a list."""
    repo = init_repo(tmp_path)
    doc = base_review_doc()
    write_and_commit(repo, doc, "chore(loom): checkpoint review — round 1")
    doc2 = copy.deepcopy(doc)
    doc2["verdicts"] = {"reviewer": "r1", "verdict": "PASS"}
    write_and_commit(
        repo, doc2, "chore(loom): checkpoint review — quietly replace verdicts with an object"
    )
    result = run_review_edits(repo)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rule_ids(result)
    assert "array type changed" in result.stderr


def test_review_edits_reviewed_sha_changed_with_replace_policy_removed_blocks(tmp_path: Path) -> None:
    """`load_manifest()` always resolves the real
    loom-code/contract/manifest.yaml, never a path this test's own tmp
    repo could redirect (mirroring the adversary's
    test_review_edits_unsupported_policy_id_blocks_closed), so this test
    patches that manifest on disk to drop
    `reviewed-sha-scope-cost-replaced` from the review charter's
    edits_after, then checks that quietly moving `reviewed_sha` between
    two committed rounds blocks with the replace policy gone."""
    manifest_path = CHECKER.parent.parent / "contract" / "manifest.yaml"
    original = manifest_path.read_text(encoding="utf-8")
    line = (
        '        - {id: reviewed-sha-scope-cost-replaced,                '
        'text: "reviewed_sha, scope and cost are replaced"}\n'
    )
    assert line in original, "expected edits_after line not found in manifest.yaml"
    patched = original.replace(line, "")
    assert patched != original
    repo = init_repo(tmp_path)
    doc = base_review_doc()
    write_and_commit(repo, doc, "chore(loom): checkpoint review — round 1")
    doc2 = copy.deepcopy(doc)
    doc2["reviewed_sha"] = "2222222b"
    write_and_commit(repo, doc2, "chore(loom): checkpoint review — quietly move reviewed_sha")
    scratch = tmp_path / "manifest.yaml"
    scratch.write_text(patched, encoding="utf-8")
    result = run_review_edits(repo, env={**os.environ, "LOOM_MANIFEST_PATH": str(scratch)})
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rule_ids(result)


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))


def test_review_edits_vendors_gains_entry_with_policy_passes(tmp_path: Path) -> None:
    """A second vendor joining at a later round is an accretion the review
    charter names by its own id (`vendors-gain-entries`): with the id
    declared, a round whose vendors list grows by one entry passes."""
    repo = init_repo(tmp_path)
    doc = base_review_doc()
    doc["vendors"] = ["anthropic"]
    write_and_commit(repo, doc, "chore(loom): checkpoint review — round 1")
    doc2 = copy.deepcopy(doc)
    doc2["vendors"] = ["anthropic", "openai"]
    write_and_commit(repo, doc2, "chore(loom): checkpoint review — round 2 adds a vendor")
    result = run_review_edits(repo)
    assert result.returncode == 0, result.stderr


def test_review_edits_vendors_gains_entry_with_policy_removed_blocks(tmp_path: Path) -> None:
    """Drop the `vendors-gain-entries` id from the real manifest for the
    duration of the run: a vendors list that grows between two rounds then
    blocks, so vendors rides on its own allowance and never on the four
    other arrays' id."""
    manifest_path = CHECKER.parent.parent / "contract" / "manifest.yaml"
    original = manifest_path.read_text(encoding="utf-8")
    line = next(l for l in original.splitlines(keepends=True) if "id: vendors-gain-entries" in l)
    repo = init_repo(tmp_path)
    doc = base_review_doc()
    doc["vendors"] = ["anthropic"]
    write_and_commit(repo, doc, "chore(loom): checkpoint review — round 1")
    doc2 = copy.deepcopy(doc)
    doc2["vendors"] = ["anthropic", "openai"]
    write_and_commit(repo, doc2, "chore(loom): checkpoint review — round 2 adds a vendor")
    scratch = tmp_path / "manifest.yaml"
    scratch.write_text(original.replace(line, ""), encoding="utf-8")
    result = run_review_edits(repo, env={**os.environ, "LOOM_MANIFEST_PATH": str(scratch)})
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rule_ids(result)
    assert "vendors" in result.stderr


def test_review_edits_reviewed_sha_replaced_by_list_blocks_even_with_policy(tmp_path: Path) -> None:
    """wave-end:2-01: the replace-set policy allows `reviewed_sha` to take a
    NEW value, never a new TYPE. Swapping the string for a two-item list
    between two committed rounds must block naming "replace-set type
    changed", even though `reviewed-sha-scope-cost-replaced` is enabled."""
    repo = init_repo(tmp_path)
    doc = base_review_doc()
    write_and_commit(repo, doc, "chore(loom): checkpoint review — round 1")
    doc2 = copy.deepcopy(doc)
    doc2["reviewed_sha"] = ["1111111a", "2222222b"]
    write_and_commit(
        repo, doc2, "chore(loom): checkpoint review — quietly retype reviewed_sha"
    )
    result = run_review_edits(repo)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rule_ids(result)
    assert "replace-set type changed" in result.stderr
    assert "reviewed_sha" in result.stderr


def test_review_edits_cost_replaced_by_list_blocks_even_with_policy(tmp_path: Path) -> None:
    """wave-end:2-01: `cost` must stay a mapping across a replace; swapping
    it for a list between two committed rounds blocks the same way, even
    with the replace policy enabled."""
    repo = init_repo(tmp_path)
    doc = base_review_doc()
    write_and_commit(repo, doc, "chore(loom): checkpoint review — round 1")
    doc2 = copy.deepcopy(doc)
    doc2["cost"] = ["rounds", 1]
    write_and_commit(
        repo, doc2, "chore(loom): checkpoint review — quietly retype cost"
    )
    result = run_review_edits(repo)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rule_ids(result)
    assert "replace-set type changed" in result.stderr
    assert "cost" in result.stderr


def test_review_edits_reviewed_sha_string_to_string_replacement_passes(tmp_path: Path) -> None:
    """A same-type replacement (string to string) is exactly what the
    replace-set policy is for -- it must still pass once the type guard
    lands, not just before it."""
    repo = init_repo(tmp_path)
    doc = base_review_doc()
    write_and_commit(repo, doc, "chore(loom): checkpoint review — round 1")
    doc2 = copy.deepcopy(doc)
    doc2["reviewed_sha"] = "2222222b"
    write_and_commit(
        repo, doc2, "chore(loom): checkpoint review — move reviewed_sha forward"
    )
    result = run_review_edits(repo)
    assert result.returncode == 0, result.stderr


def test_review_edits_questions_gain_a_decision_point_entry_passes(tmp_path: Path) -> None:
    """The ship station appends one `questions[]` entry per decision-point-3
    question, into the review-only commit it amends (ship §2-§3), and the
    review station copies decision-point-1 questions in at the first
    checkpoint: `questions` accretes like `verdicts` does. The charter names
    that by its own id (`questions-gain-entries`): a later round whose
    questions list is the earlier list plus new entries passes."""
    repo = init_repo(tmp_path)
    doc = base_review_doc()
    doc["questions"] = [{"decision_point": 1, "text": "Is this what you want?", "type": "what"}]
    write_and_commit(repo, doc, "chore(loom): checkpoint review — round 1")
    doc2 = copy.deepcopy(doc)
    doc2["questions"].append({"decision_point": 3, "text": "Line 1 works as shown — OK?", "type": "done"})
    write_and_commit(repo, doc2, "chore(loom): checkpoint review — branch-end, decision point 3 recorded")
    result = run_review_edits(repo)
    assert result.returncode == 0, result.stderr


def test_review_edits_questions_earlier_entry_rewritten_blocks(tmp_path: Path) -> None:
    """Gaining entries is the whole allowance: an earlier question rewritten
    in place, or dropped, is a changed record of what the user was asked and
    blocks under `review.round-append-only` naming `questions`."""
    repo = init_repo(tmp_path)
    doc = base_review_doc()
    doc["questions"] = [
        {"decision_point": 1, "text": "Is this what you want?", "type": "what"},
        {"decision_point": 1, "text": "Use Codex as a second reader?", "type": "what"},
    ]
    write_and_commit(repo, doc, "chore(loom): checkpoint review — round 1")
    doc2 = copy.deepcopy(doc)
    doc2["questions"][1]["text"] = "Use Codex as the only reader?"
    write_and_commit(repo, doc2, "chore(loom): checkpoint review — round 2 rewrites a question")
    result = run_review_edits(repo)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rule_ids(result)
    assert "questions" in result.stderr

    doc3 = copy.deepcopy(doc)
    doc3["questions"] = doc3["questions"][:1]
    write_and_commit(repo, doc3, "chore(loom): checkpoint review — round 3 drops a question")
    result = run_review_edits(repo)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rule_ids(result)
