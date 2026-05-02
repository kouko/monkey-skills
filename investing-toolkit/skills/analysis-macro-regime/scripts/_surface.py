#!/usr/bin/env python3
"""
_surface.py — Phase 1 convention-level uniformity envelope (per ADR-0004).

The 6 outer keys (country / framework_used / native_verdict /
indicators_used / data_quality / confidence / provenance) are convention.
The `native_verdict` interior is deliberately schema-free — each country
owns its shape. Phase 2 (deferred ADR-0005) may convert any inner field
to a comparable-surface contract later, informed by what each country
actually emits.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class CountryRegimeCard:
    """Per-country regime card produced by classify_{country} modules."""
    country: str
    framework_used: str
    native_verdict: dict[str, Any]
    indicators_used: list[str]
    data_quality: dict[str, Any]
    confidence: Literal["low", "medium", "high"]
    provenance: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "country": self.country,
            "framework_used": self.framework_used,
            "native_verdict": self.native_verdict,
            "indicators_used": list(self.indicators_used),
            "data_quality": dict(self.data_quality),
            "confidence": self.confidence,
            "provenance": dict(self.provenance),
        }


@dataclass
class Phase1Output:
    """Top-level regime_compose.py output schema for Phase 1."""
    schema_version: str = "2.0-phase1"
    by_country: dict[str, dict[str, Any]] = field(default_factory=dict)
    cross_country: None = None  # Phase 2 placeholder per ADR-0004
    _legacy: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "by_country": dict(self.by_country),
            "cross_country": self.cross_country,
            "_legacy": dict(self._legacy),
        }
