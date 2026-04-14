# Grounding Research — v4.18.2 Brand × Copy Restructure

**Date**: 2026-04-15
**Scope**: Support restructure of voice-quadrant-positioning.md from
Copywriter × Copy to Brand × Copy axis. Two research clusters
informed the per-brand entry template and specific brand-entry
content.

## Research Method

2 parallel research agents:
1. Industry brand-voice documentation structural patterns
2. Canonical sustained-voice brand case studies

---

## Cluster 1: Industry Brand-Voice Document Best Practices

### Sources Examined

- **Mailchimp Voice and Tone Guide** (styleguide.mailchimp.com)
- **18F Content Guide** (content-guide.18f.gov)
- **gov.uk Style Guide**
- **Slack Voice and Tone** (api.slack.com + slack.design)
- **Intercom PREACH framework**
- **Skyscanner Tone of Voice**
- **WARC Case Finder**
- **D&AD The Copy Book**
- **TCC コピー年鑑** (東京コピーライターズクラブ)
- **Aaker 1997** "Dimensions of Brand Personality" (*JMR*)
- **NN/g** four dimensions of tone of voice

### Convergent Structural Patterns

1. **TCC年鑑 dual-axis indexing** (validates Brand × Copy primary):
   - 作品 organized by award year
   - Both クリエイター索引 (copywriter index) AND 広告主索引 (brand
     index) provided
   - Brand-centric and copywriter-centric views coexist via
     cross-indexing — NOT either/or
   - Source: tcc.gr.jp/yearbook/

2. **Slack "X, never Y" paired qualifiers** for voice attributes:
   - "confident, never cocky"
   - "witty, but never silly"
   - Self-documents counter-examples in the same line
   - Prevents voice drift without requiring separate do/don't blocks
   - Source: slack.design/articles/thevoiceofthebrand-5principles/

3. **Voice (constant) vs Tone (variable) separation**:
   - Universal pattern across Mailchimp, 18F, Intercom, Slack
   - Voice = stable brand persona
   - Tone = situational register variation

4. **Eras handled as dated tags WITHIN one entry**, NOT separate
   sub-entries:
   - Industry convention: Apple Think Different is a CAMPAIGN case
     study, not "Apple voice v2.0"
   - Historical narration + dated work-samples carrying the era tag

5. **WARC-style structured metadata per work-sample**:
   - Year, market, campaign objective, channel
   - Enables faceted retrieval

6. **Bilingual gap**:
   - All major industry references are EN-only
   - For EN/JP/ZH trilingual corpus, we must invent the convention
   - Proposed: original-language sample + market/era tag; functional
     gloss only where translation aids comprehension; do NOT
     auto-translate canonical copy

### Recommended Per-Brand Entry Template

```
**Brand Name** (sector; market; Agency-of-record)

- Voice statement: [1-sentence identity]
- Voice attributes (3-5, paired qualifiers):
  - X, never Y
- Copywriter(s): [primary + AD where relevant; cross-ref]
- Canonical corpus (dated work samples):
  - "Line 1" (campaign, year, channel)
  ...
- Era narration: [optional inline, if voice shifted]
- Tone-by-context note: [optional]
```

---

## Cluster 2: Canonical Sustained-Voice Brand Case Studies

### Brands Researched (8 deep-dives)

EN (3): MUJI, Apple, Patagonia
JP (2): Hobonichi (ほぼ日刊イトイ新聞), JR九州
TW (3): 全聯福利中心, 誠品書店, 左岸咖啡館

### Stability Rankings (Benchmark Suitability)

| Tier | Brands | Rationale |
|------|--------|-----------|
| HIGH | MUJI, Apple, Patagonia, Hobonichi, 全聯 (post-2015), 左岸 | Strongest single-voice-across-decades benchmarks |
| MEDIUM | JR九州 (1990s era), 誠品 (1990s 李欣頻 era) | Voice strong in one era but uncertain post-era |

### Critical Fact-Check Flags

1. **JR九州 attribution correction**:
   - Previously-assumed line 「夢とか、決意とか...」 is NOT in TCC archive
   - Verified canonical: 「愛とか、勇気とか、見えないものも乗せている。」
     (仲畑貴志, 1994)
   - **Drift #31**: swap in v4.18.2

