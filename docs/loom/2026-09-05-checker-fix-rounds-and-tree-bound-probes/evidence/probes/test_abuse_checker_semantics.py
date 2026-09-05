"""Adversarial probes for W0-01 (docs/loom/2026-09-05-checker-fix-rounds-and-
tree-bound-probes/plan.md). Every case builds a REAL sandbox git repository
under pytest's `tmp_path` (never under this repo) and shells out to the
checker at `loom-code/scripts/loom_checker.py` exactly the way it is really
invoked, then asserts on the `BLOCK <rule.id>` lines its stderr carries.

Each test's docstring states its Attack, whether it is RED or GREEN against
today's checker, and what change would turn it GREEN. Nothing here pins an
exact BLOCK message string except test_intake_confirmed_closed_branch_form
_blocked_as_terminal, which the task itself asks to assert on message shape;
every other test pins a rule id and an exit code, not prose (plan risk:
"Agent-decided: pin behaviours, not messages").
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
CHECKER = REPO_ROOT / "loom-code" / "scripts" / "loom_checker.py"
CHANGE = "zzz-checker-probe"
INTAKE_CHANGE = "zzz-intake-probe"
REVIEW_REL = f"docs/loom/{CHANGE}/review.json"
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


# --- sandbox scaffolding -----------------------------------------------------


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


def write_review(repo: Path, body: dict) -> None:
    path = repo / REVIEW_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=1), encoding="utf-8")


def commit_review(repo: Path, body: dict) -> str:
    write_review(repo, body)
    git(repo, "add", REVIEW_REL)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")
    return git(repo, "rev-parse", "HEAD")


DISPATCH_TWO_REVIEWERS = [
    {"task": "T1", "role": "implementer", "agent_id": "impl-1", "model": "m",
     "started": "2026-09-05T09:00:00Z", "fresh_context": True},
    {"task": "T1", "role": "reviewer", "agent_id": "rev-a", "model": "m",
     "started": "2026-09-05T09:10:00Z", "fresh_context": True},
    {"task": "T1", "role": "reviewer", "agent_id": "rev-b", "model": "m",
     "started": "2026-09-05T09:11:00Z", "fresh_context": True},
]


# --- (a) / (b): the returning-reader recompute of push.verdicts-ge-2 -------


def _build_returning_reader_repo(tmp_path: Path, *, touch_outside_anchor: bool) -> Path:
    """A full-lane checkpoint: round 1 has two readers, one (`rev-a`) raises
    a finding anchored at `notes/F.md:1`; the fix commit resolves it. Round 2
    carries only `rev-a`'s PASS. `touch_outside_anchor` decides whether the
    fix delta stays inside the finding's anchor file or spills onto a second
    file `notes/G.md` the finding never named."""
    repo = init_repo(tmp_path)
    write_kickoff(repo)  # a standing doc on the branch always forces full lane
    note = repo / "notes/F.md"
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text("# F\nv1\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: add F\n\nTask: T1")
    code_sha = git(repo, "rev-parse", "HEAD")

    round1_body = {
        "reviewed_sha": code_sha,
        "scope": "checkpoint",
        "vendors": ["anthropic"],
        "verdicts": [
            {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 1, "verdict": "NEEDS_REVISION", "dimension_scores": {}, "sha": code_sha,
             "findings": [{"severity": "important", "dimension": "correctness",
                           "anchor": "notes/F.md:1", "text": "wrong", "fix": "fix it"}]},
            {"reviewer": "rev-b", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 1, "verdict": "PASS", "dimension_scores": {}, "sha": code_sha, "findings": []},
        ],
        "probes": [
            {"kind": "package-tests", "command": PASSING_COMMAND, "sha": code_sha,
             "result": "pass", "artifact": ""},
        ],
        "open_findings": [
            {"id": "F-1", "anchor": "notes/F.md:1", "origin_sha": code_sha, "raised_by": "rev-a"},
        ],
        "dispatch": DISPATCH_TWO_REVIEWERS,
    }
    commit_review(repo, round1_body)

    note.write_text("# F\nv2 fixed\n", encoding="utf-8")
    if touch_outside_anchor:
        other = repo / "notes/G.md"
        other.write_text("# G\nunrelated\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "fix: address finding\n\nTask: T1")
    fix_sha = git(repo, "rev-parse", "HEAD")

    round2_body = dict(round1_body)
    round2_body["reviewed_sha"] = fix_sha
    round2_body["verdicts"] = round1_body["verdicts"] + [
        {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
         "round": 2, "verdict": "PASS", "dimension_scores": {}, "sha": fix_sha, "findings": []},
    ]
    round2_body["probes"] = [
        {"kind": "package-tests", "command": PASSING_COMMAND, "sha": fix_sha,
         "result": "pass", "artifact": ""},
    ]
    round2_body["open_findings"] = [
        {"id": "F-1", "anchor": "notes/F.md:1", "origin_sha": code_sha, "raised_by": "rev-a",
         "resolved": f"fixed in {fix_sha[:8]}; confirmed rev-a round 2"},
    ]
    commit_review(repo, round2_body)
    return repo


def test_verdicts_ge_2_returning_reader_anchor_scoped_fix_not_blocked(tmp_path: Path) -> None:
    """Attack: round 2 carries only the raising reader's (`rev-a`) PASS, and
    the fix delta touches only the anchor file the finding named. RED today:
    `check_verdicts` counts distinct reviewers of the latest round alone (no
    anchor recompute), so 1 < the full-lane floor of 2 blocks. GREEN once
    W1-01 lets a non-returning reader's earlier PASS stand when every path
    in `<that reader's verdict sha>..<this round's sha>` sits inside some
    open finding's anchor of the returning reader."""
    repo = _build_returning_reader_repo(tmp_path, touch_outside_anchor=False)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr
    assert "push.verdicts-ge-2" not in blocked_rules(result)


