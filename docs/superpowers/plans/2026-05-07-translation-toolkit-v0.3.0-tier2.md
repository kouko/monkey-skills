# translation-toolkit v0.3.0 — Novel Tier 2

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended; v0.1.0 + v0.2.0 both validated this pattern) or `superpowers:executing-plans` to implement this plan phase-by-phase. Each phase = one commit.

**Date**: 2026-05-07
**Status**: Plan — pickup-ready for fresh session
**Predecessor**: v0.2.0 (PR #262, merged 2026-05-06; Tier 1 = scene-aware chunking)
**Tier 2 effort**: 3-5 days; Tier 3 still deferred

---

## Context

translation-toolkit v0.2.0 shipped `translation-novel` with **scene-aware chunking** + **scene-window prompts** — Tier 1 of the v0.2.0 plan. The structural cost claim (O(N²) → O(N), ~17× at real-novel scale) was proven via the 走れメロス smoke fixture (4 scenes, byte-conservation + cost-inequality assertions).

The Tier 2 work that v0.2.0 explicitly deferred — and that the [2026-05-07 prior-art survey](../research/2026-05-07-novel-translation-prior-art.md) flagged three concrete patterns to borrow from (TransAgents prep / GalTransl problemAnalyze / qw02 cheap-model split) — is now scoped here. v0.3.0 adds:

1. **Whole-book pre-pass** (TransAgents prep-phase pattern) — a fresh-context subagent reads all chapters in a book once, extracts character profiles + world-glossary + recurring cultural references into `<repo>/.translations/{characters,world-glossary}.json`, and seeds M2 enforcement + I1 decision logs. Runs **once per book**, before any scene translation.
2. **5D literary critic** (TransAgents critic role-split concept, single-agent realization) — adds a fifth axis `Literariness` to the per-scene reflect step for novel mode, distinct from creative mode's `Effectiveness` axis. Sub-concerns: rhythm / euphony / archaism / register-shift fidelity.
3. **M3 deterministic post-translation linter** (GalTransl `problemAnalyze` pattern) — runs **before S1**, catches residual source-language characters / length-ratio violations / wrong punctuation convention. Cheap, no-LLM, short-circuits S1 when output is structurally broken.
4. **Cheap-model split** (qw02 pattern) — `model: str | dict` schema; pre-pass EXTRACTOR + S1 BACK-TRANSLATOR can use a cheaper model than the WRITER / CRITIC / REVISER roles. Keeps pre-pass cost amortized across the book.

Tier 1 had a single demonstrable acceptance bar (cost-reduction inequality). Tier 2 has four borrowed features; acceptance is composite — functional smoke per feature + a single quantitative bar (pre-pass cost ≤ 50% of one chapter's translation cost).

## Goal — Tier 2

Extend `translation-novel` to:

1. Dispatch a whole-book **pre-pass** (`EXTRACTOR` role, fresh-context subagent) that reads all chapters in book order, extracts character profiles / world-glossary terms / recurring cultural references, and writes JSON artifacts to `<repo>/.translations/`.
2. Replace per-scene 4D reflect with **5D literary reflect** by default for novel mode (4D remains the fallback when `intake_spec.register == colloquial-only` or caller opts out).
3. Run **M3 deterministic linter** as a HARD gate between M2 and S1 — residual source-language characters HARD-block; length-ratio + punctuation convention WARN.
4. Accept **`model: str | dict`** in intake-spec; route per-role (extractor / back_translator default to cheap; writer / critic / reviser default to standard).
5. Validate via fixture-only smoke + cost-ceiling assertion (no live LLM dependency for acceptance — same standard as v0.2.0).

Out-of-scope features (Tier 3) are listed in §Deferred below.

## Architecture decisions

### Decision A — Pre-pass = subagent dispatched from `translation-novel` (NOT new skill)

Same input shape (chapter `.md` files); a new skill would add 5 × 19 functional copies + SKILL.md overhead for what is fundamentally a *phase* before per-chapter translation. Survey alignment: TransAgents prep / darkautism Pass 1 / qw02 auto-glossary all model this as a pipeline phase, not a separate skill.

The `EXTRACTOR` role joins existing roles vocabulary (WRITER / CRITIC / REVISER / BACK-TRANSLATOR / JUDGE) per the v0.2.0 SKILL.md "Roles are behavioral. Any LLM model can fill any role" idiom. Subagent dispatch fits because the pre-pass needs to read multi-chapter input under fresh context — pre-pass cannot share context with a chapter-N translation that has already happened.

### Decision B — 5D's fifth axis = `Literariness` (文学性 / 文學性)

Distinct from creative mode's 5D `Effectiveness` axis (CTA / persuasion). Novel-mode 5D adds a literary-craft dimension that 4D's `Style` axis under-serves (Style covers register/tone matching; Literariness covers craft).

Sub-concerns enumerated in the critic prompt body (not exposed as separate JSON keys):
- **Rhythm** — sentence-cadence / breath-grouping fidelity
- **Euphony** — sound-pattern (alliteration / mora pattern / tonal pacing) preservation where feasible
- **Archaism** — appropriate level of period-specific vocabulary / honorific register
- **Register-shift fidelity** — when the source shifts register mid-scene (narrator vs dialogue, formal vs casual within the same character), the target should shift in kind

JSON output keeps a single `literariness: [{issue, suggestion}, ...]` key for parity with the other four axes. Trilingual axis name: EN `Literariness` / JP `文学性` / ZH `文學性` — all standard academic terms.

5D literary mode is the **default** for `translation-novel`. Caller can opt to 4D via intake-spec `reflect_axes: 4d` when the chapter is colloquial-only (e.g. light-novel high-school dialogue with negligible literary content) — falls back to existing `prompt-reflect-4d.md`.

### Decision C — New gate `M3` deterministic post-translation linter

Pipeline order changes from `M1 → M2 → S1 → S2 → I1` to `M1 → M2 → M3 → S1 → S2 → I1`.

M3 short-circuits S1 when the output is structurally broken — saves the cost of a blind back-translation that will be meaningless on broken output. M3 is **deterministic** (no LLM); the M-class semantic in the existing taxonomy.

Subrule tier breakdown (verdict aggregation: any HARD subrule fail → M3 FAIL; only SHOULD subrules trip → M3 WARN):

| Subrule | Tier | Pass criterion |
|---|---|---|
| **M3a** Residual source-language characters | HARD | Target contains < 1% source-language script characters (CJK heuristic: count chars whose Unicode block matches source language, divide by total non-whitespace target chars; threshold tuned per locale pair in `scripts/lib/gate_m3_problem_analyze.py`) |
| **M3b** Length-ratio sanity | SHOULD | Target token count / source token count ∈ [0.5, 2.5] (locale-pair-tuned defaults; intake-spec can override) |
| **M3c** Punctuation convention | SHOULD | CJK target uses fullwidth punctuation per JLReq/CLReq; ASCII target uses halfwidth. Counted as ratio violations, not per-character. |

M3 produces a uniform `gate_verdicts.M3` audit entry with `subrules: {m3a, m3b, m3c}` field carrying per-subrule verdicts so callers can inspect individually.

### Decision D — Cheap-model split via `model: str | dict`

Intake-spec extension. Both forms accepted:

```yaml
# Existing v0.2.0 form — single string applies to all roles
model: claude-opus-4-7

# v0.3.0 form — dict; required `default` + optional per-role overrides
model:
  default: claude-opus-4-7
  extractor: claude-haiku-4-5
  back_translator: claude-haiku-4-5
```

Routing rules (`scripts/lib/model_routing.py`):
1. If `model` is `str`, every role uses that model.
2. If `model` is `dict`, the `default` key is mandatory; missing → validation error at intake.
3. Per-role override keys recognized: `default`, `writer`, `critic`, `reviser`, `back_translator`, `judge`, `extractor` (v0.3.0 new). Unknown keys at intake → validation warning (forward-compat for future role splits).
4. Output: `resolve_model_for_role(model, role) -> str` returns the resolved model string for a given role.

The intake-spec validator extends to accept the dict form. v0.2.0 callers pass strings; behavior unchanged. v0.3.0 callers may opt into per-role splits for cost. SKILL.md documents this without prescribing model names — repo's "Roles are behavioral" idiom holds.

### Decision E — Composite acceptance criteria

Tier 2 has no single cost-reduction inequality. Acceptance is multi-component:

1. **Functional smoke for every borrowed feature** (no LLM calls — same standard as v0.2.0):
   - Pre-pass extraction → glossary JSON shape correct, fixture characters/places populated; round-trip extracted-name → M2 enforcement works
   - 5D literary critic prompt → produces 5-axis JSON with `literariness` key + sub-concerns enumerated in prompt body; structure verified by fixture parse
   - M3 → unit tests cover each subrule (m3a / m3b / m3c) on seeded failure fixtures
   - Cheap-model split → `model: dict` parsed correctly; per-role override flows to prompt metadata
2. **Pre-pass cost ceiling** (sole quantitative bar):
   - With cheap-model split (`extractor: claude-haiku-4-5`-class), whole-book pre-pass token cost on the 走れメロス fixture **≤ 50% of expected single-chapter scene-translation cost** (asserted via `approx_tokens` math, no real LLM calls). On a multi-chapter book this ratio drops further as pre-pass amortizes.
3. **No regression**: all 164 v0.2.0 tests still pass; novel-smoke 0.75-ratio inequality still holds.
4. **Quality bar = explicit non-goal** in v0.3.0 (defer to translator-user feedback, same as Tier 1's optional Phase E).

### Decision F — Pre-pass scope = whole-book (NOT per-chapter cumulative)

User decision (overriding initial plan-author default of per-chapter cumulative). Aligns with TransAgents prep phase, drops darkautism per-chapter cumulative pattern.

**Implications:**
- Pre-pass is invoked **once per book**, not per chapter. Input: a `book_manifest` — a directory of chapter `.md` files in order, OR an explicit ordered list of chapter paths.
- Output: `<repo>/.translations/characters.json` + `<repo>/.translations/world-glossary.json` (single set of artifacts per book). Subsequent per-chapter translation runs read the same JSON.
- Cache invalidation: pre-pass detects book_manifest changes (file SHA-256 + ordering hash); if any chapter file changed or chapters were added/removed, pre-pass rerun is required. Stale-cache detection emits `WARN: pre-pass artifacts may be stale (manifest hash mismatch)` and the caller can decide to rerun or proceed.
- Cross-chapter coreference resolution (same character's aliases / titles / nicknames across chapters) becomes possible — the design rationale beyond pure cost: a per-chapter pre-pass cannot detect that "陛下" in chapter 3 refers to the same character as "アレキシス王" in chapter 5.

When user has only one chapter (e.g. a one-shot story or testing on a fixture), pre-pass still runs once and is trivially small.

### Decision G — Pre-pass output JSON schema (informally fixed)

`<repo>/.translations/characters.json`:

```json
{
  "schema_version": "0.3.0",
  "book_manifest_hash": "sha256:...",
  "extracted_at": "2026-05-07T...",
  "extractor_model": "claude-haiku-4-5",
  "characters": [
    {
      "canonical_name": "メロス",
      "canonical_target": "Melos",
      "aliases": [
        {"source": "メロス", "target": "Melos"},
        {"source": "彼", "target": "he"},
        {"source": "妹の婿", "target": null}
      ],
      "voice_notes": "earnest, impulsive, friend-loyalty motif",
      "first_seen_chapter": 1,
      "last_seen_chapter": 1
    }
  ]
}
```

Schema notes:
- **`aliases`** is a paired-structure array `[{source, target}, ...]` (G2). `target` may be `null` when the EXTRACTOR cannot confidently propose a target form — the human translator resolves at L1.5 → L1 promotion. Pairing prevents drift between `aliases_source` / `aliases_target` parallel arrays.
- **`voice_notes`** (G1) is a one-sentence behavioral observation seeding 5D `Literariness` axis sub-concern `register-shift fidelity` and Tier 3 S3 voice-consistency gate (when it ships). Observations only ("uses 候 archaic ending"), not interpretations ("feels formal").
- `canonical_name` is the source-language form most often used in the book; `canonical_target` is the proposed target form (may be `null` when uncertain).

`<repo>/.translations/world-glossary.json`:

```json
{
  "schema_version": "0.3.0",
  "book_manifest_hash": "sha256:...",
  "extracted_at": "2026-05-07T...",
  "extractor_model": "claude-haiku-4-5",
  "places": [
    {"canonical_source": "シラクサ", "canonical_target": "Syracuse", "first_seen_chapter": 1}
  ],
  "organizations": [],
  "world_terms": [
    {"canonical_source": "暴君", "canonical_target": "tyrant", "notes": "context-dependent — could be 'despot' depending on register", "first_seen_chapter": 1}
  ],
  "cultural_references": [
    {
      "source_phrase": "信実とは決して空虚な妄想ではなかった",
      "category": "literary_quotation",
      "handling_hint": "borrow",
      "first_seen_chapter": 1
    }
  ]
}
```

Schema notes:
- **`cultural_references[].category`** is a closed enum (G3): `literary_quotation | idiom | religious_term | food_term | place_culture | historical_reference | other`. Validator rejects unknown values; `other` is the catch-all. Closed enum lets downstream stats / audit-trail aggregate by class.
- `handling_hint` is the recommended I1 disposition (`borrow | explain | approximate`); IMPROVE may override at translation time but the audit-trail records the hint vs the actual handling.

Both JSON files are merged into the project glossary at runtime (L1.5 tier — between L1 project-glossary and L2 bundled). M2 enforces character/place mappings (paired-alias structure means each alias gets its own enforcement entry); I1 receives `cultural_references` as the seed list (instead of detecting on the fly).

### Decision H — Verification gates table updated

Per `references/verification-gates.md` §Per-skill gate application after Tier 2:

| Skill | Gates run |
|---|---|
| `translation-i18n` | M1 + M2 (strict) |
| `translation-doc` | M1 + M2 + **M3** + S1 + S2 |
| `translation-novel` | M1 + M2 + **M3** + S1 (MUST in transcreation, SHOULD in faithful) + S2 + I1 |
| `translation-creative` | M1 + M2 + S1 (MUST in transcreation, SHOULD in faithful) + S2 |
| `translation-audit` | full M1 + M2 + S1 + S2 + I1 |

`translation-doc` and `translation-novel` both add M3 in v0.3.0. Both are prose-shape skills where M3's three subrules apply cleanly:
- M3a (residual source-language) — applicable to any long-form translation; doc + novel both surface "partial translation" failures the same way
- M3b (length-ratio sanity) — doc and novel have stable length-ratio expectations; ratio outside [0.5, 2.5] indicates a real anomaly
- M3c (punctuation convention) — JLReq / CLReq apply to both prose forms

`translation-i18n` skips M3 because UI strings are too short for length-ratio to be meaningful and often have no punctuation. `translation-creative` skips M3 because transcreation mode legitimately produces wide length-ratio swings (ad copy is rewritten, not translated literally) — a future v0.4 may add M3 with mode-conditional skip of M3b when `mode == transcreation`. `translation-audit` is itself a downstream auditor — when it audits a doc / novel translation, M3 has already run upstream; re-running M3 inside audit is redundant.

## Implementation Phases

6 commits over 3-5 days. Branch: `feat/translation-toolkit-v0.3.0-tier2`.

Order rationale: bottom-up — leaf libraries first (M3 + model routing), then canonical prompt + pre-pass, then SKILL.md integration last (because it pulls all four into the pipeline at once).

### Phase A — M3 deterministic gate library (1 commit)

**Files:**
- Create: `translation-toolkit/scripts/lib/gate_m3_problem_analyze.py`
- Create: `translation-toolkit/scripts/tests/test_gate_m3_problem_analyze.py`
- Modify: `translation-toolkit/scripts/lib/gates.py` (register M3 in the gate registry)
- Modify: `translation-toolkit/scripts/canonical/verification-gates.md` (add §M3 section, update Per-skill table per Decision H)

**API:**
```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class M3SubruleVerdict:
    subrule: Literal["m3a", "m3b", "m3c"]
    verdict: Literal["PASS", "WARN", "FAIL"]
    tier: Literal["HARD", "SHOULD"]
    metric: float          # e.g. residual-language ratio for m3a
    threshold: float
    detail: str            # human-readable explanation

@dataclass
class M3Verdict:
    verdict: Literal["PASS", "WARN", "FAIL"]
    subrules: list[M3SubruleVerdict]   # always 3 entries: m3a, m3b, m3c

def evaluate_m3(
    *,
    source_text: str,
    target_text: str,
    source_locale: str,
    target_locale: str,
) -> M3Verdict:
    """Run M3a (residual-source) HARD + M3b (length-ratio) SHOULD + M3c (punct) SHOULD.

    Aggregation:
      - any HARD subrule FAIL  -> M3 FAIL
      - any SHOULD subrule WARN -> M3 WARN (only if no HARD FAIL)
      - all PASS              -> M3 PASS
    """
```

**Subrule details:**
- **M3a** (HARD residual-source): use `unicodedata.name()` block detection. For `target_locale='en-US'` reading `source_locale='ja-JP'`, count chars whose Unicode block is one of {Hiragana, Katakana, CJK Unified Ideographs, CJK Symbols and Punctuation}; divide by `len([c for c in target_text if not c.isspace()])`. Threshold = 0.01 (1%). Tunable per pair via `_LOCALE_PAIR_THRESHOLDS` constant.
- **M3b** (SHOULD length-ratio): use `scene_chunker.approx_tokens()` (already public in v0.2.0). Default range [0.5, 2.5]. Tunable per pair via `_LOCALE_PAIR_LENGTH_RATIO` constant.
- **M3c** (SHOULD punct): for CJK targets (`zh-*` / `ja-*`), count fullwidth-vs-halfwidth ratio for {`,`/`，` `.`/`。` `?`/`？` `!`/`！`}. Pass if fullwidth ratio ≥ 0.8 in CJK target. For ASCII targets, no check (returns PASS by default). JLReq/CLReq references in detail string.

**Tests:**
1. `test_m3a_clean_target_passes` — JP→EN target with no JP chars → PASS
2. `test_m3a_residual_jp_fails` — JP→EN target with 5% JP chars → FAIL
3. `test_m3a_below_threshold_passes` — JP→EN target with 0.5% JP chars (e.g. one stray katakana name not in glossary) → PASS
4. `test_m3b_length_ratio_within_range` — ratio 1.2 → PASS
5. `test_m3b_length_ratio_too_short` — ratio 0.3 → WARN
6. `test_m3b_length_ratio_too_long` — ratio 3.0 → WARN
7. `test_m3c_zh_fullwidth_passes` — `target_locale=zh-TW` with fullwidth `，。？！` → PASS
8. `test_m3c_zh_halfwidth_warns` — `target_locale=zh-TW` with halfwidth `,.?!` → WARN
9. `test_m3c_en_target_skips` — `target_locale=en-US` → PASS (no check)
10. `test_aggregate_hard_fail_dominates` — m3a FAIL + m3b WARN → M3 FAIL
11. `test_aggregate_warn_only` — m3a PASS + m3b WARN + m3c PASS → M3 WARN
12. `test_aggregate_all_pass` — all subrules PASS → M3 PASS

**Distribution:** Run `python3 scripts/distribute.py` to redistribute the updated `verification-gates.md` to all 5 active skills' `references/`. Run `python3 scripts/verify-drift.py` to confirm byte-identical functional copies. Both go in the same commit.

**Note on Decision H scope** — M3 lib is skill-agnostic; the per-skill gate registry in `gates.py` adds two new entries: `translation-doc` and `translation-novel` both invoke `evaluate_m3()` from their Layer 4 verification step. `translation-i18n / creative / audit` callers do NOT call `evaluate_m3()`. The 12 unit tests cover the lib only; per-skill integration is exercised in Phase E (novel) and Phase F (doc smoke).

### Phase B — Cheap-model split: model routing library + intake-spec extension (1 commit)

**Files:**
- Create: `translation-toolkit/scripts/lib/model_routing.py`
- Create: `translation-toolkit/scripts/tests/test_model_routing.py`
- Modify: `translation-toolkit/scripts/canonical/orthogonal-axes.md` (document `model` accepting `str | dict`)
- Modify: `translation-toolkit/skills/translation-intake/SKILL.md` (intake-spec validation accepts the dict form; add §"Per-role model overrides" section)

**API:**
```python
from typing import TypedDict

class ModelDict(TypedDict, total=False):
    default: str           # required
    writer: str
    critic: str
    reviser: str
    back_translator: str
    judge: str
    extractor: str         # v0.3.0 new

KNOWN_ROLES = ("writer", "critic", "reviser", "back_translator", "judge", "extractor")

def validate_model_field(model: str | dict) -> None:
    """Raise ValueError if invalid.
    - str: any non-empty string accepted
    - dict: must have `default` key (non-empty str); other keys must be in KNOWN_ROLES; values non-empty str
    Unknown role keys -> warning printed to stderr (forward-compat).
    """

def resolve_model_for_role(model: str | dict, role: str) -> str:
    """Return the model string for the given role.
    - str: returns as-is
    - dict: returns dict[role] if present, else dict['default']
    Raises KeyError if dict and `default` missing (caller should validate first).
    """
```

**Tests:**
1. `test_validate_string_form` — `model="claude-opus-4-7"` → no error
2. `test_validate_dict_with_default_only` — `{"default": "claude-opus-4-7"}` → no error
3. `test_validate_dict_missing_default_raises` — `{"writer": "..."}` → ValueError
4. `test_validate_dict_unknown_role_warns` — `{"default": "...", "future_role": "..."}` → no error, but stderr warning
5. `test_validate_dict_empty_value_raises` — `{"default": ""}` → ValueError
6. `test_resolve_string_form_returns_same` — every role resolves to the single string
7. `test_resolve_dict_role_present` — role override returned
8. `test_resolve_dict_role_absent_returns_default` — fallback to `default`
9. `test_resolve_extractor_role` — `{"default": "opus", "extractor": "haiku"}` → role=extractor returns "haiku"

**Intake-spec doc extension** (in `translation-intake/SKILL.md`):
- Add a "Per-role model overrides" subsection under inputs, showing both forms with a callout: "Roles are behavioral. The same skill body runs regardless of model; only token cost / latency change."
- Reference v0.3.0 plan Decision D for rationale.

### Phase C — Canonical 5D literary prompt + functional copy distribution (1 commit)

**Files:**
- Create: `translation-toolkit/scripts/canonical/prompts/reflect-5d-literary.md`
- Modify: `translation-toolkit/scripts/distribute.py` — add `"prompts/reflect-5d-literary.md"` to `PROMPT_FILES` set
- Modify: `translation-toolkit/scripts/lib/novel_prompts.py` — add `build_scene_reflect_5d_literary_prompt()`; modify `build_scene_reflect_prompt()` to dispatch to 4d or 5d-literary based on `intake_spec.reflect_axes`
- Modify: `translation-toolkit/scripts/tests/test_novel_prompts.py` — add tests for 5d-literary builder
- Modify: `translation-toolkit/scripts/canonical/4d-reflection.md` — add §"Novel-mode 5D literary variant" cross-reference (note: this canonical doc is the spec; the prompt is the renderable artifact)

**Canonical prompt content** (`prompts/reflect-5d-literary.md` — frontmatter shape mirrors `reflect-5d.md`):

```markdown
---
role: critic
inputs: [source_lang, target_lang, mode, register, strategy, domain, glossary_terms, source_chunk, draft_v1, prev_scene_v2, next_scene_source]
axes: [accuracy, fluency, style, terminology, literariness]
output: structured_critique_json
applies_to: [translation-novel]
---

You are a translation critic reviewing this scene draft for novel translation. Produce
structured 5D critique across these axes (one paragraph per axis, with concrete
suggestions where issues found):

1. Accuracy — semantic faithfulness. Are there additions, omissions, distortions?
2. Fluency — does target read naturally? Awkward phrasings?
3. Style — does register/rhythm/rhetoric match source and intended {{mode}}/{{register}}?
4. Terminology — does it match the glossary? Domain conventions?
5. Literariness — assess the literary craft of the target:
   - Rhythm — sentence-cadence and breath-grouping fidelity
   - Euphony — sound-pattern (alliteration / mora pattern / tonal pacing) preservation
     where the target language admits a comparable effect
   - Archaism — appropriate level of period-specific vocabulary / honorific register
     for the source's period and tone
   - Register-shift fidelity — when the source shifts register mid-scene (narrator
     vs dialogue, formal vs casual within the same character), does the target
     shift in kind?

Output format (JSON):
{
  "accuracy":     [{"issue": "...", "suggestion": "..."}, ...],
  "fluency":      [...],
  "style":        [...],
  "terminology":  [...],
  "literariness": [...]
}

If an axis has no issues, return empty array. Do NOT rewrite the translation —
only critique.
```

**Builder API:**
```python
def build_scene_reflect_5d_literary_prompt(
    *,
    scene: Scene,
    draft_v1: str,
    intake_spec: dict,
    glossary_hits: list[dict],
    prev_scene_v2: str | None,
    next_scene_source: str | None,
) -> str:
    """5D literary variant of the scene critic prompt.

    Same scene-window context as the 4D reflect builder (prev/next windows
    available so the critic can judge cross-scene consistency on the literary
    axis), but loads `references/prompt-reflect-5d-literary.md` and renders
    the 5-axis JSON output schema.
    """
```

**Dispatch logic** (in existing `build_scene_reflect_prompt`):
```python
def build_scene_reflect_prompt(...):
    axes = intake_spec.get("reflect_axes", "5d-literary")  # default = 5d-literary for novel
    if axes == "4d":
        return _build_4d(...)
    elif axes == "5d-literary":
        return build_scene_reflect_5d_literary_prompt(...)
    else:
        raise ValueError(f"unsupported reflect_axes: {axes}")
```

**Tests:**
1. `test_5d_literary_prompt_loads_canonical` — builder reads `references/prompt-reflect-5d-literary.md` from skill's references dir
2. `test_5d_literary_prompt_includes_5_axes` — output mentions all 5 axis names
3. `test_5d_literary_prompt_lists_subconcerns` — output enumerates rhythm / euphony / archaism / register-shift
4. `test_5d_literary_prompt_includes_scene_window` — prev_v2 + current + next_source all present
5. `test_dispatch_default_is_5d_literary` — `intake_spec.reflect_axes` absent → 5d-literary chosen
6. `test_dispatch_4d_when_opted` — `intake_spec.reflect_axes='4d'` → 4d builder chosen
7. `test_dispatch_unknown_raises` — `intake_spec.reflect_axes='6d'` → ValueError

**Distribution:** Run `python3 scripts/distribute.py` to flatten new prompt to `references/prompt-reflect-5d-literary.md` × 5 active skills. Run `verify-drift.py`. Same commit.

### Phase D — Pre-pass character/world-glossary extraction (1 commit)

**Files:**
- Create: `translation-toolkit/scripts/lib/character_extractor.py`
- Create: `translation-toolkit/scripts/lib/world_glossary_extractor.py` (separate file because the prompts diverge — character profiles need voice notes; world-glossary entries need place/org/term type tagging)
- Create: `translation-toolkit/scripts/tests/test_character_extractor.py`
- Create: `translation-toolkit/scripts/tests/test_world_glossary_extractor.py`
- Create: `translation-toolkit/skills/translation-novel/protocols/character-extraction.md` (skill-local protocol — owns the EXTRACTOR role behavioral contract + character-specific schema/merge/voice_notes rules; lighter-rules per `feedback_skill_internal_readme_exempt_from_docs_team.md`; ~150 lines)
- Create: `translation-toolkit/skills/translation-novel/protocols/world-glossary-extraction.md` (skill-local protocol — world-glossary-specific schema, four-class breakdown {places / organizations / world_terms / cultural_references}, cultural_references closed-enum reference; cross-references EXTRACTOR role contract in character-extraction.md to avoid drift; ~150 lines)
- Create: `translation-toolkit/scripts/canonical/prompts/extract-characters.md`
- Create: `translation-toolkit/scripts/canonical/prompts/extract-world-glossary.md`
- Modify: `translation-toolkit/scripts/distribute.py` — add both to `PROMPT_FILES`
- Modify: `translation-toolkit/scripts/lib/glossary.py` — add L1.5 tier (post-Phase D pre-pass artifacts) to `lookup()` resolution order: L1 → **L1.5** → L2 → L3 → L4

**API:**
```python
# character_extractor.py

@dataclass
class BookManifest:
    chapters: list[Path]   # ordered list of chapter .md files
    manifest_hash: str     # sha256 of joined (path + content sha) for cache invalidation

def load_book_manifest(book_dir: Path) -> BookManifest:
    """Walk book_dir for *.md files, sort by name, compute manifest hash."""

def build_character_extraction_prompt(
    *,
    chapter_text: str,
    chapter_index: int,
    accumulated_characters: list[dict],  # what we've extracted so far
    intake_spec: dict,
) -> str:
    """Render `prompt-extract-characters.md` template.

    Pre-pass walks chapters in order; each chapter's prompt receives the
    accumulated extraction so far so the LLM can MERGE (add new characters,
    extend aliases, refine voice notes) rather than RE-EXTRACT each chapter.
    """

def parse_character_extraction_response(response: str) -> list[dict]:
    """Parse JSON response into list of character dicts per Decision G schema."""

def run_pre_pass_characters(
    *,
    book_manifest: BookManifest,
    intake_spec: dict,
    output_path: Path,            # .translations/characters.json
    dispatch_subagent: Callable,  # injected by skill orchestration
) -> dict:
    """Orchestrate whole-book character extraction.

    For each chapter (in order): build prompt with accumulated state, dispatch
    EXTRACTOR subagent (fresh context, model=resolve_model_for_role(model, 'extractor')),
    parse response, merge into accumulated state. After all chapters: write JSON
    artifact with schema_version + book_manifest_hash + extracted_at + extractor_model.

    Returns the final characters.json dict.
    """
```

`world_glossary_extractor.py` mirrors the same shape with different prompt template + output JSON schema (places / organizations / world_terms / cultural_references per Decision G).

**Canonical prompt content** (`prompts/extract-characters.md` — abbreviated):

```markdown
---
role: extractor
inputs: [source_lang, target_lang, chapter_text, chapter_index, accumulated_characters]
output: characters_json_array
applies_to: [translation-novel]
---

You are a character-extraction subagent reading a book chapter for translation
preparation. Your task: identify named characters appearing in this chapter
and produce/extend a character profile JSON.

Input includes `accumulated_characters` — characters extracted from prior
chapters. For each character in the current chapter:
- If already in accumulated_characters: ADD any new aliases (titles, nicknames),
  REFINE voice_notes if the chapter reveals new traits, UPDATE last_seen_chapter.
- If new: CREATE a new entry per the schema below.

Schema for each character entry:
{
  "canonical_name": "<source-language form, the name most often used>",
  "canonical_target": "<proposed target-language form; null if uncertain>",
  "aliases_source": [...],
  "aliases_target": [...],
  "voice_notes": "<one sentence; speech register, motifs, key traits>",
  "first_seen_chapter": <int>,
  "last_seen_chapter": <int>
}

Output format (JSON):
{
  "characters": [<entries...>]
}

Rules:
- ONLY characters with a name or distinct identifying title. Skip generic crowd
  ("the soldiers", "a passerby") unless they're given a recurring identifier.
- Voice notes are observation, not interpretation. "uses 候 archaic ending"
  not "feels formal".
- Use `null` for canonical_target when uncertain — translator will resolve.
```

`extract-world-glossary.md` follows the same shape with sections for places / organizations / world_terms / cultural_references.

**Tests** (no LLM calls):
1. `test_book_manifest_hash_stable` — same dir → same hash; mutated file → different hash
2. `test_book_manifest_orders_chapters` — files sorted by name; ordering reflected in manifest
3. `test_build_character_prompt_includes_accumulated` — accumulated state from prior chapters appears in prompt
4. `test_build_character_prompt_includes_schema` — output schema is in the prompt body
5. `test_parse_character_response_round_trips` — JSON response parses back to list of dicts matching Decision G shape
6. `test_run_pre_pass_writes_artifact` — fixture: 2 chapter `.md` files; mock subagent returns canned JSON; assert `characters.json` written with schema_version, manifest_hash, extracted_at, extractor_model
7. `test_run_pre_pass_merges_across_chapters` — chapter 1 returns char A; chapter 2 returns char A (refined) + char B; final JSON has 2 characters with merged aliases
8. `test_run_pre_pass_uses_extractor_model` — `model={'default': 'opus', 'extractor': 'haiku'}` → mock subagent invoked with model='haiku'
9. `test_run_pre_pass_stale_cache_warns` — existing `characters.json` with mismatching `book_manifest_hash` → log warning (does NOT auto-rerun; caller decides)

`world_glossary_extractor` gets parallel tests.

**Protocol content** — split per Decision D-Option 2:

`skills/translation-novel/protocols/character-extraction.md` (canonical owner of EXTRACTOR role contract):
- §EXTRACTOR role behavioral contract (fresh context per chapter, no cross-context leakage) — referenced by world-glossary-extraction.md
- §Subagent dispatch contract — receives **paths** (chapter file paths + accumulated state path), not file content (per repo Cross-Plugin Delegation Contract idiom)
- §Accumulated-state merge semantics — applies uniformly to both extractors
- §Cache invalidation contract — manifest_hash check + caller decision rule
- §Character schema (Decision G) — paired aliases structure, voice_notes observation-not-interpretation rule, canonical_target null semantics
- §Character merge rules — alias accumulation, voice_notes refinement, last_seen_chapter update
- Cross-reference: §"World-glossary extraction shares the EXTRACTOR role contract above; see protocols/world-glossary-extraction.md for world-glossary schema + four-class breakdown."

`skills/translation-novel/protocols/world-glossary-extraction.md` (skill-local; defers role contract to character-extraction.md):
- §"This protocol shares the EXTRACTOR role / dispatch / cache rules defined in protocols/character-extraction.md §EXTRACTOR role behavioral contract. Read that first."
- §World-glossary schema (Decision G) — places / organizations / world_terms / cultural_references four sections
- §cultural_references category enum — closed enum `{literary_quotation | idiom | religious_term | food_term | place_culture | historical_reference | other}`; validator rejects unknown
- §handling_hint semantics — borrow / explain / approximate; IMPROVE may override at translation time
- §World-glossary merge rules — append-only for places/orgs (no merge across chapters; same source-name = same entry); world_terms refines `notes` field; cultural_references append-only
- §Difference from L2 bundled glossary — L1.5 is book-specific, L2 is locale-pair generic; M2 enforces L1.5 with same priority as L1 within scope of this book

**Distribution:** Run distribute + verify-drift. Same commit.

### Phase E — translation-novel + translation-doc SKILL.md integration + intake hook (1 commit)

**Files:**
- Modify: `translation-toolkit/skills/translation-novel/SKILL.md` — wire pre-pass + 5D + M3 + cheap-model into the documented pipeline
- Modify: `translation-toolkit/skills/translation-doc/SKILL.md` — add M3 row to Layer 4 gate table; pipeline order line updated to include M3 between M2 and S1; one-liner crediting v0.3.0 M3 addition (no other changes — doc does not adopt 5D / pre-pass / cheap-model)
- Modify: `translation-toolkit/skills/translation-novel/checklists/novel-quality-checklist.md` — add pre-pass artifact freshness check + M3 verdict surface check
- Create: `translation-toolkit/skills/translation-novel/checklists/prepass-cost-ceiling.md` — Decision E #2 acceptance reference for callers
- Modify: `translation-toolkit/skills/using-translation-toolkit/SKILL.md` — add `EXTRACTOR` to Roles vocabulary; mention v0.3.0 pre-pass at routing-tip level; mention M3 as a doc + novel addition

**SKILL.md changes** (specific edit targets — keep edits minimal, follow v0.2.0 SKILL.md voice):

1. **Inputs** section — add new field:
   - **book_manifest** *(strongly recommended for novels with >1 chapter)* — directory or ordered list of chapter `.md` files; enables whole-book pre-pass. If absent, skill runs in single-chapter mode (pre-pass over the one input chapter; degenerate but valid).

2. **Pipeline** section — insert new "Layer 1.5: Pre-pass" between Layer 1 (intake) and Layer 2 (preparation):
   - Triggered on first invocation per book (book_manifest_hash absent or stale).
   - Dispatches `EXTRACTOR` subagent (model resolved via `resolve_model_for_role(model, 'extractor')`).
   - Reads `book_manifest`, walks chapters in order with accumulated-state merge.
   - Writes `<repo>/.translations/characters.json` and `<repo>/.translations/world-glossary.json`.
   - Subsequent per-chapter invocations skip pre-pass (artifacts cached); manifest hash mismatch → WARN + caller decides rerun.

3. **Layer 2 → Glossary resolve** — extend the L1-L4 fallthrough to **L1 → L1.5 → L2 → L3 → L4**: L1.5 reads pre-pass artifacts merged with L1.

4. **Layer 3 → REFLECT 4D** changes to **REFLECT 5D-literary** (default), with a callout that 4D remains available via `intake_spec.reflect_axes='4d'`. Cite `references/prompt-reflect-5d-literary.md`.

5. **Layer 4 verification table** — add M3 row per Decision H. Pipeline order line updated to `M1 → M2 → M3 → S1 → S2 → I1`.

6. **Roles** section — add `EXTRACTOR` line: "produces character/world-glossary JSON during whole-book pre-pass; never modifies source or translation."

7. **What this skill does NOT do** — add: "Does not auto-rerun pre-pass on stale book_manifest. Surfaces a stale-cache WARN; caller decides whether to rerun."

**Checklist update** (`novel-quality-checklist.md`):
- Add item: "Pre-pass artifacts present and not stale (book_manifest_hash matches current manifest)."
- Add item: "M3 verdict surfaced in audit-trail; subrules m3a/m3b/m3c each present."

**New checklist** (`prepass-cost-ceiling.md`):
- Document the Decision E #2 cost-ceiling acceptance criterion at caller-facing level: how to compute the assertion + when it's expected to fail (very small books / non-cheap extractor).

### Phase F — E2E smoke test + cost ceiling assertion + version bump + docs (1 commit)

**Files:**
- Create: `translation-toolkit/scripts/tests/fixtures/sample-book-ja/` — directory with 2 chapters:
  - `chapter-01.md` — 走れメロス excerpt (reuse v0.2.0 fixture content; ~2,700 chars)
  - `chapter-02.md` — synthetic stub at **~1,500 chars (≥ 50% of chapter 1 length)**. Stub MUST satisfy: same character set as chapter 1 so pre-pass merging is exercised; one new place name + one new cultural reference so world-glossary growth is exercised; ~50% length floor is the **cost-ceiling design guideline** — too-short stubs starve the denominator in test 10's `prepass_tokens / single_chapter_translation_tokens` ratio and trip the 0.5 hard-fail bar even when production-scale ratios are healthy. Public-domain extension or fabricated text both acceptable; record provenance in NOTICES.md.
- Create: `translation-toolkit/scripts/tests/test_e2e_v0.3.0_tier2_smoke.py`
- Modify: `translation-toolkit/scripts/tests/test_e2e_novel_smoke.py` — assert v0.2.0 baseline still holds (164 tests pass; novel-smoke 0.75-ratio still asserted)
- Modify: `translation-toolkit/skills/translation-novel/README.md` (en) — Tier 2 features section (pre-pass / 5D literary / M3)
- Create: `translation-toolkit/skills/translation-novel/README.ja.md` — JA translation of README updates
- Create: `translation-toolkit/skills/translation-novel/README.zh-TW.md` — ZH-TW translation of README updates
- Modify: `translation-toolkit/NOTICES.md` — note the synthetic chapter-2 stub source (likely "fabricated for test fixture" since it's a stub)
- Modify: `translation-toolkit/.claude-plugin/plugin.json` — bump version to 0.3.0
- Modify: `.claude-plugin/marketplace.json` — sync description + version

Note: the v0.2.0 plan's Phase E lessons-learned (`feedback_skill_readme_i18n_required.md`) requires en/ja/zh-TW for skill READMEs. Manually authored per `feedback_skill_internal_readme_exempt_from_docs_team.md` (lighter rules apply).

**Smoke test** (`test_e2e_v0.3.0_tier2_smoke.py` — no real LLM calls):

1. `test_pre_pass_extracts_against_fixture` — run `run_pre_pass_characters` against `sample-book-ja/` with mocked subagent that returns canned per-chapter responses; assert final `characters.json` contains expected character set (走れメロス: メロス, ディオニス, セリヌンティウス) with merged aliases across the 2-chapter fixture
2. `test_pre_pass_world_glossary_extracts` — same shape for world-glossary; assert places (シラクサ) + cultural_references seeded
3. `test_5d_literary_prompt_renders_for_fixture` — pull a scene from chapter 1, build 5D-literary critic prompt; assert structure + literariness key + sub-concerns enumerated
4. `test_m3_passes_clean_target_fixture_novel` — pre-translated EN excerpt of 走れメロス → M3 PASS
5. `test_m3_fails_seeded_residual_jp_novel` — same EN target with 5% katakana residual → M3 FAIL via m3a
6. `test_m3_warns_seeded_length_violation_novel` — synthetic short target → M3 WARN via m3b
7. **`test_m3_runs_in_doc_pipeline`** — translation-doc Layer 4 invokes M3; assert M3 verdict surfaces in doc audit-trail (per Decision H, doc adopts M3 in v0.3.0)
8. `test_cheap_model_split_routes_to_extractor` — invoke pre-pass with `model={'default': 'opus', 'extractor': 'haiku'}`; assert mock subagent received `model='haiku'`
9. `test_glossary_l1_5_tier_resolves` — pre-pass JSON → glossary.lookup hits L1.5 before L2; audit_path shows `L1.5`
10. **`test_prepass_cost_ceiling_assertion`** — KEY ACCEPTANCE TEST per Decision E #2 (HARD-FAIL). Compute pre-pass total tokens (using `approx_tokens` over generated prompts) with a synthesized "haiku-equivalent" cost model assumption (1×). Compute single-chapter scene-translation total tokens (using existing v0.2.0 prompt builders) with default model assumption (1×). Assert `prepass_tokens / single_chapter_translation_tokens ≤ 0.5`. (Math-only; no LLM calls.) Failure message MUST include actionable remediation hints:
    ```
    AssertionError: pre-pass cost ratio = {actual:.2f} (limit: 0.5)
      pre-pass tokens (cheap model assumed): {prepass_tokens}
      single-chapter translation tokens (default model assumed): {chapter_tokens}
    Possible remediations:
      - Verify intake-spec uses model: dict with extractor=cheap (Decision D)
      - Trim pre-pass prompt template (canonical/prompts/extract-*.md)
      - Verify chapter-02.md stub is ≥ 50% of chapter-01.md length (Phase F fixture guideline)
      - If actual production-scale ratio is known healthy, audit fixture proportions
    ```
    Aligns with v0.2.0 Tier 1 hard-assertion convention (cost-reduction inequality was hard-fail; Tier 2 cost-ceiling is hard-fail).

**Version bump targets:**
- `plugin.json`: `"version": "0.3.0"` + description mentions "novel pre-pass / 5D literary / M3 deterministic linter"
- `marketplace.json`: synced version + description (kept to `{name, source}` shape per `feedback_plugin_metadata_conventions.md`)

**README content** (en/ja/zh-TW per skill — manually authored, lighter rules):
- Add §"What's new in v0.3.0" section: pre-pass / 5D literary / M3 / cheap-model split
- Add §"Setting up a book for translation" mini-tutorial: tsundoku:book-extract → arrange chapter `.md` files → run pre-pass once → translate chapter-by-chapter
- Add cost note: pre-pass uses cheap extractor by default once `model: dict` form is used; total cost amortizes across the book

## Verification

After all 6 phases:

```bash
cd translation-toolkit
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest scripts/tests/ -v
# Expect: 164 (v0.2.0 baseline) + ~51 new (Phase A: 12, B: 9, C: 7, D: 18, F: 10 incl. doc M3 integration) = ~215 tests pass

python3 scripts/distribute.py
# Expect: distributed=22 (was 19; +3 new prompts: reflect-5d-literary + extract-characters + extract-world-glossary)
#         skipped=1 unrouted=0 skills=5
# Note: 19 -> 22 reflects 3 new canonical files; 22 * 5 = 110 functional copies (was 95)

python3 scripts/verify-drift.py
# Expect: OK: all 110 functional copies byte-identical (was 95)

bash .claude/hooks/validate-skill-folder-structure.sh translation-toolkit/skills/translation-novel/SKILL.md
# Expect: PASS

# Acceptance bar (Decision E #2)
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest scripts/tests/test_e2e_v0.3.0_tier2_smoke.py::test_prepass_cost_ceiling_assertion -v
# Expect: PASS — pre-pass tokens / single-chapter translation tokens ≤ 0.5
```

CI workflow `.github/workflows/translation-toolkit-ci.yml` should pass without modification (loops over skills via shell; new skill files / new lib files / new tests all picked up automatically).

## Out of Scope (deferred to Tier 3 / permanently)

> **Prior-art reference**: see [`docs/superpowers/research/2026-05-07-novel-translation-prior-art.md`](../research/2026-05-07-novel-translation-prior-art.md) for borrow-source attribution.

### Tier 3 — Cross-chapter voice audit + multi-pass polish (~1-2 weeks)

Re-trigger condition: Tier 2 ships and translator-user reports voice drift across chapters or wants editorial passes.

Adds:
- New gate **S3 voice consistency** — sample N=5 utterances per character per chapter, LLM-judge whether register / 口癖 match the character's voice profile from pre-pass (now grounded in v0.3.0 pre-pass artifacts). WARN by default; FAIL if any character profile bins drift > threshold.
  - **Prior-art status**: architecturally novel — survey found no comparable feature in any of the 7 projects. Frame as research positioning if Tier 3 ships.
- **Multi-pass orchestration**:
  - Pass 1: literal pass (current Tier 1 + 2 output)
  - Pass 2: literary polish (new prompt) — rhythm / register / naturalness — separate from REFLECT-5D-literary, which critiques only
  - Pass 3: voice consistency repair (driven by S3 gate findings)
  - **Borrow from**: hydropix `--refine`, KazKozDev "stage-two refinement"
- Chapter-level human review checkpoint (skill emits "review needed" markers for translator)
- Audit-trail per-character voice-bin tracking

### Permanently out of scope

- Whole-novel single-pass translation (will always require chapter-level boundaries)
- Audio / voice acting integration
- Multi-language parallel translation in one run (each target language is a separate invocation)
- Incremental / streaming pre-pass (always whole-book one-shot per Decision F; if user adds chapters later, manifest_hash mismatch surfaces and they choose to rerun)
- Format other than markdown chapters (other formats route through tsundoku:book-extract or other prep step)

## Pickup hints for fresh session

When starting:
1. `git checkout main && git pull`
2. `git checkout -b feat/translation-toolkit-v0.3.0-tier2`
3. Read this plan in full, then:
   - `docs/superpowers/research/2026-05-07-novel-translation-prior-art.md` — prior-art borrow attributions
   - `docs/superpowers/plans/2026-05-06-translation-toolkit-v0.2.0-novel-mode.md` — v0.2.0 plan that locked Decisions 1-8 (NOT to relitigate)
   - `translation-toolkit/skills/translation-novel/SKILL.md` — the v0.2.0 baseline this plan extends
4. Run baseline before starting: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest scripts/tests/ -q` — should be 164 tests pass.
5. **Use `superpowers:subagent-driven-development`** — proven on v0.1.0 + v0.2.0 (10-task plan ran 11 commits / 0 broken / all CI green first push). Spec reviewer catches drift implementer self-review misses; both stages required.
6. Each phase = one commit. Phase order is bottom-up dependency: A (M3 lib) → B (model routing) → C (5D prompt + dispatch) → D (pre-pass) → E (SKILL.md integration) → F (smoke + version + READMEs).
7. **`PYTHONDONTWRITEBYTECODE=1`** on every pytest invocation — `__pycache__` in skill subfolders trips `validate-skill-folder-structure.sh`. Bake into subagent prompts.
8. For new canonical prompt files: `prompts/<name>.md` flattens to `references/prompt-<name>.md` per `distribute.py::PROMPT_FILES` rule. Add to the set in Phase C and Phase D.
9. PR title: `translation-toolkit v0.3.0 — novel Tier 2 (whole-book pre-pass + 5D literary + M3 deterministic linter)`

## File path reference (for fresh session orientation)

- v0.2.0 plan: `docs/superpowers/plans/2026-05-06-translation-toolkit-v0.2.0-novel-mode.md`
- v0.2.0 spec: `docs/superpowers/specs/2026-05-06-translation-toolkit-design.md`
- Prior-art survey: `docs/superpowers/research/2026-05-07-novel-translation-prior-art.md`
- Plugin root: `translation-toolkit/`
- Existing skills (5 active): `translation-toolkit/skills/{using-translation-toolkit, translation-intake, translation-i18n, translation-doc, translation-creative, translation-audit, translation-novel}/`
- Existing lib (10): `scripts/lib/{glossary, protect_pass, gates, gate_s1_backtrans, gate_s2_register, gate_i1_untranslatability, audit_trail, web_search, scene_chunker, novel_prompts}.py`
- New lib in v0.3.0 (5): `scripts/lib/{gate_m3_problem_analyze, model_routing, character_extractor, world_glossary_extractor}.py` (+ glossary.py modified for L1.5 tier)
- Canonical (currently 19 distributed; +3 new in v0.3.0 = 22): `scripts/canonical/`
- Distribution: `scripts/distribute.py` (`PROMPT_FILES` set extended in Phase C + Phase D)
- CI: `.github/workflows/translation-toolkit-ci.yml` (no modification needed)
- Skill folder hook: `.claude/hooks/validate-skill-folder-structure.sh`

## Effort estimate (Tier 2 only)

| Item | Estimate |
|---|---|
| Phase A — `gate_m3_problem_analyze.py` + canonical update + 12 tests | ~250 LOC + ~150 LOC tests |
| Phase B — `model_routing.py` + intake-spec extension + 9 tests | ~80 LOC + ~80 LOC tests |
| Phase C — `prompts/reflect-5d-literary.md` + `novel_prompts.py` extension + 7 tests | ~100 LOC prompt + ~80 LOC builder + ~80 LOC tests |
| Phase D — `character_extractor.py` + `world_glossary_extractor.py` + 2 canonical prompts + 2 protocols (character + world-glossary, Decision D-Option 2) + 18 tests | ~400 LOC + ~250 LOC prompts + ~300 LOC protocols + ~250 LOC tests |
| Phase E — SKILL.md edits (novel + doc M3 row) + checklists + using-* doc | ~230 LOC markdown |
| Phase F — fixture extension + 10 smoke tests (incl. doc M3 integration) + tri-language READMEs + version bump | ~110 LOC + 1 fixture + ~600 LOC markdown |
| **Total new code** | **~2,490 LOC** |
| **Implementer time (single session)** | **3-5 days** |

Compared to v0.2.0 (~960 LOC, 1-2 days). Tier 2 is roughly 2.5× the v0.2.0 surface — pre-pass + new gate + new prompt + new role compose multiplicatively, but each piece is small.

---

**Plan complete.** Ready for fresh-session pickup.
