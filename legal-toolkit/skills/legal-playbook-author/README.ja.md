# legal-playbook-author

> `legal-contract-review` および (Phase 2+) 他の playbook-aware skill が依拠する per-clause Markdown entry を author / extend / revise する skill。

Read this in: [English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

## この skill の役割

`legal-playbook-author` は working folder 下の `legal-playbook/` への**唯一の sanctioned writer**。（もちろん手動編集も可能だが、skill 経由は schema 強制 + conflict 防止 + 補助 prompt が付く。）

context から自動判定される 3 mode：

| Mode | Trigger | Output |
|---|---|---|
| **bootstrap** | `legal-playbook/` が missing / 空 | 初回 setup；3 択：(a) bundled fallback から seed / (b) 5 問 interview / (c) skip して bundled read-only で使う |
| **extend** | playbook 存在、新 clause 追加 | 新規 `legal-playbook/<clause-id>.md` (flat) または `<clause-id>/<variant-id>.md` (variant-folder) |
| **revise** | 既存 clause file を指定 | 選択的 field 編集 → diff 確認 → write |

## 使うとき

- legal-toolkit の初回 install
- `legal-contract-review` が `source_type: advisory` を返してきて（その clause の entry がない）、自社立場を codify したくなったとき
- `legal-contract-review` が fallback trigger を報告してきて、しめ直したいとき
- 定期 refresh（設計推奨：四半期に一度）

## 使わないとき

- playbook を**読みたい**だけ → file を開けば良い
- 本当に契約 review がしたい → `/legal-contract-review`
- non-clause asset (template / checklist / config) を追加したい → `legal-playbook/` の対象外

## File 書き込みの作法

全ての write は**質問毎 persist** — conversation が interview 途中で中断しても、部分的 entry は保存される（frontmatter に `status: incomplete`、未回答 body section に `TODO:` marker）。再起動すると続きから再開できる。

## Stub templates

新規 entry 作成時、skill は 3 種 stub のいずれかから seed する：

- [`assets/stub.flat.md`](assets/stub.flat.md) — flat clause（frontmatter + body の 1 file）
- [`assets/stub.variant.md`](assets/stub.variant.md) — variant-folder 内の per-variant file
- [`assets/stub._clause.md`](assets/stub._clause.md) — variant-folder 先頭の `_clause.md` container

## Variant-upgrade 検知

extend / revise mode で、flat clause を variant-folder へ upgrade すべき signal を監視：

- deal size により walk-away が異なる（「小単では受け入れ可、大単では絶対不可」）
- counterparty type 条件付き立場（「enterprise 客には緩める」）
- jurisdiction overlay（「台湾では十分、GDPR ではもう一層必要」）

検出時、skill が migration を提案；migration 時、既存 flat entry は第一 variant として保持される。

## Disclaimer / Escalation Override

本 skill は legal-toolkit の全 output skill 間で byte-identical な Disclaimer + Override asset を ship する：

- [`assets/disclaimer-block.md`](assets/disclaimer-block.md) — 全 emit output の footer に付ける
- [`assets/escalation-override.md`](assets/escalation-override.md) — 高 risk trigger 発火時に prepend

playbook entry の authoring 自体は通常 Override を trigger しない（entry は交渉 rule であり、特定 fact への法的意見ではない）。bootstrap 時に `legal-playbook/` へ seed される README には Disclaimer が 1 回含まれる。

## Anti-pattern 防御

設計ノート §七の 5 種反 pattern を skill で enforce：

- **Bloat** — SHOULD ≤ 24 clause；超過時 warn
- **Drift** — `last_updated` 追跡；180d 経過で staleness warning
- **Conflict** — duplicate `clause_id` / overlapping `gates` 検出
- **Static** — 全 entry に `## 為什麼這條重要` 業務翻訳が必須
- **Over-rigid** — `escalate_to` が escape valve；reject はしない

## Reference

- SKILL.md（skill 本体 instruction）：[`SKILL.md`](SKILL.md)
- Plugin spec：[`PRODUCT-SPEC.md`](../../PRODUCT-SPEC.md) / [`TECH-SPEC.md`](../../TECH-SPEC.md)
- Mode protocols：[`protocols/bootstrap-mode.md`](protocols/bootstrap-mode.md) / [`extend-mode.md`](protocols/extend-mode.md) / [`revise-mode.md`](protocols/revise-mode.md)
- Roadmap：[`ROADMAP.md`](../../ROADMAP.md)

## License

MIT — monorepo root の [LICENSE](../../../LICENSE) 参照。
