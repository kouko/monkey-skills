"""Structural + behavioral test: driver_10_guard.js's fail-loud input contract.

Guards against the F4 silent-derail incident (2026-07-03 dogfood): template
slots leaked as the literal string "undefined" and stations improvised
substitute seeds instead of failing. guardArgs() must throw, naming exactly
which input is bad, rather than let a bad run proceed.

"""
import subprocess
from pathlib import Path

MODULE = Path(__file__).parent / "driver_10_guard.js"

REQUIRED_ARG_NAMES = ["segment", "changeId", "projectPath", "budgets", "models", "resumeRunId", "skillsRoot"]

FAIL_LOUD_PHRASE = "fail-loud: refusing to improvise missing inputs"


def test_fail_loud_guard():
    assert MODULE.exists(), f"missing {MODULE}"

    check = subprocess.run(
        ["node", "--check", str(MODULE)], capture_output=True, text=True
    )
    assert check.returncode == 0, f"node --check failed: {check.stderr}"

    source = MODULE.read_text()

    for name in REQUIRED_ARG_NAMES:
        assert name in source, f"driver_10_guard.js must reference arg {name!r}"

    assert "throw" in source, "guardArgs must throw on bad input"
    assert '"undefined"' in source or "'undefined'" in source, (
        "guardArgs must explicitly check for the literal string \"undefined\" "
        "(the exact F4 leak)"
    )
    assert FAIL_LOUD_PHRASE in source, (
        f"driver_10_guard.js must state the fail-loud contract ({FAIL_LOUD_PHRASE!r})"
    )

    # Behavioral: concatenate the module with a call using a leaked "undefined"
    # string for a required field and confirm the process actually fails.
    harness = source + "\n" + (
        "try {\n"
        '  guardArgs({segment: "undefined", changeId: "c1", projectPath: "/tmp/x", '
        "budgets: {}, models: {}});\n"
        "  process.exit(0);\n"
        "} catch (e) {\n"
        "  console.error(e.message);\n"
        "  process.exit(1);\n"
        "}\n"
    )
    result = subprocess.run(["node", "-e", harness], capture_output=True, text=True)
    assert result.returncode != 0, (
        'guardArgs({segment: "undefined", ...}) must throw, not proceed'
    )
    assert FAIL_LOUD_PHRASE in result.stderr, (
        "thrown error message must carry the fail-loud contract phrase"
    )

    # Behavioral: changeId with a path separator or traversal must throw
    # (it becomes a path segment under docs/loom/<changeId>/).
    traversal_harness = source + "\n" + (
        "try {\n"
        '  guardArgs({segment: 2, changeId: "../evil", projectPath: "/tmp/x", '
        'budgets: {tokens: 1000}, models: {code: "sonnet"}});\n'
        "  process.exit(0);\n"
        "} catch (e) {\n"
        "  console.error(e.message);\n"
        "  process.exit(1);\n"
        "}\n"
    )
    traversal_result = subprocess.run(
        ["node", "-e", traversal_harness], capture_output=True, text=True
    )
    assert traversal_result.returncode != 0, (
        'guardArgs({changeId: "../evil", ...}) must throw, not proceed'
    )

    # Behavioral: changeId allow-list — a shell-metacharacter changeId (no
    # "/" and no ".." so the old deny-list would have let it through) must
    # also throw. changeId becomes a path segment; only
    # [A-Za-z0-9._-] is safe there.
    shell_metachar_harness = source + "\n" + (
        "try {\n"
        '  guardArgs({segment: 2, changeId: "foo$(x)", projectPath: "/tmp/x", '
        'budgets: {tokens: 1000}, models: {code: "sonnet"}});\n'
        "  process.exit(0);\n"
        "} catch (e) {\n"
        "  console.error(e.message);\n"
        "  process.exit(1);\n"
        "}\n"
    )
    shell_metachar_result = subprocess.run(
        ["node", "-e", shell_metachar_harness], capture_output=True, text=True
    )
    assert shell_metachar_result.returncode != 0, (
        'guardArgs({changeId: "foo$(x)", ...}) must throw, not proceed'
    )

    # Behavioral: the OPTIONAL resumeRunId leaking as the literal "undefined"
    # must also throw — it lives in its own branch (not the REQUIRED_FIELDS
    # loop), so grep-presence alone would let a regression slip through.
    resume_harness = source + "\n" + (
        "try {\n"
        '  guardArgs({segment: 2, changeId: "c1", projectPath: "/tmp/x", '
        'budgets: {tokens: 1000}, models: {code: "sonnet"}, '
        'resumeRunId: "undefined"});\n'
        "  process.exit(0);\n"
        "} catch (e) {\n"
        "  console.error(e.message);\n"
        "  process.exit(1);\n"
        "}\n"
    )
    resume_result = subprocess.run(
        ["node", "-e", resume_harness], capture_output=True, text=True
    )
    assert resume_result.returncode != 0, (
        'guardArgs({..., resumeRunId: "undefined"}) must throw, not proceed'
    )
    assert FAIL_LOUD_PHRASE in resume_result.stderr, (
        "resumeRunId leak error must carry the fail-loud contract phrase"
    )

    # Behavioral: the OPTIONAL skillsRoot leaking as the literal "undefined"
    # must also throw (segment-2-only field; same F4-style leak guard as
    # resumeRunId).
    skills_root_harness = source + "\n" + (
        "try {\n"
        '  guardArgs({segment: 2, changeId: "c1", projectPath: "/tmp/x", '
        'budgets: {tokens: 1000}, models: {code: "sonnet"}, '
        'skillsRoot: "undefined"});\n'
        "  process.exit(0);\n"
        "} catch (e) {\n"
        "  console.error(e.message);\n"
        "  process.exit(1);\n"
        "}\n"
    )
    skills_root_result = subprocess.run(
        ["node", "-e", skills_root_harness], capture_output=True, text=True
    )
    assert skills_root_result.returncode != 0, (
        'guardArgs({..., skillsRoot: "undefined"}) must throw, not proceed'
    )
    assert FAIL_LOUD_PHRASE in skills_root_result.stderr, (
        "skillsRoot leak error must carry the fail-loud contract phrase"
    )

    # Behavioral: a fully valid args object must not throw.
    ok_harness = source + "\n" + (
        "guardArgs({segment: 2, changeId: 'c1', projectPath: '/tmp/x', "
        "budgets: {tokens: 1000}, models: {code: 'sonnet'}});\n"
        "process.exit(0);\n"
    )
    ok_result = subprocess.run(["node", "-e", ok_harness], capture_output=True, text=True)
    assert ok_result.returncode == 0, (
        f"guardArgs must accept a fully valid args object: {ok_result.stderr}"
    )
