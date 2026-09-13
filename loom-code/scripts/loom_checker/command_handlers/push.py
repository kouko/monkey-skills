from __future__ import annotations

from loom_checker.attestation import validate_attestation
from loom_checker.helpers import UsageError
from loom_checker.helpers import changed_paths
from loom_checker.helpers import git_maybe
from loom_checker.helpers import git_text
from loom_checker.helpers import glob_to_regex
from loom_checker.helpers import load_manifest
from loom_checker.helpers import repo_root
from loom_checker.helpers import report
from loom_checker.rule_checks.push import canonical_git_push
from loom_checker.rule_checks.push import canonical_pr_create_repo
from loom_checker.rule_checks.push import check_pr_create_remote_head
from loom_checker.rule_checks.push import git_dash_c_push_cwd
from loom_checker.rule_checks.push import is_git_push_command
from loom_checker.rule_checks.push import is_pr_create_command
from loom_checker.rule_checks.push import is_push_command
from loom_checker.rule_checks.push import quote_all_shell_token
from pathlib import Path
import json
import os
import re
import shutil
import sys


def read_hook_payload(stdin=sys.stdin) -> dict | None:
    """PreToolUse payload (Claude Code and Codex share the shape) when the
    checker is invoked as a hook; None when run from a terminal or with an
    empty stdin. Malformed JSON is a UsageError → exit 2 (fail-closed)."""
    if stdin is None or stdin.isatty():
        return None
    raw = stdin.read()
    if not raw.strip():
        return None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise UsageError(f"hook payload is not JSON: {exc}")
    if not isinstance(payload, dict):
        raise UsageError("hook payload must be a JSON object.")
    return payload


def cmd_push(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    """`--hook` is what selects hook mode, never the shape of stdin: a
    checker run from a station (or a terminal, or any harness that hands it
    a pipe nobody ever closes) must never block on `stdin.read()`."""
    rest = list(args)
    if "--hook" not in rest:
        return _cmd_push(rest, out, err)
    rest.remove("--hook")

    payload = read_hook_payload()
    if payload is None:
        raise UsageError("push --hook expects a PreToolUse JSON payload on stdin.")
    # The matcher is the tool name, so every Bash command arrives here; only
    # push-shaped commands are judged.
    command = str((payload.get("tool_input") or {}).get("command", ""))
    canonical_pr_repo = canonical_pr_create_repo(command)
    push_shaped = canonical_pr_repo is not None or is_push_command(command)
    git_push = is_git_push_command(command)
    malformed_canonical_push = False
    if not push_shaped:
        # A malformed quote can defeat the permissive recogniser, but not a
        # command that visibly starts with the canonical command trust root
        # and trusted executable.
        trusted = shutil.which("git")
        trusted_prefix = (
            f"{quote_all_shell_token('command')} "
            f"{quote_all_shell_token(str(Path(trusted).resolve()))}"
            if trusted
            else ""
        )
        malformed_canonical_push = bool(
            trusted_prefix
            and command.startswith(trusted_prefix)
            and quote_all_shell_token("push") in command
        )
        if not malformed_canonical_push:
            return 0
    cwd = str(payload.get("cwd") or os.getcwd())
    if git_push or malformed_canonical_push:
        repo, immutable_head, refspec_error = canonical_git_push(command, cwd)
        if refspec_error:
            print(f"BLOCK push.attestation: {refspec_error}", file=err)
            return 2
        assert repo is not None and immutable_head is not None
        os.chdir(repo)
        rc = _cmd_push(["--head", immutable_head, "--require-live-head"] + rest, out, err)
        return 2 if rc == 1 else rc

    # A metadata-only PR create carries its own function-proof repository
    # selection. Other gh actions keep the existing conservative parser.
    pr_create = canonical_pr_repo is not None or is_pr_create_command(command)
    if pr_create and canonical_pr_repo is None:
        print(
            "BLOCK push.attestation: PR creation must use the canonical "
            "trusted-gh command from loom-code:ship",
            file=err,
        )
        return 2
    push_cwd = str(canonical_pr_repo) if canonical_pr_repo else git_dash_c_push_cwd(command, cwd)
    if push_cwd is None:
        print(
            "BLOCK push.attestation: ambiguous repository selection; "
            "use one absolute git -C path, or cd to one absolute path first",
            file=err,
        )
        return 2
    os.chdir(push_cwd)
    if pr_create:
        remote_error = check_pr_create_remote_head(Path.cwd(), command)
        if remote_error:
            print(f"BLOCK push.attestation: {remote_error}", file=err)
            return 2
    rc = _cmd_push(rest, out, err)
    if pr_create and rc == 0:
        remote_error = check_pr_create_remote_head(Path.cwd(), command)
        if remote_error:
            print(f"BLOCK push.attestation: {remote_error}", file=err)
            return 2
    return 2 if rc == 1 else rc


def _cmd_push(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    head = "HEAD"
    require_live_head = False
    rest = list(args)
    while rest:
        token = rest.pop(0)
        if token == "--head":
            if not rest:
                raise UsageError("--head needs a ref.")
            head = rest.pop(0)
        elif token == "--require-live-head":
            require_live_head = True
        else:
            raise UsageError(f"unexpected argument {token!r}.")

    manifest = load_manifest()
    repo = repo_root(Path.cwd())
    head_sha = git_maybe(repo, "rev-parse", head)
    if not head_sha:
        raise UsageError(f"cannot resolve {head!r} in {repo}.")

    # The 1.1 publication path reads one generated attestation from the
    # branch delta. It validates content identity and recorded outcomes but
    # deliberately does not replay functional executables.
    attestation_template = manifest.get("artifacts", {}).get("attestation", {}).get("path")
    if not attestation_template:
        raise UsageError("contract manifest declares no attestation artifact.")
    matcher = glob_to_regex(attestation_template.replace("<change-id>", "*"))
    candidates = sorted(path for path in changed_paths(repo) if matcher.fullmatch(path))
    if len(candidates) != 1:
        return report([(
            "push.attestation",
            f"branch must carry exactly one generated attestation; found {len(candidates)}",
        )], err)
    attestation_rel = candidates[0]
    match = re.fullmatch(
        re.escape(attestation_template).replace(re.escape("<change-id>"), r"(?P<change_id>[^/]+)"),
        attestation_rel,
    )
    if match is None:
        return report([("push.attestation", "cannot derive change id from attestation path")], err)
    try:
        attestation = json.loads(git_text(repo, "show", f"{head_sha}:{attestation_rel}"))
    except (UsageError, json.JSONDecodeError) as exc:
        return report([("push.attestation", f"cannot read generated attestation: {exc}")], err)
    failures = validate_attestation(
        repo, head_sha, match.group("change_id"), attestation, manifest
    )
    if require_live_head and git_text(repo, "rev-parse", "HEAD") != head_sha:
        failures.append(("push.attestation", "live HEAD moved during publication validation"))
    return report(failures, err)
