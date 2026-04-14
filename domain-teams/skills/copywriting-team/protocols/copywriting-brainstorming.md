# Copywriting Brainstorming Protocol

模糊な文案依頼から明確な制作規格を導き出す。Checklist-driven の
対話プロセス。完了するまで copy 作成に進まない。

## Primary Sources

- `../standards/voice-and-tone.md` — Ogilvy / 糸井 / 岩崎 / 18F /
  Mailchimp voice axes。Task 6 voice 選択の選択肢は本檔 §JP 情緒
  共鳴傳統 §Ogilvy 長文案 voice 經典原則 に準拠。
- `../standards/persuasion-psychology-anchor.md` — Schwartz 1966
  *Breakthrough Advertising* 5 levels of awareness。Task 5 の長文
  awareness level 欄位はここに準拠（Unaware / Problem-Aware /
  Solution-Aware / Product-Aware / Most-Aware）。
- `../standards/short-form-catchcopy-canon.md` — §5 種切入点決策樹
  （利益 / 恐懼 / 顛覆 / 呼喚 / 提問）。Task 7 短文 approach 選択
  はここに準拠。
- `../standards/long-form-pasona-canon.md` — 旧 / 新 / PASBECONA
  の使い分け規範。Task 7 長文 framework 推薦の根拠。
- `../standards/mid-form-beaf-canon.md` — BEAF (Benefit → Evidence
  → Advantage → Feature) の適用範囲（樂天 / Amazon / POP / 説明会）。
- 構造先例：`../../planning-team/protocols/planning-brainstorming.md`
  — sequential checklist + Socratic grill + Understanding Summary +
  user confirmation gate の canonical pattern。本 protocol は同構造を
  copywriting 向けに書き直したもの。

## Hard Gate

Do NOT load `write-long-form-copy.md` / `write-mid-form-copy.md` /
`write-short-form-copy.md` / `copy-ideation-parallel.md` /
`copy-audit.md`, generate any copy draft, or dispatch ideation
subagents **until** this checklist is fully completed **and** the
user has explicitly approved the Understanding Summary.

Level 1 欄位 (form type / product / audience / form-specific must
fields) が揃わない状態で先に進んだ場合は `intake-completeness-checklist.md`
MUST gate が FAIL_FATAL → NEEDS_REVISION を返し BLOCKED となる。

## Checklist

Complete each task in order. Each task requires user input (または
明示的な「推薦採用」) before proceeding. One question per message.
Prefer multiple choice with **推薦回答** when possible.

### 1. Understand the request

使用者の依頼を**判断せずに**読む。「キャッチコピーお願いします」
レベルの曖昧さでも OK。この段階では質問しない。使用者が literally
何を言ったかを 1-2 文で言い換えて確認する。

- ヤング (1988 日譯) 『アイデアのつくり方』の **材料収集** 段階に
  相当。判断せずに情報を吸収する。
- 依頼文に既に form type / product / audience 等が書かれていれば
  後続 Task でその情報を再度質問しない（「可查的不問」原則）。

### 2. Identify form type

何を書くかを確定する。複数選択：

- **Long-form**（LP / sales letter / 記事広告 / メルマガ）
- **Mid-form**（EC 商品説明 / 樂天 / Amazon / 店頭 POP / 説明会）
- **Short-form**（キャッチコピー / tagline / headline / SNS / banner）
- **Ideation Workshop**（value prop から候補角度を発散 → 後続 protocol の種）
- **Audit**（既存文案の review + 改善提案）

依頼文脈から推薦する（例：「LP の headline 10 本」→ Ideation or
Short-form）。曖昧なら確認。

### 3. Clarify product / service

**Level 1 Must 欄位**（欠けたら BLOCKED）。

- 何の商品 / サービスか
- 主要 value proposition（1 文で）
- すでに PRODUCT-SPEC.md / planning-team 出力があればそれを指し、
  読んで取得する（「可查的不問」）

不明確なまま進むと 5 切入点 / Schwartz level / BEAF benefit 段
いずれも選択不能。依頼者が value prop を言語化できない場合は
`planning-team` を推薦し、BLOCKED で返す。

### 4. Identify target audience

**Level 1 Must 欄位**（欠けたら BLOCKED）。form type により深さ
が変わる。

- **Short-form** の場合：target emotion / pain を優先確認
  （「どんな気持ちに寄り添いたいか / どんな痛点を突きたいか」）
  → Task 7 の 5 切入点 map の前提。
- **Long-form** の場合：demographic + **Schwartz awareness level**
  （5 段階：Unaware / Problem-Aware / Solution-Aware /
  Product-Aware / Most-Aware）を確認。推薦：商品種別 + 既存
  市場成熟度から推論して AI が提案 → 使用者が確認 or 修正。
- **Mid-form** の場合：channel 前提の受眾（樂天利用者 / Amazon
  prime 会員 / POP 店頭客 等）を確認。
- **Ideation / Audit** は上 3 type の下位 frame として質問。