def test_verdicts_ge_2_fix_delta_outside_anchor_files_blocked(tmp_path: Path) -> None:
    """Attack: same round-2-single-reader shape, but the fix commit also
    touches `notes/G.md`, a file no open finding names. GREEN today AND
    after the fix (regression pin): the anchor-scoped exemption must never
    cover a delta that leaves the finding's own files, so the floor of 2
    distinct readers still applies and `push.verdicts-ge-2` blocks."""
    repo = _build_returning_reader_repo(tmp_path, touch_outside_anchor=True)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.verdicts-ge-2" in blocked_rules(result)


# --- (c): tree-bound probes/reviewed-sha across a review-only stack --------


def _build_probe_tree_bound_repo(tmp_path: Path) -> Path:
    """`code_sha` (X) carries the recorded package-tests + 3 adversarial
    probes. `review_y` (Y) sits directly on `code_sha`, touching only
    review.json. HEAD (Z) sits on `review_y`, ALSO touching only
    review.json, with `reviewed_sha` = `review_y` -- Y's own tree (minus
    review.json) is byte-identical to X's, but its commit id is not X."""
    repo = init_repo(tmp_path)
    write_kickoff(repo)
    (repo / "a.py").write_text("value = 1\n", encoding="utf-8")
    (repo / "evidence").mkdir()
    for name in ("empty", "boundary", "hostile"):
        (repo / f"evidence/abuse_{name}.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: a\n\nTask: T1")
    code_sha = git(repo, "rev-parse", "HEAD")

    def adversarial_records(sha: str) -> list[dict]:
        return [
            {"kind": "adversarial", "command": f"python3 evidence/abuse_{name}.py",
             "sha": sha, "result": "pass", "artifact": f"evidence/abuse_{name}.py"}
            for name in ("empty", "boundary", "hostile")
        ]

    def body(reviewed_sha: str, verdict_sha: str) -> dict:
        return {
            "reviewed_sha": reviewed_sha,
            "scope": "checkpoint",
            "vendors": ["anthropic"],
            "verdicts": [
                {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
                 "round": 1, "verdict": "PASS", "dimension_scores": {}, "sha": verdict_sha, "findings": []},
                {"reviewer": "rev-b", "vendor": "anthropic", "model": "m", "lens": "code",
                 "round": 1, "verdict": "PASS", "dimension_scores": {}, "sha": verdict_sha, "findings": []},
            ],
            "probes": [
                {"kind": "package-tests", "command": PASSING_COMMAND, "sha": code_sha,
                 "result": "pass", "artifact": ""},
                *adversarial_records(code_sha),
            ],
            "open_findings": [],
            "dispatch": DISPATCH_TWO_REVIEWERS,
        }

    review_y = commit_review(repo, body(code_sha, code_sha))
    commit_review(repo, body(review_y, review_y))
    return repo


