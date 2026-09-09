#!/usr/bin/env python3
"""Adversarial, stdlib-only checks for the goal-create activation contract."""

from pathlib import Path
import re


REPO = Path(__file__).resolve().parents[5]
SKILL = REPO / "loom-workflow/skills/goal-create/SKILL.md"
MECHANISMS = REPO / "docs/loom/evidence/mechanisms.yaml"


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"missing required contract text: {needle}")


def validate(skill: str, mechanisms: str) -> None:
    start = skill.index("<!-- gate: goal-create.session-activation -->")
    end = skill.index("<!-- /gate -->", start)
    gate = " ".join(skill[start:end].split())

    for required in (
        "complete four-field condition",
        "at most 500 characters",
        "host-provided success",
        "every behavior-changing Constraint",
        "skip `ProposeGoal`",
        "not the compact proposal",
        "one copyable `/goal <condition>` command",
        "`/goal clear`",
        "without a separate replacement confirmation",
        "https://github.com/openai/codex/blob/main/codex-rs/ext/goal/src/spec.rs",
        "https://github.com/openai/codex/blob/main/codex-rs/ext/goal/src/tool.rs",
        "https://unpkg.com/@anthropic-ai/claude-code@2.1.227/sdk-tools.d.ts",
        "an attempted call, displayed prose, pending confirmation, or manual command is not activation evidence",
    ):
        require(gate, required)

    if "truncate" in gate.lower():
        raise AssertionError("proposal overflow must fall back, never truncate")

    require(mechanisms, 'id: "goal-create.session-activation"')
    require(mechanisms, "test_session_activation_rules_are_one_registered_gate")


def expect_rejected(skill: str, mechanisms: str, mutation: str) -> None:
    try:
        validate(skill, mechanisms)
    except (AssertionError, ValueError):
        return
    raise AssertionError(f"adversarial mutation escaped detection: {mutation}")


def replace_once(text: str, pattern: str, replacement: str) -> str:
    mutated, count = re.subn(pattern, replacement, text, count=1)
    if count != 1:
        raise AssertionError(f"mutation pattern matched {count} times: {pattern}")
    return mutated


def main() -> None:
    skill = SKILL.read_text(encoding="utf-8")
    mechanisms = MECHANISMS.read_text(encoding="utf-8")
    validate(skill, mechanisms)

    mutations = {
        "500-character bound removed": replace_once(
            skill, r"at\s+most\s+500\s+characters", "at most several characters"
        ),
        "Codex spec schema path removed": skill.replace(
            "codex-rs/ext/goal/src/spec.rs", "codex-rs/ext/goal/src/schema.rs", 1
        ),
        "Codex implementation path removed": skill.replace(
            "codex-rs/ext/goal/src/tool.rs", "codex-rs/ext/goal/src/runtime.rs", 1
        ),
        "Anthropic schema path removed": skill.replace(
            "@2.1.227/sdk-tools.d.ts", "@2.1.227/other.d.ts", 1
        ),
        "attempted call treated as activation evidence": skill.replace(
            "is not activation evidence", "is activation evidence", 1
        ),
    }
    for name, mutated_skill in mutations.items():
        expect_rejected(mutated_skill, mechanisms, name)


if __name__ == "__main__":
    main()
