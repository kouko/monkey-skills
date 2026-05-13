#!/usr/bin/env python3
"""Deterministic keyword-based path classifier for legal-incident-response.

Reads an incident description + path-classifier-keywords.yml; returns
matched keywords per path. LLM (in protocols/classify-path.md) judges
confidence and selects primary path from this output.

Public API:
    classify(description: str, keywords_path: Path) -> ClassifyResult

ClassifyResult:
    matched_paths: list[str]      paths with at least 1 matched keyword
    signals: dict[str, list[str]] per-path list of matched keywords
"""
# NOTE: do NOT add `from __future__ import annotations` — see SP3a
# load_profile.py / grade_draft.py for the importlib+@dataclass trap.

from dataclasses import dataclass, field
from pathlib import Path

import yaml

PATH_TYPES = ("pii-breach", "authority-letter", "contract-breach")


@dataclass
class ClassifyResult:
    matched_paths: list[str] = field(default_factory=list)
    signals: dict[str, list[str]] = field(default_factory=dict)


def classify(description: str, keywords_path: Path) -> ClassifyResult:
    """Match description against per-path keyword bank.

    Args:
      description: free-text incident description from user.
      keywords_path: path to path-classifier-keywords.yml.

    Returns:
      ClassifyResult; empty matched_paths if no keyword hit.
    """
    if not keywords_path.is_file():
        return ClassifyResult()

    data = yaml.safe_load(keywords_path.read_text(encoding="utf-8")) or {}
    desc_lower = description.lower()

    signals: dict[str, list[str]] = {p: [] for p in PATH_TYPES}
    for path_type in PATH_TYPES:
        path_def = data.get(path_type, {}) or {}
        keywords = path_def.get("high_confidence_keywords", []) or []
        for kw in keywords:
            if kw.lower() in desc_lower:
                signals[path_type].append(kw)

    matched_paths = [p for p in PATH_TYPES if signals[p]]
    return ClassifyResult(matched_paths=matched_paths, signals=signals)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) != 3:
        print("usage: classify_path.py <description> <path/to/path-classifier-keywords.yml>", file=sys.stderr)
        sys.exit(2)

    result = classify(sys.argv[1], Path(sys.argv[2]))
    print(json.dumps({"matched_paths": result.matched_paths, "signals": result.signals}, ensure_ascii=False, indent=2))
    sys.exit(0)
