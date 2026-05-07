# NOTICES — translation-toolkit v0.3.0

This plugin bundles translation glossaries and reference materials from
upstream sources. Each entry below lists the source, license, and required
attribution per its license terms. Full license texts ship at
`vendor/<source>/LICENSE`.

---

## Glossary entries (feeds glossary-{a}--{b}.md tables)

### Mozilla Pontoon (TBX export)

- **License**: MPL-2.0 / CC-BY-SA (per termbase metadata).
- **Attribution**: Mozilla Foundation. https://pontoon.mozilla.org/
- **License file**: `vendor/mozilla-pontoon/LICENSE`

### GNOME i18n glossary

- **License**: LGPL / GPL (per upstream package metadata).
- **Attribution**: The GNOME Project. https://gitlab.gnome.org/Translation/gnome-i18n
- **License file**: `vendor/gnome-i18n/LICENSE`

### NAER 國家教育研究院樂詞網 (兩岸對照名詞)

- **License**: 政府資料開放授權條款 第 1 版 (Open Government Data License v1, ≈ CC-BY 4.0).
- **Attribution**: 國家教育研究院 (National Academy for Educational Research, Taiwan). https://terms.naer.edu.tw/
- **License file**: `vendor/naer/LICENSE`

### JLT 日本法令外国語訳データベース (法務省)

- **License**: CC-BY 4.0 互換 per upstream notice.
- **Attribution**: 法務省 日本法令外国語訳データベースシステム. https://www.japaneselawtranslation.go.jp/
- **License file**: `vendor/jlt/LICENSE`

### e-Stat 日英統計用語集 (政府統計の総合窓口)

- **License**: 政府標準利用規約 (Japanese Government Open Data License).
- **Attribution**: 総務省統計局 e-Stat. https://www.e-stat.go.jp/
- **License file**: `vendor/e-stat/LICENSE`

### 東京都 日英対訳用語集

- **License**: CC-BY 4.0.
- **Attribution**: 東京都. https://www.metro.tokyo.lg.jp/
- **License file**: `vendor/tokyo/LICENSE`

### 内閣官房 政府機関英語名称集

- **License**: 政府標準利用規約.
- **Attribution**: 内閣官房. https://www.cas.go.jp/
- **License file**: `vendor/cabinet/LICENSE`

---

## Parallel-corpus reference (feeds corpus/nict-en-ja-zh.md as exemplars)

### NICT 日英中基本文 v1.2

- **License**: CC-BY 3.0 Unported.
- **Attribution**: 国立研究開発法人 情報通信研究機構 (National Institute of Information and Communications Technology). https://alaginrc.nict.go.jp/jecbs/
- **License file**: `vendor/nict/LICENSE`
- **Note**: v0.1.0 ships a small fixture (~30 sentence triples). Full 5,304-triple corpus deferred to v0.2.

### 青空文庫 — 太宰治『走れメロス』 (smoke-test fixture)

- **License**: Public domain. 太宰治 (1909-1948); copyright expired 1999 in Japan (life+50, pre-TPP) and 2019 internationally (life+70).
- **Attribution**: 青空文庫 — https://www.aozora.gr.jp/cards/000035/card1567.html
- **Excerpt scope**: ~2700-char opening. Plain prose only — ruby annotations (《》) and editor notes (〔〕) removed. Used by `scripts/tests/test_e2e_novel_smoke.py` for translation-novel chunking + cost-reduction verification (no LLM calls).
- **Fixture path**: `scripts/tests/fixtures/sample-novel-chapter-ja.md`
- **Mirror**: `scripts/tests/fixtures/sample-book-ja/chapter-01.md` (byte-identical copy used by `test_e2e_v0.3.0_tier2_smoke.py` as the first chapter of the two-chapter book fixture).

### Two-chapter book fixture (synthetic continuation)

- **License**: Fabricated for translation-toolkit v0.3.0 Tier 2 smoke testing — NOT public-domain content. Released under the same MIT License as the rest of the plugin code (see repo-level `LICENSE`).
- **Author**: translation-toolkit maintainers (Phase F).
- **Scope**: `chapter-02.md` is a ~1,580-char synthetic continuation in matching archaic-narrative register, designed to exercise pre-pass cross-chapter merging (same character set as chapter 1 — メロス / ディオニス / セリヌンティウス) and world-glossary growth (one new place — アクロポリス; one new cultural reference — a fabricated literary maxim attributed to "an old poet"). The maxim is original synthetic prose, not a quotation from any published source.
- **Fixture path**: `scripts/tests/fixtures/sample-book-ja/chapter-02.md`
- **Used by**: `scripts/tests/test_e2e_v0.3.0_tier2_smoke.py` (no LLM calls — mocked subagent dispatch).

---

## Typography rules (feeds typography/{jlreq,clreq}-summary.md meta-section)

### W3C jlreq + clreq

- **License**: W3C Document License (3 February 2023).
- **Attribution**: W3C® (MIT, ERCIM, Keio, Beihang). https://www.w3.org/copyright/document-license-2023/
- **License file**: `vendor/w3c/LICENSE`
- **Source**: https://www.w3.org/TR/jlreq/ + https://www.w3.org/TR/clreq/
- **Note**: v0.1.0 ships manually-extracted summaries derived from W3C specs. Full programmatic extraction deferred.

---

## Optional fetch (NOT bundled — opt-in via scripts)

### Microsoft Terminology Collection

- **License**: GRAY (use permitted; redistribution NOT explicit). Treated as
  fetch-on-demand; never committed to this repo.
- **Fetch script**: `scripts/fetch-microsoft-terms.py` downloads to user cache only.
- **Attribution**: Microsoft Corporation.

### 特許庁 UTX patent term dictionary

- **License**: AAMT distribution; format-converted derivatives permitted with attribution.
- **Fetch script**: `scripts/fetch-jpo-utx.py` downloads to user cache only.
- **Attribution**: 特許庁 + 独立行政法人工業所有権情報・研修館 (INPIT).

---

## Plugin license

The translation-toolkit plugin code itself (skill bodies, build scripts, lib
modules) is released under the **MIT License**, consistent with other plugins
in this monkey-skills repository. See repo-level `LICENSE`.

The bundled upstream content listed above retains its original license; this
plugin does not relicense it.
