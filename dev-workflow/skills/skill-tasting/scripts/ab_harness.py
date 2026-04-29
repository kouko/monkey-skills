#!/usr/bin/env python3
"""ab_harness.py — orchestrates skill-tasting Phase 3 blind A/B presentation.

This script handles the deterministic parts of the A/B harness:
random label assignment, side-by-side rendering for terminal display,
truncation, and atomic decision logging. Variant generation (Phase 1)
and constitutional pre-filter (Phase 2) are spawned by the skill's
main agent — those need subagent / LLM access this script doesn't have.

Per references/ab-harness-protocol.md.

Inputs:
    A directory containing variant outputs:
        <workspace>/variants/eval-N/
            baseline/output.md
            variant-1/output.md
            variant-2/output.md
            ...

Output:
    Renders side-by-side blind comparison to stdout (terminal); reads
    user pick (a / b / c / m / n / r); writes pick + label decoding to
    a session-scoped JSON file.

Usage:
    python ab_harness.py \\
        --variants-dir <workspace>/variants/eval-1/ \\
        --prompt "the user prompt" \\
        --session-out <workspace>/session.json \\
        [--max-display-lines 200]
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path


def collect_variants(variants_dir: Path) -> list[dict]:
    """Read variant outputs from variants_dir/{name}/output.md."""
    variants = []
    if not variants_dir.exists():
        return variants
    for entry in sorted(variants_dir.iterdir()):
        if not entry.is_dir():
            continue
        output_path = entry / "output.md"
        if not output_path.exists():
            continue
        try:
            content = output_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        variants.append({
            "identity": entry.name,
            "output_path": str(output_path),
            "content": content,
        })
    return variants


def assign_random_labels(variants: list[dict]) -> dict[str, dict]:
    """Shuffle variants and assign A/B/C... labels."""
    if not variants:
        return {}
    shuffled = list(variants)
    random.shuffle(shuffled)
    labels = "ABCDEFGHIJ"
    return {labels[i]: v for i, v in enumerate(shuffled[: len(labels)])}


def truncate(text: str, max_lines: int) -> tuple[str, bool]:
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text, False
    truncated = "\n".join(lines[:max_lines])
    return truncated, True


def render(label_map: dict[str, dict], prompt: str, max_lines: int = 200) -> str:
    sep = "─" * 65
    out = [sep]
    out.append("TEST PROMPT")
    out.append(sep)
    out.append(prompt)
    out.append("")

    for label in sorted(label_map.keys()):
        variant = label_map[label]
        body, was_truncated = truncate(variant["content"], max_lines)
        out.append(sep)
        out.append(f"OUTPUT {label}")
        out.append(sep)
        out.append(body)
        if was_truncated:
            out.append(f"[... truncated; full output: {variant['output_path']}]")
        out.append("")

    out.append(sep)
    out.append("PICK ONE:")
    for label in sorted(label_map.keys()):
        out.append(f"  [{label.lower()}] Variant {label}")
    out.append("  [m] Multiple (specify which two: e.g., 'a+c')")
    out.append("  [n] None — all worse than current state")
    out.append("  [r] Refine — different test prompt or different variants needed")
    out.append(sep)
    return "\n".join(out)


VALID_SINGLE = set("abcdefghij")
VALID_SPECIAL = {"m", "n", "r"}


def parse_pick(raw: str, label_map: dict[str, dict]) -> dict:
    """Parse user input into a structured pick.

    Returns:
        {"type": "single", "label": "A", "identity": "baseline"}
        {"type": "multiple", "labels": ["A", "C"], "identities": ["baseline", "variant_b"]}
        {"type": "none"} | {"type": "refine"}
    """
    raw = raw.strip().lower()

    if raw in VALID_SINGLE:
        upper = raw.upper()
        if upper not in label_map:
            return {"type": "invalid", "reason": f"label {upper} not in this round"}
        return {"type": "single", "label": upper, "identity": label_map[upper]["identity"]}

    if raw == "n":
        return {"type": "none"}
    if raw == "r":
        return {"type": "refine"}

    if raw == "m" or "+" in raw:
        # Multiple pick: parse "a+c" or "a,c" or treat 'm' as request for clarification
        if raw == "m":
            return {"type": "needs_clarification", "reason": "specify e.g. 'a+c'"}
        parts = [p.strip() for p in raw.replace(",", "+").split("+") if p.strip()]
        if not all(p in VALID_SINGLE for p in parts):
            return {"type": "invalid", "reason": f"unknown labels in {raw!r}"}
        upper = [p.upper() for p in parts]
        if not all(u in label_map for u in upper):
            return {"type": "invalid", "reason": f"some labels not in this round"}
        return {
            "type": "multiple",
            "labels": upper,
            "identities": [label_map[u]["identity"] for u in upper],
        }

    return {"type": "invalid", "reason": f"unrecognized input: {raw!r}"}


def write_session(session_out: Path, prompt: str, label_map: dict[str, dict], pick: dict) -> None:
    """Persist the session decision atomically to a JSON file."""
    record = {
        "prompt": prompt,
        "label_assignment": {label: v["identity"] for label, v in label_map.items()},
        "pick": pick,
    }
    session_out.parent.mkdir(parents=True, exist_ok=True)
    session_out.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--variants-dir", required=True, type=Path)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--session-out", required=True, type=Path)
    parser.add_argument("--max-display-lines", type=int, default=200)
    parser.add_argument("--pick", default=None,
                        help="Provide pick non-interactively (for testing); otherwise read from stdin")
    args = parser.parse_args()

    variants = collect_variants(args.variants_dir)
    if not variants:
        print(f"error: no variants found in {args.variants_dir}", file=sys.stderr)
        return 2
    if len(variants) < 2:
        print(f"error: need ≥2 variants for A/B; got {len(variants)}", file=sys.stderr)
        return 2

    label_map = assign_random_labels(variants)
    rendered = render(label_map, args.prompt, args.max_display_lines)
    print(rendered)

    if args.pick is not None:
        raw = args.pick
    else:
        try:
            raw = input("\nYour pick: ")
        except EOFError:
            print("error: no input received", file=sys.stderr)
            return 2

    pick = parse_pick(raw, label_map)
    write_session(args.session_out, args.prompt, label_map, pick)

    if pick["type"] == "invalid":
        print(f"\nInvalid pick: {pick['reason']}", file=sys.stderr)
        print(f"Session record saved to {args.session_out} for retry.", file=sys.stderr)
        return 2

    print(f"\nSession written to {args.session_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
