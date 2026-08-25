import json
import importlib.util
from pathlib import Path
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
    assert record["schema_version"] == 1
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


def test_auth_link_is_removed_when_run_raises(monkeypatch, tmp_path):
    link = tmp_path / "auth.json"
    source = tmp_path / "source-auth.json"
    source.write_text("{}", encoding="utf-8")
    link.symlink_to(source)
    with pytest.raises(RuntimeError):
        with preflight.temporary_auth_link(link):
            raise RuntimeError("boom")
    assert not link.exists() and not link.is_symlink()
