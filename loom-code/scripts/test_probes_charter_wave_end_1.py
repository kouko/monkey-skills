"""Adversarial probes for wave-end:1 of
2026-09-05-artifact-charter-boundaries-and-edit-rights -- attacking what the
implementer's own tests (loom-code/scripts/test_review_round_append_only.py,
test_plan_edits_after_commit.py, test_plan_field_caps.py) and the earlier
adversary rounds (test_abuse_review_edits.py, test_abuse_plan_edits*.py,
test_abuse_field_caps.py, already green) did not cover: the sha-sync
exception's narrowness, double-key-gain on one open finding, editing an
already-set `dismissed` reason, `second_vendor` moving backwards, verdict
reordering, the old bare-string `edits_after` shape on both the review and
the plan charter, and the surface gap between `plan <path>` and
`plan-edits <change-id>`.

Every test below is written against the current tree (HEAD 10db4e06, where
all three rules already exist and pass their own suites) -- these are not
RED-before-GREEN probes for new behaviour, they are regression attacks on
already-shipped behaviour. A `pass` result records that the attack failed to
break anything; a `fail` result is a live bug.

Each test is independently re-runnable from the repo root:
    python3 -m pytest docs/loom/2026-09-05-artifact-charter-boundaries-and-edit-rights/evidence/probes/test_abuse_wave_end_1.py -q -k <name>
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
MANIFEST_PATH = REPO / "loom-code" / "contract" / "manifest.yaml"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def run_checker(*args: str, cwd: Path, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args], capture_output=True, text=True, env=env, cwd=str(cwd)
    )


def blocked_rules(result: subprocess.CompletedProcess) -> set[str]:
    return {
        line.split(":", 1)[0].removeprefix("BLOCK ").strip()
        for line in result.stderr.splitlines()
        if line.startswith("BLOCK ")
    }


def _init_repo(tmp_path: Path, name: str = "repo") -> Path:
    repo = tmp_path / name
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "adv@example.com")
    git(repo, "config", "user.name", "Adversary")
    return repo


# ---------------------------------------------------------------------------
# review.round-append-only (W1-03) -- gaps in the earlier adversary round
# ---------------------------------------------------------------------------

REVIEW_CHANGE_ID = "2099-02-02-wave-end-1-probe-review"


def _review_path(repo: Path, change_id: str = REVIEW_CHANGE_ID) -> Path:
    return repo / "docs" / "loom" / change_id / "review.json"


def _base_review(*, charter: str | None = "1.0") -> dict[str, Any]:
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
            },
            {
                "reviewer": "r2", "vendor": "anthropic", "model": "opus",
                "lens": "docs", "scope": "wave-end:1", "round": 1,
                "verdict": "PASS_WITH_NOTES", "dimension_scores": {"clarity": 4}, "findings": [],
                "sha": "aaaaaaa1",
            },
        ],
        "probes": [
            {
                "kind": "package-tests", "command": "pytest -q",
                "sha": "aaaaaaa1", "result": "pass", "artifact": "tests/test_z.py",
            }
        ],
        "questions": [],
        "open_findings": [
            {"id": "f1", "anchor": "a.py:1", "origin_sha": "aaaaaaa1", "raised_by": "r1"}
        ],
        "dispatch": [
            {
                "task": "W1-01", "role": "implementer", "agent_id": "i1",
                "model": "sonnet", "started": "2026-01-01T00:00:00Z", "fresh_context": True,
            }
        ],
        "cost": {"rounds": 1, "dispatches": 1, "cap_changes": [], "hours_plan_to_pr": None},
    }
    if charter is not None:
        doc["charter"] = charter
    return doc


def _write_review(repo: Path, doc: dict[str, Any], change_id: str = REVIEW_CHANGE_ID) -> None:
    path = _review_path(repo, change_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _commit_review(repo: Path, doc: dict[str, Any], message: str, change_id: str = REVIEW_CHANGE_ID) -> str:
    _write_review(repo, doc, change_id)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def run_review_edits(repo: Path, change_id: str = REVIEW_CHANGE_ID, env: dict | None = None) -> subprocess.CompletedProcess:
    return run_checker("review-edits", change_id, cwd=repo, env=env)


def test_verdict_sha_sync_exception_smuggled_second_field_change_blocks(tmp_path: Path) -> None:
    """The `reviewed-sha-scope-cost-replaced` exception lets a verdict's
    `sha` track a replaced `reviewed_sha` -- it must NOT also let a second
    field ride along under that same cover. Changing `verdict` from PASS to
    NEEDS_REVISION in the same edit that syncs `sha` must still block, naming
    the earlier round as rewritten."""
    repo = _init_repo(tmp_path)
    doc1 = _base_review()
    _commit_review(repo, doc1, "chore(loom): checkpoint review — seed")
    doc2 = copy.deepcopy(doc1)
    doc2["reviewed_sha"] = "bbbbbbb2"
    doc2["verdicts"][0]["sha"] = "bbbbbbb2"
    doc2["verdicts"][0]["verdict"] = "NEEDS_REVISION"
    _commit_review(repo, doc2, "chore(loom): checkpoint review — round 2 (smuggled verdict flip)")
    result = run_review_edits(repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "review.round-append-only" in blocked_rules(result)
    assert "earlier round rewritten" in result.stderr


def test_verdict_sha_diverges_from_new_reviewed_sha_blocks(tmp_path: Path) -> None:
    """A verdict's `sha` changing to a value that is NOT the new
    `reviewed_sha` (not merely unsynced, actively wrong) must still block --
    the exception requires exact lockstep, not merely "sha changed"."""
    repo = _init_repo(tmp_path)
    doc1 = _base_review()
    _commit_review(repo, doc1, "chore(loom): checkpoint review — seed")
    doc2 = copy.deepcopy(doc1)
    doc2["reviewed_sha"] = "bbbbbbb2"
    doc2["verdicts"][0]["sha"] = "ccccccc3"  # neither the old nor the new reviewed_sha
    _commit_review(repo, doc2, "chore(loom): checkpoint review — round 2 (sha to nowhere)")
    result = run_review_edits(repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "review.round-append-only" in blocked_rules(result)


def test_open_finding_gains_both_resolved_and_dismissed_at_once_blocks(tmp_path: Path) -> None:
    """`open-finding-resolved-or-dismissed-in-place` allows gaining exactly
    one of `resolved`/`dismissed` -- gaining BOTH on the same entry in one
    edit (an attempt to double-stamp a finding closed two ways at once) must
    still block."""
    repo = _init_repo(tmp_path)
    doc1 = _base_review()
    _commit_review(repo, doc1, "chore(loom): checkpoint review — seed")
    doc2 = copy.deepcopy(doc1)
    doc2["open_findings"][0]["resolved"] = True
    doc2["open_findings"][0]["dismissed"] = "not applicable by r1"
    _commit_review(repo, doc2, "chore(loom): checkpoint review — round 2 (double-close)")
    result = run_review_edits(repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "review.round-append-only" in blocked_rules(result)


def test_dismissed_reason_edited_after_being_set_blocks(tmp_path: Path) -> None:
    """Once `dismissed` is set on an open finding, the exception is 'gained
    in place' -- it never authorises editing an already-set dismissal
    reason. A second edit that rewrites the reason text must block."""
    repo = _init_repo(tmp_path)
    doc1 = _base_review()
    doc1["open_findings"][0]["dismissed"] = "duplicate of f0 by r1"
    _commit_review(repo, doc1, "chore(loom): checkpoint review — seed (already dismissed)")
    doc2 = copy.deepcopy(doc1)
    doc2["open_findings"][0]["dismissed"] = "not a real bug by r1"
    _commit_review(repo, doc2, "chore(loom): checkpoint review — round 2 (reason rewritten)")
    result = run_review_edits(repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "review.round-append-only" in blocked_rules(result)


def test_second_vendor_unset_after_being_set_blocks(tmp_path: Path) -> None:
    """`second-vendor-set-once` only authorises the absent-to-value move.
    Setting it back to null after it was already a value must block -- the
    id is 'set once', not 'set or cleared'."""
    repo = _init_repo(tmp_path)
    doc1 = _base_review()
    doc1["second_vendor"] = "codex"
    _commit_review(repo, doc1, "chore(loom): checkpoint review — seed (second vendor set)")
    doc2 = copy.deepcopy(doc1)
    doc2["second_vendor"] = None
    _commit_review(repo, doc2, "chore(loom): checkpoint review — round 2 (second vendor cleared)")
    result = run_review_edits(repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "review.round-append-only" in blocked_rules(result)


def test_verdicts_reordered_same_multiset_different_position_blocks(tmp_path: Path) -> None:
    """Swapping two distinct verdict entries' positions (same two entries,
    same total content, different index) is compared positionally, index by
    index -- it must still block as an earlier-round rewrite at whichever
    index no longer matches, not silently pass because the *set* of
    verdicts is unchanged."""
    repo = _init_repo(tmp_path)
    doc1 = _base_review()
    _commit_review(repo, doc1, "chore(loom): checkpoint review — seed")
    doc2 = copy.deepcopy(doc1)
    doc2["verdicts"] = [doc1["verdicts"][1], doc1["verdicts"][0]]
    _commit_review(repo, doc2, "chore(loom): checkpoint review — round 2 (verdicts swapped)")
    result = run_review_edits(repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "review.round-append-only" in blocked_rules(result)


def test_review_edits_after_bare_string_shape_fails_closed_not_crash(tmp_path: Path) -> None:
    """The old `edits_after` shape (a bare list of strings, no `id`/`text`
    mapping) must not crash the checker -- `_review_edits_after_ids` drops
    non-mapping entries, so the enabled-ids set becomes empty and every
    previously-legal accretion (a pure append) now blocks. This is the
    fail-closed behaviour the recipe asks about: confirmed here, not
    assumed."""
    original = MANIFEST_PATH.read_text(encoding="utf-8")
    patched = original.replace(
        "      edits_after:\n"
        "        - {id: verdicts-probes-findings-dispatch-gain-entries, text: \"verdicts, probes, open_findings and dispatch gain entries\"}\n"
        "        - {id: reviewed-sha-scope-cost-replaced,                text: \"reviewed_sha, scope and cost are replaced\"}\n"
        "        - {id: open-finding-resolved-or-dismissed-in-place,     text: \"an open finding is resolved or dismissed in place\"}\n"
        "        - {id: questions-gain-entries,                          text: \"questions gains entries, one per decision-point question asked; earlier entries unchanged\"}\n"
        "        - {id: second-vendor-set-once,                          text: \"second_vendor is set once\"}\n",
        "      edits_after:\n"
        "        - verdicts-probes-findings-dispatch-gain-entries\n"
        "        - reviewed-sha-scope-cost-replaced\n"
        "        - open-finding-resolved-or-dismissed-in-place\n"
        "        - questions-gain-entries\n"
        "        - second-vendor-set-once\n",
        1,
    )
    assert patched != original, "the review charter's edits_after block did not match the text this probe patches"
    repo = _init_repo(tmp_path)
    doc1 = _base_review()
    _commit_review(repo, doc1, "chore(loom): checkpoint review — seed")
    doc2 = copy.deepcopy(doc1)
    doc2["verdicts"].append(
        {
            "reviewer": "r3", "vendor": "anthropic", "model": "haiku",
            "lens": "spec", "scope": "wave-end:1", "round": 2,
            "verdict": "PASS", "dimension_scores": {}, "findings": [], "sha": "aaaaaaa1",
        }
    )
    _commit_review(repo, doc2, "chore(loom): checkpoint review — round 2 (pure append)")
    scratch = tmp_path / "manifest.yaml"
    scratch.write_text(patched, encoding="utf-8")
    result = run_review_edits(repo, env={**os.environ, "LOOM_MANIFEST_PATH": str(scratch)})
    # No traceback: the process must exit with a clean 0/1/2, never a
    # Python exception dumped to stderr.
    assert "Traceback" not in result.stderr, result.stderr
    assert result.returncode == 1, (
        "bare-string edits_after should fail CLOSED (block the now-unrecognised "
        f"gain), got exit {result.returncode}: {result.stdout}{result.stderr}"
    )
    assert "review.round-append-only" in blocked_rules(result)


def test_smuggled_verdict_deletion_still_blocks_alongside_legal_second_vendor_set(tmp_path: Path) -> None:
    """A round that legally sets `second_vendor` for the first time AND
    illegally deletes a verdict entry in the same commit must still block on
    the deletion -- one authorised change in a commit must never whitelist
    an unrelated unauthorised change riding along in the same edit."""
    repo = _init_repo(tmp_path)
    doc1 = _base_review()
    _commit_review(repo, doc1, "chore(loom): checkpoint review — seed")
    doc2 = copy.deepcopy(doc1)
    doc2["second_vendor"] = "codex"  # legal: absent -> value
    doc2["verdicts"] = [doc1["verdicts"][0]]  # illegal: second verdict entry dropped
    _commit_review(repo, doc2, "chore(loom): checkpoint review — round 2 (mixed legal+illegal)")
    result = run_review_edits(repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "review.round-append-only" in blocked_rules(result)
    assert "earlier round rewritten" in result.stderr


# ---------------------------------------------------------------------------
# plan.edits-after-commit (W1-02) -- bare-string manifest shape
# ---------------------------------------------------------------------------

PLAN_CHANGE_ID = "2099-02-02-wave-end-1-probe-plan"


def _plan_text() -> str:
    return "\n".join(
        [
            f"# Probe plan -- {PLAN_CHANGE_ID}",
            f"intent: {PLAN_CHANGE_ID}@0000000",
            "charter: 1.0",
            "",
            "## Current State Evidence",
            "- Forward: some/path.py:1 names the current gap in one short bullet here.",
            "",
            "## Task DAG",
            "",
            "**W1 Only task**  after: --",
            "- Files: a.py",
            "- Test: the W1 test passes",
            "- Risk: agent-decided -- low risk",
            "",
            "## Questions asked",
            "① — what — one recorded question and its answer here.",
            "",
            "## Risks",
            "1. agent-decided -- a single bounded plan-wide risk, one line.",
            "",
        ]
    )


def _plan_path(repo: Path) -> Path:
    return repo / "docs" / "loom" / PLAN_CHANGE_ID / "plan.md"


def _seed_plan_commit(repo: Path, text: str) -> str:
    path = _plan_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", f"docs(loom): plan {PLAN_CHANGE_ID}")
    return git(repo, "rev-parse", "HEAD")


def run_plan_edits(repo: Path, env: dict | None = None) -> subprocess.CompletedProcess:
    return run_checker("plan-edits", PLAN_CHANGE_ID, cwd=repo, env=env)


def test_plan_edits_after_bare_string_shape_fails_closed_not_crash(tmp_path: Path) -> None:
    """Same probe as the review-side one, against the plan charter's
    `edits_after` list: a bare-string (pre-id) shape must not crash
    `_plan_edits_after_ids`, and must fail closed -- a previously-legal
    `**claimed(...)**` mark addition now blocks because no id is
    recognised at all."""
    original = MANIFEST_PATH.read_text(encoding="utf-8")
    marker = "      edits_after:\n        - {id: mark-claimed-or-blocked,"
    assert marker in original, "plan charter edits_after block not found at the text this probe anchors on"
    start = original.index(marker)
    # Replace the five plan edits_after entries (ending right before the
    # `fields:` key that always follows this artifact's charter block) with
    # bare strings -- the pre-id shape the recipe asks about.
    end = original.index("\n    fields:", start)
    block = original[start:end]
    bare = "      edits_after:\n" + "\n".join(
        f"        - {line.split('id: ', 1)[1].split(',', 1)[0]}"
        for line in block.splitlines()[1:]
        if "id:" in line
    )
    patched = original[:start] + bare + original[end:]
    assert patched != original
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _plan_text())
    marked = _plan_text().replace("**W1 Only task**", "**W1 Only task****claimed(i1)**")
    _plan_path(repo).write_text(marked, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs(loom): plan edit — claim W1")
    scratch = tmp_path / "manifest.yaml"
    scratch.write_text(patched, encoding="utf-8")
    result = run_plan_edits(repo, env={**os.environ, "LOOM_MANIFEST_PATH": str(scratch)})
    assert "Traceback" not in result.stderr, result.stderr
    assert result.returncode == 1, (
        "bare-string plan edits_after should fail CLOSED (block the now-"
        f"unrecognised mark), got exit {result.returncode}: {result.stdout}{result.stderr}"
    )
    assert "plan.edits-after-commit" in blocked_rules(result)


# ---------------------------------------------------------------------------
# Cross-rule surface: `plan <path>` vs `plan-edits <change-id>`
# ---------------------------------------------------------------------------


def test_plan_and_plan_edits_subcommands_disagree_when_plan_lives_off_convention(tmp_path: Path) -> None:
    """`plan <path>` runs `plan.field-caps` against any path handed to it
    directly; `plan-edits <change-id>` resolves its own path from the
    manifest's `docs/loom/<change-id>/plan.md` convention and never accepts
    a path argument. A plan file committed at a location that does not
    match that convention is fully visible to `plan <path>` (field-caps
    still fires) but invisible to `plan-edits` (exit 2, file not found) --
    the two subcommands do not agree on where 'the plan' is, and nothing
    reconciles them. This is a finding, not a crash: recorded, not fixed
    here."""
    repo = _init_repo(tmp_path)
    off_convention = repo / "scratch" / "not-the-canonical-place.md"
    off_convention.parent.mkdir(parents=True)
    text = _plan_text().replace(
        "- Test: the W1 test passes",
        "- Test: " + " ".join(f"word{i}" for i in range(45)),  # over the 40-word cap
    )
    off_convention.write_text(text, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs(loom): plan off-convention location")

    direct = run_checker("plan", str(off_convention), cwd=repo)
    via_change_id = run_plan_edits(repo)

    assert direct.returncode == 1, direct.stdout + direct.stderr
    assert "plan.field-caps" in blocked_rules(direct)
    assert via_change_id.returncode == 2, (
        "plan-edits should exit 2 (file not found at the canonical path) "
        f"while `plan <path>` blocks the same content directly: got "
        f"{via_change_id.returncode}: {via_change_id.stdout}{via_change_id.stderr}"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
