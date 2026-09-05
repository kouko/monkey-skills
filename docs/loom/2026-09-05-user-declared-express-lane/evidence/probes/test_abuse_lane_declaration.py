"""W0-01 adversary-first probes for
2026-09-05-user-declared-express-lane, written before W1-01/W1-02 exist.

Every case asserts the FUTURE behaviour the plan promises (plan.md W0-01,
Acceptance 2-4 of docs/loom/intent/2026-09-05-user-declared-express-lane.md).
Today's `loom_checker.py` recomputes only `small | full` from the diff
(`change_lane_detail`) and never reads a `lane:` frontmatter line, a
`default-lane:` KICKOFF key, or a switch commit's grammar at all -- so
every case marked RED fails today by design; W1-01/W1-02 are expected to
turn it green. Every case marked GREEND is an invariant that must not
regress while that work lands, pinned here so a fix round cannot silently
break it while chasing the RED cases.

Fixtures follow `test_loom_checker_push.py`'s pattern (a real git repo per
test, `push`/`intent` invoked via subprocess against THIS tree's
`loom_checker.py`) -- lane recomputation, review-only-head shape,
dispatch[]/Task: trailers and the adversarial/package-tests probe rules
are all diff- and content-driven, so a mocked repo would test nothing.
Helpers are reused from `test_loom_checker_push.py` (repo/commit/review
primitives) and `test_loom_checker_intent.py` (schema-valid intent
authoring for the `intent` subcommand cases) rather than re-derived.

Grammar pinned by these probes (the implementer follows it):
`lane: express` or `lane: gate-only` in the intent frontmatter, optionally
`lane: <name> -- switched <YYYY-MM-DD> by <name>, from <wave <n>|round <n>>`;
the LAST `lane:` line in the file wins; a switch commit is the commit that
last changed that line, and its message must carry that line verbatim
(mirroring `check_needs_design_reason`'s mechanism). KICKOFF-DEFAULTS.md
carries `- default-lane: full|express|gate-only -- <why> (<date>)`. A
switch's `from <round n>` reading pinned here: the declared lane applies
only to rounds STRICTLY AFTER `n` -- round `n` itself still runs under the
lane that was in force before the switch.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# file: docs/loom/2026-09-05-user-declared-express-lane/evidence/probes/<this>.py
# parents: [0]=probes [1]=evidence [2]=<change-id> [3]=loom [4]=docs [5]=repo root
REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT / "loom-code" / "scripts"))

from test_loom_checker_push import (  # noqa: E402
    ABUSE_CASES,
    PASSING_COMMAND,
    blocked_rules,
    git,
    run_checker,
)
from test_loom_checker_intent import (  # noqa: E402
    make_repo as make_intent_repo,
)

CHECKER = REPO_ROOT / "loom-code" / "scripts" / "loom_checker.py"


# --- shared low-level fixture builders --------------------------------------


def _seed_branch(tmp_path: Path) -> Path:
    """`main` with one seed commit, checked out onto a `work` branch --
    the same shape `test_loom_checker_push.build_repo` uses, but built
    fresh here since each case wants a different delta shape."""
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


def _write(repo: Path, rel: str, content: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _lane_intent_text(change_id: str, *, lane_line: str | None) -> str:
    """A schema-complete intent (every required frontmatter field and
    section from contract/manifest.yaml) with an optional `lane:` line --
    complete so a schema/recompute failure never masquerades as the lane
    behaviour under test."""
    lines = [
        f"# {change_id}",
        "originator: kouko",
        "kind: engineering",
        "needs-design: no — no interface surface touched",
    ]
    if lane_line is not None:
        lines.append(lane_line)
    lines += [
        "",
        "## Problem",
        "People doing this work want less verification for a light change.",
        "",
        "## Proposed outcome",
        "A declared lane.",
        "",
        "## Acceptance",
        "1. The declared lane is honoured.",
        "",
        "## Constraints",
        "- none",
        "",
        "## Out of scope",
        "- none",
        "",
        "## Open questions",
        "- none",
        "",
    ]
    return "\n".join(lines)


def _write_kickoff(repo: Path, *, extra_lines: tuple[str, ...] = ()) -> None:
    lines = [
        "# Kickoff Defaults",
        "",
        f"- package-tests: {PASSING_COMMAND} — the fixture's whole suite (2026-09-05)",
        *extra_lines,
        "",
    ]
    _write(repo, "docs/loom/KICKOFF-DEFAULTS.md", "\n".join(lines))


def _write_evidence(repo: Path, count: int = 3) -> None:
    (repo / "evidence").mkdir(exist_ok=True)
    (repo / "evidence/tests.txt").write_text("1 passed\n", encoding="utf-8")
    for name in ABUSE_CASES[:count]:
        (repo / f"evidence/abuse_{name}.py").write_text(
            "raise SystemExit(0)\n", encoding="utf-8"
        )


def _adversarial_records(reviewed_sha: str, count: int = 3) -> list[dict]:
    return [
        {
            "kind": "adversarial",
            "command": f"python3 evidence/abuse_{name}.py",
            "sha": reviewed_sha,
            "result": "pass",
            "artifact": f"evidence/abuse_{name}.py",
        }
        for name in ABUSE_CASES[:count]
    ]


def _package_tests_record(reviewed_sha: str) -> dict:
    return {
        "kind": "package-tests",
        "command": PASSING_COMMAND,
        "sha": reviewed_sha,
        "result": "pass",
        "artifact": "evidence/tests.txt",
    }


def _verdict(reviewer: str, round_: int, scope: str, sha: str, verdict: str = "PASS") -> dict:
    return {
        "reviewer": reviewer,
        "vendor": "anthropic",
        "model": "m",
        "lens": "docs",
        "verdict": verdict,
        "dimension_scores": {},
        "findings": [],
        "sha": sha,
        "round": round_,
        "scope": scope,
    }


def _dispatch(role: str, agent_id: str, task: str = "T1") -> dict:
    return {
        "task": task,
        "role": role,
        "agent_id": agent_id,
        "model": "m",
        "started": "2026-09-05T09:00:00Z",
        "fresh_context": True,
    }


def _commit_intent(repo: Path, change_id: str, *, lane_line: str | None) -> str:
    """The intent, committed ALONE -- so the next (delta) commit never
    itself touches the intent path. `check_close_commit_shape` fires on
    ANY commit at HEAD^ (the reviewed commit) that touches the intent
    artifact template at all, not only a real close commit, so a delta
    commit that also happens to introduce/edit the intent file would be
    spuriously blocked as a malformed close commit -- a confound this
    file must not introduce into its own RED/GREEN readings."""
    intent_rel = f"docs/loom/intent/{change_id}.md"
    _write(repo, intent_rel, _lane_intent_text(change_id, lane_line=lane_line))
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", "docs(loom): add the intent")
    return intent_rel


def _write_review(repo: Path, change_id: str, body: dict) -> str:
    rel = f"docs/loom/{change_id}/review.json"
    _write(repo, rel, json.dumps(body, indent=1))
    return rel


def _commit_review(repo: Path, review_rel: str) -> None:
    git(repo, "add", review_rel)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")


# =============================================================================
# (a) declared `lane: express`, a docs+skill delta, one reader at branch-end.
# RED today: change_lane_detail never reads `lane:`; a SKILL.md path forces
# the full lane (floor 2), so one reader is blocked.
# =============================================================================


def test_push_declared_express_lane_docs_skill_delta_single_reader_passes(
    tmp_path: Path,
) -> None:
    """A `lane: express` intent, a docs+skill delta, one reader at
    branch-end -- `push` must exit 0 once the declared lane is honoured.
    Written directly (not via `_commit_intent`, whose plain "add the
    intent" message never states the line) because `push` now verifies
    the deciding commit's message carries the `lane:` line verbatim
    (provenance check, wave-end:1-r3) before honouring a declaration."""
    repo = _seed_branch(tmp_path)
    change_id = "2026-09-05-lane-a"
    lane_line = "lane: express — declared 2026-09-05 by kouko"
    intent_rel = f"docs/loom/intent/{change_id}.md"
    _write(repo, intent_rel, _lane_intent_text(change_id, lane_line=lane_line))
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): add the intent\n\n{lane_line}")
    _write_kickoff(repo)
    _write(repo, "docs/notes.md", "some notes\n")
    _write(repo, "loom-code/skills/example/SKILL.md", "---\nname: example\n---\nbody\n")
    _write_evidence(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs(loom): example skill note\n\nTask: T1")
    reviewed_sha = git(repo, "rev-parse", "HEAD")

    body = {
        "reviewed_sha": reviewed_sha,
        "scope": "branch-end",
        "vendors": ["anthropic"],
        "verdicts": [_verdict("agent-rev", 1, "branch-end", reviewed_sha)],
        "probes": [_package_tests_record(reviewed_sha), *_adversarial_records(reviewed_sha)],
        "open_findings": [],
        "dispatch": [
            _dispatch("implementer", "agent-imp", "T1"),
            _dispatch("reviewer", "agent-rev"),
        ],
    }
    review_rel = _write_review(repo, change_id, body)
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, (
        "declared `lane: express` should let one reader pass a docs+skill "
        f"delta at branch-end; blocked instead: {result.stderr}"
    )


# =============================================================================
# (b) same declared express lane, plus one line changed in loom_checker.py.
# GREEN today and must stay GREEN: loom_checker.py is non-test code, which
# already forces the full lane independent of any declared lane, so one
# reader stays blocked before and after W1-01/W1-02.
# =============================================================================


def test_push_declared_express_lane_checker_code_delta_blocked(tmp_path: Path) -> None:
    """The same fixture as (a), but the delta ALSO touches
    `loom-code/scripts/loom_checker.py` -- a code-typed, non-test path --
    so one reader must stay blocked, declared `lane: express` or not."""
    repo = _seed_branch(tmp_path)
    change_id = "2026-09-05-lane-b"
    _commit_intent(repo, change_id, lane_line="lane: express — declared 2026-09-05 by kouko")
    _write_kickoff(repo)
    _write(repo, "docs/notes.md", "some notes\n")
    _write(repo, "loom-code/skills/example/SKILL.md", "---\nname: example\n---\nbody\n")
    _write(repo, "loom-code/scripts/loom_checker.py", "# one extra line\n")
    _write_evidence(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat(loom-code): touch the checker\n\nTask: T1")
    reviewed_sha = git(repo, "rev-parse", "HEAD")

    body = {
        "reviewed_sha": reviewed_sha,
        "scope": "branch-end",
        "vendors": ["anthropic"],
        "verdicts": [_verdict("agent-rev", 1, "branch-end", reviewed_sha)],
        "probes": [_package_tests_record(reviewed_sha), *_adversarial_records(reviewed_sha)],
        "open_findings": [],
        "dispatch": [
            _dispatch("implementer", "agent-imp", "T1"),
            _dispatch("reviewer", "agent-rev"),
        ],
    }
    review_rel = _write_review(repo, change_id, body)
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode != 0, (
        "a code-typed delta on loom_checker.py must force the full lane and "
        "stay blocked with one reader, whatever `lane:` declares"
    )
    assert "push.verdicts-ge-2" in blocked_rules(result)


# =============================================================================
# (c) declared `lane: gate-only`, pure docs delta, ZERO verdicts, >=3
# adversarial probes and a package-tests probe recorded, review-only HEAD.
# RED today: check_verdicts still requires >=1 reader for the small lane
# it recomputes (docs-only forces neither full nor a reader floor of 0).
# =============================================================================


def test_push_declared_gate_only_lane_pure_docs_delta_zero_verdicts_passes(
    tmp_path: Path,
) -> None:
    """A `lane: gate-only` intent, a pure docs delta, zero verdicts but
    >=3 adversarial probes and a package-tests probe recorded at the
    reviewed sha -- the whole `push` must exit 0 once gate-only's reader
    floor of 0 is honoured. `KICKOFF-DEFAULTS.md` is seeded on `main`
    BEFORE the branch is checked out (a standing document forces the raw
    recompute to `full`, and gate-only is now eligible only when that raw
    recompute is `small` -- ratified follow-up, PRINCIPLES.md 56a4dc4c),
    so this delta stays genuinely docs-only and raw-small."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    kickoff = repo / "docs/loom/KICKOFF-DEFAULTS.md"
    kickoff.parent.mkdir(parents=True, exist_ok=True)
    kickoff.write_text(
        f"# Kickoff Defaults\n\n- package-tests: {PASSING_COMMAND} — the "
        "fixture's whole suite (2026-09-05)\n",
        encoding="utf-8",
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "seed")
    git(repo, "checkout", "-q", "-b", "work")
    change_id = "2026-09-05-lane-c"
    # Written directly (not via `_commit_intent`) so the deciding commit's
    # message states the `lane:` line verbatim -- push's provenance check
    # (wave-end:1-r3) would otherwise ignore the declaration.
    lane_line = "lane: gate-only — declared 2026-09-05 by kouko"
    intent_rel = f"docs/loom/intent/{change_id}.md"
    _write(repo, intent_rel, _lane_intent_text(change_id, lane_line=lane_line))
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): add the intent\n\n{lane_line}")
    _write(repo, "docs/notes.md", "some notes, no code or skill touched\n")
    _write_evidence(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs: pure docs delta")
    reviewed_sha = git(repo, "rev-parse", "HEAD")

    body = {
        "reviewed_sha": reviewed_sha,
        "scope": "branch-end",
        "vendors": ["anthropic"],
        "verdicts": [],
        "probes": [_package_tests_record(reviewed_sha), *_adversarial_records(reviewed_sha)],
        "open_findings": [],
        # `not reviewers` (push.reviewer-ne-implementer) reads dispatch[]
        # roles reviewer/blind-runner/adversary -- a gate-only round with
        # zero verdicts is still covered by its adversary dispatch entry.
        "dispatch": [_dispatch("adversary", "agent-adv", "T1")],
    }
    review_rel = _write_review(repo, change_id, body)
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, (
        "declared `lane: gate-only` should let a zero-verdict round pass a "
        f"pure docs delta with its probes recorded; blocked instead: {result.stderr}"
    )


# =============================================================================
# (d) same as (c), but the delta ALSO carries a SKILL.md/agents/*.md path.
# GREEN today and must stay GREEN: gate-only's own eligibility (plan W1-02)
# excludes any skill/agent-contract path, so a skill-typed delta forces the
# full lane whatever is declared -- zero readers stays blocked.
# =============================================================================


def test_push_declared_gate_only_lane_skill_delta_zero_verdicts_blocked(
    tmp_path: Path,
) -> None:
    """The same fixture as (c), but the delta ALSO touches a SKILL.md path
    -- gate-only is ineligible for a skill-typed delta, so zero readers
    must stay blocked."""
    repo = _seed_branch(tmp_path)
    change_id = "2026-09-05-lane-d"
    _commit_intent(repo, change_id, lane_line="lane: gate-only — declared 2026-09-05 by kouko")
    _write_kickoff(repo)
    _write(repo, "docs/notes.md", "some notes\n")
    _write(repo, "loom-code/skills/example/SKILL.md", "---\nname: example\n---\nbody\n")
    _write_evidence(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat(loom-code): a skill delta\n\nTask: T1")
    reviewed_sha = git(repo, "rev-parse", "HEAD")

    body = {
        "reviewed_sha": reviewed_sha,
        "scope": "branch-end",
        "vendors": ["anthropic"],
        "verdicts": [],
        "probes": [_package_tests_record(reviewed_sha), *_adversarial_records(reviewed_sha)],
        "open_findings": [],
        "dispatch": [
            _dispatch("implementer", "agent-imp", "T1"),
            _dispatch("adversary", "agent-adv", "T1"),
        ],
    }
    review_rel = _write_review(repo, change_id, body)
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode != 0, (
        "a skill-typed delta must force the full lane and stay blocked "
        "with zero readers, whatever `lane:` declares"
    )
    assert "push.verdicts-ge-2" in blocked_rules(result)


# =============================================================================
# (e) mid-flight switch: rounds 1-2 (scope wave-end:1, two readers PASS),
# then a switch commit, then round 3 (scope branch-end, one reader).
# =============================================================================


def _mid_flight_switch_repo(tmp_path: Path, *, change_id: str, from_marker: str) -> tuple[Path, str]:
    """A branch whose intent starts with NO `lane:` line, gets a wave-end:1
    checkpoint's worth of round-1/round-2 history (two readers each,
    narrative only -- `scored_verdicts` scopes to the CURRENT round's own
    `scope`, so these never affect what `push` decides), a switch commit
    that adds `lane: express — switched 2026-09-05 by kouko, from
    {from_marker}` (message carries the same line verbatim), one more
    ordinary commit (so HEAD^ never touches the intent path itself and
    `check_close_commit_shape` stays untouched), then a branch-end round 3
    with one reader. Returns (repo, reviewed_sha of the final ordinary
    commit)."""
    repo = _seed_branch(tmp_path)
    _write(repo, f"docs/loom/intent/{change_id}.md",
           _lane_intent_text(change_id, lane_line=None))
    _write_kickoff(repo)
    _write(repo, "docs/notes.md", "wave-end:1 delta\n")
    _write(repo, "loom-code/skills/example/SKILL.md", "---\nname: example\n---\nbody\n")
    _write_evidence(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat(loom-code): wave-end:1 delta\n\nTask: T1")

    switch_line = f"lane: express — switched 2026-09-05 by kouko, from {from_marker}"
    text = (repo / f"docs/loom/intent/{change_id}.md").read_text(encoding="utf-8")
    text = text.replace(
        "needs-design: no — no interface surface touched\n",
        "needs-design: no — no interface surface touched\n" + switch_line + "\n",
    )
    (repo / f"docs/loom/intent/{change_id}.md").write_text(text, encoding="utf-8")
    git(repo, "add", f"docs/loom/intent/{change_id}.md")
    git(repo, "commit", "-q", "-m", f"docs(loom): switch lane\n\n{switch_line}")

    # One more ordinary commit so HEAD^ (of the final review-only commit)
    # never itself touches the intent path -- otherwise
    # `check_close_commit_shape` would try to read it as a close commit.
    _write(repo, "docs/more-notes.md", "after the switch\n")
    git(repo, "add", "docs/more-notes.md")
    git(repo, "commit", "-q", "-m", "docs: after the switch\n\nTask: T1")
    reviewed_sha = git(repo, "rev-parse", "HEAD")
    return repo, reviewed_sha


def _mid_flight_switch_review(reviewed_sha: str) -> dict:
    return {
        "reviewed_sha": reviewed_sha,
        "scope": "branch-end",
        "vendors": ["anthropic"],
        "verdicts": [
            _verdict("r1", 1, "wave-end:1", reviewed_sha),
            _verdict("r2", 1, "wave-end:1", reviewed_sha),
            _verdict("r1", 2, "wave-end:1", reviewed_sha),
            _verdict("r2", 2, "wave-end:1", reviewed_sha),
            _verdict("r3", 3, "branch-end", reviewed_sha),
        ],
        "probes": [_package_tests_record(reviewed_sha), *_adversarial_records(reviewed_sha)],
        "open_findings": [],
        "dispatch": [
            _dispatch("implementer", "agent-imp", "T1"),
            _dispatch("reviewer", "r1"),
            _dispatch("reviewer", "r2"),
            _dispatch("reviewer", "r3"),
        ],
    }


def test_push_mid_flight_switch_before_current_round_single_reader_passes(
    tmp_path: Path,
) -> None:
    """`from round 2`: the switch takes effect for every round strictly
    after round 2, so round 3 (the current, branch-end round) already
    runs express -- one reader must pass. RED today: `push` reads no
    `lane:` line at all, so round 3's one reader is blocked against the
    still-recomputed full lane."""
    change_id = "2026-09-05-lane-e1"
    repo, reviewed_sha = _mid_flight_switch_repo(
        tmp_path, change_id=change_id, from_marker="round 2"
    )
    review_rel = _write_review(repo, change_id, _mid_flight_switch_review(reviewed_sha))
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, (
        "a switch `from round 2` should let round 3's one reader pass; "
        f"blocked instead: {result.stderr}"
    )


def test_push_mid_flight_switch_after_current_round_single_reader_blocked(
    tmp_path: Path,
) -> None:
    """`from round 3`: the switch takes effect only for rounds strictly
    after round 3, so round 3 ITSELF still runs under the pre-switch full
    lane -- one reader must stay blocked. GREEN today and must stay GREEN
    (the mirror of the case above): today's checker blocks unconditionally
    for the same reason, and the future lane-aware checker must still
    block here because round 3 is not yet past the declared switch point."""
    change_id = "2026-09-05-lane-e2"
    repo, reviewed_sha = _mid_flight_switch_repo(
        tmp_path, change_id=change_id, from_marker="round 3"
    )
    review_rel = _write_review(repo, change_id, _mid_flight_switch_review(reviewed_sha))
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode != 0, (
        "a switch `from round 3` must not apply to round 3 itself; one "
        "reader should stay blocked"
    )
    assert "push.verdicts-ge-2" in blocked_rules(result)


# =============================================================================
# (f) the switch commit's message lacks the `lane:` line -> `intent`
# subcommand must block, mirroring check_needs_design_reason's mechanism.
# RED today: FRONTMATTER_DECISION only covers `status:`/`needs-design:`.
# =============================================================================


def test_intent_switch_commit_message_missing_lane_line_blocked(tmp_path: Path) -> None:
    """The commit that introduces `lane: express` must carry that exact
    line in its own commit message (the same discipline
    `check_needs_design_reason` applies to `needs-design:`) -- a commit
    whose message omits it must block `loom_checker.py intent <path>`."""
    repo = make_intent_repo(tmp_path)
    change_id = "2026-09-05-lane-f"
    intent_rel = f"docs/loom/intent/{change_id}.md"
    _write(
        repo, intent_rel,
        _lane_intent_text(change_id, lane_line="lane: express — declared 2026-09-05 by kouko"),
    )
    git(repo, "add", intent_rel)
    # Carries `needs-design:` verbatim (that mechanism's own requirement,
    # unrelated to this probe) but deliberately omits `lane: express`.
    message = (
        "docs(loom): add an intent\n\n"
        "needs-design: no — no interface surface touched"
    )
    git(repo, "commit", "-q", "-m", message)

    result = run_checker("intent", str(repo / intent_rel), cwd=repo)
    assert result.returncode != 0, (
        "a commit introducing `lane: express` without carrying that line "
        "verbatim in its own message must block the `intent` subcommand"
    )


# =============================================================================
# (g) a `lane:` switch line without `by <name>` -> intent schema blocks.
# RED today: the manifest declares no `lane` field at all, so
# check_intent_schema never looks at it.
# =============================================================================


def test_intent_lane_switch_line_without_by_name_blocked(tmp_path: Path) -> None:
    """A switch-form `lane:` line missing `by <name>` -- who switched it is
    unrecoverable -- must block `intent`'s schema check."""
    repo = make_intent_repo(tmp_path)
    change_id = "2026-09-05-lane-g"
    intent_rel = f"docs/loom/intent/{change_id}.md"
    lane_line = "lane: express — switched 2026-09-05, from round 2"
    text = _lane_intent_text(change_id, lane_line=lane_line)
    _write(repo, intent_rel, text)
    git(repo, "add", intent_rel)
    # Carries both `needs-design:` (that mechanism's own requirement) and
    # the `lane:` line verbatim, so only the missing `by <name>` is under
    # test here.
    message = (
        "docs(loom): add an intent\n\n"
        "needs-design: no — no interface surface touched\n"
        f"{lane_line}"
    )
    git(repo, "commit", "-q", "-m", message)

    result = run_checker("intent", str(repo / intent_rel), cwd=repo)
    assert result.returncode != 0, (
        "a switch-form `lane:` line missing `by <name>` must block the "
        "intent schema check"
    )


# =============================================================================
# (h) GREEN pin: the rule count is unchanged by this adversary-first probe
# file. A real rule change belongs to W1-01/W1-02, not to this file.
# =============================================================================


def test_list_rules_count_pinned_at_twenty_seven() -> None:
    """`--list-rules` prints exactly 27 lines today; this probe file adds
    no rule of its own, so the count must not move yet."""
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--list-rules"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, result.stderr
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) == 27, f"expected 27 rules, saw {len(lines)}:\n{result.stdout}"


# =============================================================================
# (i) `default-lane: express` in KICKOFF, no `lane:` in the intent, a pure
# docs delta -> one reader must pass; the mirror `default-lane: gate-only`
# with a skill delta must stay blocked.
# =============================================================================


def test_push_default_lane_express_no_intent_lane_docs_delta_single_reader_passes(
    tmp_path: Path,
) -> None:
    """KICKOFF declares `default-lane: express` and the intent carries no
    `lane:` line at all; the delta is pure docs -- one reader must pass
    once the repo default is honoured. RED today: KICKOFF-DEFAULTS.md is a
    standing document, and touching it always forces the full lane
    (`change_lane_detail`'s docstring), so one reader is blocked before
    the repo default can ever be read for lane purposes."""
    repo = _seed_branch(tmp_path)
    change_id = "2026-09-05-lane-i1"
    _commit_intent(repo, change_id, lane_line=None)
    _write_kickoff(repo, extra_lines=(
        "- default-lane: express — repo defaults to a light reader floor (2026-09-05)",
    ))
    _write_evidence(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs(loom): declare the repo default lane")
    reviewed_sha = git(repo, "rev-parse", "HEAD")

    body = {
        "reviewed_sha": reviewed_sha,
        "scope": "branch-end",
        "vendors": ["anthropic"],
        "verdicts": [_verdict("agent-rev", 1, "branch-end", reviewed_sha)],
        "probes": [_package_tests_record(reviewed_sha), *_adversarial_records(reviewed_sha)],
        "open_findings": [],
        "dispatch": [_dispatch("reviewer", "agent-rev")],
    }
    review_rel = _write_review(repo, change_id, body)
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, (
        "`default-lane: express` with no declared `lane:` should let one "
        f"reader pass a docs-only delta; blocked instead: {result.stderr}"
    )


def test_push_default_lane_gate_only_skill_delta_blocked(tmp_path: Path) -> None:
    """The mirror of the case above: KICKOFF declares `default-lane:
    gate-only`, but the delta ALSO carries a SKILL.md path -- gate-only is
    ineligible for a skill-typed delta (same rule as case (d)), so one
    reader must stay blocked. GREEN today and must stay GREEN."""
    repo = _seed_branch(tmp_path)
    change_id = "2026-09-05-lane-i2"
    _commit_intent(repo, change_id, lane_line=None)
    _write_kickoff(repo, extra_lines=(
        "- default-lane: gate-only — repo defaults to no reviewer (2026-09-05)",
    ))
    _write(repo, "loom-code/skills/example/SKILL.md", "---\nname: example\n---\nbody\n")
    _write_evidence(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat(loom-code): a skill delta\n\nTask: T1")
    reviewed_sha = git(repo, "rev-parse", "HEAD")

    body = {
        "reviewed_sha": reviewed_sha,
        "scope": "branch-end",
        "vendors": ["anthropic"],
        "verdicts": [_verdict("agent-rev", 1, "branch-end", reviewed_sha)],
        "probes": [_package_tests_record(reviewed_sha), *_adversarial_records(reviewed_sha)],
        "open_findings": [],
        "dispatch": [
            _dispatch("implementer", "agent-imp", "T1"),
            _dispatch("reviewer", "agent-rev"),
        ],
    }
    review_rel = _write_review(repo, change_id, body)
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode != 0, (
        "a skill-typed delta must force the full lane and stay blocked "
        "with one reader, whatever `default-lane:` declares"
    )
    assert "push.verdicts-ge-2" in blocked_rules(result)
