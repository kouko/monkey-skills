---
title: Voice Library Recast Audit — Individual-Creator Principle
date: 2026-04-21
schema_version_target: v2.0
---

# Voice Library Recast Audit

Applies v2 inclusion criterion: **voice anchor = individual creator with identifiable sentence-level register across body of work**. Institutional / brand / campaign / platform entries either recast to their individual creator, or move out of voice library.

## Summary counts

- Total anchors audited: ~80 (excluding SKIP notes / pointer entries / gap placeholders / cross-ref-only)
- **✅ KEEP as-is** (already individual): 47
- **🟡 RECAST** (institutional → individual creator): 20
- **❌ MOVE OUT** (cannot recast, no single creator): 26

Result: voice library shrinks from ~105 to ~67 valid entries; 26 moves to `format-templates/` or `register-references/`.

## Per-file classification

### jp-q1-anchors.md

| Anchor | Type | Decision | Recast target |
|---|---|---|---|
| 朝日新聞「天声人語」 | institutional column (rotating) | ❌ MOVE OUT | format-templates/ |
| 東洋経済 / 日経ビジネス | institutional magazine | ❌ MOVE OUT | format-templates/ |
| ロイター日本語版 Reuters JP | wire service | ❌ MOVE OUT | format-templates/ |
| 日経新聞 社説 / 春秋 | institutional | ❌ MOVE OUT | format-templates/ |
| 夏目漱石 余裕派 | author | ✅ KEEP | — |
| 伊丹十三 軽妙洒脱 | essayist + film director | ✅ KEEP | — |

### jp-q2-anchors.md

| Anchor | Type | Decision | Recast target |
|---|---|---|---|
| MUJI 原研哉 era | brand-era → design director | 🟡 RECAST | 原研哉 |
| JR東海「そうだ 京都、行こう。」 | campaign → individual CW | 🟡 RECAST | 太田恵美 (v1.3.3 corrected) |
| 寺山修司 言葉の錬金術師 | poet / playwright | ✅ KEEP | — |
| 谷崎潤一郎『陰翳礼讃』 | author | ✅ KEEP | — |
| 川端康成『雪国』| author | ✅ KEEP | — |

### jp-q3-anchors.md

| Anchor | Type | Decision | Recast target |
|---|---|---|---|
| 向田邦子 真打ち随筆 | essayist + screenwriter | ✅ KEEP | — |
| 坂元裕二 言葉の魔術師 | screenwriter | ✅ KEEP | — |
| 谷川俊太郎 詩のことば | poet | ✅ KEEP | — |
| 宮沢賢治 心象スケッチ | author | ✅ KEEP | — |
| 吉本ばなな 大胆な省略 | author | ✅ KEEP | — |
| 梅田悟司 ジョージア | named copywriter | ✅ KEEP | — |
| SoftBank 白戸家 | campaign (佐々木宏 + 澤本嘉光) | 🟡 RECAST | 佐々木宏 OR 澤本嘉光 (需 disambiguate) |
| Craft-gate pointer 糸井重里 | already in craft-lineage | ✅ KEEP | — |

### jp-q4-anchors.md

| Anchor | Type | Decision | Recast target |
|---|---|---|---|
| クックパッド つくれぽ文化 | platform | ❌ MOVE OUT | format-templates/ |
| 北欧、暮らしの道具店 | brand | 🟡 RECAST (if trackable) | 青木耕平 founder? TBD |
| ジャパネットたかた 高田明 | named founder | ✅ KEEP | — |
| 通販生活 一点主義 | magazine institutional | ❌ MOVE OUT | format-templates/ |
| UNIQLO LifeWear | brand | 🟡 RECAST | 佐藤可士和 AD? TBD |
| ワークマン SNS era | platform / aggregate | ❌ MOVE OUT | format-templates/ |

### zh-q1-anchors.md

| Anchor | Type | Decision | Recast target |
|---|---|---|---|
| 天下雜誌 CommonWealth | magazine | ❌ MOVE OUT | register-references/ (殷允芃 era note preserved) |
| 報導者 The Reporter center | non-profit media | ❌ MOVE OUT | register-references/ (何榮幸 recast possible but register is team) |
| 研之有物 Research @ Sinica | institutional platform | ❌ MOVE OUT | format-templates/ |
| 報導者 investigative extreme | same as above | ❌ MOVE OUT | format-templates/ |
| 商業周刊 Business Weekly | magazine | ❌ MOVE OUT | register-references/ (金惟純 era note preserved) |

