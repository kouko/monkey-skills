#!/usr/bin/env python3
"""Freeze and verify a skill-package baseline exported from Git."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile


PACKAGE_VERDICTS = frozenset({"PASS", "FAIL", "UNGRADABLE"})
_CHEAP_LAYERS = ("resource", "owning-skill", "package")
_DUAL_HOSTS = ("claude", "codex")


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ("git", "-C", str(repo), *args),
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _resolved_commit(repo: Path, revision: str) -> str:
    result = subprocess.run(
        ("git", "-C", str(repo), "rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}"),
        check=False,
        capture_output=True,
        text=True,
    )
    commit = result.stdout.strip()
    if result.returncode or len(commit) != 40:
        raise ValueError(f"invalid Git revision: {revision}")
    return commit


def _skill_path(skill_path: str) -> PurePosixPath:
    path = PurePosixPath(skill_path)
    if path.is_absolute() or not skill_path or ".." in path.parts:
        raise ValueError(f"invalid skill path: {skill_path}")
    return path


def _file_snapshot(
    root: Path,
) -> tuple[dict[str, bytes], dict[str, dict[str, object]]]:
    if not root.is_dir() or root.is_symlink():
        raise ValueError(f"invalid package root: {root}")

    contents: dict[str, bytes] = {}
    files: dict[str, dict[str, object]] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"package contains symlink: {path.relative_to(root)}")
        if path.is_file():
            relative = str(path.relative_to(root))
            with path.open("rb") as stream:
                before = os.fstat(stream.fileno())
                content = stream.read()
                after = os.fstat(stream.fileno())
            if (before.st_size, before.st_mtime_ns, before.st_mode) != (
                after.st_size,
                after.st_mtime_ns,
                after.st_mode,
            ):
                raise ValueError(f"package file changed while reading: {relative}")
            contents[relative] = content
            files[relative] = {
                "sha256": hashlib.sha256(content).hexdigest(),
                "executable": bool(after.st_mode & 0o111),
            }
    return contents, files


def _file_hashes(root: Path) -> dict[str, dict[str, object]]:
    return _file_snapshot(root)[1]


def _file_contents(root: Path) -> dict[str, bytes]:
    return _file_snapshot(root)[0]


def _counts(contents: dict[str, bytes]) -> dict[str, int]:
    return {
        "words": sum(len(content.decode("utf-8", errors="replace").split()) for content in contents.values()),
        "bytes": sum(len(content) for content in contents.values()),
    }


def _delta(baseline: int, candidate: int) -> dict[str, int]:
    return {"baseline": baseline, "candidate": candidate, "delta": candidate - baseline}


def _extract_skill(archive: bytes, destination: Path) -> None:
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as tar:
        members = tar.getmembers()
        for member in members:
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or member.issym() or member.islnk():
                raise ValueError(f"unsafe baseline archive member: {member.name}")
            if not (member.isdir() or member.isfile()):
                raise ValueError(f"unsupported baseline archive member: {member.name}")
        tar.extractall(destination, members=members, filter="data")


def _archive_file_hashes(archive: bytes) -> dict[str, dict[str, object]]:
    """Fingerprint regular files directly from a trusted Git archive."""
    files: dict[str, dict[str, object]] = {}
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as tar:
        for member in tar.getmembers():
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or member.issym() or member.islnk():
                raise ValueError(f"unsafe baseline archive member: {member.name}")
            if member.isdir():
                continue
            if not member.isfile():
                raise ValueError(f"unsupported baseline archive member: {member.name}")
            stream = tar.extractfile(member)
            if stream is None:
                raise ValueError(f"unreadable baseline archive member: {member.name}")
            files[path.as_posix()] = {
                "sha256": hashlib.sha256(stream.read()).hexdigest(),
                "executable": bool(member.mode & 0o111),
            }
    return files


def export_baseline(repo: Path, workspace: Path, skill_path: str, revision: str) -> Path:
    """Export one skill from *revision* and return its immutable manifest path."""
    relative_path = _skill_path(skill_path)
    commit = _resolved_commit(repo, revision)
    tree = _git(repo, "rev-parse", f"{commit}:{relative_path.as_posix()}")
    _git(repo, "cat-file", "-e", f"{commit}:{relative_path.as_posix()}/SKILL.md")

    baseline = workspace / "baseline"
    manifest_path = baseline / "manifest.json"
    skill_root = baseline / "skill"
    if manifest_path.exists() or skill_root.exists():
        raise ValueError("baseline already exists; refusing to replace it")

    archive = subprocess.run(
        ("git", "-C", str(repo), "archive", "--format=tar", f"{commit}:{relative_path.as_posix()}"),
        check=True,
        capture_output=True,
    ).stdout
    baseline.mkdir(parents=True)
    try:
        _extract_skill(archive, skill_root)
        manifest = {
            "repository": str(repo.resolve()),
            "skill_path": relative_path.as_posix(),
            "resolved_commit": commit,
            "skill_tree": tree,
            "files": _file_hashes(skill_root),
        }
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except Exception:
        if skill_root.exists():
            for path in sorted(skill_root.rglob("*"), reverse=True):
                if path.is_file() or path.is_symlink():
                    path.unlink()
                elif path.is_dir():
                    path.rmdir()
            skill_root.rmdir()
        raise
    return manifest_path.resolve()


def _verified_baseline_snapshot(
    manifest_path: Path, manifest_sha256: str
) -> tuple[
    dict[str, bytes] | None,
    dict[str, dict[str, object]] | None,
    dict[str, str],
]:
    try:
        if not manifest_path.is_absolute() or manifest_path.resolve() != manifest_path:
            return None, None, {
                "verdict": "REFUSED",
                "reason": "manifest path is not canonical",
            }
        manifest_bytes = manifest_path.read_bytes()
        if hashlib.sha256(manifest_bytes).hexdigest() != manifest_sha256:
            return None, None, {
                "verdict": "REFUSED",
                "reason": "manifest digest mismatch",
            }
        manifest = json.loads(manifest_bytes.decode("utf-8"))
        repository = manifest["repository"]
        skill_path = manifest["skill_path"]
        commit = manifest["resolved_commit"]
        tree = manifest["skill_tree"]
        expected = manifest["files"]
        if (
            not isinstance(repository, str)
            or not isinstance(skill_path, str)
            or not isinstance(commit, str)
            or not isinstance(tree, str)
            or not isinstance(expected, dict)
            or not all(
            isinstance(path, str)
            and isinstance(fingerprint, dict)
            and set(fingerprint) == {"sha256", "executable"}
            and isinstance(fingerprint["sha256"], str)
            and isinstance(fingerprint["executable"], bool)
            for path, fingerprint in expected.items()
            )
        ):
            raise ValueError("invalid file fingerprint manifest")
        repo = Path(repository)
        relative_path = _skill_path(skill_path)
        if _resolved_commit(repo, commit) != commit:
            raise ValueError("resolved commit no longer matches Git")
        if _git(repo, "rev-parse", f"{commit}:{relative_path.as_posix()}") != tree:
            raise ValueError("skill tree no longer matches Git")
        archive = subprocess.run(
            ("git", "-C", str(repo), "archive", "--format=tar", f"{commit}:{relative_path.as_posix()}"),
            check=True,
            capture_output=True,
        ).stdout
        git_expected = _archive_file_hashes(archive)
        actual_contents, actual = _file_snapshot(manifest_path.parent / "skill")
    except (OSError, ValueError, json.JSONDecodeError, KeyError, subprocess.CalledProcessError) as error:
        return None, None, {
            "verdict": "REFUSED",
            "reason": f"baseline verification failed: {error}",
        }

    if git_expected != expected:
        return None, None, {
            "verdict": "REFUSED",
            "reason": "Git baseline drift detected",
        }
    if actual != expected:
        return None, None, {
            "verdict": "REFUSED",
            "reason": "baseline drift detected",
        }
    return actual_contents, actual, {
        "verdict": "PASS",
        "reason": "baseline matches manifest",
    }


def verify_baseline(manifest_path: Path, manifest_sha256: str) -> dict[str, str]:
    """Return PASS when exported bytes match the manifest, otherwise REFUSED."""
    return _verified_baseline_snapshot(manifest_path, manifest_sha256)[2]


def account_package(
    manifest_path: Path,
    manifest_sha256: str,
    candidate_root: Path,
    target_file: str,
) -> dict[str, object]:
    """Report target and whole-package word/byte deltas from a verified baseline."""
    baseline_files, baseline_fingerprints, verification = _verified_baseline_snapshot(
        manifest_path, manifest_sha256
    )
    if verification["verdict"] != "PASS":
        return verification

    try:
        target = _skill_path(target_file).as_posix()
        if baseline_files is None or baseline_fingerprints is None:
            raise ValueError("verified baseline snapshot is unavailable")
        candidate_files, candidate_fingerprints = _file_snapshot(candidate_root)
        baseline_target = baseline_files[target]
        candidate_target = candidate_files[target]
    except (KeyError, OSError, ValueError) as error:
        return {"verdict": "REFUSED", "reason": f"package accounting failed: {error}"}

    mode_drift = sorted(
        path
        for path in baseline_fingerprints.keys() & candidate_fingerprints.keys()
        if baseline_fingerprints[path]["executable"]
        != candidate_fingerprints[path]["executable"]
    )
    if mode_drift:
        return {
            "verdict": "REFUSED",
            "reason": f"candidate executable mode drift detected: {', '.join(mode_drift)}",
        }

    baseline_counts = _counts(baseline_files)
    candidate_counts = _counts(candidate_files)
    baseline_target_counts = _counts({target: baseline_target})
    candidate_target_counts = _counts({target: candidate_target})
    return {
        "verdict": "PASS",
        "target": {
            "words": _delta(baseline_target_counts["words"], candidate_target_counts["words"]),
            "bytes": _delta(baseline_target_counts["bytes"], candidate_target_counts["bytes"]),
        },
        "package": {
            "words": _delta(baseline_counts["words"], candidate_counts["words"]),
            "bytes": _delta(baseline_counts["bytes"], candidate_counts["bytes"]),
        },
    }


def _ungradeable(reason: str, accounting: object = None) -> dict[str, object]:
    """Return only package-mode verdicts, including malformed evidence."""
    result: dict[str, object] = {"verdict": "UNGRADABLE", "reason": reason}
    if accounting is not None:
        result["accounting"] = accounting
    return result


def _layer_verdict(records: object) -> str:
    if not isinstance(records, list) or not records:
        raise ValueError("layer needs at least one verdict record")
    verdicts = []
    for record in records:
        if not isinstance(record, dict) or set(record) != {"verdict"}:
            raise ValueError("layer record must contain only verdict")
        verdict = record["verdict"]
        if verdict not in PACKAGE_VERDICTS:
            raise ValueError("layer record has an invalid verdict")
        verdicts.append(verdict)
    if "UNGRADABLE" in verdicts:
        return "UNGRADABLE"
    return "FAIL" if "FAIL" in verdicts else "PASS"


def _normalize_host_evidence(records: object) -> list[dict[str, object]]:
    if not isinstance(records, list):
        raise ValueError("host_evidence must be a list")
    normalized = []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("host evidence must be an object")
        expected = {"host", "replicate"}
        if not expected <= set(record) or not set(record) <= expected | {"verdict", "error"}:
            raise ValueError("host evidence has an invalid schema")
        host, replicate = record["host"], record["replicate"]
        if host not in _DUAL_HOSTS or not isinstance(replicate, int) or isinstance(replicate, bool) or replicate < 0:
            raise ValueError("host evidence has an invalid host or replicate")
        if "error" in record:
            if not isinstance(record["error"], str) or not record["error"]:
                raise ValueError("host error must be a non-empty string")
            normalized.append({"host": host, "replicate": replicate, "verdict": "UNGRADABLE", "error": record["error"]})
            continue
        if set(record) != expected | {"verdict"} or record["verdict"] not in PACKAGE_VERDICTS:
            raise ValueError("host evidence must contain one closed verdict or an error")
        normalized.append({"host": host, "replicate": replicate, "verdict": record["verdict"]})
    return normalized


def reduce_package_evidence(evidence: object, *, dual_host: bool = False) -> dict[str, object]:
    """Reduce normalized package evidence without invoking a host.

    The input boundary is intentionally closed: adapters must normalize their
    observations into the documented layer and host records before this pure
    reducer sees them.  This keeps host invocation and paid replay outside the
    package gate while making malformed or failed host evidence non-passing.
    """
    if not isinstance(evidence, dict):
        return _ungradeable("evidence must be an object")
    expected = {"accounting", *_CHEAP_LAYERS, "host_evidence"}
    accounting = evidence.get("accounting")
    if set(evidence) != expected:
        return _ungradeable("evidence has an invalid schema", accounting)
    if not isinstance(accounting, dict) or accounting.get("verdict") != "PASS":
        return _ungradeable("accounting must be a passing report", accounting)

    try:
        layers = [
            {"layer": layer, "verdict": _layer_verdict(evidence[layer])}
            for layer in _CHEAP_LAYERS
        ]
    except ValueError as error:
        return _ungradeable(str(error), accounting)
    layers[-1]["accounting"] = accounting

    cheap_verdicts = [layer["verdict"] for layer in layers]
    if "UNGRADABLE" in cheap_verdicts:
        return {"verdict": "UNGRADABLE", "layers": layers, "host_evidence": []}
    if "FAIL" in cheap_verdicts:
        return {"verdict": "FAIL", "layers": layers, "host_evidence": []}

    try:
        hosts = _normalize_host_evidence(evidence["host_evidence"])
    except ValueError as error:
        return _ungradeable(str(error), accounting)
    if any(record["verdict"] == "UNGRADABLE" for record in hosts):
        verdict = "UNGRADABLE"
    elif dual_host and any(
        len({record["replicate"] for record in hosts if record["host"] == host}) < 2
        for host in _DUAL_HOSTS
    ):
        verdict = "UNGRADABLE"
    elif any(record["verdict"] == "FAIL" for record in hosts):
        verdict = "FAIL"
    else:
        verdict = "PASS"
    return {"verdict": verdict, "layers": layers, "host_evidence": hosts}


def _cli_result(result: dict[str, object]) -> dict[str, object]:
    """Keep the CLI boundary within the package-mode verdict vocabulary."""
    if result.get("verdict") == "REFUSED":
        result = {**result, "verdict": "UNGRADABLE"}
    return result


def main(argv: list[str] | None = None) -> int:
    """Expose package-gate APIs as one JSON stdin/stdout CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    export = commands.add_parser("export")
    export.add_argument("--repo", required=True)
    export.add_argument("--workspace", required=True)
    export.add_argument("--skill-path", required=True)
    export.add_argument("--revision", required=True)

    verify = commands.add_parser("verify")
    verify.add_argument("--manifest", required=True)
    verify.add_argument("--manifest-sha256", required=True)

    account = commands.add_parser("account")
    account.add_argument("--manifest", required=True)
    account.add_argument("--manifest-sha256", required=True)
    account.add_argument("--candidate-root", required=True)
    account.add_argument("--target-file", required=True)

    reduce = commands.add_parser("reduce")
    reduce.add_argument("--dual-host", action="store_true")

    args = parser.parse_args(argv)
    try:
        if args.command == "export":
            manifest_path = export_baseline(
                Path(args.repo), Path(args.workspace), args.skill_path, args.revision
            )
            result: dict[str, object] = {
                "verdict": "PASS",
                "manifest": str(manifest_path),
                "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            }
        elif args.command == "verify":
            result = verify_baseline(Path(args.manifest), args.manifest_sha256)
        elif args.command == "account":
            result = account_package(
                Path(args.manifest),
                args.manifest_sha256,
                Path(args.candidate_root),
                args.target_file,
            )
        else:
            result = reduce_package_evidence(json.load(sys.stdin), dual_host=args.dual_host)
    except (OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        result = {"verdict": "UNGRADABLE", "reason": str(error)}

    print(json.dumps(_cli_result(result), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
