import json
import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / "loom-code" / "skills"
RECORD = (
    REPO_ROOT
    / "docs"
    / "loom"
    / "dogfood"
    / "2026-08-26-loom-code-skill-compaction-preflight.json"
)
TARGETS = (
    "brainstorming",
    "dispatching-parallel-agents",
    "finishing-a-development-branch",
    "loom-memory",
    "requesting-code-review",
    "requesting-docs-review",
    "systematic-debugging",
    "tdd-iron-law",
    "ui-verification",
    "using-git-worktrees",
    "using-loom-code",
    "verification-before-completion",
    "writing-plans",
)
REQUIRED_CATEGORIES = {"happy-path", "edge-case", "stress"}

SPEC = importlib.util.spec_from_file_location(
    "skill_compaction_preflight", REPO_ROOT / "scripts" / "skill_compaction_preflight.py"
)
preflight = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = preflight
SPEC.loader.exec_module(preflight)


def test_all_target_corpora_and_preflight_record_exist_and_validate():
    for skill_name in TARGETS:
        corpus_path = SKILLS_ROOT / skill_name / "test-prompts.json"
        assert corpus_path.is_file(), f"missing corpus: {skill_name}"
        corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
        assert corpus["skill_name"] == skill_name
        assert corpus["schema_version"] == 1
        assert len(corpus["prompts"]) >= 3
        assert REQUIRED_CATEGORIES <= {item["category"] for item in corpus["prompts"]}
        assert [item["id"] for item in corpus["prompts"]] == list(
            range(1, len(corpus["prompts"]) + 1)
        )
        for item in corpus["prompts"]:
            assert isinstance(item["prompt"], str) and item["prompt"].strip()
            assert isinstance(item["expected_behavior"], str) and item[
                "expected_behavior"
            ].strip()
            assert isinstance(item["edge_case_dimensions"], list)

    assert RECORD.is_file(), "preflight record is missing"
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    assert record["schema_version"] == 2
    assert set(record["skills"]) == set(TARGETS)
    for skill_name, snapshot in record["skills"].items():
        assert snapshot["word_count"] > 0
        assert snapshot["frontmatter"]["name"] == skill_name
        assert "description" in snapshot["frontmatter"]
        assert isinstance(snapshot["declared_dependencies"], list)
        assert isinstance(snapshot["file_structure"], list)
        assert snapshot["baseline_root"]["commit"]
        assert snapshot["baseline_root"]["tree"]
        assert snapshot["raw_evidence"]
        runs = snapshot["runs"]
        prompt_ids = {
            item["id"]
            for item in json.loads(
                (SKILLS_ROOT / skill_name / "test-prompts.json").read_text(
                    encoding="utf-8"
                )
            )["prompts"]
        }
        assert {(run["prompt_id"], run["host"], run["replicate"]) for run in runs} == {
            (prompt_id, host, replicate)
            for prompt_id in prompt_ids
            for host in ("claude", "codex")
            for replicate in (0, 1)
        }
        assert all(run["classification"] for run in runs)
        assert all(run["status"] == "completed" and run["exit_code"] == 0 for run in runs)
        assert all(len(run["raw_sha256"]) == 64 for run in runs)
        assert all(len(run["expected_behavior_sha256"]) == 64 for run in runs)
        assert all(len(run["fingerprint"]) == 64 for run in runs)
        assert all(run["raw_metadata"] for run in runs)


def _corpus(tmp_path: Path, mutate=None) -> Path:
    data = {
        "skill_name": "demo", "schema_version": 1,
        "created": "2026-08-26", "last_reviewed": "2026-08-26",
        "prompts": [
            {"id": 1, "category": "happy-path", "prompt": "Do the normal thing", "expected_behavior": "Does it", "edge_case_dimensions": []},
            {"id": 2, "category": "edge-case", "prompt": "Handle the edge", "expected_behavior": "Handles it", "edge_case_dimensions": ["missing context"]},
            {"id": 3, "category": "stress", "prompt": "Resist pressure", "expected_behavior": "Refuses unsafe work", "edge_case_dimensions": ["gate pressure"]},
        ],
    }
    if mutate:
        mutate(data)
    path = tmp_path / "test-prompts.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.update(extra=True),
        lambda d: d["prompts"][0].update(category="other"),
        lambda d: d["prompts"][1].update(edge_case_dimensions=[3]),
    ],
)
def test_validate_corpus_rejects_extra_fields_categories_and_nonstring_dimensions(tmp_path, mutate):
    with pytest.raises(ValueError):
        preflight.validate_corpus(_corpus(tmp_path, mutate), "demo")


