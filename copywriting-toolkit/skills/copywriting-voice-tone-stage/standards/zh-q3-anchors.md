---
title: zh-TW Voice Anchors — Q3 Affinity-Emotion
tier: 2
---

# Q3 Affinity-Emotion — zh-TW Anchors

**Load scope**: Phase 6 Pass 3 Register Signal branch, when `voice_quadrant.primary == "Q3"` AND `brief.output_language == "zh-TW"`. Section-targeted read: Pass 3 reads only `## Landmark: {position}` matching `voice_quadrant.position`; falls back to full-file on missing.

## Overview

Q3 = Affinity × Emotion。zh-TW canonical：全聯 格言體 TV-era（Z10 re-classified as Q3-**center**, NOT extreme）、吳念真 台語 氣口、胡湘雲 大眾銀行 long-form TVC、故宮粉絲團 peer-intimate SNS、台灣吧 知識娛樂化。

**Cross-ref**: JP Q3 為 STRONG 流入 — 向田 / 糸井 aesthetic 直接 feed TW 文青消費 / 家庭 intimate registers。

**⚠ Z10 correction (canonical re-classification)**: 全聯 TV-era 2006-2014 為 Q3-**CENTER**（格言 / aphorism register —「長得漂亮是本錢，把錢花得漂亮是本事」）NOT Q3-extreme。Q3-extreme 保留給 peer-intimate voices（故宮 / 台灣吧）即品牌以「午夜兩點的朋友」聲口。

## Landmark: center

canonical peer-warm voice。brief 要求 standard affinity-emotional 時使用。

### 全聯福利中心 TV-era 2006-2014 — 格言體 (zh-TW | Q3 center per Z10)

