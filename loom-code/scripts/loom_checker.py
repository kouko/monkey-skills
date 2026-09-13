#!/usr/bin/env python3
"""The loom checker -- the single deterministic layer of the loom flow.

Every rule here RECOMPUTES its fact from the repository (the intent file,
the manifest, the git diff, or the generated attestation). No rule
trusts an agent's claim about itself; concept-model §7 is explicit that
this layer stops missed steps, not a goal-directed agent.

Sub-commands (the CLI contract other stations depend on):

    loom_checker.py --list-rules
    loom_checker.py intent <path> [--commit-msg <file>]
    loom_checker.py intents [<change-id>] [--remote <name>] [--metadata]
    loom_checker.py intake <station> <change-id>
    loom_checker.py push [--head <ref>] [--hook]
    loom_checker.py publish --intent <absolute-path> --title <text> --body-file <absolute-path>
    loom_checker.py publish --confirm-authorized --title <text> --body-file <absolute-path>
    loom_checker.py reviewer-count <change-id>
    loom_checker.py finalize-review <change-id> --input <review-input.json>
    loom_checker.py standing <path-to-intent>
    loom_checker.py contract --require <major.minor>

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

from loom_checker.command_handlers.charter import cmd_charter
from loom_checker.command_handlers.contract import cmd_contract
from loom_checker.command_handlers.finalize import cmd_finalize_review
from loom_checker.command_handlers.intake import cmd_intake
from loom_checker.command_handlers.intent import cmd_intent
from loom_checker.command_handlers.intents import cmd_intents
from loom_checker.command_handlers.plan import cmd_plan
from loom_checker.command_handlers.publish import cmd_publish
from loom_checker.command_handlers.push import cmd_push
from loom_checker.command_handlers.reviewer_count import cmd_reviewer_count
from loom_checker.command_handlers.standing import cmd_standing
from loom_checker.helpers import UsageError
from loom_checker.rules import list_rules


USAGE = __doc__.split("Sub-commands (the CLI contract other stations depend on):", 1)[1]


COMMANDS = {
    "intent": cmd_intent,
    "intents": cmd_intents,
    "intake": cmd_intake,
    "push": cmd_push,
    "publish": cmd_publish,
    "standing": cmd_standing,
    "contract": cmd_contract,
    "charter": cmd_charter,
    "plan": cmd_plan,
    "reviewer-count": cmd_reviewer_count,
    "finalize-review": cmd_finalize_review,
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
    except Exception as exc:
        err.write(f"loom_checker internal error: {type(exc).__name__}: {exc}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
