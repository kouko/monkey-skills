# ja 翻訳定訳表

> monkey-skills repo の README 翻訳に使用する術語の対応表。
> 調査日：2026-04-28。調査方法：Anthropic 公式 ja ドキュメント + 日本業界慣例（Zenn / Qiita / DevelopersIO / 公式 IT 用語集）。
>
> **凡例**
> - **主訳**：原則として優先採用する訳語
> - **副訳**：文脈上許容される代替表記。並存する場合は使い分けを記述
> - **英語のまま**：日本 IT 業界で英語表記が定着しているもの（製品名・固有名詞・略語など）
> - **要 user review**：業界慣例が確立していない / 文脈依存性が高い

---

## 🔒 グローバルルール（2026-04-28 user override）

**英語原文の技術用語 / 固有名詞 / role 名 / framework 名はすべて英語のまま保持し、カタカナ化・漢字訳しない。**

このルールは下記各カテゴリ表の「主訳」欄を上書きする — カタカナ訳・漢字訳が主訳として記載されているものも、**翻訳実行時はすべて英語原文で記載する**。カタカナ訳・漢字訳は参考として、初出時にカッコで補足できる。

**英語のまま保持する範囲**：
- プラットフォーム / アーキ：agent、skill、plugin、marketplace、slash command、MCP、router、workflow、pipeline、envelope、worker、evaluator、orchestrator、hook、dispatch
- 品質コントロール：quality gate、checkpoint、gate verdict、PASS、NEEDS_REVISION、SELF check、MUST、SHOULD、MAY、protocol、standards、checklist、rubric、bounce-back、retry cap、audit trail、primary-source-grounded、canonical、byte-identical、divergence、precondition
- Skill 開発：domain-team、meta-skill、grounding、citation、attribution、ADR、Conventional Commits、semver、CI/CD、monorepo、SSOT
- Obsidian：vault、daily note、canvas、file intel、dashboard、callout、wikilink、frontmatter、properties、embed、base file
- 投資 / データ：macro regime、nowcast、composite index、proxy、ticker、equity、holdings、portfolio、snapshot、technical indicator、DCF valuation、stock screener、backtest、primary source
- コピーライティング：copywriting、copy、ideation、brief、headline、tagline、voice anchor、voice quadrant、brainstorming、awareness level
- 一般：README、repository、deployment、integration test、regression、refactoring、fixture、dry-run、CLI、API、SDK、commit、PR、branch、merge、log、token、prompt
- 日本語 framework：キャッチコピー（日本語のまま）

**翻訳する部分**：
- 一般的な説明文（接続詞・形容詞・動詞・語尾）
- 章節タイトルの非術語部分（例：「インストール」「ライセンス」「貢献」）
- 表のカラムの非術語部分
- コードブロックのコメント（人間言語部分）

**初出時はカッコで補足可**：例「skill（スキル）」「vault（ボールト）」— ただし初出のみ、以降は英語のまま。

下記表の「主訳」欄は原調査結果。翻訳実行時は**本セクションの override を最優先**とし、副訳欄は初出時の補足参考のみ。

---

## プラットフォーム / アーキテクチャ

