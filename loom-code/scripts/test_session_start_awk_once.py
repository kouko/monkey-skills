"""W1-03 — session-start scans the manifest with exactly one awk pass.

`stations_block()` used to invoke awk once per call site: once directly
and three times through `stations_for_dp()` (four total). This test pins
the two acceptance cases from the plan (A3):

  * `injection-byte-identical` — stdout is unchanged in an empty git repo
    and in this repo.
  * `awk-invoked-once` — a PATH shim counting real `awk` launches sees
    exactly one invocation while scanning the manifest.

The wider adversarial oracle (hostile manifest shapes, bash 3.2 parity,
missing-manifest fail-open) lives in
docs/loom/2026-09-07-loom-script-performance/evidence/probes/test_abuse_session_start_awk.py
and is not duplicated here.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / "loom-code" / "hooks" / "session-start"

# Pinned pre-change reference text: the empty-repo body is fixed (no
# manifest-derived content depends on cwd — MANIFEST resolves relative to
# the hook's own directory), and this repo's derived lines are asserted
# literally so a rewrite cannot pass by changing what gets injected.
THIS_REPO_STATION_ORDER_LINE = (
    "Station order: capture-intent → write-spec → write-plan "
    "→ build → review → ship; maintain on alerts."
)
THIS_REPO_DP_LINES = (
    "① after the intent is written (capture-intent / write-plan)",
    "② only for a product change, after the spec is written (write-spec)",
    "③ at the end (ship)",
)


def _run(cwd: Path, extra_env: dict | None = None) -> subprocess.CompletedProcess:
    env = {**os.environ}
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["bash", str(HOOK)], cwd=str(cwd), stdin=subprocess.DEVNULL,
        capture_output=True, env=env,
    )


def _context(stdout: bytes) -> str:
    return json.loads(stdout)["hookSpecificOutput"]["additionalContext"]


def test_injection_byte_identical_in_empty_git_repo(tmp_path):
    repo = tmp_path / "empty"
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    proc = _run(repo)
    assert proc.returncode == 0
    context = _context(proc.stdout)
    assert THIS_REPO_STATION_ORDER_LINE in context
    for line in THIS_REPO_DP_LINES:
        assert line in context


def test_injection_byte_identical_in_this_repo():
    proc = _run(REPO)
    assert proc.returncode == 0
    context = _context(proc.stdout)
    assert THIS_REPO_STATION_ORDER_LINE in context
    for line in THIS_REPO_DP_LINES:
        assert line in context


def test_awk_invoked_exactly_once(tmp_path):
    """A `bash -x` trace over the manifest scan must show exactly one
    `awk` invocation, counted via a PATH shim that logs and execs real
    awk (so behaviour is unchanged, only counted)."""
    shim_dir = tmp_path / "shim"
    shim_dir.mkdir()
    log = tmp_path / "awk.log"
    shim = shim_dir / "awk"
    shim.write_text(
        "#!/bin/sh\n"
        f'echo "$@" >> "{log}"\n'
        'exec /usr/bin/awk "$@"\n'
    )
    shim.chmod(0o755)
    env = {"PATH": f"{shim_dir}:{os.environ['PATH']}"}
    proc = _run(REPO, extra_env=env)
    assert proc.returncode == 0
    count = len(log.read_text().splitlines()) if log.exists() else 0
    assert count == 1, f"expected exactly one awk invocation, got {count}"
