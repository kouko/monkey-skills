# Field-value microstructure — brief

> **Phase**: brainstorming output (`brainstorming` → `writing-plans` handoff)
> **Date**: 2026-08-19
> **Author**: agent (kouko in the loop)

## Design-side on-ramp

fired: rows 1 — standing direct (KICKOFF-DEFAULTS.md)

## Problem

When kouko opens a loom plan or spec to approve or redirect it, the document's structure is rich but every field value and every long paragraph is a single unbroken run of English prose, so the reader must parse a 1,000-character block to extract one decision. The rule that should bound this already exists — plan-format.md's `one-assertion unit of work` — but it is judgment-shaped, so a writer who produces a 1,452-character Description believes in good faith that it is one assertion.

## Users

- **kouko, reading a plan at PR-review time or when opening the file directly** — reads once, sequentially, needs the task's action in the first line, not after a 200-word paragraph. The rendered progress card (`plan_card.py`) is the day-to-day surface, but the `.md` is what gets read at review and on GitHub.
- **`plan-document-reviewer` (agent, verdict-only)** — grades Description/GREEN prose content (Checks 7, 16, 17, 18); an unbounded field body makes "names an observable condition" a judgment over a wall of text.
- **`implementer` subagents (agent)** — receive the `Description` **verbatim** in the dispatch packet (`plan-format.md:257`, `subagent-driven-development/SKILL.md:103`); every extra clause rides every dispatch.
- **`docs-reviewer` (agent, verdict-only)** — reviews changed `.md` whole; currently has no dimension for paragraph form.

## Smallest End State

A writer can no longer produce an unbounded field value or an unbounded long paragraph without either splitting it or declaring, in the artifact, that the paragraph is a reasoning chain — and a mechanical check, not a reviewer's judgment, decides whether that duty was met. The check runs at plan-authoring time and in the docs/code review path. Success criterion: on the 5 current plans and 7 post-#699 specs, every violation is either fixed or carries an explicit declaration. Non-criterion: we do NOT measure whether paragraphs got shorter on average — the median is not the target, the tail is.