| EN term | 主訳 | 副訳 | 決定根拠 / 出典 |
|---|---|---|---|
| agent | エージェント | agent（コード文脈は英語のまま） | Anthropic 公式 ja docs：「汎用エージェントを専門家に変える」「オーケストレーターエージェント」とカタカナ表記。([Anthropic ja docs](https://platform.claude.com/docs/ja/agents-and-tools/agent-skills/overview)) |
| skill | スキル | Skills（製品名として） / `SKILL.md`（コード） | Anthropic 公式 ja は本文では「スキル」「Skills」を併用。製品名・ファイル名は英語保持、説明文ではカタカナ「スキル」が主流。([Zenn skill-creator ガイド](https://zenn.dev/yamato_snow/articles/30e8dcf9490c88), [DevelopersIO Agent Skills](https://dev.classmethod.jp/articles/claude-code-skills-cve-report/)) |
| plugin | プラグイン | — | Anthropic 公式 ja docs「プラグインを作成する」がカタカナ。Obsidian / VS Code / Claude Code 全てカタカナ表記が業界標準。([code.claude.com ja](https://code.claude.com/docs/ja/plugins)) |
| marketplace | マーケットプレイス | — | Claude Code 日本語ドキュメント・Zenn 記事で「マーケットプレイス」がカタカナ表記で定着 |
| slash command | スラッシュコマンド | — | Zenn / Qiita 多数で「スラッシュコマンド」がカタカナ主流。([Zenn Claude Code 攻略ガイド](https://zenn.dev/uguisu_blog/articles/003_claude-code-slash-commands)) |
| MCP | MCP | Model Context Protocol（初出時補足可） | 略語のまま使用が業界標準。日本語記事も MCP のまま。([Zenn MCP 設定](https://zenn.dev/karaage0703/articles/3bd2957807f311)) |
| MCP server | MCP サーバー | MCP server（コード文脈） | 「サーバー」表記が JIS 標準・Microsoft スタイルガイド準拠。([Qiita MCP サーバー設定](https://qiita.com/nak1104/items/392a0f5aa4c78566d99b)) |
| router | ルーター | router（skill 名は英語のまま） | カタカナ表記が IT 業界主流。skill 名（例：`using-copywriting-toolkit`）は英語保持 |
| workflow | ワークフロー | — | IT 業界カタカナ主流。Google Cloud ja docs / IT トレンド用語集で確定。([Google Cloud ja](https://cloud.google.com/blog/ja/products/application-development/orchestrate-data-pipelines-using-workflows?hl=ja)) |
| pipeline | パイプライン | — | IBM ja / Google Cloud ja でカタカナ表記が標準 |
| envelope (envelope contract / handoff envelope) | エンベロープ | エンベロープ契約 / 受け渡しエンベロープ | カタカナ「エンベロープ」が標準。「契約」「受け渡し」は意味訳（要 user review：repo 独自概念のため初出時に英語併記推奨） |
| worker | worker | ワーカー（説明文） | repo 内では agent role の固有名詞として `worker` を英語保持。一般説明では「ワーカー」も可 |
| evaluator | evaluator | エバリュエーター（説明文） | 同上。repo 内 role 名は英語保持。一般説明では「評価者」も使用可（要 user review） |
| orchestrator | オーケストレーター | orchestrator（コード文脈） | Google Cloud ja / VSCode Claude Workflow リポジトリで「オーケストレーター」表記。([VSCode Claude Workflow GitHub](https://github.com/michihiro-316/vscode-claude-workflow)) |
| hook | フック | hook（コード文脈） | Anthropic 公式 ja / Git ja docs で「フック」カタカナ表記が標準 |
| dispatch | ディスパッチ | 呼び出し / 振り分け（文脈による） | カタカナ主訳。文脈次第で意味訳採用 |

## 品質コントロール

| EN term | 主訳 | 副訳 | 決定根拠 / 出典 |
|---|---|---|---|
| quality gate | 品質ゲート | クオリティゲート | JASST 学術論文・テスター10・Musashi AI 用語集で「品質ゲート」漢字訳が定着。([JASST PDF](https://www.jasst.jp/archives/jasst03/pdf/yasuda_doc.pdf), [テスター10](https://minna-systems.co.jp/test/test-automation/quality-gate-implementation/)) |
| checkpoint | チェックポイント | — | カタカナ表記が IT 業界主流 |
| gate verdict | ゲート判定 | gate 判定 / verdict（英語） | 「判定」は QA / テスト業界で標準訳。要 user review（repo 独自用法あり） |
| PASS / NEEDS_REVISION | PASS / NEEDS_REVISION | 合格 / 要修正（説明文） | 列挙値は英語保持。説明文では「合格」「要修正」と併記可 |
| SELF check | SELF チェック | セルフチェック | repo 独自 4-tier の上位概念。SELF は英語保持、check はカタカナ |
| MUST / SHOULD / MAY | MUST / SHOULD / MAY | 必須 / 推奨 / 任意（説明文） | RFC 2119 由来。原語保持が技術文書慣例 |
| protocol | プロトコル | — | IT 業界カタカナ主流 |
| standards | 標準 | スタンダード | 「標準」漢字訳が docs/ja で多数。ファイル名 `standards/` は英語保持 |
| checklist | チェックリスト | — | カタカナ標準 |
| rubric | ルーブリック | 評価基準（教育文脈） | カタカナ「ルーブリック」が教育・QA 業界で定着 |
| bounce-back | バウンスバック | 差し戻し | 一般的には「差し戻し」、repo 独自用法ならカタカナ可（要 user review） |
| retry cap | リトライ上限 | — | 「リトライ」カタカナ + 「上限」漢字のハイブリッドが IT 標準 |
| audit trail | 監査証跡 | 監査ログ | 会計 / セキュリティ業界で「監査証跡」漢字訳が JIS 標準 |
| primary-source-grounded | 一次資料に基づく | 一次ソース準拠 | 「一次資料」が学術・調査業界の定訳 |
| canonical | 正準 | 標準 / 公式 | 「正準形」「正準ソース」など漢字訳が CS 教科書で定着 |
| byte-identical | バイト単位で同一 | バイト一致 | 「バイト」カタカナ + 漢字併記。要 user review |
| divergence | 乖離 | 差分 / ダイバージェンス | 「乖離」漢字訳が金融・データ業界主流 |
| precondition | 事前条件 | プリコンディション | 漢字訳が IT 用語集で標準 |

## Skill 開発

| EN term | 主訳 | 副訳 | 決定根拠 / 出典 |
|---|---|---|---|
| domain-team | ドメインチーム | domain-team（skill 名） | カタカナ「ドメイン」+「チーム」。skill 名は英語保持 |
| meta-skill | メタスキル | meta-skill | 「メタ」カタカナ接頭辞 + 「スキル」 |
| grounding | グラウンディング | 根拠付け / 一次資料への接地 | AI / LLM 文脈で「グラウンディング」カタカナ定着。説明文で意味訳併記 |
| citation | 引用 | サイテーション | 「引用」漢字が学術・出版業界で定訳 |
| attribution | 帰属表示 | アトリビューション（マーケ文脈） | 「帰属表示」がライセンス・著作権文脈で標準 |
| ADR (Architecture Decision Record) | ADR（アーキテクチャ決定記録） | — | 略語のまま使用 + 初出時に日本語併記が業界慣例 |
| Conventional Commits | Conventional Commits | コンベンショナルコミット | 仕様名は英語保持が標準。([conventionalcommits.org](https://www.conventionalcommits.org/en/v1.0.0/)) |
| semver | semver | セマンティックバージョニング（初出時） | 略語英語保持が標準 |
| CI/CD | CI/CD | 継続的インテグレーション/継続的デリバリー（初出時） | 略語英語保持が業界標準 |
| monorepo | モノレポ | monorepo | カタカナ「モノレポ」が Zenn / Qiita で定着 |
| SSOT (single source of truth) | SSOT | 信頼できる唯一の情報源 | Wikipedia ja 項目名「信頼できる唯一の情報源」が定訳。略語 SSOT も併用。([Wikipedia ja](https://ja.wikipedia.org/wiki/%E4%BF%A1%E9%A0%BC%E3%81%A7%E3%81%8D%E3%82%8B%E5%94%AF%E4%B8%80%E3%81%AE%E6%83%85%E5%A0%B1%E6%BA%90), [Zenn SSOT 解説](https://zenn.dev/yurukusa/articles/c082a6aea7155e)) |
| source of truth | 信頼できる情報源 | 真実の源泉 | SSOT 構成要素。漢字訳が標準 |

## Obsidian 領域

| EN term | 主訳 | 副訳 | 決定根拠 / 出典 |
|---|---|---|---|
| vault | Vault | ボールト（説明文） | Obsidian 公式 ja UI で「Vault」英語保持が主流。日本コミュニティ翻訳でも Vault 表記が定着 |
| daily note | デイリーノート | daily note | カタカナ表記が Obsidian 日本コミュニティで標準 |
| canvas | Canvas | キャンバス（説明文） | 機能名 Canvas は英語保持。一般語として「キャンバス」も可 |
| file intel | ファイル解析 | file intel | repo 独自用語。「ファイル解析」意味訳 + 英語併記推奨（要 user review） |
| dashboard | ダッシュボード | — | カタカナ標準 |
| callout | コールアウト | — | Obsidian 日本コミュニティで「コールアウト」カタカナ定着 |
| wikilink | Wikilink | ウィキリンク | 機能名は英語保持。`[[...]]` 構文の総称 |
| frontmatter | フロントマター | YAML フロントマター | カタカナ「フロントマター」が業界主流。Markdown 業界標準 |
| properties | プロパティ | properties | Obsidian の機能名。カタカナ標準 |
| embed | 埋め込み | エンベッド | 「埋め込み」漢字訳が Markdown / HTML 文脈で標準 |
| base file | base ファイル | ベースファイル | Obsidian Bases 機能用語。`.base` 拡張子は英語保持 |

## 投資 / データ領域

| EN term | 主訳 | 副訳 | 決定根拠 / 出典 |
|---|---|---|---|
| macro regime | マクロレジーム | マクロ局面 | 「レジーム」カタカナがヘッジファンド・経済学業界で定着。([SMBC日興 グローバル・マクロ](https://www.smbcnikko.co.jp/terms/japan/ku/J0883.html)) |
| nowcast | ナウキャスト | — | 経済予測業界で「ナウキャスト」カタカナ定着（日銀・内閣府も使用） |
| composite index | 合成指数 | コンポジット指数 | 内閣府・統計業界で「合成指数」漢字訳が標準（景気動向指数等） |
| proxy | プロキシ | 代理変数（経済文脈） | IT 文脈は「プロキシ」、統計・経済文脈は「代理変数」 |
| ticker | ティッカー | 銘柄コード | 「ティッカー」カタカナが米国株文脈で標準。日本株は「銘柄コード」 |
| equity | 株式 | エクイティ | 「株式」漢字訳が JPX 用語集で標準。([JPX 用語集](https://www.jpx.co.jp/glossary/all/index.html)) |
| holdings | 保有銘柄 | ホールディングス | 「保有銘柄」が個人投資家慣例。「ホールディングス」は会社名文脈 |
| portfolio | ポートフォリオ | — | カタカナ表記が金融業界標準 |
| snapshot | スナップショット | — | カタカナ表記が IT / データ業界標準 |
| technical indicator | テクニカル指標 | — | 「テクニカル」カタカナ + 「指標」漢字のハイブリッド標準 |
| DCF valuation | DCF 法 | DCF バリュエーション / 割引キャッシュフロー法 | 野村総研 / 日本取締役協会で「DCF 法」表記が定着。([NRI](https://www.nri.com/jp/knowledge/glossary/npv.html), [日本取締役協会](https://www.jacd.jp/news/column/column-opinion/251210_dcf.html)) |
| stock screener | 株式スクリーナー | 銘柄スクリーニング | 「スクリーナー」「スクリーニング」カタカナが個人投資家慣例 |
| backtest | バックテスト | — | 投資・アルゴリズム業界でカタカナ標準 |
| primary source | 一次資料 | 一次ソース | 学術・調査業界で「一次資料」漢字訳が定訳 |

## コピーライティング領域

| EN term | 主訳 | 副訳 | 決定根拠 / 出典 |
|---|---|---|---|
| copywriting | コピーライティング | — | カタカナ表記が広告業界標準 |
| copy | コピー | 広告コピー | 文脈次第。広告文脈では「コピー」のみで通じる |
| ideation | アイディエーション | アイデア出し / 発想 | 「アイディエーション」カタカナがデザイン思考業界で定着 |
| brief | ブリーフ | 要件書 | 「ブリーフ」カタカナが広告制作業界標準 |
| headline | ヘッドライン | 見出し | 「ヘッドライン」カタカナが LP / 広告文脈標準。新聞文脈は「見出し」 |
| キャッチコピー | キャッチコピー | — | ja 既定訳語（和製英語）。そのまま使用 |
| tagline | タグライン | スローガン / コーポレートメッセージ | カタカナ主訳。文脈で「スローガン」も可 |
| voice anchor | ボイスアンカー | 声の基準 | repo 独自用語。カタカナ + 説明文で意味訳併記推奨（要 user review） |
| voice quadrant | ボイス・クアドラント | 声の象限 | repo 独自用語（4 象限分析）。カタカナ + 漢字併記推奨（要 user review） |
| brainstorming | ブレインストーミング | ブレスト | カタカナ標準。「ブレスト」省略形も日常的 |
| awareness level (Schwartz) | 認知段階 | 顧客認知レベル / Awareness Level | Eugene Schwartz の "Five States of Awareness" 訳語。日本マーケ業界で「認知段階」漢字訳が広告コピー本で定着 |

## 文物脱構築領域

deconstruct-toolkit 専用用語。本 plugin は外部の「精緻な制作物」（コピー / UI / ドキュメントパック / 論証 / 製品 / 組織）を逆向きに分解し、Derrida（哲学）/ Barthes（記号学）/ Toulmin（論証）/ Lakoff（フレーム）/ Goffman（社会フレーム）/ Cialdini（説得）/ Bhatia（ジャンル）/ Nielsen-Norman（UX）の primary source に紐付けて分析する。BCG「バリュー・チェーンの脱構築」(Evans & Wurster) と山口周『武器になる哲学』を実務 anchor として README で参照。

| EN term | 主訳 | 副訳 | 決定根拠 / 出典 |
|---|---|---|---|
| deconstruct (verb) | 脱構築する | 解体する（口語）/ deconstruct（英語保持）| 日本哲学界・思想界・BCG 戦略コンサル業界で一致して「脱構築」。BCG『Blown to Bits』（Evans & Wurster, 2000）の「バリュー・チェーンの脱構築」が日本ビジネス界で定着。山口周『武器になる哲学』(2018) でも採用。「デコンストラクション」（カタカナ）も使われるが冗長。 |
| deconstruction (noun) | 脱構築 | デコンストラクション（タイトル等）| 同上。本文では漢字「脱構築」、タイトルでカタカナ「デコンストラクション」併用可。 |
| artifact | 制作物 | アーティファクト（カタカナ） | 本 plugin は「制作物」を採用（具体性・読みやすさ）。「アーティファクト」は IT エンジニアリング文脈（build artifact）と混同されやすいため副訳。 |
| lens (analytical) | lens（英語保持） | レンズ（不推奨：光学的歧義）| 批評理論コミュニティで `lens` が方法論用語として定着。日本語「レンズ」は光学用語が支配的。本 plugin は body 内全て英語保持。 |
| frame (analytical) | フレーム | 枠組み | Goffman / Lakoff のフレーム分析は日本社会学・認知言語学界で「フレーム」カタカナ標準。「枠組み」も併用可。 |
| reframe | リフレーミング / 再フレーム化 | reframe（英語保持）| 認知科学・NLP（神経言語プログラミング）日本コミュニティで「リフレーミング」が定着。 |
| warrant (Toulmin) | warrant（英語保持） | 論拠 / 根拠 | Toulmin 議論モデルの日本語訳に統一なし（「論拠」「根拠」「保証」三派並立）。本 repo は英語保持路線；補足説明で「論拠」。 |
| claim (Toulmin) | 主張 / クレーム | 論点 | 哲学・論理学界で「主張」、ビジネス文脈で「クレーム」。本 plugin は「主張」（Toulmin 原意に近い）。 |
| grounds (Toulmin) | 根拠 / データ | grounds（英語保持）| Toulmin 日本語訳で「根拠」「データ」並立。 |
| rebuttal (Toulmin) | 反駁 / 反論 | rebuttal（英語保持）| 法律・哲学日本語で「反駁」「反論」併用。本 plugin は「反駁」（Toulmin 原意に近い）。 |
| qualifier (Toulmin) | 限定詞 | qualifier（英語保持）| 論理学日本語標準訳「限定詞」。 |
| dark pattern | ダークパターン | dark pattern（英語保持）/ 欺瞞的パターン | UX 日本コミュニティでカタカナ「ダークパターン」が標準。Brignull 2024 改称 "deceptive pattern" は副訳「欺瞞的パターン」。 |
| binary opposition | 二項対立 | バイナリ・オポジション（カタカナ、稀）| Derrida / 構造主義日本語標準訳「二項対立」。 |
| affordance | アフォーダンス | affordance（英語保持）| Gibson / Norman 「アフォーダンス」カタカナが日本 HCI / UX 業界で完全定着。「行為可能性」訳もあるが業界では使われない。 |
| signifier | シニフィアン / 指示子 | signifier（英語保持）| Saussure 記号学日本語訳「シニフィアン」（カタカナ）；Norman 設計論文脈で「指示子」。 |
| genre move | ジャンル move / move | move（英語保持）| Swales/Bhatia genre analysis の日本語訳語なし；学術ライティング日本指導書で英語保持が一般。 |
| pentad (Burke) | 五要素 / ペンタッド | pentad（英語保持）| Burke 修辞学日本語訳「五要素」（act / scene / agent / agency / purpose）。 |
| dramatism (Burke) | ドラマティズム | 劇的主義（稀） | Burke 修辞学カタカナ訳が学術界で定着。 |
| heuristic (Nielsen) | ヒューリスティック | 経験則 / 発見的手法 | Nielsen 10 heuristics 日本 UX 業界カタカナ「ヒューリスティック」標準。 |
| teardown | teardown（英語保持）| 分解（混同回避のため非推奨）| 業界用語、deconstruct と区別（teardown = 戦略分解；deconstruct = 隠れた構造を露出）。本 plugin は teardown を採用しない。 |
| reverse engineering | リバースエンジニアリング | reverse engineering（英語保持）| ソフトウェア / ハードウェア工学日本業界カタカナ標準。本 plugin はこの意味では使わない（§2.2 fence 除外）。 |
| primary source | primary source（英語保持） | 一次資料 / 原典 | 学術日本語「一次資料」「原典」併用。本 repo は英語保持路線。 |
| symptomatic reading | 症候的読解 / シンプトマティック・リーディング | symptomatic reading（英語保持）| Althusser 訳介日本文献で「症候的読解」（不在を読む）。 |
| バリュー・チェーンの脱構築 | バリュー・チェーンの脱構築（保持） | value chain deconstruction | BCG『Blown to Bits』(Evans & Wurster, 2000) の日本語定着訳。本 plugin の JP README で実務 anchor として参照。 |

## 一般

| EN term | 主訳 | 副訳 | 決定根拠 / 出典 |
|---|---|---|---|
| README | README | — | ファイル名のため英語保持が絶対 |
| repository | リポジトリ | repo（略称） | カタカナ「リポジトリ」が GitHub ja docs で標準 |
| deployment | デプロイ | デプロイメント | 「デプロイ」カタカナが Zenn / Qiita で主流。「デプロイメント」も可 |
| integration test | 結合テスト | インテグレーションテスト | JIS X 0129 / IPA で「結合テスト」漢字訳が定訳 |
| regression | リグレッション | 回帰 / 後退（文脈による） | テスト文脈は「リグレッションテスト」カタカナ、統計文脈は「回帰」 |
| refactoring | リファクタリング | — | カタカナ表記が業界標準（書籍『リファクタリング』邦訳） |
| fixture | フィクスチャ | テスト用データ | カタカナ「フィクスチャ」がテスト業界主流。説明文で意味訳併記可 |
| dry-run | ドライラン | 試運転 | カタカナ「ドライラン」が CI/CD・コマンドライン業界標準 |

---

## 翻訳の一般ルール

1. **コードブロック内の英語は訳さない**（command、ファイル名、URL、変数名）
2. **コメントは人間言語なら訳す**、プログラム文法部分はそのまま
3. **初出の術語はカッコで原語を併記**してよい：「プラグイン（plugin）」「一次資料（primary source）」
4. **見出しレベル（# / ## / ###）は原文と同じに保つ**
5. **Markdown 表のカラム数を維持**
6. **リンク `[text](url)` の text を訳す、url は不変**
7. **カタカナとひらがな・漢字のバランス**：技術用語はカタカナ主流、それ以外は自然な日本語
8. **製品名・ファイル名・skill 名・YAML キーは英語保持**：`SKILL.md`、`PRODUCT-SPEC.md`、`investing-toolkit`、`name:`、`description:`
9. **略語は原則そのまま**：API、SDK、CLI、CI/CD、MCP、ADR、SSOT、DCF、JSON、YAML
10. **重複翻訳を避ける**：「PR レビュー」と「プルリクエストレビュー」を同一文書内で混在させない（用語選択は文書冒頭で固定）
11. **要 user review マークは初版翻訳時に必ず確認**：repo 独自用語（envelope, voice anchor, voice quadrant, file intel, gate verdict, byte-identical, bounce-back）は翻訳前に kouko に確認

---

## 主要出典

- [Anthropic Agent Skills 公式 ja docs](https://platform.claude.com/docs/ja/agents-and-tools/agent-skills/overview)
- [Claude Code Plugins 公式 ja docs](https://code.claude.com/docs/ja/plugins)
- [Wikipedia ja: 信頼できる唯一の情報源](https://ja.wikipedia.org/wiki/%E4%BF%A1%E9%A0%BC%E3%81%A7%E3%81%8D%E3%82%8B%E5%94%AF%E4%B8%80%E3%81%AE%E6%83%85%E5%A0%B1%E6%BA%90)
- [JPX 日本取引所グループ用語集](https://www.jpx.co.jp/glossary/all/index.html)
- [野村総研 NPV/IRR/DCF 用語解説](https://www.nri.com/jp/knowledge/glossary/npv.html)
- [SMBC日興 グローバル・マクロ戦略用語](https://www.smbcnikko.co.jp/terms/japan/ku/J0883.html)
- [JASST 品質ゲート学術論文](https://www.jasst.jp/archives/jasst03/pdf/yasuda_doc.pdf)
- [Conventional Commits 公式仕様](https://www.conventionalcommits.org/en/v1.0.0/)
- Zenn / Qiita / DevelopersIO 各記事（個別エントリで引用）
