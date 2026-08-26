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
    """Grounded by live `git rev-parse -h` and `git archive -h` on 2026-08-26."""
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


def test_export_baseline_rejects_cached_symlink(tmp_path):
    repo = tmp_path / "repo"; repo.mkdir()
    subprocess.run(("git", "init", str(repo)), check=True, capture_output=True)
    (repo / "loom-code").mkdir()
    (repo / "loom-code" / "marker").write_text("baseline", encoding="utf-8")
    subprocess.run(("git", "-C", str(repo), "add", "loom-code/marker"), check=True)
    subprocess.run((
        "git", "-C", str(repo), "-c", "user.name=Test",
        "-c", "user.email=test@example.invalid", "commit", "-m", "baseline",
    ), check=True, capture_output=True)
    workspace = tmp_path / "workspace"
    root, _, _ = preflight.export_baseline(repo, workspace)
    outside = tmp_path / "outside"; outside.mkdir()
    (root / "injected").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        preflight.export_baseline(repo, workspace)


def test_export_baseline_rejects_cached_root_symlink(tmp_path):
    repo = tmp_path / "repo"; repo.mkdir()
    subprocess.run(("git", "init", str(repo)), check=True, capture_output=True)
    (repo / "loom-code").mkdir()
    (repo / "loom-code" / "marker").write_text("baseline", encoding="utf-8")
    subprocess.run(("git", "-C", str(repo), "add", "loom-code/marker"), check=True)
    subprocess.run((
        "git", "-C", str(repo), "-c", "user.name=Test",
        "-c", "user.email=test@example.invalid", "commit", "-m", "baseline",
    ), check=True, capture_output=True)
    workspace = tmp_path / "workspace"
    root, _, _ = preflight.export_baseline(repo, workspace)
    outside = tmp_path / "outside"
    root.rename(outside)
    root.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        preflight.export_baseline(repo, workspace)


def test_export_baseline_rejects_executable_mode_drift(tmp_path):
    repo = tmp_path / "repo"; repo.mkdir()
    subprocess.run(("git", "init", str(repo)), check=True, capture_output=True)
    (repo / "loom-code").mkdir()
    marker = repo / "loom-code" / "marker"
    marker.write_text("baseline", encoding="utf-8")
    subprocess.run(("git", "-C", str(repo), "add", "loom-code/marker"), check=True)
    subprocess.run((
        "git", "-C", str(repo), "-c", "user.name=Test",
        "-c", "user.email=test@example.invalid", "commit", "-m", "baseline",
    ), check=True, capture_output=True)
    workspace = tmp_path / "workspace"
    root, _, _ = preflight.export_baseline(repo, workspace)
    cached_marker = root / "marker"
    cached_marker.chmod(cached_marker.stat().st_mode | 0o100)
    with pytest.raises(ValueError, match="does not match"):
        preflight.export_baseline(repo, workspace)


def test_bound_cache_rejects_changed_invocation_and_structured_failure(tmp_path):
    raw = tmp_path / "run.jsonl"
    provenance = {
        "baseline_commit": "c", "baseline_tree": "t", "corpus_sha256": "h",
        "prompt_id": 1, "prompt_sha256": "p", "expected_behavior_sha256": "e",
        "host": "claude", "model": "haiku", "replicate": 0,
        "argv_semantics": {"max_turns": 12}, "timeout_seconds": 180,
    }
    fingerprint = preflight.provenance_fingerprint(provenance)
    preflight.write_raw_with_metadata(
        raw,
        preflight.RunOutcome('{"type":"result","subtype":"success"}\n', 0, "completed"),
        provenance, fingerprint,
    )
    changed = {**provenance, "argv_semantics": {"max_turns": 4}}
    assert preflight.load_bound_raw(raw, changed) is None

    preflight.write_raw_with_metadata(
        raw,
        preflight.RunOutcome(
            '{"type":"result","subtype":"error_max_turns"}\n', 0, "completed"
        ),
        provenance, fingerprint,
    )
    assert preflight.load_bound_raw(raw, provenance) is None


def test_claude_run_does_not_touch_codex_auth_link(monkeypatch, tmp_path):
    source = tmp_path / "auth-source.json"
    source.write_text("{}", encoding="utf-8")
    codex_link = tmp_path / "codex-home" / "auth.json"
    codex_link.parent.mkdir()
    codex_link.symlink_to(source)
    invocation = preflight.HostInvocation(
        "claude", "baseline", tmp_path, {"query": "q"}, 0,
        ("claude",), None, {},
    )
    expected = preflight.RunOutcome(
        '{"type":"result","subtype":"success"}\n', 0, "completed"
    )
    monkeypatch.setattr(preflight, "_run_bounded", lambda *_: expected)
    assert preflight._run_with_auth(invocation, 10, source) == expected
    assert codex_link.is_symlink()


