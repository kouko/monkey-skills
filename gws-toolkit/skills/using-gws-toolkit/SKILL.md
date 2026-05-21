---
name: using-gws-toolkit
description: Router skill for gws-toolkit. Route the user to the right skill based on intent (design consultation / onboarding / deck generation / Drive operations / Docs / Sheets). Slides backend is the primary use case; raw Drive / Docs / Sheets API access via vendored upstream gws-* skills. 簡報・投影片・deck・プレゼン・slides・presentation・幻灯片・Drive・Docs・Sheets・試算表・文件。
---

# using-gws-toolkit

Entry router for the `slides-toolkit` plugin. Inspect the user's intent, read the `slide-plan.json` `target` field (if one exists), and route to the right skill. This router **does not** execute shell commands, call APIs, or make design decisions — routing only.

## When to use

- The user's request is vague ("make me a deck", 「プレゼン作って」, 「做一份 deck」) and no specific skill is named yet.
- The user has a `slide-plan.json` but is not sure which builder to call next.
- First-time use of slides-toolkit, or an auth / setup error.

## When NOT to use

- The user names a target skill explicitly ("run slides-builder") → call it directly.
- The task is outside slides-toolkit (copywriting → `copywriting-toolkit`; investment analysis → `investing-toolkit`).

## Routing table (intent to skill)

