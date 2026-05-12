# translation-novel

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> 小説の章 / long-form fiction を翻訳する。
> Scene-aware chunking + scene-window prompt（whole-doc windowing 比 ~17× cost 削減）。
> v0.3.0 で whole-book pre-pass、5D literary critic、M3 deterministic linter を追加。

[translation-toolkit](../..) plugin の一部。Claude が読み込む operational
spec は [`SKILL.md`](SKILL.md)。本 README は人間向け。

## v0.3.0 で追加されたもの

v0.2.0 の scene-window 基盤の上に、Tier 2 の 4 機能が積まれる：

- **Whole-book pre-pass** — chapter ごとの翻訳に入る前に、skill が全章を
  一度だけ歩いて 2 つの extractor を走らせる：
  - `character_extractor` — 全 named character + paired-structure aliases
    + voice notes + first/last chapter index を `characters.json` に出力。
  - `world_glossary_extractor` — places / organizations / world terms /
    cultural references を `world-glossary.json` に出力。cultural reference
    は closed-enum の `category`（literary_quotation / idiom / religious /
    food / place_culture / historical / other）と `handling_hint`
    （borrow / explain / approximate）を持つ。
  両 artifact は per-scene glossary lookup の **L1.5** tier として feed
  される（project glossary L1 と bundled glossary L2 の間）— 全章を
  跨いだキャラクター呼称 + world term の anchoring を、whole-novel
  context を膨らませずに得られる。
- **5D literary critic** — per-scene REFLECT step（novel mode の
  デフォルト）が、v0.2.0 の 4D（Accuracy / Fluency / Style / Terminology）に
  Literariness 軸を追加する。Sub-concerns：rhythm（文の cadence）、
  euphony（sound pattern）、archaism（period vocabulary / honorific）、
  register-shift fidelity（narrator vs dialogue、同一キャラクター内の
  formal vs casual）。`translation-creative` の 5D（5 番目の軸が
  Effectiveness）とは別物。
- **M3 deterministic linter** — S1 back-translation の *前に* 走る
  no-LLM な構造健全性チェック：M3a（residual source-script chars、
  HARD）、M3b（length-ratio band、SHOULD）、M3c（CJK fullwidth
  punctuation、SHOULD）。v0.3.0 で `translation-doc` も同時採用
  （Decision H — novel + doc の両方が Layer 4 audit-trail で M3 を surface）。
- **Cheap-model split** — intake-spec の `model` フィールドが dict 形式
  `{default: ..., extractor: ..., back_translator: ...}` を受ける。
  whole-book pre-pass は `extractor` model に route されるので、
  pre-pass の固定コストが per-scene translation コストに amortize される。
  推奨設定は下の「book を翻訳に向けて準備する」を参照。

## book を翻訳に向けて準備する

複数 chapter book を翻訳するときの推奨ワークフロー：

1. **章を Markdown に展開する。**
   [`tsundoku:book-extract`](../../../tsundoku/skills/book-extract) で
   EPUB を chapter-split `.md` ファイルに変換し、`book-ja/` ディレクトリに
   置く。ファイル名は読書順で lexicographic に sort される名前にする
   （`chapter-01.md`、`chapter-02.md`、…）。
2. **whole-book pre-pass を一度走らせる。** いずれの章を翻訳する前にも
   skill を `book-ja/` に向けて、`characters.json` と
   `world-glossary.json` を生成する。pre-pass は各章を full で読む唯一の
   段階 — その後の翻訳は per-scene で動く。
3. **章ごとに翻訳する。** 各章 run は 2 つの pre-pass artifact を load し、
   glossary lookup chain で L1.5 として参照する（L2 / L3 / L4 にフォール
   バックする前）。Cross-scene voice continuity は依然 `prev_scene_v2` に
   anchor され、pre-pass は *cross-chapter* な canonical-rendering anchoring
   を加える。
