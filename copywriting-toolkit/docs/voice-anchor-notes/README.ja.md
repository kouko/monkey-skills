# Voice Anchor Deep Dives

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

**目的**：`docs/anchor-schema-v2.md` に基づく Layer 2/3 research artifact。Pass 3 はこれらをロードしない；audit / provenance / 将来の deep-dive research 拡張のために存在する。

## Layer 分離（`anchor-schema-v2.md` 準拠）

| Layer | 位置 | 消費者 | 内容 |
|---|---|---|---|
| **Layer 1**（voice body）| `skills/copywriting-voice-tone-stage/standards/anchor-{slug}.md` | Pass 3（hot path）| Voice direction / Native critical read / Prose mechanics / Examples / Don't / Metadata — Pass 3 が draft をその voice で書き直すために必要なフィールド |
| **Layer 2/3**（research）| `docs/voice-anchor-notes/{slug}.md`（本フォルダ）| Audit / evaluator rationale（任意）/ 将来の研究者 | 完全な research notes / 一次資料 URL & ISBN / 伝記と時代背景 / 受賞歴タイムライン / 批評史 / ドキュメント化された lineage 影響 + 落選候補の研究トレイル（v1.13.1 で旧 voice-anchor-deep-dives + voice-anchor-research-notes から統合）|

## 現状（v1.6.1）

本フォルダ内の 64 ファイルすべては、v1.6.0 移行時点の Layer 1 v2 エントリの**凍結スナップショット**（commit `b9b1c39`、scaffolding-cleanup 後）。内容は `standards/` の対応する `anchor-{slug}.md` と一致するが、Layer 2/3 research が各エントリを拡張するにつれ、**時間とともに発散することが許容される**：

- 伝記タイムライン
- 時代背景（周辺の文化 / 政治 / 市場条件）
- `Native critical read` の批評引用以外の完全な一次資料 bibliography
- 受賞 / 認知歴
- ドキュメント化された lineage（誰が誰に影響したか、具体的な interview / 書簡 / 学術 citation 付き）
- 批評史の議論（その register の境界に関する学術的論争）

## ファイル名 convention

現行（v1.6.1）：`pilot-layer1-v2-{creator-slug}.md`（歴史的命名、v1.4-v1.5 pilot 期から保持）。

将来（v1.7.0+）：deep-dive research が各エントリを拡張するにつれ `{trigger-slug}.md`（Layer 1 anchor slug と一致）にリネーム — その時点でファイル名アラインメントは audit ツーリングをシンプルにする。

## 本フォルダの使い方

- **Pass 3**：MUST NOT load。`standards/anchor-{slug}.md` の Layer 1 が Pass 3 の唯一のソース。
- **Dimension 6 evaluator**（voice-consistency-gate）：over-mimic 判断に Layer 1 が持たない伝記 / 時代 / lineage コンテキストが必要な場合、rationale で deep-dive エントリを任意に引用 MAY。
- **人間の研究者**：research の進展に応じて、新しい伝記 / 時代 / lineage 発見で任意のエントリを拡張する。Layer 1 slug が変わってもファイル名は安定に保つ（または同期 — どちらかの規律を選ぶ）。
- **Commit 規律**：Layer 1 anchor 更新と Layer 2/3 deep-dive 更新は**独立した commit** — 混同しない。Layer 1 変更は production-facing（Pass 3 挙動）、Layer 2/3 変更は audit-facing。

## 誤削除の経緯（v1.6.0 → v1.6.1）

v1.6.0 移行時、pilot ファイルを `standards/` に `git mv` した際、本フォルダ（と 64 ファイル）が誤って削除された。意図は Layer 1 body を pilot 位置から移すことだったが、Layer 2/3 の **seed material** とフォルダ自体は残すはずだった。v1.6.1 は commit `b9b1c39`（削除前スナップショット）から 64 ファイルすべてを逐字復元した。

これらのファイルは現在、将来の Layer 2/3 research の **seed material**。deep-dive research はまだ行われていない — 各ファイルは現状 Layer 1 schema のみを保持。これがスタート地点であって、終点ではない。
