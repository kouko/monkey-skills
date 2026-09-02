#!/usr/bin/env python3
"""The loom checker -- the single deterministic layer of the loom flow.

Every rule here RECOMPUTES its fact from the repository (the intent file,
the manifest, the git diff, review.json, the dispatch record). No rule
trusts an agent's claim about itself; concept-model §7 is explicit that
this layer stops missed steps, not a goal-directed agent.

Sub-commands (the CLI contract other stations depend on):

    loom_checker.py --list-rules
    loom_checker.py intent <path> [--commit-msg <file>]
    loom_checker.py intake <station> <change-id>
    loom_checker.py push [--head <ref>] [--base <ref>]
    loom_checker.py standing <path-to-intent>
    loom_checker.py hooks-probe

Exit codes: 0 pass, 1 a rule failed (`BLOCK <rule.id>: <reason>` on
stderr), 2 usage or internal error. Any unexpected exception fails
closed as exit 2 -- a checker that cannot decide never says "fine".

Schemas are not restated here: the required frontmatter fields, sections,
station names, interface-surface defaults and artifact paths are read
from `loom-code/contract/manifest.yaml`, which is the versioned contract
package this checker ships with.
"""
from __future__ import annotations

import sys
from pathlib import Path

MANIFEST_PATH = Path(__file__).resolve().parents[1] / "contract" / "manifest.yaml"

USAGE = __doc__.split("Sub-commands (the CLI contract other stations depend on):", 1)[1]

RULES: list[tuple[str, str]] = [
    (
        "intake.confirmed",
        "write-spec / write-plan accept only an intent whose status line reads `confirmed <date>`.",
    ),
    (
        "intake.confirmed-behavior",
        "write-plan accepts a product change only when its spec carries a `confirmed-behavior: <date>` line.",
    ),
    (
        "intake.spec-pass",
        "write-plan accepts a needs-design: yes change only when the latest spec review round is all PASS or PASS_WITH_NOTES.",
    ),
    (
        "intent.needs-design-reason",
        "The needs-design line carries a reason and the same line appears verbatim in the intent's commit message.",
    ),
    (
        "intent.needs-design-recompute",
        "needs-design: no is rejected when the diff touches a declared interface-surface glob.",
    ),
    (
        "intent.product-no-identifiers",
        "A product intent's Problem section names no file path, code identifier or script filename.",
    ),
    (
        "intent.schema",
        "The intent file carries every required frontmatter field and H2 section declared in the contract manifest.",
    ),
    (
        "push.open-findings-closed",
        "Every open_findings entry in review.json is resolved or dismissed.",
    ),
    (
        "push.probes-package-tests",
        "review.json probes[] records a package-test run for this branch whose result is pass.",
    ),
    (
        "push.review-only-head",
        "HEAD is a review-only commit that touches nothing but docs/loom/<change-id>/review.json.",
    ),
    (
        "push.reviewed-sha",
        "review.json reviewed_sha names the commit HEAD^, so the reviewed tree is the pushed tree.",
    ),
    (
        "push.reviewer-ne-implementer",
        "No reviewer, blind-runner or adversary in the dispatch record also implemented the change.",
    ),
    (
        "push.verdicts-ge-2",
        "The latest review round carries at least two distinct fresh-context reviewers.",
    ),
    (
        "standing.product-principles-reject",
        "A product change is rejected while the repo has no ratified PRINCIPLES.md.",
    ),
    (
        "standing.silence",
        "KICKOFF-DEFAULTS `standing-docs: waived` silences the WARN only, never the product rejection.",
    ),
    (
        "standing.warn",
        "A missing PRINCIPLES.md or DESIGN.md prints the fixed three-line WARN and never blocks.",
    ),
]


class UsageError(Exception):
    """Bad invocation or an unreadable operand -- exit 2, never exit 0."""


def list_rules(out=sys.stdout) -> int:
    for rule_id, description in sorted(RULES):
        out.write(f"{rule_id}\t{description}\n")
    return 0


def report(failures: list[tuple[str, str]], err=sys.stderr) -> int:
    for rule_id, reason in failures:
        err.write(f"BLOCK {rule_id}: {reason}\n")
    return 1 if failures else 0


def cmd_intent(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    raise NotImplementedError("intent rules land in plan task W0-03")


def cmd_intake(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    raise NotImplementedError("intake rules land in plan task W0-03")


def cmd_push(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    raise NotImplementedError("push rules land in plan task W0-04")


def cmd_standing(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    raise NotImplementedError("standing rules land in plan task W0-04")


def cmd_hooks_probe(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    raise UsageError("hooks-probe is reserved and not implemented yet (plan task W0-05)")


COMMANDS = {
    "intent": cmd_intent,
    "intake": cmd_intake,
    "push": cmd_push,
    "standing": cmd_standing,
    "hooks-probe": cmd_hooks_probe,
}


def main(argv: list[str], out=sys.stdout, err=sys.stderr) -> int:
    try:
        if not argv:
            raise UsageError("no sub-command given." + USAGE)
        if argv[0] == "--list-rules":
            return list_rules(out)
        command = COMMANDS.get(argv[0])
        if command is None:
            raise UsageError(f"unknown sub-command {argv[0]!r}." + USAGE)
        return command(argv[1:], out, err)
    except UsageError as exc:
        err.write(f"{exc}\n")
        return 2
    except Exception as exc:  # fail-closed: an undecidable check never passes
        err.write(f"loom_checker internal error: {type(exc).__name__}: {exc}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
