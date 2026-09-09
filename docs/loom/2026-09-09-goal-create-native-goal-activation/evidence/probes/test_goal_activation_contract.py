#!/usr/bin/env python3
"""Adversarial, stdlib-only checks for the goal-create activation contract."""

from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
SKILL = REPO / "loom-workflow/skills/goal-create/SKILL.md"
MECHANISMS = REPO / "docs/loom/evidence/mechanisms.yaml"


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"missing required contract text: {needle}")


def main() -> None:
    skill = SKILL.read_text(encoding="utf-8")
    start = skill.index("<!-- gate: goal-create.session-activation -->")
    end = skill.index("<!-- /gate -->", start)
    gate = " ".join(skill[start:end].split())

    for required in (
        "complete four-field condition",
        "host-provided success",
        "every behavior-changing Constraint",
        "skip `ProposeGoal`",
        "not the compact proposal",
        "one copyable `/goal <condition>` command",
        "`/goal clear`",
        "without a separate replacement confirmation",
        "https://github.com/openai/codex/blob/",
        "https://unpkg.com/@anthropic-ai/claude-code@",
    ):
        require(gate, required)

    if "truncate" in gate.lower():
        raise AssertionError("proposal overflow must fall back, never truncate")
    if "attempted call is activation evidence" in gate.lower():
        raise AssertionError("an attempted call must not prove activation")

    mechanisms = MECHANISMS.read_text(encoding="utf-8")
    require(mechanisms, 'id: "goal-create.session-activation"')
    require(mechanisms, "test_session_activation_rules_are_one_registered_gate")


if __name__ == "__main__":
    main()
