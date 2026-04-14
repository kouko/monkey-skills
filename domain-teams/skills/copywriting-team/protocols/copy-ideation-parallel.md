# Protocol: Copy Ideation Parallel（散らかす → 選ぶ 2 階段並行發想）

**When to use**：需要從 value proposition 生成多個文案候選角度時。典型情境為 landing page headline 候選發想、キャッチコピー 選角 workshop、キャンペーン コンセプト 発散、或撰寫 protocol 執行前的 Phase 0 準備（為長 / 中 / 短文案 protocol 提供種子材料）。

**Output**：3-5 個經 KJ 收斂的優勝角度（每角度附「なぜ良いか」3 項理由），作為後續撰寫 protocol 的 Phase 3 種子（長文 → Affinity seed / 中文 → Benefit seed / 短文 → headline seed）。

**Grounds on**：`../standards/ideation-mandalart.md`、`../standards/ideation-kj-convergence.md`、`../standards/ideation-taniyama-discipline.md`、`../standards/verbalized-sampling.md`

本 protocol は copywriting-team の ideation layer を代表するパイプラインであり、撰寫 protocol（write-long / mid / short-form-copy）の Phase 0 として呼び出されるか、独立した発想 workshop として実行される。

主要な役割分担：
- main worker：dispatch / 収斂統括 / 人類 checkpoint 代理（evaluator agent 経由）
- parallel subagents：散らかす段階（Phase 1）のみ、独立文脈から発散を担う
- KJ 収斂（Phase 2）と 谷山審査：main worker + 人類 / evaluator checkpoint が担当
- 撰寫 protocol：Phase 3 の handoff を受け取り、各文案類型に応じて展開

## Phase 1: 発散（parallel subagents）

main worker 接收三項必備入力，再決定發散工具的組合。

1. **入力確認**：
   - value proposition / key message（planning-team 輸出、或使用者直接指定）
   - target audience 敘述（persona 草稿或 segment 定義）
   - 文案類型（長 / 中 / 短、媒体）— 影響後續 handoff 目標

2. **工具組合決策**：`ideation-mandalart.md` §「輔助方向庫」提供 16+ 個衍生方向（非今泉原典規範，可自由挑選或忽略）。
   - 題目情緒重 / 有明確文化脈絡 → **曼陀羅 8 fan-out 推薦**。從輔助方向庫依「選擇策略」選 8 方向。
   - 題目方向尚未明確 / 短時間內需大量詞彙 variation → **VS 單 agent 推薦**（跳過曼陀羅結構層）。
   - 若採曼陀羅，同時仍以 VS 作為詞彙層多樣化手段（`verbalized-sampling.md` §Mandal-Art との補完関係 Pattern B）。
   - 長文案の Phase 0 用途では「PASONA 段階 × 各段独立 Mandal-Art」の分層運用を推奨（`ideation-mandalart.md` §應用於 copywriting — 長文案適用度は低、各段独立展開が正）。

3. **方向選定（曼陀羅 path のみ）**：`ideation-mandalart.md` §輔助方向庫 §選擇策略 に従い 8 方向を決める：
   - 題目情緒重 → {情感觸發、故事開頭、共通体験、感官描寫} 寄り
   - 題目理性重 → {數字刺激、比較對照、権威 / 証拠、問題解決路徑} 寄り
   - 題目短文 / 標語 → {掛詞、逆説、余白、極端化、疑問句式} 寄り
   - 題目商品導向 → {ベネフィット表達、feature 轉譯、比較對照} 寄り
   - 8 方向を上記 4 軸から mix しても、単一軸から集中的に取っても可。選定根拠は後工程検証用に記録。
   - 「輔助方向庫」は後人衍生である旨を handoff に明記する。今泉 1987 原典の規範と混同しない（`ideation-mandalart.md` §Critical Attribution Corrections #1）。
   - 8 方向を強制固定（毎回同じ 8 方向）しない。固定すると「意外な観点」の湧現率が下がる（`ideation-mandalart.md` §Anti-Patterns）。

