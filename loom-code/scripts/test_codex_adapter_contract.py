"""Structural contract for Codex's immutable review-context adapter.

``codex-tools.md`` is the host adapter that an orchestrator reads rather than
an executable module.  These assertions therefore pin its load-bearing
instructions: the installed plugin, never the consumer checkout, resolves
the common context script; downstream dispatches forward that JSON packet
unchanged; and a docs fix starts a labelled fresh whole-artifact review rather
than pretending Codex has Claude Code's ``SendMessage`` continuation.
"""
from __future__ import annotations

import re
from pathlib import Path


CODEX_TOOLS = (
    Path(__file__).parents[1]
    / "skills"
    / "using-loom-code"
    / "references"
    / "codex-tools.md"
)


def _text() -> str:
    assert CODEX_TOOLS.is_file(), f"Codex adapter is absent at {CODEX_TOOLS}"
    return CODEX_TOOLS.read_text(encoding="utf-8")


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _window(raw: str, start_heading: str, end_heading: str) -> str:
    """Raw-text slice from `start_heading` up to (not including) `end_heading`."""
    start = raw.index(start_heading)
    end = raw.index(end_heading, start)
    return raw[start:end]


def _root_derivation_window() -> str:
    """The root-derivation half of the adapter section, before the post-fix flow."""
    return _normalise(
        _window(_text(), "## Immutable review-context adapter", "After a docs fix,")
    )


def _adapter_window() -> str:
    """The whole Immutable review-context adapter section."""
    return _normalise(
        _window(_text(), "## Immutable review-context adapter", "## Subagent dispatch")
    )


def test_codex_adapter_resolves_and_forwards_immutable_review_context() -> None:
    """Codex must use the installed plugin root and preserve its packet.

    "not the target repository" is narrowed to the adapter window: `verbatim`
    also names an unrelated hook-injection claim elsewhere in this file, so a
    whole-file match on the bare keyword would stay green even if this
    section's forwarding rule were deleted.
    """
    text = _normalise(_text())
    root_window = _root_derivation_window()
    adapter_window = _adapter_window()

    assert "## Immutable review-context adapter" in _text()
    assert "installed `loom-code` plugin root" in text
    assert "not the target repository" in root_window
    assert (
        "python3 <installed-plugin-root>/scripts/review_context.py "
        "--repo <target_repo>" in text
    )
    assert "verbatim" in adapter_window
    assert "must not derive, replace, or merge packet fields" in adapter_window


def test_codex_adapter_derives_installed_root_without_cache_guessing() -> None:
    """The loaded reference path, not a cache convention, identifies the plugin."""
    text = _normalise(_text())
    root_window = _root_derivation_window()

    assert "loaded `codex-tools.md` absolute path" in text
    assert "$(cd \"$(dirname \"$canonical_reference\")/../../..\" && pwd -P)" in text
    assert 'test -f "$plugin_root/scripts/review_context.py" || {' in _text()
    assert "exit 1" in _text()
    assert "refuse the review" in text
    assert "cache, marketplace, or consumer path" in root_window


def test_codex_adapter_rejects_an_untrusted_loaded_reference_path() -> None:
    """Root derivation must not fall back to the current directory."""
    source = _text()

    assert 'case "$loaded_reference_path" in' in source
    assert "/*) ;;" in source
    assert '[ ! -f "$loaded_reference_path" ]' in source
    assert 'basename "$loaded_reference_path"' in source
    assert '"codex-tools.md"' in source
    assert "before deriving `plugin_root`" in _normalise(source)
    assert "not use the current working directory as a fallback" in _normalise(source)


def test_codex_adapter_requires_canonical_expected_reference_layout() -> None:
    """A same-named foreign file must not select a foreign plugin root."""
    source = _text()

    assert "canonical_reference" in source
    assert "skills/using-loom-code/references/codex-tools.md" in source
    assert '"$canonical_reference" != "$expected_reference"' in source
    assert "must match the installed loom-code reference layout" in source
    assert '[ -L "$loaded_reference_path" ]' in source


def test_codex_adapter_requires_labelled_fresh_whole_artifact_docs_review() -> None:
    """A docs fix gets a new SHA review, never a fictional SendMessage reuse."""
    text = _normalise(_text())

    assert "labelled `fresh whole-artifact review (Codex)`" in text
    assert "post-fix SHA" in text
    assert "do not represent this as a `SendMessage` continuation" in text
    assert "echoes that fresh packet's `reviewed_sha`" in text
    assert "`CONFIRMED_RESOLVED` or `STILL_BLOCKING`" in text
    assert "must differ from the initial packet's `reviewed_sha`" in text


def test_codex_post_fix_maps_to_public_reviewer_agent_paths() -> None:
    """Codex dispatches role prompts from the loaded installed plugin root."""
    source = _text()
    plugin_root = CODEX_TOOLS.parents[3]

    assert "skills/subagent-driven-development/agents/*.md" not in source
    for role in (
        "implementer",
        "spec-reviewer",
        "code-quality-reviewer",
        "code-reviewer",
        "docs-reviewer",
    ):
        public_path = f"loom-code/agents/{role}.md"
        assert public_path in source
        assert (plugin_root / "agents" / f"{role}.md").is_file()
        assert f"$plugin_root/agents/{role}.md" in source

    assert "consumer checkout" in source
    assert "current working directory as a fallback" in source
    guard = re.search(
        r'for role_prompt in .*?; do\n(?P<body>.*?)\ndone', source, re.DOTALL
    )
    assert guard, "runtime reviewer-prompt loop is absent"
    assert 'test -f "$role_prompt" || {' in guard["body"]
    assert (
        'echo "reviewer prompt is absent from the installed plugin: '
        '$role_prompt" >&2'
    ) in guard["body"]
    assert "exit 1" in guard["body"]
