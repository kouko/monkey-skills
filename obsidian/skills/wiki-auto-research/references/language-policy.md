<!-- BEGIN language-policy-v1 — managed by obsidian/scripts/distribute.py from obsidian/skills/wiki-ingest/references/language-policy.md — do not edit in place -->
<!-- This is a functional copy. Edit the canonical source above and re-run distribute.py. -->

# Language Policy — Body Language Resolution

`wiki-ingest` generates wiki page bodies in the language specified by this policy. This reference is the authoritative spec for `STEP 4c` of the ingest pipeline — the point where each target wiki page receives its body language instruction.

---

## 1. Purpose

### Two modes of operation

```
OBSIDIAN_WIKI_LANGUAGE_POLICY=enabled    → evaluate the decision tree in §2
OBSIDIAN_WIKI_LANGUAGE_POLICY=<unset>   → legacy LLM heuristic (v3.10.0 behavior)
```

**Legacy mode** (`LANGUAGE_POLICY` unset or empty) preserves the v3.10.0 behavior exactly: the LLM uses its training-data defaults, which favor English with CJK loanwords left in their source script (e.g. "余白", "侘寂"). No config reading, no tree evaluation. This is the backward-compatible path — vaults that never set `LANGUAGE_POLICY` are unaffected by this spec.

**Enabled mode** (`LANGUAGE_POLICY=enabled`) activates the decision tree. The tree evaluates path-based and tag-based rules in order and falls back to `OBSIDIAN_WIKI_PRIMARY_LANGUAGE` when no rule matches. Every page gets an explicit body language; the LLM's implicit bias is overridden.

`OBSIDIAN_WIKI_PRIMARY_LANGUAGE` is required when `LANGUAGE_POLICY=enabled`. It is the mandatory fallback and the default for any page not matched by a more specific rule.

---

## 2. Decision Tree Spec

### Evaluation order

Rules are evaluated in the order they appear in the tree. The **first matching rule wins**; lower rules are not consulted. If no rule matches, the fallback applies.

```
for each wiki page target:
  for each rule in tree (top to bottom):
    if rule.match(source_path, source_tags):
      body_language = rule.body_language
      preserve_group = rule.preserve_terms_group  # optional
      break
  else:
    body_language = OBSIDIAN_WIKI_PRIMARY_LANGUAGE
    preserve_group = None
```

### Rule format

Each rule is an ordered list entry with two mandatory fields and one optional field:

```
match → body_language [+ preserve-terms-group:<group>]
```

- **`match`** — one or both of:
  - `path:<prefix>` — source file vault-relative path starts with the given prefix
  - `tags-contain:<tag>` — source frontmatter `tags` list contains the given value (case-insensitive)
  - Multiple conditions on one rule: evaluated with AND logic
- **`body_language`** — BCP-47 code (`zh-TW`, `en`, `ja`, `ko`, …)
- **`preserve-terms-group:<group>`** (optional) — load named group from `OBSIDIAN_WIKI_PRESERVE_TERMS_FILE` and instruct the LLM to leave those terms untranslated in the body

### Empty tree is valid

A tree with no rules is semantically equivalent to a single-language ("primary-only") vault: every page body uses `PRIMARY_LANGUAGE`. This is the recommended starting point for single-language vaults that want explicit, auditable language control without per-domain rules.

```
# No rules → every page body uses PRIMARY_LANGUAGE
OBSIDIAN_WIKI_PRIMARY_LANGUAGE=en
OBSIDIAN_WIKI_LANGUAGE_POLICY=enabled
# (no LANGUAGE_POLICY_RULES entries)
```

### Tree representation in `.obsidian-wiki.config`

Rules are specified as ordered `LANGUAGE_POLICY_RULE_<n>` entries (1-indexed, no gaps):

```bash
LANGUAGE_POLICY_RULE_1=path:investing/ → zh-TW
LANGUAGE_POLICY_RULE_2=path:references/playlist/ tags-contain:ja-channel → PRIMARY + preserve-terms-group:jp-aesthetics
LANGUAGE_POLICY_RULE_3=tags-contain:coding → en
```

`PRIMARY` is a keyword meaning "resolve to the current value of `OBSIDIAN_WIKI_PRIMARY_LANGUAGE`" — it allows a rule to express "use the primary language but also apply a preserve-terms group" without repeating the BCP-47 code.

---

## 3. Preserve-Terms Protocol

### Purpose

Some domain terms should never be translated regardless of body language. The preserve-terms mechanism gives vaults a curated list of such terms. The LLM receives them as a "do not translate" instruction applied before body generation.

### File format (`OBSIDIAN_WIKI_PRESERVE_TERMS_FILE`)

The file is a plain-text list at a vault-relative path (e.g. `wiki/preserve-terms.txt`):

- One term per line
- `#group:<tag>` opens a named group; all subsequent lines belong to that group until the next `#group:` or end of file
- Blank lines and lines starting with `#` (other than `#group:`) are comments and are ignored
- CJK terms are matched **case-sensitively** (no casefold)
- ASCII terms are matched **case-insensitively** unless the term is wrapped in double quotes, which forces exact-case matching

```
# wiki/preserve-terms.txt — vault term-preservation list

#group:jp-aesthetics
余白
侘寂
間
wabi-sabi
yohaku

#group:finance
EBITDA
CoWoS
HBM
"Free Cash Flow"

#group:jp-tech
GitHub
Claude
API
```

### Group scoping

When a rule specifies `preserve-terms-group:<tag>`, only that group's terms are loaded. If `PRESERVE_TERMS_FILE` is unset or the group tag does not exist in the file, the preserve-terms instruction is silently omitted (no error; the body language rule still applies).