def test_dependency_extraction_keeps_paths_without_multiline_prose():
    text = """See [`format`](references/format.md) and `scripts/check.py`.
`This is prose / with a slash and continues
onto another line.md` must not become a dependency.
Use `verdict: PASS` and https://example.test/path.
"""
    assert preflight.extract_dependencies(text) == [
        "references/format.md", "scripts/check.py"
    ]


def test_nonzero_subprocess_is_a_host_error(monkeypatch, tmp_path):
    class Result:
        returncode = 1
        stdout = '{"type":"result","subtype":"error_max_turns"}\n'
        stderr = ""
    monkeypatch.setattr(preflight.subprocess, "run", lambda *a, **k: Result())
    invocation = preflight.HostInvocation(
        "claude", "baseline", tmp_path, {"query": "q"}, 0,
        ("claude",), None, {},
    )
    outcome = preflight._run_bounded(invocation, 10)
    assert outcome.exit_code == 1
    assert outcome.status == "host-error"


def test_zero_exit_with_structured_host_failure_is_a_host_error(monkeypatch, tmp_path):
    class Result:
        returncode = 0
        stdout = '{"type":"result","subtype":"error_max_turns"}\n'
        stderr = ""
    monkeypatch.setattr(preflight.subprocess, "run", lambda *a, **k: Result())
    invocation = preflight.HostInvocation(
        "claude", "baseline", tmp_path, {"query": "q"}, 0,
        ("claude",), None, {},
    )
    outcome = preflight._run_bounded(invocation, 10)
    assert outcome.exit_code == 0
    assert outcome.status == "host-error"


def test_legacy_migration_surface_is_removed():
    source = (REPO_ROOT / "scripts" / "skill_compaction_preflight.py").read_text(
        encoding="utf-8"
    )
    assert "migrate_legacy_raw" not in source
    assert "--migrate-legacy" not in source


