"""Tests for loom-code/hooks/git-guard.py — the PreToolUse git gate.

Each test subprocess-runs the hook exactly as Claude Code would invoke
it: hook-event JSON on stdin, exit code as the verdict (0 = allow,
2 = block, stderr shown to the model). Marker checks are exercised
against real throwaway git repos (tmp_path + ``git init`` + an empty
commit) so head_sha freshness compares against an actual HEAD, not a
mocked string.

Env isolation is done by constructing the subprocess env explicitly
per call (see ``_iso_env``: LOOM_CODE_MODE / GIT_DIR / GIT_WORK_TREE
stripped, GIT_CONFIG_GLOBAL / GIT_CONFIG_SYSTEM emptied so the user's
gpgsign / hooksPath cannot leak in) rather than monkeypatching
os.environ — the hook runs in a child process, so only the env dict
handed to subprocess.run matters.

External surfaces grounded (per
loom-code/skills/subagent-driven-development/standards/external-surface-grounding.md):

- git plumbing (``git rev-parse --git-dir``, ``git rev-parse HEAD``,
  ``git -C <path>``, ``git commit --allow-empty``): source-(a) live
  verification — this suite builds real throwaway repos and every
  marker-freshness assertion drives those exact invocations against
  them (via the hook subprocess and the fixtures below), so a flag
  drift fails the suite instead of slipping past it.
- Claude Code PreToolUse hook contract (``tool_name`` /
  ``tool_input.command`` / ``cwd`` as JSON on stdin; exit 0 = allow,
  exit 2 = block with stderr shown to the model): source-(d) in-repo
  evidence — the identical event schema is consumed by this repo's own
  hook scripts under ``.claude/hooks/`` (PostToolUse,
  ``validate-skill-folder-structure.sh`` reads ``tool_input.*`` from
  stdin and uses the same 0/2 exit semantics), and the guard is
  registered as a PreToolUse hook in ``loom-code/hooks/hooks.json``.
  This suite additionally live-drives the hook via subprocess with
  exactly that stdin/exit contract.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "git-guard.py"


def _iso_env(extra=None):
    """Isolated env: no user git config / git env vars / loom mode leak."""
    env = os.environ.copy()
    env.pop("LOOM_CODE_MODE", None)
    env.pop("GIT_DIR", None)
    env.pop("GIT_WORK_TREE", None)
    env["GIT_CONFIG_GLOBAL"] = ""   # skip ~/.gitconfig (gpgsign, hooksPath…)
    env["GIT_CONFIG_SYSTEM"] = ""   # skip /etc/gitconfig
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if extra:
        env.update(extra)
    return env


def run_hook(payload, env_extra=None):
    """Run the hook with `payload` (dict → JSON, str → raw) on stdin."""
    env = _iso_env(env_extra)
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=stdin,
        capture_output=True,
        text=True,
        env=env,
    )


def bash_event(command, cwd=None):
    event = {"tool_name": "Bash", "tool_input": {"command": command}}
    if cwd is not None:
        event["cwd"] = str(cwd)
    return event


@pytest.fixture
def repo(tmp_path):
    """A real git repo with one commit (so HEAD resolves)."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True,
                   env=_iso_env())
    subprocess.run(
        [
            "git", "-c", "user.email=t@t", "-c", "user.name=t",
            "commit", "--allow-empty", "-m", "init", "-q",
        ],
        cwd=tmp_path,
        check=True,
        env=_iso_env(),
    )
    return tmp_path


def head_sha(repo_path):
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_path, capture_output=True, text=True, check=True,
        env=_iso_env(),
    ).stdout.strip()


def loom_dir(repo_path):
    d = repo_path / ".git" / "loom"
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_review_pass(repo_path, sha=None, verdict="PASS"):
    (loom_dir(repo_path) / "review-pass.json").write_text(json.dumps({
        "schema": 1,
        "branch": "feat/x",
        "head_sha": sha or head_sha(repo_path),
        "verdict": verdict,
        "written_at": "2026-07-04T00:00:00+08:00",
    }))


def write_verified(repo_path, sha=None):
    (loom_dir(repo_path) / "verified.json").write_text(json.dumps({
        "schema": 1,
        "head_sha": sha or head_sha(repo_path),
        "suite_line": "42 passed in 1.00s",
        "written_at": "2026-07-04T00:00:00+08:00",
    }))


