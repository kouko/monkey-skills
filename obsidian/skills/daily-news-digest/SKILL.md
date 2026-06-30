---
name: daily-news-digest
description: |
  Compile one day's vault notes into a two-tier daily digest — clustered time-sensitive stories + evergreen knowledge links — at news/YYYY-MM-DD. Use for '整理今天的新聞', '每日新聞', 'daily news digest', or rounding up a day's content.
---

# Daily News Digest（每日新聞彙整）

Turn one day's scattered consumed content into a single, skimmable note with
**two tiers**: synthesized time-sensitive news, plus a curated index of the day's
knowledge content.

The vault's `references/` folder accumulates dozens of notes a day — YouTube
summaries, article clips, event recaps. Some of it is genuine **time-sensitive
news** (what moved markets, what launched, what happened); much of it is
**evergreen-but-valuable** (a sharp op-ed, a tool review, a tutorial, an
investing-strategy breakdown). Both deserve a place — but handled differently.
This skill **synthesizes the news into rewritten, integrated stories** (so a week
later you get a richer picture than any single note), and **indexes the knowledge
content** as categorized links (so nothing valuable is silently dropped), without
reopening 50 notes.

## Triage — sort every candidate into one of three buckets

Judge each note on its **content**, using `tags` + `snippet` as the primary
signal. The YouTube `categories` field lies — an AI-market analysis gets tagged
`Entertainment`, a coding tutorial gets `Education` — so never triage on it.

| Bucket | What goes here | How it's handled |
|---|---|---|
| **📰 新聞(整合故事)** | Dated events: 個股/財報/油價/利率/Fed・央行, 衝突/選舉/政策/制裁, 發表會/新模型/併購 | Clustered + synthesized into rewritten stories, then grouped under thematic category headings (the heart of the skill) |
| **🧠 知識與觀點** | Substantive but not date-driven: 社論/評論, 工具評測/跑分, 教學/walkthrough, 投資策略/方法論, 長青深度分析 | Categorized short-labeled links + one-line takeaway each (NOT rewritten) |
| **研究附錄 / drop** | The user's own research / analysis notes → research appendix (links only). Pure filler with no takeaway → drop. | Links only |

> [!tip] The litmus test for tier 1 vs tier 2
> Ask: "If I read this six months from now, would the **date** matter?" A market
> move or launch is stale in a week → 時效新聞. A tutorial or a thinking-model
> essay is just as useful next year → 知識與觀點. Both stay in the digest; only
> the **treatment** differs (synthesized story vs indexed link).

Borderline event-driven explainers lean on whether a **specific dated event**
drives the piece. When genuinely unsure between the two tiers, prefer 知識與觀點
(a link is cheaper than a forced story).

## Workflow

### STEP 0 — Pre-flight

Before spending tokens on collection, do two things:

1. **Check for an existing digest** — `ls "news/<YYYY-MM-DD>*"`. If found, ask
   **overwrite / merge / abort** and wait for the user's answer before continuing.
2. **Resolve the skill base directory** — it appears as `Base directory for this
   skill:` in the skill metadata header injected by the runtime. Store it as a
   shell variable; every script call below uses it:
   ```bash
   SKILL_DIR="<the path shown in the skill metadata header>"
   ```
   Using the runtime-provided path avoids hard-coding the plugin cache version.

### STEP 1 — Collect candidates

Resolve the date (default `date +%Y-%m-%d`; or the user's named date — must be
`YYYY-MM-DD`), then run the collector. It does the cheap deterministic gathering
so tokens go to judgment, not file-opening:

```bash
python3 "$SKILL_DIR/scripts/collect_sources.py" <YYYY-MM-DD> .
```

