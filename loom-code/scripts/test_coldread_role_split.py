"""Executable contract for `coldread_role_split.parse_response`/`score`.

Uses a small inline fixture (not the docs/ evidence file) so this
package test stays repo-independent, matching `test_git_exec.py`'s
bare-import convention.
"""
from __future__ import annotations

import coldread_role_split

parse_response = coldread_role_split.parse_response
score = coldread_role_split.score


def _fixture() -> dict:
    return {
        "items": [
            {"n": 1, "text": "a", "expected": "reviewer"},
            {"n": 2, "text": "b", "expected": "adversary"},
            {"n": 3, "text": "c", "expected": "adversary"},
            {"n": 4, "text": "d", "expected": "reviewer"},
            {"n": 5, "text": "e", "expected": "reviewer"},
            {"n": 6, "text": "f", "expected": "adversary"},
            {"n": 7, "text": "g", "expected": "reviewer"},
            {"n": 8, "text": "h", "expected": "implementer"},
        ],
        "source": "inline-test-fixture",
    }


def _response(labels: dict[int, str], n_items: int = 8) -> str:
    lines = []
    for n in range(1, n_items + 1):
        if n in labels:
            lines.append(f"{n}. {labels[n]} -- because reasons")
    return "\n".join(lines)


def test_score_counts_labels_per_item_and_flags_systematic():
    fixture = _fixture()
    correct = {1: "mine", 2: "other", 3: "other", 4: "mine",
               5: "mine", 6: "other", 7: "mine", 8: "implementer"}

    resp_all_correct = _response(correct)
    resp_wrong_1 = _response({**correct, 1: "other"})
    resp_wrong_1_same_label = _response({**correct, 1: "other"})

    result = score(
        [resp_all_correct, resp_wrong_1, resp_wrong_1_same_label],
        fixture,
        "reviewer",
    )

    assert result["n"] == 3
    for n in range(1, 9):
        item = result["items"][str(n)]
        assert set(item["counts"]) <= {"mine", "other", "implementer", "unparsed"}

    # item 1: 2/3 wrong, all wrong runs say "other" -> systematic (>=50% wrong,
    # >=50% dominant wrong label share)
    assert 1 in result["systematic"]
    # items 2-8 all correct in every run -> never systematic
    for n in range(2, 9):
        assert n not in result["systematic"]

    assert result["own_not_own_correct"] < result["own_not_own_total"]
    assert result["three_way_correct"] < result["three_way_total"]
    assert result["three_way_total"] == 3 * 8


def test_parse_response_unparsed_line_never_scored_correct():
    fixture = _fixture()
    garbage = "not a valid line at all"
    result = score([garbage], fixture, "reviewer")
    assert result["own_not_own_correct"] == 0
    assert result["three_way_correct"] == 0
    for n in range(1, 9):
        assert result["items"][str(n)]["counts"]["unparsed"] == 1


def test_role_reviewer_maps_expected_owners_to_labels():
    fixture = _fixture()
    resp = _response({1: "mine", 2: "other", 8: "implementer"})
    result = score([resp], fixture, "reviewer")
    assert result["items"]["1"]["expected"] == "mine"
    assert result["items"]["2"]["expected"] == "other"
    assert result["items"]["8"]["expected"] == "implementer"


def test_role_adversary_maps_expected_owners_to_labels_symmetric():
    fixture = _fixture()
    resp = _response({1: "other", 2: "mine", 8: "implementer"})
    result = score([resp], fixture, "adversary")
    assert result["items"]["1"]["expected"] == "other"
    assert result["items"]["2"]["expected"] == "mine"
    assert result["items"]["8"]["expected"] == "implementer"


# ---------------------------------------------------------------------------
# CLI/runner tests (W1-03): monkeypatch subprocess.run and shutil.which,
# inline fixture written to tmp_path, no real `claude` call.
# ---------------------------------------------------------------------------

import json as _json

main = coldread_role_split.main


def _cli_fixture_dict() -> dict:
    return {
        "items": [
            {"n": 1, "text": "first finding text", "expected": "reviewer"},
            {"n": 2, "text": "second finding text", "expected": "adversary"},
            {"n": 3, "text": "third finding text", "expected": "implementer"},
        ],
        "source": "inline-cli-test-fixture",
    }


