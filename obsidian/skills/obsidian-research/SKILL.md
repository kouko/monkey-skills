---
name: obsidian-research
description: Research a topic on the web (English + Japanese, plus the topic's own language when it has one) from several angles, verify the key claims, and save a human-readable research note with a TOC into the Obsidian vault's research/ folder. Use for "research X into a note in my vault" / 「研究一下 X 寫成筆記」/「X を調べてノートにまとめて」. Do NOT use to fill wiki/ gaps (wiki-auto-research), for a report saved outside the vault, or for a chat-only answer. 研究ノート・調査。研究筆記・調查。
---

# Obsidian Research

Research a topic the user names and save one note a person can read end to end: conclusion first, a table of contents, chapters shaped by the topic, cited and checked claims, and next actions.

**Self-contained**: uses only the host's own tools (`WebSearch`, `WebFetch`, subagents) and skills in this plugin. Never invoke a skill from another plugin — this skill must work when only `obsidian` is installed.

Frameworks are used at four layers; [references/frameworks.md](references/frameworks.md) lists them:

| Layer | Job | When |
|---|---|---|
| 0 Triage | Pick the note's structure from the question type | Step 1 |
| 1 Skeleton | A step sequence that orders the chapters — a suggestion, not a template | Step 1, Step 5 |
| 2 In-chapter tools | Matrices and checklists that break down one chapter's issue | Step 5 |
| 3 Principles and checks | Rules that hold throughout, plus checks run on the whole note | Steps 2, 4, 5, 6 |

## Pre-flight

1. **Vault root** = the nearest directory containing `.obsidian/`, starting from the current directory and walking up. If none is found, ask the user for the vault path.
2. **Web tools**: check that the host's web search tool (`WebSearch` in Claude Code) is in this session's tool list.
   - Missing and the user gave material → continue with that material only; say so in the chat reply and in the note's limitations.
   - Missing and no material → stop: "obsidian-research needs the WebSearch tool, which this session does not have (e.g. a Cowork sandbox). Run it from Claude Code CLI, or give me the sources to work from."
3. `mkdir -p <vault-root>/research`.

## Step 1 — Scope and structure

1. Restate the core question and what is out of scope in one or two lines. Ask the user only when the topic has two readings that would produce different notes; otherwise pick the plain reading and state it.
2. **Triage (layer 0)**: match the question type in the frameworks reference's question-type table. If a skeleton fits, use it to order the chapters; if none fits, order chapters by the topic's own dimensions — the aspects a reader would ask about (e.g. for a hobby or product topic: what it is → how people use it → costs → problems → where it is heading).
3. **Source languages**:

| Topic | Languages searched | Primary |
|---|---|---|
| Default (no language leaning) | English + Japanese | — (both searched in full) |
| Leans to one language — culture, history, or a specific country's market, law, society, or companies | English + Japanese + that language | That language: most queries and most cited sources in it |
| User names languages | English + Japanese + the named ones | As the user says |

English or Japanese is dropped only when the user explicitly excludes it.

Examples: 台灣半導體補助政策 → 繁中 primary + EN + JA. 江戸時代の貨幣制度 → JA primary + EN. US 401(k) rules → EN primary + JA.

## Step 2 — Expand into angles

1. Split the question into 3–6 distinct research angles — each angle is one sub-question researched on its own — written freely for this topic.
2. **Gap check (on by default)**: walk the frameworks reference's blind-spot list and the tools named for this question type in its question-type table. Add an angle only for a cell that is relevant and uncovered. Finding no gap is a valid result — do not pad.
3. Tell the user, one line each: the angles, the skeleton (or "by topic dimensions"), the languages. Then continue without waiting; the user may interrupt to change them.

## Step 3 — Research each angle

- **User material** (URLs, files, a report produced by another tool): read it first. The URLs it cites join the source pool; only sources the note actually cites get a number.
- **Web search** runs by default, even when the user gave material. The user can narrow it ("only verify key claims", "fill gaps only") or turn it off ("use only my material") — follow their scope. An angle the material already covers well needs no new search; Step 4 still runs.
- **Dispatch one subagent per angle, all in the same message.** Each gets: the question, its angle, the languages (primary first), and these instructions — write queries natively in each language (not translations of the English query); read 2–4 pages with `WebFetch` (or this plugin's `defuddle` skill when its CLI is installed); return each claim with a supporting quote, fact/opinion tag, and the source's title, URL, publisher, language, and date; do not dispatch further subagents. If subagents are unavailable, follow the same instructions yourself, one angle after another, and say so in the method section.
- If a required language yields no usable source, record it for the limitations section instead of dropping it silently.
- Stop searching an angle when new sources stop changing its conclusions.

**Merge**: remove duplicate URLs. Sources from the same origin — a syndicated press release, several articles quoting one report, several works by the same author or organization — count as one source when judging independence (Step 4); each still gets its own source-list entry.

## Step 4 — Verify key claims

1. Pick the claims the conclusion depends on (usually 8–10).
2. For each **fact** claim, dispatch a fresh subagent (all in one message; one subagent may take 2–3 related claims) whose job is to refute it: search for counter-evidence, find the original source, check whether it is outdated. It returns stands / refuted / uncertain with evidence and a URL. For each **opinion** claim, only confirm the cited source actually says it. If subagents are unavailable, run each refutation check yourself, one claim after another, and say so in the method section.
3. Assign confidence:
   - **High** — at least two independent sources and it survived the refutation check.
   - **Medium** — one good source, or the check was inconclusive.
   - **Low** — weak or single secondary source.
   - A source whose publisher or funder benefits from the result, or whose sample is non-random or undisclosed, caps the claim at **Medium** unless an independent source agrees.
   - **Refuted / outdated** — moves to the disagreements section; never silently dropped.
4. Write every subagent's full report from Steps 3 and 4 into one scratch file outside the vault — the **source packet** Step 6 checks against.

## Step 5 — Write the note

Write in the **user's conversation language**, whatever the source languages were. Quotes may stay in the original language with a translation. Match the style of the vault's recent research notes: open the two or three newest files in `research/` and follow their heading style and tone (if `research/` is empty, use plain numbered headings); write plainly, define terms on first use.

**Reading order differs from research order**: the conclusion and TOC come first; the chapters after them follow the skeleton from Step 1 (or the topic's dimensions). Drop skeleton steps that have nothing to say — never write an empty chapter. Inside a chapter, use a layer-2 tool when it makes the material clearer (options × criteria → a comparison table; causes → a fishbone-style breakdown).

The note must pass these checkpoints (layer 3 — they play the role a reporting checklist plays in science writing):

1. **Frontmatter**: follow the vault's frontmatter convention when its CLAUDE.md defines one; otherwise use `title`, `type: research`, `date`, `tags`, `status: completed`. Always add `source_count: <n>` and `source_languages: [en, ja, …]`. `related_notes` only for notes confirmed to exist in the vault.
2. **Conclusion first**: a one-line `> 📌` bottom line, then one paragraph of 2–3 sentences. Anything longer belongs in a chapter.
3. **Table of contents** right after the summary: one line per `##` section except the TOC itself, written as `[[#<exact heading text>|<label>]]`. After writing, check that every link target matches a heading character for character.
4. **Chapters follow the skeleton or the topic's dimensions**. A comparison gets a comparison table.
5. **Citations**: every non-obvious claim cites a numbered source `[n]`; key claims show their confidence.
6. **Disagreements and open questions**: where sources disagree, which claims were refuted or outdated, and what remains unresolved (omit only if none).
7. **Method and limitations**: the angles, the skeleton used, how many claims were checked and refuted, the Step 6 counts copied from its table (never claim a check that has no table), languages searched and any that yielded nothing, source bias, time sensitivity.
8. **Next actions**: concrete recommendations for the reader, most important first. When the note recommends something, add the key assumptions it rests on and a pre-mortem line (if this turns out wrong, the most likely reason).
9. **Source list**: a numbered list matching the `[n]` citations — `1. Title — publisher — URL — language — accessed YYYY-MM-DD`, one URL per entry (a mirror may follow as `; mirror: URL`).

Use `obsidian-markdown` for Obsidian syntax (callouts, wikilinks). Link other vault notes only if they exist.

[references/research-note-example.md](references/research-note-example.md) shows the exact form of the frontmatter, TOC, a claim with confidence, the method section, and source entries. It is not a structure to copy.

Save to `<vault-root>/research/YYYY-MM-DD <title>.md`. In the filename, replace `/` and `:` with full-width `／` and `：`. If that file exists, append ` (2)`, ` (3)`, … — never overwrite.

## Step 6 — Check citations (required)

Dispatch one fresh subagent (a cheaper model when the host lets you choose) with the note path and the source packet path. It must:

1. List every checkable item in the note: each number, date, percentage, rank, attribution ("X showed…"), causal claim, and quote, with its line and `[n]`.
2. Tier 1, text only: find the supporting passage in the packet under the same URL as the item's `[n]`. For a causal claim, the passage must state the cause, not only the dates.
3. Tier 2, only for items that fail tier 1: open the cited URL and check there.
4. Return a table — item, line, `[n]`, verdict, fix — with counts: items checked, passed, failed.

Apply every fix to the saved note (correct, re-cite, or remove), keep the source list and `source_count` in step, run tier 1 again on the items you changed, then fill checkpoint 7's counts from the table. If subagents are unavailable, run tiers 1–2 yourself and write "self-checked" in the method section.

## Step 7 — Report

- Reply in chat with: the file path, the one-line conclusion, source counts per language, claims checked / refuted, citation-check counts, and anything skipped (a language with no results, web search unavailable, subagents unavailable).

## Related skills

- `wiki-auto-research` scans `wiki/` for open questions and writes gap-filling notes; this skill researches a topic the user names. Notes written here carry no wiki fields. `wiki-ingest` may still ingest `research/` later — that is the user's choice.
- After saving, the user may ask for a diagram (`obsidian-mermaid-visualizer`) or a canvas (`obsidian-canvas-creator`); do not add those unasked.
