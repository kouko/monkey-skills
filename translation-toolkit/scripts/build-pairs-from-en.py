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
  - NAER CSV    (Task B3, zh-TW) — 樂詞網 學術名詞 academic terminology
  - e-Stat CSV  (Task B3, ja-JP) — 政府統計 統計用語集
  - Tokyo CSV/XLSX (Task B3, ja-JP) — 東京都 日英対訳辞書
  - Cabinet CSV (Task B3, ja-JP) — 内閣官房 部局課名・官職名英訳名称一覧

Output: scripts/canonical/glossary-en-US--<target>.md with frontmatter +
domain sections + 4-column tables (en-US | <target> | source | notes).

Domain inference:
  - Pontoon: "tech.web" if EN term contains url / browser / web / http;
             else "ui".
  - GNOME:   always "ui" (GNOME desktop UI strings).
  - JLT:     "gov" if ja_term contains 省/庁/局/府 (gov-org name);
             else "legal".
  - NAER:    NAER_CATEGORY_TO_DOMAIN map (CS/info → tech.software;
             統計學 → statistics; 法律 → legal; 醫學 → medical;
             經濟學 → finance; default → general).
  - e-Stat:  always "statistics".
  - Tokyo:   TOKYO_CATEGORY_TO_DOMAIN map (行政/福祉 → gov; default → general).
  - Cabinet: always "gov".

