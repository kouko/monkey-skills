"""Exercise preference export and inactive trainer against the same raw records."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPTS = Path(__file__).resolve().parents[1] / "skills/skill-tuning/scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("judge_train_stub", SCRIPTS / "judge_train_stub.py")
stub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stub)


def record(verdict="ADOPT", picked="candidate"):
    return {"skill": "example", "verdict": verdict, "user_pick": "B",
            "user_pick_identity": picked, "test_prompt_hash": "prompt-hash",
            "variants_shown": [
                {"identity": "baseline", "skill_md_hash": "baseline-hash"},
                {"identity": "candidate", "skill_md_hash": "candidate-hash"},
                {"identity": "other", "skill_md_hash": "other-hash"}]}


def run(script, *args):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                          capture_output=True, text=True)


@pytest.mark.parametrize("verdict,picked", [("ADOPT", "candidate"), ("DROP", "baseline")])
def test_explicit_single_preferences_export(tmp_path, verdict, picked):
    entry = record(verdict, picked)
    original = copy.deepcopy(entry)
    log, out, model = (tmp_path / name for name in ("log.jsonl", "pairs.json", "model.pt"))
    raw = ("  " + json.dumps(entry) + "\n\n").encode()
    log.write_bytes(raw)
    result = run("preference_log.py", "export-for-training", log, "--skill", "example",
                 "--out", out, "--min-entries", 1)
    assert result.returncode == 0, result.stderr
    exported = json.loads(out.read_text())
    assert exported["n_entries_used"] == 1
    assert exported["n_entries_skipped"] == 0
    assert exported["n_training_pairs"] == 2
    assert {p["preferred_skill_md_hash"] for p in exported["training_pairs"]} == {picked + "-hash"}
    pairs = stub.extract_preference_pairs([entry], "example")
    assert {p["preferred"] for p in pairs} == {picked} and len(pairs) == 2
    trained = run("judge_train_stub.py", "--log", log, "--skill", "example",
                  "--out", model, "--min-entries", 1)
    assert "Threshold met (1 ≥ 1)" in trained.stderr
    assert "not implemented" in trained.stderr and not model.exists()
    assert log.read_bytes() == raw and entry == original


@pytest.mark.parametrize("invalid", ["none", "multiple", "refine", "missing", "hash",
                                     "prompt_hash", "same", "shape", "duplicate_pick"])
def test_unusable_preferences_not_ready(tmp_path, invalid):
    bad = record()
    if invalid in {"none", "multiple", "refine"}:
        bad["user_pick"] = bad["user_pick_identity"] = invalid
    elif invalid == "missing":
        bad["user_pick_identity"] = "absent"
    elif invalid == "hash":
        bad["variants_shown"][1].pop("skill_md_hash")
    elif invalid == "prompt_hash":
        bad.pop("test_prompt_hash")
    elif invalid == "same":
        for variant in bad["variants_shown"]:
            variant["skill_md_hash"] = "same"
    elif invalid == "shape":
        bad["variants_shown"] = ["baseline", "candidate"]
    else:
        bad["variants_shown"].append(dict(bad["variants_shown"][1]))
    assert stub.extract_preference_pairs([bad], "example") == []
    many = record()
    many["variants_shown"] += [{"identity": f"v{i}", "skill_md_hash": f"hash-{i}"} for i in range(1000)]
    log, out, model = (tmp_path / name for name in ("log.jsonl", "pairs.json", "model.pt"))
    raw = (json.dumps(bad) + "\n" + json.dumps(many) + "\n").encode()
    log.write_bytes(raw)
    exported = run("preference_log.py", "export-for-training", log, "--skill", "example", "--out", out)
    trained = run("judge_train_stub.py", "--log", log, "--skill", "example", "--out", model)
    for result in (exported, trained):
        assert result.returncode == 1, result.stderr
        assert "1 usable" in result.stderr and "1 skipped" in result.stderr
        assert "1002 pairs" in result.stderr and "1000" in result.stderr
    assert not out.exists() and not model.exists() and log.read_bytes() == raw
