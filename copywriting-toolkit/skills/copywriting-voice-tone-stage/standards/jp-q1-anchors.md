---
title: JP Voice Anchors — Q1 Authority-Reason (Router Index)
tier: 2
schema_version: router-v1
migrated_date: 2026-04-21
---

# Q1 Authority-Reason — JP Anchor Router

**Load scope**: Phase 6 Pass 3 Register Signal branch, when `voice_quadrant.primary == "Q1"` AND `brief.output_language == "ja"`. Router index — Pass 3 reads landmark section matching `voice_quadrant.position`, then loads the named `anchor-*.md` file for full voice body.

## Overview

Q1 = Authority × Reason. 制度的・思考優先. Schwartz most-aware 層と相性がよい (Level 5 は Phase 5 hard rule 禁止).

**Cross-ref**: JP Q1 は zh-TW Q1 へ STRONG に流入 (天声人語 → 聯合報「黑白集」/ 東洋経済 → 天下雜誌 parallel).

**Inclusion criterion reminder** (v2): voice anchor = individual creator. Institutional / rotating-author newspapers + magazines + wire services have migrated to `docs/format-templates/` as format references; Pass 3 does NOT load them as voice anchors.

## Landmark: center

Canonical expert + trusted authority register.

### JP Q1 center — individual creators (v1.11.0 filled)

- **池上彰 — 解説ジャーナリズム** (journalist, NHK 出身, 1950-) — [anchor-jp-ikegami-akira-kaisetsu-journalism.md](anchor-jp-ikegami-akira-kaisetsu-journalism.md)
  - Slug: `jp-ikegami-akira-kaisetsu-journalism`
  - Register: わかりやすさ解説 + 和文和訳 + 擬人化直接話法; 素朴な疑問起点 + 中立ジャーナリスト境界
  - ⚠ Over-mimic MEDIUM: 「つまり/たとえば」接続詞乱発 + 擬人化過多 + 幼稚童話調 drift

- **養老孟司 — 口述→整文 intellectual register** (解剖学者, 東大名誉教授, 1937-) — [anchor-jp-yoro-takeshi-baka-no-kabe.md](anchor-jp-yoro-takeshi-baka-no-kabe.md)
  - Slug: `jp-yoro-takeshi-baka-no-kabe`
  - Register: バカの壁 / 一元論批判 / 身体論 + 口述ヘッジ助詞「〜わけです」「〜と思います」+ 具体身体→抽象概念の一気跳躍 + 一行タウトロジー punchline
  - Secondary landmark: toward-Q2 (一元論批判 manifesto edge)
  - ⚠ Over-mimic MEDIUM-HIGH: 2000s-2010s 新書ブーム 濫用 register. Mitigation: 身体の具体観察を 1 段落に 1 つ置く
  - `safe_substitute_for: [原研哉]` — 知性的 authority 要件で Q2 manifesto の重さを避けたい brief

**Moved out to format templates** (v1.6.0):
- 朝日新聞「天声人語」rotating 論説委員 → [../../../../docs/format-templates/jp-tensei-jingo-compressed-essay.md](../../../../docs/format-templates/jp-tensei-jingo-compressed-essay.md)
- 東洋経済 / 日経ビジネス rotating editorial → [../../../../docs/format-templates/jp-toyo-keizai-nikkei-analytical-editorial.md](../../../../docs/format-templates/jp-toyo-keizai-nikkei-analytical-editorial.md)

## Landmark: extreme

Authority × Reason maximum. 温度ゼロ, narrative ゼロ.

### JP Q1 extreme — thin native-creator pool

Original v1 entries were wire-service / institutional editorial; both migrated out (rotating-author criterion). For pure-JP extreme-authority register:

**Moved out to format templates** (v1.6.0):
- ロイター日本語版 wire format → [../../../../docs/format-templates/jp-reuters-wire-zero-warmth.md](../../../../docs/format-templates/jp-reuters-wire-zero-warmth.md)
- 日経新聞 社説 / 春秋 policy-editorial format → [../../../../docs/format-templates/jp-nikkei-shasetsu-policy-editorial.md](../../../../docs/format-templates/jp-nikkei-shasetsu-policy-editorial.md)

Strategy: select Q1 toward-Q2 (夏目漱石) for authorial voice + use wire or social format template from `format-templates/` for structural requirement.

## Landmark: toward-Q2

Authority edging toward emotional manifesto register.

- **夏目漱石 — 余裕派 / ironic-observer** (novelist, 1867-1916) — [anchor-jp-soseki-yoyu-ha-dry-observer.md](anchor-jp-soseki-yoyu-ha-dry-observer.md)
  - Slug: `jp-soseki-yoyu-ha-dry-observer`
  - Register: 余裕派 + 低徊趣味 + 写生文; 漢文調 / 美文調 / 写生文調 / 翻訳調 の使い分け
  - ⚠ Over-mimic MEDIUM: 「〜である」archaic grammar leak (meta-core mitigation). Mitigation: 現代口語文法のみ; 観察的距離のみ borrow.

## Landmark: toward-Q4

Authority edging toward peer-helpful register.

- **伊丹十三 — 軽妙洒脱** (essayist + film director, 1933-1997) — [anchor-jp-itami-juzo-keimyou-shadatsu.md](anchor-jp-itami-juzo-keimyou-shadatsu.md)
  - Slug: `jp-itami-juzo-keimyou-shadatsu`
  - Register: 軽妙洒脱 + しなやかで軽い独特な文体 + 日本における "essay" 導入者; coolness × 国際的感覚 × 教養という名の背骨

## Cross-references

JP Q1 brief 使用可能な external anchor:

- **EN Q1**: David Ogilvy (`anchor-en-david-ogilvy-*`) / Claude Hopkins (`anchor-en-claude-hopkins-*`) / George Orwell (`anchor-en-george-orwell-*`) — translation corpus 経由で MEDIUM
- **zh-TW Q1**: format-templates + register-references fill most Q1-authority registers (institutional-rotating pool); individual-creator zh-TW Q1 currently gap-flagged in `docs/voice-library-gaps-v2.md`
- **EN translation 参照**: Hemingway iceberg (`anchor-en-hemingway-*`) を EN-adjacent の spare-authority に (Q1↔Q4 edge)

## Migration history (audit trail)

- **v1.0-v1.4.x**: aggregate `jp-q1-anchors.md` with 6 entries inline (天声人語 + 東洋経済/日経ビジネス + ロイター + 日経社説 + 夏目漱石 + 伊丹十三)
- **v1.5.0**: Phase A Layer 1 v2 rewrites for 夏目漱石 / 伊丹十三 in `docs/voice-anchor-deep-dives/`
- **v1.6.0** (this file): 2 individual-creator v2 entries moved to standards/ as flat `anchor-*.md`; 4 institutional/wire entries moved to `docs/format-templates/`; this file becomes router index
