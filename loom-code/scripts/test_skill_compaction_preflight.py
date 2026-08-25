import json
from pathlib import Path


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