### 5. Form-specific Level 1 fields（branching）

form type に応じて以下の追加必須 fields を取得する。

- **Long-form**:
  - 字數範囲（例：800-1200 / 2000-3000 / 5000+ 字）
  - Schwartz awareness level（Task 4 で未確定なら確定）
  - `long-form-pasona-canon.md` §使い分け表 に基づき framework
    推薦：短中文 → 旧 PASONA、中長文 → 新 PASONA、高説得厚 →
    PASBECONA。
- **Mid-form**:
  - benefits list（**具體條列 3+ 項**、抽象語不可）
  - channel（樂天 / Amazon JP / 店頭 POP / 説明会）
- **Short-form**:
  - target emotion / pain（Task 4 で既取得ならスキップ）→
    5 切入点 map の前提
  - intended channel（SNS / banner / tagline / CM 等）
  - 字數上限（預設 15 字、JP 7-15 字帯を canonical とする）
- **Ideation Workshop**:
  - 候補数（預設 5、3-5 範囲推薦）
  - value prop source（user-supplied / planning-team /
    PRODUCT-SPEC / 他）
- **Audit**:
  - existing copy 全文（summary でなく原文必須）
  - review focus（framework / ethics / voice / form-appropriate /
    全体）

### 6. Voice / tone preference（Level 2）

使用者にとって望ましい語感を複数選択 + 推薦で確認：

- **糸井系**（状態提案・曖昧余地・助詞結尾）—『voice-and-tone.md』
  §JP 情緒共鳴傳統 §糸井。
- **岩崎系**（人生観・季節感・いのち温度）— 同 §岩崎。
- **眞木系**（掛詞・音韻・短文技巧）— 代表作「恋が着せ、愛が
  脱がせる。」系。
- **谷山系**（入口設計・「書きたいこと vs 言いたいこと」の分離）—
  `../standards/ideation-taniyama-discipline.md` 全体。
- **Ogilvy系**（benefit-clear・respect the reader・fact-based）—
  `voice-and-tone.md` §Ogilvy 長文案 voice 經典原則。
- **預設**（AI が audience + form + channel から推薦、使用者承認で
  Level 3 扱いに降格）。

ブランドに既存 voice guide があれば honor を優先し本 Task をスキップ。

### 7. Framework / approach preference（Level 2 — branching）

form type に応じて選択肢が異なる：

- **Long-form**:
  - 旧 PASONA（短中文、DM / メール）
  - 新 PASONA（中長文 LP / メルマガ、Affinity 入口）
  - PASBECONA（2000+ 字帯、B/E/C で説得厚重増）
  - 推薦は Task 5 字數範囲 + Task 4 awareness level に基づき AI
    提示（未確定なら Solution-Aware 既定 + 新 PASONA 既定）。
- **Mid-form**:
  - BEAF (Benefit → Evidence → Advantage → Feature) 既定。
  - channel により順序 tweak（POP = Benefit-heavy / 説明会 =
    Evidence-heavy 等）を確認。
- **Short-form**:
  - 5 切入点（利益 / 恐懼 / 顛覆 / 呼喚 / 提問）より選択。
    `short-form-catchcopy-canon.md` §5 種切入点決策樹 に基づき
    audience emotion から AI が推薦。
- **Ideation**:
  - 曼陀羅 8 fan-out + VS / VS 単独 / 短文系 5 切入点組込み
    いずれかを `copy-ideation-parallel.md` §Phase 1 工具組合決策 に
    従い推薦。
- **Audit**:
  - form type 既知なら同じ framework を適用、未知なら
    `copy-audit.md` の Type ID step で先行推定。

### 8. Grill — challenge assumptions

Task 1-7 で収集した情報を基に、使用者の意図と仮定を質問して
共通理解を構築する。一度に一つの質問。各質問に**推薦回答**を
添える。`planning-brainstorming.md` §Task 4b Grill の 3 軸を
copywriting 向けに転写：

- **前提への挑戦**: 「X とおっしゃいましたが、受眾の awareness
  level を考えると Y の approach のほうが効果的では？」例：
  「Problem-Aware 受眾に直接 Offer を closer する指定は Schwartz
  1966 core rule に反します — 新 PASONA で Affinity から入るのが
  canonical ですが、意図的ですか？」
- **依存関係の深掘り**: 「もし audience 仮定が間違っていたら、
  文案全体を書き直す必要がありますか？ 主要欄位を確定させて
  から発散すれば後戻りが少なくなります」
- **境界条件**: 「倫理的に避けるべき表現はありますか？ 例：
  『業界 No.1』『24 時間限定』など景品表示法抵触リスクのある
  最上級 / 稀少性表現。競合を貶す、偽の期限、偽の testimonial
  も同様です」
- **voice 衝突の確認**: 「既存ブランド voice guide と Task 6
  選択が衝突していませんか？ voice guide は framework より優先
  です（`voice-and-tone.md` §Framework と voice の接点）」

