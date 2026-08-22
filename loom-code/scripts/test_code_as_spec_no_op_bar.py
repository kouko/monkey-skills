"""Bars the code-as-spec lens from declaring deletion-first a no-op.

@req: none (this arc carries no registered REQ-ids in its plan/spec).
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CODE_REVIEWER = REPO_ROOT / "loom-code" / "agents" / "code-reviewer.md"
DOCS_REVIEWER = REPO_ROOT / "loom-code" / "agents" / "docs-reviewer.md"

NO_OP_CLAUSE = "makes this dimension never a no-op"


def _flatten(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def test_code_arm_bars_the_no_op_declaration():
    # Reads the WORKING TREE, not a committed blob: an implementer cannot
    # commit under the SDD contract, so a test reading committed content
    # can never go green here.
    text = CODE_REVIEWER.read_text(encoding="utf-8")
    flattened = _flatten(text)
    assert NO_OP_CLAUSE in flattened, (
        "code-reviewer.md's code-as-spec lens must bar declaring the "
        "deletion-first dimension a no-op when the diff touches docstring "
        "or comment lines"
    )


def test_docs_arm_bars_the_no_op_declaration():
    # Mirrors the code arm's bar: the two reviewer arms hold mirrored
    # halves of one rule, so both must carry the shared no-op clause or
    # the rule binds only one arm.
    text = DOCS_REVIEWER.read_text(encoding="utf-8")
    flattened = _flatten(text)
    assert NO_OP_CLAUSE in flattened, (
        "docs-reviewer.md's code-as-spec lens must bar declaring the "
        "omission dimension a no-op when the diff touches contract-class "
        "prose lines"
    )
