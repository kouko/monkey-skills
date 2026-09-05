"""Round-3 adversary probes for `loom-code/scripts/coldread_role_split.py`
pinning the run-status semantics from the design re-look
`docs/loom/2026-09-04-adversary-three-way-attribution-measured/evidence/design-relook-run-status-2026-09-05.md`
((a)-(f) and its adversary-checkable invariant).

Targets wave-end:1-02 (a non-zero `claude` exit is folded into
`status "ok"` and scored into `n`) and wave-end:1-09 (`failed_runs`
counts a validated `resumed` run as a failure), plus the surrounding
semantics the design re-look pins: `attempted_runs` vs scored `n`,
`complete`, the exit-code contract, the `# status:` transcript header,
and the resume-only-if-not-an-error-transcript rule.

`subprocess.run` and `shutil.which` are monkeypatched throughout; no
case calls the real `claude` binary. Every case here is RED against
the pre-fix module: error runs are still appended to `responses` and
scored, `failed_runs` counts `status != "ok"` (so a validated
`resumed` run is miscounted as failed), no `# status:` header is ever
written, `complete` is absent from summary.json, and `main` returns 0
unconditionally.
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

main = module.main
build_prompt = module.build_prompt

CLAUDE_BIN = "/usr/bin/claude"

_CORRECT_STDOUT = "1. mine -- x\n2. other -- y\n3. implementer -- z"
_WRONG_STDOUT_ONE_ITEM = "1. other -- wrong"


def _write_contract(tmp_path: Path, text: str = "a small round-3 contract", name: str = "contract.md") -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def _three_item_fixture() -> dict:
    return {
        "items": [
            {"n": 1, "text": "item one", "expected": "reviewer"},
            {"n": 2, "text": "item two", "expected": "adversary"},
            {"n": 3, "text": "item three", "expected": "implementer"},
        ],
        "source": "round-3 run-status abuse fixture",
    }


def _one_item_fixture() -> dict:
    return {
        "items": [{"n": 1, "text": "item one", "expected": "reviewer"}],
        "source": "round-3 run-status floor fixture",
    }


def _write_fixture(tmp_path: Path, fixture: dict, name: str = "fixture.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(fixture), encoding="utf-8")
    return path


def _base_argv(contract: Path, fixture: Path, out: Path, runs: str, role: str = "reviewer") -> list:
    return [
        "--contract", str(contract),
        "--fixture", str(fixture),
        "--role", role,
        "--runs", runs,
        "--out", str(out),
    ]


def _hashes(contract: Path, fixture_path: Path, fixture_dict: dict, role: str) -> dict:
    contract_hash = hashlib.sha256(contract.read_bytes()).hexdigest()
    fixture_hash = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
    prompt = build_prompt(contract.read_text(encoding="utf-8"), fixture_dict, role)
    prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    return {"contract_hash": contract_hash, "fixture_hash": fixture_hash, "prompt_hash": prompt_hash}


def _hand_header_lines(
    contract: Path,
    contract_hash: str,
    fixture_path: Path,
    fixture_hash: str,
    prompt_hash: str,
    i: int,
    n: int,
    model: str = "sonnet",
    status: str | None = None,
) -> list:
    """Build a run-file header in the exact shape `_parse_run_header`
    reads, with an optional `# status:` line inserted where the fixed
    module is expected to write one -- omitted entirely to test the
    legacy/absent-status sniff path (design re-look (e))."""
    lines = [
        f"# command: {CLAUDE_BIN} -p --model {model} --output-format text  (prompt on stdin, sha256 {prompt_hash})",
        f"# contract: {contract} sha256 {contract_hash}",
        f"# fixture: {fixture_path} sha256 {fixture_hash}",
        f"# run: {i} of {n}",
        f"# model: {model}",
    ]
    if status is not None:
        lines.append(f"# status: {status}")
    lines.append(f"# prompt-sha256: {prompt_hash}")
    return lines


def _setup_resume_dir(tmp_path: Path, contract: Path, fixture_path: Path, fixture_dict: dict, role: str,
                       status: str | None, body: str) -> Path:
    out = tmp_path / "out"
    out.mkdir()
    hashes = _hashes(contract, fixture_path, fixture_dict, role)
    header = "\n".join(_hand_header_lines(
        contract, hashes["contract_hash"], fixture_path, hashes["fixture_hash"],
        hashes["prompt_hash"], i=1, n=1, status=status,
    ))
    (out / "run-1.txt").write_text(header + "\n\n" + body, encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# 1. The design re-look's adversary-checkable invariant
# ---------------------------------------------------------------------------


def test_summary_extra_failing_run_changes_only_status_fields_and_exit_code(tmp_path, monkeypatch):
    """Design re-look invariant: injecting one extra failing run into an
    otherwise-identical batch must change nothing in summary.json except
    `attempted_runs`, `failed_runs`, `complete`, `runs[]`, and the
    process exit code -- every scoring-relevant key (`n`, `items`,
    `own_not_own_*`, `three_way_*`, `systematic`, `role`, `contract`,
    `fixture`, `model`, `seed`, `seed_note`, `contract_delivery`,
    `systematic_min_n`) must be identical.

    `argv`/`command_template` are excluded from this comparison: they
    literally embed `--runs`, which necessarily differs between a
    3-run and a 4-run invocation -- they are invocation echoes, not
    scoring output, and comparing them would not test the pinned
    invariant, only the harness's own test setup."""
    contract = _write_contract(tmp_path)
    fixture_dict = _three_item_fixture()
    fixture_path = _write_fixture(tmp_path, fixture_dict)

    def make_fake_run(fail_at):
        calls = {"n": 0}

        def fake_run(argv, **kwargs):
            calls["n"] += 1
            if fail_at is not None and calls["n"] == fail_at:
                return module.subprocess.CompletedProcess(argv, 17, stdout="", stderr="boom")
            return module.subprocess.CompletedProcess(argv, 0, stdout=_CORRECT_STDOUT, stderr="")

        return fake_run

    monkeypatch.setattr(module.shutil, "which", lambda name: CLAUDE_BIN)

    out_a = tmp_path / "out_a"
    monkeypatch.setattr(module.subprocess, "run", make_fake_run(fail_at=None))
    rc_a = main(_base_argv(contract, fixture_path, out_a, runs="3"))
    summary_a = json.loads((out_a / "summary.json").read_text(encoding="utf-8"))

    out_b = tmp_path / "out_b"
    monkeypatch.setattr(module.subprocess, "run", make_fake_run(fail_at=4))
    rc_b = main(_base_argv(contract, fixture_path, out_b, runs="4"))
    summary_b = json.loads((out_b / "summary.json").read_text(encoding="utf-8"))

    assert rc_a == 0
    assert rc_b == 1
    assert summary_a["n"] == 3
    assert summary_b["n"] == 3

    excluded = {"argv", "command_template", "attempted_runs", "failed_runs", "complete", "runs"}
    for key in summary_a:
        if key in excluded:
            continue
        assert key in summary_b, f"key {key!r} present in batch A summary but missing from batch B"
        assert summary_a[key] == summary_b[key], (
            f"key {key!r} differs between batch A and B: {summary_a[key]!r} != {summary_b[key]!r}"
        )
    for key in summary_b:
        if key in excluded:
            continue
        assert key in summary_a, f"key {key!r} present in batch B summary but missing from batch A"