It casts a **wide net**: every dated note **anywhere in the vault** — no folder
layout assumed — is returned in one `candidates` list (each with `path` /
**`wikilink`** / `folder` / title / url / channel / tags / ~400-char snippet).
It skips only `wiki/`, `news/` (this skill's own output), `_templates/`, and
dot-folders by default (`--exclude` to change). **You decide what's in or out at
triage** — the collector doesn't pre-filter by folder. If `counts.candidates` is
0, tell the user no dated notes exist for that day and stop — don't fabricate.

### STEP 2 — Triage each candidate into the buckets

For **each** `candidates` entry, assign one of: **時效新聞** / **知識與觀點** /
**研究附錄** (the user's own research/analysis — goes to the appendix, not the
body) / **drop**. Use `tags` + `snippet` as the primary signal; `folder` is a
hint, not a rule (e.g. a `research/`- or `notes/`-style folder leans 研究附錄, a
clippings/references-style folder leans consumed-content) — but judge on content.
Keep a running tally (you'll report kept-vs-dropped to the user).

### STEP 3 — Cluster the news into stories, then group stories by theme

A single day's references cover the same event from many angles — on a heavy
news day, 8–10 finance videos all orbit one crisis. **Cluster sources that cover
the same underlying story** so you can merge them. A "story" is one
event/development covered by ≥1 source; group by what actually happened, not by
folder or language. The same crisis told through a military lens, an oil-price
lens, a market-reaction lens, and a diplomat lens is **one story with four
sources**. Aim for **4–7 stories** on a busy day. A lone source is a valid
one-source story; just don't pad it.

Then **group the stories under 2–4 thematic category headings** using the
**anchored-open** taxonomy below. There is **no single "時效新聞" umbrella
heading**; the news is categorized the same way 知識與觀點 is. **Story headings
carry no number** — `### <故事標題>`. The 來源索引 references each story by its
short title, not a number.

**時效新聞 category anchor list** — pick 2–4 that fit the day's stories:

| Category | Typical stories |
|---|---|
| 國際・地緣政治 | conflict, diplomacy, sanctions, elections, international orgs |
| 金融市場・總經 | equities, FX, rates, inflation, central banks, bonds |
| AI・科技 | model releases, AI products, tech platforms, semiconductors |
| 商業・產業 | earnings, M&A, corporate strategy, industry dynamics |
| 能源・商品 | oil/gas prices, mining, commodities, supply chains |
| 政策・監管 | legislation, regulatory action, tariffs, government policy |

If none of the six fits, create a new heading — but add a one-line comment in
the digest's frontmatter `notes` field explaining why (e.g. `notes: "新增「社會・
文化」— 當日有重大社會事件"`), so the taxonomy can be reviewed and extended
deliberately.

### STEP 3.5 — For evolving stories, pull history and build 事件進程

Some stories are **not one-off events but ongoing arcs** — a geopolitical
conflict, an oil-price move, a rate/inflation cycle, a stock-index trajectory,
an earnings arc. For these, reconstruct the progression so the reader sees the
*trend*, not just today's snapshot.

> [!important] Sweep EVERY story, across ALL categories
> This is **not just for the headline geopolitical story**. Walk your full story
> list and flag every multi-week arc. Market/macro stories are the most common
> miss — a stock index hitting a record is an arc (the rebound only means
> something against the prior correction); long-end yields, inflation prints,
> and an FX cycle are all arcs. A 📈 金融市場・總經 category with zero 事件進程 on
> a volatile day is usually a miss, not a clean day.

**What SKIPS 事件進程:**
- **One-off events** — a product launch, a regulatory action, an M&A headline,
  a single earnings beat. There is no multi-week trajectory to draw.
- **Forward-looking single events** — "this week's central-bank decision" is an
  upcoming datapoint, not a progression. (Its *backdrop* — the rate/yield arc —
  may already be covered by a sibling story's 事件進程; don't duplicate it.)

1. **Pull prior notes** with the history collector — it greps `references/` +
   `investing/` for earlier dated notes on the same entity/keywords:

   ```bash
   python3 "$SKILL_DIR/scripts/collect_history.py" \
     "<關鍵字,OR,逗號分隔>" . --since <YYYY-MM-DD> --until <digest date − 1>
   ```

   `--until` = the day **before** the digest date (today's notes are already in
   the story). It returns a date-sorted timeline of {date, wikilink, snippet}.

2. **Extract the trajectory** — read a few milestone notes for the real numbers
   (e.g. oil 104 → 90 → 80 across the weeks), then write a short progression
   sub-section: a 趨勢分析 paragraph + (optionally) a visual. **Give the `####`
   heading a dynamic, content-specific title** — not a fixed "事件進程" label.
   Name the actual arc: 「油價三個月:104 高峰跌破 80」、「日經過山車:創高→修正→再創高」、
   「升息路徑:從擺脫通縮到 31 年高位」、「Fable 5 一週風暴:發布→被禁→傳返場」. Use a
   **`timeline`** Mermaid for milestone chronology, or an **`xychart`** line for a
   clean numeric series. **Proportionality**: if the story already carries a
   mechanism diagram (a flowchart/graph), a **prose-only** 趨勢分析 is enough —
   don't stack 3 charts in one category. (E.g. on 2026-06-15, the market-rebound
   story got a timeline; the sibling 大摩-fragility story, which already had a
   graph, got a prose yield-trajectory paragraph.)
3. **Cross-reference the user's own `investing/` analyses** when they exist —
   surfacing "you predicted this in March" is high-value (per vault CLAUDE.md).
4. **Cite the history minimally.** If you cross-referenced an `investing/`
   analysis, keep a short inline link to it at the paragraph end (e.g. 「可對照
   investing/ [[…|3月油價通膨分析]]」). **Do NOT** add generic boilerplate like
   「綜合 references/ 近月逐日筆記」 — it repeats across every story and adds no
   information; the 事件進程 already implies prior-note synthesis. Never imply
   numbers you didn't read, but a bare references/-only attribution can be dropped.

**事件進程 sweep table — fill this for EVERY story before moving to STEP 4.**
Do not skip; leaving a row blank is itself a decision that must be made explicitly:

| # | Story title | Multi-week arc? | Action |
|---|---|---|---|
| 1 | `<story 1>` | Yes / No | `collect_history(...)` / skip |
| 2 | `<story 2>` | Yes / No | `collect_history(...)` / skip |
| … | | | |

> [!warning] Red flags — stop and re-examine if you see any of these:
> - A 📈金融市場・總經 category with **"No"** across every row on a volatile day
> - Story subject is an FX rate, stock index, inflation print, or bond yield
>   → almost certainly an arc even if today's is the first note you've collected
> - Story title contains 「再創高」「連續」「第N天」「持續」「突破」→ arc by definition

### STEP 4 — Synthesize each story (the heart of this skill)

> [!important] Execution model — delegate the note-reading on heavy days
> Reading every clustered note (full bodies, often with long transcripts) into the
> main context is the real context cost. So **route by load**:
> - **Heavy day** (`counts.candidates` ≳ 40, OR any single cluster ≳ 6 notes):
>   **dispatch one subagent per story-cluster, in parallel** (one assistant message,
>   multiple `Agent`/`Task` calls — they're independent). Give each subagent the
>   cluster's note **paths** + the story angle; it reads the full notes and returns
>   the **structured story object** (contract below) — the main agent never loads
>   raw transcripts, only finished stories. The knowledge tier (STEP 5) can be one
>   more subagent. Then the **main agent assembles, renders every CoT via
>   `$SKILL_DIR/scripts/cot_mermaid.py`, writes the file, and runs the link self-check** —
>   rendering and verification stay central for consistency.
> - **Light day**: skip subagents — the dispatch overhead isn't worth it; the main
>   agent reads and synthesizes directly.
>
> **Subagent return contract** (one per story, so the main agent can assemble
> uniformly) — return JSON-ish:
> ```
> { heading, category(🌍/📈/🤖/🚀…), tldr,
>   cot: {type:"chain", nodes:[{title, bullets:[…]}, …]},   // → $SKILL_DIR/scripts/cot_mermaid.py
>   narrative: ["<段1>", "<段2>"],            // inline links as [[stem|短標籤]]
>   table?: "<markdown table or null>",
>   progression?: { title, milestones:[{date, text}], note },  // 事件進程, evolving only
>   sources: [{stem, label}] }                // for inline links + 來源索引
> ```
> The CoT `nodes` carry only content; `$SKILL_DIR/scripts/cot_mermaid.py` applies the fixed
> colours/style. The main agent owns dedup, the day-level 總圖, and STEP 8 verify.

For each cluster, **rewrite an integrated story** — you are the editor merging a
wire feed, not summarizing notes one by one:

1. **Read the actual source notes**, not just the manifest snippets — open every
   note in the cluster (`references/`) for the real facts, numbers, and quotes.
2. **Integrate and cross-reference.** Reconcile numbers (if two sources cite WTI
   at 80.3 vs 81, say so), combine the timeline, assemble the fullest picture.
   Where sources disagree on interpretation, **surface the disagreement** — that
   tension is signal.
3. **Write a one-line TL;DR — the bottom-line takeaway / so-what**, NOT a
   restating of the causal steps (the COT 圖 below carries those). Then a **COT
   mini-diagram** directly (a compact `flowchart LR` of the story's 3–4-hop causal
   chain (**3–5 hops as the story warrants, not a fixed 4** — 觸發→機制→結果→含義 is
   a natural arc, collapse or extend as needed) — **no `推演`/caption label before
   it**. Each node = 標題 + ━━━━ + a **left-aligned bullet list of 3–5 `• ` facts**
   (`<div style='text-align:left'>`; not prose — it renders unevenly). **Colour
   every node by role with the fixed scheme** (觸發 綠 / 機制 紫 / 結果 橙 / 含義 青 —
   see digest-format §COT), consistent across all CoT diagrams. So TL;DR =
   conclusion, COT 圖 = steps, narrative =
   detail — three complementary layers. Then **1–3 narrative paragraphs** in
   繁體中文. (The day-level 總圖 lives in the merged `## 🧭 當日總覽` — see STEP 6.)
   **Segment for readability** — break a long block into short paragraphs (≈ 2–4
   sentences each, one idea per paragraph: framework / terms / market reaction /
   disagreement…). Never ship a 5+ sentence wall of text; a blank line between
   ideas is the cheapest readability win.
4. **Add a visual only when it earns its place** (table for comparable data,
   Mermaid for a causal chain / one-cause-many-effects / timeline).

### STEP 5 — Index the 知識與觀點 tier

(On a **heavy day**, this whole tier can be **one more subagent** — see STEP 4's
execution model — returning each sub-category's 精選/整合 summaries + CoT node
content; the main agent renders + assembles.)

Group tier-2 items under sub-headings using the **anchored-open** taxonomy
below — pick 2–4 that fit the day's knowledge content:

| Sub-category | Typical content |
|---|---|
| 投資策略・市場觀點 | investing frameworks, stock analysis, market commentary, strategy |
| AI・開發・工具 | LLM applications, dev tools, engineering practices, AI research |
| 科技產品・趨勢 | product reviews, tech launches, hardware, platform trends |
| 商業・策略・思維 | business models, strategy frameworks, mental models, management |
| 設計・創作 | UI/UX, industrial design, visual design, creative tools |

If none of the five fits, create a new sub-heading and add a one-line comment
in `notes` (same rule as the news tier). In **each** sub-category:

1. **Promote ≥1 important piece to a 2–3 sentence summary** in a `> [!example]`
   callout. The callout title is **the piece's short title only** (no "精選摘要 —"
   prefix); end with a `> 來源:[[<stem>|<短標籤>]]` line, then a **CoT 小圖**
   (same style as the news COT: `flowchart LR`, bullet-list nodes, 3–5 hops) that
   visualises that piece's argument logic.
2. **When ≥2 items in the category cover the same sub-topic or debate, integrate
   them into a short analysis** instead of listing them separately — a
   `**整合分析 — <主題>**` sub-block (2–3 sentences) that reconciles the pieces,
   names the agreement/tension, and links each contributing source inline with a
   short label, then its own **CoT 小圖** (兩方辯論 → 共識 → 分歧, etc.). (e.g. a
   bull-case and a bear-case on the same stock → one 多空辯論 analysis.) This is
   the knowledge-tier analogue of STEP 3–4 clustering.
3. Then a **`**其他相關文章**` sub-label**, followed by the *remaining* unrelated
   items as one-liners: `- [[<stem>|<短標籤>]] — <核心論點或方法,一句>` (these are
   link-only — **no CoT 圖**). The sub-label keeps the section reading smoothly
   (摘要+圖 → 整合+圖 → 相關清單).

Only force integration where relatedness is real; disparate items stay as a
curated one-liner list. The value is a categorized index with synthesis where it
earns its place.

### STEP 6 — Write the digest

**READ `references/digest-format.md` first** — it holds the output template, the
link-presentation rules, and the Mermaid house style. Then create
`news/<YYYY-MM-DD> 每日新聞.md`. **Order at the top: `## 目錄` first (right under the
title)**, then a merged **`## 🧭 當日總覽`** section. The 目錄 is in-page
`[[#完整標題|短名]]` anchor links to each story (grouped by news category) plus
知識與觀點 / 其他觀察 / 來源索引 / 附錄. The 當日總覽 section merges the `> [!abstract]`
overview text **and** the day-level COT `flowchart TD` 總圖 (causal web of the day's
stories). **Render every CoT diagram — the 總圖 and each story / knowledge 小圖 —
through `$SKILL_DIR/scripts/cot_mermaid.py`** (feed it node content JSON), so
the fixed role-colours and style are identical everywhere; don't hand-write the
`style` lines. Concrete calling pattern:

```bash
# Per-story chain (flowchart LR) — roles assigned by position (first=trigger, last=concl):
cat > /tmp/cot_chain.json << 'COTJSON'
{"type":"chain","nodes":[
  {"title":"觸發節點","bullets":["事實1","事實2","事實3"]},
  {"title":"機制節點","bullets":["原因1","原因2"]},
  {"title":"結果節點","bullets":["影響1","影響2"]},
  {"title":"含義節點","bullets":["結論1","結論2"]}
]}
COTJSON
python3 "$SKILL_DIR/scripts/cot_mermaid.py" /tmp/cot_chain.json

# Day-level 總圖 web (flowchart TD) — each node needs explicit "role":
cat > /tmp/cot_web.json << 'COTJSON'
{"type":"web",
 "nodes":[
   {"id":"A","title":"故事1","bullets":["要點"],"role":"trigger"},
   {"id":"B","title":"故事2","bullets":["要點"],"role":"mech"},
   {"id":"C","title":"共同結果","bullets":["要點"],"role":"result"},
   {"id":"D","title":"含義","bullets":["結論"],"role":"concl"}
 ],
 "edges":[
   {"from":"A","to":"C","label":"推動"},
   {"from":"B","to":"C","label":"加速"},
   {"from":"C","to":"D","label":"導致"}
 ]}
COTJSON
python3 "$SKILL_DIR/scripts/cot_mermaid.py" /tmp/cot_web.json
```

The script writes a ready-to-paste ` ```mermaid ``` ` block to stdout.
`(` `)` in node titles are automatically converted to `「」` (Obsidian-Mermaid safe).

Follow the vault's Obsidian conventions
(complete frontmatter, callouts) and the digest-format link rules: **embed
short-labelled jump-links inline in the body (anchored on words already in the
prose), AND also collect every source into a `## 來源索引` at the end as a
standard full-filename list under per-story `###` sub-headings** (see §Hard rules
on why raw long links are banned in narrative).

### STEP 7 — Appendices & report

- **Research appendix**: each item you triaged as **研究附錄** as a short-labeled
  link + one line.
- **Handwritten appendix**: if `daily/<YYYY-MM-DD>.md` exists, surface real
  handwritten content from its `## Note` section; skip silently if empty.
- **Report**: digest path, story count (and sources merged), tier-2 item count,
  kept-vs-dropped one-liner, and anything borderline to double-check.

## Hard rules

> [!warning] references/ 是唯讀的 Sources 層
> NEVER edit, rename, or add wikilinks **into** any `references/` note. This skill
> only **reads** them and links **from** the new `news/` note **to** them — the
> vault's three-layer wiki contract (`wiki/SCHEMA.md`); the Sources layer is
> immutable.

> [!important] 連結用 wikilink stem,不是 title;且必須短
> A source note's frontmatter `title` is NOT its filename — the vault's
> YouTube-summary workflow strips `&`, `()`, ` (summary)` etc. from the filename.
> Linking `[[<title>]]` produces a **broken link**. ALWAYS build the target from
> the collector's `wikilink` field (= the real stem), and give it a short display
> label: `[[<stem>|<短標籤>]]`. Never inline a **bare long** wikilink. Do embed
> **jump-links inline by wrapping an existing prose phrase** (display text = the
> words already in the sentence), NOT a `(短標籤)` parenthetical — so the reader
> hops to a source while reading. AND **also** list every source in the end
> `## 來源索引` as a full-filename list (see `references/digest-format.md` for
> the inline-vs-index split).
>
> **Beware truncated triage views.** When you print the manifest to eyeball
> candidates, the `title` is often clipped (`… (summary)` cut off, long titles
> shortened). NEVER copy a link target from that printed/truncated view — go back
> to the manifest JSON and copy the full `wikilink` field. (Real failure on
> 2026-06-16: three misc links built from clipped titles broke until rebuilt from
> the stem.)

> [!important] 寫完跑自檢（COT 完整性 + 連結解析 + Mermaid 語法）
> After writing the digest, run **three checks** before declaring done.
>
> **① COT 完整性** — every time-sensitive story must have a `flowchart LR`.
> Count story headings in the news section and compare to COT diagram count:
> ```bash
> python3 - "news/<YYYY-MM-DD> 每日新聞.md" <<'PY'
> import re, sys
> text = open(sys.argv[1], encoding="utf-8").read()
> news = text.split("## 🧠")[0] if "## 🧠" in text else text
> stories = len(re.findall(r"^### ", news, re.M))
> cots = len(re.findall(r"^flowchart LR", text, re.M))
> print(f"Stories (news section): {stories}  |  COT diagrams (LR): {cots}")
> if cots < stories:
>     print(f"⚠️  {stories - cots} story/stories missing COT — add before finishing")
> else:
>     print("COT completeness ✓")
> PY
> ```
>
> **② 連結解析** — every wikilink must resolve to a real file:
> ```bash
> python3 - "news/<YYYY-MM-DD> 每日新聞.md" <<'PY'
> import re, os, sys
> doc = open(sys.argv[1], encoding="utf-8").read()
> links = {m.split("|")[0].split("#")[0].strip()
>          for m in re.findall(r"\[\[([^\]]+)\]\]", doc)}
> stems = {f[:-3] for _,_,fs in os.walk(".") for f in fs if f.endswith(".md")}
> miss = sorted(links - stems - {""})
> print("broken:", miss or "none ✓")
> PY
> ```
> Note: `""` is filtered out — it comes from page-anchor-only links like
> `[[#heading|label]]` where `split("#")[0]` is empty; these are not broken.
>
> **③ Mermaid 語法** — parse every mermaid block through mermaid-cli (requires `npx`):
> ```bash
> bash "$SKILL_DIR/scripts/validate.sh" "news/<YYYY-MM-DD> 每日新聞.md"
> ```
> FAIL = real syntax error (fix before finishing). WARN = literal `"` in rendered
> text (likely a wrongly-quoted title/label). PASS = parses in mermaid-cli —
> note: cli is more lenient than Obsidian, so CJK-heavy diagrams should also be
> verified in Obsidian directly.
> This check is most valuable for hand-written diagrams (`timeline`, `xychart`
> in 事件進程); `cot_mermaid.py`-generated diagrams rarely fail here.

> [!danger] 合成失敗模式 — NEVER do these
> - **NEVER merge two events into one story just because they share an asset or
>   region.** A Fed decision and an oil shock both moving markets are TWO stories.
> - **NEVER let the most detailed source set the narrative frame** — reconcile
>   across all sources in the cluster first, then write.
> - **NEVER invent a causal link to bridge a cluster.** If sources don't state the
>   connection, present them side by side, not as cause-and-effect.
> - **NEVER trust the YouTube `categories` field for triage** — it mislabels;
>   judge on `tags` + `snippet`.
> - **NEVER fabricate a fact to fill a theme.** If a snippet is too thin to know
>   what happened, open the source note and read it rather than guessing.

- **Create `news/` if it doesn't exist** — it's a new top-level folder.
- **One file per day.** If `news/<date> 每日新聞.md` already exists, ask whether to
  overwrite or merge before clobbering it. **When merging new content**, also
  complete these before declaring done:
  - [ ] Update frontmatter `source_count` and `story_count`
  - [ ] Update `> [!abstract]` to mention the new stories added
  - [ ] Add new story nodes to the 總圖 `flowchart TD` in `## 🧭 當日總覽`
- **Non-`.md` links keep the extension** (`[[file.txt]]`), per vault convention.

## Reference files

- `references/digest-format.md` — output template, link-presentation rules,
  Mermaid house style. **Load at STEP 6**, not before.
- `$SKILL_DIR/scripts/collect_sources.py` — the single-day collector (STEP 1).
- `$SKILL_DIR/scripts/collect_history.py` — the cross-date history collector for
  evolving stories (STEP 3.5): keyword + date-window search over the whole vault
  (minus `--exclude`, same default as collect_sources); `--folders` to restrict.
- `$SKILL_DIR/scripts/cot_mermaid.py` — renders CoT node **content** (JSON) →
  coloured Mermaid with the FIXED role→colour scheme (STEP 4/6). Chain
  (`flowchart LR`, positional roles) or web (`flowchart TD`, explicit roles).
  Also auto-escapes `(` `)` → `「」` (Obsidian-Mermaid safe). Use it so every
  CoT diagram is byte-consistent; subagents emit node content, the main agent
  renders. See STEP 6 for the concrete calling pattern.
- `scripts/test_*.py` — tests. Run with `python3 -B <file>` (the `-B` keeps
  `__pycache__` from being written — nested dirs violate the skill-folder rule).
