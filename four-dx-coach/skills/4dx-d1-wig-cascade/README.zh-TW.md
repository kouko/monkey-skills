# 4DX D1 — Team WIG Cascade

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 帶你（leader-of-leaders）按 Ch 7 四條規則，把已定的 org Primary WIG 翻譯到下屬 3-7 個團隊各自的 Team WIG。

## 何時觸發這個 skill

- 「上面定的 WIG，我團隊要怎麼接？」
- 「每位主管要有自己的 Team WIG，怎麼選？」
- 上層丟下來一條 WIG，你要往下分解
- 多團隊組織需要 region → district、division → team 一層層接下去
- 第一次 cascade 跑出 7+ Battle WIG，或每個團隊分到一模一樣的 WIG

## 它做什麼（protocol 摘要）

Consultant 對 leader-of-leaders。這個 skill 最關鍵的工作是執行 **Rule 3 — veto, don't dictate**：

1. **確認上游 Primary WIG** — 必須是 *From X to Y by When* 形式
2. **列出下屬團隊** — N 個團隊 + 各自功能（3-7 為理想）
3. **判斷 cascade 形狀** — functionally diverse 還是 functionally similar
4. **找出 Key Battles** — 越少越好（Opryland：17 → 3）；典型落在 2-3
5. **由各 team-leader 提 Team WIG 提案** — pull，不是 push；不替他們指派
6. **跑 ladder-up 測試** — 算數，不是感覺；contributions 的總和 ≥ Battle ≥ Primary WIG
7. **跑 veto 測試（Rule 3）** — 接受或退回讓對方重提；不改寫
8. **One-WIG-per-individual（Rule 1）** — 不要超載
9. **cascade 深度檢查** — 超過 2 層？每一層重跑一次這個 skill
10. **輸出 cascade map** — Primary WIG → Battles → Team WIGs，每個都唸出聲確認

## 不要在這些情境使用

| 情境 | 改去 |
|---|---|
| org Primary WIG 還沒定 | `4dx-d1-wig-formulation` |
| Leader 只帶一個團隊（沒有下屬 team-leader） | `4dx-d1-wig-formulation` |
| solo / 單獨目標 | `4dx-d1-wig-formulation` |
| 固定終點的 single-shot project | 專案管理（WBS / Gantt） |
| 方法論適配還不確定 | `4dx-meta-strategy-triage` |

## 出處

蒸餾自 *The 4 Disciplines of Execution*（2nd ed., 2021）第 7 章 Translating Organizational Focus Into Executable Targets。三個 anchor case：Opryland Hotel（functionally diverse cascade — 75 個團隊，17 → 3 Battles）、多分店 retailer（functionally similar cascade，leaf 層擁 Battle 選擇自主權）、Sydney 會計師事務所（小公司 cascade，中間 Battle 層直接收掉）。

完整 RIA++ 渲染（含 Rule 1-4、Targets-not-Plans 原則、cascade-too-deep-in-one-pass anti-pattern）見 [`SKILL.md`](SKILL.md)。
