from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path
from urllib.parse import quote

import yaml

from git_exec import run_git

from ..attestation import validate_attestation
from ..helpers import UsageError, changed_paths, git_maybe, git_text, glob_to_regex, load_manifest, repo_root, report




SEGMENT_SPLIT = re.compile(r"\|\||&&|[;\n|&]")


ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


GIT_VALUE_OPTIONS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}


GH_VALUE_OPTIONS = {"-R", "--repo", "--hostname"}


GIT_REPOSITORY_ENV = {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GH_REPO"}


ENV_VALUE_OPTIONS = {"-u", "--unset", "-C", "--chdir", "-S", "--split-string"}


PREFIX_WORDS = {"sudo", "command", "env", "nohup", "time", "nice", "builtin", "exec", "xargs"}


SHELL_PROGRAMS = {"bash", "sh", "zsh", "dash"}


def _shell_segments(command: str) -> list[str]:
    """Split on shell operators outside quotes; malformed input stays strict."""
    segments: list[str] = []
    conservative_command = list(command)
    start = 0
    quote: str | None = None
    escaped = False
    dynamic = False
    index = 0
    while index < len(command):
        character = command[index]
        if escaped:
            escaped = False
        elif character == "\\" and quote != "'":
            escaped = True
        elif (
            character == "$"
            and quote != "'"
            and index + 1 < len(command)
            and command[index + 1] == "("
        ):
            dynamic = True
            conservative_command[index] = "\n"
            conservative_command[index + 1] = "\n"
        elif character == "`" and quote != "'":
            dynamic = True
            conservative_command[index] = "\n"
        elif quote:
            if character == quote:
                quote = None
        elif character in {"'", '"'}:
            quote = character
        elif character in ";\n|&":
            segments.append(command[start:index])
            if (
                character in "|&"
                and index + 1 < len(command)
                and command[index + 1] == character
            ):
                index += 1
            start = index + 1
        index += 1
    if quote or escaped or dynamic:
        return SEGMENT_SPLIT.split("".join(conservative_command))
    segments.append(command[start:])
    return segments


def _tokenise(segment: str) -> list[str]:
    try:
        return shlex.split(segment)
    except ValueError:  # an unbalanced quote is still worth judging
        return segment.split()


def _strip_prefix(tokens: list[str]) -> list[str]:
    """Drop `VAR=…` assignments and wrapper words that precede the program."""
    index = 0
    while index < len(tokens):
        if ASSIGNMENT.match(tokens[index]):
            index += 1
            continue
        wrapper = Path(tokens[index]).name
        if wrapper not in PREFIX_WORDS:
            break
        index += 1
        if wrapper == "env":
            while index < len(tokens) and tokens[index].startswith("-"):
                option = tokens[index]
                index += 2 if option in ENV_VALUE_OPTIONS else 1
    return tokens[index:]


def _subcommand_at(tokens: list[str], value_options: set[str]) -> tuple[int, str] | None:
    """The position and value of the first non-option, non-value word."""
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            return None
        if token in value_options:
            index += 2
            continue
        if token.startswith("-"):
            index += 1
            continue
        return index, token
    return None


def _subcommand(tokens: list[str], value_options: set[str]) -> str | None:
    """The first word that is neither an option nor an option's value."""
    found = _subcommand_at(tokens, value_options)
    return found[1] if found else None


def is_push_command(command: str) -> bool:
    """True when any segment of this shell line pushes or opens/merges a PR."""
    if is_git_push_command(command):
        return True
    for segment in _shell_segments(command):
        tokens = _strip_prefix(_tokenise(segment))
        if not tokens:
            continue
        program = Path(tokens[0]).name
        if program == "eval":
            if is_push_command(" ".join(tokens[1:])):
                return True
        elif program in SHELL_PROGRAMS and "-c" in tokens[1:]:
            index = tokens.index("-c")
            if index + 1 < len(tokens) and is_push_command(tokens[index + 1]):
                return True
        elif program == "gh":
            rest = tokens[1:]
            found = _subcommand_at(rest, GH_VALUE_OPTIONS)
            if found and found[1] == "pr":
                after = rest[found[0] + 1:]
                if _subcommand(after, GH_VALUE_OPTIONS) in {"create", "merge"}:
                    return True
    return False


def is_pr_create_command(command: str) -> bool:
    """True when a shell segment creates a PR."""
    for segment in _shell_segments(command):
        tokens = _strip_prefix(_tokenise(segment))
        if not tokens or Path(tokens[0]).name != "gh":
            continue
        rest = tokens[1:]
        found = _subcommand_at(rest, GH_VALUE_OPTIONS)
        if found and found[1] == "pr":
            after = rest[found[0] + 1:]
            if _subcommand(after, GH_VALUE_OPTIONS) == "create":
                return True
    return False


def is_pr_merge_command(command: str) -> bool:
    """True when a shell segment merges a PR."""
    for segment in _shell_segments(command):
        tokens = _strip_prefix(_tokenise(segment))
        if not tokens or Path(tokens[0]).name != "gh":
            continue
        rest = tokens[1:]
        found = _subcommand_at(rest, GH_VALUE_OPTIONS)
        if found and found[1] == "pr":
            after = rest[found[0] + 1:]
            if _subcommand(after, GH_VALUE_OPTIONS) == "merge":
                return True
    return False


def github_repo_from_origin(repo: Path) -> str | None:
    """Return GH_REPO syntax derived from the literal configured origin URL."""
    url = git_maybe(repo, "remote", "get-url", "origin")
    if not url:
        return None
    match = re.fullmatch(r"https?://([^/]+)/([^/]+)/(.+?)(?:\.git)?", url)
    if not match:
        match = re.fullmatch(r"git@([^:]+):([^/]+)/(.+?)(?:\.git)?", url)
    if not match:
        match = re.fullmatch(r"ssh://git@([^/]+)/([^/]+)/(.+?)(?:\.git)?", url)
    if not match:
        return None
    host, owner, name = match.groups()
    return f"{host}/{owner}/{name}"


def is_canonical_pr_create_command(repo: Path, command: str) -> bool:
    """True only for one function-proof, origin-bound PR creation command."""
    trusted = shutil.which("gh")
    trusted_env = shutil.which("env")
    gh_repo = github_repo_from_origin(repo)
    if not trusted or not trusted_env or not gh_repo:
        return False
    gh_tokens = _tokenise(command)
    expected_prefix = [
        "command", str(Path(trusted_env).resolve()), f"LOOM_REPO_ROOT={repo.resolve()}",
        f"GH_REPO={gh_repo}", str(Path(trusted).resolve()), "pr", "create",
    ]
    trailing = gh_tokens[7:]
    repo_overrides = {"-R", "--repo", "--hostname"}
    has_repo_override = any(
        token in repo_overrides
        or token.startswith("--repo=")
        or token.startswith("--hostname=")
        or (token.startswith("-R") and token != "-R")
        for token in trailing
    )
    return (
        gh_tokens[:7] == expected_prefix
        and not has_repo_override
        and command == render_quote_all(gh_tokens)
    )


def canonical_pr_create_repo(command: str) -> Path | None:
    """Return the selected repo only when the whole PR-create form is trusted."""
    tokens = _tokenise(command)
    if len(tokens) < 7 or not tokens[2].startswith("LOOM_REPO_ROOT="):
        return None
    selected = Path(tokens[2].split("=", 1)[1])
    if not selected.is_absolute() or not selected.is_dir():
        return None
    try:
        repo = repo_root(selected.resolve())
    except UsageError:
        return None
    if repo.resolve() != selected.resolve():
        return None
    return repo if is_canonical_pr_create_command(repo, command) else None


def check_pr_create_remote_head(repo: Path, command: str) -> str | None:
    """Require PR creation to reference the already-published current HEAD."""
    branch = git_maybe(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
    head = git_maybe(repo, "rev-parse", "HEAD")
    if not branch or not head:
        return "PR creation requires a current symbolic branch and commit"

    tokens = _tokenise(command)
    head_values: list[str] = []
    for index, token in enumerate(tokens):
        if token in {"--head", "-H"} and index + 1 < len(tokens):
            head_values.append(tokens[index + 1])
        elif token.startswith("--head="):
            head_values.append(token.split("=", 1)[1])
        elif token.startswith("-H") and token != "-H":
            head_values.append(token[2:])
        if token == "--body-file" and (
            index + 1 >= len(tokens) or not Path(tokens[index + 1]).is_absolute()
        ):
            return "PR body file must be an absolute path"
        if token.startswith("--body-file=") and not Path(token.split("=", 1)[1]).is_absolute():
            return "PR body file must be an absolute path"
    if head_values != [branch]:
        if not head_values:
            return f"PR creation requires explicit current branch head {branch!r}"
        else:
            return f"PR head must be the current branch {branch!r}"

    gh_repo = github_repo_from_origin(repo)
    trusted_gh = shutil.which("gh")
    if not gh_repo or not trusted_gh:
        return "PR creation requires a trusted GitHub origin and gh executable"
    repo_parts = gh_repo.split("/")
    host, owner, name = repo_parts[0], repo_parts[-2], repo_parts[-1]
    try:
        # GitHub CLI documents the endpoint form plus --hostname and --jq:
        # https://cli.github.com/manual/gh_api
        # GitHub documents this reference endpoint and its object.sha response:
        # https://docs.github.com/en/rest/git/refs#get-a-reference
        observed = subprocess.run(
            [str(Path(trusted_gh).resolve()), "api", "--hostname", host,
             f"repos/{owner}/{name}/git/ref/heads/{quote(branch, safe='')}",
             "--jq", ".object.sha"],
            cwd=repo, capture_output=True, text=True, timeout=30,
            env={**os.environ, "GH_REPO": gh_repo, "LOOM_REPO_ROOT": str(repo)},
        )
    except (OSError, subprocess.TimeoutExpired):
        observed = None
    if observed is not None and observed.returncode == 0 and observed.stdout.strip() == head:
        return None
    return f"remote branch {branch!r} must already equal reviewed HEAD {head}"


def is_git_push_command(command: str) -> bool:
    """True when any shell segment can reach a Git push."""
    for segment in _shell_segments(command):
        tokens = _strip_prefix(_tokenise(segment))
        if not tokens:
            continue
        program = Path(tokens[0]).name
        if program == "eval":
            if is_git_push_command(" ".join(tokens[1:])):
                return True
        elif program in SHELL_PROGRAMS and "-c" in tokens[1:]:
            index = tokens.index("-c")
            if index + 1 < len(tokens) and is_git_push_command(tokens[index + 1]):
                return True
        elif program == "git" and _subcommand(tokens[1:], GIT_VALUE_OPTIONS) == "push":
            return True
    return False


def git_dash_c_push_cwd(command: str, fallback: str) -> str | None:
    """Return the one unambiguous repository selected by every Git push.

    The host-reported cwd is authoritative only when a push has no directory
    override. An absolute ``-C`` anchors later relative ``-C`` options. A
    relative first ``-C``, another directory-changing option, a missing or
    invalid directory, or pushes selecting distinct repositories is unsafe
    because the hook cannot prove which repository the shell will push.
    """
    selected_roots: set[str] = set()
    shell_root: Path | None = None
    repository_env_changed = False
    for segment in _shell_segments(command):
        raw_tokens = _tokenise(segment)
        tokens = _strip_prefix(raw_tokens)
        if not tokens:
            continue
        if any(Path(token).name == "env" for token in raw_tokens) and any(
            token.startswith("-C")
            or token == "--chdir"
            or token.startswith("--chdir=")
            for token in raw_tokens
        ):
            return None
        segment_changes_repository_env = any(
            ASSIGNMENT.match(token)
            and token.split("=", 1)[0] in GIT_REPOSITORY_ENV
            for token in raw_tokens
        )
        program = Path(tokens[0]).name.lstrip("(")
        if program == "export" and any(
            token.split("=", 1)[0] in GIT_REPOSITORY_ENV
            for token in tokens[1:]
        ):
            segment_changes_repository_env = True
        repository_env_changed = (
            repository_env_changed or segment_changes_repository_env
        )
        if program in {"cd", "pushd"}:
            directory_args = [
                token for token in tokens[1:]
                if token != "--" and not token.startswith("-")
            ]
            if len(directory_args) != 1:
                return None
            candidate = Path(directory_args[0])
            if candidate.is_absolute():
                shell_root = candidate
            elif shell_root is not None:
                shell_root = shell_root / candidate
            else:
                return None
            if not shell_root.is_dir():
                return None
            continue
        if program == "popd":
            return None
        if program == "eval" and is_push_command(" ".join(tokens[1:])):
            return None
        if program in SHELL_PROGRAMS and "-c" in tokens[1:]:
            index = tokens.index("-c")
            if index + 1 < len(tokens) and is_push_command(tokens[index + 1]):
                return None
        if any(Path(token).name == "xargs" for token in raw_tokens) and is_push_command(segment):
            return None
        if program == "gh" and is_push_command(segment):
            if repository_env_changed or any(
                token.startswith("-R")
                or token == "--repo"
                or token.startswith("--repo=")
                for token in tokens[1:]
            ):
                return None
            if is_pr_merge_command(segment) and shell_root is None:
                return None
            root = shell_root if shell_root is not None else Path(fallback)
            selected_roots.add(str(root.resolve()))
            continue
        if program != "git" or _subcommand(tokens[1:], GIT_VALUE_OPTIONS) != "push":
            continue
        if repository_env_changed:
            return None
        selected = shell_root
        index = 1
        while index < len(tokens):
            token = tokens[index]
            if token == "-C":
                if index + 1 >= len(tokens):
                    return None
                candidate = Path(tokens[index + 1])
                if candidate.is_absolute():
                    selected = candidate
                elif selected is not None:
                    selected = selected / candidate
                else:
                    return None
                index += 2
                continue
            if token.startswith("-C") or token in {"--git-dir", "--work-tree"}:
                return None
            if token.startswith("--git-dir=") or token.startswith("--work-tree="):
                return None
            if token in GIT_VALUE_OPTIONS:
                index += 2
                continue
            if token.startswith("-"):
                index += 1
                continue
            break
        root = selected if selected is not None else Path(fallback)
        if not root.is_dir():
            return None
        selected_roots.add(str(root.resolve()))
    if len(selected_roots) > 1:
        return None
    return next(iter(selected_roots)) if selected_roots else None


CANONICAL_PUSH_FLAGS = ["--no-follow-tags", "--recurse-submodules=no", "-u", "--no-verify"]


SAFE_REMOTE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


def quote_all_shell_token(token: str) -> str:
    """Render one argv token without leaving any shell expansion position."""
    return "'" + token.replace("'", "'\"'\"'") + "'"


def render_quote_all(tokens: list[str]) -> str:
    return " ".join(quote_all_shell_token(token) for token in tokens)


def canonical_git_push(
    command: str, fallback: str
) -> tuple[Path | None, str | None, str | None]:
    """Validate the complete shell bytes for the one supported Git push."""
    trusted = shutil.which("git")
    if not trusted:
        return None, None, "the hook environment has no trusted Git executable"
    trusted_git = str(Path(trusted).resolve())
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError as exc:
        return None, None, f"the Git push command has malformed quoting: {exc}"
    if command != render_quote_all(tokens):
        return None, None, "the entire Git push command must use canonical quote-all rendering"
    if len(tokens) < 2 or tokens[0] != "command":
        return None, None, "the Git push must begin with the standard command builtin"
    if tokens[1] != trusted_git or not Path(tokens[1]).is_absolute():
        return None, None, f"the Git executable must be the trusted absolute path {trusted_git!r}"

    index = 2
    selected = Path(fallback)
    if index < len(tokens) and tokens[index] == "-C":
        if index + 1 >= len(tokens) or not Path(tokens[index + 1]).is_absolute():
            return None, None, "Git -C must name the selected repository by absolute path"
        selected = Path(tokens[index + 1])
        index += 2
    try:
        repo = repo_root(selected.resolve())
    except UsageError as exc:
        return None, None, str(exc)
    if "-C" in tokens[1:index] and selected.resolve() != repo.resolve():
        return None, None, "Git -C must name the selected repository root exactly"

    required = ["push", *CANONICAL_PUSH_FLAGS]
    if tokens[index:index + len(required)] != required:
        return None, None, (
            "Git push must use exactly --no-follow-tags --recurse-submodules=no -u --no-verify"
        )
    tail = tokens[index + len(required):]
    if len(tail) != 2:
        return None, None, "Git push must name one literal remote and one explicit refspec"
    remote, refspec = tail
    if not SAFE_REMOTE.fullmatch(remote):
        return None, None, f"Git push remote {remote!r} is not a safe literal name"
    if remote != "origin":
        return None, None, "the Git push remote must be literal 'origin'"

    head = git_text(repo, "rev-parse", "HEAD")
    branch = git_maybe(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
    if not branch:
        return None, None, "the selected repository has no current symbolic branch"
    expected = f"{head}:refs/heads/{branch}"
    if refspec != expected:
        return None, None, f"Git push refspec must be exactly {expected!r}, got {refspec!r}"
    return repo, head, None


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


PUBLISH_REDIRECT_ENV = {
    "GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_NAMESPACE", "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_EXEC_PATH", "GIT_SSH",
    "GIT_SSH_COMMAND", "GIT_PROXY_COMMAND", "GIT_CONFIG", "GIT_CONFIG_SYSTEM",
    "GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_COUNT",
    "GIT_CONFIG_PARAMETERS", "GH_HOST", "GH_REPO",
}


PUBLISH_REDIRECT_CONFIG = (
    r"^(remote\.origin\.(pushurl|proxy|vcs|receivepack|uploadpack)"
    r"|url\..*\.(push)?insteadof|core\.sshcommand)$"
)


PUBLISH_EXECUTABLE_DIRS = (
    Path("/usr/bin"), Path("/usr/local/bin"), Path("/opt/homebrew/bin"),
    Path("/home/linuxbrew/.linuxbrew/bin"),
)


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


__all__ = [name for name in globals() if not name.startswith("__")]