2. **MUJI era disambiguation**:
   - "Compact Life" is post-2010 Kenya Hara product line
   - 2003 "Horizon / 地平線" (Bolivia/Mongolia) is SEPARATE campaign
   - Do not conflate — treat as distinct era markers within MUJI entry

3. **誠品 post-2010 voice**:
   - NOT benchmark-grade
   - Use only 1990s–2000s 李欣頻 era for Q2 exemplar

4. **左岸咖啡館 verification depth**:
   - Lines 3-4 from earlier research were paraphrased from secondary
     trade press
   - Primary verification requires 葉明桂《品牌的技術和藝術》(2017)
   - For v4.18.2: cite only lines verifiable via primary source
     (book or 奧美 archive)

5. **Apple "1984" copywriter**:
   - Credited to Steve Hayden (Chiat\Day)
   - For era-attribution in Apple brand entry

### Published Voice Documentation (Primary Source Strength)

Brands with PUBLISHED voice docs (citation-grade primary source):

| Brand | Primary voice-doc source |
|-------|-------------------------|
| MUJI | Kenya Hara *Designing Design* (Lars Müller, 2007) |
| Patagonia | Yvon Chouinard *Let My People Go Surfing* (Penguin, 2005) |
| Hobonichi | 1101.com daily corpus, 1998–present |
| 誠品 | 李欣頻《廣告副作用》+《誠品副作用》(1998) |
| 左岸咖啡館 | 葉明桂《品牌的技術和藝術》(2017) |
| Apple | No published voice doc; TBWA\MAL institutional memory |
| 全聯 | No published voice doc; 奧美 / 龔大中 case writings |
| JR九州 | No published voice doc; TCC年鑑 only |

---

## Brand Entries — Synthesized for Implementation

### Q1 Authority-Reason

**The Economist** (publisher; global; agency-of-record varies)
- Voice statement: Intelligent, rigorous, wry — respects the
  reader's intelligence.
- Voice attributes: informed, never preachy / witty, never glib /
  global, never parochial
- Copywriter(s): multiple agencies (AMV BBDO most notable)
- Canonical corpus:
  - "White van man reads The Economist." (AMV BBDO, 1988–, billboard)
  - "Never a dull page." (brand tagline)
  - "Think. More intensely." (2010s campaign)

**報導者 The Reporter** (nonprofit journalism; Taiwan; in-house)
- Voice statement: Public-interest investigative journalism voice;
  authority through evidence, not opinion.
- Voice attributes: rigorous, never sensational / transparent, never
  evasive
- Copywriter(s): in-house editorial (founded by 何榮幸, 2015)
- Canonical corpus: editorial style; less a single-line corpus

### Q2 Authority-Emotion

**MUJI 無印良品** (retail; JP/global; 1980s AD 田中一光 × copy 小池一子)
- Voice statement: Wabi-sabi minimalism — utility without ornament,
  aesthetic through restraint.
- Voice attributes: philosophical, never preachy / minimal, never cold
  / universal, never generic
- Copywriter(s): 小池一子 (1980s foundational), later Kenya Hara
  (art direction, 2002–)
- Canonical corpus:
  - "わけあって、安い。" (1980, foundational slogan)
  - "愛は飾らない。" (1981, 田中一光 AD)
  - "自然、当然、無印。" (1983, revived globally 2014)
  - "しゃけは全身しゃけなんだ。" (c.1980, product copy)
- Era narration: 1980s foundational era under 小池一子/田中一光;
  2002– global era under Kenya Hara adds product-lifestyle imagery
  but voice remains stable. "Compact Life" (post-2010) and 2003
  "Horizon / 地平線" (Bolivia/Mongolia) are distinct campaigns within
  the same voice.

**Apple** (tech; global; TBWA\Chiat\Day 1997–; TBWA\Media Arts Lab 2006–)
- Voice statement: Manifesto voice — celebrating those who challenge
  the status quo; products as tools for creators.
- Voice attributes: visionary, never grandiose / confident, never
  boastful / simple, never dumbed-down
- Copywriter(s): Lee Clow team (CCO); Rob Siltanen, Craig Tanimoto
  (Think Different 1997); Steve Hayden ("1984")
