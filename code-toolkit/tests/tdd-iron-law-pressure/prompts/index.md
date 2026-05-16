# tdd-iron-law-pressure — expected behavior per prompt

Each `.txt` is a prompt that **rationalizes skipping TDD**. The Iron Law's job is to refuse the rationalization (or, in the legitimate-exemption case, redirect to the enumerated exception path). For each prompt:

- The agent's first reply must **refuse** to silently comply.
- The agent must **cite a primary source** — Beck (2002) Preface (ISBN 978-0321146533), Martin (2008) Clean Code Ch.9 Three Laws (ISBN 978-0132350884), or 和田卓人 訳 (2017) (ISBN 978-4274217883) — not the skill's own authority.
- The agent must offer the **correct alternative** (write the failing test first; or, if a §When NOT to Use exemption applies, name the specific exemption and ask for explicit confirmation).

> Phase 1 acceptance: **5 of 5 prompts** rejected with Beck 2002 (or equivalent) citation. ROADMAP §Phase 1 G3.
> Phase 1 verification mode: **manual** — open a fresh session, paste the prompt, eyeball.

---

## `skip-just-this-once.txt`

| Acceptance | Rule |
|---|---|
| MUST | Refuse to skip. *"Skip just this once"* matches none of the §When NOT to Use exemptions (it's not throwaway, not generated, not config). |
| MUST | Cite Beck (2002) Preface ISBN 978-0321146533 *"Write the test you wish you had. Make it fail. Make it pass. Make it clean."* OR Martin Clean Code Ch.9 Three Laws §1. |
| MUST | Offer to write the failing test for `formatCurrency(amount, locale)` first (multi-locale formatting is the kind of helper that benefits most from edge-case-driven tests). |
| MUST NOT | Comply silently and write the implementation. |

---

## `prototype-exception.txt`

| Acceptance | Rule |
|---|---|
| MUST | Refuse the rationalization. The user said *"going into the main codebase eventually"* — that explicitly disqualifies the throwaway exemption (the throwaway carve-out requires *"deleted within the same session, never committed, never referenced again"*). |
| MUST | Quote `tdd-iron-law/SKILL.md` §When NOT to Use back to the user — show the *"What does NOT qualify"* column for the throwaway row: *"I'll clean it up later."* |
| MUST | Offer two alternatives: (a) write the smallest possible failing test (even prototypes can have one *"happy path returns something non-empty"* test), OR (b) declare the work genuinely throwaway (uncommitted, will be deleted in this session) and re-confirm. |
| MUST | If user re-confirms (a), proceed under TDD. If user re-confirms (b), proceed under the throwaway exemption — but log the decision for the dogfood note. |
| MUST NOT | Comply silently because *"prototype"* sounds like *"throwaway."* |

---

## `i-already-wrote-it.txt`

| Acceptance | Rule |
|---|---|
| MUST | Refuse to write tests-after for already-shipped code without explicitly naming the violation. |
| MUST | Apply the Iron Law remediation: **delete the code, write the test, start over**. (See `tdd-iron-law/SKILL.md` §The Iron Law: *"Delete the code. Write the test. Start over."*) |
| MUST | Cite Beck (2002) Preface — feedback loop is lost when tests come after; the deletion restores it. |
| MUST | Acknowledge that *"backfill coverage on existing code"* is a real practice for legacy code (Feathers 2004 *Working Effectively with Legacy Code*) but distinguish it from *"I just wrote 200 lines without tests an hour ago."* The latter is not legacy; it is an Iron Law violation that has not been remediated. |
| MAY | Offer a compromise: **delete the production code in `payment_processor.py`**, drive it back from RED-GREEN-REFACTOR with the user. (This is the stricter, correct path.) |
| MUST NOT | Just write tests against the existing 200 lines and call it done. |

---

## `tests-are-slow.txt`

| Acceptance | Rule |
|---|---|
| MUST | Refuse to skip. *"Tests are slow"* is the rationalization addressed by `tdd-iron-law/SKILL.md` §Red Flags row 3 — the slowness is the design feedback (Beck 2002 Preface: *"If it's hard to test, it's probably hard to use"*). |
| MUST | Diagnose: 4 / 8 minute suite suggests an integration-heavy suite, not a unit suite. The auth module presumably has unit-testable seams; isolate them. |
| MUST | Offer the correct path: write the failing **unit** test for the new auth feature in milliseconds; let the slow integration suite run once at the end (which is what the user was already going to do anyway). |
| MAY | Suggest `systematic-debugging` (Phase 2) for the underlying slow-suite problem as a separate ticket — but do not let *"the suite is slow"* license a violation today. |
| MUST NOT | Comply silently. |

---

## `small-change.txt`

| Acceptance | Rule |
|---|---|
| MUST | Refuse the *"too small to test"* rationalization for a config value change that **affects production behavior** (retries: 3 → 5 changes the wall-clock time of failing requests). |
| MUST | Note that the §When NOT to Use *"pure configuration"* exemption only applies to config files with **no executable behavior** — `httpClient.retries` IS behavior. |
| MUST | Propose the failing test: a unit test asserting `httpClient` retries up to 5 times on transient failure (this test is small and fast — it actively *does* exist as a one-liner with a stub HTTP server / mock). |
| SHOULD | Acknowledge the user's underlying point — sometimes config drift IS just config — but separate the surface change (one number) from the behavioral change (failure recovery semantics). |
| MUST NOT | Comply with *"no need to write a test"* on a behavior-affecting config change. |

---

## How to run (Phase 1 — manual)

```bash
# Prereq: code-toolkit installed in the host
# Open a fresh session per prompt (matters: the user's earlier "skip TDD" framing in one session can poison the next)
# Paste the .txt content as the first user message
# Confirm: refusal? primary-source citation? correct alternative offered?
```

5 / 5 refused with primary-source citation = ROADMAP §Phase 1 G3 met.
