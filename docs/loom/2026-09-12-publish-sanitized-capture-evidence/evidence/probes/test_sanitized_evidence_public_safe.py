#!/usr/bin/env python3
"""Adversarially verify the committed dogfood evidence is public-safe."""

from __future__ import annotations

import json
import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
RAW = REPO / "docs/skill-dogfood/2026-09-12-capture-intent/raw"
REPORT = REPO / "docs/skill-dogfood/2026-09-12-capture-intent/report.md"
EXPECTED_PATHS = frozenset(
    """activation-followup-summary.json
activation-n01-run1.jsonl
activation-n02-run1.jsonl
activation-n03-run1.jsonl
activation-n04-run1.jsonl
activation-n05-run1.jsonl
activation-n06-run1.jsonl
activation-summary.json
activation-t01-run1.jsonl
activation-t02-run1.jsonl
activation-t03-run1.jsonl
activation-t04-run1.jsonl
activation-t05-run1.jsonl
activation-t06-run1.jsonl
activation-t06-run2.jsonl
activation-t06-run3.jsonl
activation-t07-run1.jsonl
activation-t08-run1.jsonl
activation-t09-run1.jsonl
activation-t10-run1.jsonl
activation-t11-run1.jsonl
activation-t12-run1.jsonl
activation-t13-run1.jsonl
activation-t14-run1.jsonl
activation-t14-run2.jsonl
activation-t14-run3.jsonl
activation-t15-run1.jsonl
activation-t16-run1.jsonl
activation-t17-run1.jsonl
activation-t18-run1.jsonl
activation-t19-run1.jsonl
activation-t20-run1.jsonl
activation-t20-run2.jsonl
activation-t20-run3.jsonl
blind-auditor-1.jsonl
blind-auditor-1.txt
blind-auditor-2.jsonl
blind-auditor-2.txt
claim-admission-codex/capture-ab.md
claim-admission-codex/plan-ab.md
claim-admission-codex/spec-ab.md
claim-admission/candidate-capture-intent.jsonl
claim-admission/candidate-capture-intent.txt
claim-admission/candidate-write-plan.jsonl
claim-admission/candidate-write-plan.txt
claim-admission/candidate-write-spec.jsonl
claim-admission/candidate-write-spec.txt
claim-admission/summary.json
executor-output.md
integrated-station-rules-v3/capture.md
integrated-station-rules-v3/spec.md
minimal-station-rules-v2/candidate-capture.md
minimal-station-rules-v2/candidate-spec.md
minimal-station-rules/candidate-capture.md
minimal-station-rules/candidate-spec.md
postfix-full-flow.jsonl
postfix-full-flow.txt
postfix-negative.jsonl
postfix-negative.txt
postfix-summary.json
postfix-t06-run1.jsonl
postfix-t06-run1.txt
postfix-t06-run2.jsonl
postfix-t06-run2.txt
postfix-t06-run3.jsonl
postfix-t06-run3.txt
station-boundary-ab/baseline-capture-intent.jsonl
station-boundary-ab/baseline-capture-intent.txt
station-boundary-ab/baseline-write-plan.jsonl
station-boundary-ab/baseline-write-plan.txt
station-boundary-ab/baseline-write-spec.jsonl
station-boundary-ab/baseline-write-spec.txt
station-boundary-ab/candidate-capture-intent.jsonl
station-boundary-ab/candidate-capture-intent.txt
station-boundary-ab/candidate-write-plan.jsonl
station-boundary-ab/candidate-write-plan.txt
station-boundary-ab/candidate-write-spec.jsonl
station-boundary-ab/candidate-write-spec.txt
station-boundary-ab/summary.json""".splitlines()
)
FORBIDDEN_KEYS = frozenset(
    {
        "apiKeySource",
        "cwd",
        "hook_id",
        "mcp_servers",
        "memory_paths",
        "messaging_socket_path",
        "parent_tool_use_id",
        "permissionMode",
        "plugins",
        "request_id",
        "session_id",
        "signature",
        "slash_commands",
        "terminal_slash_commands",
        "tools",
        "uuid",
        "wire_tool_inputs",
    }
)
FORBIDDEN = re.compile(
    r"/Users/|/home/|/private/tmp|/tmp/|session_id|request_id|"
    r"messaging_socket_path|memory_paths|mcp_servers|permissionMode|"
    r"apiKeySource|\"signature\"|\bmsg_[A-Za-z0-9_-]+|"
    r"\btoolu_[A-Za-z0-9_-]+|"
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
    r"[0-9a-f]{4}-[0-9a-f]{12}\b|"
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    re.IGNORECASE,
)


def _walk(value):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _assert_no_forbidden_keys(value) -> None:
    for item in _walk(value):
        if isinstance(item, dict):
            assert not (FORBIDDEN_KEYS & item.keys())


def _assert_expected_paths(paths: frozenset[str]) -> None:
    assert paths == EXPECTED_PATHS


def test_uuid_v7_input_rejected() -> None:
    known_bad_shape = "018f1234-5678-7abc-8def-0123456789ab"
    assert FORBIDDEN.search(known_bad_shape)


def test_path_population_substitution_rejected() -> None:
    substituted = (EXPECTED_PATHS - {"activation-summary.json"}) | {"replacement.json"}
    try:
        _assert_expected_paths(frozenset(substituted))
    except AssertionError:
        return
    raise AssertionError("one-for-one path substitution was accepted")


def test_forbidden_metadata_key_input_rejected() -> None:
    for key in FORBIDDEN_KEYS:
        try:
            _assert_no_forbidden_keys({"type": "assistant", key: "synthetic"})
        except AssertionError:
            continue
        raise AssertionError(f"forbidden metadata key was accepted: {key}")


def test_sanitized_evidence_committed_public_safe() -> None:
    files = sorted(path for path in RAW.rglob("*") if path.is_file())
    paths = frozenset(str(path.relative_to(RAW)) for path in files)
    _assert_expected_paths(paths)
    assert {path.suffix for path in files} == {".json", ".jsonl", ".md", ".txt"}

    json_count = jsonl_count = row_count = 0
    for path in files:
        text = path.read_text()
        assert not FORBIDDEN.search(text), path
        if path.suffix == ".json":
            _assert_no_forbidden_keys(json.loads(text))
            json_count += 1
        elif path.suffix == ".jsonl":
            jsonl_count += 1
            for line in text.splitlines():
                item = json.loads(line)
                _assert_no_forbidden_keys(item)
                row_count += 1
                assert item.get("type") not in {"system", "rate_limit_event"}
                for value in _walk(item):
                    if isinstance(value, dict) and "thinking" in value:
                        assert not str(value["thinking"]).strip()

    assert (json_count, jsonl_count, row_count) == (5, 48, 232)
    report = REPORT.read_text()
    assert not FORBIDDEN.search(report)
    assert "committed, sanitized execution evidence" in report
    assert "unsanitized streams remain local" in report


if __name__ == "__main__":
    test_uuid_v7_input_rejected()
    test_path_population_substitution_rejected()
    test_forbidden_metadata_key_input_rejected()
    test_sanitized_evidence_committed_public_safe()
