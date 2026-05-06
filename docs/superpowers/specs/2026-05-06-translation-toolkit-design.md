# translation-toolkit Plugin Design

**Date**: 2026-05-06
**Status**: Draft (decisions locked, ready for implementation plan)
**Author**: kouko + Claude Opus 4.7 (1M context)
**Plan reference**: TBD (to be created via writing-plans skill)

---

## Context & Motivation

### The Problem

Existing LLM translation projects fall into two categories, neither of which fits a Claude Code skill that must (a) handle three distinct scenarios — i18n strings, technical documentation, advertising copy — across EN / JA / ZH-TW / ZH-CN with first-class quality, and (b) be portable across multiple agent runtimes (Claude Code, Gemini CLI, Codex):

| Category | Example | Limitation |
|---|---|---|
| Single-pipeline reflect/improve | [andrewyng/translation-agent](https://github.com/andrewyng/translation-agent) | No glossary, no format awareness, no placeholder protection, no transcreation, no verification |
| Web app + persona dropdown | [Max-Lee-explore/agentic-ai-translation-company](https://github.com/Max-Lee-explore/agentic-ai-translation-company) | Conflates domain/mode/register into one persona dropdown; chunk-isolation regression; multi-provider HTTP duplicated; no placeholder protection |
| Pluggable workflow framework | [DavidLMS/aphra](https://github.com/DavidLMS/aphra) | Only one workflow shipped; per-role model assignment hard-coded (anti-portable); no format awareness |

The gap: no existing project provides **format-typed pipelines + 5-axis user control + 4-tier glossary fallthrough + 5-gate verification** in a single skill, and none address translation-theory know-how (skopos / Vinay-Darbelnet / domestication-foreignization / back-translation QA / translation memory) explicitly.

### Research Findings (2026-05-06)

Two parallel research passes surfaced:

**Pass 1 — Common framework across the 3 reference projects** ([transcript at top of brainstorming]):

The shared 3-step `translate → reflect → improve` core (TA's contribution) is the consensus base. Aphra adds preparation layer (analyze + search + glossary), AATC adds verification layer (terminology check). Generalized:

```
PREPARATION → CORE LOOP (3-step) → VERIFICATION
```

This 3-layer skeleton is the universal shape, with Layer 1 (intake) and Layer 5 (output / format-roundtrip / audit trail) as the missing wrappers.

**Pass 2 — Existing glossary sources for bundling** ([transcript at top of brainstorming]):

Bundle-able CC-BY-compatible sources (license verified per source):

| Source | License | Scope | Entries (approx) |
|---|---|---|---|
| Mozilla Pontoon TBX (ja/zh-TW/zh-CN) | MPL-2.0/CC-BY-SA | web/dev/privacy UI | 95 × 3 locales |
| GNOME i18n glossary | LGPL/GPL | desktop UI | ~150 × 3 |
| 法務省 JLT 標準対訳辞書 | CC-BY 4.0 互換 | 法令・行政 (JA) | several thousand |
| 國家教育研究院樂詞網 | OGDL v1 ≈ CC-BY 4.0 | 全 domain (zh-TW) | 100 万+ (selectively bundled) |
| e-Stat 日英統計用語集 | 政府標準利用規約 | 統計・経済 (JA) | ~4,773 |
| 東京都 日英対訳用語集 | CC-BY 4.0 | 行政・観光 (JA) | several hundred-thousand |
| NICT 日英中基本文 | CC-BY 3.0 | 基本文 (JA) | 5,304 sentences |
| 內閣官房 政府機關名英訳 | 政府標準利用規約 | gov 組織名 (JA) | several hundred |
| W3C jlreq / clreq | W3C Document License | typography rules | (rules, not entries) |

Total bundled: ~10,000+ entries for JA, similar for zh-TW, ~150-200 for zh-CN (acknowledged limitation — open-licence zh-CN sources are scarce).

Optional fetch (NOT bundled, license too gray to redistribute):

| Source | Entries | Reason |
|---|---|---|
| Microsoft Terminology Collection | ~33,000 × 100+ langs | License unclear post-2023 portal closure |
| 特許庁 UTX (AAMT) | ~130,000 EN-JA | License forbids dead-copy redistribution |

These ship as opt-in `fetch-microsoft-terms.py` / `fetch-jpo-utx.py` scripts that download to `~/.cache/translation-toolkit/`.

### Key Insight

The translation-toolkit's value comes from **separating axes that the reference projects conflate**:

- AATC's "9 personas" = mode + register + domain bundled into one knob, so "technical doc but warm" is impossible
- TA's `country` = locale + register implied
- Aphra's `is_suitable_for` = domain + format implied

Our skill exposes **5 orthogonal axes** (mode / register / strategy / locale / domain) plus a binary `auto` / `explicit` intake mode so end users get high quality with zero friction in default mode, while power users get full control when needed.

---

## Architecture

### Plugin Layout

```
translation-toolkit/
├── plugin.json
├── README.md / README.ja.md / README.zh-TW.md   # tri-language per repo PR #150
├── NOTICES.md                                    # bundled-source attributions
│
├── docs/                                          # plugin-level documentation (NOT a skill)
│   ├── glossary-format-spec.md                    # how users extend their project glossary
│   └── architecture.md                            # plugin architecture overview
│
├── vendor/                                        # bundled-source LICENSE files (plugin-level, NOT a skill)
│   ├── mozilla-pontoon/LICENSE
│   ├── gnome-i18n/LICENSE
│   ├── naer/LICENSE
│   ├── jlt/LICENSE
│   ├── e-stat/LICENSE
│   ├── tokyo/LICENSE
│   ├── nict/LICENSE
│   ├── cabinet/LICENSE
│   └── w3c/LICENSE
│
├── using-translation-toolkit/SKILL.md             # Router skill (entry point)
│
├── translation-intake/                            # Layer 1 owner — fully self-contained
│   ├── SKILL.md
│   ├── protocols/intake-auto.md
│   ├── protocols/intake-explicit.md
│   └── references/orthogonal-axes.md             # functional copy
│
├── translation-i18n/                              # PO/JSON/XLIFF/Android/iOS — fully self-contained
│   ├── SKILL.md                                    # supports `--audit-only` flag for review-without-rewrite
│   ├── glossary/                                   # functional copies of all glossary files
│   │   ├── glossary-en-US--ja-JP.md               # uniform pair-file schema
│   │   ├── glossary-en-US--zh-CN.md
│   │   ├── glossary-en-US--zh-TW.md
│   │   ├── glossary-ja-JP--zh-TW.md
│   │   └── glossary-zh-CN--zh-TW.md
│   ├── corpus/                                     # functional copies of parallel-sentence corpora (NOT glossary)
│   │   └── nict-en-ja-zh.md                       # NICT 5,304 sentence triples — exemplar reference for LLM
│   ├── typography/                                 # functional copies
│   │   ├── jlreq-summary.md
│   │   └── clreq-summary.md
│   ├── references/                                 # functional copies of shared core docs
│   │   ├── core-loop.md
│   │   ├── 4d-reflection.md
│   │   ├── orthogonal-axes.md
│   │   ├── verification-gates.md
│   │   └── audit-trail-spec.md
│   ├── checklists/i18n-format-checklist.md       # skill-specific (NOT distributed elsewhere)
│   └── protocols/placeholder-protect.md          # skill-specific
│
├── translation-doc/                               # markdown / technical docs — fully self-contained
│   └── (same self-contained pattern as translation-i18n; skill-specific checklists/protocols differ)
│
├── translation-creative/                          # ad copy / transcreation — fully self-contained
│   └── (same self-contained pattern; references/ also includes 5d-effectiveness.md)
│
└── scripts/                                        # plugin-level build pipeline (NOT a skill)
    ├── README.md                                  # SSOT-and-functional-copy explanation
    ├── canonical/                                 # Single Source of Truth
    │   ├── glossary-en-US--ja-JP.md               # uniform pair-file schema (5 pair files)
    │   ├── glossary-en-US--zh-CN.md
    │   ├── glossary-en-US--zh-TW.md
    │   ├── glossary-ja-JP--zh-TW.md
    │   ├── glossary-zh-CN--zh-TW.md
    │   ├── manual-entries-ja-JP--zh-TW.md         # hand-curated entries → glossary-ja-JP--zh-TW.md
    │   ├── jlreq-summary.md
    │   ├── clreq-summary.md
    │   ├── core-loop.md                           # 3-step shared reference
    │   ├── 4d-reflection.md
    │   ├── 5d-effectiveness.md
    │   ├── orthogonal-axes.md
    │   ├── verification-gates.md
    │   └── audit-trail-spec.md
    ├── build-pairs-from-en.py                     # build glossary-en-US--{X}.md from upstream EN-X sources (Pontoon/GNOME/JLT/NAER/...)
    ├── build-pair-zh-CN--zh-TW.py                 # build from NAER 兩岸對照
    ├── build-pair-ja-JP--zh-TW.py                 # merge manual + derive from EN-pivot intersection
    ├── distribute.py                              # canonical/* → 各 skill subfolder
    ├── verify-drift.py                            # CI: byte-identical check across all functional copies
    ├── fetch-microsoft-terms.py                   # opt-in download script
    └── fetch-jpo-utx.py                           # opt-in download script
```

### Skill Self-Containment Guarantee

**Every skill in this plugin is fully self-contained at runtime.** A skill never reads files belonging to another skill, never invokes another skill via the Skill tool, and can be physically extracted to a different plugin without modification.

Concrete guarantees:

| Rule | Mechanism |
|---|---|
| Each skill reads only its own subfolder files | All shared content (glossary, typography rules, reference docs) is distributed as functional copies to each skill's `glossary/` / `typography/` / `references/` subfolders |
| Skills do NOT invoke each other | Coordination between router → intake → 4 active skills happens via runtime data passing (intake spec, audit trail JSON) only, not via Skill tool dispatch |
| Plugin-level `docs/` `vendor/` `scripts/` are NOT read at runtime | These are user-facing or build-time resources only. Active skills' SKILL.md never references paths outside their own skill folder |
| Any skill can be physically extracted | Copy `translation-i18n/` to another plugin and it still works (it has its own complete glossary + references) |

### SSOT-and-Functional-Copy Pattern

Pattern source: PR #159 in this repo (codified as memory `feedback_ssot_functional_copy_pattern`). Applied here because:

1. Anthropic skill convention requires each skill to be self-contained (no cross-skill file reads)
2. Multiple translation skills need identical glossary + reference content
3. Pure path-only delegation cannot work — skills must Read content at runtime, and runtime cannot reach into sibling skills without violating isolation

Resolution:

- **Canonical source of truth**: `scripts/canonical/*.md` — the only place to edit shared content. Lives at plugin level, NOT inside any skill.
- **Functional copies**: each skill has its own `glossary/` / `typography/` / `references/` folder containing byte-identical copies of relevant canonical files (distributed by `distribute.py`)
- **Drift rule**: edits to canonical require running `distribute.py` in same commit; `verify-drift.py` runs in CI to enforce byte-identical
- **At runtime**: each skill reads only its local copies; truly self-contained per Anthropic convention

### Glossary Architecture

**Resolution chain** (4-tier fallthrough, executed in Layer 2 preparation):

```
L1: Project glossary  (<repo>/docs/i18n/glossary-{tgt}.md)
    User's repo-specific overrides — highest authority
        │ miss
        ▼
L2: Bundled glossary  (skill-internal functional copy)
    Cross-repo standard terminology
        │ miss
        ▼
L3: Web search        (default ON; --web-search=off to disable)
    Live lookup for difficult terms
        │ miss / disabled
        ▼
L4: LLM fallback      (no reference material)
    Audit-trail flagged
```

(Earlier draft included a 3rd tier "Translation memory" between L1 and bundled glossary, backed by `<repo>/.translations/memory-*.json`. Deferred to v0.2 — see Out of Scope. v0.1 ships 4-tier; L1 project glossary is the consistency mechanism within a repo.)

Every hit at every tier is recorded in audit trail with source attribution.

**Uniform pair-file schema** — every glossary file is a bi-directional language pair table. Filename: `glossary-{lang-A}--{lang-B}.md` (BCP-47, alphabetical, double-hyphen separator). Total 5 pair files in v0.1.0:

```
glossary-en-US--ja-JP.md     glossary-en-US--zh-TW.md     glossary-ja-JP--zh-TW.md
glossary-en-US--zh-CN.md     glossary-zh-CN--zh-TW.md
```

Example (`glossary-en-US--ja-JP.md`):

```yaml
---
pair: [en-US, ja-JP]                          # BCP-47, alphabetical
version: 0.1.0
sources: [mozilla-pontoon-2026-05-01, gnome-i18n-2024-02-15, jlt-v18.0, e-stat-2025-q4, tokyo-2024-12, cabinet-2023-04]
domains_supported: [general, ui, tech.software, tech.web, tech.data, tech.crypto, gov, legal, statistics, marketing, typography]
---

## meta
(typography rules — 句末「。」、列舉「、」、半角英数字 spacing 規則、etc.)

## domain: general
| en-US | ja-JP | source | notes |
| translate | 翻訳する | jlt | — |

## domain: ui
| en-US | ja-JP | source | notes |
| Cancel | キャンセル | gnome | — |

## domain: tech.software
| en-US | ja-JP | source | notes |
| key | 鍵 | pontoon | crypto 文脈は tech.crypto を見よ |

## domain: tech.crypto
| en-US | ja-JP | source | notes |
| key | 暗号鍵 | — | tech.software の "key" を上書き |
```

Example (`glossary-ja-JP--zh-TW.md` — same schema, different pair):

```yaml
---
pair: [ja-JP, zh-TW]
version: 0.1.0
sources: [manual-curated, derived-en-pivot]
domains_supported: [general, ui, tech.software, ...]
---

## meta
(ja 新字体 ↔ zh-TW 正體互換規則)

## domain: general
| ja-JP | zh-TW | source | notes |
| 手紙 | 信 | manual | ⚠️ NOT「衛生紙」(false friend) |
| 勉強 | 學習 / 努力 | manual | ⚠️ NOT「強迫」(false friend) |
| 愛人 | 情婦 | manual | ⚠️ false friend, zh-TW「配偶」誤譯風險 |
| 図書館 | 圖書館 | manual | 漢字共通詞・新字体↔正體 |
| 御朱印 | 御朱印 | manual | 借用 |
| 翻訳する | 翻譯 | derived (en: translate; jlt × naer) | — |

## domain: ui
| ja-JP | zh-TW | source | notes |
| キャンセル | 取消 | derived (en: Cancel; pontoon × naer) | — |
```

Both files use **identical schema** — same frontmatter shape, same `## meta` + `## domain: <name>` sections, same 4-column table (`<lang-A>` | `<lang-B>` | `source` | `notes`). The `pair` frontmatter field declares which languages this file covers; the table column headers match `pair` element order.

**Domain taxonomy** (frozen at v0.1.0):

```
general          # 通用語彙
ui               # UI strings
tech.software    # 程式語彙
tech.web         # web/API/networking
tech.data        # database/data engineering
tech.crypto      # cryptography/security
gov              # 政府機関 / 役職名
legal            # 法令 / 契約
medical          # 医療
finance          # 金融 / 投資
marketing        # 広告 / コピー
statistics       # 統計
typography       # 排版規則 (meta-section)
```

**Lookup algorithm** — given source language `S`, target language `T`, and a term:

```
Step 1: Try direct pair file glossary-{S}--{T}.md (or {T}--{S}.md, alphabetical)
        Find term in S column → return T column value, audit_trail.path = "direct"

Step 2 (if Step 1 misses and neither S nor T is en-US): pivot via en-US
        Step 2a: glossary-{en-US}--{S}.md — find term in S column → get en-US pivot
        Step 2b: glossary-{en-US}--{T}.md — find pivot in en-US column → get T target
        audit_trail.path = "pivot.en-US"

Step 3 (if pivot misses): fall through to L4 web search → L5 LLM
```

The pair-file format is uniform; all 5 pair files use the same schema. EN serves as runtime pivot fallback only when a direct pair file is unavailable for some pair (e.g., `ja-JP ↔ zh-CN` — not bundled in v0.1.0; runtime pivots via EN automatically).

**Manual / derived entries** (visible via `source` column, not separate file structure):
- `source: manual` — hand-curated (false-friend warnings, 漢字共通詞, 文化借用). Priority over derived if same source-term appears in both.
- `source: derived (en: <pivot>; <upstream-pair-A> × <upstream-pair-B>)` — auto-built by build script intersecting two upstream EN-pivoted pair files.
- `source: <upstream-name>` — directly sourced from a single upstream (e.g., `pontoon`, `jlt`, `naer`, `gnome`, `e-stat`, `tokyo`, `cabinet`).

For `glossary-ja-JP--zh-TW.md` specifically, seed manual list (~80-100 entries) covers:
- 漢字 false friends (~25)
- 漢字共通詞 + 字形差異規則 (~20)
- 文化借用 (御朱印 / 居酒屋 / 寿司 etc.) (~15)
- 高頻法律 / 金融 / gov 共通字 (~15)
- 其他 high-frequency false-friend candidates (~15)

---

## Translation Pipeline (5 Layers)

Shared across all 4 active translation skills (i18n / doc / creative / audit). Layer 2 and Layer 5 contain format-specific code; Layers 1, 3, 4 are uniform.

### Layer 1: Intake

**Auto mode** (default — user provides only source + target locale):
- Source analysis via LLM extracts: domain (top-3 keyword match against taxonomy), formality register, mode hint (literal/faithful/localized/transcreation), strategy bias (domestication/foreignization)
- All inferences written to audit trail; user can review and rerun in explicit mode if needed

**Explicit mode** (`--explicit` / `-e`):
- Skill prompts user for all 5 axes + skopos (intent: who reads, what action expected)
- 5 axes: mode / register / strategy / locale / domain

### Layer 2: Preparation

**a. Format parse** (per-skill specialization):
- `translation-i18n`: PO / JSON / XLIFF / Android `strings.xml` / iOS `.strings`
- `translation-doc`: markdown → AST, separate prose from code/URL/HTML
- `translation-creative`: plain text + optional brand brief
- `--audit-only` flag (any of above 3 skills): source + existing target translation pair (instead of source-only)

**b. Protect-pass** (HARD pre-filter — three reference projects all skip this):
- Regex extracts and masks:
  - `{{var}} {0} %s {name}` ICU plurals → `⟦P:01⟧`
  - `` `inline code` `` ` ```fenced``` ` `<html>` tags → `⟦P:02⟧`
  - URLs / emails / file paths → `⟦P:03⟧`
- Token map recorded for restoration
- Source placeholder count saved as `expected_count` for L4 verification

**c. Source analysis** (Aphra-style):
- LLM extracts:
  - Industry jargon
  - Culture-specific concepts (御朱印 / 紅包 / 神田昌典)
  - Untranslatability candidates (puns, rhymes, culture memes)
  - Domain hints (used to load relevant glossary domain sections)

**d. Glossary resolve** (5-tier fallthrough — see Architecture above)

### Layer 3: Core Loop

**Chunking**: `tiktoken`-based, threshold = 2000 tokens (per TA convention)

**3-step**:
- DRAFT (writer role): with TA's `<TRANSLATE_THIS>` cross-chunk windowing — every chunk's prompt re-emits whole document, but only wraps active chunk in tag
- REFLECT (critic role): structured 4D critique output (5D for transcreation mode)
- IMPROVE (reviser role): consume critique, output v2

**Reflection axes**:
1. **Accuracy** — semantic faithfulness, no addition/omission/distortion
2. **Fluency** — naturalness in target language
3. **Style** — register / rhythm / rhetoric matches source and mode
4. **Terminology** — glossary compliance, domain conventions
5. **Effectiveness** (transcreation only) — persuasion intent preserved in target culture

**Glossary injection strategy**: Only terms appearing in source are injected into system prompt (not the entire glossary). Per chunk, recompute relevant terms. Avoids context bloat and irrelevant-term contamination.

### Layer 4: Verification

**MUST gates** (fail → block output):

- **M1. Placeholder integrity**: `count(target ⟦P:*⟧) == count(source ⟦P:*⟧)`. Diff reported on failure.
- **M2. L1 glossary compliance**: source terms with project-glossary mappings must appear with mapped translation in target. Exception: entries with `notes: context-dependent` are advisory only.

**SHOULD gates** (fail → warn but allow output, audit-trail flagged):

- **S1. Back-translation diff**: v2 → translate back to source language using a fresh LLM context (blind to original). Compare with original via embedding cosine similarity. Threshold: `< 0.85` warns. Transcreation mode: threshold relaxed to `< 0.70` (surface deviation expected).
- **S2. Register preservation**: LLM judge — does target register match intake-specified register? formal/neutral/warm/playful comparison.

**MAY gates** (info only, audit-trail flagged, NOT interactive — audit-only flag callers must continue without prompts):

- **I1. Untranslatability flagging**: source-analysis-flagged untranslatable phrases — record decision (borrow / explain / approximate) in audit trail. Does NOT block or prompt user; surfaces info for review.

### Layer 5: Output

- **a. Restore**: `⟦P:01⟧ → {{userName}}` token map applied
- **b. Format-write back** (per-skill):
  - i18n: original PO/JSON/XLIFF format preserved, keys intact
  - doc: markdown reassembled, code blocks pristine
  - creative: text (default 1 output); `--variants=N` flag opt-in for N alternative variants
  - `--audit-only` mode: diff report only, no rewrite
- **c. Audit trail JSON** (canonical schema in `audit-trail-spec.md`):
  - Intake: mode/register/strategy/locale/domain/intent
  - Glossary resolution per term (which tier hit, which source)
  - Chunk-level draft/reflect/improve outputs
  - Gate verdicts + warnings
  - Untranslatability decisions
  - Sources used (project glossary version, web search citations if any)

(Layer 5d translation memory update from earlier draft is deferred to v0.2 with re-trigger condition: when ≥3 users report cross-document drift in same repo.)

---

## Sub-skill Responsibility Matrix

| Skill | Layer 1 | Layer 2 | Layer 3 | Layer 4 | Layer 5 | web search default | back-trans default |
|---|---|---|---|---|---|---|---|
| `using-translation-toolkit` | route only | — | — | — | — | n/a | n/a |
| `translation-intake` | OWNS | — | — | — | — | n/a | n/a |
| `translation-i18n` | reads intake | PO/JSON/XLIFF/strings + strict placeholder | shared 4D | M1+M2 strict | format roundtrip | ON | SHOULD |
| `translation-doc` | reads intake | markdown AST + code/URL/HTML protect | shared 4D + windowing | M1+M2+S1+S2 | markdown roundtrip | ON | SHOULD |
| `translation-creative` | reads intake | brand brief intake | 5D (+effectiveness in transcreation mode) | M1+M2+S1 (MUST in transcreation, SHOULD in faithful)+S2 | text (+ optional `--variants=N`) | ON | MUST in transcreation mode, SHOULD in faithful mode |

**Audit-only mode**: each of the 3 active translation skills (`translation-i18n` / `-doc` / `-creative`) supports a `--audit-only` flag. With this flag, the skill takes `(source, existing-target)` instead of `(source)` and produces a 5-gate verification diff report instead of a translation. Replaces the earlier `translation-audit` skill from the draft (collapsed per fresh-eyes audit — no incremental capability over a flag, but full skill scaffolding cost).

(Glossary and typography rules used to be wrapped in a `translation-glossary` skill in an even earlier draft. Removed in favor of plugin-level `docs/glossary-format-spec.md` + `vendor/` LICENSE files + `scripts/canonical/` SoT, with each active skill holding its own functional copies — see Skill Self-Containment Guarantee above.)

Web search default = ON across all 3 active skills (per Q4.2 — "user invoked the tool because they want max quality"). Skills can be overridden to OFF via `--web-search=off` for cost/latency control. The router SKILL.md documents this trade-off in one paragraph (no per-skill duplicate file needed).

---

## Portability

### Roles, not models

Every SKILL.md describes **roles + behavioral constraints**, NEVER model names. Pattern source: existing `copywriting-toolkit` / `domain-teams` / `investing-toolkit` in this repo.

Roles defined:
- WRITER — produces draft, preserves placeholders
- CRITIC — structured critique only, no rewrites
- REVISER — consumes critique, outputs v2
- BACK-TRANSLATOR — blind retranslation v2 → source
- JUDGE — register / similarity verdicts

### Tool abstraction

External capabilities described by behavior, not tool name:

| Capability | Skill body wording | Runtime mapping |
|---|---|---|
| Web search | "if a web search capability is available, …" | CC: WebSearch / Gemini: google_web_search / Codex: browser |
| Subagent dispatch | "if subagent / task isolation is available, …" | CC: Agent tool / Gemini: sub-task / fallback: same-thread |
| File I/O | (Read tool — universal) | direct |

### Execution mode

**v0.1.0 ships single-thread only**: all roles run sequentially in the same context. This is the most portable mode (works on CC / Gemini / Codex identically) and avoids untested capability-detection branching.

Subagent / fresh-eyes parallel mode (CRITIC and BACK-TRANSLATOR running in independent contexts to amplify the "fresh-eyes effect") is deferred to v0.2 with re-trigger condition: when measurements show single-thread reflection consistently misses errors that subagent reflection catches. Until then, runtime branching is not implemented.

---

## Service Interface (Cross-skill)

Other skills (docs-team / copywriting-toolkit per user request / investing-team / arbitrary i18n tools) can invoke any of the 3 active translation skills via:

**Input contract** (4 fields):
```yaml
source_text:       string OR file path
source_locale:     BCP-47 (required, no auto)
target_locale:     BCP-47 (required)
glossary_path:     string (optional, default: <caller_repo>/docs/i18n/glossary-{tgt}.md)
web_search:        on (default) | off
```

(Earlier draft had `format_hint`, `intake_mode`, `tm_path`, `bypass_gates`, `source_locale: auto`. All cut per fresh-eyes audit: format is determined by skill choice; auto/explicit intake is interactive concern not service contract; TM is deferred; gate bypass is anti-pattern (per-gate flags if needed); locale auto-detect on short strings is unreliable.)

**Output contract**:
```yaml
translated_text:   string (or file path if format-roundtrip)
audit_trail:       JSON (per audit-trail-spec.md)
gate_verdicts:     {M1: PASS, M2: PASS, S1: WARN, S2: PASS, I1: INFO}
warnings:          [string]
untranslatables:   [{source_phrase, decision, alternatives}]
```

**Cross-plugin delegation contract** (per repo's CLAUDE.md):
- Caller passes paths, not content (except short inline strings)
- translation-toolkit reads its own files, decides chunking
- Gate verdicts flow back, never swallowed
- Caller cannot silent-override on gate failure — gate failure surfaces in `gate_verdicts` and caller must explicitly handle it
- translation-toolkit does not run caller's domain gates (e.g., copywriting-toolkit's ethics-check is not translation-toolkit's responsibility)

**Note on copywriting-toolkit**: Per user override, `copywriting-toolkit` will NOT auto-invoke `translation-toolkit`. Composition only when user explicitly requests, as the two represent orthogonal quality dimensions (translation quality ≠ copywriting quality).

---

## License & Attribution

**Plugin license**: MIT (consistent with other monkey-skills sub-plugins).

**Bundled attributions** (NOTICES.md) — split between glossary and parallel-corpus:

```
[Glossary entries — feeds glossary-{a}--{b}.md tables]
Source                  | License            | Attribution
------------------------|--------------------|--------------
Mozilla Pontoon TBX     | MPL-2.0/CC-BY-SA   | required
GNOME i18n glossary     | LGPL/GPL           | required
NAER 樂詞網             | OGDL v1 ≈ CC-BY 4.0| required
JLT 標準対訳辞書        | CC-BY 4.0 互換     | required
e-Stat 統計用語集       | 政府標準利用規約   | required
東京都 日英対訳         | CC-BY 4.0          | required
內閣官房 政府機關名     | 政府標準利用規約   | required

[Parallel-corpus reference — feeds corpus/nict-en-ja-zh.md as exemplars]
NICT 日英中基本文       | CC-BY 3.0          | required (5,304 sentence triples; not glossary entries)

[Typography rules — feeds typography/{jlreq,clreq}-summary.md meta-section]
W3C jlreq / clreq       | W3C Document Lic   | required
```

Each source's LICENSE file is bundled at plugin-level `vendor/<source>/LICENSE`.

**Optional fetch (NOT bundled)**:
- Microsoft Terminology Collection (~33k × 100+ langs) — `fetch-microsoft-terms.py`
- 特許庁 UTX (~130k EN-JA) — `fetch-jpo-utx.py` (requires format conversion + 出典明示)

Both download to `~/.cache/translation-toolkit/` on first user-invoked run.

---

## Decisions Locked

| # | Decision | Source |
|---|---|---|
| 1 | A_revised: standalone plugin, peer to copywriting-toolkit, NOT in domain-teams | User Q1 |
| 2 | 3 active translation skills (`translation-i18n` / `-doc` / `-creative`) + 1 router + 1 intake = 5 skills total. Format-routed pattern. Audit-only is a `--audit-only` flag on the 3 active skills, not a separate skill. (Earlier drafts had `translation-glossary` and `translation-audit` skills; both removed — glossary became plugin-level SoT + functional copies, audit became a flag.) | User Q2 + self-containment audit + fresh-eyes triage |
| 3 | 5 orthogonal axes (mode/register/strategy/locale/domain), exposed as auto/explicit binary | User Q3.1 |
| 4 | back-translation = SHOULD gate (MUST for transcreation only) | User Q3.2 |
| 5 | Roles, not models — no model names in skill body | User Q3.3 |
| 6 | Auto-discover + override glossary path. (Translation memory L2 deferred to v0.2 — see Out of Scope.) | (implied from Q3 setup) + fresh-eyes triage |
| 7 | Web search global ON by default for advanced quality | User Q4.2 |
| 8 | Bundle scope = S2-S3 via Q5.2-B + opt-in Microsoft + opt-in JPO UTX | User Q4.1 / Q5.2 |
| 9 | SSOT-and-functional-copy pattern (canonical/ + per-skill copies + CI drift check) | User Q5.1 (skill self-containment objection) |
| 10 | Uniform pair-file schema: every glossary file is `glossary-{lang-A}--{lang-B}.md` (BCP-47, alphabetical, double-hyphen). 5 pair files in v0.1.0. EN serves as runtime pivot fallback when a direct pair is unavailable, NOT as a schema concept. | User Q6.1-A + unification audit |
| 11 | 13 generic domain taxonomy (general/ui/tech.{software,web,data,crypto}/gov/legal/medical/finance/marketing/statistics/typography) | User Q6.2-A |
| 12 | All pair files use identical structure (frontmatter + `## meta` + `## domain: <name>` sections + 4-column tables). The `source` column distinguishes upstream-sourced / manual-curated / derived entries within the same file. | User unification audit |
| 13 | Wikidata runtime fallback deferred to v0.2 (was originally scoped to L4 web search; deferred per fresh-eyes triage — currently no implementation surface). | User scope-clarity push-back + fresh-eyes triage |
| 14 | Strict skill self-containment: `translation-glossary` skill removed; glossary / typography / shared references live as plugin-level `scripts/canonical/` SoT distributed as functional copies into each active skill. No skill reads another skill's files at runtime. No skill invokes another skill via Skill tool. | User self-containment audit |
| 15 | Fresh-eyes triage applied (2026-05-06). Cuts: `translation-audit` → `--audit-only` flag, L2 TM deferred, Wikidata deferred, subagent auto-detect deferred, service-interface fields trimmed (8→4), creative `--variants` opt-in (was always-3), per-skill `web-search-tradeoffs.md` collapsed, NICT moved from glossary to corpus reference (sentences ≠ term pairs). NOT cut (per user override): bundled glossary scope (kept S2-S3 = ~10K+ entries), 13 domains, S1/S2/I1 gate semantics, ja-JP↔zh-TW manual seed (~80-100), fetch-microsoft / fetch-jpo opt-in scripts. | dev-workflow:proposal-critique fresh-eyes audit + user "做滿不省略 glossary" override |

---

## Out of Scope (v0.1.0)

**Permanently out**:
- Streaming output (response is single shot per chunk)
- Real-time collaborative translation
- Voice / audio translation
- OCR / image translation
- Sub-segment alignment for legal-tier verification (e.g., MQM scoring)
- TBX / TMX import-export at runtime (only build-time)
- Style-guide PDFs (Microsoft / Apple) — license too gray

**Deferred to v0.2 with explicit re-trigger conditions** (per fresh-eyes triage 2026-05-06):
- **L2 translation memory tier** (`<repo>/.translations/memory-{src}-{tgt}.json` + Layer 5d update). Re-trigger: ≥3 users report cross-document translation drift in same repo.
- **Subagent auto-detect runtime branching** (CRITIC / BACK-TRANSLATOR in independent contexts). Re-trigger: measurements show single-thread reflection consistently misses errors that subagent reflection catches.
- **Wikidata runtime fallback** for entity/concept names. Re-trigger: users hit named-entity translation gaps that L1-L3 don't cover.
- **Creative variants always-on output** (currently `--variants=N` opt-in, default 1). Re-trigger: users consistently request variants by default.
- **Per-major-domain glossary file split** (e.g., `glossary-en-US--ja-JP-legal.md`). Re-trigger: any single pair file exceeds 1MB or 50K entries.

**Extensible — not in v0.1 scope but easy to add**:
- Additional locales beyond `ja-JP / zh-TW / zh-CN / en-US` (add via new `glossary-{lang-A}--{lang-B}.md` pair file)
- Additional domains beyond the 13 frozen at v0.1 (add to `domains_supported` frontmatter + new `## domain: <name>` section)

---

## Next Steps

1. User reviews this spec
2. Invoke `superpowers:writing-plans` to draft implementation plan
3. Plan will decompose into ordered commits (likely: scaffolding → glossary build pipeline → core skills → format adaptors → verification gates → CI drift check → docs)