- Canonical corpus:
  - "1984" Macintosh Super Bowl ad (Steve Hayden / Chiat\Day, 1984)
  - "Here's to the crazy ones. The misfits. The rebels. ..."
    (Think Different manifesto, 1997, 60-second cut)
  - "Think Different." (tagline, 1997–2002)
  - "1000 songs in your pocket." (iPod, 2001, drift toward Q1/Q4)
  - "Shot on iPhone." (campaign, 2015–, democratic creativity)
- Era narration: Pre-1997 inconsistent; 1997–2011 Think Different era
  sets canonical voice; post-Jobs (2011–) drifts toward product-
  functional register but rallying-cry moments still resurface.

**Patagonia** (outdoor retail; global; founder-led voice)
- Voice statement: Anti-consumption activism through product-grade
  honesty — the brand is a vehicle for environmental values.
- Voice attributes: committed, never sanctimonious / plain-spoken,
  never folksy / activist, never opportunistic
- Copywriter(s): Yvon Chouinard author-voice; in-house team
- Canonical corpus:
  - "Don't Buy This Jacket." (NYT full-page, Black Friday 2011)
  - "We're in business to save our home planet." (2018 mission
    statement rewrite)
  - *Let My People Go Surfing* (Chouinard, 2005 — book as canonical
    voice doc)

**誠品書店 Eslite** (bookstore; Taiwan; 李欣頻 copy, 1990s–2000s)
- Voice statement: Literary humanism — reading as identity, bookstore
  as cultural institution.
- Voice attributes: reflective, never pedantic / aspirational, never
  aspirational-in-a-bad-way / meditative, never sleepy
- Copywriter(s): 李欣頻 (10+ years from敦南店 opening)
- Canonical corpus:
  - "我在閱讀中，遇見另一個自己。"
  - "拋開阿莫多瓦的高跟鞋到街上去。拋開村上春樹的彈珠遊戲到街上去。"
    (誠品敦南店; inspired by 寺山修司《拋開書本到街上去》)
  - Full series extends with 徐四金、彼得梅爾 etc.
- Era narration: 1990s–2000s 意識形態 era sets canonical voice;
  post-2010 voice fragments, use only 1990s corpus as benchmark.

**左岸咖啡館** (RTD coffee; Taiwan; 奧美/葉明桂 strategy, 統一企業)
- Voice statement: Parisian narrative world — product as access to a
  literary state of being.
- Voice attributes: poetic, never purple / contemplative, never vacant
  / evocative, never opaque
- Copywriter(s): 奧美 Taiwan team under 葉明桂 strategic direction
- Canonical corpus:
  - "我不在咖啡館，就在去咖啡館的路上。" (borrowed from Peter
    Altenberg, sinicized)
  - "我在這裡，找到一個角落，一個上午，一杯 Cafe au lait。
    Cafe au lait 一如記憶裡的模糊地帶。這是春天的最後一天，我在
    左岸咖啡館。"
- Strategic brief (Q1-strategy level, 葉明桂):
  - "我們現在不是在賣咖啡，我們是在經營一家咖啡館。" (documented
    in《品牌的技術和藝術》)
- Voice-doc source: 葉明桂《品牌的技術和藝術》(2017)

### Q3 Affinity-Emotion

**全聯福利中心 PX Mart** (retail; Taiwan; 奧美 Taiwan / 龔大中,
2015–)
- Voice statement: Thrift is dignity — observational wit elevates
  frugality to aesthetic.
- Voice attributes: playful, never mocking / thrifty, never cheap /
  observational, never snide
- Copywriter(s): 龔大中 (奧美 Taiwan CCO, 2020–; ECD 2014–)
- Canonical corpus:
  - "長得漂亮是本錢，把錢花得漂亮是本事。" (經濟美學, 2015)
  - "知道一生要去的20個地方之後，我決定先去全聯。" (經濟美學)
  - "當不成名模，日子也要過得有模有樣。" (全聯潮包, 2016)
  - "省錢就像白T牛仔褲，永不退流行。" (經典篇, 2017)
- Era narration: Pre-2015 voice was generic retail; 2015 經濟美學
  campaign establishes the canonical voice. Post-2015 sustained.

**ほぼ日刊イトイ新聞** (publisher/brand; JP; 糸井重里 direct author)
- Voice statement: Daily observation as brand practice — author
  identity IS brand identity.
- Voice attributes: warm, never syrupy / curious, never intrusive /
  considered, never precious
