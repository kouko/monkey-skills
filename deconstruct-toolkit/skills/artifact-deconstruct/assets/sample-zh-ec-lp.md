# Fixture: TW 蝦皮 / momo style 老字號 食品 LP (synthetic-representative)

**Source**: synthetic-representative (composed by maintainer for evaluation purposes; modeled on 蝦皮商城 / momo / TW 老字號食品 e-commerce LP register conventions, ca. 2024)
**Accessed**: 2026-05-05 (composed)
**Capture method**: synthetic representative — not a real artifact
**License**: maintainer-authored, freely usable for plugin evaluation
**Honesty flag**: This is NOT a real fetched artifact. It is a maintainer-composed text built to exhibit lens features cleanly (老字號 authority + 關係 + 面子 + 自己人 in-group + 道德綁架 dark pattern). Real-world TW e-commerce LPs vary in directness; eval results from this fixture are a smoke-test of `lens-persuasion-zh` application, not a benchmark of real-text deconstruction quality.
**Eval target**: `artifact-deconstruct` must enumerate ≥4 of Cialdini-7 with ZH weighting, identify ≥3 ZH-specific mechanisms (面子 / 關係 / 人情 / 自己人 / 道德綁架), flag ≥1 🔴 manipulation move, name the register variant (zh-TW), and explicitly attribute analysis to `lens-persuasion-zh`.

---

## 【限時搶購】百年老字號永和阿婆豆漿粉

### 創立於民國十二年，第四代傳人親自監製

從阿祖手中接過石磨的那一刻起，我們就知道——
這碗豆漿，不只是早餐，更是一家人的記憶。

百年老字號，創立於民國十二年（西元 1923 年）。
四代傳承，永和在地人從小喝到大的私房早餐。

### 名醫推薦・衛福部食品認證・ISO 22000 通過

榮獲衛生福利部食品安全認證（食字第 11500001 號）；
台大醫學院營養學科 林志明 教授專業推薦；
ISO 22000 / HACCP 雙認證國內自有工廠生產。

### 自己人才知道的好物

「在地人才知道的私房早餐，現在你也能買到。」
不是觀光客買的東西，是永和阿嬤從小煮給孫子喝的那一杯。
我們家三代都喝這個——你也是吃這家長大的吧？

### 老主顧 VIP 限時 7 折・今天是最後一天

上次跟您介紹的客戶都覺得讚——這次特別給您開放：
- 通常一包 NT$ 380
- 老主顧 VIP 限時價 NT$ 266（7 折）
- **今天是最後一天**，明天恢復原價

點擊立即加入購物車。

### 28,367 個家庭加入會員，全家大小都愛喝

蝦皮商城評分 4.9 / 5.0（累計 12,453 則五星評論）；
連續五年榮獲「TW 早餐最愛品牌」票選第一名。
全家人都喝得安心，孝敬長輩、餵飽小孩，一包搞定。

### 給阿嬤一個面子吧

阿嬤辛苦了一輩子，把這份手藝傳下來——
不買就是對不起阿嬤的好意。
給個面子，先試一包，自己人不收這個錢的價。

[立即下單　NT$ 266]

---

## Annotations for evaluator

The fixture exhibits a high-pressure TW e-commerce LP register stacking authority + collective-social-proof + 自己人 in-group + 道德綁架 + manufactured face-stakes. Evaluator should attribute analysis explicitly to `lens-persuasion-zh` and identify register as zh-TW.

### lens-persuasion-zh: Cialdini-7 (ZH weighting)

