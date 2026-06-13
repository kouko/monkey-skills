"""Framework completeness-audit: gap-angle schema + prompts + selector.

Lever ① of the deep-deep-research opt-in passes. Where schemas.py's
SCOPE_SCHEMA emits the base research angles, FRAMEWORK_AUDIT_SCHEMA emits
*gap-fill* angles — each tagged with the analytical framework + uncovered
cell that motivated it — so an audit pass can top up the angle set before
the unchanged Stage 2 (Search) consumes it.

The gap items reuse the SCOPE_SCHEMA angle shape (`label` / `query` /
optional `rationale`) so a later dedup+budget-cap step can strip them back
to plain angles and hand Stage 2 the same shape it always sees; `framework`
+ `cell` are the only additions and are dropped before Stage 2.

This module is built incrementally across four tasks (schema → classify
prompt → audit prompt → stdin `select`); the CLI uses subparsers so each
later subcommand slots in beside `schema` without restructuring.

CLI:
  python framework_audit.py schema     prints FRAMEWORK_AUDIT_SCHEMA as JSON
Exit 0. Unknown/missing subcommand → stderr + exit 1.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# (later tasks add audit-pass constants here)

# ---------------------------------------------------------------------------
# JSON Schema
# ---------------------------------------------------------------------------

FRAMEWORK_AUDIT_SCHEMA = {
    "type": "object",
    "required": ["question", "gaps"],
    "properties": {
        "question": {"type": "string"},
        "gaps": {
            "type": "array",
            "items": {
                "type": "object",
                # label/query mirror the SCOPE_SCHEMA angle shape; framework/
                # cell tag which framework's uncovered cell this gap fills.
                "required": ["label", "query", "framework", "cell"],
                "properties": {
                    "label": {"type": "string"},
                    "query": {"type": "string"},
                    "rationale": {"type": "string"},
                    "framework": {"type": "string"},
                    "cell": {"type": "string"},
                },
            },
        },
    },
}

# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

# (later tasks add classify_prompt / audit_prompt here)

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv=None) -> int:
    import argparse
    import json
    import sys

    args = sys.argv[1:] if argv is None else argv

    parser = argparse.ArgumentParser(prog="framework_audit.py", add_help=False)
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

    if ns.command == "schema":
        print(json.dumps(FRAMEWORK_AUDIT_SCHEMA, indent=2))
        return 0
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
