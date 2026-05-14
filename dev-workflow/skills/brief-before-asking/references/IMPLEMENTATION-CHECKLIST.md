# Implementation Checklist

Status: SKILL.md draft v1.0 committed. Below are next steps to validate, refine, and integrate.

## Phase 0 — Pre-flight (already done)

- [x] Worktree created: `feat/briefing-first-skill` from main
- [x] Skill folder scaffolded: `dev-workflow/skills/brief-before-asking/`
- [x] SKILL.md draft v1.0 written
- [x] DESIGN.md captures 4-iteration rationale
- [x] EXAMPLES.md provides 3 worked examples + 6 anti-patterns

## Phase 1 — Manual sanity check (do this first in next session)

Goal: read SKILL.md fresh and check it survives basic sanity.

- [ ] Read SKILL.md top-to-bottom in a new Claude Code session — does it parse without external context?
- [ ] Check token count: target ≤6,000 tokens (project rule). Use `wc -w` × 1.3 as rough proxy, or actual tokenizer.
- [ ] Check Anthropic folder convention: only single-level subfolders allowed under skill root (`.claude/hooks/validate-skill-folder-structure.sh` will block violations).
- [ ] Try invoking via natural language: "use brief-before-asking before you ask X" — does Claude pick it up?
- [ ] Try the description triggers: 「看不懂」「跟不上」「太多術語」 — does Claude correctly identify Mode B vs Mode C?

## Phase 2 — Test prompts (use `dev-workflow:skill-creator-advance`)

Goal: build a `test-prompts.json` for repeatable evaluation. Pattern follows existing dev-workflow skills (see `skill-creator-advance/test-prompts.json`).

Suggested test cases:

- [ ] **TC1 — Mode A trivial**: agent about to ask "should we rename this variable from `userId` to `user_id`?" → expected: skill does NOT trigger (trivial)
- [ ] **TC2 — Mode A complex**: agent about to ask "should we add an index to this query?" → expected: full 6-block briefing
- [ ] **TC3 — Mode B trigger**: user says "什麼意思" after short ambiguous question → expected: 6-block briefing + re-ask in specific form
- [ ] **TC4 — Mode C trigger (long explanation)**: user says "太多術語跟不上" after dense technical paragraph → expected: ONLY Mental Model + glossary + pause-and-choose
- [ ] **TC5 — Ambiguous reactive ("more context")**: expected: default to Mode C (safer — pauses)
- [ ] **TC6 — Mental Model jargon leakage**: agent puts "aggregate" / "saga" inside Mental Model without flagging → expected: anti-pattern detected
- [ ] **TC7 — Fake neutrality**: agent writes "I have no strong preference" in My take → expected: rejected, agent should state lean
- [ ] **TC8 — Unbalanced options**: option A in 5 lines, option B in 1 line → expected: rejected, equal-depth rule
- [ ] **TC9 — Bundled forks**: 3 independent questions in one briefing → expected: rejected, one fork per briefing
- [ ] **TC10 — Escape hatch**: user says "just decide, don't ask" → expected: skill defers, agent acts autonomously and notes choice

## Phase 3 — Description optimization (use `dev-workflow:skill-creator-advance`)

Goal: maximize trigger accuracy for both proactive and reactive modes.

- [ ] Current description is intentionally rich with trigger phrases. Test recall on phrases NOT in the list (e.g., "等等" "？？" "啊?" — minimalist Chinese confusion signals)
- [ ] Test precision: does the skill over-trigger on phrases like "what do you mean" used in casual context?
- [ ] Consider whether description should explicitly list **what is NOT this skill's job** (to reduce false positives against `complexity-critique` / `proposal-critique`)
- [ ] If description exceeds reasonable length, factor common patterns into `references/description-triggers.md`

## Phase 4 — Mode C precision/recall (the key new behavior)

Mode C is the iteration-4 addition that hasn't been tested. This is the highest-risk new behavior.