# ---------------------------------------------------------------------------
# 2. A timeout run is a non-observation: not scored, still a failure
# ---------------------------------------------------------------------------


def test_run_timeout_not_scored_failed_and_status_header(tmp_path, monkeypatch):
    """A `TimeoutExpired` run must not be scored (design re-look (a)):
    `failed_runs == 1`, `n == 0` (nothing scored), `complete` is false,
    `main` returns 1, and the written transcript's header carries
    `# status: timeout` -- the pinned header token (e), not merely an
    `# error:` line buried in the body."""

    def fake_run(argv, **kwargs):
        raise module.subprocess.TimeoutExpired(cmd=argv, timeout=kwargs.get("timeout", 180))

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.shutil, "which", lambda name: CLAUDE_BIN)

    contract = _write_contract(tmp_path)
    fixture_path = _write_fixture(tmp_path, _one_item_fixture())
    out = tmp_path / "out"

    rc = main(_base_argv(contract, fixture_path, out, runs="1"))
    assert rc == 1
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert summary["failed_runs"] == 1
    assert summary["n"] == 0
    assert summary["complete"] is False

    header = (out / "run-1.txt").read_text(encoding="utf-8").split("\n\n", 1)[0]
    assert "# status: timeout" in header


# ---------------------------------------------------------------------------
# 3. A validated resumed run is scored, never a failure (closes wave-end:1-09)
# ---------------------------------------------------------------------------


