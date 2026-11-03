"""Offline behavior checks for the advertised creator commands."""

import importlib
import io
import json
import subprocess
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor
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
def optimizer(monkeypatch, tmp_path):
    monkeypatch.syspath_prepend(str(CREATOR))
    with patch.dict(sys.modules):
        for name in list(sys.modules):
            if name == "scripts" or name.startswith("scripts."):
                del sys.modules[name]
        module = importlib.import_module("scripts.run_loop")
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(importlib.import_module("scripts.run_eval"), "ProcessPoolExecutor", ThreadPoolExecutor)
        yield module


def optimize(module, skill, monkeypatch, capsys):
    cases = [{"query": f"query-{i}", "should_trigger": i % 2 == 0} for i in range(10)]
    eval_path = skill.parent / "eval.json"
    eval_path.write_text(json.dumps(cases))
    monkeypatch.setattr(sys, "argv", ["run_loop", "--eval-set", str(eval_path),
        "--skill-path", str(skill), "--model", "offline-fixture", "--report", "none",
        "--results-dir", str(skill.parent / "results"), "--num-workers", "1",
        "--runs-per-query", "1", "--max-iterations", "3"])
    module.main()
    output = json.loads(capsys.readouterr().out)
    assert json.loads(next((skill.parent / "results").rglob("results.json")).read_text()) == output
    assert not list(skill.parent.rglob("*.html"))
    return output


