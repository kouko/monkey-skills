"""Purpose-fit (relevance-floor) lever — verdict schema + synthesis directive.

Companion to mode_route.py / scope_vs.py. Where mode_route.py decides the
synthesis *stance* (settled vs unsettled) and scope_vs.py picks *which angles*
to research, purpose_fit.py is an opt-in END-CHECK run over the Stage-5
confirmed claims: it classifies each confirmed claim against an INFERRED
decision purpose into decisive / contextual / not-relevant buckets, then emits
a directive that PREPENDs the synthesis prompt.

It is a relevance FLOOR, not a filter: a claim that scores not-relevant is
demoted in emphasis, never deleted. The lever only ever changes how synthesis
*weights* and *frames* the confirmed evidence; it never drops a confirmed
claim or touches the synced base synthesis prompt (prompts.py stays
byte-identical — the directive is PREPENDED at the SKILL.md opt-in branch).

Mirrors mode_route.py: a JSON-schema dict + a classify-prompt builder + an
argparse CLI. The synthesis directive block lands in a later task.

CLI:
  python purpose_fit.py schema    prints PURPOSE_FIT_SCHEMA as JSON
  python purpose_fit.py purpose-classify-prompt --question Q --confirmed-block CB \
      [--frames-ref PATH]         prints the purpose-fit classify prompt
  python purpose_fit.py block     reads a verdict (PURPOSE_FIT_SCHEMA) from stdin,
                                  prints {purpose_fit_block: "<directive>"} to stdout
Exits 0. Unknown/missing subcommand → stderr + exit 1.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CONFIDENCE_LEVELS = ["high", "medium", "low"]
MODES = ["consolidated", "multi-frame"]

# ---------------------------------------------------------------------------
# JSON Schema
# ---------------------------------------------------------------------------

PURPOSE_FIT_SCHEMA = {
    "type": "object",
    "required": ["inferred_purpose", "confidence", "mode", "mooting_factors", "frames"],
    "properties": {
        # The decision purpose the lever INFERRED for the question (free text).
        "inferred_purpose": {"type": "string"},
        # Confidence in that inference — gates how hard the directive leans.
        "confidence": {"enum": CONFIDENCE_LEVELS},
        # Synthesis stance: one consolidated answer vs map multiple frames.
        "mode": {"enum": MODES},
        # Claim-refs whose own conditions are mooted (made irrelevant) by the
        # inferred purpose — surfaced, never silently dropped.
        "mooting_factors": {
            "type": "array",
            "items": {"type": "string"},
        },
        # One object per analytical frame; each buckets the confirmed claims by
        # relevance to the inferred purpose. Relevance FLOOR, not a filter —
        # not_relevant is demoted in emphasis, never deleted.
        "frames": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["frame", "decisive", "contextual", "not_relevant"],
                "properties": {
                    "frame": {"type": "string"},
                    "decisive": {"type": "array", "items": {"type": "string"}},
                    "contextual": {"type": "array", "items": {"type": "string"}},
                    "not_relevant": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
    },
}

# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------


def purpose_classify_prompt(
    question: str,
    confirmed_block: str,
    frames_ref: str = "references/purpose-frames.md",
) -> str:
    """Return the purpose-fit classification prompt for the confirmed claims.

    The prompt drives a relevance-FLOOR end-check: infer the decision purpose,
    pick a synthesis mode by inference confidence, then bucket every confirmed
    claim by relevance to that purpose WITHOUT deleting any (not_relevant items
    are kept and labeled, never dropped). It cites ``frames_ref`` as a path the
    agent reads at runtime for the question type's analytical frames.

    Mirrors mode_route.classify_prompt: f-string body, evidence block injected,
    structured-output-only close. Emits a verdict conforming to
    PURPOSE_FIT_SCHEMA.
    """
    return f"""\
Run a PURPOSE-FIT end-check over the confirmed claims. This is a relevance
FLOOR, not a filter: it decides how synthesis WEIGHTS and FRAMES the evidence
toward an inferred decision purpose. It never drops a confirmed claim.

## Question
{question}

