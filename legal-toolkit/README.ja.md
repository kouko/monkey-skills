# legal-toolkit

> 台湾 SME → 上場企業向け社内法務 toolkit — 7 層 schema-driven 契約レビュー、playbook-driven 交渉、disclaimer-driven 出力。

Read this in: [English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

![version](https://img.shields.io/badge/version-0.2.0-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![phase](https://img.shields.io/badge/phase-1.5_DSL-orange)

> ⚠️ **法的助言ではありません。** 本ツールは無料の open-source utility であり、法律事務所でも執業弁護士でもない。全ての出力に Mandatory Disclaimer が付き、高 risk findings には Escalation Override（「執業弁護士に相談してください」）が表示される。詳細は [§Disclaimer policy](#disclaimer-policy)。

## 機能概要

legal-toolkit は社内法務（個人 / SME / 上場中堅）に対して、**Markdown-first / runtime-portable** な workflow を提供する。対象は in-house 業務時間の高頻度 80% — **契約レビュー**（主戦場）、**playbook authoring**（自社の交渉ルール）、および (Phase 2-5 予定) 文書 drafting / incident response / issue spotting / research / 契約 lifecycle tracker / regulation watch / corporate governance / DD quickscan。

BigLaw 移植 tool との差別化となる 3 つの設計方針：

1. **Schema-driven、vibe-driven ではない** — 契約レビューは決定論的な 7 層 pipeline を走る（Stark 7 contract concepts / Adams 10 language categories / Burnham 6 functional tiers）+ 台湾 jurisdiction overlay（強行/任意規定二分 / 定型化契約 §247-1 / 六準則 contract interpretation）。
2. **Playbook は見える場所に置き、自分で編集できる** — `legal-playbook/<clause>.md` を working folder に visible で置く。Markdown / git-trackable。SQLite blob に埋もれない、dotfile 隠し folder にもしない、vendor cloud にも置かない。三層 ownership：visible `legal-playbook/`（ユーザー所有）+ visible `legal-outputs/`（ユーザー所有）+ hidden `.legal-toolkit/`（tool internals）。
3. **Disclaimer-driven、機能を削らない** — 台湾の弁護士法 §48 は「自然人」を規律対象とする規定であり「tool」ではない。無料 open-source utility ≠ 有償 service。「法的意見の生成」を hard-exclude すると、Phase 3 計画の sub-skill（issue-spot / research）が成立しなくなる。全 output に Mandatory Disclaimer を付け、高 risk findings に Escalation Override 赤字 banner を付ける。

## 3 skills (MVP + Phase 1.5 DSL infra, v0.2.0)

| Skill | 役割 |
|---|---|
| `using-legal-toolkit` | **Router** — 6 cluster（Playbook / Template / Runbook / IRAC / Tracker / Compliance）にわたる意図を識別、dispatch する。Phase 2-5 の sub-skill は not-yet-available として明示。 |
| `legal-playbook-author` | **Cross-cluster utility** — bootstrap / extend / revise mode。per-clause Markdown entry を生成（決定論的 frontmatter：`gates` / `walk_away_triggers` / `escalate_to` / `risk_default` + LLM-comparison body：`preferred` / `fallback N` / `為什麼這條重要`）。flat clause が variant-folder へ upgrade すべきかを検知（deal_size / counterparty_type / jurisdiction で gate keyed）。 |
| `legal-contract-review` | **主戦場** — TW overlay 付きの 7 層 pipeline。ABAC pre-filter が LLM 評価前に matched variant を選ぶ（LLM は単一 variant のみ参照、選択させない）。3 mode：`review`（full 6-output）/ `redline`（substitute clause text に focus）/ `nda`（簡易構造のため L2-L3 skip）。出力 6 ファイル：`issues.md` / `redline.md` / `memo-legal.md` / `memo-business.md` / `escalation.md` / `self-grade.md`。 |

Phase 2-5 でさらに 8 skill 追加 — v0.1.0 → v1.0.0 plan / version strategy / critical path / risk callouts は **[ROADMAP.md](ROADMAP.md)** 参照。

## Cold-start fallback（独自 playbook なしでも動作）

初回 install 時：working folder に `legal-playbook/` は **存在しない**。それでも toolkit は動作する — `legal-contract-review` が plugin 内 bundled の **4 件 fallback baseline clause** を読む：

| clause_id | Layout |
|---|---|
| `confidentiality` | flat |
| `governing-law-jurisdiction` | flat |
| `auto-renewal` | flat |
| `termination-and-survival` | flat |

bundled clause から生成された finding には banner が付く：`⚠️ Bundled fallback baseline を使用中 — legal-playbook-author で自社向け custom 化を推奨`。`escalate_to` field は placeholder 文字列で出荷（`[請編輯為你公司的角色：法務主管 / GC / 部門主管]`）；review 時に placeholder 検知 warning を発する（user が最終決定とする前に気付けるように）。

`legal-playbook-author bootstrap` で bundled fallback → 自社 customised playbook へ移行できる。**v0.2.0 (Phase 1.5)** で bundled baseline を 8 clause へ拡張 — variant-folder `limitation-of-liability`（small/mid/large-deal）/ `indemnification`（small/mid/large-deal）/ `data-protection-dpa`（tw-only/gdpr-overlay/cross-border）+ flat `ip-assignment-and-license` を追加。`seed_baseline.py` で 8-clause tarball を working folder に展開可能。

## Playbook layout（交渉判断の Source of Truth）

```
<working folder>/
├── legal-playbook/                    ← visible / ユーザー所有
│   ├── README.md                      # auto-seed 版「playbook の維持の仕方」
│   ├── confidentiality.md             # flat clause
│   ├── governing-law-jurisdiction.md
│   ├── limitation-of-liability/       ← variant-folder（deal-size keyed）
│   │   ├── _clause.md
│   │   ├── small-deal.md              # gates: deal_size < 100K USD
│   │   ├── mid-deal.md                # gates: 100K-1M USD
│   │   └── large-deal.md              # gates: >= 1M USD
│   └── data-protection-dpa/           ← variant-folder（jurisdiction keyed）
│       ├── _clause.md
│       ├── tw-only.md
│       ├── gdpr-overlay.md
│       └── cross-border.md
│
├── legal-outputs/                     ← visible / ユーザー所有（per-run review 結果）
│   └── 2026-05-11-acme-saas-msa/
│       ├── issues.md
│       ├── redline.md
│       ├── memo-legal.md
│       ├── memo-business.md
│       ├── escalation.md
│       └── self-grade.md
│
└── .legal-toolkit/                    ← hidden / tool 所有
    ├── config.yml                     # profile + global_rules
    ├── schema.json
    └── cache/
```

Discovery は `<cwd>` → ancestor 5 階層 → BFS 深度 5 → bundled fallback の順で探索。`legal-outputs/` と `.legal-toolkit/` は `.gitignore` 対象、`legal-playbook/` のみ track（自社の交渉知財）。

## 契約レビュー pipeline

```
INPUT （契約 path + contract_type + jurisdiction + deal_context）
   ↓
LOAD PLAYBOOK  （legal-playbook/ を scan → index 構築；schema validate；last_updated > 180 日 で staleness warning）
   ↓
[台湾のみ]  L0a 強行/任意 規定二分  →  L0b 定型化契約 §247-1 + 消保法 §11-1
   ↓
L1  Expectations           bundled template ∪ playbook_index keys
L2  Anatomy mapping        preamble / definitions / action / endgame / boilerplate
L3  Categorize             Stark 7 contract concepts + Adams 10 language categories
L4  Functional tier        money / risk / control / standards / endgame
L5  Domain priority        bundled[contract_type] + playbook augment
L6  Cycle / cross-ref      if-breach branch; definitions 再読; missing-items flag（gaps == 0 AND cycle >= 2 で loop 終了）
   ↓
[台湾のみ]  L6.5  六準則 contract interpretation （当事者目的 → 慣習 → 任意規定 → 信義則）
   ↓
L7  Evaluate Against Playbook  （clause 毎）
       ├── clause.id が user playbook_index にある？     → user variant 評価
       ├── clause.id が bundled fallback にある？         → bundled fallback + banner
       └── どちらでもない？                                 → advisory mode + playbook-author extend を提案
   ↓
   matched entry 毎：
   ABAC pre-filter（gates vs deal_context）→ 単一 matched variant
   walk_away_trigger LLM judge → 🔴 walk / 🟢 preferred / 🟡 fallback / 🔴 worse
   LLM 不確実？ → frontmatter risk_default を採用
   ↓
SELF-GRADE  （Harvey dual-score：answer_score / source_score — 合算しない；all-pass binary）
   ↓
OUTPUT  6 ファイル → legal-outputs/<timestamp>-<contract-name>/
   + Mandatory Disclaimer（全 output、footer）
   + Escalation Override（高 risk のみ、header 赤字 banner）
```

## Disclaimer policy

全 output file の footer に Mandatory Disclaimer：

- 法律事務所でも執業弁護士でもない
- 無料 open-source tool、service ではない（料金なし、SLA なし、advisor-client 関係なし）
- 出力は内部意思決定の **参考用** のみ、法的助言を構成しない
- 訴訟 / 刑事 exposure / 重大経営判断の際は **執業弁護士に相談**
- 引用される法条 / 判例 / 函令は **全國法規資料庫 / 司法院判決系統 / 主管機関官網** を一次 source とする

高 risk findings — `risk_default: red` / `walk_away_triggered: true` / `confidence < 0.7` / 刑事責任関連 / `deal_size > escalation_threshold` — の場合、影響を受ける output の冒頭に **Escalation Override** 赤字 banner が追加され、*「請諮詢執業律師」* と明示される。

業界 context：Harvey / Spellbook / LawGeex / Lawsnote / 律果 LegalSign.ai いずれも disclaimer-driven 設計を採用、「法的意見の生成」を hard-exclude する vendor は **皆無**。台湾の弁護士法 §48 は自然人による弁護士業務（法廷代理、有償の法律文書作成、弁護士名義での対外活動）を規律する規定であり、無料 open-source utility や社内法務の社内 advisory 業務には及ばない。

## Install

```bash
# Claude Code 上で monkey-skills marketplace を enable した状態で
/plugin install legal-toolkit@monkey-skills
```

Plugin は self-contained — bundled fallback baseline + protocols + schemas が同梱。Toolkit は local-FS-first 動作で完全 offline、外部 API 呼び出しなし。Claude Code CLI で動作確認；Cowork「Work in a Folder」mount もサポートだが FUSE pre-existing-file 動作に起因する初回 onboarding 1 step が必要な場合あり（Phase 2 で document 化予定）。

## 使い方

```
/using-legal-toolkit
```

代表的 3 シェイプ：

| Shape | Trigger | Path |
|---|---|---|
| **Shape A** — 契約 review | 「この SaaS MSA を playbook 基準で review して」/「この NDA を redline」 | router → contract-review → 6 output |
| **Shape B** — playbook author / extend | 「auto-renewal の clause を追加」/「LoL の enterprise tier fallback を更新」 | router → playbook-author（extend / revise mode）|
| **Shape C** — 初回 install | 「install したばかり、何から始めれば？」 | router → playbook-author（bootstrap mode）→ bundled fallback seed か interview from scratch を提示 |

意図が明確な場合は skill 直接呼出も可能（例：契約 path に対して `/legal-contract-review`）。

## Language policy（cross-cutting）

**英語骨格 + zh-TW 血肉**（design phase で決定、TECH-SPEC で lock）：

- **英語**：SKILL.md / protocols / scripts / JSON schema key — LLM instruction-following は英語で有意に強い；Anthropic 公式 skill convention に整合；cross-runtime portability も高い。
- **zh-TW（原文保持）**：法条引用（民法 §247-1 / 個資法 §21 / 勞基法 §9-1）/ 台湾判例 / baseline playbook 本文 / user-facing output。
- **Bilingual triggers**：frontmatter `description` に EN + zh-TW keyword を併記 — 命中率は上がる、false-positive routing は増えない。
- **翻訳しないもの**：法条原文（民法 §247-1 を "unconscionability" と訳すと LLM が米国 doctrine へ誤誘導する）、Stark / Adams / Burnham terminology（専有名詞、訳すと citation lookup が壊れる）。

## Status

- **Version**：0.2.0 (2026-05-12)
- **Stability**：MVP shell + Phase 1.5 DSL infra 完了；end-to-end dogfood validation は未実施
- **Phase**：1.5 (DSL + scripts + 8-clause baseline) — v0.1.0 → v1.0.0 plan は [ROADMAP.md](ROADMAP.md) 参照
- **Test suite**：80+ tests（schema / discover / validate / detect_conflicts / abac_filter / build_baseline / seed_baseline）— `uv run --with jsonschema --with pyyaml --with pytest` で全 green
- **License**：MIT (plugin code)

## Reference

- **ROADMAP**：[`ROADMAP.md`](ROADMAP.md) — 7-phase plan、version strategy、risk callouts
- **PRODUCT-SPEC**：(Step B、pending) — 商業 + 設計方向
- **TECH-SPEC**：(Step B、pending) — module + data flow + interface contract
- **Design note (SoT)**：`<obsidian-vault>/research/2026-05-09 法務 Agent Skill (legal-toolkit) 整體架構與執行流程設計.md` (1344 行、38+ locked decision)

## Contributing

PR は `https://github.com/kouko/monkey-skills` 経由で歓迎。Conventions：

- **Skill structure** は monkey-skills convention に従う：flat skill directory、`<subfolder>/` 内に nested subfolder を作らない。Hook enforcement の詳細は repo `CLAUDE.md` 参照。
- **Commit prefix**：`feat(legal-toolkit)` / `fix(legal-toolkit)` / `docs(legal-toolkit)` / `chore(legal-toolkit)` / `refactor(legal-toolkit)` / `test(legal-toolkit)`。
- **三言語 skill README（en/ja/zh-TW）必須** — monkey-skills PR #150 convention により、per-skill README.md にも本 plugin-level README にも適用。
- **Disclaimer block** — 全 output file footer の disclaimer 文言は、これを ship する 3 skill 間で byte-identical でなければならない（Phase 6 で CI gate 追加予定）。

## License

MIT — repository root の [LICENSE](../LICENSE) 参照。
