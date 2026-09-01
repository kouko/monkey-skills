"""CI scan: the loom-design suite must be invoked from ONE workflow step.

Task 1 of this arc gave `loom-design/scripts/` a pytest root that collects
every station directory in a single invocation. This test pins the CI side
of that: the five per-directory pytest jobs collapse to one, and no workflow
comment may keep asserting that the suites need separate invocations.
"""

import pathlib
import re

WORKFLOWS = pathlib.Path(__file__).resolve().parents[1] / ".github" / "workflows"

# The invocation shape itself -- `pytest <path under loom-design/scripts>` --
# not merely a line that mentions loom-design.
INVOCATION = re.compile(r"\bpytest\s+(loom-design/scripts\S*)")

# A comment asserting the suites cannot share one invocation, e.g.
# "The suites MUST run as separate pytest invocations" /
# "This suite runs as its OWN pytest invocation".
SEPARATE_CLAIM = re.compile(r"(?i)\b(?:own|separate)\s+pytest\s+invocations?\b")


def _workflow_files():
    return sorted(
        p for p in WORKFLOWS.iterdir() if p.suffix in (".yml", ".yaml")
    )


def _split_comment_and_code(text):
    """Return (joined comment prose, code-only lines) for one workflow file."""
    comments, code = [], []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            comments.append(line.lstrip().lstrip("#").strip())
        else:
            code.append(line)
    return " ".join(comments), code


def test_workflows_invoke_loom_design_suite_once():
    invocations = []
    offending_comments = []

    for path in _workflow_files():
        text = path.read_text(encoding="utf-8")
        if "loom-design" not in text:
            # Other plugins' workflows are out of scope: loom-workflow-ci.yml
            # legitimately runs a pytest invocation per skill directory.
            continue
        prose, code = _split_comment_and_code(text)
        for line in code:
            for match in INVOCATION.finditer(line):
                invocations.append(f"{path.name}: {match.group(1)}")
        if SEPARATE_CLAIM.search(prose):
            offending_comments.append(path.name)

    assert invocations == ["loom-pipeline-ci.yml: loom-design/scripts/"], (
        "expected exactly one unified loom-design pytest invocation across "
        f".github/workflows/, got {invocations}"
    )
    assert offending_comments == [], (
        "workflow comments still claim the loom-design suites need separate "
        f"pytest invocations: {offending_comments}"
    )
