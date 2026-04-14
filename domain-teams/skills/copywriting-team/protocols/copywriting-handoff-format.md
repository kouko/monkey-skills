# Copywriting Handoff Format Protocol

copywriting-team 候補と完成品の標準出力フォーマット + pipeline
progress reporting。候補の提示方法と使用者介入点の規範。

## Primary Sources

- `copy-ideation-parallel.md` §Phase 3 Handoff — 既に候補出力
  フォーマット（優勝 3-5 本 + 「なぜ良いか」3 項 + 次点 3-5 本 +
  A 型図解）を定義。本 protocol はそれを一般化し、ideation 以外
  の workflow（long / mid / short / audit）にも適用可能な
  共通フォーマットとして再定義する。
- `copywriting-brainstorming.md` §Task 9 Understanding Summary —
  intake フェーズの構造化 spec。handoff 時に再掲して candidate
  との対応関係を明示する。
- `../standards/ideation-taniyama-discipline.md` §「なんかいいよね
  禁止」— 3 項理由の義務化の根拠。
- `../standards/short-form-catchcopy-canon.md` §5 種切入点決策樹 +
  `../standards/long-form-pasona-canon.md` — approach / framework
  label の vocabulary 出典。

## Section 1: Candidate Output Format

候補（短文 headline / 長文 draft / 中文 BEAF block いずれも）
を提示するときは必ず以下の 6 要素を明示する：

```
候補 #N：[文案本體]
├─ voice reference: [糸井 / 岩崎 / 眞木 / 谷山 / Ogilvy / 預設]
├─ approach / framework:
│   - short-form: 5 切入点のいずれか（利益 / 恐懼 / 顛覆 / 呼喚 / 提問）
│   - mid-form: BEAF 順序 + channel tag（樂天 / Amazon / POP / 説明会）
│   - long-form: PASONA 系 framework 名（旧 / 新 / PASBECONA）+ 段別
│   - ideation: Mandal-Art 方向 + VS probability
├─ VS probability（ideation Phase 1 産出時のみ）: p = 0.xx
├─ 為何好（3 項、必須、「なんかいいよね」禁止）:
│   1. 何が読者に何を伝えるか
│   2. 既存の類似コピーに対して何が新しいか
│   3. ターゲットの生活 / 文脈で何が共鳴するか
└─ 倫理 self-check: [通過 / 有疑慮 + 説明]
    - 景品表示法 / FTC / ステマ告示 の risky 表現 self-scan 結果
    - 疑慮ありの場合は ethics-checklist.md MUST gate に委ねる旨を明示
```

### Long-form draft 提示のバリエーション

長文案 draft（2000 字+）の候補は full text を 1 候補だけ提示する
ことが多い。その場合：

- 上 block の 6 要素は冒頭 metadata として提示
- 段別（Affinity / Problem / Offer / Narrowing / Action 等）に
  subsection heading を付け、各段で使った voice / 心理技法の
  annotation を添える
- 字數カウントを末尾に記載（`{actual} / {target range}` 形式）

### Audit 時の Variant rewrite フォーマット

`copy-audit.md` Phase 3 で rewrite variants を提示する場合は上の
6 要素 block を variant ごとに並列提示。各 variant の冒頭に「原文
との差分」要約を 1 文添える。

## Section 2: Progress Reporting Templates

pipeline が multi-phase に入るとき、使用者への透明性を保つために
以下のテンプレートで報告する。

### Phase 啟動メッセージ

```
[Claude] ✓ Phase {X}-{Y} 啟動：{protocol_name}
  入力: {input summary, 1 line}
  予定: {phase 内の step sequence}
```

例：
```
[Claude] ✓ Phase 1-3 啟動：copy-ideation-parallel.md Phase 1 発散
  入力: 商品=X, audience=Y, form=short
  予定: 曼陀羅 8 方向 dispatch → VS 候補生成 → 64 候補集計
```

### Step-by-step 進度條

```
⏳ Step 1/8: 曼陀羅方向 decision — 8 方向を選定中
✓ Step 1/8: 曼陀羅方向 decision — {情感觸發 / 掛詞 / 逆説 / …}
⏳ Step 2/8: subagent dispatch — 8 並行 agent 起動
✓ Step 2/8: subagent dispatch — 8 agent 並行走行中
…
```

未完了は `⏳`、完了は `✓`。失敗は `✗` + 原因 1 行。skip した step
は `—` + skip 理由 1 行。

