"""Structural test: using-loom-pipeline SKILL.md carries the fire-condition
gate, the N/A-loud clause, the 6-field run-input contract, and the
Workflow({scriptPath...}) invocation resolved from the skill's base path.

"""
import base64
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

PLUGIN_ROOT = Path(__file__).parents[2]
SKILL_MD = PLUGIN_ROOT / "skills" / "using-loom-pipeline" / "SKILL.md"


def _body(text: str) -> str:
    """Text AFTER the closing frontmatter fence.

    The description frontmatter legitimately mentions Workflow / the station
    plugins / N/A, so whole-file matching would let the body's §When-it-fires
    section be deleted while the test stays green (house precedent:
    loom-code/scripts/test_ui_verification_skill.py's _frontmatter split).
    """
    parts = text.split("---", 2)
    assert len(parts) >= 3, "SKILL.md lost its frontmatter fences"
    return parts[2]


def test_fire_inputs_and_invocation():
    assert SKILL_MD.exists(), f"missing {SKILL_MD}"
    text = SKILL_MD.read_text()
    lower = text.lower()
    body = _body(text)
    body_lower = body.lower()

    # Both fire conditions — asserted against the BODY so deleting
    # §When it fires cannot pass on frontmatter mentions alone.
    assert "workflow" in body_lower and "available" in body_lower, \
        "missing Workflow-tool-availability fire condition in the body"
    assert (
        "loom-design" in body
        and "loom-code" in body
    ), "missing the two station-plugin names in the body"

    # N/A-loud clause (body-scoped).
    assert "loom-design: n/a" in body_lower, \
        "missing the N/A-loud emission clause in the body"

    # 5 run-input fields.
    assert "change-id" in lower, "missing change-id run input"
    assert "project path" in lower, "missing target project path run input"
    assert "budget" in lower, "missing token-budget run input"
    assert "model" in lower, "missing model-policy run input"
    assert "resumerunid" in lower, "missing resumeRunId run input"
    assert "skillsroot" in lower, "missing skillsRoot run input"

    # Invocation mechanism.
    assert "Workflow({scriptPath" in text, \
        "missing the literal Workflow({scriptPath invocation snippet"
    assert "base path" in lower or "base directory" in lower, \
        "missing base-path-resolution mention"


def test_skill_batch_mode_section_contract():
    assert SKILL_MD.exists(), f"missing {SKILL_MD}"
    text = SKILL_MD.read_text()
    body = _body(text)
    body_lower = body.lower()

    batch_idx = body_lower.find("## §batch mode")
    assert batch_idx != -1, "missing §Batch mode heading"
    batch_section = body[batch_idx:]
    batch_section_lower = batch_section.lower()

    # Three dispatcher-only prohibitions, verbatim (plan Task 11 / brief
    # Smallest End State §3), scoped to the §Batch mode section itself so
    # this can't pass on an unrelated mention elsewhere in the file.
    assert "never parses the queue file" in batch_section_lower, \
        "missing 'never parses the queue file' prohibition"
    assert "never composes git commands" in batch_section_lower, \
        "missing 'never composes git commands' prohibition"
    assert "never diagnoses failures mid-batch" in batch_section_lower, \
        "missing 'never diagnoses failures mid-batch' prohibition"

    # next -> Workflow -> mark loop, in that order, within §Batch mode
    # (the §Invocation section earlier in the file has its own unrelated
    # Workflow({ call, so this must not scan the whole document).
    next_match = re.search(r'batchQueueArgv = \["next"', batch_section)
    workflow_idx = batch_section.find("Workflow(")
    mark_match = re.search(r'batchQueueArgv = \["mark-running"', batch_section)
    next_idx = next_match.start() if next_match else -1
    mark_idx = mark_match.start() if mark_match else -1
    assert -1 not in (next_idx, workflow_idx, mark_idx), \
        "missing one of next / Workflow / mark in the §Batch mode loop description"
    assert next_idx < workflow_idx < mark_idx, \
        "next -> Workflow -> mark loop is not documented in that order"

    # Both queue files named.
    assert "QUEUE.toml" in batch_section, "missing QUEUE.toml"
    assert "queue-state.json" in batch_section, "missing queue-state.json"


