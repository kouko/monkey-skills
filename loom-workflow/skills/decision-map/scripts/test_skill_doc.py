"""Doc-drift test: every script command SKILL.md cites must match the
§Command surface SSOT in references/map-format.md.

map-format.md quotes only one full invocation literally — the
`map_store.py validate <target> --repo-root <path>` example — so a
citation of that script is checked by exact (whitespace-normalized)
substring match against map-format.md. The other four scripts are
never spelled out as full invocations in map-format.md; instead it
pins their shape in prose (§Command surface's "canonical arg shape"
paragraph): a bare positional `target` plus `--repo-root <path>`,
with NO leading verb — only map_store.py carries a verb (`validate`).
So a citation of those four is checked structurally against that
pinned shape. Either check failing means SKILL.md drifted from the
SSOT; the assertion names the offending quote.
"""

import re
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_MD = SKILL_DIR / "SKILL.md"
MAP_FORMAT_MD = SKILL_DIR / "references" / "map-format.md"

SCRIPT_NAMES = (
    "map_init.py",
    "map_store.py",
    "check_map_links.py",
    "check_map_fog.py",
    "map_parts.py",
)

INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")

# script[.py] [verb] <target> --repo-root <path>
COMMAND_SHAPE_RE = re.compile(
    r"^(?P<script>[a-z_]+\.py)"
    r"(?:\s+(?P<verb>[a-z_]+))?"
    r"\s+(?P<target><[^>]+>)"
    r"\s+--repo-root\s+(?P<repo><[^>]+>)$"
)


def _normalize(command: str) -> str:
    """Collapse whitespace so line-wrapped or re-spaced quotes still match."""
    return " ".join(command.split())


def _script_commands(text: str) -> list[str]:
    """Every inline-code span that opens with one of the five script names."""
    commands = []
    for span in INLINE_CODE_RE.findall(text):
        stripped = span.strip()
        if stripped.startswith(SCRIPT_NAMES):
            commands.append(stripped)
    return commands


def test_skill_commands_match_command_surface():
    assert SKILL_MD.is_file(), f"missing {SKILL_MD}"
    assert MAP_FORMAT_MD.is_file(), f"missing {MAP_FORMAT_MD}"

    skill_text = SKILL_MD.read_text(encoding="utf-8")
    surface_text = MAP_FORMAT_MD.read_text(encoding="utf-8")
    normalized_surface = _normalize(surface_text)

    skill_commands = _script_commands(skill_text)
    assert skill_commands, (
        "SKILL.md cites no script commands from the pinned command surface "
        f"({', '.join(SCRIPT_NAMES)}) — expected at least one"
    )

    offenders = []
    for quote in skill_commands:
        normalized = _normalize(quote)
        match = COMMAND_SHAPE_RE.match(normalized)
        if not match:
            offenders.append((quote, "does not match canonical arg shape "
                              "'<script>.py [verb] <target> --repo-root <path>'"))
            continue
        script = match.group("script")
        verb = match.group("verb")
        if script == "map_store.py":
            # The one script with a literal full-invocation quote in the
            # SSOT — require exact (whitespace-normalized) substring match.
            if verb != "validate":
                offenders.append((quote, "map_store.py must carry the "
                                  "'validate' verb — no other verb is pinned"))
            elif normalized not in normalized_surface:
                offenders.append((quote, "not found verbatim in "
                                  "references/map-format.md §Command surface"))
        else:
            # The other four take the bare positional shape — no verb.
            if verb is not None:
                offenders.append((quote, f"{script} takes no verb "
                                  f"(§Command surface pins a bare positional "
                                  f"shape) — found verb {verb!r}"))

    assert not offenders, "SKILL.md command citation(s) drifted from " \
        "references/map-format.md §Command surface:\n" + "\n".join(
            f"  {quote!r}: {reason}" for quote, reason in offenders
        )