4. **Subagent prompt 組件**（每 subagent prompt 必須包含三要素）：
   - 單一方向主題（「生活情境」「掛詞」等，取自 `ideation-mandalart.md` §輔助方向庫）
   - Verbalized Sampling template：產 8 候選 + 各候選 probability（遵循 `verbalized-sampling.md` §Pattern A）
   - **散らかす 原則**（`ideation-taniyama-discipline.md` §階段 1）：禁止自我審查、量優先於質、允許「意図的に変な方向」（無難 80% + 奇抜 20% の比率を明示）

5. **並行 dispatch**：採用 `dispatching-parallel-agents` 模式，8 subagent 同時執行。每 subagent 輸出 8 候選 → 合計 64 候選（VS 單 agent 路線則輸出 40-80 候選）。main worker 不在此階段做任何質量過濾。

6. **Mode collapse check**：全 subagent の出力を確認し、候補全体が高 probability 近傍に偏っていないかを見る。偏っている場合は mode collapse が緩和されていないサイン（`verbalized-sampling.md` §Pattern C）。該当 subagent のみ re-generate を指示する。

7. **候補量の canonical 目安**：64-100 本を満たすまでは Phase 2 に進まない。量を満たさない状態での収斂は「選ぶ階段」が機能せず、既知の安全圏から抜け出せない（`ideation-taniyama-discipline.md` §階段 1 量の目安）。もし subagent が量を出せない場合は方向を変えて追加 dispatch する。

## Phase 2: 収斂（KJ 6 階段 + 谷山「なんかいいよね禁止」審査）

`ideation-kj-convergence.md` §6 階段詳細定義 + `ideation-taniyama-discipline.md` §「なんかいいよね禁止」ルール 並行運作。

1. **テーマ設定（階段 1）**：重申本次收斂的焦點問題。例：「〇〇商品の LP headline 優勝を 3-5 本選ぶ」「〇〇キャンペーンのキャッチ候補 3-5 本を選ぶ」等。テーマ が曖昧な場合は planning-team 回到 value-prop 再確認。テーマ の粒度が大きすぎる場合（「全商品ライン向け」等）は収斂が機能しないため、単一商品 / 単一訴求軸に絞る。

2. **ラベル作成（階段 2）**：64 候選 → 64 張卡片。**一卡一概念**。各卡記載：copy 本文 / Mandal-Art 方向 / VS probability。1 卡に複数概念を混ぜると後続のグループ編成で粒度が崩れる（`ideation-kj-convergence.md` §階段 2）。

3. **グループ編成（階段 3）**：embedding-assisted 初期クラスタ 10-15 群 → 人類（或 evaluator agent）checkpoint で「感性親和性」再配置。
   - embedding は「初期クラスタの叩き台」として使い、完全自動クラスタを KJ法 と称しない（`ideation-kj-convergence.md` §Anti-Patterns）。
   - 事前に persona / AIDMA / 4P 等の既存タクソノミー で分類しない（渾沌をして語らしめる）。
   - 人類 checkpoint で「これは近くない」「これは分けるべき」と感じた 3-5 件を再配置する。
   - 小グループ（2-5 枚）→ 中グループ → 大グループへ階層化。

4. **表札づくり（階段 4）**：各大グループに「この copy 群が共通に訴える本質」を一行で命名。
   - カテゴリ名（「数字関連」「価格関連」）は NG。
   - 物語（「合理派を安心させる数字訴求群」「感性派を物語で引き込む群」）が canonical。
   - LLM 候補 3-5 提案 → 人類 / evaluator が最終選択（`ideation-kj-convergence.md` §自動化邊界表）。

5. **図解化（A 型、階段 5）**：大グループを 2 軸（例：合理 ↔ 感性 × 短 ↔ 長、または 行動促進 ↔ 状態提案 × 個人 ↔ 共通体験）に空間配置。
   - この作業は LLM 不可、人類 / evaluator agent が担当（`ideation-kj-convergence.md` §自動化邊界表）。
   - LLM を使う場合はテキスト階層リストに留める（空間配置なし）。
   - 空白帯（どの群も置かれない領域）を可視化することが A 型の価値の 1 つ — 競合と差別化できるホワイトスペースを発見する。