def test_external_cli_surfaces_have_live_help_grounding():
    """Grounding: live BSD `wc -w`, `claude --help`, `codex exec --help`,
    `codex plugin marketplace add --help`, and `codex plugin add --help`
    captured on 2026-08-26; production argv mirrors those installed CLIs.
    """
    assert preflight.TARGETS


def test_merge_refuses_conflicts_incomplete_and_host_errors(tmp_path):
    contract = {
        "host": "claude", "model": "haiku", "argv_semantics": {},
        "timeout_seconds": 1,
    }
    base = {
        "schema_version": 2, "models": {"claude": "haiku", "codex": "gpt-5.6-luna"},
        "capture_contracts": [contract],
        "replicates_per_host": 2, "baseline": {"commit": "c", "tree": "t"},
        "raw_workspace": "one", "skills": {},
    }
    a = tmp_path / "a.json"; b = tmp_path / "b.json"; out = tmp_path / "out.json"
    a.write_text(json.dumps(base), encoding="utf-8")
    b.write_text(json.dumps({**base, "models": {"claude": "other"}, "raw_workspace": "two"}), encoding="utf-8")
    with pytest.raises(ValueError, match="models"):
        preflight.merge_records([a, b], out, expected_targets=())

    bad = {**base, "skills": {"demo": {"corpus_sha256": "x", "runs": [{
        "status": "host-error", "exit_code": 1, "host": "claude",
        "model": "haiku",
        "capture_contract_fingerprint": preflight.capture_contract_fingerprint(contract),
    }]}}}
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
    contracts = [
        {"host": host, "model": model, "argv_semantics": {}, "timeout_seconds": 1}
        for host, model in (("claude", "haiku"), ("codex", "gpt-5.6-luna"))
    ]
    contract_fingerprints = {
        contract["host"]: preflight.capture_contract_fingerprint(contract)
        for contract in contracts
    }
    runs = []
    for prompt in corpus["prompts"]:
        for host in ("claude", "codex"):
            for replicate in (0, 1):
                runs.append({
                    "prompt_id": prompt["id"], "host": host,
                    "model": "haiku" if host == "claude" else "gpt-5.6-luna",
                    "replicate": replicate, "status": "completed", "exit_code": 0,
                    "fingerprint": "f" * 64, "raw_sha256": "a" * 64,
                    "expected_behavior_sha256": preflight.sha256_text(prompt["expected_behavior"]),
                        "raw_metadata": "workspace/raw.meta.json",
                        "capture_contract_fingerprint": contract_fingerprints[host],
                    "observable": {"fired": True, "result_subtype": "ok", "tool_count": 3},
                })
    snapshot = {
        "corpus_sha256": preflight.sha256_bytes(corpus_path.read_bytes()),
        "word_count": 10, "runs": runs,
    }
    part = {
        "schema_version": 2, "models": {"claude": "haiku", "codex": "gpt-5.6-luna"},
        "capture_contracts": contracts,
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

    bad_model = json.loads(json.dumps(part))
    bad_model["skills"]["demo"]["runs"][0]["model"] = "unapproved"
    a.write_text(json.dumps(bad_model), encoding="utf-8")
    with pytest.raises(ValueError, match="model header mismatch"):
        preflight.merge_records(
            [a], out, expected_targets=("demo",), corpora_root=tmp_path
        )

    contractless = json.loads(json.dumps(part))
    contractless.pop("capture_contracts")
    a.write_text(json.dumps(contractless), encoding="utf-8")
    with pytest.raises(ValueError, match="capture contracts missing"):
        preflight.merge_records(
            [a], out, expected_targets=("demo",), corpora_root=tmp_path
        )

    swapped = json.loads(json.dumps(part))
    for run in swapped["skills"]["demo"]["runs"]:
        other = "codex" if run["host"] == "claude" else "claude"
        run["capture_contract_fingerprint"] = contract_fingerprints[other]
    a.write_text(json.dumps(swapped), encoding="utf-8")
    with pytest.raises(ValueError, match="run capture contract mismatch"):
        preflight.merge_records(
            [a], out, expected_targets=("demo",), corpora_root=tmp_path
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


def test_codex_provenance_does_not_claim_claude_turn_limit():
    prompt = {"id": 1, "prompt": "probe", "expected_behavior": "route"}
    common = {
        "commit": "c", "tree": "t", "corpus_sha256": "h", "prompt": prompt,
        "model": "gpt-5.6-luna", "replicate": 0, "timeout_seconds": 180,
    }
    codex_four = preflight.invocation_provenance(
        **common, host="codex", max_turns=4
    )
    codex_ninety_nine = preflight.invocation_provenance(
        **common, host="codex", max_turns=99
    )
    assert codex_four["argv_semantics"] == codex_ninety_nine["argv_semantics"]
    assert "max_turns" not in codex_four["argv_semantics"]

    header_contracts = preflight.capture_contracts_for_models(
        {"claude": "haiku", "codex": "gpt-5.6-luna"},
        max_turns=4, timeout_seconds=180,
    )
    assert preflight.capture_contract(codex_four) in header_contracts


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
            "capture_contract_fingerprint": preflight.capture_contract_fingerprint(
                preflight.capture_contract(provenance)
            ),
        "raw": "workspace/raw/demo/p1-claude-r0.jsonl",
        "raw_metadata": "workspace/raw/demo/p1-claude-r0.meta.json",
    }
    record = {
        "schema_version": 2, "baseline": {"commit": "c", "tree": "t"},
        "models": {"claude": "haiku", "codex": "gpt-5.6-luna"},
        "capture_contracts": [{
            "host": "claude", "model": "haiku",
            "argv_semantics": provenance["argv_semantics"],
            "timeout_seconds": provenance["timeout_seconds"],
        }],
        "skills": {"demo": {"corpus_sha256": provenance["corpus_sha256"], "runs": [run]}},
    }
    record_path = tmp_path / "record.json"
    record_path.write_text(json.dumps(record), encoding="utf-8")
    assert preflight.verify_raw_record(
        record_path, tmp_path / "raw-base", tmp_path / "corpora"
    ) == 1

    wrong_header = json.loads(record_path.read_text(encoding="utf-8"))
    wrong_header["models"]["claude"] = "wrong"
    record_path.write_text(json.dumps(wrong_header), encoding="utf-8")
    with pytest.raises(ValueError, match="model header mismatch"):
        preflight.verify_raw_record(
            record_path, tmp_path / "raw-base", tmp_path / "corpora"
        )

    wrong_contract = json.loads(json.dumps(record))
    wrong_contract["capture_contracts"][0]["timeout_seconds"] = 1
    record_path.write_text(json.dumps(wrong_contract), encoding="utf-8")
    with pytest.raises(ValueError, match="capture contract mismatch"):
        preflight.verify_raw_record(
            record_path, tmp_path / "raw-base", tmp_path / "corpora"
        )

    missing_contracts = json.loads(json.dumps(record))
    missing_contracts.pop("capture_contracts")
    record_path.write_text(json.dumps(missing_contracts), encoding="utf-8")
    with pytest.raises(ValueError, match="capture contracts missing"):
        preflight.verify_raw_record(
            record_path, tmp_path / "raw-base", tmp_path / "corpora"
        )

    missing_run_contract = json.loads(json.dumps(record))
    missing_run_contract["skills"]["demo"]["runs"][0].pop(
        "capture_contract_fingerprint", None
    )
    record_path.write_text(json.dumps(missing_run_contract), encoding="utf-8")
    with pytest.raises(ValueError, match="run capture contract mismatch"):
        preflight.verify_raw_record(
            record_path, tmp_path / "raw-base", tmp_path / "corpora"
        )

    record_path.write_text(json.dumps(record), encoding="utf-8")
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


def test_verify_record_raw_rejects_empty_evidence(tmp_path):
    record = tmp_path / "empty.json"
    record.write_text(json.dumps({"schema_version": 2, "skills": {}}), encoding="utf-8")
    with pytest.raises(ValueError, match="no skill evidence"):
        preflight.verify_raw_record(record, tmp_path)


def test_verify_record_raw_rejects_incomplete_run_matrix(tmp_path):
    skill_dir = tmp_path / "corpora" / "demo"
    skill_dir.mkdir(parents=True)
    corpus = _corpus(skill_dir)
    record = tmp_path / "incomplete.json"
    record.write_text(json.dumps({
        "schema_version": 2,
        "replicates_per_host": 2,
        "capture_contracts": [{
            "host": "claude", "model": "haiku", "argv_semantics": {},
            "timeout_seconds": 1,
        }],
        "skills": {"demo": {
            "corpus_sha256": preflight.sha256_bytes(corpus.read_bytes()),
            "runs": [],
        }},
    }), encoding="utf-8")
    with pytest.raises(ValueError, match="incomplete run matrix"):
        preflight.verify_raw_record(
            record, tmp_path, tmp_path / "corpora", expected_targets=("demo",)
        )


def test_capture_completion_gate_rejects_host_errors():
    record = {"skills": {"demo": {"runs": [
        {"status": "completed", "exit_code": 0},
        {"status": "host-error", "exit_code": 0},
    ]}}}
    with pytest.raises(ValueError, match="capture incomplete"):
        preflight.require_complete_capture(record)


def test_external_path_rejects_symlink_escape(tmp_path):
    raw_base = tmp_path / "raw-base"
    outside = tmp_path / "outside"
    raw_base.mkdir(); outside.mkdir()
    (raw_base / "link").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="escapes raw evidence root"):
        preflight._external_path(raw_base, "link/evidence.jsonl")
