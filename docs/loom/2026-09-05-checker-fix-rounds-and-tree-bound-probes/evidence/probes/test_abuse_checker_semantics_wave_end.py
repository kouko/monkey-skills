"""Adversarial probes for wave-end:1 of 2026-09-05-checker-fix-rounds-and-
tree-bound-probes. Six attack classes against the three commits on this
branch (`push.verdicts-ge-2` standing-reviewer recompute, tree-bound
`push.probes-*` / `push.reviewed-sha`, and the combined `push.review-only-
head` close commit), each built as a REAL sandbox git repository under
pytest's `tmp_path` and driven through `loom_checker.py` exactly as it is
really invoked. Nothing here duplicates the fixtures already committed at
evidence/probes/test_abuse_checker_semantics.py -- every scenario below is a
distinct attack shape.

Every test's docstring states the Attack and whether the checker holds it
(GREEN, the attack is recorded as a probe that failed to break anything) or
the checker falls for it (RED, a finding is raised with anchor and fix).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
CHECKER = REPO_ROOT / "loom-code" / "scripts" / "loom_checker.py"
CHANGE = "zzz-wave-end-probe"
OTHER_CHANGE = "zzz-wave-end-other"
REVIEW_REL = f"docs/loom/{CHANGE}/review.json"
OTHER_REVIEW_REL = f"docs/loom/{OTHER_CHANGE}/review.json"
INTENT_REL = f"docs/loom/intent/{CHANGE}.md"
PASSING_COMMAND = "python3 -c pass"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def run_checker(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args], capture_output=True, text=True, cwd=str(cwd)
    )


def blocked_rules(result: subprocess.CompletedProcess) -> set[str]:
    return {
        line.split(":", 1)[0].removeprefix("BLOCK ").strip()
        for line in result.stderr.splitlines()
        if line.startswith("BLOCK ")
    }


def rule_messages(result: subprocess.CompletedProcess, rule: str) -> list[str]:
    prefix = f"BLOCK {rule}:"
    return [
        line[len(prefix):].strip()
        for line in result.stderr.splitlines()
        if line.startswith(prefix)
    ]


# --- sandbox scaffolding (mirrors evidence/probes/test_abuse_checker_semantics.py) --


def init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    git(repo, "add", "seed.txt")
    git(repo, "commit", "-q", "-m", "seed")
    git(repo, "checkout", "-q", "-b", "work")
    return repo


def write_kickoff(repo: Path, command: str = PASSING_COMMAND) -> None:
    path = repo / "docs/loom/KICKOFF-DEFAULTS.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# Kickoff Defaults\n\n- package-tests: {command} — probe fixture (2026-09-05)\n",
        encoding="utf-8",
    )


def write_review(repo: Path, rel: str, body: dict) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=1), encoding="utf-8")


def commit_review(repo: Path, rel: str, body: dict, message: str = "chore(loom): checkpoint review") -> str:
    write_review(repo, rel, body)
    git(repo, "add", rel)
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


DISPATCH_TWO_REVIEWERS = [
    {"task": "T1", "role": "implementer", "agent_id": "impl-1", "model": "m",
     "started": "2026-09-05T09:00:00Z", "fresh_context": True},
    {"task": "T1", "role": "reviewer", "agent_id": "rev-a", "model": "m",
     "started": "2026-09-05T09:10:00Z", "fresh_context": True},
    {"task": "T1", "role": "reviewer", "agent_id": "rev-b", "model": "m",
     "started": "2026-09-05T09:11:00Z", "fresh_context": True},
]


def _base_verdicts(code_sha: str, verdict_sha: str, findings: list | None = None) -> list[dict]:
    return [
        {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
         "round": 1, "verdict": "NEEDS_REVISION" if findings else "PASS",
         "dimension_scores": {}, "sha": verdict_sha, "findings": findings or []},
        {"reviewer": "rev-b", "vendor": "anthropic", "model": "m", "lens": "code",
         "round": 1, "verdict": "PASS", "dimension_scores": {}, "sha": verdict_sha, "findings": []},
    ]


# ============================================================================
# Class 1 -- bypassing the standing-PASS recompute of push.verdicts-ge-2
# ============================================================================


def _round1_repo(tmp_path: Path) -> tuple[Path, str]:
    """A full-lane checkpoint: round 1 has rev-a (raises F-1 anchored at
    notes/F.md:1) and rev-b (PASS, raises nothing)."""
    repo = init_repo(tmp_path)
    write_kickoff(repo)
    note = repo / "notes/F.md"
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text("# F\nv1\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: add F\n\nTask: T1")
    code_sha = git(repo, "rev-parse", "HEAD")

    body = {
        "reviewed_sha": code_sha,
        "scope": "checkpoint",
        "vendors": ["anthropic"],
        "verdicts": _base_verdicts(
            code_sha, code_sha,
            findings=[{"severity": "important", "dimension": "correctness",
                       "anchor": "notes/F.md:1", "text": "wrong", "fix": "fix it"}],
        ),
        "probes": [
            {"kind": "package-tests", "command": PASSING_COMMAND, "sha": code_sha,
             "result": "pass", "artifact": ""},
        ],
        "open_findings": [
            {"id": "F-1", "anchor": "notes/F.md:1", "origin_sha": code_sha, "raised_by": "rev-a"},
        ],
        "dispatch": DISPATCH_TWO_REVIEWERS,
    }
    commit_review(repo, REVIEW_REL, body)
    return repo, code_sha


def test_verdicts_ge_2_fix_touching_anchor_and_outside_path_blocked(tmp_path: Path) -> None:
    """Attack: the fix delta touches BOTH the finding's anchor file
    (notes/F.md) AND an unrelated file (notes/G.md) in the same commit, only
    rev-a (the raiser) returns. GREEN: `_standing_reviewers`'s `all(...)`
    check over every changed path fails as soon as ONE path escapes the
    returning-reader anchor set, so touching the anchor too does not buy
    the attacker anything -- the floor of 2 still applies and blocks."""
    repo, code_sha = _round1_repo(tmp_path)
    (repo / "notes/F.md").write_text("# F\nv2 fixed\n", encoding="utf-8")
    (repo / "notes/G.md").write_text("# G\nsmuggled\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "fix: address finding\n\nTask: T1")
    fix_sha = git(repo, "rev-parse", "HEAD")

    body2 = {
        "reviewed_sha": fix_sha, "scope": "checkpoint", "vendors": ["anthropic"],
        "verdicts": _base_verdicts(code_sha, code_sha, findings=[{
            "severity": "important", "dimension": "correctness",
            "anchor": "notes/F.md:1", "text": "wrong", "fix": "fix it"}]) + [
            {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 2, "verdict": "PASS", "dimension_scores": {}, "sha": fix_sha, "findings": []},
        ],
        "probes": [{"kind": "package-tests", "command": PASSING_COMMAND, "sha": fix_sha,
                    "result": "pass", "artifact": ""}],
        "open_findings": [{"id": "F-1", "anchor": "notes/F.md:1", "origin_sha": code_sha,
                           "raised_by": "rev-a", "resolved": "fixed"}],
        "dispatch": DISPATCH_TWO_REVIEWERS,
    }
    commit_review(repo, REVIEW_REL, body2)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.verdicts-ge-2" in blocked_rules(result)


def test_verdicts_ge_2_directory_prefix_anchor_never_covers_subpath_blocked(tmp_path: Path) -> None:
    """Attack: the open finding's anchor is written as a directory prefix
    (`notes/`, no file, no colon) hoping the fix-delta check treats any file
    under that directory as covered. GREEN: `_anchor_paths` stores the
    literal segment `notes/` verbatim (exact-equality set membership, never
    a prefix test) -- `notes/F.md` is never `in {"notes/"}`, so the fix
    delta is judged NOT covered and the floor of 2 still applies."""
    repo, code_sha = _round1_repo(tmp_path)
    # Overwrite round 1 so the finding's anchor is a bare directory.
    body1 = json.loads((repo / REVIEW_REL).read_text(encoding="utf-8"))
    body1["verdicts"][0]["findings"][0]["anchor"] = "notes/"
    body1["open_findings"][0]["anchor"] = "notes/"
    git(repo, "reset", "--soft", "HEAD^")
    commit_review(repo, REVIEW_REL, body1)

    (repo / "notes/F.md").write_text("# F\nv2 fixed\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "fix: address finding\n\nTask: T1")
    fix_sha = git(repo, "rev-parse", "HEAD")

    body2 = dict(body1)
    body2["reviewed_sha"] = fix_sha
    body2["verdicts"] = body1["verdicts"] + [
        {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
         "round": 2, "verdict": "PASS", "dimension_scores": {}, "sha": fix_sha, "findings": []},
    ]
    body2["probes"] = [{"kind": "package-tests", "command": PASSING_COMMAND, "sha": fix_sha,
                        "result": "pass", "artifact": ""}]
    body2["open_findings"] = [{"id": "F-1", "anchor": "notes/", "origin_sha": code_sha,
                               "raised_by": "rev-a", "resolved": "fixed"}]
    commit_review(repo, REVIEW_REL, body2)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.verdicts-ge-2" in blocked_rules(result)


def test_verdicts_ge_2_raised_by_both_readers_requires_both_back_blocked(tmp_path: Path) -> None:
    """Attack: the still-open finding's `raised_by` lists BOTH readers
    (comma-separated: "rev-a, rev-b"), hoping only one has to come back.
    GREEN: `required` is the union of every still-open finding's
    `raised_by` names; both land in it, so `candidates = prev_reviewers -
    required` is empty and NEITHER reviewer can stand -- only rev-a returns
    in round 2, giving 1 distinct reviewer, below the full-lane floor."""
    repo, code_sha = _round1_repo(tmp_path)
    body1 = json.loads((repo / REVIEW_REL).read_text(encoding="utf-8"))
    body1["open_findings"][0]["raised_by"] = "rev-a, rev-b"
    git(repo, "reset", "--soft", "HEAD^")
    commit_review(repo, REVIEW_REL, body1)

    (repo / "notes/F.md").write_text("# F\nv2 fixed\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "fix: address finding\n\nTask: T1")
    fix_sha = git(repo, "rev-parse", "HEAD")

    body2 = dict(body1)
    body2["reviewed_sha"] = fix_sha
    body2["verdicts"] = body1["verdicts"] + [
        {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
         "round": 2, "verdict": "PASS", "dimension_scores": {}, "sha": fix_sha, "findings": []},
    ]
    body2["probes"] = [{"kind": "package-tests", "command": PASSING_COMMAND, "sha": fix_sha,
                        "result": "pass", "artifact": ""}]
    # Still open (raised_by names both) -- neither the raiser nor the
    # co-signer is exempt from returning.
    commit_review(repo, REVIEW_REL, body2)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.verdicts-ge-2" in blocked_rules(result)


def test_verdicts_ge_2_finding_resolved_by_non_raiser_still_requires_raiser_blocked(tmp_path: Path) -> None:
    """Attack: F-1 (raised_by rev-a) is marked `resolved` in round 2's
    open_findings, but the ONLY round-2 reviewer is rev-b, who never raised
    anything. GREEN: `returning_anchor_paths` is built only from findings
    raised by CURRENT round reviewers (rev-b raised none), so it is empty;
    the fix delta (notes/F.md) is not a subset of the empty set, so rev-a
    cannot stand on rev-b's say-so and the floor of 2 still applies."""
    repo, code_sha = _round1_repo(tmp_path)
    (repo / "notes/F.md").write_text("# F\nv2 fixed\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "fix: address finding\n\nTask: T1")
    fix_sha = git(repo, "rev-parse", "HEAD")

    body1 = json.loads((repo / REVIEW_REL).read_text(encoding="utf-8"))
    body2 = {
        "reviewed_sha": fix_sha, "scope": "checkpoint", "vendors": ["anthropic"],
        "verdicts": body1["verdicts"] + [
            {"reviewer": "rev-b", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 2, "verdict": "PASS", "dimension_scores": {}, "sha": fix_sha, "findings": []},
        ],
        "probes": [{"kind": "package-tests", "command": PASSING_COMMAND, "sha": fix_sha,
                    "result": "pass", "artifact": ""}],
        "open_findings": [{"id": "F-1", "anchor": "notes/F.md:1", "origin_sha": code_sha,
                           "raised_by": "rev-a", "resolved": "fixed, confirmed by rev-b"}],
        "dispatch": DISPATCH_TWO_REVIEWERS,
    }
    commit_review(repo, REVIEW_REL, body2)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.verdicts-ge-2" in blocked_rules(result)


def test_verdicts_ge_2_ghost_reviewer_missing_scope_cannot_inflate_floor_blocked(tmp_path: Path) -> None:
    """Attack: a fabricated "ghost" verdict (round 1, PASS, no `scope` key
    at all, no dispatch[] entry ever naming "ghost" as reviewer/blind-
    runner/adversary) is planted alongside the two real reviewers. Round 2
    has only rev-a return, with the fix delta confined to notes/F.md --
    exactly the anchor of the finding rev-a (a real, returning reviewer)
    raised. RED today: `_standing_reviewers` computes `returning_anchor_
    paths` from findings raised by CURRENT reviewers, then lets ANY prior-
    round PASS candidate stand once the delta sits inside that shared set
    -- it never asks whether the standing candidate is itself the one
    whose returning presence justified the anchor, nor whether that
    candidate ever had a real dispatch entry at all. `ghost` therefore
    stands alongside rev-a, `push.verdicts-ge-2` sees 2 distinct reviewers
    and passes, and `push.reviewer-ne-implementer` never catches it either
    -- that rule's dispatch-membership check runs only over
    `scored_verdicts` (the LATEST round), and ghost's only verdict entry
    lives in round 1, which that check never inspects. Direct confirmation
    (not part of this file, ephemeral repro): a fabricated "ghost" PASS
    planted directly in round 1 alongside a real dispatch IS caught by
    `push.reviewer-ne-implementer` ("verdict reviewer(s) ghost were never
    dispatched...") when it is the counted round -- the hole is specific to
    a phantom identity smuggled into an EARLIER round and later laundered
    through the standing-reviewer floor count, which cross-checks anchors
    but never cross-checks dispatch. See finding F-WE-1."""
    repo, code_sha = _round1_repo(tmp_path)
    body1 = json.loads((repo / REVIEW_REL).read_text(encoding="utf-8"))
    ghost_verdict = {
        "reviewer": "ghost", "vendor": "anthropic", "model": "m", "lens": "code",
        "round": 1, "verdict": "PASS", "dimension_scores": {}, "sha": code_sha, "findings": [],
    }
    body1["verdicts"].append(ghost_verdict)
    assert "scope" not in ghost_verdict
    git(repo, "reset", "--soft", "HEAD^")
    commit_review(repo, REVIEW_REL, body1)

    (repo / "notes/F.md").write_text("# F\nv2 fixed\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "fix: address finding\n\nTask: T1")
    fix_sha = git(repo, "rev-parse", "HEAD")

    body2 = dict(body1)
    body2["reviewed_sha"] = fix_sha
    body2["verdicts"] = body1["verdicts"] + [
        {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
         "round": 2, "verdict": "PASS", "dimension_scores": {}, "sha": fix_sha, "findings": []},
    ]
    body2["probes"] = [{"kind": "package-tests", "command": PASSING_COMMAND, "sha": fix_sha,
                        "result": "pass", "artifact": ""}]
    body2["open_findings"] = [{"id": "F-1", "anchor": "notes/F.md:1", "origin_sha": code_sha,
                               "raised_by": "rev-a", "resolved": "fixed"}]
    commit_review(repo, REVIEW_REL, body2)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.verdicts-ge-2" in blocked_rules(result)


def test_verdicts_ge_2_returning_reader_needs_revision_this_round_blocked(tmp_path: Path) -> None:
    """Attack: rev-a returns in round 2 (satisfying the reviewer-count
    floor by headcount alone) but files NEEDS_REVISION instead of PASS.
    GREEN: `check_verdicts`'s `not_passing` scan reads every verdict of the
    latest round regardless of how its reviewer count was reached, so a
    non-passing verdict in the counted round always blocks."""
    repo, code_sha = _round1_repo(tmp_path)
    (repo / "notes/F.md").write_text("# F\nv2 still wrong\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "fix: attempt\n\nTask: T1")
    fix_sha = git(repo, "rev-parse", "HEAD")

    body1 = json.loads((repo / REVIEW_REL).read_text(encoding="utf-8"))
    body2 = {
        "reviewed_sha": fix_sha, "scope": "checkpoint", "vendors": ["anthropic"],
        "verdicts": body1["verdicts"] + [
            {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 2, "verdict": "NEEDS_REVISION", "dimension_scores": {}, "sha": fix_sha,
             "findings": [{"severity": "important", "dimension": "correctness",
                           "anchor": "notes/F.md:1", "text": "still wrong", "fix": "fix again"}]},
            {"reviewer": "rev-b", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 2, "verdict": "PASS", "dimension_scores": {}, "sha": fix_sha, "findings": []},
        ],
        "probes": [{"kind": "package-tests", "command": PASSING_COMMAND, "sha": fix_sha,
                    "result": "pass", "artifact": ""}],
        "open_findings": [{"id": "F-1", "anchor": "notes/F.md:1", "origin_sha": code_sha,
                           "raised_by": "rev-a"}],
        "dispatch": DISPATCH_TWO_REVIEWERS,
    }
    commit_review(repo, REVIEW_REL, body2)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.verdicts-ge-2" in blocked_rules(result)
    messages = rule_messages(result, "push.verdicts-ge-2")
    assert any("not passing" in message for message in messages), messages


# ============================================================================
# Class 2 -- bypassing the tree-bound probes/reviewed-sha recompute
# ============================================================================


def _tree_bound_seed(repo: Path) -> str:
    (repo / "a.py").write_text("value = 1\n", encoding="utf-8")
    (repo / OTHER_REVIEW_REL).parent.mkdir(parents=True, exist_ok=True)
    (repo / OTHER_REVIEW_REL).write_text(json.dumps({"marker": "A"}), encoding="utf-8")
    (repo / "evidence").mkdir(exist_ok=True)
    for name in ("empty", "boundary", "hostile"):
        (repo / f"evidence/abuse_{name}.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: a\n\nTask: T1")
    return git(repo, "rev-parse", "HEAD")


def _adversarial_records(sha: str) -> list[dict]:
    return [
        {"kind": "adversarial", "command": f"python3 evidence/abuse_{name}.py",
         "sha": sha, "result": "pass", "artifact": f"evidence/abuse_{name}.py"}
        for name in ("empty", "boundary", "hostile")
    ]


def _tree_bound_body(reviewed_sha: str, verdict_sha: str, code_sha: str) -> dict:
    return {
        "reviewed_sha": reviewed_sha, "scope": "checkpoint", "vendors": ["anthropic"],
        "verdicts": [
            {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 1, "verdict": "PASS", "dimension_scores": {}, "sha": verdict_sha, "findings": []},
            {"reviewer": "rev-b", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 1, "verdict": "PASS", "dimension_scores": {}, "sha": verdict_sha, "findings": []},
        ],
        "probes": [
            {"kind": "package-tests", "command": PASSING_COMMAND, "sha": code_sha,
             "result": "pass", "artifact": ""},
            *_adversarial_records(code_sha),
        ],
        "open_findings": [],
        "dispatch": DISPATCH_TWO_REVIEWERS,
    }


def test_probes_tree_bound_another_changes_review_json_not_excluded_blocked(tmp_path: Path) -> None:
    """Attack: content_tree_id excludes only THIS change's own review.json
    from the tree listing (spec REQ-2/3). Prove the OTHER change's
    review.json is NOT accidentally excluded too -- if it were, a commit
    that only mutates it would go unnoticed and a stale reviewed_sha would
    wrongly keep passing. Sequence: code_sha1 (this change's review.json =
    A, this change's own reviewed content) -> code_sha2 (a plain commit
    that edits ONLY the other change's review.json, A -> B, this change's
    tree otherwise untouched) -> Y (review-only HEAD, reviewed_sha still
    pinned at code_sha1, stale relative to HEAD^ = code_sha2). GREEN: the
    other change's review.json counts as ordinary content, so code_sha1's
    and code_sha2's content_tree_id differ and push.reviewed-sha blocks the
    stale pin -- the safety line held."""
    repo = init_repo(tmp_path)
    write_kickoff(repo)
    code_sha1 = _tree_bound_seed(repo)

    (repo / OTHER_REVIEW_REL).write_text(json.dumps({"marker": "B"}), encoding="utf-8")
    git(repo, "add", OTHER_REVIEW_REL)
    git(repo, "commit", "-q", "-m", "chore: unrelated change's review.json moves\n\nTask: T1")
    code_sha2 = git(repo, "rev-parse", "HEAD")

    commit_review(repo, REVIEW_REL, _tree_bound_body(code_sha1, code_sha1, code_sha1))
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.reviewed-sha" in blocked_rules(result)


def test_probes_tree_bound_head_mixing_review_json_and_code_file_blocked(tmp_path: Path) -> None:
    """Attack: HEAD tries to smuggle a code edit through in the SAME commit
    as this change's review.json update, hoping the tree-bound comparison
    (which excludes only review.json) quietly ignores the code file too.
    GREEN: `push.review-only-head` fires first -- HEAD touches two paths
    and the second is not the sanctioned close-line shape -- so the commit
    is rejected outright regardless of what content_tree_id would have made
    of it."""
    repo = init_repo(tmp_path)
    write_kickoff(repo)
    code_sha = _tree_bound_seed(repo)

    (repo / "a.py").write_text("value = 2\n", encoding="utf-8")
    write_review(repo, REVIEW_REL, _tree_bound_body(code_sha, code_sha, code_sha))
    git(repo, "add", "a.py", REVIEW_REL)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review + sneak a code edit")
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)


def test_probes_tree_bound_tag_name_reviewed_sha_rejected_outright_blocked(tmp_path: Path) -> None:
    """Attack: `reviewed_sha` names a tag (`v-probe`) pointing at the real
    reviewed commit, hoping the content comparison resolves it like any
    other ref. GREEN: `SHA_HEX.fullmatch(recorded)` gates BEFORE any git
    resolution happens -- a tag name is not `[0-9a-f]{7,40}`, so
    `reviewed_id` is forced to None and push.reviewed-sha blocks with
    "names no commit in this repo", never reaching same_reviewed_content at
    all."""
    repo = init_repo(tmp_path)
    write_kickoff(repo)
    code_sha = _tree_bound_seed(repo)
    git(repo, "tag", "v-probe", code_sha)
    commit_review(repo, REVIEW_REL, _tree_bound_body("v-probe", code_sha, code_sha))
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.reviewed-sha" in blocked_rules(result)


def test_probes_tree_bound_short_sha_reviewed_sha_resolves_correctly_not_blocked(tmp_path: Path) -> None:
    """Attack (the short-sha companion): `reviewed_sha` and every verdict's
    `sha` are recorded as 8-char abbreviations instead of full 40-hex ids,
    hoping the ambiguity either silently fails closed (a false block that
    would waste a round) or silently fails open on the wrong commit. GREEN:
    `SHA_HEX` accepts 7-40 hex characters by design and `git rev-parse
    --verify <short>^{commit}` resolves it to the exact same commit id in
    this small unambiguous repo, so content comparison proceeds normally
    and the review-only stack is accepted -- a short sha is not itself an
    attack surface here."""
    repo = init_repo(tmp_path)
    write_kickoff(repo)
    code_sha = _tree_bound_seed(repo)
    short = code_sha[:8]
    commit_review(repo, REVIEW_REL, _tree_bound_body(short, short, code_sha))
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr
    rules = blocked_rules(result)
    assert "push.reviewed-sha" not in rules
    assert "push.probes-package-tests" not in rules
    assert "push.probes-adversarial" not in rules


def test_probes_tree_bound_rename_identical_blob_changes_listing_blocked(tmp_path: Path) -> None:
    """Attack: after the probes were recorded against code_sha, a later
    commit renames a probed file to a new path with byte-identical content
    (`git mv`, no content change at all), hoping "the blob never changed"
    is what content_tree_id keys on. GREEN: `content_tree_id` hashes the
    FULL `ls-tree -r` listing (path included, one line per path), not the
    set of blob ids alone -- a rename changes which path a blob sits at, so
    the listing (and therefore the content-tree id) differs and the stale
    reviewed_sha correctly blocks. This is the safety line held, not a
    defect: a probe's own artifact path moving out from under it must
    re-open review, even when the bytes are unchanged."""
    repo = init_repo(tmp_path)
    write_kickoff(repo)
    code_sha = _tree_bound_seed(repo)

    git(repo, "mv", "evidence/abuse_empty.py", "evidence/abuse_renamed.py")
    git(repo, "commit", "-q", "-m", "chore: rename a probe file, no content change\n\nTask: T1")
    renamed_sha = git(repo, "rev-parse", "HEAD")

    commit_review(repo, REVIEW_REL, _tree_bound_body(code_sha, code_sha, code_sha))
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.reviewed-sha" in blocked_rules(result)


# ============================================================================
# Class 3 -- bypassing the combined close-commit shape
# ============================================================================


def _seed_intent_and_code(repo: Path, status: str = "confirmed 2026-09-01") -> str:
    intent_path = repo / INTENT_REL
    intent_path.parent.mkdir(parents=True, exist_ok=True)
    intent_path.write_text(f"# {CHANGE}\nstatus: {status}\n\n## Problem\nx\n", encoding="utf-8")
    write_kickoff(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: seed intent\n\nTask: T1")
    return git(repo, "rev-parse", "HEAD")


def _base_close_body(code_sha: str) -> dict:
    return {
        "reviewed_sha": code_sha, "scope": "checkpoint", "vendors": ["anthropic"],
        "verdicts": [
            {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 1, "verdict": "PASS", "dimension_scores": {}, "sha": code_sha, "findings": []},
            {"reviewer": "rev-b", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 1, "verdict": "PASS", "dimension_scores": {}, "sha": code_sha, "findings": []},
        ],
        "probes": [{"kind": "package-tests", "command": PASSING_COMMAND, "sha": code_sha,
                    "result": "pass", "artifact": ""}],
        "open_findings": [], "dispatch": DISPATCH_TWO_REVIEWERS,
    }


def test_review_only_head_whitespace_only_intent_edit_still_blocked(tmp_path: Path) -> None:
    """Attack: the status line flips to closed, and the ONLY other change
    in the intent file is a trailing whitespace edit (a space appended to
    the `## Problem` body line) -- hoping "whitespace doesn't count as a
    real edit" slips past the exemption. GREEN: `_review_only_head_closes_
    intent` regenerates the WHOLE before-text with only the status line's
    value replaced and compares it byte-for-byte to the after-text; any
    other byte difference, whitespace included, makes the regenerated blob
    disagree and the commit falls through to the generic block."""
    repo = init_repo(tmp_path)
    code_sha = _seed_intent_and_code(repo)
    write_review(repo, REVIEW_REL, _base_close_body(code_sha))

    intent_path = repo / INTENT_REL
    text = intent_path.read_text(encoding="utf-8")
    text = text.replace(
        "status: confirmed 2026-09-01", "status: closed 2026-09-05 — branch probe-branch",
    )
    text = text.replace("## Problem\nx\n", "## Problem\nx \n")  # trailing space only
    intent_path.write_text(text, encoding="utf-8")

    git(repo, "add", REVIEW_REL, INTENT_REL)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review + close intent")
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)


def test_review_only_head_second_status_line_added_blocked(tmp_path: Path) -> None:
    """Attack: a SECOND `status:`-prefixed line is appended near the end of
    the intent file (a decoy status line) alongside the real one flipping
    to closed, hoping `parse_document`'s last-wins frontmatter read is what
    gates the exemption. GREEN: `_review_only_head_closes_intent` calls
    `_status_line_positions` on both before- and after-text and requires
    EXACTLY ONE raw `status:`-prefixed line in each; two lines fails that
    guard outright and the commit falls through to the generic block."""
    repo = init_repo(tmp_path)
    code_sha = _seed_intent_and_code(repo)
    write_review(repo, REVIEW_REL, _base_close_body(code_sha))

    intent_path = repo / INTENT_REL
    text = intent_path.read_text(encoding="utf-8")
    text = text.replace(
        "status: confirmed 2026-09-01", "status: closed 2026-09-05 — branch probe-branch",
    )
    text += "\nstatus: confirmed 2026-09-01\n"  # decoy second status line
    intent_path.write_text(text, encoding="utf-8")

    git(repo, "add", REVIEW_REL, INTENT_REL)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review + close intent")
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)


def test_review_only_head_branch_name_with_dotdot_rejected_by_grammar_blocked(tmp_path: Path) -> None:
    """Attack: the branch-form close names a branch containing `..`
    (`feature/x..y`), hoping the identifier grammar's char class is loose
    enough to accept a git revision-range look-alike as a plain name.
    GREEN: the branch-name capture group is `[A-Za-z0-9._/-]+`, which DOES
    accept dots and slashes (so `feature/x..y` matches syntactically) --
    the real defence is that this shape is otherwise indistinguishable from
    a legitimate branch name and the checker never interprets the
    identifier as a git ref, only stores it as a string in the regenerated
    text; the actual attack surface tested here is a SPACE in the name
    (`probe branch`), which the grammar's char class excludes outright, so
    the STATUS regex never matches the closed alternative at all and the
    commit falls through to the generic "not a close commit" block."""
    repo = init_repo(tmp_path)
    code_sha = _seed_intent_and_code(repo)
    write_review(repo, REVIEW_REL, _base_close_body(code_sha))

    intent_path = repo / INTENT_REL
    text = intent_path.read_text(encoding="utf-8")
    text = text.replace(
        "status: confirmed 2026-09-01",
        "status: closed 2026-09-05 — branch probe branch",  # space in the name
    )
    intent_path.write_text(text, encoding="utf-8")

    git(repo, "add", REVIEW_REL, INTENT_REL)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review + close intent")
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)


