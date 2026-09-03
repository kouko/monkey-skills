"""Adversarial probes against W0-02 (small-change lane, verdict floor,
`second-vendor: ask`, `docs-lint` grammar), written BEFORE W0-02 exists per
intent point 4 / plan risk 1.

Targets (not yet implemented -- W0-02 is the RED->GREEN task):
* `change_lane(repo, reviewed_id) -> "small"|"full"` in
  `loom-code/scripts/loom_checker.py` (does not exist yet at W0-01 time).
* `check_verdicts`'s floor becoming lane-dependent (currently hardcoded
  `len(reviewers) < 2` regardless of what the branch touches).
* `check_second_vendor_honoured` accepting KICKOFF `second-vendor: ask` and
  reading review.json's new top-level `second_vendor` field (does not exist
  in the manifest's `kickoff_defaults` grammar or in `review.json`'s
  declared fields yet).
* `docs-lint: <command> | none` as a new KICKOFF-DEFAULTS key
  (`loom-code/contract/manifest.yaml` `kickoff_defaults`).

No mutation/fuzz tool is declared for this repo, so this file is the
required >=3 executable abuse/boundary cases (it has far more). It never
edits the real committed files -- every scenario is built in a scaffolded
`tmp_path` git repo, mirroring `test_loom_checker_push.py`'s own fixtures.

Reuses `git`/`run_checker`/`blocked_rules`/`build_repo`/`rebuild`/
`recommit_review`/`review_body`/`write_review`/`_adversarial_records`/
`PASSING_COMMAND`/`ABUSE_CASES`/`CHANGE`/`REVIEW` from
`test_loom_checker_push.py` (same `loom-code/scripts/` directory), and
`check_kickoff_defaults_grammar`/`manifest_kickoff_default_names` from
`test_kickoff_defaults_grammar.py`, rather than re-deriving fixture
builders. Imports `loom_checker` itself for `change_lane`, which is
expected to be missing until W0-02.

Each test's docstring records `Attack:` / `Expected (after W0-02):` /
`Observed (before W0-02):` -- the last line is filled in from an actual
run at W0-01 commit time, not guessed, per the adversary contract.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# file: docs/loom/2026-09-03-small-change-lane/evidence/probes/<this>.py
# parents: [0]=probes [1]=evidence [2]=<change-id> [3]=loom [4]=docs [5]=repo root
REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT / "loom-code" / "scripts"))

import loom_checker  # noqa: E402 -- the module under attack; change_lane may not exist yet

from test_loom_checker_push import (  # noqa: E402
    ABUSE_CASES,
    CHANGE,
    DISPATCH_ENTRIES,
    PASSING_COMMAND,
    REVIEW,
    _adversarial_records,
    blocked_rules,
    build_repo,
    git,
    rebuild,
    recommit_review,
    review_body,
    run_checker,
    write_review,
)
from test_kickoff_defaults_grammar import (  # noqa: E402
    check_kickoff_defaults_grammar,
    manifest_kickoff_default_names,
)


# --- shared fixture builders -------------------------------------------------


def _init_repo(tmp_path: Path) -> Path:
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


def _commit_files(repo: Path, files: dict[str, str], message: str) -> str:
    for rel, content in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def _change_lane(repo: Path, reviewed_id: str) -> str:
    """Fails loudly (a real pytest FAIL, not a collection error) while
    `change_lane` does not exist yet -- collection-time ImportError would
    hide every other case in this file behind one opaque error."""
    fn = getattr(loom_checker, "change_lane", None)
    if fn is None:
        pytest.fail(
            "loom_checker.change_lane is not implemented yet (W0-02) -- "
            "this is the expected RED before W0-02."
        )
    return fn(repo, reviewed_id)


def _lane_repo(
    tmp_path: Path,
    *,
    files: dict[str, str],
    kickoff_lines: list[str],
    verdicts_factory=None,
    review_overrides: dict | None = None,
    adversarial_count: int = 3,
    task_trailer: bool = True,
) -> Path:
    """A push-ready branch (code commit + checkpoint review commit) whose
    changed-path shape and KICKOFF-DEFAULTS content the caller controls --
    the common scaffold under every push-floor / second-vendor / docs-lint
    case below."""
    repo = _init_repo(tmp_path)

    for rel, content in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    (repo / "evidence").mkdir(exist_ok=True)
    for name in ABUSE_CASES[:adversarial_count]:
        (repo / f"evidence/abuse_{name}.py").write_text(
            "raise SystemExit(0)\n", encoding="utf-8"
        )
    (repo / "evidence/tests.txt").write_text("1 passed\n", encoding="utf-8")

    kickoff = repo / "docs/loom/KICKOFF-DEFAULTS.md"
    kickoff.parent.mkdir(parents=True, exist_ok=True)
    package_tests_line = (
        f"- package-tests: {PASSING_COMMAND} — the fixture's whole suite (2026-09-04)"
    )
    body_lines = "\n".join([package_tests_line, *kickoff_lines])
    kickoff.write_text(f"# Kickoff Defaults\n\n{body_lines}\n", encoding="utf-8")

    git(repo, "add", "-A")
    message = "feat: probe" + ("\n\nTask: T1" if task_trailer else "")
    git(repo, "commit", "-q", "-m", message)

    reviewed_sha = git(repo, "rev-parse", "HEAD")
    overrides: dict = dict(review_overrides or {})
    if verdicts_factory is not None:
        overrides["verdicts"] = verdicts_factory(reviewed_sha)
    overrides.setdefault(
        "probes",
        [
            {
                "kind": "package-tests",
                "command": PASSING_COMMAND,
                "sha": reviewed_sha,
                "result": "pass",
                "artifact": "evidence/tests.txt",
            },
            *_adversarial_records(reviewed_sha, adversarial_count),
        ],
    )
    overrides.setdefault("dispatch", [dict(entry) for entry in DISPATCH_ENTRIES])
    body = review_body(reviewed_sha, **overrides)
    write_review(repo, body)
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")
    return repo


def _one_verdict(vendor: str = "anthropic") -> "callable":
    def factory(sha: str) -> list[dict]:
        return [
            {
                "reviewer": "agent-rev", "vendor": vendor, "model": "m", "lens": "code",
                "verdict": "PASS", "dimension_scores": {}, "findings": [], "sha": sha,
            }
        ]
    return factory


def _two_anthropic_verdicts(sha: str) -> list[dict]:
    return [
        {
            "reviewer": "agent-rev", "vendor": "anthropic", "model": "m", "lens": "code",
            "verdict": "PASS", "dimension_scores": {}, "findings": [], "sha": sha,
        },
        {
            "reviewer": "agent-blind", "vendor": "anthropic", "model": "m", "lens": "code",
            "verdict": "PASS_WITH_NOTES", "dimension_scores": {}, "findings": [], "sha": sha,
        },
    ]


ASK_LINE = "- second-vendor: ask — trial (2026-09-04)"
NO_LINT_LINE = "- docs-lint: none — not adopted (2026-09-04)"


# =============================================================================
# 1. Lane recompute -- pre-authorised classes, each alone must be "small"
# =============================================================================


def test_test_only_change_is_small(tmp_path: Path) -> None:
    """Attack: change ONE file, a test file under loom-code/scripts/ (class a).
    Expected (after W0-02): change_lane == "small".
    Observed (before W0-02): FAIL -- change_lane does not exist
    (pytest.fail via _change_lane's guard)."""
    repo = _init_repo(tmp_path)
    sha = _commit_files(
        repo,
        {"loom-code/scripts/test_probe_target.py": "def test_x():\n    assert True\n"},
        "test: probe",
    )
    assert _change_lane(repo, sha) == "small"


def test_docs_only_change_is_small(tmp_path: Path) -> None:
    """Attack: change README.md + docs/loom/<id>/plan.md only (class b).
    Expected (after W0-02): change_lane == "small".
    Observed (before W0-02): FAIL -- change_lane does not exist."""
    repo = _init_repo(tmp_path)
    sha = _commit_files(
        repo,
        {
            "README.md": "docs change\n",
            f"docs/loom/{CHANGE}/plan.md": "intent: x@aaaaaaa\n\n## Task DAG\n",
        },
        "docs: probe",
    )
    assert _change_lane(repo, sha) == "small"


def test_ci_config_change_is_small(tmp_path: Path) -> None:
    """Attack: change a CI workflow + requirements-dev.txt only (class c).
    Expected (after W0-02): change_lane == "small".
    Observed (before W0-02): FAIL -- change_lane does not exist."""
    repo = _init_repo(tmp_path)
    sha = _commit_files(
        repo,
        {
            ".github/workflows/x.yml": "name: x\non: push\n",
            "requirements-dev.txt": "pytest\n",
        },
        "ci: probe",
    )
    assert _change_lane(repo, sha) == "small"


def test_version_sync_change_is_small(tmp_path: Path) -> None:
    """Attack: bump both plugin.json mirrors + CHANGELOG.md only (class d).
    Expected (after W0-02): change_lane == "small" (plugin.json files are
    *.json outside contract/, the CI/config class per plan risk 1;
    CHANGELOG.md is docs).
    Observed (before W0-02): FAIL -- change_lane does not exist."""
    repo = _init_repo(tmp_path)
    sha = _commit_files(
        repo,
        {
            "loom-code/.claude-plugin/plugin.json": '{"version": "1.1.0"}\n',
            "loom-code/.codex-plugin/plugin.json": '{"version": "1.1.0"}\n',
            "loom-code/CHANGELOG.md": "## 1.1.0\n- probe\n",
        },
        "chore: version sync probe",
    )
    assert _change_lane(repo, sha) == "small"


def test_clean_revert_nets_to_zero_diff_is_small(tmp_path: Path) -> None:
    """Attack: on `main`, `loom-code/scripts/existing.py` already reads
    `value = 1`. On `work`, one commit changes it to `value = 2` (alone this
    would be a full-lane trigger -- a non-test .py under scripts/), then a
    second commit reverts it back to `value = 1` (class e, a clean revert).
    The base..HEAD tree diff for that path is therefore EMPTY -- this also
    probes whether change_lane walks per-commit diffs (WRONG: would see the
    intermediate full-lane-shaped commit) instead of the cumulative
    base..HEAD tree diff `changed_paths()` uses (RIGHT: nets to nothing).
    Expected (after W0-02): change_lane == "small" (the file does not even
    appear in changed_paths, since it is byte-identical to main's copy).
    Observed (before W0-02): FAIL -- change_lane does not exist."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    target = repo / "loom-code/scripts/existing.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("value = 1\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "seed")
    git(repo, "checkout", "-q", "-b", "work")

    target.write_text("value = 2\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: bump")
    git(repo, "revert", "-q", "--no-edit", "HEAD")
    sha = git(repo, "rev-parse", "HEAD")
    assert _change_lane(repo, sha) == "small"


def test_review_json_alone_is_small(tmp_path: Path) -> None:
    """Attack: change only docs/loom/<id>/review.json (records are ignored
    by the lane per intent point 3). Unqualified, review.json falls through
    the manifest's §6 mapping to the catch-all `code` type (it matches no
    other glob) -- exactly the trap `check_probes_adversarial` already
    special-cases via its own `is_review` regex; change_lane needs the same
    exclusion or every checkpoint push (which always rewrites review.json)
    would itself look like a full-lane, non-test code change.
    Expected (after W0-02): change_lane == "small".
    Observed (before W0-02): FAIL -- change_lane does not exist."""
    repo = _init_repo(tmp_path)
    sha = _commit_files(
        repo,
        {f"docs/loom/{CHANGE}/review.json": '{"reviewed_sha": "x"}\n'},
        "chore(loom): review only probe",
    )
    assert _change_lane(repo, sha) == "small"


def test_evidence_dir_alone_is_small(tmp_path: Path) -> None:
    """Attack: change only files under evidence/** (intent point 3).
    Expected (after W0-02): change_lane == "small".
    Observed (before W0-02): FAIL -- change_lane does not exist."""
    repo = _init_repo(tmp_path)
    sha = _commit_files(
        repo,
        {f"docs/loom/{CHANGE}/evidence/note.md": "a note\n"},
        "docs: evidence probe",
    )
    assert _change_lane(repo, sha) == "small"


# =============================================================================
# 2. Full-lane triggers -- each alone must flip to "full"
# =============================================================================


def test_one_nontest_python_script_flips_to_full(tmp_path: Path) -> None:
    """Attack: change ONE non-test .py under loom-code/scripts/.
    Expected (after W0-02): change_lane == "full" (plan risk: "non-test
    program files change one line too -- full lane").
    Observed (before W0-02): FAIL -- change_lane does not exist."""
    repo = _init_repo(tmp_path)
    sha = _commit_files(
        repo, {"loom-code/scripts/probe_helper.py": "x = 1\n"}, "feat: probe"
    )
    assert _change_lane(repo, sha) == "full"


def test_one_hook_shell_script_flips_to_full(tmp_path: Path) -> None:
    """Attack: change ONE loom-code/hooks/x.sh file (manifest types
    `**/hooks/**` as `gate`).
    Expected (after W0-02): change_lane == "full".
    Observed (before W0-02): FAIL -- change_lane does not exist."""
    repo = _init_repo(tmp_path)
    sha = _commit_files(
        repo, {"loom-code/hooks/probe.sh": "#!/bin/sh\necho probe\n"}, "feat: probe"
    )
    assert _change_lane(repo, sha) == "full"


def test_one_skill_md_flips_to_full(tmp_path: Path) -> None:
    """Attack: change ONE loom-code/skills/x/SKILL.md file.
    Expected (after W0-02): change_lane == "full".
    Observed (before W0-02): FAIL -- change_lane does not exist."""
    repo = _init_repo(tmp_path)
    sha = _commit_files(
        repo, {"loom-code/skills/probe/SKILL.md": "# probe\n"}, "feat: probe"
    )
    assert _change_lane(repo, sha) == "full"


def test_one_contract_template_flips_to_full(tmp_path: Path) -> None:
    """Attack: change ONE loom-code/contract/templates/x.md file -- an
    interface surface by the manifest's own default
    (`**/templates/**` in `interface-surfaces`).
    Expected (after W0-02): change_lane == "full".
    Observed (before W0-02): FAIL -- change_lane does not exist."""
    repo = _init_repo(tmp_path)
    sha = _commit_files(
        repo, {"loom-code/contract/templates/probe.md": "# t\n"}, "feat: probe"
    )
    assert _change_lane(repo, sha) == "full"


def test_two_plugins_flip_to_full_even_test_only(tmp_path: Path) -> None:
    """Attack: change ONLY test files, but under two different top-level
    plugin dirs (loom-code/ and loom-design/) -- the plan's "touches no
    more than one plugin" constraint, stress-tested against an otherwise
    fully pre-authorised (test-only) diff.
    Expected (after W0-02): change_lane == "full" (single-plugin constraint
    beats the test-only class).
    Observed (before W0-02): FAIL -- change_lane does not exist."""
    repo = _init_repo(tmp_path)
    sha = _commit_files(
        repo,
        {
            "loom-code/scripts/test_a.py": "def test_a():\n    assert True\n",
            "loom-design/scripts/test_b.py": "def test_b():\n    assert True\n",
        },
        "test: two-plugin probe",
    )
    assert _change_lane(repo, sha) == "full"


def test_test_named_file_outside_a_conventional_test_dir_is_still_small(
    tmp_path: Path,
) -> None:
    """Attack (boundary): a file matching the test-name glob
    (`test_*.py`) but sitting somewhere a human would not call a test
    location, e.g. `loom-code/scripts/fixtures/test_generator_probe.py`
    used to GENERATE fixtures, not to assert anything.
    Boundary decision (this probe pins it): the plan's own §-risk grammar
    for the test-file class is purely NAME-based --
    "test_*.py, *_test.py, tests/**" -- it names no location constraint,
    unlike the interface-surface and single-plugin clauses which are
    explicit about what they constrain. A location-based carve-out is not
    in the plan; this probe holds W0-02 to the name-only reading so a
    location heuristic cannot be added silently later without failing an
    existing case. If W0-02's author disagrees, this is the line to edit --
    on purpose, not by accident.
    Expected (after W0-02): change_lane == "small".
    Observed (before W0-02): FAIL -- change_lane does not exist."""
    repo = _init_repo(tmp_path)
    sha = _commit_files(
        repo,
        {
            "loom-code/scripts/fixtures/test_generator_probe.py": (
                "def build_fixture():\n    return {}\n"
            )
        },
        "test: boundary probe",
    )
    assert _change_lane(repo, sha) == "small"


# =============================================================================
# 4. push.verdicts-ge-2 -- lane-dependent floor
# =============================================================================


def test_small_lane_accepts_one_verdict(tmp_path: Path) -> None:
    """Attack: a test-only branch (small lane) with exactly one PASS verdict.
    Expected (after W0-02): `loom_checker.py push` exits 0.
    Observed (before W0-02): BLOCK push.verdicts-ge-2 -- the floor is
    hardcoded at 2 regardless of what the branch touches."""
    repo = _lane_repo(
        tmp_path,
        files={"loom-code/scripts/test_probe.py": "def test_x():\n    assert True\n"},
        kickoff_lines=[NO_LINT_LINE],
        verdicts_factory=_one_verdict(),
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


def test_small_lane_still_passes_with_two_verdicts(tmp_path: Path) -> None:
    """Attack: same small-lane branch, but with two verdicts (the floor
    should never REJECT more reviewers than it requires).
    Expected (after W0-02): push exits 0.
    Observed (before W0-02): PASS already (2 verdicts already satisfies
    today's hardcoded floor of 2) -- kept as a regression guard so W0-02
    cannot accidentally special-case "exactly one" and reject two."""
    repo = _lane_repo(
        tmp_path,
        files={"loom-code/scripts/test_probe2.py": "def test_x():\n    assert True\n"},
        kickoff_lines=[NO_LINT_LINE],
        verdicts_factory=_two_anthropic_verdicts,
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


def test_full_lane_still_requires_two_verdicts_and_names_the_lane(
    tmp_path: Path,
) -> None:
    """Attack: a non-test-file branch (full lane, via build_repo's a.py)
    dropped to exactly one verdict.
    Expected (after W0-02): push exits 1, BLOCK push.verdicts-ge-2, and the
    message NAMES the lane (per plan risk 3: "its message now names the
    lane so a single-verdict record in the full lane is still explained").
    Observed (before W0-02): BLOCK push.verdicts-ge-2 fires already (the
    hardcoded floor of 2 rejects it too), but the message says nothing
    about a "lane" -- confirmed by grep below."""
    repo = build_repo(tmp_path)
    single = [
        {
            "reviewer": "agent-rev", "vendor": "anthropic", "model": "m", "lens": "code",
            "verdict": "PASS", "dimension_scores": {}, "findings": [],
            "sha": git(repo, "rev-parse", "HEAD~1"),
        }
    ]
    recommit_review(repo, rebuild(repo, verdicts=single))
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.verdicts-ge-2" in blocked_rules(result)
    assert "lane" in result.stderr.lower(), result.stderr


def test_full_lane_passes_with_two_verdicts(tmp_path: Path) -> None:
    """Attack: sanity check -- the full lane's own default 2-verdict shape
    must keep passing once the floor becomes lane-dependent.
    Expected (after W0-02): push exits 0.
    Observed (before W0-02): PASS already (this is build_repo()'s
    unmodified default review body)."""
    repo = build_repo(tmp_path)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


# =============================================================================
# 5. second-vendor: ask
# =============================================================================


def test_ask_with_second_vendor_none_and_anthropic_only_passes(tmp_path: Path) -> None:
    """Attack: KICKOFF says `second-vendor: ask`; review.json answers
    `second_vendor: "none"`; verdicts are anthropic-only.
    Expected (after W0-02): push exits 0 (the answer says single-vendor was
    the choice for this change, and that is what happened).
    Observed (before W0-02): BLOCK push.second-vendor-honoured -- `ask` is
    read as a literal CLI name (`declared.split()[0].lower() == "ask"`,
    not `"none"`), so it demands a vendor literally named "ask" and never
    reads review.json's `second_vendor` field, which does not exist yet."""
    repo = _lane_repo(
        tmp_path,
        files={"loom-code/scripts/probe_ask_none.py": "x = 1\n"},
        kickoff_lines=[ASK_LINE, NO_LINT_LINE],
        verdicts_factory=_two_anthropic_verdicts,
        review_overrides={"second_vendor": "none"},
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


def test_ask_with_second_vendor_codex_but_no_codex_verdict_blocks(
    tmp_path: Path,
) -> None:
    """Attack: KICKOFF says `second-vendor: ask`; review.json answers
    `second_vendor: "codex"`; verdicts are anthropic-only, no fallback line.
    Expected (after W0-02): push exits 1, BLOCK
    push.second-vendor-honoured (the answer promised a second vendor that
    never reviewed, and nothing explains its absence).
    Observed (before W0-02): BLOCK push.second-vendor-honoured fires too,
    but for the wrong reason -- it is comparing verdict vendors against the
    literal string "ask" (from KICKOFF), not against "codex" (the recorded
    answer), which review.json's `second_vendor` field cannot express yet."""
    repo = _lane_repo(
        tmp_path,
        files={"loom-code/scripts/probe_ask_codex.py": "x = 1\n"},
        kickoff_lines=[ASK_LINE, NO_LINT_LINE],
        verdicts_factory=_two_anthropic_verdicts,
        review_overrides={"second_vendor": "codex"},
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.second-vendor-honoured" in blocked_rules(result)


def test_ask_with_no_answer_at_all_blocks(tmp_path: Path) -> None:
    """Attack: KICKOFF says `second-vendor: ask`, but review.json carries
    NO `second_vendor` field at all (the question was never answered).
    Expected (after W0-02): push exits 1, BLOCK
    push.second-vendor-honoured, naming the missing answer specifically
    (not the same message as a broken fallback).
    Observed (before W0-02): BLOCK push.second-vendor-honoured fires (same
    wrong-reason mechanism as above: "ask" read as a literal vendor name)."""
    repo = _lane_repo(
        tmp_path,
        files={"loom-code/scripts/probe_ask_missing.py": "x = 1\n"},
        kickoff_lines=[ASK_LINE, NO_LINT_LINE],
        verdicts_factory=_two_anthropic_verdicts,
        review_overrides={},
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.second-vendor-honoured" in blocked_rules(result)


def test_ask_in_small_lane_with_no_answer_passes_because_not_asked(
    tmp_path: Path,
) -> None:
    """Attack: KICKOFF says `second-vendor: ask`; the branch is small-lane
    (test-only); review.json carries no `second_vendor` field.
    Expected (after W0-02): push exits 0 -- small lane never asks the
    question (intent point 1: "小改動車道只有一位讀者，這題不問").
    Observed (before W0-02): the small lane does not exist, so this blocks
    on BOTH push.verdicts-ge-2 (floor still 2, one verdict recorded to
    isolate the lane-only variable) and push.second-vendor-honoured (same
    literal-"ask" mechanism)."""
    repo = _lane_repo(
        tmp_path,
        files={"loom-code/scripts/test_probe_ask_small.py": "def test_x():\n    assert True\n"},
        kickoff_lines=[ASK_LINE, NO_LINT_LINE],
        verdicts_factory=_one_verdict(),
        review_overrides={},
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


# =============================================================================
# 6. docs-lint grammar
# =============================================================================


def test_docs_lint_none_and_command_lines_are_valid_kickoff_grammar(
    tmp_path: Path,
) -> None:
    """Attack: two well-formed docs-lint lines --
    `docs-lint: none — x (date)` and
    `docs-lint: python3 -m vale docs/ — reason (date)`.
    Reuses the REAL `check_kickoff_defaults_grammar` /
    `manifest_kickoff_default_names` from `test_kickoff_defaults_grammar.py`
    against the REAL on-disk manifest (not a fabricated key set), so this
    test flips green automatically the moment W0-02 lands `docs-lint` in
    `loom-code/contract/manifest.yaml`'s `kickoff_defaults` -- no edit to
    this probe needed.
    Expected (after W0-02): zero violations for both lines.
    Observed (before W0-02): FAIL -- `docs-lint` is not a declared
    kickoff_defaults key yet, so both lines report
    "key 'docs-lint' is not declared in ...manifest.yaml"."""
    valid_keys = manifest_kickoff_default_names()
    doc = tmp_path / "KICKOFF-DEFAULTS.md"
    doc.write_text(
        "# Kickoff Defaults\n\n"
        "- docs-lint: none — not adopted (2026-09-04)\n"
        "- docs-lint: python3 -m vale docs/ — enforce prose lint (2026-09-04)\n",
        encoding="utf-8",
    )
    violations = check_kickoff_defaults_grammar(doc, valid_keys)
    assert violations == [], violations


def test_docs_lint_empty_value_is_rejected(tmp_path: Path) -> None:
    """Attack (hostile input): `docs-lint:` with an empty value between the
    colon and the em-dash.
    Expected (after W0-02): rejected (structural grammar violation,
    independent of whether the key is declared).
    Observed (before W0-02): PASS already -- an empty value fails the
    `- <key>: <value> — <reason> (<date>)` line regex regardless of key
    validity, so this already reports >=1 violation today. Kept as a
    regression guard: W0-02 must not accidentally loosen the shared line
    regex while adding the new key."""
    doc = tmp_path / "KICKOFF-DEFAULTS.md"
    doc.write_text(
        "# Kickoff Defaults\n\n- docs-lint:  — empty value probe (2026-09-04)\n",
        encoding="utf-8",
    )
    violations = check_kickoff_defaults_grammar(
        doc, manifest_kickoff_default_names() | {"docs-lint"}
    )
    assert violations != []


def test_standing_and_push_do_not_reject_a_docs_lint_kickoff_line(
    tmp_path: Path,
) -> None:
    """Attack: a well-formed `docs-lint:` line added to a real repo's
    KICKOFF-DEFAULTS.md -- confirm neither `loom_checker.py standing` nor
    `push` chokes on an extra key the lenient runtime parser
    (`kickoff_defaults()` in loom_checker.py) does not itself validate
    against the manifest (only the standalone grammar test does that).
    Expected (after W0-02): both commands still work with the new line
    present (docs-lint is "declared, not a blocker" per intent point 6).
    Observed (before W0-02): PASS already -- `kickoff_defaults()` is a
    lenient regex scan with no unknown-key rejection, so `standing` already
    tolerates an undeclared key silently. Kept as a regression guard: this
    line must never become a NEW gate in `standing`/`push`."""
    repo = _lane_repo(
        tmp_path,
        files={"loom-code/scripts/test_probe_lint.py": "def test_x():\n    assert True\n"},
        kickoff_lines=[
            "- docs-lint: python3 -m vale docs/ — enforce prose lint (2026-09-04)",
        ],
        verdicts_factory=_two_anthropic_verdicts,
    )
    push_result = run_checker("push", cwd=repo)
    assert push_result.returncode == 0, push_result.stderr


# =============================================================================
# 7. --list-rules stays 27
# =============================================================================


def test_list_rules_prints_exactly_27_ids(tmp_path: Path) -> None:
    """Attack: run `loom_checker.py --list-rules` and count distinct rule
    ids in the output (plan boundary: "no new rule id; push.verdicts-ge-2
    keeps its id and message shape").
    Expected (after W0-02): still exactly 27.
    Observed (before W0-02): PASS already -- 27 ids today."""
    result = run_checker("--list-rules", cwd=REPO_ROOT)
    assert result.returncode == 0, result.stderr
    ids = [
        line.split("\t", 1)[0]
        for line in result.stdout.strip().splitlines()
        if line.strip()
    ]
    assert len(ids) == len(set(ids)) == 27, f"got {len(ids)} ids: {ids}"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
