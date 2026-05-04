# Fixture: JP business letter — 取引開始のご挨拶 (synthetic-representative)

**Source**: synthetic-representative (composed by maintainer for evaluation purposes; modeled on standard JP 商用文 / 拝啓-formula register, per NHK 放送文化研究所 / 文化庁 文化審議会 国語分科会 reference conventions)
**Accessed**: 2026-05-05 (composed)
**Capture method**: synthetic representative — not a real artifact
**License**: maintainer-authored, freely usable for plugin evaluation
**Honesty flag**: This is NOT a real fetched artifact. It is a maintainer-composed text built to exhibit the canonical 拝啓-formula 7 moves cleanly (頭語 / 時候の挨拶 / 安否の挨拶 / 主文 / 末文 / 結語 / 後付). Real-world JP business letters vary; eval results from this fixture are a smoke-test of `lens-genre-ja` application, not a benchmark of real-text deconstruction quality.
**Eval target**: `artifact-deconstruct` must identify all 7 canonical moves with section mapping, verify 頭語/結語 pairing (拝啓 → 敬具), confirm 時候の挨拶 matches season, identify the sub-genre (取引開始 / 挨拶状), and explicitly attribute analysis to `lens-genre-ja`.

---

```
                                                  令和八年五月五日

株式会社 みなと商事
営業本部長　高橋 健一 様

                                          株式会社 山手物産
                                          代表取締役　佐藤 太郎


              拝啓


  新緑の候、貴社ますますご清栄のこととお慶び申し上げます。
平素は格別のお引き立てを賜り、厚く御礼申し上げます。

  さて、このたび弊社では、長年の懸案でございました関西方面における
販路拡大の一環といたしまして、四月一日付をもちまして大阪支店を新設
いたしました。つきましては、貴社との取引開始につきまして、ぜひとも
ご検討を賜りたく、別添の会社案内ならびに取扱商品一覧をお送り申し
上げる次第でございます。

  なお、弊社営業担当の田中が、後日改めましてご挨拶に伺わせて
いただきたく存じております。ご多忙の折、誠に恐縮ではございますが、
ご都合のよろしい日時をお知らせいただければ幸いに存じます。

  まずは略儀ながら書中をもちまして、ご挨拶かたがたお願い申し
上げます。今後とも変わらぬご厚情を賜りますよう、何卒よろしくお願い
申し上げます。


                                                          敬具


別添：
  一、会社案内　　一部
  二、取扱商品一覧　一部
                                                            以上
```

---

## Annotations for evaluator

The fixture exhibits all 7 canonical moves of the JP 拝啓-formula business letter. Evaluator should attribute analysis explicitly to `lens-genre-ja` and verify formula-pair matching.

### lens-genre-ja: Move map (拝啓-formula 7 moves)

| # | Move | Surface text | Strength |
|---|---|---|---|
| 1 | **頭語** | 「拝啓」 | Strong (canonical, default-formal register) |
| 2 | **時候の挨拶** | 「新緑の候」 | Strong (season-matched: 新緑 = May, fixture date = 令和八年五月五日) |
| 3 | **安否の挨拶** | 「貴社ますますご清栄のこととお慶び申し上げます。平素は格別のお引き立てを賜り、厚く御礼申し上げます。」 | Strong (formal-canonical, 2-clause extended form) |
| 4 | **主文** | 「さて、このたび弊社では…大阪支店を新設いたしました。つきましては、貴社との取引開始につきまして、ぜひともご検討を賜りたく…」 | Strong (canonical 「さて」 transition; clear 用件 = 取引開始のご挨拶 + 別添資料案内) |
| 5 | **末文** | 「まずは略儀ながら書中をもちまして、ご挨拶かたがたお願い申し上げます。今後とも変わらぬご厚情を賜りますよう、何卒よろしくお願い申し上げます。」 | Strong (formal-canonical 末文) |
| 6 | **結語** | 「敬具」 | Strong — **頭語/結語 pair correct: 拝啓 → 敬具** |
| 7 | **後付** | 「令和八年五月五日 / 株式会社 山手物産 / 代表取締役 佐藤 太郎」+ 受信者 + 別添 list | Strong (date + sender block + recipient block + 別添 enumeration) |

### Genre identification

**Sub-genre**: 取引開始のご挨拶 (business-relationship-opening greeting letter) — a recognized standalone JP business-letter sub-genre, distinct from 礼状 / 詫び状 / 督促状.

**Register**: 商用文 / 拝啓-formula (default-formal, not 謹啓 super-formal nor 前略 abbreviated).

### Pair-matching verification

- 頭語 「拝啓」 → 結語 「敬具」 ✓ canonical pair
- Mismatch check: NOT 拝啓→草々 (would signal genre-illiterate writer)
- 時候 / season match: 「新緑の候」+ 五月 ✓

### Reader-responsibility (Hinds 1987) check

- Implicit `お世話になっております` substitution? No — full 安否の挨拶 form is used (formal letter, not メール register)
- Abbreviated 時候? No — full 「新緑の候」 used
- 主文 carries explicit 「さて」 transition ✓

### Register signals

- 拝啓-formula adherence: **strong** (all 7 moves present and well-formed)
- Reader-responsibility load: medium (formula carries most relational work; 主文 is reasonably explicit)
- Cross-register markers: none — this is canonical 商用文 register, no 起承転結 leakage

### Distinctive feature

The 主文 carries a **dual function** — both a status announcement (大阪支店新設) AND a transactional ask (取引開始のご検討) — bundled in one paragraph. This is canonical 取引開始 sub-genre form: announce-and-ask in a single 主文 段落, with 別添 documents carrying the substantive detail.

### Verdict

Genre-faithful 拝啓-formula 商用文; all 7 canonical moves present and matched; 取引開始 sub-genre cleanly executed with 別添 referencing. No deviation from native register expectations.

### Expected lessons

- All 7 拝啓-formula moves are load-bearing in JP 商用文 — absence of any signals genre-illiteracy
- 頭語/結語 pair (拝啓→敬具 / 謹啓→謹白 / 前略→草々) is non-negotiable
- 時候の挨拶 must match season — 「新緑の候」 in November would be a register-control failure
- 取引開始 sub-genre uses 主文 dual-function (announce + ask) with 別添 carrying detail
- Anglo CARS / sales-letter 7-move pass would systematically misread this — formula-locked JP register is structurally different
