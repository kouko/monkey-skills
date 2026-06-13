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
  python framework_audit.py schema                    prints FRAMEWORK_AUDIT_SCHEMA as JSON
  python framework_audit.py classify-prompt --question Q  prints the type-classify prompt
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

# Path to the routing table the agent consults to pick frameworks. Kept as a
# bare relative reference (skill-root relative) so the prompt points at the
# bundled resource without hard-coding an absolute path.
LIBRARY_REF: str = "references/framework-audit-library.md"


def classify_prompt(question: str) -> str:
    """Return the question-type classification prompt with {QUESTION} interpolated.

    Asks the agent to classify the research question's *type* against the
    routing-table 題型 keys in references/framework-audit-library.md, then
    pick the 2–3 audit frameworks that type routes to. Text-only — the agent
    reasons over the bundled routing table, it does not fetch anything.

    Mirrors scope_vs_prompt's structure/tone (Question / Task / Output).
    """
    return f"""\
Classify this research question's TYPE so an audit pass can pick the right
completeness-audit frameworks. This is a text-only reasoning step — no web
search, no retrieval; reason over the bundled routing table only.

## Question
{question}

## Task
1. Read the **routing table (路由表)** in `{LIBRARY_REF}` — its left column
   lists question types (題型 keys, e.g. investment/個股, macro/產業,
   policy/法規, product/UX, risk/安全, or the general 萬用起手 row).
2. Decide which 題型 row this question best matches. If it spans two types,
   name the primary one and note the secondary.
3. From that row's first-line frameworks (走查格子), pick the **2–3** audit
   frameworks that best fit this question. Add one reinforcement framework
   only if the route's cells feel thin.

## Output
- `type` — the routing-table 題型 key you matched (plus any secondary).
- `frameworks` — the 2–3 framework names you picked from that route.
- `why` — one line per framework: why it fits THIS question's gaps.

These 2–3 frameworks feed the next (audit) step; pick for coverage of the
question's likely blind spots, not for prestige.

Reasoning over the routing table only — no web search, no retrieval."""


# (later tasks add audit_prompt here)

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
    p_classify = sub.add_parser("classify-prompt", add_help=False)
    p_classify.add_argument("--question", required=True)

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
    if ns.command == "classify-prompt":
        print(classify_prompt(ns.question))
        return 0
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
