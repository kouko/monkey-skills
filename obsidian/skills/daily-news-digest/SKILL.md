---
name: daily-news-digest
description: |
  Compile one day's vault notes into a two-tier daily digest — clustered time-sensitive stories + evergreen knowledge links — at news/YYYY-MM-DD. Use for '整理今天的新聞', '每日新聞', 'daily news digest', rounding up a day's content, or summarizing what you consumed/read today.
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
| **📰 Time-Sensitive News** | Dated events: individual stocks/earnings/oil/rates/central banks, conflict/elections/policy/sanctions, launches/new models/M&A | Clustered + synthesized into rewritten stories, then grouped under thematic category headings (the heart of the skill) |
| **🧠 Knowledge & Perspectives** | Substantive but not date-driven: op-eds/commentary, tool reviews/benchmarks, tutorials/walkthroughs, investing strategy/methodology, long-form deep analysis | Categorized short-labeled links + one-line takeaway each (NOT rewritten) |
| **Research Appendix / drop** | The user's own research / analysis notes → research appendix (links only). Pure filler with no takeaway → drop. | Links only |

> [!note] Output section names follow the user's language
> The bucket labels above are English shorthand used throughout this document.
> Translate to the user's language when writing the actual digest sections (e.g.
> "Time-Sensitive News" → 「時效新聞」, "Knowledge & Perspectives" → 「知識與觀點」,
> "Source Index" → 「來源索引」in Traditional Chinese). The same applies to all
> section headings called out in this skill.

> [!tip] The litmus test for tier 1 vs tier 2
> Ask: "If I read this six months from now, would the **date** matter?" A market
> move or launch is stale in a week → Time-Sensitive News. A tutorial or a
> thinking-model essay is just as useful next year → Knowledge & Perspectives.
> Both stay in the digest; only the **treatment** differs (synthesized story vs
> indexed link).

Borderline event-driven explainers lean on whether a **specific dated event**
drives the piece. When genuinely unsure between the two tiers, prefer
Knowledge & Perspectives (a link is cheaper than a forced story).

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
   If the metadata header is absent (cold-start or direct invocation without the
   plugin runtime), locate the scripts automatically:
   ```bash
   SKILL_DIR=$(find "$HOME/.claude/plugins/cache" -type d -name "daily-news-digest" 2>/dev/null | sort -r | head -1)
   ```
   (`sort -r` picks the highest version number if multiple cache versions exist.)

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