Pontoon TBX <xml:lang> mapping (Pontoon's own locale code, NOT BCP-47):
  ja-JP  -> ja
  zh-TW  -> zh-TW
  zh-CN  -> zh-CN

GNOME glossary filename mapping (vendor/gnome-i18n/<locale>.po):
  ja-JP  -> ja.po
  zh-TW  -> zh-TW.po
  zh-CN  -> zh-CN.po

Dependencies:
  - polib    (for parse_gnome_po;  python3 -m pip install polib)
  - openpyxl (for parse_tokyo_xlsx when xlsx is supplied; CSV path
              works without it. python3 -m pip install openpyxl)
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

# NAER 樂詞網 — map 學術領域 (academic field) -> domain.
NAER_CATEGORY_TO_DOMAIN = {
    "電子計算機名詞": "tech.software",
    "資訊名詞": "tech.software",
    "計算機名詞": "tech.software",
    "電機工程名詞": "tech.software",
    "統計學名詞": "statistics",
    "法律名詞": "legal",
    "醫學名詞": "medical",
    "牙醫學名詞": "medical",
    "藥學名詞": "medical",
    "經濟學名詞": "finance",
    "管理學名詞": "finance",
    "會計學名詞": "finance",
    # default → "general"
}

# 東京都 日英対訳 — map カテゴリ (category) -> domain.
TOKYO_CATEGORY_TO_DOMAIN = {
    "行政": "gov",
    "福祉": "gov",
    "観光": "general",
    "防災": "general",
    "生活": "general",
    # default → "general"
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


def parse_naer_csv(csv_path: Path) -> list[dict]:
    """Parse a NAER 學術名詞 / 樂詞網 CSV file -> list of entry dicts.

    Header autodetection: tries common Chinese / English column names.
    Domain inferred from `學術領域` (academic field) via NAER_CATEGORY_TO_DOMAIN;
    unknown categories default to "general".

    Returns: list of {en, target, source: 'naer', domain, notes (= category)}.
    """
    import csv

    entries: list[dict] = []
    # NAER CSVs sometimes carry UTF-8 BOM; utf-8-sig handles both.
    with csv_path.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return entries
        for row in reader:
            en = (row.get("英文名稱") or row.get("英文")
                  or row.get("en_term") or row.get("English") or "").strip()
            zh_tw = (row.get("中文名稱") or row.get("中文")
                     or row.get("zh_TW_term")
                     or row.get("Traditional Chinese") or "").strip()
            category = (row.get("學術領域") or row.get("category")
                        or row.get("分類") or "").strip()
            if not en or not zh_tw:
                continue
            domain = NAER_CATEGORY_TO_DOMAIN.get(category, "general")
            entries.append({
                "en": en,
                "target": zh_tw,
                "source": "naer",
                "domain": domain,
                "notes": category or "—",
            })
    return entries


def parse_estat_csv(csv_path: Path) -> list[dict]:
    """Parse an e-Stat 統計用語集 CSV file -> list of entry dicts.

    Handles UTF-8 BOM via utf-8-sig. All entries land in domain=statistics.

    Returns: list of {en, target, source: 'e-stat', domain: 'statistics', notes}.
    """
    import csv

    entries: list[dict] = []
    with csv_path.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return entries
        for row in reader:
            en = (row.get("English") or row.get("en_term")
                  or row.get("英文") or "").strip()
            ja = (row.get("Japanese") or row.get("ja_term")
                  or row.get("日本語") or row.get("用語") or "").strip()
            if not en or not ja:
                continue
            entries.append({
                "en": en,
                "target": ja,
                "source": "e-stat",
                "domain": "statistics",
                "notes": "—",
            })
    return entries


def parse_tokyo_csv(csv_path: Path) -> list[dict]:
    """Parse a Tokyo 日英対訳 CSV file -> list of entry dicts.

    Domain inferred from カテゴリ via TOKYO_CATEGORY_TO_DOMAIN; default = general.

    Returns: list of {en, target, source: 'tokyo', domain, notes (= category)}.
    """
    import csv

    entries: list[dict] = []
    with csv_path.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return entries
        for row in reader:
            en = (row.get("English") or row.get("英語")
                  or row.get("en_term") or "").strip()
            ja = (row.get("Japanese") or row.get("日本語")
                  or row.get("ja_term") or row.get("用語") or "").strip()
            cat = (row.get("カテゴリ") or row.get("category")
                   or row.get("分類") or "").strip()
            if not en or not ja:
                continue
            domain = TOKYO_CATEGORY_TO_DOMAIN.get(cat, "general")
            entries.append({
                "en": en,
                "target": ja,
                "source": "tokyo",
                "domain": domain,
                "notes": cat or "—",
            })
    return entries


def parse_tokyo_xlsx(xlsx_path: Path) -> list[dict]:
    """Parse a Tokyo 日英対訳 .xlsx file -> list of entry dicts.

    Requires `openpyxl`. Raises RuntimeError if not installed — callers
    should catch and fall through gracefully (the dispatcher logs a WARN
    and continues), mirroring the polib pattern in parse_gnome_po.
    """
    try:
        import openpyxl  # noqa: WPS433 — runtime dep guarded
    except ImportError as exc:  # pragma: no cover - dep guard
        raise RuntimeError(
            "openpyxl not installed; run: python3 -m pip install openpyxl"
        ) from exc

    wb = openpyxl.load_workbook(str(xlsx_path), read_only=True, data_only=True)
    sheet = wb.active
    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        return []
    headers = [str(c).strip() if c is not None else "" for c in rows[0]]

    en_keys = ("English", "英語", "en_term")
    ja_keys = ("Japanese", "日本語", "ja_term", "用語")
    cat_keys = ("カテゴリ", "category", "分類")

    en_col = next((i for i, h in enumerate(headers) if h in en_keys), None)
    ja_col = next((i for i, h in enumerate(headers) if h in ja_keys), None)
    cat_col = next((i for i, h in enumerate(headers) if h in cat_keys), None)

    if en_col is None or ja_col is None:
        return []

    entries: list[dict] = []
    for row in rows[1:]:
        en = str(row[en_col]).strip() if row[en_col] is not None else ""
        ja = str(row[ja_col]).strip() if row[ja_col] is not None else ""
        if not en or not ja:
            continue
        cat = ""
        if cat_col is not None and row[cat_col] is not None:
            cat = str(row[cat_col]).strip()
        domain = TOKYO_CATEGORY_TO_DOMAIN.get(cat, "general")
        entries.append({
            "en": en,
            "target": ja,
            "source": "tokyo",
            "domain": domain,
            "notes": cat or "—",
        })
    return entries


def parse_cabinet_csv(csv_path: Path) -> list[dict]:
    """Parse a Cabinet 部局課名・官職名 CSV file -> list of entry dicts.

    Handles UTF-8 BOM via utf-8-sig. All entries land in domain=gov.

    Returns: list of {en, target, source: 'cabinet', domain: 'gov', notes}.
    """
    import csv

    entries: list[dict] = []
    with csv_path.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return entries
        for row in reader:
            en = (row.get("English") or row.get("en_term") or "").strip()
            ja = (row.get("Japanese") or row.get("ja_term") or "").strip()
            if not en or not ja:
                continue
            entries.append({
                "en": en,
                "target": ja,
                "source": "cabinet",
                "domain": "gov",
                "notes": "—",
            })
    return entries


# --- Emitter --------------------------------------------------------------

def emit_pair_file(*,
                   pair: tuple[str, str] | None = None,
                   target_locale: str | None = None,
                   entries_by_domain: dict[str, list[dict]],
                   out_path: Path,
                   sources: list[str] | None = None,
                   generator_note: str | None = None,
                   manual_companion_note: str | None = None) -> None:
    """Emit glossary-{A}--{B}.md with frontmatter + domain sections.

    Two calling conventions (backwards-compat):
      A) New pair-generic:
           emit_pair_file(pair=("ja-JP", "zh-TW"),
                          entries_by_domain={domain: [{"ja-JP": ..., "zh-TW": ..., ...}]},
                          out_path=...)
         Each entry has keys matching the two locales in `pair`.
      B) Legacy en-US--<target>:
           emit_pair_file(target_locale="ja-JP",
                          entries_by_domain={domain: [{"en": ..., "target": ..., ...}]},
                          out_path=...)
         Each entry uses {"en": ..., "target": ...}; emitted as
         (lang_a="en-US", lang_b=target_locale).

    `pair` (when given) must be a (lang_a, lang_b) tuple; caller is
    responsible for any ordering convention (BCP-47 alphabetical recommended).

    `sources` overrides auto-detected source list. `generator_note` and
    `manual_companion_note` override the default header lines.
    """
    if pair is not None and target_locale is not None:
        raise ValueError("pass either pair=... or target_locale=..., not both")
    if pair is None and target_locale is None:
        raise ValueError("must pass either pair=... or target_locale=...")

    if pair is None:
        # Legacy en-US--<target> mode: build pair tuple + key entries
        # under {lang_a, lang_b} from {en, target}.
        lang_a, lang_b = "en-US", target_locale  # type: ignore[assignment]
        normalized: dict[str, list[dict]] = {}
        for domain, rows in entries_by_domain.items():
            normed = []
            for e in rows:
                if lang_a in e and lang_b in e:
                    normed.append(e)
                else:
                    normed.append({
                        **e,
                        lang_a: e.get("en", e.get(lang_a, "")),
                        lang_b: e.get("target", e.get(lang_b, "")),
                    })
            normalized[domain] = normed
        entries_by_domain = normalized
    else:
        lang_a, lang_b = pair

    if sources is None:
        sources = sorted({e["source"]
                          for entries in entries_by_domain.values()
                          for e in entries})
    domains = sorted(entries_by_domain.keys())
    total = sum(len(v) for v in entries_by_domain.values())

    sources_yaml = "[" + ", ".join(sources) + "]" if sources else "[]"
    domains_yaml = "[" + ", ".join(domains) + "]" if domains else "[]"

    if generator_note is None:
        generator_note = "Generated by scripts/build-pairs-from-en.py — do not hand-edit."
    if manual_companion_note is None:
        manual_companion_note = (
            f"Manual additions go in canonical/manual-entries-{lang_a}--{lang_b}.md (when added)."
        )

    lines: list[str] = []
    lines.append("---")
    lines.append(f"pair: [{lang_a}, {lang_b}]")
    lines.append("version: 0.1.0")
    lines.append(f"sources: {sources_yaml}")
    lines.append(f"domains_supported: {domains_yaml}")
    lines.append("---")
    lines.append("")
    lines.append(f"# Glossary {lang_a} ↔ {lang_b}")
    lines.append("")
    lines.append(f"> {generator_note}")
    lines.append(f"> {manual_companion_note}")
    lines.append("")
    lines.append("## meta")
    lines.append("")
    lines.append("(typography rules — see typography/jlreq-summary.md for ja-JP, "
                 "clreq-summary.md for zh-*)")
    lines.append("")

    for domain in domains:
        lines.append(f"## domain: {domain}")
        lines.append("")
        lines.append(f"| {lang_a} | {lang_b} | source | notes |")
        lines.append("|---|---|---|---|")
        rows = sorted(entries_by_domain[domain],
                      key=lambda x: str(x.get(lang_a, "")).lower())
        # De-duplicate (lang_a-term, lang_b-term, source) while preserving order.
        seen: set[tuple[str, str, str]] = set()
        for e in rows:
            a = e.get(lang_a, "")
            b = e.get(lang_b, "")
            src = e.get("source", "")
            notes = e.get("notes", "—")
            key = (a, b, src)
            if key in seen:
                continue
            seen.add(key)
            lines.append(f"| {a} | {b} | {src} | {notes} |")
        lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))
    print(f"OK: wrote {out_path.name} ({total} entries, "
          f"{len(domains)} domain(s), sources={sources})")


