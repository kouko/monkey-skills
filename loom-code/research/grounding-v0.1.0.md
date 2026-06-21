# grounding — v0.1.0

> **Purpose**: trace every authoritative measure shipped in `code-toolkit` v0.1.0 back to its primary source. This is the auditable record that says *"we did not invent these rules; here is the canon."* Audience: future maintainer (or external reviewer) asking *"why does `tdd-iron-law` cite Beck 2002 Preface specifically, and not Ch.4?"*

## How to read this doc

`code-toolkit` ships with a **two-layer architecture** (TECH-SPEC §2.2):

- **Process layer** — original to this plugin. The router measure, the subagent dispatch model, the per-skill orchestration. These are *engineering decisions* (this toolkit's authority), not citations from a book.
- **Knowledge layer** — byte-identical functional copies (with a 5-line SSOT header) of `domain-teams:code-team/{standards,rubrics,checklists}/`. The primary-source citations live in those canonical files; this plugin inherits them via `scripts/distribute.py`. The set is constant across this plugin's versions until code-team's version moves.

This doc is split accordingly: §1 enumerates what we inherit, §2 enumerates what we authoritatively claim, §3 lists explicit non-claims (things we are deliberately *not* asserting in v0.1.0).

---

## 1. Inherited primary sources — code-team v5.6.0 canon

`code-team` (canonical SoT for the knowledge layer at the time of v0.1.0 ship) cites the following primary sources. Each is reproduced verbatim in the functional copies under `skills/*/standards|rubrics|checklists/`. Drift between this list and the canonical files is enforced by `scripts/verify-drift.py` (CI gate).

| # | Standard / canon | Source (verbatim from canonical) | Where in v0.1.0 |
|---|---|---|---|
| 1 | TDD discipline | **Kent Beck (2002) *Test-Driven Development: By Example*, Addison-Wesley Signature Series, ISBN 978-0321146533.** Cited: Preface (the "never write production code without a failing test" rule), Ch.1 "Multi-Currency Money" (worked walkthrough), Part II "Test-Driven Development Patterns" (Ch.25 in particular — *Fake It*, *Triangulate*, *Obvious Implementation*, *Child Test*, *One Step Test*). | `tdd-iron-law/standards/tdd-standard.md`, `subagent-driven-development/standards/tdd-standard.md` |
| 2 | TDD Three Laws + F.I.R.S.T | **Robert C. Martin (2008) *Clean Code: A Handbook of Agile Software Craftsmanship*, Prentice Hall (Robert C. Martin Series), ISBN 978-0132350884.** Cited: Ch.2 Meaningful Names; Ch.3 Functions; Ch.4 Comments; Ch.9 Unit Tests (Three Laws of TDD §1–3 + F.I.R.S.T properties). | `tdd-iron-law/SKILL.md`, `*/standards/tdd-standard.md`, `*/standards/naming-and-functions.md` |
| 3 | TDD JP 一次参照 | **和田卓人 訳 (2017) 『テスト駆動開発』, オーム社, ISBN 978-4274217883.** Beck (2002) の日本語正規訳。日本人プログラマ向けレビューの de facto primary。和田の訳者解説「テストは仕様の具体化であり、設計の feedback loop である」を JP anchor として引用。 | `tdd-iron-law/SKILL.md`, `*/standards/tdd-standard.md` |
| 4 | TDD JP supplemental | **Henney, K. (ed.) / 和田卓人 (監修) (2010) 『プログラマが知るべき 97 のこと』, オライリー・ジャパン, ISBN 978-4-87311-479-8.** 和田卓人 執筆エッセイ「不具合にテストを書いて立ち向かう」。 | `*/standards/tdd-standard.md` (JP echo) |
| 5 | Naming + Functions | Martin (2008) *Clean Code* Ch.2 + Ch.3 + Ch.4 (above); plus **Hunt, A. & Thomas, D. (2019) *The Pragmatic Programmer: Your Journey to Mastery, 20th Anniversary Edition*, Addison-Wesley, ISBN 978-0135957059** (Ch.2 Topic 9 DRY; Topic 10 Orthogonality). JP anchor: 『97 のこと』まつもとゆきひろ「名前重要」. | `*/standards/naming-and-functions.md` |
| 6 | SOLID | **Martin, R.C. (2000) *Design Principles and Design Patterns*, objectmentor.com** (canonical mirror: https://staff.cs.utu.fi/~jounsmed/doos_06/material/DesignPrinciplesAndPatterns.pdf — the original compilation). Plus **Martin (2017) *Clean Architecture*, Prentice Hall, ISBN 978-0134494166** Part III. Plus **Martin (2002) *Agile Software Development, Principles, Patterns, and Practices*, Prentice Hall, ISBN 978-0135974445**. Acronym attribution: Michael Feathers (~2004). | `*/standards/solid-principles.md` |
| 7 | Pragmatic principles | Hunt & Thomas (2019) (above). Plus **Fowler, M. — bliki entry "Yagni"**: https://martinfowler.com/bliki/Yagni.html (authoritative Fowler bliki). Plus **Fowler (2018) *Refactoring*, 2nd ed.** for the Rule of Three (Don Roberts). | `*/standards/pragmatic-principles.md` |
| 8 | Refactoring | **Fowler, M. (2018) *Refactoring: Improving the Design of Existing Code*, 2nd ed., Addison-Wesley, ISBN 978-0134757599.** 2nd ed uses JavaScript, contains 68 refactorings. Cited: Ch.1 walkthrough, Ch.2 "Principles in Refactoring" (Rule of Three, Two Hats), "Bad Smells in Code" chapter (carried forward from 1999 1st ed Ch.3 — 2nd ed chapter number unverified per code-team's citation-honesty note). | `*/standards/refactoring-standard.md` |
| 9 | Legacy code | **Feathers, M. (2004) *Working Effectively with Legacy Code*, Prentice Hall (Robert C. Martin Series), ISBN 978-0131177055.** Cited: Preface ("legacy code = code without tests"); Ch.4 The Seam Model; Ch.13 Characterization Tests; Ch.25 Dependency-Breaking Techniques (24 techniques). | `*/standards/refactoring-standard.md` |
| 10 | App security | **OWASP Foundation (2025) *Application Security Verification Standard, Version 5.0.0*.** Released 2025-05-30 at OWASP Global AppSec EU (Barcelona). URLs: https://asvs.dev/v5.0.0/, https://owasp.org/www-project-application-security-verification-standard/. License CC BY-SA 4.0. 17 chapters (V1–V17), ~350 verification requirements, 3-tier L1/L2/L3. | `*/standards/app-security-standard.md`, `*/checklists/security-checklist.md` |
| 11 | Multi-byte / encoding security | **徳丸浩 (2018) 『体系的に学ぶ 安全な Web アプリケーションの作り方 第 2 版 — 脆弱性が生まれる原理と対策の実践』, SB クリエイティブ, ISBN 978-4797393163.** Ch.6「文字コードとセキュリティ」. NDL record ID R100000002-I029031208. 第 3 版は 2026-04 現在未発表。 | `*/standards/character-encoding-security.md` |

**Total**: 8 primary sources (counted by distinct authoritative text — book / spec / bliki entry; the JP supplement #4 is a secondary echo, not an independent source). Two are JP-language primaries (#3 and #11); one is a living spec (#10, OWASP ASVS — pin to v5.0.0 as of v0.1.0 ship).

---

## 2. Authoritative claims this toolkit makes (process layer, original to v0.1.0)

These are **engineering decisions**, not citations. They are the toolkit's own authority. Where a related body of work exists upstream (`obra/superpowers`, Anthropic skill convention), it is acknowledged as inspiration but not as canonical citation.

### 2.1 SessionStart hook injection (router pattern)

- **Claim**: the router skill (`using-code-toolkit/SKILL.md`) is auto-injected at session start so the agent does not depend on the user remembering to invoke it.
- **Inspiration**: `obra/superpowers` v5.1.0 — same hook pattern. **Not a citation** because Superpowers is a contemporary peer project, not a primary source.
- **Authority**: this toolkit's design choice (PRODUCT-SPEC Q-lock Q1, Q6).
- **Token budget**: 2000 tokens for the router (P1-A). Empirical estimate at v0.1.0 ship: ~1853 tokens.

### 2.2 "Delete it. Start over." remediation measure

- **Claim**: Iron Law violation has exactly one remediation — *"delete the production code, write the failing test, start over."*
- **Inspiration**: `obra/superpowers` measure language (intentionally preserved for its rhetorical force; PRODUCT-SPEC Q7).
- **Authority**: the *force* of the measure is this toolkit's choice; the *rule it enforces* (no production code without a failing test first) is grounded in inherited source #1 (Beck 2002 Preface) and #2 (Martin 2008 Three Laws §1).
- **Why it works**: the rule + the remediation are presented together, so an agent that reads §The Iron Law cannot rationalize a soft compliance ("I'll add tests later"). PRODUCT-SPEC §1.1 — the failure mode this measure addresses is "tests-after rationalization" being the most-common Iron Law breach.

### 2.3 Three-subagent triad per atomic task

- **Claim**: SDD dispatches three subagents per atomic task — implementer (worker) + spec-reviewer (evaluator) + code-quality-reviewer (evaluator) — with non-overlapping scope.
- **Inspiration**: `obra/superpowers` SDD model (PRODUCT-SPEC Q8).
- **Authority**: this toolkit's design choice. Why three (not two, not four):
  - Two collapses spec coverage and code quality into one verdict, hiding which dimension failed.
  - Four (e.g. adding security-reviewer) has been considered (Phase 3 may revisit) but at v0.1.0 the security checklist is rolled into code-quality-reviewer's six dimensions; splitting it adds dispatch cost without orthogonal signal yet.
  - Implementer ↔ reviewer separation enforces the CLAUDE.md role discipline: workers produce artifacts, evaluators produce verdicts; they do not cross.

### 2.4 Verdict aggregation rule (PASS / PASS_WITH_NOTES / NEEDS_REVISION)

- **Claim**: code-quality-reviewer verdict is `NEEDS_REVISION` if any 🔴 fatal flag fires; `PASS` if all six dimensions PASS and no flags; otherwise `PASS_WITH_NOTES`.
- **Authority**: this toolkit's design choice. The three-tier rather than binary scheme is to surface 🟡 should-fix flags as triageable debt (orchestrator may file or fix) without blocking the per-task progress bar, while 🔴 fatal blocks unconditionally. Spec-reviewer is binary because spec coverage is binary by definition (covered or not).

### 2.5 SSOT-and-functional-copy mechanism (cross-plugin variant)

- **Claim**: the knowledge layer is a byte-identical functional copy (canonical bytes + 5-line HTML comment SSOT header) of `domain-teams:code-team/`. Drift gated by `scripts/verify-drift.py`.
- **Inspiration**: `legal-toolkit/scripts/canonical/` + `distribute.py` + `verify-drift.py` (in-plugin variant). The cross-plugin variant introduced here reads from a sibling plugin (`../domain-teams/`) instead of in-plugin `canonical/`.
- **Authority**: monkey-skills convention (PRODUCT-SPEC Q5). The cross-plugin pull is the deliberate departure from legal-toolkit's pattern; reason is that the canonical knowledge layer is shared across multiple plugins (already mirrored in `dev-workflow:complexity-critique/references/mindset-*.md`) and centralizing canonical in `code-team` reduces drift surface.

### 2.6 Token budget for the hook-injected router

- **Claim**: `using-code-toolkit/SKILL.md` ≤ 2000 tokens (Phase 1 P1-A).
- **Authority**: this toolkit's choice. Reasoning: the SessionStart hook fires on `startup | clear | compact`, so this content is paid for **N times per session**. 2000 tokens × N = real cost. Other skills are lazy-loaded via the `Skill` tool; their budgets are correspondingly relaxed (TECH-SPEC §1.4).
- **Verification**: `python3 -c "..."` in PoC sanity check showed v0.1.0 router at ~1853 tokens.

### 2.7 Coexistence contract

- **Claim**: code-toolkit coexists with (a) `domain-teams:code-team` as passive-gate entry, (b) `dev-workflow:{git-memory, complexity-critique, proposal-critique}` via delegation, (c) `obra/superpowers` via `CODE_TOOLKIT_MODE=off` env var.
- **Authority**: PRODUCT-SPEC Q2 (do not deprecate code-team) + cross-plugin delegation contract (CLAUDE.md). The Superpowers env var is the only soft-fork escape because Superpowers is the only contemporary peer with overlapping skill names + dual SessionStart hooks.

---

## 3. Explicit non-claims in v0.1.0

To avoid quiet scope creep into Phase 2-3 territory, the following are NOT asserted by code-toolkit at v0.1.0 ship:

| Non-claim | Why deferred | Phase |
|---|---|---|
| Brainstorming-time complexity critique is mandatory | OQ-3 in PRODUCT-SPEC §7. Until evaluated, `using-code-toolkit` only mentions `dev-workflow:complexity-critique` as available. | Phase 2 |
| `--soft-mode` flag for Iron Law enforcement strength | OQ-1. Honest answer at v0.1.0: we don't know whether the strict measure is too rigid until 5 dogfood sessions tell us. | Phase 1.5 |
| `verification-before-completion` re-checks Iron Law from commit history | TQ-6. Tdd-iron-law SKILL.md mentions this as future cross-reference, but the verification skill itself is not in v0.1.0. | Phase 3 |
| Codex CLI plugin actually ships | P1-F. Manifest skeleton exists at `.codex-plugin/plugin.json`; full ship is Phase 2.5. | Phase 2.5 |
| systematic-debugging primary-source citations | Skill itself is Phase 2; v0.1.0 makes no claims here. | Phase 2 |
| Final-reviewer subagent (post-all-tasks orchestrator-level review) | Considered for v0.1.0 SDD; deferred — adds dispatch cost without orthogonal signal at the per-task level. May revisit in Phase 3 with `requesting-code-review`. | Phase 3 |
| Plan-document-reviewer subagent | Used by Superpowers `writing-plans`; that skill is Phase 2. | Phase 2 |

---

## 4. Drift policy

The 11 functional copies (1 in `tdd-iron-law/standards/` + 10 in `subagent-driven-development/{standards,rubrics,checklists}/`) MUST equal `(SSOT header) + (canonical bytes)`. Enforcement:

```
1. Canonical edit lands in domain-teams/skills/code-team/<subdir>/<file>.
2. Same commit runs: python3 code-toolkit/scripts/distribute.py
3. CI runs: python3 code-toolkit/scripts/verify-drift.py
4. Any byte-mismatch fails the build with md5 + unified diff.
```

Tested at v0.1.0 ship: positive case (12 functional copies match expected) AND negative case (corrupting a copy with `echo EXTRA_LINE >> ...` fires the drift detector with the specific inserted line in the diff output).

---

## 5. Audit commands

For a future maintainer to re-verify this doc against the running toolkit:

```bash
# All functional copies match expected (canonical + header)
python3 code-toolkit/scripts/verify-drift.py

# Re-extract Primary Sources sections from the canonical layer
grep -A 20 "^## Primary Sources" \
  domain-teams/skills/code-team/standards/*.md

# Confirm router skill is under token budget (P1-A)
python3 -c "
import sys
content = open('code-toolkit/skills/using-code-toolkit/SKILL.md').read()
chars = len(content)
cjk = sum(1 for c in content if 0x3000 <= ord(c) <= 0x9fff or 0xff00 <= ord(c) <= 0xffef)
est = int(cjk * 1.2 + (chars - cjk) / 3.5)
print(f'estimated tokens: {est} (budget: 2000)')
sys.exit(0 if est <= 2000 else 1)
"

# Confirm hook bash script emits valid JSON with all 3 keys.
# CANONICAL: hookSpecificOutput.additionalContext — the nested camelCase
#   key BOTH hosts consume (Codex hooks doc, developers.openai.com/codex/
#   hooks: "That additionalContext text is added as extra developer
#   context"; Claude Code reads the same nested key).
# DEFENSIVE: additional_context + bare additionalContext — top-level
#   belt-and-suspenders emitted for cross-version/host portability, NOT
#   because Codex requires a snake_case shape.
code-toolkit/hooks/session-start | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert 'hookSpecificOutput' in d and 'additionalContext' in d['hookSpecificOutput']
assert 'additional_context' in d
assert 'additionalContext' in d
print('hook JSON shape OK')
"
```

---

## 6. Version log

### v0.1.0 (Phase 1 ship target)

- First version. All 11 inherited primary sources enumerated above are loaded via functional copy from `domain-teams:code-team` (v5.6.0 at code-team-side commit at the time of v0.1.0 ship — record the exact code-team SHA in `CHANGELOG.md` when v0.1.0 ships).
- Process-layer claims §2.1 through §2.7 are introduced new in v0.1.0.
- No retractions, no replaced citations.

### Future version-log entries

When a new version of code-toolkit ships:

- If a code-team standard changed → re-run `distribute.py`; this doc's §1 row needs updating only if a primary source was added / removed / replaced (not for editorial changes within the canonical body).
- If a process-layer claim changes (new subagent role; verdict scheme change; etc.) → add a row in §2 with the change rationale.
- If an explicit non-claim in §3 is now claimed → move that row from §3 to §2 with rationale.

---

## See also

- [`../PRODUCT-SPEC.md`](../PRODUCT-SPEC.md) §8 (Q-lock) — the eight design decisions §2 refers to.
- [`../TECH-SPEC.md`](../TECH-SPEC.md) §2.5 — SSOT mechanism implementation.
- [`../ROADMAP.md`](../ROADMAP.md) §Decision Ledger — Phase 1 P-codes referenced inline.
- [`../scripts/canonical/README.md`](../scripts/canonical/README.md) — full SSOT pointer table (canonical → functional copy mapping).
- [`../skills/tdd-iron-law/standards/tdd-standard.md`](../skills/tdd-iron-law/standards/tdd-standard.md) — functional copy (verbatim Beck 2002 / Martin 2008 / 和田訳 2017 citations).
