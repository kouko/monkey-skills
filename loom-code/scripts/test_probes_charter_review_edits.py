"""Adversarial probes for W1-03 (review.json round-append-only) of
2026-09-05-artifact-charter-boundaries-and-edit-rights -- written BEFORE the
implementer, against `loom_checker.py review-edits <change-id>` and the new
`review.round-append-only` rule described in the plan's W1-03 task line.

None of this exists yet at the commit these probes were written against
(HEAD 16cbb2e4): there is no `review-edits` sub-command and no
`review.round-append-only` rule in `RULES` (`--list-rules` prints 30 lines
today, none of them this id). Every test below that expects the finished
behaviour (exit 0 on an allowed accretion, exit 1 naming the rule on a
disallowed rewrite) is expected to FAIL today, because `review-edits` is an
unknown sub-command and exits 2 with "unknown sub-command 'review-edits'."
regardless of the review.json content -- that is the implementer's RED.
Turning every one of these green, without weakening any assertion here, is
the acceptance bar for W1-03.

Each test is independently re-runnable from the repo root:
    python3 -m pytest docs/loom/2026-09-05-artifact-charter-boundaries-and-edit-rights/evidence/probes/test_abuse_review_edits.py -q -k <name>

Interface pins (the W1-03 task line and dispatch prompt left these to the
adversary to nail down first; each is also a `findings` entry in the
report, not a silent guess):
  - the sub-command is `review-edits <change-id>`, run with cwd at the
    repo root, mirroring `plan-edits` (test_abuse_plan_edits.py);
  - the policy ids read from `manifest.artifacts.review.charter.
    edits_after` are: `verdicts-probes-findings-dispatch-gain-entries`,
    `reviewed-sha-scope-cost-replaced`, `open-finding-resolved-or-
    dismissed-in-place`, `questions-written-once` (read from
    loom-code/contract/manifest.yaml at dispatch time -- a fifth id,
    `second-vendor-set-once`, was added to the manifest mid-round; see
    the findings below);
  - a round with no top-level `charter` key is skipped entirely
    (grandfathering), even when an earlier verdict is rewritten;
  - missing review.json exits 2; an unsupported policy id in the
    manifest's review row blocks closed, mirroring `plan-edits`;
  - a rewritten earlier verdict blocks with the literal wording "earlier
    round rewritten", regardless of which field of the verdict changed.
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

REPO = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
)

CHECKER = REPO / "loom-code" / "scripts" / "loom_checker.py"

THIS_CHANGE_ID = "2026-09-05-artifact-charter-boundaries-and-edit-rights"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def run_checker(*args: str, cwd: Path, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args], capture_output=True, text=True, env=env, cwd=str(cwd)
    )


def run_review_edits(repo: Path, change_id: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return run_checker("review-edits", change_id, cwd=repo, env=env)


def blocked_rules(result: subprocess.CompletedProcess) -> set[str]:
    return {
        line.split(":", 1)[0].removeprefix("BLOCK ").strip()
        for line in result.stderr.splitlines()
        if line.startswith("BLOCK ")
    }


CHANGE_ID = "2099-01-01-probe-review-edits"


def _review_path(repo: Path) -> Path:
    return repo / "docs" / "loom" / CHANGE_ID / "review.json"


def _base_review(*, charter: str | None = "1.0") -> dict[str, Any]:
    """A minimal but shape-complete review.json (every field the manifest's
    review artifact `must` list requires), matching
    loom-code/contract/templates/review.json's schema with concrete
    (rather than placeholder) sample values."""
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
                "kind": "adversarial", "command": "pytest -q -k x",
                "sha": "aaaaaaa1", "result": "fail",
                "artifact": "docs/loom/2099-01-01-probe-review-edits/evidence/probes/x.py",
            }
        ],
        "questions": [],
        "open_findings": [
            {
                "id": "f1", "anchor": "a.py:1", "origin_sha": "aaaaaaa1",
                "raised_by": "r1",
            }
        ],
        "dispatch": [
            {
                "task": "W1-01", "role": "implementer", "agent_id": "i1",
                "model": "sonnet", "started": "2026-01-01T00:00:00Z",
                "fresh_context": True,
            }
        ],
        "cost": {"rounds": 1, "dispatches": 1, "cap_changes": [], "hours_plan_to_pr": None},
    }
    if charter is not None:
        doc["charter"] = charter
    return doc


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "adv@example.com")
    git(repo, "config", "user.name", "Adversary")
    return repo


def _write_review(repo: Path, doc: dict[str, Any]) -> None:
    path = _review_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _seed_review_commit(repo: Path, doc: dict[str, Any], message: str = "chore(loom): checkpoint review — seed") -> str:
    _write_review(repo, doc)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def _commit_review_edit(repo: Path, doc: dict[str, Any], message: str) -> str:
    _write_review(repo, doc)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


# ---------------------------------------------------------------------------
# Allowed accretions -- must all pass (exit 0).
# ---------------------------------------------------------------------------


def test_review_edits_two_commits_pure_appends_passes(tmp_path: Path) -> None:
    """A second commit that only appends a new verdict, a new probe, a new
    open finding and a new dispatch entry -- every pre-existing entry
    byte-for-byte unchanged -- is an allowed accretion."""
    repo = _init_repo(tmp_path)
    doc = _base_review()
    _seed_review_commit(repo, doc)
    doc2 = copy.deepcopy(doc)
    doc2["verdicts"].append({
        "reviewer": "r2", "vendor": "anthropic", "model": "opus",
        "lens": "code", "scope": "wave-end:1", "round": 2,
        "verdict": "PASS_WITH_NOTES", "dimension_scores": {"tests": 4}, "findings": [],
        "sha": "bbbbbbb2",
    })
    doc2["probes"].append({
        "kind": "package-tests", "command": "pytest -q", "sha": "bbbbbbb2",
        "result": "pass", "artifact": "tests/test_y.py",
    })
    doc2["open_findings"].append({
        "id": "f2", "anchor": "b.py:2", "origin_sha": "bbbbbbb2", "raised_by": "r2",
    })
    doc2["dispatch"].append({
        "task": "W1-02", "role": "reviewer", "agent_id": "r2",
        "model": "opus", "started": "2026-01-02T00:00:00Z", "fresh_context": True,
    })
    _commit_review_edit(repo, doc2, "chore(loom): checkpoint review — round 2")
    result = run_review_edits(repo, CHANGE_ID)
    assert result.returncode == 0, result.stderr


def test_review_edits_reviewed_sha_and_scope_replaced_passes(tmp_path: Path) -> None:
    """`reviewed_sha` and `scope` may both be replaced wholesale between
    rounds -- the charter names both as replaceable together."""
    repo = _init_repo(tmp_path)
    doc = _base_review()
    _seed_review_commit(repo, doc)
    doc2 = copy.deepcopy(doc)
    doc2["reviewed_sha"] = "ccccccc3"
    doc2["scope"] = "branch-end"
    doc2["verdicts"][0]["sha"] = "ccccccc3"
    _commit_review_edit(repo, doc2, "chore(loom): checkpoint review — advance sha")
    result = run_review_edits(repo, CHANGE_ID)
    assert result.returncode == 0, result.stderr


def test_review_edits_cost_replaced_passes(tmp_path: Path) -> None:
    """`cost` is replaced wholesale every round (it is a running process
    tally, not an accreting log) -- must never block."""
    repo = _init_repo(tmp_path)
    doc = _base_review()
    _seed_review_commit(repo, doc)
    doc2 = copy.deepcopy(doc)
    doc2["cost"] = {"rounds": 2, "dispatches": 3, "cap_changes": ["wave-end raised"], "hours_plan_to_pr": 1.5}
    _commit_review_edit(repo, doc2, "chore(loom): checkpoint review — update cost")
    result = run_review_edits(repo, CHANGE_ID)
    assert result.returncode == 0, result.stderr


def test_review_edits_open_finding_gains_resolved_passes(tmp_path: Path) -> None:
    """An open finding gaining a `resolved` key in place, every other key
    on that entry unchanged, is an allowed edit."""
    repo = _init_repo(tmp_path)
    doc = _base_review()
    _seed_review_commit(repo, doc)
    doc2 = copy.deepcopy(doc)
    doc2["open_findings"][0]["resolved"] = "fixed in ccccccc3"
    _commit_review_edit(repo, doc2, "chore(loom): checkpoint review — resolve f1")
    result = run_review_edits(repo, CHANGE_ID)
    assert result.returncode == 0, result.stderr


def test_review_edits_questions_filled_once_passes(tmp_path: Path) -> None:
    """`questions` going from empty to non-empty exactly once is allowed."""
    repo = _init_repo(tmp_path)
    doc = _base_review()
    _seed_review_commit(repo, doc)
    doc2 = copy.deepcopy(doc)
    doc2["questions"] = [{"decision_point": 1, "text": "second vendor?", "type": "what"}]
    _commit_review_edit(repo, doc2, "chore(loom): checkpoint review — record question")
    result = run_review_edits(repo, CHANGE_ID)
    assert result.returncode == 0, result.stderr


def test_review_edits_no_charter_key_skips_even_with_rewritten_verdict(tmp_path: Path) -> None:
    """A review.json with no top-level `charter` key is skipped entirely --
    even an earlier verdict's `verdict` value flipped from NEEDS_REVISION
    to PASS, which would otherwise block, passes."""
    repo = _init_repo(tmp_path)
    doc = _base_review(charter=None)
    doc["verdicts"][0]["verdict"] = "NEEDS_REVISION"
    _seed_review_commit(repo, doc)
    doc2 = copy.deepcopy(doc)
    doc2["verdicts"][0]["verdict"] = "PASS"
    _commit_review_edit(repo, doc2, "chore(loom): checkpoint review — no charter stamp")
    result = run_review_edits(repo, CHANGE_ID)
    assert result.returncode == 0, result.stderr


# ---------------------------------------------------------------------------
# Disallowed rewrites -- must all block (exit 1, naming the rule).
# ---------------------------------------------------------------------------


def test_review_edits_earlier_verdict_value_changed_blocks_naming_rewrite(tmp_path: Path) -> None:
    """Flipping an EARLIER round's own `verdict` value (NEEDS_REVISION to
    PASS) is not an append -- it is rewriting history -- and must block
    naming the literal wording "earlier round rewritten"."""
    repo = _init_repo(tmp_path)
    doc = _base_review()
    doc["verdicts"][0]["verdict"] = "NEEDS_REVISION"
    _seed_review_commit(repo, doc)
    doc2 = copy.deepcopy(doc)
    doc2["verdicts"][0]["verdict"] = "PASS"
    _commit_review_edit(repo, doc2, "chore(loom): checkpoint review — quietly flip verdict")
    result = run_review_edits(repo, CHANGE_ID)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rules(result)
    assert "earlier round rewritten" in result.stderr


def test_review_edits_verdict_entry_deleted_blocks(tmp_path: Path) -> None:
    """Deleting an existing verdict entry outright (not appending, not
    resolving, just gone) must block -- append-only never means
    subtract-and-append is fine."""
    repo = _init_repo(tmp_path)
    doc = _base_review()
    doc["verdicts"].append({
        "reviewer": "r2", "vendor": "anthropic", "model": "opus",
        "lens": "code", "scope": "wave-end:1", "round": 1,
        "verdict": "PASS", "dimension_scores": {}, "findings": [], "sha": "aaaaaaa1",
    })
    _seed_review_commit(repo, doc)
    doc2 = copy.deepcopy(doc)
    doc2["verdicts"].pop(0)
    _commit_review_edit(repo, doc2, "chore(loom): checkpoint review — drop a verdict")
    result = run_review_edits(repo, CHANGE_ID)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rules(result)


def test_review_edits_open_finding_anchor_edited_blocks(tmp_path: Path) -> None:
    """The same finding gaining `resolved` is allowed (see the passing
    case above); editing its `anchor` in the same breath must still
    block -- `resolved`/`dismissed` are the only keys allowed to move."""
    repo = _init_repo(tmp_path)
    doc = _base_review()
    _seed_review_commit(repo, doc)
    doc2 = copy.deepcopy(doc)
    doc2["open_findings"][0]["resolved"] = "fixed"
    doc2["open_findings"][0]["anchor"] = "a.py:99"
    _commit_review_edit(repo, doc2, "chore(loom): checkpoint review — resolve and relocate f1")
    result = run_review_edits(repo, CHANGE_ID)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rules(result)


def test_review_edits_questions_filled_twice_blocks_on_second_change(tmp_path: Path) -> None:
    """`questions` may go from empty to non-empty once; a THIRD commit that
    changes the now-non-empty `questions` again must block -- immutable
    after the first fill, not merely append-preferred."""
    repo = _init_repo(tmp_path)
    doc = _base_review()
    _seed_review_commit(repo, doc)
    doc2 = copy.deepcopy(doc)
    doc2["questions"] = [{"decision_point": 1, "text": "second vendor?", "type": "what"}]
    _commit_review_edit(repo, doc2, "chore(loom): checkpoint review — record question")
    doc3 = copy.deepcopy(doc2)
    doc3["questions"][0]["text"] = "a rewritten question text"
    _commit_review_edit(repo, doc3, "chore(loom): checkpoint review — quietly reword question")
    result = run_review_edits(repo, CHANGE_ID)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rules(result)


def test_review_edits_top_level_key_removed_blocks(tmp_path: Path) -> None:
    """Removing a required top-level key (`dispatch`) outright must block
    -- the charter's `must` list names it required in every round."""
    repo = _init_repo(tmp_path)
    doc = _base_review()
    _seed_review_commit(repo, doc)
    doc2 = copy.deepcopy(doc)
    del doc2["dispatch"]
    _commit_review_edit(repo, doc2, "chore(loom): checkpoint review — drop dispatch entirely")
    result = run_review_edits(repo, CHANGE_ID)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rules(result)


