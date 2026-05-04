# Lens: Persuasion Analysis (Japanese register — Cialdini + JP cultural variants)

> **Sources**:
> - Robert Cialdini, *Influence: The Psychology of Persuasion*, New and Expanded edition (Harper Business, 2021). Original 6 principles introduced in 1984 first edition (Reciprocity / Commitment & Consistency / Social Proof / Authority / Liking / Scarcity); **Unity is the seventh principle, added as Ch 8 of the 2021 expanded edition** (originally surfaced in *Pre-Suasion*, 2016). Japanese translation: 『影響力の武器〔第三版〕』社会行動研究会訳, 誠信書房 — establishes the canonical JP terminology used below (返報性 / 一貫性 / 社会的証明 / 権威 / 好意 / 希少性 / 一体性).
> - Doi Takeo (土居健郎), 『「甘え」の構造』 (弘文堂, 1971; English: *The Anatomy of Dependence*, Kodansha International 1973). Canonical post-war JP cultural-anthropology source for **甘え (amae)**, **建前/本音 (tatemae/honne)**, **遠慮 (enryo)**, **察し (sasshi)** — Doi frames these as communicative manifestations of amae psychology, and treats tatemae/honne explicitly in the 1986 follow-up 『表と裏』(*The Anatomy of Self*, Kodansha International).
> - Geert Hofstede, *Culture's Consequences* (Sage, 1980; expanded 2nd ed. 2001) and the Hofstede Insights / theculturefactor country profile for Japan. JP scores referenced in this file: **Power Distance ≈ 54** (moderate, not extreme — close to US 40), **Individualism ≈ 46** (more collectivist than WEIRD samples but not as low as East/Southeast Asian collectivist cluster), **Uncertainty Avoidance ≈ 92** (one of the highest worldwide), **Masculinity ≈ 95** (highest in the dataset).
> - Orji, R., "Persuasion and Culture: Individualism-Collectivism and Susceptibility to Influence Strategies" (PERSUASIVE 2016 / CEUR-WS Vol-1582). Empirical N=335 cross-cultural study showing **collectivists are more susceptible to most Cialdini strategies, not less** — the inverse of the common Anglo intuition that collectivists "resist" Western marketing.
> - Cialdini et al. cross-cultural compliance work — the canonical study comparing US (individualist) vs Polish (collectivist) responses to social-proof vs commitment-consistency framings; collectivists more responsive to social proof, individualists more responsive to commitment.

> **Synthesis disclosure**: This file applies Cialdini's 7 principles to the **Japanese cultural register** AND adds **JP-specific persuasion mechanisms** (建前/本音 layered communication, 婉曲表現 indirect expression as virtue, 空気 reading, 老舗/暖簾 institutional-longevity authority) that are absent from Anglo Cialdini. Cialdini did not co-publish with Doi or any JP cultural-anthropologist; the combination is a methodological choice by `deconstruct-toolkit` (see [ADR-0003](../../../docs/adr/0003-lens-synthesis-disclosure.md) and [ADR-0004](../../../docs/adr/0004-cultural-lens-variants.md)). The JP mechanisms are NOT translations of Cialdini principles — they operate in a register layer Cialdini's WEIRD-sample design did not surface.

> **Cultural-register note**: Cialdini's empirical base is overwhelmingly WEIRD (Western / Educated / Industrialized / Rich / Democratic) and US-undergraduate-heavy. Applied to JP register: **authority weight is up** (Hofstede PDI 54 + 老舗 institutional reverence amplify #4); **social proof + unity weight is up** (IDV 46 collectivist tilt amplifies #3 and #7 — and the Orji 2016 finding flips the Anglo intuition about who is "more manipulable"); **scarcity behavior differs** (queue / 限定 / 行列 culture turns scarcity into a status-signaling virtue rather than urgency-induced anxiety); **persuasion-via-indirection (婉曲表現) is virtue, not weakness** — the JP register treats directness as low-skill or aggressive, inverting the Anglo "be direct = be honest" frame. **Do NOT apply Cialdini-anglo dark-pattern weightings as if culturally-neutral.**

## When to apply this lens

- JP marketing copy, advertising, sales pages (楽天 / メルカリ / ZOZOTOWN-style DTC e-commerce LP)
- JP business proposal documents (企画書 / 提案書) — note overlap with `lens-genre-ja`
- JP political speech / 演説 / 政見放送 — especially where 建前/本音 layering is operative
- JP onboarding flows (LINE 公式アカウント / アプリ登録)
- JP subscription / 定期購入 flows — 解約導線 is a known dark-pattern surface in JP register
- Any JP-language artifact designed to change behavior

