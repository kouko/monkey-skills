from __future__ import annotations

from loom_checker.attestation import ATTESTATION_SCHEMA
from loom_checker.attestation import _command_digest
from loom_checker.digest import functional_content_digest
from loom_checker.helpers import UsageError
from loom_checker.helpers import artifact_path
from loom_checker.helpers import git_ok
from loom_checker.helpers import git_text
from loom_checker.helpers import load_manifest
from loom_checker.helpers import read_text
from loom_checker.helpers import repo_root
from loom_checker.helpers import report
from loom_checker.probes import NO_PACKAGE_TESTS
from loom_checker.probes import PROBE_RUN_TIMEOUT
from loom_checker.probes import argv_for
from loom_checker.probes import command_executes_artifact
from loom_checker.probes import command_names_artifact
from loom_checker.probes import declared_test_command
from loom_checker.reviewers import required_reviewer_count
from pathlib import Path
import json
import subprocess
import sys
import tempfile


def cmd_finalize_review(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    """Run functional verification once and generate content-bound evidence."""
    if not args:
        raise UsageError("finalize-review needs a change-id.")
    change_id, *rest = args
    if len(rest) != 2 or rest[0] != "--input":
        raise UsageError("finalize-review expects `--input <review-input.json>`.")
    input_path = Path(rest[1])
    try:
        review_input = json.loads(read_text(input_path))
    except (OSError, json.JSONDecodeError) as exc:
        raise UsageError(f"cannot read review input: {exc}") from exc
    if not isinstance(review_input, dict):
        raise UsageError("review input must be a JSON object.")
    repo = repo_root(Path.cwd())
    head_sha = git_text(repo, "rev-parse", "HEAD")
    status_before = git_text(repo, "status", "--porcelain")
    if status_before:
        return report([("finalize.clean-tree", "commit functional content before finalizing review")], err)
    verdicts = review_input.get("verdicts")
    findings = review_input.get("findings", [])
    adversarial = review_input.get("adversarial", [])
    if not isinstance(verdicts, list) or not verdicts:
        return report([("finalize.verdicts", "review input has no verdicts")], err)
    if any(not isinstance(v, dict) or v.get("verdict") not in {
        "PASS", "PASS_WITH_NOTES"
    } for v in verdicts):
        return report([("finalize.verdicts", "every reviewer verdict must pass")], err)
    reviewers = {str(v.get("reviewer", "")).strip() for v in verdicts}
    reviewers.discard("")
    reviewer_floor = required_reviewer_count(repo, change_id, head_sha)
    if len(reviewers) < reviewer_floor:
        needed = "two" if reviewer_floor == 2 else "one"
        return report(
            [("finalize.verdicts", f"{needed} distinct reviewers are required")],
            err,
        )
    if not isinstance(findings, list) or not isinstance(adversarial, list):
        return report([("finalize.schema", "findings and adversarial must be lists")], err)
    if not adversarial:
        return report([("finalize.adversarial", "at least one adversarial artifact is required")], err)

    manifest = load_manifest()
    config_before = git_text(repo, "config", "--list", "--null")
    package_command, source = declared_test_command(repo)
    if package_command is None or package_command.strip().lower() == NO_PACKAGE_TESTS:
        return report([("finalize.package-tests", f"no executable package command ({source})")], err)
    work: list[tuple[str, str, str]] = [("package-tests", package_command, "")]
    for item in adversarial:
        if not isinstance(item, dict):
            return report([("finalize.adversarial", "malformed adversarial input")], err)
        command = str(item.get("command", "")).strip()
        artifact = str(item.get("artifact", "")).strip()
        if not command or not artifact:
            return report([("finalize.adversarial", "adversarial input needs command and artifact")], err)
        if not command_names_artifact(command, artifact):
            return report([("finalize.adversarial", "command must name its artifact argument")], err)
        if not command_executes_artifact(command, artifact):
            return report([("finalize.adversarial", "command must execute the artifact directly")], err)
        if not git_ok(repo, "cat-file", "-e", f"{head_sha}:{artifact}"):
            return report([("finalize.adversarial", "artifact must exist in the selected commit")], err)
        work.append(("adversarial", command, artifact))

    executions: list[dict] = []
    for kind, command, artifact in work:
        try:
            completed = subprocess.run(
                argv_for(command), cwd=str(repo), capture_output=True, text=True,
                timeout=PROBE_RUN_TIMEOUT,
            )
        except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
            return report([(f"finalize.{kind}", f"execution failed: {exc}")], err)
        if completed.returncode != 0:
            detail = (completed.stdout + completed.stderr).strip()
            suffix = f"\n{detail[-4000:]}" if detail else ""
            return report([(
                f"finalize.{kind}",
                f"`{command}` exited {completed.returncode}{suffix}",
            )], err)
        executions.append({
            "kind": kind, "command": command, "artifact": artifact,
            "result": "pass", "command_digest": _command_digest(command),
        })

    if git_text(repo, "rev-parse", "HEAD") != head_sha:
        return report([("finalize.stable-tree", "HEAD moved during functional verification")], err)
    if git_text(repo, "status", "--porcelain") != status_before:
        return report([("finalize.stable-tree", "working tree or index changed during functional verification")], err)
    if git_text(repo, "config", "--list", "--null") != config_before:
        return report([("finalize.stable-tree", "git configuration changed during functional verification")], err)

    digest = functional_content_digest(repo, head_sha, change_id, manifest)
    if digest is None:
        return report([("finalize.digest", "cannot compute functional content digest")], err)
    attestation = {
        "schema": ATTESTATION_SCHEMA, "change_id": change_id,
        "content_digest": digest, "executions": executions,
        "verdicts": verdicts, "findings": findings,
    }
    target = artifact_path(manifest, "attestation", change_id, repo)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=target.parent, prefix=f".{target.name}.", delete=False,
    ) as handle:
        json.dump(attestation, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(target)
    out.write(f"wrote {target.relative_to(repo)} for {digest}\n")
    return 0