def test_resume_valid_ok_header_counts_as_scored_not_failed(tmp_path, monkeypatch):
    """A resumed run whose header validates against the current
    invocation must be scored (`status "resumed"` counted in `n`), must
    never count toward `failed_runs` (closes wave-end:1-09), and the
    batch must be `complete` with exit 0."""

    def fake_run(argv, **kwargs):
        raise AssertionError("must not run -- this item is resumed from disk")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.shutil, "which", lambda name: CLAUDE_BIN)

    contract = _write_contract(tmp_path)
    fixture_dict = _one_item_fixture()
    fixture_path = _write_fixture(tmp_path, fixture_dict)
    out = _setup_resume_dir(
        tmp_path, contract, fixture_path, fixture_dict, "reviewer",
        status="ok", body="1. mine -- resumed answer",
    )

    rc = main(_base_argv(contract, fixture_path, out, runs="1") + ["--resume"])
    assert rc == 0
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert summary["runs"][0]["status"] == "resumed"
    assert summary["n"] == 1
    assert summary["failed_runs"] == 0
    assert summary["complete"] is True


# ---------------------------------------------------------------------------
# 4. --resume never resumes an error transcript; only an ok one
# ---------------------------------------------------------------------------


def test_resume_status_error_header_reruns_and_overwrites(tmp_path, monkeypatch):
    """(e): a run file whose header carries `# status: error` must never
    be resumed -- even though its hash/model/N/index all validate -- it
    is re-run and the file is overwritten with a fresh transcript."""
    calls = []

    def fake_run(argv, **kwargs):
        calls.append(argv)
        return module.subprocess.CompletedProcess(argv, 0, stdout=_WRONG_STDOUT_ONE_ITEM, stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.shutil, "which", lambda name: CLAUDE_BIN)

    contract = _write_contract(tmp_path)
    fixture_dict = _one_item_fixture()
    fixture_path = _write_fixture(tmp_path, fixture_dict)
    out = _setup_resume_dir(
        tmp_path, contract, fixture_path, fixture_dict, "reviewer",
        status="error", body="# error: exit 9\nold failure",
    )

    rc = main(_base_argv(contract, fixture_path, out, runs="1") + ["--resume"])
    assert len(calls) == 1, "an error-status run must be re-run, not resumed"
    assert rc == 0
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert summary["runs"][0]["status"] == "ok"
    body = (out / "run-1.txt").read_text(encoding="utf-8").split("\n\n", 1)[1]
    assert body == _WRONG_STDOUT_ONE_ITEM