### Phase 完了 checkpoint メッセージ

```
[Claude] ✓ Phase {X} 完了：{phase_name}
  生成物: {artifact summary}
  所要: {step count}, {duration if relevant}

次の選択肢:
  ▶ continue — 直接 Phase {X+1} に進む
  ⏸ adjust — Phase {X} 結果を調整してから進む
  ↻ retry — Phase {X} を再実行（入力を変えて）
  ✗ stop — ここで停止し使用者に return

使用者が何も指定しない場合、{default option} を採用します。
```

default option の選択規則：

- ideation Phase 1 → Phase 2: default は `continue`（64-100 候補
  の mode collapse check をパスした場合）
- ideation Phase 2 完了後：default は `⏸ adjust`（優勝 3-5 本の
  使用者選択 checkpoint）
- long-form draft 完了後：default は `⏸ adjust`（字數 / voice /
  段別の調整確認）
- gate 失敗後：default は `stop`（NEEDS_REVISION の場合は必ず
  使用者判断を待つ）

## Section 3: Mid-Pipeline Checkpoint Rules

以下の checkpoint は skip 禁止。silent proceed は anti-pattern。

### ideation Phase 2（KJ 収斂）完了後

`copy-ideation-parallel.md` §Phase 2 §文章化 + 谷山審査 直後：

- 優勝 3-5 角度を**必ず使用者に提示**して選択させる
  - (a) `accept all` → 全 3-5 を後続 protocol の seed として採用
  - (b) `pick subset` → 手動で 1-3 を subset 選択
  - (c) `reject, redo` → Phase 1 発散に戻って方向を変える
- 次点 3-5 本も appendix として提示（A/B 変体用）
- 省略して即座に次 phase へ進むのは anti-pattern

### long-form draft（> 2000 字）完了後

預設は**段階式展示**：

1. Draft 全体の outline（段別 heading + 各段 1 文要約）を先に提示
2. 使用者が「見たい段」を指定 → その段だけ full text 提示
3. 段ごとの調整を終えてから全体 full text を最終提示

使用者が「整篇一次に全部見せて」と指定した場合のみ一括提示。
2000 字以上の一括提示は デフォルト動作ではない。

### Gate NEEDS_REVISION 発生時

MUST / SHOULD gate のいずれかが `NEEDS_REVISION` を返した場合：

- gate 名 + 失敗した checklist item / rubric dimension を提示
- 具体的な修正方向（evaluator の fix_instruction）を提示
- 使用者に以下の選択肢を出す：
  - `auto-retry` → worker を再起動して自動修正（原則 max 2 回）
  - `manual` → 使用者自身が修正指示を書いて再 dispatch
  - `override` → 使用者がこの gate 失敗を受容（非推奨、理由記録必須）

silent auto-retry は禁止。使用者に必ず gate 失敗を見せる。

### Gate PASS_WITH_NOTES 発生時

feedback を提示した上で auto-revise が走る。ただし使用者には**何を
修正したか**を完了後に 1 行報告：

```
[Claude] ✓ auto-revise 完了（PASS_WITH_NOTES feedback 対応）
  修正内容: {diff summary, 1-2 line}
```

2 回目の PASS_WITH_NOTES で re-revise は **NEEDS_REVISION 扱い**に
escalate（`SKILL.md §Gate Protocol §Max 2 rounds before escalating`）。

## Section 4: Audit Report Format

`copy-audit.md` の最終成果物フォーマット：

### Type ID block

```
## Audit Type ID

- Form type detected: {long / mid / short}
- Framework detected: {新 PASONA / BEAF / 利益切入 / 不明 / etc.}
- Voice pattern detected: {糸井系 / 岩崎系 / Ogilvy系 / 混在 / etc.}
- Channel（推測）: {LP / EC / SNS / CM / etc.}
```

### Issues by severity

issue は severity で sort、同 severity 内は artifact 出現順：

```
## Issues

### 🔴 HIGH — {count} 件
1. **{issue title}**
   - Location: {quoted line / paragraph reference}
   - Problem: {what's wrong, 1-2 sentence}
   - Grounded in: {standard file or checklist item id}
   - Fix suggestion: {concrete before → after 提案}

### 🟡 MEDIUM — {count} 件
…

### 🟢 LOW — {count} 件
…
```

severity 定義：