## Evidence — confirmed claims (survived adversarial verification)
{confirmed_block}

## Step 1 — Infer the decision purpose
Infer the DECISION PURPOSE behind this question from the question text plus
any context (what decision is the asker actually trying to make?). State it
explicitly as a VISIBLE ASSUMPTION, and attach a `confidence` of `high`,
`medium`, or `low` in that inference.

## Step 2 — Choose the synthesis mode (by confidence)
- **high** confidence in the inferred purpose → `consolidated`: foreground the
  ONE inferred decision-frame and answer to it directly.
- **low** confidence, or a thin / ambiguous purpose → `multi-frame`: use the
  question type's N analytical frames from `{frames_ref}` (read that file) and
  present them EVENLY, without privileging one frame.
- medium → lean toward `multi-frame` unless the purpose is clearly singular.

## Step 3 — Classify each confirmed claim (do NOT delete any)
For each frame, bucket EVERY confirmed claim into exactly one of:
- **decisive** — directly settles or strongly drives the inferred decision.
- **contextual** — relevant background; informs but does not decide.
- **not_relevant** — does not bear on the inferred purpose.
This is a relevance floor: KEEP every claim. **Do not delete** any claim —
`not_relevant` items are RETAINED and LABELED, never removed. A claim demoted
to not_relevant stays in the output, just down-weighted in emphasis.

## Step 4 — Flag mooting factors
Surface any `mooting_factors`: confirmed claims that could SETTLE the decision
OUTRIGHT — a single fact that moots the rest of the analysis (e.g. a hard
constraint that makes other considerations irrelevant). Flag them; never let a
mooting factor sit silently inside a frame bucket.

## Claim references — use the [N] index
Every claim-ref you emit (in `decisive` / `contextual` / `not_relevant` /
`mooting_factors`) MUST be the bracketed **[N] index** exactly as printed in
the confirmed claims above (e.g. `[0]`, `[3]`) — NOT claim text, paraphrases,
or invented labels. The synthesis step reads the same `### [N]`-indexed block,
so only the `[N]` index lets it resolve your refs; any other scheme dangles.

## Output
Emit a verdict conforming to PURPOSE_FIT_SCHEMA:
- `inferred_purpose` (REQUIRED) — the decision purpose you inferred.
- `confidence` (REQUIRED) — high / medium / low.
- `mode` (REQUIRED) — consolidated / multi-frame.
- `mooting_factors` (REQUIRED) — array of claim-refs that could settle it.
- `frames` (REQUIRED) — array of frame objects, each with decisive /
  contextual / not_relevant claim-ref arrays.