4. **book に変更があれば pre-pass を再実行する。** 各 artifact は
   filenames + per-file SHA-256 を覆う `book_manifest_hash` で stamp
   される。manifest hash が drift したら（章の追加 / 編集 / 並べ替え）、
   次の pre-pass run は `UserWarning` を発し artifact を上書きする。
   skill は stale な artifact を黙って使わない。

### コストノート

`model: dict` 形式が指定された時点で、pre-pass はデフォルトで cheap な
**extractor** model を使う — pre-pass 総コストは per-scene prompt
overhead ではなく raw chapter text にだけスケールし、book 全体に
amortize される（一度払えば、全章が恩恵を受ける）。典型的な 20-30 章
小説では pre-pass コストは 1 章分の翻訳コストの 10% 以下に収まる；
非常に小さな book（≤2 章）では比率が高くなり、cheap-model split が
load-bearing な設計選択になる。smoke fixture
（`scripts/tests/fixtures/sample-book-ja/`）は 2-章ケースを ship して
CI で cost ceiling を行使できるようにしている；calibrated な worst-case
bound は `scripts/tests/test_e2e_v030_tier2_smoke.py` の
`test_prepass_cost_ceiling_assertion` を参照。

dict 形式の `model` フィールド例（intake spec）：

```yaml
model:
  default: claude-opus-4-7
  extractor: claude-haiku-4-5         # whole-book pre-pass
  back_translator: claude-haiku-4-5   # S1 round-trip
```

## なぜ専用の novel skill か

小説は prose 主体。`translation-doc` が行う markdown AST 処理（code block、
math、mermaid、frontmatter）は適用されず、依拠する whole-doc
`<TRANSLATE_THIS>` windowing は chunk 数に対して O(N²) のコストになる。
30-scene の章を whole-doc windowing で回すと共有 context が 900× 再送される —
5-10 chunk の technical doc では許容範囲だが、fiction の batch では破滅的。

novel-mode はさらに **cross-scene voice continuity** を必要とする — doc-mode
では暗黙に保たれていたもの：同じキャラクターの呼称、同じ speech-tier、
scene 間で一貫した register。doc-mode は whole-doc context のおかげで偶然
保てているが、コスト都合で scene window に落とした瞬間、voice continuity を
明示的に運ばなければならなくなる。

`translation-novel` はこれを一度に解く：heading / explicit-marker / blank-gap /
token-fill 境界による scene-aware chunking、そして直前 scene の **target 言語**
翻訳（`prev_scene_v2`）と次 scene の source 冒頭（`next_scene_source`）を
運ぶ scene-window prompt。コストは O(N) に縮退し、voice は target 側の
履歴に anchor される。

（v0.2.0 plan の Decision 1：これは `translation-doc` の flag ではなく
新しい skill — chunking、prompt、gate weight が分離に値するほど分岐する。）

## Pipeline

```
intake-spec（translation-intake から）
        │
Layer 2 — Preparation
        ├── 章を plain prose としてパース（markdown AST 処理なし）
        ├── 任意の protect-pass（デフォルト OFF — fiction には code / math /
        │   diagram がない；M1 は ON のときのみ強制）
        ├── scene chunk: heading > explicit_marker > blank_gap >
        │   fallback_token_fill、max_scene_tokens=2000
        └── per-scene glossary resolve（4-tier: L1 project → L2 bundled
            → L3 web → L4 LLM）；scope = current + prev_source + next_source
        │
Layer 3 — Per-scene core loop（DRAFT → REFLECT 4D → IMPROVE）
        │   └── scene-window prompt（Decision 4）：
        │       params → glossary → prev_scene_v2（~500 tok）→
        │       <TRANSLATE_THIS>current</TRANSLATE_THIS> →
        │       next_scene_source（~200 tok）→ output requirements
        │
Layer 4 — Verification（M1 + M2 HARD; S1 + S2 SHOULD; I1 INFO）
        │
Layer 5 — Output
        ├── ⟦P:NN⟧ → 元の span に restore（protect-pass 実行時のみ）
        ├── 元の index 順で scene v2 を連結、消費した境界 string
        │   （explicit-marker / blank-gap）を再発行
        ├── roundtrip check（scene 順序、heading、scene 内の段落区切り、
        │   章レベル glossary、truncation-window のリーク無し）
        └── audit-trail.json を発行
```

