# Skill Judge

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 用 8 個維度組成的 rubric（0–120 分 + A〜F 的 grade）為
> SKILL.md 評分，並指出該修哪裡 — 量的是真正的 expert 知識密度，
> 而不是表面工整。

使用者主動 invoke 的 **evaluation skill**：當你手上有 draft 或已 ship
的 SKILL.md，想知道它是真的承載 expert 知識，還是只是把 Claude 已經
知道的東西重新壓縮一遍時，就 invoke 這個 skill，得到含各維度分數、
Critical Issues、優先順序改進建議的結構化 report。

這份 README 是給在 GitHub 上閱讀本 skill 的人類看的。Claude 真正
load 的 operational 檔案是 [`SKILL.md`](SKILL.md)。

---

## 為什麼有這個 skill

**重複出現的失敗模式**：多數 skill 都在浪費 token。作者本想「教
Claude 關於 X」，最後寫成 tutorial — 解釋 PDF 是什麼、怎麼寫
for-loop、一般 best practice（「寫 clean code」、「處理 error」）。
這些都是 Claude 已經有的內容。context window 是共享資源，redundant
內容會把真正重要的部分擠出去。

作者自己很難可靠地察覺這件事。skill *感覺起來*很有幫助，因為解釋
寫得清楚。只有用「這內容模型已經有了嗎？」當尺去量，浪費才會浮現。

這個 skill 把那把尺的量法捕捉下來。核心 formula：

> **Good Skill = Expert-only Knowledge − What Claude Already Knows**

SKILL.md 的每個 section 被分類為：

- **Expert** — Claude 真的不知道；這是價值所在
- **Activation** — Claude 知道，但提醒一下有幫助
- **Redundant** — Claude 一定知道；該刪除

好的 skill Expert 比例 >70%。差的 skill Expert <40%，後面跟著一長串
redundant 的 tutorial 內容。

---

## 怎麼運作

這個 skill 對任何 SKILL.md 套用由 8 個維度組成的 rubric（共 120 分），
輸出：

```
Total: X/120 (X%)  →  Grade A / B / C / D / F
Pattern: Mindset / Navigation / Philosophy / Process / Tool
Knowledge Ratio: E:A:R = X:Y:Z

Dimension scores:
  D1 Knowledge Delta          (20)  ← 最核心的維度
  D2 Mindset + Procedures     (15)
  D3 Anti-Pattern Quality     (15)  ← 含 WHY 的具體 NEVER list
  D4 Spec Compliance          (15)  ← description 品質（WHAT/WHEN/KEYWORDS）
  D5 Progressive Disclosure   (15)
  D6 Freedom Calibration      (15)
  D7 Pattern Recognition      (10)
  D8 Practical Usability      (15)

Critical Issues + Top 3 Improvements
```

rubric 取材自 17 個以上的 Anthropic 官方 skill 觀察出來的 pattern，
加上 9 個典型失敗模式（"The Tutorial"、"The Dump"、
"The Orphan References"、"The Invisible Skill" 等），每個都附具體
修補建議。

---

## 何時用

- ship 前 review SKILL.md draft
- audit 「感覺怪怪的」既存 skill
- 用一致基準比較兩個 skill 的 design quality
- 透過實際套 rubric 學習 skill design 原則

## 何時不用

- **Behavioral / runtime testing** — 用
  [`skill-creator-advance`](../skill-creator-advance/)
  （它有 eval-loop，含 test prompt 與 quantitative assertion）
- **domain-team skill 的 convention 強制** — 用
  domain-team structural convention gates
  （對 monkey-skills convention 的 PASS/FAIL gate：4-tier gate
  hierarchy、3-commit split、primary-source grounding、~6,000-token
  cap）
- **一般 code review** — 工具不對

三個 skill 是互補關係：

| Skill                                             | Mode      | Output                         |
|---------------------------------------------------|-----------|--------------------------------|
| `skill-judge`（本 skill）                         | Static    | 0–120 advisory score           |
| `skill-dev-toolkit:skill-creator-advance`              | Behavioral| test prompt 的 pass/fail       |
| structural convention gates                         | Structural| convention gate 的 PASS/FAIL   |

一個 skill 可以通過 structural convention gates 的 gate，卻在 `skill-judge` 拿 D
（沒有 convention 違規，但內容大多 redundant）。也可以在
`skill-judge` 拿 A，卻在 structural convention gates 失敗（內容很好，但 directory
layout 不對）。它們量的是不同的東西。

---

## monkey-skills domain-team skill 的 adaptation

評估 `domain-teams/skills/{team}/` 底下的 skill 時，rubric 套用一個
小的 adaptation：

- **D7 Pattern Recognition**：domain-team skill 依結構特徵符合
  upstream 的 **Process** pattern（phased workflow + checkpoint +
  medium freedom）。行數是 correlate 不是 criterion — domain-team
  skill 設計上會超過 upstream typical 行數，不因此扣分。
- **D4 / D5 supplementary check**：domain-team structural gates 的 `CHK-SKL-001`
  （description 40–200 字）和 `CHK-SKL-010`（~6,000-token cap）失敗
  時，在 report 列為 **Critical Issues**，但評分本身仍依 upstream
  rubric，不引入任意 cap。
- **重點維度**：D4/D5/D8 已被 structural convention gate 部分 cover，在 gate
  已通過的情況下，D1/D3/D6 帶來最多新增價值。

完整細節見 [`SKILL.md` §Adaptation for monkey-skills domain-team skills](SKILL.md)。

---

## Attribution

本 skill 改寫自
[`softaworks/agent-toolkit`](https://github.com/softaworks/agent-toolkit/tree/main/skills/skill-judge)
（MIT、Copyright (c) 2026 Leonardo Flores），upstream 提供由 8 個
維度組成的 rubric、E:A:R 知識分類、evaluation protocol、9 種典型
失敗模式。

kouko 的 modifications：依 skill-dev-toolkit plugin convention 改寫
frontmatter；新增 "Adaptation for monkey-skills domain-team skills"
section；插入 sibling skill 的 cross-reference 釐清 scope。完整
upstream chain 與 modification 摘要見 [`NOTICE`](NOTICE)，dual-
copyright header 見 [`LICENSE`](LICENSE)。