def write_waiver(repo_path, reason="user waived"):
    (loom_dir(repo_path) / "waiver.json").write_text(json.dumps({
        "schema": 1,
        "scope": "push",
        "reason": reason,
        "written_at": "2026-07-04T00:00:00+08:00",
    }))


def commit_again(repo_path):
    subprocess.run(
        [
            "git", "-c", "user.email=t@t", "-c", "user.name=t",
            "commit", "--allow-empty", "-m", "again", "-q",
        ],
        cwd=repo_path,
        check=True,
        env=_iso_env(),
    )


# --- matrix row 1: non-Bash tools pass through ---------------------------


def test_non_bash_tool_allowed(repo):
    res = run_hook({"tool_name": "Read",
                    "tool_input": {"file_path": "/x"},
                    "cwd": str(repo)})
    assert res.returncode == 0


# --- matrix row 2: LOOM_CODE_MODE=off bypasses everything ----------------


def test_mode_off_bypasses_push_gate(repo):
    res = run_hook(bash_event("git push", cwd=repo),
                   env_extra={"LOOM_CODE_MODE": "off"})
    assert res.returncode == 0


def test_mode_off_bypasses_no_verify_block(repo):
    res = run_hook(bash_event("git commit --no-verify -m x", cwd=repo),
                   env_extra={"LOOM_CODE_MODE": "off"})
    assert res.returncode == 0


# --- matrix row 3: git commit --no-verify / -n ----------------------------


def test_commit_no_verify_blocked(repo):
    res = run_hook(bash_event("git commit --no-verify -m x", cwd=repo))
    assert res.returncode == 2
    assert "load-bearing" in res.stderr


def test_commit_short_n_blocked(repo):
    res = run_hook(bash_event("git commit -n -m x", cwd=repo))
    assert res.returncode == 2


def test_commit_bundled_short_n_blocked(repo):
    # -n hidden inside a bundled short-option cluster still bypasses hooks.
    res = run_hook(bash_event("git commit -anm x", cwd=repo))
    assert res.returncode == 2


def test_plain_commit_allowed(repo):
    res = run_hook(bash_event("git commit -m x", cwd=repo))
    assert res.returncode == 0


def test_commit_am_cluster_allowed(repo):
    # False-positive pin: -am bundles a+m with no n — must NOT be read
    # as --no-verify (guards the fullmatch cluster regex against a
    # future substring-matching regression).
    res = run_hook(bash_event("git commit -am x", cwd=repo))
    assert res.returncode == 0


def test_commit_amend_allowed(repo):
    # False-positive pin: --amend contains the letter n but is a long
    # option, not a short cluster.
    res = run_hook(bash_event("git commit --amend -m x", cwd=repo))
    assert res.returncode == 0


def test_n_outside_commit_not_blocked(repo):
    # -n only counts for the commit subcommand; git clean -n is a dry-run.
    res = run_hook(bash_event("git clean -n", cwd=repo))
    assert res.returncode == 0


# --- matrix row 4a: push outside any repo is allowed ----------------------


def test_push_outside_repo_allowed(tmp_path):
    res = run_hook(bash_event("git push", cwd=tmp_path))
    assert res.returncode == 0


# --- matrix row 4b: waiver is honored exactly once -------------------------


def test_waiver_one_shot(repo):
    write_waiver(repo, reason="demo waiver")
    first = run_hook(bash_event("git push", cwd=repo))
    assert first.returncode == 0
    assert "waiver consumed" in first.stderr
    assert "demo waiver" in first.stderr
    assert not (repo / ".git" / "loom" / "waiver.json").exists()

    second = run_hook(bash_event("git push", cwd=repo))
    assert second.returncode == 2


@pytest.mark.skipif(os.geteuid() == 0,
                    reason="root unlinks regardless of dir perms (CI containers)")
def test_waiver_undeletable_fails_closed(repo):
    # Read-only loom dir: the waiver cannot be unlinked, so honoring it
    # would be a permanent silent bypass. The guard must say so loudly
    # and fall through to the (absent) marker gates instead.
    write_waiver(repo, reason="stuck waiver")
    loom = repo / ".git" / "loom"
    loom.chmod(0o555)
    try:
        res = run_hook(bash_event("git push", cwd=repo))
    finally:
        loom.chmod(0o755)  # restore so tmp_path cleanup succeeds
    assert res.returncode == 2
    assert "could NOT be deleted" in res.stderr
    assert (loom / "waiver.json").exists()  # not consumed


# --- matrix row 4c: review-pass marker -------------------------------------


