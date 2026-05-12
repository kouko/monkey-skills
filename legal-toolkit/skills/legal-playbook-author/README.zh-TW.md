# legal-playbook-author

> 建立 / 擴充 / 修改 per-clause Markdown entries — 給 `legal-contract-review` 跟 (Phase 2+) 其他 playbook-aware skill 用的議價規則。

Read this in: [English](README.md) | [日本語](README.ja.md) | **繁體中文**

## 這個 skill 做什麼

`legal-playbook-author` 是 working folder 下 `legal-playbook/` 的**唯一 sanctioned writer**。（你當然可以手動編輯這些檔案；走 skill 的好處是強制 schema、避免 conflict、有互動 prompt 引導。）

從 context 自動判斷三 mode：

| Mode | Trigger | Output |
|---|---|---|
| **bootstrap** | `legal-playbook/` 不存在 / 空 | 第一次 setup；三選一：(a) 從 bundled fallback seed / (b) 5 題 interview / (c) skip 直接用 bundled read-only |
| **extend** | playbook 已有條目，要加新 clause | 新增 `legal-playbook/<clause-id>.md`（flat）或 `<clause-id>/<variant-id>.md`（variant-folder）|
| **revise** | 使用者指向既有 clause file | 選欄位編輯 → diff 確認 → write |

## 何時用

- 第一次裝 legal-toolkit
- `legal-contract-review` 回 `source_type: advisory`（沒這條 clause 的 entry）—— 你決定把自家立場 codify
- `legal-contract-review` 報告 fallback 被觸發 —— 你想把紅線繃緊一點
- 定期 refresh（設計建議每季一次）

## 何時不用

- 你只是想**讀** playbook，不是要改 → 直接開檔案
- 任務其實是合約 review → 用 `/legal-contract-review`
- 想加 non-clause 資源（template / checklist / config）→ `legal-playbook/` 不放這些

## File 寫入策略

每次 write 都是**per-question persist** —— 對話在 interview 中被打斷，部分 entry 仍會存（frontmatter 加 `status: incomplete`，未答 body section 加 `TODO:` 標記）。重啟 skill 會自動續接。

## Stub templates

skill 建立新 entry 時從三種 stub seed：

- [`assets/stub.flat.md`](assets/stub.flat.md) — flat clause（frontmatter + body 一個檔）
- [`assets/stub.variant.md`](assets/stub.variant.md) — variant-folder 內的 per-variant file
- [`assets/stub._clause.md`](assets/stub._clause.md) — variant-folder 頂層的 `_clause.md` container

## Variant-upgrade 偵測

extend / revise mode 會監看 flat clause 該升級為 variant-folder 的訊號：

- 不同 deal size 有不同 walk-away（「小單可以接受 X，大單絕對不行」）
- 對 counterparty type 有不同立場（「對 enterprise 客戶會放鬆」）
- Jurisdiction overlay（「台灣只需要這樣，但 GDPR 要再加一層」）

偵測到時，skill 會 offer migration；migration 過程把現有 flat entry 保留成第一個 variant。

## Disclaimer / Escalation Override

本 skill ship legal-toolkit 全 output skill 共用的 byte-identical Disclaimer + Override asset：

- [`assets/disclaimer-block.md`](assets/disclaimer-block.md) — 加在每份 output footer
- [`assets/escalation-override.md`](assets/escalation-override.md) — 高風險 trigger 時 prepend

Authoring playbook entry 本身通常不會觸發 Override（entry 是議價規則，不是針對特定事實的法律意見）。bootstrap 時 seed 進 `legal-playbook/` 的 README 含一份 Disclaimer。

## Anti-pattern 防禦

設計 note §七 5 種反 pattern，skill 內 enforce：

- **Bloat** — SHOULD ≤ 24 條；超過會 warn
- **Drift** — `last_updated` 追蹤；超過 180d staleness warning
- **Conflict** — duplicate `clause_id` / overlapping `gates` 偵測
- **Static** — 每條 entry 必含 `## 為什麼這條重要` 業務翻譯
- **Over-rigid** — `escalate_to` 是 escape valve；不 reject 條款

## Reference

- SKILL.md（skill 本身的 instruction）：[`SKILL.md`](SKILL.md)
- Plugin spec：[`PRODUCT-SPEC.md`](../../PRODUCT-SPEC.md) / [`TECH-SPEC.md`](../../TECH-SPEC.md)
- Mode protocols：[`protocols/bootstrap-mode.md`](protocols/bootstrap-mode.md) / [`extend-mode.md`](protocols/extend-mode.md) / [`revise-mode.md`](protocols/revise-mode.md)
- Roadmap：[`ROADMAP.md`](../../ROADMAP.md)

## License

MIT — 詳見 monorepo root 的 [LICENSE](../../../LICENSE)。
