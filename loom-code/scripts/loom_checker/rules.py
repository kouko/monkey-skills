from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path
from urllib.parse import quote

import yaml

from git_exec import run_git


RULES: list[tuple[str, str]] = [
    (
        "contract.requires",
        "A consumer plugin's requires-contract floor is met by this contract manifest version: "
        "the same major, and a minor at or above the required one.",
    ),
    (
        "contract.charter-complete",
        "Every artifact in the contract manifest carries a complete `charter:` block -- "
        "non-empty answers/readers/must/must_not/edits_after, a must_not goes_to naming "
        "another artifact in the table, and a signoff naming a real station.",
    ),
    (
        "intake.confirmed",
        "write-spec / write-plan accept only an intent whose status line reads `confirmed <date>` "
        "with a date the calendar has; `closed <date> — PR #<N>` or `closed <date> — branch <name>` "
        "is blocked -- that change is closed and a new change starts from a new intent. closed is "
        "terminal either way, and a confirmed intent is also blocked after canonical delivery evidence "
        "appears on the selected remote-default snapshot. Local branches and worktree evidence never "
        "prove delivery; an unresolved remote default is indeterminate and blocks intake.",
    ),
    (
        "intake.confirmed-behavior",
        "write-plan accepts a product change only when its spec carries a "
        "`confirmed-behavior: <date> @<spec-blob-sha7>` line naming the spec as it stands.",
    ),
    (
        "intake.test-case-pair",
        "Every task in a newly authored plan names the intent Acceptance lines it owns, "
        "and each named line has positive plus negative or boundary test cases.",
    ),
    (
        "intake.spec-ready",
        "write-plan accepts a needs-design: yes change only when its spec exists and carries "
        "an explicit `pre-build-review: required|not-required — <reason>` declaration. Review "
        "independence is enforced by the write-spec station, not persisted in a ledger.",
    ),
    (
        "intent.kind-recompute",
        "kind: engineering is rejected when the diff touches a declared interface-surface glob.",
    ),
    (
        "intent.needs-design-reason",
        "The needs-design line carries a reason and appears verbatim in the message of the "
        "commit that last changed the intent's status, needs-design or lane line.",
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
        "plan.field-caps",
        "A plan whose frontmatter carries a `charter:` key (any value, presence only) caps each "
        "task's Test and Risk lines at 40 words, its Files line at 8 comma-separated entries "
        "(a comma inside backticks does not split), each numbered `## Risks` item at 40 words, "
        "and each `## Current State Evidence` bullet at 30 words -- CJK runs with no internal "
        "whitespace count as one word by len(text.split()); a task missing its Files, Test or "
        "Risk line blocks too. A plan with no `charter:` line is skipped entirely.",
    ),
    (
        "spec.req-grammar",
        "Every Requirements entry reads `REQ-<n> — <name>` with n contiguous from 1, "
        "unique, and points at an Acceptance number the intent actually carries.",
    ),
    (
        "spec.ui-flows-recompute",
        "While the diff touches a declared interface-surface glob, the spec's UI flows section "
        "carries at least one prose line (outside fences, indented code and HTML comments) with an arrow and "
        "at least four visible characters on each side. This is a structural floor only -- "
        "whether the flow says anything true or useful is the reviewer lens's job, not a "
        "keyword list's. Runs at write-plan intake only.",
    ),
    (
        "standing.product-principles-reject",
        "A product change is rejected until PRINCIPLES.md is ratified: a `ratified-by: <name> "
        "<YYYY-MM-DD>` signature with a real date, over three or more distinct non-negotiables.",
    ),
    (
        "standing.second-vendor-valid",
        "KICKOFF-DEFAULTS rejects the removed `second-vendor: none` value with explicit "
        "migration guidance to use the non-blocking `suggest` mode.",
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


RULES.append((
    "push.attestation",
    "The branch carries one generated attestation whose functional-content digest, "
    "successful executions, command identities, and passing reviewer verdicts validate "
    "without replaying package tests or adversarial probes.",
))


RULES.append((
    "push.contextual-body",
    "The exact pull-request body carries Ship's nine top-level contextual headings "
    "exactly once and in order, with no competing Memory heading or explicit claim "
    "to expose private or hidden chain-of-thought.",
))


def list_rules(out=sys.stdout) -> int:
    for rule_id, description in sorted(RULES):
        out.write(f"{rule_id}\t{description}\n")
    return 0


__all__ = [name for name in globals() if not name.startswith("__")]
