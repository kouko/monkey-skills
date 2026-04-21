---
title: zh-TW Voice Anchors — Q3 Affinity-Emotion
tier: 2
---

# Q3 Affinity-Emotion — zh-TW Anchors

**Load scope**: Phase 6 Pass 3 Register Signal branch, when `voice_quadrant.primary == "Q3"` AND `brief.output_language == "zh-TW"`. Section-targeted read: Pass 3 reads only `## Landmark: {position}` matching `voice_quadrant.position`; falls back to full-file on missing.

## Overview

Q3 = Affinity × Emotion. zh-TW canonical: 全聯 格言體 TV-era (Z10 re-classified as Q3-**center**, NOT extreme), 吳念真 台語口白, 胡湘雲 大眾銀行 long-form TVC, 故宮粉絲團 peer-intimate SNS, 台灣吧 educational-comedy. JP Q3 cross-reference is STRONG — 向田 / 糸井 aesthetic directly feeds TW 文青消費 / 家庭 intimate registers.

**⚠ Z10 correction (canonical re-classification)**: 全聯 TV-era 2006-2014 is Q3-**CENTER** (格言 / aphorism register — 「長得漂亮是本錢，把錢花得漂亮是本事」) NOT Q3-extreme. Q3-extreme is reserved for peer-intimate voices (故宮 / 台灣吧) where the brand speaks as friend-at-2am.

## Landmark: center

Canonical peer-warm voice. Use when brief asks for standard affinity-emotional.

### 全聯福利中心 TV-era 2006-2014 — 格言體 (zh-TW | Q3 center per Z10)

