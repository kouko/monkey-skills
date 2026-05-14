# legal-incident-response

Read this in: [English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

![version](https://img.shields.io/badge/version-0.4.2-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![phase](https://img.shields.io/badge/phase-2_クローズアウト-orange)

> ⚠️ **法的助言ではありません。** 本ツールは無料 open-source utility であり、法律事務所でも執業弁護士でもない。出力は社内 法務 の参考用 のみ — 刑事 exposure / 主管機関 対応 risk / 重大経営判断が絡む案件は必ず執業弁護士にエスカレーションすること。
>
> **対象**：台湾 in-house 法務 向け（zh-TW jurisdiction 専用）。日本法務には適用不可。

台湾 in-house 法務 向け **事後 incident response** skill — 3 path classifier（個資外洩 / 主管機関函覆 / 合約違約）+ auto-classification + per-path sub-protocol + audience-shaped 2-file output。台湾現行法（Path A、SP2 verify run でロック）に pin。台湾 個資法 は 「即時」 reporting language + 委託/受託 model を採る — grader が拒否する禁止 phrase の canonical list は `scripts/grade_response.py PATH_A_ANTIPATTERNS` 参照。

## 機能概要

incident 自由記述を受け取り、3 path のいずれかへ dispatch する：

1. **個資外洩 (pii-breach)** — skeleton + LLM-fill templates → PDPC 通報文 + 当事者通知文 + 内部記録 を起草（個資法 §12 + 施行細則 §22 + 関連 主管機関函釋 を anchor）
2. **主管機関函覆 (authority-letter)** — pure-LLM protocol → 来文（PDPC / 金管會 / 公平會 / etc.）を読み取り → 公文格式 函覆 を起草（canonical-§-gated citation + ISO 8601 deadline tracker）
3. **合約違約 (contract-breach)** — thin classifier + handoff JSON → `legal-contract-review` への soft delegation（user が手動 接力）

auto-classification（決定論的 keyword scan + LLM confidence judgement）が最初に走る。user は sub-protocol dispatch 前に path を確認する。

## こんな時に使う

- 個資外洩 alert を受信した（内部報告 / セキュリティ事故 / vendor leak）→ PDPC 通報 / 当事者通知の起草前に走らせる
- 主管機関（PDPC / 金管會 / 公平會 / 勞動部 / etc.）から 来文 が届き 函覆 が必要 → 法源 anchor + deadline tracker 付きで起草
- 取引相手側に違約事象（納期遅延 / 支払滞納 / SLA miss）→ triage + `legal-contract-review` への handoff bundle を emit
- 法務向け（完全タイムライン + 法条引用）と 非法務向け（Top 3 即時動作 + deadline 警示）を audience-shaped に分離出力する必要

## こんな時には使わない

- **事前 policy / template 起草** → `legal-document-draft`（隱私權政策 / ToS / DPA / NDA）
- **既存合約の深い clause 分析** → `legal-contract-review`（7 層 pipeline + TW overlay）
- **法律研究 / 諮詢** → Phase 3 planned `legal-research` + `legal-issue-spot`（IRAC cluster）
- **事前 playbook authoring** → `legal-playbook-author`
- **訴訟戦略** — PRODUCT-SPEC §9 で明確に scope outside
- **台湾外 jurisdiction** — Path A は台湾現行法のみ；GDPR-style 機能は意図的除外

## 使い方

1. router 経由で起動：
   ```
   /using-legal-toolkit
   ```
   router の Q3（個資外洩 / 違約 / 主管機関來文）に yes と答える。

2. repo に `legal-playbook/profile.yml` v2 を用意（`assets/profile-schema.yml` 参照）。必須項目：会社 identity + 主管機関 + optional `external_counsel` + `regulatory_authorities`（v2 追加；v1 profile は auto-upgrade）。

3. incident 自由記述を入力。skill が auto-classify + 確認を求める。

各 path の 1-liner 例：

- **PII breach** — 「昨日某 database に外部存取記錄あり、5000 顧客の氏名 + 電話番号 が影響を受けた可能性」→ `legal.md` + `business.md`（PDPC 通報草稿 + 当事者通知 + 内部記録）
- **Authority letter** — 来文内容 + 来文機関 + 来文日付 を paste → 函覆草稿（§ anchor citation + ISO 8601 deadline tracker）
- **Contract breach** — 「相手側は §3 で 2026-05-01 までに納品の義務、未納品」→ handoff-context.json（`legal-contract-review` 接力用）+ business-side 即時動作 summary

## Inputs

- **Required**：`legal-playbook/profile.yml`（schema v2；session 開始前に `scripts/load_profile.py` が validate；v1→v2 delta は `references/profile-schema-v2-migration.md` を参照）
- **Required at session**：incident 自由記述（または explicit `--type pii-breach|authority-letter|contract-breach` override）
- **Optional from profile**：`external_counsel` + `regulatory_authorities` + `dpo.phone`（schema v2 で全て optional）

完全 schema は SKILL.md §Inputs + spec §4 参照。

## Outputs

セッション毎に `legal-outputs/<timestamp>-incident-<path-type>/` へ出力：

- `legal.md` — 法務 audience：event record + ISO 8601 時間軸 + path 固有 content + compliance checklist + TBD migration tracker
- `business.md` — 非法務 audience：1 句 summary + Top 3 即時動作 + deadline 警示 + 対外コミュニケーション要点
- `handoff-context.json` — contract-breach path のみ（schema_version 1；10 必須キー；`legal-contract-review` への soft delegation）

完全 schema は SKILL.md §Outputs + spec §5 参照。

## Quality gates

- `scripts/load_profile.py`（`legal-toolkit/scripts/canonical/` の functional copy）が `legal-playbook/profile.yml` を `assets/profile-schema.yml` v2 と照合 validate；必須項目欠落で session start halt
- `scripts/grade_response.py` が path 毎に決定論的 structural check を実行（2 file 存在 / ISO timeline / canonical TBD id / PII section 完備 / authority-letter 函覆 + ISO deadline / contract-breach handoff JSON schema）。Path A anti-pattern bank は SP3a v0.4.1 と byte-identical — `<doc-type>.md` output で grader が拒否する禁止 phrase の canonical list は `scripts/grade_response.py PATH_A_ANTIPATTERNS` 参照
- 手作業 curated の path 別 compliance checklist（`checklists/compliance-pii-breach.md` / `compliance-authority-letter.md` / `compliance-contract-breach.md`）+ 法条引用 + `**{{verdict}}**` template

## 制限事項

- Path A scope：台湾現行法のみ追跡；台湾 個資法 は 「即時」 reporting language + 委託/受託 model を採用 — grader が拒否する禁止 phrase の canonical list は `scripts/grade_response.py PATH_A_ANTIPATTERNS` 参照
- 違約 path = thin delegator；`legal-contract-review` が深い clause 分析を担当（soft delegation；user が handoff-context.json で 手動 接力）
- zh-TW 出力のみ；多言語対応は `translation-toolkit` plugin 経由（別 concern）
- このスキルから `legal-contract-review` への auto-invocation なし；`--seed` flag consumption は v0.4.3+ へ deferred
- v0.4.2 では `legal-playbook/` IR 固有 clause なし — v0.4.3+ dogfood-driven 設計へ deferred

## 関連 skill

- `legal-document-draft` — **事前** drafting（隱私權政策 / ToS / DPA / NDA）。インシデント発生 *前* に使用；`legal-incident-response` は発生 *後*
- `legal-contract-review` — 深い clause 分析（7 層 pipeline + TW overlay）；このスキルの contract-breach path からの `handoff-context.json` を受け取る
- `legal-playbook-author` — `legal-contract-review` が consume する交渉 stance を作成
- `using-legal-toolkit` — entry-point router（Q3 が当 skill へ dispatch）
- Phase 3+ planned：`legal-issue-spot` + `legal-research`（IRAC cluster）；`legal-regulation-watch`（PDPC 子法 RSS poll）

## 参考

- Spec：`docs/superpowers/specs/2026-05-13-legal-toolkit-sp3b-incident-response-design.md`
- SP2 ground truth（Path A 5 pillars）：`legal-toolkit/research/2026-05-12-pdpa-2025-11-verify.md`
- ROADMAP：`legal-toolkit/ROADMAP.md`（§Phase 2 v0.4.2）
- Plugin spec：`legal-toolkit/PRODUCT-SPEC.md` + `legal-toolkit/TECH-SPEC.md`