@pytest.mark.parametrize("entry, baseline", [
    ("package_skill", None), ("aggregate_benchmark", "without_skill"),
    ("aggregate_benchmark", "old_skill"), ("run_loop", None),
])
def test_creator_commands_valid(entry, baseline, tmp_path, skill, request, monkeypatch, capsys):
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
        for config, rates in [("with_skill", [0.5, 1.0]), (baseline, [0.0, 0.5])]:
            for index, rate in enumerate(rates, 1):
                run = tmp_path / f"eval-7/{config}/run-{index}"
                run.mkdir(parents=True)
                multiplier = 2 if config == "with_skill" else 1
                (run / "grading.json").write_text(json.dumps({
                    "summary": {"pass_rate": rate, "passed": int(rate * 2), "failed": int(2 - rate * 2), "total": 2},
                    "expectations": [{"text": "fixture", "passed": bool(rate), "evidence": "offline"}],
                    "timing": {"total_duration_seconds": index * multiplier if config == "with_skill" else 0},
                    "execution_metrics": {"output_chars": index * 1000},
                }))
                (run / "timing.json").write_text(json.dumps({"total_duration_seconds": index * 10 if config == "with_skill" else index, "total_tokens": index * multiplier * 5}))
        result = command(entry, tmp_path, "--skill-name", "example-skill")
        assert result.returncode == 0, result.stderr + result.stdout
        benchmark = json.loads((tmp_path / "benchmark.json").read_text())
        assert benchmark["metadata"]["evals_run"] == [7]
        assert benchmark["metadata"]["runs_per_configuration"] == 2
        assert len(benchmark["runs"]) == 4
        summary = benchmark["run_summary"]
        assert summary["with_skill"]["pass_rate"] == {"mean": 0.75, "stddev": 0.3536, "min": 0.5, "max": 1.0}
        assert summary["with_skill"]["time_seconds"]["mean"] == 3
        assert summary["with_skill"]["tokens"]["mean"] == 15
        assert [run["result"]["tokens"] for run in benchmark["runs"] if run["configuration"] == "with_skill"] == [10, 20]
        assert summary["delta"]["pass_rate"] == "+0.50"
        assert summary["delta"]["time_seconds"] == "+1.5"
        assert summary["delta"]["tokens"] == "+8"
        markdown = (tmp_path / "benchmark.md").read_text()
        baseline_label = baseline.replace("_", " ").title()
        assert f"| Metric | With Skill | {baseline_label} | Delta |" in markdown
        assert "75% ± 35%" in markdown
        assert "(2 runs each per configuration)" in markdown
        assert "| Tokens | 15 ± 7 | 8 ± 4 | +8 |" in markdown
        for captures, values in [
            ([{"total_tokens": 0}, {}], [0, None]),
            ([{"total_tokens": 10}, {}], [10, None]),
            ([{"total_tokens": 0}, {"total_tokens": 0}], [0, 0]),
            ([None, "malformed"], [None, None]),
            ([{}, {"total_tokens": None}], [None, None]),
            ([[], False], [None, None]),
            ([{"total_tokens": "10"}, {"total_tokens": True}], [None, None]),
            ([{"total_tokens": -1}, {"total_tokens": float("nan")}], [None, None]),
        ]:
            for index, captured in enumerate(captures, 1):
                timing = tmp_path / f"eval-7/with_skill/run-{index}/timing.json"
                if captured is None:
                    timing.unlink()
                else:
                    timing.write_text("{" if captured == "malformed" else json.dumps(captured))
            result = command(entry, tmp_path)
            assert result.returncode == 0, result.stderr + result.stdout
            benchmark = json.loads((tmp_path / "benchmark.json").read_text())
            assert [run["result"]["tokens"] for run in benchmark["runs"] if run["configuration"] == "with_skill"] == values
            token_stats = benchmark["run_summary"]["with_skill"]["tokens"]
            count = sum(value is not None for value in values)
            measured = next((value for value in values if value is not None), None)
            expected_stats = {"mean": measured, "stddev": 0 if count else None, "min": measured, "max": measured}
            assert token_stats == expected_stats | {"sample_count": count, "total_count": 2}
            assert benchmark["run_summary"]["delta"]["tokens"] == ("-8" if count == 2 else None)
            rendered = "0 ± 0" if count == 2 else f"{measured} ± 0 (partial: 1/2 captured)" if count else "not captured (0/2)"
            delta = "-8" if count == 2 else "not captured"
            assert f"| Tokens | {rendered} | 8 ± 4 | {delta} |" in (tmp_path / "benchmark.md").read_text()
            if count == 2:
                timing = tmp_path / f"eval-7/{baseline}/run-2/timing.json"
                original = timing.read_text()
                timing.write_text("{}")
                assert command(entry, tmp_path).returncode == 0
                assert json.loads((tmp_path / "benchmark.json").read_text())["run_summary"]["delta"]["tokens"] is None
                assert "| Tokens | 0 ± 0 | 5 ± 0 (partial: 1/2 captured) | not captured |" in (tmp_path / "benchmark.md").read_text()
                timing.write_text(original)
        for grading in (tmp_path / "eval-7").rglob("grading.json"):
            copied = tmp_path / "eval-8" / grading.relative_to(tmp_path / "eval-7")
            copied.parent.mkdir(parents=True)
            copied.write_text(grading.read_text())
        result = command(entry, tmp_path)
        assert result.returncode == 0, result.stderr + result.stdout
        assert json.loads((tmp_path / "benchmark.json").read_text())["metadata"]["runs_per_configuration"] == 2
        for index in [2, 1]:
            (tmp_path / f"eval-8/{baseline}/run-{index}/grading.json").unlink()
            result = command(entry, tmp_path)
            assert result.returncode == 0, result.stderr + result.stdout
            assert json.loads((tmp_path / "benchmark.json").read_text())["metadata"]["runs_per_configuration"] is None
            assert "unequal run counts per eval/configuration; see runs" in (tmp_path / "benchmark.md").read_text()
        for grading in tmp_path.rglob("grading.json"):
            grading.unlink()
        result = command(entry, tmp_path)
        assert result.returncode == 0, result.stderr + result.stdout
        assert json.loads((tmp_path / "benchmark.json").read_text())["metadata"]["runs_per_configuration"] == 0
        empty_summary = json.loads((tmp_path / "benchmark.json").read_text())["run_summary"]
        assert empty_summary["with_skill"]["tokens"] == dict.fromkeys(["mean", "stddev", "min", "max"], None) | {"sample_count": 0, "total_count": 0}
        assert empty_summary["delta"]["tokens"] is None
        assert "| Tokens | not captured (0/0) | not captured (0/0) | not captured |" in (tmp_path / "benchmark.md").read_text()
        assert "(0 runs each per configuration)" in (tmp_path / "benchmark.md").read_text()
    else:
        module = request.getfixturevalue("optimizer")
        evaluated, improved = [], []

        def evaluate(query, skill_name, description, *args):
            evaluated.append((query, description))
            return int(query.split("-")[1]) % 2 != 0

        def improve(**kwargs):
            improved.append(kwargs)
            train_queries = {row["query"] for row in kwargs["eval_results"]["results"]}
            heldout = {f"query-{i}" for i in range(10)} - train_queries
            assert len(train_queries) == 6 and len(heldout) == 4
            assert all(query not in json.dumps(kwargs, default=str) for query in heldout)
            for history in kwargs["history"]:
                assert not any(key.startswith("test_") for key in history)
                assert {row["query"] for row in history["results"]} == train_queries
            return f"Candidate {len(improved)}"

        monkeypatch.setattr(importlib.import_module("scripts.run_eval"), "run_single_query", evaluate)
        monkeypatch.setattr(module, "improve_description", improve)
        output = optimize(module, skill, monkeypatch, capsys)
        assert output["exit_reason"] == "max_iterations (3)"
        assert output["iterations_run"] == 3 and len(evaluated) == 30
        assert len(improved) == 2
        assert [item["description"] for item in output["history"]] == ["Original description", "Candidate 1", "Candidate 2"]
        assert output["best_description"] == "Original description"
        assert output["train_size"] == 6 and output["test_size"] == 4