def test_probes_tree_bound_review_only_commit_on_top_not_blocked(tmp_path: Path) -> None:
    """Attack: the package-tests and adversarial probes were recorded
    against `code_sha`, but HEAD's `reviewed_sha` names a review-only
    commit stacked one level higher whose tree, minus review.json, is
    identical to `code_sha`'s. RED today: the comparison is exact-sha, so
    both `push.probes-package-tests` and `push.probes-adversarial` block on
    "ran against sha ..., not the reviewed commit". GREEN once probes are
    bound to `content_tree_id` (tree with review.json excluded) instead of
    the commit id."""
    repo = _build_probe_tree_bound_repo(tmp_path)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr
    rules = blocked_rules(result)
    assert "push.probes-package-tests" not in rules
    assert "push.probes-adversarial" not in rules


# --- (d): a message-only history rewrite (same trees, new shas) -----------


def _build_trailer_rewrite_repo(tmp_path: Path) -> Path:
    repo = init_repo(tmp_path)
    write_kickoff(repo)
    note = repo / "notes/F.md"
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text("# F\ncontent\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: add F\n\nTask: T1")
    original_code_sha = git(repo, "rev-parse", "HEAD")

    body = {
        "reviewed_sha": original_code_sha,
        "scope": "checkpoint",
        "vendors": ["anthropic"],
        "verdicts": [
            {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 1, "verdict": "PASS", "dimension_scores": {}, "sha": original_code_sha, "findings": []},
            {"reviewer": "rev-b", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 1, "verdict": "PASS", "dimension_scores": {}, "sha": original_code_sha, "findings": []},
        ],
        "probes": [
            {"kind": "package-tests", "command": PASSING_COMMAND, "sha": original_code_sha,
             "result": "pass", "artifact": ""},
        ],
        "open_findings": [],
        "dispatch": DISPATCH_TWO_REVIEWERS,
    }
    commit_review(repo, body)

    # Rewrite the code commit's MESSAGE only -- the tree does not move --
    # producing a new commit id that review.json's recorded shas never saw.
    git(repo, "checkout", "-q", original_code_sha)
    git(repo, "commit", "-q", "--amend", "-m", "feat: add F (message rewritten)\n\nTask: T1")
    new_code_sha = git(repo, "rev-parse", "HEAD")
    git(repo, "rebase", "-q", "--onto", new_code_sha, original_code_sha, "work")
    return repo


def test_reviewed_sha_trailer_only_rewrite_not_blocked(tmp_path: Path) -> None:
    """Attack: `git commit --amend` rewrote the reviewed commit's message
    (trailer added, tree untouched), then the review-only commit was
    replayed on top by `git rebase --onto` -- same tree throughout, brand
    new commit ids. RED today: `push.reviewed-sha` compares `reviewed_id`
    to `HEAD^` as exact commit ids, which now differ, so it blocks even
    though nothing a reviewer looked at changed. GREEN once the comparison
    is `content_tree_id` (tree minus review.json) instead of the commit id."""
    repo = _build_trailer_rewrite_repo(tmp_path)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr
    assert "push.reviewed-sha" not in blocked_rules(result)


# --- (e): the close line riding in the review-only commit ------------------


