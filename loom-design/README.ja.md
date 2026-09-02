# loom-design

> **漠然としたアイデアを、確認済みの intent と、ユーザー自身の言葉で読み返す
> spec に変える 2 つのステーション。そして、プロダクトの原則と見た目を決める
> 2 つのツール。** loom-design は下書きを書くだけで、採点はしない。ここで作った
> ものへの verdict はすべて `loom-code` の review ステーションが、下書きを書いて
> いない agent の手で下す。

**Status**: v1.0.0 — skill 4 個。Breaking：pre-1.0 の skill・script・分割 README は
リネームではなく削除。[CHANGELOG.md](CHANGELOG.md) を参照。
**Languages**: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)
**Repository**: [`monkey-skills`](https://github.com/kouko/monkey-skills) の一部

---

## 2 つのステーション

| ステーション | 生成物 | 読む |
|---|---|---|
| `capture-intent` | `docs/loom/intent/<change-id>.md` — ユーザーの言葉で書かれた変更。`status: confirmed` 付き | [SKILL.md](skills/capture-intent/SKILL.md) |
| `write-spec` | `docs/loom/<change-id>/spec.md` — 要件、決定と決定者、現状の証拠、UI flows | [SKILL.md](skills/write-spec/SKILL.md) |

計画ではなくアイデアから始まる変更の入口が `capture-intent`。ヒアリングし、
intent を書き、引き渡す — 設計が要る変更は `write-spec` へ、要らなければ
`loom-code` の `write-plan` へ直接。loom-design を入れていない場合は
`write-plan` が両方を自分でやる（品質は落ちる）。

## 2 つのツール

| ツール | 生成物 | 読む |
|---|---|---|
| `product-principles` | `docs/loom/PRINCIPLES.md` — Who / Non-negotiables（3 件以上）/ Won't do / Failure we must avoid / Fixed choices、そしてユーザー自身の yes が書き込む `ratified-by: <name> <date>` の行 | [SKILL.md](skills/product-principles/SKILL.md) |
| `design-system` | `docs/loom/DESIGN.md` — GUI 向けの色・タイポグラフィ・レイアウト・コンポーネントの token。TUI/CLI は conventions stub | [SKILL.md](skills/design-system/SKILL.md) |

ツールは頼まれたときに動き、ファイルを 1 つ作って止まる。`design-system` は
変更を止めない — DESIGN.md が無いのは注記であって gate ではない。
`product-principles` は違う：`kind: product` の変更では、non-negotiables が
3 件以上あり `ratified-by:` の行を持つ `PRINCIPLES.md` が無い限り loom-code の
checker が変更を受け付けない。ratify できるのはユーザーだけだから。

## 2 つの決定ポイント

1 つの変更がユーザーに尋ねる 3 つの質問のうち、最初の 2 つが loom-design の
担当。3 つ目（「動いた？」）は `loom-code` の ship ステーションが持つ。

1. **① これがやりたいことですか？** — `capture-intent` が変更を平易な言葉で
   言い直す。問題文にファイルパス・モジュール名・スクリプト名は入れない。
   yes を待つ。`status: confirmed` でない intent は下流のどこも受け取らない。
2. **② X をすると Y が見える、で合っていますか？** — `write-spec` が目に見える
   振る舞いを読み返す。product の変更だけで、engineering の変更では決して
   尋ねない。答えは `confirmed-behavior:` として記録される。

不可逆な分岐（データの削除、公開インターフェース、片道の migration）は
別の質問にせず、開いている ① か ② に、その結果の形で織り込む。

## loom-code 1.0 以上が必要

loom-design は `loom-code` の contract package を読むだけで、書かない。
`contract/manifest.yaml` が artifact の schema を宣言し、
`contract/templates/` が各種の空テンプレートを持つ。`plugin.json` は
`requires-contract: ">=1.0"` を宣言し、すべてのステーションとツールは

```bash
python3 <loom-code>/scripts/loom_checker.py contract --require 1.0
```

から始まる。バージョンが合わなければ、理解できない contract に向けて
下書きを書くのではなく BLOCK する。checker は loom-code のもので、
loom-design は gate を実行せず、名前を挙げるだけ。

## インストール

### Claude Code

```bash
claude plugin marketplace add https://github.com/kouko/monkey-skills.git
claude plugin install loom-design@monkey-skills
claude plugin list | grep loom-design     # enabled と出れば OK
```

`loom-code` も同じ手順で入れる（必須）。plugin 同士は
`loom-design:write-spec` のような plugin 名付き skill 名、contract package、
そしてプロジェクト自身の `docs/loom/` の artifact だけで繋がる — 他 plugin の
`hooks/`・`skills/`・`scripts/` を直接触ることは絶対にない。

### Codex CLI

Codex に marketplace は無いので、plugin は checkout から読み、loom-code の
checker は `.codex/hooks/loom_checker.py` として repo 内に scaffold される。
コマンドは loom-code の README を参照。`/hooks` を実行しろと言われたら実行する
こと — 信頼されていない Codex hook は黙ってスキップされ、check が通ったのと
見分けがつかない。

## テストの走らせ方

```bash
python3 -m pytest loom-design/scripts/
```

1 回の実行で 3 つのステーションディレクトリ（`interface/`・`principles/`・
`spec/`）をすべて収集する。`scripts/pytest.ini` が `--import-mode=importlib` を
設定して同名の test モジュールが並存できるようにし、`pythonpath` が bare な
sibling import のためにステーションディレクトリを `sys.path` に戻す。
`test_unified_pytest_root.py` がこの配置を pin しているので、ディレクトリごとに
job を分ける fan-out が事故で復活することはない。

## ライセンス

MIT（`monkey-skills` の一部として）。
