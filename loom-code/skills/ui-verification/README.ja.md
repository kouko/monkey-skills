# ui-verification

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> **ブランチを閉じる前に、`ui-flows.md` が列挙する全ての状態を、実際にレンダリングされたアプリで走らせて確認する。** 出自は 2026-07-03 のパイプライン dogfood：テストスイートは 28/28 グリーンなのに、レンダリング側は **行動検証ゼロ** のまま GUI 製品が出荷された（コードステーション自身の台帳いわく "no live browser was used"）。パッケージテストが検証するのはロジックであり、empty state が描画されるか、error toast に到達できるかは検証できない。

[loom-code](../..) プラグインの一部。エージェントが読み込むのは [`SKILL.md`](SKILL.md)、本 README は人間向け。

## このスキルがすること

UI 変更のうちテストスイートには見えない半分のためのランタイムゲート：ホストの自動化ツール（`chrome-devtools` MCP、Playwright 系、`agent-device` MCP）で実アプリ（ブラウザ / シミュレータ）を開き、`ui-flows.md` が列挙する §1 インベントリ行・render-variant フラグ（empty / loading / error / success / …）・フロー・entry/exit point を全て歩き、状態ごとに観察を 1 件記録する。`critic-found` 行は一級のチェックリスト項目 — writer が見落としたからこそ design-critic が追加したもの。各状態は `verified` / `mismatch` / `unreachable` / `untestable` に分類。ドライブ不能な状態を弱い静的チェックで代用した場合は **half-measure** とラベルし、決して `verified` に昇格させない。

## 使う場面

このゲートは **CONDITIONAL** — 最初に両条件を確認する：

1. この変更に対する `ui-flows.md` が存在する（正規の位置は `docs/loom/<change-id>/ui-flows.md`）。それがチェックリスト。列挙の所有者はデザインステーションで、このスキルが持つのはランタイムチェックだけ。
2. ブランチが UI サーフェスに触れた — HTML / JSX / テンプレート / スタイル / DOM 配線。

どちらかが偽なら **`ui-verification: N/A`** を理由付きで出す。N/A は一級の正直な結果であり、黙ってスキップすることは決してない。ホストにブラウザ / デバイス自動化がない場合も同じ：N/A と理由を言う — ソースの読み直しでウォークスルーを偽装しない。

`finishing-a-development-branch` が `verification-before-completion` と並べて呼び出す（検証の二つの半分：スイート + UI）。UI に触れる最後の SDD タスクが着地した直後のオンデマンド実行も可能 — 早い側の実行なら、whole-branch reviewer に再導出の UI 主張ではなく観察エビデンスを渡せる。

## 使わない場面

- 純ロジックのブランチ — UI を持つリポジトリでも条件 2 が偽、N/A。
- この変更の `ui-flows.md` がない — 条件 1 が偽、N/A（このスキルは列挙を再導出しない）。
- TUI / CLI — v1 のスコープ外（デザインステーションの phase-2 姿勢に合わせる）。その旨を記して停止。

## Verdict — 二値、bare PASS なし

- **`NEEDS_REVISION`** — `mismatch` が 1 件でもある、または `ui-flows.md` で future / deferred と印されていない `unreachable` 状態がある。解決先は implementer、列挙そのものが誤っているならデザインステーション — どちらかを明示する。
- **`PASS_WITH_NOTES`** — ドライブ可能な列挙済み状態が全て `verified`；`untestable` 項目は条件付きでリスト化（このスキルの blind-spots セクションであり、空でなくてよい）。

bare `PASS` は意図的に存在しない：カバレッジは `ui-flows.md` の列挙に対する相対値で、その列挙自体に盲点がある。カバレッジは「列挙 M 状態中 N 状態を verified」と述べる —「UI は検証済み」とは決して言わない。

## このスキルがしないこと

- **パッケージテストのゲートではない** — `verification-before-completion` を補完するのであって、代替しない。
- **DESIGN.md トークン準拠チェックではない** — 色 / 余白 / タイポグラフィの照合は明示的に保留中（loom-interface-design README §Scope、PR #473）。このスキルが検証するのは挙動としての状態であり、視覚トークン値ではない。
- **design critic ではない** — `ui-flows.md` に状態を追加せず、列挙の良し悪しも判定しない。見落とし狩りは上流の `loom-interface-design:design-critic` の仕事。
- **コードエディタではない** — verdict のみの役割。修正は implementer 経由で戻す。

## 関連

- [`SKILL.md`](SKILL.md) — エージェント向け運用仕様（条件付きゲート + ツーリング解決 + 5 ステッププロセス + verdict ルール）。
- [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) — パッケージテスト側の兄弟ゲート。
- [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) — 両ゲートを呼び出すオーケストレータ。
- `loom-interface-design:interaction-flows` — このスキルが走らせる `ui-flows.md` の生産者；`loom-interface-design:design-critic` — `critic-found` 行で同ファイルを増補。