## Scene-window vs whole-doc — コストの話

`translation-doc` は **whole-doc `<TRANSLATE_THIS>` windowing** を使う：
chunk ごとの prompt が文書全体を再発行し、active chunk のみラップする。
コストは chunk 数に対して **O(N²)**。

`translation-novel` は **scene-window prompt** を使う：`prev_scene_v2`
（直近 ~500 token）+ 現 scene + `next_scene_source`（先頭 ~200 token）
のみが現れる。1 scene あたりのコストは **O(N)** — 30-scene の章では
whole-doc windowing よりおよそ **17× 小さい**。

Voice continuity は `prev_scene_v2`（直前 scene の **target 側** 翻訳、
Decision 5）から来る — prompt のたびに source を再翻訳するわけではない。
WRITER は前回の翻訳が再登場キャラクターの voice をどう処理したかを
直接見るので、その判断を scene ごとに再発見するコストを払わない。
glossary term の章レベル一貫性は M2（HARD）で保ち、checklist 項目 5 で
ダブルチェックする。

2000-token chunk threshold 未満では、章は単一 scene となり windowing は
prev / next が空の通常 prompt に縮退する。

## Verification gate matrix

scene 長 prose（典型 500-2000 token）向けに調整：

| Gate | Tier | チェック内容 |
|---|---|---|
| **M1** | HARD | Placeholder integrity — `⟦P:NN⟧` count + ID set parity。protect-pass OFF（prose-only novel のデフォルト）では no-op。 |
| **M2** | HARD | Project glossary 準拠 — L1-mandated 全 source term が mapped target form として現れる。**novel-mode で critical** — キャラクター名・地名は scene を跨いで再出現し、per-scene M2 PASS は章レベルの一貫性を保証しない（checklist 項目 5 がそれを catch）。v0.3.0+ は pre-pass の `characters.json` / `world-glossary.json` に対し **L1.5** で先に解決し、その後 project glossary L1 と bundled glossary L2 にフォールバックする。 |
| **M3** | HARD（m3a）/ SHOULD（m3b、m3c） | Deterministic post-translation linter — 3 つの subrule：m3a residual source-script chars（HARD；例えば JP→EN target は hiragana / katakana / CJK ideograph を locale-pair の 1% threshold 以上含むべきでない）、m3b length-ratio band（target/source token 比が locale-pair に応じた band 内）、m3c CJK fullwidth punctuation（JLReq / CLReq 準拠）。S1 の *前に* 走り、target が構造的に壊れているとき S1 を short-circuit する — 意味のない back-translation のコストを払わない。v0.3.0+；同 release で `translation-doc` も採用。 |
| **S1** | SHOULD（faithful）/ MUST（transcreation） | Back-translation — BACK-TRANSLATOR が scene ごとに blind に v2 → source を retranslation；source に対する embedding-cosine 類似度。scene 長 prose で reliable。runtime が isolation を提供しない場合は audit-trail フラグ付きでスキップ。 |
| **S2** | SHOULD | Register preservation — JUDGE が source vs target を discourse / formality 軸で分類。fiction register は scene 長で high-signal。 |
| **I1** | INFO | Untranslatability flagging — 文化参照、wordplay、慣用句、訳出不可能な敬称。borrow / explain / approximate の判断を記録するのみ；block せず、user に問わず。 |

