# Grounding Research — v4.18.1 Voice Quadrant Rebalance

**Date**: 2026-04-15
**Scope**: Verify canonical ad copy samples to replace thin sample
inventory in v4.18.0. Also verify attribution corrections for
existing entries. Support the language-compliance fix (EN-only
framework labels).

## Research Method

3-cluster parallel WebSearch verification. Every added copy sample
must have a verification URL; unverified samples are excluded with
explicit flag.

---

## Cluster A: EN Canonical Ad Corpus

### A-1. Ogilvy Rolls-Royce (1958) — VERIFIED with wording fix

- **Exact canonical headline**: "At 60 miles an hour the loudest
  noise in **this** new Rolls-Royce comes from the electric clock."
  (Fix: v4.18.0 draft said "the new" — canonical is "this new")
- **Model**: Rolls-Royce Silver Cloud (companion Bentley S-series)
- **Year**: 1958
- **Agency**: Ogilvy, Benson & Mather (pre-1965 rename to Ogilvy & Mather)
- **Placement**: *The New Yorker* and *The New York Times*
- **Origin**: Ogilvy wrote 26 candidate headlines; line adapted from
  *The Motor* magazine. Sales rose ~50% in 1958.
- Source: https://swiped.co/file/rolls-royce-ad-by-david-ogilvy/
- Source: https://adland.tv/rolls-royce-david-ogilvy-loudest-noise-comes-electric-clock-1958/

### A-2. Apple "Think Different" (1997) — VERIFIED full text

**Full canonical text** (60-second TV, "Crazy Ones"):

> "Here's to the crazy ones. The misfits. The rebels. The
> troublemakers. The round pegs in the square holes. The ones who
> see things differently. They're not fond of rules. And they have
> no respect for the status quo. You can quote them, disagree with
> them, glorify or vilify them. About the only thing you can't do
> is ignore them. Because they change things. They push the human
> race forward. While some may see them as the crazy ones, we see
> genius. Because the people who are crazy enough to think they
> can change the world, are the ones who do."

- **Year**: September 28, 1997
- **Agency**: TBWA\Chiat\Day
- **Creative team**: Lee Clow (CCO), Rob Siltanen (copywriter),
  Craig Tanimoto (art director). Authorship contested between
  Siltanen and Clow's team — cite as "TBWA\Chiat\Day team led by
  Lee Clow" for safety.
- **Narrators**: Richard Dreyfuss (broadcast); Steve Jobs recorded
  version aired posthumously.
- Source: https://www.cultofmac.com/apple-history/apple-think-different-ad-campaign
- Source: https://www.thecrazyones.it/spot-en.html

### A-3. Nike "Just Do It" (1988) — Q2 classification confirmed

- **Copywriter**: Dan Wieden (Wieden+Kennedy, Portland)
- **Origin**: Inspired by Gary Gilmore's 1977 last words "Let's
  do it." Wieden changed to "Just."
- **Q2 vs Q4 classification**: Practitioner and academic literature
  treats "Just Do It" as **Q2 (Authority+Emotion / Ideology-
  manifesto voice)**, NOT Q4 direct-action. Key evidence:
  - Branding Strategy Insider + rhetoric analyses describe as
    "cultural manifesto" and "rallying cry," not transactional CTA
  - Consumer studies: associations are "empowerment, determination,
    achievement" (emotional/ideological, not feature-rational)
  - Imperative grammar is Q4-syntactic, but brand function is
    Q2-identity (commodity activism, post-Kaepernick 2018)
- **Decision**: keep in Q2; flag the syntactic-vs-functional
  ambiguity in the standard.
- Source: https://en.wikipedia.org/wiki/Just_Do_It
- Source: https://brandingstrategyinsider.com/behind-nikes-campaign/
- Source: https://digital.library.villanova.edu/files/vudl:563882/MASTER?download=true

### A-4. Dove "Real Beauty" (2004) — VERIFIED with precision note

- **Launch year**: 2004 ("Campaign for Real Beauty")
- **Original launch**: billboard prompts like "Fat or Fab?" / "Wrinkled
  or Wonderful?"; foundational stat = ~2% of women considered
  themselves beautiful
- **Tagline "You're more beautiful than you think"**: from 2013
  "Real Beauty Sketches" evolution — NOT the 2004 launch
- **Agency**: Ogilvy (primarily Düsseldorf and London)
- **Brand owner**: Unilever
- Source: https://en.wikipedia.org/wiki/Dove_Campaign_for_Real_Beauty
- Source: https://www.ogilvy.com/ideas/dove-ogilvys-decades-long-real-beauty-campaign-wins-creative-strategy-grand-prix

---

## Cluster B: JP Canonical Ad Corpus — Critical Attribution Fixes

### B-1. 「恋を何年、休んでますか。」 — CRITICAL FIX

- **Correct attribution**: **眞木準** / 伊勢丹 / 1989
- **v4.18.0 error**: file attributed to "眞木/岩崎" hybrid — INCORRECT
- **Fix**: strip 岩崎; sole attribution is 眞木準
- Source: https://ja.wikipedia.org/wiki/%E7%9C%9E%E6%9C%A8%E6%BA%96

