# Lens: Persuasion Analysis (Chinese register — Cialdini + ZH cultural variants)

> **Sources**:
> - Robert Cialdini, *Influence: The Psychology of Persuasion*, New and Expanded edition (Harper Business, 2021). The 7 principles (Reciprocity / Commitment & Consistency / Social Proof / Authority / Liking / Scarcity / Unity). The 1984 first edition's empirical base is overwhelmingly US-WEIRD; cross-cultural extension is post-hoc.
> - Hwang Kwang-Kuo (黃光國), "Face and Favor: The Chinese Power Game," *American Journal of Sociology* 92(4): 944–974, 1987. Canonical sociological model of the **face-and-favor** system: distinguishes 情感性關係 (expressive ties) / 工具性關係 (instrumental ties) / 混合性關係 (mixed ties), each governed by a different allocation rule (need-rule / equity-rule / 人情 renqing-rule). KEY primary source for ZH persuasion.
> - Hu Hsien-chin (胡先縉), "The Chinese Concept of 'Face,'" *American Anthropologist* 46(1): 45–64, 1944. Original distinction between **面子** (mianzi — public dignity tied to social status / accomplishment) and **臉** (lian — moral character / integrity). Hwang 1987 builds on this.
> - Geert Hofstede, *Culture's Consequences* (Sage, 1980 / expanded 2001) + hofstede-insights.com country profile. China dimensions: power-distance ≈ 80 (very high), individualism ≈ 20 (very collectivist), uncertainty-avoidance ≈ 30 (low), long-term-orientation ≈ 87 (very high). Taiwan profile shifts (PD ≈ 58, IDV ≈ 17, UAI ≈ 69, LTO ≈ 93) — the variant register matters.

> **Synthesis note**: This file combines (a) Cialdini's 7 principles (1984/2021) for the universal-type catalog, (b) Hwang K-K.'s face-and-favor framework (1987) for the ZH-specific **mechanisms not in Cialdini**, and (c) Hofstede CN/TW dimension data for **weighting differences** between the WEIRD-sample baseline and the ZH register. Cialdini and Hwang did not co-publish; Hwang explicitly developed the ZH model **as a parallel sociological framework**, not as an extension of Cialdini. Combining them is a methodological choice by `deconstruct-toolkit`: Cialdini gives us the cross-cultural-comparable scaffold; Hwang gives us the structurally-distinct mechanisms (關係 / 人情 / 面子) that have no clean Cialdini analogue. This combination disclosure is mandatory per [ADR-0003](../../../docs/adr/0003-lens-synthesis-disclosure.md).

> **Cultural-register statement**: This variant grounds in **Chinese-language artifacts** across zh-TW (Taiwan) / zh-HK (Hong Kong) / zh-CN (Mainland) registers. Within the variant, register-level differences exist (TW: lower PD, more individualist drift since 1990s democratization; HK: post-1997 register hybrid; PRC: high PD, post-2010 nationalist Unity register amplification) — these are flagged inline. The default reference register is **zh-TW academic / business / consumer** because this is the maintainer's competence per ADR-0004.

---

## When to apply this lens

- ZH marketing copy, advertising, sales pages (蝦皮 / momo / 淘寶 / 天貓 / Lazada landing pages)
- ZH B2B sales pitches and business proposals (where 關係 is half the work)
- ZH political speeches / 政令宣導 (especially Mainland CCP register / Taiwan election register — face dynamics differ)
- Insurance / wealth-management / 直銷 (MLM) sales scripts — heavy 關係 + 人情 mobilization
- 政府公文 with persuasive intent (公告 / 通知 with action-forcing language)
- Social media KOL marketing in ZH register (小紅書 / 抖音 / Threads-TW)

## When NOT to apply

- Pure technical documentation in ZH (use lens-genre-zh instead)
- Literary / poetic ZH (use lens-rhetoric-zh — 文心雕龍 register, not Cialdini)
- Academic ZH papers (use lens-genre-zh)
- Personal correspondence / 私信
- ZH translations of Anglo-original copy — apply both `-anglo` and `-zh` and compare register drift

---

## Cultural-register weight calibration vs Anglo

Cialdini's WEIRD-sample weightings shift in the ZH register. Approximate **directional adjustments** (not precise effect sizes — these are scoring heuristics, not empirical measurements):