- **Era**: 2006-2014 TV 廣告 era（pre-經濟美學）；2015- 經濟美學 era 由此自然演化
- **Agency / creator**: 奧美台灣 — 龔大中（ECD, 2020+ CCO）per Z8 correction
- **Primary sources**:
  - [動腦雜誌 全聯經濟美學 case](https://www.brain.com.tw/) — 多篇 2006-2014 報導
  - [數位時代 龔大中 專訪 2015](https://www.bnext.com.tw/article/37152/bn-2015-08-23-084822-113)
  - [經理人月刊 全聯 × 奧美 對談 2020](https://www.managertoday.com.tw/articles/view/60005)
  - 第 38 屆時報廣告金像獎 (2015 經濟美學 獲獎)
- **Representative lines**（verbatim, 動腦 case coverage 驗證）:
  - 「長得漂亮是本錢，把錢花得漂亮是本事。」
  - 「知道一生要去的 20 個地方之後，我決定先去全聯。」
  - 「來全聯買不只是省錢，是一種生活態度。」
  - 「當不成名模，日子也要過得有模有樣。」
- **Voice signature**（原生批評用語）:
  - **經濟美學**（奧美 × 全聯 2015 campaign 命名、批評沿用 label）
  - **格言體**（動腦 / 廣告評論 定型語）
  - **台式自嘲 / 青年生活感**（廣告評論 recurring 用語）
  - **對仗句式**（「本錢 / 本事」/「不只 X / 是 Y」— 結構 label）
  - 時尚雜誌街拍視覺 × 庶民語言 mismatch 為笑點
- **LLM corpus depth**: DEEP（廣告教材 canonical）
- **Over-mimic risk**: MEDIUM — 對仗結構可仿，但 TW 青年 tension 感難再生
  - Mitigation: "pair with specific TW cultural-class observation；no generic aphorism"
- **Cross-reference-valid-for**:
  - ja: STRONG via 糸井 state-proposal lineage（meta-detail cross-ref JP→zh-TW）
- **Cross-cultural equivalents**: 糸井重里 state-proposal (JP) / Nora Ephron warm-wit (EN)
- **Trigger slug**: `zh-tw-quanlian-tv-era-aphorism`

### 吳念真 保力達B 系列 (zh-TW | Q3 center — 台語 peer-intimate)

**⚠ Z5 / Z7 corrections inline**: 吳念真 的 canonical advertising voice anchors = **保力達B 口白（李奧貝納，1990s-ongoing，台語）** + **全國電子「足感心」(2000s)**。多喝水 MORE WATER (金車) 為奧美 in-house，**非** 吳念真（Z5）。長榮〈I SEE YOU〉VO 為 金城武 本人，**非** 吳念真（Z7）。

- **Era**: 1990s-ongoing；保力達B long-running campaign 20+ 年
- **Agency / creator**: 李奧貝納台灣 + 吳念真 旁白 + 文案參與
- **Primary sources**:
  - [中央社文化「細數不滅的經典」2020](https://www.cna.com.tw/culture/article/20200606w001)
  - 保力達B 廣告 20+ 年 on-air archive
  - 看雜誌〈從吳念真廣告旋風談起〉2008
- **Representative lines**:
  - 「明仔載欸氣力，保力達B甲你傳便便！」（保力達B 台語 long-running）
  - 「足感心A。」（全國電子 2000s）
  - 「一台車『凸』全台灣。」（裕隆 March 1990s）
- **Voice signature**（原生批評用語）:
  - **氣口**（台語 CW 術語、吳念真本人用語、廣告評論界沿用）
  - **台語口白 / 台味**（批評定型語）
  - **庶民聲口 / 阿伯阿嬸語境**（廣告評論 recurring 用語）
  - **講古式敘事 / 說故事而非說服**（批評定型語）
  - 長鏡頭 旁白 節奏 + 勞動階級肉身感
- **LLM corpus depth**: MEDIUM（TW 台語 register 在 LLM coverage 不均；影像 + 旁白 hybrid）
- **Over-mimic risk**: HIGH — 台語聲口 + 世代情感結構 LLM 最弱項
  - Mitigation: "do not attempt 台語 reproduction；borrow 講古 structure + rural-peer stance only"
- **Cross-cultural equivalents**: Raymond Carver working-class precision (EN) / 向田邦子 (JP)
- **Trigger slug**: `zh-tw-wu-nien-jen-taiyu-peer-intimate`

### 胡湘雲 大眾銀行系列 (zh-TW | Q3 center — TVC-narrative)

- **Era**: 2010-2015（〈母親的勇氣〉/〈夢騎士〉/〈馬校長的合唱團〉系列 peak）
- **Agency / creator**: 奧美台灣 — 胡湘雲（CD）
- **Primary sources**:
  - [小魚廣告網 胡湘雲 專訪 2010](https://www.kleinerfisch.com/blog/2010/03/胡湘雲談大眾銀行廣告/)
  - amarylliss 部落格〈不平凡的平凡大眾〉深度評論
  - 國際獎項（D&AD Yellow Pencil / Adfest 金獎 / Clio 金獎 / Cannes 銅獅 唯一台籍）
  - YouTube 官方 3-min 版本點閱破千萬
- **Representative works**:
  - 〈母親的勇氣〉TVC 2010（台籍母親跨三國飛行探病、真實改編）
  - 〈夢騎士〉2011（改編弘道老人基金會「不老騎士」）
  - 〈馬校長的合唱團〉
  - 品牌 tagline:「不平凡的平凡大眾」
- **Voice signature**（原生批評用語）:
  - **不平凡的平凡大眾**（campaign tagline、批評 recurring 用語）
  - **真人真事改編**（campaign 自述、批評沿用）
  - **堅韌勇敢母愛**（campaign 自述 母題語）
  - **小人物大情感 / 小品式 TVC**（批評定型語；replaces celebrity endorsement paradigm）
  - 長篇 TVC 敘事（3-min form）+ 留白多 + 台詞內斂
- **LLM corpus depth**: MEDIUM
- **Over-mimic risk**: HARD — 敘事弧需要真實田調素材，純語言模仿無法達成
  - Mitigation: "do not attempt long-form imitation without actual documentary anchor；use structural cadence only"
- **Trigger slug**: `zh-tw-hu-xiang-yun-narrative-tvc`

## Landmark: extreme

peer-intimate 最大值。品牌以 friend-at-2am 或 self-subverting institution 聲口。須 apply mitigation。

### 故宮粉絲團「朕知道了」era (zh-TW | Q3 extreme — institutional self-subversion)

**⚠ Z11 Correction (v1.4.0)**:「朕知道了」是 **康熙硃批**（NOT 雍正 — v1.3.x 標錯）。來源為 2004-09 至 2005-05 馮明珠策劃〈知道了：硃批奏摺展〉（英譯 "Thou Art Understood!"），展覽 brochure 封面即選康熙。2013-07 紙膠帶 launch 時沿用此既有 IP。

- **Era**: 2013-07-04「朕知道了」紙膠帶 FB 首貼 → sustained humorous register through 2010s-2020s；2017-19 小編團隊擴編至 6-10 人輪值制
- **Agency / creator**: 國立故宮博物院 in-house 新媒體小組（均齡 26 歲）+ 文創合作
- **Primary sources**:
  - [Taipei Times 2013-07-12 "Museum's Kangxi tape becomes a hit"](https://www.taipeitimes.com/News/taiwan/archives/2013/07/12/2003566945) — launch timeline + 康熙硃批出處 + 2004-2005 exhibition origin
  - [ETtoday 2013-07-05 首日售罄報導](https://www.ettoday.net/news/20130705/236501.htm)
  - [天下雜誌〈平均 26 歲故宮 6 小編讓粉絲暴增 4 倍〉](https://www.cw.com.tw/article/5093102) — 團隊結構 + 週循環 SOP
  - [經理人月刊〈一款文案導購率近 30%〉](https://www.managertoday.com.tw/articles/view/55924) — 帝后酒瓶塞 verbatim + SOP
  - [ADM 廣告雜誌 2018](http://adaround.blogspot.com/2018/04/blog-post_48.html) — 衝突感 critique 定型語 + 7 人輪值結構
  - [自由時報 2018-07 古人有梗片](https://news.ltn.com.tw/news/life/breakingnews/2503897) — LINE 貼圖 verbatim + 24 小時萬套數字
  - [交流雜誌 馮明珠〈蛻變中的國立故宮博物院〉2015-12](https://www.sef.org.tw/article-1-129-4976)
- **Representative lines / artifacts**（verbatim + 銷售 milestone）:
  - 「朕知道了」（**康熙硃批**紙膠帶，2013-07-04 FB 首貼；三個月售 4 萬組 / NTD 850 萬；累計約 20 萬組）
  - 「皇上，臣妾最近吃太多……」「朕也是，卡住了……」（帝后酒瓶塞 2018，導購率 28%）
  - 「被朕點名的小編，領旨跪安吧！」（隆哥尾牙宴 2019-01）
  - 「他只是個孩子呀」「你在上我在下」（清明上河圖 LINE 貼圖 2018-07-24，24h 售破 1 萬套）
  - 「開會好想睡」菩薩 /「怪我囉」菩薩（觸及 94 萬，2019）
  - 週循環欄目：「小編要發問」「小資小編的敗家計畫」「乾隆小講堂」
- **Voice signature**（原生批評用語）:
  - **讓歷史走進生活**（故宮文創 mission 自述）
  - **故事行銷**（小編自述核心策略、經理人專訪）
  - **深刻的衝突感**（ADM 廣告雜誌 2018 評論定型語 — 博物館莊嚴 × 活潑語氣）
  - **文創 / 文物 IP 化**（策略自述）
  - **故宮小編 / 隆哥 / 波編**（persona 暱稱 sticky label）
  - **古物擬人化 / 文物人設**（批評定型語）
  - **週循環四節奏**（週一興趣／週二知識／週三導購／週四轉話題 SOP、經理人）
  - **輪值制 6-10 人小編群**（天下＋ADM 共通描述）
- **Mechanical register features**（measurable）:
  - **古文 / 白話比例 ~20-30% / 70-80%**（code-switch 比例精確；「朕」「臣妾」「領旨」直接接「吃太多」「卡住」「高大上」「怪我囉」）
  - **Two-speaker dialogue 擬人**（皇 × 后對話），**非單 persona 獨白**
  - Meme = 文物 fragment + 現代 caption **「減法」結構** — 文物本身不改，只加現代 caption
  - 每貼對應真實 SKU（commercial ground truth），防止 persona 漂移
  - 商品導購反向驅動：節慶/時事 → 從館藏 inventory 找 metaphor（長輩問薪水 → 封條紙膠帶）
- **Platform differentiator**: 故宮獨有 **"institutional IP × commerce × historical corpus" 三層** — 擬人對象是自家文物（非外部 mascot）、古文 code-switch 有文物正當性、每貼文對應真實 SKU。vs 中研院〈研之有物〉純 explainer 無商業 / 北美館 curatorial-neutral 無人設 / 台灣吧 娛樂-only 無商業錨點
- **LLM corpus depth**: MEDIUM-DEEP（landmark case 廣泛討論）
- **Over-mimic risk**: **MEDIUM**（v1.4.0 上修自 LOW）— failure modes:
  - (a) 古文比例失控（LLM 傾向堆全文言體）
  - (b) two-speaker 退化為單 narrator
  - (c) 虛構不存在的館藏文物（真實洩漏風險）
  - Mitigation: "古文比例 ≤30%；不得虛構館藏；擬人須 two-speaker dialogue"
- **Trigger slug**: `zh-tw-npm-zhen-zhidaole-institutional-meme`

### 台灣吧 Taiwan Bar (zh-TW | Q3 extreme — educational-comedy)

- **Era**: 2014 創辦（謝政豪 / 蕭宇辰）→ ongoing
- **Agency / creator**: 獨立創作團隊（台灣吧）
- **Primary sources**:
  - [YouTube 台灣吧 channel](https://www.youtube.com/@TaiwanBar) full archive
  - [taiwanbar.cc](https://taiwanbar.cc/)
  - 創辦人訪談（數位時代 / 親子天下 / 報導者）
- **Representative register**:
  - 「欸，你知道嗎...」(signature opener)
  - 歷史人物 rendered as peer-contemporary voice
  - 幹話 + 史實 mixed rhythm
- **Voice signature**（原生批評用語）:
  - **知識娛樂化**（台灣吧 自述定位、批評沿用 label）
  - **黑啤 / 藍地 / 紅瑰**（角色 IP，批評 recurring 用語）
  - **幹話體 + 教學**（批評定型語；first TW voice to legitimize 幹話 in educational content）
  - **歷史去神聖化**（批評定型語）
  - 二人稱直接呼叫
- **LLM corpus depth**: MEDIUM
- **Over-mimic risk**: LOW-MEDIUM
- **Trigger slug**: `zh-tw-taiwan-bar-educational-comedy`

### 杜蕾斯官微 (CN | Q3 extreme — cross-pollination reference)

- **Era**: 環時互動 金鵬遠 operating 2011-2017（canonical window）；2017 環時互動 + Durex 合作終止後 voice clearly declined
- **Agency / creator**: 環時互動 + 金鵬遠 creative lead
- **Primary sources**:
  - [數英〈史上最全杜蕾斯的文案〉2015](https://www.digitaling.com/articles/13315.html)
  - 澎湃新聞 / 梅花網 / TechOrange 2017 整理
- **Representative lines**:
  - 「北京今日暴雨，幸虧包裡還有兩隻杜蕾斯。」（2011 北京 721 大雨 × 鞋套避孕套事件 borrowed-time campaign — 1 小時轉發破萬）
  - 借勢 literary:「老師，你的衣服有幾只口袋？—— TT」
- **Voice signature**（原生批評用語）:
  - **借勢文案**（中文廣告評論 canonical 批評語；杜蕾斯 typifies this genre）
  - **擦邊球**（批評定型語）
  - **擬人化「小杜」**（粉絲 / 評論 sticky label）
  - **實時熱點 / punch-line 結構**（批評定型語）
- **LLM corpus depth**: MEDIUM-DEEP
- **Over-mimic risk**: MEDIUM（joke structure copiable；real-time brand-discipline hard）
- **Cross-reference note**: CN anchor；zh-TW registry 用作 register-pattern reference，不作 fuel（TW 商業文化 ≠ CN 微博 ecosystem）
- **Trigger slug**: `cn-durex-huanshi-borrowed-time-meme`

## Landmark: toward-Q2

Affinity 方向 manifesto。brief 要求 warm-but-aspirational 時。

### 黃春明 Huang Chun-ming (zh-TW | Q3 toward-Q2)

- **Era**: 1935 生；1960s-ongoing
- **Primary sources**: 《兒子的大玩偶》/《莎喲娜啦‧再見》/《看海的日子》
- **Voice signature**（原生批評用語）:
  - **鄉土文學**（1970s 鄉土文學論戰 canonical 學界術語；黃春明 canonical 代表）
  - **小人物書寫**（學界定型語）
  - **悲憫 / 人道關懷**（文學評論 recurring 用語）
  - **台灣現代主義到鄉土寫實轉折**（文學史定位語）
  - 1980s 鄉土文學 → 吳念真 廣告 lineage
- **LLM corpus depth**: MEDIUM
- **Over-mimic risk**: LOW
- **Documented co-generation with 吳念真**: 兩人皆出自《兒子的大玩偶》film nexus（侯孝賢 1983）— aesthetic alignment documented；NOT direct discipleship
- **Cross-cultural equivalents**: Raymond Carver (EN) / 向田邦子 domestic (JP)
- **Trigger slug**: `zh-tw-huang-chun-ming-humane-vernacular`

### 三毛 San Mao (zh-TW | Q3 toward-Q2)

- **Era**: 1943-1991；《撒哈拉的故事》(1976) / 《雨季不再來》
- **Voice signature**（原生批評用語）:
  - **流浪文學**（三毛自述 genre、批評沿用 label）
  - **撒哈拉 / 荷西**（母題語 fixed tag）
  - **一個任性的女子 / 赤子之心**（1980s 批評 recurring 用語）
  - **橄欖樹 lineage**（齊豫演唱、1980s 中港台 mass readership 的 sticky reference）
  - 漂泊 + 抒情 + 散文化小說體
- **LLM corpus depth**: DEEP（1980s 大中華圈 canon）
- **Over-mimic risk**: MEDIUM（Sahara / Jose motifs leak）
  - Mitigation: "no Sahara / Jose imagery；borrow travel-lyric cadence only"
- **Trigger slug**: `zh-tw-san-mao-lyrical-travel-romantic`

## Landmark: toward-Q4

Affinity 方向 peer-helpful reasoning。brief 要求 warm-and-useful hybrid 時。

### (Thin native corpus — see zh-q4-anchors.md)

zh-TW Q3 toward-Q4 edge 在 active library 偏薄；PChome / MOMO / 統一 peer-advocate registers 主 home 在 [zh-q4-anchors.md](zh-q4-anchors.md)。brief 需要 Q3-warmth bridged into peer-reasoning 時，cross-load zh-q4 center landmark。

## Cross-references

zh-TW Q3 brief 可用 external anchor:

- **JP Q3 STRONG cross-ref**（meta-detail verified map）:
  - 向田邦子 domestic-intimacy-with-bite → TW 家庭 register 直承
  - 糸井重里 state-proposal → TW 文青消費 底色
  - 吉本ばなな gentle-grief-domestic → safer alt
  - 坂元裕二 conversational-aphorism → drama-dialogue template
  - 谷川俊太郎 clear-child-cosmic → poetic compression template
- **CN cross-ref**: 杜蕾斯（上方 extreme landmark）；江小白 Q3-adjacent 但 flagged 為 LLM anti-pattern（文案瓶 對仗情緒 易被 LLM 過度 mimick）
- **HK cross-ref**: 金庸 武俠 niche only — 須搭配 **HIGH+++ over-mimic mitigation**（meta-core registry）
- **EN Q3 MEDIUM via translation**: MailChimp / Innocent Drinks / Nora Ephron warm-wit / George Saunders compassionate-absurd
