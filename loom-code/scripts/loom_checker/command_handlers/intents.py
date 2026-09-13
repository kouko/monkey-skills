from __future__ import annotations

from loom_checker.helpers import UsageError
from loom_checker.helpers import artifact_path
from loom_checker.helpers import git_maybe
from loom_checker.helpers import load_manifest
from loom_checker.helpers import read_text
from loom_checker.helpers import repo_root
from loom_checker.intent_state import CHANGE_ID
from loom_checker.intent_state import REMOTE_NAME
from loom_checker.intent_state import STATUS
from loom_checker.intent_state import intent_delivery_state
from loom_checker.intent_state import remote_default_snapshot
from loom_checker.parsing import parse_document
from pathlib import Path
import re
import sys


def _intent_delivery_metadata(
    repo: Path, change_id: str, remote: str, manifest: dict
) -> list[str]:
    """Optional repository-only metadata for the commit that added the witness."""
    default_ref, snapshot, _ = remote_default_snapshot(repo, remote)
    if default_ref is None or snapshot is None:
        return []
    attestation_rel = artifact_path(manifest, "attestation", change_id, repo).relative_to(repo)
    # `--diff-filter=A` selects an added path, while `%cI` is strictly the
    # committer date rather than a merge timestamp:
    # https://git-scm.com/docs/git-diff#Documentation/git-diff.txt---diff-filterACDMRTUXB82308203
    # https://git-scm.com/docs/pretty-formats.html
    # https://git-scm.com/docs/git-log#Documentation/git-log.txt---first-parent
    history = git_maybe(
        repo,
        "log",
        "--first-parent",
        "--diff-filter=A",
        "--format=%H%x09%cI%x09%s",
        snapshot,
        "--",
        str(attestation_rel),
    )
    entries = [line for line in (history or "").splitlines() if line.strip()]
    if not entries:
        return []
    commit, committed_at, subject = entries[-1].split("\t", 2)
    fields = [f"commit={commit}"]
    if match := re.search(r"\(#(\d+)\)\s*$", subject):
        fields.append(f"pr=#{match.group(1)}")
    fields.append(f"committed_at={committed_at}")
    return fields


def _parse_intents_args(args: list[str]) -> tuple[str | None, str, bool]:
    change_id: str | None = None
    remote = "origin"
    metadata = False
    rest = list(args)
    while rest:
        token = rest.pop(0)
        if token == "--remote":
            if not rest:
                raise UsageError("--remote needs a name.")
            remote = rest.pop(0)
        elif token == "--metadata":
            metadata = True
        elif change_id is None:
            change_id = token
        else:
            raise UsageError(f"unexpected argument {token!r}.")
    if not REMOTE_NAME.fullmatch(remote):
        raise UsageError(f"remote name {remote!r} is not a safe literal.")
    if change_id is not None and not CHANGE_ID.fullmatch(change_id):
        raise UsageError(f"{change_id!r} is not a valid change-id.")
    if metadata and change_id is None:
        raise UsageError("--metadata requires one change-id.")
    return change_id, remote, metadata


def _confirmed_intent_ids(repo: Path, manifest: dict) -> list[str]:
    template = manifest["artifacts"]["intent"]["path"]
    change_ids: list[str] = []
    for path in sorted(repo.glob(template.replace("<change-id>", "*"))):
        candidate = path.stem
        front, _ = parse_document(read_text(path))
        match = STATUS.fullmatch(front.get("status", "").strip())
        if CHANGE_ID.fullmatch(candidate) and match is not None and match.group(1) is not None:
            change_ids.append(candidate)
    return change_ids


def cmd_intents(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    """List active confirmed intents, or report one intent's derived state."""
    change_id, remote, metadata = _parse_intents_args(args)
    manifest = load_manifest()
    repo = repo_root(Path.cwd())
    if change_id is not None:
        intent_path = artifact_path(manifest, "intent", change_id, repo)
        if not intent_path.is_file():
            raise UsageError(f"no intent file at {intent_path.relative_to(repo)}.")
    change_ids = [change_id] if change_id is not None else _confirmed_intent_ids(repo, manifest)

    rc = 0
    for candidate in change_ids:
        state, detail = intent_delivery_state(repo, candidate, remote=remote, manifest=manifest)
        if change_id is None and state not in {"active", "indeterminate"}:
            continue
        fields = [candidate, state]
        if metadata and state == "delivered":
            fields += _intent_delivery_metadata(repo, candidate, remote, manifest)
        elif change_id is not None and state == "active":
            fields.append(detail)
        elif state == "indeterminate":
            fields.append(detail + "; refresh the selected remote-default ref")
            rc = 1
        out.write("\t".join(fields) + "\n")
    return rc