Structured output only."""


# ---------------------------------------------------------------------------
# Synthesis directive block
# ---------------------------------------------------------------------------

# The moot-hoist callout marker. The eval found this is the LOAD-BEARING fix:
# when a confirmed claim could settle the decision OUTRIGHT, it MUST surface as
# a top-level callout ABOVE the frames — the macOS / k8s / microservices cases
# all failed because a mooting factor got dissolved into a single frame instead
# of being hoisted. Plain-ASCII fallback wording kept in the marker text so the
# signal survives even if the ⚠ glyph is stripped downstream.
_MOOT_MARKER = "MAY SETTLE THE DECISION OUTRIGHT"


def _render_bucket(label: str, refs) -> list[str]:
    """Render one relevance bucket as directive lines, or [] when empty.

    Keeps the bucket label even for not_relevant — the relevance FLOOR means a
    demoted claim is RETAINED and LABELED, never deleted.
    """
    if not refs:
        return []
    lines = [f"  {label}:"]
    lines.extend(f"    - {ref}" for ref in refs)
    return lines


def _render_frame(frame: dict) -> list[str]:
    """Render one frame as its own labeled sub-section.

    In multi-frame mode each frame is presented on its own terms (NOT merged
    into one union list); in consolidated mode there is one frame and its
    decisive set is foregrounded. Either way every bucket is rendered so no
    claim-ref is dropped.
    """
    name = frame.get("frame", "(unnamed frame)")
    lines = [f"### Frame — {name}"]
    lines.extend(_render_bucket("decisive", frame.get("decisive") or []))
    lines.extend(_render_bucket("contextual", frame.get("contextual") or []))
    # not_relevant is kept + honestly labeled (relevance floor, not a filter).
    lines.extend(_render_bucket("not_relevant (kept, down-weighted)",
                                frame.get("not_relevant") or []))
    return lines


def purpose_fit_block(verdict: dict) -> str:
    """Assemble the purpose-fit synthesis directive from a verdict.

    The directive is a synthesis-PREPEND (like mode_route.stance_block): the
    SKILL.md opt-in branch PREPENDs it to the base synthesis prompt; the synced
    prompts.py stays byte-identical.

    The assembled directive:
      (i)   states the inferred_purpose + confidence;
      (ii)  MOOT-HOIST — if mooting_factors is non-empty, renders a top-level
            callout ABOVE the frames (the load-bearing fix);
      (iii) consolidated mode foregrounds the single frame's decisive set;
            multi-frame mode renders each frame as its own labeled sub-section
            (never merged into one union list);
      (iv)  labels not_relevant honestly (kept, never deleted);
      (v)   NEVER drops a claim-ref — every ref anywhere in the verdict
            (decisive / contextual / not_relevant across all frames +
            mooting_factors) appears somewhere in the rendered block.
    """
    purpose = verdict.get("inferred_purpose", "(no purpose inferred)")
    confidence = verdict.get("confidence", "low")
    mode = verdict.get("mode", "multi-frame")
    mooting = verdict.get("mooting_factors") or []
    frames = verdict.get("frames") or []

    lines = [
        "SYNTHESIS DIRECTIVE — purpose-fit (relevance floor).",
        f"Inferred decision purpose: {purpose} (confidence: {confidence}).",
        "This weights and frames the confirmed evidence toward that purpose; it "
        "never drops a confirmed claim.",
    ]

    # (ii) MOOT-HOIST — top-level callout ABOVE the frames. Placed before any
    # frame content so a settle-outright fact is never buried in a bucket.
    if mooting:
        lines.append("")
        lines.append(f"⚠ {_MOOT_MARKER}:")
        lines.extend(f"  - {ref}" for ref in mooting)
        lines.append(
            "  Resolve this FIRST: if it holds, it may settle the decision and "
            "moot the frame analysis below. Do not bury it inside a frame."
        )

    # (iii) Frames. Consolidated → foreground the single frame's decisive set;
    # multi-frame → each frame is its own labeled section.
    lines.append("")
    if mode == "consolidated":
        lines.append(
            "MODE: consolidated — foreground the decisive set of the inferred "
            "frame and answer to it directly."
        )
    else:
        lines.append(
            "MODE: multi-frame — present each frame below on its own terms; do "
            "NOT merge them into one union list or privilege a single frame."
        )

    for frame in frames:
        lines.append("")
        lines.extend(_render_frame(frame))

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv=None) -> int:
    import argparse
    import json
    import sys

    args = sys.argv[1:] if argv is None else argv

    parser = argparse.ArgumentParser(prog="purpose_fit.py", add_help=False)
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("schema", add_help=False)
    sub.add_parser("block", add_help=False)  # reads verdict JSON from stdin
    p_classify = sub.add_parser("purpose-classify-prompt", add_help=False)
    p_classify.add_argument("--question", required=True)
    p_classify.add_argument("--confirmed-block", required=True)
    p_classify.add_argument("--frames-ref", default="references/purpose-frames.md")

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
        print(json.dumps(PURPOSE_FIT_SCHEMA, indent=2))
        return 0
    if ns.command == "purpose-classify-prompt":
        print(purpose_classify_prompt(ns.question, ns.confirmed_block, ns.frames_ref))
        return 0
    if ns.command == "block":
        # Mirror mode_route.py `stance`: read a verdict JSON object from stdin,
        # write the directive result object to stdout.
        verdict = json.load(sys.stdin)
        block = purpose_fit_block(verdict)
        json.dump({"purpose_fit_block": block}, sys.stdout)
        return 0
    return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