def test_skill_intake_section_contract():
    """§Intake is the first '## ' section in the body, carries the three
    steps (前站檢查 / 對站檢查 / re-affirm this skill's own fire condition),
    references the reception's on-ramp table by path (never copies its
    rows), and leaves the existing N/A-loud wording byte-present and
    unsoftened (plan Task A2 / brief §Open Q2).
    """
    assert SKILL_MD.exists(), f"missing {SKILL_MD}"
    text = SKILL_MD.read_text()
    body = _body(text)

    headings = re.findall(r"^## (.+)$", body, re.MULTILINE)
    assert headings, "no '## ' headings found in body"
    assert headings[0].strip().lower() == "§intake", (
        f"§Intake must be the FIRST '## ' section in the body "
        f"(after frontmatter/SUBAGENT-STOP); found {headings[0]!r} first"
    )

    intake_idx = body.find("## " + headings[0])
    next_idx = body.find("\n## ", intake_idx + 1)
    intake_section = body[intake_idx:next_idx] if next_idx != -1 else body[intake_idx:]

    # Step 1 — 前站檢查: point to the reception's on-ramp table by
    # path/name, never copy the table body (Reception SSOT rule).
    assert "前站檢查" in intake_section, "missing step 1 前站檢查 label"
    assert "family-reception.md" in intake_section, \
        "step 1 must point to the reception file by path"
    assert "on-ramp" in intake_section.lower(), \
        "step 1 must name the on-ramp criteria table"
    assert "| Condition |" not in intake_section, \
        "§Intake must not copy the on-ramp criteria table body"

    # Step 2 — 對站檢查: interactive design/spec/code work hands off to
    # that family's own using-loom-* entry.
    assert "對站檢查" in intake_section, "missing step 2 對站檢查 label"
    for entry in (
        "using-loom-design",
        "using-loom-design",
        "using-loom-design",
        "using-loom-code",
    ):
        assert entry in intake_section, f"step 2 missing hand-off to {entry}"

    # Step 3 — restates this skill's own fire condition; must not soften
    # or duplicate-with-drift the existing N/A-loud constitution.
    pinned_phrase = "never silently skip, and never fake the orchestration inline"
    assert pinned_phrase in body, \
        "existing N/A-loud phrase was altered or removed — no softening allowed"


