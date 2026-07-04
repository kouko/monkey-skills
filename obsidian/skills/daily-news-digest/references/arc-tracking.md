# Arc tracking — long-running story books（追蹤本）

One markdown file per ongoing story under `news/store-arcs/`. The digest run
reads the books' frontmatter (cheap), matches today's stories against
them, appends one milestone line per hit, and reports lifecycle changes.
Books are the **material the digest's trend paragraphs read from** AND
the memory the digest writes back to. The user manages books
conversationally（「開一本追蹤 X」「暫停追蹤 Y」「不用追 Z 了」）— no
config file. **These lifecycle requests are valid standalone** — no
digest run needed: open = create the book (frontmatter + empty sections,
seeded keywords); pause/close/reactivate = edit the `status:` field.

## Book format

Location: `news/store-arcs/-Store Arc- <topic>.md` — the **filename
carries the fixed English prefix `-Store Arc- ` (including the
trailing space before the topic), in every vault
language** (the topic part still localizes) so book basenames never
collide with wiki pages or notes that share the topic/event name
(Obsidian resolves wikilinks vault-wide by basename), and so the
basename sorts to the end of any Notebook-Navigator-style flattened
file list next to dated `YYYY-MM-DD …` notes. Example:
`news/store-arcs/-Store Arc- 油價與能源.md`. Frontmatter `title` stays
the clean topic name (no prefix); links to a book always use the full
prefixed filename + a display alias (`[[-Store Arc- 油價與能源|油價]]`).
Book titles and body headings are in the **user's language**; this
spec's examples use zh-TW.

```yaml
---
title: 油價與能源
type: news-arc
concept: oil-energy  # language-neutral identity — starter books: use the slug from the starter table VERBATIM; event books coin their own
kind: topic          # topic = standing theme | event = named multi-week event
status: active       # active | paused | closed
keywords:            # canonical, multi-language (zh/en/ja) — reused every day, never re-guessed
  - 油價
  - WTI
  - Brent
  - 原油
  - OPEC+
  - 原油価格
indicators:          # numeric-table column definitions; may be empty for pure-event books
  - WTI
  - Brent
created: 2026-07-03   # actual run date the book was created — NOT the digest
                      # date on a backfill; the first milestone carries the story date
last_updated: 2026-07-03
---
```

Body — two fixed sections, plus one optional:

```markdown
## 數字表

| 日期 | WTI | Brent |
|---|---|---|
| 2026-07-02 | 80.1 | 83.4 |

## 里程碑

- **2026-07-02** — OPEC+ 增產決議推遲，WTI 反彈 3%（[[2026-07-02 每日新聞#油價|當日故事]]）
- **2026-07-02** — 〔發言〕Fed 理事 Waller：支持 7 月降息（鴿）（[[...|來源]]）

## 機構觀點

| 日期 | 機構 | 觀點 | 時效 |
|---|---|---|---|
| 2026-06-28 | GS | Brent 年底看 90 | 2026 年底 |
```

- **數字表** (numeric table): date × 1–3 columns per `indicators`.
  Append a row only when today's sources actually state the number —
  never interpolate. Trend charts (`xychart`) are generated FROM this
  table; no re-reading of old notes.
- **里程碑** (milestones): chronological append, one line per digest day
  that touched the story. **Line format is fixed — follow the example
  above exactly**: `- **<date>** — <one-line development>（[[<digest
  file>#<story heading>|當日故事]]）`. The closing digest link is
  mandatory (a milestone without it is invalid); the `#<story heading>`
  anchor must be **copied verbatim from the digest's actual `###`
  heading — same language, same characters; never invent or translate
  it** (anchors are exact-match, an invented anchor is a broken link).
  Do NOT paste source filenames into the line — sources are reachable
  via the digest's Source Index. Only days with real developments get a line — no
  "nothing today" filler. **Central-bank speak** is an entry type here,
  not a separate book: prefix `〔發言〕`, name the speaker, and tag the
  lean（鷹/鴿/中性）.