def test_resume_legacy_error_body_reruns_and_overwrites(tmp_path, monkeypatch):
    """(e): a legacy run file with no `# status:` line at all, whose body
    starts with `# error:` (the pre-fix error marker), must not be
    resumed via the absent-status sniff -- it is re-run and
    overwritten."""
    calls = []

    def fake_run(argv, **kwargs):
        calls.append(argv)
        return module.subprocess.CompletedProcess(argv, 0, stdout=_WRONG_STDOUT_ONE_ITEM, stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.shutil, "which", lambda name: CLAUDE_BIN)

    contract = _write_contract(tmp_path)
    fixture_dict = _one_item_fixture()
    fixture_path = _write_fixture(tmp_path, fixture_dict)
    out = _setup_resume_dir(
        tmp_path, contract, fixture_path, fixture_dict, "reviewer",
        status=None, body="# error: exit 9\nold legacy failure",
    )

    rc = main(_base_argv(contract, fixture_path, out, runs="1") + ["--resume"])
    assert len(calls) == 1, "a legacy '# error:' body must be re-run, not resumed"
    body = (out / "run-1.txt").read_text(encoding="utf-8").split("\n\n", 1)[1]
    assert body == _WRONG_STDOUT_ONE_ITEM


def test_resume_empty_body_reruns_and_overwrites(tmp_path, monkeypatch):
    """(e): a legacy run file with no `# status:` line and an empty body
    (the all-`unparsed`-silently defect the design re-look calls out)
    must not be resumed -- it is re-run and overwritten."""
    calls = []

    def fake_run(argv, **kwargs):
        calls.append(argv)
        return module.subprocess.CompletedProcess(argv, 0, stdout=_WRONG_STDOUT_ONE_ITEM, stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.shutil, "which", lambda name: CLAUDE_BIN)

    contract = _write_contract(tmp_path)
    fixture_dict = _one_item_fixture()
    fixture_path = _write_fixture(tmp_path, fixture_dict)
    out = _setup_resume_dir(
        tmp_path, contract, fixture_path, fixture_dict, "reviewer",
        status=None, body="",
    )

    rc = main(_base_argv(contract, fixture_path, out, runs="1") + ["--resume"])
    assert len(calls) == 1, "an empty body must be re-run, not resumed"
    body = (out / "run-1.txt").read_text(encoding="utf-8").split("\n\n", 1)[1]
    assert body == _WRONG_STDOUT_ONE_ITEM


def test_resume_status_ok_header_skips_rerun(tmp_path, monkeypatch):
    """Control case for the three probes above: a run file whose header
    carries `# status: ok` must be resumed -- subprocess.run is never
    called and the file is left byte-for-byte untouched."""

    def fake_run(argv, **kwargs):
        raise AssertionError("must not run -- status: ok header is resumable")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.shutil, "which", lambda name: CLAUDE_BIN)

    contract = _write_contract(tmp_path)
    fixture_dict = _one_item_fixture()
    fixture_path = _write_fixture(tmp_path, fixture_dict)
    out = _setup_resume_dir(
        tmp_path, contract, fixture_path, fixture_dict, "reviewer",
        status="ok", body="1. mine -- resumed and untouched",
    )
    original = (out / "run-1.txt").read_text(encoding="utf-8")

    rc = main(_base_argv(contract, fixture_path, out, runs="1") + ["--resume"])
    assert rc == 0
    assert (out / "run-1.txt").read_text(encoding="utf-8") == original


# ---------------------------------------------------------------------------
# 5. Every fresh transcript header carries a `# status:` line
# ---------------------------------------------------------------------------


def test_run_header_status_line_present_for_ok_and_error(tmp_path, monkeypatch):
    """(e): every transcript header -- not just the timeout case -- must
    carry a `# status: ok|error|timeout` line: one run that succeeds and
    one that returns a non-zero exit code must each get the matching
    token in their own header block."""
    calls = []

    def fake_run(argv, **kwargs):
        calls.append(argv)
        if len(calls) == 1:
            return module.subprocess.CompletedProcess(argv, 0, stdout=_CORRECT_STDOUT, stderr="")
        return module.subprocess.CompletedProcess(argv, 5, stdout="", stderr="boom")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.shutil, "which", lambda name: CLAUDE_BIN)

    contract = _write_contract(tmp_path)
    fixture_path = _write_fixture(tmp_path, _three_item_fixture())
    out = tmp_path / "out"

    main(_base_argv(contract, fixture_path, out, runs="2"))

    header1 = (out / "run-1.txt").read_text(encoding="utf-8").split("\n\n", 1)[0]
    header2 = (out / "run-2.txt").read_text(encoding="utf-8").split("\n\n", 1)[0]
    assert "# status: ok" in header1
    assert "# status: error" in header2


