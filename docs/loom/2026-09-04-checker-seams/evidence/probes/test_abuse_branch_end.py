"""Adversarial probes for the branch-end checkpoint of 2026-09-04-checker-seams
(full lane). Written by the adversary agent per the branch-end dispatch, not
by whoever implemented W0-03/W1-01/W1-02/W1-03/W1-04 -- reviewer/adversary ne
implementer.

Case (1) turns the Codex reader's wave-end finding 05 into an executable
probe: a side-branch, single-parent commit whose subject ends ` (#1)` that
gets merged into `main` with `--no-ff` must still be BLOCKED by
`intent.needs-design-reason`. This is a DIFFERENT shape from
`test_abuse_squash_needs_design.py::test_fake_squash_subject_off_main_still_blocked`,
which keeps the fake commit off `main`'s history entirely (asserts
`merge-base --is-ancestor` fails). Here the fake commit IS reachable from
`main` (it is merged in) but is NOT on `main`'s first-parent chain -- the
exact distinction `_squash_note()`'s docstring calls "reachable... but
never walked by a first-parent traversal". No probe exercised that specific
git topology before this file; without it, `_squash_note()`'s choice of
`git rev-list --first-parent <candidate>` MEMBERSHIP over
`merge-base --is-ancestor` REACHABILITY was argued in prose only, not
proven by a case that would actually tell the two apart.

Cases (2)-(6) attack W1-03 (KICKOFF second-vendor ask, the codex mirror,
plugin versions, CHANGELOGs) and (7) is an executable grep for W1-01 (the
deleted script leaves no live reference). Case (8) is a byte-mutation
sensitivity check on the mirror-equality comparison itself, proving it is
not vacuously green.

The six attack-catalogue classes applied to the two W1 skill-text edits
(ship SKILL.md `loom-code/skills/ship/SKILL.md:175-180`, build SKILL.md
`loom-code/skills/build/SKILL.md:101-118`) -- these are cold-read attempts
against prose, not runnable probes, so they are recorded here as one line
each rather than as pytest cases:

* forge an artifact the gate trusts -- N/A to both paragraphs: neither
  names a machine-checked gate a forged artifact could fool (per
  CLAUDE.md `散文不當閘`, only `<!-- gate: <id> -->`-marked prose is a
  gate, and neither paragraph carries that marker); held only in the
  sense that there is nothing here to forge.
* bypass a gate by editing its input -- REPRODUCED against the ship
  paragraph: "whenever no existing test in that directory shares a
  probe's test-function name" dedups by FUNCTION NAME ONLY, not content.
  A permanent test with the same name as a future probe (accidental
  collision, or planted) silently drops that probe from graduating with
  no error -- the paragraph never says to diff bodies or flag a
  same-name/different-body collision. Reproduced as a real duplicate-name
  scenario in case (9) below (not a checker call, since this is prose
  process text with no CLI to invoke -- the "gate" here is the ship
  station's own read of the directory, so "running" the attack means
  constructing the exact directory state the instruction describes and
  showing its literal reading silently skips the file).
* replay a stale artifact -- N/A: neither paragraph reads a
  freshness-checked record.
* cross a trust boundary -- held-by-absence for the build paragraph
  (single repo, single process, no worktree/cwd claim made); the ship
  paragraph's graduation copy has no boundary either (same repo).
* self-exempt via a prose condition -- REPRODUCED against the build
  paragraph: "a task whose 檔 paths map to the `code` or `gate` artifact
  type is adversary-first... dispatch `loom-code:adversary` before the
  implementer" has no checker-side order enforcement --
  `check_dispatch_covers_tasks` (loom_checker.py:3142) verifies dispatch
  *coverage*, never dispatch *sequence*. An implementer-first task on a
  full-lane `code`/`gate` path, recorded honestly in `dispatch[]`, passes
  `push` exactly as an adversary-first one does. This matches the
  project's own stated convention (prose is not a gate unless marked) so
  it is reported as a low-severity finding, not a surprise -- but the
  paragraph's own stated rationale ("independent adversarial tests catch
  false passes the implementing agent's own tests miss") is exactly the
  property that goes unenforced.
* race a concurrent writer -- held-by-absence for the build paragraph (no
  shared mutable state named); REPRODUCED as a real gap for the ship
  paragraph: the graduation copy step names no protocol for two changes'
  copy steps landing on the same permanent-test path in the same window
  (this dispatch's own trap-guard -- "another agent may commit a report
  file concurrently... commit with the explicit path" -- is exactly this
  risk, and the paragraph is silent on it).

No mutation/fuzz tool is declared for this repo, so this file is the
required executable abuse/boundary cases (9 here, floor is 3). Every
fixture that touches git topology runs the real `loom_checker.py intent`
subcommand via subprocess against a real git repo, per
`test_abuse_squash_needs_design.py`'s established pattern; the W1-03
second-vendor cases reuse `test_loom_checker_push.py`'s own `_lane_push_repo`
fixture (imported, not reimplemented) so the full `push` pipeline -- lane
recompute, review schema, dispatch checks -- runs for real rather than
being mocked.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT / "loom-code" / "scripts"))

import loom_checker  # noqa: E402 -- the module under attack
from test_loom_checker_push import (  # noqa: E402 -- reuse, don't reimplement
    _lane_push_repo,
    _ONE_ANTHROPIC_VERDICT,
    _TWO_ANTHROPIC_VERDICTS,
)

CHECKER = REPO_ROOT / "loom-code" / "scripts" / "loom_checker.py"
CHECKER_SOURCE = REPO_ROOT / "loom-code" / "scripts" / "loom_checker.py"
CHECKER_MIRROR = REPO_ROOT / ".codex" / "hooks" / "loom_checker.py"


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


INTENT_TEXT = """# {title}
originator: kouko
kind: product
needs-design: yes — {reason}
status: confirmed {date}