- BI-1 — In a plan task's `Description`, `Acceptance.RED` and `Acceptance.GREEN`, no single prose unit exceeds 300 characters — a unit being the field's own first line, or one nested bullet's text folded across however many physical lines it wraps to; everything that does not fit becomes another bullet or a table row. (Amended three times, all at plan time, all recorded here rather than patched into the plan. 1: "exactly one sentence" was falsified — 33 of 142 `RED`/`GREEN` first lines carry the `Fails today because ...` grounding clause `plan-format.md` itself teaches. 2: sentence counting was abandoned after two review rounds proved regex cannot do it — occurrence counting false-positived on `0.89.0` / `e.g.` / `i.e.` / ellipsis, and the boundary heuristic that replaced it false-negatived on a lowercase-initial sentence. 3: the cap moved from "the first line" to "any prose unit", because capping only the first line let a one-word decoy bullet carry unlimited indented prose beneath it. Each amendment made the rule shorter; this wording states one number and one idea, and subsumes all three.)
- BI-2 — A plan header's `Goal:` value admits no nested body, because `plan_card.py` folds any indented content into the card's single `goal:` line and ships the mangled result to the reader. (Amended twice, both at plan time. First: "one sentence" was dropped from the mechanical check — BI-1 had already abandoned sentence counting after two review rounds proved regex cannot do it, and re-deriving it here would have repeated those failures in a second function. Second: the 300-character ceiling was dropped too. `plan-format.md:32-36` freezes `Goal:` — "transcribed from the brief's Smallest End State at plan time... never edited afterward" — and `check_goal` forbids splitting it, so an existing over-cap `Goal:` had no legal resolution: two independent reviewers found real fact loss in the five compressions attempted, and re-compressing the two worst to carry both the missing facts and 300 characters produced 320 and 390. The ceiling had no justification of its own beyond matching BI-1's number, while the no-nested-body half carries the stated reason. The half with a reason survives.)
- BI-3 — A brief or spec paragraph longer than the stated threshold, inside a named prose section, is either split into bullets/table or carries an inline narrative declaration on its own line.
- BI-4 — One mechanical checker decides BI-1/BI-2/BI-3 compliance, exits non-zero on violation, and is proven unable to pass by matching nothing.
- BI-5 — `plan_card.py` renders a nested-bullet or table field body without silently corrupting it, in both the card and `--detail T<N>`.
- BI-6 — The narrative-declaration escape is written as a positive, declarable duty (`fill-or-declare`), never as a category the checker must classify.

## Current State Evidence

- **Forward**: `loom-code/scripts/plan_card.py:196` `_bullet_value` joins a field's continuation lines with `" ".join(...)`, so a nested-bullet `Description` renders as `description: <sentence> - first bullet - second bullet` in `--detail`; `plan_card.py:127` `_header_value` does the same fold for `Goal:` and `Stage:`, and that value ships to the user's card (`loom-code/hooks/family-relay.md:73` pins it as "one line, verbatim").
- **Reverse**: `plan-format.md:96-136` is the SSOT the narrowing must be written into; it is restated by `loom-code/skills/writing-plans/README.md:34-42` and its `.ja` / `.zh-TW` mirrors, and graded by `plan-document-reviewer-prompt.md:35` (Check 3), `:39` (Check 7), `:48` (Check 16), `:49` (Check 17), `:50` (Check 18).
- **Error**: `plan_card.py:426-436` `build_detail` matches Acceptance sub-items with `re.match(r"^\s*-\s+(.*?)\s*$", raw)` and has an `elif items:` branch with no `else`, so a markdown table under `Acceptance` is silently dropped rather than raising.
- **Data**: `Description` travels verbatim into implementer dispatch packets (`plan-format.md:257`, `subagent-driven-development/SKILL.md:103`), so its shape is payload, not only presentation.
- **Boundary**: `[FRAGILE]` `scripts/check_files_touched.py:129-146` `_is_continuation_line` excludes `- `-prefixed lines by design, and `loom-code/scripts/check_scenario_coverage.py:116-117` `_BRIEF_ITEM_LINE` requires `(.+)$` on the colon's own line — both silently drop data if their fields gain nested bodies, so this change must not touch `Files touched` or `Brief item covered`.
- **Evidence paths**:
  - `loom-code/scripts/plan_card.py:111,127,146,174,196,205,239,274,280,332,335,420,423,426-436,453,501,528`
  - `loom-code/skills/writing-plans/references/plan-format.md:31-56,74-91,96-136,253-263`
  - `loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md:35,39,48,49,50`
  - `loom-code/hooks/family-relay.md:71-92,93-99`
  - `loom-code/skills/subagent-driven-development/SKILL.md:103,113-117`
  - `scripts/check_files_touched.py:100,103,129-146`
  - `loom-code/scripts/check_scenario_coverage.py:116-117,128,140,170`
  - `loom-code/scripts/check_open_questions.py:96,99,121,250-256`
  - `loom-code/scripts/backlog_index.py:233-246`
  - `loom-code/scripts/adjudication_split.py:9-11,56,126,154`
  - `docs/loom/backlog/2026-08-18-remaining-container-rules-callout-toc-paragraph-net-plan-tables.md`
  - `docs/loom/backlog/2026-08-13-a-widened-field-grammar-has-no-mechanical-consumer-enumeration.md`
  - `docs/loom/dogfood/2026-08-17-artifact-table-routing-dogfood.md:74`

## Decision

We replace the judgment-shaped `one-assertion` rule with a positional rule the machine can check, and extend it to the one slice of brief prose that is structurally the same defect as the plan-field one.

- The rule constrains WHERE a field's overflow goes, not how long the document is. Content moves into bullets and tables; nothing is deleted.
- We will NOT ask any checker to classify a paragraph as narrative-or-not. That judgement stays with the author, who declares it inline, and with the reviewer, who can point at the declaration.
- We will NOT cap the whole document, `Description`'s total size, or the median paragraph. Measured evidence says the corpus does not pad, so a size cap treats the wrong disease.
- The chosen thresholds are the falsifiable half of this design; the structural rule — overflow becomes a bullet or a table — is the load-bearing half and survives if the numbers are wrong.

- BI-7 — `plan-format.md` states the field-value grammar as a positional rule with a worked before/after example, replacing `one-assertion` as the operative wording.

## Out of Scope

- **`## Open Questions` entry grammar** — `check_open_questions.py:250-256` already ignores continuation lines, so a nested body neither breaks nor helps; `.claude/workflows/principles-replay-matrix.js:278` also writes these entries, so narrowing them costs a producer change for no measured gain.
- **`Files touched` and `Brief item covered`** — both have parsers that silently drop nested content (`check_files_touched.py:129`, `check_scenario_coverage.py:116`); widening them is a separate arc with its own consumer work.
- **Genuinely narrative paragraphs (the measured (N) class, 40% of long paragraphs)** — no container rule reaches a reasoning chain; the remedy is the per-unit CoT diagram already decided in `docs/loom/backlog/2026-08-18-per-unit-cot-diagram-in-the-adjudication-view.md`, which lives in the view, not the artifact.
- **Callout roles, TOC, plan-level summary tables, a general 2–4-sentence paragraph net** — parked in `docs/loom/backlog/2026-08-18-remaining-container-rules-callout-toc-paragraph-net-plan-tables.md`; that entry's own "Do not stack rules blind" warning applies.
- **Enforcing the existing table-routing rule on the measured (T) class (14% of long paragraphs)** — that is a compliance gap in `family-relay.md §(b)`, not a missing rule; fixing compliance is a different intervention from adding a grammar.
- **`backlog_index.py`'s identical bullet grammar** — the closest structural twin, but backlog entries are a different artifact family and no measurement of their defect rate exists.

## Alternatives Considered

| Alternative | Who ships it / source | Mechanically checkable? | Why rejected |
|---|---|---|---|
| Keep `one-assertion`, enforce via reviewer judgment | ADR (Nygard) "Decision: one sentence or a short paragraph" — copied by gov.uk, ThoughtWorks (EN) | No — no linter ships with any ADR tooling | This is the status quo, and it is what produced 682–1,095-char medians; the same convention fails the same way industry-wide |
| Whole-document or whole-field length cap | `commitlint` `header-max-length`; textlint `sentence-length` (JA) | Yes | Measured: 0 filler hits across 318 files — the corpus does not pad, so a size cap deletes explanation rather than relocating it, and cannot be satisfied by a genuinely 16-task plan |
| Semantic atomicity check (NLP) | INCOSE *Guide for Writing Requirements* "one thought per requirement"; QVscribe (EN) | Only via paid NLP tooling | Too heavy for a repo-local gate, and it re-introduces the judgment this arc exists to remove |
| Fixed clause template per field | GitHub Spec-Kit `FR-###: System MUST …`; AWS Kiro EARS (EN) | Yes | Constrains which fields exist and their opening clause, not the prose form of a free-text body — the wrong axis |
| Per-paragraph Mermaid CoT diagram beside the prose | kouko's Obsidian `references/` corpus, 8,806 notes, 80% at exactly one diagram per H4 (JA/ZH vault convention) | Partly | Additive, not routing: measured twice in loom that a diagram slot lengthens prose (plans 12k→26.6k chars median after the diagram slot shipped); and the corpus's own diagrams fabricate ungrounded nodes. Already decided to live in the adjudication view instead |

## What Becomes Obsolete

- BI-8 — The phrase `one-assertion unit of work` in `plan-format.md:97` is replaced in the same PR, not left standing beside the new rule as a second, weaker statement of the same duty.

## Open Questions

- OQ-1 [RESOLVED] — Threshold for BI-3 → resolved 2026-08-19 by measurement over 281 paragraphs in the 17 specs (7 post-#699 + 10 older): **600 characters**. Distribution is median 146 / p75 272 / p90 557 / p95 740 / max 2,399; candidate thresholds flag 400→16.0%, 500→12.1%, **600→8.2%**, 700→6.4%, 800→3.9% of all paragraphs. 600 sits just above p90, leaves the median a factor of four clear, and is the only candidate whose flagged population has already been classified (8 (T) / 26 (S) / 23 (N) in the earlier audit) — any other value would flag a set of unknown composition. Reversal condition: if a plan-time trial shows the rule firing on paragraphs the author declares narrative more often than it fires on splittable ones, raise to 800 rather than weakening the structural rule.

## Diagrams

Caption: the three measured paragraph classes and which mechanism owns each — this arc owns only the middle column.

```mermaid
flowchart TD
    P["long prose block<br/>&gt;threshold, in a named section"]
    T["(T) comparison-shaped<br/>8 of 57 measured"]
    S["(S) sequential / field-list<br/>26 of 57 measured"]
    N["(N) reasoning chain<br/>23 of 57 measured"]
    RT["family-relay.md §(b)<br/>table routing — ALREADY SHIPPED"]
    RS["this arc:<br/>split to bullets or table"]
    RN["adjudication view CoT diagram<br/>backlog, separate arc"]

    P --&gt;|"compares ≥2 named options<br/>on shared axes"| T
    P --&gt;|"items are independent;<br/>reordering loses nothing"| S
    P --&gt;|"sentences joined by but / so /<br/>therefore — connectives ARE content"| N
    T --&gt;|"compliance gap, not a rule gap"| RT
    S --&gt;|"no existing rule reaches it"| RS
    N --&gt;|"no container reaches a chain;<br/>author declares, reviewer checks"| RN

    classDef own fill:#d3f9d8,stroke:#2f9e44,color:#000
    classDef other fill:#e7f5ff,stroke:#1971c2,color:#000
    class S,RS own
    class T,N,RT,RN other
```