| Cialdini principle | Anglo (WEIRD baseline) | ZH (zh-TW / zh-CN) | Why the shift |
|---|---|---|---|
| #1 Reciprocity | transaction-bounded | **expanded into 人情 ledger** — multi-year, relational, accumulating | Hwang 1987: 人情 is the currency of 混合性關係 (mixed ties); obligations carry forward across years, are tracked, and "calling in 人情" is a social act |
| #2 Commitment | individual self-consistency | **face-bound public commitment** — 承諾 with face implications | Public 承諾 ties personal 面子; breaking public commitment causes 丟臉 (face-loss) — stakes higher than Anglo cognitive-dissonance |
| #3 Social proof | weight ↑ vs WEIRD | **weight ↑↑** — collective social proof potent | Hofstede CN IDV ≈ 20; 大家都 ("everyone") and 群眾 ("the crowd") frames operate strongly. CN > TW > Anglo |
| #4 Authority | weight ↑ via PD ≈ 40 in US | **weight ↑↑↑** — PD ≈ 80 (CN) / 58 (TW); 老字號 (lao zihao, established brand) + age-hierarchy + title amplify | Power-distance dominant; 長輩 / 老師 / 醫師 / 老闆 register carries automatic deference weight Anglo lacks |
| #5 Liking | individual rapport | **largely replaced by 關係 (guanxi)** — pre-existing structural tie predicts persuasion success more than instant rapport | Hwang 1987: relational tie is structural, not affective. Cold-call rapport-building is **less effective** than 引介 (warm intro through shared 關係) |
| #6 Scarcity | classic loss-aversion | **similar mechanism + face-loss interaction** — 限量 / 絕版 work; but missing the chance carries face-loss layer ("買不到的人會被笑") | Brignull-style fake countdowns work; additional ZH-specific layer of face-loss compounds urgency |
| #7 Unity | identity-based weight ↑ in WEIRD-with-tribal-marker | **weight ↑↑** — 自己人 (zijiren, in-group) vs 外人 (wairen, outsider) is an explicit binary in ZH social structure | Markers: 同鄉 / 校友 / 同事 / 同行 / 同胞 (compatriot — politically loaded in CN/TW). Activates 內團體偏好 (in-group preference) |

**Note**: TW post-1990s democratization shifted IDV slightly upward and PD slightly down vs PRC. Treat **PRC artifacts** as higher-PD / higher-collectivism than **TW artifacts**; HK is a hybrid that drifted post-1997.

---

## Part 1: Cialdini's 7 Principles — ZH manifestation table

For each principle, check **if** and **how** the artifact triggers it in **ZH-register-specific** form, then assign an **ethical position** (see Part 4).

### 1. Reciprocity — 人情 (renqing) variant

Anglo manifestation: free trial / sample / lead magnet — **single-transaction**.

ZH manifestation: 人情 ledger — **multi-transaction, relational, accumulating across years**.

- 「上次幫您處理過 X，這次……」 (last time I helped you with X, this time...) — explicit 人情 invocation
- 「我跟你爸是老朋友」 (I'm your father's old friend) — relational debt across generations
- 「不收紅包不好意思」 (it would be embarrassing not to accept the gift) — face-saving accept
- 贈禮 / 送禮文化 — gift-giving creates 人情 debt that *is the persuasion mechanism*, not preamble to it
- 「先試用，不喜歡再說」 (try it first, decide later) — Anglo-style free trial; **less weighted in ZH** unless paired with relational frame

Detection signals: explicit relational invocations; gift mentions; 「上次」/「之前」 references that anchor obligation; 紅包 / 茶水費 framing in business contexts.

### 2. Commitment & Consistency — 承諾 + face variant

Anglo manifestation: foot-in-the-door, public pledge, identity claim.

ZH manifestation: same mechanism but **face-amplified**.

