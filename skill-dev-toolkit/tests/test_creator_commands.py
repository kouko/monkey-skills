"""Offline behavior checks for the advertised creator commands."""

import importlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest


CREATOR = Path(__file__).resolve().parents[1] / "skills/skill-creator-advance"


def command(module, *args):
    return subprocess.run(
        [sys.executable, "-m", f"scripts.{module}", *map(str, args)],
        cwd=CREATOR, capture_output=True, text=True, timeout=10,
    )


@pytest.fixture
def skill(tmp_path):
    path = tmp_path / "example-skill"
    path.mkdir()
    (path / "SKILL.md").write_text(
        "---\nname: example-skill\ndescription: Original description\n---\nBody\n"
    )
    return path


@pytest.fixture
def optimizer(monkeypatch):
    monkeypatch.syspath_prepend(str(CREATOR))
    with patch.dict(sys.modules):
        for name in list(sys.modules):
            if name == "scripts" or name.startswith("scripts."):
                del sys.modules[name]
        module = importlib.import_module("scripts.run_loop")
        monkeypatch.setattr(module, "find_project_root", lambda: CREATOR)
        yield module


def optimize(module, skill, **kwargs):
    cases = [{"query": f"query-{i}", "should_trigger": i % 2 == 0} for i in range(10)]
    return module.run_loop(
        eval_set=cases, skill_path=skill, description_override=None,
        num_workers=1, timeout=1, max_iterations=3, runs_per_query=1,
        trigger_threshold=0.5, holdout=0.4, model="offline-fixture",
        verbose=False, **kwargs,
    )


@pytest.mark.parametrize("entry", ["package_skill", "aggregate_benchmark", "run_loop"])
def test_creator_commands_valid(entry, tmp_path, skill, request, monkeypatch):
    if entry == "package_skill":
        for relative in ["references/guide.md", "references/evals/keep.txt", "evals/case.json", "__pycache__/cache.pyc"]:
            path = skill / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(relative)
        result = command(entry, skill, tmp_path / "dist")
        assert result.returncode == 0, result.stderr + result.stdout
        with zipfile.ZipFile(tmp_path / "dist/example-skill.skill") as archive:
            assert set(archive.namelist()) == {
                "example-skill/SKILL.md", "example-skill/references/guide.md",
                "example-skill/references/evals/keep.txt",
            }
            assert archive.read("example-skill/SKILL.md").decode() == (skill / "SKILL.md").read_text()
    elif entry == "aggregate_benchmark":
        for config, rates in [("with_skill", [0.5, 1.0]), ("without_skill", [0.0, 0.5])]:
            for index, rate in enumerate(rates, 1):
                run = tmp_path / f"eval-7/{config}/run-{index}"
                run.mkdir(parents=True)
                (run / "grading.json").write_text(json.dumps({
                    "summary": {"pass_rate": rate, "passed": int(rate * 2), "failed": int(2 - rate * 2), "total": 2},
                    "expectations": [{"text": "fixture", "passed": bool(rate), "evidence": "offline"}],
                }))
                (run / "timing.json").write_text(json.dumps({"total_duration_seconds": index * 2, "total_tokens": index * 10}))
        result = command(entry, tmp_path, "--skill-name", "example-skill")
        assert result.returncode == 0, result.stderr + result.stdout
        benchmark = json.loads((tmp_path / "benchmark.json").read_text())
        assert benchmark["metadata"]["evals_run"] == [7]
        assert len(benchmark["runs"]) == 4
        summary = benchmark["run_summary"]
        assert summary["with_skill"]["pass_rate"] == {"mean": 0.75, "stddev": 0.3536, "min": 0.5, "max": 1.0}
        assert summary["with_skill"]["time_seconds"]["mean"] == 3
        assert summary["with_skill"]["tokens"]["mean"] == 15
        assert summary["delta"]["pass_rate"] == "+0.50"
        assert "75% ± 35%" in (tmp_path / "benchmark.md").read_text()
    else:
        module = request.getfixturevalue("optimizer")
        evaluated, improved = [], []

        def evaluate(**kwargs):
            evaluated.append(kwargs)
            return {"results": [dict(case, **{"pass": False}) for case in kwargs["eval_set"]]}

        def improve(**kwargs):
            improved.append(kwargs)
            train_queries = {row["query"] for row in kwargs["eval_results"]["results"]}
            heldout = {row["query"] for row in evaluated[-1]["eval_set"]} - train_queries
            assert len(train_queries) == 6 and len(heldout) == 4
            assert all(query not in json.dumps(kwargs) for query in heldout)
            for history in kwargs["history"]:
                assert not any(key.startswith("test_") for key in history)
                assert {row["query"] for row in history["results"]} == train_queries
            return f"Candidate {len(improved)}"

        monkeypatch.setattr(module, "run_eval", evaluate)
        monkeypatch.setattr(module, "improve_description", improve)
        output = optimize(module, skill)
        assert output["exit_reason"] == "max_iterations (3)"
        assert output["iterations_run"] == len(evaluated) == 3
        assert len(improved) == 2
        assert [item["description"] for item in output["history"]] == ["Original description", "Candidate 1", "Candidate 2"]
        assert output["best_description"] == "Original description"
        assert output["train_size"] == 6 and output["test_size"] == 4


@pytest.mark.parametrize("entry", ["package_skill", "aggregate_benchmark", "run_loop"])
def test_creator_commands_invalid(entry, tmp_path, skill, request, monkeypatch):
    if entry in {"package_skill", "aggregate_benchmark"}:
        result = command(entry, tmp_path / "missing")
        assert result.returncode != 0
        assert "not found" in result.stdout.lower()
        assert not list(tmp_path.rglob("*.skill"))
        assert not (tmp_path / "benchmark.json").exists()
    else:
        module = request.getfixturevalue("optimizer")

        def failed_backend(**kwargs):
            raise RuntimeError("offline evaluator failed")

        def forbidden_improvement(**kwargs):
            pytest.fail("Failed evaluation must not reach improvement")

        monkeypatch.setattr(module, "run_eval", failed_backend)
        monkeypatch.setattr(module, "improve_description", forbidden_improvement)
        with pytest.raises(RuntimeError, match="offline evaluator failed"):
            optimize(module, skill)
