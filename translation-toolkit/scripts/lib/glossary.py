"""Glossary parser + EN-pivot fallback lookup.

Runtime library used by translation-toolkit skills (translation-i18n,
translation-doc, translation-creative, translation-audit) to look up
canonical term translations.

Pair files live at ``scripts/canonical/glossary-{lang_a}--{lang_b}.md`` where
``lang_a < lang_b`` in BCP-47 alphabetical order (``en-US < ja-JP < zh-CN <
zh-TW``). Each file shares the structure:

    ---
    pair: [<lang_a>, <lang_b>]
    version: 0.1.0
    sources: [...]
    domains_supported: [...]
    ---

    # Glossary <lang_a> ↔ <lang_b>

    ## meta              ← optional, NOT a domain
    (typography rules)

    ## domain: general
    | <lang_a> | <lang_b> | source | notes |
    |---|---|---|---|
    | <term>  | <translation> | <src> | <notes> |

    ## domain: <other>
    ...

Five canonical files exist today:
    glossary-en-US--ja-JP.md
    glossary-en-US--zh-CN.md
    glossary-en-US--zh-TW.md
    glossary-ja-JP--zh-TW.md
    glossary-zh-CN--zh-TW.md

EN-pivot fallback: when a non-EN pair (e.g. ja-JP → zh-TW) misses the direct
file, the lookup hops through ``glossary-en-US--<S>.md`` then
``glossary-en-US--<T>.md`` to produce an audit-trail-bearing answer.

This module is independent of any skill folder (lives at plugin-level
``translation-toolkit/scripts/lib/``) and is therefore not subject to the
flat-skill-folder convention.
"""
from __future__ import annotations

import functools
import re
from collections import defaultdict
from pathlib import Path

# --------------------------------------------------------------------------- #
# Markdown structural patterns                                                #
# --------------------------------------------------------------------------- #

_DOMAIN_HDR = re.compile(r"^##\s+domain:\s+(\S+)\s*$")
_META_HDR = re.compile(r"^##\s+meta\s*$")
_SEP_ROW = re.compile(r"^\|\s*[-:|\s]+\|\s*$")
_FRONTMATTER_PAIR = re.compile(r"^pair:\s*\[\s*([^,\]]+?)\s*,\s*([^,\]]+?)\s*\]\s*$")


def _split_table_row(line: str):
    """Split a markdown table row into trimmed cells; return None if not a row."""
    line = line.rstrip("\n")
    if not line.startswith("|") or not line.endswith("|"):
        return None
    if _SEP_ROW.match(line):
        return None
    inner = line[1:-1]
    return [c.strip() for c in inner.split("|")]


def _parse_frontmatter_pair(lines):
    """Extract `pair: [lang_a, lang_b]` from YAML frontmatter.

    Returns (lang_a, lang_b). Raises ValueError if the file has no
    frontmatter block or no `pair:` line within it.
    """
    if not lines or lines[0].rstrip() != "---":
        raise ValueError(
            "malformed glossary file: missing opening '---' frontmatter delimiter"
        )
    closed = False
    for raw in lines[1:]:
        s = raw.rstrip()
        if s == "---":
            closed = True
            break
        m = _FRONTMATTER_PAIR.match(s)
        if m:
            return m.group(1).strip(), m.group(2).strip()
    if not closed:
        raise ValueError(
            "malformed glossary file: unclosed YAML frontmatter (no closing '---')"
        )
    raise ValueError(
        "malformed glossary file: frontmatter has no 'pair: [<lang_a>, <lang_b>]' line"
    )


# --------------------------------------------------------------------------- #
# Parser                                                                       #
# --------------------------------------------------------------------------- #