def test_pipeline_public_commands_use_installed_plugin_root_and_preserve_code_handoffs(
    tmp_path,
):
    """Public commands resolve from loom-design's installed root, while the
    conductor retains only public, plugin-qualified code-stage composition.

    Check both the positive command shape and the obsolete checkout shape so
    deleting either half of the contract makes this test fail.
    """
    body = _body(SKILL_MD.read_text())

    assert (
        "**skillsRoot**" in body
        and "installed loom-design plugin root" in body
    ), "skillsRoot must be defined as the installed loom-design plugin root"
    batch_commands = re.findall(r"batchQueueArgv\s*=\s*\[([^\]]+)\]", body)
    assert len(batch_commands) == 7, \
        "expected every one of the seven public batch argv arrays"
    required_arguments = {
        "reconcile": ('"--project", projectPath',),
        "next": ('"--project", projectPath', '"--skills-root", pluginRoot'),
        "mark-running": (
            'id', '"--run-id", workflowRunId', '"--session-dir", sessionDir',
            '"--project", projectPath',
        ),
        "mark": (
            'id', 'outcome', '"--project", projectPath',
            '"--run-id", workflowRunId',
        ),
        "reset": ('id', '"--project", projectPath', '"--reason", reason'),
        "force-fail": ('id', '"--reason", reason', '"--project", projectPath'),
        "status": ('"--project", projectPath',),
    }
    for verb, arguments in required_arguments.items():
        command = next(
            command for command in batch_commands if f'"{verb}"' in command
        )
        assert command.lstrip().startswith(f'"{verb}"'), \
            f"{verb} must be the first batch_queue argv element"
        for argument in arguments:
            assert argument in command, \
                f"{verb} must pass dynamic argument as an argv element: {argument}"
    assert "<skillsRoot>/loom-design/scripts/" not in body, \
        "checkout-shaped sibling path remains in the public contract"
    assert "monkey-skills checkout / plugin source root" not in body, \
        "skillsRoot still describes the monorepo checkout"
    assert "loom-code/" not in body, \
        "pipeline contract must not reach into loom-code private paths"

    for public_handoff in (
        "loom-code:subagent-driven-development",
        "loom-code:requesting-code-review",
        "loom-code:ui-verification",
    ):
        assert public_handoff in body, \
            f"Segment 3 lost public code-stage handoff {public_handoff}"

    # Execute the documented read-only status command from roots containing
    # both whitespace and a single quote. A lexical-only check cannot prove
    # the shell example survives real argument parsing.
    installed_root = tmp_path / "installed loom-design's root"
    script_dir = installed_root / "scripts" / "pipeline"
    script_dir.mkdir(parents=True)
    shutil.copy2(PLUGIN_ROOT / "scripts" / "pipeline" / "batch_queue.py", script_dir)
    project_path = tmp_path / "consumer project's files"
    loom_dir = project_path / "docs" / "loom"
    loom_dir.mkdir(parents=True)
    (loom_dir / "QUEUE.toml").write_text(
        '[[change]]\nid = "quote-safe"\nplan = "docs/loom/plans/x.md"\n'
        '[change.budgets]\nrun = 1\n',
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            "python3", str(script_dir / "batch_queue.py"), "status",
            "--project", str(project_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "quote-safe" in result.stdout


def test_pipeline_dynamic_values_are_passed_as_literal_argv(tmp_path):
    """Consumer values are data, never shell source code."""
    body = _body(SKILL_MD.read_text())

    # Characterize why the former double-quoted shell-template contract is
    # unsafe: command substitution is still evaluated inside double quotes.
    old_side_effect = tmp_path / "old-shell-side-effect"
    hostile_old_value = f'$(touch "{old_side_effect}")'
    subprocess.run(
        f'python3 -c "import sys" "{hostile_old_value}"',
        shell=True,
        executable="/bin/bash",
        check=True,
    )
    assert old_side_effect.exists(), "fixture no longer demonstrates the old risk"

    command_match = re.search(
        r'`(python3 "\$\{CLAUDE_PLUGIN_ROOT\}/scripts/pipeline/'
        r'argv_exec\.py" <URL_SAFE_BASE64_JSON_ARGV>)`',
        body,
    )
    assert command_match, "missing the fixed shell-host bridge command"
    assert "urlsafe_b64encode" in body and "JSON list of strings" in body
    assert "outcome is exactly `done` or `failed`" in body
    assert "omit both elements" in body, \
        "reset must define how its optional reason is omitted"

    installed_root = tmp_path / "installed loom-design's root"
    script_dir = installed_root / "scripts" / "pipeline"
    script_dir.mkdir(parents=True)
    for script_name in ("argv_exec.py", "batch_queue.py"):
        shutil.copy2(PLUGIN_ROOT / "scripts" / "pipeline" / script_name, script_dir)
    project_path = tmp_path / "consumer project's files"
    loom_dir = project_path / "docs" / "loom"
    loom_dir.mkdir(parents=True)
    (loom_dir / "QUEUE.toml").write_text(
        '[[change]]\nid = "safe-id"\nplan = "docs/loom/plans/x.md"\n'
        '[change.budgets]\nrun = 1\n',
        encoding="utf-8",
    )
    (loom_dir / "queue-state.json").write_text(
        json.dumps({"safe-id": {"status": "FAILED"}}),
        encoding="utf-8",
    )
    forbidden_side_effect = tmp_path / "argv-side-effect"
    hostile_reason = (
        'double " quote $literal-dollar '
        f'$(touch "{forbidden_side_effect}") '
        f'`touch "{forbidden_side_effect}"` '
        f'; touch "{forbidden_side_effect}"\nsecond line'
    )
    argv = [
        "reset", "safe-id", "--project", str(project_path),
        "--reason", hostile_reason,
    ]
    payload = base64.urlsafe_b64encode(
        json.dumps(argv).encode("utf-8")
    ).decode("ascii").rstrip("=")
    assert re.fullmatch(r"[A-Za-z0-9_-]+", payload)
    command = command_match.group(1).replace(
        "<URL_SAFE_BASE64_JSON_ARGV>", payload
    )
    env = os.environ.copy()
    env["CLAUDE_PLUGIN_ROOT"] = str(installed_root)
    subprocess.run(
        command,
        shell=True,
        executable="/bin/bash",
        env=env,
        check=True,
    )
    state = json.loads((loom_dir / "queue-state.json").read_text())
    assert state["safe-id"]["audit"][-1]["reason"] == hostile_reason
    assert not forbidden_side_effect.exists()

    helper = script_dir / "argv_exec.py"
    malformed_payloads = [
        "not+url-safe",  # forbidden alphabet
        base64.urlsafe_b64encode(b"not json").decode("ascii"),
        base64.urlsafe_b64encode(json.dumps({"not": "a list"}).encode()).decode(),
        base64.urlsafe_b64encode(json.dumps(["status", 1]).encode()).decode(),
        base64.urlsafe_b64encode(json.dumps(["unknown"]).encode()).decode(),
        base64.urlsafe_b64encode(
            json.dumps(["status", "--project", ".", "--extra", "x"]).encode()
        ).decode(),
    ]
    for malformed in malformed_payloads:
        rejected = subprocess.run(
            ["python3", str(helper), malformed], capture_output=True, text=True
        )
        assert rejected.returncode == 2, malformed
