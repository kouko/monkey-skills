#!/usr/bin/env python3
"""Validate compaction corpora and freeze an immutable dual-host baseline."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
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
LINK_RE = re.compile(r"\[[^]]+\]\(([^)#]+)(?:#[^)]+)?\)")
CODE_PATH_RE = re.compile(r"`([^`]*(?:\.py|\.md|\.json|\.sh|/)[^`]*)`")


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
    if data.get("skill_name") != skill_name or data.get("schema_version") != 1:
        raise ValueError(f"{path}: skill_name/schema_version mismatch")
    prompts = data.get("prompts")
    if not isinstance(prompts, list) or len(prompts) < 3:
        raise ValueError(f"{path}: at least three prompts required")
    if not CATEGORIES <= {p.get("category") for p in prompts}:
        raise ValueError(f"{path}: happy-path, edge-case, stress required")
    for index, prompt in enumerate(prompts, 1):
        required = {"id", "category", "prompt", "expected_behavior", "edge_case_dimensions"}
        if set(prompt) != required or prompt["id"] != index:
            raise ValueError(f"{path}: prompt {index} violates schema")
        if not all(isinstance(prompt[k], str) and prompt[k].strip() for k in ("prompt", "expected_behavior")):
            raise ValueError(f"{path}: prompt {index} has blank text")
        if not isinstance(prompt["edge_case_dimensions"], list):
            raise ValueError(f"{path}: prompt {index} dimensions must be a list")
    return data


def snapshot_skill(skill_dir: Path) -> dict:
    skill_file = skill_dir / "SKILL.md"
    text = skill_file.read_text(encoding="utf-8")
    frontmatter = _frontmatter(text)
    dependencies = sorted(set(LINK_RE.findall(text)) | set(CODE_PATH_RE.findall(text)))
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


def export_baseline(repo: Path, workspace: Path) -> tuple[Path, str, str]:
    commit = _git(repo, "rev-parse", "HEAD")
    tree = _git(repo, "rev-parse", "HEAD:loom-code")
    root = workspace / "baseline" / "loom-code"
    if not root.is_dir():
        archive = subprocess.run(
            ("git", "-C", str(repo), "archive", "--format=tar", "HEAD", "loom-code"),
            check=True, capture_output=True,
        ).stdout
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as tar:
            tar.extractall(workspace / "baseline", filter="data")
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


def _run_bounded(invocation: HostInvocation, timeout_seconds: int) -> str:
    env = {**os.environ, **invocation.environment}
    if invocation.host == "codex":
        _prepare_codex_root(invocation, env)
    proc = subprocess.run(
        invocation.argv, capture_output=True, text=True, check=False,
        env=env, timeout=timeout_seconds,
    )
    transcript = proc.stdout + proc.stderr
    if proc.returncode:
        transcript += json.dumps({
            "type": "harness_exit", "host": invocation.host,
            "returncode": proc.returncode,
        }) + "\n"
    return transcript


def capture(
    repo: Path, out: Path, raw_workspace: Path, targets=TARGETS,
    timeout_seconds: int = 180,
) -> dict:
    skills_root = repo / "loom-code" / "skills"
    baseline_root, commit, tree = export_baseline(repo, raw_workspace)
    raw_dir = raw_workspace / "raw"
    work_dir = raw_workspace / "work"
    raw_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(exist_ok=True)
    auth_source = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "auth.json"
    record = {
        "schema_version": 1,
        "captured": "2026-08-26",
        "acknowledgement": "The user previously acknowledged genuine prompts and weak-model equivalence testing on Claude Code and Codex.",
        "models": {"claude": "haiku", "codex": "gpt-5.6-luna"},
        "replicates_per_host": 2,
        "raw_workspace": raw_workspace.name,
        "skills": {},
    }
    try:
        for skill_name in targets:
            corpus_path = skills_root / skill_name / "test-prompts.json"
            corpus = validate_corpus(corpus_path, skill_name)
            snapshot = snapshot_skill(skills_root / skill_name)
            snapshot.update({
                "corpus_sha256": hashlib.sha256(corpus_path.read_bytes()).hexdigest(),
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
                    if auth_source.is_file() and not (codex_home / "auth.json").exists():
                        (codex_home / "auth.json").symlink_to(auth_source)
                invocation_work = work_dir / f"{skill_name}-p{prompt['id']}-{host}-r{replicate}"
                invocation_work.mkdir(parents=True, exist_ok=True)
                invocation = HostInvocation(
                    host, "baseline", baseline_root, item, replicate,
                    host_argv_for_root(host, baseline_root, item, max_turns=4, working_directory=invocation_work, claude_model=model if host == "claude" else None, codex_model=model if host == "codex" else None),
                    codex_home if host == "codex" else None,
                    {"CODEX_HOME": str(codex_home)} if host == "codex" else {},
                )
                raw_path = skill_raw / f"p{prompt['id']}-{host}-r{replicate}.jsonl"
                if raw_path.is_file() and raw_path.stat().st_size:
                    raw = raw_path.read_text(encoding="utf-8")
                else:
                    try:
                        raw = _run_bounded(invocation, timeout_seconds)
                    except Exception as exc:  # preserve, classify, continue
                        raw = json.dumps({
                            "type": "harness_error",
                            "host": host,
                            "error": str(exc),
                        }, ensure_ascii=False) + "\n"
                    raw_path.write_text(raw, encoding="utf-8")
                status = "host-error" if '"type": "harness_error"' in raw else "completed"
                from loom_firing_harness import _normalize_observable
                observable = _normalize_observable(host, raw)
                result = {
                    "prompt_id": prompt["id"], "host": host,
                    "model": model, "replicate": replicate,
                    "classification": _classification(skill_name, observable) if status == "completed" else "HOST_ERROR",
                    "status": status,
                    "observable": _record_observable(observable),
                    "raw": f"{raw_workspace.name}/raw/{skill_name}/{raw_path.name}",
                }
                auth_link = codex_home / "auth.json"
                if host == "codex" and auth_link.is_symlink():
                    auth_link.unlink()
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


def merge_records(paths: list[Path], out: Path) -> dict:
    parts = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    merged = dict(parts[0])
    merged["raw_workspaces"] = [part["raw_workspace"] for part in parts]
    merged.pop("raw_workspace", None)
    merged["skills"] = {}
    for part in parts:
        # Later partial retry records intentionally replace earlier snapshots.
        merged["skills"].update(part["skills"])
    if set(merged["skills"]) != set(TARGETS):
        raise ValueError("merged record does not contain all targets")
    for snapshot in merged["skills"].values():
        snapshot["declared_dependencies"] = [
            _sanitize_dependency(item) for item in snapshot["declared_dependencies"]
        ]
        for run in snapshot["runs"]:
            run["observable"] = _record_observable(run["observable"])
    for skill_name, snapshot in merged["skills"].items():
        snapshot["word_count"] = int(subprocess.run(
            ("wc", "-w", str(REPO_ROOT / "loom-code" / "skills" / skill_name / "SKILL.md")),
            check=True, capture_output=True, text=True,
        ).stdout.split()[0])
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
        args.repo, args.out, workspace, tuple(args.skills or TARGETS), args.timeout
    )
    print(f"PASS: record={args.out} raw={workspace}")


if __name__ == "__main__":
    main()