def parse_pair_file(md_path):
    """Parse a glossary pair file into a domain-keyed dict.

    Return shape (chosen for direct iteration during lookup):

        {
            "_meta": {"pair": [<lang_a>, <lang_b>]},
            "<domain>": [
                {
                    "lang_a": "<lang_a>",       # e.g. "en-US"
                    "lang_b": "<lang_b>",       # e.g. "ja-JP"
                    "lang_a_term": "Cancel",
                    "lang_b_term": "キャンセル",
                    "source": "pontoon",
                    "notes": "—",
                },
                ...
            ],
            ...
        }

    The ``_meta`` slot carries ``pair`` so the caller knows which column is
    ``lang_a`` vs ``lang_b`` (needed for direction-agnostic lookup). All other
    keys are domain names.

    A ``## meta`` section is recognised and ignored (NOT promoted to a domain).
    Domain matching downstream is exact: ``"tech.crypto"`` does NOT fall back
    to ``"tech.software"`` — each domain section is independent.

    Errors:
        - File not found: returns an empty dict (no entries, no _meta) is NOT
          desired here — callers should pre-check via ``path.exists()``. We
          raise FileNotFoundError to surface accidental misuse.
        - Malformed frontmatter (missing block, missing `pair:`): ValueError.
    """
    md_path = Path(md_path)
    if not md_path.exists():
        raise FileNotFoundError(str(md_path))

    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    lang_a, lang_b = _parse_frontmatter_pair(lines)

    result = {"_meta": {"pair": [lang_a, lang_b]}}
    entries_by_domain = defaultdict(list)

    current_domain = None
    in_meta = False
    header_cells = None

    for raw in lines:
        # Section transitions: any `## ...` heading resets table state.
        if raw.startswith("## "):
            if _META_HDR.match(raw):
                in_meta = True
                current_domain = None
                header_cells = None
                continue
            m = _DOMAIN_HDR.match(raw)
            if m:
                current_domain = m.group(1)
                in_meta = False
                header_cells = None
                continue
            # Some other `## ...` heading (e.g. unrelated) — leave both
            # tracking states cleared.
            current_domain = None
            in_meta = False
            header_cells = None
            continue

        if current_domain is None:
            # In frontmatter, title, meta, or between sections — skip.
            continue

        if _SEP_ROW.match(raw):
            continue

        cells = _split_table_row(raw)
        if cells is None:
            # Any non-table line ends the current table; require a new
            # header row before resuming data parsing.
            header_cells = None
            continue

        if header_cells is None:
            # First row in domain block names the columns.
            header_cells = cells
            continue

        row = dict(zip(header_cells, cells))
        a_term = row.get(lang_a, "").strip()
        b_term = row.get(lang_b, "").strip()
        if not a_term or not b_term:
            continue

        entries_by_domain[current_domain].append({
            "lang_a": lang_a,
            "lang_b": lang_b,
            "lang_a_term": a_term,
            "lang_b_term": b_term,
            "source": (row.get("source", "") or "").strip() or "—",
            "notes": (row.get("notes", "") or "").strip() or "—",
        })

    for domain, rows in entries_by_domain.items():
        result[domain] = rows

    return result


# --------------------------------------------------------------------------- #
# Cached parse-by-path                                                         #
# --------------------------------------------------------------------------- #


@functools.lru_cache(maxsize=64)
def _parse_cached(path_str):
    """LRU-cached wrapper over `parse_pair_file`. Keyed on resolved path string.

    Pair files are immutable at runtime (built offline by build-pair-*.py); the
    cache stays valid for the duration of the process. Cache size 64 covers all
    plausible (lang, lang) combinations many times over.
    """
    return parse_pair_file(Path(path_str))


# --------------------------------------------------------------------------- #
# Lookup                                                                       #
# --------------------------------------------------------------------------- #


def _pair_filename(lang_x, lang_y):
    """Return canonical filename for a pair, sorted alphabetically."""
    a, b = sorted([lang_x, lang_y])
    return f"glossary-{a}--{b}.md"