# ---------------------------------------------------------------------------
# 6. Every run fails: no crash, zero totals, exit 1
# ---------------------------------------------------------------------------


def test_all_runs_fail_no_crash_zero_totals_exit_one(tmp_path, monkeypatch):
    """(f)/(d): when every run in the batch fails (`n == 0` scored), the
    runner must not crash: zero totals and an empty `systematic`,
    summary.json is still written with `complete: false`, and `main`
    returns 1."""

    def fake_run(argv, **kwargs):
        return module.subprocess.CompletedProcess(argv, 1, stdout="", stderr="down")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.shutil, "which", lambda name: CLAUDE_BIN)

    contract = _write_contract(tmp_path)
    fixture_path = _write_fixture(tmp_path, _three_item_fixture())
    out = tmp_path / "out"

    rc = main(_base_argv(contract, fixture_path, out, runs="3"))
    assert rc == 1
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert summary["n"] == 0
    assert summary["complete"] is False
    assert summary["failed_runs"] == 3
    assert summary["own_not_own_correct"] == 0
    assert summary["own_not_own_total"] == 0
    assert summary["three_way_correct"] == 0
    assert summary["three_way_total"] == 0
    assert summary["systematic"] == []


# ---------------------------------------------------------------------------
# 7. The systematic floor applies to scored n, not attempted_runs
# ---------------------------------------------------------------------------


def test_systematic_floor_applies_to_scored_n_not_attempted(tmp_path, monkeypatch):
    """(f): the `SYSTEMATIC_MIN_N` floor applies to scored `n`, not
    `attempted_runs` -- 10 attempted with 4 scored wrong-and-uniform
    answers must flag `systematic` (scored n=4 meets the floor exactly
    as a 4-attempted/4-scored batch would), while 10 attempted with only
    2 scored must never flag it (below the floor) regardless of how
    uniformly wrong those 2 are."""

    def make_fake_run(n_ok):
        calls = {"n": 0}

        def fake_run(argv, **kwargs):
            calls["n"] += 1
            if calls["n"] <= n_ok:
                return module.subprocess.CompletedProcess(argv, 0, stdout=_WRONG_STDOUT_ONE_ITEM, stderr="")
            return module.subprocess.CompletedProcess(argv, 1, stdout="", stderr="down")

        return fake_run

    monkeypatch.setattr(module.shutil, "which", lambda name: CLAUDE_BIN)

    contract = _write_contract(tmp_path)
    fixture_path = _write_fixture(tmp_path, _one_item_fixture())

    out_floor_met = tmp_path / "out_floor_met"
    monkeypatch.setattr(module.subprocess, "run", make_fake_run(n_ok=4))
    main(_base_argv(contract, fixture_path, out_floor_met, runs="10"))
    summary_met = json.loads((out_floor_met / "summary.json").read_text(encoding="utf-8"))
    assert summary_met["n"] == 4
    assert summary_met["systematic"] == [1]

    out_floor_missed = tmp_path / "out_floor_missed"
    monkeypatch.setattr(module.subprocess, "run", make_fake_run(n_ok=2))
    main(_base_argv(contract, fixture_path, out_floor_missed, runs="10"))
    summary_missed = json.loads((out_floor_missed / "summary.json").read_text(encoding="utf-8"))
    assert summary_missed["n"] == 2
    assert summary_missed["systematic"] == []


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