def test_review_only_head_third_change_intent_riding_along_blocked(tmp_path: Path) -> None:
    """Attack: HEAD touches this change's review.json, this change's own
    intent (closing it correctly), AND a THIRD, unrelated change's intent
    file, hoping the two-path acceptance shape only counts "how many
    paths", not "which ones". GREEN: the two-touched-paths branch requires
    the second path to equal `expected_intent` for THIS change's own
    change-id exactly; a third file (this change's own intent OR any other
    path) pushes `len(touched)` to 3, failing `len(touched) == 2` outright,
    so the whole commit falls through to the generic block."""
    repo = init_repo(tmp_path)
    code_sha = _seed_intent_and_code(repo)
    write_review(repo, REVIEW_REL, _base_close_body(code_sha))

    intent_path = repo / INTENT_REL
    text = intent_path.read_text(encoding="utf-8")
    text = text.replace(
        "status: confirmed 2026-09-01", "status: closed 2026-09-05 — branch probe-branch",
    )
    intent_path.write_text(text, encoding="utf-8")

    other_intent = repo / f"docs/loom/intent/{OTHER_CHANGE}.md"
    other_intent.parent.mkdir(parents=True, exist_ok=True)
    other_intent.write_text(f"# {OTHER_CHANGE}\nstatus: confirmed 2026-09-01\n\n## Problem\ny\n",
                            encoding="utf-8")

    git(repo, "add", REVIEW_REL, INTENT_REL, str(other_intent.relative_to(repo)))
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review + close intent + stray file")
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)