## When NOT to apply

- Pure informational JP content (technical docs, dictionaries, 取扱説明書 reference sections)
- Personal correspondence with no persuasive intent
- Translated Anglo artifacts where source-language register dominates → use `lens-persuasion-anglo.md` and flag the translation
- Mixed JP/EN bilingual artifacts → run both variants per `protocols/lens-variant-selection.md`

---

## Part 1: Cialdini's 7 Principles — JP weighting + manifestation

For each principle, check **if** and **how** the artifact triggers it,
then assign an **ethical position** (see Part 4). The table below maps
Anglo manifestation → JP manifestation/weight.

### 1. Reciprocity (返報性)

| Aspect | Anglo manifestation | JP manifestation / weight |
|---|---|---|
| Trigger | Free gifts, samples, free-tier trials, "give first" | お試し / 試供品 / おまけ / 心ばかり; 御中元・御歳暮 gift-giving cycle is a year-round institutionalized reciprocity engine |
| Weight | Standard | **Up** — 義理 (giri) obligation amplifies the felt-debt; declining a gift is socially expensive |
| Detection signals | "Free guide / template" | 「無料サンプル」「お試しセット」「初回限定特典」「気持ちばかりですが」; physical gift-with-purchase common even in DTC e-commerce |

### 2. Commitment & Consistency (一貫性)

| Aspect | Anglo manifestation | JP manifestation / weight |
|---|---|---|
| Trigger | Foot-in-the-door, public/written commitments, identity claims | 段階的 multi-step 申込; 表明 of intent before transaction; 会員登録 → 本会員 progression |
| Weight | Slightly down vs Anglo — JP individuals are more interdependent-self (Markus & Kitayama 1991), so private-commitment-to-self is weaker; **collective commitment** is stronger |
| Detection signals | "Do you agree?" early-form questions | 「ご賛同いただけますか」 group-affirming framings; 「弊社一同」 collective-commitment framings; 連名 co-signature norms |

### 3. Social Proof (社会的証明)

| Aspect | Anglo manifestation | JP manifestation / weight |
|---|---|---|
| Trigger | "X thousand users", testimonials, ratings, recent activity | 「累計○万本突破」「楽天ランキング1位」「リピーター○%」; 行列 (visible queues); media mention "テレビで紹介" |
| Weight | **Up** (per Orji 2016 + Cialdini cross-cultural compliance research — collectivists significantly more responsive to social proof) |
| Detection signals | "Join 10,000+ founders" | 「○万人が選んだ」「日本で一番売れている」「○年連続売上No.1」; 口コミ評価; 雑誌掲載; 行列写真; インフルエンサー使用 |

### 4. Authority (権威)

| Aspect | Anglo manifestation | JP manifestation / weight |
|---|---|---|
| Trigger | PhD, MBA, expert endorsement, professional photo | **肩書き** (titles) + **老舗 (long-established) brand** + **創業○年** + **皇室御用達** + **○○大学○○教授監修** + government/ministry seals (厚労省認可 / トクホ) |
| Weight | **Up** (Hofstede PDI 54 amplifies deference; 老舗 culture institutionalizes longevity-as-authority — "創業1853年" reads as proof) |
| Detection signals | "as featured in", institutional logos | 「創業○年」「宮内庁御用達」「東大医学部監修」「厚労省認可」「グッドデザイン賞受賞」; 白衣 in pharma; 専門家コメント from named 医師 with affiliation |

### 5. Liking (好意)

| Aspect | Anglo manifestation | JP manifestation / weight |
|---|---|---|
| Trigger | Similarity, founder origin story, compliments, humor | **共感** — empathy-resonance framing; 創業者の想い; 親しみやすい語り; **キャラクター** mascots (くまモン / ふなっしー pattern) used as liking-vector |
| Weight | Standard but **expressed through different surfaces** — JP register prefers warmth (温かみ) and humility (謙遜) over informal cleverness |
| Detection signals | "we get it", localized references | 「私たちの想い」「お客様の声に寄り添って」 founder-letter framings; 手書き風 fonts; キャラクター親近感; 方言 / 地域性 framing |

### 6. Scarcity (希少性)