- **機構觀點** (house views, optional): sell-side / investment-bank
  calls are a **source type feeding a topic**, not a topic — a GS oil
  call belongs in the oil book. When a source carries a concrete bank
  view (price target, rate call, year-end forecast), append it here
  with its horizon so stale calls are visible.

## Daily integration (runs inside STEP 5)

1. **Instantiate starters** — create every §Starter-books entry whose
   `concept` is missing from `news/store-arcs/` (ALL 16 of them, matched or
   not — unmatched starters are created empty). Filename = `-Store Arc-
   <Title column text verbatim>` (with the trailing space before the
   topic). **Copy the table's Seed-keywords and
   Indicators columns into the frontmatter verbatim** — `keywords: []`
   is invalid (empty keywords silently break tomorrow's matching), and
   the 數字表 header must carry the indicator columns（e.g.
   `| 日期 | WTI | Brent |`）. This runs before matching, on every run,
   unconditionally — "I only created the books today's stories matched"
   is a known failure mode; the step-6 gate counts it.
2. **Load the registry** — read frontmatter of every `news/store-arcs/*.md`
   (grep/head is enough; do NOT read bodies of unmatched books).
3. **Match** each of today's stories against the `keywords` of
   non-`closed` books. A story may update more than one topic book when
   it genuinely spans them (one milestone line each). `paused` books:
   never append; note the match in the report only.
4. **Update** each matched active book: append milestone line + number
   rows (+ house-view rows); bump `last_updated`. When the digest's own
   Event Arc subsection needs history, use the book's 里程碑/數字表
   first — `collect_history.py` is the fallback for gaps and for
   backfilling a newly-opened book.
5. **Open** a new `kind: event` book ONLY when the arc sweep flags a
   multi-week arc that matches NO existing book — meaning: **the story
   shares zero keywords with every existing book**. Any keyword overlap
   (e.g. an HBM story vs the AI 與半導體 book's `HBM` keyword) = update
   that existing book instead; if you believe the story still deserves a
   dedicated book, PROPOSE it in the STEP 9 report for the user to
   approve — never auto-create over an overlap. Give a legitimately new
   book canonical multi-language keywords and one frontmatter `notes:`
   line stating the multi-week justification.
6. **THE GATE — run `arc_check.py` after the digest is written
   (machine-check, exit code decides; do not skip, do not paraphrase):**
   ```bash
   python3 "$SKILL_DIR/scripts/arc_check.py" "$VAULT_ROOT" <YYYY-MM-DD> \
     --expect-milestones <number of sweep-table rows you marked as matched>
   ```
   It verifies in one shot: all 16 starters present · no empty
   `keywords` · milestone anchors are real digest headings · milestone
   count ≥ sweep matches (defeats the empty-set pass) · event books
   share zero keywords with any other book AND their title/milestones
   contain no other book's keyword (defeats keyword-dodging). **Exit
   code non-zero = fix the listed items in THIS run and re-run until
   `ALL PASS ✓`.** Paste the final output verbatim into your report —
   never summarize it as "passed" without the output.
7. **Report** (STEP 9): books updated (count), event books newly opened
   (list), and any `kind: event` book idle > 14 days → suggest `closed` —
   when suggesting (or executing) a close, also remind the user: a
   closed event book's timeline is ready-made distillation material for
   `wiki-ingest` (manual handoff; this skill never writes to wiki/).
   `kind: topic` books are standing: never auto-flagged, never
   auto-closed. **The report is post-hoc, never an approval gate**: all
   creation and updating in steps 1–5 happens immediately and
   unconditionally during THIS run — do NOT ask permission first, do NOT
   defer creation to a future run. The user's veto is conversational and
   after the fact（「Y 不用追」→ close/delete the already-created book）.
8. **Propose trackable items** — surface the open/pause/close feature to
   users who may not know it exists. Take every sweep-table row marked
   `matched book` (a story that recurred but only updated an existing
   book, never got one of its own) and add one line each to the report:
   "『<story>』持續出現在 <matched book>，如果想單獨追蹤可以說『開一本追蹤
   <story>』。" No frequency/novelty filtering for now — surface every
   eligible row every run; revisit with a dedup/noise rule only if this
   proves repetitive after running for a while.

## Arc sweep table + red flags

Fill for EVERY story before moving to STEP 6 — leaving a row blank is
itself a decision that must be made explicitly:

| # | Story title | Multi-week arc? | Matched book / new book / skip |
|---|---|---|---|
| 1 | `<story 1>` | Yes / No | `store-arcs/-Store Arc- 油價與能源` / new event book / skip |

> [!warning] Red flags — stop and re-examine if you see any of these:
> - A Financial Markets & Macro category with **"No"** across every row
>   on a volatile day
> - Story subject is an FX rate, stock index, inflation print, or bond
>   yield → almost certainly an arc even if today's is the first note
> - Story title contains momentum/continuation markers（「創新高」
>   「連續」「第 N 天」"ongoing", "breakthrough"）→ arc by definition

## Language adaptivity

The **Concept** column below is the canonical, language-neutral
identity of each book. Everything else localizes at creation time:

- **Book title & body headings** → the user's conversation language
  (same rule as digest section names). The zh-TW titles below are the
  localized instance for this plugin's home vault — an English-vault
  user gets `-Store Arc- US Equities.md`; a zh-TW vault gets
  `-Store Arc- 美股大盤.md` — the prefix never localizes, only the
  topic does.
- **Keywords** → seed from the concept, then **cover the languages
  actually present in the vault's sources**: sample **~30 titles; any
  language appearing in ≥10% of the sample gets keyword coverage**. The
  sampling happens once, at first-run starter-book creation (inside
  STEP 5): use today's manifest `candidates` titles; if fewer than 30,
  top up from recent `references/` filenames (glob, newest first) until
  ~30 or the vault is exhausted. (The zh/en/ja mix below reflects a
  zh-TW-primary vault consuming EN+JA media.) Worked example for an
  EN-only vault: all 30 samples English → create `-Store Arc- US Equities.md` with
  `keywords: [US stocks, S&P 500, Nasdaq, Dow, futures, earnings]` —
  no CJK keywords, title in English, done. Keywords are vault data
  living in each book's frontmatter — once created they evolve with the
  vault, independent of this spec.
- **Frontmatter field names** (`title`/`kind`/`status`/`keywords`/…)
  stay English everywhere — they are machine-read.
- Matching is plain case-insensitive substring — language-agnostic by
  construction; no per-language code path exists or is needed.
- **Create-if-missing keys on the frontmatter `concept` field** (the slug printed in the
  Concept column below — use it verbatim, never re-derive it), never on
  the localized filename — so renaming a book or switching vault
  language never spawns a duplicate.

## Starter books — create-if-missing

Taxonomy aligned with standard sell-side / financial-media morning
briefings (Bloomberg Five Things, Reuters Morning Bid, JP bank FX
dailies, MacroMicro): overnight equities → rates & the dollar →
energy & metals → central banks → policy/geopolitics. On any run,
create the books below that don't exist yet (frontmatter + empty
sections; backfill optional via `collect_history.py`). All are
`kind: topic`, `status: active`. **Creation is unconditional and happens
in the current run** — starter books never require user approval; only
report what was created, afterwards.

| Concept (canonical) | Title (zh-TW instance) | Seed keywords (localize/extend at creation) | Indicators |
|---|---|---|---|
| **Equities** | | | |
| US Equities `us-equities` | 美股大盤 | 美股, S&P 500, 標普, Nasdaq, 那斯達克, 道瓊, 財報, futures, 米国株 | S&P 500, Nasdaq, VIX |
| Taiwan Equities `taiwan-equities` | 台股 | 台股, 加權指數, TAIEX, 台積電, 外資買賣超, 電子權值股 | 加權指數, USD/TWD |
| Japan Equities `japan-equities` | 日股 | 日股, 日經, Nikkei, 日経平均, TOPIX, 東証, 半導体株, 商社株 | 日經 225, TOPIX |
| **Rates & Bonds** | | | |
| USTs & US Rates `ust-us-rates` | 美債與美國利率 | 美債, 殖利率, 10Y yield, 2Y, yield curve, 美債拍賣, term premium, 米金利 | 2Y, 10Y（選配 HY 利差） |
| US Inflation & Data `us-inflation-data` | 美國通膨與經濟數據 | CPI, PCE, 非農, NFP, ISM, PMI, 零售銷售, GDP, 経済指標, 衰退 | —（事件驅動） |
| **FX** | | | |
| BOJ & JPY `boj-jpy` | 日銀與日圓 | 日銀, BOJ, 植田, 日圓, 円安, 円高, USDJPY, carry trade, 春鬥 | USD/JPY, JGB 10Y |
| USD & Majors `usd-majors` | 美元與主要貨幣 | 美元, DXY, dollar index, EURUSD, 人民幣, USDTWD, ドル高 | DXY |
| **Commodities** | | | |
| Oil & Energy `oil-energy` | 油價與能源 | 油價, WTI, Brent, 原油, OPEC+, 天然氣, 庫存, 原油価格 | WTI, Brent |
| Precious Metals `precious-metals` | 貴金屬 | 黃金, gold, 金價, 白銀, silver, 實質利率, 央行購金, 金価格 | 金 XAU, 銀 XAG |
| Industrial Metals & Broad Commodities `industrial-metals-commodities` | 工業金屬與大宗 | 銅, copper, 鐵礦砂, 農產品, CRB, 大宗商品, 商品市況 | 銅 |
| **Central Banks** | | | |
| Fed Policy & Fed Speak `fed-policy-speak` | Fed 政策與官員發言 | Fed, FOMC, 聯準會, Warsh, 沃許, Powell, 鮑爾, dot plot, 官員發言, 降息, 升息, 縮表, 利下げ | FFR 目標, FedWatch 機率 |
| Other Central Banks `other-central-banks` | 其他央行 | ECB, BOE, PBOC, 人行, 央行, LPR, 韓銀, RBA, 歐洲央行, 利下げ | — |
| **Geopolitics** | | | |
| Geopolitics: Middle East `geopolitics-middle-east` | 地緣政治：中東 | 中東, 以色列, 伊朗, 荷莫茲, Hormuz, 加薩, 紅海, 胡塞, 油輪 | — |
| Geopolitics: US-China & Taiwan Strait `geopolitics-us-china-taiwan` | 地緣政治：美中與台海 | 美中, 關稅, tariffs, 貿易戰, 出口管制, 半導體管制, 台海, 軍演, 制裁 | USD/CNH |
| **Macro regions / Industry** | | | |
| China Macro `china-macro` | 中國經濟 | 中國經濟, 房地產, 刺激政策, 中國 PMI, 內需, 通縮, 中国経済 | — |
| AI & Semiconductors `ai-semiconductors` | AI 與半導體 | AI, 輝達, Nvidia, 台積電, TSMC, HBM, AI capex, 半導體, ASML, 生成式 AI | 費半 SOX |

**Not standing books** (create on demand only): 歐股/歐洲個別市場（併入
其他央行，除非來源常態覆蓋）、加密貨幣（來源出現再開）、財報季（季節性
—— 個股財報路由到 美股大盤 / AI 與半導體）、韓股/韓國總經（來源常態出現
再開）。Keyword overlap across books is expected（台積電 → 台股 + AI
與半導體）; a genuinely-spanning story updates both, one line each.

**Person names in keywords are current officeholders, not permanent
vocabulary** (as of 2026-07: Fed chair = Kevin Warsh／沃許, sworn in
2026-05-22; Powell remains a governor; BOJ governor = 植田和男). When a
matched story reports a succession or personnel change (new chair /
governor / president), **update that book's `keywords` in the same
run** — add the incoming name, keep the outgoing name while the person
still holds a market-moving seat, drop it once they exit entirely.

## Hard rules

- Books live in `news/store-arcs/` — inside the collector's default exclude
  (`news/`), so they are never re-ingested as daily candidates.
- `references/` stays immutable (three-layer contract) — books link TO
  digests and sources, never edit them.
- Lifecycle changes (`paused`/`closed`, deletions) are user decisions;
  the agent only proposes them in the report.
- Milestone lines follow the same stem-linking Hard rules as the digest
  (short label, link built from the real stem, never a truncated title).
