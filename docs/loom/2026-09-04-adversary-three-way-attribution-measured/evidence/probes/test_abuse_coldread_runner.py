"""Adversary probes for W1-03 (`loom-code/scripts/coldread_role_split.py`
`build_prompt`, `run_once`, `main`), written before those functions exist.

Every case here is RED right now with `AttributeError` -- `build_prompt`,
`run_once`, and `main` are not defined on the module yet (only
`parse_response` and `score` from W1-02 exist). That is the intended RED
for the implementer's failing-test-first task. Once the functions land,
every probe must go GREEN unmodified; a probe that needs the
implementation weakened to pass is not a probe.

Interface pinned by the dispatch packet (loom-code plan.md W1-03):

    build_prompt(contract_text: str, fixture: dict, role: str) -> str
        Contains the contract text verbatim, all item texts verbatim in
        order, and the answer-format instruction
        `<n>. mine|other|implementer -- <reason>`. Never names the other
        role's contract or the expected owners.

    run_once(claude_bin: str, model: str, prompt: str, timeout: int)
        -> tuple[list[str], str]
        Returns (argv, stdout); argv is
        [claude_bin, "-p", prompt, "--model", model, "--output-format", "text"].
        Raises subprocess.TimeoutExpired upward.

    main(argv: list[str] | None = None) -> int
        Writes run-<i>.txt (5 "# " header lines, blank line, raw stdout)
        and summary.json. `--runs 0`/negative -> exit 2. Missing `claude`
        binary (shutil.which -> None) -> exit 2 naming the binary.
        Non-`--resume` run into an out dir already holding run files ->
        exit 2, existing files untouched. `--resume` reads back existing
        run-<i>.txt (header stripped at the first blank line) instead of
        re-running, and still scores all N. A TimeoutExpired on one run
        writes that run's transcript with `# error:`, scores `unparsed`
        for every item of that run, and the loop continues to the next
        run.
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


def _write_fixture(tmp_path: Path, name: str = "fixture.json") -> Path:
    """A tiny 3-item fixture covering all three expected owners."""
    fixture = {
        "items": [
            {"n": 1, "text": "item one -- plan says 23, review has 126", "expected": "reviewer"},
            {"n": 2, "text": "item two -- stale origin short-circuits the probe", "expected": "adversary"},
            {"n": 3, "text": "item three -- happy path has no unit test", "expected": "implementer"},
        ],
        "source": "test fixture, not the real 8-item file",
    }
    path = tmp_path / name
    path.write_text(json.dumps(fixture), encoding="utf-8")
    return path


def _write_contract(tmp_path: Path, text: str = "dummy contract text", name: str = "contract.md") -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def _canned_stdout() -> str:
    return "1. mine -- x\n2. other -- y\n3. implementer -- z"


def _base_argv(contract: Path, fixture: Path, out: Path, runs: str = "3", role: str = "adversary") -> list:
    return [
        "--contract", str(contract),
        "--fixture", str(fixture),
        "--role", role,
        "--runs", runs,
        "--out", str(out),
    ]


# ---------------------------------------------------------------------------
# 1. Boundary: zero and negative --runs
# ---------------------------------------------------------------------------


def test_main_runs_zero_exits_2_without_calling_subprocess(tmp_path, monkeypatch, capsys):
    """`--runs 0` must exit 2 with a message and must never invoke subprocess.run."""
    calls = []
    monkeypatch.setattr(module.subprocess, "run", lambda *a, **k: calls.append((a, k)))
    monkeypatch.setattr(module.shutil, "which", lambda name: "/usr/bin/claude")
    contract = _write_contract(tmp_path)
    fixture = _write_fixture(tmp_path)
    out = tmp_path / "out"
    rc = module.main(_base_argv(contract, fixture, out, runs="0"))
    assert rc == 2
    captured = capsys.readouterr()
    assert captured.err.strip() or captured.out.strip()
    assert calls == []


def test_main_runs_negative_exits_2_without_calling_subprocess(tmp_path, monkeypatch, capsys):
    """`--runs -3` must exit 2 the same way as `--runs 0`, not attempt -3 iterations."""
    calls = []
    monkeypatch.setattr(module.subprocess, "run", lambda *a, **k: calls.append((a, k)))
    monkeypatch.setattr(module.shutil, "which", lambda name: "/usr/bin/claude")
    contract = _write_contract(tmp_path)
    fixture = _write_fixture(tmp_path)
    out = tmp_path / "out"
    rc = module.main(_base_argv(contract, fixture, out, runs="-3"))
    assert rc == 2
    assert calls == []


# ---------------------------------------------------------------------------
# 2. Failing dependency: missing claude binary
# ---------------------------------------------------------------------------


def test_main_missing_claude_binary_exits_2_naming_binary(tmp_path, monkeypatch, capsys):
    """shutil.which returning None must exit 2 with a message naming the binary,
    and must not attempt a subprocess call."""
    calls = []
    monkeypatch.setattr(module.subprocess, "run", lambda *a, **k: calls.append((a, k)))
    monkeypatch.setattr(module.shutil, "which", lambda name: None)
    contract = _write_contract(tmp_path)
    fixture = _write_fixture(tmp_path)
    out = tmp_path / "out"
    rc = module.main(_base_argv(contract, fixture, out))
    assert rc == 2
    captured = capsys.readouterr()
    combined = captured.err + captured.out
    assert "claude" in combined
    assert calls == []


# ---------------------------------------------------------------------------
# 3. Wrong order / forgotten state: refuse to overwrite evidence
# ---------------------------------------------------------------------------


def test_main_existing_run_dir_without_resume_exits_2_preserves_file(tmp_path, monkeypatch):
    """Running into an out dir that already holds run-1.txt, without --resume,
    must exit 2 and must leave the existing file byte-for-byte unchanged."""
    calls = []

    def fake_run(argv, **kwargs):
        calls.append(argv)
        return module.subprocess.CompletedProcess(argv, 0, stdout=_canned_stdout(), stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.shutil, "which", lambda name: "/usr/bin/claude")

    out = tmp_path / "out"
    out.mkdir()
    existing = out / "run-1.txt"
    existing.write_text("PRE-EXISTING EVIDENCE, MUST NOT BE OVERWRITTEN", encoding="utf-8")

    contract = _write_contract(tmp_path)
    fixture = _write_fixture(tmp_path)
    rc = module.main(_base_argv(contract, fixture, out))
    assert rc == 2
    assert existing.read_text(encoding="utf-8") == "PRE-EXISTING EVIDENCE, MUST NOT BE OVERWRITTEN"
    assert calls == []


def test_main_resume_skips_existing_runs_calls_subprocess_once(tmp_path, monkeypatch):
    """With --resume and run-1.txt/run-2.txt already present, only run 3 is
    actually executed (subprocess.run called exactly once), and summary.json
    still reports n == 3 (all three runs scored, two from disk).

    wave-end:1-03 follow-up: `--resume` now validates every resumed
    header's contract/fixture/prompt hashes, run/N and model against the
    current invocation before trusting it, so the two hand-written run
    files must carry the full valid header (computed the same way the
    module computes it) instead of the pre-fix minimal one -- otherwise
    the validation this probe does not target rejects them before the
    behaviour under test (resume skips re-running, still scores all N)
    is ever exercised."""
    calls = []

    def fake_run(argv, **kwargs):
        calls.append(argv)
        return module.subprocess.CompletedProcess(argv, 0, stdout=_canned_stdout(), stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.shutil, "which", lambda name: "/usr/bin/claude")

    out = tmp_path / "out"
    out.mkdir()

    contract = _write_contract(tmp_path)
    fixture_path = _write_fixture(tmp_path)
    contract_hash = hashlib.sha256(contract.read_bytes()).hexdigest()
    fixture_bytes = fixture_path.read_bytes()
    fixture_hash = hashlib.sha256(fixture_bytes).hexdigest()
    fixture = json.loads(fixture_bytes.decode("utf-8"))
    prompt = module.build_prompt(contract.read_text(encoding="utf-8"), fixture, "adversary")
    prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    for i in (1, 2):
        header = "\n".join(
            [
                f"# command: claude -p --model sonnet --output-format text  (prompt on stdin, sha256 {prompt_hash})",
                f"# contract: {contract} sha256 {contract_hash}",
                f"# fixture: {fixture_path} sha256 {fixture_hash}",
                f"# run: {i} of 3",
                "# model: sonnet",
                f"# prompt-sha256: {prompt_hash}",
            ]
        )
        (out / f"run-{i}.txt").write_text(header + f"\n\n{_canned_stdout()}", encoding="utf-8")

    argv = _base_argv(contract, fixture_path, out) + ["--resume"]
    rc = module.main(argv)
    assert rc == 0
    assert len(calls) == 1
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert summary["n"] == 3


# ---------------------------------------------------------------------------
# 4. Failure of a dependency mid-loop: TimeoutExpired on one run
# ---------------------------------------------------------------------------


def test_main_timeout_expired_run_written_as_error_and_loop_continues(tmp_path, monkeypatch):
    """A TimeoutExpired on run 2 of 3 must not abort the batch: run-2.txt gets
    an `# error:` line and that run is scored unparsed for every item, but
    run-3 is still attempted and written."""
    calls = []

    def fake_run(argv, **kwargs):
        calls.append(argv)
        if len(calls) == 2:
            raise module.subprocess.TimeoutExpired(cmd=argv, timeout=kwargs.get("timeout", 180))
        return module.subprocess.CompletedProcess(argv, 0, stdout=_canned_stdout(), stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.shutil, "which", lambda name: "/usr/bin/claude")

    contract = _write_contract(tmp_path)
    fixture = _write_fixture(tmp_path)
    out = tmp_path / "out"
    rc = module.main(_base_argv(contract, fixture, out))

    assert len(calls) == 3, "the loop must still attempt run 3 after run 2 times out"
    assert (out / "run-3.txt").exists()
    text2 = (out / "run-2.txt").read_text(encoding="utf-8")
    assert "# error:" in text2

    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    run2_entry = next(r for r in summary["runs"] if r["i"] == 2)
    assert run2_entry["status"] == "timeout"
    for item in summary["items"].values():
        assert item["counts"].get("unparsed", 0) >= 1


# ---------------------------------------------------------------------------
# 5. Hostile: the contract text must never leak through the command header
# ---------------------------------------------------------------------------


def test_main_command_header_never_leaks_contract_text_but_hash_matches(tmp_path, monkeypatch):
    """The `# command:` header line must never contain the raw contract text
    (the prompt is redacted), yet summary.json's contract sha256 must equal
    hashlib.sha256 of the contract file's bytes."""
    contract_text = "SECRET CONTRACT TEXT MUST NOT LEAK INTO run-1.txt HEADER"
    contract = _write_contract(tmp_path, text=contract_text)
    fixture = _write_fixture(tmp_path)

    def fake_run(argv, **kwargs):
        return module.subprocess.CompletedProcess(argv, 0, stdout=_canned_stdout(), stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.shutil, "which", lambda name: "/usr/bin/claude")

    out = tmp_path / "out"
    rc = module.main(_base_argv(contract, fixture, out, runs="1"))
    assert rc == 0

    text = (out / "run-1.txt").read_text(encoding="utf-8")
    header = text.split("\n\n", 1)[0]
    assert "SECRET CONTRACT TEXT MUST NOT LEAK" not in header

    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    expected_hash = hashlib.sha256(contract_text.encode("utf-8")).hexdigest()
    assert summary["contract"]["sha256"] == expected_hash


