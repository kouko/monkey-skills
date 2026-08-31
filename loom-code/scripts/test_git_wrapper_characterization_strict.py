"""Characterization pins for the raise family behind the three git wrappers
this repo is about to consolidate (Task 2, script-helper-extraction plan).

Zero prior tests asserted the exception TYPE raised on a non-zero git exit
for ``live_gate_station_receipt._git`` / ``live_host_review_gate._git`` /
``batch_review_cli._run_git`` before this file. Task 7-9 replace their
bodies with a shared ``git_exec.py`` core; these pins are the net that
must still hold after that move — a silent swallow of the raise is a
regression this file exists to catch.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

import live_gate_station_receipt as station
import live_host_review_gate as gate


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "loom-code" / "scripts"


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


cli = _load("batch_review_cli_for_git_wrapper_characterization", "batch_review_cli.py")
rb = cli.rb  # same module instance cli._run_git raises against — not a fresh load


# ---------------------------------------------------------------------------
# live_gate_station_receipt._git
# ---------------------------------------------------------------------------


def test_live_gate_station_receipt_git_raises_called_process_error(tmp_path) -> None:
    """A non-zero git exit (here: not a repo) propagates as-is —
    check=True's own CalledProcessError, not a wrapped/swallowed error."""
    with pytest.raises(subprocess.CalledProcessError):
        station._git(tmp_path, "status")


def test_live_gate_station_receipt_git_propagates_oserror(tmp_path, monkeypatch) -> None:
    def _raises(*args, **kwargs):
        raise OSError("git binary missing")

    monkeypatch.setattr(station.subprocess, "run", _raises)
    with pytest.raises(OSError):
        station._git(tmp_path, "status")


def test_live_gate_station_receipt_git_passes_timeout_20(tmp_path, monkeypatch) -> None:
    captured: dict[str, object] = {}

    def _capture(*args, **kwargs):
        captured.update(kwargs)
        return subprocess.CompletedProcess(args=args[0] if args else [], returncode=0, stdout="")

    monkeypatch.setattr(station.subprocess, "run", _capture)
    station._git(tmp_path, "status")
    assert captured["timeout"] == 20


# ---------------------------------------------------------------------------
# live_host_review_gate._git
# ---------------------------------------------------------------------------


def test_live_host_review_gate_git_raises_called_process_error(tmp_path) -> None:
    with pytest.raises(subprocess.CalledProcessError):
        gate._git(tmp_path, "status")


def test_live_host_review_gate_git_propagates_oserror(tmp_path, monkeypatch) -> None:
    def _raises(*args, **kwargs):
        raise OSError("git binary missing")

    monkeypatch.setattr(gate.subprocess, "run", _raises)
    with pytest.raises(OSError):
        gate._git(tmp_path, "status")


def test_live_host_review_gate_git_passes_timeout_20(tmp_path, monkeypatch) -> None:
    captured: dict[str, object] = {}

    def _capture(*args, **kwargs):
        captured.update(kwargs)
        return subprocess.CompletedProcess(args=args[0] if args else [], returncode=0, stdout="")

    monkeypatch.setattr(gate.subprocess, "run", _capture)
    gate._git(tmp_path, "status")
    assert captured["timeout"] == 20


# ---------------------------------------------------------------------------
# batch_review_cli._run_git
# ---------------------------------------------------------------------------


def test_run_git_nonzero_raises_packet_refused(tmp_path) -> None:
    """Non-zero git exit (here: not a repo) must surface as PacketRefused
    whose message starts with the ``git <args> failed:`` prefix — not the
    raw CalledProcessError/return code."""
    with pytest.raises(rb.PacketRefused) as excinfo:
        cli._run_git(tmp_path, "status")
    assert str(excinfo.value).startswith("git status failed:")


def test_run_git_timeout_raises_packet_refused(tmp_path, monkeypatch) -> None:
    def _hangs(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0] if args else "git", timeout=30)

    monkeypatch.setattr(cli.subprocess, "run", _hangs)
    with pytest.raises(rb.PacketRefused):
        cli._run_git(tmp_path, "status")
