"""Reject review contracts that can reopen a bounded closing episode."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
review = (ROOT / "loom-code/skills/review/SKILL.md").read_text(encoding="utf-8")
reviewer = (ROOT / "loom-code/agents/reviewer.md").read_text(encoding="utf-8")
contract = " ".join((review + "\n" + reviewer).split())

required = (
    "at most three distinct functional-content digests",
    "changing the task, app, branch, reviewer, vendor, model, or technical design does not reset",
    "never dispatch Round 4",
    "Do not ask the user whether to continue",
    "retry once against the same functional-content digest",
    "A second executor failure ends the episode as `EXECUTION_FAILED`",
    "Do not create a review-round ledger or committed state schema",
)
missing = [clause for clause in required if clause not in contract]
if missing:
    raise SystemExit("missing convergence clauses: " + "; ".join(missing))

print("bounded review convergence contract: PASS")