def test_review_edits_unknown_top_level_key_added_blocks(tmp_path: Path) -> None:
    """Adding a top-level key the manifest schema never declared (a fresh
    field slipped in outside any charter allowance) must block."""
    repo = _init_repo(tmp_path)
    doc = _base_review()
    _seed_review_commit(repo, doc)
    doc2 = copy.deepcopy(doc)
    doc2["notes_to_self"] = "quietly smuggled prose the charter never named"
    _commit_review_edit(repo, doc2, "chore(loom): checkpoint review — add a notes field")
    result = run_review_edits(repo, CHANGE_ID)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rules(result)


def test_review_edits_probe_result_flipped_blocks_as_tampering(tmp_path: Path) -> None:
    """Flipping an existing probe's `result` from `fail` to `pass` without
    a new probe run is evidence tampering, not an accretion -- must
    block even though `probes` is an append-target array."""
    repo = _init_repo(tmp_path)
    doc = _base_review()
    _seed_review_commit(repo, doc)
    doc2 = copy.deepcopy(doc)
    doc2["probes"][0]["result"] = "pass"
    _commit_review_edit(repo, doc2, "chore(loom): checkpoint review — quietly flip probe result")
    result = run_review_edits(repo, CHANGE_ID)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rules(result)


def test_review_edits_dispatch_started_edited_blocks(tmp_path: Path) -> None:
    """Editing an existing dispatch entry's `started` timestamp must
    block -- the dispatch charter names existing entries never edited."""
    repo = _init_repo(tmp_path)
    doc = _base_review()
    _seed_review_commit(repo, doc)
    doc2 = copy.deepcopy(doc)
    doc2["dispatch"][0]["started"] = "2026-01-01T23:59:59Z"
    _commit_review_edit(repo, doc2, "chore(loom): checkpoint review — backdate dispatch")
    result = run_review_edits(repo, CHANGE_ID)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rules(result)


