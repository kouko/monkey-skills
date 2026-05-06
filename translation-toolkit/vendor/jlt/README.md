# JLT 標準対訳辞書 (Standard Bilingual Dictionary)

## Origin

Japan Ministry of Justice — 日本法令外国語訳データベースシステム (Japanese Law
Translation, JLT). Operated by Ministry of Justice 大臣官房司法法制部.

Site: https://www.japaneselawtranslation.go.jp/

The 標準対訳辞書 (Standard Bilingual Dictionary) is the canonical EN↔JA glossary
of Japanese legal and government-administrative terminology used across the
JLT translation database.

## Manual download (recommended for full dataset)

The CSV download endpoint requires an interactive session; `curl` cannot fetch
directly. To replace the bundled sample with the full dataset:

1. Open https://www.japaneselawtranslation.go.jp/ja/dicts/download in a browser.
2. Select the CSV (UTF-8) variant.
3. Save the downloaded file as `standard-bilingual-dictionary.csv` in this
   directory, replacing the sample shipped with v0.1.

The full dataset is approximately several thousand entries; the sample below
ships ~38 entries for v0.1 development and tests.

## Sample shipped with v0.1.0

`standard-bilingual-dictionary.csv` is a curated 38-entry sample representative
of JLT content. It exercises both domain-inference branches in the build
script:

- `gov` — entries whose `ja_term` contains 省 / 庁 / 局 / 府 (government
  organisation names)
- `legal` — all other entries (statutes, legal-procedure terminology, civil
  /commercial/criminal-law concepts)

Columns: `en_term, ja_term, source_law, notes`.

The sample covers the Constitution, Civil Code, Penal Code, Companies Act,
Code of Civil Procedure, Cabinet Act, Local Autonomy Act, and various
Establishment Acts.

## License

CC-BY 4.0 互換 — per the 標準利用規約 (Standard Terms of Use) of Japanese
government open data, JLT translations and the dictionary are redistributable
under terms compatible with Creative Commons Attribution 4.0 International.

See `LICENSE` in this directory and the official terms of use:
https://www.japaneselawtranslation.go.jp/ja/about_dicts
