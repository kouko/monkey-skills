"""Synthesis calibration-prepend directive for the deep-deep-research lever.

Companion to mode_route.py / purpose_fit.py. Where mode_route.py sets
*what stance* synthesis takes toward settled vs unsettled questions, and
purpose_fit.py adapts output to the research purpose, calibrate.py
enforces *confidence integrity at the aggregation step* — ensuring that
a merged finding's confidence tag reflects the weakest evidence under it,
not the strongest.

This module is a STATIC emitter: the same 3 anti-laundering rules apply
every run, so it has no classify step and no schema. SKILL.md Stage 6
PREPENDS the block closest to the base synthesis prompt (purpose-fit →
meta-mode → calibration → base), because calibration governs the tagging
mechanics at the point the model actually assigns confidence values.
Degradation: if this module errors, SKILL.md falls back to the unmodified
synthesis prompt — never block.

Provenance (recorded here, NOT used as runtime logic):
- Rule 1 is grounded in the GRADE anti-averaging principle and the
  Network-Meta-Analysis (NMA) weakest-link property: when a synthesis chain
  combines direct and indirect evidence, the certainty of the merged result
  equals min(direct, indirect) — the "Certainty Bound" formal result. A
  merged finding that rests on any single-source, secondary, blog-quality,
  or split-vote claim cannot inherit the confidence of its strongest
  component.
- Rule 2 is grounded in the ICMJE abstract-consistency requirements and the
  CONSORT-A extension for abstract reporting: a structured abstract must not
  overstate findings relative to the full report body. The "spin" literature
  (Boutron et al.; Lazarus et al.) documents how summary headlines routinely
  overstate the certainty of hedged findings — Rule 2 is the direct counter.
  This is the strongest-grounded of the three rules.
- Rule 3 is grounded in GRADE's inconsistency-downgrade principle (high I²
  or genuinely conflicting outcomes lower the evidence grade) and the
  "Faithful Summarisation under Disagreement" line of NLP/LLM research
  (Goyal & Durrett 2020 et seq.; Pagnoni et al. 2021). LLMs' documented
  default behaviour is smoothing conflicting evidence into false consensus
  (the BURIED_TENSION failure class observed in the calibration eval, 6/8
  seeds, cross-model). Rule 3 is distinct from meta-mode's question-level
  stance: it governs within-synthesis claim tensions regardless of the
  question's epistemic mode.

CLI:
  python calibrate.py block    prints {"calibration_block": "<directive>"} to stdout
Exits 0. Unknown/missing subcommand → stderr + exit 1.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Calibration directive (static — same 3 rules every run)
# ---------------------------------------------------------------------------

CALIBRATION_BLOCK = (
    "SYNTHESIS CALIBRATION — confidence-integrity rules (anti-laundering).\n"
    "Apply all three rules when assigning confidence tags and writing the summary.\n\n"
    "Rule 1 — Weakest-link: a merged finding's confidence equals its WEAKEST "
    "load-bearing claim. Never tag a finding 'high' if any claim it rests on is "
    "secondary-source, single-source, blog-quality, or split-vote. "
    "Confidence rubric: high = multiple primary sources, near-unanimous; "
    "medium = secondary sources or split votes; low = single source or blog-quality. "
    "Do not average up from a weak claim to reach 'high' — the weakest link sets "
    "the ceiling.\n\n"
    "Rule 2 — Summary must not exceed body: the summary headline must not state "
    "the conclusion more certainly than the findings and caveats it summarizes. "
    "If the body uses hedged language or reports a low- or medium-confidence finding, "
    "the summary must reflect that same uncertainty — do not launder a hedge into "
    "a confident assertion at the summary level.\n\n"
    "Rule 3 — No false consensus: never present split or tied votes, or two "
    "confirmed claims that are in genuine conflict, as 'consensus'. A contested "
    "or tied claim must be surfaced as contested, not smoothed into agreement. "
    "When two confirmed claims are mutually conflicting, report the tension "
    "explicitly rather than silently promoting one to the headline answer."
)


def calibration_block() -> str:
    """Return the static synthesis calibration directive.

    The directive encodes 3 anti-laundering rules (weakest-link confidence,
    summary-does-not-exceed-body, no-false-consensus). SKILL.md Stage 6
    prepends this block to the base synthesis prompt when the calibration
    lever is opt-in enabled.
    """
    return CALIBRATION_BLOCK


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv=None) -> int:
    import argparse
    import json
    import sys

    args = sys.argv[1:] if argv is None else argv

    parser = argparse.ArgumentParser(prog="calibrate.py", add_help=False)
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("block", add_help=False)

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

    # ns.command == "block"
    json.dump({"calibration_block": calibration_block()}, sys.stdout)
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
