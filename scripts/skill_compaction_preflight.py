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
    _normalize_observable,
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
    manifest = {}
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError(
                f"cached baseline contains symlink: {path.relative_to(root)}"
            )
        if path.is_file():
            executable = path.stat().st_mode & 0o111
            manifest[str(path.relative_to(root))] = (
                f"{executable:o}:{sha256_bytes(path.read_bytes())}"
            )
    return manifest


def export_baseline(
    repo: Path, workspace: Path, baseline_commit: str | None = None
) -> tuple[Path, str, str]:
    revision = baseline_commit or "HEAD"
    resolved = subprocess.run(
        (
            "git", "-C", str(repo), "rev-parse", "--verify",
            "--end-of-options", f"{revision}^{{commit}}",
        ),
        check=False, capture_output=True, text=True,
    )
    commit = resolved.stdout.strip()
    if resolved.returncode != 0 or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise ValueError(f"invalid baseline commit: {revision}")
    tree = _git(repo, "rev-parse", f"{commit}:loom-code")
    root = workspace / "baseline" / "loom-code"
    archive = subprocess.run(
        ("git", "-C", str(repo), "archive", "--format=tar", commit, "loom-code"),
        check=True, capture_output=True,
    ).stdout
    if root.is_symlink():
        raise ValueError("cached baseline root is a symlink")
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
    tool_count = observable.get("tool_count")
    if tool_count is None:
        tool_count = len(observable.get("tool_sequence") or ())
    return {
        "fired": observable.get("fired"),
        "result_subtype": observable.get("result_subtype"),
        "tool_count": tool_count,
    }


def invocation_argv_semantics(host: str, max_turns: int) -> dict:
    argv_semantics = {
        "mode": "claude-plugin-dir" if host == "claude" else "codex-isolated-plugin",
        "allowed_tools": ["Skill"] if host == "claude" else None,
        "sandbox": None if host == "claude" else "workspace-write",
    }
    if host == "claude":
        argv_semantics["max_turns"] = max_turns
    return argv_semantics


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
        "argv_semantics": invocation_argv_semantics(host, max_turns),
        "timeout_seconds": timeout_seconds,
    }


def provenance_fingerprint(provenance: dict) -> str:
    return sha256_text(json.dumps(provenance, sort_keys=True, separators=(",", ":")))


def capture_contract(provenance: dict) -> dict:
    return {
        "host": provenance["host"], "model": provenance["model"],
        "argv_semantics": provenance["argv_semantics"],
        "timeout_seconds": provenance["timeout_seconds"],
    }


def capture_contract_fingerprint(contract: dict) -> str:
    return sha256_text(json.dumps(contract, sort_keys=True, separators=(",", ":")))


def capture_contracts_for_models(
    models: dict[str, str], max_turns: int, timeout_seconds: int
) -> list[dict]:
    return [
        {
            "host": host, "model": model,
            "argv_semantics": invocation_argv_semantics(host, max_turns),
            "timeout_seconds": timeout_seconds,
        }
        for host, model in models.items()
    ]


def _capture_contract_map(contracts: object) -> dict[str, dict]:
    if not isinstance(contracts, list) or not contracts:
        raise ValueError("capture contracts missing")
    return {
        capture_contract_fingerprint(contract): contract
        for contract in contracts
    }


def _validate_run_capture_contract(
    run: dict, contract_map: dict[str, dict], models: dict, label: str
) -> None:
    host = run.get("host")
    model = run.get("model")
    if model != models.get(host):
        raise ValueError(f"model header mismatch: {label}")
    contract = contract_map.get(run.get("capture_contract_fingerprint"))
    if (
        not isinstance(contract, dict)
        or contract.get("host") != host
        or contract.get("model") != model
    ):
        raise ValueError(f"run capture contract mismatch: {label}")


def metadata_path(raw_path: Path) -> Path:
    return raw_path.with_suffix(".meta.json")


