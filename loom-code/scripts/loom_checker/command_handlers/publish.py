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

from .push import CANONICAL_PUSH_FLAGS, _cmd_push, github_repo_from_origin
from ..helpers import UsageError, artifact_path, changed_paths, git_maybe, git_ok, git_text, glob_to_regex, is_real_date, load_manifest, repo_root, report
from ..parsing import parse_document




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


def resolve_publish_executable(name: str) -> str | None:
    """Resolve publication tools from host install roots, never caller PATH."""
    for directory in PUBLISH_EXECUTABLE_DIRS:
        candidate = directory / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate.resolve())
    return None


def run_publish_external(argv: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run one trusted publication argv; kept as a seam for isolated tests."""
    return subprocess.run(argv, capture_output=True, text=True, timeout=30, **kwargs)


wait_publish_interval = time.sleep


PUBLISH_CI_POLL_SECONDS = 10


PUBLISH_CI_REGISTRATION_WAITS = 6


PUBLISH_CI_PENDING_WAITS = 360


def _publish_usage(reason: str, err) -> int:
    err.write(f"publish: {reason}\n")
    return 2


def _publish_block(reason: str, err) -> int:
    return report([("push.attestation", reason)], err)


CONTEXTUAL_PR_HEADINGS = (
    "Context", "Intended outcome", "Scope", "Decisions", "Implementation",
    "Behaviour change", "Verification", "Risks and rollback", "Follow-ups",
)


def validate_contextual_pr_body(body: str) -> str | None:
    """Recompute the structural PR-body floor; semantic truth stays review-owned."""
    sections: list[tuple[str, list[str]]] = []
    outside_fences: list[str] = []
    fence: tuple[str, int] | None = None
    for line in body.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if marker and fence is None:
            token = marker.group(1)
            fence = (token[0], len(token))
            continue
        if marker and fence is not None:
            token, suffix = marker.group(1), marker.group(2)
            if token[0] == fence[0] and len(token) >= fence[1] and not suffix.strip():
                fence = None
            continue
        if fence is not None:
            continue
        outside_fences.append(line)
        heading = re.fullmatch(r"## ([^#\n].*)", line)
        if heading:
            sections.append((heading.group(1), []))
        elif sections:
            sections[-1][1].append(line)

    if [heading for heading, _content in sections] != list(CONTEXTUAL_PR_HEADINGS):
        return (
            "PR body must contain Ship's nine top-level contextual headings "
            "exactly once and in order, with no competing top-level heading"
        )
    for heading, lines in sections:
        content = "\n".join(lines)
        visible = re.sub(r"<!--.*?-->", " ", content, flags=re.DOTALL)
        alphanumeric_count = sum(character.isalnum() for character in visible)
        one_ascii_token = re.fullmatch(r"\s*[A-Za-z]+[.!?:;,-]*\s*", visible) is not None
        template_placeholder = re.fullmatch(r"\s*<[^>\n]+>\s*", visible) is not None
        sentinel = (
            heading == "Follow-ups"
            and re.sub(r"[\W_]+", "", visible).casefold() == "none"
        )
        if (
            (alphanumeric_count < 8 or one_ascii_token or template_placeholder)
            and not sentinel
        ):
            return f"PR body section {heading!r} has no substantive content"
    visible_body = re.sub(
        r"<!--.*?-->", " ", "\n".join(outside_fences), flags=re.DOTALL
    )
    if re.search(
        r"\b(?:private|hidden)(?:\s+or\s+(?:private|hidden))?\s+chain-of-thought\b",
        visible_body,
        flags=re.IGNORECASE,
    ):
        return "PR body must not claim to expose private or hidden chain-of-thought"
    return None


def _publish_origin_state(repo: Path, expected_branch: str) -> tuple[str | None, str | None]:
    """Return the single literal origin URL or a publication identity error."""
    branch = git_maybe(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
    if branch != expected_branch:
        return None, "symbolic branch changed before publication"
    origin_urls = (git_maybe(repo, "config", "--get-all", "remote.origin.url") or "").splitlines()
    if len(origin_urls) != 1:
        return None, "literal origin must have exactly one fetch URL"
    redirect_config = git_maybe(repo, "config", "--get-regexp", PUBLISH_REDIRECT_CONFIG)
    if redirect_config:
        return None, (
            "origin redirection, transport, remote executable, pushurl, insteadOf, "
            "sshCommand, or proxy configuration must be removed"
        )
    return origin_urls[0], None


def _publish_args(args: list[str]) -> tuple[str, Path, Path | None, bool] | str:
    authorized = False
    title: str | None = None
    body_file: Path | None = None
    intent_file: Path | None = None
    rest = list(args)
    while rest:
        token = rest.pop(0)
        if token == "--confirm-authorized":
            if authorized:
                return "--confirm-authorized may appear only once"
            authorized = True
        elif token in {"--title", "--body-file", "--intent"}:
            if not rest:
                return f"{token} needs a value"
            value = rest.pop(0)
            if token == "--title":
                if title is not None:
                    return "--title may appear only once"
                title = value
            elif token == "--body-file":
                if body_file is not None:
                    return "--body-file may appear only once"
                body_file = Path(value)
            else:
                if intent_file is not None:
                    return "--intent may appear only once"
                intent_file = Path(value)
        else:
            return f"unexpected argument {token!r}"
    if not authorized and intent_file is None:
        return "--intent or --confirm-authorized is required for publication authorization"
    if not title or not title.strip():
        return "--title needs non-empty text"
    if body_file is None or not body_file.is_absolute():
        return "--body-file must name an absolute path"
    if not body_file.is_file() or not os.access(body_file, os.R_OK):
        return f"--body-file is not a readable file: {body_file}"
    if intent_file is not None:
        if not intent_file.is_absolute():
            return "--intent must name an absolute path"
        if not intent_file.is_file() or not os.access(intent_file, os.R_OK):
            return f"--intent is not a readable file: {intent_file}"
    return title, body_file, intent_file, authorized


def _publication_change_id(repo: Path) -> tuple[str | None, str | None]:
    """Derive the publication identity from the sole attestation in the branch."""
    manifest = load_manifest()
    template = manifest.get("artifacts", {}).get("attestation", {}).get("path")
    if not template:
        return None, "contract manifest declares no attestation artifact"
    matcher = glob_to_regex(template.replace("<change-id>", "*"))
    candidates = sorted(path for path in changed_paths(repo) if matcher.fullmatch(path))
    if len(candidates) != 1:
        return None, f"branch must carry exactly one attested change; found {len(candidates)}"
    match = re.fullmatch(
        re.escape(template).replace(re.escape("<change-id>"), r"(?P<change_id>[^/]+)"),
        candidates[0],
    )
    if match is None:
        return None, "cannot derive attested change id"
    change_id = match.group("change_id")
    try:
        payload = json.loads(git_text(repo, "show", f"HEAD:{candidates[0]}"))
    except (UsageError, json.JSONDecodeError):
        return None, "attestation must be committed at HEAD"
    if not isinstance(payload, dict) or payload.get("change_id") != change_id:
        return None, "attestation change_id does not match its path"
    return change_id, None


def _intent_authorizes_publication(
    repo: Path, intent_file: Path
) -> tuple[bool, str | None]:
    """Trust only the attested change's canonical intent as committed at HEAD."""
    change_id, error = _publication_change_id(repo)
    if error:
        return False, error
    manifest = load_manifest()
    canonical = artifact_path(manifest, "intent", change_id, repo).resolve()
    if intent_file.resolve() != canonical:
        return False, "intent path does not match the attested change"
    intent_rel = canonical.relative_to(repo)
    try:
        committed = git_text(repo, "show", f"HEAD:{intent_rel}")
    except UsageError:
        return False, "automatic publication requires a committed intent at HEAD"
    front, _sections = parse_document(committed)
    if not re.fullmatch(r"confirmed \d{4}-\d{2}-\d{2}", front.get("status", "")):
        return False, "committed intent is not confirmed"
    publication = front.get("publication", "")
    match = re.fullmatch(
        r"automatic — authorized (\d{4}-\d{2}-\d{2}) by (\S(?:.*\S)?)",
        publication,
    )
    if match is None or not is_real_date(match.group(1)):
        return False, "committed intent has no valid automatic-publication authorization"
    return True, None


def _publish_env(repo_identity: str, repo: Path, trusted_paths: tuple[str, str]) -> dict[str, str]:
    env = {
        key: value for key, value in os.environ.items()
        if key not in PUBLISH_REDIRECT_ENV and not key.startswith("GIT_CONFIG_KEY_")
        and not key.startswith("GIT_CONFIG_VALUE_")
    }
    safe_path = os.pathsep.join(dict.fromkeys(
        [str(Path(path).parent) for path in trusted_paths] + ["/usr/bin", "/bin"]
    ))
    env.update({"GH_REPO": repo_identity, "LOOM_REPO_ROOT": str(repo), "PATH": safe_path})
    return env


def _external_or_block(argv: list[str], *, repo: Path, env: dict[str, str], err):
    try:
        result = run_publish_external(argv, cwd=repo, env=env)
    except (OSError, subprocess.TimeoutExpired) as exc:
        _publish_block(f"publication command could not run: {type(exc).__name__}: {exc}", err)
        return None
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or f"exit {result.returncode}").strip()
        _publish_block(f"publication command failed: {detail}", err)
        return None
    return result


