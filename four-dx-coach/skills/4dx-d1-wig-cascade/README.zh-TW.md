# 4DX D1 — Team WIG Cascade

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 帶你（leader-of-leaders）按 Ch 7 四條規則，把已定的 org Primary WIG 翻譯到下屬 3-7 個團隊各自的 Team WIG，或診斷既有 cascade。**兩種 mode**：coach（從零組建）+ audit（診斷既有 cascade map + 下面 leader 的抱怨）。

## 何時觸發這個 skill

**Coach-mode（從零組建）：**
- 「上面定的 WIG，我團隊要怎麼接？」
- 「每位主管要有自己的 Team WIG，怎麼選？」
- 上層丟下來一條 WIG，你要往下分解
- 多團隊組織需要 region → district、division → team 一層層接下去

**Audit-mode（診斷既有 cascade）：**
- 「幫我看 cascade 哪裡有問題，下面的 leader 都在抱怨」
- 「上面說 cascade 不對，這是 map」
- 下面 leader 在說「硬塞下來」「跟戰略沒關係」「太多事要做」
- 第一次 cascade 跑出 7+ Battle WIG／每隊一樣的 WIG — 想做診斷（不是重組）

## 它做什麼

Consultant 對 leader-of-leaders。兩個 protocol（按需 load）：

### `protocols/coach-mode.md` — Socratic 10 步 build

最關鍵的是執行 **Rule 3 — veto, don't dictate**。

1. 確認上游 Primary WIG（X→Y→When）
2. 列出下屬團隊（3-7 為理想）
3. 判斷 cascade 形狀（diverse vs similar）
4. 找出 Key Battles（Opryland：17 → 3；典型 2-3）
5. 各 team-leader 提 Team WIG 提案（pull，不是 push）
6. 跑 ladder-up 測試（算數，不是感覺）
7. 跑 veto 測試（接受或退回；不改寫）
8. One-WIG-per-individual
9. cascade 深度檢查（>2 層？每層重跑）
10. 輸出 cascade map

### `protocols/audit-mode.md` — 對既有 cascade 的 consultant 診斷

讀 cascade map + 下面 leader 批評 → per-rule verdict 表 → 修正案 + 再協商腳本。

- 「硬塞」/「不接受」 → Rule 3 違反
- 「跟戰略沒關係」/「上面接不起來」 → Rule 2 違反
- 「太多事要做」 → Rule 1 違反
- 「沒辦法判斷」 → Rule 4 違反
- 5+ Battles → Battles-count 不過（narrowing 不完整）
- 動作列表型 Team WIG → Targets-not-Plans 不過

## 不要在這些情境使用

| 情境 | 改去 |
|---|---|
| org Primary WIG 還沒定 | `4dx-d1-wig-formulation` |
| Leader 只帶一個團隊（沒有下屬 team-leader） | `4dx-d1-wig-formulation` |
| solo / 單獨目標 | `4dx-d1-wig-formulation` |
| 單一 Team WIG audit（沒有 cascade） | `4dx-d1-wig-formulation` audit-mode |
| Cross-layer audit（cascade + leads + scoreboard + cadence） | `4dx-audit`（全層） |
| OKR / KR / 季度目標 cascade | `using-four-dx-coach` |
| 固定終點的 single-shot project | 專案管理（WBS / Gantt） |
| 方法論適配還不確定 | `4dx-meta-strategy-triage` |

## 出處

蒸餾自 *The 4 Disciplines of Execution*（2nd ed., 2021）第 7 章 Translating Organizational Focus Into Executable Targets。三個 anchor case：Opryland Hotel（functionally diverse cascade — 75 個團隊，17 → 3 Battles）、多分店 retailer（functionally similar cascade，leaf 層擁 Battle 選擇自主權）、Sydney 會計師事務所（小公司 cascade，中間 Battle 層直接收掉）。

Orchestrator 見 [`SKILL.md`](SKILL.md)；Socratic 10 步 build（含 Rule 1-4、Targets-not-Plans、cascade-too-deep-in-one-pass anti-pattern）見 [`protocols/coach-mode.md`](protocols/coach-mode.md)；對既有 cascade artifact 的 consultant verdict matrix 見 [`protocols/audit-mode.md`](protocols/audit-mode.md)。
