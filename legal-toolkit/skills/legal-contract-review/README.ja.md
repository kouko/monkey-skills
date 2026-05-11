# legal-contract-review

> legal-toolkit の主戦場。7 層 schema-driven 契約レビュー（Stark + Adams + Burnham + 台湾 overlay）、playbook-driven L7 評価、disclaimer-driven 出力。

Read this in: [English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

## この skill の役割

契約に対して決定論的な 7 層 pipeline を走らせ、**構造化 Markdown 6 ファイル**を出力する：

| ファイル | 内容 |
|---|---|
| `issues.md` | Findings 矩陣 + business-issue tag + playbook trace |
| `redline.md` | 代替条項 text（playbook body 起源 or LLM 生成）|
| `memo-legal.md` | 完整 CRAC memo + 法条 / 判例 citation |
| `memo-business.md` | 非法務向け Why/What/What-if 3 文 |
| `escalation.md` | 誰が何を sign する + trigger 条件 |
| `self-grade.md` | Harvey dual-score（answer + source）+ failed criteria |

全 output に Mandatory Disclaimer footer；高 risk findings に Escalation Override 赤字 banner が前置される。

## Pipeline

```
INPUT （契約 + type + jurisdiction + deal_context + mode + stance）
   ↓
LOAD PLAYBOOK （user legal-playbook/ OR bundled fallback）
   ↓
[台湾のみ] L0a 強行/任意 → L0b 定型化契約 §247-1
   ↓
L1 Expectations → L2 Anatomy → L3 Categorize → L4 Functional tier → L5 Domain priority → L6 Cycle
   ↓
[台湾のみ] L6.5 六準則契約解釈
   ↓
L7 Evaluate against playbook （ABAC pre-filter + LLM compare）
   ↓
SELF-GRADE （Harvey dual-score：answer / source、合算しない）
   ↓
WRITE 6 outputs → legal-outputs/<timestamp>-<contract-name>/
```

各層の protocol file は [`protocols/`](protocols/) 配下に独立 instruction として存在。

## 3 mode

| Mode | 走る層 | 出力 emphasis |
|---|---|---|
| `review`（default）| L0a → L7 + L6.5（full）| 6-output 完全 review |
| `redline` | L1-L7 + L6.5 | 替代条項 text 強化 |
| `nda` | bundled NDA template + L4-L7 | issues + redline + memo-legal（3 outputs）|

## Cold-start fallback

User に `legal-playbook/` が無い場合、skill は abort しない。L7 が plugin 内の 4 件 bundled fallback baseline を [`assets/`](assets/) から読む：

- `baseline-fallback-confidentiality.md`
- `baseline-fallback-governing-law-jurisdiction.md`
- `baseline-fallback-auto-renewal.md`
- `baseline-fallback-termination-and-survival.md`

bundled fallback から派生した finding には banner（custom 化を促す）が付く。`escalate_to` フィールドは `[請編輯為你公司的角色：...]` placeholder；L7 が検出して escalation.md に warning callout を追加。

4 件以外の clause は L7 で **advisory mode** に落ちる：`source_type: advisory`、`legal-playbook-author extend <clause-id>` の提案付き。

Phase 1.5 で bundled fallback を 8 件へ拡張（LoL / Indemnification / DPA / IP-Assignment の variant-folder 版追加）。

## Inputs

| Field | Required | Default |
|---|---|---|
| `contract_path` | yes | — |
| `contract_type` | no | auto-detect |
| `jurisdiction` | no | `TW` |
| `deal_context` | no | best-effort 抽出 |
| `mode` | no | `review` |
| `stance` | no | `ours` |

## 使うとき

- 契約 sign / 反提案 前の review
- 交渉往復用の redline 生成
- Portfolio consistency のため playbook 基準対照
- 法律 counsel 討論用 memo 作成

## 使わないとき

- playbook entry を**作成**したい → `/legal-playbook-author`
- privacy policy / ToS をゼロから**起草**したい → （Phase 2）`legal-document-draft`
- fact-pattern 質問（"Xできるか？"）→ （Phase 3）`legal-issue-spot`
- 訴訟戦略 / 複雑交渉 tactics — **設計上 out of scope**

## Output 構造

```
<cwd>/legal-outputs/<YYYY-MM-DD>-<contract-name-slugified>/
├── issues.md              # findings 矩陣
├── redline.md             # 替代条項
├── memo-legal.md          # CRAC + citation
├── memo-business.md       # Why/What/What-if
├── escalation.md          # 誰が sign
└── self-grade.md          # answer + source dual-score
```

全 file footer：Mandatory Disclaimer（`assets/disclaimer-block.md` 起源）
高 risk file header：Escalation Override 赤字 banner（`assets/escalation-override.md` 起源）

## External-share mode

`--external-share` flag で `issues.md` / `memo-legal.md` / `escalation.md` から playbook ID を strip（「依本公司紅線政策」へ置換）。Override 赤字 banner は **絶対** strip されない。

## Reference

- SKILL.md（instruction）：[`SKILL.md`](SKILL.md)
- 各層 protocol：[`protocols/`](protocols/)
- Output schema：[`assets/output-schema-*.json`](assets/)
- Bundled fallback：[`assets/baseline-fallback-*.md`](assets/)
- Self-grade rubric：[`checklists/answer-criteria.md`](checklists/answer-criteria.md) + [`source-criteria.md`](checklists/source-criteria.md)
- Domain reference：[`references/`](references/)（Stark 7 概念 / Adams 10 カテゴリ / type 別 priority）
- Plugin spec：[`PRODUCT-SPEC.md`](../../PRODUCT-SPEC.md) / [`TECH-SPEC.md`](../../TECH-SPEC.md)
- Roadmap：[`ROADMAP.md`](../../ROADMAP.md)

## License

MIT — monorepo root の [LICENSE](../../../LICENSE) 参照。