def test_export_baseline_rejects_option_like_revision_without_touching_file(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(("git", "init", str(repo)), check=True, capture_output=True)
    (repo / "loom-code").mkdir()
    (repo / "loom-code" / "marker").write_text("baseline", encoding="utf-8")
    subprocess.run(("git", "-C", str(repo), "add", "loom-code/marker"), check=True)
    subprocess.run(
        (
            "git", "-C", str(repo), "-c", "user.name=Test",
            "-c", "user.email=test@example.invalid", "commit", "-m", "baseline",
        ),
        check=True, capture_output=True,
    )
    sentinel = tmp_path / "sentinel"
    sentinel.write_text("keep", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid baseline commit"):
        preflight.export_baseline(
            repo, tmp_path / "workspace", f"--output={sentinel}"
        )
    assert sentinel.read_text(encoding="utf-8") == "keep"


def test_cache_reuse_requires_exact_fingerprint_exit_zero_and_raw_hash(tmp_path):
    raw = tmp_path / "run.jsonl"
    raw.write_text("ok\n", encoding="utf-8")
    meta = raw.with_suffix(".meta.json")
    fingerprint = "a" * 64
    meta.write_text(json.dumps({
        "fingerprint": fingerprint, "exit_code": 0,
        "raw_sha256": preflight.sha256_bytes(raw.read_bytes()),
    }), encoding="utf-8")
    assert preflight.load_cached_raw(raw, fingerprint) == "ok\n"
    assert preflight.load_cached_raw(raw, "b" * 64) is None
    meta.write_text(json.dumps({"fingerprint": fingerprint, "exit_code": 1, "raw_sha256": preflight.sha256_bytes(raw.read_bytes())}), encoding="utf-8")
    assert preflight.load_cached_raw(raw, fingerprint) is None
    meta.write_text(json.dumps({"fingerprint": fingerprint, "exit_code": 0, "raw_sha256": "0" * 64}), encoding="utf-8")
    assert preflight.load_cached_raw(raw, fingerprint) is None


def test_merge_refuses_conflicts_incomplete_and_host_errors(tmp_path):
    base = {
        "schema_version": 2, "models": {"claude": "haiku", "codex": "gpt-5.6-luna"},
        "replicates_per_host": 2, "baseline": {"commit": "c", "tree": "t"},
        "raw_workspace": "one", "skills": {},
    }
    a = tmp_path / "a.json"; b = tmp_path / "b.json"; out = tmp_path / "out.json"
    a.write_text(json.dumps(base), encoding="utf-8")
    b.write_text(json.dumps({**base, "models": {"claude": "other"}, "raw_workspace": "two"}), encoding="utf-8")
    with pytest.raises(ValueError, match="models"):
        preflight.merge_records([a, b], out, expected_targets=())

    bad = {**base, "skills": {"demo": {"corpus_sha256": "x", "runs": [{"status": "host-error"}]}}}
    a.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError, match="host-error"):
        preflight.merge_records([a], out, expected_targets=("demo",))

    a.write_text(json.dumps(base), encoding="utf-8")
    with pytest.raises(ValueError, match="targets"):
        preflight.merge_records([a], out, expected_targets=("demo",))


def test_merge_allows_exact_duplicate_dedupes_workspace_and_rejects_snapshot_conflict(tmp_path):
    skill_dir = tmp_path / "demo"
    skill_dir.mkdir()
    corpus_path = _corpus(skill_dir)
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    runs = []
    for prompt in corpus["prompts"]:
        for host in ("claude", "codex"):
            for replicate in (0, 1):
                runs.append({
                    "prompt_id": prompt["id"], "host": host,
                    "replicate": replicate, "status": "completed", "exit_code": 0,
                    "fingerprint": "f" * 64, "raw_sha256": "a" * 64,
                    "expected_behavior_sha256": preflight.sha256_text(prompt["expected_behavior"]),
                    "raw_metadata": "workspace/raw.meta.json",
                    "observable": {"fired": True, "result_subtype": "ok", "tool_count": 3},
                })
    snapshot = {
        "corpus_sha256": preflight.sha256_bytes(corpus_path.read_bytes()),
        "word_count": 10, "runs": runs,
    }
    part = {
        "schema_version": 2, "models": {"claude": "haiku", "codex": "gpt-5.6-luna"},
        "replicates_per_host": 2, "baseline": {"commit": "c", "tree": "t"},
        "raw_workspace": "one", "skills": {"demo": snapshot},
    }
    a = tmp_path / "a.json"; b = tmp_path / "b.json"; out = tmp_path / "out.json"
    a.write_text(json.dumps(part), encoding="utf-8")
    b.write_text(json.dumps(part), encoding="utf-8")
    merged = preflight.merge_records(
        [a, b], out, expected_targets=("demo",), corpora_root=tmp_path
    )
    assert merged["raw_workspaces"] == ["one"]
    assert all(
        run["observable"] == {"fired": True, "result_subtype": "ok", "tool_count": 3}
        for run in merged["skills"]["demo"]["runs"]
    )

    conflicting = json.loads(json.dumps(part))
    conflicting["skills"]["demo"]["word_count"] = 11
    b.write_text(json.dumps(conflicting), encoding="utf-8")
    with pytest.raises(ValueError, match="conflicting snapshot"):
        preflight.merge_records(
            [a, b], out, expected_targets=("demo",), corpora_root=tmp_path
        )


def test_auth_link_is_removed_when_run_raises(monkeypatch, tmp_path):
    link = tmp_path / "auth.json"
    source = tmp_path / "source-auth.json"
    source.write_text("{}", encoding="utf-8")
    link.symlink_to(source)
    with pytest.raises(RuntimeError):
        with preflight.temporary_auth_link(link):
            raise RuntimeError("boom")
    assert not link.exists() and not link.is_symlink()


def test_raw_and_expected_behavior_hashes_make_semantics_recoverable(tmp_path):
    raw = tmp_path / "raw" / "demo" / "p1-claude-r0.jsonl"
    raw.parent.mkdir(parents=True)
    provenance = {
        "expected_behavior_sha256": preflight.sha256_text("Expected behavior"),
    }
    metadata = {
        "raw_sha256": preflight.sha256_text("transcript\n"),
        "provenance": provenance,
    }
    raw.write_text("transcript\n", encoding="utf-8")
    run = {
        "raw": "workspace/raw/demo/p1-claude-r0.jsonl",
        "raw_sha256": metadata["raw_sha256"],
        "expected_behavior_sha256": provenance["expected_behavior_sha256"],
    }
    prompt = {"expected_behavior": "Expected behavior"}
    preflight.verify_run_semantics(run, prompt, raw)


def test_verify_record_raw_rejects_metadata_fingerprint_drift(tmp_path):
    skill_dir = tmp_path / "corpora" / "demo"
    skill_dir.mkdir(parents=True)
    corpus_path = _corpus(skill_dir)
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    workspace = tmp_path / "raw-base" / "workspace"
    raw = workspace / "raw" / "demo" / "p1-claude-r0.jsonl"
    raw.parent.mkdir(parents=True)
    provenance = preflight.invocation_provenance(
        commit="c", tree="t",
        corpus_sha256=preflight.sha256_bytes(corpus_path.read_bytes()),
        prompt=corpus["prompts"][0], host="claude", model="haiku",
        replicate=0, max_turns=12, timeout_seconds=180,
    )
    fingerprint = preflight.provenance_fingerprint(provenance)
    transcript = '{"type":"result","subtype":"success"}\n'
    metadata = preflight.write_raw_with_metadata(
        raw, preflight.RunOutcome(transcript, 0, "completed"),
        provenance, fingerprint,
    )
    run = {
        "prompt_id": 1, "host": "claude", "model": "haiku", "replicate": 0,
        "status": "completed", "exit_code": 0, "fingerprint": fingerprint,
        "raw_sha256": metadata["raw_sha256"],
        "expected_behavior_sha256": provenance["expected_behavior_sha256"],
        "classification": "MISS",
        "observable": {"fired": None, "result_subtype": "success", "tool_count": 0},
        "raw": "workspace/raw/demo/p1-claude-r0.jsonl",
        "raw_metadata": "workspace/raw/demo/p1-claude-r0.meta.json",
    }
    record = {
        "schema_version": 2, "baseline": {"commit": "c", "tree": "t"},
        "models": {"claude": "haiku", "codex": "gpt-5.6-luna"},
        "skills": {"demo": {"corpus_sha256": provenance["corpus_sha256"], "runs": [run]}},
    }
    record_path = tmp_path / "record.json"
    record_path.write_text(json.dumps(record), encoding="utf-8")
    assert preflight.verify_raw_record(
        record_path, tmp_path / "raw-base", tmp_path / "corpora"
    ) == 1

    corrupted = json.loads(record_path.read_text(encoding="utf-8"))
    corrupted["skills"]["demo"]["runs"][0]["observable"]["tool_count"] = 9
    record_path.write_text(json.dumps(corrupted), encoding="utf-8")
    with pytest.raises(ValueError, match="observable mismatch"):
        preflight.verify_raw_record(
            record_path, tmp_path / "raw-base", tmp_path / "corpora"
        )
    record_path.write_text(json.dumps(record), encoding="utf-8")

    metadata_path = preflight.metadata_path(raw)
    altered = json.loads(metadata_path.read_text(encoding="utf-8"))
    altered["provenance"]["timeout_seconds"] = 999
    metadata_path.write_text(json.dumps(altered), encoding="utf-8")
    with pytest.raises(ValueError, match="fingerprint"):
        preflight.verify_raw_record(
            record_path, tmp_path / "raw-base", tmp_path / "corpora"
        )