**zh-q1 result**: ALL currently institutional → 0 kept in voice library. New zh-q1 anchors needed from individual-author pool (e.g. Taiwan essayists writing analytical long-form: 龍應台, 南方朔, 楊照?).

### zh-q2-anchors.md

| Anchor | Type | Decision | Recast target |
|---|---|---|---|
| 中興百貨 brand-era | 許舜英 creative lead | 🟡 RECAST (collapse) | 許舜英 (already in craft-lineage) |
| 誠品書店 brand-era | 李欣頻 creative lead | 🟡 RECAST (collapse) | 李欣頻 (already in craft-lineage) |
| 左岸咖啡館 brand-era | 葉明桂 strategy | 🟡 RECAST (collapse) | 葉明桂 (already in craft-lineage) |
| 朱家鼎 Mike Chu Titus | individual ECD | ✅ KEEP | — |
| 王家衛 Wong Kar-wai | screenwriter / director | ✅ KEEP | — |
| 錢鍾書《圍城》 | author | ✅ KEEP | — |
| 白先勇 | author | ✅ KEEP | — |
| 曾錦程 KC Tsang | individual ECD | ✅ KEEP | — |
| 張愛玲 Eileen Chang | author | ✅ KEEP | — |
| 朱天文 Chu Tien-wen | author / screenwriter | ✅ KEEP | — |

### zh-q3-anchors.md

| Anchor | Type | Decision | Recast target |
|---|---|---|---|
| 全聯 TV-era 格言體 | campaign → named ECD | 🟡 RECAST | 龔大中 (already in craft-gate) |
| 吳念真 保力達B 系列 | named CW + VO | ✅ KEEP | — |
| 胡湘雲 大眾銀行系列 | named CD | ✅ KEEP | — |
| 故宮粉絲團「朕知道了」 | institutional SNS (rotating 小編) | ❌ MOVE OUT | format-templates/ |
| 台灣吧 Taiwan Bar | dual founders | 🟡 RECAST (if one dominant) OR OUT | 謝政豪 / 蕭宇辰 disambiguate needed |
| 杜蕾斯官微 CN | agency operating 2011-2017 | 🟡 RECAST | 金鵬遠 (環時互動 founder) |
| 黃春明 Huang Chun-ming | author | ✅ KEEP | — |
| 三毛 San Mao | author | ✅ KEEP | — |

### zh-q4-anchors.md

| Anchor | Type | Decision | Recast target |
|---|---|---|---|
| PChome / MOMO 購物專家 | platform distributed | ❌ MOVE OUT | format-templates/ |
| 7-ELEVEN OPEN 將 | IP mascot | ❌ MOVE OUT | format-templates/ |
| 全聯 SNS post-2020 | platform distributed | ❌ MOVE OUT | format-templates/ |
| 蝦皮 Shopee / 雙11 | platform | ❌ MOVE OUT | format-templates/ |
| Pinkoi 商品故事 | platform (crowdsourced designers) | ❌ MOVE OUT | format-templates/ |

**zh-q4 result**: ALL institutional / platform. 0 kept. Need individual CW anchors for zh-TW Q4 (TW direct-response CW tradition is thin — may genuinely need cross-ref to JP/EN).

### en-q1-anchors.md

| Anchor | Type | Decision | Recast target |
|---|---|---|---|
| David Ogilvy Rolls-Royce/Hathaway | named copywriter | ✅ KEEP | — |
| AMV BBDO Economist | agency (David Abbott individual chairman-CW) | 🟡 RECAST | David Abbott |
| BMW Ultimate — Ammirati Puris | campaign | 🟡 RECAST (if one dominant CW trackable) | TBD (Martin Puris?) |
| Economist brand voice | institutional | ❌ MOVE OUT | register-references/ |
| WebMD / Reuters / Bloomberg | institutional wire/reference | ❌ MOVE OUT | format-templates/ |
| Bill Bernbach DDB VW Think Small | named ECD | ✅ KEEP | — |
| Basecamp Rework — Fried + DHH | named author duo | ✅ KEEP (collapse w/ en-q4 entry) | — |
| John McPhee | author | ✅ KEEP | — |
| Hemingway | author | ✅ KEEP | — |
| Raymond Carver | author | ✅ KEEP | — |
| Amy Hempel | author | ✅ KEEP | — |
| Strunk & White | named author duo | ✅ KEEP | — |
| Orwell | author | ✅ KEEP | — |

