#!/usr/bin/env python3
"""Verify each plugin.json description does not reference skill slugs that no
longer exist under the plugin's skills/ folder.

Background: existing CI script `check-marketplace-description-sync.py` verifies
plugin.json description == marketplace.json description verbatim — it does NOT
verify that mentioned skill names correspond to actual folders. After several
absorptions (v0.4 absorbed `loop-and-link-primitives` into `cld-craft`; v0.6
absorbed `innovaction-martian-test` into `strategy-lever-and-cascade`) the
description carried stale slug references. This script fills that gap.

Heuristic (conservative — wants zero false positives on legitimate prose):
  Tier-A (fail): backtick-quoted token that looks like a skill slug AND no
                 matching folder exists.
  Tier-B (fail): bare kebab-case token followed by a role parenthetical like
                 `(router)`, `(skill)`, `(skXX)`, `(bootstrap...)`,
                 `(review/redline/nda mode)` AND no matching folder exists.

A token "looks like a skill slug" iff:
  - matches /^[a-z][a-z0-9]*(-[a-z0-9]+){1,}$/ (kebab-case, ≥1 hyphen);
  - has 2+ hyphens OR carries a role parenthetical (Tier-B);
  - is NOT in the stop-list of well-known generic kebab terms (e.g.
    `stock-flow`, `limits-to-growth`, `lead-measure`).

Edge cases handled:
  - Plugin with no skills/ folder (e.g. dev-workflow has skills/ — but some
    other plugins may not): skipped gracefully.
  - plugin.json with no `description` field: skipped.
  - Cross-plugin skill references in `plugin:skill` form (e.g.
    `tsundoku:book-distill`): not flagged — the skill exists in the named
    plugin, not in this plugin.
  - Backticked non-slug method notation (`Mermaid`, `S/O`, `R/B`,
    `uv run`): filtered by the kebab-shape requirement above.

Exit codes:
  0  all plugin descriptions coherent with their skills/ folders
  1  one or more stale skill references detected
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Generic kebab terms that frequently appear in prose but are never skill
# slugs. Keeps Tier-A from flagging them when accidentally backticked
# (rare but possible) and lets us reuse the stop-list for future expansion.
STOP_LIST: set[str] = {
    # Domain concepts (systems thinking)
    "stock-flow",
    "limits-to-growth",
    "feedback-loop",
    "causal-loop-diagram",
    "lead-measure",
    "lead-measures",
    "wig-cascade",
    "wig-session",
    "targets-not-plans",
    # Prose / formatting words
    "fully-annotated",
    "text-only",
    "facilitation-vocabulary-only",
    "native-caption",
    "symptom-phrase",
    "scope-flex",
    "single-layer-audit",
    "cross-layer-aggregator",
    "artifact-audit",
    "consultant-mode",
    "dual-mode",
    "coach-mode",
    "audit-mode",
    "primary-wig",
    "commitment-vs-compliance",
    "scope-symmetry",
    "lead-measure-facilitation",
    "scoreboard-design",
    "xps-evaluation",
    "personal-coaching",
    "team-leader",
    "team-member",
    "multi-file",
    "book-distill",  # cross-plugin reference, not a slug in any non-tsundoku plugin
    "accountability-partner",
    "goal-setting",
    "wildly-important-goal",
    "lead-measures",
    "cadence-of-accountability",
    "1-router",
    "1m-context",
}

# Role parentheticals that strongly signal "this kebab token is a skill slug
# being introduced". Used by Tier-B.
ROLE_PARENS_PATTERN = re.compile(
    r"\(\s*("
    r"router"
    r"|skill"
    r"|sk\d+"
    r"|bootstrap[^)]*"
    r"|review[^)]*"
    r"|skeleton[^)]*"
    r"|orchestrator"
    r")\s*\)",
    re.IGNORECASE,
)

# Token shape — a kebab-case identifier: alphanumeric start (some skills
# legitimately start with a digit, e.g. `4dx-audit`), lowercase alnum body,
# 1+ hyphens. Length unbounded; we filter further downstream.
KEBAB_TOKEN_PATTERN = re.compile(r"[a-z0-9][a-z0-9]*(?:-[a-z0-9]+)+")

# Backtick-quoted span — captures whatever sits between matched backticks.
BACKTICK_SPAN_PATTERN = re.compile(r"`([^`]+)`")


def looks_like_skill_slug(token: str, min_hyphens: int) -> bool:
    """Heuristic test: does this token look like it could be a skill folder name?"""
    if token in STOP_LIST:
        return False
    if token.count("-") < min_hyphens:
        return False
    if not KEBAB_TOKEN_PATTERN.fullmatch(token):
        return False
    # Skip cross-plugin reference form `plugin:skill` (the `:` is filtered
    # out by tokenization, but defensive).
    if ":" in token:
        return False
    # Reject pure-numeric kebab strings like "1-2" or "v1-0".
    if not any(c.isalpha() for c in token):
        return False
    return True


def find_backtick_skill_tokens(description: str) -> list[str]:
    """Tier-A: backtick-quoted kebab tokens with ≥1 hyphen, excluding
    cross-plugin references like `plugin:skill`."""
    out: list[str] = []
    for span in BACKTICK_SPAN_PATTERN.findall(description):
        # Skip cross-plugin reference form `plugin-name:skill-name`. The
        # referenced skill lives in another plugin; coherence is the
        # OTHER plugin's responsibility (and its own coherence check will
        # catch a stale ref there).
        if ":" in span:
            continue
        # The backtick span may contain just the slug (e.g. `cld-craft`) or a
        # phrase (e.g. `uv run`). Extract kebab tokens inside.
        for token in KEBAB_TOKEN_PATTERN.findall(span):
            if looks_like_skill_slug(token, min_hyphens=1):
                out.append(token)
    return out


def find_paren_role_skill_tokens(description: str) -> list[str]:
    """Tier-B: bare kebab tokens immediately followed by a role parenthetical.

    Example matches:
        using-legal-toolkit (router)
        legal-playbook-author (bootstrap/extend/revise)
    """
    out: list[str] = []
    # Walk every role-parenthetical hit, then look backwards for the kebab
    # token that introduces it.
    for match in ROLE_PARENS_PATTERN.finditer(description):
        # Take a window of 80 chars before the paren and find the last kebab
        # token that abuts the paren (allowing whitespace).
        window_start = max(0, match.start() - 80)
        window = description[window_start : match.start()]
        kebab_tokens = list(KEBAB_TOKEN_PATTERN.finditer(window))
        if not kebab_tokens:
            continue
        last = kebab_tokens[-1]
        # The kebab token must be at the very end of the window (allowing
        # only whitespace between it and the paren), otherwise the paren
        # belongs to something else.
        trailing = window[last.end():]
        if trailing.strip() != "":
            continue
        token = last.group(0)
        if looks_like_skill_slug(token, min_hyphens=1):
            out.append(token)
    return out


def check_plugin(plugin_dir: Path) -> tuple[int, list[str]]:
    """Returns (errors_added, error_messages) for one plugin."""
    plugin_json = plugin_dir / ".claude-plugin" / "plugin.json"
    if not plugin_json.exists():
        return 0, []

    try:
        data = json.loads(plugin_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return 1, [f"{plugin_json.relative_to(ROOT)}: invalid JSON — {exc}"]

    description = data.get("description")
    if not description:
        return 0, []

    skills_dir = plugin_dir / "skills"
    if not skills_dir.is_dir():
        # Plugins without skills/ (rare) cannot have stale skill refs.
        return 0, []

    actual_skills = {
        child.name for child in skills_dir.iterdir() if child.is_dir()
    }

    errors: list[str] = []

    # Tier-A — backtick-quoted slug-like tokens.
    for token in find_backtick_skill_tokens(description):
        if token not in actual_skills:
            errors.append(
                f"{plugin_json.relative_to(ROOT)}: backtick-quoted slug "
                f"`{token}` referenced in description, but no folder "
                f"`{plugin_dir.name}/skills/{token}/` exists"
            )

    # Tier-B — bare kebab token with role parenthetical.
    for token in find_paren_role_skill_tokens(description):
        if token not in actual_skills:
            errors.append(
                f"{plugin_json.relative_to(ROOT)}: '{token} (...)' "
                f"referenced in description with role-parenthetical, but no "
                f"folder `{plugin_dir.name}/skills/{token}/` exists"
            )

    return len(errors), errors


def main() -> int:
    # plugin.json lives at <plugin>/.claude-plugin/plugin.json, so the plugin
    # directory is two levels up.
    plugin_dirs = sorted(
        p.parent.parent for p in ROOT.glob("*/.claude-plugin/plugin.json")
    )

    total_errors = 0
    total_plugins = 0
    all_messages: list[str] = []

    for plugin_dir in plugin_dirs:
        if not (plugin_dir / "skills").is_dir():
            continue
        total_plugins += 1
        n, msgs = check_plugin(plugin_dir)
        total_errors += n
        all_messages.extend(msgs)

    if total_errors:
        print(
            f"FAIL: {total_errors} stale skill reference(s) across "
            f"{total_plugins} plugin(s):",
            file=sys.stderr,
        )
        for msg in all_messages:
            print(f"  {msg}", file=sys.stderr)
        print(
            "\nFix: either restore the skill folder, or remove the stale "
            "reference from the plugin.json description (mirror the change "
            "to marketplace.json in the same commit).",
            file=sys.stderr,
        )
        return 1

    print(
        f"OK: {total_plugins} plugin description(s) coherent with skills/ folders"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