def _find_in_parsed(parsed, source_lang, term, domain=None):
    """Search parsed glossary for `term` in the source-language column.

    Returns (entry_dict, matched_domain) or (None, None) on miss.

    `entry_dict` is the raw entry from `parse_pair_file`. Caller is responsible
    for picking the correct target column.
    """
    pair_meta = parsed.get("_meta", {}).get("pair")
    if not pair_meta:
        return None, None
    if source_lang not in pair_meta:
        return None, None

    # Determine which column ('lang_a_term' / 'lang_b_term') the source term
    # lives in.
    src_col = (
        "lang_a_term" if source_lang == pair_meta[0] else "lang_b_term"
    )

    domains_to_search = (
        [domain] if domain is not None
        else [k for k in parsed.keys() if k != "_meta"]
    )

    for d in domains_to_search:
        for entry in parsed.get(d, []):
            if entry.get(src_col) == term:
                return entry, d
    return None, None


def _target_term_from_entry(entry, target_lang):
    """Pick the target-language term from a parsed entry."""
    if entry["lang_a"] == target_lang:
        return entry["lang_a_term"]
    if entry["lang_b"] == target_lang:
        return entry["lang_b_term"]
    return None


def _lookup_l1_5_prepass(prepass_artifacts, term):
    """L1.5 lookup against pre-pass artifacts (v0.3.0 Tier 2).

    Search order within ``prepass_artifacts``:

    1. ``characters[*]`` — match on ``canonical_name`` (exact) or any
       ``aliases[*].source`` (exact, paired-structure). On match return the
       corresponding target rendering (``canonical_target`` for canonical
       hits, ``alias.target`` for alias hits) when non-None; otherwise miss.
    2. ``world_glossary["places"|"organizations"|"world_terms"]`` — match on
       ``canonical_source``. On match return ``canonical_target`` when
       non-None; otherwise miss.
    3. ``cultural_references`` — NOT searched here; cultural references are
       phrase-level decisions (handled by the I1 untranslatability gate),
       not term-level lookups.

    Returns ``(result_dict, None)`` on hit (mirroring the
    ``(entry, matched_domain)`` shape used elsewhere) or ``None`` on miss.
    The returned dict has keys ``target_term``, ``source``, ``notes``,
    ``audit_path``.
    """
    if not prepass_artifacts:
        return None

    # 1. characters
    for entry in prepass_artifacts.get("characters", []) or []:
        canonical_target = entry.get("canonical_target")
        if (
            entry.get("canonical_name") == term
            and canonical_target
        ):
            return {
                "target_term": canonical_target,
                "source": "pre-pass.characters",
                "notes": entry.get("voice_notes", "") or "—",
                "audit_path": "L1.5.character",
            }
        # Whether canonical matched (with None target) or not, try aliases on
        # this entry — paired-structure aliases may resolve even when the
        # canonical target is still unresolved. Then fall through to the next
        # character entry; never `break` (an alias might match a later entry).
        for alias in entry.get("aliases", []) or []:
            if alias.get("source") == term:
                target = alias.get("target")
                if target:
                    return {
                        "target_term": target,
                        "source": "pre-pass.characters",
                        "notes": entry.get("voice_notes", "") or "—",
                        "audit_path": "L1.5.character",
                    }

    # 2. world_glossary places / organizations / world_terms
    world = prepass_artifacts.get("world_glossary") or {}
    for class_name in ("places", "organizations", "world_terms"):
        for entry in world.get(class_name, []) or []:
            if entry.get("canonical_source") == term:
                target = entry.get("canonical_target")
                if target:
                    return {
                        "target_term": target,
                        "source": f"pre-pass.world_glossary.{class_name}",
                        "notes": entry.get("notes", "") or "—",
                        "audit_path": f"L1.5.world_glossary.{class_name}",
                    }

    return None