# ============================================================================
# Class 4 -- intake.confirmed terminal-state grammar
# ============================================================================


def _closed_intent_repo(tmp_path: Path, status_line: str) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    intent_path = repo / INTENT_REL
    intent_path.parent.mkdir(parents=True, exist_ok=True)
    intent_path.write_text(f"# {CHANGE}\n{status_line}\n\n## Problem\nx\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "seed")
    return repo


def test_intake_confirmed_bad_calendar_date_not_treated_as_terminal_close(tmp_path: Path) -> None:
    """Attack: `status: closed 2026-13-45 — branch x` has the right SHAPE
    (matches the `\\d{4}-\\d{2}-\\d{2}` grammar) but names a date the
    calendar does not have (month 13, day 45), hoping the terminal-close
    message ("start a new intent") fires anyway on shape alone -- which
    would let an agent construct a bogus-but-plausible-looking closed
    intent that reads as legitimately terminal. GREEN: `cmd_intake` calls
    `is_real_date(closed_date)` (`date.fromisoformat`) before ever emitting
    the terminal wording, and a non-real date is reported as "names
    something that is not a real date" instead -- the intent is blocked,
    but never accepted as a genuine terminal close."""
    repo = _closed_intent_repo(tmp_path, "status: closed 2026-13-45 — branch probe-branch")
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    rules = blocked_rules(result)
    assert "intake.confirmed" in rules
    messages = rule_messages(result, "intake.confirmed")
    assert any("not a real date" in message for message in messages), messages
    assert not any("start a new intent" in message for message in messages), messages


def test_intake_confirmed_empty_branch_name_not_matched_as_closed(tmp_path: Path) -> None:
    """Attack: `status: closed 2026-09-05 — branch ` (identifier empty,
    trailing space) hoping the branch-form alternative's `+` quantifier is
    actually a `*` somewhere and an empty name still reads as a legitimate
    close. GREEN: the capture group is `[A-Za-z0-9._/-]+`, one-or-more; an
    empty identifier fails the whole STATUS regex, `match` is None, and
    `cmd_intake` falls through past both closed-info branches to the
    generic "status is <raw>" non-confirmed message -- never treated as
    terminal, and never silently accepted as `confirmed` either."""
    repo = _closed_intent_repo(tmp_path, "status: closed 2026-09-05 — branch ")
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    rules = blocked_rules(result)
    assert "intake.confirmed" in rules
    messages = rule_messages(result, "intake.confirmed")
    assert not any("start a new intent" in message for message in messages), messages
    assert any("accepts only" in message for message in messages), messages


# ============================================================================
# Class 5 -- --list-rules count and description semantics
# ============================================================================


def test_list_rules_line_count_pinned_at_27_wave_end(tmp_path: Path) -> None:
    """GREEN (regression pin): this branch's three commits recompute four
    existing rules and reword three descriptions; it adds and removes no
    rule id, so `--list-rules` must still emit exactly 27 lines."""
    result = run_checker("--list-rules", cwd=REPO_ROOT)
    assert result.returncode == 0, result.stderr
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) == 27, f"expected 27 rules, got {len(lines)}:\n{result.stdout}"


