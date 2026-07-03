# distill-sessions proposals — 2026-07-02

**Target SKILL.md**: `/Users/kouko/.supacode/repos/monkey-skills/obsidian-skill-r1/obsidian/skills/obsidian-markdown/SKILL.md`
**Counts**: 1 addition(s), 0 modification(s), 0 anchor mismatch(es), 10 pending cross-session evidence, 0 deferred to v0.2.

> No silent writes — review the proposals below, then run `python -m apply --approved ...` to commit the diff.

## Proposed additions

### Addition 1 [insert into §Properties (Frontmatter)]

```
**Document custom type/status property vocabulary beyond the three defaults**

_Agent extended frontmatter with type: research / status: completed / related_notes without hesitation; the three-default example block reads as exhaustive._

Add one line to §Properties (Frontmatter): note-type-specific custom properties (type / status / related_notes) are expected and encouraged, following the vault's per-folder convention; suggest a starter enum (type: research/reference/journal; status: draft/in-progress/completed).

_(supported by 2 session(s): 2cf16ba1-1445-4f04-a87e-d2ce45295139, d271e6cf-821b-47d1-b014-975cbad11e68)_
```

## Proposed modifications

_(none)_

## Anchor mismatch — needs review

_(none)_

## Cross-session evidence pending

_These items were observed in only 1 session and did not reach the minimum cross-session evidence threshold (min_n=2). They are NOT auto-applied — re-run after more sessions accumulate to promote them._

### Assign callout types fixed semantic roles instead of defaulting to note
_abstract=TL;DR, warning=caveats, tip=how-to, success=delivery summary, question=open follow-ups — one role per type kept a long note scannable._

Add to §Callouts a short 'pick the type by the sentence's job' guideline with the observed role mapping, so agents choose deliberately instead of defaulting to note/info everywhere.

_Observed in 1 session: `04f39690-5f0a-45b8-8c2f-eeae44460ea2` — re-run after more session evidence accumulates._

### Grep heading anchors for surgical edits on large notes
_grep -n on surrounding headings + narrow offset/limit Read kept edits surgical on a 1429-line note instead of full rereads._

Note in §Table of Contents: headings double as the grep index for locating edit insertion points in a note too large to read in full — grep -n the surrounding headings, then narrow Read around those lines.

_Observed in 1 session: `04f39690-5f0a-45b8-8c2f-eeae44460ea2` — re-run after more session evidence accumulates._

### Verify same-note anchors programmatically before declaring a long note done
_A heading-set vs [[#target]]-set diff script caught real breakage from heading-text drift across 4 edit rounds (22 anchors vs 199 headings) that manual rereading missed — despite §Internal Links marking same-note links as exempt-always-resolve._

In §Internal Links (Wikilinks), qualify the same-note exemption: after multi-round edits of a long note, re-verify [[#Heading]] anchors with a cheap heading-set vs link-target-set diff before declaring the note done; heading-text drift silently breaks 'always resolving' anchors.

_Observed in 1 session: `04f39690-5f0a-45b8-8c2f-eeae44460ea2` — re-run after more session evidence accumulates._

### Load obsidian skills before drafting, not mid-write
_Agent loaded obsidian-markdown + mermaid-visualizer back-to-back after research and before the single Write that shipped a 20KB note with zero rework._

Sharpen §Workflow: load this skill as soon as note-creation is decided, before drafting body content — front-loading is what produces first-write-correct frontmatter/TOC/diagrams.

_Observed in 1 session: `07c5e12e-e3b7-489f-ab6b-c084a71f3cbd` — re-run after more session evidence accumulates._

### Populate related_notes and wikilinks only from targets confirmed in-session
_related_notes contained exclusively titles already read or seen in another note's frontmatter — every link resolved without a separate existence check._

Add to §Properties (Frontmatter): related_notes / body wikilink targets should be drawn only from notes confirmed to exist in-session (prior Read or cross-referenced frontmatter).

_Observed in 1 session: `07c5e12e-e3b7-489f-ab6b-c084a71f3cbd` — re-run after more session evidence accumulates._

### Reuse one semantic mermaid palette across all diagrams in a note
_Four diagrams of different types shared one classDef palette (gate=red, context=blue) instead of ad-hoc per-diagram colors._

Note under §When to invoke the visualizer: once conventions are loaded, reuse the same semantic palette across all diagrams in one note for visual consistency.

_Observed in 1 session: `07c5e12e-e3b7-489f-ab6b-c084a71f3cbd` — re-run after more session evidence accumulates._

### External tool names bold, external URLs markdown links, vault notes wikilinks — worked triad
_20+ external product mentions rendered as **bold**, 20+ citations as [title](url), wikilinks reserved for in-vault notes — correct three-way split by inference._

Add a concrete worked triad to §Internal Links (Wikilinks): external tool/brand in prose → bold; external URL citation → markdown link; in-vault note → wikilink — turning the correct-by-inference split into a checkable rule for research-style notes.

_Observed in 1 session: `2cf16ba1-1445-4f04-a87e-d2ce45295139` — re-run after more session evidence accumulates._

### TOC entries copy heading text verbatim including numeric prefix
_9-entry TOC where every [[#Heading]] mirrored its target heading verbatim (incl. numeric prefix) resolved on first write with no correction pass._

Strengthen §Table of Contents with an explicit rule: copy the heading text verbatim — including any numeric prefix — into the [[#Heading]] entry; the TOC is a literal echo of headings, not a paraphrase.

_Observed in 1 session: `2cf16ba1-1445-4f04-a87e-d2ce45295139` — re-run after more session evidence accumulates._

### Disambiguate TOC/COT acronyms against this section's meaning before acting
_User's 'COT' meant Table of Contents; agent mapped it to Chain-of-Thought, wrote a wrong section into three files, burned two AskUserQuestion rounds (one flatly rejected) before the user clarified._

Add a line under §Table of Contents: TOC-related acronyms (TOC/COT/目錄) should first be checked against this section's [[#Heading]] anchor-link meaning before assuming any other in-session term such as Chain-of-Thought.

_Observed in 1 session: `9e195a61-343d-47a0-845f-ee60bd999517` — re-run after more session evidence accumulates._

### Add a vault-discovery search step before drafting when cross-references are implied
_Agent volunteered '先快速查一下 vault 現有的相關筆記' (find across wiki/ + research/) before writing — a step absent from the numbered workflow, whose step 4 only gates emission, not discovery timing. Produced 13 correct wikilinks._

Add an explicit early step to §Workflow: Glob/search the vault for candidate related notes BEFORE drafting body content whenever the request implies cross-references — make discovery a guaranteed workflow output, not agent-initiative bonus.

_Observed in 1 session: `d271e6cf-821b-47d1-b014-975cbad11e68` — re-run after more session evidence accumulates._

## Marked for v0.2

_(none)_