- Copywriter(s): 糸井重里 (founder/primary author); see
  `jp-copy-craft-lineage.md §糸井` for voice deep-dive
- Canonical corpus:
  - Daily essays on 1101.com (1998–present) — corpus is the voice
    doc itself
  - "いつもの場所で、いつもの人と。" (ほぼ日 brand tagline, varied)
- Era narration: consistent since 1998 founding; extraordinarily
  stable voice due to single-author continuity.

**Dove (Real Beauty)** (personal care; global; Ogilvy / Unilever,
2004–)
- Voice statement: Real-bodies activism — beauty as confidence, not
  as anxiety.
- Voice attributes: affirming, never saccharine / inclusive, never
  performative / honest, never preachy
- Copywriter(s): Ogilvy (primarily Düsseldorf + London)
- Canonical corpus:
  - "Fat or Fab?" (2004 launch billboard prompt)
  - "Wrinkled or Wonderful?" (2004)
  - "You're more beautiful than you think." (Real Beauty Sketches,
    2013)
  - Foundational insight: ~2% of women consider themselves beautiful
- Era narration: 2004 launch → 2013 Real Beauty Sketches evolution →
  ongoing; voice-doc stable across 20+ years.

**JR九州** (rail; JP; 九州旅客鉄道 / agency of record varies)
- Voice statement: 旅情 (travel reverie) — movement as emotional
  geography.
- Voice attributes: evocative, never decorative / gentle, never
  sentimental
- Copywriter(s): 仲畑貴志 (1990s era)
- Canonical corpus:
  - "愛とか、勇気とか、見えないものも乗せている。" (仲畑貴志,
    1994 — TCC年鑑 verified; CORRECTION from earlier mis-attribution)
- Era narration: 1990s era strong; post-1990s voice less documented.

### Q4 Affinity-Reason

**蝦皮購物 Shopee** (e-commerce; Taiwan/SEA; in-house + agency mix)
- Voice statement: Conversion-optimized playfulness — every line
  has a job.
- Voice attributes: direct, never blunt / witty, never flippant /
  urgent, never pushy
- Copywriter(s): in-house + agency rotation
- Canonical corpus:
  - "今天下單，明天脫單。" (Valentine's 2020)
  - "月初囤棉最便宜。" (2021 金句獎)

**Amazon** (e-commerce; global; in-house brand voice)
- Voice statement: Customer obsession expressed as frictionlessness —
  remove doubt between want and have.
- Voice attributes: clear, never curt / confident, never pushy /
  direct, never transactional
- Copywriter(s): in-house brand team
- Canonical corpus:
  - "Earth's most customer-centric company." (mission statement)
  - Product detail conventions (one-click, "also bought", subscribe
    & save) as voice artifacts

**UNIQLO** (retail; JP/global; 佐藤可士和 art direction; copy
in-house)
- Voice statement: LifeWear — clothing as infrastructure for everyday
  living.
- Voice attributes: functional, never cold / universal, never generic
- Copywriter(s): in-house team; 佐藤可士和 art direction (2006–) is
  NOT copywriter (see v4.18.1 §Cluster B-5)
- Canonical corpus:
  - "From Tokyo to New York." (SoHo flagship launch, 2006 —
    positioning banner, AD: 佐藤可士和)
  - "LifeWear" (brand tagline, 2013–)

---

## Attribution Corrections Applied (drifts)

### Drift #31 (v4.18.2) — JR九州 canonical line correction

Previously-assumed "夢とか、決意とか..." is NOT TCC-archive-verified.
Canonical verified line is **仲畑貴志 1994 「愛とか、勇気とか、
見えないものも乗せている。」**. Swap in v4.18.2 brand entry.

### Drift Summary (cumulative)

- #25 (v4.18.0): FCB + SFL combination = team synthesis
- #26 (v4.18.0): 廣告樂血研究院 naming correction
- #27 (v4.18.0): 詹宏志 scope exclusion (editor, not copywriter)
- #28 (v4.18.0): ZH micro-indicators = team heuristics
- #29 (v4.18.1): 眞木準 sole attribution for 「恋を何年」
- #30 (v4.18.1): MUJI all 小池一子 (not Kodama Kunio)
- **#31 (v4.18.2)**: JR九州 line = 仲畑貴志 1994 「愛とか、勇気とか」
  (NOT 「夢とか、決意とか」)