## Problem
people cannot see something they need to see.

## Proposed outcome
show it to them plainly.

## Acceptance
1. it works.

## Constraints
- none

## Out of scope
- none

## Open questions
- none
"""


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    git(repo, "add", "seed.txt")
    git(repo, "commit", "-q", "-m", "seed")
    return repo


def _intent_relpath(change_id: str) -> str:
    return f"docs/loom/intent/{change_id}.md"


def _write_intent_on_branch(
    repo: Path, change_id: str, *, reason: str, commit_message: str
) -> None:
    path = repo / _intent_relpath(change_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        INTENT_TEXT.format(title=change_id, reason=reason, date=change_id[:10]),
        encoding="utf-8",
    )
    git(repo, "add", _intent_relpath(change_id))
    git(repo, "commit", "-q", "-m", commit_message)


# --- (1) finding-05: fake-squash commit MERGED into main, off first-parent -


def test_fake_squash_subject_merged_into_main_still_blocked(tmp_path: Path) -> None:
    """Codex wave-end reader finding 05: a side-branch single-parent commit
    whose subject ends ` (#1)` (fake squash shape) that reaches `main` via a
    real `--no-ff` merge must still be BLOCKED -- it IS an ancestor of
    `main` (unlike test_abuse_squash_needs_design.py's off-main case) but
    is NOT on `main`'s first-parent chain, which is the only membership
    `_squash_note()` checks. If `_squash_note()` used
    `merge-base --is-ancestor` instead of first-parent-chain MEMBERSHIP,
    this exact case would wrongly PASS. Failure here means the topology
    check regressed from membership back to reachability."""
    repo = _init_repo(tmp_path)
    change_id = "2099-03-06-fake-squash-merged"
    git(repo, "checkout", "-q", "-b", "feature")
    _write_intent_on_branch(
        repo,
        change_id,
        reason="new page for the team to see something",
        # Fake squash shape: single parent, subject ends ` (#<n>)`, but the
        # message body never carries the needs-design line -- exactly the
        # attack, planted on the commit that actually decides the line.
        commit_message=f"docs(loom): intent {change_id} confirmed (#1)",
    )
    feature_sha = git(repo, "rev-parse", "HEAD")
    assert len(git(repo, "log", "-1", "--pretty=%P").split()) == 1  # single parent

    git(repo, "checkout", "-q", "main")
    git(
        repo,
        "merge",
        "--no-ff",
        "feature",
        "-q",
        "-m",
        f"Merge pull request #1 from x/feature (#1)",
    )
    # Reachable from main now (unlike the off-main case) --
    is_ancestor = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", feature_sha, "HEAD"]
    ).returncode
    assert is_ancestor == 0  # IS an ancestor of main -- this is the whole point
    # -- but NOT on main's first-parent chain:
    first_parent_chain = git(repo, "rev-list", "--first-parent", "HEAD").split()
    assert feature_sha not in first_parent_chain

    result = run_checker("intent", _intent_relpath(change_id), cwd=repo)
    assert result.returncode == 1, (
        "fake-squash commit merged into main but off the first-parent chain "
        f"was NOT blocked: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "intent.needs-design-reason" in blocked_rules(result)


# --- (8) mirror-equality comparison is not vacuous --------------------------


def test_mirror_equality_check_is_sensitive_to_a_single_byte(tmp_path: Path) -> None:
    """Attack test_codex_mirror_matches_checker.py's own comparison: prove a
    one-byte mutation of a COPY of the mirror actually flips the assertion,
    so that test is not silently green regardless of content (e.g. from a
    line-count-only check, or comparing a file to itself by accident)."""
    source_lines = CHECKER_SOURCE.read_text(encoding="utf-8").splitlines(keepends=True)
    mirror_lines = CHECKER_MIRROR.read_text(encoding="utf-8").splitlines(keepends=True)
    assert len(mirror_lines) == len(source_lines) + 1

    at = 1 if source_lines and source_lines[0].startswith("#!") else 0
    rebuilt = mirror_lines[:at] + mirror_lines[at + 1 :]
    assert rebuilt == source_lines  # the real comparison holds at HEAD today

    mutated = tmp_path / "mirror_mutated.py"
    mutated_lines = list(mirror_lines)
    # Flip one byte deep in a body line (not the stamp line at `at`, not a
    # trailing newline-only line) so the mutation is real content drift.
    target_index = next(
        i for i in range(at + 1, len(mutated_lines)) if mutated_lines[i].strip()
    )
    original_line = mutated_lines[target_index]
    mutated_lines[target_index] = "#" + original_line
    mutated.write_text("".join(mutated_lines), encoding="utf-8")

    reread = mutated.read_text(encoding="utf-8").splitlines(keepends=True)
    rebuilt_from_mutant = reread[:at] + reread[at + 1 :]
    assert rebuilt_from_mutant != source_lines, (
        "a one-byte mutation of the mirror did not flip the equality check -- "
        "the comparison is vacuous"
    )


# --- (2)-(4) W1-03: second-vendor ask, through the real push pipeline ------


def test_second_vendor_ask_missing_answer_blocks_full_lane(tmp_path: Path) -> None:
    repo = _lane_push_repo(
        tmp_path,
        files={"loom-code/scripts/adv_ask_missing.py": "x = 1\n"},
        kickoff_lines=[
            "- second-vendor: ask — trial (2026-09-04)",
            "- docs-lint: none — not adopted (2026-09-04)",
        ],
        verdicts=_TWO_ANTHROPIC_VERDICTS,
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.second-vendor-honoured" in blocked_rules(result)


def test_second_vendor_ask_answer_none_passes(tmp_path: Path) -> None:
    repo = _lane_push_repo(
        tmp_path,
        files={"loom-code/scripts/adv_ask_none.py": "x = 1\n"},
        kickoff_lines=[
            "- second-vendor: ask — trial (2026-09-04)",
            "- docs-lint: none — not adopted (2026-09-04)",
        ],
        verdicts=_TWO_ANTHROPIC_VERDICTS,
        review_overrides={"second_vendor": "none"},
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


def test_second_vendor_ask_hostile_whitespace_value_blocks(tmp_path: Path) -> None:
    """Boundary/hostile input: a `second_vendor` answer that is present but
    pure whitespace must be treated as no answer (blocked), not silently
    accepted as truthy JSON content."""
    repo = _lane_push_repo(
        tmp_path,
        files={"loom-code/scripts/adv_ask_ws.py": "x = 1\n"},
        kickoff_lines=[
            "- second-vendor: ask — trial (2026-09-04)",
            "- docs-lint: none — not adopted (2026-09-04)",
        ],
        verdicts=_TWO_ANTHROPIC_VERDICTS,
        review_overrides={"second_vendor": "   "},
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.second-vendor-honoured" in blocked_rules(result)


# --- (5) KICKOFF-DEFAULTS.md declares `ask` on this repo --------------------


def test_kickoff_defaults_second_vendor_is_ask() -> None:
    text = (REPO_ROOT / "docs/loom/KICKOFF-DEFAULTS.md").read_text(encoding="utf-8")
    match = re.search(r"^- second-vendor:\s*(.+)$", text, re.MULTILINE)
    assert match is not None
    assert match.group(1).strip().startswith("ask")


# --- (6) plugin versions and CHANGELOG headings -----------------------------


def test_loom_code_version_is_1_2_0() -> None:
    import json as _json

    manifest = _json.loads(
        (REPO_ROOT / "loom-code/.claude-plugin/plugin.json").read_text(encoding="utf-8")
    )
    assert manifest["version"] == "1.2.0"
    changelog = (REPO_ROOT / "loom-code/CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [1.2.0]" in changelog


def test_loom_design_version_is_1_0_3() -> None:
    import json as _json

    manifest = _json.loads(
        (REPO_ROOT / "loom-design/.claude-plugin/plugin.json").read_text(encoding="utf-8")
    )
    assert manifest["version"] == "1.0.3"
    changelog = (REPO_ROOT / "loom-design/CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [1.0.3]" in changelog


# --- (7) W1-01: the deleted script leaves no live reference -----------------


def test_check_open_questions_referenced_nowhere_outside_history() -> None:
    result = subprocess.run(
        ["grep", "-rln", "check_open_questions", str(REPO_ROOT)],
        capture_output=True,
        text=True,
    )
    hits = [
        line
        for line in result.stdout.splitlines()
        if line.strip()
        and "/docs/loom/" not in line
        and not line.endswith("CHANGELOG.md")
        and "/.git/" not in line
        and "/.pytest_cache/" not in line
        and "/__pycache__/" not in line
        and ".pyc" not in line
        # this file legitimately names the deleted script -- it is the
        # regression test proving it stays gone (W1-01's own new test).
        and "test_no_stale_open_questions_script" not in line
    ]
    assert hits == [], f"live references to check_open_questions remain: {hits}"


# --- (9) ship graduation copy: same test-function-name collision -----------


def test_graduation_dedup_by_function_name_silently_skips_different_body(
    tmp_path: Path,
) -> None:
    """Attack on the ship SKILL.md graduation paragraph (cold-read, not a
    checker call -- there is no CLI for this step): the instruction dedups
    "whenever no existing test in that directory shares a probe's
    test-function name". Construct the exact directory state the paragraph
    describes -- a permanent test with the same function name as a new
    probe but a DIFFERENT body -- and show the literal instruction, applied
    as written, tells the operator to skip copying the new probe. That is a
    real gap: a genuinely new regression case is silently dropped, not
    flagged for human judgment, because the rule reads names only."""
    permanent_dir = tmp_path / "permanent"
    permanent_dir.mkdir()
    evidence_dir = tmp_path / "evidence" / "probes"
    evidence_dir.mkdir(parents=True)

    (permanent_dir / "test_widget.py").write_text(
        "def test_widget_rejects_empty_input():\n"
        "    assert True  # old case: empty string\n",
        encoding="utf-8",
    )
    (evidence_dir / "test_widget_probe.py").write_text(
        "def test_widget_rejects_empty_input():\n"
        "    # NEW case: empty BYTES, not empty string -- a different attack\n"
        "    assert True\n",
        encoding="utf-8",
    )

    def function_names(path: Path) -> set[str]:
        return set(re.findall(r"^def (test_\w+)\(", path.read_text(encoding="utf-8"), re.M))

    existing_names = set()
    for existing in permanent_dir.glob("*.py"):
        existing_names |= function_names(existing)

    would_copy = [
        probe
        for probe in evidence_dir.glob("*.py")
        if not (function_names(probe) & existing_names)
    ]
    assert would_copy == [], (
        "the name-only dedup, applied literally, silently drops a "
        "different-bodied probe that shares a permanent test's function "
        "name -- reported as a finding against the ship SKILL.md paragraph"
    )
