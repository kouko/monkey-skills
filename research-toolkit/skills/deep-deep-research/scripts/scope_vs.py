"""Scope schema + constants for the angle-selector (vs) variant.

Companion to schemas.py: where SCOPE_SCHEMA emits 3-6 research angles,
SCOPE_VS_SCHEMA emits >=10 typicality-tiered candidate angles for a
head/tail self-consistency selection pass.

CLI:
  python scope_vs.py schema                 prints SCOPE_VS_SCHEMA as JSON
  python scope_vs.py prompt --question Q     prints the assembled scope-vs prompt
Both exit 0. Unknown/missing subcommand → stderr + exit 1.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HEAD_K: int = 3
TAIL_K: int = 2
CANDIDATE_COUNT: int = 12
SELF_CONSISTENCY_RUNS: int = 2
RELEVANCE_FLOOR: str = "medium"

# ---------------------------------------------------------------------------
# JSON Schema
# ---------------------------------------------------------------------------

SCOPE_VS_SCHEMA = {
    "type": "object",
    "required": ["question", "summary", "candidates"],
    "properties": {
        "question": {"type": "string"},
        "summary": {"type": "string"},
        "candidates": {
            "type": "array",
            "minItems": 10,
            "items": {
                "type": "object",
                "required": ["label", "query", "relevance", "typicality_tier"],
                "properties": {
                    "label": {"type": "string"},
                    "query": {"type": "string"},
                    "relevance": {"enum": ["high", "medium", "low"]},
                    "typicality_tier": {
                        "enum": ["most-obvious", "mid", "least-obvious"]
                    },
                    "rationale": {"type": "string"},
                },
            },
        },
    },
}

# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------


def scope_vs_prompt(question: str) -> str:
    """Return the SCOPE-VS prompt with {QUESTION} interpolated.

    Constants (CANDIDATE_COUNT, the three tier names) are interpolated so
    the prompt text stays in sync with SCOPE_VS_SCHEMA.
    """
    return f"""\
Decompose this research question into a ranked, typicality-tiered set of
candidate search angles for a head/tail self-consistency selection pass.

## Question
{question}

## Task
Generate {CANDIDATE_COUNT} distinct candidate angles that cover the question
from different angles. Pick angles that suit the question's domain.

Then score each candidate:
1. **First RANK** all {CANDIDATE_COUNT} candidates from most-obvious to
   least-obvious. **Then** bucket them into three typicality tiers:
   `most-obvious` / `mid` / `least-obvious`. Score typicality RELATIVELY
   within THIS single call (a relative ordering among these candidates) —
   NOT as absolute floats on some universal scale.
2. Score typicality BLIND to authorship: judge each angle on its own
   obviousness, decoupled from the fact that you generated it. Do not let
   "I produced this" bias a candidate toward the most-obvious tier.
3. Rate each angle's `relevance` to the ORIGINAL question as
   high / medium / low.

## Output
Emit JSON conforming to SCOPE_VS_SCHEMA. Each candidate has:
- `label` — short name for the angle
- `query` — a specific, high-signal web search query
- `rationale` — why this angle bears on the question
- `relevance` — high / medium / low
- `typicality_tier` — most-obvious / mid / least-obvious

Avoid redundancy. Make queries specific enough to surface high-signal
results.

Structured output only."""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv=None) -> int:
    import argparse
    import json
    import sys

    args = sys.argv[1:] if argv is None else argv

    parser = argparse.ArgumentParser(prog="scope_vs.py", add_help=False)
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("schema", add_help=False)
    p_prompt = sub.add_parser("prompt", add_help=False)
    p_prompt.add_argument("--question", required=True)

    # Derive the valid-subcommand list from the registered subparsers so it
    # cannot drift from what's actually wired up (single source of truth).
    valid = ", ".join(sub.choices)

    # Reject an unknown / missing subcommand up front, BEFORE argparse — so a
    # missing-required-arg error on a *known* subcommand (e.g. `prompt` with no
    # --question) isn't mislabeled "unknown subcommand".
    if not args or args[0] not in sub.choices:
        name = args[0] if args else "(none)"
        print(f"unknown subcommand {name!r}; expected one of {{{valid}}}",
              file=sys.stderr)
        return 1

    try:
        ns = parser.parse_args(args)
    except SystemExit:
        # Known subcommand, bad/missing args — argparse already wrote its own
        # specific error to stderr; just normalize the exit code.
        return 1

    if ns.command == "schema":
        print(json.dumps(SCOPE_VS_SCHEMA, indent=2))
        return 0
    # ns.command == "prompt" (the only other registered subcommand)
    print(scope_vs_prompt(ns.question))
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