### en-q2-anchors.md

| Anchor | Type | Decision | Recast target |
|---|---|---|---|
| Apple "Think Different" | campaign (TBWA) | 🟡 RECAST | Lee Clow OR Steve Hayden (CW) |
| Nike "Just Do It" center | campaign (Wieden+Kennedy) | 🟡 RECAST | Dan Wieden |
| Patagonia "Don't Buy This Jacket" | brand stance | 🟡 RECAST | Yvon Chouinard? or Patagonia CW TBD |
| Extinction Rebellion Declaration | movement | ❌ MOVE OUT | register-references/ (mitigation-only) |
| Nike "Dream Crazy / Crazier" | campaign | 🟡 RECAST | Wieden+Kennedy team (ECD TBD) |
| Patek Philippe Generations | campaign (Leagas Delaney) | 🟡 RECAST | Tim Delaney CW |
| Absolut Vodka print | campaign (TBWA) | 🟡 RECAST | Richard Costello / Geoff Hayes |
| BMW Ultimate Q2 edge | campaign (duplicate) | — | same as en-q1 |
| Oatly activist — Schoolcraft | named CD | ✅ KEEP | — |
| Toni Morrison | author | ✅ KEEP | — |
| James Baldwin | author | ✅ KEEP | — |
| Kazuo Ishiguro | author | ✅ KEEP | — |
| Joan Didion | author | ✅ KEEP | — |

### en-q3-anchors.md

| Anchor | Type | Decision | Recast target |
|---|---|---|---|
| MailChimp Voice & Tone | brand style guide | 🟡 RECAST | Kate Kiefer Lee |
| Innocent Drinks 1999-2009 | brand wackaging | 🟡 RECAST | Richard Reed |
| Oatly center — Schoolcraft | named CD | ✅ KEEP | — |
| Nora Ephron | writer | ✅ KEEP | — |
| Raymond Carver Q3-edge | duplicate from en-q1 | — | consolidate |
| Steak-umm — Allebach | already individual | ✅ KEEP | — |
| Duolingo Parvez 2021-2022 | already individual | ✅ KEEP | — |
| Phoebe Waller-Bridge Fleabag | writer / screenwriter | ✅ KEEP | — |
| Liquid Death punk-peer | brand | 🟡 RECAST (if founder CW trackable) | Mike Cessario? |
| George Saunders | author | ✅ KEEP | — |
| Taika Waititi | screenwriter / director | ✅ KEEP | — |
| Greta Gerwig | screenwriter / director | ✅ KEEP | — |
| Dollar Shave Club 2012 launch | single CW writer | 🟡 RECAST | Michael Dubin (founder + writer) |
| Gary Halbert peer-edge | duplicate from en-q4 | — | consolidate |
| Anton Chekhov | author | ✅ KEEP | — |

### en-q4-anchors.md

| Anchor | Type | Decision | Recast target |
|---|---|---|---|
| Amazon product copy | distributed / platform | ❌ MOVE OUT | format-templates/ |
| REI expert-advice | brand | ❌ MOVE OUT | format-templates/ |
| Basecamp Rework center — Fried+DHH | named duo | ✅ KEEP (consolidate en-q1) | — |
| IKEA assembly voice | institutional | ❌ MOVE OUT | format-templates/ |
| Gary Halbert Boron Letters | named CW | ✅ KEEP | — |
| Bill Jayme direct-mail | named CW | ✅ KEEP | — |
| Morning Brew | brand | 🟡 RECAST | Alex Lieberman / Austin Rief |
| Stratechery — Ben Thompson | named writer | ✅ KEEP | — |
| Hopkins reason-why | named CW (Claude Hopkins) | ✅ KEEP | — |
| Raymond Chandler | author | ✅ KEEP | — |
| Dashiell Hammett | author | ✅ KEEP | — |