def lookup(
    glossary_dir,
    source_lang,
    target_lang,
    term,
    domain=None,
    *,
    prepass_artifacts=None,
):
    """Look up a term in the glossary directory.

    Algorithm:
        1. **L1.5** (v0.3.0+) — if ``prepass_artifacts`` is provided, search
           ``characters[*].canonical_name`` / ``aliases[*].source`` and
           ``world_glossary["places"|"organizations"|"world_terms"][*].canonical_source``.
           Hit → return with ``audit_path = "L1.5.character"`` or
           ``"L1.5.world_glossary.<class>"``.
        2. **L2 direct** — try direct pair file ``glossary-{S}--{T}.md``
           (sorted alphabetical). Hit → return with ``audit_path = "direct"``.
        3. **L2 EN-pivot** — if miss AND neither S nor T is en-US, hop
           through ``glossary-en-US--{S}.md`` then ``glossary-en-US--{T}.md``.
           Hit → return with ``audit_path = "pivot.en-US (via '<en_term>')"``.
        4. Miss → return None.

    L1 (project glossary) and L3 / L4 (web search / LLM fallback) are caller
    concerns — this function covers L1.5 + L2 only.

    Args:
        glossary_dir: directory containing ``glossary-*--*.md`` files.
        source_lang: BCP-47 source language tag (e.g. ``"ja-JP"``).
        target_lang: BCP-47 target language tag.
        term: source-language term (exact match).
        domain: optional domain filter (e.g. ``"ui"``). Exact match only —
            ``"tech.crypto"`` does NOT fall back to ``"tech.software"``.
        prepass_artifacts: optional merged pre-pass artifact dict with shape
            ``{"characters": [...], "world_glossary": {"places": [...],
            "organizations": [...], "world_terms": [...],
            "cultural_references": [...]}}``. When supplied, searched FIRST
            (L1.5) before falling through to L2.

    Returns:
        On hit, a dict::

            {
                "target_term": "...",
                "source": "pontoon",        # L2 — or "pre-pass.characters" /
                                            # "pre-pass.world_glossary.<class>" for L1.5
                "notes": "...",
                "audit_path": "L1.5.character" |
                              "L1.5.world_glossary.<class>" |
                              "direct" |
                              "pivot.en-US (via '<en_term>')",
            }

        On miss, ``None``. File-not-found is treated as a miss, not an error.
    """
    # ---- Step 0: L1.5 pre-pass ----
    l1_5_hit = _lookup_l1_5_prepass(prepass_artifacts, term)
    if l1_5_hit is not None:
        return l1_5_hit

    glossary_dir = Path(glossary_dir)

    # ---- Step 1: direct pair file ----
    direct_path = glossary_dir / _pair_filename(source_lang, target_lang)
    if direct_path.exists():
        parsed = _parse_cached(str(direct_path.resolve()))
        entry, _matched_domain = _find_in_parsed(
            parsed, source_lang, term, domain=domain
        )
        if entry is not None:
            target_term = _target_term_from_entry(entry, target_lang)
            if target_term is not None:
                return {
                    "target_term": target_term,
                    "source": entry["source"],
                    "notes": entry["notes"],
                    "audit_path": "direct",
                }

    # ---- Step 2: EN-pivot fallback ----
    en = "en-US"
    if source_lang != en and target_lang != en:
        s_pivot_path = glossary_dir / _pair_filename(en, source_lang)
        t_pivot_path = glossary_dir / _pair_filename(en, target_lang)
        if s_pivot_path.exists() and t_pivot_path.exists():
            s_parsed = _parse_cached(str(s_pivot_path.resolve()))
            # Step 2a: source-term → EN pivot.
            s_entry, _ = _find_in_parsed(
                s_parsed, source_lang, term, domain=domain
            )
            if s_entry is not None:
                en_pivot = _target_term_from_entry(s_entry, en)
                if en_pivot:
                    # Step 2b: EN pivot → target term.
                    t_parsed = _parse_cached(str(t_pivot_path.resolve()))
                    t_entry, _ = _find_in_parsed(
                        t_parsed, en, en_pivot, domain=domain
                    )
                    if t_entry is not None:
                        target_term = _target_term_from_entry(t_entry, target_lang)
                        if target_term is not None:
                            return {
                                "target_term": target_term,
                                "source": t_entry["source"],
                                "notes": t_entry["notes"],
                                "audit_path": (
                                    f"pivot.en-US (via '{en_pivot}')"
                                ),
                            }

    # ---- Step 3: miss ----
    return None
