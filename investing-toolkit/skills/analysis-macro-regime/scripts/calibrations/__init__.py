"""calibrations/ — per-country YAML calibrations plumbed from
references/thresholds-{country}.md (per ADR-0004).

Each YAML carries country-specific thresholds: inflation_target,
policy_rate_neutrality, real_rate bands, NAIRU, structural overlays,
and provenance. classify_{country}.py modules read these via
`load_calibration(country)`.

Phase 1: not all calibration YAMLs land in the same PR. An empty
calibration is acceptable; classify_X decides how to handle missing fields.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

CALIBRATIONS_DIR = Path(__file__).parent
SUPPORTED_COUNTRIES = {"us", "jp", "tw", "kr", "cn"}


@dataclass
class CountryCalibration:
    country: str
    raw: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.raw.get(key, default)

    def has(self, key: str) -> bool:
        return key in self.raw


def load_calibration(country: str) -> CountryCalibration:
    """Load calibrations/{country}.yaml. Returns empty calibration if file
    missing (Phase 1 acceptable state during incremental rollout)."""
    if country not in SUPPORTED_COUNTRIES:
        raise ValueError(f"unsupported country: {country!r}")
    path = CALIBRATIONS_DIR / f"{country}.yaml"
    if not path.exists():
        return CountryCalibration(country=country, raw={})
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return CountryCalibration(country=country, raw=payload)