def _seed_intent_and_code(repo: Path, status: str = "confirmed 2026-09-01") -> str:
    intent_path = repo / INTENT_REL
    intent_path.parent.mkdir(parents=True, exist_ok=True)
    intent_path.write_text(f"# {CHANGE}\nstatus: {status}\n\n## Problem\nx\n", encoding="utf-8")
    write_kickoff(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: seed intent\n\nTask: T1")
    return git(repo, "rev-parse", "HEAD")


def _build_review_only_close_repo(tmp_path: Path, *, extra_line: bool) -> Path:
    """One review-only HEAD commit that touches review.json AND the
    intent's `status:` line, switching it to the option-A closed form
    `closed <date> — branch <name>`. `extra_line` decides whether a second,
    unrelated intent line changes alongside it."""
    repo = init_repo(tmp_path)
    code_sha = _seed_intent_and_code(repo)

    body = {
        "reviewed_sha": code_sha,
        "scope": "checkpoint",
        "vendors": ["anthropic"],
        "verdicts": [
            {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 1, "verdict": "PASS", "dimension_scores": {}, "sha": code_sha, "findings": []},
            {"reviewer": "rev-b", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 1, "verdict": "PASS", "dimension_scores": {}, "sha": code_sha, "findings": []},
        ],
        "probes": [
            {"kind": "package-tests", "command": PASSING_COMMAND, "sha": code_sha,
             "result": "pass", "artifact": ""},
        ],
        "open_findings": [],
        "dispatch": DISPATCH_TWO_REVIEWERS,
    }
    write_review(repo, body)

    intent_path = repo / INTENT_REL
    text = intent_path.read_text(encoding="utf-8")
    text = text.replace(
        "status: confirmed 2026-09-01",
        "status: closed 2026-09-05 — branch probe-branch",
    )
    if extra_line:
        text = text.replace("## Problem\nx\n", "## Problem\ny\n")
    intent_path.write_text(text, encoding="utf-8")

    git(repo, "add", REVIEW_REL, INTENT_REL)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review + close intent")
    return repo


def test_review_only_head_status_line_with_review_json_not_blocked(tmp_path: Path) -> None:
    """Attack: HEAD touches review.json AND the intent file, but the ONLY
    line the intent file's diff carries is its `status:` line flipping to
    the option-A closed form. RED today: `check_review_only_head` accepts
    only a HEAD that touches exactly one path (review.json), so a second
    touched path blocks outright, whatever it changed. GREEN once
    `push.review-only-head` allows this one specific second-file shape."""
    repo = _build_review_only_close_repo(tmp_path, extra_line=False)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr
    assert "push.review-only-head" not in blocked_rules(result)


def test_review_only_head_extra_intent_line_still_blocked(tmp_path: Path) -> None:
    """Attack: same shape, but the intent file's diff ALSO changes an
    unrelated body line (`## Problem` content) alongside the status flip.
    GREEN today AND after the fix (regression pin): the close-line
    exemption must stay scoped to the status line alone, never to "the
    intent file, whatever else moved in it", so this keeps blocking."""
    repo = _build_review_only_close_repo(tmp_path, extra_line=True)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)


# --- (f): intake write-plan on a branch-form-closed intent -----------------


def _build_closed_branch_intent_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    intent_rel = f"docs/loom/intent/{INTAKE_CHANGE}.md"
    intent_path = repo / intent_rel
    intent_path.parent.mkdir(parents=True, exist_ok=True)
    intent_path.write_text(
        f"# {INTAKE_CHANGE}\nstatus: closed 2026-09-05 — branch probe-branch\n\n## Problem\nx\n",
        encoding="utf-8",
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "seed")
    return repo, intent_rel


def test_intake_confirmed_closed_branch_form_blocked_as_terminal(tmp_path: Path) -> None:
    """Attack: an intent whose `status:` line already reads the option-A
    branch-form close grammar (`closed <date> — branch <name>`) is handed
    to `intake write-plan`. RED today: `STATUS` (built from
    `_STATUS_CLOSED_ALT`, which only spells `closed <date> — PR #<N>`) does
    not match this line at all, so `cmd_intake` falls through to the
    generic "status is <raw text>" message instead of the terminal
    "this change is closed ...; a new change starts from a new intent"
    wording the PR form already gets -- the SAME shape of block, `BLOCK
    intake.confirmed`, fires either way, but the reason text never names
    the intent as closed-and-terminal. GREEN once the branch form is a
    second alternative recognised by the same terminal message."""
    repo, _intent_rel = _build_closed_branch_intent_repo(tmp_path)
    result = run_checker("intake", "write-plan", INTAKE_CHANGE, cwd=repo)
    assert result.returncode == 1
    rules = blocked_rules(result)
    assert "intake.confirmed" in rules
    messages = rule_messages(result, "intake.confirmed")
    assert any("start a new intent" in message for message in messages), messages


# --- (g): --list-rules stays at 27 (regression pin) -------------------------


def test_list_rules_line_count_pinned_at_27() -> None:
    """GREEN today and after the fix (regression pin): the plan changes how
    four existing rules recompute and updates three of their descriptions;
    it adds and removes none, so `--list-rules` must keep emitting exactly
    27 lines, one `<rule.id>\\t<description>` per line."""
    result = run_checker("--list-rules", cwd=REPO_ROOT)
    assert result.returncode == 0, result.stderr
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) == 27, f"expected 27 rules, got {len(lines)}:\n{result.stdout}"