| Aspect | Anglo manifestation | JP manifestation / weight |
|---|---|---|
| Trigger | Limited-time, limited-quantity, countdown, loss framing | 「限定」「数量限定」「期間限定」「先着○名様」; **行列文化** — visible queues outside ramen shops / pop-up cafes invert "scarcity = anxiety" into "scarcity = status" |
| Weight | **Different shape, not strictly up or down** — JP scarcity often functions as **status signal** (limited-edition collectibles, 御朱印, ガチャ) more than urgency-trigger |
| Detection signals | "X left in stock", countdown | 「数量限定」「○○限定」「先着」「予約受付中」; 「在庫残りわずか」; リアルタイム在庫表示; 待ち列 / 整理券 imagery |

### 7. Unity (一体性)

| Aspect | Anglo manifestation | JP manifestation / weight |
|---|---|---|
| Trigger | "We" framing, shared identity, tribal markers | 「私たち日本人」「ニッポンの○○」「○○ファミリー」; **ウチ/ソト (uchi/soto)** in-group / out-group distinction operationalized in copy register |
| Weight | **Up** (interdependent self-construal makes group membership identity-central; nation-level appeals work where they would feel jingoistic in Anglo register) |
| Detection signals | nationality / generation appeals | 「日本の伝統」「メイドインジャパン」「○○県民の皆様」「○○世代」「○○ママ」; insider 専門用語 (e.g. オタク fandom-specific shorthand) |

---

## Part 2: JP-specific mechanisms not in Cialdini

These four mechanisms operate in JP register but are **absent from
Cialdini's 7-principle taxonomy**. They must be checked separately;
collapsing them into Cialdini buckets loses information.

### M1. 建前/本音 (tatemae/honne) layered communication

| Field | Content |
|---|---|
| Romaji + gloss | tatemae (public stance / facade) vs honne (true feelings / underlying ask) |
| Description | The artifact carries two simultaneous messages: a **surface message** that is socially appropriate / face-saving, and an **underlying ask** that is the actual persuasive intent. JP business communication treats the layering as a *competence*, not a deception (per Doi 1971/1986; ginza-bc.co.jp business-communication consensus: 海外では交渉ごとの際に建前を使うことはほとんどないが、日本では建前が前提で交渉が進む). |
| Surface signal | 「○○させていただきます」「ご検討いただければ幸いです」「前向きに検討いたします」 ("I'll positively consider it" — often functional honne is "no"); 「上長に確認します」「社に持ち帰って検討します" — graceful deferrals; clause-level hedging where the proposition stays implicit. |
| Ethical position | **Register-appropriate by default → 🟢**; becomes 🟡 / 🔴 only when the gap between tatemae and honne is **manufactured to obscure a known cost** (e.g., "前向きに検討" when the answer is already a hard no and the deferral is pure stalling). The lens reader's job is to surface the honne layer, not to label tatemae as deception. |

### M2. 婉曲表現 (enkyoku hyōgen) indirect expression as virtue

| Field | Content |
|---|---|
| Romaji + gloss | enkyoku hyōgen (indirect / euphemistic / circumlocutory expression) |
| Description | JP register treats indirection as politeness-skill and reader-respect, not evasion. Per Indeed JP / TRANS.Biz / Domani business-communication consensus: ビジネスシーンにおいて円滑なコミュニケーションを築くため、メールや会話をする際に用いられることが多い. Inverts the Anglo "be direct = be honest / clear" frame — in JP register, *too direct* reads as low-skill, aggressive, or 失礼. The persuasive force often lives in what is **not** said (省略 / 含み). |
| Surface signal | クッション言葉 「恐れ入りますが」「あいにくですが」「もしよろしければ」「差し支えなければ」; 推量・婉曲 grammar 「〜かもしれません」「〜のようでございます」「〜と存じます」; passive-voice softening 「〜となっております」 instead of 「〜です」. |
| Ethical position | **Register-appropriate by default → 🟢**; becomes 🟡 when 婉曲 is used to **bury a material disclosure** (e.g., "場合によっては追加料金が発生することがございます" hiding a guaranteed surcharge), 🔴 when used to obscure a known harm (per cotohajime コトハジメ note: 婉曲表現は受動攻撃 / "passive-aggressive" register can weaponize politeness). |

### M3. 空気を読む (kūki wo yomu) collective-mind persuasion

