"""Schemas, constants, and dataclasses for the deep-research pipeline.

Port of the CC built-in deep-research v2.1.159 schema definitions.
All dict shapes are byte-faithful to the decompiled-source reference.

CLI: `python schemas.py {scope|search|extract|verdict|report}` prints the
named JSON Schema to stdout. Unknown name → stderr + exit 1.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VOTES_PER_CLAIM: int = 3
REFUTATIONS_REQUIRED: int = 2
MAX_FETCH: int = 15
MAX_VERIFY_CLAIMS: int = 25

# ---------------------------------------------------------------------------
# JSON Schemas (verbatim port from decompiled-source §Schemas)
# ---------------------------------------------------------------------------

SCOPE_SCHEMA = {
    "type": "object",
    "required": ["question", "angles", "summary"],
    "properties": {
        "question": {"type": "string"},
        "summary": {"type": "string"},
        "angles": {
            "type": "array",
            "minItems": 3,
            "maxItems": 6,
            "items": {
                "type": "object",
                "required": ["label", "query"],
                "properties": {
                    "label": {"type": "string"},
                    "query": {"type": "string"},
                    "rationale": {"type": "string"},
                },
            },
        },
    },
}

SEARCH_SCHEMA = {
    "type": "object",
    "required": ["results"],
    "properties": {
        "results": {
            "type": "array",
            "maxItems": 6,
            "items": {
                "type": "object",
                "required": ["url", "title", "relevance"],
                "properties": {
                    "url": {"type": "string"},
                    "title": {"type": "string"},
                    "snippet": {"type": "string"},
                    "relevance": {"enum": ["high", "medium", "low"]},
                },
            },
        },
    },
}

EXTRACT_SCHEMA = {
    "type": "object",
    "required": ["claims", "sourceQuality"],
    "properties": {
        "sourceQuality": {"enum": ["primary", "secondary", "blog", "forum", "unreliable"]},
        "publishDate": {"type": "string"},
        "claims": {
            "type": "array",
            "maxItems": 5,
            "items": {
                "type": "object",
                "required": ["claim", "quote", "importance"],
                "properties": {
                    "claim": {"type": "string"},
                    "quote": {"type": "string"},
                    "importance": {"enum": ["central", "supporting", "tangential"]},
                },
            },
        },
    },
}

VERDICT_SCHEMA = {
    "type": "object",
    "required": ["refuted", "evidence", "confidence"],
    "properties": {
        "refuted": {"type": "boolean"},
        "evidence": {"type": "string"},
        "confidence": {"enum": ["high", "medium", "low"]},
        "counterSource": {"type": "string"},
    },
}

REPORT_SCHEMA = {
    "type": "object",
    "required": ["summary", "findings", "caveats"],
    "properties": {
        "summary": {"type": "string"},
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["claim", "confidence", "sources", "evidence"],
                "properties": {
                    "claim": {"type": "string"},
                    "confidence": {"enum": ["high", "medium", "low"]},
                    "sources": {"type": "array", "items": {"type": "string"}},
                    "evidence": {"type": "string"},
                    "vote": {"type": "string"},
                },
            },
        },
        "caveats": {"type": "string"},
        "openQuestions": {"type": "array", "items": {"type": "string"}},
    },
}

# Lookup table for the CLI — name → schema dict.
SCHEMAS_BY_NAME = {
    "scope": SCOPE_SCHEMA,
    "search": SEARCH_SCHEMA,
    "extract": EXTRACT_SCHEMA,
    "verdict": VERDICT_SCHEMA,
    "report": REPORT_SCHEMA,
}

# ---------------------------------------------------------------------------
# Typed dataclasses — mirror the schema fields with Python-idiomatic names
# ---------------------------------------------------------------------------


@dataclass
class Angle:
    label: str
    query: str
    rationale: Optional[str] = None


@dataclass
class SearchResult:
    url: str
    title: str
    relevance: str  # "high" | "medium" | "low"
    snippet: Optional[str] = None


@dataclass
class ExtractedClaim:
    claim: str
    quote: str
    importance: str  # "central" | "supporting" | "tangential"
    source_url: str = ""
    source_quality: str = "unreliable"
    publish_date: Optional[str] = None


@dataclass
class Verdict:
    refuted: bool
    evidence: str
    confidence: str  # "high" | "medium" | "low"
    counter_source: Optional[str] = None


@dataclass
class Finding:
    claim: str
    confidence: str  # "high" | "medium" | "low"
    sources: List[str] = field(default_factory=list)
    evidence: str = ""
    vote: Optional[str] = None


@dataclass
class Report:
    summary: str
    findings: List[Finding] = field(default_factory=list)
    caveats: str = ""
    open_questions: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    import json
    import sys

    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1 or args[0] not in SCHEMAS_BY_NAME:
        valid = "|".join(SCHEMAS_BY_NAME)
        name = args[0] if args else "(none)"
        print(f"unknown schema name {name!r}; expected one of {{{valid}}}",
              file=sys.stderr)
        return 1
    print(json.dumps(SCHEMAS_BY_NAME[args[0]], indent=2))
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
