"""Internal helpers shared between :mod:`character_extractor` and
:mod:`world_glossary_extractor`.

Not part of the public API; do not import from outside the ``lib`` package.

Extracted (2026-05-07 Phase D review fix) to remove the cross-module
underscore-import contract — both extractors previously imported these
private names from each other, which works but creates an undocumented
maintenance coupling. Hosting them here makes the shared-internal status
explicit at the file level.

Contents
--------
- :func:`_check_stale_cache` — emit ``UserWarning`` when an existing artifact
  was stamped with a different ``book_manifest_hash`` than the fresh run.
- :func:`_extract_json_object` — best-effort JSON extraction from a model
  response (strips fenced code blocks and stray prose).
- :func:`_format_intake_spec_compact` — render intake spec as compact
  key/value lines for prompt injection.
"""
from __future__ import annotations

import json
import re
import warnings
from pathlib import Path


def _check_stale_cache(output_path: Path, fresh_hash: str) -> None:
    """Emit UserWarning if existing artifact's hash mismatches fresh hash."""
    if not output_path.exists():
        return
    try:
        existing = json.loads(output_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    stamped = existing.get("book_manifest_hash")
    if stamped and stamped != fresh_hash:
        warnings.warn(
            f"existing pre-pass artifact at {output_path} stamped with "
            f"book_manifest_hash={stamped!r} but the current book manifest "
            f"hashes to {fresh_hash!r}; the artifact is stale and will be "
            f"overwritten by this run. Caller should decide whether to "
            f"re-run the pre-pass.",
            UserWarning,
            stacklevel=3,
        )


def _extract_json_object(response: str) -> dict:
    r"""Best-effort JSON extraction from a model response.

    The extractor prompt asks for a JSON object directly; in practice models
    sometimes wrap the output in fenced code blocks or prose. We strip a
    leading ```json / ``` fence if present, then decode.

    Raises :class:`ValueError` (with the underlying decode error chained)
    when the response can't be parsed.
    """
    text = response.strip()
    # Strip optional fenced code block (```json ... ``` or ``` ... ```).
    fence_match = re.match(
        r"```(?:json)?\s*\n(.*?)\n```\s*$",
        text,
        re.DOTALL,
    )
    if fence_match:
        text = fence_match.group(1).strip()
    # If still wrapped in stray prose, find the outermost {...} block.
    if not text.startswith("{"):
        first = text.find("{")
        last = text.rfind("}")
        if first != -1 and last != -1 and last > first:
            text = text[first : last + 1]
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"failed to parse extractor response as JSON: {exc}"
        ) from exc


def _format_intake_spec_compact(intake_spec: dict) -> str:
    """Render intake spec as compact key/value lines (mirrors novel_prompts)."""
    if not intake_spec:
        return "(none)"
    keys = ("source_locale", "target_locale", "mode", "register", "domain")
    lines: list[str] = []
    for k in keys:
        if k in intake_spec:
            lines.append(f"- {k}: {intake_spec[k]}")
    for k, v in intake_spec.items():
        if k in keys:
            continue
        # Skip nested dicts (e.g. model dict) — they bloat the prompt and the
        # extractor doesn't need routing detail.
        if isinstance(v, (dict, list)):
            continue
        lines.append(f"- {k}: {v}")
    return "\n".join(lines) if lines else "(none)"
