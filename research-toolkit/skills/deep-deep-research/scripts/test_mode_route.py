"""Tests for mode_route.py — MODE_VERDICT_SCHEMA shape and `schema` CLI.

Mirrors test_scope_vs.py style: flat imports (`from mode_route import ...`)
plus a subprocess CLI round-trip test.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent


def test_mode_schema_binary_required_label_optional():
    from mode_route import MODE_VERDICT_SCHEMA

    props = MODE_VERDICT_SCHEMA["properties"]

    # mode_binary is the ONLY required field, enum settled/unsettled
    assert MODE_VERDICT_SCHEMA["required"] == ["mode_binary"]
    assert props["mode_binary"]["enum"] == ["settled", "unsettled"]

    # mode_label is OPTIONAL (NOT in required) — low-confidence soft signal,
    # 4-mode Cynefin enum. The clear/complicated/complex sub-distinction is
    # model-dependent noise, so it must never be a hard required switch.
    assert "mode_label" not in MODE_VERDICT_SCHEMA["required"]
    assert props["mode_label"]["enum"] == [
        "clear",
        "complicated",
        "complex",
        "chaotic",
    ]

    # rationale is an optional free-text string
    assert "rationale" not in MODE_VERDICT_SCHEMA["required"]
    assert props["rationale"]["type"] == "string"

    # CLI round-trip: `schema` prints valid JSON, exit 0
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "mode_route.py"), "schema"],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 0
    assert json.loads(proc.stdout) == MODE_VERDICT_SCHEMA


def test_classify_prompt_has_taxonomy_and_hardrules():
    from mode_route import classify_prompt

    question = "Are microservices more scalable for most companies?"
    confirmed_block = "CONFIRMED: monolith-first preferred by many teams"
    killed_block = "KILLED: microservices always reduce coupling"

    prompt = classify_prompt(question, confirmed_block, killed_block)

    # The question + both evidence blocks must be interpolated verbatim.
    assert question in prompt
    assert confirmed_block in prompt
    assert killed_block in prompt

    # Load-bearing taxonomy markers (cross-model-validated; must appear).
    # "context-dependent" maps to complex — a context-dependent answer is
    # complex, not settled.
    assert "context-dependent" in prompt
    assert "complex" in prompt
    # A loud / popular opinion is NOT the same as genuine contestation;
    # judge by evidence stance-spread, not by how loudly a view is held.
    assert "loud" in prompt
    assert "contested" in prompt

    # All four Cynefin modes present.
    for mode in ("clear", "complicated", "complex", "chaotic"):
        assert mode in prompt

    # Hard rule 1: classify FROM THE EVIDENCE / stance spread, not the
    # question-text framing ("X vs Y" biases toward over-calling complex).
    assert "stance spread" in prompt
    assert "from the evidence" in prompt

    # Hard rule 2: when unsure, fail-safe to unsettled / complex.
    assert "fail-safe" in prompt
    assert "unsettled" in prompt

    # Hard rule 3: clear/complicated/complex is a low-confidence soft signal;
    # only settled-vs-unsettled is the binding output.
    assert "low-confidence" in prompt
    assert "settled" in prompt

    # Output must reference the verdict schema.
    assert "MODE_VERDICT_SCHEMA" in prompt

    # CLI round-trip: classify-prompt prints the prompt, exit 0.
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "mode_route.py"),
            "classify-prompt",
            "--confirmed-block", confirmed_block,
            "--killed-block", killed_block,
            "--question", question,
        ],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 0
    assert question in proc.stdout
    assert "context-dependent" in proc.stdout


def test_stance_block_maps_modes():
    from mode_route import stance_block

    # settled → give the consensus clearly, do not over-hedge.
    settled = stance_block("settled")
    assert "consensus" in settled
    assert "clearly" in settled or "do not over-hedge" in settled

    # unsettled → map competing positions, calibrate DOWN, do not force a
    # verdict. This is the fix for the synthesis prompt's false-consensus bias
    # (§三-C 測試1: mode-blind synthesis manufactures false consensus on
    # genuinely contested questions).
    unsettled = stance_block("unsettled")
    assert "competing positions" in unsettled or "map" in unsettled
    assert "calibrate" in unsettled
    assert "do not force" in unsettled or "not force a verdict" in unsettled

    # chaotic surfaces via the OPTIONAL mode_label → ALSO add a
    # volatility / recency flag note (on top of the unsettled directive).
    chaotic = stance_block("unsettled", mode_label="chaotic")
    assert "volatil" in chaotic.lower() or "recency" in chaotic.lower()
    # the chaotic note is additive — the unsettled stance is still present.
    assert "calibrate" in chaotic

    # Unknown / missing / garbage mode_binary → fail-safe to the unsettled
    # directive (hard rule 2: surfacing a debate is safer than false
    # consensus). The fallback returns the SAME text as unsettled.
    assert stance_block("garbage") == unsettled
    assert stance_block("") == unsettled
    assert stance_block(None) == unsettled


def test_stance_cli_round_trip():
    # stance subcommand: read {mode_binary, mode_label?} from stdin, write
    # {stance_block: "<directive>"} to stdout (mirrors vs_select.py main()).
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "mode_route.py"), "stance"],
        input='{"mode_binary": "unsettled"}',
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    assert "stance_block" in out
    assert "calibrate" in out["stance_block"]

    # mode_label flows through stdin → chaotic note appears.
    proc2 = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "mode_route.py"), "stance"],
        input='{"mode_binary": "unsettled", "mode_label": "chaotic"}',
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc2.returncode == 0
    out2 = json.loads(proc2.stdout)
    block = out2["stance_block"].lower()
    assert "volatil" in block or "recency" in block


def test_cli_unknown_subcommand():
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "mode_route.py"), "bogus"],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 1
    assert proc.stdout.strip() == ""
    assert "bogus" in proc.stderr