@pytest.mark.parametrize("entry", ["package_skill", "aggregate_benchmark", "run_loop"])
def test_creator_commands_invalid(entry, tmp_path, skill, request, monkeypatch, capsys):
    if entry in {"package_skill", "aggregate_benchmark"}:
        result = command(entry, tmp_path / "missing")
        assert result.returncode != 0
        assert "not found" in result.stdout.lower()
        assert not list(tmp_path.rglob("*.skill"))
        assert not (tmp_path / "benchmark.json").exists()
    else:
        module = request.getfixturevalue("optimizer")

        def failed_backend(*args):
            raise RuntimeError("offline evaluator failed")

        def forbidden_improvement(**kwargs):
            pytest.fail("Failed evaluation must not reach improvement")

        monkeypatch.setattr(importlib.import_module("scripts.run_eval"), "run_single_query", failed_backend)
        monkeypatch.setattr(module, "improve_description", forbidden_improvement)
        with pytest.raises(RuntimeError, match="offline evaluator failed"):
            optimize(module, skill, monkeypatch, capsys)
        assert not list(tmp_path.rglob("results.json"))
        assert "all_passed" not in capsys.readouterr().out
        (skill / "SKILL.md").unlink()
        with pytest.raises(SystemExit) as error:
            module.main()
        assert error.value.code == 1