def _write_cli_fixture(tmp_path):
    path = tmp_path / "fixture.json"
    path.write_text(_json.dumps(_cli_fixture_dict()), encoding="utf-8")
    return path


def _write_cli_contract(tmp_path, text="a small contract"):
    path = tmp_path / "contract.md"
    path.write_text(text, encoding="utf-8")
    return path


def _canned_stdout():
    return "1. mine -- x\n2. other -- y\n3. implementer -- z"


def _cli_argv(contract, fixture, out, runs="3", role="adversary"):
    return [
        "--contract", str(contract),
        "--fixture", str(fixture),
        "--role", role,
        "--runs", runs,
        "--out", str(out),
    ]


def test_main_writes_run_files_with_command_line_and_summary(tmp_path, monkeypatch):
    calls = []

    def fake_run(argv, **kwargs):
        calls.append(argv)
        return coldread_role_split.subprocess.CompletedProcess(argv, 0, stdout=_canned_stdout(), stderr="")

    monkeypatch.setattr(coldread_role_split.subprocess, "run", fake_run)
    monkeypatch.setattr(coldread_role_split.shutil, "which", lambda name: "/usr/bin/claude")

    contract = _write_cli_contract(tmp_path)
    fixture = _write_cli_fixture(tmp_path)
    out = tmp_path / "out"

    rc = main(_cli_argv(contract, fixture, out, runs="3"))
    assert rc == 0
    assert len(calls) == 3

    for i in (1, 2, 3):
        run_file = out / f"run-{i}.txt"
        assert run_file.exists()
        text = run_file.read_text(encoding="utf-8")
        header, body = text.split("\n\n", 1)
        command_line = header.splitlines()[0]
        assert command_line.startswith(
            "# command: /usr/bin/claude -p --model sonnet --output-format text"
        )
        assert "prompt on stdin" in command_line
        assert "sha256" in command_line
        assert f"# contract: {contract} sha256" in header
        assert f"# fixture: {fixture} sha256" in header
        assert f"# run: {i} of 3" in header
        assert "# timestamp:" in header
        assert body == _canned_stdout()

    summary = _json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert summary["argv"] == _cli_argv(contract, fixture, out, runs="3")
    assert summary["n"] == 3
    assert summary["model"] == "sonnet"
    assert summary["seed"] is None
    assert summary["seed_note"] == "claude -p exposes no seed flag"
    assert summary["contract"]["path"] == str(contract)
    assert summary["fixture"]["path"] == str(fixture)
    assert summary["contract_delivery"] == "inline"
    for key in ("items", "own_not_own_correct", "own_not_own_total",
                "three_way_correct", "three_way_total", "systematic"):
        assert key in summary


