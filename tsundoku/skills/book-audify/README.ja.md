# book-audify

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> 所有する電子書籍をパーソナルオーディオブックに——チャプター付き `.m4b`
> を無料の Microsoft ニューラル音声(edge-tts)で合成。

`book-extract` の章別 Markdown を受け取り、
クリーニング → **検証ハードゲート** → 章別 TTS → ffmpeg で m4b 結合。

- クリーニングは TTS が誤読するもの(マークアップ、脚注アンカー、訳注、
  装飾的な章題)をすべて除去し、献辞/謝辞/奥付をスキップ。
  `validate_tts.py` を通らないフォルダは合成を拒否します。
- 音声と話速はユーザーの選択——同じ抜粋で A/B サンプルを作って耳で決める。
  1.5 倍速で聴く人にはベース話速を遅くして抑揚を保ちます。
- 外国語の書籍:章ごとの全文「聴くための翻訳」(書籍ごとの用語集付き)。
  まず 1 章だけ翻訳して試聴 OK が出てから全体を翻訳します。

依存関係は `scripts/install_deps.sh` が導入します:`edge-tts` は隔離された
CLI ツールとして(`uv tool install edge-tts` / `pipx install edge-tts`、
素の `pip` は不使用)、`ffmpeg`/`ffprobe` は brew または SHA256 検証付き
static build。

データフローに関する注意:edge-tts は Microsoft のオンライン読み上げ
サービスのクライアントであり、合成時に書籍の全文が章ごとに Microsoft へ
送信されます。所有する書籍の個人利用に限る。音声ファイルの配布は不可。