For **each** `candidates` entry, assign one of: **Time-Sensitive News** /
**Knowledge & Perspectives** / **Research Appendix** (the user's own
research/analysis — goes to the appendix, not the body) / **drop**. Use `tags` +
`snippet` as the primary signal; `folder` is a hint, not a rule (e.g. a
`research/`- or `notes/`-style folder leans Research Appendix, a
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
**anchored-open** taxonomy below (**anchored-open**: pick from the fixed list;
only create a new heading when nothing fits, and record the reason in the
digest's frontmatter `notes` field so the taxonomy can be reviewed). There is
**no single "Time-Sensitive News" umbrella heading**; the news is categorized the same way Knowledge & Perspectives
is. **Story headings carry no number** — `### <story title>`. The Source Index
references each story by its short title, not a number.

**Time-Sensitive News category anchor list** — pick 2–4 that fit the day's
stories. Write the actual heading in the **user's language** (e.g. 「國際・地緣
政治」in Traditional Chinese, "International & Geopolitics" in English):

| Concept | Typical stories |
|---|---|
| International & Geopolitics | conflict, diplomacy, sanctions, elections, international orgs |
| Financial Markets & Macro | equities, FX, rates, inflation, central banks, bonds |
| AI & Technology | model releases, AI products, tech platforms, semiconductors |
| Business & Industry | earnings, M&A, corporate strategy, industry dynamics |
| Energy & Commodities | oil/gas prices, mining, commodities, supply chains |
| Policy & Regulation | legislation, regulatory action, tariffs, government policy |

If none of the six fits, create a new heading — but add a one-line comment in
the digest's frontmatter `notes` field explaining why, so the taxonomy can be
reviewed and extended deliberately.

### STEP 3.5 — For evolving stories, pull history and build an Event Arc

Some stories are **not one-off events but ongoing arcs** — a geopolitical
conflict, an oil-price move, a rate/inflation cycle, a stock-index trajectory,
an earnings arc. For these, reconstruct the progression so the reader sees the
*trend*, not just today's snapshot.

> [!important] Sweep EVERY story, across ALL categories
> This is **not just for the headline geopolitical story**. Walk your full story
> list and flag every multi-week arc. Market/macro stories are the most common
> miss — a stock index hitting a record is an arc (the rebound only means
> something against the prior correction); long-end yields, inflation prints,
> and an FX cycle are all arcs. A 📈 Financial Markets & Macro category with zero
> Event Arc on a volatile day is usually a miss, not a clean day.

**What SKIPS Event Arc:**
- **One-off events** — a product launch, a regulatory action, an M&A headline,
  a single earnings beat. There is no multi-week trajectory to draw.
- **Forward-looking single events** — "this week's central-bank decision" is an
  upcoming datapoint, not a progression. (Its *backdrop* — the rate/yield arc —
  may already be covered by a sibling story's Event Arc; don't duplicate it.)

1. **Pull prior notes** with the history collector — it greps `references/` +
   `investing/` for earlier dated notes on the same entity/keywords:

   ```bash
   python3 "$SKILL_DIR/scripts/collect_history.py" \
     "<keyword1,OR,keyword2>" . --since <YYYY-MM-DD> --until <digest date − 1>
   ```

   `--until` = the day **before** the digest date (today's notes are already in
   the story). It returns a date-sorted timeline of {date, wikilink, snippet}.

2. **Extract the trajectory** — read a few milestone notes for the real numbers
   (e.g. oil 104 → 90 → 80 across the weeks), then write a short progression
   sub-section: a trend paragraph + (optionally) a visual. **Give the `####`
   heading a dynamic, content-specific title** — not a fixed "Event Arc" label.
   Name the actual arc (e.g. "Oil: 3-month slide from peak 104 to 80",
   "Nikkei rollercoaster: new high → correction → new high",
   "Rate path: from deflation escape to 31-year high"). Use a **`timeline`**
   Mermaid for milestone chronology, or an **`xychart`** line for a clean
   numeric series. **Proportionality**: if the story already carries a mechanism
   diagram (a flowchart/graph), a **prose-only** trend paragraph is enough —
   don't stack 3 charts in one category.
3. **Cross-reference the user's own `investing/` analyses** when they exist —
   surfacing "you predicted this in March" is high-value (per vault CLAUDE.md).
4. **Cite the history minimally.** If you cross-referenced an `investing/`
   analysis, keep a short inline link to it at the paragraph end (e.g.
   `→ see [[…|Mar oil-price analysis]]`). **Do NOT** add generic boilerplate
   like "synthesized from recent references/ notes" — it repeats across every
   story and adds no information; the Event Arc already implies prior-note
   synthesis. Never imply numbers you didn't read, but a bare
   references/-only attribution can be dropped.

**Event Arc sweep table — fill this for EVERY story before moving to STEP 4.**
Do not skip; leaving a row blank is itself a decision that must be made explicitly:

| # | Story title | Multi-week arc? | Action |
|---|---|---|---|
| 1 | `<story 1>` | Yes / No | `collect_history(...)` / skip |
| 2 | `<story 2>` | Yes / No | `collect_history(...)` / skip |
| … | | | |

> [!warning] Red flags — stop and re-examine if you see any of these:
> - A 📈 Financial Markets & Macro category with **"No"** across every row on a
>   volatile day
> - Story subject is an FX rate, stock index, inflation print, or bond yield
>   → almost certainly an arc even if today's is the first note you've collected
> - Story title contains momentum/continuation markers (e.g. "new high",
>   "consecutive", "day N", "ongoing", "breakthrough") → arc by definition

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
>   narrative: ["<para 1>", "<para 2>"],       // inline links as [[stem|short label]]
>   table?: "<markdown table or null>",
>   progression?: { title, milestones:[{date, text}], note },  // Event Arc, evolving only
>   sources: [{stem, label}] }                // for inline links + Source Index
> ```
> The CoT `nodes` carry only content; `$SKILL_DIR/scripts/cot_mermaid.py` applies the fixed
> colours/style. The main agent owns dedup, the day-level overview diagram, and STEP 8 verify.

For each cluster, **rewrite an integrated story** — you are the editor merging a
wire feed, not summarizing notes one by one:

1. **Read the actual source notes**, not just the manifest snippets — open every
   note in the cluster (`references/`) for the real facts, numbers, and quotes.
2. **Integrate and cross-reference.** Reconcile numbers (if two sources cite WTI
   at 80.3 vs 81, say so), combine the timeline, assemble the fullest picture.
   Where sources disagree on interpretation, **surface the disagreement** — that
   tension is signal.
3. **Write a one-line TL;DR — the bottom-line takeaway / so-what**, NOT a
   restating of the causal steps (the COT diagram below carries those). Then a
   **COT (Chain-of-Thought) mini-diagram** directly (a compact `flowchart LR` of the story's causal
   chain (**3–5 hops as the story warrants** — trigger → mechanism → result →
   conclusion is a natural arc, collapse or extend as needed) — **no caption
   label before it**. Each node = title + ━━━━ + a **left-aligned bullet list of
   3–5 `• ` facts** (`<div style='text-align:left'>`; not prose — it renders
   unevenly). **Colour every node by role with the fixed scheme** (trigger green /
   mechanism purple / result orange / conclusion cyan — see digest-format §COT),
   consistent across all CoT diagrams. So TL;DR = conclusion, COT diagram =
   steps, narrative = detail — three complementary layers. Then **1–3 narrative
   paragraphs** in the user's language. **Segment for readability** — break a
   long block into short paragraphs (≈ 2–4 sentences each, one idea per
   paragraph: framework / terms / market reaction / disagreement…). Never ship a
   5+ sentence wall of text; a blank line between ideas is the cheapest
   readability win.
4. **Add a visual only when it earns its place** (table for comparable data,
   Mermaid for a causal chain / one-cause-many-effects / timeline).

### STEP 5 — Index the Knowledge & Perspectives tier

(On a **heavy day**, this whole tier can be **one more subagent** — see STEP 4's
execution model — returning each sub-category's promoted summaries + CoT node
content; the main agent renders + assembles.)

Group tier-2 items under sub-headings using the **anchored-open** taxonomy
below — pick 2–4 that fit the day's knowledge content. Write the actual
sub-heading in the **user's language** (e.g. 「投資策略・市場觀點」in Traditional
Chinese, "Investing Strategy & Market Views" in English):

| Concept | Typical content |
|---|---|
| Investing Strategy & Market Views | investing frameworks, stock analysis, market commentary, strategy |
| AI, Development & Tools | LLM applications, dev tools, engineering practices, AI research |
| Tech Products & Trends | product reviews, tech launches, hardware, platform trends |
| Business, Strategy & Thinking | business models, strategy frameworks, mental models, management |
| Design & Creativity | UI/UX, industrial design, visual design, creative tools |

If none of the five fits, create a new sub-heading and add a one-line comment
in `notes` (same rule as the news tier). In **each** sub-category:

1. **Promote ≥1 important piece to a 2–3 sentence summary** in a `> [!example]`
   callout. The callout title is **the piece's short title only** (no prefix);
   end with a `> Source: [[<stem>|<short label>]]` line, then a **CoT mini-diagram**
   (same style as the news COT: `flowchart LR`, bullet-list nodes, 3–5 hops) that
   visualises that piece's argument logic.
2. **When ≥2 items in the category cover the same sub-topic or debate, integrate
   them into a short analysis** instead of listing them separately — a
   `**Synthesis — <topic>**` sub-block (in user's language; 2–3 sentences) that
   reconciles the pieces, names the agreement/tension, and links each contributing
   source inline with a short label, then its own **CoT mini-diagram** (two sides
   → consensus → divergence, etc.). (e.g. a bull-case and a bear-case on the same
   stock → one bull-vs-bear synthesis.) This is the knowledge-tier analogue of
   STEP 3–4 clustering.
3. Then a **`**Related Articles**`** sub-label (in user's language), followed by
   the *remaining* unrelated items as one-liners:
   `- [[<stem>|<short label>]] — <core argument or method, one sentence>`
   (these are link-only — **no CoT diagram**). The sub-label keeps the section
   reading smoothly (summary+chart → synthesis+chart → link list).

Only force integration where relatedness is real; disparate items stay as a
curated one-liner list. The value is a categorized index with synthesis where it
earns its place.

### STEP 6 — Write the digest

**READ `_templates/digest-format.md` first** — it holds the output template, the
link-presentation rules, and the Mermaid house style. (If the file is missing or
unreadable, fall back to: standard YAML frontmatter with title/date/type/tags/status,
COT colour scheme from §STEP 4 — trigger green / mechanism purple / result orange /
conclusion cyan — and the link rules in §Hard rules below.) Then create the digest file
at `news/<YYYY-MM-DD> <title>.md` (title in the user's language; e.g.
`news/2026-07-01 每日新聞.md` in Traditional Chinese). **Order at the top:
`## Table of Contents`** (in user's language, right under the title), then a
merged **`## 🧭 Day Overview`** section (in user's language). The Table of
Contents is in-page `[[#full heading|short name]]` anchor links to each story
(grouped by news category) plus Knowledge & Perspectives / Other Notes / Source
Index / Appendix. The Day Overview section merges the `> [!abstract]` overview
text **and** the day-level COT `flowchart TD` overview diagram (causal web of the
day's stories). **Render every CoT diagram — the overview diagram and each story
/ knowledge mini-diagram — through `$SKILL_DIR/scripts/cot_mermaid.py`** (feed it
node content JSON), so the fixed role-colours and style are identical everywhere;
don't hand-write the `style` lines. Concrete calling pattern:

```bash
# Per-story chain (flowchart LR) — roles assigned by position (first=trigger, last=concl):
# Node titles and bullets should be in the user's language.
cat > /tmp/cot_chain.json << 'COTJSON'
{"type":"chain","nodes":[
  {"title":"Trigger node","bullets":["fact 1","fact 2","fact 3"]},
  {"title":"Mechanism node","bullets":["reason 1","reason 2"]},
  {"title":"Result node","bullets":["impact 1","impact 2"]},
  {"title":"Conclusion node","bullets":["takeaway 1","takeaway 2"]}
]}
COTJSON
python3 "$SKILL_DIR/scripts/cot_mermaid.py" /tmp/cot_chain.json

# Day-level overview web (flowchart TD) — each node needs explicit "role":
cat > /tmp/cot_web.json << 'COTJSON'
{"type":"web",
 "nodes":[
   {"id":"A","title":"Story 1","bullets":["key point"],"role":"trigger"},
   {"id":"B","title":"Story 2","bullets":["key point"],"role":"mech"},
   {"id":"C","title":"Shared result","bullets":["key point"],"role":"result"},
   {"id":"D","title":"Implication","bullets":["conclusion"],"role":"concl"}
 ],
 "edges":[
   {"from":"A","to":"C","label":"drives"},
   {"from":"B","to":"C","label":"accelerates"},
   {"from":"C","to":"D","label":"leads to"}
 ]}
COTJSON
python3 "$SKILL_DIR/scripts/cot_mermaid.py" /tmp/cot_web.json
```

The script writes a ready-to-paste ` ```mermaid ``` ` block to stdout.
`(` `)` in node titles are automatically converted to `「」` (Obsidian-Mermaid safe).

Follow the vault's Obsidian conventions (complete frontmatter, callouts) and the
digest-format link rules: **embed short-labelled jump-links inline in the body
(anchored on words already in the prose), AND also collect every source into a
`## Source Index` (in user's language) at the end as a standard full-filename
list under per-story `###` sub-headings** (see §Hard rules on why raw long links
are banned in narrative).

### STEP 7 — Appendices & report

- **Research appendix**: each item you triaged as **Research Appendix** as a
  short-labeled link + one line.
- **Handwritten appendix**: if `daily/<YYYY-MM-DD>.md` exists, surface real
  handwritten content from its `## Note` section; skip silently if empty.
- **Report**: digest path, story count (and sources merged), tier-2 item count,
  kept-vs-dropped one-liner, and anything borderline to double-check.

## Hard rules

> [!warning] references/ is the immutable Sources layer
> NEVER edit, rename, or add wikilinks **into** any `references/` note. This skill
> only **reads** them and links **from** the new `news/` note **to** them — the
> vault's three-layer wiki contract (`wiki/SCHEMA.md`); the Sources layer is
> immutable.

> [!important] Use the wikilink stem, not the title — and keep labels short
> A source note's frontmatter `title` is NOT its filename — the vault's
> YouTube-summary workflow strips `&`, `()`, ` (summary)` etc. from the filename.
> Linking `[[<title>]]` produces a **broken link**. ALWAYS build the target from
> the collector's `wikilink` field (= the real stem), and give it a short display
> label: `[[<stem>|<short label>]]`. Never inline a **bare long** wikilink. Do
> embed **jump-links inline by wrapping an existing prose phrase** (display text =
> the words already in the sentence), NOT a `(short label)` parenthetical — so
> the reader hops to a source while reading. AND **also** list every source in the
> end `## Source Index` (in user's language) as a full-filename list (see
> `_templates/digest-format.md` for the inline-vs-index split).
>
> **Beware truncated triage views.** When you print the manifest to eyeball
> candidates, the `title` is often clipped (`… (summary)` cut off, long titles
> shortened). NEVER copy a link target from that printed/truncated view — go back
> to the manifest JSON and copy the full `wikilink` field. (Real failure on
> 2026-06-16: three misc links built from clipped titles broke until rebuilt from
> the stem.)

> [!important] Run self-checks after writing (COT completeness + link resolution + Mermaid syntax)
> After writing the digest, run **three checks** before declaring done.
>
> **① COT completeness** — every time-sensitive story must have a `flowchart LR`.
> Count story headings in the news section and compare to COT diagram count:
> ```bash
> python3 - "news/<YYYY-MM-DD> <digest title>.md" <<'PY'
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
> **② Link resolution** — every wikilink must resolve to a real file:
> ```bash
> python3 - "news/<YYYY-MM-DD> <digest title>.md" <<'PY'
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
> **③ Mermaid syntax** — parse every mermaid block through mermaid-cli (requires `npx`):
> ```bash
> bash "$SKILL_DIR/scripts/validate.sh" "news/<YYYY-MM-DD> <digest title>.md"
> ```
> FAIL = real syntax error (fix before finishing). WARN = literal `"` in rendered
> text (likely a wrongly-quoted title/label). PASS = parses in mermaid-cli —
> note: cli is more lenient than Obsidian, so CJK-heavy diagrams should also be
> verified in Obsidian directly.
> This check is most valuable for hand-written diagrams (`timeline`, `xychart`
> in Event Arc); `cot_mermaid.py`-generated diagrams rarely fail here.

> [!danger] Synthesis failure modes — NEVER do these
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
- **One file per day.** If `news/<date> <title>.md` already exists, ask whether
  to overwrite or merge before clobbering it. **When merging new content**, also
  complete these before declaring done:
  - [ ] Update frontmatter `source_count` and `story_count`
  - [ ] Update `> [!abstract]` to mention the new stories added
  - [ ] Add new story nodes to the overview `flowchart TD` in the Day Overview section
- **Non-`.md` links keep the extension** (`[[file.txt]]`), per vault convention.

## Reference files

- `_templates/digest-format.md` — output template, link-presentation rules,
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
