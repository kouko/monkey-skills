# Verification Gates — M1 / M2 / M3 / S1 / S2 / I1

**Status**: canonical reference (Single Source of Truth in `scripts/canonical/`; functional copies in active skills' `references/`)
**Cross-refs**: [`core-loop.md`](core-loop.md), [`4d-reflection.md`](4d-reflection.md), [`orthogonal-axes.md`](orthogonal-axes.md), [`audit-trail-spec.md`](audit-trail-spec.md)
**Spec source**: `docs/superpowers/specs/2026-05-06-translation-toolkit-design.md` §Layer 4: Verification

---

## Gate matrix overview

| ID | Name | Tier | Default behavior on fail | Mode-conditional |
|---|---|---|---|---|
| M1 | Placeholder integrity | MUST (HARD) | BLOCK output | — |
| M2 | Project glossary compliance | MUST (HARD) | BLOCK output (FAIL) or PASS_ADVISORY for `notes: context-dependent` entries | — |
| M3 | Deterministic post-translation linter (residual source / length-ratio / punctuation) | MUST (HARD) — composite of one HARD subrule (M3a) + two SHOULD subrules (M3b, M3c) | BLOCK output on M3a FAIL; WARN on M3b / M3c WARN | — |
| S1 | Back-translation diff | SHOULD (MUST in transcreation mode) | WARN (allow output) → BLOCK in transcreation | threshold + tier flip on `mode == transcreation` |
| S2 | Register preservation | SHOULD | WARN (allow output) | — |
| I1 | Untranslatability flagging | INFO (MAY) | INFO only — never blocks, never prompts | — |

**Tier semantics**:
- **MUST (HARD)**: failure blocks output. Caller's only recourse is fix the underlying issue and re-run. No `--bypass-gates` flag (anti-pattern per Decision #15 in design spec; per-gate flags considered if a real need surfaces).
- **SHOULD**: failure produces a WARN audit entry; output proceeds. Caller may inspect `gate_verdicts` and decide what to do.
- **MAY / INFO**: never blocks. Records information for the caller's review. **Non-interactive** — `translation-audit` and other non-interactive callers see the same INFO entry; no user prompt is ever raised.

---

## M1 — Placeholder Integrity (HARD GATE)

### Trigger
Runs on every chunk's v2 output, before Layer 5 placeholder restore.

### Pass criterion
```
count(target ⟦P:*⟧) == count(source ⟦P:*⟧)   # exact integer equality
{IDs in target} == {IDs in source}             # set equality (no missing, no extra, no duplicate)
```

### Pass / fail behavior
- **PASS** — placeholder set matches; proceed to Layer 5 restore
- **FAIL** — block output. Surface diff in `gate_verdicts.M1.diff` and via `warnings`.

### Diff format on failure
```yaml
gate_id: M1
verdict: FAIL
diff:
  source_count: 5
  target_count: 4
  source_ids: ["P:01", "P:02", "P:03", "P:04", "P:05"]
  target_ids: ["P:01", "P:02", "P:03", "P:05"]
  missing_in_target: ["P:04"]
  extra_in_target: []
  duplicated_in_target: []
metadata:
  chunk_index: 2
  source_chunk_excerpt: "Hello ⟦P:04⟧, your order is ready."
  target_chunk_excerpt: "你好，您的訂單已準備就緒。"
```

### Why HARD
Missing placeholder = broken software (missing variable substitution at runtime, broken inline link, lost code reference). Cannot be down-graded.

### Implementation note
M1 is regex-checkable; no LLM judge needed. Cheap and deterministic.

---

## M2 — Project Glossary Compliance (HARD GATE)

### Trigger
Runs on every chunk's v2 output, after L1 (project glossary) terms have been resolved. Source-side terms with L1 mappings in the active domain that appear in the source are checked against the target.

### Pass criterion
For each source term `T_s` with L1 mapping `T_t` for the active domain:
- The mapped target form `T_t` (or a documented variant — see exception below) appears in the target.

### Pass / fail / pass_advisory behavior
- **PASS** — every L1-mandated source term has its mapped target form rendered correctly
- **FAIL** — at least one L1 source term has its mapping ignored AND the entry is not flagged `notes: context-dependent`. Block output.
- **PASS_ADVISORY** — only `notes: context-dependent` entries deviated; the deviation is recorded but does not block. The caller can inspect `gate_verdicts.M2.advisory` for review.

### Exception — context-dependent entries
Glossary entries with `notes: context-dependent` (e.g., `key` in some domains; verbs that admit multiple targets) are **advisory** — the gate records deviations from the mapped form but does not fail.

### Diff format on failure
```yaml
gate_id: M2
verdict: FAIL
diff:
  violations:
    - term: "key"
      domain: "tech.crypto"
      project_glossary: "暗号鍵"
      target_used: "鍵"
      tier: "L1"
      audit_path: "direct"
      chunk_index: 0
      severity: "fail"
  advisories: []
metadata:
  project_glossary_path: "/path/to/repo/docs/i18n/glossary-ja-JP.md"
  project_glossary_version: "0.3.2"
```

### PASS_ADVISORY example
```yaml
gate_id: M2
verdict: PASS_ADVISORY
diff:
  violations: []
  advisories:
    - term: "engagement"
      project_glossary: "エンゲージメント"
      target_used: "関与度"
      notes: "context-dependent"
      chunk_index: 1
      severity: "advisory"
metadata:
  ...
```

### Why HARD (with advisory escape)
Project glossary is the user's repo-specific authority — the consistency mechanism within a repo. Bypassing it breaks the user's QA/style invariants.

### Known limitations (v0.1)

- **Negation/composition false negatives.** M2 uses substring matching, so an expected translation like `確認` would falsely PASS if the target contains `未確認` ("not confirmed") — the literal characters appear, but the meaning is reversed by the negation prefix. Negation detection (`未`, `非`, `不`, `無` ...) requires NLP beyond simple string matching and is deferred to v0.2. For legal / medical translation work, an additional human-review pass is recommended.
- **Source-side scope detection.** ASCII glossary terms (e.g. `cancel`) use word-boundary regex matching against the source, so `cancel` does NOT trigger the rule when the source says `cancellation`. CJK glossary terms (e.g. `取消`) use plain substring matching because CJK scripts have no whitespace word boundaries — `取消` IS considered in scope when the source contains `取消按鈕`. Deliberate trade-off: word-boundary semantics for the script that has them, substring fallback for the script that doesn't.

---

## S1 — Back-translation Diff (SHOULD; MUST in transcreation)

### Trigger
Runs on the assembled v2 (post-restore not required — embedding similarity is computed on the masked or unmasked form consistently). Requires **subagent dispatch capability** for blindness — the back-translation must run in a context that has not seen the source.

### Pass criterion
1. Dispatch a subagent: translate v2 from `target_locale` back to `source_locale`. Subagent input is **only** the v2 text and the locale pair — **no original source provided**.
2. Compute embedding cosine similarity between back-translation and original source. (Embedding model: any sentence-embedding model available to the runtime; consistent within a single run.)
3. Compare to threshold:
   - `mode ∈ {literal, faithful, localized}` → threshold = **0.85**
   - `mode == transcreation` → threshold = **0.70** (relaxed; surface deviation expected)

### Pass / warn / skipped behavior
- **PASS** — similarity ≥ threshold
- **WARN** — similarity < threshold (output proceeds; warning surfaced); in transcreation mode this becomes **FAIL** because S1 is promoted to MUST
- **SKIPPED** — runtime provides no subagent / task-isolation capability. Audit-trail flag set; M1 / M2 / S2 / I1 continue normally.

### Mode-conditional tier flip
- Default tier = SHOULD across modes
- `mode == transcreation` → tier promoted to **MUST**. A back-translation that drops below 0.70 in transcreation indicates the v2 has drifted off-topic, not just been re-styled. This blocks output.

### Audit-trail format
```yaml
gate_id: S1
verdict: PASS | WARN | FAIL | SKIPPED
diff:
  similarity: 0.78
  threshold: 0.85
  back_translation: "Hello, your order has been prepared."
  original_source: "Hello, your order is ready."
metadata:
  embedding_model: "(runtime-supplied — recorded for reproducibility)"
  subagent_dispatch: "Agent tool"        # or "Gemini sub-task" / "..."  / null if SKIPPED
  isolation_capability: true             # false → SKIPPED
  mode: faithful
  tier_applied: SHOULD
```

### When SKIPPED
If the runtime cannot provide a fresh-context subagent, S1 cannot guarantee blindness — running the back-translation in the main context would leak the original source into the comparison input, making the gate meaningless. The gate gracefully skips with `verdict: SKIPPED` and a `warnings` entry. **In transcreation mode, SKIPPED is itself a quality concern** because S1 is the primary semantic-fidelity gate when surface deviation is expected — the warning is more prominent but still does not block (because no graceful-skip alternative exists). The user should re-run on a runtime that supports isolation if transcreation quality matters.

### Implementation note
Subagent dispatch capability per [`core-loop.md`](core-loop.md) — design spec §Execution context per layer. Runtime mappings: Claude Code Agent tool / Gemini sub-task / etc. Skill body wording: "if subagent / task isolation is available, …".

---

## S2 — Register Preservation (SHOULD)

### Trigger
Runs on the assembled v2 (per chunk or document-wide).

### Pass criterion
LLM judge compares target register against the intake-specified register (`formal | neutral | warm | playful`). Judge prompt is structured: the judge classifies the target register and compares to expected.

### Pass / warn behavior
- **PASS** — judged register matches intake
- **WARN** — judged register diverges; output proceeds, warning recorded

### Audit-trail format
```yaml
gate_id: S2
verdict: PASS | WARN
diff:
  expected_register: formal
  judged_register: neutral
  rationale: "draft uses です・ます but lacks 敬語 / 謙譲語 forms expected for the formal-register intake"
metadata:
  judge_role: "JUDGE"
  judged_chunks: [0, 1, 2]
  judged_overall: "neutral"
```

### When to trust S2
S2 is an LLM judge call — subjective by nature. Treat WARN as a flag for human review rather than a definitive failure. S2 is most reliable on register categories with strong surface markers (formal vs playful) and least reliable on neighboring categories (neutral vs warm).

---

## I1 — Untranslatability Flagging (INFO only — non-interactive)

### Trigger
Runs after Layer 2 source analysis flags untranslatable phrases (puns, culture memes, idiom-without-equivalent). For each flagged phrase, I1 records the v2's chosen handling.

### Pass criterion
None — I1 is informational. Always emits an INFO audit entry; never blocks, never warns, never prompts the user.

### Detected handling categories
- **borrow** — source phrase preserved as-is in target (with optional gloss / parenthetical)
- **explain** — source phrase replaced with explanatory paraphrase
- **approximate** — source phrase replaced with target-culture nearest-equivalent (often a different idiom with similar function)

### Audit-trail format
```yaml
gate_id: I1
verdict: INFO
diff: null
metadata:
  untranslatables:
    - source_phrase: "御朱印"
      decision: "borrow"
      target_rendering: "御朱印 (goshuin — temple/shrine seal stamp)"
      alternatives:
        - approximate: "temple stamp"
        - explain: "a hand-inked seal collected as proof of pilgrimage"
    - source_phrase: "It's raining cats and dogs."
      decision: "approximate"
      target_rendering: "土砂降りだ。"
      alternatives:
        - borrow: "It's raining cats and dogs.（猫と犬が降る — 大雨を意味する英語の慣用句）"
        - explain: "雨が激しく降っている"
```

### Why INFO and non-interactive
- The gate's job is to surface **decisions** for the audit trail, not to make them. The decision was made by IMPROVE; I1 just records it.
- **Non-interactive** is a hard requirement — `translation-audit` and other non-interactive callers must continue without user prompts. Per [design spec Layer 4](../docs/superpowers/specs/2026-05-06-translation-toolkit-design.md): "I1 ... does NOT block or prompt user; surfaces info for review."
- The `alternatives` field gives the reader other reasonable handlings without forcing a re-run.

---

## M3 — Deterministic Post-Translation Linter (HARD GATE — composite)

### Trigger
Runs on the assembled v2 output after Layer 5 placeholder restore, **between M2 and S1**. M3 is deterministic (no LLM judge) and short-circuits S1 when the output is structurally broken — saving the cost of a blind back-translation that would be meaningless on broken output.

M3 is a **composite** gate: one HARD subrule (M3a) plus two SHOULD subrules (M3b, M3c). The aggregate verdict follows the standard pipeline rule — any HARD subrule FAIL → M3 FAIL; otherwise any SHOULD WARN → M3 WARN; otherwise PASS.

### Subrules

| Subrule | Tier | Pass criterion |
|---|---|---|
| **M3a** Residual source-language characters | HARD | Target contains < 1% source-language script chars. Computed as `count(source_script_chars in target) / count(non_whitespace_chars in target)`. Source-script class derived from BCP-47 source-locale prefix (`ja-*` → Hiragana / Katakana / CJK Ideographs / CJK Symbols & Punctuation; `zh-*` → CJK Ideographs / CJK Symbols & Punctuation). Threshold tunable per `(source_locale, target_locale)` pair via `_LOCALE_PAIR_THRESHOLDS` in `scripts/lib/gate_m3_problem_analyze.py` (default 0.01). |
| **M3b** Length-ratio sanity | SHOULD | `approx_tokens(target) / approx_tokens(source)` ∈ `[low, high]` where `(low, high)` defaults to `(0.5, 2.5)` and is tunable per locale pair via `_LOCALE_PAIR_LENGTH_RATIO`. Uses `scripts.lib.scene_chunker.approx_tokens` (char/3 heuristic). |
| **M3c** Punctuation convention | SHOULD | For CJK targets (`zh-*` / `ja-*`): fullwidth ratio across `{,/，, ./。, ?/？, !/！}` ≥ 0.8, per JLReq / CLReq fullwidth-as-default convention. ASCII / other targets: skipped (returns PASS). `ko-*` is treated as non-CJK for M3c — Korean prose does not require fullwidth ASCII punctuation. |

### Pass / fail / warn behavior
- **PASS** — all three subrules pass.
- **WARN** — at least one SHOULD subrule (M3b or M3c) reported WARN AND no HARD subrule failed. Output proceeds; warnings recorded.
- **FAIL** — M3a reported FAIL (HARD). Output blocked. The aggregate is FAIL even if M3b / M3c also reported WARN — HARD dominates SHOULD.

### Diff format on failure
```yaml
gate_id: M3
verdict: FAIL  # or WARN / PASS
subrules:
  - subrule: m3a
    verdict: FAIL
    tier: HARD
    metric: 0.04           # residual ratio
    threshold: 0.01
    detail: "residual source-script ratio 0.04 >= threshold 0.01 (ja-JP -> en-US); 8 of 200 non-whitespace target chars belong to the source-language script — likely partial translation"
  - subrule: m3b
    verdict: WARN
    tier: SHOULD
    metric: 0.30
    threshold: 0.50
    detail: "length ratio 0.30 outside [0.50, 2.50] — too short (en-US -> de-DE); src_tokens=100, tgt_tokens=30"
  - subrule: m3c
    verdict: PASS
    tier: SHOULD
    metric: 1.00
    threshold: 0.80
    detail: "target locale 'en-US' is not CJK; fullwidth punctuation check skipped (PASS by default per JLReq/CLReq scope)"
metadata:
  source_locale: ja-JP
  target_locale: en-US
  chunk_index: 2
```

### Why HARD (with WARN escape on length / punctuation)

- **M3a is HARD** because residual source-language chars in the target indicate a *partial translation* — the model gave up and pasted source text through. This is a structural failure indistinguishable from a missing placeholder: surface looks plausible but the target is broken. No advisory escape.
- **M3b is SHOULD** because length-ratio anomalies are real signals but admit legitimate exceptions (intentional summary; fixed-length UI; transcreation reframing). WARN lets a translator inspect rather than force a re-run.
- **M3c is SHOULD** because punctuation convention is style, not correctness. JLReq / CLReq are typographic conventions; some venues legitimately use halfwidth punctuation in CJK technical contexts (e.g. inline code-fenced terminals). WARN flags the deviation; output proceeds.

### Implementation note
M3 is fully deterministic — no LLM judge call, no embedding similarity. Cheap to run on every chunk. The lib lives at `scripts/lib/gate_m3_problem_analyze.py`; the public entry point is `evaluate_m3(*, source_text, target_text, source_locale, target_locale) -> M3Verdict`. The verdict shape is a frozen dataclass (`M3Verdict` with `subrules: list[M3SubruleVerdict]`) rather than the dict shape used by M1 / M2 / S1 / S2 / I1 — callers convert to the uniform `{verdict, diff, details}` shape at the per-skill audit-trail integration boundary.

Inspired by GalTransl's `problemAnalyze` pattern. M3 short-circuits S1: if M3a FAILs, the back-translation will be meaningless on partial output, so the runtime should record M3 FAIL and skip S1 dispatch to save cost (per Tier 2 plan §Phase A pipeline order).

---

## Per-skill gate application

(From design spec §Sub-skill Responsibility Matrix; updated for v0.3.0 Tier 2 Decision H — translation-doc + translation-novel adopt M3.)

| Skill | Gates run |
|---|---|
| `translation-i18n` | M1 + M2 (strict) |
| `translation-doc` | M1 + M2 + **M3** + S1 + S2 |
| `translation-novel` | M1 + M2 + **M3** + S1 (MUST in transcreation, SHOULD in faithful) + S2 + I1 |
| `translation-creative` | M1 + M2 + S1 (MUST in transcreation, SHOULD in faithful) + S2 |
| `translation-audit` | full M1 + M2 + S1 + S2 + I1, gate semantics typically stricter |

`translation-i18n` skips S1/S2 because UI strings are too short for back-translation similarity to be meaningful and are register-pinned by format conventions. It also skips M3 because length-ratio is uninformative on UI strings (a 3-character button label has wide legitimate ratios) and most UI strings carry no punctuation.

`translation-creative` skips M3 because transcreation legitimately produces wide length-ratio swings (ad copy is rewritten, not translated literally) — a future v0.4 may add M3 with mode-conditional skip of M3b when `mode == transcreation`.

`translation-audit` does not re-run M3 on a downstream artifact: when audit reads a translation produced by `translation-doc` / `translation-novel`, M3 has already executed upstream and its verdict is in the audit trail. Re-running would be redundant.

---

## Audit-trail entry format (per gate, uniform shape)

Every gate emits an entry into `audit_trail.gate_verdicts.<id>` with this shape:

```yaml
gate_id: M1 | M2 | M3 | S1 | S2 | I1
verdict: PASS | FAIL | WARN | PASS_ADVISORY | SKIPPED | INFO
diff: <gate-specific structured diff, null when PASS or INFO>
metadata: <gate-specific>
```

M3 is the only composite gate — its audit entry additionally carries a `subrules` list with per-subrule (m3a / m3b / m3c) verdicts. The aggregate `verdict` follows the HARD-dominates-SHOULD rule documented in §M3.

See [`audit-trail-spec.md`](audit-trail-spec.md) §`gate_verdicts` for how these are nested in the full audit trail and §Appendix for an end-to-end example.

---

## Verdict legend (consistent across gates)

| Verdict | Meaning | Output proceeds? |
|---|---|---|
| `PASS` | Gate passed cleanly | yes |
| `PASS_ADVISORY` | Passed; advisory deviation recorded (M2 context-dependent only) | yes |
| `WARN` | SHOULD gate failed; output proceeds with warning | yes |
| `FAIL` | HARD gate failed (or S1 in transcreation mode) | **no — output blocked** |
| `SKIPPED` | Gate could not run (runtime capability missing — S1 only) | yes |
| `INFO` | Informational record (I1 only) | yes |

---

## Anti-patterns

- **Bypass flags as escape hatches**. There is no `--bypass-gates`. Per-gate flags are considered only if real users hit real false-positive cases that cannot be fixed at the gate-logic level. Today: no such flag exists.
- **LLM-judge-only HARD gates**. M1 and M2 are deterministic (regex / glossary lookup) — never LLM-judged for HARD verdicts. LLM judges (S2) only emit SHOULD-tier verdicts because their reliability is subjective.
- **Silently dropping S1 in transcreation when SKIPPED**. The skip is loud — surfaced in `warnings` and in `gate_verdicts.S1.metadata.isolation_capability: false`. The caller cannot pretend S1 ran.
- **Caller-side gate verdict swallowing**. Per cross-plugin delegation contract (repo CLAUDE.md): gate verdicts flow back to caller; caller must explicitly handle them. No silent override on FAIL.