### B-2. MUJI (無印良品) Corpus — all 小池一子

| Copy | Year | Copywriter | AD |
|------|------|-----------|-----|
| わけあって、安い。 | 1980 | 小池一子 | 田中一光 |
| 愛は飾らない。 | 1981 | 小池一子 | 田中一光 (illust: 山下勇三) |
| 自然、当然、無印。 | 1983 (revived 2014) | 小池一子 / MUJI team | — |
| しゃけは全身しゃけなんだ。 | c.1980 | 小池一子 | — |

**Correction**: user-draft attributed しゃけ to "Kodama Kunio" —
unsupported. All 4 MUJI lines are 小池一子.

- Source: https://muji.com/jp/flagship/huaihai755/archive/koike.html
- Source: https://muji.net/lab/mujiarchive/091125.html
- Source: https://ryohin-keikaku.jp/news/2014_0416.html
- Source: https://muji.net/lab/blog/aoyama/015017.html

### B-3. 糸井重里 西武百貨店 — VERIFIED

| Copy | Year | Source |
|------|------|--------|
| じぶん、新発見。 | 1980 | ja.wikipedia.org; 1101.com |
| 不思議、大好き。 | 1981 | tcc.gr.jp/copira/id/11647/ |
| おいしい生活。 | 1982 | (already canonical in voice-and-tone.md) |

### B-4. 岩崎俊一 Extensions — VERIFIED with client corrections

| Copy | Year | Client | Correction |
|------|------|--------|-----------|
| あなたに会えた、お礼です。 | 1985 | **サントリー お歳暮ギフト** | NOT beer/whisky (gift campaign); punctuation preserves the comma |
| 幸福は、ごはんが炊かれる場所にある。 | post-2010 | **プレナス「ほっともっと」** | Smaller/regional client; lower brand recognition than ミツカン 2004 |

- Source: https://i-and-o.com/2908
- Source: https://advertimes.com/20211210/article371136/
- Source: https://sendenkaigi.com/creative/media/brain/001088/

### B-5. UNIQLO / 佐藤可士和 — EXCLUDE

- 佐藤可士和 is creative/art director, NOT copywriter
- "FROM TOKYO TO NEW YORK" (2006 SoHo flagship) is positioning
  tagline authored as art direction, not TCC-style copywriter line
- **Decision**: EXCLUDE from Q4 practitioner corpus in v4.18.1
- Source: https://uniqlo.com/jp/ja/contents/corp/press-release/2006/07/backstage_report_2006_1.html

---

## Cluster C: TW Canonical Ad Corpus — 7 INCLUDE / 2 EXCLUDE

### C-1. 葉明桂 Strategic Quote — INCLUDE (label as brief)

- **"我們現在不是在賣咖啡，我們是在經營一家咖啡館"**
- Verified as 葉明桂's documented strategic framing for 左岸咖啡館
  (奧美 Taiwan / 統一企業 brand)
- Classification: **internal strategy/brief language, not public
  slogan** — label accordingly in the standard (belongs in Q1 as
  strategist framing, not Q2 creative output)
- Source: https://www.storm.mg/lifestyle/308711
- Source: https://www.businessweekly.com.tw/careers/blog/19542

### C-2. 左岸咖啡館 Ad Copy Series

**C-2a. "我不在咖啡館，就在去咖啡館的路上" — INCLUDE with note**

- Verified as used in 左岸咖啡館 campaign (奧美 / 葉明桂 era)
- **Origin**: Peter Altenberg (Austrian writer, Café Central Vienna,
  late 19c). 左岸 sinicized/borrowed it.
- **Note for standard**: annotate as "左岸咖啡館 borrowed from Peter
  Altenberg; not original copy"
- Source: https://en.wikipedia.org/wiki/Caf%C3%A9_Central

**C-2b. "我在這裡，找到一個角落..." — INCLUDE with orthography fix**

- Exact canonical text: "我在這裡，找到一個角落，一個上午，一杯
  Cafe au lait。Cafe au lait 一如記憶**裡**的模糊地帶。這是春天
  的最後一天，我在左岸咖啡館。"
- **Orthography fix**: use 「裡」 (TW form), not 「里」 (mainland form)
- Source: https://www.digitaling.com/articles/17686.html

**C-2c. "你在左岸咖啡館，我也在左岸咖啡館..." — EXCLUDE**

- Searched Digitaling / 设计之家 文案 collections — no exact match
- Cannot verify via primary source
- **Decision**: EXCLUDE from v4.18.1

### C-3. 許舜英 中興百貨 Extended Corpus

**C-3a. "購物冷感症" — EXCLUDE**

- Exact wording "如果你在其他百貨公司得了購物冷感症，請來中興百貨
  接受治療" not surfaced in searched archives (PIXNET, Digitaling,
  動腦)
- **Decision**: EXCLUDE until primary source (e.g., 許舜英 book
  《我不是一本型錄》) confirms exact wording