| Intent signals (EN / JP / ZH) | Route to |
|---|---|
| Design consultation (デザイン相談 / 設計諮詢) — EN: "narrative structure", "which chart type", "information hierarchy", "Minto / SCQA". JP: 「敘事構成」「どの図表」「情報階層」「Minto / SCQA」. ZH: 「敘事結構」「哪種圖表」「資訊層級」「Minto / SCQA」 | `slides-design` |
| Setup / auth (初期設定 / 初次設定) — EN: "first time", "401 / 403 / invalid_scope", "auth failed", "gws not installed", "token expired". JP: 「初めて使う」「認証エラー」「gws まだ入れてない」「token 切れ」. ZH: 「第一次用」「auth 失敗」「gws 還沒裝」「token 過期」 | `gws-setup` |
| Deck generation (デッキ生成 / 生成 deck) — EN: "generate the deck", "turn slide-plan into Google Slides", "export", "run pipeline". JP: 「deck を作る」「slide-plan を Google Slides に」「エクスポート」「パイプライン実行」. ZH: 「生成 deck」「把 slide-plan 變 Google Slides」「匯出」「執行 pipeline」 | `slides-builder` |
| Low-level API learning / debugging (API 学習・デバッグ / API 學習・除錯) — EN: "how do I call this op", "debug a Slides error", "learn batchUpdate", "tweak a recipe". JP: 「この API の使い方」「Slides のエラーをデバッグ」「batchUpdate を学ぶ」「recipe を改造」. ZH: 「單一 API op 怎麼打」「debug Slides 錯誤」「學 batchUpdate」「想改 recipe」 | upstream `gws-slides` skill (raw API method discovery) or `slides-builder` (the 4 bundled recipes — composition patterns, error mapping) |
| Email management (メール管理 / 郵件管理) — EN: "read my inbox", "find an email", "list messages", "inbox triage". JP: 「メール検索」「インボックス」「Gmail を読む」「スレッド」. ZH: 「找信件」「收信」「Gmail 信件」「列出郵件」 | `gws-gmail` (parent API reference) + `gws-gmail-read` (general read recipes for messages / threads / labels / search) |
| Calendar / scheduling (カレンダー・スケジューリング / 行事曆・安排) — EN: "today's agenda", "find a free slot", "schedule a meeting", "list events". JP: 「予定」「カレンダー」「空き時間」「アジェンダ」. ZH: 「行事曆」「今天行程」「找空檔」「找會議時間」 | `gws-calendar` (parent API reference) + `gws-calendar-agenda` (agenda-view recipes) |
| Gmail send / write — EN: "send mail", "send email", "compose and send", "reply to thread". JP: 「メール送信」「メール作成」「返信」. ZH: 「寄信」「寄送郵件」「回信」 | `gws-gmail-send` (vendored API reference). **Recommended entry**: `scripts/gws/gmail-confirm-send.sh` (safety wrapper — see Safety wrappers row below) |
| Calendar event create / write — EN: "create event", "insert calendar event", "book a meeting", "add to calendar". JP: 「イベント作成」「カレンダー追加」「予定を入れる」. ZH: 「建立行事曆事件」「新增事件」「加進行事曆」 | `gws-calendar-insert` (vendored API reference). **Recommended entry**: `scripts/gws/calendar-confirm-insert.sh` (safety wrapper — see Safety wrappers row below) |
| Docs write / modify — EN: "modify doc", "write to doc", "append to document", "edit doc". JP: 「ドキュメント編集」「ドキュメント追記」「Docs に書く」. ZH: 「改文件」「寫進文件」「文件追加」 | `gws-docs-write` (vendored API reference). **Recommended entry**: `scripts/gws/docs-confirm-append.sh` (safety wrapper — see Safety wrappers row below) |
| Sheets write / append — EN: "append row", "add to sheet", "write cell", "clear range", "overwrite sheet". JP: 「行追加」「シート書き込み」「セル更新」「範囲クリア」. ZH: 「加列」「寫入試算表」「更新儲存格」「清除範圍」 | `gws-sheets-append` (vendored API reference). **Recommended entry**: `scripts/gws/sheets-confirm-write.sh` (safety wrapper — see Safety wrappers row below) |
| Drive upload / file create — EN: "upload file", "create file on Drive", "put file in Drive". JP: 「ファイルアップロード」「Drive にアップ」「ファイル作成」. ZH: 「上傳檔案」「上傳到 Drive」「建立檔案」 | `gws-drive-upload` (vendored API reference). **Provenance / safety wrapper**: `scripts/gws/tag-create.sh` (pre-existing since v0.4.0 — stamps provenance metadata on Drive uploads; no new v0.7.1 wrapper needed for Drive) |
| Safety wrappers — write-side ops with confirm prompts (書き込み確認ラッパー / 寫入確認包裝) — EN: "send mail with confirm", "compose + safe send", "create event with confirm", "append/clear sheet with confirm", "append/replace doc with confirm". JP: 「メール作成と確認送信」「イベント作成と確認」「シート書き込みと確認」「ドキュメント追記と確認」. ZH: 「寫信加防呆」「建立事件加確認」「試算表寫入加確認」「文件加入加確認」 | `scripts/gws/gmail-confirm-send.sh` (L3 — typed recipient + subject) / `scripts/gws/calendar-confirm-insert.sh` (L2 attendees, L1 solo) / `scripts/gws/sheets-confirm-write.sh` (L1 append, L2 clear/overwrite) / `scripts/gws/docs-confirm-append.sh` (L1 with broad-stroke warning). Prefer these over direct vendored `gws-*-send/insert/write/append` calls for any interactive write. |
| Vague or "make a simple deck" with no explicit target | Default `target: "google-slides"` (MVP's only backend); continue through setup → builder. |

**Example A** (design consultation):
> User: "I'm making a product proposal — how should the opener flow?"
> Route → `slides-design` (reads `references/minto-scqa.md`), replies with an SCQA suggestion; no deck is generated.

**Example B** (pipeline execution):
> User: "Run this `slide-plan.json` for me."
> Check `slide-plan.target == "google-slides"` → confirm setup is complete → route to `slides-builder`.

**Example C** (low-level API learning / debugging):
> User: "How exactly do I pass `predefinedLayout` to gws `createSlide`?"
> First-line: upstream `gws-slides` skill (raw method/parameter reference) or `gws schema slides.<resource>.<method>` introspection.
> For composition patterns (e.g. how the placeholder map threads across calls): `slides-builder`'s `protocols/recipe-create-slides.md` + `references/api-error-codes.md`. Does not run the pipeline.

## Target backend detection

Read the top-level `target` field in `slide-plan.json` (schema v1.2, TECH-SPEC §4.1):

```
target == "google-slides"  → route through gws-setup / slides-builder
target missing             → assume "google-slides" (MVP's only backend); tell the user explicitly
target ∈ {"html","pptx","marp"}  → error out and point at the Phase 2+ trigger below
target == anything else    → error: unsupported backend
```

If the user has a plan without `target`, the router may fill in `"google-slides"` and note that other backends are Phase 2+.

## Phase 2+ backends (trigger-gated, not a commitment)

The backends below are **not implemented in MVP**. They are listed as forward-looking only. Trigger conditions live in PRODUCT-SPEC §3.5:

| Backend | Skill (future) | Trigger |
|---|---|---|
| `html` | `html-builder` | First request for HTML / reveal.js / remark output |
| `pptx` | `pptx-builder` | First `.pptx` output request (e.g. delivery to an MS Office recipient) |
| `marp` | `marp-builder` | First Marp CLI output request (engineering tech talk / markdown-native) |

If the user sets `target` to one of these, reply: "Backend `<value>` is not yet implemented; MVP only supports `google-slides`. Trigger conditions are in PRODUCT-SPEC §3.5."

## Out of scope — hand off

| Need | Target |
|---|---|
| Copywriting / headlines / PASONA / QUEST | `copywriting-toolkit:using-copywriting-toolkit` |
| Investment analysis / decks that embed financial content | `investing-toolkit:using-investing-toolkit` |
| Technical documentation / API reference | `domain-teams:docs-team` |

---

> 🔄 CHECKPOINT: This artifact is raw output. Pipeline: consult your workflow for the next gate.
