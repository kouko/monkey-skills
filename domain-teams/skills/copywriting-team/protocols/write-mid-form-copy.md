# Protocol: Write Mid-Form Copy（BEAF Canon 中文案撰寫）

**When to use**：中文案需求。典型情境為 樂天市場 / Yahoo!ショッピング / Amazon JP の商品ページ本文、店頭 POP（スーパー / 家電量販店 / 書店）、説明会 / 展示会 配布資料、B2B 製品カタログの 1 製品 1 ページ説明、EC サイトの商品一覧ページサマリー文。字數帯 数十〜数百字（1,000 字を超える場合は長文 protocol を検討）。

**Output**：BEAF 順序で構成された中文案 artifact。冒頭 Benefit / 第 2 段 Evidence / 第 3 段 Advantage / 最終段 Feature の 4 段階構成。購入ボタン隣接を前提として CTA 段は含めない。

**Grounds on**：`../standards/mid-form-beaf-canon.md`、`../standards/voice-and-tone.md`、`../standards/persuasion-ethics.md`

## Phase 1: BEAF 骨架

`mid-form-beaf-canon.md` §BEAF の 4 段階定義 に従い、4 段の骨格を**先に決める**。各段の骨格を確定してから文章化する（逆順で書くと Feature 先出しの誘惑に負ける）。

1. **Benefit 骨格**：購入後、読者の生活がどう良くなるか。「成った姿」を 1 文で記述。
   - 例（△）：「容量 500ml で便利」 → これは Feature の翻訳
   - 例（○）：「通勤バッグに入れて 1 日分の水分が賄える」 → 具体的生活変化
   - `copy-ideation-parallel.md` Phase 3 の「Benefit seed」を起点素材として使う。

2. **Evidence 骨格**：Benefit の客観的裏付けを 3 種以上列挙候補として準備。
   - 受賞 / 第三者評価 / 顧客レビュー / 臨床試験 / 検査結果 / 数値データ
   - 各 Evidence は**検証可能な形**で記述する（景品表示法 優良誤認対策）。

3. **Advantage 骨格**：競合商品との差別化。同カテゴリの他商品と比較した独自の強み。
   - 「高品質」「最高」などの主観的形容詞は Advantage ではない。
   - 「他社比 2 倍の〜」「業界唯一の〇〇認証」「独自技術の〇〇」など、**具体的数値 / 技術 / 認証** が canonical。

4. **Feature 骨格**：規格・成分・サイズ・カラー・素材・同梱物など客観基本情報。スペック一覧の役割。

## Phase 2: Benefit-first 順序検証

BEAF の最大の canonical 主張は「**先に糖を与え、後に証明を与える**」順序（`mid-form-beaf-canon.md` §Benefit-first 順序の重要性）。骨格が揃ったら順序を検証する。

1. **第一段の確認**：第一段が**必ず Benefit** であること。Feature を冒頭に置く商品ページは以下 2 点で失敗しやすい：
   - 読者は Feature の意味を自力で Benefit に翻訳しない（「500ml」を「1 日分の水分」と連想しない）
   - Benefit 不在の商品ページは「広告らしくない広告」になり購買モチベーションを形成しない

2. **段階間の認知 flow 対照**：
   - 興味（Benefit）→ 納得（Evidence）→ 差別化（Advantage）→ 確認（Feature）
   - この順序は読者の抱く疑問の順序「魅力 → 本当か → 他と何が違う → 具体的には何か」に一致する。

3. **字數分布の目安**：
   - 数十字 POP：B 60% / E 20% / A 10% / F 10%（Benefit が大部分）
   - 数百字 商品ページ：B 25% / E 30% / A 25% / F 20%（バランス型）
   - 1,000 字超の気配があれば **長文 protocol に切替**（`write-long-form-copy.md` の新 PASONA を検討）。

## Phase 3: Evidence 具体性検証 + 倫理境界

Evidence 段は景品表示法（JP）/ FTC Endorsement Guides（US）の直接影響範囲。`persuasion-ethics.md` §景品表示法要點 + §FTC Endorsement Guides 要點 を適用。

1. **禁用表現 check**：以下は**空話**であり Evidence として機能しない。
   - 「多くの方にご愛用いただいています」（具体数なし）
   - 「業界最高品質」「世界初」「No.1」（根拠なしの最上級表示 — 景品表示法 優良誤認）
   - 「お客様の声：大満足でした」（架空 testimonial の疑い）

