# skill-triggering — expected behavior per prompt

Each `.txt` in this directory is a single user prompt, copy-pastable into a fresh Claude Code / Codex CLI session **with `loom-code` installed** (so the SessionStart hook injects `using-loom-code/SKILL.md`).

For each prompt, the assertion is what the **first agent reply** must contain (or must NOT contain). If the agent's reply matches all `MUST` rows, that prompt **passes**.

> Phase 1 verification mode: **manual** — open a fresh session, paste the prompt, eyeball the reply against the assertions. Phase 1.5+ may add an automated harness (mirror Superpowers `tests/skill-triggering/run-all.sh`).

---

## `new-feature.txt`

| Acceptance | Rule |
|---|---|
| MUST | Reply mentions `using-loom-code` was loaded (or routes through it implicitly) |
| MUST | Reply does **not** start writing implementation code in the first turn |
| MUST | Reply EITHER invokes `brainstorming` (Phase 2 — when shipped) OR asks 2-3 clarifying questions framed as *what problem*, *smallest end state*, *what becomes obsolete* |
| MUST | Reply mentions `tdd-iron-law` will apply when implementation begins |
| MUST | Reply mentions `subagent-driven-development` is a candidate (>1 module: editor, store, autosave hook, restore-on-load → 3-4 modules) |

**Maps to**: ROADMAP §Phase 1 acceptance — "Let's build X" auto-trigger discovery flow; G2 (SessionStart hook injects router); G4 (SDD as candidate for >1-module work).

---

## `bug-fix.txt`

| Acceptance | Rule |
|---|---|
| MUST | Reply mentions `using-loom-code` and `tdd-iron-law` |
| MUST | Reply proposes **writing a failing test first** that reproduces the BOM-stripping bug (use the existing `tests/parsers/` suite) |
| MUST | Reply does **not** propose patching `src/parsers/csv.py` before writing the failing reproducer test |
| SHOULD | Reply cites Beck 2002 §Preface or 和田訳 2017 when explaining why test-first |
| MAY | Reply mentions `character-encoding-security.md` (BOM handling has primary-source coverage) |

**Maps to**: G3 (Iron Law applies even on bug-fix scope, not just feature work).

---

## `refactor.txt`

| Acceptance | Rule |
|---|---|
| MUST | Reply mentions `subagent-driven-development` (god-class extraction → multiple atomic tasks) |
| MUST | Reply emphasises **preserve existing tests as safety net** before extracting collaborators (Beck 2002 Refactor step + Fowler 2018 §Extract Class) |
| MUST | Reply does **not** propose deleting or weakening the existing 85%-coverage test suite to "clean up" anything |
| SHOULD | Reply names a candidate task split (e.g. extract Pricer → Tax → Inventory → Notifier as 4 atomic tasks) |
| SHOULD | Reply mentions `tdd-iron-law` applies to *new* tests for *new* collaborators (not re-derivation of existing tests) |

**Maps to**: G4 (4-task plan → 12-subagent SDD dispatch — refactor scope is exactly this scenario).

---

## `pure-question.txt`

| Acceptance | Rule |
|---|---|
| MUST | Reply answers the question directly. **No** brainstorming, no SDD dispatch, no `tdd-iron-law` invocation |
| MUST | Reply does **not** propose changing the code |
| MUST | Reply does **not** create new files |
| SHOULD | Reply explicitly notes that this is a read-only question (so the user knows the router correctly identified the non-coding scope) |

**Maps to**: §When NOT to use in `using-loom-code/SKILL.md` — pure read-only questions are out of scope. Tests that the router does not over-trigger.

---

## `explicit-skip.txt`

| Acceptance | Rule |
|---|---|
| MUST | Reply confirms this matches one of the **enumerated** §When NOT to Use exemptions in `tdd-iron-law/SKILL.md` (throwaway / spike) |
| MUST | Reply quotes or references the §When NOT to Use criteria — does **not** silently comply with "skip TDD" |
| MUST | Reply asks the user to confirm explicitly: *"throwaway, will not commit, will delete within the session — confirmed?"* |
| MUST | Only after explicit confirmation: writes the script. If confirmation withheld, reverts to TDD flow. |
| MUST NOT | Reply silently writes the script on first turn just because the user said "skip TDD" |

**Maps to**: G3 + ROADMAP P1-B (Iron Law has a narrow enumerated exception path, not a soft override). Tests that **legitimate** override is honored AFTER explicit re-confirmation.

---

## How to run (Phase 1 — manual)

```bash
# Prereq: loom-code installed in the host (Claude Code / Codex CLI)
# Open a fresh session (matters: SessionStart hook fires once per session)
# Paste the .txt content as the first user message
# Eyeball the agent's first reply against the table above
```

5 / 5 PASS = Phase 1 acceptance §"using-loom-code auto-loaded via hook + appropriate routing per task type" met.
