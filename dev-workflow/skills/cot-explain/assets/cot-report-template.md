---
title: "{{TITLE}}"
type: cot-explain
date: {{DATE}}
tags:
  - cot-explain
{{TOPIC_TAGS}}
aliases: []
source: "{{SOURCE_ABSOLUTE_PATH}}"
source_mode: "{{SOURCE_MODE}}"
language: {{LANGUAGE}}
status: completed
processed_at: "{{PROCESSED_AT}}"
timezone: Asia/Taipei
llm_provider: anthropic
llm_model: "{{LLM_MODEL}}"
generator: "dev-workflow:cot-explain"
arcs: {{ARCS}}
nodes: {{NODES}}
layout: "{{LAYOUT}}"
verified: ""
fidelity_checked: ""
---

<!-- cot-explain markdown template. DELETE THIS COMMENT BLOCK before writing.

     This .md is the artifact. The HTML is derived from it mechanically by
     scripts/render_cot_html.py — never hand-edit the HTML, and never let
     the two disagree.

     Placeholders are double-brace. `verified` and `fidelity_checked` in the
     frontmatter are filled by the tooling, not by you: leave them empty.
     `source` takes the ABSOLUTE path — the renderer links it, and only an
     absolute path survives the page being moved or read from elsewhere.
     In conversation mode write 本次對話 instead; it is not a path.

     Structure rules the converter depends on:
       - `### ` starts a page-level section
       - `#### ` starts one arc (one reasoning chain, one diagram)
       - `##### ` starts one node card, written `##### A — 節點標題`
       - a ```mermaid fence belongs to the arc it sits in
     Delete any section with no content — an empty heading is a defect,
     an absent section is honest. Headings and labels are content, not
     fixed chrome: write them in the language the user asked in, the same
     as the body. Quotes keep the source's own wording.
-->

### 概述

{{ONE_LINE_CONCLUSION}}

### 推理鏈

#### {{ARC_TITLE}}

{{ARC_LEAD}}

```mermaid
{{MERMAID_DIAGRAM}}
```

##### {{NODE_ID}} — {{NODE_TITLE}}

- **主張**：{{NODE_CLAIM}}
- **依據**：{{NODE_EVIDENCE}}
- **這一步改變了什麼**：{{NODE_DELTA}}
- **例外／失效條件**：{{NODE_REBUTTAL}}

> {{NODE_VERBATIM}}

<!-- The `>` blockquote appears ONLY on a node that specifies something
     to be done or built — a rule, an obligation, a procedure, a code
     change — and it holds the source's OWN sentences, in the source's
     own language. Use markdown's quote syntax, not a list item — a
     blockquote is what a quotation is, and the structure is what the gate
     checks. Several sentences go on several `>` lines.
     On such a node the *what* is quoted or it is absent; it is never
     paraphrased. 主張 and 依據 still explain WHY, in the reader's language.
     One mechanism per node: do not merge several mechanisms into a
     single "the decision" node, or this rule covers nothing.
     Delete the blockquote on nodes that report a fact or an insight.

     The 例外 line appears ONLY when the source states a limit on when the
     claim holds, or a condition under which the step would be dropped.
     Delete the whole line otherwise — an empty one asserts "no exceptions
     apply", which is a claim the source did not make. A node may carry
     more than one; list them as sub-bullets rather than concatenating.
     Repeat this ##### block per node, in diagram order.
     Repeat the whole #### block per arc. -->

### 這份結論要求你做什麼

<!-- Duties and contract rules the source states — "before X you must Y",
     "without Z this must not ship". These are not reasoning steps and will
     never become nodes, so without this section they vanish: a fidelity
     test found a reader receiving every reason for a mechanism and none of
     the obligation that makes it work. Delete the section if the source
     states none. -->

- {{OBLIGATION}}

### 岔路

<!-- Options weighed and never adopted. A judgment that was held and then
     overturned is NOT here — it is a node in the chain, with whatever
     overturned it as the edge into the next node. Delete if none. -->

| 考慮過的選項 | 否決理由 |
|---|---|
| {{ALT_OPTION}} | {{ALT_REASON}} |

### 未解問題與前提

#### 這條推理鏈依賴的前提

<!-- Only what the SOURCE itself leaves untested or flags as unverified.
     Do not infer "this was probably never checked" — that manufactures an
     assumption the source did not make, and a fidelity run caught exactly
     that invention. Delete the list if the source flags none. -->

- {{ASSUMPTION}}

#### 還沒有答案的問題

<!-- Where the source records its own leaning ("leaning no", "my take"),
     carry the leaning verbatim rather than presenting the question as open. -->

- {{OPEN_QUESTION}}

---

{{PROVENANCE_NOTE}}
