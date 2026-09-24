# Example fragments (obsidian-research)

Fragments of one note, showing the exact form of the parts SKILL.md Step 5 fixes: frontmatter, the conclusion and TOC, a claim with confidence, the method section, and source entries. Everything else — chapter names, order, length — comes from the topic and the vault's recent notes, not from here. Claims, figures, and URLs are placeholders.

Topic: a Taiwan market, user writing in 繁中 → 繁中 primary + English + 日本語; the note is in 繁中.

**Frontmatter** (vault without its own convention):

```yaml
---
title: 台灣電動機車換電網路的普及現況
type: research
date: 2026-09-23
tags: [research, electric-scooter, taiwan]
status: completed
source_count: 11
source_languages: [zh-TW, en, ja]
---
```

**Conclusion, summary, TOC** (TOC targets copy the headings exactly):

```markdown
> 📌 換電網路在都會區已足以支撐日常通勤，但補助退場後的新車銷量是未來兩年的主要變數。

換電站密度在六都已高於一般通勤距離所需 [1][3]。成長放緩的主因是購車補助縮減，而不是站點不足 [2][5]。

## 目錄

- [[#一、市場規模與站點密度|市場規模與站點密度]]
- [[#二、補助政策與銷量|補助與銷量]]
- [[#來源清單|來源清單]]
```

**A claim with confidence**:

```markdown
- 偏鄉覆蓋仍有缺口 [4] — **信心度 Medium**（只有一份地方新聞，反向查證未找到反例）
```

**Method and limitations**:

```markdown
- 研究角度：站點、補助、營運商、使用者評價、日本比較；缺口檢查補上「時間」（補助退場時程）
- 查證：關鍵說法 9 條，被推翻或過時 1 條
- 引用核對：查 64 項，不符 7 項（來源掛錯 5、原文不支持 2），已改正或刪除
- 日文來源只有試點新聞，缺乏使用數據；業者公告占來源三成，可能偏樂觀
```

**Source entries**:

```markdown
1. 電動機車換電站統計 — 交通部 — https://example.com/1 — zh-TW — accessed 2026-09-23
8. 電動バイク電池交換の実証事業 — 経済産業省 — https://example.com/8 — ja — accessed 2026-09-23; mirror: https://example.com/8m
```