| Principle | Triggered? | How (ZH-specific manifestation) | Position |
|---|---|---|---|
| #1 Reciprocity (→ 人情) | ✓ | 「上次跟您介紹的客戶都覺得讚」— 人情 ledger invocation; 「先試一包」 | 🟡 Gray (relational debt frame, customer unaware of script) |
| #2 Commitment (face-amplified) | ✓ | 「老主顧 VIP」— prior-commitment recall + face stakes | 🟡 if user is not actually 老主顧 |
| #3 Social proof (collectivist) | ✓✓ | 「28,367 個家庭」+「我們家三代都喝這個」+「全家大小都愛喝」+「TW 早餐最愛品牌」+ 蝦皮 4.9/5.0 — collective + family-unit + ranking stacked | 🟢 if numbers verifiable |
| #4 Authority (老字號 + PD≈58) | ✓✓✓ | 老字號 + 創立於民國十二年 + 第四代傳人 + 衛福部認證 + 台大教授推薦 + ISO 22000 + HACCP — 7-stack | 🟢 if all verifiable; 🟡 if "教授推薦" is paid endorsement undisclosed |
| #5 Liking (→ 關係) | ✓ | 「在地人才知道」+「老主顧」+「自己人」+「永和阿嬤」 — 自己人 + long-relationship + 在地 frame | 🟡 Gray (parasocial 自己人 frame on a 大眾 commerce platform) |
| #6 Scarcity (+ face-loss layer) | ✓ | 限時搶購 + 今天是最後一天 + 7 折; missing-out frame | 🔴 Manipulation if deadline is rolling/fake |
| #7 Unity (→ 自己人/外人) | ✓✓ | 「在地人才知道」+「不是觀光客買的」+「我們家三代」+「全家大小」 — 自己人 / 在地 / 家庭單位 stacked, explicit 外人 (觀光客) exclusion | 🟢 if register-authentic |

### lens-persuasion-zh: ZH-specific mechanisms

| Mechanism | Triggered? | How | Position |
|---|---|---|---|
| **面子 (mianzi)** | ✓✓ | 「給阿嬤一個面子吧」「給個面子」— explicit face-request, manufactured face-stakes | 🔴 Manipulation — engineered face-stakes for a transactional purchase |
| **關係 (guanxi)** | ✓ | 「老主顧」+「上次介紹的客戶」+「自己人不收這個錢的價」 — invoked relational tie | 🟡 Gray (parasocial 關係 on commerce platform; user is not actual 老主顧) |
| **人情 (renqing)** | ✓ | 「上次跟您介紹的客戶都覺得讚」— implicit 人情 ledger | 🟡 Gray |
| **自己人 / 外人** | ✓✓ | 「在地人才知道」+「不是觀光客買的」 — explicit 自己人/外人 binary | 🟡 if parasocial; 🟢 if register-authentic |
| **道德綁架** | ✓✓ | 「不買就是對不起阿嬤的好意」「阿嬤辛苦了一輩子」 — moral framing for trivial purchase, invoking 孝順 / 對得起 register | 🔴 Manipulation — moral-kidnapping inappropriate to commercial transaction |

### Brignull dark-pattern check (ZH register)

| Pattern | Detected? | Note |
|---|---|---|
| 限時 fake deadline | ✓ likely | 「今天是最後一天」 commonly rolling on TW e-commerce → 🔴 |
| 道德綁架 (ZH-specific #13) | ✓ | 「不買就是對不起阿嬤」 → 🔴 |
| 假關係 (ZH-specific #15) | borderline | 「老主顧」 may not actually apply to all targeted users → 🟡 to 🔴 |
| Hidden Costs | ✗ | not in this excerpt |
| Forced Continuity | ✗ | not a subscription |

### Verdict

🔴 **Manipulation-leaning** — high authority + Unity stacking is **transparent and culturally appropriate** for ZH consumer register, but:

1. 「給阿嬤一個面子吧」 weaponizes 面子 for a low-stakes purchase (engineered face-stakes)
2. 「不買就是對不起阿嬤的好意」 is 道德綁架 — moral framing inappropriate to commercial transaction
3. 「今天是最後一天」 + 「明天恢復原價」 needs verification; if rolling, this is Brignull fake-deadline → 🔴
4. 「老主顧 VIP」 + 「自己人不收這個錢的價」 frame is 假關係 if applied indiscriminately

If 老字號 stack is real and deadline is real, downgrades to 🟡 gray-zone with 道德綁架 line still 🔴.

**Overall: 🔴** — 4 principles transparent, 3 in gray zone, 2 ZH-specific mechanisms in 🔴 manipulation territory; register variant: **zh-TW**.

### Expected lessons

- 老字號 + 衛福部 + 教授推薦 stack is legitimate ZH-register authority (PD≈58 amplifies)
- 關係 ≠ Cialdini Liking — it is structural multi-year tie, mark it separately
- 道德綁架 is ZH-specific dark pattern (#13) — moral-identity invocation, not Brignull confirmshaming
- 面子 weaponized for trivial purchase = 🔴 (engineered face-stakes)
- Anglo Cialdini-anglo pass would under-detect 面子 / 關係 / 人情 / 自己人 / 道德綁架 — apply zh variant