def load_bound_raw(raw_path: Path, expected_case: dict) -> tuple[str, dict] | None:
    try:
        raw = raw_path.read_bytes()
        metadata = json.loads(metadata_path(raw_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    provenance = metadata.get("provenance")
    expected_fingerprint = provenance_fingerprint(expected_case)
    if (
        not isinstance(provenance, dict)
        or provenance != expected_case
        or metadata.get("fingerprint") != provenance_fingerprint(provenance)
        or metadata.get("fingerprint") != expected_fingerprint
        or metadata.get("exit_code") != 0
        or metadata.get("status") != "completed"
        or metadata.get("raw_sha256") != sha256_bytes(raw)
        or not raw_has_successful_exit(expected_case["host"], raw.decode("utf-8"))
    ):
        return None
    return raw.decode("utf-8"), metadata


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


def verify_run_semantics(run: dict, prompt: dict, raw_path: Path) -> None:
    if sha256_bytes(raw_path.read_bytes()) != run.get("raw_sha256"):
        raise ValueError(f"raw hash mismatch: {raw_path}")
    if sha256_text(prompt["expected_behavior"]) != run.get("expected_behavior_sha256"):
        raise ValueError(f"expected behavior hash mismatch: prompt {prompt.get('id')}")


def _external_path(raw_base: Path, label: str) -> Path:
    relative = Path(label)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"unsafe raw evidence label: {label}")
    base = raw_base.resolve()
    candidate = (base / relative).resolve()
    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise ValueError(f"path escapes raw evidence root: {label}") from exc
    return candidate


def verify_raw_record(
    record_path: Path, raw_base: Path,
    corpora_root: Path = REPO_ROOT / "loom-code" / "skills",
    expected_targets: tuple[str, ...] | None = None,
) -> int:
    """Verify that every accepted run remains recoverable from bound raw evidence."""
    record = json.loads(record_path.read_text(encoding="utf-8"))
    skills = record.get("skills")
    if not isinstance(skills, dict) or not skills:
        raise ValueError("no skill evidence")
    if expected_targets is not None and set(skills) != set(expected_targets):
        raise ValueError("record does not contain all expected targets")
    contracts = record.get("capture_contracts")
    contract_map = _capture_contract_map(contracts)
    contract_set = {
        json.dumps(contract, sort_keys=True, separators=(",", ":"))
        for contract in contracts
    }
    verified = 0
    for skill_name, snapshot in skills.items():
        corpus_path = corpora_root / skill_name / "test-prompts.json"
        corpus = validate_corpus(corpus_path, skill_name)
        if snapshot.get("corpus_sha256") != sha256_bytes(corpus_path.read_bytes()):
            raise ValueError(f"corpus hash mismatch: {skill_name}")
        prompts = {prompt["id"]: prompt for prompt in corpus["prompts"]}
        if expected_targets is not None:
            expected_runs = {
                (prompt_id, host, replicate)
                for prompt_id in prompts
                for host in ("claude", "codex")
                for replicate in range(record.get("replicates_per_host", 0))
            }
            actual_runs = {
                (run.get("prompt_id"), run.get("host"), run.get("replicate"))
                for run in snapshot.get("runs", [])
            }
            if not expected_runs or actual_runs != expected_runs or len(snapshot.get("runs", [])) != len(expected_runs):
                raise ValueError(f"incomplete run matrix: {skill_name}")
        for run in snapshot.get("runs", []):
            raw_path = _external_path(raw_base, run["raw"])
            meta_path = _external_path(raw_base, run["raw_metadata"])
            if meta_path != metadata_path(raw_path):
                raise ValueError(f"metadata label mismatch: {skill_name}")
            try:
                metadata = json.loads(meta_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise ValueError(f"unreadable raw metadata: {meta_path}") from exc
            provenance = metadata.get("provenance")
            if (
                not isinstance(provenance, dict)
                or metadata.get("fingerprint") != provenance_fingerprint(provenance)
                or run.get("fingerprint") != metadata.get("fingerprint")
            ):
                raise ValueError(f"fingerprint mismatch: {skill_name} p{run.get('prompt_id')}")
            prompt = prompts.get(run.get("prompt_id"))
            expected = {
                "baseline_commit": record["baseline"]["commit"],
                "baseline_tree": record["baseline"]["tree"],
                "corpus_sha256": snapshot["corpus_sha256"],
                "prompt_id": run["prompt_id"],
                "prompt_sha256": sha256_text(prompt["prompt"]) if prompt else None,
                "expected_behavior_sha256": sha256_text(prompt["expected_behavior"]) if prompt else None,
                "host": run["host"], "model": run["model"],
                "replicate": run["replicate"],
            }
            if any(provenance.get(key) != value for key, value in expected.items()):
                raise ValueError(f"provenance mismatch: {skill_name} p{run.get('prompt_id')}")
            _validate_run_capture_contract(
                run, contract_map, record.get("models", {}),
                f"{skill_name} p{run.get('prompt_id')}",
            )
            encoded_contract = json.dumps(
                capture_contract(provenance), sort_keys=True, separators=(",", ":")
            )
            if encoded_contract not in contract_set:
                raise ValueError(f"capture contract mismatch: {skill_name} p{run.get('prompt_id')}")
            expected_contract_fp = capture_contract_fingerprint(capture_contract(provenance))
            if run.get("capture_contract_fingerprint") != expected_contract_fp:
                raise ValueError(f"run capture contract mismatch: {skill_name} p{run.get('prompt_id')}")
            if (
                metadata.get("exit_code") != 0
                or metadata.get("status") != "completed"
                or run.get("exit_code") != 0
                or run.get("status") != "completed"
            ):
                raise ValueError(f"nonzero raw evidence: {skill_name} p{run.get('prompt_id')}")
            verify_run_semantics(run, prompt, raw_path)
            if metadata.get("raw_sha256") != run.get("raw_sha256"):
                raise ValueError(f"metadata raw hash mismatch: {skill_name}")
            raw = raw_path.read_text(encoding="utf-8")
            if not raw_has_successful_exit(run["host"], raw):
                raise ValueError(f"structured host failure: {skill_name} p{run.get('prompt_id')}")
            observable = _record_observable(_normalize_observable(run["host"], raw))
            if observable != run.get("observable"):
                raise ValueError(f"observable mismatch: {skill_name} p{run.get('prompt_id')}")
            if _classification(skill_name, observable) != run.get("classification"):
                raise ValueError(f"classification mismatch: {skill_name} p{run.get('prompt_id')}")
            verified += 1
    return verified


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
    status = (
        "completed"
        if proc.returncode == 0 and raw_has_successful_exit(invocation.host, transcript)
        else "host-error"
    )
    return RunOutcome(transcript, proc.returncode, status)


def _run_with_auth(
    invocation: HostInvocation, timeout_seconds: int, auth_source: Path
) -> RunOutcome:
    if invocation.host != "codex":
        return _run_bounded(invocation, timeout_seconds)
    if invocation.codex_home is None:
        raise ValueError("Codex invocation has no CODEX_HOME")
    auth_link = invocation.codex_home / "auth.json"
    if auth_source.is_file() and not auth_link.exists():
        auth_link.symlink_to(auth_source)
    with temporary_auth_link(auth_link):
        return _run_bounded(invocation, timeout_seconds)


def _capture_invocation(
    *, host: str, model: str, skill_name: str, prompt: dict, replicate: int,
    baseline_root: Path, raw_workspace: Path, work_dir: Path, max_turns: int,
) -> HostInvocation:
    item = {
        "query": prompt["prompt"], "expected": f"loom-code:{skill_name}",
        "notes": prompt["expected_behavior"],
    }
    codex_home = raw_workspace / "homes" / f"codex-{skill_name}-{prompt['id']}-{replicate}"
    if host == "codex":
        if (
            codex_home.is_symlink()
            or not codex_home.resolve().is_relative_to(raw_workspace.resolve())
        ):
            raise ValueError("Codex home escapes raw workspace or is a symlink")
        codex_home.mkdir(parents=True, exist_ok=True)
    invocation_work = work_dir / f"{skill_name}-p{prompt['id']}-{host}-r{replicate}"
    invocation_work.mkdir(parents=True, exist_ok=True)
    return HostInvocation(
        host, "baseline", baseline_root, item, replicate,
        host_argv_for_root(
            host, baseline_root, item, max_turns=max_turns,
            working_directory=invocation_work,
            claude_model=model if host == "claude" else None,
            codex_model=model if host == "codex" else None,
        ),
        codex_home if host == "codex" else None,
        {"CODEX_HOME": str(codex_home)} if host == "codex" else {},
    )


def _capture_run(
    job: tuple[dict, str, str, int], *, skill_name: str, baseline_root: Path,
    raw_workspace: Path, work_dir: Path, skill_raw: Path, commit: str, tree: str,
    corpus_hash: str, max_turns: int, timeout_seconds: int, auth_source: Path,
) -> dict:
    prompt, host, model, replicate = job
    invocation = _capture_invocation(
        host=host, model=model, skill_name=skill_name, prompt=prompt,
        replicate=replicate, baseline_root=baseline_root,
        raw_workspace=raw_workspace, work_dir=work_dir, max_turns=max_turns,
    )
    raw_path = skill_raw / f"p{prompt['id']}-{host}-r{replicate}.jsonl"
    provenance = invocation_provenance(
        commit=commit, tree=tree, corpus_sha256=corpus_hash, prompt=prompt,
        host=host, model=model, replicate=replicate, max_turns=max_turns,
        timeout_seconds=timeout_seconds,
    )
    fingerprint = provenance_fingerprint(provenance)
    bound = load_bound_raw(raw_path, provenance)
    if bound is None:
        try:
            outcome = _run_with_auth(invocation, timeout_seconds, auth_source)
        except Exception as exc:
            outcome = RunOutcome(json.dumps({
                "type": "harness_error", "host": host, "error": str(exc),
            }, ensure_ascii=False) + "\n", 124, "host-error")
        raw = outcome.raw
        metadata = write_raw_with_metadata(raw_path, outcome, provenance, fingerprint)
    else:
        raw, metadata = bound
    status = metadata["status"]
    observable = _normalize_observable(host, raw)
    return {
        "prompt_id": prompt["id"], "host": host, "model": model,
        "replicate": replicate,
        "classification": _classification(skill_name, observable) if status == "completed" else "HOST_ERROR",
        "status": status, "exit_code": metadata["exit_code"],
        "fingerprint": metadata["fingerprint"],
        "raw_sha256": metadata["raw_sha256"],
        "expected_behavior_sha256": provenance["expected_behavior_sha256"],
        "capture_contract_fingerprint": capture_contract_fingerprint(
            capture_contract(provenance)
        ),
        "observable": _record_observable(observable),
        "raw": f"{raw_workspace.name}/raw/{skill_name}/{raw_path.name}",
        "raw_metadata": f"{raw_workspace.name}/raw/{skill_name}/{metadata_path(raw_path).name}",
    }


def require_complete_capture(record: dict) -> None:
    failed = [
        (skill_name, run.get("prompt_id"), run.get("host"), run.get("replicate"))
        for skill_name, snapshot in record.get("skills", {}).items()
        for run in snapshot.get("runs", [])
        if run.get("status") != "completed" or run.get("exit_code") != 0
    ]
    if failed:
        raise ValueError(f"capture incomplete: {len(failed)} failed runs; first={failed[0]}")


def capture(
    repo: Path, out: Path, raw_workspace: Path, targets=TARGETS,
    timeout_seconds: int = 180, max_turns: int = 12,
    baseline_commit: str | None = None,
) -> dict:
    raw_workspace = raw_workspace.resolve()
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
        "capture_contracts": capture_contracts_for_models(
            {"claude": "haiku", "codex": "gpt-5.6-luna"},
            max_turns, timeout_seconds,
        ),
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
            snapshot = snapshot_skill(baseline_root / "skills" / skill_name)
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

            with ThreadPoolExecutor(max_workers=4) as pool:
                futures = [pool.submit(
                    _capture_run, job, skill_name=skill_name,
                    baseline_root=baseline_root, raw_workspace=raw_workspace,
                    work_dir=work_dir, skill_raw=skill_raw, commit=commit, tree=tree,
                    corpus_hash=corpus_hash, max_turns=max_turns,
                    timeout_seconds=timeout_seconds, auth_source=auth_source,
                ) for job in jobs]
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
    contract_maps = [
        _capture_contract_map(part.get("capture_contracts")) for part in parts
    ]
    merged = dict(parts[0])
    contracts = {
        json.dumps(contract, sort_keys=True, separators=(",", ":")): contract
        for part in parts for contract in part.get("capture_contracts", [])
    }
    merged["capture_contracts"] = [contracts[key] for key in sorted(contracts)]
    workspaces = []
    for part in parts:
        workspaces.extend(part.get("raw_workspaces", []))
        if part.get("raw_workspace"):
            workspaces.append(part["raw_workspace"])
    merged["raw_workspaces"] = list(dict.fromkeys(workspaces))
    merged.pop("raw_workspace", None)
    merged["skills"] = {}
    for part, contract_map in zip(parts, contract_maps, strict=True):
        for skill_name, snapshot in part.get("skills", {}).items():
            for run in snapshot.get("runs", []):
                _validate_run_capture_contract(
                    run, contract_map, part.get("models", {}), skill_name
                )
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
            _validate_run_capture_contract(
                run,
                {capture_contract_fingerprint(value): value for value in contracts.values()},
                merged.get("models", {}), skill_name,
            )
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
    parser.add_argument("--merge", nargs="+", type=Path)
    parser.add_argument("--verify-record-raw", type=Path)
    parser.add_argument("--raw-base", type=Path, default=Path("/tmp"))
    args = parser.parse_args()
    if args.verify_record_raw:
        count = verify_raw_record(
            args.verify_record_raw, args.raw_base, expected_targets=TARGETS
        )
        print(f"PASS: verified {count} bound raw runs")
        return
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
    record = capture(
        args.repo, args.out, workspace, tuple(args.skills or TARGETS), args.timeout,
        args.max_turns, args.baseline_commit,
    )
    require_complete_capture(record)
    print(f"PASS: record={args.out} raw={workspace}")


if __name__ == "__main__":
    main()
