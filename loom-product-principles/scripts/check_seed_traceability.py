"""Oracle parser for the Level-2 mechanical traceability gate (brief
§Level 2, docs/loom/specs/2026-07-10-principles-replay-loop.md).

This module's `parse_oracle` DEFINES the oracle format contract:

  - Flat `key: value` lines. Each of the three checker-scope keys —
    `named_anchors:`, `deferred_items:`, `negative:` — appears on its own
    single line: `<key>: <value>`.
  - A value is a `;`-separated list of exact-match tokens; each token is
    stripped of surrounding whitespace before being returned.
  - The empty sentinel `none in this seed` (optionally followed by
    trailing parenthetical commentary, e.g. "none in this seed (2-deferred
    trap lives in seed 2)") parses to an empty list `[]`. A key absent
    from the document also parses to `[]`.
  - A document carrying NONE of the three checker-scope keys raises
    `ValueError`, naming which keys are missing.
  - `stances:` and `out_of_jurisdiction_bait:` are deliberately ignored by
    this parser — they need semantic judgment and stay with LLM
    graders/humans (out of checker scope by design, brief §Level 2). Any
    other unrecognized key is likewise ignored.

Artifact checks and the CLI (`main`) are added in a later task; this
module currently exposes only the parser.
"""

from __future__ import annotations

import re

_KEYS = ("named_anchors", "deferred_items", "negative")
_EMPTY_SENTINEL = "none in this seed"


def parse_oracle(text: str) -> dict:
    """Parse an oracle document's three checker-scope keys.

    Returns a dict with all three keys always present:
    `{"named_anchors": [...], "deferred_items": [...], "negative": [...]}`.

    Raises `ValueError` if none of the three keys appear anywhere in
    `text`, naming which keys are missing.
    """
    raw_values = {}
    for key in _KEYS:
        match = re.search(rf"^{key}:[ \t]*(.*)$", text, re.MULTILINE)
        if match is not None:
            raw_values[key] = match.group(1).strip()

    if not raw_values:
        missing = ", ".join(f"{key}:" for key in _KEYS)
        raise ValueError(
            f"oracle document is missing all three checker-scope keys: {missing}"
        )

    return {key: _parse_value(raw_values.get(key, "")) for key in _KEYS}


def _parse_value(value: str) -> list:
    if not value or value.lower().startswith(_EMPTY_SENTINEL):
        return []
    return [token.strip() for token in value.split(";") if token.strip()]
