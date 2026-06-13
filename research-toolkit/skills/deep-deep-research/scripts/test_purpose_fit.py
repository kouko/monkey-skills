"""Tests for purpose_fit.py — PURPOSE_FIT_SCHEMA shape and `schema` CLI.

Mirrors test_mode_route.py style: flat imports (`from purpose_fit import ...`)
plus a subprocess CLI round-trip test. This task covers ONLY the schema + the
`schema` subcommand; the classify prompt + directive block land in later tasks.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent


def test_purpose_fit_schema():
    from purpose_fit import PURPOSE_FIT_SCHEMA

    props = PURPOSE_FIT_SCHEMA["properties"]

    # The five required top-level keys of the purpose-fit verdict.
    for key in ("inferred_purpose", "confidence", "mode", "mooting_factors", "frames"):
        assert key in props, f"missing top-level key: {key}"

    # inferred_purpose is the free-text inferred decision purpose.
    assert props["inferred_purpose"]["type"] == "string"

    # confidence is a low/medium/high enum.
    assert props["confidence"]["enum"] == ["high", "medium", "low"]

    # mode selects consolidated vs multi-frame synthesis stance.
    assert props["mode"]["enum"] == ["consolidated", "multi-frame"]

    # mooting_factors is an array of claim-refs (factors that moot claims).
    assert props["mooting_factors"]["type"] == "array"

    # frames is an array of frame objects; each frame buckets confirmed claims
    # into decisive / contextual / not_relevant (never deleting — relevance
    # floor, not a filter).
    assert props["frames"]["type"] == "array"
    frame_props = props["frames"]["items"]["properties"]
    assert frame_props["frame"]["type"] == "string"
    for bucket in ("decisive", "contextual", "not_relevant"):
        assert bucket in frame_props, f"frame missing bucket: {bucket}"
        assert frame_props[bucket]["type"] == "array"

    # CLI round-trip: `schema` prints valid JSON equal to the schema, exit 0.
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "purpose_fit.py"), "schema"],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 0
    assert json.loads(proc.stdout) == PURPOSE_FIT_SCHEMA


def test_purpose_classify_prompt():
    from purpose_fit import purpose_classify_prompt

    prompt = purpose_classify_prompt(
        question="Should we migrate to Postgres?",
        confirmed_block="C1: Postgres handles our scale.",
        frames_ref="references/purpose-frames.md",
    )
    low = prompt.lower()

    # (a) infer the decision purpose + state a confidence (high/medium/low).
    assert "purpose" in low
    assert "confidence" in low
    for level in ("high", "medium", "low"):
        assert level in low, f"confidence level absent: {level}"

    # (b) mode selection by confidence — consolidated vs multi-frame.
    assert "consolidated" in low
    assert "multi-frame" in low

    # (c) classify each confirmed claim into decisive / contextual /
    #     not_relevant WITHOUT deleting — not_relevant items kept + labeled.
    for bucket in ("decisive", "contextual", "not_relevant"):
        assert bucket in low, f"bucket absent: {bucket}"
    assert any(
        phrase in low
        for phrase in ("do not delete", "never delete", "keep", "without deleting")
    ), "missing the keep / do-not-delete instruction"

    # (d) flag mooting_factors — claims that could settle the decision outright.
    assert "mooting" in low
    assert any(word in low for word in ("settle", "moot")), "missing settle/moot"

    # The frames-ref path is cited so the agent reads it at runtime.
    assert "references/purpose-frames.md" in prompt

    # CLI round-trip: the subcommand prints the same prompt, exit 0.
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "purpose_fit.py"),
            "purpose-classify-prompt",
            "--question",
            "Should we migrate to Postgres?",
            "--confirmed-block",
            "C1: Postgres handles our scale.",
        ],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 0
    assert proc.stdout.strip() == prompt.strip()


def test_purpose_classify_prompt_pins_claim_ref_indices():
    """Dogfood F1: the prompt MUST pin that claim-refs are the bracketed [N]
    indices printed in the confirmed_block, so the verdict's refs line up with
    what synthesis.py blocks emits (`### [0]`...). Without this, a schema-valid
    verdict could use free-text/made-up refs that silently dangle downstream."""
    from purpose_fit import purpose_classify_prompt

    prompt = purpose_classify_prompt(
        question="Should we migrate to Postgres?",
        confirmed_block="### [0] Postgres handles our scale.",
        frames_ref="references/purpose-frames.md",
    )
    low = prompt.lower()
    assert "[n]" in low, "prompt must reference the [N] index scheme"
    assert "index" in low, "prompt must name the claim-ref scheme as an index"


def test_purpose_fit_block_consolidated_moot_hoist():
    from purpose_fit import purpose_fit_block

    # A consolidated verdict that HAS a mooting factor. The load-bearing fix:
    # the mooting factor must be hoisted to a top-level callout ABOVE the
    # frame's decisive content — never dissolved into a frame bucket.
    verdict = {
        "inferred_purpose": "Decide whether to run k8s in-house",
        "confidence": "high",
        "mode": "consolidated",
        "mooting_factors": ["C7: org has no platform team and cannot hire one"],
        "frames": [
            {
                "frame": "Operational cost",
                "decisive": ["C3: k8s needs dedicated SRE headcount"],
                "contextual": ["C5: managed k8s reduces ops load"],
                "not_relevant": ["C9: k8s has a large plugin ecosystem"],
            },
        ],
    }
    block = purpose_fit_block(verdict)

    # (i) inferred_purpose + confidence stated.
    assert "Decide whether to run k8s in-house" in block
    assert "high" in block.lower()

    # (ii) moot-hoist: the mooting factor's claim-ref appears, and it appears
    #      BEFORE the frame's decisive content (top-level callout above frames).
    moot_pos = block.find("C7")
    decisive_pos = block.find("C3")
    assert moot_pos != -1, "mooting factor claim-ref absent"
    assert decisive_pos != -1, "decisive claim-ref absent"
    assert moot_pos < decisive_pos, "moot callout must be hoisted ABOVE the frame decisive content"

    # The callout is recognizable as a settle-outright signal.
    assert any(
        marker in block.upper()
        for marker in ("MAY SETTLE", "SETTLE THE DECISION", "SETTLE OUTRIGHT")
    ), "missing the settle-outright callout marker"

    # (iii) consolidated mode foregrounds the decisive set (label present).
    assert "decisive" in block.lower()


def test_purpose_fit_block_multi_frame():
    from purpose_fit import purpose_fit_block

    # A multi-frame verdict — each frame must render as its own labeled section,
    # NOT merged into one union list.
    verdict = {
        "inferred_purpose": "Evaluate microservices vs monolith",
        "confidence": "low",
        "mode": "multi-frame",
        "mooting_factors": [],
        "frames": [
            {
                "frame": "Team topology",
                "decisive": ["C1: single 4-person team"],
                "contextual": ["C2: co-located"],
                "not_relevant": [],
            },
            {
                "frame": "Deployment cadence",
                "decisive": ["C4: weekly releases"],
                "contextual": [],
                "not_relevant": ["C6: CDN choice"],
            },
        ],
    }
    block = purpose_fit_block(verdict)

    # Each frame label appears as its own section (>=2 distinct labels present).
    assert "Team topology" in block
    assert "Deployment cadence" in block

    # The two frames' distinctive claims are not collapsed — both decisive refs
    # present, each under its own frame (the frame label precedes its claim).
    assert block.find("Team topology") < block.find("C1")
    assert block.find("Deployment cadence") < block.find("C4")
    # And the second frame's label comes after the first frame's claim — i.e.
    # claims are grouped per-frame, not merged into a single union list.
    assert block.find("C1") < block.find("Deployment cadence")


def test_purpose_fit_block_never_drops_claims():
    from purpose_fit import purpose_fit_block

    # Every claim-ref appearing ANYWHERE in the verdict (decisive / contextual /
    # not_relevant across all frames + mooting_factors) must appear in the block.
    verdict = {
        "inferred_purpose": "Pick a database",
        "confidence": "medium",
        "mode": "multi-frame",
        "mooting_factors": ["M1: compliance mandates EU data residency"],
        "frames": [
            {
                "frame": "Scale",
                "decisive": ["D1: 10M rows"],
                "contextual": ["X1: current load is low"],
                "not_relevant": ["N1: vendor T-shirts are nice"],
            },
            {
                "frame": "Cost",
                "decisive": ["D2: budget is fixed"],
                "contextual": ["X2: pricing tiers"],
                "not_relevant": ["N2: logo color"],
            },
        ],
    }
    block = purpose_fit_block(verdict)

    all_refs = ["M1", "D1", "X1", "N1", "D2", "X2", "N2"]
    for ref in all_refs:
        assert ref in block, f"claim-ref dropped from block: {ref}"

    # (iv) not_relevant is labeled honestly (kept, not deleted).
    assert "not" in block.lower() and "relevant" in block.lower()


def test_purpose_fit_block_cli_roundtrip():
    from purpose_fit import purpose_fit_block

    verdict = {
        "inferred_purpose": "Decide whether to run k8s in-house",
        "confidence": "high",
        "mode": "consolidated",
        "mooting_factors": ["C7: no platform team"],
        "frames": [
            {
                "frame": "Operational cost",
                "decisive": ["C3: needs SRE headcount"],
                "contextual": [],
                "not_relevant": [],
            },
        ],
    }
    expected = purpose_fit_block(verdict)

    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "purpose_fit.py"), "block"],
        input=json.dumps(verdict),
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    assert out == {"purpose_fit_block": expected}


def test_purpose_fit_block_empty_verdict_degrades():
    """Degradation contract (SKILL.md): an empty/partial verdict must not crash —
    it returns a usable directive string so synthesis is never blocked."""
    from purpose_fit import purpose_fit_block

    # In-process: empty verdict yields a string, no exception.
    block = purpose_fit_block({})
    assert isinstance(block, str)

    # CLI: empty JSON object on stdin → exit 0 + valid {purpose_fit_block} envelope.
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "purpose_fit.py"), "block"],
        input="{}",
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    assert "purpose_fit_block" in out and isinstance(out["purpose_fit_block"], str)
