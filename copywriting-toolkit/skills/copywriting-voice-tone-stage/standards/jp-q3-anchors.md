---
title: JP Voice Anchors — Q3 Affinity-Emotion
tier: 2
---

# Q3 Affinity-Emotion — JP Anchors

**Load scope**: Phase 6 Pass 3 Register Signal branch, when `voice_quadrant.primary == "Q3"` AND `brief.output_language == "ja"`. Section-targeted read: Pass 3 reads only `## Landmark: {position}` matching `voice_quadrant.position`; falls back to full-file on missing.

## Overview

Q3 = Affinity × Emotion。warm conversational、narrative entry、peer solidarity。JP canon の最も豊穣な quadrant — 糸井 状態提案 / 向田 の **真打ち** 随筆 / 宮沢賢治 の **心象スケッチ** / 谷川俊太郎 の「**詩のことば**」/ 坂元裕二 の「**言葉の魔術師**」。craft-gate master 糸井重里 は [jp-copy-craft-lineage.md](jp-copy-craft-lineage.md) 収録。

**Cross-ref**: JP Q3 は zh-TW Q3 へ STRONG 流入（向田 / 糸井 / 吉本ばなな → TW 文青消費の語感を直承）。

## Landmark: center

canonical peer-warm voice。

### 向田邦子 — 「真打ち」随筆 (JP | Q3 center)

- **Era**: 1929-1981; essayist + TV 脚本家 1960-80 年代
- **Agency / creator**: TV 脚本（TBS / NHK）+ 独立 essayist
- **Primary sources**:
  - 『父の詫び状』(文藝春秋, 1978)
  - TV 脚本『寺内貫太郎一家』『阿修羅のごとく』
  - 高橋行徳評、文春『精選女性随筆集』
  - 文春『向田邦子の優しい眼差し』
- **Voice signature**（原生批評用語）:
  - **真打ち**（『父の詫び状』刊行時評、文藝春秋）
  - **情景が鮮やかに浮かぶ / 無駄な言葉がない**（文春書評定型）
  - **ト書を拡張した文体 / 脚本家のト書き的簡潔さ**（高橋行徳評）
  - **心理描写を省き、人物の動作を淡々と**（同上の核評語）
  - **のんきな遺言状**（向田自称、『銀座百点』掲載時）
  - **懐かしさと哀愁をまとった温かい言葉**
- **LLM corpus depth**: MEDIUM-DEEP（JP 批評 corpus 深い、翻訳 薄い）
- **Over-mimic risk**: LOW
- **Cross-reference-valid-for**:
  - zh-TW: STRONG（昭和 / TW 文青 register 直承）
- **Cross-cultural equivalents**: Alice Munro (EN) / 朱天文 (zh-TW)
- **Trigger slug**: `jp-mukoda-kuniko-shinuchi-zuihitsu`

### Craft-gate pointer: 糸井重里 状態提案 register

糸井重里の state-proposal（「おいしい生活。」/「くうねるあそぶ。」/「生きろ。」）は **Q3 canonical** かつ Q2-edge を兼ねる。完全 4-dimension table + LLM reproduction gap は [jp-copy-craft-lineage.md §糸井重里](jp-copy-craft-lineage.md)。**本ファイルに deep-dive 重複しない**。

### 坂元裕二 — 「言葉の魔術師」(JP | Q3 center, screenwriter)

