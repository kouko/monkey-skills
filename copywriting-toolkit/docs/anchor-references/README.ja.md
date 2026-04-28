# Anchor References

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

**目的**：v2 inclusion criterion（個別の creator + 識別可能な sentence-level register）に該当**しない**ため Layer 1 voice anchor として認められない register / format / movement 記述を保持する。これらは引き続き有用 — Pass 3 over-mimic registry はそのうちのいくつかを mitigation-only で引用し、Phase 8 form-check は format convention として参照することがある — が、voice anchor としてはロードしない。

**v1.13.1 で統合**：旧 `docs/format-templates/` + `docs/register-references/` を統合した。両フォルダとも非 Layer 1 reference を保持し目的が重なっていたため、ナビゲーションのオーバーヘッドを減らすべく単一フォルダ化。

## 2 種類のエントリ

### Format templates（`jp-*`、`en-*`、`zh-tw-*-platforms-*`、`zh-tw-*-institutional-*`）

機関 / プラットフォーム / IP エンティティで、再利用可能な構造的 format を生み出すもの。例：
- **雑誌 / 新聞 / 通信社** — 著者がローテーション（天声人語 / 東洋経済 / Reuters JP / 日経社説）
- **機関プラットフォーム / SNS / IP マスコット**（研之有物 / 故宮粉絲團 / 全聯 SNS / クックパッド つくれぽ / ワークマン SNS）
- **EC プラットフォーム** — 著者が分散（Shopee 雙11 / PChome / MOMO / Pinkoi）
- **ブランドの機関的 voice** — register-defining の瞬間に単一の named author が居ない（Amazon product copy / REI expert-advice / IKEA assembly voice）

voice は、1 つの手によって繰り返し行使される sentence-level の一貫した sensibility から立ち上がる。これらのエントリが生むのは **FORMAT、PROTOCOL、または TEMPLATE** — ローテーションする著者は house-style ルールに収束し、単一作者の voice を表現するわけではない。

### Register references（movement レベル / campaign レベル / 出版時代）

ドキュメント化された運動 / 有名 campaign / 編集部 voice — 影響力が強く、draft に anti-pattern として漏れ出すが、ロード可能な単一著者 voice が存在しないもの。例：
- **ドキュメント化された運動**、civic-declarative または manifesto register を持つもの（XR Declaration / Occupy declarations）
- **出版社の機関 voice**、編集者がローテーションしても house style が mitigation reference として機能するもの（Economist brand voice / 天下雜誌 / 商業周刊 / 報導者）
- **campaign レベル**、register がチーム合意から立ち上がったもの（一部の Nike 「Dream Crazy」 — ローテーションする CW で実行）

format-template と register-reference の境界は soft — どちらも非 Layer 1 で、Pass 3 voice 選択ではなく下流 gate に資する。エントリは主要な lens（構造的 format vs ドキュメント化された運動）でファイリングするが、フォルダ全体としては単一の「non-anchor references」バケツ。

## Pass 3 と gate がこのフォルダをどう使うか

- **Pass 3 はこれらを voice anchor としてロードしない。** `voice-consistency-gate.md` の Voice Consistency（Dimension 6）と Thesis Alignment（Dimension 7）は `standards/anchor-*.md` の Layer 1 エントリのみで動作する。
- **`voice-anchor-meta.md §Over-mimic mitigation fallback registry` の over-mimic registry** は、ここのいくつかのエントリを mitigation 源として引用する — 例：「XR Declaration civic-declarative register ONLY; NOT for commercial product copy」。
- **Phase 8 form-check（8a）** は、プラットフォーム固有 convention のため format templates を参照することがある（EC product copy のビート / 通信社 headline 長 / SNS IP マスコット register）。
- **audit / evaluator** は、「draft はプラットフォーム format template や civic-movement のリズムを模倣している、voice register ではない — 再 anchor または再 direction」といった rationale でこれらを引用することがある。

## 他の skill layer との関係

- **正規 voice library**（`standards/anchor-*.md`）— Layer 1 の個別 creator voice anchor（80+ エントリ）。Pass 3 はここからロードする。
- **Anchor references**（本フォルダ）— 非 Layer 1：format templates + register references。mitigation-only / form-convention-only。
- **Voice anchor notes**（`../voice-anchor-notes/`）— Layer 1 エントリに対する Layer 2/3 research artifact + 落選候補の研究トレイル。

## 重要：voice register source ではない

brief がこのフォルダの領域に着地した場合、skill は以下に route する：
1. **Form appropriateness**（Phase 8 8a）— format-template なら、その template の構造 convention
2. **Over-mimic mitigation**（Dimension 6）— register-reference なら、anti-pattern として引用
3. **Tone** — ブランドの brief から、または Layer 1 から別途選ばれた named-individual voice anchor から派生

絶対に「Amazon product copy を voice register として適用」してはいけない — Amazon の register **は** product copy template そのもの。template は構造に使い、voice anchor は Layer 1 から別途選ぶ。「XR Declaration を voice として適用」も同様 — それは mitigation warning であって source ではない。

## 移行ステータス

Phase C（v1.5.0）はもともと `docs/format-templates/` + `docs/register-references/` を独立フォルダとして作成した。v1.13.1 で両者を `docs/anchor-references/` に統合 — 内容は同じ、ナビゲーション先を一本化。

**v1 `standards/*-anchors.md` から本フォルダへのエントリ別移行**：`docs/voice-library-recast-audit.md` に従って漸進的に。format-template（ローテーション著者が house style を生む）または register-reference（運動または出版時代）に明確にマップされるエントリはここに着地し、個別 creator の sentence-level register を表すエントリは Layer 1 として `standards/anchor-{slug}.md` に行く。
