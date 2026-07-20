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
MARKERS_CLI = Path(__file__).resolve().parent / "loom_gate_markers.py"


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


def write_review_pass(repo_path, sha=None, verdict="PASS", schema=1):
    (loom_dir(repo_path) / "review-pass.json").write_text(json.dumps({
        "schema": schema,
        "branch": "feat/x",
        "head_sha": sha or head_sha(repo_path),
        "verdict": verdict,
        "written_at": "2026-07-04T00:00:00+08:00",
    }))


def write_verified(repo_path, sha=None, schema=1):
    (loom_dir(repo_path) / "verified.json").write_text(json.dumps({
        "schema": schema,
        "head_sha": sha or head_sha(repo_path),
        "run_cmd": "true",
        "exit_code": 0,
        "output_tail": "",
        "written_at": "2026-07-04T00:00:00+08:00",
    }))


def write_waiver(repo_path, reason="user waived", schema=1):
    (loom_dir(repo_path) / "waiver.json").write_text(json.dumps({
        "schema": schema,
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


def _git_ok(args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, env=_iso_env())


@pytest.fixture
def feature_repo(repo):
    """`repo` plus a feature branch carrying one content commit, for
    patch-id fallback scenarios (message-only amend / content change /
    rebase onto an advanced default branch)."""
    default_branch = subprocess.run(
        ["git", "branch", "--show-current"], cwd=repo,
        capture_output=True, text=True, env=_iso_env(), check=True,
    ).stdout.strip()
    _git_ok(["checkout", "-q", "-b", "feature/x"], repo)
    (repo / "f.txt").write_text("hello\n")
    _git_ok(["add", "f.txt"], repo)
    _git_ok(["-c", "user.email=t@t", "-c", "user.name=t",
             "commit", "-m", "add f.txt", "-q"], repo)
    return repo, default_branch


def _mint_markers(repo, tmp_path):
    """Mint review-pass + verified markers via the real CLI (seam test:
    exercises the actual patch-id write path, not hand-crafted JSON)."""
    verdict_file = tmp_path / "verdict.txt"
    verdict_file.write_text(
        "standards_version: v1\n"
        "verdict: PASS\n"
        "dimension_scores:\n"
        "  security: green\n"
    )
    mint_review = subprocess.run(
        [sys.executable, str(MARKERS_CLI), "review-pass",
         "--repo", str(repo), "--verdict-file", str(verdict_file)],
        capture_output=True, text=True, env=_iso_env(),
    )
    assert mint_review.returncode == 0, mint_review.stderr
    mint_verified = subprocess.run(
        [sys.executable, str(MARKERS_CLI), "verified",
         "--repo", str(repo), "--run", "true"],
        capture_output=True, text=True, env=_iso_env(),
    )
    assert mint_verified.returncode == 0, mint_verified.stderr


# --- patch-id relaxation: message-only amend / content change / rebase ----


def test_push_allowed_after_message_only_amend_via_patch_id(feature_repo, tmp_path):
    repo, _default_branch = feature_repo
    _mint_markers(repo, tmp_path)

    _git_ok(["-c", "user.email=t@t", "-c", "user.name=t",
             "commit", "--amend", "-m", "add f.txt (reworded)", "-q"], repo)

    res = run_hook(bash_event("git push", cwd=repo))
    assert res.returncode == 0, res.stderr


def test_push_blocked_after_content_change_despite_patch_id_fields(
    feature_repo, tmp_path
):
    repo, _default_branch = feature_repo
    _mint_markers(repo, tmp_path)

    # Content change, not just message: recomputed patch-id must differ,
    # so the fallback must NOT accept this as a fresh-enough review.
    (repo / "f.txt").write_text("hello\nmore\n")
    _git_ok(["add", "f.txt"], repo)
    _git_ok(["-c", "user.email=t@t", "-c", "user.name=t",
             "commit", "--amend", "-m", "add f.txt", "-q"], repo)

    res = run_hook(bash_event("git push", cwd=repo))
    assert res.returncode == 2


def test_push_allowed_after_rebase_onto_advanced_default_branch(
    feature_repo, tmp_path
):
    repo, default_branch = feature_repo
    _mint_markers(repo, tmp_path)

    # Advance the default branch with an unrelated commit, then rebase
    # the feature branch onto it — head_sha changes, base_sha changes,
    # but the diff content (and thus patch-id) is unchanged.
    _git_ok(["checkout", "-q", default_branch], repo)
    (repo / "unrelated.txt").write_text("noise\n")
    _git_ok(["add", "unrelated.txt"], repo)
    _git_ok(["-c", "user.email=t@t", "-c", "user.name=t",
             "commit", "-m", "advance main", "-q"], repo)
    _git_ok(["checkout", "-q", "feature/x"], repo)
    # rebase rewrites commits → needs committer identity, same as commit;
    # CI runners have no global git config (exit 128 without this).
    _git_ok(["-c", "user.email=t@t", "-c", "user.name=t",
             "rebase", "-q", default_branch], repo)

    res = run_hook(bash_event("git push", cwd=repo))
    assert res.returncode == 0, res.stderr


def test_push_blocked_without_patch_id_fields_on_stale_sha(repo):
    # Old-format marker (no base_sha/patch_id, as written by a pre-patch-id
    # writer): backward compatibility — stale head_sha still blocks via
    # the strict-equality path only.
    write_review_pass(repo)
    write_verified(repo)
    commit_again(repo)
    res = run_hook(bash_event("git push", cwd=repo))
    assert res.returncode == 2


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


# --- schema field is validated on every marker -------------------------------


def test_push_blocked_wrong_schema_review(repo):
    write_review_pass(repo, schema=2)
    write_verified(repo)
    res = run_hook(bash_event("git push", cwd=repo))
    assert res.returncode == 2


def test_push_blocked_wrong_schema_verified(repo):
    write_review_pass(repo)
    write_verified(repo, schema=2)
    res = run_hook(bash_event("git push", cwd=repo))
    assert res.returncode == 2


def test_waiver_wrong_schema_ignored(repo):
    # Invalid waiver is IGNORED (not honored, not consumed): the marker
    # gates apply and the file stays for a human to inspect.
    write_waiver(repo, reason="bad schema waiver", schema=2)
    res = run_hook(bash_event("git push", cwd=repo))
    assert res.returncode == 2
    assert (repo / ".git" / "loom" / "waiver.json").exists()


# --- matrix row 4e: fresh markers allow the push ----------------------------


def test_push_allowed_with_fresh_markers(repo):
    write_review_pass(repo, verdict="PASS_WITH_NOTES")
    write_verified(repo)
    res = run_hook(bash_event("git push origin feat/x", cwd=repo))
    assert res.returncode == 0


def test_e2e_markers_cli_to_hook_allows_push(repo, tmp_path):
    # Seam test: markers minted by the REAL loom_gate_markers.py CLI
    # (not hand-written fixtures) must satisfy the hook — pins the two
    # sides of the frozen marker contract together so neither can
    # drift alone.
    verdict_file = tmp_path / "verdict.txt"
    verdict_file.write_text(
        "standards_version: v1\n"
        "verdict: PASS\n"
        "dimension_scores:\n"
        "  security: green\n"
    )
    mint_review = subprocess.run(
        [sys.executable, str(MARKERS_CLI), "review-pass",
         "--repo", str(repo), "--verdict-file", str(verdict_file)],
        capture_output=True, text=True, env=_iso_env(),
    )
    assert mint_review.returncode == 0, mint_review.stderr
    mint_verified = subprocess.run(
        [sys.executable, str(MARKERS_CLI), "verified",
         "--repo", str(repo), "--run", "true"],
        capture_output=True, text=True, env=_iso_env(),
    )
    assert mint_verified.returncode == 0, mint_verified.stderr

    res = run_hook(bash_event("git push", cwd=repo))
    assert res.returncode == 0, res.stderr


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


def test_git_dir_flag_push_blocked(repo, tmp_path_factory):
    # --git-dir takes a value: the value must not be mistaken for the
    # subcommand (which would let push slip through ungated), and the
    # gate must resolve the --git-dir repo even from a non-repo cwd.
    elsewhere = tmp_path_factory.mktemp("gd-not-a-repo")
    res = run_hook(
        bash_event(f"git --git-dir {repo}/.git push", cwd=elsewhere))
    assert res.returncode == 2


def test_git_dir_equals_form_push_blocked(repo, tmp_path_factory):
    elsewhere = tmp_path_factory.mktemp("gdeq-not-a-repo")
    res = run_hook(
        bash_event(f"git --git-dir={repo}/.git push", cwd=elsewhere))
    assert res.returncode == 2


def test_namespace_flag_push_blocked(repo):
    # --namespace takes a value (real git accepts this shape): the
    # value must not eat the subcommand and let push slip through.
    res = run_hook(bash_event("git --namespace foo push", cwd=repo))
    assert res.returncode == 2


def test_bogus_git_dir_push_allowed_fail_open(repo, tmp_path_factory):
    # Pin of ACTUAL behavior: a nonexistent --git-dir makes rev-parse
    # fail (exit 128), so the gate takes the not-a-repo path and
    # ALLOWS. Safe fail-open — the push itself fails identically
    # against the same bogus --git-dir, so nothing reaches a remote.
    elsewhere = tmp_path_factory.mktemp("bogus-gd-cwd")
    res = run_hook(bash_event(
        "git --git-dir /nonexistent/nowhere/.git push", cwd=elsewhere))
    assert res.returncode == 0


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


def test_heredoc_git_push_line_fail_closed(repo):
    # Accepted fail-closed limitation (documented in the hook's module
    # docstring): newline-splitting treats heredoc body lines as
    # segments, so a body line starting `git push` trips the gate even
    # though it is only data. Pinned so the behavior is explicit.
    cmd = "cat <<'EOF' > notes.txt\ngit push\nEOF"
    res = run_hook(bash_event(cmd, cwd=repo))
    assert res.returncode == 2


# --- wrapper bypass forms: push/merge behind known wrappers -----------------


def test_absolute_path_git_push_blocked(repo):
    # /usr/bin/git is git — an absolute-path invocation must not slip
    # past a matcher that only recognized a bare leading `git`.
    res = run_hook(bash_event("/usr/bin/git push", cwd=repo))
    assert res.returncode == 2


def test_env_wrapper_git_push_blocked(repo):
    res = run_hook(bash_event("env git push", cwd=repo))
    assert res.returncode == 2


def test_command_builtin_git_push_blocked(repo):
    res = run_hook(bash_event("command git push", cwd=repo))
    assert res.returncode == 2


def test_sh_c_git_push_blocked(repo):
    res = run_hook(bash_event('sh -c "git push"', cwd=repo))
    assert res.returncode == 2


def test_gh_api_pulls_merge_put_blocked(repo):
    # The REST equivalent of `gh pr merge`: PUT on a pulls .../merge
    # endpoint must be gated the same as the porcelain form.
    res = run_hook(bash_event(
        "gh api repos/o/r/pulls/5/merge -X PUT", cwd=repo))
    assert res.returncode == 2


def test_gh_api_merge_glued_short_method_blocked(repo):
    # gh (cobra/pflag) accepts the glued short-flag form `-XPUT` same as
    # spaced `-X PUT` — a real merge that must be gated identically.
    res = run_hook(bash_event(
        "gh api repos/o/r/pulls/5/merge -XPUT", cwd=repo))
    assert res.returncode == 2


# false-positive pins: legit non-push commands (behind the same wrappers)
# must stay allowed — see-through-known-wrappers, never block-on-suspicion.


def test_git_status_allowed(repo):
    res = run_hook(bash_event("git status", cwd=repo))
    assert res.returncode == 0


def test_git_log_allowed(repo):
    res = run_hook(bash_event("git log", cwd=repo))
    assert res.returncode == 0


def test_absolute_path_git_diff_allowed(repo):
    res = run_hook(bash_event("/usr/bin/git diff", cwd=repo))
    assert res.returncode == 0


def test_env_assignment_git_status_allowed(repo):
    res = run_hook(bash_event("env FOO=bar git status", cwd=repo))
    assert res.returncode == 0


def test_sh_c_ls_allowed(repo):
    res = run_hook(bash_event('sh -c "ls"', cwd=repo))
    assert res.returncode == 0


def test_gh_api_merge_get_allowed(repo):
    # A GET on the merge endpoint (merge-status check) is a read, not a
    # merge — no mutating method present, so it must NOT be blocked.
    res = run_hook(bash_event("gh api repos/o/r/pulls/5/merge", cwd=repo))
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


# --- cd-chain cwd tracking ---------------------------------------------


def test_cd_chain_absolute_path_gates_target_repo(repo, tmp_path_factory):
    # The ORIGINAL cwd is not a repo; the `cd` target is. The gate must
    # follow the cd, not stay pinned to the shell's starting cwd.
    elsewhere = tmp_path_factory.mktemp("cd-elsewhere")
    res = run_hook(bash_event(f"cd {repo} && git push", cwd=elsewhere))
    assert res.returncode == 2


def test_cd_chain_relative_path_gates_target_repo(repo):
    parent = repo.parent
    res = run_hook(bash_event(f"cd {repo.name} && git push", cwd=parent))
    assert res.returncode == 2


def test_cd_chain_tilde_path_gates_target_repo(repo, tmp_path_factory):
    elsewhere = tmp_path_factory.mktemp("cd-tilde-elsewhere")
    res = run_hook(bash_event("cd ~ && git push", cwd=elsewhere),
                   env_extra={"HOME": str(repo)})
    assert res.returncode == 2


def test_cd_chain_dynamic_path_keeps_previous_cwd(repo):
    # `cd $SOME_VAR` is dynamic/unresolvable — the guard must NOT trust
    # it blindly (which could silently escape to an unknown location);
    # it keeps the previous (known) cwd, so the push is still gated
    # against `repo` (fail-closed toward gating, not toward allowing).
    res = run_hook(bash_event("cd $SOME_VAR && git push", cwd=repo))
    assert res.returncode == 2


def test_cd_chain_nonexistent_absolute_target_keeps_previous_cwd(repo):
    # Real bash: `cd /nope` FAILS and cwd stays unchanged; with `;` the
    # push still runs — in the ORIGINAL repo. The guard must therefore
    # keep gating against the previous cwd, not adopt the fictitious
    # path (which resolves to "not a repo" → silent allow = gate bypass).
    res = run_hook(bash_event("cd /this/path/does/not/exist; git push", cwd=repo))
    assert res.returncode == 2


def test_cd_chain_nonexistent_relative_target_keeps_previous_cwd(repo):
    # Same bypass via a plain typo'd subdirectory name.
    res = run_hook(bash_event("cd nonexistent-typo-dir; git push", cwd=repo))
    assert res.returncode == 2


def test_cd_chain_file_target_keeps_previous_cwd(repo):
    # `cd` to an existing FILE also fails in real bash — same rule.
    target = repo / "somefile.txt"
    target.write_text("x")
    res = run_hook(bash_event("cd somefile.txt; git push", cwd=repo))
    assert res.returncode == 2


def test_cd_chain_applies_only_within_same_command_string(repo, tmp_path_factory):
    # A `cd` in one Bash invocation must not leak into a later, separate
    # invocation — each hook call gets a fresh effective cwd from the
    # event's own "cwd" field.
    elsewhere = tmp_path_factory.mktemp("cd-no-leak")
    first = run_hook(bash_event(f"cd {repo} && ls", cwd=elsewhere))
    assert first.returncode == 0
    second = run_hook(bash_event("git push", cwd=elsewhere))
    assert second.returncode == 0  # elsewhere is not a repo — still allowed


def test_unrelated_command_allowed(repo):
    res = run_hook(bash_event("ls -la", cwd=repo))
    assert res.returncode == 0


def test_malformed_stdin_fail_open():
    res = run_hook("this is not json {")
    assert res.returncode == 0
    assert res.stderr.strip()  # fail-open must still leave a note