def test_push_blocked_without_review_marker(repo):
    res = run_hook(bash_event("git push", cwd=repo))
    assert res.returncode == 2
    assert "requesting-code-review" in res.stderr


def test_push_blocked_stale_review_sha(repo):
    write_review_pass(repo)
    write_verified(repo)
    commit_again(repo)  # markers now point at the previous HEAD
    res = run_hook(bash_event("git push", cwd=repo))
    assert res.returncode == 2


def test_push_blocked_bad_verdict(repo):
    write_review_pass(repo, verdict="NEEDS_REVISION")
    write_verified(repo)
    res = run_hook(bash_event("git push", cwd=repo))
    assert res.returncode == 2


def test_push_blocked_unparseable_review(repo):
    (loom_dir(repo) / "review-pass.json").write_text("{not json")
    write_verified(repo)
    res = run_hook(bash_event("git push", cwd=repo))
    assert res.returncode == 2


# --- matrix row 4d: verified marker -----------------------------------------


def test_push_blocked_without_verified_marker(repo):
    write_review_pass(repo)
    res = run_hook(bash_event("git push", cwd=repo))
    assert res.returncode == 2
    # Discriminating: "verification marker" appears only in MSG_VERIFIED,
    # so a review-gate misfire cannot fake this pass.
    assert "verification marker" in res.stderr
    assert "requesting-code-review" not in res.stderr


def test_push_blocked_stale_verified_sha(repo):
    write_review_pass(repo)
    write_verified(repo, sha="0" * 40)
    res = run_hook(bash_event("git push", cwd=repo))
    assert res.returncode == 2


# --- matrix row 4e: fresh markers allow the push ----------------------------


def test_push_allowed_with_fresh_markers(repo):
    write_review_pass(repo, verdict="PASS_WITH_NOTES")
    write_verified(repo)
    res = run_hook(bash_event("git push origin feat/x", cwd=repo))
    assert res.returncode == 0


# --- push-family variants ----------------------------------------------------


def test_gh_pr_create_blocked_without_markers(repo):
    res = run_hook(bash_event("gh pr create --title x --body y", cwd=repo))
    assert res.returncode == 2


def test_gh_pr_merge_blocked_without_markers(repo):
    res = run_hook(bash_event("gh pr merge 123", cwd=repo))
    assert res.returncode == 2


def test_push_dry_run_allowed(repo):
    res = run_hook(bash_event("git push --dry-run", cwd=repo))
    assert res.returncode == 0


def test_push_short_n_dry_run_allowed(repo):
    # git push -n IS git's dry-run short form — non-destructive, allowed.
    res = run_hook(bash_event("git push -n", cwd=repo))
    assert res.returncode == 0


def test_git_dash_c_push_resolves_c_path_repo(repo, tmp_path_factory):
    # cwd is NOT a repo; only -C points into one. If the hook resolved
    # cwd instead of -C, this would fall through row 4a and wrongly allow.
    elsewhere = tmp_path_factory.mktemp("not-a-repo")
    res = run_hook(bash_event(f"git -C {repo} push", cwd=elsewhere))
    assert res.returncode == 2


def test_compound_command_segment_detected(repo):
    res = run_hook(bash_event("echo hi && git push", cwd=repo))
    assert res.returncode == 2


def test_multiline_command_segment_detected(repo):
    # Multiline Bash commands are routine in Claude Code; a push on
    # line 2 must not hide behind line 1's leading word.
    res = run_hook(bash_event("echo hi\ngit push", cwd=repo))
    assert res.returncode == 2


def test_single_ampersand_background_segment_detected(repo):
    res = run_hook(bash_event("sleep 1 & git push", cwd=repo))
    assert res.returncode == 2


def test_quoted_git_push_in_echo_not_matched(repo):
    res = run_hook(bash_event('echo "git push"', cwd=repo))
    assert res.returncode == 0


def test_cwd_absent_falls_back_to_process_cwd(repo):
    # No "cwd" key in the event: hook must use its own working dir.
    res = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps({"tool_name": "Bash",
                          "tool_input": {"command": "git push"}}),
        capture_output=True, text=True, env=_iso_env(), cwd=repo,
    )
    assert res.returncode == 2


# --- matrix row 5 + fail-open ------------------------------------------------


def test_unrelated_command_allowed(repo):
    res = run_hook(bash_event("ls -la", cwd=repo))
    assert res.returncode == 0


def test_malformed_stdin_fail_open():
    res = run_hook("this is not json {")
    assert res.returncode == 0
    assert res.stderr.strip()  # fail-open must still leave a note