- [ ] Build 5+ examples where user explicitly says they don't follow a long explanation. Verify agent ONLY delivers Mental Model + glossary, then pauses.
- [ ] Build 5+ examples where user says vague "more context" right after agent's long explanation. Verify Mode C is preferred over Mode B.
- [ ] Test failure mode: agent triggers Mode C but then "continues" past the pause point (don't wait for user direction). This is the most likely regression.
- [ ] Test: agent's "previous turn" detection. Can it tell its own previous turn was a dense explanation vs a short question?

## Phase 5 — Integration touchpoints

- [ ] Add to `dev-workflow/README.md` skills table (currently lists 7 skills; brief-before-asking becomes #8)
- [ ] Cross-link from `superpowers:brainstorming` (brief-before-asking is mid-task; brainstorming is task-start)
- [ ] Cross-link from `superpowers:verification-before-completion` (brief-before-asking is mid-task; verification is task-finish)
- [ ] Consider whether `dev-workflow:complexity-critique` should reference brief-before-asking (when complexity critique surfaces a fork, that fork may need briefing)
- [ ] Add to `dev-workflow/CHANGELOG.md`

## Phase 6 — Quality gates (use `dev-workflow:skill-judge`)

Run advisory 8-dimension evaluation:

- [ ] Knowledge Delta — does the skill provide knowledge agent doesn't already have?
- [ ] Mindset + Procedures — does it shift agent behavior, not just add structure?
- [ ] Anti-Pattern coverage — does it explicitly reject failure modes?
- [ ] Spec Compliance — Anthropic skill conventions met?
- [ ] Progressive Disclosure — does it load only what's needed?
- [ ] Freedom Calibration — does it constrain enough without over-prescribing?
- [ ] Pattern Recognition — does it pick correct mode (A/B/C) reliably?
- [ ] Practical Usability — does using it actually speed up decisions?

Target: ≥85/120 (A-/B+ grade).

## Phase 7 — Skill tuning (later, use `dev-workflow:skill-tuning`)

Once draft is validated:

- [ ] Run blind A/B variants on key prompts:
  - V1: current draft
  - V2: shorter Mental Model rule (1 sentence cap)
  - V3: My take goes BEFORE Options
- [ ] Capture user preference data
- [ ] Iterate

## Phase 8 — Commit and PR

- [ ] Run skill folder validation: `bash .claude/hooks/validate-skill-folder-structure.sh` (PostToolUse hook should also catch violations live)
- [ ] Commit messages should follow project convention (see existing commits on dev-workflow skills)
- [ ] PR description should reference DESIGN.md for "why this design"
- [ ] PR description should call out Mode C as the key novel behavior

## Open Questions to Resolve Before First Release

1. **Mode B vs Mode C disambiguation**: current heuristic "default to Mode C if ambiguous" — validate this is actually safer in practice
2. **Mental Model length**: 1-2 sentences may not scale to multi-service architecture forks. Consider per-stakes length rule.
3. **Glossary persistence**: should there be a project-level glossary that accumulates over sessions? Out of scope for v1.0 but worth flagging.
4. **Escalation hook to scqa-decision-style heavyweight mode**: when user says "go full SCQA," what does that look like? Currently a TODO.

## Reference Links (Internal)

- Skill source: `dev-workflow/skills/brief-before-asking/SKILL.md`
- Design rationale: `dev-workflow/skills/brief-before-asking/references/DESIGN.md`
- Worked examples: `dev-workflow/skills/brief-before-asking/references/EXAMPLES.md`
- Anthropic skill conventions: project `CLAUDE.md` (root)
- Test prompts pattern: `dev-workflow/skills/skill-creator-advance/test-prompts.json`
- Folder validator: `.claude/hooks/validate-skill-folder-structure.sh`

## Reference Links (External / Vault)

- Full research narrative (v4, current): `kouko-obsidian-vault/research/2026-05-13 briefing-first Skill 設計——複雜工程問題的結構化提問前簡報.md`
- Background framework research (v1, scope-corrected): `kouko-obsidian-vault/research/2026-05-13 SCQA 框架與 LLM·人類雙向偏見防禦——技術決策溝通框架深度研究.md`
- Original Grok conversation: https://grok.com/c/a58d4bf8-7f5e-4d8b-b46e-9e4f9fbe1455
