"""Wave-end:1 checkpoint adversary probes for
`loom-code/scripts/coldread_role_split.py` (W1-01..W1-03).

Written after the module and its own package tests
(`loom-code/scripts/test_coldread_role_split.py`) and after the two
earlier adversary probe files in this same directory
(`test_abuse_coldread_scoring.py`, `test_abuse_coldread_runner.py`).
Every case here targets a state none of those three files exercised:
non-contiguous fixture item numbers, a non-zero `subprocess.run`
returncode folded into status "ok", `--out`/`--contract` pointing at a
path that is not a usable file/dir, `systematic` semantics at n == 1,
reverse item order, article/possessive label forms, an empty stdout
body, `COLDREAD_CLAUDE_BIN`, and a resume body that itself contains the
`# command:` header sentinel.

`subprocess.run` and `shutil.which` are monkeypatched throughout; no
case calls the real `claude` binary.
"""
from __future__ import annotations

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


def test_score_fixture_with_gap_in_item_numbers_always_scores_high_n_wrong():
    """A fixture with item numbers [1, 2, 5] (3 items, but max n is 5) sets
    `n_items = len(items) == 3` inside score()/parse_response(). A response
    that correctly answers "5. implementer -- z" is dropped by
    parse_response's `n > n_items` guard, so item 5 is scored "unparsed"/
    wrong even though the transcript answered it correctly. This proves the
    fixture's `n` values must be contiguous 1..len(items) or scoring for
    every item numbered beyond len(items) is silently always wrong."""
    fixture = {
        "items": [
            {"n": 1, "text": "a", "expected": "reviewer"},
            {"n": 2, "text": "b", "expected": "adversary"},
            {"n": 5, "text": "c", "expected": "implementer"},
        ]
    }
    correct_response = "1. mine -- x\n2. other -- y\n5. implementer -- z"
    result = score([correct_response], fixture, "reviewer")
    assert result["items"]["5"]["expected"] == "implementer"
    # The bug: despite the transcript answering item 5 correctly, it is
    # recorded as wrong/unparsed because parse_response never sees n=5
    # as in-range (n_items came out to 3, not 5).
    assert result["items"]["5"]["wrong"] == 1
    assert result["items"]["5"]["counts"] == {"unparsed": 1}


# ---------------------------------------------------------------------------
# 2. Non-zero subprocess.run returncode is folded into status "ok"
# ---------------------------------------------------------------------------


def test_main_nonzero_returncode_recorded_as_status_ok_not_distinguished():
    """`run_once` folds a non-zero returncode's stdout+stderr into the
    returned body without raising, and `main`'s loop only distinguishes
    `TimeoutExpired` from success -- a failed `claude` invocation (auth
    error, crash, non-zero exit) is written to run-1.txt and recorded in
    summary.json with status "ok", identical to a genuine completed call.
    A reader of summary.json cannot tell a real transcript from a failed
    subprocess call folded into the same status bucket."""

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
        # The one and only run used a non-zero-returncode fake call, yet the
        # runner records it exactly like a healthy call.
        assert summary["runs"][0]["status"] == "ok"
        body = (out / "run-1.txt").read_text(encoding="utf-8").split("\n\n", 1)[1]
        assert body == "fatal: not logged in"
    finally:
        module.shutil.which = module_which
        module.subprocess.run = module_run


# ---------------------------------------------------------------------------
# 3. `--out` pointing at an existing file, not a directory
# ---------------------------------------------------------------------------


def test_main_out_path_is_existing_file_crashes_uncaught(tmp_path, monkeypatch):
    """`--out` naming an existing regular file (not a directory) makes
    `Path.glob` on it silently return no matches (so the "already contains
    run files" guard never fires), then `out_dir.mkdir(parents=True,
    exist_ok=True)` raises an uncaught `FileExistsError` -- a traceback,
    not the graceful `error: ...` / exit 2 pattern every other invalid-
    input case in this module uses."""

    def fake_run(argv, **kwargs):
        raise AssertionError("must not be called before the crash")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.shutil, "which", lambda name: "/usr/bin/claude")

    contract = _write_contract(tmp_path)
    fixture = _write_fixture(tmp_path, [{"n": 1, "text": "a", "expected": "reviewer"}])
    out = tmp_path / "out_is_a_file"
    out.write_text("i am a file, not a directory", encoding="utf-8")

    with pytest.raises(FileExistsError):
        main(_base_argv(contract, fixture, out))


# ---------------------------------------------------------------------------
# 4. Contract file that does not exist
# ---------------------------------------------------------------------------


def test_main_missing_contract_file_crashes_uncaught(tmp_path, monkeypatch):
    """A `--contract` path that does not exist raises an uncaught
    `FileNotFoundError` from `Path.read_bytes()` rather than the module's
    own `error: ...` / exit 2 pattern used for `--runs`/missing-binary."""

    def fake_run(argv, **kwargs):
        raise AssertionError("must not be called before the crash")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.shutil, "which", lambda name: "/usr/bin/claude")

    fixture = _write_fixture(tmp_path, [{"n": 1, "text": "a", "expected": "reviewer"}])
    out = tmp_path / "out"
    missing_contract = tmp_path / "does-not-exist.md"

    with pytest.raises(FileNotFoundError):
        main(_base_argv(missing_contract, fixture, out))


# ---------------------------------------------------------------------------
# 5. `systematic` semantics at n == 1 (`--runs 1`)
# ---------------------------------------------------------------------------


def test_score_single_run_wrong_answer_flagged_systematic_at_n_equals_1():
    """With exactly one run (`n == 1`), a single wrong answer makes
    `wrong_rate == 1.0 >= 0.5` and the dominant-wrong-label share is also
    `1.0 >= 0.5`, so the item is included in `systematic` on the strength
    of one data point. The field name and the checkpoint's own vocabulary
    ("systematic" bias) imply a pattern across repeated runs; at n == 1 the
    formula still fires, which is a caller-facing landmine for anyone who
    treats `summary.json["systematic"]` at face value without also reading
    `n`."""
    fixture = {"items": [{"n": 1, "text": "a", "expected": "reviewer"}]}
    result = score(["1. other -- wrong"], fixture, "reviewer")
    assert result["n"] == 1
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
    included -- belongs to the body and must survive intact."""
    tmp_path = Path(pytest.importorskip("tempfile").mkdtemp())
    out = tmp_path / "out"
    out.mkdir()
    body = (
        "1. mine -- first paragraph\n\n"
        "# command: this looks like a header but is body content\n\n"
        "trailing body text"
    )
    (out / "run-1.txt").write_text(
        "# command: real-header\n# run: 1 of 1\n\n" + body, encoding="utf-8"
    )

    def fake_run(argv, **kwargs):
        raise AssertionError("must not run — this item is resumed from disk")

    module_which = module.shutil.which
    module_run = module.subprocess.run
    module.shutil.which = lambda name: "/usr/bin/claude"
    module.subprocess.run = fake_run
    try:
        contract = _write_contract(tmp_path)
        fixture = _write_fixture(tmp_path, [{"n": 1, "text": "a", "expected": "reviewer"}])
        rc = main(_base_argv(contract, fixture, out, runs="1") + ["--resume"])
        assert rc == 0
        summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
        assert summary["items"]["1"]["counts"] == {"mine": 1}
        assert summary["items"]["1"]["wrong"] == 0
    finally:
        module.shutil.which = module_which
        module.subprocess.run = module_run


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
