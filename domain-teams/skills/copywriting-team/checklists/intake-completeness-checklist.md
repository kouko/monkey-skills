# Checklist: Intake Completeness

MUST gate（binary pass/fail）。Trigger: `copywriting-brainstorming.md`
§Task 9 Understanding Summary 出力後、next-phase protocol を load
する前。本 gate は copywriting-team の全 workflow（long / mid /
short / ideation / audit）が共通に通過する前提 gate であり、Level 1
欄位が揃わない状態での next phase 進行を blocks する。

## Primary Sources

- `../protocols/copywriting-brainstorming.md` — 本 gate の intake
  source。Task 2-5 で collect した fields をここで検証する。
- `../standards/persuasion-psychology-anchor.md` §Schwartz 5 Levels
  of Awareness — 長文の awareness level 欄位の根拠。
- `../standards/short-form-catchcopy-canon.md` §5 種切入点決策樹 —
  短文の target emotion / pain → approach map の前提。
- `../standards/long-form-pasona-canon.md` §PASONA 系列使い分け表 —
  長文 framework 選択の前提。
- `../standards/mid-form-beaf-canon.md` — 中文 BEAF の前提（benefits
  list 必須）。

## Evaluation Instructions

You are a strict auditor. Check each item below against the worker's
Understanding Summary output. Give `PASS`, `FAIL_FATAL`,
`FAIL_FIXABLE`, or `N/A` for each item, with specific evidence
(quoted line or artifact reference).

Failure type for each item is defined below — use the type specified.

`N/A` は **当該 form type では該当しない item の場合のみ**許可。
例：form_type = short の artifact では CHK-CTW-INTAKE-L01（長文
字數範囲）は `N/A`。

## Checklist

### Common items（全 form type 適用）

- [ ] **CHK-CTW-INTAKE-001 (Form type declared)** [FATAL]: Understanding
  Summary §Form Type に `long / mid / short / ideation / audit` の
  いずれかが明示されている。曖昧表現（「キャッチコピー的なもの」
  「文案いろいろ」等）は FATAL。**Grounded in**:
  `../protocols/copywriting-brainstorming.md` §Task 2。
- [ ] **CHK-CTW-INTAKE-002 (Product / service)** [FATAL]: Understanding
  Summary §Product / Value Proposition に商品 / サービス名 + 主要
  value proposition（1 文）が明示されている。「何かいい商品」
  「サービス一般」等の抽象は FATAL。PRODUCT-SPEC.md or planning-team
  出力への参照で具体化されていれば PASS。**Grounded in**:
  `../protocols/copywriting-brainstorming.md` §Task 3。
- [ ] **CHK-CTW-INTAKE-003 (Target audience)** [FATAL]: Understanding
  Summary §Target Audience に最低 1 つの具体情報（demographic /
  persona / segment / role）が明示されている。「一般消費者」
  「広く万人」等の無限定は FATAL。**Grounded in**:
  `../protocols/copywriting-brainstorming.md` §Task 4。
- [ ] **CHK-CTW-INTAKE-004 (Understanding Summary structure)**
  [FIXABLE]: Understanding Summary block が `copywriting-brainstorming.md`
  §Task 9 で定義された 9 subsection（Request / Form Type / Product /
  Target Audience / Form-Specific Spec / Voice Reference / Framework /
  Confirmed Assumptions / Resolved Ambiguities / Level 2/3 Defaults
  Accepted）を含んでいる。missing subsection は FIXABLE。**Grounded
  in**: `../protocols/copywriting-brainstorming.md` §Task 9。

### Long-form items（form_type = long の場合適用）

- [ ] **CHK-CTW-INTAKE-L01 (Word count range)** [FATAL]: Understanding
  Summary §Form-Specific Spec に字數範囲が明示されている（例：
  800-1200 / 2000-3000 / 5000+）。framework 選択と段構成の前提。
  未指定は FATAL。form_type ≠ long は `N/A`。**Grounded in**:
  `../protocols/copywriting-brainstorming.md` §Task 5 Long-form +
  `../standards/long-form-pasona-canon.md` §使い分け表。
