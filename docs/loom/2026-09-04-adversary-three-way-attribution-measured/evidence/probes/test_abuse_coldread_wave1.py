"""Wave-end:1 checkpoint adversary probes for
`loom-code/scripts/coldread_role_split.py` (W1-01..W1-03).

Written after the module and its own package tests
(`loom-code/scripts/test_coldread_role_split.py`) and after the two
earlier adversary probe files in this same directory
(`test_abuse_coldread_scoring.py`, `test_abuse_coldread_runner.py`).
Every case here targets a state none of those three files exercised:
non-contiguous fixture item numbers, a non-zero `subprocess.run`
returncode, `--out`/`--contract` pointing at a path that is not a
usable file/dir, `systematic` semantics near the n == 1 floor, reverse
item order, article/possessive label forms, an empty stdout body,
`COLDREAD_CLAUDE_BIN`, and a resume body that itself contains the
`# command:` header sentinel.

**Fix-round update (wave-end:1-02, -06, -07, -08):** four functions
below were rewritten from pinning the pre-fix defect to asserting the
corrected behaviour the fix round must deliver — a non-contiguous
fixture must raise `ValueError`; a non-zero returncode must be
recorded `status "error"`, not `"ok"`; an existing-file `--out` and a
missing `--contract` must exit 2 with an `error:` message on stderr,
never crash uncaught; and `systematic` must never fire below
`n == 3`. Their function names now state the fixed expectation. They
are RED against the pre-fix module and are the implementer's target
for those four findings. The remaining functions in this file are
unaffected by the fix and stay GREEN throughout.

`subprocess.run` and `shutil.which` are monkeypatched throughout; no
case calls the real `claude` binary.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest


def _find_repo_root(start: Path) -> Path:
    """Walk upward from `start` until a directory containing docs/loom is found."""
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "docs" / "loom").is_dir():
            return candidate
    raise RuntimeError(f"could not locate repo root (docs/loom) above {start}")


REPO_ROOT = _find_repo_root(Path(__file__).parent)
SCRIPTS_DIR = REPO_ROOT / "loom-code" / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))

import coldread_role_split as module  # noqa: E402  (import after sys.path mutation, by design)

parse_response = module.parse_response
score = module.score
main = module.main


def _write_contract(tmp_path: Path, text: str = "a small contract", name: str = "contract.md") -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def _write_fixture(tmp_path: Path, items: list, name: str = "fixture.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps({"items": items, "source": "wave1-abuse"}), encoding="utf-8")
    return path


def _canned_stdout() -> str:
    return "1. mine -- x\n2. other -- y\n3. implementer -- z"


def _base_argv(contract: Path, fixture: Path, out: Path, runs: str = "1", role: str = "reviewer") -> list:
    return [
        "--contract", str(contract),
        "--fixture", str(fixture),
        "--role", role,
        "--runs", runs,
        "--out", str(out),
    ]


# ---------------------------------------------------------------------------
# 1. Non-contiguous fixture item numbers: n_items = len(items), not max(n)
# ---------------------------------------------------------------------------


def test_score_fixture_with_gap_in_item_numbers_raises_valueerror():
    """A fixture with item numbers [1, 2, 5] (3 items, but max n is 5) is
    not contiguous 1..len(items). `score` must reject it with
    `ValueError` rather than silently computing `n_items = len(items)
    == 3` and scoring every item numbered beyond len(items) (here, item
    5) as always wrong/unparsed regardless of what the transcript says."""
    fixture = {
        "items": [
            {"n": 1, "text": "a", "expected": "reviewer"},
            {"n": 2, "text": "b", "expected": "adversary"},
            {"n": 5, "text": "c", "expected": "implementer"},
        ]
    }
    correct_response = "1. mine -- x\n2. other -- y\n5. implementer -- z"
    try:
        score([correct_response], fixture, "reviewer")
    except ValueError:
        pass
    else:
        raise AssertionError(
            "score() accepted a fixture whose item numbers are not "
            "contiguous 1..len(items) instead of raising ValueError"
        )


def test_score_fixture_with_contiguous_item_numbers_scores_normally():
    """A control case for the probe above: a fixture whose item numbers
    are exactly 1..len(items) must be accepted and scored without
    raising, so the contiguity check does not reject valid fixtures."""
    fixture = {
        "items": [
            {"n": 1, "text": "a", "expected": "reviewer"},
            {"n": 2, "text": "b", "expected": "adversary"},
            {"n": 3, "text": "c", "expected": "implementer"},
        ]
    }
    correct_response = "1. mine -- x\n2. other -- y\n3. implementer -- z"
    result = score([correct_response], fixture, "reviewer")
    assert result["items"]["3"]["expected"] == "implementer"
    assert result["items"]["3"]["wrong"] == 0
    assert result["items"]["3"]["counts"] == {"implementer": 1}


# ---------------------------------------------------------------------------
# 2. Non-zero subprocess.run returncode is folded into status "ok"
# ---------------------------------------------------------------------------


def test_main_nonzero_returncode_recorded_as_status_error_not_ok():
    """A `claude` invocation that returns a non-zero exit code (auth
    error, crash, ...) must be recorded in summary.json with status
    "error", never "ok" -- and the transcript body must carry an
    `# error: exit <code>` marker so a reader of run-1.txt alone can
    tell the call failed. `summary.json["runs"][0]["returncode"]` must
    carry the actual code, and `summary.json["failed_runs"]` must count
    this run."""

    def fake_run(argv, **kwargs):
        return module.subprocess.CompletedProcess(
            argv, 17, stdout="", stderr="fatal: not logged in"
        )

    tmp_path = Path(pytest.importorskip("tempfile").mkdtemp())
    module_which = module.shutil.which
    module_run = module.subprocess.run
    module.shutil.which = lambda name: "/usr/bin/claude"
    module.subprocess.run = fake_run
    try:
        contract = _write_contract(tmp_path)
        fixture = _write_fixture(tmp_path, [{"n": 1, "text": "a", "expected": "reviewer"}])
        out = tmp_path / "out"
        rc = main(_base_argv(contract, fixture, out))
        assert rc == 0
        summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
        # The one and only run used a non-zero-returncode fake call; the
        # fixed runner must record it as "error", distinguishable from a
        # genuine completed call.
        assert summary["runs"][0]["status"] == "error"
        assert summary["runs"][0]["returncode"] == 17
        assert summary["failed_runs"] == 1
        body = (out / "run-1.txt").read_text(encoding="utf-8").split("\n\n", 1)[1]
        assert "# error: exit 17" in body
    finally:
        module.shutil.which = module_which
        module.subprocess.run = module_run


# ---------------------------------------------------------------------------
# 3. `--out` pointing at an existing file, not a directory
# ---------------------------------------------------------------------------


def test_main_out_path_is_existing_file_exits_two_with_error(tmp_path, monkeypatch, capsys):
    """`--out` naming an existing regular file (not a directory) must exit
    2 with an `error:` message on stderr naming the path -- the same
    graceful pattern every other invalid-input case in this module uses --
    never an uncaught `FileExistsError` traceback, and the fake claude
    call must never run."""

    def fake_run(argv, **kwargs):
        raise AssertionError("must not be called on an invalid --out")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.shutil, "which", lambda name: "/usr/bin/claude")

    contract = _write_contract(tmp_path)
    fixture = _write_fixture(tmp_path, [{"n": 1, "text": "a", "expected": "reviewer"}])
    out = tmp_path / "out_is_a_file"
    out.write_text("i am a file, not a directory", encoding="utf-8")

    rc = main(_base_argv(contract, fixture, out))
    assert rc == 2
    err = capsys.readouterr().err
    assert "error:" in err
    assert str(out) in err


# ---------------------------------------------------------------------------
# 4. Contract file that does not exist
# ---------------------------------------------------------------------------


def test_main_missing_contract_file_exits_two_with_error(tmp_path, monkeypatch, capsys):
    """A `--contract` path that does not exist must exit 2 with an
    `error:` message on stderr naming the missing path, matching the
    module's own convention used for `--runs`/missing-binary, never an
    uncaught `FileNotFoundError` traceback."""

    def fake_run(argv, **kwargs):
        raise AssertionError("must not be called on a missing --contract")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.shutil, "which", lambda name: "/usr/bin/claude")

    fixture = _write_fixture(tmp_path, [{"n": 1, "text": "a", "expected": "reviewer"}])
    out = tmp_path / "out"
    missing_contract = tmp_path / "does-not-exist.md"

    rc = main(_base_argv(missing_contract, fixture, out))
    assert rc == 2
    err = capsys.readouterr().err
    assert "error:" in err
    assert str(missing_contract) in err


# ---------------------------------------------------------------------------
# 5. `systematic` semantics at n == 1 (`--runs 1`)
# ---------------------------------------------------------------------------


def test_score_single_run_wrong_answer_not_flagged_systematic_below_floor():
    """With exactly one run (`n == 1`), a single wrong answer must NOT be
    included in `systematic` -- the field name and the checkpoint's own
    vocabulary ("systematic" bias) imply a pattern across repeated runs,
    and one data point is not a pattern. `score` enforces a floor of
    `n >= 3` before `systematic` can fire at all, below which the list
    must always be empty regardless of how uniformly wrong the single (or
    double) run was."""
    fixture = {"items": [{"n": 1, "text": "a", "expected": "reviewer"}]}
    result = score(["1. other -- wrong"], fixture, "reviewer")
    assert result["n"] == 1
    assert result["systematic"] == []

    result_two = score(["1. other -- wrong", "1. other -- wrong"], fixture, "reviewer")
    assert result_two["n"] == 2
    assert result_two["systematic"] == []


def test_score_three_runs_all_wrong_flagged_systematic_at_floor():
    """A control case for the probe above: at `n == 3` (the floor), three
    unanimous wrong answers for the same item must still be flagged
    `systematic` -- the floor must not silently swallow a genuine
    systematic pattern once enough runs exist to call it one."""
    fixture = {"items": [{"n": 1, "text": "a", "expected": "reviewer"}]}
    result = score(
        ["1. other -- wrong", "1. other -- wrong", "1. other -- wrong"],
        fixture,
        "reviewer",
    )
    assert result["n"] == 3
    assert result["systematic"] == [1]


# ---------------------------------------------------------------------------
# 6. Reverse item order in the response transcript
# ---------------------------------------------------------------------------


def test_parse_response_items_in_reverse_order_still_parse_correctly():
    """All eight items answered in descending order (8 down to 1) must
    parse identically to ascending order -- parse_response iterates lines,
    not item numbers, so declaration order in the transcript must not
    matter."""
    lines = [f"{n}. mine -- reason {n}" for n in range(8, 0, -1)]
    text = "\n".join(lines)
    result = parse_response(text, 8)
    assert result == {n: "mine" for n in range(1, 9)}


# ---------------------------------------------------------------------------
# 7. Article/possessive label decoration the pinned format does not use
# ---------------------------------------------------------------------------


def test_parse_response_article_prefixed_label_is_unparsed_not_crash():
    """`8. the implementer's -- reason` (an article before the label, as a
    model might paraphrase instead of using the pinned
    `<n>. mine|other|implementer` form) must not crash and must not be
    silently miscounted as a valid label -- the leading "the " is not
    markdown noise the regex tolerates, so this is correctly "unparsed"."""
    result = parse_response("8. the implementer's -- reason", 8)
    assert result[8] == "unparsed"


def test_parse_response_bare_possessive_label_without_article_parses():
    """`8. other's -- reason` (no article, just the label token with a
    trailing possessive) must parse to the base label "other" -- this is
    the possessive form the regex is documented to tolerate, as opposed to
    the article-prefixed form above which it must not."""
    result = parse_response("8. other's -- reason", 8)
    assert result[8] == "other"


# ---------------------------------------------------------------------------
# 8. Resume: body containing the literal `# command:` header sentinel
# ---------------------------------------------------------------------------


def test_main_resume_body_containing_header_sentinel_still_splits_correctly():
    """A run file whose *body* itself contains a blank line followed by
    text starting with `# command:` (mimicking the header) must still be
    read back whole on `--resume`: `text.split("\\n\\n", 1)` splits only on
    the FIRST blank line, so everything after it -- sentinel lookalike
    included -- belongs to the body and must survive intact.

    wave-end:1-03 follow-up: `--resume` now validates the resumed
    header's contract/fixture/prompt hashes, run/N and model against the
    current invocation, so the hand-written run file must carry the full
    valid header (computed the same way the module computes it) instead
    of the pre-fix minimal one -- otherwise validation rejects it before
    the body-split behaviour under test is ever exercised."""
    tmp_path = Path(pytest.importorskip("tempfile").mkdtemp())
    out = tmp_path / "out"
    out.mkdir()

    contract = _write_contract(tmp_path)
    fixture_path = _write_fixture(tmp_path, [{"n": 1, "text": "a", "expected": "reviewer"}])
    contract_hash = hashlib.sha256(contract.read_bytes()).hexdigest()
    fixture_bytes = fixture_path.read_bytes()
    fixture_hash = hashlib.sha256(fixture_bytes).hexdigest()
    fixture_json = json.loads(fixture_bytes.decode("utf-8"))
    prompt = module.build_prompt(contract.read_text(encoding="utf-8"), fixture_json, "reviewer")
    prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    body = (
        "1. mine -- first paragraph\n\n"
        "# command: this looks like a header but is body content\n\n"
        "trailing body text"
    )
    header = "\n".join(
        [
            f"# command: claude -p --model sonnet --output-format text  (prompt on stdin, sha256 {prompt_hash})",
            f"# contract: {contract} sha256 {contract_hash}",
            f"# fixture: {fixture_path} sha256 {fixture_hash}",
            "# run: 1 of 1",
            "# model: sonnet",
            f"# prompt-sha256: {prompt_hash}",
        ]
    )
    (out / "run-1.txt").write_text(header + "\n\n" + body, encoding="utf-8")

    def fake_run(argv, **kwargs):
        raise AssertionError("must not run — this item is resumed from disk")

    module_which = module.shutil.which
    module_run = module.subprocess.run
    module.shutil.which = lambda name: "/usr/bin/claude"
    module.subprocess.run = fake_run
    try:
        rc = main(_base_argv(contract, fixture_path, out, runs="1") + ["--resume"])
        assert rc == 0
        summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
        assert summary["items"]["1"]["counts"] == {"mine": 1}
        assert summary["items"]["1"]["wrong"] == 0
    finally:
        module.shutil.which = module_which
        module.subprocess.run = module_run


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
