# Fixture: JP DTC supplement landing page (synthetic-representative)

**Source**: synthetic-representative (composed by maintainer for evaluation purposes; modeled on 楽天市場 / 自社 D2C 定期購入 LP register conventions)
**Accessed**: 2026-05-05 (composed)
**Capture method**: synthetic representative — not a real artifact
**License**: maintainer-authored, freely usable for plugin evaluation
**Honesty flag**: This is NOT a real fetched artifact. It is a maintainer-composed text built to exhibit lens features cleanly (老舗 authority + 限定 scarcity + 建前/本音 layering + 婉曲 disclosure burial + 暖簾 credibility). Real-world JP DTC LPs vary in subtlety; eval results from this fixture are a smoke-test of `lens-persuasion-ja` application, not a benchmark of real-text deconstruction quality.
**Eval target**: `artifact-deconstruct` must enumerate ≥4 of Cialdini-7 with JP weighting, identify ≥3 of M1-M4 (建前/本音, 婉曲表現, 空気, 老舗/暖簾), flag at least one ⚫ dark-pattern (定期購入 / 婉曲 disclosure burial), and explicitly attribute analysis to `lens-persuasion-ja`.

---

## 【創業1887年】京都・老舗薬房がつくる、和漢サプリメント「養心丸」

### 京の暖簾、百三十余年。

明治二十年、京都の片隅で生まれた小さな薬房から、私たちの物語は始まりました。
四代にわたり、ご家族の健やかな毎日に寄り添ってまいります。

### 厚生労働省認可・GMP工場製造

東京大学医学部・佐藤一郎教授（栄養学）監修。伝統の和漢処方と現代の科学が出会いました。
ISO 9001 取得・国内自社工場にて、一粒一粒、丁寧に仕上げております。

### 累計販売 88万個突破。リピート率 92%。

「母の日にプレゼントしたら、とても喜ばれました」（東京都・60代女性）
「もう五年、毎朝欠かさず飲んでいます」（大阪府・70代男性）
すでに多くの皆様にご愛用いただいております。

### 【初回限定・特別価格】6,800円 → 980円（送料無料）

通常価格 6,800円のところ、初回限定価格 **980円**。
まずは「お試し」のお気持ちで、安心してお手にとっていただければ幸いに存じます。

### 数量限定 — 先着300名様

ご好評につき、毎月の数量に限りがございます。
売り切れ次第、終了とさせていただきます。お早めにお申し込みください。

### お客様の声に寄り添って

「皆様のお気持ちにお応えしたい」——四代目当主の願いを、商品に込めました。
日本の伝統を、これからも大切にしてまいります。

### お申し込みはこちらから

[今すぐ申し込む]

※本商品は、初回お届け後、2回目以降は自動的に「健康定期便コース」（月額 6,800円・送料込み）に移行いたします。
解約をご希望の場合は、次回お届け予定日の10日前までに、マイページよりお手続きいただきますようお願い申し上げます。場合によっては、お電話での確認が必要になることがございます。

---

## Annotations for evaluator

The fixture is constructed to surface multiple Cialdini-7 + JP-specific mechanisms + ⚫ dark-pattern (定期購入 with 婉曲 disclosure burial). Evaluator should attribute analysis explicitly to `lens-persuasion-ja`.

### lens-persuasion-ja: Cialdini-7 (JP weighting)

| Principle | Triggered? | How | Position |
|---|---|---|---|
| Reciprocity (返報性) | ✓ | 「初回限定 980円・送料無料」 — loss-leader-as-gift | 🟡 — bait for 6,800円 subscription |
| Commitment (一貫性) | ✓ | 申込→自動定期コース移行; staged commitment | ⚫ — micro-commitment funnels into roach motel |
| Social proof (社会的証明) | ✓ | 「累計88万個」+「リピート率 92%」+ 顧客の声 | 🟡 — numbers unverified |
| Authority (権威) | ✓✓✓ | 「創業1887年」+ 厚生労働省認可 + GMP + 東大医学部教授監修 + ISO 9001 — quintuple-stacked | 🟢 if verifiable; 🟡 if 教授 is paid undisclosed |
| Liking (好意) | ✓ | 「四代目当主の願い」「皆様のお気持ちに寄り添って」warmth + 創業者ストーリー | 🟢 |
| Scarcity (希少性) | ✓ | 「数量限定・先着300名様」+「売り切れ次第終了」 | 🟡 — verify whether "300名" rolls daily |
| Unity (一体性) | ✓ | 「日本の伝統」「京の暖簾」 — national + regional in-group | 🟢 weak |

### lens-persuasion-ja: JP-specific mechanisms (M1-M4)

| Mechanism | Triggered? | How | Position |
|---|---|---|---|
| **M1 建前/本音** | ✓ | tatemae 「お試しのお気持ちで安心して」/ honne 自動定期コースへの誘導 | 🔴 — gap between surface invitation and friction reality |
| **M2 婉曲表現** | ✓✓ | 「場合によっては、お電話での確認が必要になることがございます」「お早めにお申し込みください」「特別価格 → 980円」 — 解約条件 buried in 米印 footnote with cushion words | ⚫ — material disclosure deliberately softened |
| **M3 空気を読む** | △ | 「皆様にご愛用いただいております」implicit consensus | 🟡 |
| **M4 老舗/暖簾** | ✓✓✓ | 「創業1887年」+「四代目当主」+「京の暖簾」+「明治二十年から」+ 京都という場所性 — institutional-longevity authority is primary vector | 🟢 if literal; 🔴 if 薬房 is dormant/unrelated entity |

### Brignull dark-pattern check (JP-translation-aware)

| Pattern | Detected? | Note |
|---|---|---|
| Forced Continuity | ✓ | 「2回目以降、自動的に定期コース」 — classic ⚫ |
| Roach Motel | likely ✓ | 「お電話での確認が必要になることがございます」buries friction; 解約導線 is JP regulatory surface (特定商取引法 2022/2024) → ⚫ |
| Hidden Costs | ✓ | 6,800円/月 actual price buried in 米印 footnote |
| 申し訳なさそうな圧 (JP-specific) | ✓ | 「お早めに」「お手続きいただきますようお願い申し上げます」— politeness register weaponized as friction |

### Verdict

⚫ **Dark pattern in subscription / disclosure flow** despite 🟢 legitimate institutional authority (創業1887年 + GMP + 厚労省 + ISO stack is real authority on JP register). The problem is the **建前/本音 gap** between surface invitation ("お試しのお気持ちで") and 定期購入 commitment, and the 婉曲表現 burial of the material 6,800円/月 disclosure in 米印 footnote. Regulatory risk: 特定商取引法 (定期購入規制) + 景品表示法 優良誤認.

### Ethical position

⚫ **Overall**: 5 Cialdini principles transparent, 2 in gray zones, 2 dark patterns + 2 JP-specific mechanism issues (M1 + M2). The 老舗/暖簾 authority is the ONE legitimately 🟢 element; everything else degrades it.

### Expected lessons

- 老舗/暖簾 authority is structurally legitimate in JP register, not "manufactured authority"
- 建前/本音 layering must be checked separately; surface analysis catches half the persuasion
- 婉曲表現 in 米印 footnote = ⚫ when burying material disclosure; 🟢 elsewhere
- Anglo Cialdini pass would under-detect M4 老舗/暖簾 + M1 tatemae/honne + M2 婉曲 burial
- 申し訳なさそうな圧 is a JP-register-specific dark pattern (politeness as friction vector)
