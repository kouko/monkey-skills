"""Adversarial probes for W1-03 (one awk pass in session-start).

Written before the fix (adversary-first): the rewrite must collapse the
awk-count boundary from 4 to 1 while leaving every byte of stdout, and
every derived station/decision-point line, exactly as they are today.
These probes pin the pre-change facts as a differential oracle so the
implementer cannot pass by weakening output instead of the awk count.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[5]
HOOK = REPO / "loom-code" / "hooks" / "session-start"

# --- golden oracle (probe 1): pinned TODAY, before the rewrite -------------
EMPTY_REPO_STDOUT_SHA256 = (
    "ce5edc72c06649eb71a423621abe1bbe9429703c1acf32b0f6f426d8acb94af2"
)
THIS_REPO_STATION_ORDER_LINE = (
    "Station order: capture-intent → write-spec → write-plan "
    "→ build → review → ship; maintain on alerts."
)
THIS_REPO_DP_LINES = (
    "① after the intent is written (capture-intent / write-plan)",
    "② only for a product change, after the spec is written (write-spec)",
    "③ at the end (ship)",
)


def _run(cwd: Path, bash: str = "bash", extra_env: dict | None = None) -> subprocess.CompletedProcess:
    env = {**os.environ}
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [bash, str(HOOK)], cwd=str(cwd), stdin=subprocess.DEVNULL,
        capture_output=True, env=env,
    )


def _context(stdout: bytes) -> str:
    return json.loads(stdout)["hookSpecificOutput"]["additionalContext"]


def _init_git(path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(path)], check=True)


# --- probe 1: golden stdout oracle ------------------------------------------

def test_session_start_empty_git_repo_stdout_matches_pinned_sha256(tmp_path):
    """An empty git repo's stdout must hash to the pre-change golden value."""
    repo = tmp_path / "empty"
    _init_git(repo)
    proc = _run(repo)
    assert proc.returncode == 0
    assert hashlib.sha256(proc.stdout).hexdigest() == EMPTY_REPO_STDOUT_SHA256


def test_session_start_non_git_dir_stdout_matches_pinned_sha256(tmp_path):
    """A non-git cwd must produce byte-identical stdout to an empty git repo."""
    plain = tmp_path / "not-a-repo"
    plain.mkdir()
    proc = _run(plain)
    assert proc.returncode == 0
    assert hashlib.sha256(proc.stdout).hexdigest() == EMPTY_REPO_STDOUT_SHA256


def test_session_start_this_repo_derived_lines_match_pinned_text():
    """The station-order line and all three decision-point lines, derived
    from THIS repo's real manifest, must be byte-identical pre/post-change
    (the KICKOFF-DEFAULTS tail is excluded because it drifts across commits)."""
    proc = _run(REPO)
    assert proc.returncode == 0
    context = _context(proc.stdout)
    assert THIS_REPO_STATION_ORDER_LINE in context
    for line in THIS_REPO_DP_LINES:
        assert line in context


# --- probe 2: awk invocation count (RED today: 4, want 1) ------------------

def test_session_start_manifest_scan_invokes_awk_exactly_once(tmp_path):
    """A PATH shim counts real `awk` process launches while scanning the
    manifest; today's implementation calls awk once per stations_block()
    call site (4), which the rewrite must collapse to exactly 1."""
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


# --- probe 3: bash 3.2 (macOS system bash) parity ---------------------------

def _system_bash_is_3_2() -> bool:
    try:
        out = subprocess.run(
            ["/bin/bash", "--version"], capture_output=True, text=True, check=True
        ).stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False
    return bool(re.search(r"version 3\.2", out))


@pytest.mark.skipif(
    not _system_bash_is_3_2(),
    reason="this host's /bin/bash is not 3.2 — bash-3.2-specific quoting bugs cannot be probed here",
)
def test_session_start_bash_3_2_and_path_bash_produce_identical_stdout(tmp_path):
    """A multi-line captured variable (stations_yaml) must be quoted at
    every use — bash 3.2 has no mapfile and is unforgiving of unquoted
    multi-line expansion, so /bin/bash (3.2) and PATH bash must agree."""
    repo = tmp_path / "empty"
    _init_git(repo)
    default_bash = _run(repo, bash="bash")
    system_bash = _run(repo, bash="/bin/bash")
    assert default_bash.returncode == 0
    assert system_bash.returncode == 0
    assert default_bash.stdout == system_bash.stdout


# --- probe 4: hostile manifest shapes — differential oracle -----------------

_NAME_RE = re.compile(r"^[ \t]*-[ \t]*\{name:[ \t]*([a-z0-9-]*).*")


def _oracle_stations_block(text: str) -> list[str]:
    """Pure-Python re-implementation of the current awk state machine:
    `awk '/^stations:/{f=1;next} /^[a-z_]+:/{f=0} f'`."""
    out: list[str] = []
    active = False
    for line in text.split("\n"):
        if re.match(r"^stations:", line):
            active = True
            continue
        if re.match(r"^[a-z_]+:", line):
            active = False
        if active:
            out.append(line)
    return out