def test_review_edits_vendors_replaced_blocks(tmp_path: Path) -> None:
    """`vendors` carries no `edits_after` allowance in the manifest (only
    `reviewed_sha`, `scope` and `cost` are named replaceable) -- silently
    swapping it for a different vendor list must still block."""
    repo = _init_repo(tmp_path)
    doc = _base_review()
    _seed_review_commit(repo, doc)
    doc2 = copy.deepcopy(doc)
    doc2["vendors"] = ["openai"]
    _commit_review_edit(repo, doc2, "chore(loom): checkpoint review — swap vendor list")
    result = run_review_edits(repo, CHANGE_ID)
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rules(result)


# ---------------------------------------------------------------------------
# Absent/hostile input and CLI surface.
# ---------------------------------------------------------------------------


def test_review_edits_missing_review_file_exits_2(tmp_path: Path) -> None:
    """A change-id with no review.json at all exits 2 (usage/internal
    error), never a silent 0 or a rule BLOCK on data that doesn't exist."""
    repo = _init_repo(tmp_path)
    git(repo, "commit", "-q", "--allow-empty", "-m", "chore: empty seed")
    result = run_review_edits(repo, CHANGE_ID)
    assert result.returncode == 2


def test_review_edits_unsupported_policy_id_blocks_closed(tmp_path: Path) -> None:
    """An id on `manifest.artifacts.review.charter.edits_after` with no
    matching branch in the checker's implemented-ids set must fail
    closed -- mirroring `plan-edits`'s `IMPLEMENTED_EDITS_AFTER_IDS`
    contract (loom_checker.py:1791) -- rather than silently passing
    everything through. This probe patches a scratch copy of
    manifest.yaml with a bogus id and points the checker at it via cwd,
    since `load_manifest()` resolves the manifest relative to the
    checker script's own repo, not the tmp repo; it documents the
    expectation as a finding if the real implementation reads the
    manifest by a path this probe cannot redirect."""
    manifest_path = REPO / "loom-code" / "contract" / "manifest.yaml"
    original = manifest_path.read_text(encoding="utf-8")
    patched = original.replace(
        "        - {id: questions-written-once,                          text: \"questions is written once\"}\n",
        "        - {id: questions-written-once,                          text: \"questions is written once\"}\n"
        "        - {id: a-brand-new-unimplemented-policy-id,             text: \"a made-up policy id the checker cannot possibly implement yet\"}\n",
    )
    assert patched != original, "the manifest's review edits_after block did not match the expected text to patch"
    repo = _init_repo(tmp_path)
    doc = _base_review()
    _seed_review_commit(repo, doc)
    scratch = tmp_path / "manifest.yaml"
    scratch.write_text(patched, encoding="utf-8")
    result = run_review_edits(repo, CHANGE_ID, env={**os.environ, "LOOM_MANIFEST_PATH": str(scratch)})
    assert result.returncode == 1
    assert "review.round-append-only" in blocked_rules(result)
    assert "a-brand-new-unimplemented-policy-id" in result.stderr