読めば分かる質問（依頼文 / PRODUCT-SPEC / 既存ブランドアセット
から取得可能なもの）は使用者に聞かず自分で調べる。未解決の分岐が
なくなるか、使用者が先に進みたいと言うまで続ける。

### 9. Produce Understanding Summary

Task 10 の user confirmation gate に進む前に、理解の要約を構造化
して提示：

```
## Understanding Summary

### Request
[Task 1 で言い換えた使用者の依頼]

### Form Type
[long / mid / short / ideation / audit]

### Product / Value Proposition
[Task 3 で確定した内容]

### Target Audience
[demographic / persona / Schwartz level (long) / emotion (short)]

### Form-Specific Spec
[Task 5 で確定した字數・channel・benefits・候補数 等]

### Voice Reference
[Task 6 選択 — 糸井 / 岩崎 / 眞木 / 谷山 / Ogilvy / 預設]

### Framework / Approach
[Task 7 選択 — 新 PASONA / BEAF / 利益切入 等 + 推薦根拠]

### Confirmed Assumptions
[Task 8 grill で検証された仮定]

### Resolved Ambiguities
[曖昧だったが解決された問題]

### Level 2/3 Defaults Accepted
[使用者が選ばず預設採用したもの — intake-completeness-checklist
 の PASS_WITH_NOTES 対象]
```

### 10. User confirmation gate

Understanding Summary を提示した上で以下の選択肢を示す：

- **✓ 確認開始撰写** → 次 phase の protocol を load（form type に
  応じて `write-long-form-copy.md` / `write-mid-form-copy.md` /
  `write-short-form-copy.md` / `copy-ideation-parallel.md` /
  `copy-audit.md`）
- **✗ 調整某項** → 当該 Task に戻って再確認
- **↻ 重新來過** → Task 1 から再スタート（使用者が依頼内容を
  根本的に変更した場合）

使用者の明示的な ✓ 確認を得るまで次 phase に進まない。**silent
proceed は禁止**。

## Rules

- **一度に一つの質問**。複数の質問を一つのメッセージにまとめない
- **Multiple choice 優先**。open-ended より選択肢を提示する
- **各質問に推薦回答を添える**。聞くだけでなく提案もする
  （Task 6/7 では audience + form から AI 推論した推薦を提示）
- **可查的不問**。依頼文 / PRODUCT-SPEC / 既存 voice guide から
  取得可能な情報は使用者に聞かず自分で読む
- **Understanding Summary は hard gate**。使用者の ✓ 確認を得る
  まで next phase の protocol を load しない
- **Level 1 欠落 → BLOCKED**。form type / product / audience /
  form-specific must のいずれかが一輪質問後も未取得なら
  `intake-completeness-checklist.md` で FAIL_FATAL → NEEDS_REVISION
- **Level 2 預設採用は Summary に明示**。使用者が選ばず AI 推薦を
  採用した項目は Understanding Summary §Level 2/3 Defaults
  Accepted に disclosure。silent default は禁止（intake gate で
  FAIL_FIXABLE）
- **voice guide > framework**。既存ブランド voice guide と Task 6
  選択が衝突する場合は voice guide を優先
- **grill を省略しない**。依頼が明確な場合でも Task 8 は簡略化
  可だが完全スキップしない（最低 1 問：倫理境界条件）

## Anti-Patterns

- **批量提問**：「form type は？ audience は？ 字數は？ voice は？」
  を 1 メッセージで並べる。使用者の認知負担が増え、回答の品質が
  下がる。一問一答を守る
- **Task 8 grill を省略して Task 9 に直行**：assumption 検証なしに
  Summary を書くと、silent assumption が含まれたまま next phase に
  渡り、後工程で「audience 仮定が違った」の手戻りが発生する
- **Level 1 未取得で next phase に進む**：form type / product /
  audience のいずれかが欠けた状態で `write-*.md` を load するのは
  intake gate 違反。必ず BLOCKED を返す
- **voice 選択肢を open-ended で聞く**：「どんな声で書きましょうか」
  は使用者が答えられない。糸井 / 岩崎 / 眞木 / 谷山 / Ogilvy /
  預設の multiple choice + 各系の代表作サンプル提示で負担を減らす
- **依頼文に answer が書いてあるのに質問する**：使用者が「Amazon JP
  の商品説明 800 字」と明示しているのに「form type は？」と聞くの
  は信頼を失う。読める情報は読んでから不足分のみ質問する
- **推薦なしの質問**：「5 切入点どれにしますか」だけで推薦を添えない。
  AI は audience emotion + 商品タイプから推論して「利益切入を推薦
  します、理由は〜」と添えるのが canonical
- **silent default で進める**：Level 2 を使用者が選ばなかったから
  といって AI 判断で採用しつつ Summary に書かない。必ず §Defaults
  Accepted に disclosure する
- **✓ 確認を取らずに next protocol を load**：Understanding Summary
  を提示した瞬間に「では write-long-form-copy.md を読みます」と
  進める。使用者の明示的 ✓ を待つ