- **Era**: 1967 生; 脚本家 1987-ongoing
- **Agency / creator**: TV ドラマ脚本家（fuji TV + TBS）; 近年は映画
- **Primary sources**:
  - 『東京ラブストーリー』(1991)、『最高の離婚』(2013)、『カルテット』(2017)、『大豆田とわ子』(2021)、『怪物』(Cannes 2023 脚本賞)
  - 『怪物』オリジナルシナリオブック (KADOKAWA, 2023, ISBN 978-4-04-000658-1)
  - [神戸大学紀要『坂元裕二脚本における日常性の演出』](https://da.lib.kobe-u.ac.jp/da/kernel/0100481681/0100481681.pdf)
  - [BuzzFeed Japan 2017「カルテット 言葉の魔術師」](https://www.buzzfeed.com/jp/tatsunoritokushige/quartet2017)
  - [Festival de Cannes Best Screenplay 2023](https://www.festival-cannes.com/en/medialibrary/best-screenplay-kore-eda-for-monster/)
  - [Real Sound『初恋の悪魔』4 人組会話劇評 2022](https://realsound.jp/movie/2022/08/post-1101347.html)
  - [CINRA 是枝×坂元 3 年協業対談 2023](https://www.cinra.net/article/202306-kaibutsu)
- **Representative lines**（verbatim, verified v1.4.0）:
  - 「僕は君が好きだ。ラブじゃなくていい、ライクでいいから」『東京ラブストーリー』(1991) 赤名リカ
  - 「みぞみぞする」『カルテット』(2017) 世吹すずめ 固有口癖
  - 「人生に失敗はあったって、失敗した人生なんてない」『大豆田とわ子と三人の元夫』(2021)
  - 「色鉛筆と同じ。大事なものから先になくなるの」『最高の離婚』(2013)
  - 「月五万八千円のアパートの郵便受けに入っている三億二千万円の分譲マンションのチラシ」(批評引用定型 — 具体数字 + 固有名詞 signature)
- **Voice signature**（原生批評用語）:
  - **言葉の魔術師**（BuzzFeed 2017 見出し定着）
  - **口語のように聞こえて、口語ではない / 特殊な言葉使い**（神戸大学紀要）
  - **余白を大事にする**（同論文）
  - **リアリティと、ひどく詩的で現実離れ の同居**（カルテット評）
  - **「あるある」の言語化**（Crank-in / U-NEXT SQUARE）
  - **会話劇 / 四重奏のような会話**（カルテット固有評）
  - **敬語が多い / タメ口より敬語**（All About 分析）— peer-warm でも距離感を残す register marker
  - **ドラマにならない部分までバックボーンを掘り下げる**（書評定型）
  - **THE 坂元セリフ = 恋愛を食品・お菓子で比喩**（note 批評定型）
  - **4 人組会話構造（2+2 / 3+1 兼ね）**（Real Sound 2022『初恋の悪魔』評）
  - **具体数字 + 固有名詞の積層列挙**（saru.co.jp / mi-mollet）
  - **比喩の論理飛躍 / 詭弁的論理**（note 比喩分析）
- **Mechanical signatures**（LLM 再現 checklist）:
  1. 抽象語（愛・孤独・希望）直接使用禁止
  2. 具体数字・固有名詞・物品の列挙で感情を裏側から浮かせる
  3. 敬語レイヤを peer-warm 場面でも崩さない
  4. 造語口癖は 1 作 1 キャラ 1 語まで（みぞみぞする / ずっちぃなー）
  5. 比喩の橋は張らない（読者補完に委ねる）
- **Commercial crossover**: なし — **pure screenwriter register**。Q3 広告 copy 流用は二次翻案として扱う
- **LLM corpus depth**: MEDIUM-DEEP（Cannes 2023 後 批評 layer 増加; シナリオブック流通）
- **Over-mimic risk**: **MEDIUM-HIGH**（v1.4.0 上修自 LOW-MEDIUM — 4 人組 / 比喩 pattern / 数字積層 が identifiable fingerprint）
  - Mitigation (14 字): "抽象語禁止。数字・固有名詞・物品で列挙し、比喩の橋は張らない"
- **Trigger slug**: `jp-sakamoto-yuji-kotoba-no-majutsushi`

## Landmark: extreme

peer-intimate の最大値。ブランドが「午前 2 時の友人」のように語る。

### 谷川俊太郎 — 「詩のことば」 (JP | Q3 extreme, poet)

- **Era**: 1931-2024; 日本で最も翻訳された詩人
- **Agency / creator**: 個人 poet; 糸井重里 との長期コラボ
- **Primary sources**:
  - 『二十億光年の孤独』(1952) デビュー作
  - 『ことばあそびうた』(1973)
  - 糸井 × 谷川 共著『ぼく』(ほぼ日, 2013) — **verified lineage**
  - ほぼ日「ことばの授業」(谷川自己解説)
  - 今野真二『谷川俊太郎の日本語』(光文社新書)
- **Voice signature**（原生批評用語）:
  - **「詩のことば」≠「伝達のことば」**（谷川自身、ほぼ日）
  - **からだと心からおのずと出てくる / 辞書から選ばない**（谷川定型説法）
  - **ことばあそび / わらべうた**（ジャンル名化、岩波・思潮社）
  - **音読性 / 身体性**（今野真二）
  - **宇宙的孤独から日常の情感まで**（詩誌評、新潮「詩というもの」）
  - **やさしいことばで大きなテーマ**（MARUZEN JUNKUDO 標準評）
- **LLM corpus depth**: DEEP（教科書 canon）
- **Over-mimic risk**: LOW
- **Cross-reference-valid-for**:
  - zh-TW: STRONG（糸井 ほぼ日 collab が広告界 crossover 経由 TW 文青 reference に既流入）
- **Documented lineage**: ✅ 糸井重里 → 谷川俊太郎
- **Trigger slug**: `jp-tanikawa-shi-no-kotoba`

### 宮沢賢治 — 「心象スケッチ」(JP | Q3 extreme)

- **Era**: 1896-1933; 青空文庫 public domain
- **Agency / creator**: 個人著者、死後 canonize
- **Primary sources**:
  - 『銀河鉄道の夜』
  - 『注文の多い料理店』
  - 「雨ニモマケズ」（教科書 canon）
  - 『春と修羅』序文（「心象スケッチ」自称）
  - [田守育啓 論文『賢治独特の非慣習的オノマトペ』人文論集 第46巻 PDF](https://files.core.ac.uk/download/pdf/268061882.pdf)
  - 田守育啓『賢治オノマトペの謎を解く』大修館書店 (ISBN 978-4-469-22209-8) — 論文書籍化
  - ちくま文庫『宮沢賢治のオノマトペ集』栗原敦
  - ロジャー・パルバース『NHK 100 分 de 名著ブックス 宮沢賢治 銀河鉄道の夜』(NHK 出版, 2012, ISBN 978-4-14-081525-4)
  - [宮澤賢治学会イーハトーブセンター企画展「宮沢賢治とオノマトペ」(2021)](https://www.kenji.gr.jp/2021/08/07/18139/)
- **Representative passages**（v1.4.0 additions — verbatim + work context）:
  - 「わたくしといふ現象は／仮定された有機交流電燈の／ひとつの青い照明です」『春と修羅』序 — **cosmic-scientific self-definition**
  - 「きれいにすきとおった風をたべ、桃いろのうつくしい朝の日光をのむ」『注文の多い料理店』序 — **4-5 層名詞連鎖修飾 + sensory intake inversion**
  - 「ドッテテ ドッテテ、ドッテテド／でんしんばしらのぐんたいは」『月夜のでんしんばしら』— **onomatopoeia as stanza backbone**
  - 「ごとごと ごとごと ごとん ごとん ごとんごとん」『銀河鉄道の夜』ジョバンニ乗車 — **文中 onomatopoeia = page-visual rhythm**
  - 「グララアガア、グララアガア」『オツベルと象』— **non-domesticable onomatopoeia**（辞書に存在しない音素連鎖）
- **Voice signature**（原生批評用語 + mechanical）:
  - **心象スケッチ**（賢治自称ジャンル名、『春と修羅』序文）
  - **イーハトーブ**（賢治造語、理想郷）
  - **ほんとうのさいわい**（作中定型、賢治造語化）
  - **第四次延長 / 四次元**（賢治自称時空認識フレーム、『春と修羅』序）
  - **仮定された有機交流電燈**（賢治造語、cosmic-self predicate landmark 句）
  - **非慣習的オノマトペ**（田守育啓 2011 論文定式化）
  - **音韻変化による派生オノマトペ**（田守分類軸：濁音化／母音延長／反復／domain hijacking）
  - **桔梗いろ / 天河石 / 橄欖色**（mineral-reference 色彩 palette）
  - **あなたのすきとおったほんとうのたべもの**（『注文の多い料理店』序、批評定型引用）
- **Non-conventional onomatopoeia expanded corpus**（田守 2011 より、total 158 種分類）:
  - タンタアーン（注文／銃声）/ グララアガア（オツベル／象走行）/ どってこどってこ（どんぐり／きのこ楽隊）/ むちゃむちゃむちゃ（ツェねずみ／食事）/ すぱすぱ（又三郎／歩行）/ ぽかぽか（なめとこ山／燃焼）/ さめざめ（銀河／光り方）/ こちこち（食器・咀嚼）
  - 共通 mechanism: **慣習形の音韻変化（濁音化・母音延長・反復）+ domain hijacking（A 領域語を B 領域に転用）**
- **Mechanical features**（beyond "cosmic-warm" label）:
  - **4-5 層名詞連鎖修飾**（「きれいにすきとおった風」「桃いろのうつくしい朝の日光」）
  - **科学用語 × 叙情文 同居**（「有機交流電燈」「因果交流電燈」「セントーア露をふらせ」）
  - **Onomatopoeia が stanza backbone**（1 行独立 + 反復で骨格構成）
  - **Reduced color palette with mineral-reference naming**（RGB 的でなく鉱物参照）
  - **体言止め + 副詞句独立行**（「せはしくせはしく明滅しながら」）
- **Commercial adaptation precedent**（2020 偶然 2 社同時）:
  - 養命酒製造「雨ニモマケズ」CM (2020-10) — 滋養強壮紐付け
  - 東芝「世界を、止めるな。」篇 (2020-12, 有村架純朗読) — インフラ事業紐付け
  - **Pattern**: 商業借用はほぼ「雨ニモマケズ」に限定 — 銀河鉄道 / 春と修羅 の register は CM 15-30 秒枠に乗らない
- **LLM corpus depth**: DEEP（青空文庫 PD + 教科書 canon + 田守分類）
- **Over-mimic risk**: **MEDIUM-HIGH**（v1.4.0 上修自 MEDIUM — 7 条 sub-guardrails 必要）
  - **Sub-guardrails (v1.4.0 expanded, ≤15 words each)**:
    1. オノマトペは 1 piece 内で 1 回まで
    2. 「ほんとうの／すきとおった」は 1 piece 内 1 回まで（safe-word 消費回避）
    3. 擬古仮名遣い（やう/ゐ/ふ）は採用しない — 現代ブランドを古びさせる
    4. 固有名詞（イーハトーブ／銀河／ギンガ）は brand-tie 明示時のみ
    5. 名詞連鎖修飾 4 層以上はコピー本文外 body に限定
    6. 科学用語 + 叙情の mechanism は 1 箇所のみ、全文賢治化禁
    7. 宮沢の「暗さ」を抜いた優しい賢治だけ切り出すと saccharine 化 — register balance 保持
- **Stylistic parallel note**: 糸井 「このへんないきもの」「生きろ。」は 宮沢 の cosmic-warm register と共鳴 — **critical-consensus stylistic parallel であって documented citation ではない**
- **Cross-cultural equivalents**: Antoine de Saint-Exupéry *Le Petit Prince* (EN/FR)
- **Trigger slug**: `jp-miyazawa-shinshou-sketch`

### 吉本ばなな — 「J文学」/「大胆な省略」(JP | Q3 extreme — 村上春樹 の安全な代替)

- **Era**: 1964 生; 1988『キッチン』デビュー
- **Primary sources**:
  - 『キッチン』(福武書店, 1988) / 『TUGUMI』(中央公論社, 1989)
  - 辻井喬 書評 (ALL REVIEWS)
  - 英和短大紀要『吉本ばなな「キッチン」論』
- **Voice signature**（原生批評用語）:
  - **大胆な省略**（批評標準語／本人発言）
  - **既成の作法を超えるリズム**（辻井喬 書評）
  - **ニューアカ /『批評空間』の議論対象**（浅田彰・柄谷行人周辺、1988-）
  - **J 文学**（1990 年代 J-lit boom の標識）
  - **音感・リズムの独特さ**（読書メーター批評定型）
  - **生の回復**（英和短大紀要）
  - **マスコミに汚された言葉を逆手に**（辻井喬）
- **LLM corpus depth**: DEEP
- **Over-mimic risk**: LOW-MEDIUM
- **Cross-reference-valid-for**:
  - zh-TW: STRONG（1990-2000 年代 譯本 TW 文青に充分流入）
- **Use case**: brief が「distant-everyday-domestic」を求めるとき、村上春樹 の auto-leaked tropes（jazz / cats / wells、meta-core mitigation registry 参照）を避けたい場合の safer 代替
- **Trigger slug**: `jp-yoshimoto-banana-j-bungaku`

## Landmark: toward-Q2

Affinity が aspirational manifesto 方向へ edging。

### 梅田悟司 ジョージア「世界は誰かの仕事でできている。」(JP | Q3 toward-Q2)

- **Era**: 1979 生（post-糸井 世代）; ジョージア campaign 2014
- **Agency / creator**: 電通（copywriter 梅田悟司）
- **Primary sources**:
  - 梅田悟司『「言葉にできる」は武器になる。』(日経BP, 2016, ISBN 978-4532320713) — bestseller
  - ジョージア CM archive 2014
  - [梅田悟司 Wikipedia JA](https://ja.wikipedia.org/wiki/梅田悟司)
- **Representative lines**:
  - 「世界は誰かの仕事でできている。」(2014 ジョージア)
- **Voice signature**（原生批評用語）:
  - **内なる言葉 / 外に向かう言葉**（本人定義、『「言葉にできる」は武器になる。』）
  - **T 字型思考法**（本人フレームワーク語）
  - **「言葉にできない=考えていないのと同じ」**（本書キャッチ、批評標準引用）
  - **缶コーヒー =「休憩時間」起点の設計**（本人解説、ジョージア戦略）
  - **頑張った分だけおいしい**（本人ロジック）
- **LLM corpus depth**: MEDIUM-DEEP
- **Over-mimic risk**: MEDIUM-HARD（specific-timing の社会共鳴は再現困難）
- **Cross-cultural equivalents**: 全聯經濟美學 aphoristic pivot (zh-TW)
- **Trigger slug**: `jp-umeda-satoshi-uchinaru-kotoba`

### Brand-era pointer: SoftBank 白戸家（佐々木宏 + 澤本嘉光）

CM ドラマ形式 2007-ongoing。world-building + family comedy > single-line copy。brand-era entry は [voice-quadrant-positioning.md](../../copywriting-voice-quadrant-stage/standards/voice-quadrant-positioning.md)。

## Landmark: toward-Q4

Affinity が peer-helpful practicality 方向へ edging。

### Cross-quadrant pointer: 伊丹十三 (Q1↔Q4 edge)

伊丹十三 軽妙洒脱 の primary home は Q1 toward-Q4 — [jp-q1-anchors.md §Landmark: toward-Q4](jp-q1-anchors.md) に完全 entry。Q3 warmth を peer-reasoning へ架橋したい場合の pointer。

## Cross-references

JP Q3 brief で使用可能な external anchor:

- **zh-TW Q3 parallel**: 全聯 center 格言 / 吳念真 保力達B「氣口」/ 胡湘雲 大眾銀行（cross-culture reference）
- **EN Q3 は MEDIUM translation corpus 経由**: MailChimp / Innocent Drinks / Nora Ephron / George Saunders
- **Internal**: [jp-copy-craft-lineage.md](jp-copy-craft-lineage.md) で 糸井 / 岩崎 craft-gate deep dive