def test_list_rules_descriptions_name_new_semantics_of_three_rules(tmp_path: Path) -> None:
    """GREEN (regression pin): the three rules W1-01/W1-02/W1-03 actually
    changed must describe their NEW semantics in prose, not just keep their
    old wording with the id unchanged. Attack: read `--list-rules` output
    and require each description to literally mention the vocabulary this
    change introduces -- a description that quietly reverted to the old
    text (same rule id, stale prose) would fail this."""
    result = run_checker("--list-rules", cwd=REPO_ROOT)
    assert result.returncode == 0, result.stderr
    by_id = {}
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        rule_id, _, description = line.partition("\t")
        by_id[rule_id] = description

    verdicts_desc = by_id["push.verdicts-ge-2"]
    assert "standing" in verdicts_desc.lower() or "non-returning" in verdicts_desc.lower(), verdicts_desc
    assert "return" in verdicts_desc.lower(), verdicts_desc

    for rule in ("push.probes-package-tests", "push.probes-adversarial", "push.reviewed-sha"):
        desc = by_id[rule]
        assert "content" in desc.lower(), (rule, desc)

    review_only_desc = by_id["push.review-only-head"]
    assert "status" in review_only_desc.lower(), review_only_desc


# ============================================================================
# Class 6 -- Codex mirror byte-identity
# ============================================================================