| Field | Content |
|---|---|
| Romaji + gloss | kūki wo yomu (literally "read the air"; collective-mood-sensing) |
| Description | Persuasion mechanism distinct from social proof: **the artifact creates or enforces a 場の空気** ("atmosphere of the situation") and persuades by making dissent feel like 空気が読めない (KY, "can't read the air"). Per 山本七平 『「空気」の研究』 (1977, often-cited canonical source): 日本人が集団で何かを決定する時、最終的には場の空気がすべて決めてしまう — atmosphere overrides logical argumentation. Cialdini social-proof says "follow the crowd"; 空気 says "the crowd's consensus is already binding on you, before you've decided". |
| Surface signal | Implicit-consensus framings 「皆様もうすでにご利用です」「○○するのが当然」「常識的に考えて」; closed-question framings that pre-suppose agreement; 「みんな選んでいる」 with no quantification (different from #3 which has numbers); peer-pressure deadlines 「今みんな登録しています」. |
| Ethical position | **Mostly 🟡 by default** — 空気 mechanisms work below the user's deliberation threshold. Becomes 🔴 when the "air" is **manufactured** (paid influencer waves engineering false consensus). Becomes ⚫ when combined with shame triggers — "everyone sane is doing this, you don't want to be the weird one" reads as confirmshaming with cultural backing. |

### M4. 老舗 / 暖簾 (shinise / noren) credibility — institutional-longevity authority

| Field | Content |
|---|---|
| Romaji + gloss | shinise (long-established business; lit. "old shop") / noren (lit. "shop curtain" — metonymic for accumulated trust + reputation) |
| Description | A JP-register-specific **authority sub-mechanism** that does not collapse into Cialdini #4 cleanly. JP has ~33,000 firms older than 100 years and ~4,000 older than 200 years (Teikoku Databank 2019) — by far the world's largest 老舗 stock. "創業○年" is not just authority signal; it is a structural class of institutional credibility ("暖簾を守る" = "守る the accumulated reputation"). Per Meiji Univ / reiro branding research: 老舗企業にとって最大の資産は、長年の実績と顧客からの信頼. |
| Surface signal | 「創業○年」「○代目」「江戸時代より続く」「宮内庁御用達」「老舗の味」「のれん分け」; family-succession imagery; 蔵 / 工房 photography; founder-portrait pedigrees; traditional 印章 / seal motifs in branding. |
| Ethical position | **🟢 by default when factually accurate** — JP register grants longevity claims real weight, and the underlying institutional-longevity is genuinely informative (a 200-year-old miso brewery has survived multiple shocks, which IS evidence). Becomes 🟡 when the founding date refers to a corporate predecessor with weak continuity (M&A reset; rebranding masquerading as descent). Becomes 🔴 when fabricated outright. **Critical pitfall**: do not classify 老舗 framing as "manufactured authority" by default — it is closer to "credentialed authority" in JP register. |

---

## Part 3: Dark patterns (Brignull) JP equivalents

Most Anglo dark patterns translate directly to JP register, but several
are **register-shifted** or **register-specific**. The 12 Brignull
patterns from `lens-persuasion-anglo.md` Part 2 still apply; the table
below documents JP-specific translation issues.

| Brignull pattern | JP register translation issue |
|---|---|
| Confirmshaming | Translates **harder** in JP — politeness register makes guilt-trips read as register-appropriate humility ("私のような者にはご利用いただけませんよね…"). Watch for 申し訳なさそうな圧 ("apologetic pressure") that softens shame into politeness. |
| Roach Motel (解約導線) | Translates directly; **JP 定期購入** subscription-trap is a known regulatory surface (特定商取引法 amendments 2022/2024 specifically targeting). |
| Hidden costs | Translates directly. JP-specific: 税抜き表示 vs 税込表示 ambiguity is a long-standing local pattern; **総額表示義務** (Apr 2021 onwards) constrains some surfaces but not all. |
| Forced Continuity | Translates directly; pairs with 定期購入 above. |
| Trick Questions | Translates with **higher false-positive risk** — JP grammar's double-negative + 婉曲表現 can read as trick questions to Anglo eyes when they are register-appropriate. Verify against native register before flagging. |
| Sneak into Basket | Translates directly. |
| Disguised Ads | Translates directly. JP **ステマ規制** (Stealth Marketing Regulation, Oct 2023, 景表法) now criminalizes some disguised-ads patterns explicitly. |
| Friend Spam | Less prevalent in JP (LINE / SMS sharing patterns differ from US contact-list patterns). |
| Misdirection | Translates directly; visual hierarchy patterns universal. |
| Privacy Zuckering | Translates directly. JP **個人情報保護法** (APPI) baseline is similar to GDPR-lite. |
| Bait and Switch | Translates directly; 景品表示法 優良誤認 explicitly criminalizes. |
| Price Comparison Prevention | Translates directly. |

**JP-register-specific dark-pattern variant**: 申し訳なさそうな圧
("apologetic pressure") — using extreme politeness-humility register to
make refusal feel like the user is being rude to the brand. Example:
「もしご都合がよろしければ…」 followed by a one-click upsell where
declining requires multiple click-throughs of equally-polite "本当に
よろしいですか？" confirmations. Maps to Brignull confirmshaming +
roach motel hybrid in Anglo taxonomy, but the **politeness register is
the dark-pattern vector**, not despite of it.

---

## Part 4: Ethical Position Verdict (mandatory, cross-cultural)

This 4-position taxonomy is shared across all variants per
`lens-persuasion.md`:

| Position | Definition | JP example |
|---|---|---|
| 🟢 **Transparent** | Principle used + user can see and reject | 「累計100万本突破」 with linked verification page |
| 🟡 **Gray zone** | Principle used + user is unaware | 婉曲表現 burying a material surcharge clause |
| 🔴 **Manipulation** | Creates urgency / false belief | 偽の在庫カウント (fake "残り3点!") |
| ⚫ **Dark pattern** | Actively deceives, harms user | 定期購入 解約導線 phone-only / 9-17時 only |

**Rule**: Every detected mechanism (Cialdini 7 OR JP-specific M1-M4 OR
Brignull 12) gets one of these positions. Neutral description without
ethical position is **not allowed** in the output.

---

## Worked example: a JP DTC supplement landing page (synthetic-representative)

**Snippet** (~7 sentences, realistic 楽天 / D2C-style register):

> 創業1928年、京都の老舗薬局がつくる、こだわりの和漢サプリメント。
> 厚労省認可・GMP工場で一粒一粒、丁寧に仕上げております。
> ○○大学医学部・山田太郎教授も推奨する、伝統と科学の融合。
> すでに累計50万人以上のお客様にご愛用いただいております。
> 通常価格 6,800円のところ、初回限定 980円（送料無料）。
> 数量限定・先着300名様まで。お一人様一回限り。
> ※本商品は2回目以降、自動的に定期コース（月6,800円）に移行します。解約はマイページよりお手続きください。

### Cialdini-7 (JP weighting)

| Principle | Triggered? | How | Position |
|---|---|---|---|
| Reciprocity (返報性) | ✓ | 「初回限定 980円」 + 送料無料 (loss-leader as gift-frame) | 🟡 Gray zone — 980円 is bait for 6,800円 subscription |
| Commitment (一貫性) | ✓ | 「お一人様一回限り」 + 自動移行 to subscription | ⚫ Dark pattern — micro-commitment funnels into roach-motel |
| Social proof (社会的証明) | ✓ | 「累計50万人」 unverified | 🟡 Gray zone (no link / no audit) |
| Authority (権威) | ✓✓ | 「創業1928年」 + 厚労省認可 + GMP + 大学教授推奨 — quadruple-stacked | 🟢 if claims verifiable; 🟡 if 教授推奨 is paid endorsement undisclosed |
| Liking (好意) | ✓ | 「京都の老舗薬局」 warmth / regional pride; 丁寧に仕上げております | 🟢 |
| Scarcity (希少性) | ✓ | 「数量限定・先着300名様」 | 🟡 — verify whether "300名" rolls daily (manufactured) |
| Unity (一体性) | ◯ | 「日本の伝統」 implicit via 京都 + 和漢 | 🟢 weak |

### JP-specific mechanisms (M1-M4)

| Mechanism | Triggered? | How | Position |
|---|---|---|---|
| M1 建前/本音 | ✓ | tatemae "丁寧にお手続きください" / honne "解約導線は意図的に重い" | 🔴 — gap between surface invitation and friction reality |
| M2 婉曲表現 | ✓ | 「自動的に定期コースに移行します」 buried in 米印 footnote | ⚫ — material disclosure deliberately softened to footnote |
| M3 空気を読む | △ | weak — 「すでに50万人」 implies "everyone is doing it" | 🟡 |
| M4 老舗 / 暖簾 | ✓✓ | 「創業1928年、京都の老舗薬局」 — institutional-longevity authority is a primary vector here, not just decoration | 🟢 if literal; 🔴 if "薬局" is dormant/unrelated and only the year is true |

### Brignull dark-pattern check

| Pattern | Detected? | Note |
|---|---|---|
| Forced Continuity | ✓ | 「2回目以降、自動的に定期コース」 — classic ⚫ |
| Roach Motel | likely ✓ | "解約はマイページより" tells us nothing about friction; needs flow inspection |
| Hidden Costs | ✓ | 6,800円 actual price buried in 米印 footnote | ⚫ |
| Confirmshaming | ✗ | not in this snippet |
| Disguised Ads | ✗ | clearly an LP, not editorial |

### Verdict

**⚫ Multiple dark patterns** in subscription / disclosure flow despite
**🟢 legitimate institutional authority** (the 創業1928年 + GMP + 厚労省
认可 stack is real authority on JP register, not manufactured). The
problem is not the persuasion mechanisms — it is the **建前/本音 gap**
between surface invitation and 定期購入 commitment, and the 婉曲表現
burial of the material 6,800円 disclosure. Recommend escalation: this
artifact is a regulatory risk under JP 特定商取引法 (定期購入規制 2022
amendments) and 景品表示法 優良誤認 / 有利誤認 — even though each
individual claim might be technically defensible.

---

## Output format

```markdown
### Cialdini-7 (JP weighting)
| Principle | Triggered? | How | Position |
|---|---|---|---|
| Reciprocity (返報性) | ✓/✗ | <description> | 🟢/🟡/🔴/⚫ |
| Commitment (一貫性) | ... | ... | ... |
| Social proof (社会的証明) | ... | ... | ... |
| Authority (権威) | ... | ... | ... |
| Liking (好意) | ... | ... | ... |
| Scarcity (希少性) | ... | ... | ... |
| Unity (一体性) | ... | ... | ... |

### JP-specific mechanisms
| Mechanism | Triggered? | How | Position |
|---|---|---|---|
| M1 建前/本音 | ... | ... | ... |
| M2 婉曲表現 | ... | ... | ... |
| M3 空気を読む | ... | ... | ... |
| M4 老舗 / 暖簾 | ... | ... | ... |

### Brignull dark patterns (JP-translation-aware)
| Pattern | Detected? | Note |
|---|---|---|
| ... | ... | ... |

### Ethical position per mechanism
<one paragraph synthesizing Cialdini-7 + M1-M4 + Brignull>
```

End with 1-line ethical position: "**Overall: 🟢/🟡/🔴/⚫** — N
Cialdini principles triggered transparently, M in gray zones, K dark
patterns + L JP-specific mechanism issues."

## Cross-variant pointer

The same artifact analyzed via `lens-persuasion-anglo.md` would
**likely under-detect**: the 老舗 / 暖簾 authority weight, the 建前/本音
gap, the 婉曲表現 disclosure burial, and the 空気-based implicit
consensus. The same artifact via `lens-persuasion-zh.md` would weight
**面子 (face)** and **關係 (guanxi)** instead of 老舗 / 暖簾 — TC/SC
register has its own institutional-credibility shape that is **not**
identical to JP shinise culture.

## Pitfalls

- **Applying Anglo dark-pattern labels (e.g. "sneaking" / "confirmshaming") without checking if the artifact is using ホスピタリティ politeness conventions** — JP 婉曲 / クッション言葉 is register-appropriate, not deception. Verify against native register before flagging 🔴.
- **Missing 建前/本音 layer — surface analysis only catches half the persuasion**. Per Doi 1971/1986, JP communication is layered by design; a one-pass surface read misses the honne ask.
- **Treating 婉曲 indirectness as deception** — it's register-appropriate. The dark-pattern test is whether material disclosures are buried (🔴/⚫), not whether the prose is indirect (🟢 by default).
- **Forcing a JP artifact through WEIRD-sample Cialdini weightings** — Orji 2016 + Cialdini cross-cultural data show collectivists are MORE susceptible to most Cialdini triggers, not less. Anglo intuition that "JP audiences resist Western marketing" is empirically backward.
- **Collapsing 老舗 / 暖簾 into Cialdini #4 (authority)** — they overlap but are not identical. 老舗 is structural (institutional-longevity-as-credential); Cialdini #4 is largely individual (expert/title). Both can be present; both must be detected separately.
- **Over-detecting 空気 mechanisms** — implicit-consensus framings are common register, not always 🔴. Reserve 🔴/⚫ for cases where the "air" is manufactured (paid waves) or weaponized (KY-shaming).
- **Defaulting to 🔴 / ⚫ on JP politeness register out of WEIRD-eye suspicion** — the inverse pitfall. The 4-position verdict must be calibrated on JP register, not transplanted from `lens-persuasion-anglo.md`.