def _observe_required_ci(
    pr_url: str, *, trusted_gh: str, repo: Path, env: dict[str, str], out, err
) -> int:
    """Observe required PR checks in this process until a terminal state."""
    pending_waits = 0
    registration_waits = 0
    while True:
        argv = [
            trusted_gh, "pr", "checks", pr_url, "--required",
            "--json", "name,state,bucket",
        ]
        try:
            result = run_publish_external(argv, cwd=repo, env=env)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return _publish_block(
                f"required CI could not be observed: {type(exc).__name__}: {exc}", err
            )
        # gh 2.88.1 emits these quoted-branch errors before checks register;
        # the command layer maps the returned error to exit 1 with blank stdout.
        # https://github.com/cli/cli/blob/v2.88.1/pkg/cmd/pr/checks/checks.go
        # https://github.com/cli/cli/blob/v2.88.1/pkg/cmd/pr/checks/checks_test.go
        # https://github.com/cli/cli/issues/7401
        no_checks_yet = (
            result.returncode == 1
            and not result.stdout.strip()
            and re.fullmatch(
                r"no (?:required )?checks reported on the '.*' branch",
                result.stderr.strip(),
            ) is not None
        )
        # gh uses exit 8 while checks are pending and exit 1 before a new
        # branch's checks register. JSON remains authoritative otherwise.
        if result.returncode not in {0, 8} and not no_checks_yet:
            detail = (result.stderr or result.stdout or f"exit {result.returncode}").strip()
            return _publish_block(f"required CI could not be observed: {detail}", err)
        if no_checks_yet or (result.returncode == 0 and not result.stdout.strip()):
            checks = []
        else:
            try:
                checks = json.loads(result.stdout)
            except json.JSONDecodeError as exc:
                return _publish_block(f"cannot decode required CI response: {exc}", err)
        if not isinstance(checks, list) or any(not isinstance(check, dict) for check in checks):
            return _publish_block("required CI response is not a list of checks", err)
        if not checks:
            if registration_waits >= PUBLISH_CI_REGISTRATION_WAITS:
                out.write("No required checks registered\n")
                return 0
            wait_publish_interval(PUBLISH_CI_POLL_SECONDS)
            registration_waits += 1
            continue

        states = [(str(check.get("name", "unnamed")),
                   str(check.get("state", "")).upper(),
                   str(check.get("bucket", "")).casefold()) for check in checks]
        action = [name for name, state, _ in states if state == "ACTION_REQUIRED"]
        cancelled = [name for name, state, bucket in states
                     if state in {"CANCELLED", "CANCELED"} or bucket == "cancel"]
        failed = [name for name, state, bucket in states
                  if state in {"FAILURE", "TIMED_OUT", "STARTUP_FAILURE"}
                  or bucket == "fail"]
        if action:
            return _publish_block(
                "required CI requires user action: " + ", ".join(action), err
            )
        if cancelled:
            return _publish_block("required CI cancelled: " + ", ".join(cancelled), err)
        if failed:
            return _publish_block("required CI failed: " + ", ".join(failed), err)

        pending = [name for name, state, bucket in states
                   if state in {"PENDING", "QUEUED", "IN_PROGRESS", "WAITING", "REQUESTED"}
                   or bucket == "pending"]
        if pending:
            if pending_waits >= PUBLISH_CI_PENDING_WAITS:
                return _publish_block(
                    "required CI requires user action because no reliable terminal result "
                    "was available after 60 minutes",
                    err,
                )
            wait_publish_interval(PUBLISH_CI_POLL_SECONDS)
            pending_waits += 1
            continue
        unknown = [name for name, _, bucket in states
                   if bucket not in {"pass", "skipping"}]
        if unknown:
            return _publish_block(
                "required CI requires user action because its state is unknown: "
                + ", ".join(unknown), err,
            )
        out.write("Required CI passed\n")
        return 0


