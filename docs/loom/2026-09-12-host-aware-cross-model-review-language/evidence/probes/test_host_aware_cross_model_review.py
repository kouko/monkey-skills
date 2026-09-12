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


def reject_forbidden(text: str, phrases: tuple[str, ...], source: str) -> None:
    prose = " ".join(text.split()).lower()
    for phrase in phrases:
        if phrase.lower() in prose:
            raise AssertionError(f"{source}: retains {phrase!r}")


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
            prose = " ".join(text.split())
            require(prose, "On Codex, probe `claude` then `gemini`", name)
            require(prose, "On Claude Code, probe `codex` then `gemini`", name)
            require(prose, "Never offer the current host family", name)
            require(prose, "`AskUserQuestion`", name)
            require(prose, "`request_user_input`", name)
            require(
                prose,
                "render both choices in the user's current conversation language",
                name,
            )
            require(prose, "decline this change", name)
            require(prose, "https://code.claude.com/docs/en/tools-reference", name)
            require(
                prose,
                "https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/request_user_input.rs",
                name,
            )
            require(prose, "blocking plain-language Markdown question", name)
            require(prose, "no runnable different-model-family CLI", name)
            require(prose, "continue without asking", name)

        table = (
            "```markdown\n\n\n"
            "| <heading> |\n|---|\n| <description> |\n\n\n```"
        )
        code_prose = " ".join(code.split())
        require(code, table, "loom-code-reference.md")
        require(
            code_prose,
            "one heading and one descriptive cell",
            "loom-code-reference.md",
        )
        require(code_prose, "continue without waiting", "loom-code-reference.md")

        forbidden = ("第二位讀者", "second reader", "use Codex as", "這次不使用")
        reject_forbidden(combined, forbidden, "packaged runtime")

        try:
            reject_forbidden("wrapped second\nreader", forbidden, "wrapped fixture")
        except AssertionError:
            pass
        else:
            raise AssertionError("wrapped forbidden phrase was not rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
