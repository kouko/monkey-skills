"""Branch-end adversary probes for
2026-09-04-codex-hook-trust-covers-every-definition-and-worktree — attacking
the already-landed `codex_scaffold.py` (per-definition trust ledger) against
the dispatch's five named concerns: real-repo ledger pollution, ledger
forgery, cwd bypass of the thin shims, replay/stale ledger state, and
concurrent writers.

Every case below runs against scratch repos under ``tmp_path``. None of them
ever fires a shim with cwd set to THIS repo — the class of bug this file's
first probe exists to document was found by watching
``test_abuse_hook_trust.py``'s own ``test_codex_and_claude_*_agree*`` cases
do exactly that (see the finding in the dispatching agent's report; verified
live, ledger deleted afterward, not re-reproduced here on purpose).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from pathlib import Path

import pytest

# evidence/probes/test_abuse_hook_trust_branch_end.py -> parents[5] is the
# repo root (probes -> evidence -> <change-id> -> loom -> docs -> root).
REPO = Path(__file__).resolve().parents[5]
SCAFFOLD = REPO / "loom-code" / "scripts" / "codex_scaffold.py"

sys.path.insert(0, str((REPO / "loom-code" / "scripts")))
import codex_scaffold as cs  # noqa: E402

SHIM_COMMAND = ".codex/hooks/loom-checker"
MARKER_REL = Path(".codex/hooks/.loom-hook-fired")


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCAFFOLD), *args],
        capture_output=True,
        text=True,
        timeout=60,
    )


def git_repo(repo: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    for key, value in (("user.email", "t@example.com"), ("user.name", "T")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "seed.txt"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "seed"], check=True)


def scaffold(repo: Path) -> subprocess.CompletedProcess:
    return run("--repo", str(repo))


def pre_tool_use_bash_payload(repo: Path) -> dict:
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "git push origin HEAD"},
        "cwd": str(repo),
        "permission_mode": "default",
    }


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    target = tmp_path / "adopting-repo"
    target.mkdir()
    git_repo(target)
    scaffold(target)
    return target


# --- (1) cwd bypass: a shim invoked from a non-root cwd crashes silently,
# but the ledger still records "fired" -- --trusted then lies "safe" ---


def test_shim_invoked_from_subdirectory_crashes_but_still_records_fired(repo):
    """Fixed (branch-end-02) -- was a real hole, scratch-repo reproduction
    only (never fires against REPO).

    Both thin shims (``exec .claude/hooks/<name>`` and
    ``exec python3 .codex/hooks/loom_checker.py ...``) used to resolve
    their target relative to the PROCESS cwd, not to ``$0``'s own
    directory or the payload's ``cwd`` field. plan.md `## Risks` #4 already
    named "cwd assumption == repo root; if Codex changes cwd, both break"
    as a known risk invisible to the static self-test probe -- but it did
    not name this half: the recorder line was written BEFORE the ``exec``,
    so a crash from a non-root cwd still left a ``fired`` line in the
    ledger, and ``--trusted`` reported the definition ``fired`` (exit 0)
    forever after even though no real invocation from that cwd ever
    produced a ``BLOCK push.`` verdict. Both shims now resolve their
    target from their own location and record only once the target is
    known to exist -- a crashed/missing target is never credited as a
    firing.
    """
    subdir = repo / "sub"
    subdir.mkdir()
    shim = repo / SHIM_COMMAND
    proc = subprocess.run(
        [str(shim)],
        cwd=str(subdir),
        input=json.dumps(pre_tool_use_bash_payload(repo)),
        capture_output=True,
        text=True,
        timeout=30,
    )
    crashed_not_blocked = proc.returncode != 0 and not proc.stderr.lstrip().startswith(
        "BLOCK push."
    )
    ledger = repo / MARKER_REL
    reported_fired = False
    if ledger.is_file():
        trusted_proc = run("--repo", str(repo), "--trusted")
        reported_fired = (
            f"PreToolUse Bash {SHIM_COMMAND}: fired" in trusted_proc.stdout + trusted_proc.stderr
        )

    assert not (crashed_not_blocked and reported_fired), (
        "cwd != repo root: shim crashed without a BLOCK verdict, yet "
        "--trusted reports this definition fired -- a false 'safe to "
        "continue' signal"
    )


# --- (2) forged/malformed ledger lines never grant false trust ---


@pytest.mark.parametrize(
    "line,label",
    [
        (b"PreToolUse\t.codex/hooks/does-not-exist\tBash\n", "unknown-definition"),
        (b"PreToolUse\t/abs/path/loom-checker\tBash\n", "absolute-path-command"),
        (b"PreToolUse\t.codex/hooks/loom-checker \tBash\n", "trailing-space-command"),
        (b"PreToolUse\t.codex/hooks/loom-checker\n", "too-few-fields"),
        (b"PreToolUse\t.codex/hooks/loom-checker\tBash\textra\n", "too-many-fields"),
        (b"garbage no tabs at all\n", "no-tabs"),
    ],
    ids=lambda v: v if isinstance(v, str) else None,
)
def test_forged_or_malformed_ledger_line_grants_no_false_trust(repo, line, label):
    """A hostile or corrupted ledger line must never crash ``--trusted``
    and must never cause a real definition to read ``fired`` unless the
    line's ``(event, command)`` matches it byte-for-byte. The
    trailing-space variant exercises a NEAR-miss on the real key and must
    still fail to credit it (fail-closed, not fail-open)."""
    marker = repo / MARKER_REL
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_bytes(line)

    proc = run("--repo", str(repo), "--trusted")
    combined = proc.stdout + proc.stderr
    assert "Traceback" not in combined, f"{label}: ledger line crashed --trusted"
    assert proc.returncode != 0, (
        f"{label}: the real loom-checker definition has no genuine "
        f"evidence and must still report not-trusted"
    )
    assert f"PreToolUse Bash {SHIM_COMMAND}: fired" not in combined.replace(
        "fired (legacy)", "LEGACY_EXCLUDED"
    ), f"{label}: forged/malformed line must not read as a real firing"


def test_crlf_line_ending_on_an_otherwise_genuine_line_still_credits_fired(repo):
    """Held, not a hole: a ledger line terminated ``\\r\\n`` (e.g. a
    Windows-checked-out repo) still carries genuinely correct content --
    ``str.splitlines()`` treats CRLF as one line break and strips it
    cleanly, so the command field parses identically to the LF case. This
    must keep crediting ``fired``; it is not a forgery."""
    marker = repo / MARKER_REL
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_bytes(b"PreToolUse\t.codex/hooks/loom-checker\tBash\r\n")
    proc = run("--repo", str(repo), "--trusted")
    assert proc.returncode == 0
    assert f"PreToolUse Bash {SHIM_COMMAND}: fired" in proc.stdout + proc.stderr


# --- (3) hooks.json with an unknown event key or a command-less entry
# does not crash --trusted, and the command-less entry contributes no
# phantom definition ---


def test_unknown_event_key_and_commandless_entry_do_not_crash_trusted(repo):
    hooks_json_path = repo / ".codex" / "hooks.json"
    config = json.loads(hooks_json_path.read_text(encoding="utf-8"))
    config["hooks"]["SomeFutureCodexEvent"] = [
        {"matcher": "*", "hooks": [{"type": "command", "command": "some-future-hook"}]}
    ]
    config["hooks"]["PostToolUse"] = [
        {"matcher": "Write", "hooks": [{"type": "command"}]}  # no "command" key at all
    ]
    hooks_json_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    proc = run("--repo", str(repo), "--trusted")
    combined = proc.stdout + proc.stderr
    assert "Traceback" not in combined
    # the unknown-event definition is still listed as its own row (never)
    assert "SomeFutureCodexEvent * some-future-hook: never" in combined
    # the command-less entry must not manufacture a definition with an
    # empty/None command string
    assert "PostToolUse Write None" not in combined
    assert "PostToolUse Write : " not in combined


# --- (4) concurrent recorder appends never interleave into a corrupt line ---


def test_concurrent_recorder_appends_do_not_corrupt_the_ledger(repo):
    recorder = repo / ".codex" / "hooks" / "loom_record_fire.py"
    payload = json.dumps(
        {"hook_event_name": "PostToolUse", "tool_name": "Write", "tool_input": {}, "cwd": str(repo)}
    )

    def fire_one(i: int) -> None:
        subprocess.run(
            [sys.executable, str(recorder), f".codex/hooks/concurrent-cmd-{i}.sh"],
            input=payload,
            capture_output=True,
            text=True,
            cwd=str(repo),
            timeout=30,
        )

    threads = [threading.Thread(target=fire_one, args=(i,)) for i in range(24)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    ledger = repo / MARKER_REL
    lines = [line for line in ledger.read_text(encoding="utf-8").splitlines() if line]
    assert len(lines) == 24, f"expected 24 lines, got {len(lines)}"
    malformed = [line for line in lines if len(line.split("\t")) != 3]
    assert not malformed, f"interleaved/corrupted lines: {malformed}"


# --- (5) LOOM_SELF_TEST set permanently in the caller's own environment
# (not just by --self-test) silently blinds every real firing too -- the
# safe direction (never grants false trust), but worth recording honestly ---


def test_loom_self_test_env_set_by_caller_blinds_real_firings_too(repo):
    """If a user's shell profile happens to export ``LOOM_SELF_TEST=1``
    (typo'd, copy-pasted from a debugging session, or inherited from a CI
    wrapper), a REAL Codex-driven firing would also skip the ledger write
    -- because the recorder can't distinguish "the scaffold's own
    --self-test spawned me" from "the caller's ambient environment already
    had this set". This is the safe direction (under-reports trust, never
    over-reports it) so it is not a finding, but it is worth pinning as a
    guard: it must never flip to granting trust it shouldn't."""
    shim = repo / SHIM_COMMAND
    proc = subprocess.run(
        [str(shim)],
        cwd=str(repo),
        input=json.dumps(pre_tool_use_bash_payload(repo)),
        capture_output=True,
        text=True,
        env=dict(os.environ, LOOM_SELF_TEST="1"),
        timeout=30,
    )
    assert proc.returncode != 0  # checker still blocks the fake push
    ledger = repo / MARKER_REL
    assert not ledger.is_file() or ledger.read_bytes() == b"", (
        "a real firing must not be silently blinded into looking like it "
        "never happened just because LOOM_SELF_TEST leaked into the "
        "caller's ambient environment"
    )