6. **文章化（B 型、階段 6）+ 谷山審査**：
   - 核心洞察 → 主要グループの語り → 次のアクション を A4 1-2 枚で叙述化。
   - 「選ぶ」階段として優勝 3-5 本を切り出す。
   - 各優勝候補に **「なぜ良いか」3 項**（`ideation-taniyama-discipline.md` §「なんかいいよね禁止」ルール）を記載：
     1. 何が読者に何を伝えるか
     2. 既存の類似コピーに対して何が新しいか
     3. ターゲットの生活 / 文脈で何が共鳴するか
   - 3 項を具体化できない候補は優勝から外す（描写型は不採用）。
   - 書き手視点で選んでいないか自問する：「自分の発想ルートを知っているから良く見えるだけではないか」（`ideation-taniyama-discipline.md` §階段 2 tip「自分の最初のお気に入りを疑う」）。
   - 読者視点での再審査を必須とする：初見の読者が何を感じるかで判断し、書き手の思い入れで判断しない。

## Phase 2b: 落選群の整理（optional）

KJ法 B 型で優勝 3-5 本を切り出した後、落選群から**次点候補 3-5 本**を別リストで残す。A/B テスト / 変体提案 / Phase 4 rewrite variants（`copy-audit.md` Phase 4）で再利用可能。

1. 大グループ内で優勝になれなかった「群の 2 番手」を次点として記録。
2. 落選理由を簡記（「描写型で止まった」「書き手寄り」「既視感が強い」等）。
3. この次点リストは handoff 時の appendix として付帯する。

## Phase 3: Handoff

優勝 3-5 角度 + 「なぜ良いか」3 項理由書を後続 protocol に引き渡す。handoff の先は文案類型で分岐：長文案 → `write-long-form-copy.md`、中文案 → `write-mid-form-copy.md`、短文案 → `write-short-form-copy.md`、既存文案改善 → `copy-audit.md`（rewrite variants 生成時の Phase 4 素材）。

| 後続 protocol | 優勝角度の位置づけ |
|---|---|
| `write-long-form-copy.md` | Affinity seed（新 PASONA / PASBECONA の共感起点）+ 必要に応じ Benefit seed |
| `write-mid-form-copy.md` | Benefit seed（BEAF 第 1 段の冒頭文） |
| `write-short-form-copy.md` | headline seed（7-15 字に磨く前の材料）+ 切入點 pre-selection |
| `copy-audit.md` | rewrite variants の種（ユーザー要望時） |

handoff 時には必ず以下を引継ぐ：
- 優勝角度 3-5 本（本文 + Mandal-Art 方向）
- 各角度の「なぜ良いか」3 項
- 収斂 A 型図解（人類が描いた空間配置、テキスト階層リストで可）
- 落選群のうち「次点」候補 3-5 本（A/B 変体用）
- Phase 1 で記録した方向選定根拠（後続 protocol / evaluator が検証用に使う）
- 発散段階の候補総数 / VS 確率分布の偏りサマリ（mode collapse が残存していないかの証拠）

handoff の文書形式は自由だが、最低限 `優勝角度 / 3 項理由 / 次点` の 3 ブロックを分離して記述する。3 項理由を省略した handoff は後続 protocol で描写型コピーを生む原因となる。

## Rules

