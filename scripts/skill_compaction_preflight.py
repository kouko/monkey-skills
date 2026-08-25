#!/usr/bin/env python3
"""Validate compaction corpora and freeze an immutable dual-host baseline."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "loom-code" / "scripts"))

from loom_firing_harness import (
    HostInvocation,
    _prepare_codex_root,
    grade_record,
    host_argv_for_root,
)


TARGETS = (
    "brainstorming", "dispatching-parallel-agents",
    "finishing-a-development-branch", "loom-memory",
    "requesting-code-review", "requesting-docs-review",
    "systematic-debugging", "tdd-iron-law", "ui-verification",
    "using-git-worktrees", "using-loom-code",
    "verification-before-completion", "writing-plans",
)
CATEGORIES = {"happy-path", "edge-case", "stress"}
CORPUS_FIELDS = {"skill_name", "schema_version", "created", "last_reviewed", "prompts"}
PROMPT_FIELDS = {"id", "category", "prompt", "expected_behavior", "edge_case_dimensions"}
LINK_RE = re.compile(r"\[[^]\n]+\]\(([^)\n]+)\)")
INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
PATH_RE = re.compile(
    r"^(?:\.\.?/)?(?:[A-Za-z0-9_$<>{}.-]+/)*"
    r"[A-Za-z0-9_$<>{}.-]+\.(?:md|py|json|sh|js|toml|ya?ml)$"
)


@dataclass(frozen=True)
class RunOutcome:
    raw: str
    exit_code: int
    status: str


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def _frontmatter(text: str) -> dict[str, object]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md has no YAML frontmatter")
    block = text.split("---\n", 2)[1]
    result: dict[str, object] = {}
    key = None
    for line in block.splitlines():
        if line.startswith("  ") and key == "description":
            result[key] = f"{result[key]}\n{line.strip()}".strip()
        elif ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            result[key] = value.strip() if value.strip() != "|" else ""
    return result


def validate_corpus(path: Path, skill_name: str) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != CORPUS_FIELDS:
        raise ValueError(f"{path}: top-level fields violate schema")
    if data.get("skill_name") != skill_name or data.get("schema_version") != 1:
        raise ValueError(f"{path}: skill_name/schema_version mismatch")
    prompts = data.get("prompts")
    if not isinstance(prompts, list) or len(prompts) < 3:
        raise ValueError(f"{path}: at least three prompts required")
    if any(not isinstance(p, dict) for p in prompts):
        raise ValueError(f"{path}: every prompt must be an object")
    categories = {p.get("category") for p in prompts}
    if not CATEGORIES <= categories or not categories <= CATEGORIES:
        raise ValueError(f"{path}: happy-path, edge-case, stress required")
    for index, prompt in enumerate(prompts, 1):
        if set(prompt) != PROMPT_FIELDS or prompt["id"] != index:
            raise ValueError(f"{path}: prompt {index} violates schema")
        if not all(isinstance(prompt[k], str) and prompt[k].strip() for k in ("prompt", "expected_behavior")):
            raise ValueError(f"{path}: prompt {index} has blank text")
        dimensions = prompt["edge_case_dimensions"]
        if not isinstance(dimensions, list) or any(
            not isinstance(item, str) or not item.strip() for item in dimensions
        ):
            raise ValueError(f"{path}: prompt {index} dimensions must be strings")
    return data


def extract_dependencies(text: str) -> list[str]:
    dependencies = set()
    for target in LINK_RE.findall(text):
        target = target.split("#", 1)[0]
        if target and not re.match(r"^[a-z]+://", target):
            dependencies.add(target)
    for token in INLINE_CODE_RE.findall(text):
        if PATH_RE.fullmatch(token):
            dependencies.add(token)
    return sorted(dependencies)


def snapshot_skill(skill_dir: Path) -> dict:
    skill_file = skill_dir / "SKILL.md"
    text = skill_file.read_text(encoding="utf-8")
    frontmatter = _frontmatter(text)
    dependencies = extract_dependencies(text)
    files = sorted(
        str(path.relative_to(skill_dir)) + ("/" if path.is_dir() else "")
        for path in skill_dir.rglob("*")
    )
    return {
        "word_count": int(subprocess.run(
            ("wc", "-w", str(skill_file)), check=True,
            capture_output=True, text=True,
        ).stdout.split()[0]),
        "frontmatter": frontmatter,
        "declared_dependencies": dependencies,
        "file_structure": files,
        "skill_sha256": hashlib.sha256(text.encode()).hexdigest(),
    }


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ("git", "-C", str(repo), *args), check=True, capture_output=True, text=True
    ).stdout.strip()


def _content_manifest(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): sha256_bytes(path.read_bytes())
        for path in root.rglob("*") if path.is_file()
    }


def export_baseline(
    repo: Path, workspace: Path, baseline_commit: str | None = None
) -> tuple[Path, str, str]:
    commit = _git(repo, "rev-parse", baseline_commit or "HEAD")
    tree = _git(repo, "rev-parse", f"{commit}:loom-code")
    root = workspace / "baseline" / "loom-code"
    archive = subprocess.run(
        ("git", "-C", str(repo), "archive", "--format=tar", commit, "loom-code"),
        check=True, capture_output=True,
    ).stdout
    if not root.is_dir():
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as tar:
            tar.extractall(workspace / "baseline", filter="data")
    else:
        with tempfile.TemporaryDirectory(prefix="loom-preflight-verify-") as temp:
            fresh = Path(temp)
            with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as tar:
                tar.extractall(fresh, filter="data")
            if _content_manifest(root) != _content_manifest(fresh / "loom-code"):
                raise ValueError("existing baseline root does not match baseline commit")
    for path in root.rglob("*"):
        try:
            path.chmod(path.stat().st_mode & ~0o222)
        except OSError:
            pass
    return root, commit, tree


def _classification(skill_name: str, observable: dict) -> str:
    return grade_record({"expected": f"loom-code:{skill_name}", **observable})


def _record_observable(observable: dict) -> dict:
    """Persist behavioral facts, not host-specific commands or absolute paths."""
    return {
        "fired": observable.get("fired"),
        "result_subtype": observable.get("result_subtype"),
        "tool_count": len(observable.get("tool_sequence") or ()),
    }


def _sanitize_dependency(value: str) -> str:
    return re.sub(r"https://github\.com/[^/]+/[^/]+", "https://github.com/<repository>", value)


def invocation_provenance(
    *, commit: str, tree: str, corpus_sha256: str, prompt: dict,
    host: str, model: str, replicate: int, max_turns: int,
    timeout_seconds: int,
) -> dict:
    return {
        "baseline_commit": commit,
        "baseline_tree": tree,
        "corpus_sha256": corpus_sha256,
        "prompt_id": prompt["id"],
        "prompt_sha256": sha256_text(prompt["prompt"]),
        "expected_behavior_sha256": sha256_text(prompt["expected_behavior"]),
        "host": host,
        "model": model,
        "replicate": replicate,
        "argv_semantics": {
            "mode": "claude-plugin-dir" if host == "claude" else "codex-isolated-plugin",
            "max_turns": max_turns,
            "allowed_tools": ["Skill"] if host == "claude" else None,
            "sandbox": None if host == "claude" else "workspace-write",
        },
        "timeout_seconds": timeout_seconds,
    }


def provenance_fingerprint(provenance: dict) -> str:
    return sha256_text(json.dumps(provenance, sort_keys=True, separators=(",", ":")))


def metadata_path(raw_path: Path) -> Path:
    return raw_path.with_suffix(".meta.json")


def load_cached_raw(raw_path: Path, fingerprint: str) -> str | None:
    meta_path = metadata_path(raw_path)
    try:
        raw = raw_path.read_bytes()
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if (
        metadata.get("fingerprint") != fingerprint
        or metadata.get("exit_code") != 0
        or metadata.get("raw_sha256") != sha256_bytes(raw)
    ):
        return None
    return raw.decode("utf-8")


def write_raw_with_metadata(
    raw_path: Path, outcome: RunOutcome, provenance: dict, fingerprint: str
) -> dict:
    raw_path.write_text(outcome.raw, encoding="utf-8")
    metadata = {
        "schema_version": 1,
        "fingerprint": fingerprint,
        "provenance": provenance,
        "exit_code": outcome.exit_code,
        "status": outcome.status,
        "raw_sha256": sha256_bytes(raw_path.read_bytes()),
    }
    metadata_path(raw_path).write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return metadata


def raw_has_successful_exit(host: str, raw: str) -> bool:
    events = []
    for line in raw.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if any(event.get("type") in {"harness_error", "harness_exit"} for event in events):
        return False
    if host == "claude":
        results = [event for event in events if event.get("type") == "result"]
        return bool(results) and results[-1].get("subtype") == "success"
    return any(event.get("type") == "turn.completed" for event in events)


def migrate_legacy_raw(
    raw_path: Path, provenance: dict, fingerprint: str
) -> tuple[str, dict] | None:
    try:
        raw = raw_path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not raw_has_successful_exit(provenance["host"], raw):
        return None
    metadata = write_raw_with_metadata(
        raw_path, RunOutcome(raw, 0, "completed"), provenance, fingerprint
    )
    return raw, metadata


@contextmanager
def temporary_auth_link(link: Path):
    try:
        yield
    finally:
        if link.is_symlink():
            link.unlink()


def _run_bounded(invocation: HostInvocation, timeout_seconds: int) -> RunOutcome:
    env = {**os.environ, **invocation.environment}
    if invocation.host == "codex":
        _prepare_codex_root(invocation, env)
    proc = subprocess.run(
        invocation.argv, capture_output=True, text=True, check=False,
        env=env, timeout=timeout_seconds,
    )
    transcript = proc.stdout + proc.stderr
    status = "completed" if proc.returncode == 0 else "host-error"
    return RunOutcome(transcript, proc.returncode, status)


def capture(
    repo: Path, out: Path, raw_workspace: Path, targets=TARGETS,
    timeout_seconds: int = 180, max_turns: int = 12,
    baseline_commit: str | None = None, migrate_legacy: bool = False,
) -> dict:
    skills_root = repo / "loom-code" / "skills"
    baseline_root, commit, tree = export_baseline(repo, raw_workspace, baseline_commit)
    raw_dir = raw_workspace / "raw"
    work_dir = raw_workspace / "work"
    raw_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(exist_ok=True)
    auth_source = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "auth.json"
    record = {
        "schema_version": 2,
        "captured": "2026-08-26",
        "acknowledgement": "The user previously acknowledged genuine prompts and weak-model equivalence testing on Claude Code and Codex.",
        "models": {"claude": "haiku", "codex": "gpt-5.6-luna"},
        "replicates_per_host": 2,
        "baseline": {"commit": commit, "tree": tree},
        "raw_workspace": raw_workspace.name,
        "skills": {},
    }
    try:
        for skill_name in targets:
            corpus_path = skills_root / skill_name / "test-prompts.json"
            corpus = validate_corpus(corpus_path, skill_name)
            corpus_hash = sha256_bytes(corpus_path.read_bytes())
            snapshot = snapshot_skill(skills_root / skill_name)
            snapshot.update({
                "corpus_sha256": corpus_hash,
                "baseline_root": {"commit": commit, "tree": tree, "label": "baseline/loom-code"},
                "raw_evidence": f"{raw_workspace.name}/raw/{skill_name}/",
                "runs": [],
            })
            skill_raw = raw_dir / skill_name
            skill_raw.mkdir(exist_ok=True)
            jobs = []
            for prompt in corpus["prompts"]:
                for host, model in (("claude", "haiku"), ("codex", "gpt-5.6-luna")):
                    for replicate in range(2):
                        jobs.append((prompt, host, model, replicate))

            def run_job(job):
                prompt, host, model, replicate = job
                item = {"query": prompt["prompt"], "expected": f"loom-code:{skill_name}", "notes": prompt["expected_behavior"]}
                codex_home = raw_workspace / "homes" / f"codex-{skill_name}-{prompt['id']}-{replicate}"
                if host == "codex":
                    codex_home.mkdir(parents=True, exist_ok=True)
                invocation_work = work_dir / f"{skill_name}-p{prompt['id']}-{host}-r{replicate}"
                invocation_work.mkdir(parents=True, exist_ok=True)
                invocation = HostInvocation(
                    host, "baseline", baseline_root, item, replicate,
                    host_argv_for_root(host, baseline_root, item, max_turns=max_turns, working_directory=invocation_work, claude_model=model if host == "claude" else None, codex_model=model if host == "codex" else None),
                    codex_home if host == "codex" else None,
                    {"CODEX_HOME": str(codex_home)} if host == "codex" else {},
                )
                raw_path = skill_raw / f"p{prompt['id']}-{host}-r{replicate}.jsonl"
                provenance = invocation_provenance(
                    commit=commit, tree=tree, corpus_sha256=corpus_hash,
                    prompt=prompt, host=host, model=model, replicate=replicate,
                    max_turns=max_turns, timeout_seconds=timeout_seconds,
                )
                fingerprint = provenance_fingerprint(provenance)
                raw = load_cached_raw(raw_path, fingerprint)
                metadata = None
                if raw is not None:
                    metadata = json.loads(metadata_path(raw_path).read_text(encoding="utf-8"))
                elif migrate_legacy:
                    legacy_provenance = invocation_provenance(
                        commit=commit, tree=tree, corpus_sha256=corpus_hash,
                        prompt=prompt, host=host, model=model, replicate=replicate,
                        max_turns=4, timeout_seconds=180,
                    )
                    legacy_fingerprint = provenance_fingerprint(legacy_provenance)
                    migrated = migrate_legacy_raw(
                        raw_path, legacy_provenance, legacy_fingerprint
                    )
                    if migrated is not None:
                        raw, metadata = migrated
                        fingerprint = legacy_fingerprint
                        provenance = legacy_provenance
                if metadata is None:
                    auth_link = codex_home / "auth.json"
                    if host == "codex" and auth_source.is_file() and not auth_link.exists():
                        auth_link.symlink_to(auth_source)
                    try:
                        with temporary_auth_link(auth_link):
                            outcome = _run_bounded(invocation, timeout_seconds)
                    except Exception as exc:  # preserve, classify, continue
                        outcome = RunOutcome(json.dumps({
                            "type": "harness_error",
                            "host": host,
                            "error": str(exc),
                        }, ensure_ascii=False) + "\n", 124, "host-error")
                    raw = outcome.raw
                    metadata = write_raw_with_metadata(
                        raw_path, outcome, provenance, fingerprint
                    )
                status = metadata["status"]
                from loom_firing_harness import _normalize_observable
                observable = _normalize_observable(host, raw)
                result = {
                    "prompt_id": prompt["id"], "host": host,
                    "model": model, "replicate": replicate,
                    "classification": _classification(skill_name, observable) if status == "completed" else "HOST_ERROR",
                    "status": status,
                    "exit_code": metadata["exit_code"],
                    "fingerprint": fingerprint,
                    "raw_sha256": metadata["raw_sha256"],
                    "expected_behavior_sha256": provenance["expected_behavior_sha256"],
                    "observable": _record_observable(observable),
                    "raw": f"{raw_workspace.name}/raw/{skill_name}/{raw_path.name}",
                    "raw_metadata": f"{raw_workspace.name}/raw/{skill_name}/{metadata_path(raw_path).name}",
                }
                return result

            with ThreadPoolExecutor(max_workers=4) as pool:
                futures = [pool.submit(run_job, job) for job in jobs]
                for future in as_completed(futures):
                    snapshot["runs"].append(future.result())
            snapshot["runs"].sort(key=lambda run: (run["prompt_id"], run["host"], run["replicate"]))
            record["skills"][skill_name] = snapshot
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    finally:
        for link in (raw_workspace / "homes").glob("*/auth.json") if (raw_workspace / "homes").exists() else ():
            if link.is_symlink():
                link.unlink()
    return record


def merge_records(
    paths: list[Path], out: Path, expected_targets=TARGETS,
    corpora_root: Path | None = None,
) -> dict:
    parts = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    if not parts:
        raise ValueError("merge requires at least one record")
    header_fields = ("schema_version", "models", "replicates_per_host", "baseline")
    for field in header_fields:
        if any(part.get(field) != parts[0].get(field) for part in parts[1:]):
            raise ValueError(f"merge {field} conflict")
    if parts[0].get("schema_version") != 2:
        raise ValueError("merge schema_version must be 2")
    merged = dict(parts[0])
    workspaces = []
    for part in parts:
        workspaces.extend(part.get("raw_workspaces", []))
        if part.get("raw_workspace"):
            workspaces.append(part["raw_workspace"])
    merged["raw_workspaces"] = list(dict.fromkeys(workspaces))
    merged.pop("raw_workspace", None)
    merged["skills"] = {}
    for part in parts:
        for skill_name, snapshot in part.get("skills", {}).items():
            if skill_name in merged["skills"] and merged["skills"][skill_name] != snapshot:
                raise ValueError(f"conflicting snapshot for {skill_name}")
            merged["skills"][skill_name] = snapshot
    if set(merged["skills"]) != set(expected_targets):
        raise ValueError("merged record does not contain all expected targets")
    root = corpora_root or REPO_ROOT / "loom-code" / "skills"
    for skill_name, snapshot in merged["skills"].items():
        if any(run.get("status") != "completed" or run.get("exit_code") != 0 for run in snapshot["runs"]):
            raise ValueError(f"host-error/nonzero run for {skill_name}")
        corpus = validate_corpus(root / skill_name / "test-prompts.json", skill_name)
        corpus_hash = sha256_bytes((root / skill_name / "test-prompts.json").read_bytes())
        if snapshot.get("corpus_sha256") != corpus_hash:
            raise ValueError(f"corpus hash conflict for {skill_name}")
        expected = {
            (prompt["id"], host, replicate)
            for prompt in corpus["prompts"]
            for host in ("claude", "codex")
            for replicate in range(merged["replicates_per_host"])
        }
        actual = {
            (run.get("prompt_id"), run.get("host"), run.get("replicate"))
            for run in snapshot["runs"]
        }
        if actual != expected or len(snapshot["runs"]) != len(expected):
            raise ValueError(f"incomplete run matrix for {skill_name}")
        for run in snapshot["runs"]:
            run["observable"] = _record_observable(run["observable"])
            for field in ("fingerprint", "raw_sha256", "expected_behavior_sha256", "raw_metadata"):
                if not run.get(field):
                    raise ValueError(f"missing {field} for {skill_name}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return merged


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=REPO_ROOT)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--raw-workspace", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--skills", nargs="*", choices=TARGETS)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--max-turns", type=int, default=12)
    parser.add_argument("--baseline-commit")
    parser.add_argument("--migrate-legacy", action="store_true")
    parser.add_argument("--merge", nargs="+", type=Path)
    args = parser.parse_args()
    if args.merge:
        if args.out is None:
            raise SystemExit("--out is required with --merge")
        merge_records(args.merge, args.out)
        print(f"PASS: merged {len(args.merge)} records into {args.out}")
        return
    for skill_name in TARGETS:
        validate_corpus(args.repo / "loom-code" / "skills" / skill_name / "test-prompts.json", skill_name)
    if args.validate_only:
        print(f"PASS: {len(TARGETS)} corpora")
        return
    if args.out is None:
        raise SystemExit("--out is required unless --validate-only is used")
    workspace = args.raw_workspace or Path(tempfile.mkdtemp(prefix="loom-code-preflight-"))
    capture(
        args.repo, args.out, workspace, tuple(args.skills or TARGETS), args.timeout,
        args.max_turns, args.baseline_commit, args.migrate_legacy,
    )
    print(f"PASS: record={args.out} raw={workspace}")


if __name__ == "__main__":
    main()
