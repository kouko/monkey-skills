from __future__ import annotations

from git_exec import run_git
from loom_checker.attestation import ATTESTATION_KEYS
from loom_checker.attestation import ATTESTATION_SCHEMA
from loom_checker.helpers import GIT_TIMEOUT
from loom_checker.helpers import artifact_path
from loom_checker.helpers import git_maybe
from loom_checker.helpers import load_manifest
from loom_checker.helpers import read_text
from loom_checker.parsing import parse_document
from pathlib import Path
import json
import re
import subprocess


CHANGE_ID = re.compile(r"[A-Za-z0-9._-]+")


REMOTE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


_STATUS_CLOSED_ALT = (
    r"closed (\d{4}-\d{2}-\d{2}) — PR #(\d+)"
    r"|closed (\d{4}-\d{2}-\d{2}) — branch ([A-Za-z0-9._/-]+)"
)


STATUS = re.compile(
    r"(?:open"
    r"|confirmed (\d{4}-\d{2}-\d{2})"
    rf"|{_STATUS_CLOSED_ALT}"
    r"|withdrawn — .+)"
    r"(?:\s+#.*)?"
)


STATUS_CLOSED_LITERAL = _STATUS_CLOSED_ALT.split("(", 1)[0]


REOPEN_LOG_PATTERN = rf"^status:[[:space:]]*{STATUS_CLOSED_LITERAL}"


INTAKE_STATIONS = ("write-spec", "write-plan")


def _status_closed_info(match: re.Match) -> tuple[str, str, str] | None:
    """`(date, kind, identifier)` for a `STATUS` match that hit either
    closed alternative -- `kind` is `"PR"` or `"branch"`, `identifier` the
    PR number or the branch name. None when `match` did not hit a closed
    alternative at all (W1-03)."""
    if match.group(2) is not None:
        return match.group(2), "PR", match.group(3)
    if match.group(4) is not None:
        return match.group(4), "branch", match.group(5)
    return None


def _status_closed_descriptor(kind: str, identifier: str) -> str:
    """The human-readable naming of a closed status's identifier -- `PR
    #<n>` or `branch <name>` -- shared by every message that reports a
    closed intent (W1-03)."""
    return f"PR #{identifier}" if kind == "PR" else f"branch {identifier}"


def _status_closed_descriptor_from_text(text: str) -> str | None:
    """The closed-status descriptor (`PR #<n>` or `branch <name>`) from
    `text`'s frontmatter status line, or None when the status is anything
    else (including absent/malformed)."""
    front, _sections = parse_document(text)
    match = STATUS.fullmatch(front.get("status", "").strip())
    if match is None:
        return None
    info = _status_closed_info(match)
    if info is None:
        return None
    _date, kind, identifier = info
    return _status_closed_descriptor(kind, identifier)


def remote_default_snapshot(
    repo: Path, remote: str = "origin"
) -> tuple[str | None, str | None, str]:
    """The immutable commit selected by one remote's local default-branch ref."""
    if not REMOTE_NAME.fullmatch(remote):
        return None, None, f"remote name {remote!r} is not a safe literal"
    head = f"refs/remotes/{remote}/HEAD"
    # `symbolic-ref` follows chained symbolic refs by default and returns a
    # non-zero status when the name is not symbolic:
    # https://git-scm.com/docs/git-symbolic-ref
    target = git_maybe(repo, "symbolic-ref", "--quiet", head)
    prefix = f"refs/remotes/{remote}/"
    if target is None or not target.startswith(prefix) or target == prefix + "HEAD":
        return None, None, f"{head} is missing or does not select a branch on remote {remote!r}"
    commit = git_maybe(repo, "rev-parse", "--verify", f"{target}^{{commit}}")
    if commit is None:
        return None, None, f"{target} does not resolve to a committed snapshot"
    return target, commit, ""


