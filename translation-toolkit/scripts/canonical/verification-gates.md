# Verification Gates — M1 / M2 / S1 / S2 / I1

**Status**: canonical reference (Single Source of Truth in `scripts/canonical/`; functional copies in active skills' `references/`)
**Cross-refs**: [`core-loop.md`](core-loop.md), [`4d-reflection.md`](4d-reflection.md), [`orthogonal-axes.md`](orthogonal-axes.md), [`audit-trail-spec.md`](audit-trail-spec.md)
**Spec source**: `docs/superpowers/specs/2026-05-06-translation-toolkit-design.md` §Layer 4: Verification

---

## Gate matrix overview

| ID | Name | Tier | Default behavior on fail | Mode-conditional |
|---|---|---|---|---|
| M1 | Placeholder integrity | MUST (HARD) | BLOCK output | — |
| M2 | Project glossary compliance | MUST (HARD) | BLOCK output (FAIL) or PASS_ADVISORY for `notes: context-dependent` entries | — |
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

## Per-skill gate application

(From design spec §Sub-skill Responsibility Matrix)

| Skill | Gates run |
|---|---|
| `translation-i18n` | M1 + M2 (strict) |
| `translation-doc` | M1 + M2 + S1 + S2 |
| `translation-creative` | M1 + M2 + S1 (MUST in transcreation, SHOULD in faithful) + S2 |
| `translation-audit` | full M1 + M2 + S1 + S2 + I1, gate semantics typically stricter |

`translation-i18n` skips S1/S2 because UI strings are too short for back-translation similarity to be meaningful and are register-pinned by format conventions.

---

## Audit-trail entry format (per gate, uniform shape)

Every gate emits an entry into `audit_trail.gate_verdicts.<id>` with this shape:

```yaml
gate_id: M1 | M2 | S1 | S2 | I1
verdict: PASS | FAIL | WARN | PASS_ADVISORY | SKIPPED | INFO
diff: <gate-specific structured diff, null when PASS or INFO>
metadata: <gate-specific>
```

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