- **🔴 HIGH** — 法律抵触 / fatal framework 違反 / 景品表示法 or
  FTC risk（ethics-checklist.md FATAL 相当）
- **🟡 MEDIUM** — framework 順序逸脱 / voice 漂移 / form 不適合
  （SHOULD gate 相当）
- **🟢 LOW** — 字數オーバー軽微 / 表記ゆれ / 磨き不足
  （stylistic concern）

### 綜合 verdict + 後続アクション

```
## Verdict

- 法律層: {pass / risky / fatal}（景品表示法 / FTC / ステマ告示）
- framework 層: {canonical / deviated / unclear}
- voice 層: {consistent / drift / abstract}
- form 層: {appropriate / overflow / underflow}

## Recommended Next Steps

- [ ] Fix 🔴 HIGH items（blocker）
- [ ] Consider 🟡 MEDIUM items（strongly recommend）
- [ ] Optional 🟢 LOW items（polish）
- [ ] 必要に応じて rewrite variants 生成（→ Phase 4 ethics gate 対象）
```

使用者の選択肢：

- `fix-and-redeliver` → 上記 checklist を worker で消化、rewrite
  variants 込みで再 handoff
- `deliver-as-is` → 現状を使用者が受容（非推奨の場合は理由記録）
- `manual-only` → 使用者自身が修正、本 team は介入しない

## Rules

- **任意の候補必附 3 項理由**。「なんかいいよね」禁止（谷山 2007
  + `ideation-taniyama-discipline.md` §「なんかいいよね禁止」
  ルール）。3 項書けない候補は削除する
- **label 欄位不可空**。voice reference / approach / framework /
  channel のいずれかが「不明」のまま handoff するのは禁止。
  brainstorming phase で確定していない場合は brainstorming に
  戻る
- **progress 必透明**。phase 啟動 / 各 step / phase 完了の報告を
  skip しない。silent multi-phase 実行は anti-pattern
- **mid-pipeline checkpoint skip 禁止**。ideation Phase 2 完了後
  の優勝角度提示、long-form 2000 字+の段階式展示、gate
  NEEDS_REVISION 時の使用者判断待ちは**必須 checkpoint**
- **Gate 失敗の可視化**。NEEDS_REVISION / PASS_WITH_NOTES が出た
  ら必ず使用者に通知。silent retry 禁止
- **VS probability を省略しない**。ideation Phase 1 候補は VS
  確率欄付きで handoff（`verbalized-sampling.md` §Anti-Patterns）
- **3 項理由の視点規律**。「何を伝える / 何が新しい / 何が共鳴する」
  の 3 軸で書く（`ideation-taniyama-discipline.md` §3 項理由書
  テンプレート）

## Anti-Patterns

- **無理由の候補陳列**：「候補 A / B / C どれが好き？」だけで 3 項
  理由を付けない。谷山 2007「なんかいいよね」の典型。使用者は
  印象で選ぶことになり、後工程で品質が担保されない
- **隠れた gate 問題**：MUST gate が NEEDS_REVISION を返したのに
  使用者に伝えず silent retry。倫理 gate 失敗を使用者に見せない
  のは危険（景品表示法抵触を自動修正で誤魔化すリスク）
- **一括 2000 字+ 長文出力**：段階式展示 default を守らず 5000 字の
  LP を一気に出す。使用者の review cost が膨大になり、段別の voice
  調整ができない
- **NEEDS_REVISION を silent で retry**：gate が revision を要求
  しているのに使用者判断を経ずに worker を再起動する。max 2 rounds
  ルール違反 + 使用者の control を奪う
- **label 欄空白**：`voice reference: （未定）` のまま handoff。
  brainstorming phase で voice 選択を skip した結果。intake gate
  で PASS_WITH_NOTES の disclosure 義務を果たしていない
- **progress 報告を emoji だけで済ませる**：`✓` だけで何の phase
  が完了したか書かない。phase 名 / step 名 / 生成物 summary を
  1 行で添える
- **default option を silent proceed にする**：checkpoint で使用者
  入力を待たずに「continue」を自動採用する。checkpoint の目的は
  使用者介入の機会を作ることなので、最低 1 回は使用者 ack を待つ
- **audit report で severity を混ぜる**：🔴 HIGH と 🟡 MEDIUM を
  同じ sort で並べる。使用者が blocker を見逃す。必ず severity で
  section 分離する
