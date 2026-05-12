"""Audit-trail JSON builder per spec schema.

Records the full provenance of one translation run for review and
reproducibility: intake decisions, glossary resolution per term,
chunk-level draft/reflect/improve outputs, gate verdicts,
untranslatability decisions, sources used, warnings.

Spec: ``scripts/canonical/audit-trail-spec.md``.

Usage::

    builder = AuditTrailBuilder()
    builder.set_intake(mode="faithful", register="neutral",
                       strategy="domestication",
                       source_locale="en-US", target_locale="ja-JP",
                       domain="ui",
                       intent="UI strings for Settings screen",
                       inferred={"mode": False, "register": True})
    builder.add_glossary_resolution(term="Cancel", tier="L2",
                                    source="pontoon", value="キャンセル",
                                    audit_path="direct")
    builder.add_chunk(index=0, draft="...", reflect={...}, improve="...")
    builder.add_gate_verdict("M1", "PASS")
    audit = builder.build()                   # dict per spec schema
    json_str = builder.to_json()              # ensure_ascii=False, indent=2

This module is independent of any skill folder (lives at plugin-level
``translation-toolkit/scripts/lib/``) and is therefore not subject to
the flat-skill-folder convention.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = "0.1.0"


class AuditTrailBuilder:
    """Mutable builder; collect events as they happen, call ``.build()`` at end.

    Top-level schema keys populated:

    - ``version``                — schema version string (``"0.1.0"``)
    - ``timestamp``              — ISO 8601 UTC at construction time
    - ``intake``                 — dict; populated by ``set_intake``
    - ``glossary_resolution``    — list of per-term lookup records
    - ``chunks``                 — list of per-chunk pipeline outputs
    - ``gate_verdicts``          — dict keyed by gate id (``M1``/``M2``/``S1``/``S2``/``I1``)
    - ``untranslatables``        — list of borrow/explain/approximate decisions
    - ``sources_used``           — dict ``{category: [source_id, ...]}`` (deduped)
    - ``warnings``               — list of free-form warning strings

    See ``scripts/canonical/audit-trail-spec.md`` for the full schema and
    a worked example.
    """

    def __init__(self) -> None:
        self.data: dict[str, Any] = {
            "version": SCHEMA_VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "intake": {},
            "glossary_resolution": [],
            "chunks": [],
            "gate_verdicts": {},
            "untranslatables": [],
            "sources_used": {},
            "warnings": [],
        }

    # ----------------------------------------------------------------- #
    # intake                                                             #
    # ----------------------------------------------------------------- #

    def set_intake(
        self,
        *,
        mode: str,
        register: str,
        strategy: str,
        source_locale: str,
        target_locale: str,
        domain: str,
        intent: str | None = None,
        inferred: dict[str, bool] | None = None,
    ) -> None:
        """Set the intake spec.

        ``inferred`` is a per-axis bool map (``True`` = auto-inferred,
        ``False`` = user-supplied) per Decision #6 in the design spec.
        """
        self.data["intake"] = {
            "mode": mode,
            "register": register,
            "strategy": strategy,
            "source_locale": source_locale,
            "target_locale": target_locale,
            "domain": domain,
            "intent": intent,
            "inferred": inferred or {},
        }

    def add_inferred_value(self, axis: str, value: Any) -> None:
        """Record what auto-inference *would* have chosen for a given axis.

        Useful in explicit mode when the user overrode an axis: the
        heuristic's choice is captured under
        ``intake.inferred_values: {axis: value}`` for retrospective
        analysis of where heuristics misfire.

        Calling ``set_intake`` first is recommended but not required —
        the sub-dict is created on first call either way.
        """
        intake = self.data.setdefault("intake", {})
        inferred_values = intake.setdefault("inferred_values", {})
        inferred_values[axis] = value

    # ----------------------------------------------------------------- #
    # glossary resolution                                                #
    # ----------------------------------------------------------------- #

    def add_glossary_resolution(
        self,
        *,
        term: str,
        tier: str,
        source: str,
        value: str,
        audit_path: str,
    ) -> None:
        """Record one glossary lookup result.

        - ``tier``: ``L1`` (project) / ``L2`` (bundled) / ``L3`` (web search)
          / ``L4`` (LLM fallback)
        - ``source``: provenance string (e.g. ``"pontoon"``,
          ``"<repo>/docs/i18n/glossary-ja.md"``, ``"wikipedia.org"``)
        - ``audit_path``: ``"direct"`` / ``"pivot.en-US (...)"`` /
          ``"web-search"`` / ``"llm-fallback"``
        """
        self.data["glossary_resolution"].append({
            "term": term,
            "tier": tier,
            "source": source,
            "value": value,
            "audit_path": audit_path,
        })

    # ----------------------------------------------------------------- #
    # chunks                                                             #
    # ----------------------------------------------------------------- #

    def add_chunk(
        self,
        *,
        index: int,
        draft: str,
        reflect: dict[str, Any],
        improve: str,
        source: str | None = None,
    ) -> None:
        """Record per-chunk pipeline outputs.

        ``reflect`` is a structured dict — 4D for non-creative modes
        (accuracy / fluency / style / terminology) or 5D for creative
        modes (adds effectiveness).

        ``source`` is the optional pre-translation chunk text (post- or
        pre-protect-pass form per the implementer's convention). When
        ``None`` the ``source`` key is omitted from the entry entirely
        so the JSON stays minimal for callers that don't need it.
        """
        chunk: dict[str, Any] = {
            "index": index,
            "draft": draft,
            "reflect": reflect,
            "improve": improve,
        }
        if source is not None:
            chunk["source"] = source
        self.data["chunks"].append(chunk)

    # ----------------------------------------------------------------- #
    # gate verdicts                                                      #
    # ----------------------------------------------------------------- #

    def add_gate_verdict(
        self,
        gate_id: str,
        verdict: str,
        diff: Any = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Record one gate's verdict.

        ``gate_id`` ∈ ``{"M1", "M2", "S1", "S2", "I1"}`` per
        ``verification-gates.md``.
        """
        self.data["gate_verdicts"][gate_id] = {
            "verdict": verdict,
            "diff": diff,
            "details": details,
        }

    # ----------------------------------------------------------------- #
    # untranslatables                                                    #
    # ----------------------------------------------------------------- #

    def add_untranslatable(
        self,
        *,
        source_phrase: str,
        decision: str,
        alternatives: list[Any],
        target_rendering: str | None = None,
    ) -> None:
        """Record an untranslatability flag.

        ``decision`` ∈ ``{"borrow", "explain", "approximate"}``.

        ``target_rendering`` (optional) is how the phrase was actually
        rendered in v2 (e.g., borrowed verbatim, paraphrased, given a
        footnote). When ``None`` the ``target_rendering`` key is omitted
        from the entry.
        """
        entry: dict[str, Any] = {
            "source_phrase": source_phrase,
            "decision": decision,
            "alternatives": alternatives,
        }
        if target_rendering is not None:
            entry["target_rendering"] = target_rendering
        self.data["untranslatables"].append(entry)

    # ----------------------------------------------------------------- #
    # warnings                                                           #
    # ----------------------------------------------------------------- #

    def add_warning(self, message: str) -> None:
        self.data["warnings"].append(message)

    # ----------------------------------------------------------------- #
    # sources used                                                       #
    # ----------------------------------------------------------------- #

    def add_source_used(self, category: str, source_id: str) -> None:
        """Record a source consumed (glossary / websearch / corpus / etc.).

        Deduplicates within a category list — calling twice with the same
        ``(category, source_id)`` is a no-op.
        """
        bucket = self.data["sources_used"].setdefault(category, [])
        if source_id not in bucket:
            bucket.append(source_id)

    # ----------------------------------------------------------------- #
    # serialization                                                      #
    # ----------------------------------------------------------------- #

    def build(self) -> dict[str, Any]:
        """Return the underlying dict (live reference, not a copy)."""
        return self.data

    def to_json(self) -> str:
        """Serialize to UTF-8 JSON string with non-ASCII characters preserved.

        Uses ``ensure_ascii=False`` so Japanese / Chinese / accented
        characters appear literally in the output (no ``\\uXXXX`` escapes),
        and ``indent=2`` for human-readable diffs.
        """
        return json.dumps(self.data, ensure_ascii=False, indent=2)