def cmd_publish(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    """Validate and publish one reviewed HEAD without caller-built shell text."""
    parsed = _publish_args(args)
    if isinstance(parsed, str):
        return _publish_usage(parsed, err)
    title, body_file, intent_file, authorized = parsed

    try:
        body = body_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return _publish_usage(f"cannot read PR body as UTF-8: {exc}", err)
    body_error = validate_contextual_pr_body(body)
    if body_error:
        return report([("push.contextual-body", body_error)], err)

    redirected = sorted(
        key for key in os.environ
        if key in PUBLISH_REDIRECT_ENV
        or key.startswith("GIT_CONFIG_KEY_") or key.startswith("GIT_CONFIG_VALUE_")
    )
    if redirected:
        return _publish_usage(
            "remove repository or host redirect environment variables: "
            + ", ".join(redirected), err,
        )

    trusted_git = resolve_publish_executable("git")
    trusted_gh = resolve_publish_executable("gh")
    if not trusted_git or not trusted_gh:
        return _publish_block("publication requires trusted git and gh executables", err)

    previous_path = os.environ.get("PATH")
    os.environ["PATH"] = os.pathsep.join(dict.fromkeys(
        [str(Path(trusted_git).parent), str(Path(trusted_gh).parent), "/usr/bin", "/bin"]
    ))
    try:
        with tempfile.TemporaryDirectory(prefix="loom-publish-") as snapshot_dir:
            body_snapshot = Path(snapshot_dir) / "pr-body.md"
            body_snapshot.write_text(body, encoding="utf-8")
            body_snapshot.chmod(0o600)
            return _cmd_publish_trusted(
                title, body_snapshot, intent_file, authorized,
                trusted_git, trusted_gh, out, err,
            )
    finally:
        if previous_path is None:
            os.environ.pop("PATH", None)
        else:
            os.environ["PATH"] = previous_path


def _cmd_publish_trusted(
    title: str, body_file: Path, intent_file: Path | None, authorized: bool,
    trusted_git: str, trusted_gh: str,
    out=sys.stdout, err=sys.stderr,
) -> int:
    try:
        repo = repo_root(Path.cwd()).resolve()
    except UsageError as exc:
        return _publish_block(str(exc), err)

    intent_error: str | None = None
    if not authorized and intent_file is not None:
        intent_authorized, intent_error = _intent_authorizes_publication(repo, intent_file)
        authorized = intent_authorized
    if not authorized:
        return _publish_usage(
            f"{intent_error or 'intent has no confirmed automatic-publication authorization'}; "
            "obtain one publication decision and pass --confirm-authorized",
            err,
        )

    head = git_maybe(repo, "rev-parse", "HEAD")
    branch = git_maybe(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
    if not head or not branch or not git_ok(repo, "check-ref-format", "--branch", branch):
        return _publish_block("publication requires a safe current symbolic branch and HEAD", err)
    origin_url, origin_error = _publish_origin_state(repo, branch)
    if origin_error:
        return _publish_block(origin_error, err)
    identity = github_repo_from_origin(repo)
    if not identity:
        return _publish_block("literal origin is not a supported GitHub repository URL", err)
    env = _publish_env(identity, repo, (trusted_git, trusted_gh))

    if _cmd_push(["--head", head, "--require-live-head"], out, err) != 0:
        return 1
    out.write(f"Attestation validated for {head}\n")

    base_result = _external_or_block(
        # gh repo view accepts [HOST/]OWNER/REPO and exposes defaultBranchRef:
        # https://cli.github.com/manual/gh_repo_view
        [trusted_gh, "repo", "view", identity, "--json", "defaultBranchRef",
         "--jq", ".defaultBranchRef.name"],
        repo=repo, env=env, err=err,
    )
    if base_result is None:
        return 1
    base = base_result.stdout.strip()
    if not base or base == branch or not git_ok(repo, "check-ref-format", "--branch", base):
        return _publish_block("origin default branch is missing, unsafe, or equals the head branch", err)
    out.write(f"Publication target: {identity} base {base}\n")

    remote_result = _external_or_block(
        # Git documents ls-remote as the read-only remote-ref query:
        # https://git-scm.com/docs/git-ls-remote
        [trusted_git, "-C", str(repo), "ls-remote", "--heads", "origin",
         f"refs/heads/{branch}"], repo=repo, env=env, err=err,
    )
    if remote_result is None:
        return 1
    remote_lines = [line for line in remote_result.stdout.splitlines() if line.strip()]
    if len(remote_lines) > 1:
        return _publish_block("origin returned multiple remote branch identities", err)
    remote_head = remote_lines[0].split()[0] if remote_lines else None
    if remote_head and remote_head != head:
        if not git_ok(repo, "cat-file", "-e", f"{remote_head}^{{commit}}") or not git_ok(
            repo, "merge-base", "--is-ancestor", remote_head, head
        ):
            return _publish_block(
                "remote branch is unknown or diverged; fetch and reconcile it before publishing",
                err,
            )

    if git_text(repo, "rev-parse", "HEAD") != head:
        return _publish_block("live HEAD moved before push", err)
    current_origin, origin_error = _publish_origin_state(repo, branch)
    if origin_error or current_origin != origin_url:
        return _publish_block(
            f"publication identity changed before push: {origin_error or 'origin URL changed'}", err
        )
    if remote_head != head:
        push_result = _external_or_block(
            [trusted_git, "-C", str(repo), "push", *CANONICAL_PUSH_FLAGS,
             "origin", f"{head}:refs/heads/{branch}"],
            repo=repo, env=env, err=err,
        )
        if push_result is None:
            return 1

    verify_result = _external_or_block(
        [trusted_git, "-C", str(repo), "ls-remote", "--heads", "origin",
         f"refs/heads/{branch}"], repo=repo, env=env, err=err,
    )
    if verify_result is None:
        return 1
    verified = [line.split()[0] for line in verify_result.stdout.splitlines() if line.strip()]
    if verified != [head]:
        return _publish_block("origin branch does not resolve to the selected HEAD after push", err)
    if git_text(repo, "rev-parse", "HEAD") != head:
        return _publish_block("live HEAD moved before PR creation", err)
    current_origin, origin_error = _publish_origin_state(repo, branch)
    if origin_error or current_origin != origin_url:
        return _publish_block(
            f"publication identity changed before PR creation: "
            f"{origin_error or 'origin URL changed'}", err,
        )

    host, owner, name = identity.split("/", 2)
    # GitHub's pulls endpoint exposes both head/base repository identity and SHA:
    # https://docs.github.com/en/rest/pulls/pulls#list-pull-requests
    pulls_endpoint = (
        f"repos/{quote(owner, safe='')}/{quote(name, safe='')}/pulls"
        f"?state=open&head={quote(f'{owner}:{branch}', safe='')}"
    )
    list_result = _external_or_block(
        [trusted_gh, "api", "--hostname", host, pulls_endpoint],
        repo=repo, env=env, err=err,
    )
    if list_result is None:
        return 1
    try:
        candidates = json.loads(list_result.stdout)
    except json.JSONDecodeError as exc:
        return _publish_block(f"cannot decode existing PR response: {exc}", err)
    if not isinstance(candidates, list):
        return _publish_block("existing PR response is not a list", err)
    candidate_matches: list[tuple[str, bool]] = []
    expected_repo = f"{owner}/{name}"
    for candidate in candidates:
        try:
            candidate_url = candidate["html_url"]
            head_data, base_data = candidate["head"], candidate["base"]
            matches = (
                head_data["sha"] == head
                and head_data["repo"]["full_name"].casefold() == expected_repo.casefold()
                and base_data["ref"] == base
                and base_data["repo"]["full_name"].casefold() == expected_repo.casefold()
                and isinstance(candidate_url, str) and candidate_url.startswith("https://")
            )
        except (KeyError, TypeError, AttributeError):
            matches = False
        if not matches:
            return _publish_block("existing pull request identity does not match origin, HEAD, and base", err)
        candidate_matches.append((candidate_url, bool(candidate.get("draft", False))))
    if len(candidate_matches) > 1:
        return _publish_block("multiple open pull requests match the current branch", err)

    current_origin, origin_error = _publish_origin_state(repo, branch)
    if origin_error or current_origin != origin_url:
        return _publish_block(
            f"publication identity changed before PR creation: "
            f"{origin_error or 'origin URL changed'}", err,
        )
    pre_create_remote = _external_or_block(
        [trusted_git, "-C", str(repo), "ls-remote", "--heads", "origin",
         f"refs/heads/{branch}"], repo=repo, env=env, err=err,
    )
    if pre_create_remote is None:
        return 1
    current_remote = [
        line.split()[0] for line in pre_create_remote.stdout.splitlines() if line.strip()
    ]
    if current_remote != [head]:
        return _publish_block("remote branch moved before PR creation", err)
    if git_text(repo, "rev-parse", "HEAD") != head:
        return _publish_block("live HEAD moved before PR creation", err)
    current_origin, origin_error = _publish_origin_state(repo, branch)
    if origin_error or current_origin != origin_url:
        return _publish_block(
            f"publication identity changed before PR creation: "
            f"{origin_error or 'origin URL changed'}", err,
        )

    if candidate_matches:
        pr_url, is_draft = candidate_matches[0]
        update_result = _external_or_block(
            [trusted_gh, "pr", "edit", pr_url, "--title", title,
             "--body-file", str(body_file)],
            repo=repo, env=env, err=err,
        )
        if update_result is None:
            return 1
        if git_text(repo, "rev-parse", "HEAD") != head:
            return _publish_block("live HEAD moved after PR update", err)
        current_origin, origin_error = _publish_origin_state(repo, branch)
        if origin_error or current_origin != origin_url:
            return _publish_block(
                f"publication identity changed after PR update: "
                f"{origin_error or 'origin URL changed'}", err,
            )
        post_update_remote = _external_or_block(
            [trusted_git, "-C", str(repo), "ls-remote", "--heads", "origin",
             f"refs/heads/{branch}"], repo=repo, env=env, err=err,
        )
        if post_update_remote is None:
            return 1
        updated_remote = [
            line.split()[0] for line in post_update_remote.stdout.splitlines() if line.strip()
        ]
        if updated_remote != [head]:
            return _publish_block("remote branch moved after PR update", err)
        if is_draft:
            ready_result = _external_or_block(
                [trusted_gh, "pr", "ready", pr_url],
                repo=repo, env=env, err=err,
            )
            if ready_result is None:
                return 1
            if git_text(repo, "rev-parse", "HEAD") != head:
                return _publish_block("live HEAD moved after PR readiness", err)
            current_origin, origin_error = _publish_origin_state(repo, branch)
            if origin_error or current_origin != origin_url:
                return _publish_block(
                    f"publication identity changed after PR readiness: "
                    f"{origin_error or 'origin URL changed'}", err,
                )
            post_ready_remote = _external_or_block(
                [trusted_git, "-C", str(repo), "ls-remote", "--heads", "origin",
                 f"refs/heads/{branch}"], repo=repo, env=env, err=err,
            )
            if post_ready_remote is None:
                return 1
            ready_remote = [
                line.split()[0] for line in post_ready_remote.stdout.splitlines()
                if line.strip()
            ]
            if ready_remote != [head]:
                return _publish_block("remote branch moved after PR readiness", err)
        out.write(f"PR updated and ready: {pr_url}\n")
        return _observe_required_ci(
            pr_url, trusted_gh=trusted_gh, repo=repo, env=env, out=out, err=err
        )

    create_result = _external_or_block(
        [trusted_gh, "pr", "create", "--base", base, "--head", branch,
         "--title", title, "--body-file", str(body_file)],
        repo=repo, env=env, err=err,
    )
    if create_result is None:
        return 1
    url = create_result.stdout.strip()
    if not url:
        return _publish_block("gh pr create returned no pull request URL", err)
    if git_text(repo, "rev-parse", "HEAD") != head:
        return _publish_block("live HEAD moved after PR creation", err)
    current_origin, origin_error = _publish_origin_state(repo, branch)
    if origin_error or current_origin != origin_url:
        return _publish_block(
            f"publication identity changed after PR creation: "
            f"{origin_error or 'origin URL changed'}", err,
        )
    post_create_remote = _external_or_block(
        [trusted_git, "-C", str(repo), "ls-remote", "--heads", "origin",
         f"refs/heads/{branch}"], repo=repo, env=env, err=err,
    )
    if post_create_remote is None:
        return 1
    created_remote = [
        line.split()[0] for line in post_create_remote.stdout.splitlines() if line.strip()
    ]
    if created_remote != [head]:
        return _publish_block("remote branch moved after PR creation", err)
    out.write(f"Published PR: {url}\n")
    return _observe_required_ci(
        url, trusted_gh=trusted_gh, repo=repo, env=env, out=out, err=err
    )


__all__ = [name for name in globals() if not name.startswith("__")]