S1 / S2 は SHOULD で HARD ではない：明確な原因のある single-scene failure
（例：JUDGE が誤分類した方言 register）は audit-trail に記録され caller に
surface するが、emit を block しない。M1 / M2 は依然 failure で HARD-block。

## Roundtrip checklist

emit 前に [`checklists/novel-quality-checklist.md`](checklists/novel-quality-checklist.md)
が以下を verify：

1. Scene 順序が保持されている
2. Scene 境界 text が正しく消費されている（explicit-marker + blank-gap が再発行されている）
3. Heading level が一致
4. Scene 内の段落区切りが保持されている
5. 章レベルの M2 cross-scene glossary 一貫性
6. truncation-window のリーク無し（prev / next の切片が v2 に漏れていない）

いずれかの項目で failure があれば emit を halt し caller に surface。

## Web search ポリシー

デフォルト ON。novel batch（例：30-scene の章を一括翻訳）では OFF に
上書きする：

```
--web-search=off
```

OFF のとき、glossary resolution は L2（bundled）で停止 — L3（web）は
スキップ、L4（LLM-fallback）は依然走る。再出現する架空 term（造語の
地名、魔法体系の語彙）はそもそも web hit がないことが多いため、
fiction では OFF が概ね正しいデフォルト。

## この skill が **行わないこと**

- **intake を走らせない。** [`translation-intake`](../translation-intake)
  に hand off する（または `--intake` を使う）
- **markdown AST を parse しない。** novel の章は prose text として扱う；
  protect-pass はデフォルト OFF。source に code / math / diagram が
  埋め込まれていれば代わりに [`translation-doc`](../translation-doc) に route。
- **章構造を書き換えない。** scene 順序は保持される；chunker の round-trip
  契約は spec であって示唆ではない。
- **transcreation variant を生成しない。** [`translation-creative`](../translation-creative)
  に `--variants=N` で route。novel-mode は scene ごとに単一 faithful 翻訳を走らせる。
- **既存翻訳ペアを audit しない。** [`translation-audit`](../translation-audit) に route。
- **M1 / M2 を bypass しない。** `--bypass-gates` フラグなし（spec
  Decision #15 によりアンチパターン）。
- **小説全体の context 構築を行わない。** voice continuity は scene-window
  範囲のみ；小説全体を跨ぐキャラクター arc 認識翻訳は Tier 2（character
  pre-pass）として deferred。
- **I1 中に user に質問しない。** untranslatability の判断は記録するだけで
  問わない。

## See also

- [`SKILL.md`](SKILL.md) — operational spec
- [`protocols/scene-chunking.md`](protocols/scene-chunking.md) ·
  [`protocols/scene-window-context.md`](protocols/scene-window-context.md)
- [`checklists/novel-quality-checklist.md`](checklists/novel-quality-checklist.md)
- [`references/verification-gates.md`](references/verification-gates.md) ·
  [`references/core-loop.md`](references/core-loop.md)（DRAFT / REFLECT / IMPROVE のロール契約）
- [`references/4d-reflection.md`](references/4d-reflection.md)（Accuracy / Fluency / Style / Terminology）·
  [`references/prompt-reflect-5d-literary.md`](references/prompt-reflect-5d-literary.md)（5D literary critic — v0.3.0 デフォルト）
- [`references/prompt-extract-characters.md`](references/prompt-extract-characters.md) ·
  [`references/prompt-extract-world-glossary.md`](references/prompt-extract-world-glossary.md)（whole-book pre-pass extractor — v0.3.0）
- Typography: [`typography/jlreq-summary.md`](typography/jlreq-summary.md)（ja-JP）·
  [`typography/clreq-summary.md`](typography/clreq-summary.md)（zh-CN / zh-TW）
- Plugin: [`../../README.md`](../../README.md) ·
  Router: [`../using-translation-toolkit`](../using-translation-toolkit) ·
  Layer 1: [`../translation-intake`](../translation-intake) ·
  Sibling: [`../translation-doc`](../translation-doc)
