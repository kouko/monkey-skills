#!/usr/bin/env python3
"""Adversarial integrity checks for this frozen experiment record."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def main() -> None:
    manifest = load("corpus-manifest.json")
    oracle = load("oracle.json")
    metrics = load("metrics.json")
    runs = [load("run-1.json"), load("run-2.json")]

    assert hashlib.sha256((ROOT / "input.txt").read_bytes()).hexdigest() == manifest["input_sha256"]
    assert hashlib.sha256((ROOT / "prompt.txt").read_bytes()).hexdigest() == manifest["prompt_sha256"]
    assert all(run["returncode"] == 0 for run in runs)
    assert all(run["requested_model"] == "gpt-5.6-luna" for run in runs)

    adjudication = oracle["adjudication"]
    matched = [set(adjudication[run["run_id"]]["matched"]) for run in runs]
    observations = sum(len(run["raw_output"]["findings"]) for run in runs)
    unmatched = sum(
        len(adjudication[run["run_id"]].get("unmatched_observations", []))
        for run in runs
    )

    assert metrics["finding_rate"]["numerator"] == sum(map(len, matched)) == 7
    assert metrics["finding_rate"]["denominator"] == len(oracle["expected_findings"]) * len(runs) == 8
    assert metrics["unmatched_observation_rate"]["numerator"] == unmatched == 1
    assert metrics["unmatched_observation_rate"]["denominator"] == observations == 8
    assert metrics["unmatched_observation_rate"]["adjudication"] == "not adjudicated false"
    assert len(matched[0] & matched[1]) == metrics["repeat_agreement"]["intersection"] == 3
    assert len(matched[0] | matched[1]) == metrics["repeat_agreement"]["union"] == 4
    assert math.isclose(
        metrics["cost"]["elapsed_seconds_total"],
        sum(run["elapsed_seconds"] for run in runs),
    )

    # Abuse cases: stale false-alarm labeling and altered observations must not
    # reproduce the published evidence contract.
    assert "false_alarm_rate" not in metrics
    assert sum(map(len, matched)) - 1 != metrics["finding_rate"]["numerator"]


if __name__ == "__main__":
    main()