A rule may omit `preserve-terms-group` entirely. In that case no term preservation is applied for pages matched by that rule.

---

## 4. Aliases Conditional MUST

### Rule

| Condition | `aliases` field |
|---|---|
| slug language ≠ body language | **MUST** — required |
| slug language = body language | MAY — optional |

**Slug language** is always ASCII-only (per [page-format.md](page-format.md) — slugs are ASCII-safe identifiers). **Body language** is the language resolved by this policy's decision tree.

When a vault sets `PRIMARY_LANGUAGE=zh-TW`, most pages will have an ASCII slug and a zh-TW body — this triggers the MUST condition. The `aliases` field must include at least one alternative identifier that enables `wiki-cross-linker` to find the page from CJK references.

### What to include in `aliases`

Include all surface forms that might appear in other notes referencing this page:

- The primary CJK term (if body is CJK)
- Romanized / transliterated form (if different from the slug)
- Common English equivalent
- Alternate spellings

Example for slug `japanese-yohaku-aesthetic`, body zh-TW:

```yaml
aliases:
  - 余白
  - yohaku
  - 留白
  - white-space
```

### Enforcement

`wiki-lint` enforces this rule (from part-2 of this feature). Pages where slug language ≠ body language and `aliases` is absent or empty receive a lint warning. The severity is SHOULD (warning) in v3.11.0; may be promoted to MUST (error) in a future PR after dogfood.

---

## 5. Slug vs Body Language — Strict Decoupling

### Authority split

| Concern | Authority | Location |
|---|---|---|
| Slug / filename format | `page-format.md` | Always ASCII-safe; no change in this spec |
| Body language | This file (`language-policy.md`) | Resolved by decision tree at ingest time |
| Title language | Follows body | Same language as body |
| Summary language | Follows body | Same language as body; key terms preserved per preserve-terms list |

### Why strict decoupling matters

Slugs are external identifiers. They appear in URLs, wikilinks, and filesystem paths. Changing them breaks links; they must remain stable and ASCII-safe regardless of the vault's body language. Body language is a rendering concern — it affects how the content reads, not how the page is addressed.

This means a page can have:

```
slug (filename):   japanese-yohaku-aesthetic.md        ← ASCII, permanent
title (body):      日本余白美學——以「無」為形             ← zh-TW, follows body language
aliases:           [余白, yohaku, 留白, white-space]    ← cross-language anchors
```

The `aliases` field is the bridge: it lets `wiki-cross-linker` and Obsidian's graph view resolve references in any surface language back to the ASCII-slug page.

### Do not conflate slug authorship with body authorship

`wiki-ingest` generates the slug from the source filename (see `page-format.md`). It is **not** responsible for changing existing slugs when language policy changes. Body re-rendering (if a policy changes for existing pages) happens through `/wiki-relang` (Phase 2) or natural drift on source re-ingest — never through slug mutation.

---

## 6. Worked Example

### Vault layout

A generic multi-language vault with three domain clusters. The `PRIMARY_LANGUAGE` is `zh-TW`; English is used for coding content; Japanese aesthetic terms are preserved in the primary language.

**Config** (`.obsidian-wiki.config`):

```bash
OBSIDIAN_WIKI_PRIMARY_LANGUAGE=zh-TW
OBSIDIAN_WIKI_LANGUAGE_POLICY=enabled
OBSIDIAN_WIKI_PRESERVE_TERMS_FILE=wiki/preserve-terms.txt

LANGUAGE_POLICY_RULE_1=path:investing/ → zh-TW
LANGUAGE_POLICY_RULE_2=path:references/playlist/ tags-contain:ja-channel → PRIMARY + preserve-terms-group:jp-aesthetics
LANGUAGE_POLICY_RULE_3=tags-contain:coding → en
```

**Decision tree walkthrough**:

| Source path | Source tags | Matched rule | Body language | Preserve group |
|---|---|---|---|---|
| `investing/2026-04-台積電財報.md` | `[finance, tw]` | Rule 1 (`path:investing/`) | zh-TW | — |
| `references/playlist/茶道美学channel/episode-12.md` | `[ja-channel, aesthetics]` | Rule 2 (path + tag) | zh-TW | `jp-aesthetics` |
| `research/rust-ownership-notes.md` | `[coding, systems]` | Rule 3 (`tags-contain:coding`) | en | — |
| `reading/四千週.md` | `[book, productivity]` | No match → fallback | zh-TW | — |

### Concrete page example

Source: `references/playlist/茶道美学channel/episode-12.md`
Matched rule: Rule 2 → body zh-TW + preserve-terms-group `jp-aesthetics`
Slug generated: `chadou-aesthetics-channel-ep12` (ASCII-safe, from source basename)

Generated frontmatter:

```yaml
---
title: "茶道美學頻道 Ep.12——余白與空間感"
type: concept
domain: aesthetics
status: stub
updated: 2026-05-18
tags:
  - ja-channel
  - aesthetics
  - tea-ceremony
sources_count: 1
summary: "余白（yohaku）在茶道空間設計中代表有意留下的空白，是與侘寂（wabi-sabi）互補的美學原則。本頁整理 Ep.12 的核心論點。"
aliases:
  - 茶道美學
  - chadou aesthetics
  - tea ceremony aesthetics
---
```

**Why `aliases` is MUST here**: slug `chadou-aesthetics-channel-ep12` is ASCII; body is zh-TW. Slug ≠ body language → conditional MUST applies. The aliases list provides zh-TW and English anchors for `wiki-cross-linker`.

**Preserve-terms effect**: the terms `余白` and `侘寂` from the `jp-aesthetics` group appear in the summary in their Japanese script form, not translated to "negative space" or "wabi-sabi romanization" — consistent with the source material's register.

<!-- END language-policy-v1 -->
