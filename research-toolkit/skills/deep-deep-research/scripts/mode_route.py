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
  python mode_route.py classify-prompt --confirmed-block CB --killed-block KB \
      --question Q                prints the epistemic-mode classify prompt
Exits 0. Unknown/missing subcommand → stderr + exit 1.

(A later task adds a stdin `stance` subcommand alongside the sections below.)
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


def classify_prompt(question: str, confirmed_block: str, killed_block: str) -> str:
    """Return the epistemic-mode classification prompt.

    Asks the agent to classify the question's epistemic mode FROM THE
    EVIDENCE (the confirmed vs killed claim blocks), not from the
    question-text framing. The 4-mode taxonomy + 3 hard rules below are
    cross-model-validated (eval §三-C); they are carried verbatim and must
    not be paraphrased away — the taxonomy markers ("context-dependent" =
    complex; loud-opinion ≠ contested) are what makes question-grounded
    classification survive the "X vs Y" framing trap.
    """
    return f"""\
Classify the EPISTEMIC MODE of this research question — is the answer a
settled fact, an expert-resolvable consensus, a genuinely contested
debate, or a fast-changing/volatile situation? The classification sets
how synthesis should take a stance toward the answer.

## Question
{question}

## Evidence — confirmed claims (survived adversarial verification)
{confirmed_block}

## Evidence — killed claims (failed verification / refuted)
{killed_block}

## The 4-mode taxonomy (carry these meanings exactly)
- **clear** — a known, settled fact; one right answer that is not in
  dispute (e.g. an established scientific consensus). → settled.
- **complicated** — no live dispute, but the answer needs expertise /
  analysis to assemble; experts converge once the work is done. → settled.
- **complex** — the answer is genuinely contested OR **context-dependent**:
  a **context-dependent answer is complex, not settled** ("it depends on
  X" means there is no single settled answer). Competing positions are
  each evidence-backed. → unsettled.
- **chaotic** — fast-changing / volatile / recency-dominated; today's
  answer may not hold next quarter. → unsettled (flag volatility).

CRITICAL marker — **a loud / popular opinion is NOT the same as genuine
contestation** (loud-opinion ≠ contested). Judge by the evidence's
**stance spread**, not by how loudly or popularly a view is held. A view
that is loudly asserted but evidence-thin is NOT a real debate; a quiet
but evenly-split body of evidence IS.

## Three hard rules (do not skip)
1. **Classify from the evidence / stance spread**, NOT from the
   question-text framing. An "X vs Y" phrasing in the question biases you
   toward over-calling **complex** — ignore the framing and read how the
   confirmed vs killed claims actually spread across positions.
2. When unsure, **fail-safe to `unsettled` / complex**. Surfacing a debate
   that turns out settled is far less harmful than manufacturing false
   consensus on something genuinely open.
3. Treat clear / complicated / complex as a **low-confidence soft signal**
   only. The **only binding output is settled vs unsettled** — do NOT
   hinge behavior on the complicated↔complex line (it is model-dependent
   noise). Set `mode_binary` carefully; `mode_label` is advisory.

## Output
Emit a verdict conforming to MODE_VERDICT_SCHEMA:
- `mode_binary` (REQUIRED) — `settled` or `unsettled`.
- `mode_label` (optional) — clear / complicated / complex / chaotic.
- `rationale` (optional) — one line citing the evidence stance spread.

Structured output only."""


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
    p_classify = sub.add_parser("classify-prompt", add_help=False)
    p_classify.add_argument("--question", required=True)
    p_classify.add_argument("--confirmed-block", required=True)
    p_classify.add_argument("--killed-block", required=True)

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
        print(json.dumps(MODE_VERDICT_SCHEMA, indent=2))
        return 0
    # ns.command == "classify-prompt"
    print(classify_prompt(ns.question, ns.confirmed_block, ns.killed_block))
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
