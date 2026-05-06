# Audit Trail — Schema and Examples

**Status**: canonical reference (Single Source of Truth in `scripts/canonical/`; functional copies in active skills' `references/`)
**Cross-refs**: [`core-loop.md`](core-loop.md), [`4d-reflection.md`](4d-reflection.md), [`5d-effectiveness.md`](5d-effectiveness.md), [`orthogonal-axes.md`](orthogonal-axes.md), [`verification-gates.md`](verification-gates.md)

---

## Purpose

The audit trail is the canonical, machine-readable record of one translation run. It is emitted as JSON by the `translation-{i18n,doc,creative,audit}` skills as part of their output contract (per design spec §Service Interface), alongside the translated text and gate verdicts.

Goals:
1. **Reproducibility** — what intake values were used? what glossary versions were active? what web-search citations were consulted?
2. **Diagnosis** — when a translation looks wrong, the audit trail tells you which tier supplied each term, which gate flagged what, and what untranslatability decisions were made.
3. **Inter-skill consistency** — every active skill emits the same schema so callers can ingest uniformly.
4. **Debugging gate failures** — gate-specific `diff` and `metadata` fields surface actionable detail.

---

## Top-level schema

```json
{
  "version": "0.1.0",
  "timestamp": "ISO 8601",
  "intake": {
    "mode": "literal | faithful | localized | transcreation",
    "register": "formal | neutral | warm | playful",
    "strategy": "domestication | foreignization",
    "source_locale": "BCP-47",
    "target_locale": "BCP-47",
    "domain": "<single value from 13-domain taxonomy>",
    "intent": "free-form short string (skopos hint)",
    "inferred": {
      "mode": true,
      "register": false,
      "strategy": true,
      "domain": true
    },
    "inferred_values": {
      "mode": "faithful"
    }
  },
  "glossary_resolution": [
    {
      "term": "...",
      "tier": "L1 | L2 | L3 | L4",
      "source": "...",
      "value": "...",
      "audit_path": "direct | pivot.en-US | web | llm-fallback"
    }
  ],
  "chunks": [
    {
      "index": 0,
      "source": "...",
      "draft": "...",
      "reflect": { "accuracy": [], "fluency": [], "style": [], "terminology": [], "effectiveness": [] },
      "improve": "..."
    }
  ],
  "gate_verdicts": {
    "M1": { "verdict": "PASS | FAIL", "diff": null, "details": {} },
    "M2": { "verdict": "PASS | FAIL | PASS_ADVISORY", "diff": null, "details": {} },
    "S1": { "verdict": "PASS | WARN | FAIL | SKIPPED", "diff": null, "details": {} },
    "S2": { "verdict": "PASS | WARN", "diff": null, "details": {} },
    "I1": { "verdict": "INFO", "diff": null, "details": {} }
  },
  "untranslatables": [
    {
      "source_phrase": "...",
      "decision": "borrow | explain | approximate",
      "target_rendering": "...",
      "alternatives": [{ "decision": "...", "rendering": "..." }]
    }
  ],
  "sources_used": {
    "glossary": ["pontoon", "gnome", "<repo>/docs/i18n/glossary-ja-JP.md"],
    "web_search": ["https://wikipedia.org/wiki/Foo"],
    "corpus": ["nict-aspec"]
  },
  "warnings": ["..."]
}
```

---

## Field reference

### `version`
Audit-trail schema version. Lets future readers handle schema evolution. v0.1.0 ships as `"0.1.0"`.

### `timestamp`
ISO 8601 timestamp of the run start (UTC recommended).

### `intake`

The 5 axes plus `intent`. `inferred` is a per-axis boolean indicating whether the value came from auto-inference (`true`) or user override (`false`). `inferred_values` records what auto-inference would have chosen even when the user overrode it — useful for retrospective analysis of where heuristics misfire. Populated via `AuditTrailBuilder.add_inferred_value(axis, value)`.

- `mode`: see [`orthogonal-axes.md`](orthogonal-axes.md) §Axis 1
- `register`: see §Axis 2
- `strategy`: see §Axis 3
- `source_locale` / `target_locale`: BCP-47, both required
- `domain`: a single value from the v0.1.0 frozen 13-domain taxonomy. Callers needing to express multiple domains in v0.1 may comma-join (e.g., `"ui,tech.software"`); a structured array form is deferred to a later schema version.
- `intent`: free-form skopos hint ("user-facing onboarding doc", "marketing email subject line variants", etc.)
- `inferred.{axis}`: `true` if value came from auto-inference; `false` if user-supplied
- `inferred_values.{axis}`: the value auto-inference *would* have chosen for that axis. Recorded only when the caller wants to capture the heuristic's choice (typically when the user overrode it in explicit mode). Empty `{}` when not in use.

### `glossary_resolution`

One entry per **distinct source-side term** that was looked up (not per occurrence — distinct terms only). Records which tier supplied the value.

- `term`: the source-side term as found in source text
- `tier`:
  - `L1` — project glossary (`<repo>/docs/i18n/glossary-{tgt}.md`)
  - `L2` — bundled glossary (skill's functional copy of `glossary-{lang-A}--{lang-B}.md`)
  - `L3` — web search (default ON; `--web-search=off` to disable)
  - `L4` — LLM fallback (no reference material; flagged in `warnings`)
- `source`: source attribution within the tier (e.g., `pontoon`, `gnome`, `jlt`, `manual`, `derived`, web-citation URL, or `llm-fallback`)
- `value`: the chosen target term
- `audit_path`:
  - `direct` — found in direct pair file
  - `pivot.en-US` — pivoted via en-US pair files
  - `web` — web search hit
  - `llm-fallback` — no reference material; LLM produced the rendering on its own

### `chunks`

One entry per chunk. Index aligns with chunk order. Each entry records the **full intermediate state** for that chunk:

- `index`: integer, 0-based
- `source` (optional): original source chunk text (for traceability; pre-protect-pass placeholders unmasked, post-protect-pass placeholders masked depending on what the implementer records — see implementation note). Pass via `AuditTrailBuilder.add_chunk(..., source=...)`; omit when not needed (the key is then absent from the entry).
- `draft`: writer's v1 output
- `reflect`: critic's structured JSON (4D or 5D depending on mode)
- `improve`: reviser's v2 output

Implementation note: implementations may record the post-protect-pass form (with `⟦P:NN⟧` masks visible) so the audit trail is portable across formats. Final user-facing output uses the post-restore form.

### `gate_verdicts`

One entry per gate (M1 / M2 / S1 / S2 / I1). Each entry has the **uniform shape** described in [`verification-gates.md`](verification-gates.md):

```yaml
verdict: PASS | FAIL | WARN | PASS_ADVISORY | SKIPPED | INFO
diff: <gate-specific structured diff; null when PASS or INFO>
details: <gate-specific structured detail dict; null when not provided>
```

See [`verification-gates.md`](verification-gates.md) for per-gate schemas (`M1.diff`, `M2.diff`, `S1.diff`, `S2.diff`, `I1.details.untranslatables`).

### `untranslatables`

Top-level mirror of `gate_verdicts.I1.details.untranslatables` for caller convenience — same data, same shape. Callers that only consume the audit trail (not the gate verdicts) can read this field directly.

- `source_phrase`: the flagged phrase
- `decision`: the handling chosen (`borrow | explain | approximate`)
- `target_rendering` (optional): how it was rendered in v2 (e.g., borrowed verbatim, paraphrased, footnote). Pass via `AuditTrailBuilder.add_untranslatable(..., target_rendering=...)`; omit when not needed (the key is then absent).
- `alternatives`: other reasonable handlings the LLM considered

### `sources_used`

Tracks data-provenance for reproducibility as a flat `{category: [source_id, ...]}` map. Within each category, source IDs are **deduplicated in insertion order** (first occurrence wins; subsequent duplicates are no-ops). Populated via `AuditTrailBuilder.add_source_used(category, source_id)`.

Standard v0.1 categories:

- `glossary`: glossary sources consumed (e.g., `"pontoon"`, `"gnome"`, `"jlt"`, or a path string like `"<repo>/docs/i18n/glossary-ja-JP.md"` for the project glossary)
- `web_search`: L3 web-search citations as URLs (e.g., `"https://wikipedia.org/wiki/Foo"`). Empty if `--web-search=off` or no L3 hits.
- `corpus`: parallel-corpus / bilingual-text sources consumed (e.g., `"nict-aspec"`)

For v0.1 `web_search` stores citation URLs only (`add_source_used("web_search", "<url>")`). Rich citation objects (`{term, url, snippet}`) are deferred to v0.2.

Glossary version pinning (formerly recorded under `project_glossary_version` / `bundled_glossary_versions`) is deferred to v0.2; for v0.1 record the path or short identifier in `sources_used.glossary` and surface version mismatches in `warnings`.

### `warnings`

Free-form array of human-readable strings surfacing notable events:
- `"S1 gate SKIPPED: runtime does not support subagent isolation"`
- `"L4 LLM-fallback used for term '<term>' (no reference material found)"`
- `"glossary version mismatch: project glossary v0.4.0 expected v0.3.0"`

Warnings are duplicated from gate-specific `details` and `diff` fields where applicable, so callers reading only `warnings` get a usable summary.

---

## Appendix — End-to-end example

A complete audit trail for a small en-US → ja-JP translation in faithful mode of the source:

> "Click the **Cancel** button to discard your changes."

(The `**Cancel**` markdown emphasis becomes `⟦P:01⟧` after protect-pass.)

```json
{
  "version": "0.1.0",
  "timestamp": "2026-05-06T14:23:11Z",

  "intake": {
    "mode": "faithful",
    "register": "neutral",
    "strategy": "domestication",
    "source_locale": "en-US",
    "target_locale": "ja-JP",
    "domain": "ui,tech.software",
    "intent": "in-app help text for a SaaS settings page",
    "inferred": {
      "mode": true,
      "register": true,
      "strategy": true,
      "domain": true
    },
    "inferred_values": {}
  },

  "glossary_resolution": [
    {
      "term": "Cancel",
      "tier": "L2",
      "source": "gnome",
      "value": "キャンセル",
      "audit_path": "direct"
    },
    {
      "term": "button",
      "tier": "L2",
      "source": "pontoon",
      "value": "ボタン",
      "audit_path": "direct"
    },
    {
      "term": "discard",
      "tier": "L1",
      "source": "project-glossary-v0.3.2",
      "value": "破棄する",
      "audit_path": "direct"
    },
    {
      "term": "changes",
      "tier": "L1",
      "source": "project-glossary-v0.3.2",
      "value": "変更内容",
      "audit_path": "direct"
    }
  ],

  "chunks": [
    {
      "index": 0,
      "source": "Click the ⟦P:01⟧ button to discard your changes.",
      "draft": "⟦P:01⟧ ボタンをクリックして変更内容を破棄してください。",
      "reflect": {
        "accuracy":    [],
        "fluency":     [],
        "style":       [],
        "terminology": []
      },
      "improve": "⟦P:01⟧ ボタンをクリックして変更内容を破棄してください。"
    }
  ],

  "gate_verdicts": {
    "M1": {
      "verdict": "PASS",
      "diff": null,
      "details": {
        "source_count": 1,
        "target_count": 1,
        "ids": ["P:01"]
      }
    },
    "M2": {
      "verdict": "PASS",
      "diff": null,
      "details": {
        "checked_terms": ["discard", "changes"],
        "project_glossary_path": "/repo/docs/i18n/glossary-ja-JP.md",
        "project_glossary_version": "0.3.2"
      }
    },
    "S1": {
      "verdict": "SKIPPED",
      "diff": null,
      "details": {
        "subagent_dispatch": null,
        "isolation_capability": false,
        "reason": "translation-i18n does not run S1 by design (UI-string scope)"
      }
    },
    "S2": {
      "verdict": "PASS",
      "diff": null,
      "details": {
        "expected_register": "neutral",
        "judged_register": "neutral",
        "judge_role": "JUDGE"
      }
    },
    "I1": {
      "verdict": "INFO",
      "diff": null,
      "details": {
        "untranslatables": []
      }
    }
  },

  "untranslatables": [],

  "sources_used": {
    "glossary": [
      "gnome",
      "pontoon",
      "/repo/docs/i18n/glossary-ja-JP.md"
    ]
  },

  "warnings": []
}
```

---

## Appendix — Transcreation example with S1 WARN

Same shape, but for a transcreation run where S1 fired:

> Source (en-US, marketing CTA): "Stop wasting time. Get organized in 5 minutes. Try Notion free."
> Target (ja-JP, transcreation): "「時間がない」を、終わりにする。Notion なら、5分で仕事が整う。いますぐ無料で始める。"

(See [`5d-effectiveness.md`](5d-effectiveness.md) §Concrete example for the critique and improve trace.)

```json
{
  "version": "0.1.0",
  "timestamp": "2026-05-06T15:01:42Z",

  "intake": {
    "mode": "transcreation",
    "register": "warm",
    "strategy": "domestication",
    "source_locale": "en-US",
    "target_locale": "ja-JP",
    "domain": "marketing",
    "intent": "landing-page hero CTA for productivity SaaS",
    "inferred": {
      "mode": true,
      "register": true,
      "strategy": true,
      "domain": true
    },
    "inferred_values": {}
  },

  "glossary_resolution": [
    {
      "term": "Notion",
      "tier": "L4",
      "source": "llm-fallback",
      "value": "Notion",
      "audit_path": "llm-fallback"
    }
  ],

  "chunks": [
    {
      "index": 0,
      "source": "Stop wasting time. Get organized in 5 minutes. Try Notion free.",
      "draft": "時間を無駄にしないでください。5分で整理整頓しましょう。Notion を無料でお試しください。",
      "reflect": {
        "accuracy":      [],
        "fluency":       [],
        "style":         [
          {"issue": "register too flat / over-polite for marketing CTA",
           "suggestion": "lean into JP DR-copy hook conventions"}
        ],
        "terminology":   [],
        "effectiveness": [
          {"issue": "'Stop wasting time' as 「時間を無駄にしないでください」 is grammatically polite but rhetorically flat",
           "suggestion": "rework as pain-question: 「もう、時間に追われない。」 or 「『時間がない』を、終わりにする。」"},
          {"issue": "'Get organized in 5 minutes' as 「5分で整理整頓しましょう」 — 整理整頓 reads as housework / KonMari, not productivity",
           "suggestion": "「5分で、仕事が整う。」"},
          {"issue": "CTA 'Try Notion free' as 「無料でお試しください」 — passive, expected, low conversion",
           "suggestion": "「いますぐ無料で始める」"}
        ]
      },
      "improve": "「時間がない」を、終わりにする。Notion なら、5分で仕事が整う。いますぐ無料で始める。"
    }
  ],

  "gate_verdicts": {
    "M1": {
      "verdict": "PASS",
      "diff": null,
      "details": { "source_count": 0, "target_count": 0, "ids": [] }
    },
    "M2": {
      "verdict": "PASS",
      "diff": null,
      "details": { "checked_terms": [], "project_glossary_path": null }
    },
    "S1": {
      "verdict": "PASS",
      "diff": {
        "similarity": 0.74,
        "threshold": 0.70,
        "back_translation": "Put an end to 'I have no time'. With Notion, your work gets organized in 5 minutes. Get started free now.",
        "original_source": "Stop wasting time. Get organized in 5 minutes. Try Notion free."
      },
      "details": {
        "embedding_model": "(runtime-supplied)",
        "subagent_dispatch": "Agent tool",
        "isolation_capability": true,
        "mode": "transcreation",
        "tier_applied": "MUST"
      }
    },
    "S2": {
      "verdict": "PASS",
      "diff": null,
      "details": {
        "expected_register": "warm",
        "judged_register": "warm",
        "judge_role": "JUDGE"
      }
    },
    "I1": {
      "verdict": "INFO",
      "diff": null,
      "details": {
        "untranslatables": []
      }
    }
  },

  "untranslatables": [],

  "sources_used": {
    "glossary": ["pontoon"]
  },

  "warnings": [
    "L4 LLM-fallback used for term 'Notion' (proper noun; preserved as-is — expected behavior)"
  ]
}
```

Note: in this transcreation example S1 PASSED at 0.74 against the relaxed 0.70 threshold. If similarity had been 0.65, the verdict would have been `FAIL` (not `WARN`) because S1 is MUST in transcreation mode — output would have been blocked.

---

## Implementation guidance

- **Emit JSON, not YAML**, for the actual on-disk audit trail. YAML in this document is only for readability of nested examples in `gate_verdicts.{id}.diff` snippets within [`verification-gates.md`](verification-gates.md).
- **Keep `chunks` at full fidelity**. The intermediate draft / reflect / improve are the most useful diagnostic artifact when a translation looks wrong; do not truncate them.
- **`reflect` is the verbatim critic JSON** — same structure as the role's output. If the run was 4D, omit the `effectiveness` key; if 5D, include it.
- **Path normalization**: `project_glossary_path` should be recorded as the path the run actually opened. If the project glossary was auto-discovered at `<caller_repo>/docs/i18n/glossary-ja-JP.md`, record that absolute or repo-relative path consistently.
- **Schema evolution**: the `version` field is required. v0.2.x will introduce new fields (e.g., translation-memory tier hits, Wikidata fallbacks); consumers should ignore unknown fields rather than fail.
