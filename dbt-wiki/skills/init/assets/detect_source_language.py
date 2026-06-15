#!/usr/bin/env python3
"""
detect_source_language.py — resolve the project's source-comment language.

dbt-wiki writes knowledge pages in the language of the dbt model comments
(source of truth), not English. This resolves which language that is, so init
can record `source_language` and Phase B distillation + pack can honour it.

Resolution priority (first hit wins):
  1. --language <code>            (explicit CLI override)
  2. $DBT_WIKI_LANGUAGE           (explicit env override)
  3. auto-detect: dominant script across every evidence model's
     `## Description` + `## Inline Comments` (Phase-A output)

Auto-detect maps script presence to a code:
  kana present                  -> ja
  hangul present                -> ko
  Han is >=5% of (Han+Latin)    -> zh   (Traditional vs Simplified not distinguished)
  otherwise                     -> en
The Han test is a FRACTION, not a majority: source comments are bilingual in
practice — CJK prose interleaved with ASCII column names / SQL fragments /
model refs — so Latin almost always outnumbers Han even when the prose is
entirely CJK (a fully Chinese-commented project typically lands ~15-20% Han).
A 5% floor cleanly separates a CJK-commented project (double-digit %) from an
English-commented one (~0%). This is best-effort — prefer the explicit setting.

Usage:
  python detect_source_language.py [WIKI_DIR] [--language zh] [--verbose]
Prints the resolved code on stdout (one line). --verbose adds the script tally.
"""
import os
import re
import sys
import glob
import subprocess

RANGES = {
    "han":   (r'[一-鿿]'),
    "kana":  (r'[぀-ヿ]'),     # hiragana + katakana
    "hangul": (r'[가-힣]'),
    "latin": (r'[A-Za-z]'),
}


def resolve_wiki_dir(argv):
    value_flags = {"--language"}   # flags whose following token is a value, not a positional
    prev = ""
    for a in argv:
        if prev not in value_flags and not a.startswith("-") and os.path.isdir(a):
            return a if os.path.basename(a) == ".dbt-wiki" else os.path.join(a, ".dbt-wiki")
        prev = a
    try:
        root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"],
                                       text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        root = os.getcwd()
    return os.path.join(root, ".dbt-wiki")


def arg_value(argv, flag):
    return argv[argv.index(flag) + 1] if flag in argv and argv.index(flag) + 1 < len(argv) else None


def source_text(wiki):
    """Concatenate every evidence model's Description + Inline Comments."""
    chunks = []
    for p in glob.glob(os.path.join(wiki, "_evidence", "models", "*.md")):
        t = open(p, encoding="utf-8").read()
        for hdr in ("## Description", "## Inline Comments"):
            m = re.search(re.escape(hdr) + r'\n(.*?)(?:\n## |\Z)', t, re.S)
            if m:
                chunks.append(m.group(1))
    return "\n".join(chunks)


def detect(text):
    tally = {k: len(re.findall(rx, text)) for k, rx in RANGES.items()}
    han_latin = tally["han"] + tally["latin"]
    han_frac = (tally["han"] / han_latin) if han_latin else 0.0
    if tally["kana"] > 0:
        code = "ja"
    elif tally["hangul"] > 0:
        code = "ko"
    elif han_frac >= 0.05:
        code = "zh"
    else:
        code = "en"
    tally["han_fraction"] = round(han_frac, 3)
    return code, tally


def main(argv):
    explicit = arg_value(argv, "--language") or os.environ.get("DBT_WIKI_LANGUAGE")
    if explicit:
        print(explicit.strip())
        if "--verbose" in argv:
            print(f"(explicit override)", file=sys.stderr)
        return 0
    wiki = resolve_wiki_dir(argv)
    if not os.path.isdir(wiki):
        print("en")   # safe default when no evidence yet
        return 0
    code, tally = detect(source_text(wiki))
    print(code)
    if "--verbose" in argv:
        print(f"script tally: {tally}  -> {code}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