def _oracle_station_names(block: list[str]) -> list[str]:
    names = []
    for line in block:
        m = _NAME_RE.match(line)
        if m:
            names.append(m.group(1))
    return names


def _oracle_stations_for_dp(block: list[str], n: int) -> str:
    matched = [l for l in block if f"decision_point: {n}" in l]
    names = []
    for line in matched:
        m = _NAME_RE.match(line)
        if m:
            names.append(m.group(1))
    return " / ".join(names)


def _run_against_manifest(tmp_path: Path, manifest_bytes: bytes) -> str:
    plugin = tmp_path / "plugin"
    (plugin / "hooks").mkdir(parents=True)
    (plugin / "contract").mkdir()
    (plugin / "hooks" / "session-start").write_bytes(HOOK.read_bytes())
    (plugin / "contract" / "manifest.yaml").write_bytes(manifest_bytes)
    repo = tmp_path / "repo"
    repo.mkdir()
    proc = subprocess.run(
        ["bash", str(plugin / "hooks" / "session-start")],
        cwd=str(repo), stdin=subprocess.DEVNULL, capture_output=True,
    )
    assert proc.returncode == 0, proc.stderr
    return _context(proc.stdout)


HOSTILE_MANIFESTS = {
    "slash_and_ampersand_in_name": (
        b"version: 1.0.0\n"
        b"stations:\n"
        b"  - {name: alpha/beta, owner: x, produces: y, decision_point: 1}\n"
        b"  - {name: gamma&delta, owner: x, produces: y, decision_point: 1}\n"
        b"  - {name: maintain, owner: x, produces: y}\n"
    ),
    "decision_point_shared_by_three_stations": (
        b"version: 1.0.0\n"
        b"stations:\n"
        b"  - {name: one, owner: x, produces: y, decision_point: 2}\n"
        b"  - {name: two, owner: x, produces: y, decision_point: 2}\n"
        b"  - {name: three, owner: x, produces: y, decision_point: 2}\n"
        b"  - {name: maintain, owner: x, produces: y}\n"
    ),
    "stations_block_ends_at_eof_no_trailing_key": (
        b"version: 1.0.0\n"
        b"stations:\n"
        b"  - {name: solo, owner: x, produces: y, decision_point: 1}\n"
        b"  - {name: maintain, owner: x, produces: y}\n"
    ),
    "crlf_line_endings": (
        b"version: 1.0.0\r\n"
        b"stations:\r\n"
        b"  - {name: solo, owner: x, produces: y, decision_point: 1}\r\n"
        b"  - {name: maintain, owner: x, produces: y}\r\n"
        b"artifacts:\r\n"
        b"  foo: bar\r\n"
    ),
}


@pytest.mark.parametrize("fixture_name", sorted(HOSTILE_MANIFESTS))
def test_session_start_hostile_manifest_matches_python_oracle(tmp_path, fixture_name):
    """For every hostile manifest shape (path-hazard chars in a name field,
    one decision_point shared by 3 stations, a stations: block that runs to
    EOF with no following top-level key, CRLF line endings) the hook's
    derived station-order and decision-point text must match a pure-Python
    re-implementation of today's awk+sed pipeline byte-for-byte — this is
    the differential oracle the awk-consolidation rewrite must preserve."""
    manifest_bytes = HOSTILE_MANIFESTS[fixture_name]
    context = _run_against_manifest(tmp_path, manifest_bytes)

    text = manifest_bytes.decode("utf-8")
    block = _oracle_stations_block(text)
    names = _oracle_station_names(block)
    flow = " → ".join(n for n in names if n != "maintain")
    tail = "maintain" if "maintain" in names else ""
    expected_order = f"Station order: {flow}; {tail} on alerts."
    assert expected_order in context, (expected_order, context[:200])

    for n in (1, 2, 3):
        expected_dp = _oracle_stations_for_dp(block, n)
        # dp lines are only asserted when non-empty (an empty dp renders as
        # "()" in the body, which is the same across old and new).
        if expected_dp:
            assert expected_dp in context, (n, expected_dp, context[:400])


# --- probe 5: missing manifest (failing dependency) -------------------------

def test_session_start_missing_manifest_emits_empty_context_and_exits_zero(tmp_path):
    """A plugin tree with hooks/ but no contract/manifest.yaml must fail
    open: exit 0 and emit the fixed empty-context JSON envelope, byte for
    byte, never crash the session."""
    plugin = tmp_path / "plugin"
    (plugin / "hooks").mkdir(parents=True)
    (plugin / "contract").mkdir()
    (plugin / "hooks" / "session-start").write_bytes(HOOK.read_bytes())
    repo = tmp_path / "repo"
    repo.mkdir()
    proc = subprocess.run(
        ["bash", str(plugin / "hooks" / "session-start")],
        cwd=str(repo), stdin=subprocess.DEVNULL, capture_output=True,
    )
    assert proc.returncode == 0
    assert proc.stdout == (
        b'{"hookSpecificOutput":{"hookEventName":"SessionStart",'
        b'"additionalContext":""},"additional_context":"","additionalContext":""}\n'
    )