# --- Dispatcher -----------------------------------------------------------

def collect_entries(target: str, args: argparse.Namespace) -> dict[str, list[dict]]:
    """Run all wired parsers for `target` and return entries grouped by domain.

    Wired:
      - Pontoon (all targets)
      - GNOME PO (all targets)
      - JLT CSV (ja-JP only)
      - NAER CSV (zh-TW only)
      - e-Stat CSV (ja-JP only)
      - Tokyo CSV/XLSX (ja-JP only)
      - Cabinet CSV (ja-JP only)

    Override semantics: if any --*-tbx / --*-po / --*-csv / --*-xlsx is set
    (test-fixture mode), only the explicitly-set source(s) are read; the
    others are skipped to keep test output deterministic. In normal mode
    (no overrides), all wired sources are read from defaults under vendor/.
    """
    entries_by_domain: dict[str, list[dict]] = defaultdict(list)

    isolated = bool(
        args.pontoon_tbx or args.gnome_po or args.jlt_csv
        or args.naer_csv or args.estat_csv
        or args.tokyo_csv or args.tokyo_xlsx
        or args.cabinet_csv
    )

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

    # NAER CSV (zh-TW only — NAER is EN<->ZH-TW academic terms)
    if target == "zh-TW":
        if args.naer_csv:
            naer_csv = Path(args.naer_csv)
        elif not isolated:
            naer_csv = DEFAULT_VENDOR / "naer" / "academic-terms-zh-TW.csv"
        else:
            naer_csv = None
        if naer_csv is not None:
            if naer_csv.exists():
                for e in parse_naer_csv(naer_csv):
                    entries_by_domain[e["domain"]].append(e)
            else:
                print(f"WARN: NAER CSV not found at {naer_csv}; skipping NAER for {target}",
                      file=sys.stderr)

    # e-Stat / Tokyo / Cabinet — all ja-JP only.
    if target == "ja-JP":
        # e-Stat
        if args.estat_csv:
            estat_csv = Path(args.estat_csv)
        elif not isolated:
            estat_csv = DEFAULT_VENDOR / "e-stat" / "stat-terms-en-ja.csv"
        else:
            estat_csv = None
        if estat_csv is not None:
            if estat_csv.exists():
                for e in parse_estat_csv(estat_csv):
                    entries_by_domain[e["domain"]].append(e)
            else:
                print(f"WARN: e-Stat CSV not found at {estat_csv}; "
                      f"skipping e-Stat for {target}", file=sys.stderr)

        # Tokyo (CSV preferred; XLSX fallback if explicitly supplied or
        # only XLSX exists in vendor/)
        tokyo_csv: Path | None = None
        tokyo_xlsx: Path | None = None
        if args.tokyo_csv:
            tokyo_csv = Path(args.tokyo_csv)
        elif args.tokyo_xlsx:
            tokyo_xlsx = Path(args.tokyo_xlsx)
        elif not isolated:
            default_csv = DEFAULT_VENDOR / "tokyo" / "en-ja-translation.csv"
            default_xlsx = DEFAULT_VENDOR / "tokyo" / "en-ja-translation.xlsx"
            if default_csv.exists():
                tokyo_csv = default_csv
            elif default_xlsx.exists():
                tokyo_xlsx = default_xlsx
        if tokyo_csv is not None:
            if tokyo_csv.exists():
                for e in parse_tokyo_csv(tokyo_csv):
                    entries_by_domain[e["domain"]].append(e)
            else:
                print(f"WARN: Tokyo CSV not found at {tokyo_csv}; "
                      f"skipping Tokyo for {target}", file=sys.stderr)
        elif tokyo_xlsx is not None:
            if tokyo_xlsx.exists():
                try:
                    for e in parse_tokyo_xlsx(tokyo_xlsx):
                        entries_by_domain[e["domain"]].append(e)
                except RuntimeError as exc:
                    print(f"WARN: Tokyo XLSX parser failed ({exc}); "
                          f"skipping Tokyo for {target}", file=sys.stderr)
            else:
                print(f"WARN: Tokyo XLSX not found at {tokyo_xlsx}; "
                      f"skipping Tokyo for {target}", file=sys.stderr)

        # Cabinet
        if args.cabinet_csv:
            cabinet_csv = Path(args.cabinet_csv)
        elif not isolated:
            cabinet_csv = DEFAULT_VENDOR / "cabinet" / "gov-orgs-en-ja.csv"
        else:
            cabinet_csv = None
        if cabinet_csv is not None:
            if cabinet_csv.exists():
                for e in parse_cabinet_csv(cabinet_csv):
                    entries_by_domain[e["domain"]].append(e)
            else:
                print(f"WARN: Cabinet CSV not found at {cabinet_csv}; "
                      f"skipping Cabinet for {target}", file=sys.stderr)

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
    parser.add_argument("--naer-csv", default=None,
                        help="Override NAER CSV path (test fixture; zh-TW only). "
                             "When set, applies to whichever single --target is built.")
    parser.add_argument("--estat-csv", default=None,
                        help="Override e-Stat CSV path (test fixture; ja-JP only). "
                             "When set, applies to whichever single --target is built.")
    parser.add_argument("--tokyo-csv", default=None,
                        help="Override Tokyo CSV path (test fixture; ja-JP only). "
                             "When set, applies to whichever single --target is built.")
    parser.add_argument("--tokyo-xlsx", default=None,
                        help="Override Tokyo XLSX path (test fixture; ja-JP only; "
                             "requires openpyxl). When set, applies to whichever "
                             "single --target is built.")
    parser.add_argument("--cabinet-csv", default=None,
                        help="Override Cabinet CSV path (test fixture; ja-JP only). "
                             "When set, applies to whichever single --target is built.")
    parser.add_argument("--out-dir", default=None,
                        help="Override output directory "
                             f"(default: {DEFAULT_OUT}).")
    args = parser.parse_args(argv)

    overrides = (
        args.pontoon_tbx, args.gnome_po, args.jlt_csv,
        args.naer_csv, args.estat_csv,
        args.tokyo_csv, args.tokyo_xlsx, args.cabinet_csv,
    )
    if not args.all and not args.target:
        parser.error("must pass either --target <locale> or --all")
    if args.all and any(overrides):
        parser.error(
            "--pontoon-tbx / --gnome-po / --jlt-csv / --naer-csv / "
            "--estat-csv / --tokyo-csv / --tokyo-xlsx / --cabinet-csv "
            "may only be combined with a single --target"
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
        emit_pair_file(target_locale=target,
                       entries_by_domain=entries_by_domain,
                       out_path=out_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