## Aggregate

- **Definite KEEP individual**: 向田 / 坂元 / 谷川 / 宮沢 / 吉本 / 梅田 / 夏目 / 伊丹 / 寺山 / 谷崎 / 川端 / 高田明 / 許舜英 / 李欣頻 / 葉明桂 / 朱家鼎 / 王家衛 / 錢鍾書 / 白先勇 / 曾錦程 / 張愛玲 / 朱天文 / 吳念真 / 胡湘雲 / 黃春明 / 三毛 / Ogilvy / Bernbach / McPhee / Hemingway / Carver / Hempel / Strunk & White / Orwell / Morrison / Baldwin / Ishiguro / Didion / Schoolcraft / Ephron / Saunders / Waititi / Gerwig / Chekhov / Halbert / Jayme / Hopkins / Thompson (Stratechery) / Chandler / Hammett / Waller-Bridge / Allebach / Parvez = ~52 KEEP

- **RECAST candidates** (~18-20): 原研哉, 太田恵美, 佐々木宏, 青木耕平, 金惟純, 龔大中 (already in craft-gate), 謝政豪, 金鵬遠, David Abbott, Martin Puris, Lee Clow, Dan Wieden, Yvon Chouinard, Tim Delaney, Richard Costello, Kate Kiefer Lee, Richard Reed, Mike Cessario, Michael Dubin, Alex Lieberman

- **MOVE OUT** (~25): 天声人語, 東洋経済, 日経ビジネス, Reuters JP, 日経社説, クックパッド, 通販生活, ワークマン, 天下雜誌, 報導者, 研之有物, 商業周刊, 故宮粉絲團, PChome, 7-ELEVEN OPEN 將, 全聯 SNS, Shopee, Pinkoi, Economist brand voice, WebMD / Reuters / Bloomberg, XR Declaration, Amazon product copy, REI, IKEA assembly voice

## Migration plan

### Phase A (v1.4.0) — ship the already-individual ~52 as v2 schema

- No recast work needed for these
- Prioritize migration of the 5 pilot KEEPs (坂元, 梅田, 宮沢, Mike Chu, KC Tsang) as first-batch proof

### Phase B (v1.5.0+) — recast 18-20 individual-identifiable candidates

- Research each recast target for Layer 1 content (individual's corpus, not brand's campaigns)
- New anchor file entries under recast target's name
- Original brand entry moves to `format-templates/` as secondary artifact

### Phase C (v1.6.0) — move-out cleanup

- Create `copywriting-toolkit/docs/format-templates/` for institutional / template / platform entries
- Create `copywriting-toolkit/docs/register-references/` for movements / documented campaigns / publications
- Move 25 move-out entries; preserve content but out of voice library path
- Pass 3 SKILL.md updated: no longer loads these files

### Phase D (v1.7.0+) — fill new-anchor gaps

- zh-Q1 has 0 individual anchors after audit → need new research on individual zh-TW essayists / long-form authors
- zh-Q4 has 0 individual anchors → TW DR tradition genuinely thin; may keep cross-ref to JP/EN Q4 as primary
- Document gaps in `docs/voice-library-gaps-v2.md`

## Open questions

1. **Craft-gate master integration**: 許舜英 / 李欣頻 / 葉明桂 already exist deeply in `zh-copy-craft-lineage.md`. After collapse of brand-era entries (中興百貨 / 誠品 / 左岸), those brand entries become pointers to craft-lineage only. Should craft-lineage file itself migrate to v2 schema? **Decision deferred**.

2. **Dual-author entries**: Strunk & White, Fried + DHH, 謝政豪 + 蕭宇辰 (台灣吧). Treat as single anchor with dual attribution, or split?

3. **Era-boundary entries**: 全聯 TV-era (→ 龔大中) vs 全聯 SNS post-2020 (distributed). Split clear: first recasts, second moves out.

4. **Schwartz Level 5 concerns**: moving out narrative-entry anchors might reduce Phase 5 hard-rule infrastructure for Level-5 audiences. Verify that recasts preserve narrative-entry options.

5. **Cross-reference integrity**: meta-detail cross-reference-valid-for mappings point to specific anchors. After recasts / move-outs, cross-refs need re-mapping.
