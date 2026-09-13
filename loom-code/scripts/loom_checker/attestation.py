from __future__ import annotations

from loom_checker.digest import functional_content_digest
from loom_checker.helpers import git_ok
from loom_checker.probes import command_executes_artifact
from loom_checker.probes import command_names_artifact
from loom_checker.probes import declared_test_command
from loom_checker.reviewers import required_reviewer_count
from pathlib import Path
import hashlib


ATTESTATION_SCHEMA = "loom-attestation/v1"


ATTESTATION_KEYS = {
    "schema", "change_id", "content_digest", "executions", "verdicts", "findings"
}


def _command_digest(command: str) -> str:
    return hashlib.sha256(command.encode("utf-8")).hexdigest()


def validate_attestation(
    repo: Path, head_sha: str, change_id: str, attestation: object,
    manifest: dict | None = None,
) -> list[tuple[str, str]]:
    """Validate generated evidence without executing the recorded programs."""
    rule = "push.attestation"
    if not isinstance(attestation, dict) or set(attestation) != ATTESTATION_KEYS:
        return [(rule, "attestation has an unknown or incomplete schema")]
    if attestation.get("schema") != ATTESTATION_SCHEMA:
        return [(rule, f"unsupported attestation schema {attestation.get('schema')!r}")]
    if attestation.get("change_id") != change_id:
        return [(rule, "attestation change_id does not match its path")]
    expected = functional_content_digest(repo, head_sha, change_id, manifest)
    if expected is None or attestation.get("content_digest") != expected:
        return [(rule, "attestation functional content digest does not match the selected tree")]

    executions = attestation.get("executions")
    if not isinstance(executions, list) or not executions:
        return [(rule, "attestation records no successful functional executions")]
    package_runs = 0
    adversarial_runs = 0
    for execution in executions:
        if not isinstance(execution, dict):
            return [(rule, "attestation contains a malformed execution")]
        command = execution.get("command")
        if not isinstance(command, str) or not command.strip():
            return [(rule, "attestation execution has no command")]
        if execution.get("command_digest") != _command_digest(command):
            return [(rule, "attestation execution command digest is forged or corrupted")]
        if execution.get("result") != "pass":
            return [(rule, "attestation contains a non-passing execution")]
        if execution.get("kind") == "package-tests":
            package_runs += 1
            declared, _ = declared_test_command(repo)
            if command != declared:
                return [(rule, "package-tests execution does not match the declared package command")]
        elif execution.get("kind") == "adversarial":
            adversarial_runs += 1
            artifact = execution.get("artifact")
            if not isinstance(artifact, str) or not artifact.strip():
                return [(rule, "adversarial execution names no artifact")]
            if not command_names_artifact(command, artifact):
                return [(rule, "adversarial command does not name its artifact")]
            if not command_executes_artifact(command, artifact):
                return [(rule, "adversarial command must execute the artifact directly")]
            if not git_ok(repo, "cat-file", "-e", f"{head_sha}:{artifact}"):
                return [(rule, "adversarial execution names no committed artifact")]
        else:
            return [(rule, "attestation contains an unknown execution kind")]
    if package_runs != 1:
        return [(rule, "attestation must record exactly one package-tests execution")]
    if adversarial_runs < 1:
        return [(rule, "attestation records no adversarial execution")]

    verdicts = attestation.get("verdicts")
    if not isinstance(verdicts, list) or not verdicts:
        return [(rule, "attestation records no reviewer verdict")]
    reviewers = {str(v.get("reviewer", "")).strip() for v in verdicts if isinstance(v, dict)}
    reviewers.discard("")
    reviewer_floor = required_reviewer_count(repo, change_id, head_sha)
    if len(reviewers) < reviewer_floor:
        needed = "two" if reviewer_floor == 2 else "one"
        return [(rule, f"attestation needs {needed} distinct reviewers")]
    for verdict in verdicts:
        if not isinstance(verdict, dict) or verdict.get("verdict") not in {
            "PASS", "PASS_WITH_NOTES"
        }:
            return [(rule, "attestation contains a malformed or non-passing reviewer verdict")]
    if not isinstance(attestation.get("findings"), list):
        return [(rule, "attestation findings must be a list")]
    return []
