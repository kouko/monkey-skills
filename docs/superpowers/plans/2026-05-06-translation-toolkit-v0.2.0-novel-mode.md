# translation-toolkit v0.2.0 — Novel Translation Mode

**Date**: 2026-05-06
**Status**: Plan — pickup-ready for fresh session
**Predecessor**: v0.1.0 (PR #261, merged)
**Tier 1 effort**: 1-2 days; Tier 2 deferred; Tier 3 deferred

---

## Context

translation-toolkit v0.1.0 ships 6 skills. `translation-doc` handles markdown / technical docs and uses Andrew Ng's cross-chunk windowing — every chunk's prompt re-emits the **whole document** wrapped in `<TRANSLATE_THIS>` markers for cross-chunk term consistency. Works fine for a 1-page README. Cost-prohibitive for a 100K-word novel:

| Doc length | Chunks (2K each) | Per-chunk prompt | Total context tokens (× 3 D/R/I) |
|---|---|---|---|
| 5K word README | 1 | ~7K | ~21K |
| 100K word novel | 50 | ~104K | **~15.6M** |

Plus novel translation has needs the v0.1.0 pipeline doesn't model: literary register, character voice tracking across chapters, scene-level coherence, decision logs for cultural references / puns.

This plan ships a **focused Tier 1** that solves the cost problem (O(N²) → O(N), ~17× reduction). Tier 2/3 add literary-quality features but are deferred until Tier 1 is validated on a real chapter.

## Goal — Tier 1

Add a new skill `translation-novel` that:
1. Replaces token-based chunking with **scene-aware chunking** (uses paragraph breaks / scene markers / chapter boundaries).
2. Replaces whole-document `<TRANSLATE_THIS>` windowing with **scene-window context** (~500 prev-summary + current scene + ~200 next-tease).
3. Reuses v0.1.0 lib: glossary lookup (4-tier), protect-pass (markdown protect), gates (M1 will be no-op for prose; M2 enforces character/place glossary; S1 back-translation; S2 register).
4. Validates feasibility on one real Japanese novel chapter (cost + quality).

Out-of-scope features (Tier 2/3) are listed in §Deferred below.

## Architecture decisions

### Decision 1 — New skill, NOT a flag in `translation-doc`
Implementer may reverse if Tier 1 turns out trivially small, but default is: new skill at `translation-toolkit/skills/translation-novel/`.

Rationale:
- `translation-doc` is already 151 lines, focused on technical-doc shape (code blocks, mermaid, frontmatter); novel has different shape (scenes, dialogue, narration).
- Tier 2/3 will add character profile + voice tracking + decision log — won't fit cleanly as flags on `translation-doc`.
- Skill convention in this repo: each skill owns one input shape (intake / i18n / doc / creative / audit / now: novel).
- Cost: ~1 hour boilerplate (frontmatter + references/ functional copies + skill folder hook).

### Decision 2 — `translation-novel` IS in `ACTIVE_SKILLS` (gets functional-copy distribution)
Unlike `translation-intake` (excluded from ACTIVE_SKILLS), novel needs full glossary + prompts + corpus. Add to `scripts/distribute.py::ACTIVE_SKILLS`. Will produce 5 more functional copies × 20 = +100 (total: 80 → 180? actually +20 since it's the new skill × 20 canonical files = 20 new copies, 80 → 100).

Wait — current state is 80 (4 skills × 20 canonical files). Adding 5th active skill gives 5 × 20 = 100 functional copies.

### Decision 3 — Scene-aware chunking algorithm
Hierarchy: **chapter → scene → paragraph → sentence**.

- **Chapter**: input is one chapter file (caller hands one .md per chapter; `tsundoku:book-extract` already produces this).
- **Scene** = consecutive paragraphs separated by:
  - explicit scene-break markers (`* * *`, `***`, `―――`, `◇◇◇`, blank-line gap of ≥2 lines, or section heading change)
  - implicit boundary (≥3 blank lines)
- If no markers found, fallback: greedy fill to ~2000 source-language tokens, breaking at paragraph boundary.
- **Paragraph** = standard markdown paragraph (one or more lines separated by blank line).

### Decision 4 — Scene-window prompt structure
Replace `<DOCUMENT>...full novel...</DOCUMENT><TRANSLATE_THIS>chunk</TRANSLATE_THIS>` with:

```
# Translation parameters
{intake-spec inline: source/target locale, mode=faithful, register=literary, domain=general}

# Glossary terms (only those that hit in current scene + prev/next windows)
{glossary terms — ~30-50 entries max via lookup() filter}

# Previous scene (last ~500 tokens) — for continuity
{prev_scene_summary OR last 500 tokens of prev_scene_v2 if available}

# CURRENT SCENE — translate ALL of this
<TRANSLATE_THIS>
{current_scene_source}
</TRANSLATE_THIS>

# Next scene opening (first ~200 tokens) — for narrative flow context
{next_scene_first_paragraph_source}

# Output requirements
- Translate ONLY content inside <TRANSLATE_THIS>
- Preserve scene's paragraph breaks exactly
- Do NOT include translation of prev/next windows
- Output ONLY the translation
```

### Decision 5 — `prev_scene_summary` mechanism
First scene of a chapter has no prev — pass empty.
Subsequent scenes get prev_scene_v2 (the last completed translation) truncated to last 500 tokens. This ties scene N's output to scene N-1's actual translation, not the source — preserves voice continuity in target.

If prev_scene_v2 > 500 tokens, take last 500 (sliding window).

### Decision 6 — Glossary scope per scene
Don't inject full project glossary into every scene's prompt (bloat). Per scene:
- Scan source text for known terms via `lib.glossary.lookup(...)` over current + prev + next windows.
- Inject only matched terms.
- Falls through to L4 LLM for unknown terms (audit-trail flagged).

### Decision 7 — Reflection mode
Use 4D `prompt-reflect-4d.md` for Tier 1 (Accuracy / Fluency / Style / Terminology).

5D effectiveness (Tier 2) deferred — that's transcreation-specific.

A "voice consistency" axis (Tier 3 S3 gate) is also deferred.

### Decision 8 — Verification gates (Tier 1)
Run M1 + M2 + S1 + S2 + I1, with these tweaks per skill table:

| Gate | Tier in novel | Notes |
|---|---|---|
| M1 placeholder integrity | HARD | No-op in practice (novels rarely have placeholders) |
| M2 project glossary compliance | HARD | Critical — character names + place names in user-supplied glossary |
| S1 back-translation | SHOULD (faithful), MUST (transcreation) | Same as creative; novel is faithful by default |
| S2 register preservation | SHOULD | Verify literary register preserved scene-to-scene |
| I1 untranslatability flagging | INFO | Cultural references / wordplay → audit-trail decision log |

Same gate structure as `translation-doc`. No new gates in Tier 1.

## Implementation Phases

Roughly 5 commits over ~1-2 days. Branch: `feat/translation-toolkit-v0.2.0-novel-mode`.

### Phase A — Scene-aware chunker (1 commit)

**Files:**
- Create: `translation-toolkit/scripts/lib/scene_chunker.py`
- Create: `translation-toolkit/scripts/tests/test_scene_chunker.py`

**API:**
```python
def chunk_chapter_into_scenes(chapter_text: str, max_scene_tokens: int = 2000) -> list[Scene]:
    """Split a chapter into Scene objects using boundary markers + token-fill fallback."""

@dataclass
class Scene:
    index: int        # zero-based within chapter
    source_text: str
    boundary_type: str  # "explicit_marker" | "blank_gap" | "heading" | "fallback_token_fill"
    token_count: int    # approx, via tiktoken or char/3 heuristic
```

**Tests:**
1. Explicit marker split (`* * *`, `***`, `―――`, `◇◇◇`)
2. Blank-gap split (≥3 blank lines)
3. Heading split (next H2/H3 starts new scene)
4. Token-fill fallback when no markers
5. Real-novel fixture (use any public-domain JP text excerpt, e.g. 青空文庫 fragment)

### Phase B — Scene-window prompt builder (1 commit)

**Files:**
- Create: `translation-toolkit/scripts/lib/novel_prompts.py`
- Create: `translation-toolkit/scripts/tests/test_novel_prompts.py`

**API:**
```python
def build_scene_draft_prompt(
    *,
    scene: Scene,
    prev_scene_v2: str | None,
    next_scene_source: str | None,
    intake_spec: dict,
    glossary_hits: list[dict],
) -> str:
    """Build DRAFT prompt per Decision 4 layout."""

def build_scene_reflect_prompt(scene: Scene, draft_v1: str, intake_spec: dict, glossary_hits: list[dict]) -> str:
    """4D reflect — same shape as translation-doc."""

def build_scene_improve_prompt(scene: Scene, draft_v1: str, critique_json: dict) -> str:
    """REVISER — apply critique."""
```

**Tests:**
- prev=None case (first scene)
- prev with long prev_scene_v2 → truncates to last 500 tokens
- next=None case (last scene)
- glossary injection only includes terms appearing in current + prev + next
- Full prompt structure matches Decision 4 layout

### Phase C — `translation-novel` SKILL.md + protocols (1 commit)

**Files:**
- Modify: `translation-toolkit/scripts/distribute.py` — add `translation-novel` to `ACTIVE_SKILLS`
- Create: `translation-toolkit/skills/translation-novel/SKILL.md`
- Create: `translation-toolkit/skills/translation-novel/protocols/scene-chunking.md`
- Create: `translation-toolkit/skills/translation-novel/protocols/scene-window-context.md`
- Create: `translation-toolkit/skills/translation-novel/checklists/novel-quality-checklist.md`

**SKILL.md sections** (mirror translation-doc):
- Inputs: chapter file path (single .md per chapter; recommend pre-processing via `tsundoku:book-extract`); intake-spec; project_glossary_path (recommended for character names)
- Pipeline: Layer 2 (parse + scene chunk) → Layer 3 (per-scene DRAFT/REFLECT/IMPROVE) → Layer 4 (M1+M2+S1+S2+I1) → Layer 5 (concatenate scene v2s into chapter output)
- When to use: novel chapters, long-form fiction
- When NOT to use: technical docs (use translation-doc), ad copy (use translation-creative)
- See also: protocols + checklists + canonical references

**Run distribute + verify-drift in same commit.** Adds 20 functional copies (1 new active skill × 20 canonical files).

### Phase D — Smoke test on real Japanese novel chapter (1 commit)

**Files:**
- Create: `translation-toolkit/scripts/tests/fixtures/sample-novel-chapter-ja.md`
- Create: `translation-toolkit/scripts/tests/test_e2e_novel_smoke.py`

**Fixture choice:** A 1-2 page excerpt from public-domain 青空文庫 (e.g., 夏目漱石 / 芥川龍之介 / 太宰治 first chapter opening). ~2000-3000 source chars to keep test runtime sane. Public domain so the repo can ship it.

**Smoke test (no LLM call):**
- Chunk → verify scene count ≥ 2
- Build prompts → verify structure matches Decision 4
- Glossary lookup → verify expected character/place names found
- Token cost calculation → verify total < 50K tokens for the chapter (vs ~500K under v0.1.0 windowing)

This is **Tier 1 acceptance**: cost reduction proven structurally without burning real LLM tokens.

### Phase E — Live LLM validation + docs (1 commit, optional)

**Files:**
- Modify: `translation-toolkit/skills/translation-novel/README.md` (en/ja/zh-TW per repo convention) — manual write per skill-internal lighter rules
- Modify: `translation-toolkit/NOTICES.md` — if 青空文庫 fixture is bundled, add attribution
- Modify: `translation-toolkit/.claude-plugin/plugin.json` — bump version to 0.2.0
- Modify: `.claude-plugin/marketplace.json` — sync description + bump

**Optional live test (not committed; just session validation):**
- Install plugin locally, invoke `translation-novel` on the fixture chapter, dump audit-trail.json
- Compare draft v2 quality against v0.1.0's `translation-doc` translating the same chapter (qualitative — voice / continuity / cost)
- Document findings in commit body or follow-up ADR
- If quality is unacceptable → escalate to user before proceeding to Tier 2

## Verification

After all phases:

```bash
cd translation-toolkit
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest scripts/tests/ -v
# Expect: 134 + N new (~10-15 from Phase A+B+D) = ~145+ tests pass

python3 scripts/distribute.py
# Expect: distributed=20 skipped=1 unrouted=0 skills=5 (was 4)

python3 scripts/verify-drift.py
# Expect: OK: all 100 functional copies byte-identical (was 80)

bash .claude/hooks/validate-skill-folder-structure.sh translation-toolkit/skills/translation-novel/SKILL.md
# Expect: PASS
```

## Out of Scope (deferred to Tier 2 / Tier 3)

### Tier 2 — Pre-pass character/glossary extraction (~3-5 days)

Re-trigger condition: Tier 1 ships and quality is judged "needs glossary maintenance friction reduction" (qualitative — translator user feedback).

Adds:
- `protocols/character-extraction.md` — pre-pass dispatched as subagent, reads whole book, extracts character profiles + voice notes + relationships → `<repo>/.translations/characters.json`
- `protocols/world-glossary-extraction.md` — same shape for place names, organizations, world-building terms → enriches project glossary
- Pre-pass also identifies recurring cultural references → seeds decision log
- 5D reflect (adds literary axis: rhythm / euphony / archaism / register-shift fidelity)
- Skill body grows by ~50 lines

### Tier 3 — Cross-chapter voice audit + multi-pass polish (~1-2 weeks)

Re-trigger condition: Tier 2 ships and translator-user reports voice drift across chapters or wants editorial passes.

Adds:
- New gate **S3 voice consistency** — sample N=5 utterances per character per chapter, LLM-judge whether register/口癖 match the character's voice profile from pre-pass. WARN by default; FAIL if any character profile bins drift > threshold.
- **Multi-pass orchestration**:
  - Pass 1: literal pass (current Tier 1 output)
  - Pass 2: literary polish (new prompt) — rhythm / register / naturalness
  - Pass 3: voice consistency repair (driven by S3 gate findings)
- Chapter-level human review checkpoint (skill emits "review needed" markers for translator)
- Audit-trail per-character voice-bin tracking

### Permanently out of scope

- Whole-novel single-pass translation (will always require chapter-level boundaries)
- Audio / voice acting integration
- Multi-language parallel translation in one run (each target language is a separate invocation)
- Format other than markdown chapters (other formats route through tsundoku:book-extract or other prep step)

## Pickup hints for fresh session

When starting:
1. `git checkout main && git pull`
2. `git checkout -b feat/translation-toolkit-v0.2.0-novel-mode`
3. Read this plan in full, then `docs/superpowers/specs/2026-05-06-translation-toolkit-design.md` for v0.1.0 architecture context.
4. Check current state of `translation-toolkit/scripts/lib/` — Phase A adds `scene_chunker.py` next to existing `glossary.py / protect_pass.py / gates.py / etc`.
5. Run baseline: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest scripts/tests/ -q` — should be 134 tests pass before you start.
6. Use `superpowers:subagent-driven-development` for implementation (proven on v0.1.0 — 24-task plan, ~30 implementer + 30 reviewer dispatches).
7. Each phase = one commit. Avoid bundling A+B because B's tests need A's chunker shape stable first.
8. PR title: `translation-toolkit v0.2.0 — novel translation mode (Tier 1: scene-aware chunking)`

## File path reference (for fresh session orientation)

- v0.1.0 spec: `docs/superpowers/specs/2026-05-06-translation-toolkit-design.md`
- v0.1.0 plan: `docs/superpowers/plans/2026-05-06-translation-toolkit-v0.1.0.md`
- Plugin root: `translation-toolkit/`
- Existing skills: `translation-toolkit/skills/{using-translation-toolkit, translation-intake, translation-i18n, translation-doc, translation-creative, translation-audit}/`
- Existing lib: `translation-toolkit/scripts/lib/{glossary, protect_pass, gates, gate_s1_backtrans, gate_s2_register, gate_i1_untranslatability, audit_trail, web_search}.py`
- Distribution: `translation-toolkit/scripts/distribute.py` (ACTIVE_SKILLS list — Phase C extends)
- CI: `.github/workflows/translation-toolkit-ci.yml` — should pass without modification (loops over skills via shell)
- Skill folder hook: `.claude/hooks/validate-skill-folder-structure.sh`

## Cost estimate (Tier 1 only)

| Item | Estimate |
|---|---|
| Phase A scene_chunker.py | ~150 LOC + ~80 LOC tests |
| Phase B novel_prompts.py | ~100 LOC + ~80 LOC tests |
| Phase C SKILL.md + 2 protocols + 1 checklist | ~200 LOC markdown |
| Phase D fixture + smoke test | ~100 LOC + 1 fixture file |
| Phase E READMEs (en/ja/zh-TW) + version bumps | ~250 LOC markdown |
| **Total new code** | **~960 LOC** |
| **Implementer time (single session)** | **1-2 days** |

Compared to v0.1.0 (~7000 LOC across 24 tasks over 1 long session). Tier 1 is comfortably scoped for a single fresh-session sprint.

---

**Plan complete.** Ready for fresh-session pickup.