def test_main_cli_runs_zero_exits_2(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(coldread_role_split.subprocess, "run", lambda *a, **k: calls.append(a))
    monkeypatch.setattr(coldread_role_split.shutil, "which", lambda name: "/usr/bin/claude")
    contract = _write_cli_contract(tmp_path)
    fixture = _write_cli_fixture(tmp_path)
    out = tmp_path / "out"
    rc = main(_cli_argv(contract, fixture, out, runs="0"))
    assert rc == 2
    assert calls == []


def test_main_cli_missing_claude_binary_exits_2(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(coldread_role_split.subprocess, "run",
                         lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not call subprocess.run")))
    monkeypatch.setattr(coldread_role_split.shutil, "which", lambda name: None)
    contract = _write_cli_contract(tmp_path)
    fixture = _write_cli_fixture(tmp_path)
    out = tmp_path / "out"
    rc = main(_cli_argv(contract, fixture, out))
    assert rc == 2
    combined = capsys.readouterr()
    assert "claude" in (combined.err + combined.out)


def test_main_cli_resume_skips_existing_run_files(tmp_path, monkeypatch):
    calls = []

    def fake_run(argv, **kwargs):
        calls.append(argv)
        return coldread_role_split.subprocess.CompletedProcess(argv, 0, stdout=_canned_stdout(), stderr="")

    monkeypatch.setattr(coldread_role_split.subprocess, "run", fake_run)
    monkeypatch.setattr(coldread_role_split.shutil, "which", lambda name: "/usr/bin/claude")

    out = tmp_path / "out"
    out.mkdir()

    contract = _write_cli_contract(tmp_path)
    fixture = _write_cli_fixture(tmp_path)
    contract_hash = coldread_role_split.hashlib.sha256(contract.read_bytes()).hexdigest()
    fixture_hash = coldread_role_split.hashlib.sha256(fixture.read_bytes()).hexdigest()
    prompt = coldread_role_split.build_prompt(
        contract.read_text(encoding="utf-8"), _cli_fixture_dict(), "adversary"
    )
    prompt_hash = coldread_role_split.hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    for i in (1, 2):
        header = "\n".join(
            [
                f"# command: /usr/bin/claude -p --model sonnet --output-format text  (prompt on stdin, sha256 {prompt_hash})",
                f"# contract: {contract} sha256 {contract_hash}",
                f"# fixture: {fixture} sha256 {fixture_hash}",
                f"# run: {i} of 3",
                "# model: sonnet",
                f"# prompt-sha256: {prompt_hash}",
            ]
        )
        (out / f"run-{i}.txt").write_text(header + f"\n\n{_canned_stdout()}", encoding="utf-8")

    argv = _cli_argv(contract, fixture, out) + ["--resume"]
    rc = main(argv)
    assert rc == 0
    assert len(calls) == 1
    summary = _json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert summary["n"] == 3
    statuses = {r["i"]: r["status"] for r in summary["runs"]}
    assert statuses[1] == "resumed"
    assert statuses[2] == "resumed"
    assert statuses[3] == "ok"


def test_main_cli_timeout_expired_continues_loop(tmp_path, monkeypatch):
    calls = []

    def fake_run(argv, **kwargs):
        calls.append(argv)
        if len(calls) == 2:
            raise coldread_role_split.subprocess.TimeoutExpired(cmd=argv, timeout=kwargs.get("timeout", 180))
        return coldread_role_split.subprocess.CompletedProcess(argv, 0, stdout=_canned_stdout(), stderr="")

    monkeypatch.setattr(coldread_role_split.subprocess, "run", fake_run)
    monkeypatch.setattr(coldread_role_split.shutil, "which", lambda name: "/usr/bin/claude")

    contract = _write_cli_contract(tmp_path)
    fixture = _write_cli_fixture(tmp_path)
    out = tmp_path / "out"
    rc = main(_cli_argv(contract, fixture, out))
    assert rc == 0
    assert len(calls) == 3

    text2 = (out / "run-2.txt").read_text(encoding="utf-8")
    assert "# error:" in text2

    summary = _json.loads((out / "summary.json").read_text(encoding="utf-8"))
    run2 = next(r for r in summary["runs"] if r["i"] == 2)
    assert run2["status"] == "timeout"
    for item in summary["items"].values():
        assert item["counts"].get("unparsed", 0) >= 1


# ---------------------------------------------------------------------------
# W1-03 fix round: package-level coverage for wave-end:1 findings 01/02/03/04/06/07/08
# ---------------------------------------------------------------------------


def test_run_once_sends_prompt_on_stdin_not_argv(monkeypatch):
    """finding 01: the prompt must never be an argv element -- it must
    arrive via `subprocess.run`'s `input=` kwarg -- so a prompt whose
    text starts with `---` (real contract frontmatter) cannot be parsed
    as an unknown option."""
    captured = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        captured["kwargs"] = kwargs
        return coldread_role_split.subprocess.CompletedProcess(argv, 0, stdout="ok", stderr="")

    monkeypatch.setattr(coldread_role_split.subprocess, "run", fake_run)

    prompt = "---\nname: x\n---\nbody"
    argv, body, returncode = coldread_role_split.run_once("claude", "sonnet", prompt, timeout=30)
    assert returncode == 0
    assert body == "ok"
    assert prompt not in argv
    assert captured["kwargs"]["input"] == prompt
    assert argv == ["claude", "-p", "--model", "sonnet", "--output-format", "text"]


def test_main_records_nonzero_returncode_as_error_and_counts_failed_runs(tmp_path, monkeypatch):
    """finding 02: a non-zero `claude` return code must be recorded
    "error", never "ok", with `returncode` carried on the run entry and
    tallied into `summary.json["failed_runs"]`."""

    def fake_run(argv, **kwargs):
        return coldread_role_split.subprocess.CompletedProcess(
            argv, 3, stdout="", stderr="boom"
        )

    monkeypatch.setattr(coldread_role_split.subprocess, "run", fake_run)
    monkeypatch.setattr(coldread_role_split.shutil, "which", lambda name: "/usr/bin/claude")

    contract = _write_cli_contract(tmp_path)
    fixture = _write_cli_fixture(tmp_path)
    out = tmp_path / "out"
    rc = main(_cli_argv(contract, fixture, out, runs="1"))
    assert rc == 0
    summary = _json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert summary["runs"][0]["status"] == "error"
    assert summary["runs"][0]["returncode"] == 3
    assert summary["failed_runs"] == 1
    body = (out / "run-1.txt").read_text(encoding="utf-8").split("\n\n", 1)[1]
    assert "# error: exit 3" in body


def test_main_resume_rejects_mismatched_header_field(tmp_path, monkeypatch, capsys):
    """finding 03: --resume must validate every resumed header (contract
    hash, fixture hash, prompt hash, model, run count N) against the
    current invocation; a mismatch exits 2 with an error naming the
    field and writes no summary.json."""
    monkeypatch.setattr(
        coldread_role_split.subprocess, "run",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not run on a header mismatch")),
    )
    monkeypatch.setattr(coldread_role_split.shutil, "which", lambda name: "/usr/bin/claude")

    contract = _write_cli_contract(tmp_path)
    fixture = _write_cli_fixture(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    prompt = coldread_role_split.build_prompt(
        contract.read_text(encoding="utf-8"), _cli_fixture_dict(), "adversary"
    )
    prompt_hash = coldread_role_split.hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    fixture_hash = coldread_role_split.hashlib.sha256(fixture.read_bytes()).hexdigest()
    (out / "run-1.txt").write_text(
        "\n".join(
            [
                f"# command: /usr/bin/claude -p --model sonnet --output-format text  (prompt on stdin, sha256 {prompt_hash})",
                "# contract: stale-path sha256 not-the-real-hash",
                f"# fixture: {fixture} sha256 {fixture_hash}",
                "# run: 1 of 3",
                "# model: sonnet",
                f"# prompt-sha256: {prompt_hash}",
            ]
        )
        + f"\n\n{_canned_stdout()}",
        encoding="utf-8",
    )

    rc = main(_cli_argv(contract, fixture, out) + ["--resume"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "error:" in err
    assert "contract" in err
    assert not (out / "summary.json").exists()


def test_run_once_docstring_cites_captured_help_evidence():
    """finding 04: run_once's docstring must cite the checked-in captured
    `claude -p --help` evidence file by name, grounding the stdin
    delivery, --model, --output-format, and no-seed-flag claims instead
    of relying on an unverified assumption."""
    assert "claude-p-help-2026-09-05.txt" in (coldread_role_split.run_once.__doc__ or "")


def test_main_out_existing_file_and_missing_contract_exit_two(tmp_path, monkeypatch, capsys):
    """finding 06: --out naming an existing regular file, and a missing
    --contract path, must each exit 2 with an error: message naming the
    path -- never an uncaught traceback -- and never call the (faked,
    assertion-raising) claude binary."""
    monkeypatch.setattr(
        coldread_role_split.subprocess, "run",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not be called")),
    )
    monkeypatch.setattr(coldread_role_split.shutil, "which", lambda name: "/usr/bin/claude")

    contract = _write_cli_contract(tmp_path)
    fixture = _write_cli_fixture(tmp_path)

    out_is_a_file = tmp_path / "out_is_a_file"
    out_is_a_file.write_text("not a directory", encoding="utf-8")
    rc = main(_cli_argv(contract, fixture, out_is_a_file, runs="1"))
    assert rc == 2
    err = capsys.readouterr().err
    assert "error:" in err
    assert str(out_is_a_file) in err

    missing_contract = tmp_path / "does-not-exist.md"
    rc = main(_cli_argv(missing_contract, fixture, tmp_path / "out2", runs="1"))
    assert rc == 2
    err = capsys.readouterr().err
    assert "error:" in err
    assert str(missing_contract) in err
