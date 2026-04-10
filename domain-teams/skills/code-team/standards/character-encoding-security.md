# Character Encoding Security (JP preamble)

This standard covers character-encoding-related vulnerabilities that
arise in multi-byte (Shift_JIS, UTF-8, EUC-JP) contexts. These
attacks are **under-documented in English-language security
literature**, including OWASP ASVS v5.0.0, because the attack
surface is rooted in legacy Japanese web stacks and in the
interaction between multi-byte encodings and escaping logic that
was originally designed for single-byte ASCII.

code-team adopts **徳丸本 第 2 版 Ch.6「文字コードとセキュリティ」**
as its canonical reference for this topic. This file augments
`app-security-standard.md` (which is ASVS v5.0.0 aligned) and must
be consulted in tandem with it whenever the application under
review handles user input in a Japanese locale.

## Primary Sources

- **徳丸浩 (2018) 『体系的に学ぶ 安全な Web アプリケーションの作り方 第 2 版 — 脆弱性が生まれる原理と対策の実践』, SB クリエイティブ. ISBN 978-4797393163.** Canonical JP primary source on web application security. 9 chapters; **Ch.6「文字コードとセキュリティ」** is the chapter this standard grounds on. NDL record ID: R100000002-I029031208. 第 3 版は 2026-04 現在未発表。
- OWASP ASVS v5.0.0 — https://asvs.dev/v5.0.0/ — complementary Anglo-American primary for the general encoding/validation baseline (V1, V2). See `app-security-standard.md`.
- 徳丸浩 (2013) "文字コードに起因する脆弱性とその対策（増補版）", SlideShare / Docswell — supplementary slide deck by the 徳丸本 author covering the same material in talk form (cite book chapter as primary; slide deck as secondary).

## Why a JP-specific standard?

グローバル英語圏の security 文献では多バイト文字符号化に起因する
脆弱性の実例が少ない。OWASP ASVS v5.0.0 V1 "Encoding and
Sanitization" と V2 "Validation and Business Logic" は文字符号化
をある程度扱うが、**Shift_JIS / EUC-JP / 日本語 legacy stack
固有のリスクパターンには踏み込まない**。

日本語を扱う Web アプリケーションでは、以下のような JP 特有の
リスクが実在する：

1. **Shift_JIS の 5C 問題** — Shift_JIS 二バイト目が `0x5C`
   (ASCII `\`) と衝突し、SQL escape や文字列リテラル終端判定を
   無効化する。「表」などの文字の 2 バイト目が `0x5C` のため、
   素朴な escape 実装は容易に bypass される。
2. **UTF-8 over-long encoding** — 本来 1 バイトで表現できる ASCII
   文字を冗長な multi-byte シーケンスで encode することで、
   blacklist 型 XSS filter を bypass する古典的攻撃。
3. **文字境界 (boundary) 判定の誤り** — multi-byte 文字の 1 byte
   目だけを通過させて 2 byte 目を dangling させる攻撃で、後続の
   escaping 実装を破壊する。
4. **文字符号化を動的に変換する legacy CMS / EC サイト** での
   文字化け経由 injection — 入力・保存・出力で異なる encoding
   を使う stack (例: 入力 Shift_JIS、DB UTF-8、出力 EUC-JP) で
   変換過程に bypass が発生する。
5. **IPA「安全な Web アプリケーションの作り方」指南** — 徳丸浩
   が contributor として関わる日本政府系のセキュリティガイドライン
   でも multi-byte 処理が強調されており、日本の企業セキュリティ
   監査基準として機能している。

## Verification Checklist (JP preamble augmentation to ASVS)

This checklist augments the ASVS v5.0.0 V1/V2 baseline with the
JP-specific concerns from 徳丸本 Ch.6:

- [ ] **Unified encoding across the full request→DB→response
  pipeline** — declare one encoding (typically UTF-8) and verify
  that input parsing, DB storage, and output rendering all agree.
  No silent encoding conversion in middleware.
- [ ] **Shift_JIS interaction audit** — if any component
  (legacy DB, third-party API, uploaded CSV) uses Shift_JIS,
  review every escape point for 5C handling. Use
  encoding-aware escape functions (e.g. `mysqli_real_escape_string`
  with the correct `set_charset`), not naive string replacement.
- [ ] **Canonicalize before validate** — normalize input to the
  target encoding (UTF-8 NFC) **before** running validation rules
  (ASVS V2). Validating raw bytes is a boundary-violation trap.
- [ ] **Reject invalid byte sequences** — over-long UTF-8, isolated
  surrogate halves, and incomplete multi-byte sequences should be
  rejected, not silently "fixed".
- [ ] **Parameterized queries** — use prepared statements and
  parameter binding universally. This neutralizes the 5C problem
  at the protocol layer rather than relying on escape functions.
- [ ] **Context-aware HTML escaping** — use a library that
  understands HTML escaping contexts AND the source encoding;
  don't hand-roll `str_replace` for `<`, `>`, `&`, `"`.

## Cross-Reference

`app-security-standard.md` covers the ASVS-aligned (English-canonical)
application security baseline — V1 Encoding, V2 Validation, V6
Authentication, V7 Session, V13 + V14 Secrets, V16 Error Handling.
This file **augments** that baseline with JP-specific encoding
concerns that ASVS v5.0.0 does not cover in depth.

Both files must be consulted when evaluating code that handles user
input in JP locales. For non-JP applications, `app-security-standard.md`
is sufficient; consulting this file still does no harm because the
Unicode edge cases (over-long encoding, surrogate halves) apply
universally.

## Anti-Patterns

- ❌ **Assuming UTF-8 everywhere** when the codebase interacts with
  legacy JP systems (old DB exports, CSV uploads, third-party JP
  APIs) — silent encoding mismatch is injection's best friend
- ❌ **Silent fallback to Shift_JIS** without escaping discipline
  (particularly in PHP legacy codebases and older Rails stacks)
- ❌ **Citing only English-language OWASP** for JP-locale web apps —
  ASVS is necessary but not sufficient
- ❌ **Hand-rolled escape functions** that operate on byte strings
  without encoding awareness
- ❌ **Validating raw request bytes** before canonicalizing to a
  known encoding — you're not validating what you think you are
- ❌ **Treating 5C problem as "solved by prepared statements" and
  moving on** — prepared statements help, but any raw SQL string
  concatenation anywhere in the codebase re-opens the hole