- main worker は**発散 / 収斂のパイプライン管理と人類 checkpoint 代理**に徹する。発散は subagent、収斂は KJ 手順、人類判断が必要な箇所（グループ編成最終 / 表札 / A 型 / 優勝選定）は明示的に checkpoint を設ける。
- 発散 / 収斂の 2 階段を必ず分離する。同一 subagent で発散と収斂を混ぜない（`ideation-taniyama-discipline.md` §Anti-Patterns「散らかす段階で自己審査する」）。
- 曼陀羅 8 方向を使う場合、「輔助方向庫」は後人衍生（非今泉 1987 原典）である旨を明記し、自由に差替え可能とする（`ideation-mandalart.md` §Critical Attribution Corrections）。
- Verbalized Sampling の probability 欄を省略しない。probability が triggering の core（`verbalized-sampling.md` §Anti-Patterns）。
- KJ法 の グループ編成・表札づくり は人類 / evaluator checkpoint 必須。embedding cosine 類似度だけで完結させない（`ideation-kj-convergence.md` §Anti-Patterns）。
- 優勝選定時に「なんかいいよね」を許さない。3 項理由書が書けない候補は採用しない。
- 64-100 本の候補量を満たさないまま収斂に入らない（`ideation-taniyama-discipline.md` §階段 1 量の目安）。
- 収斂数は **3-5 本**を default とする。2 本以下は選ばれていない疑い、6 本以上は絞り込めていない疑い。
- 長文案向けの Phase 0 では「PASONA 段階 × 各段独立 Mandal-Art」の分層運用を優先する。1 度だけ 3×3 展開して全長文の材料にするのは `ideation-mandalart.md` §Anti-Patterns の典型違反。
- 中文案向け Phase 0 では BEAF の各段（B / E / A / F）ごとに独立展開することを検討する（`ideation-mandalart.md` §適用度：中文案は中適合）。
- 短文案向け Phase 0 では 5 種切入点（`short-form-catchcopy-canon.md` §5 種切入点決策樹）を 8 方向に組み込むか、掛詞 / 余白 / 極端化 の JP 短文案系統を重点的に取る。

## Anti-Patterns

- **main worker が 1 人で 8 方向全部を書く**：並行 subagent 化しないと mode collapse が緩和されない + 人間の思考癖が反映される。各方向は独立 subagent で別文脈から発想させる。
- **1 shot で 5 本出して終わり**：64-100 候補を経ずに直接 5 本を書く。mode collapse と「なんかいいよね」の温床。
- **大谷翔平 OW64 を今泉曼陀羅として扱う**：大谷の事例は原田隆史 Method + 松村寧雄 lineage であり、今泉 マンダラート とは別 lineage（`ideation-mandalart.md` §Critical Attribution Corrections #2）。
- **「What × How 四象限」を谷山メソッドとして実装する**：原書に存在しない（`ideation-taniyama-discipline.md` §Critical Attribution Corrections #1）。三階段 + なんかいいよね禁止 + 31 訓練が canonical。
- **embedding だけで KJ法 を完結させる**：感性親和性の最終判断は人類 / evaluator。embedding は「初期クラスタの叩き台」に留める（`ideation-kj-convergence.md` §Anti-Patterns）。
- **A 型図解を LLM に描かせる**：空間言語は人類認知必須。テキスト階層リストで代替しても空間配置の因果 / 対立 は表現不能。
- **優勝候補に「なぜ良いか」3 項を付けず handoff する**：後続 protocol が描写型コピーを書く危険が増える。3 項理由書を必ず同梱する。
- **長文案の Phase 0 で 1 度だけ曼陀羅を回す**：長文案は「PASONA 段階 × 各段独立 Mandal-Art」の分層運用が推奨（`ideation-mandalart.md` §應用於 copywriting 適用度）。
- **散らかす段階で優勝候補を事前宣言する**：発散の自由度を殺す。優勝は Phase 2 の KJ + 谷山審査後に初めて決まる。
- **落選候補を即削除する**：次点 3-5 本は A/B 変体 / audit rewrite / 後続キャンペーンで再利用可能。削除せず appendix に残す。
- **VS probability 欄を省略して「5 本列挙」で終わる**：論文 §4 Ablation で効果喪失が示されている。probability が triggering の core（`verbalized-sampling.md` §Anti-Patterns）。
- **表札にカテゴリ名を使う**：「品質関連」「価格関連」はグループの物語を言語化していない。「このグループが何を語っているか」の叙述でなければならない。
- **狭義 KJ法（階段 2-3 止まり）で handoff する**：copywriting では通常階段 6（B 型文章化 + 優勝選定）まで必要。階段 2-3 止まりは意思決定材料として不完全。