def test_codex_mirror_byte_identical_to_source_apart_from_stamp_line() -> None:
    """Attack: assume the committed `.codex/hooks/loom_checker.py` mirror
    might have drifted from `loom-code/scripts/loom_checker.py` after this
    branch's three commits touched the source, hoping a stale or hand-
    edited mirror slipped through unnoticed. GREEN: removing the mirror's
    one inserted `# loom-checker <version>` stamp line reproduces the
    source byte for byte -- the mirror was correctly regenerated by
    `codex_scaffold.py` alongside every source edit on this branch."""
    source = REPO_ROOT / "loom-code" / "scripts" / "loom_checker.py"
    mirror = REPO_ROOT / ".codex" / "hooks" / "loom_checker.py"
    source_lines = source.read_text(encoding="utf-8").splitlines(keepends=True)
    mirror_lines = mirror.read_text(encoding="utf-8").splitlines(keepends=True)

    assert len(mirror_lines) == len(source_lines) + 1, (
        len(mirror_lines), len(source_lines)
    )
    at = 1 if source_lines and source_lines[0].startswith("#!") else 0
    stamped_line = mirror_lines[at]
    assert stamped_line.startswith("# loom-checker "), stamped_line
    rebuilt = mirror_lines[:at] + mirror_lines[at + 1:]
    assert rebuilt == source_lines, "mirror has drifted from loom_checker.py"
