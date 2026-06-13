"""Epistemic-mode verdict schema + routing for the meta-mode (synthesis-stance) lever.

Companion to schemas.py / scope_vs.py. Where scope_vs.py picks *which angles*
to research, mode_route.py decides *what stance* synthesis should take toward
the answer: give a settled consensus clearly, or map an unsettled debate and
calibrate confidence down.

Design note — why mode_binary is the only required field:
The verdict's `mode_binary` (settled vs unsettled) is the cross-model-ROBUST
signal: across opus/sonnet/haiku it reliably protects already-settled facts
from false-uncertainty contamination. The finer Cynefin label
(clear / complicated / complex / chaotic) is a LOW-CONFIDENCE soft signal —
the clear↔complicated↔complex sub-distinction was measured to be
model-dependent noise, so it lives in an OPTIONAL `mode_label`, never a hard
required switch. Only settled-vs-unsettled is binding.

Provenance (recorded here, NOT leaked into runtime behavior):
- Cynefin framework — Dave Snowden & Mary Boone, "A Leader's Framework for
  Decision Making", Harvard Business Review, Nov 2007 (the clear/complicated/
  complex/chaotic domains; here distilled to a synthesis-stance signal, not
  used as a decision-routing engine).
- Hard-Soft systems thinking — the distinction between well-defined ("hard")
  and contested/ill-structured ("soft") problems, which maps onto the
  settled / unsettled binary.

CLI:
  python mode_route.py schema     prints MODE_VERDICT_SCHEMA as JSON
Exits 0. Unknown/missing subcommand → stderr + exit 1.

(First of three tasks building this module; later tasks add a classify-prompt
builder and a stdin `stance` subcommand alongside the sections below.)
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODE_BINARY = ["settled", "unsettled"]
MODE_LABELS = ["clear", "complicated", "complex", "chaotic"]

# ---------------------------------------------------------------------------
# JSON Schema
# ---------------------------------------------------------------------------

MODE_VERDICT_SCHEMA = {
    "type": "object",
    # mode_binary is the ONLY required field — the cross-model-robust signal.
    "required": ["mode_binary"],
    "properties": {
        "mode_binary": {"enum": MODE_BINARY},
        # Optional low-confidence soft signal; the clear/complicated/complex
        # sub-distinction is model-dependent noise, so it is NOT required.
        "mode_label": {"enum": MODE_LABELS},
        "rationale": {"type": "string"},
    },
}

# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------
#
# (classify_prompt is added by a later task in this module.)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv=None) -> int:
    import argparse
    import json
    import sys

    args = sys.argv[1:] if argv is None else argv

    parser = argparse.ArgumentParser(prog="mode_route.py", add_help=False)
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("schema", add_help=False)

    # Derive the valid-subcommand list from the registered subparsers so it
    # cannot drift from what's actually wired up (single source of truth).
    valid = ", ".join(sub.choices)

    # Reject an unknown / missing subcommand up front, BEFORE argparse — so a
    # missing-required-arg error on a *known* subcommand isn't mislabeled
    # "unknown subcommand".
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

    # ns.command == "schema" (the only registered subcommand)
    print(json.dumps(MODE_VERDICT_SCHEMA, indent=2))
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
