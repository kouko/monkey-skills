"""Per-role model routing for translation-toolkit (Phase B of v0.3.0 Tier 2).

Plan reference: ``docs/superpowers/plans/2026-05-07-translation-toolkit-v0.3.0-tier2.md``
§"Decision D — Cheap-model split via ``model: str | dict``".

The intake-spec ``model`` field accepts two forms:

- **Single-string form (v0.2.0 baseline)** — every behavioral role uses the same
  model (e.g. ``model: "claude-opus-4-7"``).
- **Per-role override form (v0.3.0+)** — a dict whose required ``default`` key
  carries the fallback model and whose optional per-role keys override
  ``default`` for that role only::

      model:
        default: claude-opus-4-7
        extractor: claude-haiku-4-5         # cheap whole-book pre-pass
        back_translator: claude-haiku-4-5   # cheap S1 round-trip

Recognized role keys (the public ``KNOWN_ROLES`` constant): ``writer``,
``critic``, ``reviser``, ``back_translator``, ``judge``, ``extractor``.
``default`` is mandatory metadata, NOT a behavioral role override; any other
unknown key emits a :class:`UserWarning` for forward-compat with future role
splits but is otherwise accepted (callers should treat the warning as advisory,
not fatal).

Routing rationale: roles are behavioral — the same skill body runs regardless
of which model executes it; only token cost and latency change. Per-role
overrides let cheap models cover I/O-bound or low-judgement-required roles
(``extractor`` / ``back_translator``) while reserving the standard model for
high-judgement roles (``writer`` / ``critic`` / ``reviser`` / ``judge``).

Public API:

- :data:`KNOWN_ROLES` — tuple of accepted per-role override keys.
- :class:`ModelDict` — :class:`typing.TypedDict` for static-typing convenience.
- :func:`validate_model_field` — raise :class:`ValueError` if invalid.
- :func:`resolve_model_for_role` — return the model string for one role.

This module lives at plugin-level ``translation-toolkit/scripts/lib/`` and
is independent of any skill folder.
"""
from __future__ import annotations

import warnings
from typing import TypedDict

__all__ = [
    "KNOWN_ROLES",
    "ModelDict",
    "validate_model_field",
    "resolve_model_for_role",
]


# Recognized per-role override keys. ``default`` is mandatory metadata and is
# intentionally NOT in this tuple — it is not a behavioral role.
KNOWN_ROLES: tuple[str, ...] = (
    "writer",
    "critic",
    "reviser",
    "back_translator",
    "judge",
    "extractor",
)


class ModelDict(TypedDict, total=False):
    """Static-typing shape for the per-role-override form of ``model``.

    Documentation-only: :func:`validate_model_field` accepts plain
    ``dict[str, str]`` at runtime. ``default`` is required; the per-role keys
    are optional overrides.
    """

    default: str
    writer: str
    critic: str
    reviser: str
    back_translator: str
    judge: str
    extractor: str


def validate_model_field(model: str | dict[str, str]) -> None:
    """Validate the intake-spec ``model`` field; mutate nothing; return None.

    Acceptance rules:

    - **str form**: any non-empty string is accepted. Empty string is rejected.
    - **dict form**: must contain a ``default`` key whose value is a non-empty
      string. Any per-role key (in :data:`KNOWN_ROLES`) must also be a
      non-empty string. Unknown keys (neither ``default`` nor in
      :data:`KNOWN_ROLES`) emit a :class:`UserWarning` for forward-compat but
      do not raise.

    Raises
    ------
    ValueError
        If the type is wrong, an empty string is supplied, or the dict form
        is missing ``default`` / contains a non-string / empty-string value.
    """
    if isinstance(model, str):
        if not model:
            raise ValueError("model field must be a non-empty string")
        return

    if isinstance(model, dict):
        if "default" not in model:
            raise ValueError(
                "model dict must contain a 'default' key (required fallback)"
            )
        for key, value in model.items():
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"model dict value for {key!r} must be a non-empty string"
                )
            if key != "default" and key not in KNOWN_ROLES:
                warnings.warn(
                    f"unknown role key {key!r} in model dict; "
                    f"recognized roles: {KNOWN_ROLES}",
                    UserWarning,
                    stacklevel=2,
                )
        return

    raise ValueError(
        f"model field must be a string or dict, got {type(model).__name__}"
    )


def resolve_model_for_role(model: str | dict[str, str], role: str) -> str:
    """Return the model string to use for ``role``.

    - **str form**: returned as-is regardless of ``role``.
    - **dict form**: returns ``model[role]`` if present, otherwise
      ``model['default']``.

    Callers should run :func:`validate_model_field` first; this function does
    not re-validate. ``KeyError`` is raised if the dict form is missing
    ``default`` and ``role`` is not present.
    """
    if isinstance(model, str):
        return model
    return model.get(role, model["default"])