2. **検証可能性の確認**：各 Evidence について以下を自問：
   - 第三者が事実確認できる情報源はあるか（受賞年度 / 機関名 / 数値の出典）
   - testimonial は実在顧客の発言か、代表的（typical）な結果か（FTC §255.2）
   - 比較優位表示（「他社比 2 倍」）の比較対象と測定条件は明示されているか

3. **ステマ告示対応**（`persuasion-ethics.md` §ステルスマーケティング告示）：
   - インフルエンサー起用の testimonial には「広告」「PR」「Sponsored」明示
   - アフィリエイトリンクを含む商品ページは関係性開示

4. **打消し表示ガイドライン**（消費者庁 2017）：
   - 「※条件あり」disclaimer でメイン訴求を実質的に否定していないか
   - disclaimer の文字サイズ・色・背景コントラストはメイン訴求と同等に読めるか

## Phase 4: Voice 整合性

中文案は機能説得型（客観）だが voice は不変（`voice-and-tone.md` §Voice vs Tone）。商品ページ / POP / カタログ の情境でも brand voice を維持する。

1. **Voice 4 軸 position 対照**（`voice-and-tone.md` §Voice 定義の 4 軸）：Formality / Seriousness / Respectfulness / Enthusiasm の各軸の position が全段で一貫しているか。

2. **Tone は情境依存で調整可**（`voice-and-tone.md` §Tone 情境切換表）：
   - 商品ページ本文 → matter-of-fact 寄り（過度な enthusiasm は空洞 hype に聞こえる）
   - POP → enthusiastic 寄り（衝動買い向け）
   - B2B カタログ → serious / formal 寄り

3. **Ogilvy「respect the reader's intelligence」**（`voice-and-tone.md` §Ogilvy 長文案 voice 經典原則）：
   - condescending 語氣や空洞 hype（amazing / revolutionary / game-changing）を使わない
   - 各文が earn its place する（削れる文がないか自問）

## Rules

- BEAF の canonical 順序（B→E→A→F）を必ず遵守する。Feature 先出しは `mid-form-beaf-canon.md` §Anti-Patterns の頭に挙がる違反（`mid-form-beaf-canon.md` §Anti-Patterns）。
- BEAF を FAB（米国 Feature-Advantage-Benefit の 3 段階）の順序で実装しない。BEAF は FAB の逆順 + Evidence 挿入（`mid-form-beaf-canon.md` §FAB との差異）。
- BEAF に CTA を必須段として追加しない。商品ページの購入ボタンが Action を兼ねる。CTA 段を足すと PASONA との境界が曖昧になる。
- 1,000 字を超える気配があれば長文 protocol（`write-long-form-copy.md`）に切替を検討。BEAF は数十〜数百字帯が canonical。
- Evidence は検証可能な情報のみ使う。架空 testimonial / 根拠なし最上級表示 / 虚偽 "as seen on" は禁止（`persuasion-ethics.md` §Copy 層面的具体反模式）。
- 主観的形容詞（「高品質」「最高」）を Advantage として使わない。具体的数値 / 技術 / 認証 に置換する。
- 打消し表示でメイン訴求を実質否定しない（消費者庁 2017 ガイドライン）。

## Anti-Patterns

- **Feature から書き始める**：BEAF の canonical 順序違反。スペック羅列が冒頭に来ると読者はスクロールを止めない（`mid-form-beaf-canon.md` §Anti-Patterns）。
- **Evidence 段を省略する**：Benefit だけでは「広告の誇張」に見える。客観的裏付けが不可欠。
- **BEAF を FAB の順序で実装する**：Evidence の位置と Benefit の位置を入れ替えると canonical 違反。
- **Advantage を主観的形容詞で埋める**：「高品質」「最高」は Advantage ではない。具体的数値 / 技術 / 認証 が canonical。
- **Benefit を Feature の翻訳で書く**：「500ml 入っているので便利」は Feature の翻訳に過ぎない。「通勤バッグに入れて 1 日分の水分が賄える」まで具体化。
- **BEAF に CTA 段を追加する**：BEAF 自体には Action 段がない。購入ボタンが Action を兼ねる。
- **架空 testimonial / 根拠なし最上級表示を Evidence として使う**：景品表示法 優良誤認 / FTC §255.1 §255.2 違反。
- **「業界 No.1」「世界初」「最安値」を根拠なしに使う**：景品表示法 優良誤認 / 有利誤認の頻出違反類型（`persuasion-ethics.md` §Anti-Patterns）。
- **condescending 語氣 / 空洞 hype で voice を壊す**：Ogilvy「respect the reader」違反（`voice-and-tone.md` §Anti-Patterns）。
