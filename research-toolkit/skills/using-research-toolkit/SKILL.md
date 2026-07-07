---
name: using-research-toolkit
description: |
  Family-entry router for research-toolkit — verify one claim, audit a document's citations, deeply read one long source, or get a multi-source verified report. Use when unsure which research skill applies, e.g. 「不確定要用哪個研究工具」.
version: 0.1.0
---

# Using Research Toolkit

Ask first: **"What are you trying to find out — and from how many
sources?"** Then route to the best-fit member skill (one of the four
skills below).

## Routing Guide

Once you've picked a row, invoke that member via the host's
skill-invocation mechanism — on Claude Code, the Skill tool, e.g.
`Skill(skill: "research-toolkit:fact-check")`; on other hosts, their
equivalent skill/tool-invocation call.

| Situation | Skill | Notes |
|---|---|---|
| One factual claim needs a verdict mid-conversation. EN: "is this true?", "really?"; 中: 「這個說法對嗎」「查一下這個說法」 | `fact-check` | Lightweight, single-claim adversarial verdict — supported / refuted / inconclusive |
| An existing document's citations need auditing. EN: "check these citations", "do the sources back this up?"; 中: 「查證這份文件的引用」 | `cite-check` | Audits a document you did not write; flags unsupported / misattributed / dead-link claims |
| One long document/book needs structured deep comprehension. EN: "help me understand this paper/book"; 中:「精讀這篇論文/這本書」 | `deep-read` | Depth-on-ONE source — sections, claims, methodology, caveats, argument structure |
| Heavyweight multi-source research REPORT wanted, adversarially verified, with an inspectable/tunable pipeline (or no built-in deep-research on this host). EN: "write me a research report on X", "research this exhaustively"; 中: 「幫我做一份多來源的研究報告」「徹底研究這個主題」「多輪深挖」 | `deep-deep-research` | Key-free; reproduces scope → search → dedup → fetch → verify → synthesize as editable skill steps |

## Negative Guard

Not every research-shaped sentence belongs in this family. A trivial
lookup, a passing mention of a fact, or a casual opinion ask — with no
verification request attached — should be answered directly; routing
those into the family is over-firing, not thoroughness. But an EXPLICIT
verification ask ("is it true?", "really?", 「這個說法對嗎」) still
routes to `fact-check`, even when the claim sounds like common
knowledge — fact-check's own trigger deliberately covers "even common
knowledge," so don't let familiarity talk you out of routing it. Only
route when the user actually wants verification, citation auditing,
structured single-document comprehension, or a synthesized multi-source
report.

Two adjacent boundaries worth naming explicitly:

- Plain summarization with no comprehension goal ("summarize this
  40-page report") → answer directly; `deep-read` is for structured
  understanding (sections, claims, argument), not summaries.
- Spot-checking numbers in the user's OWN data/spreadsheet against
  their own source → not this family (`fact-check` verifies public
  claims against published sources).

## Built-in Boundary

Claude Code's built-in `deep-research` skill legitimately owns the
generic "deep research this topic" ask — don't displace it by default.
Route to `deep-deep-research` instead when the
user wants an exhaustive multi-round investigation (徹底研究／多輪深挖),
wants to see or tune the pipeline stages, needs a key-free/portable
run, or is on a host with no built-in deep-research (e.g. Codex).

## What This Skill Does NOT Do

- Does not perform any research, verification, or synthesis itself —
  it only routes to the member skill that does.
- Does not duplicate a member skill's workflow, standards, or the
  quality checks each member runs itself — each member owns its own
  procedure.
- Does not wire hooks or automation — it is a plain routing skill,
  invoked like any other.
