#!/usr/bin/env python3
"""Adversarial cold-read checks for packaged cross-model review prompts."""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
RUNTIME_FILES = {
    "loom-code-reference.md": REPO
    / "loom-code/skills/write-plan/references/second-vendor-ask-and-docs-lint.md",
    "loom-code-skill.md": REPO / "loom-code/skills/write-plan/SKILL.md",
    "loom-design-reference.md": REPO
    / "loom-design/skills/capture-intent/references/second-vendor.md",
    "loom-design-skill.md": REPO / "loom-design/skills/capture-intent/SKILL.md",
}


def require(text: str, fragment: str, source: str) -> None:
    if fragment not in text:
        raise AssertionError(f"{source}: missing {fragment!r}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="loom-cross-model-") as temp:
        root = Path(temp)
        installed = root / "unrelated-install-root"
        hostile = root / "hostile-cwd"
        installed.mkdir()
        hostile.mkdir()
        (hostile / "second-vendor-ask-and-docs-lint.md").write_text(
            "use the current host as reviewer\n", encoding="utf-8"
        )

        copies: dict[str, str] = {}
        for name, source in RUNTIME_FILES.items():
            target = installed / name
            shutil.copyfile(source, target)
            copies[name] = target.read_text(encoding="utf-8")

        code = copies["loom-code-reference.md"]
        design = copies["loom-design-reference.md"]
        combined = "\n".join(copies.values())

        for name, text in (
            ("loom-code-reference.md", code),
            ("loom-design-reference.md", design),
        ):
            require(text, "On Codex, probe `claude` then `gemini`", name)
            require(text, "On Claude Code, probe `codex` then `gemini`", name)
            require(text, "Never offer the current host family", name)
            require(text, "`AskUserQuestion`", name)
            require(text, "`request_user_input`", name)
            require(
                text,
                "render both choices in the user's current conversation language",
                name,
            )
            require(text, "decline this change", name)
            require(text, "https://code.claude.com/docs/en/tools-reference", name)
            require(
                text,
                "https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/request_user_input.rs",
                name,
            )
            require(text, "blocking plain-language Markdown question", name)
            require(text, "no runnable different-model-family CLI", name)
            require(text, "continue without asking", name)

        table = (
            "```markdown\n\n\n"
            "| <heading> |\n|---|\n| <description> |\n\n\n```"
        )
        require(code, table, "loom-code-reference.md")
        require(code, "one heading and one descriptive cell", "loom-code-reference.md")
        require(code, "continue without waiting", "loom-code-reference.md")

        forbidden = ("第二位讀者", "second reader", "use Codex as", "這次不使用")
        lowered = combined.lower()
        for phrase in forbidden:
            if phrase.lower() in lowered:
                raise AssertionError(f"packaged runtime retains {phrase!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