- 「您剛才不是說……」 (didn't you just say...) — public commitment recall, face stakes
- 「答應的事情就要做到」 (promised things must be done) — moral framing of consistency
- 公開 / 當眾承諾 — public commitment carries 面子 weight far beyond Anglo cognitive-dissonance
- 「您這樣的人格不會……」 (someone of your character wouldn't...) — character-frame appeal (links to 臉, moral-character face)

Detection signals: public/witnessed commitment language; character / personhood framing; appeals to 信用 / 誠信.

### 3. Social Proof — 大家都 collectivist variant

Anglo manifestation: testimonial wall, "10,000+ users."

ZH manifestation: **collective frame > individual testimonial** in default register.

- 「大家都在用」 (everyone is using it) — generic-collective frame; **more potent than individual case** in ZH
- 「全家人都喜歡」 (the whole family loves it) — family-unit social proof, distinctly ZH
- 排隊 / 排很久 / 一位難求 — queue-as-proof; visible scarcity-of-access doubles as social proof
- 「網路評價超過五萬則」 / 「淘寶銷量第一」 — quantitative crowd-claim, weighted heavily
- KOL / 網紅推薦 — single-person endorsement weighted **lower than crowd** unless KOL has structural authority (老師 / 醫師 register)

Detection signals: 大家 / 全部 / 各位 / 全家 framings; queue references; aggregate sales/review numbers; family-unit invocations.

### 4. Authority — 老字號 + age-hierarchy variant

Anglo manifestation: PhD / MBA / "as featured in" / institutional logos.

ZH manifestation: **PD ≈ 80 amplifies; multiple amplifying signals stack**.

- 老字號 / 百年老店 / 創立於 XXXX 年 — establishment-age as authority (long-term-orientation LTO ≈ 87 weight)
- 老師 / 醫師 / 教授 / 院士 / 主任 — title-prefix register (much heavier than Anglo "Dr.")
- 政府認證 / 國家級 / 部頒 — state-authority appeal (CN > TW; in TW, this register is weaker post-democratization)
- 長輩推薦 / 阿嬤都用 — age-hierarchy authority (grandma/elder endorsement)
- 名人 / 名醫 / 名師 — fame + expertise stack
- ISO / GMP / HACCP / 中華民國 X 字號 — institutional certification stamps

Detection signals: establishment year prominent; title-stacking; institutional/state seals; age-hierarchy invocations.

### 5. Liking — 關係 (guanxi) replacement

Anglo manifestation: similarity claim, founder origin story, relatable narrator.

ZH manifestation: **largely replaced by 關係** — pre-existing structural tie operates as persuasion currency.

- 「我朋友介紹的」 (my friend introduced me) — warm-intro frame; **the intro itself is the persuasion**
- 「我們是 XX 同學」 / 「同鄉」 / 「同事」 — shared-network-tie invocation
- 「您表哥認識我老闆」 — 2nd-degree connection mapping
- 引介 (yinjie) — formal warm-intro practice; cold approach is structurally weaker
- 「老主顧」/「老客戶」 — long-term-relationship privilege framing

Detection signals: explicit network mapping; 引介 / 介紹 references; shared-affiliation claims; long-relationship framing. **Critical pitfall**: do not flatten 關係 into Anglo "liking" — see Part 5 pitfalls.

### 6. Scarcity — 限量 + face-loss variant

Anglo manifestation: countdown timer, "only 3 left," limited edition.

ZH manifestation: **same mechanism + face-loss compound**.

- 限量 / 絕版 / 限時 — direct equivalent
- 「買不到」/ 「搶不到」 — getting-shut-out frame; face-loss layer ("我朋友都買到了我沒買到")
- 名額有限 / 內部優惠 / VIP only — scarcity-of-access framing, doubles as in-group signal (links to Unity)
- 「過了今天沒有」 / 「截止」 — time-bounded urgency
- 「最後 3 組」/「再不下單就沒了」 — quantitative + temporal stack

Detection signals: limit framing; "miss-out" language; in-group exclusive access (Unity overlap).

### 7. Unity — 自己人 / 同胞 variant

Anglo manifestation: "we" framing, shared-identity invocation, tribal markers.

ZH manifestation: **explicit 自己人 (zijiren) vs 外人 (wairen) binary** — structurally distinct from Anglo loose tribal markers.

- 自己人 / 我們的人 — explicit in-group claim; binary frame
- 同胞 / 同鄉 / 同行 / 校友 / 戰友 — shared-affiliation tribal markers
- 「我們華人」/「我們中國人」/「我們台灣人」 — ethnic / national in-group (politically loaded — register-sensitive)
- 「在地人才知道」 / 「自己人才有的優惠」 — insider-access frame
- 「你也是吃這家長大的吧」 — generational-shared-experience frame

Detection signals: 自己人 / 我們 explicit framing; shared-place / shared-school / shared-generation invocations; ethnic-national-political register markers (handle with care — high political sensitivity in TW vs CN).

---

## Part 2: ZH-specific mechanisms not in Cialdini

These are mechanisms documented in Hwang K-K. (1987) and the broader ZH cultural-psychology literature that **do not have a clean Cialdini analogue**. They warrant their own detection slots.

### 面子 (mianzi) — face-giving / face-saving

Per Hu 1944 + Hwang 1987: **mianzi** = public dignity tied to social status / accomplishment. (Distinct from **臉** lian = moral character / integrity, which is more like Cialdini's character-frame in #2.)

**Persuasion uses**:
- 給面子 (give face) — accepting an offer because rejecting would cause **the seller** face-loss; this is *reciprocity-paid-in-acceptance*
- 留面子 (save face) — soft language allows graceful decline; absence of soft-decline language is a pressure tactic
- 不好意思拒絕 — sociocultural friction against direct refusal, exploited by sales scripts that force commitment moments
- 「給我個面子」 (give me face) — explicit face-request for a favor
- 「在大家面前不要拒絕我」 — public face-stakes weaponization

Surface signals: 面子 / 給面子 / 留面子 / 丟臉 / 不好意思 / 給點面子吧 explicit; soft-decline language absent at decision points.

Ethical position: **🟡 gray zone** when used softly; **🔴 manipulation** when face-stakes are manufactured (e.g., engineered public moment forcing acceptance); **⚫ dark pattern** when paired with confirmshaming-equivalent.

### 關係 (guanxi) — relational pre-existing-tie persuasion currency

Per Hwang 1987: 關係 is **structural** (a tie that exists between persons) not **affective** (a feeling of liking). Hwang's typology: 情感性 / 工具性 / 混合性 ties, each with a different reciprocity rule.

**Persuasion uses** (beyond what's already in Cialdini #5):
- Warm-intro framing as the **primary** persuasion vector (cold approach is structurally weaker)
- Network-mapping in copy ("您朋友 X 也是我的客戶")
- 拉關係 (pulling guanxi) — actively constructing or invoking shared ties
- 走後門 — using guanxi to bypass formal channels (NB: ethically gray; in PRC pre-2013 normalized; post-anticorruption-campaign more sensitive)

Surface signals: explicit network maps; introduction names dropped; shared-affiliation invocations as door-opener (not as similarity-rapport).

Ethical position: **🟢 transparent** in B2B warm-intro; **🟡 gray zone** when network-name-dropping is unverified; **🔴** when fabricated network claimed.

### 人情 (renqing) — multi-transaction obligation ledger

Per Hwang 1987: **人情** is the operating currency of 混合性關係 (mixed ties). Distinct from Cialdini reciprocity in three ways:

1. **Multi-transaction**: obligations accrue and are tracked across years
2. **Asymmetric**: 人情 owed to a higher-status person carries more weight
3. **Public**: 人情 ledgers are partially observable to a shared social network

**Persuasion uses**:
- 「上次的人情這次還」 — explicit ledger invocation
- 「您欠我一個人情」 — debt-call (acceptable between mixed-ties; offensive between expressive-ties)
- 「賣我個人情」 — face + 人情 stack request
- Repeated favor-giving as persuasion-investment (the favors *are* the persuasion campaign)

Surface signals: temporal references to past favors; 人情 / 還人情 / 欠人情 explicit; asymmetric favor patterns visible across multiple interactions.

Ethical position: **🟢 transparent** in stable mixed-ties; **🟡** when ledger is one-sidedly fabricated; **🔴** when 人情 is engineered specifically to extract commitment (sales-bait gifts that demand reciprocation).

### 自己人 vs 外人 (zijiren vs wairen) — in-group/outsider binary

Related to Cialdini's Unity #7 but **structurally distinct**: ZH culture marks the in-group/outsider boundary explicitly and binary, where Anglo Unity operates as graded similarity.

**Persuasion uses**:
- 「自己人不收這個錢」 — in-group exempts standard-transaction frame
- 「外人才照定價」 — outsider explicitly priced higher
- 「都是自己人，講這些幹嘛」 — in-group invoked to bypass scrutiny
- KOL / 網紅 building 自己人 frame with audience to neutralize critical distance

Surface signals: 自己人 / 外人 / 我們的人 / 你們那邊的人 explicit binary framing; differential pricing or treatment language; "no need to be polite" register-shift.

Ethical position: **🟢** when authentic in-group transaction; **🟡** when 自己人 frame is parasocial illusion (e.g., influencer marketing); **🔴** when 自己人 frame neutralizes legitimate scrutiny.

### 禮 (li) — ritual propriety as authority mechanism (optional / lower frequency)

Confucian register: ritual propriety as soft-authority. Less common in modern marketing; more present in formal business / political registers.

Surface signals: 失禮 / 禮數 / 禮節 / 拜訪 / 致意 register; structured-ritual gift exchange.

---

## Part 3: Brignull dark patterns — ZH register equivalents

Most Brignull patterns translate directly. Key adaptations + ZH-specific additions:

| # | Pattern | ZH register notes |
|---|---|---|
| 1 | Confirmshaming | ZH adds 「不好意思」 register exploitation; "我是不是太麻煩您了" guilt-baits |
| 2 | Roach Motel | Common; 退訂 / 取消 流程 hidden — direct translation |
| 3 | Privacy Zuckering | 個資 over-collection; LINE / WeChat 加好友 friction |
| 4 | Misdirection | Same |
| 5 | Hidden Costs | 運費 / 手續費 / 信用卡分期費 surprises common |
| 6 | Forced Continuity | 自動續訂 — direct translation |
| 7 | Bait and Switch | Same |
| 8 | Trick Questions | Less common in ZH (double-negatives less natural); but **複雜公文體** can function similarly |
| 9 | Sneak into Basket | 加購 default-checked — direct translation |
| 10 | Disguised Ads | 業配 / 葉佩雯 (industry slang for sponsored content) — direct translation; FTC-equivalent: TW NCC / CN 廣告法 |
| 11 | Friend Spam | 邀請好友 注册 領紅包 — direct translation |
| 12 | Price Comparison Prevention | Same |

### ZH-specific dark patterns (additions to Brignull)

**13. 道德綁架 (moral kidnapping / guilt-leverage)** — coercion via moral framing:
- 「不買就是不愛家人」 — moral framing of purchase
- 「不捐就是沒良心」 — moral pressure on giving
- 直銷 (MLM) heavy users; insurance sales scripts
- Distinct from Brignull confirmshaming because it invokes **moral identity** not just convenience-shame
- Position: **🔴 manipulation** to **⚫ dark pattern**

**14. 話術 (huashu / fast-talk script patterns)** — structured high-pressure scripts particular to TW/PRC sales register:
- Insurance / 直銷 / 房仲 (real estate) script genres with documented manipulation patterns
- Often combine 7+ Cialdini triggers in 30-second window
- Includes 「假對比」(fake comparison), 「假期限」(fake deadline), 「假權威」(fake authority)
- Position: **🔴 manipulation** baseline; **⚫** when scripted at scale

**15. 假關係 (fabricated guanxi)** — claiming non-existent network ties:
- 「我跟你老闆很熟」 (I know your boss well) when not true
- Network-claim pre-emption that the target is socially-pressured not to verify
- Position: **⚫ dark pattern** — exploits the structural authority of 關係

---

## Part 4: Ethical Position Verdict (mandatory)

Same 4-position scale as Anglo variant — what differs is **what triggers warrant which position** in ZH register:

| Position | Definition | ZH-register example |
|---|---|---|
| 🟢 **Transparent persuasion** | Mechanism used + audience can see and reject | 老字號 + 創立年份 + 銷售數據 公開可查 |
| 🟡 **Gray zone** | Mechanism used + audience unaware | 引介 frame where the introducer is paid commission undisclosed |
| 🔴 **Manipulation** | Creates urgency / false belief / moral pressure | 道德綁架; 假人情 (engineered favor-debt); fake 限量 |
| ⚫ **Dark pattern** | Actively deceives, harms user | 假關係; 話術 scripts at scale; 強制續訂 |

**Rule**: Every detected mechanism gets a position. Both **Cialdini-7-ZH** and **ZH-specific mechanisms** get positions.

---

## Worked example: 蝦皮 / momo TW landing page (synthetic-representative; zh-TW register)

**Artifact (5-7 sentences)**:

> 【限時搶購】百年老字號永和阿婆豆漿粉，創立於 1923 年，現由第四代傳人親自監製。
> 「我們家三代都喝這個」——在地人才知道的私房早餐，現在你也能買到。
> 名醫推薦、衛福部食品認證、ISO 22000 通過。
> 「上次跟您介紹的客戶都覺得讚」——老主顧 VIP 限時 7 折，今天是最後一天。
> 已經有 28,367 個家庭加入會員，全家大小都愛喝。
> 不買就是對不起阿嬤的好意，給個面子試一包吧！
> 點擊立即下單。

### Cialdini-7 (ZH weighting)

| Principle | Triggered? | How | Position |
|---|---|---|---|
| #1 Reciprocity | ✓ | 「上次跟您介紹的客戶」— 人情 ledger invocation | 🟡 Gray (relational debt frame, customer unaware of script) |
| #2 Commitment | ✓ | 「老主顧 VIP」— prior-commitment recall | 🟢 Transparent if user is actually a 老主顧 |
| #3 Social proof | ✓ | 「28,367 個家庭」+ 「我們家三代都喝這個」+ 「全家大小都愛喝」 — collective + family-unit stacked | 🟢 Transparent if numbers verifiable |
| #4 Authority | ✓✓✓ | 老字號 + 創立於 1923 + 第四代傳人 + 名醫推薦 + 衛福部認證 + ISO 22000 — 6-stack | 🟢 if all verifiable; 🟡 if "名醫" is unnamed |
| #5 Liking (→ 關係) | ✓ | 「在地人才知道」+「老主顧」 — 自己人 + long-relationship frame | 🟡 Gray (parasocial 自己人 frame) |
| #6 Scarcity | ✓ | 限時搶購 + 今天是最後一天 + 7 折 | 🔴 Manipulation if deadline is rolling/fake |
| #7 Unity | ✓ | 「在地人」+「我們家三代」+ 「全家大小」 — 自己人 / 在地 / 家庭單位 stacked | 🟢 if authentic register |

### ZH-specific mechanisms

| Mechanism | Triggered? | How | Position |
|---|---|---|---|
| 面子 (mianzi) | ✓ | 「給個面子試一包吧」— explicit face-request | 🔴 Manipulation — engineered face-stakes for a transactional purchase |
| 關係 (guanxi) | ✓ | 「老主顧」+「上次介紹的客戶」 — invoked relational tie | 🟡 Gray if customer is not actually 老主顧 |
| 人情 (renqing) | ✓ | 「上次跟您介紹的客戶」 — implicit 人情 ledger | 🟡 Gray |
| 自己人 / 外人 | ✓ | 「在地人才知道」 — in-group frame | 🟢 if register-authentic |
| 道德綁架 | ✓✓ | 「不買就是對不起阿嬤的好意」 — moral guilt framing | 🔴 Manipulation — moral framing for trivial purchase |

### Dark-pattern check (ZH register)

| Pattern | Detected? | Note |
|---|---|---|
| 限時 fake deadline | ✓ likely | 「今天是最後一天」 commonly rolling; needs verification → 🔴 |
| 道德綁架 | ✓ | Moral kidnapping via 阿嬤好意 frame → 🔴 |
| 假關係 | ⚠️ borderline | 「老主顧」 may not actually apply to this user → 🟡 to 🔴 |
| Hidden costs | ✗ | Not visible in this excerpt |
| Forced continuity | ✗ | Not a subscription |

### Verdict

**🔴 Manipulation-leaning** — high authority + Unity stacking is **transparent and culturally appropriate** for ZH consumer register, but:
1. 「給個面子試一包吧」 weaponizes 面子 for a low-stakes purchase (engineered face-stakes)
2. 「不買就是對不起阿嬤的好意」 is 道德綁架 — moral framing inappropriate to commercial transaction
3. 「今天是最後一天」 needs verification; if rolling, this is a Brignull fake-deadline → 🔴
4. 「老主顧 VIP」 frame may be 假關係 if applied indiscriminately

If the deadline is real and 老主顧 is targeted accurately, downgrades to **🟡 gray-zone** with the moral-kidnapping line still flagged 🔴.

Overall: **🔴 — 4 principles transparent, 3 in gray zone, 2 ZH-specific mechanisms in 🔴 manipulation territory.**

---

## Part 5: Output format template

```markdown
### Cialdini-7 (ZH weighting)
| Principle | Triggered? | How (ZH-specific manifestation) | Position |
|---|---|---|---|
| #1 Reciprocity (→ 人情) | ✓/✗ | <description> | 🟢/🟡/🔴/⚫ |
| #2 Commitment (face-amplified) | ... | ... | ... |
| #3 Social proof (collectivist) | ... | ... | ... |
| #4 Authority (老字號 + PD≈80) | ... | ... | ... |
| #5 Liking (→ 關係) | ... | ... | ... |
| #6 Scarcity (+ face-loss layer) | ... | ... | ... |
| #7 Unity (→ 自己人/外人) | ... | ... | ... |

### ZH-specific mechanisms
| Mechanism | Triggered? | How | Position |
|---|---|---|---|
| 面子 (mianzi) | ... | ... | ... |
| 關係 (guanxi) | ... | ... | ... |
| 人情 (renqing) | ... | ... | ... |
| 自己人 / 外人 | ... | ... | ... |
| 禮 (li) | ... (optional) | ... | ... |

### Dark-pattern check (ZH register)
| Pattern | Detected? | Note |
|---|---|---|
| (Brignull 1-12) | ... | ... |
| 道德綁架 | ... | ... |
| 話術 | ... | ... |
| 假關係 | ... | ... |

### Verdict
<one paragraph synthesizing across Cialdini-7-ZH + ZH-specific + dark patterns>
```

End with 1-line ethical position: "Overall: **🟢/🟡/🔴/⚫** — **N** principles transparent, **M** gray zones, **K** manipulation/dark patterns; ZH-specific mechanisms detected: **<list>**."

---

## Pitfalls

- **Mapping 關係 onto Cialdini #5 (Liking) and stopping there**: 關係 is a **structural tie**, not affective rapport. Hwang 1987 explicitly distinguishes 情感性 / 工具性 / 混合性 relations — flattening into "Liking" loses the structural-vs-affective distinction. **關係 needs its own slot** in the ZH-specific mechanisms section, even though it overlaps Cialdini #5.
- **Treating 人情 reciprocity as single-transaction**: 人情 is a **multi-year ledger** with asymmetric weighting (Hwang 1987). Anglo Cialdini reciprocity ("I gave, you owe me back, now") is a sub-case. Apply 人情 frame when temporal-reference-to-past-favor is present.
- **Missing 面子 dynamics in B2B copy**: face-saving is half the persuasion in ZH B2B and political register. Reading a B2B proposal through Cialdini-only and missing 給面子 / 留面子 dynamics produces a **false 🟢** when the actual mechanism is 🟡 or 🔴.
- **Forcing TW register onto PRC artifact (and vice versa)**: TW post-democratization (PD ≈ 58, IDV ≈ 17) and PRC (PD ≈ 80, IDV ≈ 20) operate at different weightings. PRC artifacts read with TW-register weights will under-weight Authority. TW artifacts read with PRC-register weights will over-weight 同胞 / 國家 framings. **Detect register first** — TW-traditional / TW-simplified-influenced / HK / PRC — and adjust.
- **Treating 道德綁架 as standard Cialdini guilt**: 道德綁架 is a **register-specific dark pattern** that invokes **moral identity** (filial piety / family loyalty / national identity), not just convenience-shame. Mark it as a ZH-specific dark pattern, not as Brignull confirmshaming.
- **Confusing 面子 (mianzi) with 臉 (lian)**: per Hu 1944, **mianzi** = public dignity tied to status/accomplishment; **lian** = moral character / integrity. Persuasion mechanisms most often weaponize 面子 (status face), but character-frame appeals invoke 臉 (moral face). Distinguish them — they have different repair mechanics.
- **Reading WEIRD-sample Cialdini weightings literally**: Hofstede CN PD ≈ 80 vs US PD ≈ 40 is a 2× difference — Authority weighting needs ≈ 2× adjustment in CN register. Cross-cultural meta-analyses (Petrova et al. 2007 on commitment-consistency; Hofstede synthesis) confirm direction; magnitudes are heuristic.
- **Over-reading 關係 in casual consumer copy**: 蝦皮 / momo C2C consumer copy uses 關係 *frames* (parasocial 自己人) but rarely engages real 關係 networks. Mark these as 🟡 parasocial-illusion, not 🟢 authentic 關係.

## See also

- [`lens-persuasion.md`](lens-persuasion.md) — universal-core router
- [`lens-persuasion-anglo.md`](lens-persuasion-anglo.md) — Cialdini + Brignull WEIRD-baseline
- [`lens-persuasion-ja.md`](lens-persuasion-ja.md) — JP-register variant (建前/本音 + 婉曲表現)
- [`lens-frame-zh.md`](lens-frame-zh.md) — 面子 / 關係 as identity/relational frames (frame analysis sibling)
- [ADR-0003](../../../docs/adr/0003-lens-synthesis-disclosure.md) — synthesis disclosure
- [ADR-0004](../../../docs/adr/0004-cultural-lens-variants.md) — cultural-lens-variant pattern