def _committed_text(repo: Path, commit: str, relative: Path) -> tuple[str, str]:
    """Return present text, confirmed absence, or an explicit read error."""
    try:
        listing = run_git(
            repo, "ls-tree", "--name-only", commit, "--", str(relative),
            timeout=GIT_TIMEOUT, check=True,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        return "error", f"cannot read {relative} from remote-default snapshot: {type(exc).__name__}"
    if listing != str(relative):
        return "absent", ""
    try:
        content = run_git(
            repo, "show", f"{commit}:{relative}", timeout=GIT_TIMEOUT, check=True,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        return "error", f"cannot read {relative} from remote-default snapshot: {type(exc).__name__}"
    return "present", content


def _delivery_witness_valid(attestation: object, change_id: str) -> bool:
    """Validate stable witness shape without comparing it to a later tree."""
    if not isinstance(attestation, dict) or set(attestation) != ATTESTATION_KEYS:
        return False
    if attestation.get("schema") != ATTESTATION_SCHEMA or attestation.get("change_id") != change_id:
        return False
    if not isinstance(attestation.get("content_digest"), str) or not attestation["content_digest"].strip():
        return False
    executions = attestation.get("executions")
    verdicts = attestation.get("verdicts")
    if not isinstance(executions, list) or not executions:
        return False
    if not isinstance(verdicts, list) or not verdicts:
        return False
    if not isinstance(attestation.get("findings"), list):
        return False
    execution_fields = {"kind", "command", "artifact", "result", "command_digest"}
    for item in executions:
        if not isinstance(item, dict) or not execution_fields <= set(item):
            return False
        kind = item.get("kind")
        if not isinstance(kind, str) or kind not in {"package-tests", "adversarial"}:
            return False
        if not isinstance(item.get("command"), str) or not item["command"].strip():
            return False
        if not isinstance(item.get("artifact"), str) or item.get("result") != "pass":
            return False
        digest = item.get("command_digest")
        if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            return False
    verdict_fields = {"reviewer", "vendor", "model", "lens", "verdict", "findings"}
    for item in verdicts:
        if not isinstance(item, dict) or not verdict_fields <= set(item):
            return False
        if any(not isinstance(item.get(key), str) or not item[key].strip()
               for key in ("reviewer", "vendor", "model", "lens")):
            return False
        verdict = item.get("verdict")
        if not isinstance(verdict, str) or verdict not in {"PASS", "PASS_WITH_NOTES"}:
            return False
        if not isinstance(item.get("findings"), list):
            return False
    return all(_delivery_finding_valid(finding) for finding in attestation["findings"])


def _delivery_finding_valid(finding: object) -> bool:
    """Accept the two complete finding carriers emitted under schema v1."""
    if not isinstance(finding, dict):
        return False
    resolved = ("id", "anchor", "raised_by", "resolution")
    review_note = ("severity", "dimension", "anchor", "text")
    for shape in (resolved, review_note):
        if all(isinstance(finding.get(key), str) and finding[key].strip() for key in shape):
            return True
    return False


def intent_delivery_state(
    repo: Path, change_id: str, *, remote: str = "origin", manifest: dict | None = None
) -> tuple[str, str]:
    """Return active, delivered, closed, or indeterminate from repository evidence."""
    contract = manifest if manifest is not None else load_manifest()
    intent_path = artifact_path(contract, "intent", change_id, repo)
    if intent_path.is_file():
        descriptor = _status_closed_descriptor_from_text(read_text(intent_path))
        if descriptor is not None:
            return "closed", descriptor

    default_ref, snapshot, error = remote_default_snapshot(repo, remote)
    if default_ref is None or snapshot is None:
        return "indeterminate", error

    intent_rel = artifact_path(contract, "intent", change_id, repo).relative_to(repo)
    intent_read, remote_intent = _committed_text(repo, snapshot, intent_rel)
    if intent_read == "error":
        return "indeterminate", remote_intent
    if intent_read == "absent":
        return "active", "canonical intent is absent from the remote-default snapshot"
    descriptor = _status_closed_descriptor_from_text(remote_intent)
    if descriptor is not None:
        return "closed", descriptor
    remote_front, _ = parse_document(remote_intent)
    remote_status = STATUS.fullmatch(remote_front.get("status", "").strip())
    if remote_status is None or remote_status.group(1) is None:
        return "active", "canonical remote-default intent is not confirmed"

    attestation_rel = artifact_path(contract, "attestation", change_id, repo).relative_to(repo)
    attestation_read, raw_attestation = _committed_text(repo, snapshot, attestation_rel)
    if attestation_read == "error":
        return "indeterminate", raw_attestation
    if attestation_read == "absent":
        return "active", "canonical attestation is absent from the remote-default snapshot"
    try:
        attestation = json.loads(raw_attestation)
    except json.JSONDecodeError:
        return "active", "canonical attestation is malformed JSON"
    if not _delivery_witness_valid(attestation, change_id):
        return "active", "canonical attestation has an unsupported or incomplete witness shape"
    return "delivered", default_ref


def check_intent_not_reopened(repo: Path, intent_path: Path, change_id: str) -> tuple[str, str] | None:
    """Catch a legacy close in this branch's own history after a local reopen."""
    intent_rel = intent_path.relative_to(repo)
    log_output = git_maybe(repo, "log", "--format=%H", f"-G{REOPEN_LOG_PATTERN}", "--", str(intent_rel))
    for commit in (log_output or "").splitlines():
        commit = commit.strip()
        if not commit:
            continue
        content = git_maybe(repo, "show", f"{commit}:{intent_rel}")
        if content is None:
            continue
        descriptor = _status_closed_descriptor_from_text(content)
        if descriptor is not None:
            return (
                "intake.confirmed",
                f"{change_id} was closed ({descriptor}) and closed intents "
                "are not reopened; start a new intent",
            )

    return None