**C-3b. "銀行倒閉不會令我不安，服裝店倒閉才會令我不安" — INCLUDE**

- Verified verbatim in 中興百貨 ad-copy roundup (PIXNET 2008, swbsr
  blog)
- Campaign era: 1988–2001
- Year: specific year not pinpointed (flag as "1990s, exact year
  unconfirmed")
- Source: https://swbsr.pixnet.net/blog/post/28950932

### C-4. 李欣頻 誠品 Extended — INCLUDE

- **"拋開阿莫多瓦的高跟鞋到街上去。拋開村上春樹的彈珠遊戲到
  街上去"**
- Verified in 迷誠品 (official) + everydayobject.us
- Source: 李欣頻《廣告副作用 藝文篇》, written for 誠品敦南店
- Inspiration: Terayama Shūji 寺山修司《拋開書本到街上去》
- Full series continues: "拋開徐四金的低音大提琴…拋開彼得梅爾的
  山居歲月…"
- Source: https://meet.eslite.com/tw/tc/article/202005270003
- Source: https://www.everydayobject.us/eslite-bookstore-leewriter/

### C-5. 龔大中 全聯經濟美學 Extended

**C-5a. "當不成名模，日子也要過得有模有樣" — INCLUDE**

- 2016 全聯經濟美學「全聯潮包」 campaign (奧美 / 龔大中, ECD)
- Source: https://www.brain.com.tw/news/articlecontent?ID=43078

**C-5b. "省錢就像白T牛仔褲，永不退流行" — INCLUDE**

- 2017 全聯經濟美學「經典篇」 (10位長輩走秀, 700+歲合計)
- Full copy: "有一種流行，無論大環境如何變遷，永遠不會隨時光老去。
  這，叫作經典，省錢的信念也是如此。就像白T牛仔褲，永不退流行。"
- Source: https://www.bnext.com.tw/article/view/id/37152

---

## Summary Tables

### Attribution Corrections Applied (drifts #29-30)

| # | Item | v4.18.0 state | v4.18.1 correction |
|---|------|--------------|-------------------|
| Drift #29 | 「恋を何年、休んでますか。」 | "眞木/岩崎" dual attribution | 眞木準 sole (伊勢丹 1989) |
| Drift #30 | MUJI しゃけ等 | unproposed / Kodama Kunio | 小池一子 (all 4 MUJI lines) |

### Samples INCLUDED (verified)

| Language | Samples | Count |
|----------|---------|-------|
| EN | Ogilvy Rolls-Royce, Apple Think Different full text, Dove Real Beauty (with 2004/2013 precision) | 3 new |
| JP | MUJI x4, 糸井 x2, 岩崎 サントリー + ほっともっと, 眞木 伊勢丹 (attribution-fixed) | 8 new/corrected |
| TW | 葉明桂 strategy, 左岸 x2, 許舜英 銀行倒閉, 李欣頻 拋開, 龔大中 x2 | 7 new |

### Samples EXCLUDED (unverified)

| Language | Sample | Reason |
|----------|--------|--------|
| TW | 左岸 "你在左岸咖啡館..." | No primary source confirmation |
| TW | 許舜英 "購物冷感症" | Exact wording unverified |
| JP | UNIQLO 佐藤可士和 | Art director, not copywriter |

## Standards Synthesis Plan

### Modifications to `voice-quadrant-positioning.md`

1. **Label refactor**: Q1-Q4 繁中 labels → EN only (per v4.13.1 policy)
2. **Per-quadrant structure**:
   - Positive Positioning Principle (new)
   - Linguistic markers (existing)
   - Use cases (existing)
   - Canonical Copy Corpus (EN / JP / TW verified samples — new,
     expanded from ~3 samples to 6-10 per quadrant)
   - Representative practitioners (existing, trimmed)
   - Representative brands (existing)
   - Positive Application Hints (new)
3. **Attribution fix**: drift #29 (眞木準 sole attribution for 恋を何年)
4. **Attribution add**: drift #30 (MUJI corpus = 小池一子)
5. **Anti-Patterns trim**: 10 → 3 load-bearing rules
6. **Move drift-correction items to Critical Attribution Corrections**

### Cross-file updates

- `voice-consistency-gate.md` Dim 5: Q1-Q4 label refs → EN
- `copywriting-brainstorming.md` Q6: quadrant options → EN labels
- `write-long-form-copy.md`: Schwartz × Quadrant Q3/Q4 refs aligned
- `SKILL.md` Resource Manifest: quadrant description → EN only

### Honesty Disclosures

- Drift #29 (眞木準 sole attribution for 「恋を何年」)
- Drift #30 (MUJI corpus = 小池一子, not Kodama Kunio)
- Language compliance: EN-only framework labels per v4.13.1 policy
- Nike Q2/Q4 ambiguity: kept in Q2 per brand-strategy literature;
  syntactic-vs-functional distinction noted
- Altenberg borrowing: 左岸 "不在咖啡館" annotated as borrowed
- 2 TW samples excluded (purchase cold / 你在左岸) for verification gaps
