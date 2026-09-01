"""CI scan: the loom-design suite must be invoked from ONE workflow step.

Task 1 of this arc gave `loom-design/scripts/` a pytest root that collects
every station directory in a single invocation. This test pins the CI side
of that: the five per-directory pytest jobs collapse to one, and no workflow
comment may keep asserting that the suites need separate invocations.

SCOPE, stated plainly because a guard that overstates itself is worse than
one that is honest: this is a TEXT scan of the workflow YAML, not a parse of
each step into `run` + `working-directory`. It sees an invocation only when
the literal path `loom-design/scripts...` appears in the step's own text. It
therefore covers: the path anywhere after `pytest` (flags in between), and a
`run: |` block splitting the command from its path across lines. The two
shapes that would otherwise reach the suite WITHOUT that literal adjacency --
`working-directory: loom-design/scripts` plus `run: pytest spec/`, and
`run: cd loom-design/scripts && pytest spec/` -- are handled by refusing the
relocation outright (`test_workflows_do_not_relocate_into_the_suite_root`)
rather than by resolving it, so the scan keeps working on explicit paths.

What is still NOT caught, and would need a real per-step YAML parse to close:
a path reaching pytest through a shell variable, a `matrix` expansion, a
composite/reusable action defined outside `.github/workflows/`, or a
positional argument sitting between `pytest` and the path
(`pytest tests/ loom-design/scripts/spec/` -- INVOCATION allows only flags
there, and that form was judged contrived enough not to widen it for).
"""

import pathlib
import re

WORKFLOWS = pathlib.Path(__file__).resolve().parents[1] / ".github" / "workflows"

# The invocation shape itself -- `pytest <path under loom-design/scripts>` --
# not merely a line that mentions loom-design. Flags are allowed between the
# command and the path (`pytest -q loom-design/scripts/spec/`): pinning the
# path as the token immediately after `pytest` left every flag-first fan-out
# invisible. `\s` spans newlines so a `run: |` block that wraps the command
# is matched too -- see `_find_invocations`, which scans the file as one
# string for exactly that reason.
INVOCATION = re.compile(
    r"\bpytest\b"                       # the command
    r"(?:\s+(?:\\|-\S+(?:\s+(?!-)\S+)?))*"  # ... flags (+ values) and `\` line-continuations
    r"\s+(loom-design/scripts\S*)"       # ... then the suite path
)

# A step that moves the shell INTO the suite root, after which a bare
# `pytest spec/` would reach the suite with no literal `loom-design/scripts`
# next to it. The text scan structurally cannot resolve those, so they are
# refused rather than resolved -- keep the invocation path explicit.
RELOCATION = re.compile(
    r"(?:working-directory:\s*|\bcd\s+)(loom-design/scripts\S*)"
)

# A comment asserting the suites cannot share one invocation, e.g.
# "The suites MUST run as separate pytest invocations" /
# "This suite runs as its OWN pytest invocation".
SEPARATE_CLAIM = re.compile(r"(?i)\b(?:own|separate)\s+pytest\s+invocations?\b")


def _workflow_files():
    return sorted(
        p for p in WORKFLOWS.iterdir() if p.suffix in (".yml", ".yaml")
    )


def _split_comment_and_code(text):
    """Return (joined comment prose, code-only text) for one workflow file."""
    comments, code = [], []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            comments.append(line.lstrip().lstrip("#").strip())
        else:
            code.append(line)
    return " ".join(comments), "\n".join(code)


def _find_invocations(code):
    """Every `pytest ... loom-design/scripts/...` invocation in workflow code.

    Scans the code as ONE string rather than line by line: a `run: |` block
    may split the command and its path across lines, and per-line matching
    would leave such a restored fan-out job invisible to the assertion.
    """
    return [m.group(1) for m in INVOCATION.finditer(code)]


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
        for found in _find_invocations(code):
            invocations.append(f"{path.name}: {found}")
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


# The four shapes a restored per-station job could take, all of which the
# guard must see. Only the first has the path as the token immediately
# after `pytest`; the other three put a flag in between.
FAN_OUT_FORMS = (
    "        run: python3 -m pytest loom-design/scripts/ -q",
    "        run: python3 -m pytest -q loom-design/scripts/spec/",
    "        run: python3 -m pytest --import-mode=importlib "
    "loom-design/scripts/interface/",
    "        run: pytest -x loom-design/scripts/principles/",
)

# A `run: |` block that splits the command from its path across lines.
MULTILINE_FAN_OUT = """    steps:
      - name: spec suite
        run: |
          python3 -m pytest \\
            loom-design/scripts/spec/
"""


def test_guard_sees_a_flag_before_the_path():
    for form in FAN_OUT_FORMS:
        _prose, code = _split_comment_and_code(form)
        assert _find_invocations(code), (
            "fan-out invocation invisible to the guard -- a restored "
            f"per-station job written this way would pass: {form!r}"
        )


def test_guard_sees_a_run_block_split_across_lines():
    _prose, code = _split_comment_and_code(MULTILINE_FAN_OUT)
    assert _find_invocations(code) == ["loom-design/scripts/spec/"], (
        "a `run: |` block splitting `pytest` from its path across lines "
        "hid the invocation from the guard"
    )


def test_workflows_do_not_relocate_into_the_suite_root():
    """No workflow step may cd / working-directory into loom-design/scripts.

    Both shapes let a restored per-station job (`pytest spec/`) run with no
    literal `loom-design/scripts` beside `pytest`, which the text scan above
    cannot see. Refusing the relocation keeps the scan's premise true.
    """
    relocations = []
    for path in _workflow_files():
        text = path.read_text(encoding="utf-8")
        if "loom-design" not in text:
            continue
        _prose, code = _split_comment_and_code(text)
        for match in RELOCATION.finditer(code):
            relocations.append(f"{path.name}: {match.group(0).strip()}")

    assert relocations == [], (
        "a workflow step relocates the shell into the loom-design suite "
        "root, which hides the pytest invocation path from the "
        f"single-invocation scan: {relocations}. Invoke the suite with its "
        "full path from the repo root instead."
    )


RELOCATION_FORMS = (
    "        working-directory: loom-design/scripts\n"
    "        run: python3 -m pytest spec/",
    "        run: cd loom-design/scripts && pytest spec/",
)


def test_relocation_forms_are_recognised():
    for form in RELOCATION_FORMS:
        _prose, code = _split_comment_and_code(form)
        assert RELOCATION.search(code), (
            "a step relocating into the suite root would slip past both "
            f"assertions: {form!r}"
        )