def test_main_summary_contract_delivery_is_inline(tmp_path, monkeypatch):
    """summary.json must record contract_delivery == 'inline' per the
    agent-decided risk note in the plan."""

    def fake_run(argv, **kwargs):
        return module.subprocess.CompletedProcess(argv, 0, stdout=_canned_stdout(), stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.shutil, "which", lambda name: "/usr/bin/claude")

    contract = _write_contract(tmp_path)
    fixture = _write_fixture(tmp_path)
    out = tmp_path / "out"
    rc = module.main(_base_argv(contract, fixture, out, runs="1"))
    assert rc == 0
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert summary["contract_delivery"] == "inline"


# ---------------------------------------------------------------------------
# 6. build_prompt: verbatim items, no leaked expected-owner labels, hostile chars
# ---------------------------------------------------------------------------


def test_build_prompt_includes_all_item_texts_verbatim_in_order():
    """build_prompt must embed every fixture item's text verbatim, in item order."""
    fixture = {
        "items": [
            {"n": 1, "text": "AAA first item text", "expected": "reviewer"},
            {"n": 2, "text": "BBB second item text", "expected": "adversary"},
        ]
    }
    prompt = module.build_prompt("a contract", fixture, "adversary")
    pos_a = prompt.index("AAA first item text")
    pos_b = prompt.index("BBB second item text")
    assert pos_a < pos_b


def test_build_prompt_never_leaks_expected_owner_sentinel():
    """build_prompt must never leak a fixture item's `expected` value into the
    prompt text -- probed with a sentinel token that has no other reason to
    appear, so any leak is unambiguous."""
    fixture = {
        "items": [
            {"n": 1, "text": "does this belong to the reviewer or not", "expected": "ZZZ_OWNER_SENTINEL_9f3"},
        ]
    }
    prompt = module.build_prompt("a contract", fixture, "adversary")
    assert "ZZZ_OWNER_SENTINEL_9f3" not in prompt


def test_build_prompt_hostile_format_chars_roundtrip_unchanged():
    """Contract text and item text containing `{`, `}`, and `%` (format-string
    injection payloads) must survive verbatim -- a naive str.format()/%-format
    implementation would raise KeyError/TypeError or silently mangle them."""
    contract_text = "weird {curly} %s %(name)s {0} braces"
    fixture = {
        "items": [
            {"n": 1, "text": "item with {braces} and %d percent and {1}", "expected": "reviewer"},
        ]
    }
    prompt = module.build_prompt(contract_text, fixture, "reviewer")
    assert contract_text in prompt
    assert "item with {braces} and %d percent and {1}" in prompt


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
