# 合約違約事件 — 法務記錄

## §1 違約 classification

民法 §227 不完全給付。對方未按照合約 §3.2 履行交付義務。

## §時間軸

| 時間 (ISO 8601) | 事件 | 來源 |
|---|---|---|
| 2026-04-01 | 簽約日 | 合約 |
| 2026-05-08 | 違約發生 | 對方 |
| 2026-05-13 | 我方知悉 | 業務通報 |
| ⏳ 待催告 | 催告日 | 民法 §229 程序 |
| ⏳ 待解除 | 解除日 | 民法 §259 |

## §2 Handoff to legal-contract-review

- contract_path: /path/to/contract.md
- 請執行: /legal-contract-review --contract /path/to/contract.md
- 可選 seed: handoff-context.json
- 預期 legal-contract-review 跑 L0-L7 七層分析

## §3 Compliance

- [x] 違約 classification 民法 § 引用 — **PASS**
- [x] 時間軸 ISO 完整 — **PASS** (3 已發生 + 2 ⏳)
- [x] alleged_breach_clauses 非空 — **PASS** (§3.2, §4.4)
- [x] handoff-context.json schema — **PASS**
- [x] legal.md §3 含 legal-contract-review 指標 — **PASS**
