# B — 全域 CLAUDE.md 修改提案（僅提案，未落檔）

> 日期：2026-07-06 · 狀態：**待 kouko 核准**（維護協議 §2：CLAUDE.md 只能提案）
> 落檔目標（真實路徑）：`~/dotfiles/claude/.claude/CLAUDE.md`
> （`~/.claude/CLAUDE.md` 是 symlink，直接寫會被拒）

## 前提修正（來自 A 診斷）

原 prompt 假設 CLAUDE.md 是最大 token 槓桿——證據不支持：全域＋專案共
10.4 KB，而 loom hook 注入才是主洩漏（已由 router-card PR 處理）。
因此 B 從「重寫」降級為「最小增量」：只加 rules/ 路由，不動既有條款。

## 提案 diff（+4 行，≈ +70 tokens/session）

在 `## Skill Routing` 段之後插入：

```diff
+## Rules Routing（案頭制度檔，需要時才讀）
+- 派 subagent／選 model・effort／升降級：先讀 `~/.claude/rules/model-dispatch.md`
+- 判斷「完成了嗎／該問嗎／卡住該換路嗎」：先讀 `~/.claude/rules/judgment-rubrics.md`
+- 要更新 memory／rules 檔／CLAUDE.md 本身：先讀 `~/.claude/rules/institution-maintenance.md`
```

## Token 對價（總量預算條款）

- 新增：+70 tokens/session（每場自動載入）。
- 同輪已省：loom-code hook 瘦身 −~2,200 tokens/session（11 KB → 2.1 KB，
  待 PR merge）。淨變化大幅為負，符合「加一條刪一條」精神，
  不需要另砍既有段落。
- 若你仍想對價：候選是 `## Search` 段的 JP 查詢範例 3 行（−~40 tokens），
  但那是你調過的措辭，**不建議**動（壓縮前科：polarity flip）。

## 不做的事（原 prompt 有、證據否決）

- 不重寫/收斂既有條款——現有 CLAUDE.md 條款各有談判史，收斂的語意風險
  大於 token 收益。
- 不把 loom on-ramp 表搬進 CLAUDE.md——reception hook 已是 SSOT。

## 核准方式

回覆「B 核准」即由當前 session 寫入 dotfiles 真實路徑（先備份
`CLAUDE.md.bak-2026-07-06`）；或自行手動貼上。
