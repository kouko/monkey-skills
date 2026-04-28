# Voice Anchor Deep Dives

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

**目的**：依 `docs/anchor-schema-v2.md` 規範存放的 Layer 2/3 研究 artifact。Pass 3 不會載入這些檔案；它們存在的目的是供 audit / provenance / 未來 deep-dive 研究擴充。

## Layer 切分（依 `anchor-schema-v2.md`）

| Layer | 位置 | 由誰消費 | 內容 |
|---|---|---|---|
| **Layer 1**（voice body）| `skills/copywriting-voice-tone-stage/standards/anchor-{slug}.md` | Pass 3（hot path）| Voice direction / Native critical read / Prose mechanics / Examples / Don't / Metadata — Pass 3 重寫 draft 為該 voice 所需要的欄位 |
| **Layer 2/3**（research）| `docs/voice-anchor-notes/{slug}.md`（本資料夾）| Audit / evaluator rationale（optional）/ 未來研究者 | 完整研究筆記 / 一手來源 URL & ISBN / 傳記與時代脈絡 / 獎項時間軸 / 評論史 / 已記錄的 lineage 影響 + 被淘汰候選的研究軌跡（v1.13.1 從原 voice-anchor-deep-dives + voice-anchor-research-notes 整併而來）|

## 目前狀態（v1.6.1）

本資料夾裡的全部 64 個檔案都是 v1.6.0 移轉時的 Layer 1 v2 條目 **凍結快照**（commit `b9b1c39`, scaffolding-cleanup 之後）。內容上與 `standards/` 中對應的 `anchor-{slug}.md` 檔案完全相同 — 但**容許隨時間發散**, 因為 Layer 2/3 研究會擴充每一條：

- 傳記時間軸
- 時代脈絡（周邊文化 / 政治 / 市場條件）
- `Native critical read` 中已引用的評論之外, 完整的一手來源 bibliography
- 獎項 / 認可歷史
- 已記錄的 lineage（誰影響了誰, 帶具體訪談 / 信件 / 學術 citation）
- 評論史辯論（關於該 register 邊界的學術爭論）

## 檔名 convention

當前（v1.6.1）：`pilot-layer1-v2-{creator-slug}.md`（歷史命名, 從 v1.4-v1.5 pilot 期間保留）。

未來（v1.7.0+）：隨著 deep-dive 研究擴充每一條, 改名為 `{trigger-slug}.md`（與 Layer 1 anchor slug 對齊）— 屆時檔名對齊讓 audit tooling 更簡單。

## 怎麼使用本資料夾

- **Pass 3**：MUST NOT load。`standards/anchor-{slug}.md` 的 Layer 1 是 Pass 3 唯一來源。
- **Dimension 6 evaluator**（voice-consistency-gate）：當 over-mimic 判斷需要 Layer 1 沒承載的傳記 / 時代 / lineage 脈絡時, MAY 在 rationale 中選擇性引用某條 deep-dive。
- **人類研究者**：隨研究進展, 用新的傳記 / 時代 / lineage 發現擴充任何條目。即使 Layer 1 slug 變了也讓檔名穩定（或同步 — 擇一紀律即可）。
- **Commit 紀律**：Layer 1 anchor 更新與 Layer 2/3 deep-dive 更新是**獨立 commit** — 不要混在一起。Layer 1 變更影響 production（Pass 3 行為）；Layer 2/3 變更影響 audit。

## 誤刪歷史（v1.6.0 → v1.6.1）

v1.6.0 移轉時意外刪除了本資料夾（與 64 個檔案）, 起因是 pilot 檔案被 `git mv` 進 `standards/`。原意是把 Layer 1 body 從 pilot 位置移走, 但 Layer 2/3 的 **seed material** 與資料夾本身原本應保留。v1.6.1 從 commit `b9b1c39`（刪除前快照）逐字還原全部 64 個檔案。

這些檔案目前是未來 Layer 2/3 研究的 **seed material**。尚未進行任何 deep-dive 研究 — 每個檔案目前只承載 Layer 1 schema。這是起點, 不是終點。