def test_checker_list_rules_carries_review_round_append_only_at_31_lines() -> None:
    """`--list-rules` must grow by exactly this one id and print exactly
    31 lines once W1-03 lands."""
    result = run_checker("--list-rules", cwd=REPO)
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert result.returncode == 0, result.stderr
    assert "review.round-append-only" in {line.split("\t", 1)[0] for line in lines}
    assert len(lines) == 31, f"expected 31 rule lines, got {len(lines)}"


def test_review_edits_this_changes_own_history_passes(tmp_path: Path) -> None:
    """Pinned against the real repository, not a scratch one: this
    change's own docs/loom/<change-id>/review.json history, as it
    actually stands in git, must pass `review-edits` clean. If the real
    history does NOT pass once this rule exists, that is a genuine
    finding about this change's own review.json to report -- not a
    reason to soften this assertion."""
    result = run_review_edits(REPO, THIS_CHANGE_ID)
    assert result.returncode == 0, result.stderr


# ---------------------------------------------------------------------------
# Self-tests for this probe file's own scaffolding.
# ---------------------------------------------------------------------------


def test_base_review_fixture_matches_required_top_level_keys() -> None:
    """The fixture's shape actually covers every top-level key the
    manifest's review artifact `fields:` list requires, so a probe that
    passes here is not passing by accident of an incomplete fixture."""
    doc = _base_review()
    for key in ("reviewed_sha", "scope", "vendors", "verdicts", "probes",
                "open_findings", "dispatch", "cost", "charter"):
        assert key in doc