@pytest.mark.parametrize("entry", ["run_eval", "run_loop"])
@pytest.mark.parametrize("outcome", ["success", "trigger", "early_no", "early_trigger", "nonzero", "error", "incomplete", "timeout"])
def test_creator_evaluation_completion(entry, outcome, optimizer, skill, monkeypatch, capsys):
    evaluator = importlib.import_module("scripts.run_eval")
    module = importlib.import_module(f"scripts.{entry}")
    eval_path = skill.parent / "negative.json"
    eval_path.write_text(json.dumps([{"query": "negative query", "should_trigger": False}]))
    chunks = []

    class Output(io.BytesIO):
        def fileno(self):
            return 0

    class Process:
        def __init__(self, *args, **kwargs):
            name = next((Path(kwargs["cwd"]) / ".claude/commands").glob("*.md")).stem
            events = {
                "success": {"type": "result", "subtype": "success", "is_error": False},
                "error": {"type": "result", "subtype": "error_during_execution", "is_error": True},
                "early_no": {"type": "stream_event", "event": {"type": "message_stop"}},
                "trigger": {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Skill", "input": {"skill": name}}]}},
            }
            events["early_trigger"] = {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read", "input": {"file_path": name + ".md"}}]}}
            payload = json.dumps(events.get(outcome, {"type": "system"})).encode()
            self.stdout = Output(payload)
            chunks.append(payload + b"\n")
            self.returncode = None if outcome in {"timeout", "early_no", "early_trigger"} else int(outcome == "nonzero")

        def poll(self):
            return self.returncode

        def kill(self):
            self.returncode = -9

        def wait(self):
            return self.returncode

    monkeypatch.setattr(evaluator.subprocess, "Popen", Process)
    monkeypatch.setattr(evaluator.select, "select", lambda *args: ([args[0][0]], [], []))
    monkeypatch.setattr(evaluator.os, "read", lambda *args: chunks.pop(0) if chunks else b"")
    argv = [entry, "--eval-set", str(eval_path), "--skill-path", str(skill), "--num-workers", "1", "--runs-per-query", "1", "--timeout", "0" if outcome == "timeout" else "1"]
    if entry == "run_loop":
        argv += ["--model", "offline", "--report", "none", "--holdout", "0", "--max-iterations", "1", "--results-dir", str(skill.parent / "saved")]
    monkeypatch.setattr(sys, "argv", argv)
    if outcome in {"nonzero", "error", "incomplete", "timeout"}:
        with pytest.raises(RuntimeError):
            module.main()
        assert not list(skill.parent.rglob("results.json"))
        assert not capsys.readouterr().out
    else:
        module.main()
        output = json.loads(capsys.readouterr().out)
        expected = outcome in {"success", "early_no"}
        if entry == "run_eval":
            assert output["results"][0]["pass"] == expected
        else:
            assert output["best_score"] == ("1/1" if expected else "0/1")
    assert not list(skill.parent.rglob(".claude/commands/*.md"))


@pytest.mark.parametrize("candidate, comment, valid", [
    ("Converts CSV files when streaming JSONL is needed.", "", True),
    ("x" * 251, "", False),
    ("x" * 251, "# KEEP: Retains CSV, JSONL and router configuration trigger surfaces\n", True),
    ("x" * 1024, "# KEEP: Retains CSV, JSONL and streaming trigger surfaces\n", True),
    ("x" * 1025, "# KEEP: Retains CSV, JSONL and streaming trigger surfaces\n", False),
    ("x" * 500, "# Firing evidence: 87% match rate from support-ticket A/B corpus\n", True),
    ("x" * 501, "# Firing evidence: 87% match rate from support-ticket A/B corpus\n", False),
    ("x" * 251, "# Router: Retains CSV, JSONL and streaming trigger surfaces\n", False),
    ("x" * 251, "# Firing evidence:\n", False),
    ("<broken>text", "", False),
    ("", "", False),
])
def test_creator_optimizer_authority(candidate, comment, valid, optimizer, skill, monkeypatch, capsys):
    generator = importlib.import_module("scripts.improve_description")
    content = "---\nname: example-skill\n" + comment + "description: Original description\n---\nBody\n"
    (skill / "SKILL.md").write_text(content)
    evaluation = {"description": "Original description", "summary": {"passed": 0, "failed": 1, "total": 1}, "results": []}
    eval_path = skill.parent / "generation.json"
    eval_path.write_text(json.dumps(evaluation))
    prompts = []

    def generate(prompt, model):
        prompts.append(prompt)
        if valid and len(prompts) == 1:
            return "<new_description><invalid></new_description>"
        return f"<new_description>{candidate}</new_description>"

    monkeypatch.setattr(generator, "_call_claude", generate)
    monkeypatch.setattr(sys, "argv", ["improve_description", "--eval-results", str(eval_path), "--skill-path", str(skill), "--model", "offline"])
    if valid:
        generator.main()
        assert json.loads(capsys.readouterr().out)["description"] == candidate
    else:
        with pytest.raises(ValueError, match="description"):
            generator.main()
        assert not capsys.readouterr().out
    authority = (CREATOR / "references/description-design.md").read_text()
    assert authority in prompts[0]
    assert "third-person" in prompts[0]
    assert "100-200 words" not in prompts[0]
    assert "phrased in the imperative" not in prompts[0]
    assert authority in prompts[1] and "ineligible" in prompts[1]
    assert (skill / "SKILL.md").read_text() == content
    if valid:
        invalid_baseline = "<invalid>baseline"
        (skill / "SKILL.md").write_text(content.replace("Original description", invalid_baseline))
        monkeypatch.setattr(importlib.import_module("scripts.run_eval"), "run_single_query",
                            lambda query, *args: int(query.split("-")[1]) % 2 == 0)
        output = optimize(optimizer, skill, monkeypatch, capsys)
        assert output["iterations_run"] == 2
        assert output["best_description"] == candidate
        assert output["history"][0]["eligible"] is False
        assert output["history"][1]["eligible"] is True
    else:
        (skill / "SKILL.md").write_text(content.replace("Original description", "<invalid>baseline"))
        monkeypatch.setattr(importlib.import_module("scripts.run_eval"), "run_single_query", lambda *args: True)
        monkeypatch.setattr(sys, "argv", ["run_loop", "--eval-set", str(eval_path), "--skill-path", str(skill),
                            "--model", "offline", "--report", "none", "--holdout", "0", "--max-iterations", "1"])
        eval_path.write_text(json.dumps([{"query": "baseline", "should_trigger": True}]))
        with pytest.raises(ValueError, match="No eligible description"):
            optimizer.main()
        assert not capsys.readouterr().out