- **Era**: 2006-2014 TV 廣告 era (pre-經濟美學); 2015- 經濟美學 era evolved naturally from this foundation
- **Agency / creator**: 奧美台灣 — team including 龔大中 (ECD, later CCO 2020+) per Z8 correction
- **Primary sources**:
  - [動腦雜誌 全聯經濟美學 case](https://www.brain.com.tw/) — multiple 2006-2014 pieces
  - [數位時代 龔大中 專訪 2015](https://www.bnext.com.tw/article/37152/bn-2015-08-23-084822-113)
  - [經理人月刊 全聯 × 奧美 對談 2020](https://www.managertoday.com.tw/articles/view/60005)
  - 第38屆時報廣告金像獎 (2015 經濟美學 win)
- **Representative lines** (verbatim, verified via 動腦 case coverage):
  - 「長得漂亮是本錢，把錢花得漂亮是本事。」
  - 「知道一生要去的20個地方之後，我決定先去全聯。」
  - 「來全聯買不只是省錢，是一種生活態度。」
  - 「當不成名模，日子也要過得有模有樣。」
- **Voice signature**:
  - 台灣青年生活感 (TW young-adult self-awareness register)
  - 自嘲式格言 (self-depreciating aphorism)
  - 對仗 structure (「本錢 / 本事」/「不只X / 是Y」) — **this is what makes it center not extreme; it's aphoristic discipline, not 2am-peer**
  - 時尚雜誌街拍視覺 × 庶民語言 mismatch as humor
- **LLM corpus depth**: DEEP (廣告教材 canonical)
- **Over-mimic risk**: MEDIUM — 對仗結構 可仿，但 TW 青年 tension 感難再生
  - Mitigation: "pair with specific TW cultural-class observation; no generic aphorism"
- **Cross-reference-valid-for**:
  - ja: STRONG via 糸井 state-proposal lineage (per meta-detail cross-ref JP→zh-TW)
- **Cross-cultural equivalents**: 糸井重里 state-proposal (JP) / Nora Ephron warm-wit (EN)
- **Trigger slug**: `zh-tw-quanlian-tv-era-aphorism`

### 吳念真 保力達B 系列 (zh-TW | Q3 center — 台語 peer-intimate)

**⚠ Z5 / Z7 corrections inline**: 吳念真's canonical advertising voice anchors are **保力達B 口白 (李奧貝納, 1990s-ongoing, 台語)** + **全國電子「足感心」(2000s)**. 多喝水 MORE WATER (金車) is奧美 in-house, NOT 吳念真 (Z5). 長榮〈I SEE YOU〉VO is 金城武 himself, NOT 吳念真 (Z7).

- **Era**: 1990s-ongoing; 保力達B long-running campaign 20+ years
- **Agency / creator**: 李奧貝納台灣 + 吳念真 旁白 + 文案參與
- **Primary sources**:
  - [中央社文化「細數不滅的經典」2020](https://www.cna.com.tw/culture/article/20200606w001)
  - 保力達B 廣告 20+ 年 on-air archive
  - 看雜誌〈從吳念真廣告旋風談起〉2008
- **Representative lines**:
  - 「明仔載欸氣力，保力達B甲你傳便便！」(保力達B 台語 long-running)
  - 「足感心A。」(全國電子 2000s)
  - 「一台車『凸』全台灣。」(裕隆 March 1990s)
- **Voice signature**:
  - 台語原音 + 勞動階級肉身感
  - Story-over-persuasion (說故事而非說服)
  - 長鏡頭 旁白 節奏
  - 反都會文青, 轉向 阿伯阿嬸 語境
- **LLM corpus depth**: MEDIUM (TW 台語 register 在 LLM 中 coverage 不均; 影像 + 旁白 hybrid)
- **Over-mimic risk**: HIGH — 台語聲口 + 世代情感結構 LLM 最弱項
  - Mitigation: "do not attempt 台語 reproduction; borrow story-structure + rural-peer stance only"
- **Cross-cultural equivalents**: Raymond Carver working-class precision (EN) / 向田邦子 JP
- **Trigger slug**: `zh-tw-wu-nien-jen-taiyu-peer-intimate`

### 胡湘雲 大眾銀行系列 (zh-TW | Q3 center — TVC-narrative)

- **Era**: 2010-2015 (〈母親的勇氣〉/〈夢騎士〉/〈馬校長的合唱團〉系列 peak)
- **Agency / creator**: 奧美台灣 — 胡湘雲 (CD)
- **Primary sources**:
  - [小魚廣告網 胡湘雲 專訪 2010](https://www.kleinerfisch.com/blog/2010/03/胡湘雲談大眾銀行廣告/)
  - amarylliss 部落格〈不平凡的平凡大眾〉深度評論
  - 國際獎項 (D&AD Yellow Pencil / Adfest 金獎 / Clio 金獎 / Cannes 銅獅 唯一台籍)
  - YouTube 官方 3-min 版本點閱破千萬
- **Representative works**:
  - 〈母親的勇氣〉TVC 2010 (台籍母親跨三國飛行探病真實改編)
  - 〈夢騎士〉2011 (改編弘道老人基金會「不老騎士」)
  - 〈馬校長的合唱團〉
  - 品牌 tagline: 「不平凡的平凡大眾」
- **Voice signature**:
  - 長篇 TVC 敘事 (3-min form)
  - 真實事件改編 (documented田調素材)
  - 小人物大情感 (replacing celebrity endorsement paradigm)
  - 台詞內斂, 留白多
- **LLM corpus depth**: MEDIUM
- **Over-mimic risk**: HARD — 敘事弧需要真實田調素材, 純語言模仿無法達成
  - Mitigation: "do not attempt long-form imitation without actual documentary anchor; use structural cadence only"
- **Trigger slug**: `zh-tw-hu-xiang-yun-narrative-tvc`

## Landmark: extreme

Maximum peer-intimate. Brand speaks as friend-at-2am or self-subverting institution. Apply mitigation.

### 故宮粉絲團「朕知道了」era (zh-TW | Q3 extreme — institutional self-subversion)

- **Era**: 2013「朕知道了」紙膠帶 爆紅 → sustained humorous register through 2010s-2020s
- **Agency / creator**: 國立故宮博物院 in-house 新媒體小組 + 文創合作
- **Primary sources**:
  - 故宮官網 2013「朕知道了」文創商品 press release
  - [動腦雜誌 故宮小編 文創案例](https://www.brain.com.tw/)
  - 數位時代 / Brand 故宮文創 case studies
  - 故宮 Facebook 粉絲專頁 archive
- **Representative lines / artifacts**:
  - 「朕知道了」(雍正硃批 → 紙膠帶 → meme — launching signature)
  - 文物 personification posts (翠玉白菜 humorous persona)
  - 「今天你來故宮了嗎」peer-tone posts
- **Voice signature**:
  - Historical-authority self-subversion (皇帝 / 文物 → meme subject)
  - Peer-intimate 二人稱 (「你」/「大家」)
  - Low-key absurdist humor built on high-culture material
  - Emoji + 古文 mixed register
- **LLM corpus depth**: MEDIUM-DEEP (landmark case widely discussed)
- **Over-mimic risk**: LOW — 故宮身份 + 文物素材 is unreproducible asset
- **Trigger slug**: `zh-tw-npm-zhen-zhidaole-institutional-meme`

### 台灣吧 Taiwan Bar (zh-TW | Q3 extreme — educational-comedy)

- **Era**: 2014 founded (謝政豪 / 蕭宇辰) → ongoing
- **Agency / creator**: 獨立創作團隊 (台灣吧)
- **Primary sources**:
  - [YouTube 台灣吧 channel](https://www.youtube.com/@TaiwanBar) full archive
  - [taiwanbar.cc](https://taiwanbar.cc/)
  - 創辦人訪談 (數位時代 / 親子天下 / 報導者)
- **Representative register**:
  - 「欸，你知道嗎...」(signature opener)
  - 歷史人物 rendered as peer-contemporary voice
  - 幹話 + 史實 mixed rhythm
- **Voice signature**:
  - 教學 + 幹話 coexist (first TW voice to legitimize 幹話 in educational content)
  - 二人稱直接呼叫
  - 歷史去神聖化 (history de-sanctification)
- **LLM corpus depth**: MEDIUM
- **Over-mimic risk**: LOW-MEDIUM
- **Trigger slug**: `zh-tw-taiwan-bar-educational-comedy`

### 杜蕾斯官微 (CN | Q3 extreme — cross-pollination reference)

- **Era**: 環時互動 金鵬遠 operating 2011-2017 (canonical window); 2017 環時互動 + Durex 合作終止 after which voice clearly declined
- **Agency / creator**: 環時互動 + 金鵬遠 creative lead
- **Primary sources**:
  - [數英〈史上最全杜蕾斯的文案〉2015](https://www.digitaling.com/articles/13315.html)
  - 澎湃新聞 / 梅花網 / TechOrange 2017 整理
- **Representative lines**:
  - 「北京今日暴雨，幸虧包裡還有兩隻杜蕾斯。」(2011 北京 721 大雨 × 鞋套避孕套 事件 borrowed-time campaign — 1 小時轉發破萬)
  - 借勢 literary: 「老師，你的衣服有幾只口袋？—— TT」
- **Voice signature**:
  - 借勢文案典範 (real-time hot-take canonical mode)
  - 擦邊球分寸 (boundary-danced suggestive)
  - 擬人化「小杜」聲口
  - Punch-line 結構 (setup + sudden pivot)
- **LLM corpus depth**: MEDIUM-DEEP
- **Over-mimic risk**: MEDIUM (joke structure copiable; real-time brand-discipline hard)
- **Cross-reference note**: This is CN anchor; zh-TW registry uses it as register-pattern reference, not fuel (TW commercial culture differs from CN 微博 ecosystem)
- **Trigger slug**: `cn-durex-huanshi-borrowed-time-meme`

## Landmark: toward-Q2

Affinity edging toward manifesto. Use when brief wants warm-but-aspirational.

### 黃春明 Huang Chun-ming (zh-TW | Q3 toward-Q2)

- **Era**: 1935 born; 1960s-ongoing
- **Primary sources**: 《兒子的大玩偶》/《莎喲娜啦‧再見》/《看海的日子》
- **Voice signature**:
  - Humane-vernacular-compassion register
  - 鄉土 + 悲憫 hybrid
  - 1980s 鄉土文學 → 吳念真 廣告 lineage
- **LLM corpus depth**: MEDIUM
- **Over-mimic risk**: LOW
- **Documented co-generation with 吳念真**: both emerged from 《兒子的大玩偶》 film nexus (Hou Hsiao-hsien 1983) — aesthetic alignment documented; NOT direct discipleship
- **Cross-cultural equivalents**: Raymond Carver (EN) / 向田邦子 domestic (JP)
- **Trigger slug**: `zh-tw-huang-chun-ming-humane-vernacular`

### 三毛 San Mao (zh-TW | Q3 toward-Q2)

- **Era**: 1943-1991; 《撒哈拉的故事》(1976) / 《雨季不再來》
- **Voice signature**:
  - Lyrical-travel-romantic register
  - 漂泊 + 抒情 hybrid
  - 1980s 中港台 mass readership; persistent reprint + 橄欖樹 song lineage
- **LLM corpus depth**: DEEP (1980s 大中華圈 canon)
- **Over-mimic risk**: MEDIUM (Sahara / Jose motifs leak)
  - Mitigation: "no Sahara / Jose imagery; borrow travel-lyric cadence only"
- **Trigger slug**: `zh-tw-san-mao-lyrical-travel-romantic`

## Landmark: toward-Q4

Affinity edging toward peer-helpful reasoning. Use when brief wants warm-and-useful hybrid.

### (Thin native corpus — see zh-q4-anchors.md)

zh-TW Q3 toward-Q4 edge is thin in active library; PChome / MOMO / 統一 peer-advocate registers primary home is [zh-q4-anchors.md](zh-q4-anchors.md). When brief wants Q3-warmth bridged into peer-reasoning, cross-load zh-q4 center landmark.

## Cross-references

External anchors usable for zh-TW Q3 briefs:

- **JP Q3 STRONG cross-ref** (per meta-detail verified map):
  - 向田邦子 domestic-intimacy-with-bite → TW 家庭 register 直承
  - 糸井重里 state-proposal → TW 文青消費 底色
  - 吉本ばなな gentle-grief-domestic → safer alt
  - 坂元裕二 conversational-aphorism → drama-dialogue template
  - 谷川俊太郎 clear-child-cosmic → poetic compression template
- **CN cross-ref**: 杜蕾斯 (already in extreme landmark above); 江小白 Q3-adjacent but flagged as LLM anti-pattern (文案瓶 對仗情緒 易被 LLM 過度 mimick)
- **HK cross-ref**: 金庸 wuxia niche only — use with **HIGH+++ over-mimic mitigation** per meta-core registry
- **EN Q3 MEDIUM via translation**: MailChimp / Innocent Drinks / Nora Ephron warm-wit / George Saunders compassionate-absurd
