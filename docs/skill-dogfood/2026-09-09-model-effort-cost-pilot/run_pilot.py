#!/usr/bin/env python3
"""Run one frozen-input Claude model/effort review arm."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import uuid
from pathlib import Path


HERE = Path(__file__).resolve().parent
CORPUS = (
    HERE.parent
    / "2026-09-09-loom-main-relative-dispatch-plan"
    / "claude-review-packet.md"
)
EXPECTED_SHA256 = "eafe902d69b4ff1c0afe311ea76e065b4a4c6af5787cc9c985856d27d4384de2"

INSTRUCTION = """You are an independent architecture and policy reviewer.
Review the proposal below using only its text. Do not use tools, external files,
prior sessions, or outside context. Distinguish factual errors from judgment
calls. Look specifically for contradictions, non-executable transitions,
false downgrade and false upgrade risks, whether routing fallback needs user
intervention, the smallest required changes, and text that should be deleted.
Return concise JSON matching the supplied schema. Do not mention this experiment.

--- BEGIN PROPOSAL ---
"""

SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {
            "type": "string",
            "enum": ["ACCEPT", "ACCEPT_WITH_CHANGES", "REJECT"],
        },
        "factual_errors": {"type": "array", "items": {"type": "string"}},
        "judgment_calls": {"type": "array", "items": {"type": "string"}},
        "contradictions_or_non_executable_transitions": {
            "type": "array",
            "items": {"type": "string"},
        },
        "false_downgrade_risks": {
            "type": "array",
            "items": {"type": "string"},
        },
        "false_upgrade_risks": {
            "type": "array",
            "items": {"type": "string"},
        },
        "fallback_assessment": {"type": "string"},
        "smallest_required_changes": {
            "type": "array",
            "items": {"type": "string"},
        },
        "delete_instead_of_expand": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "verdict",
        "factual_errors",
        "judgment_calls",
        "contradictions_or_non_executable_transitions",
        "false_downgrade_risks",
        "false_upgrade_risks",
        "fallback_assessment",
        "smallest_required_changes",
        "delete_instead_of_expand",
    ],
    "additionalProperties": False,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=("sonnet", "opus"), required=True)
    parser.add_argument("--effort", choices=("low", "medium", "high"), required=True)
    parser.add_argument("--replicate", type=int, choices=(1, 2), required=True)
    parser.add_argument("--max-budget-usd", type=float, default=1.0)
    args = parser.parse_args()

    corpus = CORPUS.read_bytes()
    digest = hashlib.sha256(corpus).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(f"corpus hash mismatch: {digest}")

    prompt = INSTRUCTION.encode() + corpus + b"\n--- END PROPOSAL ---\n"
    session_id = str(uuid.uuid4())
    stem = f"{args.model}-{args.effort}-r{args.replicate}"
    command = [
        "claude",
        "-p",
        "--safe-mode",
        "--disable-slash-commands",
        "--permission-mode",
        "dontAsk",
        "--permission-prompts",
        "none",
        "--allowedTools",
        "",
        "--model",
        args.model,
        "--effort",
        args.effort,
        "--max-budget-usd",
        f"{args.max_budget_usd:.2f}",
        "--output-format",
        "json",
        "--json-schema",
        json.dumps(SCHEMA, separators=(",", ":")),
        "--session-id",
        session_id,
    ]
    completed = subprocess.run(
        command,
        input=prompt,
        cwd=HERE,
        capture_output=True,
        check=False,
    )
    (HERE / f"{stem}.stdout.json").write_bytes(completed.stdout)
    (HERE / f"{stem}.stderr.txt").write_bytes(completed.stderr)
    metadata = {
        "arm": stem,
        "requested_model": args.model,
        "requested_effort": args.effort,
        "replicate": args.replicate,
        "session_id": session_id,
        "corpus_sha256": digest,
        "prompt_sha256": hashlib.sha256(prompt).hexdigest(),
        "max_budget_usd": args.max_budget_usd,
        "returncode": completed.returncode,
    }
    (HERE / f"{stem}.metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(metadata))
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