- [ ] **CHK-CTW-INTAKE-L02 (Schwartz awareness level)** [FATAL]:
  Understanding Summary §Target Audience または §Form-Specific Spec
  に Schwartz 5 levels のいずれか（Unaware / Problem-Aware /
  Solution-Aware / Product-Aware / Most-Aware）が明示されている。
  未明示のまま AI 推薦を silent 採用は FATAL（disclosure なしで
  Schwartz core rule「Unaware に直接 Offer 禁止」違反リスク）。
  AI 推薦を使用者が明示承認した場合は §Level 2/3 Defaults Accepted
  への disclosure 必須、disclosure あれば PASS。form_type ≠ long
  は `N/A`。**Grounded in**:
  `../standards/persuasion-psychology-anchor.md` §Schwartz 5 Levels
  of Awareness。
- [ ] **CHK-CTW-INTAKE-L03 (Framework choice)** [FIXABLE]: Understanding
  Summary §Framework に旧 PASONA / 新 PASONA / PASBECONA のいずれかが
  明示されている、または AI 推薦 (auto-pick) への使用者承認が
  §Level 2/3 Defaults Accepted に disclosure されている。未明示
  + disclosure なしは FIXABLE（next phase の `write-long-form-copy.md`
  §Phase 1 で確定可能だが intake 段階で決めていない旨の明示が必要）。
  form_type ≠ long は `N/A`。**Grounded in**:
  `../standards/long-form-pasona-canon.md` §使い分け表 +
  `../protocols/copywriting-brainstorming.md` §Task 7 Long-form。

### Mid-form items（form_type = mid の場合適用）

- [ ] **CHK-CTW-INTAKE-M01 (Benefits list)** [FATAL]: Understanding
  Summary §Form-Specific Spec に benefits が**具體條列 3+ 項**で
  明示されている。「色々な benefit」「品質が良い」等の抽象 1 項は
  FATAL（BEAF の Benefit 段が機能しない）。form_type ≠ mid は
  `N/A`。**Grounded in**:
  `../protocols/copywriting-brainstorming.md` §Task 5 Mid-form +
  `../standards/mid-form-beaf-canon.md`。
- [ ] **CHK-CTW-INTAKE-M02 (Channel)** [FIXABLE]: Understanding Summary
  §Form-Specific Spec に channel（樂天 / Amazon JP / 店頭 POP /
  説明会 等）が明示されている。未明示は FIXABLE（BEAF 順序 tweak
  の前提だが default 順序で進行可能）。form_type ≠ mid は `N/A`。
  **Grounded in**: `../protocols/copywriting-brainstorming.md`
  §Task 5 Mid-form。

### Short-form items（form_type = short の場合適用）

- [ ] **CHK-CTW-INTAKE-S01 (Target emotion / pain)** [FATAL]: Understanding
  Summary §Target Audience または §Form-Specific Spec に target
  emotion / pain が明示されている（「憧れ」「不安」「好奇心」「怒り」
  等 1 語 + 具体的 context）。未指定は FATAL（5 切入点 map 不可能
  → approach 選択できない）。form_type ≠ short は `N/A`。**Grounded
  in**: `../standards/short-form-catchcopy-canon.md` §5 種切入点
  決策樹 + `../protocols/copywriting-brainstorming.md` §Task 4
  Short-form。
- [ ] **CHK-CTW-INTAKE-S02 (Intended channel)** [FATAL]: Understanding
  Summary §Form-Specific Spec に intended channel（SNS / banner /
  tagline / CM / 店頭 / 駅広告 等）が明示されている。未明示は FATAL
  （字數上限 + voice 選択の前提）。form_type ≠ short は `N/A`。
  **Grounded in**: `../protocols/copywriting-brainstorming.md`
  §Task 5 Short-form。

### Audit items（form_type = audit の場合適用）

