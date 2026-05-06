#!/usr/bin/env python3
"""Build EN-pivoted pair glossaries from upstream sources.

Usage:
  python3 build-pairs-from-en.py --target ja-JP   # build glossary-en-US--ja-JP.md
  python3 build-pairs-from-en.py --target zh-TW   # build glossary-en-US--zh-TW.md
  python3 build-pairs-from-en.py --target zh-CN   # build glossary-en-US--zh-CN.md
  python3 build-pairs-from-en.py --all            # build all three

Wired sources:
  - Pontoon TBX (Task B1)        — Mozilla Pontoon community glossary
  - GNOME PO    (Task B2)        — GNOME Translation Project glossary
  - JLT CSV     (Task B2, ja-JP) — Japanese Law Translation 標準対訳辞書

Tasks B3/B4 will add NAER / e-Stat / Tokyo / Cabinet parsers under the same
dispatcher (see `collect_entries`).

Output: scripts/canonical/glossary-en-US--<target>.md with frontmatter +
domain sections + 4-column tables (en-US | <target> | source | notes).

Domain inference:
  - Pontoon: "tech.web" if EN term contains url / browser / web / http;
             else "ui".
  - GNOME:   always "ui" (GNOME desktop UI strings).
  - JLT:     "gov" if ja_term contains 省/庁/局/府 (gov-org name);
             else "legal".

Pontoon TBX <xml:lang> mapping (Pontoon's own locale code, NOT BCP-47):
  ja-JP  -> ja
  zh-TW  -> zh-TW
  zh-CN  -> zh-CN

GNOME glossary filename mapping (vendor/gnome-i18n/<locale>.po):
  ja-JP  -> ja.po
  zh-TW  -> zh-TW.po
  zh-CN  -> zh-CN.po

Dependencies:
  - polib  (for parse_gnome_po; install via `python3 -m pip install polib`)
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VENDOR = ROOT / "vendor"
DEFAULT_OUT = ROOT / "scripts" / "canonical"

XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"

VALID_TARGETS = ["ja-JP", "zh-TW", "zh-CN"]

# Map BCP-47 target locale -> Pontoon's xml:lang code.
PONTOON_LANG_MAP = {
    "ja-JP": "ja",
    "zh-TW": "zh-TW",
    "zh-CN": "zh-CN",
}

# GNOME glossary filenames in vendor/gnome-i18n/.
GNOME_PO_MAP = {
    "ja-JP": "ja.po",
    "zh-TW": "zh-TW.po",
    "zh-CN": "zh-CN.po",
}


# --- Parsers --------------------------------------------------------------

def parse_pontoon_tbx(tbx_path: Path, target_locale: str) -> list[dict]:
    """Parse a Pontoon TBX file and return list of entry dicts.

    target_locale: BCP-47 (ja-JP / zh-TW / zh-CN) — mapped internally to
    Pontoon's `xml:lang` code via PONTOON_LANG_MAP.

    Returns: list of {en, target, source: 'pontoon', domain, notes}.
    """
    pontoon_lang = PONTOON_LANG_MAP.get(target_locale, target_locale)
    tree = ET.parse(tbx_path)
    entries: list[dict] = []
    for term_entry in tree.iter("termEntry"):
        en_term: str | None = None
        target_term: str | None = None
        for lang_set in term_entry.findall(".//langSet"):
            lang = lang_set.get(XML_LANG)
            term = lang_set.findtext(".//term")
            if not lang or not term:
                continue
            term = term.strip()
            if not term:
                continue
            # English: accept "en" or any "en-*" variant.
            if lang == "en" or lang.startswith("en-") or lang.startswith("en_"):
                en_term = term
            # Target: accept exact match or same-primary-language match
            # (e.g., "ja" matches target "ja-JP"; "zh-TW" matches "zh-TW").
            elif lang == pontoon_lang:
                target_term = term
            elif lang.split("-")[0] == pontoon_lang.split("-")[0] and "-" not in pontoon_lang:
                target_term = term
        if en_term and target_term:
            domain = _infer_pontoon_domain(en_term)
            entries.append({
                "en": en_term,
                "target": target_term,
                "source": "pontoon",
                "domain": domain,
                "notes": "—",
            })
    return entries


def _infer_pontoon_domain(en_term: str) -> str:
    """Heuristic: web-y terms -> tech.web; everything else -> ui."""
    needles = ("url", "browser", "web", "http")
    lo = en_term.lower()
    return "tech.web" if any(n in lo for n in needles) else "ui"


def parse_gnome_po(po_path: Path) -> list[dict]:
    """Parse a GNOME glossary PO file -> list of entry dicts.

    All entries are tagged domain=ui (GNOME desktop UI terminology).
    Skips obsolete entries, empty translations, and the PO header
    (msgid="").

    Returns: list of {en, target, source: 'gnome', domain: 'ui', notes}.

    Raises RuntimeError if `polib` is not available — callers should catch
    and fall through gracefully (the dispatcher logs a WARN and continues).
    """
    try:
        import polib  # noqa: WPS433 — runtime dep guarded
    except ImportError as exc:  # pragma: no cover - dep guard
        raise RuntimeError(
            "polib not installed; run: python3 -m pip install polib"
        ) from exc

    po = polib.pofile(str(po_path))
    entries: list[dict] = []
    for entry in po:
        if entry.obsolete:
            continue
        msgid = (entry.msgid or "").strip()
        msgstr = (entry.msgstr or "").strip()
        if not msgid or not msgstr:
            continue
        entries.append({
            "en": msgid,
            "target": msgstr,
            "source": "gnome",
            "domain": "ui",
            "notes": "—",
        })
    return entries


def parse_jlt_csv(csv_path: Path) -> list[dict]:
    """Parse a JLT CSV file -> list of entry dicts.

    Header autodetection: prefers `en_term`/`ja_term`; falls back to common
    variants (`English`/`Japanese`, `Original`/`Translation`); else first 2
    columns.

    Domain inference:
      - 'gov'   if ja_term contains 省/庁/局/府 (suggests gov-org name)
      - 'legal' otherwise

    Returns: list of {en, target, source: 'jlt', domain, notes}.
    """
    import csv

    en_keys_pref = (
        ("en_term", "ja_term"),
        ("English", "Japanese"),
        ("Original", "Translation"),
    )

    entries: list[dict] = []
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return entries

        en_key: str | None = None
        ja_key: str | None = None
        for ek, jk in en_keys_pref:
            if ek in reader.fieldnames and jk in reader.fieldnames:
                en_key, ja_key = ek, jk
                break
        if en_key is None:
            # Fall back to first two columns.
            en_key = reader.fieldnames[0]
            ja_key = reader.fieldnames[1] if len(reader.fieldnames) > 1 else None
            if ja_key is None:
                return entries

        for row in reader:
            en = (row.get(en_key) or "").strip()
            ja = (row.get(ja_key) or "").strip()
            if not en or not ja:
                continue
            domain = "gov" if any(k in ja for k in ("省", "庁", "局", "府")) else "legal"
            note = (row.get("source_law") or row.get("notes") or "—").strip() or "—"
            entries.append({
                "en": en,
                "target": ja,
                "source": "jlt",
                "domain": domain,
                "notes": note,
            })
    return entries


# --- Emitter --------------------------------------------------------------

def emit_pair_file(target_locale: str,
                   entries_by_domain: dict[str, list[dict]],
                   out_path: Path) -> None:
    """Emit glossary-en-US--<target>.md with frontmatter + domain sections."""
    sources = sorted({e["source"]
                      for entries in entries_by_domain.values()
                      for e in entries})
    domains = sorted(entries_by_domain.keys())
    total = sum(len(v) for v in entries_by_domain.values())

    sources_yaml = "[" + ", ".join(sources) + "]" if sources else "[]"
    domains_yaml = "[" + ", ".join(domains) + "]" if domains else "[]"

    lines: list[str] = []
    lines.append("---")
    lines.append(f"pair: [en-US, {target_locale}]")
    lines.append("version: 0.1.0")
    lines.append(f"sources: {sources_yaml}")
    lines.append(f"domains_supported: {domains_yaml}")
    lines.append("---")
    lines.append("")
    lines.append(f"# Glossary en-US ↔ {target_locale}")
    lines.append("")
    lines.append("> Generated by scripts/build-pairs-from-en.py — do not hand-edit.")
    lines.append(f"> Manual additions go in canonical/manual-entries-en-US--{target_locale}.md (when added).")
    lines.append("")
    lines.append("## meta")
    lines.append("")
    lines.append("(typography rules — see typography/jlreq-summary.md for ja-JP, "
                 "clreq-summary.md for zh-*)")
    lines.append("")

    for domain in domains:
        lines.append(f"## domain: {domain}")
        lines.append("")
        lines.append(f"| en-US | {target_locale} | source | notes |")
        lines.append("|---|---|---|---|")
        rows = sorted(entries_by_domain[domain],
                      key=lambda x: x["en"].lower())
        # De-duplicate (en, target, source) while preserving order.
        seen: set[tuple[str, str, str]] = set()
        for e in rows:
            key = (e["en"], e["target"], e["source"])
            if key in seen:
                continue
            seen.add(key)
            lines.append(f"| {e['en']} | {e['target']} | {e['source']} | {e['notes']} |")
        lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))
    print(f"OK: wrote {out_path.name} ({total} entries, "
          f"{len(domains)} domain(s), sources={sources})")


# --- Dispatcher -----------------------------------------------------------

def collect_entries(target: str, args: argparse.Namespace) -> dict[str, list[dict]]:
    """Run all wired parsers for `target` and return entries grouped by domain.

    Wired: Pontoon (all targets), GNOME PO (all targets), JLT CSV (ja-JP only).
    B3/B4 will append NAER / e-Stat / Tokyo / Cabinet.

    Override semantics: if any of --pontoon-tbx / --gnome-po / --jlt-csv is
    set (test-fixture mode), only the explicitly-set source(s) are read; the
    others are skipped to keep test output deterministic. In normal mode
    (no overrides), all wired sources are read from defaults under vendor/.
    """
    entries_by_domain: dict[str, list[dict]] = defaultdict(list)

    isolated = bool(args.pontoon_tbx or args.gnome_po or args.jlt_csv)

    # Pontoon
    if args.pontoon_tbx:
        tbx = Path(args.pontoon_tbx)
    elif not isolated:
        pontoon_lang = PONTOON_LANG_MAP.get(target, target)
        tbx = DEFAULT_VENDOR / "mozilla-pontoon" / f"{pontoon_lang}.v2.tbx"
    else:
        tbx = None
    if tbx is not None:
        if tbx.exists():
            for e in parse_pontoon_tbx(tbx, target):
                entries_by_domain[e["domain"]].append(e)
        else:
            print(f"WARN: Pontoon TBX not found at {tbx}; skipping Pontoon for {target}",
                  file=sys.stderr)

    # GNOME PO (all 3 targets)
    if args.gnome_po:
        gnome_po = Path(args.gnome_po)
    elif not isolated:
        gnome_filename = GNOME_PO_MAP.get(target)
        gnome_po = (DEFAULT_VENDOR / "gnome-i18n" / gnome_filename) if gnome_filename else None
    else:
        gnome_po = None
    if gnome_po is not None:
        if gnome_po.exists():
            try:
                for e in parse_gnome_po(gnome_po):
                    entries_by_domain[e["domain"]].append(e)
            except RuntimeError as exc:
                print(f"WARN: GNOME PO parser failed ({exc}); skipping GNOME for {target}",
                      file=sys.stderr)
        else:
            print(f"WARN: GNOME PO not found at {gnome_po}; skipping GNOME for {target}",
                  file=sys.stderr)

    # JLT CSV (ja-JP only — JLT is EN<->JA)
    if target == "ja-JP":
        if args.jlt_csv:
            jlt_csv = Path(args.jlt_csv)
        elif not isolated:
            jlt_csv = DEFAULT_VENDOR / "jlt" / "standard-bilingual-dictionary.csv"
        else:
            jlt_csv = None
        if jlt_csv is not None:
            if jlt_csv.exists():
                for e in parse_jlt_csv(jlt_csv):
                    entries_by_domain[e["domain"]].append(e)
            else:
                print(f"WARN: JLT CSV not found at {jlt_csv}; skipping JLT for {target}",
                      file=sys.stderr)

    return entries_by_domain


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build EN-pivoted pair glossaries from upstream sources.",
    )
    parser.add_argument("--target", choices=VALID_TARGETS,
                        help="Build a single target locale.")
    parser.add_argument("--all", action="store_true",
                        help="Build all three targets (ja-JP, zh-TW, zh-CN).")
    parser.add_argument("--pontoon-tbx", default=None,
                        help="Override Pontoon TBX path (test fixture). "
                             "When set, applies to whichever single --target is built.")
    parser.add_argument("--gnome-po", default=None,
                        help="Override GNOME glossary PO path (test fixture). "
                             "When set, applies to whichever single --target is built.")
    parser.add_argument("--jlt-csv", default=None,
                        help="Override JLT CSV path (test fixture; ja-JP only). "
                             "When set, applies to whichever single --target is built.")
    parser.add_argument("--out-dir", default=None,
                        help="Override output directory "
                             f"(default: {DEFAULT_OUT}).")
    args = parser.parse_args(argv)

    if not args.all and not args.target:
        parser.error("must pass either --target <locale> or --all")
    if args.all and (args.pontoon_tbx or args.gnome_po or args.jlt_csv):
        parser.error(
            "--pontoon-tbx / --gnome-po / --jlt-csv may only be combined with "
            "a single --target"
        )

    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    targets = VALID_TARGETS if args.all else [args.target]
    out_dir = Path(args.out_dir) if args.out_dir else DEFAULT_OUT
    out_dir.mkdir(parents=True, exist_ok=True)

    for target in targets:
        entries_by_domain = collect_entries(target, args)
        if not entries_by_domain:
            print(f"WARN: no entries collected for {target}; "
                  f"emitting empty glossary file.", file=sys.stderr)
        out_path = out_dir / f"glossary-en-US--{target}.md"
        emit_pair_file(target, entries_by_domain, out_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
