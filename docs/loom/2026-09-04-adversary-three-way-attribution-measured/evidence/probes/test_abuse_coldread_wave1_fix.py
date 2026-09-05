"""Fix-round adversary probes for `loom-code/scripts/coldread_role_split.py`
targeting wave-end:1 findings 01 (stdin prompt delivery), 03 (resume
header validation), and 04 (grounding evidence for the `claude -p`
invocation) — the three findings `test_abuse_coldread_wave1.py` did not
cover (that file's four rewritten functions cover 02, 06, 07, 08).

`subprocess.run` and `shutil.which` are monkeypatched throughout; no
case calls the real `claude` binary. All probes here are RED against
the pre-fix module.
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
EVIDENCE_DIR = (
    REPO_ROOT
    / "docs"
    / "loom"
    / "2026-09-04-adversary-three-way-attribution-measured"
    / "evidence"
)
HELP_EVIDENCE_PATH = EVIDENCE_DIR / "claude-p-help-2026-09-05.txt"

sys.path.insert(0, str(SCRIPTS_DIR))

import coldread_role_split as module  # noqa: E402  (import after sys.path mutation, by design)

main = module.main


def _write_contract(tmp_path: Path, text: str = "a small contract", name: str = "contract.md") -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def _write_fixture(tmp_path: Path, items: list, name: str = "fixture.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps({"items": items, "source": "wave1-fix-abuse"}), encoding="utf-8")
    return path


def _base_argv(contract: Path, fixture: Path, out: Path, runs: str = "1", role: str = "reviewer") -> list:
    return [
        "--contract", str(contract),
        "--fixture", str(fixture),
        "--role", role,
        "--runs", runs,
        "--out", str(out),
    ]


# ---------------------------------------------------------------------------
# 01 -- prompt delivered on stdin, never as an argv element
# ---------------------------------------------------------------------------


def test_run_once_frontmatter_prompt_delivered_on_stdin_not_argv(tmp_path, monkeypatch):
    """A prompt built from a contract whose text starts with `---\\nname:
    x\\n---` (real-contract-shaped frontmatter that `claude`'s option
    parser rejects as an unknown option when passed positionally) must
    arrive verbatim in `subprocess.run`'s `input=` kwarg and must never
    appear, in whole or in part, in the argv list passed to
    `subprocess.run`."""
    captured = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        captured["kwargs"] = kwargs
        return module.subprocess.CompletedProcess(argv, 0, stdout="1. mine -- x", stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    contract_text = "---\nname: x\n---\nSome contract body."
    fixture = {"items": [{"n": 1, "text": "a", "expected": "reviewer"}]}
    prompt = module.build_prompt(contract_text, fixture, "reviewer")
    assert prompt.startswith("---\nname: x\n---")

    argv, body, returncode = module.run_once("claude", "sonnet", prompt, timeout=30)

    assert returncode == 0
    assert "input" in captured["kwargs"], "prompt must be sent via input=, not argv"
    assert captured["kwargs"]["input"] == prompt
    assert captured["kwargs"].get("capture_output") is True
    assert captured["kwargs"].get("text") is True
    assert captured["kwargs"].get("timeout") == 30
    assert prompt not in captured["argv"]
    for part in captured["argv"]:
        assert "---" not in part, f"frontmatter leaked into argv element {part!r}"
    assert captured["argv"] == ["claude", "-p", "--model", "sonnet", "--output-format", "text"]
    assert argv == captured["argv"]


def test_main_command_header_names_stdin_delivery_with_prompt_sha(tmp_path, monkeypatch):
    """The `# command:` header line written to each run file must
    document that the prompt travels on stdin and must carry the
    prompt's sha256, e.g. `claude -p --model sonnet --output-format
    text  (prompt on stdin, sha256 <hex>)` -- so a reader of the
    transcript can see how the prompt was delivered without it being
    printed inline."""

    def fake_run(argv, **kwargs):
        return module.subprocess.CompletedProcess(argv, 0, stdout="1. mine -- x", stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.shutil, "which", lambda name: "/usr/bin/claude")

    contract = _write_contract(tmp_path, text="---\nname: x\n---\nbody")
    fixture = _write_fixture(tmp_path, [{"n": 1, "text": "a", "expected": "reviewer"}])
    out = tmp_path / "out"

    rc = main(_base_argv(contract, fixture, out))
    assert rc == 0

    header = (out / "run-1.txt").read_text(encoding="utf-8").split("\n\n", 1)[0]
    command_line = next(line for line in header.splitlines() if line.startswith("# command:"))
    assert "prompt on stdin" in command_line
    assert "sha256" in command_line

    prompt_text = module.build_prompt(contract.read_text(encoding="utf-8"), json.loads(fixture.read_text()), "reviewer")
    expected_hash = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
    assert expected_hash in command_line
    assert "---" not in command_line


# ---------------------------------------------------------------------------
# 03 -- --resume validates every resumed run's header against current inputs
# ---------------------------------------------------------------------------


def test_main_resume_mismatched_contract_hash_exits_two_no_summary(tmp_path, monkeypatch, capsys):
    """A `run-1.txt` whose `# contract: ... sha256 <hex>` header does not
    match the sha256 of the `--contract` file passed on this invocation
    must make `--resume` exit 2 naming the mismatching field and file,
    write no `summary.json`, and never call the real (faked) claude
    binary."""

    def fake_run(argv, **kwargs):
        raise AssertionError("must not be called when a resumed header mismatches")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.shutil, "which", lambda name: "/usr/bin/claude")

    contract = _write_contract(tmp_path, text="contract v2")
    fixture = _write_fixture(tmp_path, [{"n": 1, "text": "a", "expected": "reviewer"}])
    out = tmp_path / "out"
    out.mkdir()
    stale_contract_hash = hashlib.sha256(b"contract v1 -- a different file").hexdigest()
    fixture_hash = hashlib.sha256(fixture.read_bytes()).hexdigest()
    prompt = module.build_prompt("contract v1", {"items": [{"n": 1, "text": "a", "expected": "reviewer"}]}, "reviewer")
    prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    (out / "run-1.txt").write_text(
        "\n".join(
            [
                "# command: claude -p --model sonnet --output-format text  (prompt on stdin, sha256 aaaa)",
                f"# contract: {contract} sha256 {stale_contract_hash}",
                f"# fixture: {fixture} sha256 {fixture_hash}",
                "# run: 1 of 1",
                "# model: sonnet",
                f"# prompt-sha256: {prompt_hash}",
            ]
        )
        + "\n\n1. mine -- old answer",
        encoding="utf-8",
    )

    rc = main(_base_argv(contract, fixture, out) + ["--resume"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "error:" in err
    assert "contract" in err.lower()
    assert not (out / "summary.json").exists()


def test_main_resume_matching_headers_succeeds_without_rerunning(tmp_path, monkeypatch):
    """A control case for the probe above: when every resumed header
    field matches the current invocation exactly (contract sha, fixture
    sha, prompt sha, run/N, model), `--resume` must succeed, write
    `summary.json`, and never call the (faked, assertion-raising)
    claude binary."""

    def fake_run(argv, **kwargs):
        raise AssertionError("must not run -- this item is fully resumed from disk")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.shutil, "which", lambda name: "/usr/bin/claude")

    contract = _write_contract(tmp_path, text="contract body")
    fixture = _write_fixture(tmp_path, [{"n": 1, "text": "a", "expected": "reviewer"}])
    out = tmp_path / "out"
    out.mkdir()

    contract_hash = hashlib.sha256(contract.read_bytes()).hexdigest()
    fixture_hash = hashlib.sha256(fixture.read_bytes()).hexdigest()
    prompt = module.build_prompt(
        contract.read_text(encoding="utf-8"), json.loads(fixture.read_text()), "reviewer"
    )
    prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    (out / "run-1.txt").write_text(
        "\n".join(
            [
                "# command: claude -p --model sonnet --output-format text  (prompt on stdin, sha256 "
                + prompt_hash + ")",
                f"# contract: {contract} sha256 {contract_hash}",
                f"# fixture: {fixture} sha256 {fixture_hash}",
                "# run: 1 of 1",
                "# model: sonnet",
                f"# prompt-sha256: {prompt_hash}",
            ]
        )
        + "\n\n1. mine -- resumed answer",
        encoding="utf-8",
    )

    rc = main(_base_argv(contract, fixture, out, runs="1") + ["--resume"])
    assert rc == 0
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert summary["items"]["1"]["counts"] == {"mine": 1}


# ---------------------------------------------------------------------------
# 04 -- grounding evidence for the claude CLI surface relied on
# ---------------------------------------------------------------------------


def test_help_evidence_file_captures_relied_on_claude_p_flags():
    """The checked-in evidence file
    `docs/loom/2026-09-04-adversary-three-way-attribution-measured/evidence/claude-p-help-2026-09-05.txt`
    must exist and contain the captured `claude -p --help` output that
    grounds this module's invocation: it must mention `--output-format`
    and `--model`, and it must NOT mention `--seed` (the module's claim
    that `claude -p` exposes no seed flag)."""
    assert HELP_EVIDENCE_PATH.is_file(), f"missing grounding evidence file: {HELP_EVIDENCE_PATH}"
    text = HELP_EVIDENCE_PATH.read_text(encoding="utf-8")
    assert "--output-format" in text
    assert "--model" in text
    assert "--seed" not in text


def test_run_once_docstring_cites_help_evidence_filename():
    """`run_once`'s docstring must cite the captured-help evidence file
    by name, so a reader can verify the stdin-delivery, `--model`,
    `--output-format text`, and no-seed-flag claims against a real
    captured `claude -p --help` transcript instead of trusting an
    unsupported assumption."""
    docstring = module.run_once.__doc__ or ""
    assert "claude-p-help-2026-09-05.txt" in docstring


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