- [ ] **CHK-CTW-INTAKE-A01 (Existing copy full text)** [FATAL]:
  Understanding Summary §Form-Specific Spec に既存 copy の**全文**が
  添付されている（summary / 要約 / 部分抜粋不可）。summary のみは
  FATAL（`copy-audit.md` Phase 1 Type ID が機能しない）。form_type
  ≠ audit は `N/A`。**Grounded in**:
  `../protocols/copywriting-brainstorming.md` §Task 5 Audit +
  `../protocols/copy-audit.md`。
- [ ] **CHK-CTW-INTAKE-A02 (Review focus)** [FIXABLE]: Understanding
  Summary §Form-Specific Spec に review focus（framework / ethics /
  voice / form-appropriate / 全体）が明示されている。未明示は
  FIXABLE（default = 全体で進行可能だが scope が広がる）。form_type
  ≠ audit は `N/A`。**Grounded in**:
  `../protocols/copywriting-brainstorming.md` §Task 5 Audit。

### Ideation items（form_type = ideation の場合適用）

- [ ] **CHK-CTW-INTAKE-I01 (Value proposition source)** [FATAL]:
  Understanding Summary §Product / Value Proposition に value prop
  source（user-supplied / planning-team output / PRODUCT-SPEC.md
  reference / 他）が明示されている。source 不明 + value prop が
  抽象のままは FATAL（発散 subagent の入力として機能しない）。
  user-supplied で value prop 文言が 1 文で具体化されていれば PASS。
  form_type ≠ ideation は `N/A`。**Grounded in**:
  `../protocols/copywriting-brainstorming.md` §Task 5 Ideation +
  `../protocols/copy-ideation-parallel.md` §Phase 1 §入力確認。

### Level 2 disclosure item（全 form type 適用）

- [ ] **CHK-CTW-INTAKE-D01 (Level 2 defaults disclosed)** [FIXABLE]:
  Task 6 voice / Task 7 framework・approach のうち使用者が明示選択
  せず AI 推薦を採用した項目は Understanding Summary §Level 2/3
  Defaults Accepted に明示 disclosure されている。silent default
  （使用者承認なし + disclosure なし）は FIXABLE。**Grounded in**:
  `../protocols/copywriting-brainstorming.md` §Rules §Level 2 預設
  採用は Summary に明示。

## Verdict Rules

- 任意 **1 項**が `FAIL_FATAL` → `NEEDS_REVISION`（BLOCKED を main
  agent に return、brainstorming phase に戻る）
- `FAIL_FIXABLE` のみ（FATAL なし）で **≤ 2 項** → `PASS_WITH_NOTES`
  （auto-revise trigger。brainstorming Task 9 Summary を 1 回
  補完して再 evaluate）
- `FAIL_FIXABLE` が **≥ 3 項** → `NEEDS_REVISION`（brainstorming
  全体に戻る）
- 全項目 `PASS` or `N/A` → `PASS`（next-phase protocol load 許可）
- `N/A` は **当該 form type では該当しない item** の場合のみ許可。
  form_type = long なら L01-L03 は評価対象、M/S/A/I-prefix は `N/A`。
  form_type = mid なら M01-M02 は評価対象、L/S/A/I-prefix は `N/A`。
  以下同様。

## Output Format

```json
{
  "verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "form_type": "long | mid | short | ideation | audit",
  "items": [
    {
      "id": "CHK-CTW-INTAKE-001",
      "status": "PASS | FAIL_FATAL | FAIL_FIXABLE | N/A",
      "evidence": "Specific Summary section reference or quoted line",
      "fix_instruction": "How to resolve (for FAIL_FIXABLE items); which brainstorming task to revisit (for FAIL_FATAL items)"
    }
  ],
  "summary": "1-3 sentence overall assessment + which Level 1 fields are missing if NEEDS_REVISION",
  "next_action": "load {protocol_name} | return to brainstorming Task {N} | auto-revise Summary"
}
```
